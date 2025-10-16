import tinycss2
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class CSSParser:

    @staticmethod
    def parse(css_text: str) -> list[tuple[str,Dict[str,str]]]:
        rules : List[Tuple[str,Dict(str,str)]] = []

        #parse the whole CSS stylesheet
        stylesheet = tinycss2.parse_stylesheet(css_text,skip_whitespace=True,skip_comments=True)

        for rule in stylesheet:
            if rule.type != "qualified-rule":
                continue
            selector = tinycss2.serialize(rule.prelude).strip()
            decls = tinycss2.parse_declaration_list(rule.content)

            props: Dict[str,str] = {}

            for decl in decls:
                if decl.type == "declaration" and not decl.name.startswith("--"):
                    value = tinycss2.serialize(decl.value).strip()
                    props[decl.name.strip()] = value

            rules.append((selector, props))

        return rules

if __name__ == "__main__":
    css = """
    body { background: black; color: white; }
    h1.title { font-size: 24px; font-weight: bold }
    #main { padding: 10px; }
    """

    parsed = CSSParser.parse(css)
    for selector, props in parsed:
        print(selector, "=>", props)
                



