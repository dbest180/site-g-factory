#!/usr/bin/python3
"""
Static Site Generator
- Reads Markdown files from content/
- Renders them using templates/layout.html
- Injects generated navigation list into {{nav}}
- Outputs HTML to dist/
"""

import os
import markdown
import shutil
from pathlib import Path

# Configuration
CONTENT_DIR = "content"
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "docs"
LAYOUT_FILE = "layout.html"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read the layout template
with open(os.path.join(TEMPLATE_DIR, LAYOUT_FILE), "r", encoding="utf-8") as f:
    layout_template = f.read()

# Read all markdown files
markdown_files = list(Path(CONTENT_DIR).glob("*.md"))
pages = []

# First pass: gather page data for navigation
for md_file in markdown_files:
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    # Extract title from first # heading, or use filename
    lines = content.splitlines()
    title = None
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        title = md_file.stem.replace("-", " ").title()
    pages.append({
        "filename": md_file.name,
        "basename": md_file.stem,
        "title": title
    })

# Sort pages alphabetically by title (optional)
pages.sort(key=lambda p: p["title"])

# Build the navigation HTML (<ul> list)
nav_items = []
for page in pages:
    # Link to the generated HTML file (same name, .html)
    link = f"{page['basename']}.html"
    nav_items.append(f'<li><a href="{link}">{page["title"]}</a></li>')
nav_html = "<ul>\n" + "\n".join(nav_items) + "\n</ul>"
nav_html = '<ul>\n<li><a href="index.html">🏠 Home</a></li>\n' + "\n".join(nav_items) + "\n</ul>"

# Process each markdown file
for md_file in markdown_files:
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['extra'])

    # Replace placeholders in layout
    page_html = layout_template.replace("{{nav}}", nav_html)
    page_html = page_html.replace("{{content}}", html_content)
    page_html = page_html.replace("{{title}}", title)

    # Output file
    out_filename = f"{md_file.stem}.html"
    out_path = os.path.join(OUTPUT_DIR, out_filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page_html)

print(f"✅ Generated {len(markdown_files)} page(s) in {OUTPUT_DIR}/")

# Build index.html
index_items = "\n".join(
    f'<li><a href="{p["basename"]}.html">{p["title"]}</a></li>'
    for p in pages
)

index_html = layout_template.replace("{{nav}}", nav_html).replace("{{content}}", f"""
<h2>Stories</h2>
<ul class="page-list">
{index_items}
</ul>
""")

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("✅ Generated index.html")

shutil.copy("templates/style.css", os.path.join(OUTPUT_DIR, "style.css"))
