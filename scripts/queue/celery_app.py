"""
Celery应用初始化
"""

from celery import Celery
from .config import get_celery_config

# 创建Celery应用实例
app = Celery('article_queue')

# 加载配置
app.config_from_object(get_celery_config())

# 自动发现任务
app.autodiscover_tasks(['scripts.queue'], related_name='tasks')

# 配置beat调度器（用于定时任务）
app.conf.beat_schedule = {
    'check-scheduled-tasks': {
        'task': 'scripts.queue.tasks.check_scheduled_publications',
        'schedule': 60.0,  # 每60秒检查一次
    },
    'cleanup-dead-letters': {
        'task': 'scripts.queue.tasks.cleanup_dead_letter_queue',
        'schedule': 3600.0 * 24,  # 每天清理一次
    },
    'generate-queue-stats': {
        'task': 'scripts.queue.tasks.generate_queue_statistics',
        'schedule': 300.0,  # 每5分钟生成一次统计
    },
    'check-queue-health': {
        'task': 'scripts.queue.tasks.check_queue_health',
        'schedule': 60.0,  # 每分钟检查一次健康状态
    },
}