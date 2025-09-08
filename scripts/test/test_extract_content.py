#!/usr/bin/env python3
"""
提取内容模块的单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加父目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract_content_starter import ContentExtractor, ContentStorage

class TestContentExtractor(unittest.TestCase):
    """内容提取器测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.extractor = ContentExtractor()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.extractor)
        self.assertEqual(self.extractor.image_counter, 0)
    
    @patch('extract_content_starter.requests.get')
    def test_fetch_article_success(self, mock_get):
        """测试成功获取文章"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>测试内容</body></html>'
        mock_get.return_value = mock_response
        
        content = self.extractor.fetch_article('https://example.com/article')
        
        self.assertEqual(content, '<html><body>测试内容</body></html>')
        mock_get.assert_called_once_with('https://example.com/article', headers=self.extractor.headers)
    
    @patch('extract_content_starter.requests.get')
    def test_fetch_article_failure(self, mock_get):
        """测试获取文章失败"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        content = self.extractor.fetch_article('https://example.com/not-found')
        
        self.assertIsNone(content)
    
    def test_extract_title(self):
        """测试提取标题"""
        html = '''
        <html>
            <head>
                <meta property="og:title" content="测试文章标题">
            </head>
            <body>
                <h1 id="activity-name">备用标题</h1>
            </body>
        </html>
        '''
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        title = self.extractor.extract_title(soup)
        
        self.assertEqual(title, '测试文章标题')
    
    def test_extract_title_fallback(self):
        """测试提取标题的后备方案"""
        html = '''
        <html>
            <body>
                <h1 id="activity-name">备用标题</h1>
            </body>
        </html>
        '''
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        title = self.extractor.extract_title(soup)
        
        self.assertEqual(title, '备用标题')


class TestContentStorage(unittest.TestCase):
    """内容存储测试类"""
    
    def setUp(self):
        """测试前的设置"""
        self.storage = ContentStorage()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.storage)
    
    @patch('extract_content_starter.os.makedirs')
    def test_ensure_directory(self, mock_makedirs):
        """测试确保目录存在"""
        self.storage.ensure_directory('test_dir')
        mock_makedirs.assert_called_once_with('test_dir', exist_ok=True)
    
    @patch('builtins.open', create=True)
    @patch('extract_content_starter.os.makedirs')
    def test_save_markdown(self, mock_makedirs, mock_open):
        """测试保存Markdown文件"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        content = {
            'title': '测试标题',
            'author': '测试作者',
            'date': '2024-01-01',
            'content': '测试内容',
            'original_url': 'https://example.com'
        }
        
        filename = self.storage.save_markdown(content, 'posts')
        
        self.assertIn('test-title', filename)
        mock_makedirs.assert_called_once_with('posts', exist_ok=True)
        mock_file.write.assert_called()


if __name__ == '__main__':
    unittest.main()