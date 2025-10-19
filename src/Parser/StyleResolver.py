from typing import Dict, List, Tuple
from .HTMLParser import Node  


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
    def parse_inline_style(style_str: str) -> Dict[str, str]:
        """Convert inline style string like 'color:red; font-size:12px' into a dict."""
        styles: Dict[str, str] = {}
        declarations = [d.strip() for d in style_str.split(";") if d.strip()]
        for decl in declarations:
            if ":" in decl:
                prop, val = decl.split(":", 1)
                styles[prop.strip()] = val.strip()
        return styles
        
    @staticmethod
    def specificity_score(selector: str) -> int:
        selector = selector.strip()
        ids = selector.count("#")
        classes = selector.count(".")
        
        tags = 1 if selector and not selector.startswith(("#",".")) else 0
        return ids * 100 + classes * 10 + tags
        
    @staticmethod
    def apply_styles(node: Node, css_rules: List[Tuple[str, Dict[str, str]]]) -> None:
        """Recursively apply CSS rules with specificity and inline style override."""
        applied_specificity: Dict[str, int] = {}
    
        #Apply regular CSS rules (with specificity)
        for selector, props in css_rules:
            selectors = [s.strip() for s in selector.split(",") if s.strip()]
            for sel in selectors:
                if StyleResolver.match_selector(node, sel):
                    score = StyleResolver.specificity_score(sel)
                    for prop, value in props.items():
                        current = applied_specificity.get(prop)
                        if current is None or score >= current:
                            node.computed_style[prop] = value
                            applied_specificity[prop] = score
    
        # Handle inline styles (highest priority)
        if "style" in node.attrs:
            inline_styles = StyleResolver.parse_inline_style(node.attrs["style"])
            for prop, value in inline_styles.items():
                node.computed_style[prop] = value
                applied_specificity[prop] = 1000  # force to top priority
    
        # Recurse for children
        for child in node.children:
            StyleResolver.apply_styles(child, css_rules)