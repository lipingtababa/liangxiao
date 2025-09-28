#!/usr/bin/env python3
"""
状态管理系统测试脚本

测试所有状态管理功能
"""

import json
import os
import tempfile
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from state_manager import ArticleStateManager


def test_basic_operations():
    """测试基本CRUD操作"""
    print("测试基本CRUD操作...")

    # 使用临时文件
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        temp_path = tmp.name

    try:
        # 初始化管理器
        manager = ArticleStateManager(temp_path)

        # 测试1: 添加新文章
        test_article = {
            "title": "测试文章",
            "author": "测试作者",
            "publish_date": "2024-01-01",
            "content": {"text": "这是测试内容", "html": "<p>这是测试内容</p>"},
            "images": [],
            "word_count": 100
        }
        url = "https://test.com/article1"

        assert manager.add_article(url, test_article), "添加文章失败"
        assert manager.is_article_processed(url), "文章未被标记为已处理"
        print("✓ 添加文章成功")

        # 测试2: 获取文章状态
        state = manager.get_article_state(url)
        assert state is not None, "无法获取文章状态"
        assert state["title"] == "测试文章", "文章标题不匹配"
        assert state["status"] == "completed", "文章状态不正确"
        print("✓ 获取文章状态成功")

        # 测试3: 检测内容更新
        original_content = test_article["content"]["text"]
        assert not manager.needs_update(url, original_content), "相同内容被误判为需要更新"

        new_content = "这是更新后的内容"
        assert manager.needs_update(url, new_content), "内容变化未被检测到"
        print("✓ 内容更新检测成功")

        # 测试4: 更新文章
        test_article["content"]["text"] = new_content
        assert manager.add_article(url, test_article), "更新文章失败"
        updated_state = manager.get_article_state(url)
        assert updated_state["process_count"] == 2, "处理次数未正确更新"
        print("✓ 更新文章成功")

        # 测试5: 标记错误
        error_url = "https://test.com/error"
        assert manager.mark_article_error(error_url, "测试错误"), "标记错误失败"
        error_state = manager.get_article_state(error_url)
        assert error_state["status"] == "error", "错误状态未正确设置"
        print("✓ 标记错误成功")

        # 测试6: 统计信息
        stats = manager.get_statistics()
        assert stats["total_articles"] == 2, "文章总数不正确"
        assert stats["successful_articles"] == 1, "成功文章数不正确"
        assert stats["error_articles"] == 1, "错误文章数不正确"
        print("✓ 统计信息正确")

        # 测试7: 删除文章
        assert manager.remove_article(url), "删除文章失败"
        assert not manager.is_article_processed(url), "文章未被正确删除"
        print("✓ 删除文章成功")

    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("基本CRUD操作测试通过！\n")


def test_incremental_processing():
    """测试增量处理功能"""
    print("测试增量处理功能...")

    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        temp_path = tmp.name

    try:
        manager = ArticleStateManager(temp_path)

        # 准备测试数据
        urls = [
            "https://test.com/article1",
            "https://test.com/article2",
            "https://test.com/article3"
        ]

        # 处理第一批文章
        for i, url in enumerate(urls[:2]):
            article = {
                "title": f"文章{i+1}",
                "content": {"text": f"内容{i+1}", "html": f"<p>内容{i+1}</p>"},
                "author": "作者",
                "publish_date": "2024-01-01",
                "images": [],
                "word_count": 100
            }
            manager.add_article(url, article)

        # 测试未处理URL筛选
        unprocessed = manager.get_unprocessed_urls(urls)
        assert len(unprocessed) == 1, "未处理URL数量不正确"
        assert unprocessed[0] == urls[2], "未处理URL不正确"
        print("✓ 未处理URL筛选成功")

        # 测试需要更新的URL检测
        articles_with_updates = [
            {"url": urls[0], "content": {"text": "更新的内容1"}},  # 需要更新
            {"url": urls[1], "content": {"text": "内容2"}},  # 不需要更新
            {"url": urls[2], "content": {"text": "新内容3"}}  # 新文章
        ]

        urls_needing_update = manager.get_urls_needing_update(articles_with_updates)
        assert len(urls_needing_update) == 2, "需要更新的URL数量不正确"
        assert urls[0] in urls_needing_update, "更新的文章未被检测"
        assert urls[2] in urls_needing_update, "新文章未被标记为需要处理"
        print("✓ 更新检测成功")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("增量处理功能测试通过！\n")


