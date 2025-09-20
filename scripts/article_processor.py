#!/usr/bin/env python3
"""
文章处理器 - 集成调度管理和内容提取

将文章调度管理器与现有的内容提取流程集成
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# 导入现有模块
from scheduling_manager import SchedulingManager, ArticleStatus, PublishPriority
from state_manager import ArticleStateManager

# 这些模块将被简化处理，因为它们可能不存在
try:
    from wechat_extractor import WeChatExtractor
except ImportError:
    WeChatExtractor = None

try:
    from markdown_generator import MarkdownGenerator
except ImportError:
    MarkdownGenerator = None

try:
    from image_processor import ImageProcessor
except ImportError:
    ImageProcessor = None


class ArticleProcessor:
    """文章处理器 - 整合调度和处理流程"""

    def __init__(self,
                 schedule_file: str = "article_schedule.json",
                 state_file: str = "article_state.json"):
        """
        初始化处理器

        Args:
            schedule_file: 调度文件路径
            state_file: 状态文件路径
        """
        self.scheduler = SchedulingManager(schedule_file)
        self.state_manager = ArticleStateManager(state_file)

        # 条件初始化可选模块
        self.extractor = WeChatExtractor() if WeChatExtractor else None
        self.markdown_generator = MarkdownGenerator() if MarkdownGenerator else None
        self.image_processor = ImageProcessor() if ImageProcessor else None

    def add_article_to_queue(self, url: str, priority: PublishPriority = PublishPriority.NORMAL) -> Optional[str]:
        """
        添加文章到处理队列

        Args:
            url: 文章URL
            priority: 优先级

        Returns:
            队列ID，失败返回None
        """
        print(f"正在添加文章到队列: {url}")

        # 检查文章是否已经处理过
        if self.state_manager.is_article_processed(url):
            print(f"警告: 文章已经处理过: {url}")
            return None

        try:
            # 提取文章基本信息（如果提取器不可用，使用简化数据）
            if self.extractor:
                article_data = self.extractor.extract_basic_info(url)
                if not article_data:
                    print(f"错误: 无法提取文章信息: {url}")
                    return None
            else:
                # 使用简化的文章数据
                article_data = {
                    'url': url,
                    'title': f'文章 - {datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'author': '未知作者',
                    'content': '待提取内容'
                }

            # 添加到调度队列
            queue_id = self.scheduler.add_to_queue(article_data, priority)
            if queue_id:
                print(f"成功添加到队列，ID: {queue_id}")
                # 更新状态管理器
                self.state_manager.record_article({
                    'url': url,
                    'queue_id': queue_id,
                    'status': 'queued',
                    'added_at': datetime.now().isoformat()
                })

            return queue_id

        except Exception as e:
            print(f"错误: 添加文章失败: {e}")
            return None

    def process_pending_articles(self, limit: int = 5) -> int:
        """
        处理待发布的文章

        Args:
            limit: 处理文章数量限制

        Returns:
            成功处理的文章数量
        """
        print(f"开始处理待发布文章...")

        # 获取待发布文章列表
        pending_articles = self.scheduler.get_pending_articles(limit)
        if not pending_articles:
            print("没有待发布的文章")
            return 0

        processed_count = 0

        for article in pending_articles:
            article_id = article['id']
            url = article['url']

            print(f"\n处理文章: {article['title']}")

            # 更新文章状态为处理中
            article['status'] = ArticleStatus.PROCESSING.value
            self.scheduler._save_schedule()

            try:
                # 提取完整内容
                full_content = self.extractor.extract_full_content(url)
                if not full_content:
                    raise Exception("无法提取文章内容")

                # 处理图片
                if full_content.get('images'):
                    processed_images = self.image_processor.process_images(
                        full_content['images'],
                        article['title']
                    )
                    full_content['processed_images'] = processed_images

                # 生成Markdown
                markdown_path = self.markdown_generator.generate(
                    full_content,
                    output_dir="posts"
                )

                # 标记为已发布
                self.scheduler.mark_as_published(
                    article_id,
                    published_url=markdown_path
                )

                # 更新状态管理器
                self.state_manager.update_article_status(url, 'published')

                processed_count += 1
                print(f"✓ 文章处理成功: {article['title']}")

            except Exception as e:
                print(f"✗ 文章处理失败: {e}")
                # 标记为失败
                self.scheduler.mark_as_failed(article_id, str(e))
                self.state_manager.update_article_status(url, 'failed')

        print(f"\n处理完成，成功: {processed_count}/{len(pending_articles)}")
        return processed_count

    def schedule_next_batch(self, count: int = 5) -> int:
        """
        调度下一批文章

        Args:
            count: 调度文章数量

        Returns:
            成功调度的文章数量
        """
        print(f"调度下一批文章...")

        scheduled_count = 0
        queue = self.scheduler.schedule_data['queue'][:count]

        for item in queue:
            if self.scheduler.schedule_article(item['id']):
                scheduled_count += 1
                print(f"已调度: {item['title']}")

        print(f"成功调度 {scheduled_count} 篇文章")
        return scheduled_count

    def get_processing_status(self) -> Dict[str, Any]:
        """获取处理状态汇总"""
        queue_status = self.scheduler.get_queue_status()
        state_summary = self.state_manager.get_summary()

        return {
            'queue': queue_status,
            'state': state_summary,
            'pending_articles': len(self.scheduler.get_pending_articles(1000)),
            'next_publish_time': self._get_next_publish_time()
        }

    def _get_next_publish_time(self) -> Optional[str]:
        """获取下一个发布时间"""
        upcoming = self.scheduler.get_upcoming_schedule(days=1)
        if upcoming:
            return upcoming[0]['scheduled_at']
        return None

    def batch_add_articles(self, urls: List[str],
                          priority: PublishPriority = PublishPriority.NORMAL) -> List[str]:
        """
        批量添加文章到队列

        Args:
            urls: 文章URL列表
            priority: 优先级

        Returns:
            成功添加的队列ID列表
        """
        print(f"批量添加 {len(urls)} 篇文章...")

        queue_ids = []
        for url in urls:
            queue_id = self.add_article_to_queue(url, priority)
            if queue_id:
                queue_ids.append(queue_id)

        print(f"成功添加 {len(queue_ids)}/{len(urls)} 篇文章")
        return queue_ids

    def auto_process_workflow(self) -> Dict[str, int]:
        """
        自动处理工作流
        1. 处理待发布文章
        2. 自动调度队列中的文章

        Returns:
            处理结果统计
        """
        print("执行自动处理工作流...")

        # 处理待发布文章
        processed = self.process_pending_articles()

        # 自动调度新文章
        scheduled = self.scheduler.auto_schedule_queue()

        result = {
            'processed': processed,
            'scheduled': scheduled
        }

        print(f"工作流完成 - 处理: {processed}, 调度: {scheduled}")
        return result


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='文章处理器 - 集成调度和处理')

    # 基本操作
    parser.add_argument('--add', type=str, help='添加文章URL到队列')
    parser.add_argument('--batch-add', type=str, help='从文件批量添加文章URL')
    parser.add_argument('--priority', type=str, default='normal',
                       choices=['low', 'normal', 'high', 'urgent'],
                       help='设置文章优先级')

    # 处理操作
    parser.add_argument('--process', action='store_true', help='处理待发布文章')
    parser.add_argument('--schedule', action='store_true', help='调度下一批文章')
    parser.add_argument('--auto', action='store_true', help='执行自动工作流')

    # 查询操作
    parser.add_argument('--status', action='store_true', help='显示处理状态')

    # 配置
    parser.add_argument('--schedule-file', type=str, default='article_schedule.json',
                       help='调度文件路径')
    parser.add_argument('--state-file', type=str, default='article_state.json',
                       help='状态文件路径')

    args = parser.parse_args()

    # 初始化处理器
    processor = ArticleProcessor(args.schedule_file, args.state_file)

    # 处理优先级
    priority_map = {
        'low': PublishPriority.LOW,
        'normal': PublishPriority.NORMAL,
        'high': PublishPriority.HIGH,
        'urgent': PublishPriority.URGENT
    }
    priority = priority_map[args.priority]

    # 执行操作
    if args.add:
        queue_id = processor.add_article_to_queue(args.add, priority)
        if queue_id:
            print(f"成功添加，队列ID: {queue_id}")
        else:
            print("添加失败")
            sys.exit(1)

    elif args.batch_add:
        # 从文件读取URL列表
        urls_file = Path(args.batch_add)
        if not urls_file.exists():
            print(f"错误: 文件不存在 {urls_file}")
            sys.exit(1)

        urls = []
        with open(urls_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)

        if urls:
            queue_ids = processor.batch_add_articles(urls, priority)
            print(f"成功添加 {len(queue_ids)} 篇文章")
        else:
            print("文件中没有有效的URL")

    elif args.process:
        count = processor.process_pending_articles()
        print(f"处理了 {count} 篇文章")

    elif args.schedule:
        count = processor.schedule_next_batch()
        print(f"调度了 {count} 篇文章")

    elif args.auto:
        result = processor.auto_process_workflow()
        print(f"自动工作流完成:")
        print(f"  处理: {result['processed']} 篇")
        print(f"  调度: {result['scheduled']} 篇")

    elif args.status:
        status = processor.get_processing_status()
        print("\n=== 处理状态 ===")
        print(f"队列大小: {status['queue']['queue_size']}")
        print(f"已调度: {status['queue']['scheduled_count']}")
        print(f"待发布: {status['pending_articles']}")

        if status['next_publish_time']:
            print(f"下次发布: {status['next_publish_time']}")

        stats = status['queue']['statistics']
        print("\n=== 统计信息 ===")
        print(f"总加入队列: {stats['total_queued']}")
        print(f"总调度: {stats['total_scheduled']}")
        print(f"总发布: {stats['total_published']}")
        print(f"总失败: {stats['total_failed']}")
        print(f"总取消: {stats['total_cancelled']}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()