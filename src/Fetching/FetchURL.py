#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
import logging
import lxml
from typing import Optional, Tuple, List
import re

try:
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# logging info for debugging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("fetcher")


# container for fetched page content and associeated resources
@dataclass
class PageResource:
    """Container for fetched page content and associated resources."""
    html: str
    css: str
    url: str
    title: Optional[str] = None
    status_code: int = 200  # might change this later in the case of an unsuccessful request or falsey data
    is_dynamic_render: bool = False

    @property
    def base_url(self) -> str:
        """Returns the base URL of the page."""
        parsed = urlparse(self.url)
        return f"{parsed.scheme}: //{parsed.netloc}"

    def __str__(self) -> str:
        return f"Pageresource(url = {self.url}, title={self.title}, dynamic={self.is_dynamic_render})"


# Determines if a page is dynamic or static
class HeuristicsEngine:
    @staticmethod
    def looks_dynamic(html: str) -> bool:
        """Looks for indicators of dynamic rendering and SPA"""
        soup = BeautifulSoup(html, "lxml")
        body = soup.body

        # checks if html body is minimal(most likely to be a dynamic page if it is)
        if not body:
            return True
        text = body.get_text(strip=True)
        text_len = len(text)

        if text_len < 100:
            script_tags = soup.find_all("script")
            if script_tags:
                logger.info("script tags found but minimal")
                return True

        framework_indicators = [
            soup.find(id="root"),
            soup.find(id="app"),
            soup.find(id="__next"),
            soup.find(attrs={"ng-app": True}),
            soup.find(attrs={f"data-reactroot": True}),
        ]

        if any(framework_indicators):
            logger.info("Page may be dynamic: SPA markers included")
            return True

        meaningful_elements = soup.find_all(
            ["h1", "h2", "p", "article", "main", "section"]
        )
        if len(meaningful_elements) < 3 and text_len < 500:
            logger.info("Page may be dynamic: minimal content")
            return True

        noscript_tags = soup.find_all("noscript")
        for tag in noscript_tags:
            noscript_text = tag.get_text(strip=True).lower()
            if any(
                word in noscript_text
                for word in ["javascript", "enable", "browser", "required"]
            ):
                logger.info(
                    "Page looks dynamic: found noscript tag with JS requirement warning"
                )
                return True

        return False


