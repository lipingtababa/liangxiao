#!/usr/bin/env python3
"""
Image handling utilities for 戚本禹 article writing.

This module provides functions to:
- Copy/organize images for articles
- Generate markdown image references
- Validate and list images
- Extract image metadata

CRITICAL: Only handle REAL images. Never fabricate or generate images.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import hashlib


def ensure_images_dir(article_path: str) -> Path:
    """
    Ensure the images directory exists for an article.

    Args:
        article_path: Path to the article directory (e.g., 'articles/my-article')

    Returns:
        Path object to the images directory

    Example:
        images_dir = ensure_images_dir('articles/translation-engineering')
        # Creates: articles/translation-engineering/images/
    """
    article_dir = Path(article_path)
    images_dir = article_dir / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)

    # Ensure group write permissions
    try:
        os.chmod(images_dir, 0o775)
    except Exception as e:
        print(f"Warning: Could not set permissions on {images_dir}: {e}")

    return images_dir


def add_image(
    source_path: str,
    article_path: str,
    custom_name: Optional[str] = None,
    preserve_original: bool = True
) -> Dict[str, str]:
    """
    Add an image to an article's images directory.

    Args:
        source_path: Path to the source image file
        article_path: Path to the article directory
        custom_name: Optional custom filename (will preserve extension)
        preserve_original: If True, copy the file. If False, move it.

    Returns:
        Dictionary with image info:
        {
            'source': original source path,
            'destination': new path in images directory,
            'relative_path': relative path from article root,
            'markdown': markdown reference string,
            'filename': final filename
        }

    Example:
        info = add_image(
            '/tmp/screenshot.png',
            'articles/translation-engineering',
            custom_name='workflow-diagram'
        )
        print(info['markdown'])  # ![workflow-diagram](images/workflow-diagram.png)
    """
    source = Path(source_path)

    if not source.exists():
        raise FileNotFoundError(f"Source image not found: {source_path}")

    # Ensure images directory exists
    images_dir = ensure_images_dir(article_path)

    # Determine destination filename
    if custom_name:
        # Preserve the original extension
        extension = source.suffix
        filename = f"{custom_name}{extension}"
    else:
        filename = source.name

    destination = images_dir / filename

    # Handle duplicate filenames
    counter = 1
    original_stem = destination.stem
    while destination.exists():
        filename = f"{original_stem}_{counter}{destination.suffix}"
        destination = images_dir / filename
        counter += 1

    # Copy or move the file
    if preserve_original:
        shutil.copy2(source, destination)
    else:
        shutil.move(str(source), str(destination))

    # Set group write permissions
    try:
        os.chmod(destination, 0o664)
    except Exception as e:
        print(f"Warning: Could not set permissions on {destination}: {e}")

    # Generate relative path and markdown reference
    relative_path = f"images/{filename}"
    markdown_ref = f"![{destination.stem}]({relative_path})"

    return {
        'source': str(source),
        'destination': str(destination),
        'relative_path': relative_path,
        'markdown': markdown_ref,
        'filename': filename
    }


def generate_markdown_ref(
    image_filename: str,
    alt_text: Optional[str] = None,
    caption: Optional[str] = None
) -> str:
    """
    Generate markdown reference for an image.

    Args:
        image_filename: Filename of the image (e.g., 'diagram.png')
        alt_text: Optional alt text (defaults to filename without extension)
        caption: Optional caption to add after the image

    Returns:
        Markdown formatted string

    Example:
        ref = generate_markdown_ref(
            'workflow.png',
            alt_text='Translation workflow diagram',
            caption='Figure 1: Complete translation workflow using Claude'
        )
    """
    if alt_text is None:
        alt_text = Path(image_filename).stem

    markdown = f"![{alt_text}](images/{image_filename})"

    if caption:
        markdown += f"\n*{caption}*"

    return markdown


def list_images(article_path: str) -> List[Dict[str, str]]:
    """
    List all images in an article's images directory.

    Args:
        article_path: Path to the article directory

    Returns:
        List of dictionaries with image information

    Example:
        images = list_images('articles/translation-engineering')
        for img in images:
            print(f"{img['filename']}: {img['size_kb']} KB")
    """
    images_dir = Path(article_path) / 'images'

    if not images_dir.exists():
        return []

    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'}
    images = []

    for file_path in sorted(images_dir.iterdir()):
        if file_path.suffix.lower() in image_extensions:
            stat = file_path.stat()
            images.append({
                'filename': file_path.name,
                'path': str(file_path),
                'relative_path': f"images/{file_path.name}",
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'extension': file_path.suffix,
                'markdown': f"![{file_path.stem}](images/{file_path.name})"
            })

    return images


def validate_image_refs(article_md_path: str) -> Dict[str, List[str]]:
    """
    Validate that all image references in a markdown file exist.

    Args:
        article_md_path: Path to the markdown file

    Returns:
        Dictionary with 'valid' and 'missing' lists of image references

    Example:
        result = validate_image_refs('articles/translation-engineering/draft.md')
        if result['missing']:
            print(f"Missing images: {result['missing']}")
    """
    import re

    md_file = Path(article_md_path)
    article_dir = md_file.parent

    if not md_file.exists():
        raise FileNotFoundError(f"Markdown file not found: {article_md_path}")

    content = md_file.read_text(encoding='utf-8')

    # Find all image references: ![alt](path)
    img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(img_pattern, content)

    valid = []
    missing = []

    for alt_text, img_path in matches:
        # Resolve relative paths
        full_path = article_dir / img_path

        if full_path.exists():
            valid.append(img_path)
        else:
            missing.append(img_path)

    return {
        'valid': valid,
        'missing': missing,
        'total': len(matches)
    }


def get_image_metadata(image_path: str) -> Dict[str, any]:
    """
    Get metadata about an image file.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary with image metadata

    Example:
        meta = get_image_metadata('articles/translation-engineering/images/diagram.png')
        print(f"Size: {meta['size_kb']} KB, Hash: {meta['hash'][:8]}")
    """
    img_file = Path(image_path)

    if not img_file.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    stat = img_file.stat()

    # Calculate file hash for deduplication
    with open(img_file, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    metadata = {
        'filename': img_file.name,
        'path': str(img_file),
        'extension': img_file.suffix,
        'size_bytes': stat.st_size,
        'size_kb': round(stat.st_size / 1024, 2),
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'hash': file_hash,
        'modified_time': stat.st_mtime
    }

    # Try to get image dimensions (requires PIL/Pillow)
    try:
        from PIL import Image
        with Image.open(img_file) as img:
            metadata['width'] = img.width
            metadata['height'] = img.height
            metadata['format'] = img.format
            metadata['mode'] = img.mode
    except ImportError:
        metadata['note'] = 'Install Pillow for dimension info: pip install Pillow'
    except Exception as e:
        metadata['note'] = f'Could not read image dimensions: {e}'

    return metadata


def create_image_inventory(article_path: str, output_file: Optional[str] = None) -> str:
    """
    Create an inventory of all images in an article.

    Args:
        article_path: Path to the article directory
        output_file: Optional path to save the inventory (markdown format)

    Returns:
        Markdown formatted inventory string

    Example:
        inventory = create_image_inventory('articles/translation-engineering')
        print(inventory)
    """
    images = list_images(article_path)

    if not images:
        return f"No images found in {article_path}/images/"

    lines = [
        f"# Image Inventory: {Path(article_path).name}",
        f"\nTotal images: {len(images)}\n",
        "| Filename | Size (KB) | Markdown Reference |",
        "|----------|-----------|-------------------|"
    ]

    for img in images:
        lines.append(f"| {img['filename']} | {img['size_kb']} | `{img['markdown']}` |")

    inventory = '\n'.join(lines)

    if output_file:
        output_path = Path(output_file)
        output_path.write_text(inventory, encoding='utf-8')

        # Set group write permissions
        try:
            os.chmod(output_path, 0o664)
        except Exception as e:
            print(f"Warning: Could not set permissions on {output_path}: {e}")

    return inventory


# Command-line interface
if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='Image handling utilities for 戚本禹 articles'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # add command
    add_parser = subparsers.add_parser('add', help='Add image to article')
    add_parser.add_argument('source', help='Source image path')
    add_parser.add_argument('article', help='Article directory path')
    add_parser.add_argument('--name', help='Custom filename (without extension)')
    add_parser.add_argument('--move', action='store_true', help='Move instead of copy')

    # list command
    list_parser = subparsers.add_parser('list', help='List images in article')
    list_parser.add_argument('article', help='Article directory path')

    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate image references')
    validate_parser.add_argument('markdown', help='Markdown file path')

    # inventory command
    inventory_parser = subparsers.add_parser('inventory', help='Create image inventory')
    inventory_parser.add_argument('article', help='Article directory path')
    inventory_parser.add_argument('--output', help='Output file path')

    # metadata command
    meta_parser = subparsers.add_parser('metadata', help='Get image metadata')
    meta_parser.add_argument('image', help='Image file path')

    args = parser.parse_args()

    if args.command == 'add':
        info = add_image(
            args.source,
            args.article,
            custom_name=args.name,
            preserve_original=not args.move
        )
        print(f"✓ Image added: {info['filename']}")
        print(f"  Path: {info['destination']}")
        print(f"  Markdown: {info['markdown']}")

    elif args.command == 'list':
        images = list_images(args.article)
        if not images:
            print(f"No images found in {args.article}")
        else:
            print(f"\nImages in {args.article}:")
            for img in images:
                print(f"  • {img['filename']} ({img['size_kb']} KB)")
                print(f"    {img['markdown']}")

    elif args.command == 'validate':
        result = validate_image_refs(args.markdown)
        print(f"\nImage validation for {args.markdown}:")
        print(f"  Total references: {result['total']}")
        print(f"  Valid: {len(result['valid'])}")
        print(f"  Missing: {len(result['missing'])}")
        if result['missing']:
            print("\nMissing images:")
            for img in result['missing']:
                print(f"  ✗ {img}")

    elif args.command == 'inventory':
        inventory = create_image_inventory(args.article, args.output)
        print(inventory)
        if args.output:
            print(f"\n✓ Inventory saved to: {args.output}")

    elif args.command == 'metadata':
        meta = get_image_metadata(args.image)
        print(f"\nMetadata for {meta['filename']}:")
        for key, value in meta.items():
            if key != 'filename':
                print(f"  {key}: {value}")

    else:
        parser.print_help()
