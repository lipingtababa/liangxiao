#!/usr/bin/env python3
"""
Generate article images using Google Imagen 4.

Usage:
    python image_generator.py <article_path> [--out-dir <dir>]

Reads article content, generates prompts for cover + section images,
calls Imagen 4, adds "AI生成" watermark badge, saves to images/.
"""

import argparse
import os
import sys
import re
import json
import base64
from pathlib import Path
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont


GOOGLE_AI_KEY_PATH = Path.home() / ".credentials" / "google.ai.txt"
CREDENTIALS_PATH = Path.home() / ".credentials"


def load_api_key() -> str:
    key = os.environ.get("GOOGLE_AI_API_KEY")
    if key:
        return key
    if GOOGLE_AI_KEY_PATH.exists():
        return GOOGLE_AI_KEY_PATH.read_text().strip()
    raise RuntimeError(f"No Google AI API key found. Set GOOGLE_AI_API_KEY or put key in {GOOGLE_AI_KEY_PATH}")


def load_article(article_path: Path) -> str:
    for name in ("draft.md", "final.md"):
        candidate = article_path / name if article_path.is_dir() else article_path
        if candidate.exists():
            return candidate.read_text()
    raise FileNotFoundError(f"No draft.md or final.md found at {article_path}")


def extract_article_meta(content: str) -> dict:
    """Extract title and sections from markdown."""
    lines = content.splitlines()
    title = ""
    sections = []
    for line in lines:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("## "):
            sections.append(line[3:].strip())
    # Strip frontmatter title if present
    if not title:
        fm = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", content, re.MULTILINE)
        if fm:
            title = fm.group(1)
    return {"title": title, "sections": sections[:4]}  # max 4 sections


def build_prompts(meta: dict, persona: str = "") -> list[dict]:
    """
    Build image prompts for cover (3:4 XHS, 16:9 WeChat) + section illustrations.
    Returns list of {name, prompt, aspect_ratio}.
    """
    title = meta["title"]
    sections = meta["sections"]

    # Determine visual style from persona
    style_suffix = (
        "dramatic lighting, bold contrast, editorial photography style, cinematic"
        if "戚" in persona
        else "clean minimal composition, soft professional lighting, thoughtful documentary style"
    )

    topic_hint = f'article titled "{title}"' if title else "technology and AI article"

    prompts = [
        {
            "name": "cover-xhs",
            "aspect_ratio": "3:4",
            "prompt": (
                f"A striking cover image for a Chinese technology article. {topic_hint}. "
                f"Purely visual, conceptual, metaphorical — absolutely no text, no letters, no words, no numbers anywhere in the image. No people's faces. "
                f"High quality photography or digital art. {style_suffix}. "
                "Suitable for Chinese social media. No watermarks."
            ),
        },
        {
            "name": "cover-weixin",
            "aspect_ratio": "16:9",
            "prompt": (
                f"A wide banner image for a Chinese WeChat article. {topic_hint}. "
                f"Purely visual, conceptual, metaphorical — absolutely no text, no letters, no words anywhere in the image. "
                f"Professional quality. {style_suffix}. "
                "No watermarks."
            ),
        },
    ]

    # Section illustrations (1:1 square, up to 3)
    for i, section in enumerate(sections[:3]):
        prompts.append(
            {
                "name": f"section-{i+1}",
                "aspect_ratio": "1:1",
                "prompt": (
                    f"A conceptual illustration representing: {section}. "
                    f"For a technology article about {title}. "
                    f"Abstract or metaphorical visual — absolutely no text, no letters, no words anywhere. {style_suffix}. "
                    "No watermarks."
                ),
            }
        )

    return prompts


def add_watermark(img: Image.Image) -> Image.Image:
    """Add visible 'AI生成' badge to bottom-right corner."""
    img = img.copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size

    label = "AI生成"
    font_size = max(24, h // 25)

    try:
        # Try system font first
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    padding = 8
    margin = 12
    rx = w - text_w - padding * 2 - margin
    ry = h - text_h - padding * 2 - margin

    # Semi-transparent background pill
    draw.rounded_rectangle(
        [rx, ry, rx + text_w + padding * 2, ry + text_h + padding * 2],
        radius=6,
        fill=(0, 0, 0, 160),
    )
    draw.text((rx + padding, ry + padding), label, font=font, fill=(255, 255, 255, 230))

    return img


def generate_image(client: genai.Client, prompt_info: dict) -> Image.Image | None:
    """Call Imagen 4 and return PIL Image."""
    try:
        response = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt_info["prompt"],
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=prompt_info["aspect_ratio"],
                safety_filter_level="block_low_and_above",
                person_generation="dont_allow",
            ),
        )
        if not response.generated_images:
            print(f"  ⚠ No image returned for {prompt_info['name']}")
            return None

        img_bytes = response.generated_images[0].image.image_bytes
        return Image.open(BytesIO(img_bytes)).convert("RGBA")

    except Exception as e:
        print(f"  ✗ Failed to generate {prompt_info['name']}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate article images with Imagen 4")
    parser.add_argument("article_path", help="Path to article directory or draft.md file")
    parser.add_argument("--out-dir", help="Output directory (default: <article_dir>/images)")
    parser.add_argument("--persona", default="", help="Persona name (benyu or hushi) for style")
    args = parser.parse_args()

    article_path = Path(args.article_path)
    article_dir = article_path if article_path.is_dir() else article_path.parent
    out_dir = Path(args.out_dir) if args.out_dir else article_dir / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading article from {article_dir}...")
    content = load_article(article_path)
    meta = extract_article_meta(content)
    print(f"  Title: {meta['title'] or '(none)'}")
    print(f"  Sections: {meta['sections']}")

    prompts = build_prompts(meta, persona=args.persona)
    print(f"\nGenerating {len(prompts)} images...")

    api_key = load_api_key()
    client = genai.Client(api_key=api_key)

    generated = []
    for p in prompts:
        print(f"  → {p['name']} ({p['aspect_ratio']})...")
        img = generate_image(client, p)
        if img is None:
            continue

        img = add_watermark(img)

        # Save as JPEG (XHS/WeChat prefer JPEG)
        out_path = out_dir / f"{p['name']}.jpg"
        img_rgb = img.convert("RGB")
        img_rgb.save(out_path, "JPEG", quality=92)
        print(f"    ✓ Saved {out_path}")
        generated.append({"name": p["name"], "path": str(out_path), "aspect_ratio": p["aspect_ratio"]})

    # Write manifest for other scripts to read
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(generated, indent=2, ensure_ascii=False))
    print(f"\n✓ Done. {len(generated)} images saved to {out_dir}/")
    print(f"  Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