class StaticFetcher:
    @staticmethod
    def fetch(url: str) -> tuple[str, int]:
        """returns the HTML content and status code of a static page"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text, response.status_code
        except Exception as e:
            logger.error(f"Error fetching static content: {e}")
            raise

    @staticmethod
    def fetch_css(base_url: str, css_url: str) -> str:
        """returns the CSS content of a static page"""
        try:
            full_url = urljoin(base_url, css_url)
            response = requests.get(full_url, timeout=10)
            response.raise_for_status()
            css_text = response.text

            css_text = re.sub(
                r'url\([\'"]?(?!http)([^\'")]+)[\'"]?\)',
                lambda m: f"url({urljoin(full_url, m.group(1))})",#returns the modified CSS text
                css_text,
            )
            return css_text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching CSS content: {e}")
            return ""

    @staticmethod
    def fetch_css(base_url: str, css_url: str) -> str:
        """Fetch a CSS file, resolving relative URLs"""
        try:
            full_url = urljoin(base_url, css_url)
            response = requests.get(full_url, timeout=5)
            response.raise_for_status()

            # Quick fix for relative URLs in CSS
            css_text = response.text
            # Convert url(relative) to url(absolute)
            css_text = re.sub(
                r'url\([\'"]?(?!http)([^\'")]+)[\'"]?\)',
                lambda m: f"url({urljoin(full_url, m.group(1))})",
                css_text,
            )

            return css_text
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch CSS from {css_url}: {e}")
            return ""  # Return empty string on failure

    @classmethod
    def fetch_with_css(cls, url: str) -> PageResource:
        """Fetch HTML and all associated CSS"""
        html, status = cls.fetch(url)
        soup = BeautifulSoup(html, "lxml")

        # Remove unwanted tags
        for tag in soup.find_all(["script", "nav", "header", "footer", "aside"]):
            tag.decompose()

        # Extract title
        title_tag = soup.find("title")
        title = title_tag.text if title_tag else url

        # Collect all CSS
        css_bundle = []

        # 1. Inline <style> tags
        for style in soup.find_all("style"):
            css_bundle.append(style.text)
            style.decompose()

        # 2. Linked stylesheets
        for link in soup.find_all("link", rel="stylesheet", href=True):
            css_url = link["href"]
            css_content = cls.fetch_css(url, css_url)
            if css_content:
                css_bundle.append(css_content)

        # 3. Collect inline styles (for reference)
        inline_styles = []
        for tag in soup.find_all(attrs={"style": True}):
            selector = cls._get_selector_for_element(tag)
            if selector:
                inline_styles.append(f"{selector} {{ {tag['style']} }}")

        if inline_styles:
            css_bundle.append("\n".join(inline_styles))

        return PageResource(
            html=str(soup),
            css="\n".join(css_bundle),
            url=url,
            title=title,
            status_code=status,
            is_dynamic_render=False,
        )

    @staticmethod
    def _get_selector_for_element(tag) -> Optional[str]:
        """Generate a simple CSS selector for an element"""
        if tag.get("id"):
            return f"#{tag['id']}"

        if tag.get("class"):
            classes = ".".join(tag["class"])
            return f"{tag.name}.{classes}"

        return tag.name


class DynamicFetcher:
    """Fetch a page using Playwright"""
    @classmethod
    def is_available(cls) -> bool:
        return PLAYWRIGHT_AVAILABLE

    @classmethod
    def fetch_with_css(cls, url: str) -> PageResource:
        """Fetch a page's HTML and CSS content using Playwright"""
        if not cls.is_available():
            raise ImportError("Playwright is not installed")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1200, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36",
            )
            page = context.new_page()
            try:
                response = page.goto(url, wait_until="networkidle", timeout=20000)
                status_code = response.status if response else 200

                # Get title
                title = page.title()

                # Get rendered HTML
                html = page.content()

                # Extract all CSS
                css_bundle = page.evaluate("""
                    () => {
                        // Collect all stylesheet content
                        const sheets = Array.from(document.styleSheets);
                        const cssTexts = [];

                        for (const sheet of sheets) {
                            try {
                                const rules = Array.from(sheet.cssRules);
                                cssTexts.push(rules.map(r => r.cssText).join("\\n"));
                            } catch (e) {
                                // CORS error for external stylesheets
                                console.warn("Could not access stylesheet rules:", e);
                            }
                        }

                        // Also collect inline styles
                        const elements = document.querySelectorAll('[style]');
                        const inlineStyles = [];

                        for (const el of elements) {
                            let selector = '';
                            if (el.id) {
                                selector = '#' + el.id;
                            } else if (el.className) {
                                selector = el.tagName.toLowerCase() + '.' +
                                    el.className.split(' ').join('.');
                            } else {
                                selector = el.tagName.toLowerCase();
                            }

                            inlineStyles.push(`${selector} { ${el.style.cssText} }`);
                        }

                        if (inlineStyles.length > 0) {
                            cssTexts.push(inlineStyles.join("\\n"));
                        }

                        return cssTexts.join("\\n");
                    }
                """)
                return PageResource(
                    html=html,
                    css=css_bundle,
                    url=url,
                    title=title,
                    status_code=status_code,
                    is_dynamic_render=True,
                )
            except:
                logger.error(f"Error fetching page content: {e}")
                raise
            finally:
                browser.close()


# main fetcher that combines static and dynamic apporaches
class Fetcher:
    def __init__(self, mode="auto", prompt_for_dynamic=True) -> None:
        self.mode = mode
        self.prompt_for_dynamic = prompt_for_dynamic
        self.heuristics = HeuristicsEngine()

        self.dynamic_available = DynamicFetcher.is_available()
        if not self.dynamic_available:
            logger.warning("Dynamic fetching is not available")
            self.mode = "static"

    def _should_use_dynamic(self, html: str) -> bool:
        """Determine if dynamic fetcher should be used"""
        if self.mode == "static" or not self.dynamic_available:
            return False

        if self.mode == "dynamic":
            return True

        # For auto mode, check heuristics
        return self.heuristics.looks_dynamic(html)

    def fetch(self, url: str) -> PageResource:
        """Fetch page content"""
        logger.info(f"Fetching page content from {url} in mode: {self.mode}")
        try:
            if self.mode == 'dynamic':
                if self.dynamic_available:
                    return DynamicFetcher.fetch_with_css(url)
                else:
                    logger.error("Dynamic fetching is not available.")
                    # Should not happen due to check in __init__
                    raise Exception("Dynamic fetching is not available.")

            # mode is 'static' or 'auto'
            resource = StaticFetcher.fetch_with_css(url)

            if self.mode == 'auto' and self.heuristics.looks_dynamic(resource.html):
                logger.info("Page appears dynamic")
                if self.prompt_for_dynamic:
                    try:
                        response = input(
                            "\nThis page appears to require JavaScript. Fetch with dynamic renderer? (y/n): "
                        )
                    except EOFError: # In case of non-interactive environment
                        response = 'n'

                    if response.lower() == "y":
                        if self.dynamic_available:
                            logger.info("Fetching page content with dynamic renderer")
                            return DynamicFetcher.fetch_with_css(url)
                        else:
                            logger.warning("Dynamic fetching requested but not available. Falling back to static.")
            
            return resource

        except Exception as e:
            logger.error(f"Error fetching page content: {e}")
            return PageResource(
                html=f"<html><body><h1>Error fetching {url}</h1><p>{str(e)}</p></body></html>",
                css="",
                url=url,
                status_code=500,
                is_dynamic_render=False,
            )
