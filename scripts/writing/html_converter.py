#!/usr/bin/env python3
"""
Convert markdown article to WeChat-friendly HTML with inline CSS.
Usage: python html_converter.py <path/to/final.md>
"""

import sys
import re
import base64
from pathlib import Path
from typing import Dict
import markdown
from bs4 import BeautifulSoup
from PIL import Image
import io


def inline_styles_to_html(html_content: str, css_styles: Dict[str, str]) -> str:
    """Apply inline styles to HTML elements based on CSS rules."""

    soup = BeautifulSoup(html_content, 'html.parser')

    # Map CSS selectors to inline styles
    style_mapping = {
        'p': f"text-align: left; line-height: 1.75; font-family: {css_styles['font_family']}; font-size: 16px; margin: 1.5em 8px; letter-spacing: 0.1em; color: rgb(63, 63, 63);",
        'h1': "text-align: center; line-height: 1.75; font-size: 24px; display: table; padding: 0.2em 0.5em; margin: 2em auto 1em; color: rgb(255, 255, 255); background: rgb(15, 76, 129); font-weight: bold;",
        'h2': "text-align: left; line-height: 1.75; font-size: 18px; margin: 2em 8px 1em; color: rgb(15, 76, 129); font-weight: bold; border-bottom: 2px solid rgb(15, 76, 129); padding-bottom: 0.3em;",
        'h3': "text-align: left; line-height: 1.75; font-size: 16px; margin: 1.5em 8px 0.8em; color: rgb(15, 76, 129); font-weight: bold;",
        'blockquote': "padding: 1em; border-left: 4px solid rgb(15, 76, 129); border-radius: 6px; color: rgba(0, 0, 0, 0.5); background: rgb(247, 247, 247); margin-bottom: 1em; margin-top: 0px;",
        'code': "font-size: 90%; color: rgb(221, 17, 68); background: rgba(27, 31, 35, 0.05); padding: 3px 5px; border-radius: 4px;",
        'ul': f"list-style: circle; padding-left: 1em; margin-left: 0px; color: rgb(63, 63, 63); line-height: 1.75; font-family: {css_styles['font_family']}; font-size: 16px;",
        'ol': f"padding-left: 1em; margin-left: 0px; color: rgb(63, 63, 63); line-height: 1.75; font-family: {css_styles['font_family']}; font-size: 16px;",
        'li': "display: block; margin: 0.2em 8px;",
        'strong': "color: rgb(15, 76, 129); font-weight: bold;",
        'a': "color: rgb(15, 76, 129); text-decoration: none;",
        'img': "max-width: 100%; height: auto; display: block; margin: 1em auto;",
    }

    # Apply styles to each element type
    for tag, style in style_mapping.items():
        for element in soup.find_all(tag):
            # Preserve existing styles if any
            existing_style = element.get('style', '')
            if existing_style:
                element['style'] = f"{existing_style}; {style}"
            else:
                element['style'] = style

    # Special handling for strong tags in blockquotes
    for blockquote in soup.find_all('blockquote'):
        for strong in blockquote.find_all('strong'):
            strong['style'] = "color: rgb(15, 76, 129); font-weight: bold;"

    return str(soup)


def compress_image(image_path: Path, max_size_kb: int = 500) -> bytes:
    """Compress image to target size while maintaining quality."""

    with Image.open(image_path) as img:
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Start with quality 85
        quality = 85
        output = io.BytesIO()

        while quality > 20:
            output.seek(0)
            output.truncate()
            img.save(output, format='JPEG', quality=quality, optimize=True)

            size_kb = len(output.getvalue()) / 1024

            if size_kb <= max_size_kb:
                break

            # Reduce quality by 5 each iteration
            quality -= 5

        return output.getvalue()


def image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 data URI."""
    b64_data = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/jpeg;base64,{b64_data}"


def process_images_to_base64(html_content: str, md_path: Path) -> str:
    """Find all images in HTML and convert to base64."""

    soup = BeautifulSoup(html_content, 'html.parser')
    md_dir = md_path.parent

    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            continue

        # Skip if already base64
        if src.startswith('data:'):
            continue

        # Resolve image path relative to markdown file
        img_path = md_dir / src

        if not img_path.exists():
            print(f"Warning: Image not found: {img_path}")
            continue

        print(f"  Processing image: {src}")
        print(f"    Original size: {img_path.stat().st_size / 1024:.1f} KB")

        # Compress image
        compressed_bytes = compress_image(img_path, max_size_kb=500)
        print(f"    Compressed size: {len(compressed_bytes) / 1024:.1f} KB")

        # Convert to base64
        base64_src = image_to_base64(compressed_bytes)
        img['src'] = base64_src

        print(f"    ✓ Converted to base64")

    return str(soup)


def extract_css_variables(css_path: Path) -> Dict[str, str]:
    """Extract key CSS variables from the styles file."""

    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Extract font-family
    font_family_match = re.search(r'font-family:\s*([^;]+);', css_content)
    font_family = font_family_match.group(1).strip() if font_family_match else 'Arial, sans-serif'

    return {
        'font_family': font_family,
    }


def convert_markdown_to_wechat_html(md_path: Path, output_path: Path = None):
    """Convert markdown file to WeChat-friendly HTML."""

    if not md_path.exists():
        print(f"Error: File not found: {md_path}")
        sys.exit(1)

    # Determine output path
    if output_path is None:
        output_path = md_path.parent / "wechat.html"

    # Read markdown
    print(f"Reading {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    print("Converting markdown to HTML...")
    html = markdown.markdown(
        md_content,
        extensions=[
            'extra',          # Tables, code blocks, etc.
            'nl2br',          # Convert newlines to <br>
            'sane_lists',     # Better list handling
            'codehilite',     # Code highlighting
        ]
    )

    # Load CSS styles
    project_dir = Path(__file__).parent.parent.parent
    css_path = project_dir / "writing" / "templates" / "wechat_styles.css"

    if not css_path.exists():
        print(f"Warning: CSS file not found at {css_path}")
        css_styles = {'font_family': 'Arial, sans-serif'}
    else:
        css_styles = extract_css_variables(css_path)

    # Apply inline styles
    print("Applying inline styles...")
    styled_html = inline_styles_to_html(html, css_styles)

    # Process images to base64
    print("Processing images...")
    styled_html = process_images_to_base64(styled_html, md_path)

    # Wrap in WeChat-compatible structure
    final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=0">
    <meta name="wechat-enable-text-zoom-em" content="true">
</head>
<body>
    <div class="rich_media_content" id="js_content" style="font-family: {css_styles['font_family']}; font-size: 16px; line-height: 1.75;">
        {styled_html}
    </div>
</body>
</html>
"""

    # Write output
    print(f"Writing to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"\n✓ Successfully converted to WeChat HTML!")
    print(f"  Output: {output_path}")
    print(f"\nYou can now open this file in a browser and copy-paste into 微信公众号 editor.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_converter.py <path/to/final.md> [output.html]")
        print("\nExample:")
        print("  python html_converter.py articles/my-article/final.md")
        print("  python html_converter.py articles/my-article/final.md custom_output.html")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    convert_markdown_to_wechat_html(md_path, output_path)
