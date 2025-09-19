from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse


# class for parsing HTML content
class HTMLParser:
    def __init__(self):
        self.soup = None
        self.base_url = None

    # ferch url and parse HTML
    def parse_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, "lxml")
            self.base_url = url
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")

    # parse HTML from string
    def parse_html(self, html_stirng):
        self.soup = BeautifulSoup(html_stirng, "lxml")
        return self.soup

    def get_title(self):
        if self.soup:
            title_tag = self.soup.find("title")
            return title_tag.text.strip() if title_tag else "Untitled"
        return "No title"

    # resolve relative URL to absolute URL
    def resolve_url(self, url):
        if self.base_url and url:
            return urljoin(self.base_url, url)
        return url
