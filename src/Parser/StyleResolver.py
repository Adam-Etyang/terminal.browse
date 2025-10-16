from typing import Dict, List, Tuple
from HTMLParser import Node  # import your existing Node class


class StyleResolver:
    """Responsible for applying parsed CSS rules to a DOM tree of Nodes."""

    @staticmethod
    def match_selector(node: Node, selector: str) -> bool:
        """Return True if the CSS selector matches the given node."""
        selector = selector.strip()

        # ID selector (#id)
        if selector.startswith("#"):
            return node.attrs.get("id") == selector[1:]

        # Class selector (.class)
        elif selector.startswith("."):
            classes = node.attrs.get("class", [])
            # normalize class attr (it may be string or list)
            if isinstance(classes, str):
                classes = [classes]
            return selector[1:] in classes

        # Tag selector (e.g. h1, div, p)
        else:
            return node.tag == selector

    @staticmethod
    def apply_styles(node: Node, css_rules: List[Tuple[str, Dict[str, str]]]) -> None:
        """Recursively apply all matching CSS rules to the Node tree."""
        for selector, props in css_rules:
            selectors = [s.strip() for s in selector.split(",") if s.strip()]
            for sel in selectors: 
                if StyleResolver.match_selector(node, sel):
                    node.computed_style.update(props)

        for child in node.children:
            StyleResolver.apply_styles(child, css_rules)