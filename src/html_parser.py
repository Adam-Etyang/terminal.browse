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
        self.last_repsonse = {}

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
            
            if result.returncode != 0:
                raise Exception(f"curl failed: {result.stderr}")
                
            #split resonse int from content
            lines = result.stdout.split('\n')
            response_info = lines[-1]
            html_content = '\n'.join(lines[:-1])
            
            #parse info
            try:
                self.last_repsonse = json.loads(response_info)
                http_code = int(self.last_repsonse.get('http_code',0))
                
                if http_code >=400:
                    raise Exception(f"HTTP{http_code} error")
            except json.JSONDecodeError:
                html_content = result.stdout
                self.last_repsonse = {'http_code': '200'}
            
            return html_content
            
        except subprocess.TimeoutExpired:
            raise Exception("Request timed out")
        except FileNotFoundError:
            raise Exception("curl not found. Please install curl.")
            
    def parse_url(self, url):
        """Fetch and parse HTML from URL using curl"""
        try:
            print(f"Fetching {url} with curl...")
            
            # Optional: Add browser-like headers
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            html_content,response_info = self.fetch_url(url, headers)
            self.base_url = url
            self.soup = BeautifulSoup(html_content, 'lxml')
            
            # Print response info
            print(f"HTTP {self.last_repsonse.get('http_code', 'Unknown')}")
            print(f"Content-Type: {self.last_repsonse.get('content_type', 'Unknown')}")
            
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
