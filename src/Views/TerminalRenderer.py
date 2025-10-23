from typing import Optional

import unicodedata

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.style import Style
from rich.syntax import Syntax
from rich.markdown import Markdown

from ..Parser.HTMLParser import Node


class TerminalRenderer:

    DEFAULT_STYLES = {
        "h1": Style(bold=True),
        "h2": Style(bold=True),
        "b": Style(bold=True),
        "strong": Style(bold=True),
        "i": Style(italic=True),
        "em": Style(italic=True),
        "u": Style(underline=True),
        "a": Style(color="cyan", underline=True),
        "code": Style(bgcolor="grey15"),
        "pre": Style(bgcolor="grey15"),
    }

    BLOCK_TAGS = {"html", "body", "div", "p", "section", "article", "header", "footer"}
    INLINE_TAGS = {"span", "a", "b", "strong", "i", "em", "u"}
    HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
    LIST_TAGS = {"ul", "ol", "li"}
    TEXT_TAG = "_text"
    

    def __init__(self, force_color: bool = True):
        self.console = Console(force_terminal=force_color, color_system="truecolor")
        self.list_depth = 0
    
    
    # ---------- Core renderer entry ----------
    def render(self, node: Node, indent: int = 0, parent_style: Optional[Style] = None):
        tag = node.tag.lower() if node.tag else "_text" 
        if node.tag  in ["head", "script", "style"]:
            return

        is_block = tag in self.BLOCK_TAGS or tag in self.HEADING_TAGS or tag in self.LIST_TAGS or tag == "pre"

        if tag in self.HEADING_TAGS:
            self.render_heading(node, tag, indent, parent_style)
        elif tag in self.BLOCK_TAGS:
            self.render_block(node, indent, parent_style)
        elif tag in self.LIST_TAGS:
            self.render_list(node, tag, indent, parent_style)
        elif tag in self.INLINE_TAGS:
            self.render_inline(node, indent, parent_style)
        elif tag == "pre" or tag == "code":
            self.render_code(node, indent)
        elif tag == self.TEXT_TAG:
            self.render_text(node, indent, parent_style)
        else:
            # default fallback
            self.render_fallback(node, indent, parent_style)
        
        if is_block:
            self.console.print()

    # ---------- style conversion ----------
    def to_rich_style(self, node: Node) -> Optional[Style]:
        """Convert node.computed_style to Rich style."""
        default_style = self.DEFAULT_STYLES.get(node.tag, Style())
        
        computed = node.computed_style or {}

        color = computed.get("color")
        if color:
            if color.startswith("#") and len(color) == 4:
                color = f"#{color[1]*2}{color[2]*2}{color[3]*2}"
            elif color.startswith("var("):
                color = None # Ignore CSS variables
            elif color == "inherit":
                color = None # Handled by parent_style
            elif color == "transparent":
                color = None # Ignore transparent color
            elif color.startswith("rgba("):
                # Convert rgba(R, G, B, A) to rgb(R, G, B)
                try:
                    parts = color[5:-1].split(',') # "R, G, B, A"
                    r, g, b = int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip())
                    color = f"rgb({r},{g},{b})"
                except (ValueError, IndexError):
                    color = None # Invalid rgba format
        
        bold = computed.get("font-weight") in {"bold", "700", "900"}
        italic = computed.get("font-style") in {"italic"}
        underline = computed.get("text-decoration") in {"underline", "underline solid"}

        computed_style = Style(color=color, bold=bold, italic=italic, underline=underline)

        return default_style + computed_style

    # ---------- renderers for various tag types ----------
    def render_heading(self, node: Node, tag: str, indent: int, parent_style: Optional[Style] = None):
        level = int(tag[1]) if len(tag) > 1 and tag[1].isdigit() else 1
        size_weight = max(7 - level, 1)  # larger number = smaller heading
        style = self.to_rich_style(node)
        if parent_style:
            style = parent_style + style
        text_content = self.extract_text(node)

        t = Text(text_content.upper(), style=style)
        self.console.print(t, style=Style(bold=True))

    def render_block(self, node: Node, indent: int, parent_style: Optional[Style] = None):
        style = self.to_rich_style(node)
        if parent_style:
            style = parent_style + style
        for child in node.children:
            self.render(child, indent + 1, parent_style=style)

    def render_list(self, node: Node, tag: str, indent: int, parent_style: Optional[Style] = None):
        style = self.to_rich_style(node)
        if parent_style:
            style = parent_style + style
        # handle <ul>, <ol>, <li>
        if tag in {"ul", "ol"}:
            self.list_depth += 1
            for child in node.children:
                self.render(child, indent + 1, parent_style=style)
            self.list_depth -= 1
        elif tag == "li":
            bullet = "*" if self.list_depth <= 1 else "-" * (self.list_depth -1)
            self.console.print("  " * indent + f"[bold]{bullet}[/bold] ", end="")
            for child in node.children:
                self.render(child, indent, parent_style=style)

    def render_inline(self, node: Node, indent: int, parent_style: Optional[Style] = None):
        style = self.to_rich_style(node)
        if parent_style:
            style = parent_style + style
        for child in node.children:
            self.render(child, indent, parent_style=style)

    def render_text(self, node: Node, indent: int, parent_style: Optional[Style] = None):
        style = self.to_rich_style(node)
        if parent_style:
            style = parent_style + style
        self.console.print(Text(node.text, style=style), end="")
    
    def render_code(self, node: Node, indent: int):
        """Render <pre><code> blocks or inline code."""
        code_text = self.extract_text(node)
        language = "text"
    
        # Detect language from class attribute (class="language-python")
        class_attr = node.attrs.get("class") if hasattr(node, "attrs") else None
        if class_attr:
            if isinstance(class_attr, list):
                for c in class_attr:
                    if c.startswith("language-"):
                        language = c.split("language-")[1]
            elif isinstance(class_attr, str) and class_attr.startswith("language-"):
                language = class_attr.split("language-")[1]
    
        # Inline <code> inside paragraph
        if node.tag == "code" and (node.parent and node.parent.tag != "pre"):
            highlighted = Syntax(code_text, language, theme="monokai", background_color="default", word_wrap=True)
            self.console.print(highlighted, end="")
            return
    
        # Block <pre><code>
        self.console.print()  # line break before block
        syntax = Syntax(code_text.strip("\n"), language, theme="monokai", background_color="default", word_wrap=True)
        panel = Panel(syntax, border_style="cyan", expand=False)
        self.console.print(panel)
        self.console.print()
	    

    def render_fallback(self, node: Node, indent: int, parent_style: Optional[Style] = None):
        # unknown tag: render its children normally
        for child in node.children:
            self.render(child, indent, parent_style=parent_style)

    # ---------- utils ----------
    def extract_text(self, node: Node) -> str:
        """Flatten all _text children recursively."""
        if node.tag == "_text":
            return node.text or ""
        combined = []
        for child in node.children:
            combined.append(self.extract_text(child))
        return "".join(combined)