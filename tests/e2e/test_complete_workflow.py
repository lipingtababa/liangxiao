#!/usr/bin/env python3
"""
端到端测试 - 完整工作流
测试从文章URL到最终Markdown文件的完整流程
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import json
import tempfile
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# 添加scripts目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from wechat_extractor import extract_from_url
from state_manager import ArticleStateManager
from markdown_generator import generate_markdown, batch_generate


class TestCompleteWorkflow(unittest.TestCase):
    """完整工作流端到端测试"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.posts_dir = Path(self.test_dir) / 'posts'
        self.images_dir = Path(self.test_dir) / 'images'
        self.state_file = Path(self.test_dir) / 'state.json'
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('wechat_extractor.requests.get')
    def test_single_article_workflow(self, mock_get):
        """测试单篇文章的完整处理流程"""
        # 模拟微信文章HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta property="og:title" content="2024年瑞典移民新政策解读">
            <meta property="og:description" content="详细解读2024年瑞典移民政策的最新变化">
            <meta name="author" content="瑞典马工">
        </head>
        <body>
            <div class="rich_media">
                <h1 class="rich_media_title">2024年瑞典移民新政策解读</h1>
                <div class="rich_media_meta_list">
                    <span class="rich_media_meta rich_media_meta_nickname">瑞典马工</span>
                    <em id="publish_time">2024-01-15</em>
                </div>
                <div id="js_content" class="rich_media_content">
                    <p>2024年，瑞典政府对移民政策进行了重大调整。</p>
                    <p>首先，工作签证的要求有所提高。申请人需要有更高的工资水平。</p>
                    <p>其次，永久居留权的申请条件也发生了变化。</p>
                    <img data-src="http://example.com/policy.jpg" alt="政策图表">
                    <p>对于留学生来说，毕业后找工作的时间延长到了12个月。</p>
                    <p>家庭团聚的条件也有所放宽，特别是对于有孩子的家庭。</p>
                    <img data-src="http://example.com/sweden.jpg" alt="瑞典风景">
                </div>
            </div>
        </body>
        </html>
        """

        # 设置mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_response.apparent_encoding = 'utf-8'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 步骤1: 提取文章内容
        url = "http://mp.weixin.qq.com/s/abc123"
        extracted_data = extract_from_url(url, save_images=False, image_dir=self.images_dir)

        # 验证提取结果
        self.assertEqual(extracted_data['title'], "2024年瑞典移民新政策解读")
        self.assertEqual(extracted_data['author'], "瑞典马工")
        self.assertEqual(extracted_data['publish_date'], "2024-01-15")
        self.assertIn("移民政策", extracted_data['content']['text'])
        self.assertEqual(len(extracted_data['images']), 2)

        # 步骤2: 使用状态管理器记录处理状态
        state_manager = ArticleStateManager(str(self.state_file))
        state_manager.add_article(url, extracted_data)

        # 验证状态记录
        self.assertTrue(state_manager.is_article_processed(url))
        article_state = state_manager.get_article_state(url)
        self.assertEqual(article_state['status'], 'completed')
        self.assertEqual(article_state['title'], "2024年瑞典移民新政策解读")

        # 步骤3: 生成Markdown文件
        markdown_result = generate_markdown(extracted_data, self.posts_dir)

        # 验证Markdown生成
        self.assertTrue(markdown_result['success'])
        self.assertIsNotNone(markdown_result['file_path'])
        self.assertTrue(Path(markdown_result['file_path']).exists())

        # 步骤4: 验证生成的Markdown内容
        with open(markdown_result['file_path'], 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # 验证frontmatter
        self.assertIn("---", markdown_content)
        self.assertIn("title: 2024年瑞典移民新政策解读", markdown_content)
        self.assertIn("date: '2024-01-15'", markdown_content)
        self.assertIn("author: 瑞典马工", markdown_content)
        self.assertIn("category:", markdown_content)
        self.assertIn("tags:", markdown_content)

        # 验证内容
        self.assertIn("# 2024年瑞典移民新政策解读", markdown_content)
        self.assertIn("移民政策", markdown_content)
        self.assertIn("工作签证", markdown_content)
        self.assertIn("永久居留权", markdown_content)
        self.assertIn("留学生", markdown_content)

        # 验证图片引用
        self.assertIn("![政策图表]", markdown_content)
        self.assertIn("![瑞典风景]", markdown_content)

        # 验证原文链接
        self.assertIn("原文链接", markdown_content)
        self.assertIn(url, markdown_content)

        # 步骤5: 验证统计信息
        stats = state_manager.get_statistics()
        self.assertEqual(stats['total_articles'], 1)
        self.assertEqual(stats['successful_articles'], 1)
        self.assertEqual(stats['total_processed'], 1)

    @patch('wechat_extractor.requests.get')
    def test_batch_processing_workflow(self, mock_get):
        """测试批量处理多篇文章的工作流"""
        # 准备多个文章的HTML响应
        articles_html = [
            """
            <html>
                <h1 class="rich_media_title">瑞典教育体系介绍</h1>
                <em id="publish_time">2024-01-10</em>
                <div id="js_content">
                    <p>瑞典的教育体系非常完善，从幼儿园到大学都是免费的。</p>
                </div>
            </html>
            """,
            """
            <html>
                <h1 class="rich_media_title">斯德哥尔摩美食推荐</h1>
                <em id="publish_time">2024-01-12</em>
                <div id="js_content">
                    <p>斯德哥尔摩有很多值得尝试的餐厅和美食。</p>
                </div>
            </html>
            """,
            """
            <html>
                <h1 class="rich_media_title">瑞典职场文化解析</h1>
                <em id="publish_time">2024-01-14</em>
                <div id="js_content">
                    <p>瑞典的职场文化强调平等、工作与生活的平衡。</p>
                </div>
            </html>
            """
        ]

        urls = [
            "http://mp.weixin.qq.com/s/edu123",
            "http://mp.weixin.qq.com/s/food456",
            "http://mp.weixin.qq.com/s/work789"
        ]

        # 设置mock响应
        mock_responses = []
        for html in articles_html:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = html
            mock_response.apparent_encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_responses.append(mock_response)

        mock_get.side_effect = mock_responses

        # 初始化状态管理器
        state_manager = ArticleStateManager(str(self.state_file))

        # 处理所有文章
        extracted_articles = []
        for url in urls:
            extracted_data = extract_from_url(url, save_images=False)
            extracted_articles.append(extracted_data)
            state_manager.add_article(url, extracted_data)

        # 保存到JSON文件
        json_file = Path(self.test_dir) / 'articles.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_articles, f, ensure_ascii=False, indent=2)

        # 批量生成Markdown
        results = batch_generate(str(json_file), str(self.posts_dir))

        # 验证批量处理结果
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertTrue(result['success'])
            self.assertTrue(Path(result['file_path']).exists())

        # 验证生成的文件
        markdown_files = list(self.posts_dir.glob('*.md'))
        self.assertEqual(len(markdown_files), 3)

        # 验证文件内容包含正确的标题
        titles = ["瑞典教育体系介绍", "斯德哥尔摩美食推荐", "瑞典职场文化解析"]
        for title in titles:
            found = False
            for md_file in markdown_files:
                with open(md_file, 'r', encoding='utf-8') as f:
                    if title in f.read():
                        found = True
                        break
            self.assertTrue(found, f"未找到标题: {title}")

        # 验证状态管理器统计
        stats = state_manager.get_statistics()
        self.assertEqual(stats['total_articles'], 3)
        self.assertEqual(stats['successful_articles'], 3)

    @patch('wechat_extractor.requests.get')
    def test_incremental_update_workflow(self, mock_get):
        """测试增量更新工作流"""
        # 初始化状态管理器
        state_manager = ArticleStateManager(str(self.state_file))

        # 第一次处理
        url = "http://mp.weixin.qq.com/s/update123"
        original_html = """
        <html>
            <h1 class="rich_media_title">原始标题</h1>
            <div id="js_content"><p>原始内容</p></div>
        </html>
        """

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = original_html
        mock_response.apparent_encoding = 'utf-8'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 第一次提取和处理
        extracted_data = extract_from_url(url, save_images=False)
        state_manager.add_article(url, extracted_data)

        # 记录第一次处理的内容哈希
        first_state = state_manager.get_article_state(url)
        first_hash = first_state['content_hash']

        # 模拟文章更新
        updated_html = """
        <html>
            <h1 class="rich_media_title">更新后的标题</h1>
            <div id="js_content"><p>更新后的内容，添加了新信息</p></div>
        </html>
        """

        mock_response.text = updated_html

        # 检测是否需要更新
        self.assertTrue(state_manager.needs_update(url, "更新后的内容，添加了新信息"))

        # 第二次提取和处理
        updated_data = extract_from_url(url, save_images=False)
        state_manager.add_article(url, updated_data)

        # 验证更新
        updated_state = state_manager.get_article_state(url)
        self.assertEqual(updated_state['title'], "更新后的标题")
        self.assertNotEqual(updated_state['content_hash'], first_hash)
        self.assertEqual(updated_state['process_count'], 2)

        # 生成更新后的Markdown
        markdown_result = generate_markdown(updated_data, self.posts_dir)
        self.assertTrue(markdown_result['success'])

        # 验证Markdown包含更新的内容
        with open(markdown_result['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("更新后的标题", content)
            self.assertIn("更新后的内容", content)

    @patch('wechat_extractor.requests.get')
    def test_error_recovery_workflow(self, mock_get):
        """测试错误恢复工作流"""
        state_manager = ArticleStateManager(str(self.state_file))
        url = "http://mp.weixin.qq.com/s/error123"

        # 第一次请求失败
        mock_get.side_effect = Exception("网络错误")

        # 提取失败
        extracted_data = extract_from_url(url, save_images=False)
        self.assertIn('error', extracted_data)

        # 记录错误状态
        state_manager.mark_article_error(url, extracted_data['error'])

        # 验证错误状态
        error_state = state_manager.get_article_state(url)
        self.assertEqual(error_state['status'], 'error')

        # 第二次请求成功
        mock_get.side_effect = None
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <h1 class="rich_media_title">恢复后的文章</h1>
            <div id="js_content"><p>成功获取内容</p></div>
        </html>
        """
        mock_response.apparent_encoding = 'utf-8'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 重新提取
        extracted_data = extract_from_url(url, save_images=False)
        self.assertNotIn('error', extracted_data)
        self.assertEqual(extracted_data['title'], "恢复后的文章")

        # 更新状态
        state_manager.add_article(url, extracted_data)

        # 验证状态恢复
        recovered_state = state_manager.get_article_state(url)
        self.assertEqual(recovered_state['status'], 'completed')
        self.assertEqual(recovered_state['title'], "恢复后的文章")

        # 生成Markdown
        markdown_result = generate_markdown(extracted_data, self.posts_dir)
        self.assertTrue(markdown_result['success'])


