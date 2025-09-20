#!/usr/bin/env python3
"""
Markdown生成器单元测试
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import sys
import json
from pathlib import Path
from datetime import datetime
import tempfile
import os
import yaml

# 添加scripts目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from markdown_generator import (
    sanitize_slug,
    generate_tags,
    determine_category,
    format_content_to_markdown,
    generate_frontmatter,
    generate_markdown,
    batch_generate
)


class TestSlugGeneration(unittest.TestCase):
    """URL slug生成测试"""

    def test_sanitize_slug_basic(self):
        """测试基本slug生成"""
        test_cases = [
            ("这是一个测试标题", "这是一个测试标题"),
            ("Title with Spaces", "title-with-spaces"),
            ("标题 With 混合 Content", "标题-with-混合-content"),
            ("Multiple   Spaces", "multiple-spaces"),
            ("Special!@#$%Characters", "specialcharacters")
        ]

        for title, expected in test_cases:
            result = sanitize_slug(title)
            self.assertEqual(result, expected)

    def test_sanitize_slug_length_limit(self):
        """测试slug长度限制"""
        long_title = "这是一个非常非常非常非常非常非常非常非常非常非常长的标题需要被截断"
        result = sanitize_slug(long_title)

        self.assertLessEqual(len(result), 50)
        self.assertFalse(result.endswith('-'))

    def test_sanitize_slug_empty_input(self):
        """测试空输入处理"""
        empty_inputs = ["", "   ", "!@#$%", "---"]

        for input_str in empty_inputs:
            result = sanitize_slug(input_str)
            self.assertTrue(result.startswith("article-"))
            self.assertIn(datetime.now().strftime('%Y%m%d'), result)


class TestTagGeneration(unittest.TestCase):
    """标签生成测试"""

    def test_generate_tags_from_content(self):
        """测试从内容生成标签"""
        content = "在瑞典斯德哥尔摩的生活，工作和教育都很好"
        title = "瑞典生活指南"

        tags = generate_tags(content, title)

        self.assertIn("瑞典", tags)
        self.assertIn("生活", tags)
        self.assertLessEqual(len(tags), 8)

    def test_generate_tags_default(self):
        """测试默认标签生成"""
        content = "没有特定关键词的内容"
        tags = generate_tags(content)

        self.assertIn("瑞典生活", tags)
        self.assertIn("Sweden Life", tags)

    def test_generate_tags_multiple_keywords(self):
        """测试多关键词标签生成"""
        content = "瑞典的科技创业环境很好，特别是在斯德哥尔摩的医疗科技领域"

        tags = generate_tags(content)

        # 应该包含多个相关标签
        self.assertTrue(any("瑞典" in tag or "Sweden" in tag for tag in tags))
        self.assertTrue(any("科技" in tag or "Technology" in tag for tag in tags))

    def test_generate_tags_deduplication(self):
        """测试标签去重"""
        content = "瑞典瑞典瑞典生活生活生活"

        tags = generate_tags(content)

        # 检查没有重复标签
        self.assertEqual(len(tags), len(set(tags)))


class TestCategoryDetermination(unittest.TestCase):
    """类别确定测试"""

    def test_determine_category_life(self):
        """测试生活类别判断"""
        title = "瑞典日常生活分享"
        content = "超市购物，居住体验，日常生活的各种细节"

        category = determine_category(title, content)
        self.assertEqual(category, "生活")

    def test_determine_category_work(self):
        """测试工作类别判断"""
        title = "瑞典求职面试经验"
        content = "公司面试流程，职场文化，工作机会"

        category = determine_category(title, content)
        self.assertEqual(category, "工作")

    def test_determine_category_education(self):
        """测试教育类别判断"""
        title = "瑞典大学申请指南"
        content = "学校选择，教育体系，学习经验"

        category = determine_category(title, content)
        self.assertEqual(category, "教育")

    def test_determine_category_default(self):
        """测试默认类别"""
        title = "随机内容"
        content = "没有明确分类的内容"

        category = determine_category(title, content)
        self.assertEqual(category, "其他")

    def test_determine_category_by_score(self):
        """测试基于分数的类别判断"""
        title = "瑞典的工作和生活"
        content = "工作机会很多，公司文化很好，职场环境优秀，但生活成本较高"

        category = determine_category(title, content)
        # 工作关键词出现更多，应该归类为工作
        self.assertEqual(category, "工作")


class TestContentFormatting(unittest.TestCase):
    """内容格式化测试"""

    def test_format_content_basic(self):
        """测试基本内容格式化"""
        content = {"text": "第一段内容。\n\n第二段内容。", "html": ""}
        images = []

        result = format_content_to_markdown(content, images)

        self.assertIn("第一段内容", result)
        self.assertIn("第二段内容", result)
        self.assertIn("\n\n", result)  # 段落分隔

    def test_format_content_with_images(self):
        """测试带图片的内容格式化"""
        content = {"text": "段落1\n\n段落2\n\n段落3\n\n段落4", "html": ""}
        images = [
            {"src": "image1.jpg", "alt": "图片1", "local_path": "/path/to/image1.jpg"},
            {"src": "image2.jpg", "alt": "图片2"}
        ]

        result = format_content_to_markdown(content, images)

        # 应该包含图片markdown
        self.assertIn("![图片1]", result)
        self.assertIn("![图片2]", result)

    @patch('markdown_generator.BeautifulSoup')
    def test_format_content_with_html(self, mock_bs):
        """测试HTML内容格式化"""
        # 模拟BeautifulSoup处理
        mock_soup = Mock()
        mock_soup.get_text.return_value = "处理后的文本内容"
        mock_soup.find_all.return_value = []
        mock_bs.return_value = mock_soup

        content = {
            "text": "原始文本",
            "html": "<p>HTML内容</p>"
        }
        images = []

        result = format_content_to_markdown(content, images)

        # 应该调用BeautifulSoup处理HTML
        mock_bs.assert_called_once()

    def test_format_content_heading_detection(self):
        """测试标题检测"""
        content = {
            "text": "短标题\n\n这是一个较长的段落内容，包含很多文字和标点符号。",
            "html": ""
        }
        images = []

        result = format_content_to_markdown(content, images)

        # 短文本应该被识别为标题
        self.assertIn("## 短标题", result)

    def test_format_content_clean_empty_lines(self):
        """测试清理多余空行"""
        content = {
            "text": "段落1\n\n\n\n\n段落2\n\n\n段落3",
            "html": ""
        }
        images = []

        result = format_content_to_markdown(content, images)

        # 不应该有超过两个连续换行
        self.assertNotIn("\n\n\n", result)


class TestFrontmatterGeneration(unittest.TestCase):
    """Frontmatter生成测试"""

    def test_generate_frontmatter_basic(self):
        """测试基本frontmatter生成"""
        data = {
            "title": "测试文章",
            "author": "测试作者",
            "publish_date": "2024-01-15",
            "original_url": "http://example.com/article",
            "content": {"text": "这是测试内容"}
        }
        slug = "test-article"

        result = generate_frontmatter(data, slug)

        # 验证YAML格式
        self.assertTrue(result.startswith("---\n"))
        self.assertTrue(result.endswith("---\n"))

        # 解析YAML内容
        yaml_content = result[4:-4]  # 去除---标记
        frontmatter = yaml.safe_load(yaml_content)

        self.assertEqual(frontmatter['title'], "测试文章")
        self.assertEqual(frontmatter['author'], "测试作者")
        self.assertEqual(frontmatter['date'], "2024-01-15")
        self.assertIn('tags', frontmatter)
        self.assertIn('category', frontmatter)
        self.assertIn('excerpt', frontmatter)

    def test_generate_frontmatter_excerpt(self):
        """测试摘要生成"""
        long_content = "这是一段非常长的内容" * 50
        data = {
            "title": "测试",
            "content": {"text": long_content}
        }

        result = generate_frontmatter(data, "test")
        yaml_content = result[4:-4]
        frontmatter = yaml.safe_load(yaml_content)

        # 摘要应该被截断
        self.assertLessEqual(len(frontmatter['excerpt']), 153)
        self.assertTrue(frontmatter['excerpt'].endswith('...'))

    def test_generate_frontmatter_translated(self):
        """测试翻译文章的frontmatter"""
        data = {
            "title": "测试",
            "content": {"text": "内容"},
            "is_translated": True,
            "original_language": "zh-CN",
            "translated_at": "2024-01-15T10:00:00"
        }

        result = generate_frontmatter(data, "test")
        yaml_content = result[4:-4]
        frontmatter = yaml.safe_load(yaml_content)

        self.assertTrue(frontmatter['translated'])
        self.assertEqual(frontmatter['originalLanguage'], "zh-CN")
        self.assertEqual(frontmatter['translatedAt'], "2024-01-15T10:00:00")


class TestMarkdownGeneration(unittest.TestCase):
    """完整Markdown生成测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_generate_markdown_success(self):
        """测试成功生成Markdown"""
        data = {
            "title": "测试文章",
            "author": "作者",
            "publish_date": "2024-01-15",
            "content": {"text": "测试内容"},
            "images": []
        }

        result = generate_markdown(data)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['slug'])
        self.assertIn('content', result)
        self.assertIn('metadata', result)

        # 验证生成的内容
        content = result['content']
        self.assertIn("# 测试文章", content)
        self.assertIn("测试内容", content)

    def test_generate_markdown_missing_title(self):
        """测试缺少标题时的处理"""
        data = {
            "content": {"text": "测试内容"}
        }

        result = generate_markdown(data)

        self.assertFalse(result['success'])
        self.assertIn("缺少文章标题", result['errors'])

    def test_generate_markdown_missing_content(self):
        """测试缺少内容时的处理"""
        data = {
            "title": "测试标题"
        }

        result = generate_markdown(data)

        self.assertFalse(result['success'])
        self.assertIn("缺少文章内容", result['errors'])

    def test_generate_markdown_with_file_output(self):
        """测试文件输出"""
        data = {
            "title": "测试文章",
            "content": {"text": "测试内容"},
            "images": []
        }

        output_dir = Path(self.temp_dir)
        result = generate_markdown(data, output_dir)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['file_path'])

        # 验证文件存在
        file_path = Path(result['file_path'])
        self.assertTrue(file_path.exists())

        # 验证文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("测试文章", content)
            self.assertIn("测试内容", content)

    def test_generate_markdown_with_images(self):
        """测试带图片的Markdown生成"""
        data = {
            "title": "带图片的文章",
            "content": {"text": "内容"},
            "images": [
                {"src": "http://example.com/image1.jpg", "alt": "图片1"},
                {"src": "http://example.com/image2.jpg", "alt": "图片2",
                 "local_path": "/tmp/image2.jpg"}
            ]
        }

        result = generate_markdown(data)

        self.assertTrue(result['success'])
        self.assertEqual(result['metadata']['image_count'], 2)

        content = result['content']
        self.assertIn("![图片1]", content)
        self.assertIn("![图片2]", content)

    def test_generate_markdown_with_original_url(self):
        """测试包含原文链接的Markdown生成"""
        data = {
            "title": "测试文章",
            "content": {"text": "内容"},
            "original_url": "http://example.com/original"
        }

        result = generate_markdown(data)

        content = result['content']
        self.assertIn("原文链接", content)
        self.assertIn("http://example.com/original", content)
        self.assertIn("瑞典马工", content)


