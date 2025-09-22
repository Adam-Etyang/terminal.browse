#!/usr/bin/env python3
import subprocess
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


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

        # TODO: Add method to fetch HTML using curl

    # fetch HTML content using curl
 
    def fetch_url(self, url, headers=None):
        try:
            cmd = [
                
            ]
            #adding additional headers
            if headers :
                for key, value in headers.items():
                    cmd.extend(['--header', f'{key}: {value}'])
            
            cmd.append(url)
            
            #execute the curl command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20
            )
            
            if result.returncode != 0;
                raise Exception(f"curl failed: {result.stderr}")
                
            #split resonse int from content
            
            
            

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
