#!/usr/bin/env python3
"""
测试微信文章提取器
"""

import sys
from pathlib import Path
from wechat_extractor import extract_from_html

def test_extraction():
    """测试提取功能"""
    # 读取测试HTML
    test_file = Path(__file__).parent / "test_article.html"
    with open(test_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 测试提取
    result = extract_from_html(html_content, save_images=False)

    # 验证结果
    print("测试结果:")
    print("-" * 50)

    # 检查标题
    assert result['title'] == "测试文章：瑞典生活指南", f"标题提取失败: {result['title']}"
    print(f"✓ 标题: {result['title']}")

    # 检查作者
    assert result['author'] == "瑞典马工", f"作者提取失败: {result['author']}"
    print(f"✓ 作者: {result['author']}")

    # 检查日期
    assert result['publish_date'] == "2024-01-15", f"日期提取失败: {result['publish_date']}"
    print(f"✓ 发布日期: {result['publish_date']}")

    # 检查内容
    content_text = result['content']['text']
    assert "瑞典生活" in content_text, "内容提取失败"
    assert "北欧国家" in content_text, "内容提取不完整"
    print(f"✓ 内容长度: {len(content_text)} 字符")

    # 检查图片
    assert len(result['images']) == 2, f"图片数量不正确: {len(result['images'])}"
    print(f"✓ 图片数量: {len(result['images'])}")

    # 检查图片信息
    for i, img in enumerate(result['images'], 1):
        assert 'src' in img, f"图片{i}缺少src"
        assert 'alt' in img, f"图片{i}缺少alt"
        print(f"  - 图片{i}: {img['alt']} ({img['src']})")

    print("-" * 50)
    print("✅ 所有测试通过!")
    return True

if __name__ == '__main__':
    try:
        success = test_extraction()
        sys.exit(0 if success else 1)
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)