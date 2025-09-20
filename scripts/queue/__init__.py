"""
队列管理系统

提供文章处理的高级调度和队列管理功能
"""

from .celery_app import app
from .models import DatabaseManager, ArticleTask, TaskStatus, TaskPriority
from .tasks import (
    process_article_high,
    process_article_medium,
    process_article_low,
    batch_process_articles,
    scheduled_publish,
    retry_failed_task
)
from .scheduler import ArticleScheduler, get_scheduler
from .monitor import QueueMonitor, get_monitor
from .manager import QueueManager
from .reporting import QueueReporter, get_reporter
from .config import Priority, CELERY_CONFIG, QUEUE_CAPACITY

__version__ = '1.0.0'

__all__ = [
    # Celery应用
    'app',

    # 数据库
    'DatabaseManager',
    'ArticleTask',
    'TaskStatus',
    'TaskPriority',

    # 任务
    'process_article_high',
    'process_article_medium',
    'process_article_low',
    'batch_process_articles',
    'scheduled_publish',
    'retry_failed_task',

    # 管理组件
    'ArticleScheduler',
    'get_scheduler',
    'QueueMonitor',
    'get_monitor',
    'QueueManager',
    'QueueReporter',
    'get_reporter',

    # 配置
    'Priority',
    'CELERY_CONFIG',
    'QUEUE_CAPACITY'
]