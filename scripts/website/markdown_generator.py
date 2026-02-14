#!/usr/bin/env python3
"""
Markdown文件生成器
将提取和翻译的文章内容转换为符合Next.js要求的Markdown文件
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml
from urllib.parse import urlparse


def log(message: str, level: str = "INFO"):
    """统一的日志输出函数"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)


def sanitize_slug(title: str) -> str:
    """
    从标题生成URL友好的slug

    Args:
        title: 文章标题

    Returns:
        URL友好的slug字符串
    """
    # 移除特殊字符，保留字母、数字、空格和中文
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title.lower())
    # 将空格替换为连字符
    slug = re.sub(r'\s+', '-', slug.strip())
    # 移除连续的连字符
    slug = re.sub(r'-+', '-', slug)
    # 限制长度
    if len(slug) > 50:
        slug = slug[:50].rsplit('-', 1)[0]

    # 如果slug为空或只有连字符，使用时间戳
    if not slug or slug == '-':
        slug = f"article-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return slug


def generate_tags(content: str, title: str = "") -> List[str]:
    """
    基于内容自动生成标签

    Args:
        content: 文章内容
        title: 文章标题

    Returns:
        标签列表
    """
    tags = []

    # 定义关键词映射
    keyword_tags = {
        '瑞典': ['瑞典', 'Sweden'],
        '斯德哥尔摩': ['斯德哥尔摩', 'Stockholm', '瑞典首都'],
        '生活': ['生活', 'Life'],
        '工作': ['工作', 'Work', '职场'],
        '教育': ['教育', 'Education'],
        '医疗': ['医疗', 'Healthcare', '健康'],
        '科技': ['科技', 'Technology', '技术'],
        '创业': ['创业', 'Startup', '创新'],
        '文化': ['文化', 'Culture'],
        '旅游': ['旅游', 'Travel', '旅行'],
        '美食': ['美食', 'Food', '饮食'],
        '房产': ['房产', 'Real Estate', '房地产'],
        '移民': ['移民', 'Immigration', '移居'],
        '语言': ['语言', 'Language', '瑞典语'],
        '福利': ['福利', 'Welfare', '社会保障']
    }

    # 检查内容和标题中的关键词
    combined_text = (title + " " + content).lower()

    for keyword, tag_list in keyword_tags.items():
        if keyword.lower() in combined_text:
            tags.extend(tag_list[:2])  # 只取前两个相关标签

    # 去重并限制数量
    tags = list(dict.fromkeys(tags))[:8]

    # 如果没有标签，添加默认标签
    if not tags:
        tags = ['瑞典生活', 'Sweden Life']

    return tags


def determine_category(title: str, content: str) -> str:
    """
    基于标题和内容确定文章类别

    Args:
        title: 文章标题
        content: 文章内容

    Returns:
        类别名称
    """
    # 定义类别关键词
    categories = {
        '生活': ['生活', '日常', '居住', '超市', '购物'],
        '工作': ['工作', '职场', '求职', '面试', '公司'],
        '教育': ['教育', '学校', '大学', '学习', '孩子'],
        '科技': ['科技', '技术', '创业', '互联网', 'IT'],
        '文化': ['文化', '节日', '传统', '习俗', '艺术'],
        '旅游': ['旅游', '景点', '游玩', '度假', '风景'],
        '美食': ['美食', '餐厅', '烹饪', '食物', '饮食'],
        '其他': []
    }

    combined_text = (title + " " + content[:500]).lower()

    # 统计每个类别的匹配次数
    category_scores = {}
    for category, keywords in categories.items():
        if category == '其他':
            continue
        score = sum(1 for keyword in keywords if keyword in combined_text)
        if score > 0:
            category_scores[category] = score

    # 返回得分最高的类别
    if category_scores:
        return max(category_scores, key=category_scores.get)

    return '其他'


