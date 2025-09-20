"""
Celery任务定义
包含文章处理、调度、监控等任务
"""

import os
import sys
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from celery import Task, group, chain
from celery.exceptions import SoftTimeLimitExceeded, Retry
from sqlalchemy.orm import Session

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .celery_app import app
from .models import (
    DatabaseManager, ArticleTask, TaskStatus, TaskPriority,
    QueueStatistics, DeadLetterQueue, TaskBatch
)
from .config import Priority, RETRY_POLICY, RATE_LIMITS

# 导入文章处理相关模块
from extract_content_with_state import extract_from_url
from markdown_generator import MarkdownGenerator
from image_processor import ImageProcessor
from state_manager import ArticleStateManager

# 基础任务类
class BaseArticleTask(Task):
    """基础文章处理任务类"""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.state_manager = ArticleStateManager()

    def before_start(self, task_id, args, kwargs):
        """任务开始前的钩子"""
        with self.db_manager.get_session() as session:
            self.db_manager.update_task_status(
                session, task_id, TaskStatus.IN_PROGRESS
            )

    def on_success(self, retval, task_id, args, kwargs):
        """任务成功完成的钩子"""
        with self.db_manager.get_session() as session:
            self.db_manager.update_task_status(
                session, task_id, TaskStatus.COMPLETED,
                result=retval
            )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败的钩子"""
        with self.db_manager.get_session() as session:
            task = session.query(ArticleTask).filter_by(task_id=task_id).first()
            if task:
                task.retry_count += 1
                task.error_message = str(exc)
                task.error_traceback = str(einfo)

                # 检查是否需要加入死信队列
                if task.retry_count >= task.max_retries:
                    self.db_manager.add_to_dead_letter(session, task, str(exc))
                else:
                    # 设置重试
                    task.status = TaskStatus.RETRYING
                    task.next_retry_at = datetime.utcnow() + timedelta(
                        seconds=RETRY_POLICY['interval_start'] * task.retry_count
                    )
                session.commit()

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """任务重试的钩子"""
        with self.db_manager.get_session() as session:
            self.db_manager.update_task_status(
                session, task_id, TaskStatus.RETRYING,
                last_retry_at=datetime.utcnow()
            )

# 高优先级文章处理任务
@app.task(
    bind=True,
    base=BaseArticleTask,
    name='tasks.process_article_high',
    queue='high_priority',
    priority=Priority.HIGH,
    rate_limit=RATE_LIMITS['wechat_fetch']
)
def process_article_high(self, url: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理高优先级文章"""
    return _process_article(self, url, task_data, priority='high')

