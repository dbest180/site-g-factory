#!/usr/bin/python3
"""
Static Site Generator
- Reads Markdown files from content/
- Renders them using templates/layout.html
- Injects generated navigation list into {{nav}}
- Outputs HTML to docs/
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

    lines = content.splitlines()

    # Extract title from first # heading, or use filename
    title = None
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        title = md_file.stem.replace("-", " ").title()

    # Extract hero image if specified
    hero = None
    for line in lines:
        if line.startswith("hero:"):
            hero = line[5:].strip()
            break

    pages.append({
        "filename": md_file.name,
        "basename": md_file.stem,
        "title": title,
        "hero": hero
    })

# Sort pages alphabetically by title
pages.sort(key=lambda p: p["title"])

# Build the navigation HTML
nav_items = []
for page in pages:
    link = f"{page['basename']}.html"
    nav_items.append(f'<li><a href="{link}">{page["title"]}</a></li>')
nav_html = '<ul>\n<li><a href="index.html">🏠 Home</a></li>\n' + "\n".join(nav_items) + "\n</ul>"

# Process each markdown file
for md_file in markdown_files:
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['extra'])

    # Get this page's data
    page_data = next((p for p in pages if p["basename"] == md_file.stem), None)
    title = page_data["title"] if page_data else md_file.stem
    hero = page_data["hero"] if page_data else None

    # Build hero image HTML
    if hero:
        hero_html = f'<div class="page-hero"><img src="assets/images/{hero}" alt="{title}"></div>'
    else:
        hero_html = ''

    # Replace placeholders in layout
    page_html = layout_template.replace("{{nav}}", nav_html)
    page_html = page_html.replace("{{hero}}", hero_html)
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

index_html = layout_template.replace("{{nav}}", nav_html)
index_html = index_html.replace("{{hero}}", "")
index_html = index_html.replace("{{title}}", "Home")
index_html = index_html.replace("{{content}}", f"""
<h2>Stories</h2>
<ul class="page-list">
{index_items}
</ul>
""")

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("✅ Generated index.html")

# Copy static assets
shutil.copy("templates/style.css", os.path.join(OUTPUT_DIR, "style.css"))
shutil.copytree("assets", os.path.join(OUTPUT_DIR, "assets"), dirs_exist_ok=True)

print("✅ Copied assets")