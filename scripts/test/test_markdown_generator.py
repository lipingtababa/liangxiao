#!/usr/bin/env python3
"""
测试Markdown生成器
"""

import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime

# 添加scripts目录到系统路径
sys.path.insert(0, str(Path(__file__).parent))

from markdown_generator import (
    generate_markdown,
    sanitize_slug,
    generate_tags,
    determine_category,
    format_content_to_markdown,
    generate_frontmatter
)


def create_sample_data():
    """创建测试用的示例数据"""
    return {
        "title": "瑞典的工作生活平衡：为什么瑞典人下午3点就下班",
        "author": "瑞典马工",
        "publish_date": "2024-01-15",
        "original_url": "https://mp.weixin.qq.com/s/test123",
        "content": {
            "text": """在瑞典工作了几年，最让我惊讶的不是高福利，而是瑞典人对工作与生活平衡的极致追求。

下午3点，办公室就开始陆续有人收拾东西准备下班了。一开始我以为他们有什么急事，后来才发现这是常态。瑞典同事告诉我，他们要去接孩子、要去健身房、要去超市买菜做晚饭。

瑞典的工作文化

瑞典人相信，高效的工作不在于时间长短，而在于专注度和创造力。疲惫的员工无法产出高质量的工作成果。因此，瑞典公司普遍实行弹性工作制。

标准工作时间是每周40小时，但实际上很多人工作35-37小时。加班在瑞典是个异类行为，会被认为是工作效率低下的表现。如果你经常加班，老板不会表扬你勤奋，反而会担心你的工作方法是否有问题。

Fika文化

每天上午10点和下午3点，是瑞典人雷打不动的Fika时间。Fika就是咖啡休息时间，但它的意义远不止喝咖啡那么简单。这是同事之间交流的重要时刻，很多创意和解决方案都是在Fika时间产生的。

在Fika时间，老板和员工平等地坐在一起，聊天内容从工作到家庭，从天气到度假计划。这种轻松的氛围让团队关系更加和谐，也提高了工作效率。

带薪假期

瑞典法律规定每年至少25天带薪假期。大部分瑞典人会在7月份休假整整一个月。整个瑞典在7月份都像是按下了暂停键，很多公司和机构都处于半停工状态。

除了年假，瑞典还有各种假期：育儿假480天（父母共享）、病假、照顾生病孩子的假期等。瑞典人把休假看作是基本权利，没有人会因为休假而感到愧疚。

家庭优先

瑞典社会把家庭放在第一位。下午4点去接孩子是天经地义的事，没有人会因此质疑你的工作态度。很多会议都会避开接送孩子的时间。

瑞典爸爸推着婴儿车的场景随处可见。男性休育儿假在瑞典是常态，这不仅让妈妈们能够尽快返回职场，也让爸爸们有更多时间陪伴孩子成长。

对中国人的启示

作为在瑞典工作的中国人，适应这种工作文化需要时间。我们习惯了996，突然要下午3点下班，反而会感到不安。但逐渐地，我发现这种平衡的生活方式确实让人更快乐、更有创造力。

工作是为了生活，而不是生活为了工作。这是瑞典给我最大的启示。""",
            "html": "<div>HTML content here</div>"
        },
        "images": [
            {
                "src": "https://example.com/image1.jpg",
                "alt": "瑞典办公室",
                "local_filename": "office",
                "local_path": "/tmp/images/office.jpg"
            },
            {
                "src": "https://example.com/image2.jpg",
                "alt": "Fika时间",
                "local_filename": "fika",
                "local_path": "/tmp/images/fika.jpg"
            }
        ],
        "word_count": 850,
        "extraction_metadata": {
            "extracted_at": datetime.now().isoformat(),
            "extractor_version": "2.0.0",
            "image_count": 2
        }
    }


def test_slug_generation():
    """测试slug生成"""
    print("\n=== 测试Slug生成 ===")

    test_cases = [
        ("瑞典的工作生活平衡", "瑞典的工作生活平衡"),
        ("Hello World! 你好世界", "hello-world-你好世界"),
        ("这是一个非常非常非常非常非常非常非常长的标题需要被截断处理", None),
        ("!!!###", None),  # 特殊字符
        ("", None)  # 空标题
    ]

    for title, expected in test_cases:
        slug = sanitize_slug(title)
        print(f"  输入: '{title}'")
        print(f"  输出: '{slug}'")
        if expected and expected != slug:
            print(f"  ✗ 期望: '{expected}'")
        else:
            print(f"  ✓ 通过")
        print()


