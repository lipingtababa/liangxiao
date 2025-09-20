#!/usr/bin/env python3
"""
状态管理器单元测试
"""

import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import os

# 添加scripts目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from state_manager import ArticleStateManager


class TestArticleStateManager(unittest.TestCase):
    """状态管理器基础功能测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.state_file_path = self.temp_file.name
        self.manager = ArticleStateManager(self.state_file_path)

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.state_file_path):
            os.unlink(self.state_file_path)

    def test_initialize_new_state_file(self):
        """测试初始化新的状态文件"""
        # 删除文件以测试新建
        os.unlink(self.state_file_path)
        manager = ArticleStateManager(self.state_file_path)

        self.assertEqual(manager.state_data['version'], ArticleStateManager.SCHEMA_VERSION)
        self.assertIn('created_at', manager.state_data)
        self.assertIn('articles', manager.state_data)
        self.assertIn('statistics', manager.state_data)

    def test_load_existing_state_file(self):
        """测试加载现有状态文件"""
        # 创建一个状态文件
        state_data = {
            "version": ArticleStateManager.SCHEMA_VERSION,
            "articles": {"test_url": {"title": "测试"}},
            "statistics": {"total_processed": 1}
        }

        with open(self.state_file_path, 'w', encoding='utf-8') as f:
            json.dump(state_data, f)

        manager = ArticleStateManager(self.state_file_path)
        self.assertEqual(manager.state_data['articles']['test_url']['title'], "测试")
        self.assertEqual(manager.state_data['statistics']['total_processed'], 1)

    def test_save_state(self):
        """测试保存状态"""
        self.manager.state_data['test_key'] = 'test_value'
        result = self.manager._save_state()

        self.assertTrue(result)

        # 重新加载并验证
        with open(self.state_file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data['test_key'], 'test_value')
        self.assertIn('last_updated', saved_data)

    def test_calculate_content_hash(self):
        """测试内容哈希计算"""
        content1 = "这是测试内容"
        content2 = "这是测试内容"
        content3 = "这是不同的内容"

        hash1 = self.manager._calculate_content_hash(content1)
        hash2 = self.manager._calculate_content_hash(content2)
        hash3 = self.manager._calculate_content_hash(content3)

        # 相同内容应该有相同哈希
        self.assertEqual(hash1, hash2)
        # 不同内容应该有不同哈希
        self.assertNotEqual(hash1, hash3)
        # 哈希应该是64字符的十六进制字符串（SHA256）
        self.assertEqual(len(hash1), 64)


class TestArticleProcessing(unittest.TestCase):
    """文章处理功能测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.state_file_path = self.temp_file.name
        self.manager = ArticleStateManager(self.state_file_path)

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.state_file_path):
            os.unlink(self.state_file_path)

    def test_is_article_processed(self):
        """测试检查文章是否已处理"""
        url = "http://example.com/article1"

        # 初始应该未处理
        self.assertFalse(self.manager.is_article_processed(url))

        # 添加文章后应该已处理
        article_data = {
            "title": "测试文章",
            "content": {"text": "测试内容"},
            "author": "作者"
        }
        self.manager.add_article(url, article_data)
        self.assertTrue(self.manager.is_article_processed(url))

    def test_needs_update(self):
        """测试检查文章是否需要更新"""
        url = "http://example.com/article1"
        content1 = "原始内容"
        content2 = "更新后的内容"

        # 未处理的文章需要更新
        self.assertTrue(self.manager.needs_update(url, content1))

        # 添加文章
        article_data = {
            "title": "测试",
            "content": {"text": content1}
        }
        self.manager.add_article(url, article_data)

        # 相同内容不需要更新
        self.assertFalse(self.manager.needs_update(url, content1))

        # 不同内容需要更新
        self.assertTrue(self.manager.needs_update(url, content2))

    def test_add_article_new(self):
        """测试添加新文章"""
        url = "http://example.com/article1"
        article_data = {
            "title": "测试文章",
            "author": "测试作者",
            "publish_date": "2024-01-15",
            "content": {"text": "测试内容"},
            "word_count": 100,
            "images": [{"src": "image1.jpg"}, {"src": "image2.jpg"}]
        }

        result = self.manager.add_article(url, article_data)

        self.assertTrue(result)
        self.assertIn(url, self.manager.state_data['articles'])

        article_state = self.manager.state_data['articles'][url]
        self.assertEqual(article_state['title'], "测试文章")
        self.assertEqual(article_state['author'], "测试作者")
        self.assertEqual(article_state['image_count'], 2)
        self.assertEqual(article_state['status'], "completed")
        self.assertEqual(article_state['process_count'], 1)
        self.assertIsNotNone(article_state['content_hash'])

    def test_add_article_update(self):
        """测试更新已存在的文章"""
        url = "http://example.com/article1"

        # 第一次添加
        article_data1 = {
            "title": "原始标题",
            "content": {"text": "原始内容"}
        }
        self.manager.add_article(url, article_data1)

        # 记录第一次处理时间
        first_processed_at = self.manager.state_data['articles'][url]['first_processed_at']

        # 第二次添加（更新）
        article_data2 = {
            "title": "更新后的标题",
            "content": {"text": "更新后的内容"}
        }
        self.manager.add_article(url, article_data2)

        article_state = self.manager.state_data['articles'][url]
        self.assertEqual(article_state['title'], "更新后的标题")
        self.assertEqual(article_state['process_count'], 2)
        self.assertEqual(article_state['first_processed_at'], first_processed_at)
        self.assertNotEqual(article_state['last_processed_at'], first_processed_at)

    def test_mark_article_error(self):
        """测试标记文章错误"""
        url = "http://example.com/article1"
        error_message = "网络请求失败"

        result = self.manager.mark_article_error(url, error_message)

        self.assertTrue(result)
        self.assertIn(url, self.manager.state_data['articles'])

        article_state = self.manager.state_data['articles'][url]
        self.assertEqual(article_state['status'], "error")
        self.assertEqual(article_state['error'], error_message)

    def test_mark_existing_article_error(self):
        """测试标记已存在文章的错误"""
        url = "http://example.com/article1"

        # 先添加成功的文章
        article_data = {
            "title": "测试文章",
            "content": {"text": "测试内容"}
        }
        self.manager.add_article(url, article_data)

        # 然后标记为错误
        self.manager.mark_article_error(url, "处理失败")

        article_state = self.manager.state_data['articles'][url]
        self.assertEqual(article_state['status'], "error")
        self.assertEqual(article_state['error'], "处理失败")


