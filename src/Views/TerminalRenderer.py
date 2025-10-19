from rich.console import Console
from rich.style import Style
from rich.text import Text

from ..Parser.HTMLParser import HTMLParser
from ..Parser.HTMLParser import Node

from typing import Optional


class TerminalRenderer:
	
	# default styles
	TAG_STYLE_MAP = {
  "h1": Style(bold=True, underline=True),
  "h2": Style(bold=True),
  "strong": Style(bold=True),
  "b": Style(bold=True),
  "em": Style(italic=True),
  "i": Style(italic=True),
	}
	
	def __init__(self):
		self.console = Console(color_system="truecolor")
	
	def render(self, node:Node, indent:int = 0, parent_style: Optional[Style] = None) -> None:
		"""Recursively render a node tree to the terminal"""
		indent_str = " "*indent
		style = self.resolve_rich_style(node)

		if parent_style:
			style = parent_style + style

		if node.tag == "_text":
			txt = Text(node.text,style=style)
			self.console.print(indent_str,end="")
			self.console.print(txt, end="")
			return
	   	# Pre & Post block linebreaks for block-level elements
		if node.tag in ["p", "div", "body"]:
			self.console.print()
		
		if node.text:
			txt = Text(node.text, style=style)
			self.console.print(indent_str, end="")
			self.console.print(txt, end="")
		
		for child in node.children:
			self.render(child, indent+1, parent_style=style)
		
		if node.tag in ["p", "div", "body"]:
			self.console.print()
		
		
	def resolve_rich_style(self, node:Node)->Optional[Style]:
		"""Convert computed style into rich style object"""
		computed = node.computed_style
		tag_style = self.TAG_STYLE_MAP.get(node.tag) # Tag fall back to use defaults
		
		color = computed.get("color")
		bold = self.is_true(computed.get("font-weight"),"bold")
		italic = self.is_true(computed.get("font-style"),"italic")
	
		return Style(bold=bold or (tag_style.bold if tag_style else False),
                italic=italic or (tag_style.italic if tag_style else False),
                underline=(tag_style.underline if tag_style else False),
                color=color)
	@staticmethod
	def is_true(prop_value,ref) -> bool:
		"""Helper function for interpretung specific CSS styles"""
		if prop_value is None:
			return False
		return str(prop_value).lower() == ref
		
		
		