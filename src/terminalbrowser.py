from .Parser.HTMLParser import HTMLParser
from .Parser.HTMLParser import Node 
from .Parser.CSSParser import CSSParser
from .Parser.StyleResolver import StyleResolver
from .Views.TerminalRenderer import TerminalRenderer
from .Fetching.FetchURL import Fetcher

import unicodedata

def normalize_texts(node: Node):
    if node.tag == "_text" and node.text:
        node.text = unicodedata.normalize("NFC", node.text)
    for child in node.children:
        normalize_texts(child)

def browse(url: str):
	
    fetcher = Fetcher(mode="auto", prompt_for_dynamic=False)
    page = fetcher.fetch(url)

    print(f"\n[+] Fetched: {page.url}  (status={page.status_code})")
    if len(page.html) > 2000:
        print(f"[i] HTML size: {len(page.html)} chars\n")
        
    root = HTMLParser.parse_html(page.html)
    body_node = next((child for child in root.children if child.tag == "body"), root)
    dom_tree = body_node  

    css_rules = CSSParser.parse(page.css)

    StyleResolver.apply_styles(dom_tree, css_rules)
    
    normalize_texts(dom_tree)

    print("\n\n[+] Rendering page\n")
    renderer = TerminalRenderer()
    renderer.render(dom_tree)


if __name__ == "__main__":
    """
    import argparse
    parser = argparse.ArgumentParser(description="Terminal Browser")
    parser.add_argument("url", type=str, help="The URL to browse")
    args = parser.parse_args()
    """
    
    url = str(input("Enter URL: "))
    browse(url)
