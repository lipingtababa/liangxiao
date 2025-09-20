"""
队列管理控制模块
提供队列管理的CLI和API接口
"""

import click
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from tabulate import tabulate
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from .models import (
    DatabaseManager, ArticleTask, TaskStatus, TaskPriority,
    DeadLetterQueue, TaskBatch, QueueConfig
)
from .tasks import (
    process_article_high, process_article_medium, process_article_low,
    batch_process_articles, retry_failed_task
)
from .scheduler import get_scheduler
from .monitor import get_monitor
from .config import Priority, QUEUE_CAPACITY

class QueueManager:
    """队列管理器"""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.scheduler = get_scheduler()
        self.monitor = get_monitor()

    # === 任务管理 ===

    def submit_task(
        self,
        url: str,
        priority: str = 'medium',
        scheduled_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        提交新任务

        Args:
            url: 文章URL
            priority: 优先级 (urgent/high/medium/low/background)
            scheduled_at: 调度时间（可选）
            metadata: 元数据

        Returns:
            任务ID
        """
        task_id = f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(url)}"

        with self.db_manager.get_session() as session:
            # 检查是否已存在
            existing = session.query(ArticleTask).filter_by(url=url).first()
            if existing and existing.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return existing.task_id

            # 创建新任务
            task = ArticleTask(
                task_id=task_id,
                url=url,
                priority=priority,
                priority_score=self._get_priority_score(priority),
                status=TaskStatus.SCHEDULED if scheduled_at else TaskStatus.PENDING,
                scheduled_at=scheduled_at,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            session.add(task)
            session.commit()

            # 如果是立即执行的任务，提交到Celery
            if not scheduled_at:
                self._submit_to_celery(task)
            else:
                # 添加到调度器
                self.scheduler.schedule_article(url, scheduled_at, priority, metadata)

            return task_id

    def submit_batch(
        self,
        urls: List[str],
        priority: str = 'medium',
        batch_name: Optional[str] = None,
        interval_minutes: int = 0
    ) -> str:
        """
        批量提交任务

        Args:
            urls: URL列表
            priority: 优先级
            batch_name: 批次名称
            interval_minutes: 任务间隔（分钟），0表示并发

        Returns:
            批次ID
        """
        batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        with self.db_manager.get_session() as session:
            # 创建批次
            batch = TaskBatch(
                batch_id=batch_id,
                name=batch_name or f"Batch {batch_id}",
                total_tasks=len(urls),
                priority=priority,
                status=TaskStatus.PENDING
            )
            session.add(batch)
            session.commit()

            # 创建任务
            task_ids = []
            base_time = datetime.utcnow() if interval_minutes > 0 else None

            for idx, url in enumerate(urls):
                scheduled_at = None
                if interval_minutes > 0:
                    scheduled_at = base_time + timedelta(minutes=interval_minutes * idx)

                task_id = self.submit_task(
                    url=url,
                    priority=priority,
                    scheduled_at=scheduled_at,
                    metadata={'batch_id': batch.id}
                )
                task_ids.append(task_id)

            # 如果是并发批处理，使用Celery group
            if interval_minutes == 0:
                batch_process_articles.apply_async(
                    args=[urls, {'name': batch_name, 'batch_id': batch.id}]
                )

            return batch_id

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self.db_manager.get_session() as session:
            task = session.query(ArticleTask).filter_by(task_id=task_id).first()
            if not task:
                return False

            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return False

            task.status = TaskStatus.CANCELLED
            session.commit()

            # 从Celery撤销任务
            from celery import current_app
            current_app.control.revoke(task_id, terminate=True)

            # 从调度器移除
            if task.scheduled_at:
                self.scheduler.cancel_scheduled(task_id)

            return True

    def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        with self.db_manager.get_session() as session:
            task = session.query(ArticleTask).filter_by(task_id=task_id).first()
            if not task or task.status != TaskStatus.SCHEDULED:
                return False

            return self.scheduler.pause_scheduled(task_id)

    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        with self.db_manager.get_session() as session:
            task = session.query(ArticleTask).filter_by(task_id=task_id).first()
            if not task or task.status != TaskStatus.SCHEDULED:
                return False

            return self.scheduler.resume_scheduled(task_id)

    def retry_task(self, task_id: str) -> bool:
        """重试任务"""
        return retry_failed_task.apply_async(args=[task_id]).get()

    def change_priority(self, task_id: str, new_priority: str) -> bool:
        """更改任务优先级"""
        with self.db_manager.get_session() as session:
            task = session.query(ArticleTask).filter_by(task_id=task_id).first()
            if not task or task.status not in [TaskStatus.PENDING, TaskStatus.QUEUED]:
                return False

            task.priority = new_priority
            task.priority_score = self._get_priority_score(new_priority)
            session.commit()

            return True

    # === 队列操作 ===

    def clear_queue(self, queue_name: str) -> int:
        """清空队列"""
        with self.db_manager.get_session() as session:
            priority = queue_name.split('_')[0]
            tasks = session.query(ArticleTask).filter(
                ArticleTask.priority == priority,
                ArticleTask.status.in_([TaskStatus.PENDING, TaskStatus.QUEUED])
            ).all()

            count = len(tasks)
            for task in tasks:
                task.status = TaskStatus.CANCELLED

            session.commit()

            # 从Celery清除
            from celery import current_app
            current_app.control.purge()

            return count

    def reorder_queue(self, task_ids: List[str]) -> bool:
        """重新排序队列"""
        with self.db_manager.get_session() as session:
            for idx, task_id in enumerate(task_ids):
                task = session.query(ArticleTask).filter_by(task_id=task_id).first()
                if task:
                    # 使用索引作为新的优先级分数（越小越优先）
                    task.priority_score = 1000 - idx

            session.commit()
            return True

    def move_to_dead_letter(self, task_id: str, reason: str) -> bool:
        """移动任务到死信队列"""
        with self.db_manager.get_session() as session:
            task = session.query(ArticleTask).filter_by(task_id=task_id).first()
            if not task:
                return False

            self.db_manager.add_to_dead_letter(session, task, reason)
            return True

    def resurrect_from_dead_letter(self, dead_letter_id: int) -> Optional[str]:
        """从死信队列恢复任务"""
        with self.db_manager.get_session() as session:
            dead_letter = session.query(DeadLetterQueue).get(dead_letter_id)
            if not dead_letter or not dead_letter.can_retry:
                return None

            # 重新创建任务
            task_data = dead_letter.original_task_data
            new_task_id = self.submit_task(
                url=task_data.get('url'),
                priority=task_data.get('priority', 'medium'),
                metadata=task_data.get('metadata', {})
            )

            # 删除死信记录
            session.delete(dead_letter)
            session.commit()

            return new_task_id

    # === 批量操作 ===

    def bulk_cancel(self, filter_criteria: Dict[str, Any]) -> int:
        """批量取消任务"""
        with self.db_manager.get_session() as session:
            query = session.query(ArticleTask)

            # 应用过滤条件
            if filter_criteria.get('status'):
                query = query.filter_by(status=filter_criteria['status'])
            if filter_criteria.get('priority'):
                query = query.filter_by(priority=filter_criteria['priority'])
            if filter_criteria.get('before'):
                query = query.filter(ArticleTask.created_at < filter_criteria['before'])

            tasks = query.all()
            count = 0

            for task in tasks:
                if self.cancel_task(task.task_id):
                    count += 1

            return count

    def bulk_retry(self, filter_criteria: Dict[str, Any]) -> int:
        """批量重试任务"""
        with self.db_manager.get_session() as session:
            query = session.query(ArticleTask).filter_by(status=TaskStatus.FAILED)

            # 应用过滤条件
            if filter_criteria.get('priority'):
                query = query.filter_by(priority=filter_criteria['priority'])
            if filter_criteria.get('after'):
                query = query.filter(ArticleTask.failed_at > filter_criteria['after'])

            tasks = query.all()
            count = 0

            for task in tasks:
                if self.retry_task(task.task_id):
                    count += 1

            return count

    def bulk_change_priority(self, task_ids: List[str], new_priority: str) -> int:
        """批量更改优先级"""
        count = 0
        for task_id in task_ids:
            if self.change_priority(task_id, new_priority):
                count += 1
        return count

    # === 导入/导出 ===

    def export_queue(self, queue_name: Optional[str] = None) -> Dict[str, Any]:
        """导出队列数据"""
        with self.db_manager.get_session() as session:
            query = session.query(ArticleTask)

            if queue_name:
                priority = queue_name.split('_')[0]
                query = query.filter_by(priority=priority)

            tasks = query.all()

            return {
                'export_time': datetime.utcnow().isoformat(),
                'queue_name': queue_name,
                'total_tasks': len(tasks),
                'tasks': [task.to_dict() for task in tasks]
            }

    def import_queue(self, data: Dict[str, Any]) -> int:
        """导入队列数据"""
        imported = 0
        for task_data in data.get('tasks', []):
            try:
                self.submit_task(
                    url=task_data['url'],
                    priority=task_data.get('priority', 'medium'),
                    scheduled_at=datetime.fromisoformat(task_data['scheduled_at'])
                    if task_data.get('scheduled_at') else None,
                    metadata=task_data.get('metadata', {})
                )
                imported += 1
            except Exception as e:
                print(f"导入任务失败: {e}")

        return imported

    # === 配置管理 ===

    def update_queue_config(self, queue_name: str, config: Dict[str, Any]) -> bool:
        """更新队列配置"""
        with self.db_manager.get_session() as session:
            queue_config = session.query(QueueConfig).filter_by(queue_name=queue_name).first()

            if not queue_config:
                queue_config = QueueConfig(queue_name=queue_name)
                session.add(queue_config)

            for key, value in config.items():
                if hasattr(queue_config, key):
                    setattr(queue_config, key, value)

            queue_config.updated_at = datetime.utcnow()
            session.commit()

            return True

    def get_queue_config(self, queue_name: str) -> Dict[str, Any]:
        """获取队列配置"""
        with self.db_manager.get_session() as session:
            queue_config = session.query(QueueConfig).filter_by(queue_name=queue_name).first()

            if queue_config:
                return {
                    'queue_name': queue_config.queue_name,
                    'enabled': queue_config.enabled,
                    'max_size': queue_config.max_size,
                    'current_size': queue_config.current_size,
                    'rate_limit': queue_config.rate_limit,
                    'default_priority': queue_config.default_priority,
                    'max_retries': queue_config.max_retries,
                    'retry_delay': queue_config.retry_delay,
                    'task_timeout': queue_config.task_timeout
                }

            return {
                'queue_name': queue_name,
                'enabled': True,
                'max_size': QUEUE_CAPACITY.get(queue_name, 1000)
            }

    # === 辅助方法 ===

    def _get_priority_score(self, priority: str) -> int:
        """获取优先级分数"""
        scores = {
            'urgent': Priority.URGENT,
            'high': Priority.HIGH,
            'medium': Priority.MEDIUM,
            'low': Priority.LOW,
            'background': Priority.BACKGROUND
        }
        return scores.get(priority, Priority.MEDIUM)

    def _submit_to_celery(self, task: ArticleTask):
        """提交任务到Celery"""
        task_func_map = {
            'high': process_article_high,
            'urgent': process_article_high,
            'medium': process_article_medium,
            'low': process_article_low,
            'background': process_article_low
        }

        task_func = task_func_map.get(task.priority, process_article_medium)
        task_func.apply_async(
            args=[task.url, task.metadata],
            task_id=task.task_id,
            priority=task.priority_score
        )

# CLI命令组
@click.group()
def cli():
    """队列管理命令行工具"""
    pass

@cli.command()
@click.argument('url')
@click.option('--priority', '-p', default='medium', help='任务优先级')
@click.option('--schedule', '-s', help='调度时间 (ISO格式)')
def submit(url, priority, schedule):
    """提交新任务"""
    manager = QueueManager()

    scheduled_at = None
    if schedule:
        scheduled_at = datetime.fromisoformat(schedule)

    task_id = manager.submit_task(url, priority, scheduled_at)
    click.echo(f"任务已提交: {task_id}")

@cli.command()
@click.argument('file_path')
@click.option('--priority', '-p', default='medium', help='任务优先级')
@click.option('--interval', '-i', default=0, help='任务间隔（分钟）')
def batch(file_path, priority, interval):
    """批量提交任务"""
    manager = QueueManager()

    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    batch_id = manager.submit_batch(urls, priority, interval_minutes=interval)
    click.echo(f"批次已创建: {batch_id}, 包含 {len(urls)} 个任务")

@cli.command()
@click.argument('task_id')
def cancel(task_id):
    """取消任务"""
    manager = QueueManager()

    if manager.cancel_task(task_id):
        click.echo(f"任务已取消: {task_id}")
    else:
        click.echo(f"无法取消任务: {task_id}")

@cli.command()
@click.argument('task_id')
def retry(task_id):
    """重试任务"""
    manager = QueueManager()

    if manager.retry_task(task_id):
        click.echo(f"任务已重试: {task_id}")
    else:
        click.echo(f"无法重试任务: {task_id}")

@cli.command()
def status():
    """显示队列状态"""
    monitor = get_monitor()
    status = monitor.get_realtime_status()

    # 显示队列信息
    click.echo("\n队列状态:")
    for queue_name, info in status['queues'].items():
        click.echo(f"  {queue_name}: {info['size']}/{info['capacity']} ({info['usage_percent']:.1f}%)")

    # 显示任务统计
    click.echo("\n任务统计:")
    for status_type, count in status['tasks'].items():
        click.echo(f"  {status_type}: {count}")

    # 显示告警
    if status['alerts']:
        click.echo("\n告警:")
        for alert in status['alerts']:
            click.echo(f"  [{alert['level']}] {alert['message']}")

@cli.command()
def health():
    """健康检查"""
    monitor = get_monitor()
    report = monitor.generate_health_report()

    click.echo(f"\n健康状态: {report['overall_health']}")
    click.echo(f"健康分数: {report['score']}/100")

    if report['issues']:
        click.echo("\n问题:")
        for issue in report['issues']:
            click.echo(f"  - {issue}")

@cli.command()
@click.option('--queue', '-q', help='队列名称')
@click.option('--output', '-o', help='输出文件')
def export(queue, output):
    """导出队列数据"""
    manager = QueueManager()
    data = manager.export_queue(queue)

    if output:
        with open(output, 'w') as f:
            json.dump(data, f, indent=2)
        click.echo(f"已导出到: {output}")
    else:
        click.echo(json.dumps(data, indent=2))

@cli.command()
@click.argument('file_path')
def import_data(file_path):
    """导入队列数据"""
    manager = QueueManager()

    with open(file_path, 'r') as f:
        data = json.load(f)

    count = manager.import_queue(data)
    click.echo(f"已导入 {count} 个任务")

if __name__ == '__main__':
    cli()