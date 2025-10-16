from HTMLParser import HTMLParser
from StyleResolver import StyleResolver

html = """
<body>
  <p id="intro" class="note" style="color: blue; font-style: italic;">
    Hello World
  </p>
</body>
"""

css_rules = [
    ("p", {"color": "black", "font-weight": "normal"}),  # base
    (".note", {"color": "green"}),  # class
    ("#intro", {"color": "red"}),  # id
]

root = HTMLParser.parse_html(html)
StyleResolver.apply_styles(root, css_rules)

# print the <p> node style
p_node = root.children[0].children[0]
print("Final computed_style:", p_node.computed_style)