class TestBatchGeneration(unittest.TestCase):
    """批量生成测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.json_file = os.path.join(self.temp_dir, 'articles.json')

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_batch_generate_multiple_articles(self):
        """测试批量生成多篇文章"""
        articles = [
            {"title": "文章1", "content": {"text": "内容1"}},
            {"title": "文章2", "content": {"text": "内容2"}},
            {"title": "文章3", "content": {"text": "内容3"}}
        ]

        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f)

        results = batch_generate(self.json_file, self.temp_dir)

        self.assertEqual(len(results), 3)
        success_count = sum(1 for r in results if r['success'])
        self.assertEqual(success_count, 3)

    def test_batch_generate_single_article(self):
        """测试单篇文章的批量处理"""
        article = {"title": "单篇文章", "content": {"text": "内容"}}

        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(article, f)

        results = batch_generate(self.json_file, self.temp_dir)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['success'])

    def test_batch_generate_with_failures(self):
        """测试包含失败的批量生成"""
        articles = [
            {"title": "正常文章", "content": {"text": "内容"}},
            {"content": {"text": "缺少标题"}},  # 会失败
            {"title": "缺少内容"}  # 会失败
        ]

        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f)

        results = batch_generate(self.json_file, self.temp_dir)

        self.assertEqual(len(results), 3)
        success_count = sum(1 for r in results if r['success'])
        fail_count = sum(1 for r in results if not r['success'])
        self.assertEqual(success_count, 1)
        self.assertEqual(fail_count, 2)

    def test_batch_generate_file_not_found(self):
        """测试文件不存在的错误处理"""
        results = batch_generate("nonexistent.json", self.temp_dir)
        self.assertEqual(len(results), 0)


class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""

    def test_generate_markdown_exception_handling(self):
        """测试异常处理"""
        data = {
            "title": "测试",
            "content": {"text": "内容"}
        }

        # 模拟异常
        with patch('markdown_generator.generate_frontmatter', side_effect=Exception("测试错误")):
            result = generate_markdown(data)

            self.assertFalse(result['success'])
            self.assertIn("测试错误", str(result['errors']))

    def test_file_exists_warning(self):
        """测试文件存在警告"""
        temp_dir = tempfile.mkdtemp()

        try:
            data = {
                "title": "测试文章",
                "content": {"text": "内容"}
            }

            # 第一次生成
            result1 = generate_markdown(data, Path(temp_dir))
            self.assertTrue(result1['success'])

            # 第二次生成相同文件
            result2 = generate_markdown(data, Path(temp_dir))
            self.assertTrue(result2['success'])
            self.assertIn("文件已存在", str(result2['warnings']))

        finally:
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)