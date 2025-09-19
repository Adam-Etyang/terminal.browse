#!/usr/bin/env python3
from html_parser import HTMLParser
from TerminalRenderer import TerminalRenderer


class TerminalBrowser:
    def __init__(self, width=80):
        self.parser = HTMLParser()
        self.renderer = TerminalRenderer(width)
        self.current_url = None
        self.history = []

    def navigate(self, url):
        """Navigate to URL and render page"""
        try:
            print(f"Loading {url}...")
            soup = self.parser.parse_url(url)
            title = self.parser.get_title()

            self.current_url = url
            self.history.append(url)

            self.renderer.render_page(soup, title)

        except Exception as e:
            print(f"Error loading page: {e}")

    def render_html_string(self, html_string, title="Local HTML"):
        """Render HTML from string"""
        try:
            soup = self.parser.parse_string(html_string)
            self.renderer.render_page(soup, title)
        except Exception as e:
            print(f"Error rendering HTML: {e}")


# Example usage
if __name__ == "__main__":
    browser = TerminalBrowser(width=100)

    print("=== Testing with sample HTML ===")

    browser.navigate("https://httpbin.org/html")