def format_content_to_markdown(content: Dict[str, Any], images: List[Dict[str, Any]]) -> str:
    """
    将内容转换为Markdown格式

    Args:
        content: 包含text和html的内容字典
        images: 图片信息列表

    Returns:
        格式化的Markdown内容
    """
    text = content.get('text', '')
    html = content.get('html', '')

    # 如果有HTML内容，尝试保留更多格式
    if html:
        # 使用BeautifulSoup处理HTML（如果可用）
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # 处理段落
            for p in soup.find_all('p'):
                p.insert_before('\n\n')
                p.insert_after('\n\n')

            # 处理标题
            for i in range(1, 7):
                for h in soup.find_all(f'h{i}'):
                    h.insert_before('\n\n')
                    h.insert_after('\n\n')
                    h.string = f"{'#' * i} {h.get_text()}"

            # 处理列表
            for ul in soup.find_all('ul'):
                for li in ul.find_all('li'):
                    li.string = f"- {li.get_text()}"
                    li.insert_after('\n')

            # 处理有序列表
            for ol in soup.find_all('ol'):
                for idx, li in enumerate(ol.find_all('li'), 1):
                    li.string = f"{idx}. {li.get_text()}"
                    li.insert_after('\n')

            # 获取处理后的文本
            text = soup.get_text()
        except ImportError:
            # 如果没有BeautifulSoup，使用简单的文本处理
            pass

    # 清理文本
    # 移除多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 确保段落之间有空行
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []

    for para in paragraphs:
        para = para.strip()
        if para:
            # 检查是否是标题（简单判断）
            if not para.startswith('#') and len(para) < 50 and not any(c in para for c in '。，、'):
                # 可能是标题，添加二级标题标记
                para = f"## {para}"
            formatted_paragraphs.append(para)

    # 重新组合段落
    markdown_content = '\n\n'.join(formatted_paragraphs)

    # 插入图片
    if images:
        # 在适当位置插入图片
        # 策略：每3-4个段落插入一张图片
        paragraphs = markdown_content.split('\n\n')
        result_paragraphs = []
        image_index = 0

        for i, para in enumerate(paragraphs):
            result_paragraphs.append(para)

            # 每3个段落插入一张图片
            if (i + 1) % 3 == 0 and image_index < len(images):
                image = images[image_index]
                # 使用本地路径或原始URL
                image_path = image.get('local_path')
                if image_path:
                    # 转换为相对路径
                    image_path = Path(image_path)
                    image_filename = image_path.name
                    image_markdown = f"![{image.get('alt', '图片')}](images/{image_filename})"
                else:
                    # 使用原始URL
                    image_markdown = f"![{image.get('alt', '图片')}]({image.get('src', '')})"

                result_paragraphs.append(image_markdown)
                image_index += 1

        # 如果还有剩余的图片，添加到末尾
        while image_index < len(images):
            image = images[image_index]
            image_path = image.get('local_path')
            if image_path:
                image_path = Path(image_path)
                image_filename = image_path.name
                image_markdown = f"![{image.get('alt', '图片')}](images/{image_filename})"
            else:
                image_markdown = f"![{image.get('alt', '图片')}]({image.get('src', '')})"
            result_paragraphs.append(image_markdown)
            image_index += 1

        markdown_content = '\n\n'.join(result_paragraphs)

    return markdown_content


