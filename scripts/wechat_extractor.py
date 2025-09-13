#!/usr/bin/env python3
"""
微信文章内容提取器
从微信公众号文章URL中提取文章内容、标题、发布时间和图片
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# 检查是否在GitHub Actions环境
IS_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') == 'true'

def log(message: str, level: str = "INFO"):
    """统一的日志输出函数"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)

def clean_text(text: str) -> str:
    """清理文本内容，去除多余的空白字符"""
    if not text:
        return ""
    # 去除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空白
    text = text.strip()
    return text

def download_image(url: str, save_dir: Path, filename: str) -> Optional[str]:
    """
    下载图片到本地

    Args:
        url: 图片URL
        save_dir: 保存目录
        filename: 文件名

    Returns:
        本地文件路径，失败返回None
    """
    try:
        # 创建保存目录
        save_dir.mkdir(parents=True, exist_ok=True)

        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://mp.weixin.qq.com/'
        }

        # 下载图片
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        # 确定文件扩展名
        content_type = response.headers.get('content-type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        elif 'gif' in content_type:
            ext = '.gif'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            # 尝试从URL中获取扩展名
            parsed_url = urlparse(url)
            path_ext = Path(parsed_url.path).suffix
            ext = path_ext if path_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] else '.jpg'

        # 确保文件名有正确的扩展名
        if not filename.endswith(ext):
            filename = filename.rsplit('.', 1)[0] + ext

        # 保存文件
        file_path = save_dir / filename
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        log(f"图片已下载: {file_path}")
        return str(file_path)

    except Exception as e:
        log(f"下载图片失败 {url}: {e}", "ERROR")
        return None

