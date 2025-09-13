#!/usr/bin/env python3
"""
文章处理状态管理器

用于跟踪已处理的文章，避免重复处理，支持增量更新
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import fcntl
import time


class ArticleStateManager:
    """文章处理状态管理器"""

    # 状态文件版本，用于未来的向后兼容
    SCHEMA_VERSION = "1.0.0"

    def __init__(self, state_file_path: str = "processed_articles.json"):
        """
        初始化状态管理器

        Args:
            state_file_path: 状态文件路径
        """
        self.state_file_path = Path(state_file_path)
        self.state_data = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """
        加载状态文件

        Returns:
            状态数据字典
        """
        if not self.state_file_path.exists():
            # 初始化新的状态文件结构
            return {
                "version": self.SCHEMA_VERSION,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "articles": {},
                "statistics": {
                    "total_processed": 0,
                    "total_updated": 0,
                    "total_errors": 0
                }
            }

        try:
            with open(self.state_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 版本兼容性检查
                if data.get("version") != self.SCHEMA_VERSION:
                    print(f"警告: 状态文件版本 {data.get('version')} 与当前版本 {self.SCHEMA_VERSION} 不匹配")

                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"错误: 无法加载状态文件: {e}")
            # 返回默认状态结构
            return {
                "version": self.SCHEMA_VERSION,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "articles": {},
                "statistics": {
                    "total_processed": 0,
                    "total_updated": 0,
                    "total_errors": 0
                }
            }

    def _save_state(self) -> bool:
        """
        保存状态到文件（带文件锁）

        Returns:
            是否保存成功
        """
        try:
            # 更新最后修改时间
            self.state_data["last_updated"] = datetime.now().isoformat()

            # 创建临时文件
            temp_file = self.state_file_path.with_suffix('.tmp')

            # 写入临时文件
            with open(temp_file, 'w', encoding='utf-8') as f:
                # 使用文件锁防止并发写入
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(self.state_data, f, ensure_ascii=False, indent=2)
                fcntl.flock(f, fcntl.LOCK_UN)

            # 原子性替换文件
            temp_file.replace(self.state_file_path)
            return True

        except Exception as e:
            print(f"错误: 无法保存状态文件: {e}")
            return False

    def _calculate_content_hash(self, content: str) -> str:
        """
        计算内容哈希值，用于检测内容变化

        Args:
            content: 文章内容

        Returns:
            内容的SHA256哈希值
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def is_article_processed(self, url: str) -> bool:
        """
        检查文章是否已处理

        Args:
            url: 文章URL

        Returns:
            是否已处理
        """
        return url in self.state_data.get("articles", {})

    def needs_update(self, url: str, content: str) -> bool:
        """
        检查文章是否需要更新（内容已改变）

        Args:
            url: 文章URL
            content: 当前文章内容

        Returns:
            是否需要更新
        """
        if not self.is_article_processed(url):
            return True

        article_state = self.state_data["articles"][url]
        current_hash = self._calculate_content_hash(content)

        return article_state.get("content_hash") != current_hash

    def add_article(self, url: str, article_data: Dict[str, Any]) -> bool:
        """
        添加新处理的文章

        Args:
            url: 文章URL
            article_data: 文章数据（包含title, content等）

        Returns:
            是否添加成功
        """
        try:
            # 计算内容哈希
            content = article_data.get("content", {}).get("text", "")
            content_hash = self._calculate_content_hash(content)

            # 构建文章状态记录
            article_state = {
                "url": url,
                "title": article_data.get("title", ""),
                "author": article_data.get("author", ""),
                "publish_date": article_data.get("publish_date", ""),
                "content_hash": content_hash,
                "word_count": article_data.get("word_count", 0),
                "image_count": len(article_data.get("images", [])),
                "first_processed_at": datetime.now().isoformat(),
                "last_processed_at": datetime.now().isoformat(),
                "process_count": 1,
                "status": "completed",
                "error": None
            }

            # 检查是否是更新
            if self.is_article_processed(url):
                existing = self.state_data["articles"][url]
                article_state["first_processed_at"] = existing["first_processed_at"]
                article_state["process_count"] = existing.get("process_count", 0) + 1
                self.state_data["statistics"]["total_updated"] += 1
            else:
                self.state_data["statistics"]["total_processed"] += 1

            # 保存文章状态
            if "articles" not in self.state_data:
                self.state_data["articles"] = {}

            self.state_data["articles"][url] = article_state

            return self._save_state()

        except Exception as e:
            print(f"错误: 无法添加文章状态: {e}")
            return False

    def mark_article_error(self, url: str, error_message: str) -> bool:
        """
        标记文章处理错误

        Args:
            url: 文章URL
            error_message: 错误信息

        Returns:
            是否标记成功
        """
        try:
            if "articles" not in self.state_data:
                self.state_data["articles"] = {}

            # 如果文章已存在，更新错误状态
            if url in self.state_data["articles"]:
                self.state_data["articles"][url]["status"] = "error"
                self.state_data["articles"][url]["error"] = error_message
                self.state_data["articles"][url]["last_processed_at"] = datetime.now().isoformat()
            else:
                # 创建新的错误记录
                self.state_data["articles"][url] = {
                    "url": url,
                    "status": "error",
                    "error": error_message,
                    "first_processed_at": datetime.now().isoformat(),
                    "last_processed_at": datetime.now().isoformat(),
                    "process_count": 1
                }

            self.state_data["statistics"]["total_errors"] += 1
            return self._save_state()

        except Exception as e:
            print(f"错误: 无法标记文章错误: {e}")
            return False

    def get_unprocessed_urls(self, urls: List[str]) -> List[str]:
        """
        从URL列表中筛选出未处理的URL

        Args:
            urls: URL列表

        Returns:
            未处理的URL列表
        """
        processed_urls = set(self.state_data.get("articles", {}).keys())
        return [url for url in urls if url not in processed_urls]

    def get_urls_needing_update(self, articles: List[Dict[str, Any]]) -> List[str]:
        """
        获取需要更新的文章URL列表

        Args:
            articles: 文章数据列表（包含url和content）

        Returns:
            需要更新的URL列表
        """
        urls_to_update = []

        for article in articles:
            url = article.get("url") or article.get("original_url")
            content = article.get("content", {}).get("text", "")

            if url and self.needs_update(url, content):
                urls_to_update.append(url)

        return urls_to_update

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取处理统计信息

        Returns:
            统计信息字典
        """
        stats = self.state_data.get("statistics", {}).copy()

        # 添加更多统计信息
        articles = self.state_data.get("articles", {})
        stats["total_articles"] = len(articles)
        stats["successful_articles"] = len([a for a in articles.values() if a.get("status") == "completed"])
        stats["error_articles"] = len([a for a in articles.values() if a.get("status") == "error"])

        return stats

    def remove_article(self, url: str) -> bool:
        """
        从状态中移除文章（用于删除场景）

        Args:
            url: 文章URL

        Returns:
            是否移除成功
        """
        try:
            if url in self.state_data.get("articles", {}):
                del self.state_data["articles"][url]
                return self._save_state()
            return True
        except Exception as e:
            print(f"错误: 无法移除文章: {e}")
            return False

    def get_article_state(self, url: str) -> Optional[Dict[str, Any]]:
        """
        获取特定文章的状态信息

        Args:
            url: 文章URL

        Returns:
            文章状态信息，如果不存在返回None
        """
        return self.state_data.get("articles", {}).get(url)

    def cleanup_old_entries(self, days: int = 30) -> int:
        """
        清理指定天数前的旧条目

        Args:
            days: 保留最近多少天的记录

        Returns:
            清理的条目数量
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        articles = self.state_data.get("articles", {})
        removed_count = 0

        urls_to_remove = []
        for url, article in articles.items():
            last_processed = article.get("last_processed_at", "")
            if last_processed:
                try:
                    last_date = datetime.fromisoformat(last_processed)
                    if last_date < cutoff_date:
                        urls_to_remove.append(url)
                except ValueError:
                    continue

        for url in urls_to_remove:
            if self.remove_article(url):
                removed_count += 1

        return removed_count