def test_version_control():
    """测试版本控制功能"""
    print("测试版本控制功能...")

    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        temp_path = tmp.name

    try:
        # 创建初始管理器
        manager1 = ArticleStateManager(temp_path)

        # 添加一些数据
        article = {
            "title": "版本测试文章",
            "content": {"text": "测试内容", "html": "<p>测试内容</p>"},
            "author": "作者",
            "publish_date": "2024-01-01",
            "images": [],
            "word_count": 100
        }
        manager1.add_article("https://test.com/version", article)

        # 重新加载验证持久化
        manager2 = ArticleStateManager(temp_path)
        assert manager2.is_article_processed("https://test.com/version"), "数据未正确持久化"

        # 检查版本信息
        assert manager2.state_data["version"] == ArticleStateManager.SCHEMA_VERSION, "版本信息不正确"
        print("✓ 版本控制成功")

        # 验证文件格式
        with open(temp_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert "version" in data, "缺少版本字段"
            assert "created_at" in data, "缺少创建时间字段"
            assert "last_updated" in data, "缺少更新时间字段"
            assert "articles" in data, "缺少文章字段"
            assert "statistics" in data, "缺少统计字段"
        print("✓ 文件格式正确")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("版本控制功能测试通过！\n")


def test_concurrent_safety():
    """测试并发安全性"""
    print("测试并发安全性...")

    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        temp_path = tmp.name

    try:
        import threading
        import time

        manager = ArticleStateManager(temp_path)

        # 并发写入测试
        def add_articles(start_idx):
            for i in range(5):
                url = f"https://test.com/concurrent_{start_idx}_{i}"
                article = {
                    "title": f"并发文章{start_idx}_{i}",
                    "content": {"text": f"内容{start_idx}_{i}", "html": ""},
                    "author": "作者",
                    "publish_date": "2024-01-01",
                    "images": [],
                    "word_count": 100
                }
                manager.add_article(url, article)
                time.sleep(0.01)  # 模拟处理延迟

        # 启动多个线程
        threads = []
        for i in range(3):
            t = threading.Thread(target=add_articles, args=(i,))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证结果
        stats = manager.get_statistics()
        assert stats["total_articles"] == 15, f"并发写入后文章数量不正确: {stats['total_articles']}"
        print("✓ 并发写入安全")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("并发安全性测试通过！\n")


def test_cleanup_old_entries():
    """测试清理旧条目功能"""
    print("测试清理旧条目功能...")

    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        temp_path = tmp.name

    try:
        from datetime import datetime, timedelta

        manager = ArticleStateManager(temp_path)

        # 手动添加一些带有不同时间戳的文章
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        recent_date = (datetime.now() - timedelta(days=10)).isoformat()

        # 直接操作状态数据以设置旧日期
        manager.state_data["articles"]["https://old.com/1"] = {
            "url": "https://old.com/1",
            "title": "旧文章",
            "status": "completed",
            "last_processed_at": old_date
        }

        manager.state_data["articles"]["https://recent.com/1"] = {
            "url": "https://recent.com/1",
            "title": "近期文章",
            "status": "completed",
            "last_processed_at": recent_date
        }

        manager._save_state()

        # 清理30天前的条目
        removed = manager.cleanup_old_entries(30)
        assert removed == 1, "清理的条目数量不正确"

        # 验证旧条目被删除，新条目保留
        assert not manager.is_article_processed("https://old.com/1"), "旧条目未被删除"
        assert manager.is_article_processed("https://recent.com/1"), "近期条目被误删"
        print("✓ 清理旧条目成功")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("清理旧条目功能测试通过！\n")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("状态管理系统测试")
    print("=" * 50 + "\n")

    try:
        test_basic_operations()
        test_incremental_processing()
        test_version_control()
        test_concurrent_safety()
        test_cleanup_old_entries()

        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        return 0

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())