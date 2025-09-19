"""A simple HTML parser using BeautifulSoup."""

from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


class HTMLParser:
    """A class for parsing HTML content."""

    def __init__(self):
        """Initialize the HTMLParser."""
        self.soup = None
        self.base_url = None

    def parse_url(self, url):
        """Fetch a URL and parse the HTML."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, "lxml")
            self.base_url = url
            return self.soup
        except requests.exceptions.RequestException as ex:
            print(f"Error fetching URL {url}: {ex}")
            return None

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
