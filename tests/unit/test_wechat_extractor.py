#!/usr/bin/env python3
"""
微信文章内容提取器单元测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加scripts目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from wechat_extractor import (
    clean_text,
    download_image,
    extract_from_html,
    extract_from_url,
    sanitize_slug,
    generate_tags,
    determine_category
)


class TestTextProcessing(unittest.TestCase):
    """文本处理功能测试"""

    def test_clean_text_removes_whitespace(self):
        """测试去除多余空白字符"""
        input_text = "  这是   一段   文本  \n\n  带有多余空白  "
        expected = "这是 一段 文本 带有多余空白"
        self.assertEqual(clean_text(input_text), expected)

    def test_clean_text_handles_empty_string(self):
        """测试处理空字符串"""
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")

    def test_clean_text_preserves_chinese_characters(self):
        """测试保留中文字符"""
        input_text = "瑞典马工 - 生活在斯德哥尔摩"
        expected = "瑞典马工 - 生活在斯德哥尔摩"
        self.assertEqual(clean_text(input_text), expected)


class TestImageDownload(unittest.TestCase):
    """图片下载功能测试"""

    @patch('wechat_extractor.requests.get')
    def test_download_image_success(self, mock_get):
        """测试成功下载图片"""
        # 模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content = Mock(return_value=[b'fake_image_data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 测试下载
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            save_dir = Path('/tmp/test_images')
            result = download_image('http://example.com/image.jpg', save_dir, 'test_image')

            # 验证结果
            self.assertIsNotNone(result)
            mock_file.write.assert_called_with(b'fake_image_data')

    @patch('wechat_extractor.requests.get')
    def test_download_image_network_error(self, mock_get):
        """测试网络错误处理"""
        mock_get.side_effect = Exception("Network error")

        save_dir = Path('/tmp/test_images')
        result = download_image('http://example.com/image.jpg', save_dir, 'test_image')

        self.assertIsNone(result)

    @patch('wechat_extractor.requests.get')
    def test_download_image_content_type_detection(self, mock_get):
        """测试图片类型检测"""
        test_cases = [
            ('image/png', '.png'),
            ('image/gif', '.gif'),
            ('image/webp', '.webp'),
            ('image/jpeg', '.jpg'),
            ('unknown/type', '.jpg')  # 默认为jpg
        ]

        for content_type, expected_ext in test_cases:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'content-type': content_type}
            mock_response.iter_content = Mock(return_value=[b'data'])
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch('builtins.open', create=True):
                save_dir = Path('/tmp/test_images')
                result = download_image('http://example.com/image', save_dir, 'test')

                if result:
                    self.assertTrue(result.endswith(expected_ext))


class TestHTMLExtraction(unittest.TestCase):
    """HTML内容提取测试"""

    def setUp(self):
        """设置测试数据"""
        self.sample_html = """
        <html>
            <head>
                <meta property="og:title" content="测试文章标题">
                <meta name="author" content="测试作者">
                <title>页面标题</title>
            </head>
            <body>
                <h1 class="rich_media_title">这是文章标题</h1>
                <span class="rich_media_meta rich_media_meta_nickname">瑞典马工</span>
                <em id="publish_time">2024-01-15</em>
                <div id="js_content">
                    <p>这是第一段内容。</p>
                    <p>这是第二段内容。</p>
                    <img data-src="http://example.com/image1.jpg" alt="图片1">
                    <img src="http://example.com/image2.jpg" alt="图片2">
                </div>
            </body>
        </html>
        """

    def test_extract_title_from_h1(self):
        """测试从h1标签提取标题"""
        result = extract_from_html(self.sample_html, save_images=False)
        self.assertEqual(result['title'], "这是文章标题")

    def test_extract_author(self):
        """测试提取作者信息"""
        result = extract_from_html(self.sample_html, save_images=False)
        self.assertEqual(result['author'], "瑞典马工")

    def test_extract_publish_date(self):
        """测试提取发布日期"""
        result = extract_from_html(self.sample_html, save_images=False)
        self.assertEqual(result['publish_date'], "2024-01-15")

    def test_extract_content_text(self):
        """测试提取正文内容"""
        result = extract_from_html(self.sample_html, save_images=False)
        self.assertIn("第一段内容", result['content']['text'])
        self.assertIn("第二段内容", result['content']['text'])

    def test_extract_images(self):
        """测试提取图片信息"""
        result = extract_from_html(self.sample_html, save_images=False)
        self.assertEqual(len(result['images']), 2)
        self.assertEqual(result['images'][0]['alt'], "图片1")
        self.assertEqual(result['images'][1]['alt'], "图片2")

    def test_extract_with_missing_elements(self):
        """测试处理缺少元素的HTML"""
        minimal_html = "<html><body><div>简单内容</div></body></html>"
        result = extract_from_html(minimal_html, save_images=False)

        # 应该有默认值
        self.assertIn('title', result)
        self.assertIn('author', result)
        self.assertIn('publish_date', result)
        self.assertIn('content', result)

    def test_extract_metadata(self):
        """测试提取元数据"""
        result = extract_from_html(self.sample_html, save_images=False)

        self.assertIn('extraction_metadata', result)
        self.assertIn('extracted_at', result['extraction_metadata'])
        self.assertIn('extractor_version', result['extraction_metadata'])
        self.assertEqual(result['extraction_metadata']['image_count'], 2)


class TestURLExtraction(unittest.TestCase):
    """URL内容提取测试"""

    @patch('wechat_extractor.requests.get')
    def test_extract_from_url_success(self, mock_get):
        """测试成功从URL提取内容"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <h1 class="rich_media_title">测试标题</h1>
            <div id="js_content">测试内容</div>
        </html>
        """
        mock_response.apparent_encoding = 'utf-8'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = extract_from_url('http://mp.weixin.qq.com/test', save_images=False)

        self.assertEqual(result['title'], "测试标题")
        self.assertIn("测试内容", result['content']['text'])
        self.assertEqual(result['original_url'], 'http://mp.weixin.qq.com/test')

    @patch('wechat_extractor.requests.get')
    def test_extract_from_url_network_error(self, mock_get):
        """测试网络错误处理"""
        mock_get.side_effect = Exception("Network error")

        result = extract_from_url('http://mp.weixin.qq.com/test', save_images=False)

        self.assertIn('error', result)
        self.assertEqual(result['title'], "")
        self.assertEqual(result['content']['text'], "")

    @patch('wechat_extractor.requests.get')
    def test_extract_from_url_anti_crawl_detection(self, mock_get):
        """测试反爬虫检测处理"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "请在微信客户端打开链接"
        mock_response.apparent_encoding = 'utf-8'
        mock_response.raise_for_status = Mock()

        # 第一次返回反爬虫页面，第二次返回正常内容
        mock_get.side_effect = [
            mock_response,
            Mock(
                status_code=200,
                text="<html><h1 class='rich_media_title'>正常内容</h1></html>",
                apparent_encoding='utf-8',
                raise_for_status=Mock()
            )
        ]

        with patch('time.sleep'):  # 跳过延迟
            result = extract_from_url('http://mp.weixin.qq.com/test', save_images=False)

            # 应该重试并获取内容
            self.assertEqual(mock_get.call_count, 2)