def extract_from_html(html_content: str, save_images: bool = True, image_dir: Path = None) -> Dict[str, Any]:
    """
    从HTML内容中提取文章数据

    Args:
        html_content: HTML字符串
        save_images: 是否下载图片到本地
        image_dir: 图片保存目录

    Returns:
        提取的文章数据字典
    """
    log("开始解析HTML内容")

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # 1. 提取标题
    title = ""
    # 首先尝试从rich_media_title类中提取
    title_elem = soup.find('h1', class_='rich_media_title')
    if title_elem:
        title = clean_text(title_elem.get_text())
        log(f"找到标题: {title}")
    else:
        # 尝试从meta标签中提取
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            title = clean_text(meta_title['content'])
            log(f"从meta标签找到标题: {title}")
        else:
            # 尝试从title标签中提取
            title_tag = soup.find('title')
            if title_tag:
                title = clean_text(title_tag.get_text())
                log(f"从title标签找到标题: {title}")

    # 2. 提取作者
    author = "瑞典马工"  # 默认值
    # 查找作者信息
    author_elem = soup.find('span', class_='rich_media_meta rich_media_meta_nickname')
    if not author_elem:
        author_elem = soup.find('a', id='js_name')
    if not author_elem:
        author_elem = soup.find('strong', class_='profile_nickname')

    if author_elem:
        author_text = clean_text(author_elem.get_text())
        if author_text:
            author = author_text
            log(f"找到作者: {author}")

    # 尝试从meta标签中提取
    if author == "瑞典马工":
        meta_author = soup.find('meta', {'name': 'author'})
        if meta_author and meta_author.get('content'):
            author = clean_text(meta_author['content'])
            log(f"从meta标签找到作者: {author}")

    # 3. 提取发布日期
    publish_date = datetime.now().strftime("%Y-%m-%d")  # 默认今天

    # 查找发布时间
    publish_time_elem = soup.find('em', id='publish_time')
    if publish_time_elem:
        date_text = publish_time_elem.get_text().strip()
        # 尝试解析日期
        try:
            # 处理不同的日期格式
            if '年' in date_text and '月' in date_text and '日' in date_text:
                # 中文日期格式：2024年1月15日
                date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_text)
                if date_match:
                    year, month, day = date_match.groups()
                    publish_date = f"{year}-{month:0>2}-{day:0>2}"
            else:
                # 尝试标准格式
                date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_text)
                if date_match:
                    publish_date = date_match.group(0)
            log(f"找到发布日期: {publish_date}")
        except Exception as e:
            log(f"解析日期失败: {e}", "WARNING")

    # 从JavaScript变量中提取日期
    if publish_date == datetime.now().strftime("%Y-%m-%d"):
        script_match = re.search(r'var\s+publish_time\s*=\s*"([^"]+)"', html_content)
        if script_match:
            date_text = script_match.group(1)
            try:
                # 尝试解析不同格式的日期
                if '-' in date_text:
                    date_parts = date_text.split('-')
                    if len(date_parts) >= 3:
                        publish_date = f"{date_parts[0]}-{date_parts[1]:0>2}-{date_parts[2][:2]:0>2}"
                        log(f"从脚本变量找到发布日期: {publish_date}")
            except:
                pass

    # 4. 提取正文内容
    content_text = ""
    content_html = ""

    # 查找正文内容区域
    content_elem = soup.find('div', id='js_content')
    if not content_elem:
        content_elem = soup.find('div', class_='rich_media_content')

    if content_elem:
        # 保存HTML内容
        content_html = str(content_elem)

        # 提取纯文本内容，保留段落结构
        paragraphs = []
        for elem in content_elem.find_all(['p', 'div', 'section', 'span']):
            text = elem.get_text(strip=True)
            if text and len(text) > 1:  # 过滤掉太短的文本（仅单个字符）
                paragraphs.append(text)

        # 合并段落，用换行分隔
        content_text = '\n\n'.join(paragraphs)
        log(f"提取到正文内容，长度: {len(content_text)} 字符")
    else:
        log("未找到正文内容区域", "WARNING")

    # 5. 提取图片
    images = []
    img_elements = []

    # 在正文内容中查找图片
    if content_elem:
        img_elements = content_elem.find_all('img')

    # 如果正文中没有图片，在整个页面查找
    if not img_elements:
        img_elements = soup.find_all('img', {'data-src': True})

    # 如果还是没有，查找所有img标签
    if not img_elements:
        img_elements = soup.find_all('img')

    # 设置图片保存目录
    if save_images and image_dir is None:
        image_dir = Path('extracted_images') / datetime.now().strftime('%Y%m%d_%H%M%S')

    for idx, img in enumerate(img_elements):
        # 获取图片URL，优先使用data-src
        img_url = img.get('data-src') or img.get('src')

        if img_url:
            # 处理相对URL
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = 'https://mp.weixin.qq.com' + img_url

            # 过滤掉太小的图片（可能是图标）
            if 'emoji' in img_url or 'icon' in img_url:
                continue

            # 获取图片描述
            alt_text = img.get('alt', '').strip()
            if not alt_text:
                alt_text = img.get('data-w', '')  # 微信图片的宽度属性
            if not alt_text:
                alt_text = f"图片{idx+1}"

            # 生成本地文件名
            local_filename = f"image_{idx+1:03d}"

            image_info = {
                "src": img_url,
                "alt": alt_text,
                "local_filename": local_filename,
                "local_path": None
            }

            # 下载图片
            if save_images and image_dir:
                local_path = download_image(img_url, image_dir, local_filename)
                if local_path:
                    image_info["local_path"] = local_path

            images.append(image_info)

    log(f"找到 {len(images)} 张图片")

    # 构建返回数据
    result = {
        "title": title,
        "author": author,
        "publish_date": publish_date,
        "original_url": "",  # 将在主函数中设置
        "content": {
            "text": content_text,
            "html": content_html
        },
        "images": images,
        "word_count": len(content_text),
        "extraction_metadata": {
            "extracted_at": datetime.now().isoformat(),
            "extractor_version": "2.0.0",
            "image_count": len(images),
            "images_downloaded": save_images
        }
    }

    return result

