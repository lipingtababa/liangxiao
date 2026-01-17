#!/usr/bin/env python3
"""
Extract WeChat article style from saved HTML file.
This is a ONE-TIME utility to create templates from style.html.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup


def extract_wechat_styles(html_path: Path, output_dir: Path):
    """Extract CSS patterns and create template from WeChat HTML."""

    print(f"Reading {html_path}...")
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Find the main content div
    article_content = soup.find('div', class_='rich_media_content')

    if not article_content:
        print("Warning: Could not find rich_media_content div")
        return

    # Extract common style patterns
    styles = {
        'font_family': '"PingFang SC", -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif',
        'base_font_size': '16px',
        'line_height': '1.75',
        'text_color': 'rgb(63, 63, 63)',
        'primary_color': 'rgb(15, 76, 129)',
        'code_color': 'rgb(221, 17, 68)',
        'code_bg': 'rgba(27, 31, 35, 0.05)',
        'blockquote_bg': 'rgb(247, 247, 247)',
        'blockquote_border': '4px solid rgb(15, 76, 129)',
    }

    # Create CSS file
    css_content = f"""/* WeChat Article Styles - Extracted from style.html */

/* Base Typography */
body {{
    font-family: {styles['font_family']};
    font-size: {styles['base_font_size']};
    line-height: {styles['line_height']};
    color: {styles['text_color']};
    letter-spacing: 0.1em;
}}

/* Paragraphs */
p {{
    margin: 1.5em 8px;
    line-height: {styles['line_height']};
}}

/* Headings */
h2 {{
    text-align: center;
    font-size: 19.2px;
    display: table;
    padding: 0px 0.2em;
    margin: 4em auto 2em;
    color: rgb(255, 255, 255);
    background: {styles['primary_color']};
    font-weight: bold;
}}

/* Blockquotes */
blockquote {{
    padding: 1em;
    border-left: {styles['blockquote_border']};
    border-radius: 6px;
    color: rgba(0, 0, 0, 0.5);
    background: {styles['blockquote_bg']};
    margin-bottom: 1em;
    margin-top: 0px;
}}

blockquote strong {{
    color: {styles['primary_color']};
    font-weight: bold;
}}

/* Code */
code {{
    font-size: 90%;
    color: {styles['code_color']};
    background: {styles['code_bg']};
    padding: 3px 5px;
    border-radius: 4px;
}}

/* Lists */
ul, ol {{
    padding-left: 1em;
    margin-left: 0px;
}}

li {{
    display: block;
    margin: 0.2em 8px;
}}

ul {{
    list-style: circle;
}}

/* Strong/Bold with primary color */
strong {{
    color: {styles['primary_color']};
    font-weight: bold;
}}

/* Images */
img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
}}

/* Links */
a {{
    color: {styles['primary_color']};
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}
"""

    css_path = output_dir / "wechat_styles.css"
    print(f"Writing CSS to {css_path}...")
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)

    # Create HTML template
    template_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="wechat-enable-text-zoom-em" content="true">
    <title>{{{{title}}}}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="rich_media_content">
        {{{{content}}}}
    </div>
</body>
</html>
"""

    template_path = output_dir / "wechat_template.html"
    print(f"Writing template to {template_path}...")
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_html)

    print("\n✓ Successfully extracted WeChat styles!")
    print(f"  - CSS: {css_path}")
    print(f"  - Template: {template_path}")


if __name__ == "__main__":
    # Paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    html_path = project_dir / "style.html"
    output_dir = project_dir / "templates"

    # Create output directory if needed
    output_dir.mkdir(exist_ok=True)

    # Extract styles
    extract_wechat_styles(html_path, output_dir)
