#!/usr/bin/env python3
"""
微信文章内容提取器 - 带状态管理版本

支持增量处理，避免重复处理已有文章
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 导入状态管理器
from state_manager import ArticleStateManager

# 检查是否在GitHub Actions环境
IS_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') == 'true'


def log(message: str, level: str = "INFO"):
    """统一的日志输出函数"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)


def extract_from_html(html_content: str) -> Dict[str, Any]:
    """
    从HTML内容中提取文章数据

    Args:
        html_content: HTML字符串

    Returns:
        提取的文章数据字典
    """
    log("开始解析HTML内容")

    # 提取标题
    title = ""
    title_match = re.search(r'<h1[^>]*class="rich_media_title"[^>]*>(.*?)</h1>', html_content, re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        log(f"找到标题: {title}")
    else:
        # 备用标题提取
        meta_title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html_content)
        if meta_title_match:
            title = meta_title_match.group(1).strip()

    # 提取作者
    author = "瑞典马工"  # 默认值
    author_match = re.search(r'<em[^>]*class="rich_media_meta[^>]*>([^<]+)</em>', html_content)
    if author_match:
        author = author_match.group(1).strip()

    # 提取发布日期
    publish_date = datetime.now().strftime("%Y-%m-%d")
    date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', html_content)
    if date_match:
        publish_date = date_match.group(1).replace('/', '-')

    # 提取正文内容
    content_text = ""
    content_html = ""
    content_match = re.search(r'<div[^>]*class="rich_media_content"[^>]*>(.*?)</div>', html_content, re.DOTALL)
    if content_match:
        content_html = content_match.group(1)
        # 简单清理HTML获取纯文本
        content_text = re.sub(r'<[^>]+>', '', content_html)
        content_text = re.sub(r'\s+', ' ', content_text).strip()

    # 提取图片
    images = []
    img_pattern = r'<img[^>]*src="([^"]+)"[^>]*>'
    img_matches = re.findall(img_pattern, html_content)
    for idx, img_url in enumerate(img_matches):
        images.append({
            "src": img_url,
            "alt": f"图片{idx+1}",
            "local_filename": f"image_{idx+1}.jpg"
        })
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
            "extractor_version": "2.0.0",  # 带状态管理的版本
            "image_count": len(images)
        }
    }

    return result


