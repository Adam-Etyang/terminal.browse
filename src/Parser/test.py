from HTMLParser import HTMLParser
from CSSParser import CSSParser
from StyleResolver import StyleResolver

html = """
<body>
  <h1 class="title">Welcome</h1>
  <p id="greeting" class="intro">Hello there!</p>
</body>
"""

css = """
h1 { color: red; }
.title { font-weight: bold; }
#greeting { font-style: italic; }
"""

dom = HTMLParser.parse_html(html)
rules = CSSParser.parse(css)

StyleResolver.apply_styles(dom, rules)

def print_tree(node, depth=0):
    indent = "  " * depth
    print(f"{indent}{node.tag} -> {node.computed_style} {node.attrs}")
    for child in node.children:
        print_tree(child, depth + 1)

print_tree(dom)
