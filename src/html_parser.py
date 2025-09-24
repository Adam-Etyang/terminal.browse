#!/usr/bin/env python3
import subprocess
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import json


# TODO: Obtain and parse HTML content using curl
class HTMLParser:
    """A class for parsing HTML content."""

    def __init__(self):
        """Initialize the HTMLParser."""
        self.soup = None
        self.base_url = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.last_response = {}

        # TODO: Add method to fetch HTML using curl

    # fetch HTML content using curl
    def fetch_url(self, url, headers=None, timeout=15):
        """
        Return (html_content, response_info_dict) fetched with curl.
        """
        # ---------- build command ----------
        cmd = [
            "curl",
            "--silent",  # no progress bar
            "--location",  # follow redirects
            "--compressed",  # accept gzip / deflate
            "--user-agent",
            "curl/8.4.0",
            # write response meta data as LAST line
            "--write-out",
            r'{"http_code":"%{http_code}","content_type":"%{content_type}"}',
        ]

        if headers:
            for k, v in headers.items():
                cmd.extend(["--header", f"{k}: {v}"])

        cmd.append(url)  # finally the URL

        # ---------- execute ----------
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5,  # add a little cushion
            )
        except FileNotFoundError:
            raise Exception("curl executable not found; install curl or add it to PATH")
        except subprocess.TimeoutExpired:
            raise Exception("curl request timed out")

        if result.returncode != 0:
            raise Exception(
                f"curl exited with code {result.returncode}: {result.stderr}"
            )

        # ---------- split HTML from meta ----------
        *html_lines, meta_line = result.stdout.splitlines()
        html_content = "\n".join(html_lines)

        try:
            self.last_response = json.loads(meta_line)
        except json.JSONDecodeError:
            self.last_response = {"http_code": "000", "content_type": "unknown"}

        return html_content, self.last_response

    def parse_url(self, url):
        """Fetch and parse HTML from URL using curl"""
        try:
            print(f"Fetching {url} with curl...")

            # Optional: Add browser-like headers
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }

            html_content, response_info = self.fetch_url(url, headers)
            self.base_url = url
            self.soup = BeautifulSoup(html_content, "lxml")

            # Print response info
            print(f"HTTP {self.last_response.get('http_code', 'Unknown')}")
            print(f"Content-Type: {self.last_response.get('content_type', 'Unknown')}")

            return self.soup

        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {e}")

    def parse_html(self, html_string):
        """Parse HTML from a string."""
        self.soup = BeautifulSoup(html_string, "lxml")
        return self.soup

    def get_title(self):
        """Get the title of the parsed HTML."""
        if self.soup:
            title_tag = self.soup.find("title")
            return title_tag.text.strip() if title_tag else "Untitled"
        return "No title"

    def resolve_url(self, url):
        """Resolve a relative URL to an absolute URL."""
        if self.base_url and url:
            return urljoin(self.base_url, url)
        return url

    def parse_string(self, html_string):
        """Parse HTML from a string."""
        self.soup = BeautifulSoup(html_string, "lxml")
        return self.soup


if __name__ == "__main__":
    p = HTMLParser()
    html, info = p.fetch_url("https://en.wikipedia.org/wiki/Maize")
    print("Status:", info["http_code"])
    print(html)
