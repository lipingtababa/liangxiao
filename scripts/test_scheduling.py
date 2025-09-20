#!/usr/bin/env python3
"""
调度管理器测试脚本

测试文章调度和队列管理功能
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import unittest

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from scheduling_manager import SchedulingManager, ArticleStatus, PublishPriority


class TestSchedulingManager(unittest.TestCase):
    """调度管理器测试类"""

    def setUp(self):
        """测试前设置"""
        # 创建临时调度文件
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        self.temp_file.close()
        self.schedule_file = self.temp_file.name

        # 初始化调度管理器
        self.manager = SchedulingManager(self.schedule_file)

    def tearDown(self):
        """测试后清理"""
        # 删除临时文件
        if os.path.exists(self.schedule_file):
            os.unlink(self.schedule_file)

    def test_initialization(self):
        """测试初始化"""
        print("测试: 初始化调度管理器")

        # 验证默认结构
        self.assertIsNotNone(self.manager.schedule_data)
        self.assertIn('version', self.manager.schedule_data)
        self.assertIn('queue', self.manager.schedule_data)
        self.assertIn('scheduled', self.manager.schedule_data)
        self.assertIn('history', self.manager.schedule_data)
        self.assertIn('statistics', self.manager.schedule_data)
        self.assertIn('settings', self.manager.schedule_data)

        print("  ✓ 初始化成功")

    def test_add_to_queue(self):
        """测试添加文章到队列"""
        print("测试: 添加文章到队列")

        # 准备测试数据
        article_data = {
            'url': 'https://mp.weixin.qq.com/s/test123',
            'title': '测试文章标题',
            'author': '测试作者',
            'content': '这是测试内容',
            'word_count': 1000,
            'images': ['image1.jpg', 'image2.jpg'],
            'tags': ['测试', '技术'],
            'category': '技术文章'
        }

        # 添加普通优先级文章
        queue_id = self.manager.add_to_queue(article_data, PublishPriority.NORMAL)
        self.assertIsNotNone(queue_id)
        print(f"  ✓ 添加普通优先级文章，ID: {queue_id}")

        # 添加高优先级文章
        article_data['title'] = '高优先级文章'
        high_priority_id = self.manager.add_to_queue(article_data, PublishPriority.HIGH)
        self.assertIsNotNone(high_priority_id)
        print(f"  ✓ 添加高优先级文章，ID: {high_priority_id}")

        # 验证队列排序（高优先级应该在前）
        queue = self.manager.schedule_data['queue']
        self.assertEqual(len(queue), 2)
        self.assertEqual(queue[0]['id'], high_priority_id)
        print("  ✓ 队列按优先级正确排序")

        # 验证统计更新
        stats = self.manager.schedule_data['statistics']
        self.assertEqual(stats['total_queued'], 2)
        print("  ✓ 统计信息正确更新")

    def test_schedule_article(self):
        """测试调度文章"""
        print("测试: 调度文章")

        # 先添加文章到队列
        article_data = {
            'url': 'https://mp.weixin.qq.com/s/schedule_test',
            'title': '待调度文章',
            'author': '测试作者'
        }
        queue_id = self.manager.add_to_queue(article_data)
        self.assertIsNotNone(queue_id)
        print(f"  ✓ 文章已加入队列: {queue_id}")

        # 调度文章
        success = self.manager.schedule_article(queue_id)
        self.assertTrue(success)
        print("  ✓ 文章调度成功")

        # 验证文章已从队列移到调度列表
        self.assertEqual(len(self.manager.schedule_data['queue']), 0)
        self.assertIn(queue_id, self.manager.schedule_data['scheduled'])
        print("  ✓ 文章已从队列移至调度列表")

        # 验证文章状态
        scheduled_article = self.manager.schedule_data['scheduled'][queue_id]
        self.assertEqual(scheduled_article['status'], ArticleStatus.SCHEDULED.value)
        self.assertIn('scheduled_at', scheduled_article)
        print("  ✓ 文章状态正确更新")

    def test_custom_schedule_time(self):
        """测试自定义调度时间"""
        print("测试: 自定义调度时间")

        # 添加文章
        article_data = {'url': 'test', 'title': '定时发布文章'}
        queue_id = self.manager.add_to_queue(article_data)

        # 设置未来的发布时间
        future_time = datetime.now() + timedelta(days=3, hours=10)
        success = self.manager.schedule_article(queue_id, future_time)
        self.assertTrue(success)

        # 验证调度时间
        scheduled = self.manager.schedule_data['scheduled'][queue_id]
        scheduled_time = datetime.fromisoformat(scheduled['scheduled_at'])
        self.assertEqual(scheduled_time, future_time)
        print(f"  ✓ 文章已调度至: {future_time.isoformat()}")

    def test_get_pending_articles(self):
        """测试获取待发布文章"""
        print("测试: 获取待发布文章")

        # 添加并调度多个文章，设置不同的发布时间
        past_time = datetime.now() - timedelta(hours=1)
        future_time = datetime.now() + timedelta(hours=1)

        # 过期文章（应该被检索到）
        article1 = {'url': 'test1', 'title': '过期文章'}
        queue_id1 = self.manager.add_to_queue(article1)
        self.manager.schedule_article(queue_id1, past_time)

        # 未来文章（不应该被检索到）
        article2 = {'url': 'test2', 'title': '未来文章'}
        queue_id2 = self.manager.add_to_queue(article2)
        self.manager.schedule_article(queue_id2, future_time)

        # 获取待发布文章
        pending = self.manager.get_pending_articles()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['id'], queue_id1)
        print("  ✓ 正确识别待发布文章")

    def test_mark_as_published(self):
        """测试标记文章为已发布"""
        print("测试: 标记文章为已发布")

        # 添加并调度文章
        article_data = {'url': 'test', 'title': '待发布文章'}
        queue_id = self.manager.add_to_queue(article_data)
        self.manager.schedule_article(queue_id)

        # 标记为已发布
        published_url = 'https://magong.se/posts/test-article'
        success = self.manager.mark_as_published(queue_id, published_url)
        self.assertTrue(success)
        print("  ✓ 文章标记为已发布")

        # 验证文章已移至历史记录
        self.assertNotIn(queue_id, self.manager.schedule_data['scheduled'])
        history = self.manager.schedule_data['history']
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['id'], queue_id)
        self.assertEqual(history[0]['status'], ArticleStatus.PUBLISHED.value)
        self.assertEqual(history[0]['published_url'], published_url)
        print("  ✓ 文章已移至历史记录")

        # 验证统计更新
        stats = self.manager.schedule_data['statistics']
        self.assertEqual(stats['total_published'], 1)
        print("  ✓ 发布统计正确更新")

    def test_mark_as_failed(self):
        """测试标记文章为失败"""
        print("测试: 标记文章为失败")

        # 添加并调度文章
        article_data = {'url': 'test', 'title': '失败文章'}
        queue_id = self.manager.add_to_queue(article_data)
        self.manager.schedule_article(queue_id)

        # 标记为失败
        error_msg = "网络连接错误"
        success = self.manager.mark_as_failed(queue_id, error_msg)
        self.assertTrue(success)
        print("  ✓ 文章标记为失败")

        # 验证错误信息
        history = self.manager.schedule_data['history']
        self.assertEqual(history[0]['status'], ArticleStatus.FAILED.value)
        self.assertEqual(history[0]['error_message'], error_msg)
        print("  ✓ 错误信息已记录")

    def test_cancel_article(self):
        """测试取消文章"""
        print("测试: 取消调度文章")

        # 添加并调度文章
        article_data = {'url': 'test', 'title': '待取消文章'}
        queue_id = self.manager.add_to_queue(article_data)
        self.manager.schedule_article(queue_id)

        # 取消文章
        success = self.manager.cancel_scheduled_article(queue_id)
        self.assertTrue(success)
        print("  ✓ 文章已取消")

        # 验证状态
        history = self.manager.schedule_data['history']
        self.assertEqual(history[0]['status'], ArticleStatus.CANCELLED.value)
        self.assertIn('cancelled_at', history[0])
        print("  ✓ 取消状态正确记录")

    def test_auto_schedule_queue(self):
        """测试自动调度队列"""
        print("测试: 自动调度队列")

        # 添加多篇文章到队列
        for i in range(5):
            article_data = {
                'url': f'test{i}',
                'title': f'文章{i}'
            }
            self.manager.add_to_queue(article_data)

        # 自动调度所有文章
        scheduled_count = self.manager.auto_schedule_queue()
        self.assertEqual(scheduled_count, 5)
        print(f"  ✓ 自动调度 {scheduled_count} 篇文章")

        # 验证队列为空
        self.assertEqual(len(self.manager.schedule_data['queue']), 0)
        # 验证所有文章都已调度
        self.assertEqual(len(self.manager.schedule_data['scheduled']), 5)
        print("  ✓ 所有文章已从队列移至调度列表")

        # 验证发布时间间隔
        scheduled_times = []
        for article in self.manager.schedule_data['scheduled'].values():
            scheduled_times.append(datetime.fromisoformat(article['scheduled_at']))

        scheduled_times.sort()
        interval_hours = self.manager.schedule_data['settings']['default_interval_hours']

        for i in range(1, len(scheduled_times)):
            time_diff = scheduled_times[i] - scheduled_times[i-1]
            self.assertEqual(time_diff.total_seconds() / 3600, interval_hours)

        print(f"  ✓ 文章按 {interval_hours} 小时间隔调度")

    def test_get_upcoming_schedule(self):
        """测试获取未来发布计划"""
        print("测试: 获取未来发布计划")

        # 添加不同时间的文章
        now = datetime.now()
        times = [
            now + timedelta(days=1),
            now + timedelta(days=3),
            now + timedelta(days=5),
            now + timedelta(days=10)  # 超出7天范围
        ]

        for i, publish_time in enumerate(times):
            article_data = {'url': f'test{i}', 'title': f'文章{i}'}
            queue_id = self.manager.add_to_queue(article_data)
            self.manager.schedule_article(queue_id, publish_time)

        # 获取未来7天的计划
        upcoming = self.manager.get_upcoming_schedule(days=7)
        self.assertEqual(len(upcoming), 3)  # 只有前3篇在7天内
        print("  ✓ 正确筛选未来7天的文章")

        # 验证排序
        for i in range(1, len(upcoming)):
            time1 = datetime.fromisoformat(upcoming[i-1]['scheduled_at'])
            time2 = datetime.fromisoformat(upcoming[i]['scheduled_at'])
            self.assertLess(time1, time2)
        print("  ✓ 文章按时间顺序排列")

    def test_update_settings(self):
        """测试更新设置"""
        print("测试: 更新调度设置")

        # 更新设置
        new_settings = {
            'default_interval_hours': 48,
            'max_queue_size': 200,
            'auto_publish': True,
            'publish_time': '14:00'
        }

        success = self.manager.update_settings(**new_settings)
        self.assertTrue(success)
        print("  ✓ 设置更新成功")

        # 验证设置已更新
        settings = self.manager.schedule_data['settings']
        for key, value in new_settings.items():
            self.assertEqual(settings[key], value)
        print("  ✓ 所有设置项正确更新")

    def test_queue_size_limit(self):
        """测试队列大小限制"""
        print("测试: 队列大小限制")

        # 设置较小的队列限制
        self.manager.update_settings(max_queue_size=3)

        # 添加文章直到达到限制
        for i in range(4):
            article_data = {'url': f'test{i}', 'title': f'文章{i}'}
            queue_id = self.manager.add_to_queue(article_data)

            if i < 3:
                self.assertIsNotNone(queue_id)
                print(f"  ✓ 成功添加文章 {i+1}/3")
            else:
                self.assertIsNone(queue_id)
                print("  ✓ 队列已满，拒绝添加")

        # 验证队列大小
        self.assertEqual(len(self.manager.schedule_data['queue']), 3)
        print("  ✓ 队列大小限制生效")

    def test_priority_sorting(self):
        """测试优先级排序"""
        print("测试: 文章优先级排序")

        # 添加不同优先级的文章
        priorities = [
            (PublishPriority.LOW, '低优先级文章'),
            (PublishPriority.NORMAL, '普通优先级文章'),
            (PublishPriority.HIGH, '高优先级文章'),
            (PublishPriority.URGENT, '紧急文章')
        ]

        for priority, title in priorities:
            article_data = {'url': f'test_{priority.value}', 'title': title}
            self.manager.add_to_queue(article_data, priority)

        # 验证队列排序
        queue = self.manager.schedule_data['queue']
        self.assertEqual(len(queue), 4)

        # 检查优先级递减
        for i in range(1, len(queue)):
            self.assertGreaterEqual(queue[i-1]['priority'], queue[i]['priority'])

        print("  ✓ 队列按优先级从高到低排序")
        for item in queue:
            print(f"    - [{item['priority']}] {item['title']}")


def run_integration_test():
    """运行集成测试"""
    print("\n" + "="*60)
    print("运行调度管理器集成测试")
    print("="*60 + "\n")

    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    temp_file.close()

    try:
        # 初始化管理器
        manager = SchedulingManager(temp_file.name)
        print("1. 初始化调度管理器")

        # 模拟完整工作流
        print("\n2. 模拟文章发布工作流:")

        # 添加文章到队列
        articles = [
            {'url': 'https://mp.weixin.qq.com/s/article1', 'title': '瑞典生活指南'},
            {'url': 'https://mp.weixin.qq.com/s/article2', 'title': '斯德哥尔摩美食'},
            {'url': 'https://mp.weixin.qq.com/s/article3', 'title': '瑞典教育体系'}
        ]

        print("   添加文章到队列:")
        for article in articles:
            queue_id = manager.add_to_queue(article)
            print(f"   ✓ {article['title']} - ID: {queue_id}")

        # 自动调度
        print("\n   自动调度文章:")
        scheduled = manager.auto_schedule_queue()
        print(f"   ✓ 已调度 {scheduled} 篇文章")

        # 显示发布计划
        print("\n   未来7天发布计划:")
        upcoming = manager.get_upcoming_schedule(days=7)
        for article in upcoming:
            print(f"   - {article['scheduled_at']}: {article['title']}")

        # 模拟发布第一篇文章
        print("\n   模拟发布流程:")
        pending = manager.get_pending_articles(limit=1)
        if not pending:
            # 如果没有待发布的，手动设置一个过去的时间
            first_id = list(manager.schedule_data['scheduled'].keys())[0]
            article = manager.schedule_data['scheduled'][first_id]
            article['scheduled_at'] = (datetime.now() - timedelta(hours=1)).isoformat()
            manager._save_schedule()
            pending = manager.get_pending_articles(limit=1)

        if pending:
            article = pending[0]
            print(f"   处理: {article['title']}")

            # 标记为已发布
            manager.mark_as_published(
                article['id'],
                f"https://magong.se/posts/{article['id']}"
            )
            print(f"   ✓ 文章已发布")

        # 显示最终状态
        print("\n3. 最终状态:")
        status = manager.get_queue_status()
        print(f"   队列: {status['queue_size']} 篇")
        print(f"   已调度: {status['scheduled_count']} 篇")
        print(f"   总发布: {status['statistics']['total_published']} 篇")

        print("\n✅ 集成测试通过!")

    finally:
        # 清理临时文件
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


if __name__ == '__main__':
    # 运行单元测试
    print("运行单元测试...")
    print("="*60)

    # 设置测试运行器
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSchedulingManager)
    runner = unittest.TextTestRunner(verbosity=1)

    # 运行测试
    result = runner.run(suite)

    # 运行集成测试
    if result.wasSuccessful():
        run_integration_test()
    else:
        print("\n❌ 单元测试失败，跳过集成测试")