def generate_frontmatter(data: Dict[str, Any], slug: str) -> str:
    """
    生成YAML frontmatter

    Args:
        data: 文章数据
        slug: URL slug

    Returns:
        YAML frontmatter字符串
    """
    # 提取基本信息
    title = data.get('title', '无标题')
    author = data.get('author', '瑞典马工')
    publish_date = data.get('publish_date', datetime.now().strftime('%Y-%m-%d'))
    original_url = data.get('original_url', '')

    # 获取内容用于生成摘要和标签
    content_text = data.get('content', {}).get('text', '')

    # 生成摘要（取前150个字符）
    excerpt = content_text[:150].replace('\n', ' ').strip()
    if len(content_text) > 150:
        excerpt += '...'

    # 生成标签和类别
    tags = generate_tags(content_text, title)
    category = determine_category(title, content_text)

    # 生成描述（用于SEO）
    description = content_text[:300].replace('\n', ' ').strip()

    # 构建frontmatter数据
    frontmatter = {
        'title': title,
        'date': publish_date,
        'category': category,
        'tags': tags,
        'excerpt': excerpt,
        'author': author,
        'description': description,
        'lastModified': datetime.now().strftime('%Y-%m-%d')
    }

    # 如果有原文链接，添加到frontmatter
    if original_url:
        frontmatter['originalUrl'] = original_url

    # 如果是翻译文章，添加相关信息
    if data.get('is_translated'):
        frontmatter['translated'] = True
        frontmatter['originalLanguage'] = data.get('original_language', 'zh-CN')
        frontmatter['translatedAt'] = data.get('translated_at', datetime.now().isoformat())

    # 转换为YAML字符串
    yaml_str = yaml.dump(
        frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )

    # 确保YAML格式正确
    return f"---\n{yaml_str}---\n"


