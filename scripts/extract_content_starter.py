#!/usr/bin/env python3
"""
微信文章内容提取器 - AI开发起始代码

这个文件提供了一个完整的起始框架，AI开发者只需要填充TODO部分
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

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
    
    # TODO: AI开发者需要实现以下提取逻辑
    # 提示：使用BeautifulSoup或正则表达式
    
    # 1. 提取标题
    # 查找 <h1 class="rich_media_title"> 或 <meta property="og:title">
    title = ""
    title_match = re.search(r'<h1[^>]*class="rich_media_title"[^>]*>(.*?)</h1>', html_content, re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        log(f"找到标题: {title}")
    else:
        # TODO: 实现备用标题提取
        pass
    
    # 2. 提取作者
    # 查找 <em class="rich_media_meta rich_media_meta_text"> 或 <meta name="author">
    author = "瑞典马工"  # 默认值
    # TODO: 实现作者提取
    
    # 3. 提取发布日期
    # 查找日期格式如 2024-01-15
    publish_date = datetime.now().strftime("%Y-%m-%d")  # 默认今天
    # TODO: 实现日期提取
    
    # 4. 提取正文内容
    # 查找 <div class="rich_media_content"> 中的所有文本
    content_text = ""
    content_html = ""
    # TODO: 实现内容提取
    # 提示：需要清理HTML标签，但保留段落结构
    
    # 5. 提取图片
    # 查找所有 <img> 标签的 src 属性
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
            "extractor_version": "1.0.0",
            "image_count": len(images)
        }
    }
    
    return result

def extract_from_url(url: str) -> Dict[str, Any]:
    """
    从URL提取文章内容
    
    Args:
        url: 微信文章URL
        
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
            result = extract_from_html(html_content)
            result["original_url"] = url
            return result
    
    # TODO: 实现真实URL获取
    # 提示：
    # 1. 使用 requests 库获取HTML
    # 2. 处理可能的编码问题（微信文章通常是UTF-8）
    # 3. 处理网络错误和超时
    
    try:
        # TODO: 实现HTTP请求
        import requests
        response = requests.get(url, timeout=30)
        response.encoding = 'utf-8'
        html_content = response.text
        
        result = extract_from_html(html_content)
        result["original_url"] = url
        return result
        
    except Exception as e:
        log(f"提取失败: {e}", "ERROR")
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

def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='提取微信文章内容')
    parser.add_argument('--url', help='微信文章URL')
    parser.add_argument('--input', help='包含URL列表的文件')
    parser.add_argument('--output', default='extracted.json', help='输出文件路径')
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
        parser.print_help()
        sys.exit(1)
    
    # 处理URL
    results = []
    for url in urls:
        log(f"处理 {url}")
        result = extract_from_url(url)
        results.append(result)
    
    # 保存结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results if len(results) > 1 else results[0], 
                  f, ensure_ascii=False, indent=2)
    
    log(f"结果已保存到: {output_path}")
    
    # 验证输出
    if IS_GITHUB_ACTIONS:
        log("运行输出验证...")
        # 简单验证
        if results and results[0].get('title'):
            log("✓ 提取成功", "SUCCESS")
            sys.exit(0)
        else:
            log("✗ 提取失败 - 没有标题", "ERROR")
            sys.exit(1)

if __name__ == '__main__':
    main()