def extract_from_url(url: str, force_update: bool = False, state_manager: Optional[ArticleStateManager] = None) -> Optional[Dict[str, Any]]:
    """
    从URL提取文章内容（支持增量处理）

    Args:
        url: 微信文章URL
        force_update: 是否强制更新（忽略状态检查）
        state_manager: 状态管理器实例

    Returns:
        提取的文章数据，如果跳过则返回None
    """
    log(f"开始处理URL: {url}")

    # 检查是否需要处理
    if state_manager and not force_update:
        if state_manager.is_article_processed(url):
            article_state = state_manager.get_article_state(url)
            if article_state and article_state.get("status") == "completed":
                log(f"文章已处理，跳过: {url}")
                return None

    # 在GitHub Actions中，使用mock数据进行测试
    if IS_GITHUB_ACTIONS and "test" in url:
        log("使用mock数据进行测试")
        mock_file = Path(__file__).parent.parent / ".github/test-data/mock-wechat-article.html"
        if mock_file.exists():
            with open(mock_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            result = extract_from_html(html_content)
            result["original_url"] = url

            # 更新状态
            if state_manager:
                state_manager.add_article(url, result)

            return result

    try:
        # 实现真实URL获取
        import requests
        response = requests.get(url, timeout=30)
        response.encoding = 'utf-8'
        html_content = response.text

        result = extract_from_html(html_content)
        result["original_url"] = url

        # 检查内容是否有更新
        if state_manager:
            content_text = result.get("content", {}).get("text", "")
            if state_manager.needs_update(url, content_text):
                log(f"文章内容已更新，重新处理: {url}")
                state_manager.add_article(url, result)
            else:
                log(f"文章内容未变化，跳过: {url}")
                return None

        return result

    except Exception as e:
        log(f"提取失败: {e}", "ERROR")

        # 记录错误状态
        if state_manager:
            state_manager.mark_article_error(url, str(e))

        # 返回空结果而不是抛出异常
        return {
            "title": "",
            "author": "",
            "publish_date": "",
            "original_url": url,
            "content": {"text": "", "html": ""},
            "images": [],
            "error": str(e)
        }


def process_incremental(urls: List[str], state_manager: ArticleStateManager, force_update: bool = False) -> Dict[str, Any]:
    """
    增量处理文章列表

    Args:
        urls: URL列表
        state_manager: 状态管理器
        force_update: 是否强制更新所有文章

    Returns:
        处理结果统计
    """
    log(f"开始增量处理 {len(urls)} 个URL")

    # 筛选需要处理的URL
    if not force_update:
        urls_to_process = state_manager.get_unprocessed_urls(urls)
        log(f"需要处理的新文章: {len(urls_to_process)} 个")
    else:
        urls_to_process = urls
        log("强制更新模式：处理所有文章")

    # 处理统计
    stats = {
        "total": len(urls),
        "processed": 0,
        "skipped": 0,
        "updated": 0,
        "errors": 0,
        "results": []
    }

    for url in urls:
        if url not in urls_to_process and not force_update:
            # 检查是否需要更新
            article_state = state_manager.get_article_state(url)
            if article_state:
                # 重新获取内容检查是否有更新
                result = extract_from_url(url, force_update=False, state_manager=state_manager)
                if result:
                    stats["updated"] += 1
                    stats["results"].append(result)
                else:
                    stats["skipped"] += 1
            else:
                stats["skipped"] += 1
        else:
            # 处理新文章或强制更新
            result = extract_from_url(url, force_update=force_update, state_manager=state_manager)
            if result:
                if result.get("error"):
                    stats["errors"] += 1
                else:
                    stats["processed"] += 1
                stats["results"].append(result)

    return stats


def main():
    """主函数 - 命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='提取微信文章内容（支持增量处理）')
    parser.add_argument('--url', help='微信文章URL')
    parser.add_argument('--input', help='包含URL列表的文件')
    parser.add_argument('--output', default='extracted.json', help='输出文件路径')
    parser.add_argument('--state-file', default='processed_articles.json', help='状态文件路径')
    parser.add_argument('--force-update', action='store_true', help='强制更新所有文章')
    parser.add_argument('--skip-state', action='store_true', help='跳过状态管理（传统模式）')
    parser.add_argument('--mock', action='store_true', help='使用mock数据测试')
    parser.add_argument('--stats', action='store_true', help='显示处理统计信息')

    args = parser.parse_args()

    # 初始化状态管理器
    state_manager = None if args.skip_state else ArticleStateManager(args.state_file)

    # 显示统计信息
    if args.stats and state_manager:
        stats = state_manager.get_statistics()
        print("当前处理统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        sys.exit(0)

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
        parser.print_help()
        sys.exit(1)

    # 处理URL
    if state_manager and not args.skip_state:
        # 增量处理模式
        process_stats = process_incremental(urls, state_manager, args.force_update)
        results = process_stats["results"]

        # 输出处理统计
        log("处理完成:")
        log(f"  总计: {process_stats['total']}")
        log(f"  新处理: {process_stats['processed']}")
        log(f"  已更新: {process_stats['updated']}")
        log(f"  跳过: {process_stats['skipped']}")
        log(f"  错误: {process_stats['errors']}")
    else:
        # 传统处理模式（不使用状态管理）
        results = []
        for url in urls:
            log(f"处理 {url}")
            result = extract_from_url(url, force_update=True)
            if result:
                results.append(result)

    # 保存结果
    if results:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results if len(results) > 1 else results[0],
                      f, ensure_ascii=False, indent=2)

        log(f"结果已保存到: {output_path}")
    else:
        log("没有新文章需要处理")

    # 验证输出
    if IS_GITHUB_ACTIONS:
        log("运行输出验证...")
        if results and results[0].get('title'):
            log("✓ 提取成功", "SUCCESS")
            sys.exit(0)
        else:
            log("✗ 提取失败 - 没有标题", "ERROR")
            sys.exit(1)


if __name__ == '__main__':
    main()