def generate_markdown(data: Dict[str, Any], output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    生成完整的Markdown文件

    Args:
        data: 包含文章数据的字典
        output_dir: 输出目录（可选）

    Returns:
        包含生成结果的字典
    """
    log(f"开始生成Markdown文件")

    result = {
        'success': False,
        'file_path': None,
        'slug': None,
        'errors': [],
        'warnings': []
    }

    try:
        # 验证必要数据
        if not data.get('title'):
            result['errors'].append("缺少文章标题")
            return result

        if not data.get('content', {}).get('text'):
            result['errors'].append("缺少文章内容")
            return result

        # 生成slug
        slug = sanitize_slug(data['title'])
        result['slug'] = slug
        log(f"生成slug: {slug}")

        # 生成frontmatter
        frontmatter = generate_frontmatter(data, slug)

        # 生成主标题
        main_title = f"# {data['title']}\n"

        # 格式化内容
        content = format_content_to_markdown(
            data.get('content', {}),
            data.get('images', [])
        )

        # 添加原文链接（如果有）
        footer = ""
        if data.get('original_url'):
            footer = f"\n\n---\n\n*原文链接：[{data.get('title', '查看原文')}]({data['original_url']})*\n"
            footer += f"\n*本文由[瑞典马工](https://magong.se)翻译整理*\n"

        # 组合完整的Markdown内容
        markdown_content = frontmatter + '\n' + main_title + '\n' + content + footer

        # 保存文件（如果指定了输出目录）
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            date_prefix = datetime.now().strftime('%Y-%m-%d')
            filename = f"{date_prefix}-{slug}.md"
            file_path = output_dir / filename

            # 检查文件是否已存在
            if file_path.exists():
                result['warnings'].append(f"文件已存在，将覆盖: {file_path}")
                log(f"警告: 文件已存在，将覆盖: {file_path}", "WARNING")

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            result['file_path'] = str(file_path)
            log(f"Markdown文件已生成: {file_path}")

            # 如果有图片，创建images目录
            if data.get('images'):
                images_dir = output_dir / 'images'
                images_dir.mkdir(parents=True, exist_ok=True)
                log(f"创建图片目录: {images_dir}")

                # 复制图片到目标目录
                for image in data['images']:
                    if image.get('local_path'):
                        src_path = Path(image['local_path'])
                        if src_path.exists():
                            dest_path = images_dir / src_path.name
                            # 这里只是记录，实际复制需要使用shutil
                            result['warnings'].append(f"需要手动复制图片: {src_path} -> {dest_path}")

        result['success'] = True
        result['content'] = markdown_content
        result['metadata'] = {
            'title': data.get('title'),
            'author': data.get('author'),
            'date': data.get('publish_date'),
            'word_count': len(content),
            'image_count': len(data.get('images', [])),
            'tags_count': len(generate_tags(content, data.get('title', '')))
        }

        log(f"Markdown生成成功")

    except Exception as e:
        error_msg = f"生成Markdown时出错: {str(e)}"
        result['errors'].append(error_msg)
        log(error_msg, "ERROR")
        import traceback
        traceback.print_exc()

    return result


def batch_generate(json_file: str, output_dir: str = 'posts') -> List[Dict[str, Any]]:
    """
    批量生成Markdown文件

    Args:
        json_file: 包含文章数据的JSON文件路径
        output_dir: 输出目录

    Returns:
        生成结果列表
    """
    results = []

    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 确保是列表
        if not isinstance(data, list):
            data = [data]

        log(f"准备处理 {len(data)} 篇文章")

        # 处理每篇文章
        for idx, article in enumerate(data, 1):
            log(f"处理第 {idx}/{len(data)} 篇: {article.get('title', '无标题')}")
            result = generate_markdown(article, Path(output_dir))
            results.append(result)

            if result['success']:
                log(f"✓ 成功生成: {result['file_path']}", "SUCCESS")
            else:
                log(f"✗ 生成失败: {', '.join(result['errors'])}", "ERROR")

        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count

        log(f"批量生成完成: 成功 {success_count} 篇, 失败 {fail_count} 篇")

    except Exception as e:
        log(f"批量生成时出错: {e}", "ERROR")
        import traceback
        traceback.print_exc()

    return results


def main():
    """主函数 - 命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='生成Markdown文件')
    parser.add_argument('--input', required=True, help='输入JSON文件路径')
    parser.add_argument('--output-dir', default='posts', help='输出目录（默认: posts）')
    parser.add_argument('--single', action='store_true', help='处理单个文件而非批量')
    parser.add_argument('--validate', action='store_true', help='生成后验证Markdown格式')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要生成的内容，不实际创建文件')

    args = parser.parse_args()

    # 检查输入文件
    if not Path(args.input).exists():
        log(f"错误: 输入文件不存在: {args.input}", "ERROR")
        sys.exit(1)

    # 读取数据
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log(f"错误: 无效的JSON文件: {e}", "ERROR")
        sys.exit(1)

    # 处理数据
    if args.single or not isinstance(data, list):
        # 单个文件处理
        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        if args.dry_run:
            # 干运行模式，只显示内容
            result = generate_markdown(data, None)
            if result['success']:
                print("\n=== 生成的Markdown内容 ===\n")
                print(result['content'])
                print("\n=== 元数据 ===")
                print(json.dumps(result['metadata'], ensure_ascii=False, indent=2))
            else:
                log(f"生成失败: {', '.join(result['errors'])}", "ERROR")
                sys.exit(1)
        else:
            # 实际生成文件
            result = generate_markdown(data, Path(args.output_dir))
            if result['success']:
                log(f"✓ 文件已生成: {result['file_path']}", "SUCCESS")

                # 如果需要验证
                if args.validate and result['file_path']:
                    log("运行格式验证...")
                    from scripts.website.test.validate_markdown import validate_single_markdown_file
                    validation_result = validate_single_markdown_file(Path(result['file_path']))
                    if validation_result['valid']:
                        log("✓ 格式验证通过", "SUCCESS")
                    else:
                        log(f"✗ 格式验证失败: {validation_result['errors']}", "ERROR")
            else:
                log(f"✗ 生成失败: {', '.join(result['errors'])}", "ERROR")
                sys.exit(1)
    else:
        # 批量处理
        if args.dry_run:
            log("批量处理不支持干运行模式", "WARNING")
            sys.exit(1)

        results = batch_generate(args.input, args.output_dir)

        # 显示摘要
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count

        print(f"\n=== 批量生成摘要 ===")
        print(f"总数: {len(results)}")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")

        if fail_count > 0:
            print("\n失败的文章:")
            for result in results:
                if not result['success']:
                    print(f"  - {result.get('slug', '未知')}: {', '.join(result['errors'])}")
            sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()