class TestBatchOperations(unittest.TestCase):
    """批量操作测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.state_file_path = self.temp_file.name
        self.manager = ArticleStateManager(self.state_file_path)

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.state_file_path):
            os.unlink(self.state_file_path)

    def test_get_unprocessed_urls(self):
        """测试获取未处理的URL列表"""
        # 添加一些已处理的文章
        processed_urls = ["http://example.com/1", "http://example.com/2"]
        for url in processed_urls:
            self.manager.add_article(url, {"title": "测试", "content": {"text": "内容"}})

        # 测试URL列表
        test_urls = [
            "http://example.com/1",  # 已处理
            "http://example.com/2",  # 已处理
            "http://example.com/3",  # 未处理
            "http://example.com/4"   # 未处理
        ]

        unprocessed = self.manager.get_unprocessed_urls(test_urls)

        self.assertEqual(len(unprocessed), 2)
        self.assertIn("http://example.com/3", unprocessed)
        self.assertIn("http://example.com/4", unprocessed)

    def test_get_urls_needing_update(self):
        """测试获取需要更新的URL列表"""
        # 添加文章
        url = "http://example.com/1"
        self.manager.add_article(url, {
            "title": "测试",
            "content": {"text": "原始内容"}
        })

        # 测试文章列表
        articles = [
            {"url": url, "content": {"text": "原始内容"}},  # 无需更新
            {"url": "http://example.com/2", "content": {"text": "新内容"}},  # 需要更新（新文章）
            {"original_url": url, "content": {"text": "更新内容"}}  # 需要更新（内容变化）
        ]

        urls_to_update = self.manager.get_urls_needing_update(articles)

        self.assertEqual(len(urls_to_update), 2)

    def test_get_statistics(self):
        """测试获取统计信息"""
        # 添加各种状态的文章
        self.manager.add_article("http://example.com/1", {
            "title": "成功1",
            "content": {"text": "内容1"}
        })
        self.manager.add_article("http://example.com/2", {
            "title": "成功2",
            "content": {"text": "内容2"}
        })
        self.manager.mark_article_error("http://example.com/3", "错误")

        stats = self.manager.get_statistics()

        self.assertEqual(stats['total_articles'], 3)
        self.assertEqual(stats['successful_articles'], 2)
        self.assertEqual(stats['error_articles'], 1)

    def test_remove_article(self):
        """测试移除文章"""
        url = "http://example.com/1"
        self.manager.add_article(url, {"title": "测试", "content": {"text": "内容"}})

        # 验证文章存在
        self.assertTrue(self.manager.is_article_processed(url))

        # 移除文章
        result = self.manager.remove_article(url)
        self.assertTrue(result)

        # 验证文章已移除
        self.assertFalse(self.manager.is_article_processed(url))

    def test_remove_nonexistent_article(self):
        """测试移除不存在的文章"""
        result = self.manager.remove_article("http://example.com/nonexistent")
        self.assertTrue(result)  # 应该返回True（幂等操作）

    def test_get_article_state(self):
        """测试获取文章状态"""
        url = "http://example.com/1"
        article_data = {
            "title": "测试文章",
            "author": "作者",
            "content": {"text": "内容"}
        }
        self.manager.add_article(url, article_data)

        state = self.manager.get_article_state(url)

        self.assertIsNotNone(state)
        self.assertEqual(state['title'], "测试文章")
        self.assertEqual(state['author'], "作者")
        self.assertEqual(state['status'], "completed")

        # 测试不存在的文章
        state = self.manager.get_article_state("http://example.com/nonexistent")
        self.assertIsNone(state)


class TestCleanupOperations(unittest.TestCase):
    """清理操作测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.state_file_path = self.temp_file.name
        self.manager = ArticleStateManager(self.state_file_path)

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.state_file_path):
            os.unlink(self.state_file_path)

    def test_cleanup_old_entries(self):
        """测试清理旧条目"""
        # 创建不同时间的文章
        now = datetime.now()
        old_date = (now - timedelta(days=40)).isoformat()
        recent_date = (now - timedelta(days=10)).isoformat()

        # 手动设置文章状态
        self.manager.state_data['articles'] = {
            "old_article": {
                "title": "旧文章",
                "last_processed_at": old_date,
                "status": "completed"
            },
            "recent_article": {
                "title": "新文章",
                "last_processed_at": recent_date,
                "status": "completed"
            }
        }
        self.manager._save_state()

        # 清理30天前的条目
        removed_count = self.manager.cleanup_old_entries(30)

        self.assertEqual(removed_count, 1)
        self.assertNotIn("old_article", self.manager.state_data['articles'])
        self.assertIn("recent_article", self.manager.state_data['articles'])

    def test_cleanup_with_invalid_dates(self):
        """测试处理无效日期的清理"""
        # 添加具有无效日期的文章
        self.manager.state_data['articles'] = {
            "invalid_date": {
                "title": "无效日期",
                "last_processed_at": "invalid_date",
                "status": "completed"
            },
            "no_date": {
                "title": "无日期",
                "status": "completed"
            }
        }
        self.manager._save_state()

        # 清理操作不应该失败
        removed_count = self.manager.cleanup_old_entries(30)

        # 无效日期的文章不应该被删除
        self.assertEqual(removed_count, 0)
        self.assertIn("invalid_date", self.manager.state_data['articles'])
        self.assertIn("no_date", self.manager.state_data['articles'])


