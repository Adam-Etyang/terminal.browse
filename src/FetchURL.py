#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urlparse,urljoin
import logging
from typing import Optional, Tuple,List
import re

"""
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
"""


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

        
