# browser.py
from html_parser import HTMLParser
from TerminalRenderer import TerminalRenderer


class TerminalBrowser:
    def __init__(self, width=80):
        self.parser = HTMLParser()
        self.renderer = TerminalRenderer(width)
        self.current_url = None
        self.history = []

    def navigate(self, url):
        """Navigate to URL and render page"""
        try:
            print(f"Loading {url}...")
            soup = self.parser.parse_url(url)
            title = self.parser.get_title()

            self.current_url = url
            self.history.append(url)

            self.renderer.render_page(soup, title)

        except Exception as e:
            print(f"Error loading page: {e}")

    def render_html_string(self, html_string, title="Local HTML"):
        """Render HTML from string"""
        try:
            soup = self.parser.parse_string(html_string)
            self.renderer.render_page(soup, title)
        except Exception as e:
            print(f"Error rendering HTML: {e}")


# Example usage
if __name__ == "__main__":
    browser = TerminalBrowser(width=100)

    # Test with sample HTML
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Welcome to My Terminal Browser</h1>
        <p>This is a <strong>test</strong> paragraph with <em>some formatting</em>.</p>
        
        <h2>Features</h2>
        <ul>
            <li>Basic HTML parsing</li>
            <li>Text rendering</li>
            <li>Link detection</li>
        </ul>
        
        <p>Visit <a href="https://example.com">Example.com</a> for more info.</p>
        
        <pre><code>
def hello_world():
    print("Hello from terminal browser!")
        </code></pre>
    </body>
    </html>
    """

    print("=== Testing with sample HTML ===")
    browser.render_html_string(sample_html)

    print("\n" + "=" * 50 + "\n")

    # Test with real URL (uncomment to test)
    browser.navigate("https://httpbin.org/html")