class TestMockMode(unittest.TestCase):
    """Mock模式测试"""

    @patch.dict('os.environ', {'GITHUB_ACTIONS': 'true'})
    def test_github_actions_mock_mode(self):
        """测试GitHub Actions中的mock模式"""
        # 创建mock文件
        mock_file_path = Path(__file__).parent.parent.parent / ".github/test-data/mock-wechat-article.html"
        mock_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(mock_file_path, 'w', encoding='utf-8') as f:
            f.write("""
            <html>
                <h1 class="rich_media_title">Mock文章标题</h1>
                <div id="js_content">Mock文章内容</div>
            </html>
            """)

        try:
            result = extract_from_url('https://mp.weixin.qq.com/s/test', save_images=False)
            self.assertEqual(result['title'], "Mock文章标题")
            self.assertIn("Mock文章内容", result['content']['text'])
        finally:
            # 清理
            if mock_file_path.exists():
                mock_file_path.unlink()


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def test_extract_from_empty_html(self):
        """测试提取空HTML"""
        result = extract_from_html("", save_images=False)
        self.assertEqual(result['title'], "")
        self.assertEqual(result['content']['text'], "")
        self.assertEqual(len(result['images']), 0)

    def test_extract_from_malformed_html(self):
        """测试提取格式错误的HTML"""
        malformed_html = "<html><h1>未闭合标题<div>内容</html>"
        result = extract_from_html(malformed_html, save_images=False)

        # 应该能够处理并返回结果
        self.assertIsNotNone(result)
        self.assertIn('title', result)
        self.assertIn('content', result)

    def test_extract_with_special_characters(self):
        """测试处理特殊字符"""
        html_with_special = """
        <html>
            <h1 class="rich_media_title">标题 & "引号" <标签></h1>
            <div id="js_content">内容 © ® ™ € ¥</div>
        </html>
        """
        result = extract_from_html(html_with_special, save_images=False)

        # 应该正确处理特殊字符
        self.assertIn("标题", result['title'])
        self.assertIn("内容", result['content']['text'])

    def test_extract_very_long_content(self):
        """测试提取超长内容"""
        long_content = "<p>" + "很长的内容" * 10000 + "</p>"
        html = f"""
        <html>
            <h1 class="rich_media_title">标题</h1>
            <div id="js_content">{long_content}</div>
        </html>
        """

        result = extract_from_html(html, save_images=False)
        self.assertGreater(len(result['content']['text']), 0)
        self.assertEqual(result['word_count'], len(result['content']['text']))


class TestPerformance(unittest.TestCase):
    """性能测试"""

    def test_extraction_performance(self):
        """测试提取性能"""
        import time

        # 创建一个复杂的HTML
        complex_html = """<html><body>"""
        for i in range(100):
            complex_html += f"""
            <div>
                <p>段落 {i}</p>
                <img src="image{i}.jpg" alt="图片{i}">
            </div>
            """
        complex_html += """</body></html>"""

        start_time = time.time()
        result = extract_from_html(complex_html, save_images=False)
        end_time = time.time()

        # 验证提取正确
        self.assertEqual(len(result['images']), 100)

        # 性能要求：应该在1秒内完成
        self.assertLess(end_time - start_time, 1.0, "提取时间超过1秒")


if __name__ == '__main__':
    unittest.main(verbosity=2)