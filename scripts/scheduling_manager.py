#!/usr/bin/env python3
"""
文章发布调度管理器

用于管理文章的发布队列和调度计划
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from enum import Enum
import fcntl
import uuid


class ArticleStatus(Enum):
    """文章状态枚举"""
    DRAFT = "draft"  # 草稿
    QUEUED = "queued"  # 已加入队列
    SCHEDULED = "scheduled"  # 已调度
    PROCESSING = "processing"  # 处理中
    PUBLISHED = "published"  # 已发布
    FAILED = "failed"  # 发布失败
    CANCELLED = "cancelled"  # 已取消


class PublishPriority(Enum):
    """发布优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class SchedulingManager:
    """文章调度管理器"""

    SCHEMA_VERSION = "1.0.0"

    def __init__(self, schedule_file_path: str = "article_schedule.json"):
        """
        初始化调度管理器

        Args:
            schedule_file_path: 调度文件路径
        """
        self.schedule_file_path = Path(schedule_file_path)
        self.schedule_data = self._load_schedule()

    def _load_schedule(self) -> Dict[str, Any]:
        """加载调度文件"""
        if not self.schedule_file_path.exists():
            return self._create_default_schedule()

        try:
            with open(self.schedule_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 版本兼容性检查
                if data.get("version") != self.SCHEMA_VERSION:
                    print(f"警告: 调度文件版本 {data.get('version')} 与当前版本 {self.SCHEMA_VERSION} 不匹配")

                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"错误: 无法加载调度文件: {e}")
            return self._create_default_schedule()

    def _create_default_schedule(self) -> Dict[str, Any]:
        """创建默认调度结构"""
        return {
            "version": self.SCHEMA_VERSION,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "settings": {
                "default_interval_hours": 24,  # 默认发布间隔（小时）
                "max_queue_size": 100,  # 最大队列大小
                "auto_publish": False,  # 是否自动发布
                "publish_time": "09:00",  # 默认发布时间
                "timezone": "Europe/Stockholm"  # 时区
            },
            "queue": [],  # 发布队列
            "scheduled": {},  # 已调度的文章
            "history": [],  # 发布历史
            "statistics": {
                "total_queued": 0,
                "total_scheduled": 0,
                "total_published": 0,
                "total_failed": 0,
                "total_cancelled": 0
            }
        }

    def _save_schedule(self) -> bool:
        """保存调度到文件"""
        try:
            # 更新最后修改时间
            self.schedule_data["last_updated"] = datetime.now().isoformat()

            # 创建临时文件
            temp_file = self.schedule_file_path.with_suffix('.tmp')

            # 写入临时文件
            with open(temp_file, 'w', encoding='utf-8') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(self.schedule_data, f, ensure_ascii=False, indent=2)
                fcntl.flock(f, fcntl.LOCK_UN)

            # 原子性替换文件
            temp_file.replace(self.schedule_file_path)
            return True

        except Exception as e:
            print(f"错误: 无法保存调度文件: {e}")
            return False

    def add_to_queue(self, article_data: Dict[str, Any], priority: PublishPriority = PublishPriority.NORMAL) -> Optional[str]:
        """
        将文章添加到发布队列

        Args:
            article_data: 文章数据（包含url, title, content等）
            priority: 发布优先级

        Returns:
            队列ID，如果添加失败返回None
        """
        try:
            # 检查队列大小限制
            max_size = self.schedule_data["settings"]["max_queue_size"]
            if len(self.schedule_data["queue"]) >= max_size:
                print(f"错误: 队列已满（最大 {max_size} 篇文章）")
                return None

            # 生成唯一ID
            queue_id = str(uuid.uuid4())

            # 创建队列项
            queue_item = {
                "id": queue_id,
                "url": article_data.get("url", ""),
                "title": article_data.get("title", ""),
                "author": article_data.get("author", ""),
                "priority": priority.value,
                "status": ArticleStatus.QUEUED.value,
                "added_at": datetime.now().isoformat(),
                "metadata": {
                    "word_count": article_data.get("word_count", 0),
                    "image_count": len(article_data.get("images", [])),
                    "tags": article_data.get("tags", []),
                    "category": article_data.get("category", "")
                }
            }

            # 添加到队列（根据优先级排序）
            self.schedule_data["queue"].append(queue_item)
            self.schedule_data["queue"].sort(key=lambda x: x["priority"], reverse=True)

            # 更新统计
            self.schedule_data["statistics"]["total_queued"] += 1

            self._save_schedule()
            return queue_id

        except Exception as e:
            print(f"错误: 无法添加文章到队列: {e}")
            return None

    def schedule_article(self, queue_id: str, publish_time: Optional[datetime] = None) -> bool:
        """
        调度队列中的文章

        Args:
            queue_id: 队列ID
            publish_time: 计划发布时间，如果为None则使用默认时间

        Returns:
            是否调度成功
        """
        try:
            # 查找队列中的文章
            queue_item = None
            for i, item in enumerate(self.schedule_data["queue"]):
                if item["id"] == queue_id:
                    queue_item = self.schedule_data["queue"].pop(i)
                    break

            if not queue_item:
                print(f"错误: 找不到队列ID {queue_id}")
                return False

            # 设置发布时间
            if publish_time is None:
                # 计算下一个可用的发布时间
                publish_time = self._calculate_next_publish_time()

            # 更新文章状态
            queue_item["status"] = ArticleStatus.SCHEDULED.value
            queue_item["scheduled_at"] = publish_time.isoformat()

            # 添加到已调度字典
            self.schedule_data["scheduled"][queue_id] = queue_item

            # 更新统计
            self.schedule_data["statistics"]["total_scheduled"] += 1

            return self._save_schedule()

        except Exception as e:
            print(f"错误: 无法调度文章: {e}")
            return False

    def _calculate_next_publish_time(self) -> datetime:
        """计算下一个可用的发布时间"""
        # 获取最后一个已调度的时间
        last_scheduled = None
        for item in self.schedule_data["scheduled"].values():
            scheduled_at = datetime.fromisoformat(item["scheduled_at"])
            if last_scheduled is None or scheduled_at > last_scheduled:
                last_scheduled = scheduled_at

        # 如果没有已调度的文章，使用明天的默认时间
        if last_scheduled is None:
            tomorrow = datetime.now() + timedelta(days=1)
            publish_time_str = self.schedule_data["settings"]["publish_time"]
            hour, minute = map(int, publish_time_str.split(":"))
            return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # 否则，在最后一个调度时间基础上加上默认间隔
        interval_hours = self.schedule_data["settings"]["default_interval_hours"]
        return last_scheduled + timedelta(hours=interval_hours)

    def get_pending_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取待发布的文章列表

        Args:
            limit: 返回的最大文章数

        Returns:
            待发布文章列表
        """
        now = datetime.now()
        pending = []

        for article in self.schedule_data["scheduled"].values():
            if article["status"] == ArticleStatus.SCHEDULED.value:
                scheduled_time = datetime.fromisoformat(article["scheduled_at"])
                if scheduled_time <= now:
                    pending.append(article)

        # 按调度时间排序
        pending.sort(key=lambda x: x["scheduled_at"])

        return pending[:limit]

    def mark_as_published(self, article_id: str, published_url: Optional[str] = None) -> bool:
        """
        标记文章为已发布

        Args:
            article_id: 文章ID
            published_url: 发布后的URL

        Returns:
            是否标记成功
        """
        try:
            if article_id not in self.schedule_data["scheduled"]:
                print(f"错误: 找不到文章ID {article_id}")
                return False

            article = self.schedule_data["scheduled"][article_id]
            article["status"] = ArticleStatus.PUBLISHED.value
            article["published_at"] = datetime.now().isoformat()
            if published_url:
                article["published_url"] = published_url

            # 移动到历史记录
            self.schedule_data["history"].append(article)
            del self.schedule_data["scheduled"][article_id]

            # 更新统计
            self.schedule_data["statistics"]["total_published"] += 1

            # 只保留最近100条历史记录
            if len(self.schedule_data["history"]) > 100:
                self.schedule_data["history"] = self.schedule_data["history"][-100:]

            return self._save_schedule()

        except Exception as e:
            print(f"错误: 无法标记文章为已发布: {e}")
            return False

    def mark_as_failed(self, article_id: str, error_message: str) -> bool:
        """
        标记文章发布失败

        Args:
            article_id: 文章ID
            error_message: 错误信息

        Returns:
            是否标记成功
        """
        try:
            if article_id not in self.schedule_data["scheduled"]:
                print(f"错误: 找不到文章ID {article_id}")
                return False

            article = self.schedule_data["scheduled"][article_id]
            article["status"] = ArticleStatus.FAILED.value
            article["failed_at"] = datetime.now().isoformat()
            article["error_message"] = error_message

            # 可以选择将失败的文章放回队列
            # 这里我们将其移到历史记录
            self.schedule_data["history"].append(article)
            del self.schedule_data["scheduled"][article_id]

            # 更新统计
            self.schedule_data["statistics"]["total_failed"] += 1

            return self._save_schedule()

        except Exception as e:
            print(f"错误: 无法标记文章为失败: {e}")
            return False

    def cancel_scheduled_article(self, article_id: str) -> bool:
        """
        取消已调度的文章

        Args:
            article_id: 文章ID

        Returns:
            是否取消成功
        """
        try:
            if article_id not in self.schedule_data["scheduled"]:
                print(f"错误: 找不到文章ID {article_id}")
                return False

            article = self.schedule_data["scheduled"][article_id]
            article["status"] = ArticleStatus.CANCELLED.value
            article["cancelled_at"] = datetime.now().isoformat()

            # 移动到历史记录
            self.schedule_data["history"].append(article)
            del self.schedule_data["scheduled"][article_id]

            # 更新统计
            self.schedule_data["statistics"]["total_cancelled"] += 1

            return self._save_schedule()

        except Exception as e:
            print(f"错误: 无法取消文章: {e}")
            return False

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态信息"""
        return {
            "queue_size": len(self.schedule_data["queue"]),
            "scheduled_count": len(self.schedule_data["scheduled"]),
            "pending_count": len(self.get_pending_articles(limit=1000)),
            "statistics": self.schedule_data["statistics"],
            "settings": self.schedule_data["settings"]
        }

    def get_upcoming_schedule(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取未来几天的发布计划

        Args:
            days: 查看未来多少天

        Returns:
            发布计划列表
        """
        now = datetime.now()
        future_date = now + timedelta(days=days)
        upcoming = []

        for article in self.schedule_data["scheduled"].values():
            if article["status"] == ArticleStatus.SCHEDULED.value:
                scheduled_time = datetime.fromisoformat(article["scheduled_at"])
                if now <= scheduled_time <= future_date:
                    upcoming.append(article)

        # 按调度时间排序
        upcoming.sort(key=lambda x: x["scheduled_at"])

        return upcoming

    def update_settings(self, **kwargs) -> bool:
        """
        更新调度设置

        Args:
            **kwargs: 要更新的设置项

        Returns:
            是否更新成功
        """
        try:
            for key, value in kwargs.items():
                if key in self.schedule_data["settings"]:
                    self.schedule_data["settings"][key] = value

            return self._save_schedule()

        except Exception as e:
            print(f"错误: 无法更新设置: {e}")
            return False

    def auto_schedule_queue(self) -> int:
        """
        自动调度队列中的所有文章

        Returns:
            调度的文章数量
        """
        scheduled_count = 0
        queue_copy = self.schedule_data["queue"].copy()

        for item in queue_copy:
            if self.schedule_article(item["id"]):
                scheduled_count += 1

        return scheduled_count


def main():
    """命令行测试接口"""
    import argparse

    parser = argparse.ArgumentParser(description='文章调度管理器')
    parser.add_argument('--file', type=str, default='article_schedule.json', help='调度文件路径')
    parser.add_argument('--status', action='store_true', help='显示队列状态')
    parser.add_argument('--queue', action='store_true', help='显示队列中的文章')
    parser.add_argument('--scheduled', action='store_true', help='显示已调度的文章')
    parser.add_argument('--upcoming', type=int, help='显示未来N天的发布计划')
    parser.add_argument('--pending', action='store_true', help='显示待发布的文章')
    parser.add_argument('--auto-schedule', action='store_true', help='自动调度队列中的所有文章')

    args = parser.parse_args()

    # 初始化调度管理器
    manager = SchedulingManager(args.file)

    if args.status:
        status = manager.get_queue_status()
        print("队列状态信息:")
        print(f"  队列大小: {status['queue_size']}")
        print(f"  已调度数: {status['scheduled_count']}")
        print(f"  待发布数: {status['pending_count']}")
        print("\n统计信息:")
        stats = status['statistics']
        print(f"  总加入队列: {stats['total_queued']}")
        print(f"  总调度数: {stats['total_scheduled']}")
        print(f"  总发布数: {stats['total_published']}")
        print(f"  总失败数: {stats['total_failed']}")
        print(f"  总取消数: {stats['total_cancelled']}")

    elif args.queue:
        queue = manager.schedule_data["queue"]
        if queue:
            print(f"队列中的文章 ({len(queue)} 篇):")
            for item in queue:
                print(f"  [{item['priority']}] {item['title']} - {item['id']}")
                print(f"      添加时间: {item['added_at']}")
        else:
            print("队列为空")

    elif args.scheduled:
        scheduled = manager.schedule_data["scheduled"]
        if scheduled:
            print(f"已调度的文章 ({len(scheduled)} 篇):")
            for item in scheduled.values():
                print(f"  {item['title']} - {item['id']}")
                print(f"    计划发布: {item['scheduled_at']}")
                print(f"    状态: {item['status']}")
        else:
            print("没有已调度的文章")

    elif args.upcoming:
        upcoming = manager.get_upcoming_schedule(args.upcoming)
        if upcoming:
            print(f"未来 {args.upcoming} 天的发布计划 ({len(upcoming)} 篇):")
            for item in upcoming:
                print(f"  {item['scheduled_at']}: {item['title']}")
        else:
            print(f"未来 {args.upcoming} 天没有发布计划")

    elif args.pending:
        pending = manager.get_pending_articles()
        if pending:
            print(f"待发布的文章 ({len(pending)} 篇):")
            for item in pending:
                print(f"  {item['title']} - {item['id']}")
                print(f"    原计划: {item['scheduled_at']}")
        else:
            print("没有待发布的文章")

    elif args.auto_schedule:
        count = manager.auto_schedule_queue()
        print(f"已自动调度 {count} 篇文章")


if __name__ == '__main__':
    main()