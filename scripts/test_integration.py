#!/usr/bin/env python3
"""
集成测试 - 测试从提取到生成Markdown的完整流程
"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# 添加scripts目录到系统路径
sys.path.insert(0, str(Path(__file__).parent))

from wechat_extractor import extract_from_html
from markdown_generator import generate_markdown


def test_full_pipeline():
    """测试完整的处理流程"""
    print("=== 集成测试：提取到Markdown生成 ===\n")

    # 1. 准备测试HTML数据
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="og:title" content="瑞典生活：如何在斯德哥尔摩找到合适的住房">
        <meta name="author" content="瑞典马工">
    </head>
    <body>
        <div class="rich_media_content" id="js_content">
            <h1 class="rich_media_title">瑞典生活：如何在斯德哥尔摩找到合适的住房</h1>
            <em id="publish_time">2024-01-20</em>

            <p>在斯德哥尔摩找房子可能是每个新来瑞典的人面临的最大挑战之一。这个城市的住房市场竞争激烈，租金高昂，而且有着独特的排队系统。</p>

            <p><strong>住房类型</strong></p>
            <p>斯德哥尔摩的住房主要分为三种类型：</p>
            <p>1. 一手合同（Förstahandskontrakt）：这是最理想的租房形式，租客直接与房东或住房公司签订合同。</p>
            <p>2. 二手合同（Andrahandskontrakt）：从已有一手合同的租客那里转租。</p>
            <p>3. 合作公寓（Bostadsrätt）：类似于国内的商品房，需要购买。</p>

            <p><strong>排队系统</strong></p>
            <p>斯德哥尔摩有一个官方的住房排队系统，叫做Bostadsförmedlingen。注册后，每天都会积累排队天数。一般来说，要在市中心租到一手合同的公寓，需要排队8-10年。</p>

            <img data-src="https://example.com/stockholm-apartment.jpg" alt="斯德哥尔摩公寓">

            <p><strong>租金水平</strong></p>
            <p>斯德哥尔摩的租金在欧洲属于较高水平：</p>
            <p>- 单间公寓（1 rum）：8000-12000克朗/月</p>
            <p>- 一室一厅（2 rum）：10000-15000克朗/月</p>
            <p>- 两室一厅（3 rum）：12000-20000克朗/月</p>

            <p><strong>找房建议</strong></p>
            <p>1. 尽早在Bostadsförmedlingen注册排队</p>
            <p>2. 考虑郊区，交通很方便</p>
            <p>3. 加入Facebook租房群组</p>
            <p>4. 注意防范租房诈骗</p>

            <img data-src="https://example.com/subway-map.jpg" alt="斯德哥尔摩地铁图">

            <p>虽然找房不易，但斯德哥尔摩的生活质量很高，值得这份等待和努力。</p>
        </div>
    </body>
    </html>
    """

    # 2. 提取内容
    print("步骤1: 提取HTML内容...")
    extracted_data = extract_from_html(html_content, save_images=False)

    print(f"  ✓ 标题: {extracted_data['title']}")
    print(f"  ✓ 作者: {extracted_data['author']}")
    print(f"  ✓ 日期: {extracted_data['publish_date']}")
    print(f"  ✓ 内容长度: {len(extracted_data['content']['text'])} 字符")
    print(f"  ✓ 图片数量: {len(extracted_data['images'])}")

    # 3. 模拟翻译（这里直接使用中文内容）
    print("\n步骤2: 准备翻译数据...")
    translated_data = {
        **extracted_data,
        "is_translated": True,
        "original_language": "zh-CN",
        "translated_at": datetime.now().isoformat()
    }
    print("  ✓ 添加翻译元数据")

    # 4. 生成Markdown
    print("\n步骤3: 生成Markdown文件...")
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_markdown(translated_data, Path(tmpdir))

        if result['success']:
            print(f"  ✓ 生成成功")
            print(f"  ✓ 文件路径: {result['file_path']}")
            print(f"  ✓ Slug: {result['slug']}")

            # 读取生成的文件进行验证
            with open(result['file_path'], 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # 验证内容
            print("\n步骤4: 验证生成的Markdown...")
            validations = [
                ('---\ntitle:', 'YAML frontmatter'),
                ('date:', '日期字段'),
                ('category:', '类别字段'),
                ('tags:', '标签字段'),
                ('# 瑞典生活', '主标题'),
                ('住房类型', '内容保留'),
                ('![', '图片引用')
            ]

            all_valid = True
            for check, desc in validations:
                if check in markdown_content:
                    print(f"  ✓ {desc}")
                else:
                    print(f"  ✗ 缺少{desc}")
                    all_valid = False

            # 显示生成的内容预览
            print("\n=== Markdown内容预览 (前800字符) ===")
            print(markdown_content[:800])
            print("...\n")

            # 检查文件大小
            file_size = Path(result['file_path']).stat().st_size
            print(f"文件大小: {file_size} 字节")

            if all_valid:
                print("\n✅ 集成测试通过！")
                return True
            else:
                print("\n❌ 集成测试失败：部分验证未通过")
                return False
        else:
            print(f"  ✗ 生成失败: {result['errors']}")
            return False


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===\n")

    # 测试无效数据
    invalid_data = {
        "title": "",
        "content": {"text": ""}
    }

    result = generate_markdown(invalid_data)

    if not result['success'] and result['errors']:
        print("✓ 正确处理无效数据")
        print(f"  错误信息: {result['errors']}")
    else:
        print("✗ 未能正确处理无效数据")

    # 测试部分数据缺失
    partial_data = {
        "title": "测试文章",
        "author": "测试作者",
        "content": {"text": "这是测试内容" * 20}
    }

    result = generate_markdown(partial_data)

    if result['success']:
        print("\n✓ 能够处理部分数据缺失的情况")
        print(f"  使用默认值生成成功")
    else:
        print("\n✗ 无法处理部分数据缺失")


def test_special_characters():
    """测试特殊字符处理"""
    print("\n=== 测试特殊字符处理 ===\n")

    special_data = {
        "title": "特殊字符测试: <>&\"'",
        "author": "测试作者",
        "publish_date": "2024-01-20",
        "content": {
            "text": "包含特殊字符的内容: <script>alert('test')</script> & \"引号\" 'apostrophe'"
        },
        "images": []
    }

    result = generate_markdown(special_data)

    if result['success']:
        print("✓ 成功处理特殊字符")
        print(f"  生成的slug: {result['slug']}")
    else:
        print("✗ 特殊字符处理失败")


def main():
    """主测试函数"""
    print("=" * 60)
    print("集成测试套件")
    print("=" * 60)
    print()

    # 运行测试
    test_results = []

    # 完整流程测试
    test_results.append(("完整流程", test_full_pipeline()))

    # 错误处理测试
    test_error_handling()

    # 特殊字符测试
    test_special_characters()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    # 返回状态码
    all_passed = all(result[1] for result in test_results if result[1] is not None)
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()