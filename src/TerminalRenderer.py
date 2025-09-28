#!/usr/bin/env python3
from multiprocessing import Array
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt
from rich.text import Text
from bs4 import BeautifulSoup, Comment


class PlaceholderPrompt(Prompt):
    def __init__(self, *args, **kwargs):
        self.placeholder = kwargs.pop("placeholder", "")
        super().__init__(*args, **kwargs)

    def process_input(self, value):
        return value or self.placeholder


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
        tag = str(element.name).lower()
        #        print(f"Debug rendering tag: {tag} type{type(tag)}")

        # handle different HTML tags
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.render_heading(element, indent, tag)
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
        elif tag in ["input", "textarea"]:
            self.render_input(element)
        else:
            # For unknown tags, just render children
            for child in element.children:
                self.render_element(child)

    # TODO: fix ts

    def render_input(self, element):
        """Render a text representation of an input box."""
        input_type = element.get("type", "text")
        name = element.get("name", "input")
        placeholder = element.get("placeholder", "")

        # Visualize the input box using rich
        content = Text(f"[{name}] ", style="bold yellow")
        content.append(f"({input_type}) ")

        if placeholder:
            content.append(f"- {placeholder} ")

        # Simulate user input via prompt
        user_input = PlaceholderPrompt.ask(f"{content}")
        self.output.append(f"{content}: {user_input}")

    def render_page(self, soup, title=""):
        self.output = []

        if title:
            self.console.print(Panel(title, style="bold blue", box=box.DOUBLE))

        body = soup.find("body") or soup
        self.remove_metadata(body)
        self.render_element(body)

        for line in self.output:
            self.console.print(line)

    def remove_metadata(self, soup) -> None:
        for element in soup(["script", "style", "link", "meta", "noscript"]):
            element.decompose()

        for comment in soup(text=lambda text: isinstance(text, Comment)):
            comment.extract()
        body = soup.find("body") or soup
        for element in body.children:
            self.render_element(element)

        for line in self.output:
            self.console.print(line)

    def render_heading(self, element, indent, tag):
        #        print(f"Debug tag: {tag} type{type(tag)}")
        text = element.get_text().strip()

        if not text:
            return

        try:
            level = int(tag[1])
        except (IndexError, TypeError) as e:
            print(f"Error determining heading level: {e} tag={tag}")
            return

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

    def render_div(self, element, indent):
        for child in element.children:
            self.render_element(child, indent)

    def render_header(self, element, indent):
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + f"#{text}")

    def render_nav(self, element, indent):
        text = element.get_text().strip()
        if text:
            self.output.append(" " * indent + f"##{text}")
