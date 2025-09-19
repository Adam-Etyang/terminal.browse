"""A module for rendering HTML in the terminal."""

from rich.console import Console
from rich.panel import Panel
from rich.box import DOUBLE


class TerminalRenderer:
    """A class for rendering HTML in the terminal."""

    def __init__(self, width=80):
        """Initialize the TerminalRenderer."""
        self.console = Console(width=width)
        self.width = width
        self.output = []
        self.tag_renderers = {
            "h1": self.render_heading,
            "h2": self.render_heading,
            "h3": self.render_heading,
            "h4": self.render_heading,
            "h5": self.render_heading,
            "h6": self.render_heading,
            "p": self.render_paragraph,
            "a": self.render_link,
            "ul": self.render_list,
            "ol": self.render_list,
            "li": self.render_list_item,
            "pre": self.render_preformatted,
            "code": self.render_code,
            "strong": self.render_bold,
            "b": self.render_bold,
            "em": self.render_italic,
            "i": self.render_italic,
            "br": lambda element, indent: self.output.append(""),
            "hr": lambda element, indent: self.output.append("─" * self.width),
        }

    def render_element(self, element, indent=0):
        """Recursively render an HTML element."""
        if element.name is None:
            text = str(element).strip()
            if text:
                self.output.append(" " * indent + text)
            return

        tag = element.name.lower()
        renderer = self.tag_renderers.get(tag)

        if renderer:
            renderer(element, indent)
        else:
            # For unknown tags, just render children
            for child in element.children:
                self.render_element(child, indent)

    def render_page(self, soup, title=""):
        """Render a full HTML page."""
        self.output = []

        if title:
            self.console.print(Panel(title, style="bold blue", box=DOUBLE))

        body = soup.find("body") or soup

        for element in body.children:
            self.render_element(element)

        for line in self.output:
            self.console.print(line)

    def render_heading(self, element, indent):
        """Render a heading element."""
        text = element.get_text().strip()
        if not text:
            return

        level = int(element.name[1])

        if level == 1:
            self.output.append(" ")
            self.output.append("=" * len(text))
            self.output.append(text.upper())
            self.output.append("═" * len(text))
        elif level == 2:
            self.output.append("")
            self.output.append(text.upper())
            self.output.append("─" * len(text))
        else:
            self.output.append("")
            self.output.append(f"{'#' * level} {text}")
            self.output.append("")

    def render_paragraph(self, element, indent):
        """Render a paragraph with word wrapping."""
        text = element.get_text().strip()
        if text:
            # Simple word wrapping
            words = text.split()
            line = " " * indent
            for word in words:
                if len(line) + len(word) + 1 > self.width:
                    self.output.append(line.rstrip())
                    line = " " * indent + word
                else:
                    line += (" " + word) if line.strip() else word
            if line.strip():
                self.output.append(line)
            self.output.append("")

    def render_list(self, element, indent):
        """Render an ordered or unordered list."""
        self.output.append("")
        list_type = element.name.lower()
        for i, list_item in enumerate(element.find_all("li", recursive=False)):
            if list_type == "ol":
                marker = f"{i + 1}. "
            else:
                marker = "• "

            li_text = list_item.get_text().strip()
            if li_text:
                self.output.append(" " * indent + marker + li_text)
        self.output.append("")

    def render_list_item(self, element, indent):
        """Render a list item."""
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + "• " + text)

    def render_link(self, element, indent):
        """Render a link."""
        text = element.get_text().strip()
        href = element.get("href", "").strip()
        if text:
            if href:
                self.output.append(" " * indent + f"{text} ({href})")
            else:
                self.output.append(text)

    def render_preformatted(self, element, indent):
        """Render preformatted text."""
        text = element.get_text()
        self.output.append("")
        for line in text.splitlines():
            self.output.append(" " * indent + line)
        self.output.append("")

    def render_code(self, element, indent):
        """Render a code block."""
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + f"`{text}`")

    def render_bold(self, element, indent):
        """Render bold text."""
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + f"**{text}**")

    def render_italic(self, element, indent):
        """Render italic text."""
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + f"*{text}*")
