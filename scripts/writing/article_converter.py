#!/usr/bin/env python3
"""
article_converter.py — Pre/post-process markdown articles for each platform.

Subcommands:
  weixin   Extract links → reference list, output cleaned md → run html_converter
  zhihu    Clean markdown for Zhihu (remove WeChat artifacts, add footer)

Usage:
  python article_converter.py weixin <draft.md>   → writes weixin.html
  python article_converter.py zhihu  <draft.md>   → writes zhihu.md
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def read_article(path: Path) -> str:
    for name in ("draft.md", "final.md"):
        candidate = path / name if path.is_dir() else path
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    raise FileNotFoundError(f"No draft.md or final.md at {path}")


def resolve_article_file(path: Path) -> Path:
    """Return the actual .md file path."""
    if path.is_dir():
        for name in ("draft.md", "final.md"):
            f = path / name
            if f.exists():
                return f
        raise FileNotFoundError(f"No draft.md or final.md in {path}")
    return path


def extract_links(content: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Extract all [text](url) links from markdown.
    Returns (content_with_links_replaced, [(text, url), ...])
    Inline links become plain text; reference list built separately.
    """
    links = []
    seen_urls = {}  # url → index (1-based)

    def replacer(m):
        text, url = m.group(1), m.group(2)
        if url not in seen_urls:
            seen_urls[url] = len(links) + 1
            links.append((text, url))
        return text  # replace [text](url) with just text

    cleaned = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replacer, content)
    return cleaned, links


def build_reference_section(links: list[tuple[str, str]]) -> str:
    if not links:
        return ""
    lines = ["\n\n---\n\n**引用来源**\n"]
    for i, (text, url) in enumerate(links, 1):
        lines.append(f"{i}. {text}: {url}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# WeChat subcommand
# ---------------------------------------------------------------------------

def cmd_weixin(article_path: Path):
    """
    1. Extract links → plain text + reference list
    2. Write temp cleaned md
    3. Run html_converter.py → wechat.html
    4. Rename to weixin.html
    """
    md_file = resolve_article_file(article_path)
    article_dir = md_file.parent
    content = md_file.read_text(encoding="utf-8")

    print(f"Extracting links from {md_file.name}...")
    cleaned, links = extract_links(content)
    print(f"  Found {len(links)} links → moved to reference section")

    ref_section = build_reference_section(links)
    weixin_md = cleaned + ref_section

    # Write temp file
    temp_md = article_dir / "_weixin_temp.md"
    temp_md.write_text(weixin_md, encoding="utf-8")

    # Run html_converter.py
    script_dir = Path(__file__).parent
    converter = script_dir / "html_converter.py"
    output_html = article_dir / "wechat.html"

    print("Running html_converter.py...")
    result = subprocess.run(
        [sys.executable, str(converter), str(temp_md), str(output_html)],
        capture_output=False,
    )

    temp_md.unlink()  # clean up temp file

    if result.returncode != 0:
        print("✗ html_converter.py failed")
        sys.exit(1)

    # Rename wechat.html → weixin.html
    weixin_html = article_dir / "weixin.html"
    if output_html != weixin_html and output_html.exists():
        output_html.rename(weixin_html)

    print(f"✓ Written: {weixin_html}")


# ---------------------------------------------------------------------------
# Zhihu subcommand
# ---------------------------------------------------------------------------

def cmd_zhihu(article_path: Path):
    """
    Format draft.md for Zhihu:
    - Strip YAML frontmatter
    - Convert WeChat-only patterns (coloured boxes, etc.) to plain markdown
    - Convert [text](url) links → keep as-is (Zhihu supports links)
    - Add discussion footer
    - Write zhihu.md
    """
    md_file = resolve_article_file(article_path)
    article_dir = md_file.parent
    content = md_file.read_text(encoding="utf-8")

    print(f"Formatting {md_file.name} for Zhihu...")

    # Strip YAML frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    # Remove WeChat-specific HTML tags if any leaked in
    content = re.sub(r'<section[^>]*>', '', content)
    content = re.sub(r'</section>', '', content)
    content = re.sub(r'<span[^>]*>', '', content)
    content = re.sub(r'</span>', '', content)

    # Normalise multiple blank lines → max 2
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Add Zhihu discussion footer
    content = content.rstrip() + "\n\n---\n*欢迎在评论区分享你的看法。*\n"

    out_path = article_dir / "zhihu.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"✓ Written: {out_path}")
    char_count = len(content.replace('\n', ''))
    print(f"  {char_count} chars")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Convert article for platform publishing")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_weixin = sub.add_parser("weixin", help="Generate weixin.html")
    p_weixin.add_argument("article", help="Article directory or draft.md path")

    p_zhihu = sub.add_parser("zhihu", help="Generate zhihu.md")
    p_zhihu.add_argument("article", help="Article directory or draft.md path")

    args = parser.parse_args()
    path = Path(args.article)

    if args.cmd == "weixin":
        cmd_weixin(path)
    elif args.cmd == "zhihu":
        cmd_zhihu(path)


if __name__ == "__main__":
    main()
