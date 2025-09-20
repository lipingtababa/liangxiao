#!/usr/bin/env python3
"""
状态管理器的单元测试
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from state_manager import ArticleStateManager


class TestArticleStateManager:
    """状态管理器测试类"""

    @pytest.fixture
    def temp_state_file(self):
        """创建临时状态文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # 清理
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def state_manager(self, temp_state_file):
        """创建状态管理器实例"""
        return ArticleStateManager(temp_state_file)

    @pytest.fixture
    def sample_article_data(self):
        """示例文章数据"""
        return {
            "title": "测试文章标题",
            "author": "测试作者",
            "publish_date": "2024-01-20",
            "content": {
                "text": "这是测试文章的内容，包含一些测试文本。" * 10,
                "html": "<p>这是测试文章的HTML内容</p>"
            },
            "images": [
                {"src": "http://example.com/image1.jpg", "alt": "图片1"},
                {"src": "http://example.com/image2.jpg", "alt": "图片2"}
            ],
            "word_count": 500
        }

    @pytest.mark.unit
    def test_initialization_new_file(self, temp_state_file):
        """测试初始化新的状态文件"""
        manager = ArticleStateManager(temp_state_file)

        assert manager.state_file_path == Path(temp_state_file)
        assert "version" in manager.state_data
        assert "articles" in manager.state_data
        assert "statistics" in manager.state_data
        assert manager.state_data["statistics"]["total_processed"] == 0

    @pytest.mark.unit
    def test_load_existing_state(self, temp_state_file):
        """测试加载已存在的状态文件"""
        # 创建测试数据
        test_data = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "articles": {
                "http://test.url": {
                    "title": "测试",
                    "status": "completed"
                }
            },
            "statistics": {
                "total_processed": 1,
                "total_updated": 0,
                "total_errors": 0
            }
        }

        with open(temp_state_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        manager = ArticleStateManager(temp_state_file)
        assert len(manager.state_data["articles"]) == 1
        assert manager.state_data["statistics"]["total_processed"] == 1

    @pytest.mark.unit
    def test_is_article_processed(self, state_manager):
        """测试检查文章是否已处理"""
        url = "http://example.com/article1"

        # 初始状态：未处理
        assert not state_manager.is_article_processed(url)

        # 添加文章
        state_manager.state_data["articles"][url] = {"status": "completed"}

        # 现在应该显示已处理
        assert state_manager.is_article_processed(url)

    @pytest.mark.unit
    def test_calculate_content_hash(self, state_manager):
        """测试内容哈希计算"""
        content1 = "这是测试内容"
        content2 = "这是不同的测试内容"
        content3 = "这是测试内容"  # 与content1相同

        hash1 = state_manager._calculate_content_hash(content1)
        hash2 = state_manager._calculate_content_hash(content2)
        hash3 = state_manager._calculate_content_hash(content3)

        assert hash1 == hash3  # 相同内容应该有相同哈希
        assert hash1 != hash2  # 不同内容应该有不同哈希
        assert len(hash1) == 64  # SHA256哈希长度

    @pytest.mark.unit
    def test_needs_update(self, state_manager, sample_article_data):
        """测试检查文章是否需要更新"""
        url = "http://example.com/article1"
        content = sample_article_data["content"]["text"]

        # 未处理的文章需要更新
        assert state_manager.needs_update(url, content)

        # 添加文章
        state_manager.add_article(url, sample_article_data)

        # 相同内容不需要更新
        assert not state_manager.needs_update(url, content)

        # 不同内容需要更新
        new_content = content + " 新增内容"
        assert state_manager.needs_update(url, new_content)

    @pytest.mark.unit
    def test_add_article(self, state_manager, sample_article_data):
        """测试添加新文章"""
        url = "http://example.com/article1"

        result = state_manager.add_article(url, sample_article_data)
        assert result is True

        # 验证文章已添加
        assert url in state_manager.state_data["articles"]
        article_state = state_manager.state_data["articles"][url]

        assert article_state["title"] == sample_article_data["title"]
        assert article_state["author"] == sample_article_data["author"]
        assert article_state["status"] == "completed"
        assert article_state["process_count"] == 1
        assert "content_hash" in article_state
        assert "first_processed_at" in article_state

    @pytest.mark.unit
    def test_update_existing_article(self, state_manager, sample_article_data):
        """测试更新已存在的文章"""
        url = "http://example.com/article1"

        # 第一次添加
        state_manager.add_article(url, sample_article_data)
        first_process_time = state_manager.state_data["articles"][url]["first_processed_at"]

        # 修改内容并再次添加
        sample_article_data["content"]["text"] += " 更新的内容"
        result = state_manager.add_article(url, sample_article_data)

        assert result is True
        article_state = state_manager.state_data["articles"][url]

        # 验证更新
        assert article_state["process_count"] == 2
        assert article_state["first_processed_at"] == first_process_time
        assert state_manager.state_data["statistics"]["total_updated"] == 1

    @pytest.mark.unit
    def test_mark_article_error(self, state_manager):
        """测试标记文章错误"""
        url = "http://example.com/article1"
        error_message = "提取失败：网络错误"

        result = state_manager.mark_article_error(url, error_message)
        assert result is True

        # 验证错误状态
        article_state = state_manager.state_data["articles"][url]
        assert article_state["status"] == "error"
        assert article_state["error"] == error_message
        assert state_manager.state_data["statistics"]["total_errors"] == 1

    @pytest.mark.unit
    def test_get_unprocessed_urls(self, state_manager, sample_article_data):
        """测试获取未处理的URL列表"""
        urls = [
            "http://example.com/article1",
            "http://example.com/article2",
            "http://example.com/article3"
        ]

        # 初始状态：全部未处理
        unprocessed = state_manager.get_unprocessed_urls(urls)
        assert len(unprocessed) == 3

        # 处理第一个URL
        state_manager.add_article(urls[0], sample_article_data)

        # 现在应该有2个未处理
        unprocessed = state_manager.get_unprocessed_urls(urls)
        assert len(unprocessed) == 2
        assert urls[0] not in unprocessed

    @pytest.mark.unit
    def test_get_statistics(self, state_manager, sample_article_data):
        """测试获取统计信息"""
        # 添加成功的文章
        state_manager.add_article("http://example.com/article1", sample_article_data)

        # 添加错误的文章
        state_manager.mark_article_error("http://example.com/article2", "错误")

        stats = state_manager.get_statistics()

        assert stats["total_articles"] == 2
        assert stats["successful_articles"] == 1
        assert stats["error_articles"] == 1
        assert stats["total_processed"] == 1
        assert stats["total_errors"] == 1

    @pytest.mark.unit
    def test_remove_article(self, state_manager, sample_article_data):
        """测试移除文章"""
        url = "http://example.com/article1"

        # 添加文章
        state_manager.add_article(url, sample_article_data)
        assert url in state_manager.state_data["articles"]

        # 移除文章
        result = state_manager.remove_article(url)
        assert result is True
        assert url not in state_manager.state_data["articles"]

        # 移除不存在的文章应该返回True
        result = state_manager.remove_article("http://nonexistent.url")
        assert result is True

    @pytest.mark.unit
    def test_get_article_state(self, state_manager, sample_article_data):
        """测试获取文章状态"""
        url = "http://example.com/article1"

        # 不存在的文章返回None
        assert state_manager.get_article_state(url) is None

        # 添加文章
        state_manager.add_article(url, sample_article_data)

        # 获取状态
        state = state_manager.get_article_state(url)
        assert state is not None
        assert state["title"] == sample_article_data["title"]
        assert state["status"] == "completed"

    @pytest.mark.unit
    def test_cleanup_old_entries(self, state_manager, sample_article_data):
        """测试清理旧条目"""
        # 添加一些文章，模拟不同时间
        urls = ["http://example.com/article1", "http://example.com/article2"]

        # 添加第一个文章
        state_manager.add_article(urls[0], sample_article_data)

        # 手动修改时间为31天前
        old_date = (datetime.now() - timedelta(days=31)).isoformat()
        state_manager.state_data["articles"][urls[0]]["last_processed_at"] = old_date

        # 添加第二个文章（当前时间）
        state_manager.add_article(urls[1], sample_article_data)

        # 清理30天前的记录
        removed_count = state_manager.cleanup_old_entries(30)

        assert removed_count == 1
        assert urls[0] not in state_manager.state_data["articles"]
        assert urls[1] in state_manager.state_data["articles"]

    @pytest.mark.unit
    def test_concurrent_save(self, state_manager, sample_article_data):
        """测试并发保存的安全性"""
        import threading

        def add_article(url):
            state_manager.add_article(url, sample_article_data)

        # 创建多个线程同时添加文章
        threads = []
        for i in range(5):
            url = f"http://example.com/article{i}"
            thread = threading.Thread(target=add_article, args=(url,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证所有文章都已添加
        assert len(state_manager.state_data["articles"]) == 5

    @pytest.mark.unit
    def test_invalid_state_file(self, temp_state_file):
        """测试处理无效的状态文件"""
        # 写入无效的JSON
        with open(temp_state_file, 'w') as f:
            f.write("invalid json content")

        # 应该能够处理并返回默认状态
        manager = ArticleStateManager(temp_state_file)
        assert "version" in manager.state_data
        assert "articles" in manager.state_data
        assert len(manager.state_data["articles"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])