def test_tag_generation():
    """测试标签生成"""
    print("\n=== 测试标签生成 ===")

    sample_data = create_sample_data()
    tags = generate_tags(sample_data['content']['text'], sample_data['title'])

    print(f"生成的标签: {tags}")
    print(f"标签数量: {len(tags)}")

    # 验证标签
    expected_keywords = ['瑞典', '工作', '生活']
    found_keywords = [k for k in expected_keywords if any(k in tag for tag in tags)]
    print(f"包含预期关键词: {found_keywords}")

    if len(tags) > 0 and len(tags) <= 8:
        print("✓ 标签数量合理")
    else:
        print("✗ 标签数量异常")


def test_category_determination():
    """测试类别判断"""
    print("\n=== 测试类别判断 ===")

    test_cases = [
        ("瑞典教育体系介绍", "瑞典的教育...", "教育"),
        ("斯德哥尔摩美食指南", "推荐几家餐厅...", "美食"),
        ("瑞典工作文化", "在瑞典工作...", "工作"),
        ("随便聊聊", "今天天气不错", "其他")
    ]

    for title, content, expected in test_cases:
        category = determine_category(title, content)
        status = "✓" if category == expected else "✗"
        print(f"  {status} '{title}' -> {category} (期望: {expected})")


def test_markdown_generation():
    """测试完整的Markdown生成"""
    print("\n=== 测试Markdown生成 ===")

    # 创建示例数据
    sample_data = create_sample_data()

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        # 生成Markdown
        result = generate_markdown(sample_data, output_dir)

        # 检查结果
        print(f"生成成功: {result['success']}")
        print(f"文件路径: {result['file_path']}")
        print(f"Slug: {result['slug']}")

        if result['errors']:
            print(f"错误: {result['errors']}")
        if result['warnings']:
            print(f"警告: {result['warnings']}")

        # 如果成功，读取并显示生成的内容
        if result['success'] and result['file_path']:
            with open(result['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()

            print("\n--- 生成的Markdown内容预览 (前500字符) ---")
            print(content[:500])
            print("...")

            # 验证frontmatter
            if content.startswith('---\n'):
                print("\n✓ Frontmatter格式正确")
            else:
                print("\n✗ Frontmatter格式错误")

            # 检查必要元素
            checks = [
                ('title:', '标题'),
                ('date:', '日期'),
                ('tags:', '标签'),
                ('category:', '类别'),
                ('# 瑞典的工作生活平衡', '主标题')
            ]

            print("\n内容检查:")
            for check_str, desc in checks:
                if check_str in content:
                    print(f"  ✓ 包含{desc}")
                else:
                    print(f"  ✗ 缺少{desc}")


def test_batch_processing():
    """测试批量处理"""
    print("\n=== 测试批量处理 ===")

    # 创建多个示例数据
    articles = [
        create_sample_data(),
        {
            **create_sample_data(),
            "title": "瑞典的教育体系：从幼儿园到大学",
            "publish_date": "2024-01-16"
        },
        {
            **create_sample_data(),
            "title": "斯德哥尔摩地铁艺术之旅",
            "publish_date": "2024-01-17"
        }
    ]

    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        temp_file = f.name

    print(f"创建临时JSON文件: {temp_file}")
    print(f"包含 {len(articles)} 篇文章")

    # 这里只是演示，实际的批量处理需要导入batch_generate函数
    print("批量处理测试完成")

    # 清理临时文件
    Path(temp_file).unlink()


def test_edge_cases():
    """测试边缘情况"""
    print("\n=== 测试边缘情况 ===")

    # 测试空数据
    empty_data = {}
    result = generate_markdown(empty_data)
    print(f"空数据测试: {'✓ 正确处理' if not result['success'] else '✗ 未正确处理'}")
    print(f"  错误信息: {result['errors']}")

    # 测试缺少内容
    no_content_data = {
        "title": "测试标题",
        "author": "测试作者",
        "publish_date": "2024-01-15"
    }
    result = generate_markdown(no_content_data)
    print(f"\n缺少内容测试: {'✓ 正确处理' if not result['success'] else '✗ 未正确处理'}")
    print(f"  错误信息: {result['errors']}")

    # 测试超长标题
    long_title_data = {
        **create_sample_data(),
        "title": "这是一个" + "非常" * 50 + "长的标题"
    }
    result = generate_markdown(long_title_data)
    print(f"\n超长标题测试: {'✓ 生成成功' if result['success'] else '✗ 生成失败'}")
    if result['slug']:
        print(f"  生成的slug长度: {len(result['slug'])}")


def main():
    """主测试函数"""
    print("=" * 60)
    print("Markdown生成器测试套件")
    print("=" * 60)

    # 运行各项测试
    test_slug_generation()
    test_tag_generation()
    test_category_determination()
    test_markdown_generation()
    test_batch_processing()
    test_edge_cases()

    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()