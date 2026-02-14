#!/usr/bin/env python3
"""
测试本地HTML文件提取
"""

from pathlib import Path
from wechat_extractor import extract_from_html
import json

def test_local_file():
    """测试本地文件提取"""
    # 读取测试HTML
    test_file = Path(__file__).parent / "test_article.html"
    with open(test_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 提取内容，并下载图片到测试目录
    image_dir = Path(__file__).parent / "test_images"
    result = extract_from_html(html_content, save_images=True, image_dir=image_dir)
    result["original_url"] = "local_test_file"

    # 保存结果
    output_file = Path(__file__).parent / "test_local_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 提取成功!")
    print(f"标题: {result['title']}")
    print(f"作者: {result['author']}")
    print(f"日期: {result['publish_date']}")
    print(f"内容长度: {result['word_count']} 字符")
    print(f"图片数量: {len(result['images'])}")
    print(f"结果已保存到: {output_file}")

    return result

if __name__ == '__main__':
    test_local_file()