class TestPerformanceAndScalability(unittest.TestCase):
    """性能和可扩展性测试"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.posts_dir = Path(self.test_dir) / 'posts'
        self.posts_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_large_batch_processing(self):
        """测试大批量文章处理性能"""
        # 生成100篇测试文章
        articles = []
        for i in range(100):
            article = {
                "title": f"测试文章 {i+1}",
                "author": "测试作者",
                "publish_date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "content": {"text": f"这是第{i+1}篇文章的内容" * 100},  # 较长内容
                "images": [{"src": f"http://example.com/img{j}.jpg", "alt": f"图片{j}"}
                          for j in range(5)],  # 每篇5张图片
                "original_url": f"http://mp.weixin.qq.com/s/test{i}"
            }
            articles.append(article)

        # 保存到JSON
        json_file = Path(self.test_dir) / 'large_batch.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        # 计时开始
        start_time = time.time()

        # 批量处理
        results = batch_generate(str(json_file), str(self.posts_dir))

        # 计时结束
        end_time = time.time()
        processing_time = end_time - start_time

        # 验证结果
        self.assertEqual(len(results), 100)
        success_count = sum(1 for r in results if r['success'])
        self.assertEqual(success_count, 100)

        # 性能要求：100篇文章应该在30秒内完成
        self.assertLess(processing_time, 30, f"处理100篇文章耗时{processing_time:.2f}秒，超过30秒限制")

        # 验证文件生成
        markdown_files = list(self.posts_dir.glob('*.md'))
        self.assertEqual(len(markdown_files), 100)

        print(f"处理100篇文章耗时: {processing_time:.2f}秒")
        print(f"平均每篇: {processing_time/100:.3f}秒")

    def test_concurrent_state_management(self):
        """测试并发状态管理"""
        import threading
        import random

        state_file = Path(self.test_dir) / 'concurrent_state.json'

        def worker(thread_id, urls):
            """工作线程函数"""
            state_manager = ArticleStateManager(str(state_file))
            for url in urls:
                article_data = {
                    "title": f"线程{thread_id}文章",
                    "content": {"text": f"内容-{random.random()}"}
                }
                state_manager.add_article(url, article_data)
                time.sleep(0.01)  # 模拟处理时间

        # 创建多个线程并发处理
        threads = []
        urls_per_thread = 10
        thread_count = 5

        for i in range(thread_count):
            urls = [f"http://example.com/thread{i}/article{j}"
                   for j in range(urls_per_thread)]
            thread = threading.Thread(target=worker, args=(i, urls))
            threads.append(thread)

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证最终状态
        final_state_manager = ArticleStateManager(str(state_file))
        stats = final_state_manager.get_statistics()

        # 应该处理了所有文章
        expected_total = thread_count * urls_per_thread
        self.assertEqual(stats['total_articles'], expected_total)
        self.assertEqual(stats['successful_articles'], expected_total)

    def test_memory_efficiency(self):
        """测试内存效率"""
        import tracemalloc

        # 开始跟踪内存
        tracemalloc.start()

        # 创建大量文章数据
        articles = []
        for i in range(1000):
            article = {
                "title": f"文章{i}",
                "content": {"text": "内容" * 1000},  # 较长内容
                "images": [{"src": f"img{j}.jpg", "alt": f"图{j}"} for j in range(10)]
            }
            articles.append(article)

        # 获取内存使用
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 转换为MB
        current_mb = current / 1024 / 1024
        peak_mb = peak / 1024 / 1024

        print(f"当前内存使用: {current_mb:.2f} MB")
        print(f"峰值内存使用: {peak_mb:.2f} MB")

        # 内存使用应该在合理范围内（小于500MB）
        self.assertLess(peak_mb, 500, f"峰值内存使用{peak_mb:.2f}MB超过500MB限制")


class TestDataIntegrity(unittest.TestCase):
    """数据完整性测试"""

    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_unicode_handling(self):
        """测试Unicode字符处理"""
        # 包含各种Unicode字符的文章
        article_data = {
            "title": "测试🎉 Emoji和特殊字符 © ® ™ € ¥",
            "author": "作者名 with English",
            "content": {
                "text": "中文内容 with English. 包含emoji😊 和特殊符号 → ← ↑ ↓"
            },
            "original_url": "http://example.com/unicode"
        }

        # 生成Markdown
        posts_dir = Path(self.test_dir) / 'posts'
        posts_dir.mkdir(parents=True, exist_ok=True)
        result = generate_markdown(article_data, posts_dir)

        self.assertTrue(result['success'])

        # 验证文件内容
        with open(result['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("🎉", content)
            self.assertIn("😊", content)
            self.assertIn("©", content)
            self.assertIn("→", content)

    def test_data_consistency_across_pipeline(self):
        """测试数据在整个管道中的一致性"""
        original_data = {
            "title": "原始标题",
            "author": "原始作者",
            "publish_date": "2024-01-15",
            "content": {"text": "原始内容"},
            "images": [{"src": "img1.jpg", "alt": "图片1"}],
            "original_url": "http://example.com/original"
        }

        # 通过状态管理器
        state_file = Path(self.test_dir) / 'state.json'
        state_manager = ArticleStateManager(str(state_file))
        state_manager.add_article(original_data['original_url'], original_data)

        # 从状态管理器获取
        stored_state = state_manager.get_article_state(original_data['original_url'])

        # 生成Markdown
        posts_dir = Path(self.test_dir) / 'posts'
        posts_dir.mkdir(parents=True, exist_ok=True)
        markdown_result = generate_markdown(original_data, posts_dir)

        # 验证数据一致性
        self.assertEqual(stored_state['title'], original_data['title'])
        self.assertEqual(stored_state['author'], original_data['author'])

        # 验证Markdown中的数据
        with open(markdown_result['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(original_data['title'], content)
            self.assertIn(original_data['author'], content)
            self.assertIn(original_data['content']['text'], content)

    def test_cleanup_old_data(self):
        """测试旧数据清理功能"""
        state_file = Path(self.test_dir) / 'state.json'
        state_manager = ArticleStateManager(str(state_file))

        # 添加不同时间的文章
        now = datetime.now()

        # 添加旧文章（40天前）
        old_article = {
            "title": "旧文章",
            "content": {"text": "旧内容"}
        }
        state_manager.add_article("http://example.com/old", old_article)

        # 手动修改时间戳
        state_manager.state_data['articles']['http://example.com/old']['last_processed_at'] = \
            (now - timedelta(days=40)).isoformat()
        state_manager._save_state()

        # 添加新文章（5天前）
        recent_article = {
            "title": "新文章",
            "content": {"text": "新内容"}
        }
        state_manager.add_article("http://example.com/recent", recent_article)
        state_manager.state_data['articles']['http://example.com/recent']['last_processed_at'] = \
            (now - timedelta(days=5)).isoformat()
        state_manager._save_state()

        # 清理30天前的数据
        removed_count = state_manager.cleanup_old_entries(30)

        # 验证清理结果
        self.assertEqual(removed_count, 1)
        self.assertFalse(state_manager.is_article_processed("http://example.com/old"))
        self.assertTrue(state_manager.is_article_processed("http://example.com/recent"))


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)