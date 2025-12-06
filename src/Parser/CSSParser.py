import tinycss2
from typing import List, Dict, Tuple, Union
from dataclasses import dataclass


@dataclass
class CSSParser:

    @staticmethod
    def parse(css_input: Union[str, dict]) -> list[tuple[str, Dict[str, str]]]:
        """
        Parse CSS from either a string or dict format.
        
        Dict format:
        {
            "inline": [css_string, ...],
            "external": {url: css_string, ...},
            "attribute": [{"selector": str, "style": str}, ...]
        }
        """
        rules: List[Tuple[str, Dict[str, str]]] = []
        
        # Handle dict format
        if isinstance(css_input, dict):
            # Parse inline styles
            for css_text in css_input.get("inline", []):
                rules.extend(CSSParser._parse_css_string(css_text))
            
            # Parse external stylesheets
            for css_text in css_input.get("external", {}).values():
                rules.extend(CSSParser._parse_css_string(css_text))
            
            # Parse attribute styles
            for attr in css_input.get("attribute", []):
                selector = attr.get("selector", "")
                style = attr.get("style", "")
                props = CSSParser._parse_style_string(style)
                if selector and props:
                    rules.append((selector, props))
        else:
            # Handle string format (backward compatibility)
            rules = CSSParser._parse_css_string(css_input)
        
        return rules
    
    @staticmethod
    def _parse_css_string(css_text: str) -> list[tuple[str, Dict[str, str]]]:
        """Parse a CSS string and return list of (selector, properties) tuples."""
        rules: List[Tuple[str, Dict[str, str]]] = []
        
        # Parse the whole CSS stylesheet
        stylesheet = tinycss2.parse_stylesheet(css_text, skip_whitespace=True, skip_comments=True)

        for rule in stylesheet:
            if rule.type != "qualified-rule":
                continue
            selector = tinycss2.serialize(rule.prelude).strip()
            decls = tinycss2.parse_declaration_list(rule.content)

            props: Dict[str, str] = {}

            for decl in decls:
                if decl.type == "declaration" and not decl.name.startswith("--"):
                    value = tinycss2.serialize(decl.value).strip()
                    props[decl.name.strip()] = value

            rules.append((selector, props))

        return rules
    
    @staticmethod
    def _parse_style_string(style: str) -> Dict[str, str]:
        """Parse inline style attribute string into properties dict."""
        props: Dict[str, str] = {}
        
        for declaration in style.split(';'):
            declaration = declaration.strip()
            if not declaration:
                continue
            
            if ':' in declaration:
                key, value = declaration.split(':', 1)
                props[key.strip()] = value.strip()
        
        return props



