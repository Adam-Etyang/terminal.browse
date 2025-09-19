#!/usr/bin/env python3


import sys
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown


def render_markdown(file_path: str):
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")  # reads the markdown file content
    md = Markdown(text)  # parses markdown text to a rich markdown object

    console = Console()  # console object to handle terminal output
    console.print(md)  # prints the rendered markdown to the terminal


def render_html(file_path: str):
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:  # ensures a file path is provided
        print("Usage: python tbr.py <markdown_file>")
        sys.exit(1)

    render_markdown(sys.argv[1])  # runs the function with the provided file path