class TestConcurrency(unittest.TestCase):
    """并发操作测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.state_file_path = self.temp_file.name
        self.manager = ArticleStateManager(self.state_file_path)

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.state_file_path):
            os.unlink(self.state_file_path)

    @patch('fcntl.flock')
    def test_file_locking(self, mock_flock):
        """测试文件锁机制"""
        import fcntl

        self.manager.state_data['test'] = 'value'
        self.manager._save_state()

        # 验证文件锁被调用
        mock_flock.assert_any_call(unittest.mock.ANY, fcntl.LOCK_EX)
        mock_flock.assert_any_call(unittest.mock.ANY, fcntl.LOCK_UN)

    def test_atomic_file_replacement(self):
        """测试原子性文件替换"""
        # 添加数据
        self.manager.state_data['test'] = 'value1'
        self.manager._save_state()

        # 模拟并发写入
        manager2 = ArticleStateManager(self.state_file_path)
        manager2.state_data['test'] = 'value2'
        manager2._save_state()

        # 重新加载并验证最后的写入生效
        manager3 = ArticleStateManager(self.state_file_path)
        self.assertEqual(manager3.state_data['test'], 'value2')


class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""

    def test_load_corrupted_json(self):
        """测试加载损坏的JSON文件"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write("{ invalid json }")
        temp_file.close()

        try:
            manager = ArticleStateManager(temp_file.name)
            # 应该返回默认结构
            self.assertIn('version', manager.state_data)
            self.assertIn('articles', manager.state_data)
        finally:
            os.unlink(temp_file.name)

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_permission_error(self, mock_open):
        """测试保存时的权限错误"""
        # 创建临时管理器
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()

        try:
            manager = ArticleStateManager(temp_file.name)
            # 模拟保存失败
            result = manager._save_state()
            self.assertFalse(result)
        finally:
            os.unlink(temp_file.name)

    def test_version_mismatch_warning(self):
        """测试版本不匹配警告"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)

        # 写入不同版本的状态文件
        state_data = {
            "version": "0.9.0",
            "articles": {},
            "statistics": {}
        }
        json.dump(state_data, temp_file)
        temp_file.close()

        with patch('builtins.print') as mock_print:
            manager = ArticleStateManager(temp_file.name)
            # 应该打印警告
            mock_print.assert_called()
            warning_msg = mock_print.call_args[0][0]
            self.assertIn("版本", warning_msg)

        os.unlink(temp_file.name)


if __name__ == '__main__':
    unittest.main(verbosity=2)