def extract_from_url(url: str, save_images: bool = True, image_dir: Path = None) -> Dict[str, Any]:
    """
    从URL提取文章内容

    Args:
        url: 微信文章URL
        save_images: 是否下载图片
        image_dir: 图片保存目录

    Returns:
        提取的文章数据
    """
    log(f"开始处理URL: {url}")

    # 在GitHub Actions中，使用mock数据进行测试
    if IS_GITHUB_ACTIONS and "test" in url:
        log("使用mock数据进行测试")
        mock_file = Path(__file__).parent.parent / ".github/test-data/mock-wechat-article.html"
        if mock_file.exists():
            with open(mock_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            result = extract_from_html(html_content, save_images, image_dir)
            result["original_url"] = url
            return result

    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        # 发送HTTP请求
        log("发送HTTP请求...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # 自动检测编码
        response.encoding = response.apparent_encoding or 'utf-8'
        html_content = response.text

        log(f"成功获取HTML内容，长度: {len(html_content)} 字符")

        # 检查是否被反爬虫拦截
        if '请在微信客户端打开链接' in html_content or 'wx.onMenuShareTimeline' not in html_content:
            log("可能被微信反爬虫机制拦截", "WARNING")
            # 尝试添加延迟后重试
            time.sleep(2)
            response = requests.get(url, headers=headers, timeout=30)
            response.encoding = response.apparent_encoding or 'utf-8'
            html_content = response.text

        # 提取内容
        result = extract_from_html(html_content, save_images, image_dir)
        result["original_url"] = url

        # 验证提取结果
        if not result.get('title'):
            log("警告: 未能提取到文章标题", "WARNING")
        if not result.get('content', {}).get('text'):
            log("警告: 未能提取到文章内容", "WARNING")

        return result

    except requests.exceptions.RequestException as e:
        log(f"网络请求失败: {e}", "ERROR")
        return {
            "title": "",
            "author": "",
            "publish_date": "",
            "original_url": url,
            "content": {"text": "", "html": ""},
            "images": [],
            "error": f"网络请求失败: {str(e)}",
            "extraction_metadata": {
                "extracted_at": datetime.now().isoformat(),
                "extractor_version": "2.0.0",
                "error": True
            }
        }
    except Exception as e:
        log(f"提取失败: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return {
            "title": "",
            "author": "",
            "publish_date": "",
            "original_url": url,
            "content": {"text": "", "html": ""},
            "images": [],
            "error": str(e),
            "extraction_metadata": {
                "extracted_at": datetime.now().isoformat(),
                "extractor_version": "2.0.0",
                "error": True
            }
        }

def main():
    """主函数 - 命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='提取微信文章内容')
    parser.add_argument('--url', help='微信文章URL')
    parser.add_argument('--input', help='包含URL列表的文件')
    parser.add_argument('--output', default='extracted.json', help='输出文件路径')
    parser.add_argument('--image-dir', help='图片保存目录')
    parser.add_argument('--no-images', action='store_true', help='不下载图片')
    parser.add_argument('--mock', action='store_true', help='使用mock数据测试')

    args = parser.parse_args()

    # 确定要处理的URL
    urls = []
    if args.mock:
        urls = ["https://mp.weixin.qq.com/s/test"]
    elif args.url:
        urls = [args.url]
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        # 如果没有提供参数，显示使用说明
        print("微信文章内容提取器")
        print("=" * 50)
        print("\n使用方法:")
        print("  1. 提取单个文章: python wechat_extractor.py --url <文章URL>")
        print("  2. 批量提取: python wechat_extractor.py --input <URL列表文件>")
        print("  3. 不下载图片: 添加 --no-images 参数")
        print("  4. 指定图片目录: --image-dir <目录路径>")
        print("\n示例:")
        print('  python wechat_extractor.py --url "https://mp.weixin.qq.com/s/xxxx"')
        print('  python wechat_extractor.py --input articles.txt --output results.json')
        sys.exit(0)

    # 设置图片目录
    image_dir = None
    if args.image_dir:
        image_dir = Path(args.image_dir)

    # 处理URL
    results = []
    success_count = 0
    fail_count = 0

    for url in urls:
        log(f"处理 {url}")
        result = extract_from_url(url, save_images=not args.no_images, image_dir=image_dir)
        results.append(result)

        # 统计成功和失败
        if result.get('title') and result.get('content', {}).get('text'):
            success_count += 1
            log(f"✓ 成功提取: {result['title']}", "SUCCESS")
        else:
            fail_count += 1
            log(f"✗ 提取失败", "ERROR")

    # 保存结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results if len(results) > 1 else results[0],
                  f, ensure_ascii=False, indent=2)

    log(f"结果已保存到: {output_path}")
    log(f"处理完成: 成功 {success_count} 篇, 失败 {fail_count} 篇")

    # 验证输出
    if IS_GITHUB_ACTIONS:
        log("运行输出验证...")
        if results and results[0].get('title'):
            log("✓ 提取成功", "SUCCESS")
            sys.exit(0)
        else:
            log("✗ 提取失败 - 没有标题", "ERROR")
            sys.exit(1)

    # 返回成功状态
    sys.exit(0 if success_count > 0 else 1)

if __name__ == '__main__':
    main()