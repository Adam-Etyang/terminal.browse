#!/usr/bin/env python3
from _typeshed import ProfileFunction
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urlparse,urljoin
import logging
from typing import Optional, Tuple,List
import re

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# logging info for debugging
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fetcher')



#container for fetched page content and associeated resources
@dataclass
class PageResource:
    html:str
    css:str
    url:str
    title:Optional[str] = None
    statust_code :int = 200
    is_dynamic_render : bool = False

    @property
    def base_url(self) -> str:
        parsed = urlparse(self.url)
        return f"{parsed.scheme}: //{parsed.netloc}"

    def __str__(self) -> str :
        return f"Pageresource(url = {self.url}, title={self.title}, dynamic={self.is_dynamic_render})"


class HeuristicsEngine:

   @staticmethod
   def looks_dynamic(html:str)  -> bool:
       soup = BeautifulSoup(html, "html-parser")
       body = soup.body

       if not body:
           return True
       text = body.get_text(strip=True)
       text_len = len(text)

       if text_len < 100:
           script_tags = soup.find_all('script')
           if script_tags:
               logger.info("script tags found but minimal")
               return True

       framework_indicators = [
            soup.find(id="root"),
            soup.find(id="app")  ,
            soup.find(id="__next"),
            soup.find(attrs={"ng-app":True}),
            soup.find(attrs={f"data-reactroot":True}),
        ]
       if any(framework_indicators):
           logger.info("Page may be dynamic: SPA markers included")
           return True
           
       meaningful_elements = soup.find_all(["h1","h2", "p", "article", "main", "section"])
       if len(meaningful_elements) < 3 and text_len <500:
           logger.info("Page may be dynamic: minimal content")
           return True
           
       noscript_tags = soup.find_all("noscript")
       for tag in noscript_tags:
           noscript_text = tag.get_text(strip=True).lower()
           if any(word in noscript_text for word in ["javascript", "enable", "browser", "required"]):
               logger.info("Page looks dynamic: found noscript tag with JS requirement warning")
               return True
               
       return False

        
class StaticFetcher:
    @staticmethod
    
    def fetch(url:str)-> Tuple[str,int]:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text, response.status_code
        except Exception as e:
            logger.error(f"Error fetching static content: {e}")
            raise 
            
    @staticmethod  
    def fetch_css(base_url:str,css_url:str) -> str:
        try:
            full_url = urljoin(base_url, css_url)
            response = requests.get(full_url, timeout=10)
            response.raise_for_status()
            css_text = response.text
            
            css_text = re.sub(r'url\([\'"]?(?!http)([^\'")]+)[\'"]?\)', 
                                         lambda m: f'url({urljoin(full_url, m.group(1))})', 
                                         css_text)
            return css_text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching CSS content: {e}")
            return ""
            
    @staticmethod
    def fetch_with_css(cls,url:str)->PageResource:
        pass
        
        
        





#main fetcher that combines static and dynamic apporaches
class Fetcher:
    def __init__(self) -> None:
        pass
    def Fetch_static(self,url):
        pass
    def fetch_dynamic(self,url):
        pass

class Heuristic:
    def __init__(self) -> None:
        pass
    def looks_dynamic(self):
        pass
