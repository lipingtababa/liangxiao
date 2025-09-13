#!/usr/bin/env python3
"""
微信文章提取器的单元测试
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
from pathlib import Path

# 添加父目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wechat_extractor import extract_from_html, extract_from_url, clean_text, download_image

class TestWeChatExtractor(unittest.TestCase):
    """微信文章提取器测试类"""

    def test_clean_text(self):
        """测试文本清理功能"""
        # 测试多余空白字符清理
        text = "  测试  文本  \n\n  内容  "
        result = clean_text(text)
        self.assertEqual(result, "测试 文本 内容")

        # 测试空文本
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")

    def test_extract_from_html_title(self):
        """测试从HTML提取标题"""
        html = '''
        <html>
            <head>
                <meta property="og:title" content="测试文章标题">
            </head>
            <body>
                <h1 class="rich_media_title">文章标题</h1>
            </body>
        </html>
        '''
        result = extract_from_html(html, save_images=False)
        self.assertEqual(result['title'], '文章标题')

    def test_extract_from_html_author(self):
        """测试从HTML提取作者"""
        html = '''
        <html>
            <body>
                <span class="rich_media_meta rich_media_meta_nickname">测试作者</span>
            </body>
        </html>
        '''
        result = extract_from_html(html, save_images=False)
        self.assertEqual(result['author'], '测试作者')

    def test_extract_from_html_date(self):
        """测试从HTML提取日期"""
        html = '''
        <html>
            <body>
                <em id="publish_time">2024-01-15</em>
            </body>
        </html>
        '''
        result = extract_from_html(html, save_images=False)
        self.assertEqual(result['publish_date'], '2024-01-15')

    def test_extract_from_html_content(self):
        """测试从HTML提取内容"""
        html = '''
        <html>
            <body>
                <div id="js_content">
                    <p>第一段内容</p>
                    <p>第二段内容</p>
                    <section>
                        <p>第三段内容</p>
                    </section>
                </div>
            </body>
        </html>
        '''
        result = extract_from_html(html, save_images=False)
        self.assertIn('第一段内容', result['content']['text'])
        self.assertIn('第二段内容', result['content']['text'])
        self.assertIn('第三段内容', result['content']['text'])
        self.assertIn('<div id="js_content">', result['content']['html'])

    def test_extract_from_html_images(self):
        """测试从HTML提取图片"""
        html = '''
        <html>
            <body>
                <div id="js_content">
                    <img data-src="https://example.com/image1.jpg" alt="图片1">
                    <img src="https://example.com/image2.jpg" alt="图片2">
                </div>
            </body>
        </html>
        '''
        result = extract_from_html(html, save_images=False)
        self.assertEqual(len(result['images']), 2)
        self.assertEqual(result['images'][0]['src'], 'https://example.com/image1.jpg')
        self.assertEqual(result['images'][0]['alt'], '图片1')
        self.assertEqual(result['images'][1]['src'], 'https://example.com/image2.jpg')
        self.assertEqual(result['images'][1]['alt'], '图片2')

    def test_extract_chinese_date_format(self):
        """测试中文日期格式提取"""
        html = '''
        <html>
            <body>
                <em id="publish_time">2024年1月15日</em>
            </body>
        </html>
        '''
        result = extract_from_html(html, save_images=False)
        self.assertEqual(result['publish_date'], '2024-01-15')

    @patch('wechat_extractor.requests.get')
    def test_download_image_success(self, mock_get):
        """测试成功下载图片"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content = MagicMock(return_value=[b'fake_image_data'])
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # 创建临时目录
        temp_dir = Path('/tmp/test_images')

        # 使用mock_open模拟文件写入
        with patch('builtins.open', mock_open()) as m:
            result = download_image('https://example.com/test.jpg', temp_dir, 'test_image')

            # 验证文件被打开以写入
            m.assert_called_once()
            # 验证写入了数据
            m().write.assert_called_with(b'fake_image_data')

    @patch('wechat_extractor.requests.get')
    def test_download_image_failure(self, mock_get):
        """测试下载图片失败"""
        mock_get.side_effect = Exception('Network error')

        temp_dir = Path('/tmp/test_images')
        result = download_image('https://example.com/test.jpg', temp_dir, 'test_image')

        self.assertIsNone(result)

    @patch('wechat_extractor.requests.get')
    def test_extract_from_url_success(self, mock_get):
        """测试从URL成功提取"""
        html = '''
        <html>
            <body>
                <h1 class="rich_media_title">测试标题</h1>
                <div id="js_content">
                    <p>测试内容</p>
                </div>
            </body>
        </html>
        '''

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_response.apparent_encoding = 'utf-8'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = extract_from_url('https://mp.weixin.qq.com/s/test', save_images=False)

        self.assertEqual(result['title'], '测试标题')
        self.assertIn('测试内容', result['content']['text'])
        self.assertEqual(result['original_url'], 'https://mp.weixin.qq.com/s/test')

    @patch('wechat_extractor.requests.get')
    def test_extract_from_url_network_error(self, mock_get):
        """测试网络错误处理"""
        mock_get.side_effect = Exception('Network error')

        result = extract_from_url('https://mp.weixin.qq.com/s/test', save_images=False)

        self.assertIn('error', result)
        self.assertEqual(result['title'], '')
        self.assertEqual(result['content']['text'], '')

    def test_extract_metadata(self):
        """测试元数据提取"""
        html = '''
        <html>
            <body>
                <h1 class="rich_media_title">测试标题</h1>
            </body>
        </html>
        '''

        result = extract_from_html(html, save_images=False)

        self.assertIn('extraction_metadata', result)
        self.assertIn('extracted_at', result['extraction_metadata'])
        self.assertEqual(result['extraction_metadata']['extractor_version'], '2.0.0')
        self.assertEqual(result['extraction_metadata']['image_count'], 0)
        self.assertFalse(result['extraction_metadata']['images_downloaded'])

if __name__ == '__main__':
    unittest.main()