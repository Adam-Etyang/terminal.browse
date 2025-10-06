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

        
