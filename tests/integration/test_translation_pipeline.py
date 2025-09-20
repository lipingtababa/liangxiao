#!/usr/bin/env python3
"""
翻译管道集成测试
测试从文章提取到生成Markdown的完整流程
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime

# 添加scripts目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from wechat_extractor import extract_from_html, extract_from_url
from state_manager import ArticleStateManager
from markdown_generator import generate_markdown, batch_generate


class TestExtractionToMarkdownPipeline(unittest.TestCase):
    """测试从提取到Markdown生成的完整流程"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, 'state.json')

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_full_pipeline_single_article(self):
        """测试单篇文章的完整处理流程"""
        # 1. 模拟HTML内容
        html_content = """
        <html>
            <head>
                <title>测试文章</title>
            </head>
            <body>
                <h1 class="rich_media_title">瑞典生活指南</h1>
                <span class="rich_media_meta rich_media_meta_nickname">瑞典马工</span>
                <em id="publish_time">2024-01-15</em>
                <div id="js_content">
                    <p>这是关于瑞典生活的第一段内容。</p>
                    <p>这是第二段内容，介绍斯德哥尔摩的生活。</p>
                    <img data-src="http://example.com/image1.jpg" alt="瑞典风景">
                </div>
            </body>
        </html>
        """

        # 2. 提取内容
        extracted_data = extract_from_html(html_content, save_images=False)
        extracted_data['original_url'] = 'http://mp.weixin.qq.com/test'

        # 验证提取结果
        self.assertEqual(extracted_data['title'], "瑞典生活指南")
        self.assertEqual(extracted_data['author'], "瑞典马工")
        self.assertIn("第一段内容", extracted_data['content']['text'])
        self.assertEqual(len(extracted_data['images']), 1)

        # 3. 使用状态管理器记录
        state_manager = ArticleStateManager(self.state_file)
        state_manager.add_article(extracted_data['original_url'], extracted_data)

        # 验证状态记录
        self.assertTrue(state_manager.is_article_processed(extracted_data['original_url']))

        # 4. 生成Markdown
        markdown_result = generate_markdown(extracted_data, Path(self.temp_dir))

        # 验证Markdown生成
        self.assertTrue(markdown_result['success'])
        self.assertIsNotNone(markdown_result['file_path'])

        # 5. 验证生成的文件
        with open(markdown_result['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("瑞典生活指南", content)
            self.assertIn("瑞典马工", content)
            self.assertIn("第一段内容", content)
            self.assertIn("![瑞典风景]", content)

    @patch('wechat_extractor.requests.get')
    def test_full_pipeline_with_url(self, mock_get):
        """测试从URL开始的完整流程"""
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <h1 class="rich_media_title">测试标题</h1>
            <div id="js_content">
                <p>测试内容</p>
            </div>
        </html>
        """
        mock_response.apparent_encoding = 'utf-8'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 1. 从URL提取
        url = "http://mp.weixin.qq.com/s/test123"
        extracted_data = extract_from_url(url, save_images=False)

        # 2. 生成Markdown
        markdown_result = generate_markdown(extracted_data)

        # 验证结果
        self.assertTrue(markdown_result['success'])
        self.assertIn("测试标题", markdown_result['content'])
        self.assertIn("测试内容", markdown_result['content'])

    def test_pipeline_with_multiple_articles(self):
        """测试多篇文章的批量处理流程"""
        # 准备多篇文章数据
        articles = []
        for i in range(3):
            article_data = {
                "title": f"文章{i+1}",
                "author": "瑞典马工",
                "publish_date": "2024-01-15",
                "original_url": f"http://mp.weixin.qq.com/s/test{i}",
                "content": {
                    "text": f"这是第{i+1}篇文章的内容",
                    "html": f"<p>这是第{i+1}篇文章的内容</p>"
                },
                "images": [],
                "word_count": 100,
                "extraction_metadata": {
                    "extracted_at": datetime.now().isoformat(),
                    "extractor_version": "2.0.0",
                    "image_count": 0
                }
            }
            articles.append(article_data)

        # 保存到JSON文件
        json_file = os.path.join(self.temp_dir, 'articles.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        # 批量生成Markdown
        results = batch_generate(json_file, self.temp_dir)

        # 验证结果
        self.assertEqual(len(results), 3)
        for i, result in enumerate(results):
            self.assertTrue(result['success'], f"文章{i+1}生成失败")
            self.assertIsNotNone(result['file_path'])

            # 验证文件内容
            with open(result['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn(f"文章{i+1}", content)
                self.assertIn(f"第{i+1}篇文章的内容", content)


class TestStateManagementIntegration(unittest.TestCase):
    """状态管理集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, 'state.json')

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_incremental_processing(self):
        """测试增量处理功能"""
        state_manager = ArticleStateManager(self.state_file)

        # 第一批文章
        first_batch = [
            {"url": "http://example.com/1", "title": "文章1", "content": {"text": "内容1"}},
            {"url": "http://example.com/2", "title": "文章2", "content": {"text": "内容2"}}
        ]

        # 处理第一批
        for article in first_batch:
            state_manager.add_article(article['url'], article)

        # 第二批包含重复和新文章
        second_batch_urls = [
            "http://example.com/1",  # 已处理
            "http://example.com/2",  # 已处理
            "http://example.com/3",  # 新文章
            "http://example.com/4"   # 新文章
        ]

        # 获取未处理的URL
        unprocessed = state_manager.get_unprocessed_urls(second_batch_urls)

        self.assertEqual(len(unprocessed), 2)
        self.assertIn("http://example.com/3", unprocessed)
        self.assertIn("http://example.com/4", unprocessed)

    def test_content_update_detection(self):
        """测试内容更新检测"""
        state_manager = ArticleStateManager(self.state_file)

        url = "http://example.com/article"
        original_content = "原始内容"
        updated_content = "更新后的内容"

        # 添加原始文章
        state_manager.add_article(url, {
            "title": "测试",
            "content": {"text": original_content}
        })

        # 检测是否需要更新
        self.assertFalse(state_manager.needs_update(url, original_content))
        self.assertTrue(state_manager.needs_update(url, updated_content))

        # 更新文章
        state_manager.add_article(url, {
            "title": "测试-更新",
            "content": {"text": updated_content}
        })

        # 验证更新
        article_state = state_manager.get_article_state(url)
        self.assertEqual(article_state['title'], "测试-更新")
        self.assertEqual(article_state['process_count'], 2)

    def test_error_recovery(self):
        """测试错误恢复机制"""
        state_manager = ArticleStateManager(self.state_file)

        url = "http://example.com/problematic"

        # 标记为错误
        state_manager.mark_article_error(url, "处理失败")

        # 验证错误状态
        article_state = state_manager.get_article_state(url)
        self.assertEqual(article_state['status'], "error")

        # 重新处理成功
        state_manager.add_article(url, {
            "title": "重新处理成功",
            "content": {"text": "内容"}
        })

        # 验证状态恢复
        article_state = state_manager.get_article_state(url)
        self.assertEqual(article_state['status'], "completed")
        self.assertEqual(article_state['title'], "重新处理成功")


class TestTranslationIntegration(unittest.TestCase):
    """翻译功能集成测试"""

    @patch('googletrans.Translator')
    def test_translation_mock(self, mock_translator_class):
        """测试翻译功能（使用Mock）"""
        # 设置翻译Mock
        mock_translator = Mock()
        mock_result = Mock()
        mock_result.text = "This is translated content"
        mock_translator.translate.return_value = mock_result
        mock_translator_class.return_value = mock_translator

        # 原始中文内容
        chinese_content = "这是中文内容"

        # 模拟翻译过程
        translator = mock_translator_class()
        result = translator.translate(chinese_content, dest='en')

        # 验证翻译结果
        self.assertEqual(result.text, "This is translated content")
        mock_translator.translate.assert_called_once_with(chinese_content, dest='en')

    def test_translation_metadata(self):
        """测试翻译元数据处理"""
        # 准备带翻译标记的文章数据
        article_data = {
            "title": "测试文章",
            "content": {"text": "中文内容"},
            "is_translated": True,
            "original_language": "zh-CN",
            "translated_at": datetime.now().isoformat()
        }

        # 生成Markdown
        result = generate_markdown(article_data)

        # 验证frontmatter包含翻译信息
        content = result['content']
        self.assertIn("translated: true", content)
        self.assertIn("originalLanguage: zh-CN", content)


class TestImageProcessingIntegration(unittest.TestCase):
    """图片处理集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('wechat_extractor.requests.get')
    def test_image_download_and_markdown(self, mock_get):
        """测试图片下载和Markdown生成集成"""
        # 模拟图片响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content = Mock(return_value=[b'fake_image_data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # HTML带图片
        html = """
        <html>
            <h1 class="rich_media_title">带图片的文章</h1>
            <div id="js_content">
                <p>内容</p>
                <img data-src="http://example.com/image.jpg" alt="测试图片">
            </div>
        </html>
        """

        # 提取内容（模拟图片下载）
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            image_dir = Path(self.temp_dir) / 'images'
            extracted = extract_from_html(html, save_images=True, image_dir=image_dir)

        # 生成Markdown
        markdown_result = generate_markdown(extracted)

        # 验证图片引用
        self.assertIn("![测试图片]", markdown_result['content'])
        self.assertEqual(markdown_result['metadata']['image_count'], 1)


class TestEndToEndWorkflow(unittest.TestCase):
    """端到端工作流测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('wechat_extractor.requests.get')
    def test_complete_workflow(self, mock_get):
        """测试完整的端到端工作流"""
        # 1. 模拟获取微信文章
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head>
                <meta property="og:title" content="瑞典创业环境介绍">
                <meta name="author" content="瑞典马工">
            </head>
            <body>
                <h1 class="rich_media_title">瑞典创业环境介绍</h1>
                <em id="publish_time">2024-01-20</em>
                <div id="js_content">
                    <p>瑞典是欧洲最适合创业的国家之一。</p>
                    <p>斯德哥尔摩有着活跃的科技创业生态系统。</p>
                    <p>政府提供了很多支持创业的政策和资金。</p>
                </div>
            </body>
        </html>
        """
        mock_response.apparent_encoding = 'utf-8'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 2. 提取文章
        url = "http://mp.weixin.qq.com/s/startup"
        article_data = extract_from_url(url, save_images=False)

        # 3. 记录到状态管理器
        state_file = os.path.join(self.temp_dir, 'state.json')
        state_manager = ArticleStateManager(state_file)
        state_manager.add_article(url, article_data)

        # 4. 生成Markdown
        output_dir = Path(self.temp_dir) / 'posts'
        markdown_result = generate_markdown(article_data, output_dir)

        # 5. 验证整个流程
        # 验证提取
        self.assertEqual(article_data['title'], "瑞典创业环境介绍")
        self.assertIn("创业", article_data['content']['text'])

        # 验证状态管理
        self.assertTrue(state_manager.is_article_processed(url))
        stats = state_manager.get_statistics()
        self.assertEqual(stats['total_articles'], 1)
        self.assertEqual(stats['successful_articles'], 1)

        # 验证Markdown生成
        self.assertTrue(markdown_result['success'])
        self.assertTrue(Path(markdown_result['file_path']).exists())

        # 验证文件内容
        with open(markdown_result['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
            # 验证frontmatter
            self.assertIn("title: 瑞典创业环境介绍", content)
            self.assertIn("category: 科技", content)  # 应该自动分类为科技
            self.assertIn("瑞典", content)  # 标签
            # 验证内容
            self.assertIn("瑞典是欧洲最适合创业的国家之一", content)
            self.assertIn("斯德哥尔摩", content)
            # 验证原文链接
            self.assertIn(url, content)

        # 6. 验证增量处理
        # 再次处理相同URL应该跳过
        unprocessed = state_manager.get_unprocessed_urls([url])
        self.assertEqual(len(unprocessed), 0)

        # 7. 统计信息验证
        final_stats = state_manager.get_statistics()
        self.assertEqual(final_stats['total_processed'], 1)
        self.assertEqual(final_stats['total_errors'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)