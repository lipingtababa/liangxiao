#!/usr/bin/env python3
"""
Markdown生成器的单元测试
"""

import pytest
import sys
import tempfile
from pathlib import Path
from datetime import datetime
import yaml

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_generator import (
    sanitize_slug, generate_tags, determine_category,
    format_content_to_markdown, generate_frontmatter,
    generate_markdown, batch_generate
)


class TestMarkdownGenerator:
    """Markdown生成器测试类"""

    @pytest.fixture
    def sample_article_data(self):
        """示例文章数据"""
        return {
            "title": "瑞典生活：如何在斯德哥尔摩找房子",
            "author": "瑞典马工",
            "publish_date": "2024-01-20",
            "original_url": "https://mp.weixin.qq.com/s/example",
            "content": {
                "text": "在斯德哥尔摩找房子是一个挑战。这里有很多需要了解的事情。" * 10,
                "html": "<p>在斯德哥尔摩找房子是一个挑战。</p><p>这里有很多需要了解的事情。</p>"
            },
            "images": [
                {"src": "http://example.com/image1.jpg", "alt": "图片1", "local_path": "/images/image1.jpg"},
                {"src": "http://example.com/image2.jpg", "alt": "图片2", "local_path": "/images/image2.jpg"}
            ],
            "word_count": 200,
            "is_translated": True,
            "original_language": "zh-CN",
            "translated_at": datetime.now().isoformat()
        }

    @pytest.mark.unit
    @pytest.mark.parametrize("title,expected", [
        ("测试标题", "测试标题"),
        ("Title with Spaces", "title-with-spaces"),
        ("标题！@#包含$%^特殊&*(字符", "标题包含特殊字符"),
        ("    前后有空格    ", "前后有空格"),
        ("连续---连字符", "连续-连字符"),
        ("超长" + "标题" * 30, None),  # 超长标题会被截断
        ("", None),  # 空标题会使用时间戳
        ("---", None),  # 只有连字符会使用时间戳
    ])
    def test_sanitize_slug(self, title, expected):
        """测试slug生成"""
        slug = sanitize_slug(title)

        if expected:
            assert slug == expected
        elif expected is None:
            if title == "":
                assert slug.startswith("article-")
            elif title == "---":
                assert slug.startswith("article-")
            else:
                # 超长标题
                assert len(slug) <= 50
                assert not slug.endswith("-")

    @pytest.mark.unit
    def test_generate_tags_with_keywords(self):
        """测试基于关键词生成标签"""
        content = "在斯德哥尔摩找房子，了解瑞典的医疗系统和教育资源。"
        title = "瑞典生活指南"

        tags = generate_tags(content, title)

        assert "瑞典" in tags or "Sweden" in tags
        assert "斯德哥尔摩" in tags or "Stockholm" in tags
        assert len(tags) <= 8

    @pytest.mark.unit
    def test_generate_tags_default(self):
        """测试默认标签生成"""
        content = "这是一篇没有明显关键词的文章。"
        tags = generate_tags(content)

        assert len(tags) > 0
        assert "瑞典生活" in tags or "Sweden Life" in tags

    @pytest.mark.unit
    @pytest.mark.parametrize("title,content,expected", [
        ("工作机会", "公司面试求职", "工作"),
        ("教育资源", "学校大学学习", "教育"),
        ("美食推荐", "餐厅烹饪食物", "美食"),
        ("旅游攻略", "景点度假风景", "旅游"),
        ("科技创业", "技术互联网IT", "科技"),
        ("文化节日", "传统习俗艺术", "文化"),
        ("日常生活", "居住购物超市", "生活"),
        ("其他内容", "没有特定关键词", "其他"),
    ])
    def test_determine_category(self, title, content, expected):
        """测试类别确定"""
        category = determine_category(title, content)
        assert category == expected

    @pytest.mark.unit
    def test_format_content_to_markdown_basic(self):
        """测试基本内容格式化"""
        content = {
            "text": "第一段内容。\n\n第二段内容。\n\n第三段内容。",
            "html": ""
        }
        images = []

        markdown = format_content_to_markdown(content, images)

        assert "第一段内容" in markdown
        assert "第二段内容" in markdown
        assert "第三段内容" in markdown

    @pytest.mark.unit
    def test_format_content_with_images(self):
        """测试带图片的内容格式化"""
        content = {
            "text": "段落1。\n\n段落2。\n\n段落3。\n\n段落4。",
            "html": ""
        }
        images = [
            {"src": "http://example.com/1.jpg", "alt": "图1", "local_path": "/images/1.jpg"},
            {"src": "http://example.com/2.jpg", "alt": "图2", "local_path": "/images/2.jpg"}
        ]

        markdown = format_content_to_markdown(content, images)

        # 应该包含图片引用
        assert "![图1]" in markdown or "![图片]" in markdown
        assert "images/" in markdown

    @pytest.mark.unit
    def test_format_content_with_html(self):
        """测试HTML内容处理"""
        content = {
            "text": "",
            "html": """
            <p>段落1</p>
            <h2>标题2</h2>
            <p>段落2</p>
            <ul>
                <li>列表项1</li>
                <li>列表项2</li>
            </ul>
            """
        }
        images = []

        # 注意：如果没有BeautifulSoup，会使用简单处理
        markdown = format_content_to_markdown(content, images)
        assert len(markdown) > 0

    @pytest.mark.unit
    def test_generate_frontmatter(self, sample_article_data):
        """测试frontmatter生成"""
        slug = "test-article"
        frontmatter_str = generate_frontmatter(sample_article_data, slug)

        assert frontmatter_str.startswith("---\n")
        assert frontmatter_str.endswith("---\n")

        # 解析YAML内容
        yaml_content = frontmatter_str.replace("---\n", "")
        frontmatter = yaml.safe_load(yaml_content)

        assert frontmatter["title"] == sample_article_data["title"]
        assert frontmatter["date"] == sample_article_data["publish_date"]
        assert frontmatter["author"] == sample_article_data["author"]
        assert frontmatter["category"] in ["生活", "工作", "教育", "科技", "文化", "旅游", "美食", "其他"]
        assert len(frontmatter["tags"]) > 0
        assert "excerpt" in frontmatter
        assert "description" in frontmatter
        assert frontmatter["translated"] is True
        assert frontmatter["originalLanguage"] == "zh-CN"

    @pytest.mark.unit
    def test_generate_markdown_success(self, sample_article_data, tmpdir):
        """测试成功生成Markdown"""
        output_dir = tmpdir.mkdir("posts")
        result = generate_markdown(sample_article_data, Path(output_dir))

        assert result["success"] is True
        assert result["file_path"] is not None
        assert result["slug"] is not None
        assert len(result["errors"]) == 0

        # 验证文件存在
        file_path = Path(result["file_path"])
        assert file_path.exists()

        # 验证文件内容
        content = file_path.read_text(encoding="utf-8")
        assert "---" in content  # frontmatter
        assert sample_article_data["title"] in content
        assert "原文链接" in content

    @pytest.mark.unit
    def test_generate_markdown_missing_title(self):
        """测试缺少标题的处理"""
        data = {
            "content": {"text": "内容"}
        }
        result = generate_markdown(data)

        assert result["success"] is False
        assert "缺少文章标题" in str(result["errors"])

    @pytest.mark.unit
    def test_generate_markdown_missing_content(self):
        """测试缺少内容的处理"""
        data = {
            "title": "标题",
            "content": {"text": ""}
        }
        result = generate_markdown(data)

        assert result["success"] is False
        assert "缺少文章内容" in str(result["errors"])

    @pytest.mark.unit
    def test_generate_markdown_metadata(self, sample_article_data):
        """测试元数据生成"""
        result = generate_markdown(sample_article_data)

        assert result["success"] is True
        metadata = result["metadata"]

        assert metadata["title"] == sample_article_data["title"]
        assert metadata["author"] == sample_article_data["author"]
        assert metadata["word_count"] > 0
        assert metadata["image_count"] == 2
        assert metadata["tags_count"] > 0

    @pytest.mark.unit
    def test_batch_generate(self, sample_article_data, tmpdir):
        """测试批量生成"""
        # 创建测试JSON文件
        import json
        json_file = tmpdir.join("articles.json")

        # 创建多个文章数据
        articles = [
            {**sample_article_data, "title": f"文章{i+1}"}
            for i in range(3)
        ]

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False)

        output_dir = tmpdir.mkdir("posts")
        results = batch_generate(str(json_file), str(output_dir))

        assert len(results) == 3
        success_count = sum(1 for r in results if r["success"])
        assert success_count == 3

        # 验证文件生成
        generated_files = list(Path(output_dir).glob("*.md"))
        assert len(generated_files) == 3

    @pytest.mark.unit
    def test_special_characters_in_content(self):
        """测试内容中的特殊字符处理"""
        data = {
            "title": "测试<>&\"'特殊字符",
            "author": "作者",
            "content": {
                "text": "包含特殊字符：<script>alert('xss')</script> & \"引号\" 'apostrophe'",
                "html": ""
            },
            "images": []
        }

        result = generate_markdown(data)
        assert result["success"] is True

        # slug应该清理特殊字符
        assert "<" not in result["slug"]
        assert ">" not in result["slug"]
        assert "&" not in result["slug"]

    @pytest.mark.unit
    def test_long_content_excerpt(self):
        """测试长内容的摘要生成"""
        long_text = "这是一段很长的内容。" * 50
        data = {
            "title": "长文章",
            "author": "作者",
            "publish_date": "2024-01-20",
            "content": {"text": long_text, "html": ""},
            "images": []
        }

        frontmatter_str = generate_frontmatter(data, "long-article")
        frontmatter = yaml.safe_load(frontmatter_str.replace("---\n", ""))

        # 摘要应该被截断
        assert len(frontmatter["excerpt"]) <= 153  # 150 + "..."
        assert frontmatter["excerpt"].endswith("...")

    @pytest.mark.unit
    def test_image_path_handling(self):
        """测试图片路径处理"""
        content = {"text": "内容", "html": ""}
        images = [
            {"src": "http://example.com/1.jpg", "alt": "图1", "local_path": "/path/to/image1.jpg"},
            {"src": "http://example.com/2.jpg", "alt": "图2"},  # 没有local_path
        ]

        markdown = format_content_to_markdown(content, images)

        # 有local_path的应该使用本地路径
        assert "images/image1.jpg" in markdown or "http://example.com/1.jpg" in markdown
        # 没有local_path的应该使用原始URL
        assert "http://example.com/2.jpg" in markdown

    @pytest.mark.unit
    def test_empty_images_list(self):
        """测试空图片列表"""
        data = {
            "title": "无图片文章",
            "author": "作者",
            "content": {"text": "这是没有图片的文章内容。", "html": ""},
            "images": []
        }

        result = generate_markdown(data)
        assert result["success"] is True
        assert "![" not in result["content"]  # 不应该有图片标记


if __name__ == "__main__":
    pytest.main([__file__, "-v"])