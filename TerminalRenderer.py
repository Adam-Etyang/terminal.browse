import re
import rich


class TerminalRenderer:
    def __init__(self, width=80):
        self.console = Console(width=width)
        self.width = width
        self.output = []

        # Recursively render HTML elements

    def render_element(self, element, indent=0):
        if element.name is None:
            text = str(element).strip()
            if text:
                self.output.append(" " * indent + text)
            return
        tag = element.name.lower()

        # handle different HTML tags
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.render_heading(element, indent, indent)
        elif tag == "p":
            self.render_paragraph(element, indent)
        elif tag == "a":
            self.render_link(element, indent)
        elif tag in ["ul", "ol"]:
            self.render_list(element, tag, indent)
        elif tag == "li":
            self.render_list_item(element, indent)
        elif tag == "pre":
            self.render_preformatted(element, indent)
        elif tag == "code":
            self.render_code(element, indent)
        elif tag in ["strong", "b"]:
            self.render_bold(element, indent)
        elif tag in ["em", "i"]:
            self.render_italic(element, indent)
        elif tag == "br":
            self.output.append("")
        elif tag == "hr":
            self.output.append("─" * self.width)
        else:
            # For unknown tags, just render children
            for child in element.children:
                self.render_element(child, indent)

    # TODO: create rendering functions for headings, paragraphs, links, lists,code blocks, blockquotes
    def render_page(self, soup, title=""):
        self.output = []

        if title:
            self.console.print(Panel(title, style="bold blue", box=box.DOUBLE))

        body = soup.find("body") or soup

        for element in body.children:
            self.render_element(element)

        for line in self.output:
            self.console.print(line)

    def render_heading(self, element, indent, tag):
        text = element.get_text().strip()

        if not text:
            return

        level = int(tag[1])

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
        """Render paragraph with word wrapping"""
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

    def render_list(self, element, list_type, indent):
        self.output.append("")
        for i, li in enumerate(element.find_all("li", recursive=False)):
            if list_type == "ol":
                marker = f"{i + 1}. "
            else:
                marker = "• "

            li_text = li.get_text().strip()
            if li_text:
                self.output.append(" " * indent + marker + li_text)
        self.output.append("")

    def render_list_item(self, element, indent):
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + "• " + text)

    def render_link(self, element, indent):
        text = element.get_text().strip()
        href = element.get("href", "").strip()
        if text:
            if href:
                self.output.append(" " * indent + f"{text} ({href})")
            else:
                self.output.append(text)

    def render_preformatted(self, element, indent):
        text = element.get_text()
        self.output.append("")
        for line in text.splitlines():
            self.output.append(" " * indent + line)
        self.output.append("")

    def render_code(self, element, indent):
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + f"`{text}`")

    def render_bold(self, element, indent):
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + f"**{text}**")

    def render_italic(self, element, indent):
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + f"*{text}*")
