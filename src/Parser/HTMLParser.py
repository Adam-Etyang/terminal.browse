from typing import Dict, List, Optional
from dataclasses import dataclass, field
from bs4 import BeautifulSoup, Tag, NavigableString


@dataclass
class Node:
    """Represents a node in the HTML tree."""
    tag: str
    attrs: Dict[str, str]
    text: str = ""
    children: List["Node"] = field(default_factory=list)
    computed_style: Dict[str, str] = field(default_factory=dict)
    parent: Optional["Node"] = field(default=None, repr=False)

    def __repr__(self) -> str:
        child_tags = [child.tag for child in self.children]
        return (f"Node(tag={self.tag}, attrs={self.attrs}, "
                f"text='{self.text[:30]}', children={child_tags}, "
                f"computed_style={self.computed_style})")


class HTMLParser:
    """Convert raw HTML into a tree of Node objects."""

    @staticmethod
    def bs4_to_node(element: Tag,parent:Optional[Node]=None) -> Node:
        """Recursively convert BeautifulSoup Tag into Node."""
        node = Node(tag=element.name or "text", attrs=element.attrs,parent=parent)

        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child)
                if text:
                    node.children.append(Node(tag="_text", text=text, attrs={},parent=node))
            elif isinstance(child, Tag):
                node.children.append(HTMLParser.bs4_to_node(child,node))
        return node

    @staticmethod
    def parse_html(html: str) -> Node:
        """Parse raw HTML into our Node tree."""
        soup = BeautifulSoup(html, "html.parser")
        root_elem = soup.find("html") or soup
        return HTMLParser.bs4_to_node(root_elem)
        
