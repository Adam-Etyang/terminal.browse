from .Parser.HTMLParser import HTMLParser
from .Parser.CSSParser import CSSParser
from .Parser.StyleResolver import StyleResolver
from .Views.TerminalRenderer import TerminalRenderer
from .Fetching.FetchURL import Fetcher


def browse(url: str):
    # 1️⃣ Fetch HTML + CSS
    fetcher = Fetcher(mode="auto", prompt_for_dynamic=False)
    page = fetcher.fetch(url)

    print(f"\n[+] Fetched: {page.url}  (status={page.status_code})")
    if len(page.html) > 2000:
        print(f"[i] HTML size: {len(page.html)} chars\n")

    # 2️⃣ Parse HTML and CSS
    dom_tree = HTMLParser.parse_html(page.html)
    css_rules = CSSParser.parse(page.css)

    # 3️⃣ Apply styles
    StyleResolver.apply_styles(dom_tree, css_rules)

    # 4️⃣ Render the page to terminal
    print("\n\n[+] Rendering page\n")
    renderer = TerminalRenderer()
    renderer.render(dom_tree)


if __name__ == "__main__":
    browse("https://docs.python.org/3/")