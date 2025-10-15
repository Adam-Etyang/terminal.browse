"""
test_fetching.py

Unit tests for the Fetching Layer of the terminal browser.
Run with:  pytest -v  (or just python test_fetching.py)
"""

import os
import sys
import tempfile
import http.server
import socketserver
import threading
import textwrap
import pytest

# Import your fetching code

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from FetchURL import Fetcher, StaticFetcher, HeuristicsEngine, PageResource

# Use a random free port (localhost mini server for testing)
PORT = 0 # 0 means the OS will pick a random available port


class TestServer:
    """Utility to serve static HTML/CSS locally for fetch tests."""

    def __init__(self, html_content: str, css_content: str = None):
        self.tempdir = tempfile.TemporaryDirectory()
        self.html_path = os.path.join(self.tempdir.name, "index.html")
        self.css_path = os.path.join(self.tempdir.name, "style.css")
        self.port = PORT
        self.httpd = None
        self.thread = None

        # Write the files
        with open(self.html_path, "w") as f:
            f.write(html_content)
        if css_content:
            with open(self.css_path, "w") as f:
                f.write(css_content)

    def start(self):
        os.chdir(self.tempdir.name)
        handler = http.server.SimpleHTTPRequestHandler
        self.httpd = socketserver.TCPServer(("127.0.0.1", self.port), handler)
        self.port = self.httpd.server_address[1] # Update port with the one chosen by the OS
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
        if self.thread:
            self.thread.join(timeout=1)
        self.tempdir.cleanup()

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.port}/index.html"


# ---------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------

def test_static_html_and_css_fetch():
    """Should correctly fetch HTML and linked CSS"""
    html = textwrap.dedent("""\
        <html>
          <head><link rel="stylesheet" href="style.css"></head>
          <body>
            <h1>Hello world</h1>
          </body>
        </html>
    """)
    css = "h1 { color: red; }"

    server = TestServer(html, css)
    server.start()

    try:
        fetcher = Fetcher(mode="static", prompt_for_dynamic=False)
        result: PageResource = fetcher.fetch(server.base_url)

        assert "<h1>Hello world</h1>" in result.html
        assert "color: red" in result.css
        assert result.status_code == 200
        assert not result.is_dynamic_render
    finally:
        server.stop()


def test_fetch_css_resolves_relative_urls():
    """Should correctly make relative URLs absolute inside CSS"""
    html = textwrap.dedent("""\
        <html><head><link rel="stylesheet" href="style.css"></head></html>
    """)
    css = "body { background: url('images/bg.png'); }"

    server = TestServer(html, css)
    os.makedirs(os.path.join(server.tempdir.name, "images"), exist_ok=True)
    with open(os.path.join(server.tempdir.name, "images", "bg.png"), "wb") as f:
        f.write(b"fakeimage")

    server.start()

    try:
        res = StaticFetcher.fetch_with_css(server.base_url)
        # URLs in CSS should be converted to absolute
        assert "http://127.0.0.1" in res.css
    finally:
        server.stop()


def test_heuristics_detects_dynamic_html():
    """Should flag modern SPA-like HTML as dynamic"""
    dynamic_like_html = """
        <html><body>
            <div id="root"></div>
            <script src="bundle.js"></script>
        </body></html>
    """
    assert HeuristicsEngine.looks_dynamic(dynamic_like_html)


def test_heuristics_accepts_static_html():
    """Should classify normal HTML as static"""
    html = "<html><body><h1>Blog Post</h1><p>Hello</p></body></html>"
    assert not HeuristicsEngine.looks_dynamic(html)


@pytest.mark.skipif(
    not hasattr(__import__("FetchURL"), "DynamicFetcher")
    or not __import__("FetchURL").DynamicFetcher.is_available(),
    reason="Playwright not installed"
)
def test_dynamic_fetch(monkeypatch):
    """Only runs if Playwright available"""
    fetcher = Fetcher(mode="dynamic")
    # You can replace this with a small test site that uses JS, like a React demo
    result = fetcher.fetch("https://httpbin.org/html")
    assert "<html" in result.html.lower()
    assert isinstance(result.css, str)
    assert result.is_dynamic_render


def test_fetch_error_handling(monkeypatch):
    """Should return error page gracefully when request fails"""

    def mock_request_fail(*args, **kwargs):
        raise Exception("Simulated network fail")

    monkeypatch.setattr(StaticFetcher, "fetch_with_css", lambda url: (_ for _ in ()).throw(Exception("Boom!")))

    fetcher = Fetcher(mode="static")
    res = fetcher.fetch("https://nonexistent.site")
    assert "Error fetching" in res.html
    assert res.status_code == 500