# 中优先级文章处理任务
@app.task(
    bind=True,
    base=BaseArticleTask,
    name='tasks.process_article_medium',
    queue='medium_priority',
    priority=Priority.MEDIUM,
    rate_limit=RATE_LIMITS['wechat_fetch']
)
def process_article_medium(self, url: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理中优先级文章"""
    return _process_article(self, url, task_data, priority='medium')

# 低优先级文章处理任务
@app.task(
    bind=True,
    base=BaseArticleTask,
    name='tasks.process_article_low',
    queue='low_priority',
    priority=Priority.LOW,
    rate_limit=RATE_LIMITS['wechat_fetch']
)
def process_article_low(self, url: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理低优先级文章"""
    return _process_article(self, url, task_data, priority='low')

def _process_article(self, url: str, task_data: Dict[str, Any], priority: str) -> Dict[str, Any]:
    """文章处理核心逻辑"""
    try:
        result = {
            'url': url,
            'priority': priority,
            'started_at': datetime.utcnow().isoformat(),
            'steps': []
        }

        # 步骤1：提取文章内容
        print(f"[{priority.upper()}] 开始提取文章内容: {url}")
        article_data = extract_from_url(url)
        if not article_data:
            raise ValueError("无法提取文章内容")

        result['steps'].append({
            'name': '内容提取',
            'status': 'completed',
            'data': {
                'title': article_data.get('title'),
                'author': article_data.get('author'),
                'word_count': article_data.get('word_count')
            }
        })

        # 步骤2：处理图片
        if article_data.get('images'):
            print(f"[{priority.upper()}] 处理 {len(article_data['images'])} 张图片")
            image_processor = ImageProcessor()
            processed_images = []

            for img in article_data['images']:
                try:
                    processed_img = image_processor.process(img['src'])
                    processed_images.append(processed_img)
                except Exception as e:
                    print(f"图片处理失败: {e}")

            result['steps'].append({
                'name': '图片处理',
                'status': 'completed',
                'data': {
                    'total_images': len(article_data['images']),
                    'processed': len(processed_images)
                }
            })

        # 步骤3：生成Markdown
        print(f"[{priority.upper()}] 生成Markdown文件")
        markdown_gen = MarkdownGenerator()
        markdown_content = markdown_gen.generate(article_data)

        result['steps'].append({
            'name': 'Markdown生成',
            'status': 'completed',
            'data': {
                'content_length': len(markdown_content)
            }
        })

        # 步骤4：保存到文件系统
        output_file = _save_article(article_data, markdown_content)
        result['steps'].append({
            'name': '文件保存',
            'status': 'completed',
            'data': {
                'file_path': output_file
            }
        })

        result['completed_at'] = datetime.utcnow().isoformat()
        result['status'] = 'success'

        return result

    except SoftTimeLimitExceeded:
        # 软时限超时
        raise self.retry(countdown=60, max_retries=3)

    except Exception as e:
        # 记录错误并重试
        print(f"处理文章失败: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

def _save_article(article_data: Dict[str, Any], markdown_content: str) -> str:
    """保存文章到文件系统"""
    from pathlib import Path

    # 生成文件名
    title_slug = article_data.get('title', 'untitled').replace(' ', '-')[:50]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{title_slug}.md"

    # 保存文件
    output_dir = Path('posts')
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / filename
    output_file.write_text(markdown_content, encoding='utf-8')

    return str(output_file)

# 调度发布任务
@app.task(
    bind=True,
    name='tasks.scheduled_publish',
    queue='scheduled'
)
def scheduled_publish(self, article_id: int, publish_data: Dict[str, Any]) -> Dict[str, Any]:
    """调度发布文章"""
    try:
        print(f"发布文章 ID: {article_id}")

        # 这里添加实际的发布逻辑
        # 例如：推送到网站、发送通知等

        result = {
            'article_id': article_id,
            'published_at': datetime.utcnow().isoformat(),
            'status': 'published'
        }

        return result

    except Exception as e:
        print(f"发布失败: {e}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

# 重试失败任务
@app.task(
    bind=True,
    name='tasks.retry_failed',
    queue='retry'
)
def retry_failed_task(self, task_id: str) -> Dict[str, Any]:
    """重试失败的任务"""
    with DatabaseManager.get_session() as session:
        task = session.query(ArticleTask).filter_by(task_id=task_id).first()
        if not task:
            return {'status': 'error', 'message': '任务不存在'}

        if task.retry_count >= task.max_retries:
            return {'status': 'error', 'message': '已达最大重试次数'}

        # 根据优先级重新提交任务
        if task.priority == TaskPriority.HIGH:
            process_article_high.apply_async(
                args=[task.url, task.metadata],
                task_id=task.task_id
            )
        elif task.priority == TaskPriority.LOW:
            process_article_low.apply_async(
                args=[task.url, task.metadata],
                task_id=task.task_id
            )
        else:
            process_article_medium.apply_async(
                args=[task.url, task.metadata],
                task_id=task.task_id
            )

        return {'status': 'retrying', 'task_id': task_id}

# 批处理任务
@app.task(
    bind=True,
    name='tasks.batch_process',
    queue='medium_priority'
)
def batch_process_articles(self, urls: List[str], batch_config: Dict[str, Any]) -> Dict[str, Any]:
    """批量处理文章"""
    batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    with DatabaseManager.get_session() as session:
        # 创建批次
        batch = TaskBatch(
            batch_id=batch_id,
            name=batch_config.get('name', 'Batch Processing'),
            total_tasks=len(urls),
            status=TaskStatus.IN_PROGRESS
        )
        session.add(batch)
        session.commit()

        # 创建任务组
        job = group([
            process_article_medium.s(url, {'batch_id': batch.id})
            for url in urls
        ])

        # 执行批处理
        result = job.apply_async()

        return {
            'batch_id': batch_id,
            'total_tasks': len(urls),
            'status': 'processing'
        }

# 监控任务
@app.task(name='scripts.queue.tasks.check_scheduled_publications')
def check_scheduled_publications():
    """检查并执行调度发布"""
    with DatabaseManager.get_session() as session:
        tasks = DatabaseManager.get_scheduled_tasks(session)

        for task in tasks:
            print(f"执行调度发布: {task.task_id}")
            scheduled_publish.apply_async(
                args=[task.id, task.metadata],
                task_id=f"publish_{task.task_id}"
            )

            task.status = TaskStatus.QUEUED
            session.commit()

        return {'processed': len(tasks)}

@app.task(name='scripts.queue.tasks.cleanup_dead_letter_queue')
def cleanup_dead_letter_queue():
    """清理过期的死信队列"""
    with DatabaseManager.get_session() as session:
        expired = session.query(DeadLetterQueue).filter(
            DeadLetterQueue.expires_at <= datetime.utcnow()
        ).all()

        for item in expired:
            session.delete(item)

        session.commit()
        return {'cleaned': len(expired)}

@app.task(name='scripts.queue.tasks.generate_queue_statistics')
def generate_queue_statistics():
    """生成队列统计信息"""
    from celery import current_app

    stats = {
        'timestamp': datetime.utcnow().isoformat(),
        'queues': {}
    }

    # 获取各队列的信息
    inspect = current_app.control.inspect()
    active = inspect.active()
    scheduled = inspect.scheduled()
    reserved = inspect.reserved()

    if active:
        for worker, tasks in active.items():
            stats['queues']['active'] = len(tasks)

    if scheduled:
        for worker, tasks in scheduled.items():
            stats['queues']['scheduled'] = len(tasks)

    if reserved:
        for worker, tasks in reserved.items():
            stats['queues']['reserved'] = len(tasks)

    # 保存统计信息
    with DatabaseManager.get_session() as session:
        for queue_name, size in stats['queues'].items():
            queue_stat = QueueStatistics(
                queue_name=queue_name,
                queue_size=size,
                timestamp=datetime.utcnow()
            )
            session.add(queue_stat)
        session.commit()

    return stats

@app.task(name='scripts.queue.tasks.check_queue_health')
def check_queue_health():
    """检查队列健康状态"""
    from .config import ALERT_THRESHOLDS, QUEUE_CAPACITY

    alerts = []

    with DatabaseManager.get_session() as session:
        # 检查各队列大小
        for queue_name, capacity in QUEUE_CAPACITY.items():
            # 获取当前队列大小
            current_size = session.query(ArticleTask).filter_by(
                status=TaskStatus.QUEUED
            ).count()

            usage_percent = (current_size / capacity) * 100

            if usage_percent >= ALERT_THRESHOLDS['queue_size_critical']:
                alerts.append({
                    'level': 'critical',
                    'queue': queue_name,
                    'message': f'队列使用率严重: {usage_percent:.1f}%'
                })
            elif usage_percent >= ALERT_THRESHOLDS['queue_size_warning']:
                alerts.append({
                    'level': 'warning',
                    'queue': queue_name,
                    'message': f'队列使用率警告: {usage_percent:.1f}%'
                })

        # 检查失败率
        total_tasks = session.query(ArticleTask).count()
        failed_tasks = session.query(ArticleTask).filter_by(
            status=TaskStatus.FAILED
        ).count()

        if total_tasks > 0:
            failure_rate = (failed_tasks / total_tasks) * 100

            if failure_rate >= ALERT_THRESHOLDS['task_failure_rate_critical']:
                alerts.append({
                    'level': 'critical',
                    'metric': 'failure_rate',
                    'message': f'任务失败率严重: {failure_rate:.1f}%'
                })
            elif failure_rate >= ALERT_THRESHOLDS['task_failure_rate_warning']:
                alerts.append({
                    'level': 'warning',
                    'metric': 'failure_rate',
                    'message': f'任务失败率警告: {failure_rate:.1f}%'
                })

    # 发送告警（这里可以接入告警系统）
    if alerts:
        print(f"队列健康检查告警: {json.dumps(alerts, ensure_ascii=False, indent=2)}")

    return {'alerts': alerts, 'checked_at': datetime.utcnow().isoformat()}