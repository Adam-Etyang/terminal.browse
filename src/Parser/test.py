from HTMLParser import HTMLParser
from StyleResolver import StyleResolver

html = """
<body>
  <p id="intro" class="info">Hello world!</p>
</body>
"""

css_rules = [
    ("p", {"color": "black", "font-weight": "normal"}),          # tag
    (".info", {"color": "green"}),                               # class
    ("#intro", {"color": "red"}),                                # id
]

root = HTMLParser.parse_html(html)
StyleResolver.apply_styles(root, css_rules)

# Inspect the <p> node
p_tag = root.children[0].children[0]   # body -> p
print("Final styles:", p_tag.computed_style)