def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(description='文章处理状态管理器')
    parser.add_argument('--status', action='store_true', help='显示统计信息')
    parser.add_argument('--check', help='检查特定URL的状态')
    parser.add_argument('--cleanup', type=int, help='清理N天前的旧记录')
    parser.add_argument('--list', action='store_true', help='列出所有已处理的文章')

    args = parser.parse_args()

    # 初始化状态管理器
    manager = ArticleStateManager()

    if args.status:
        stats = manager.get_statistics()
        print("处理统计信息:")
        print(f"  总处理文章数: {stats.get('total_processed', 0)}")
        print(f"  更新文章数: {stats.get('total_updated', 0)}")
        print(f"  错误数: {stats.get('total_errors', 0)}")
        print(f"  当前文章总数: {stats.get('total_articles', 0)}")
        print(f"  成功文章数: {stats.get('successful_articles', 0)}")
        print(f"  错误文章数: {stats.get('error_articles', 0)}")

    elif args.check:
        state = manager.get_article_state(args.check)
        if state:
            print(f"文章状态: {args.check}")
            print(f"  标题: {state.get('title', 'N/A')}")
            print(f"  状态: {state.get('status', 'N/A')}")
            print(f"  首次处理: {state.get('first_processed_at', 'N/A')}")
            print(f"  最后处理: {state.get('last_processed_at', 'N/A')}")
            print(f"  处理次数: {state.get('process_count', 0)}")
            if state.get('error'):
                print(f"  错误: {state['error']}")
        else:
            print(f"文章未处理: {args.check}")

    elif args.cleanup:
        removed = manager.cleanup_old_entries(args.cleanup)
        print(f"已清理 {removed} 条旧记录")

    elif args.list:
        articles = manager.state_data.get("articles", {})
        if articles:
            print(f"已处理的文章 ({len(articles)} 篇):")
            for url, state in articles.items():
                status = state.get('status', 'unknown')
                title = state.get('title', 'Untitled')[:50]
                print(f"  [{status}] {title}... - {url}")
        else:
            print("暂无已处理的文章")


if __name__ == '__main__':
    main()