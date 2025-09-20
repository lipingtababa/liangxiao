"""
队列配置文件
定义队列优先级、重试策略和其他配置
"""

import os
from typing import Dict, Any
from datetime import timedelta

# Redis配置
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)

# 构建Redis URL
if REDIS_PASSWORD:
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
else:
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# 数据库配置
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:password@localhost:5432/article_queue'
)

# Celery配置
CELERY_CONFIG = {
    'broker_url': REDIS_URL,
    'result_backend': REDIS_URL,
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'Asia/Shanghai',
    'enable_utc': True,

    # 任务路由配置 - 基于优先级的队列
    'task_routes': {
        'tasks.process_article_high': {'queue': 'high_priority'},
        'tasks.process_article_medium': {'queue': 'medium_priority'},
        'tasks.process_article_low': {'queue': 'low_priority'},
        'tasks.scheduled_publish': {'queue': 'scheduled'},
        'tasks.retry_failed': {'queue': 'retry'},
    },

    # 任务优先级配置
    'task_queue_max_priority': 10,
    'task_default_priority': 5,

    # 重试配置
    'task_acks_late': True,
    'task_reject_on_worker_lost': True,
    'task_ignore_result': False,

    # 任务软时限和硬时限
    'task_soft_time_limit': 300,  # 5分钟软时限
    'task_time_limit': 600,  # 10分钟硬时限

    # 结果过期时间
    'result_expires': 3600 * 24,  # 结果保存24小时
}

# 队列优先级定义
class Priority:
    """队列优先级枚举"""
    URGENT = 10  # 紧急
    HIGH = 8     # 高
    MEDIUM = 5   # 中
    LOW = 3      # 低
    BACKGROUND = 1  # 后台任务

# 任务重试策略
RETRY_POLICY = {
    'max_retries': 3,
    'interval_start': 60,  # 首次重试延迟60秒
    'interval_step': 120,  # 每次重试增加120秒
    'interval_max': 3600,  # 最大重试间隔1小时
}

# 速率限制配置
RATE_LIMITS = {
    'translation_api': '100/h',  # 翻译API每小时100次
    'wechat_fetch': '30/m',      # 微信内容获取每分钟30次
    'image_download': '50/m',    # 图片下载每分钟50次
}

# 批处理配置
BATCH_CONFIG = {
    'max_batch_size': 10,  # 最大批处理大小
    'batch_timeout': 60,   # 批处理超时时间（秒）
    'min_batch_size': 3,   # 最小批处理大小
}

# 调度配置
SCHEDULE_CONFIG = {
    'timezone': 'Asia/Shanghai',
    'max_scheduled_tasks': 100,  # 最大调度任务数
    'schedule_check_interval': 60,  # 调度检查间隔（秒）
}

# 监控配置
MONITORING_CONFIG = {
    'enable_prometheus': True,
    'prometheus_port': 9090,
    'enable_flower': True,
    'flower_port': 5555,
    'flower_basic_auth': os.environ.get('FLOWER_BASIC_AUTH', 'admin:password'),
}

# 死信队列配置
DEAD_LETTER_CONFIG = {
    'queue_name': 'dead_letter',
    'max_retries_before_dead_letter': 5,
    'retention_days': 7,  # 死信保留天数
}

# 队列容量配置
QUEUE_CAPACITY = {
    'high_priority': 100,
    'medium_priority': 500,
    'low_priority': 1000,
    'scheduled': 200,
    'retry': 100,
    'dead_letter': 500,
}

# 告警阈值配置
ALERT_THRESHOLDS = {
    'queue_size_warning': 80,  # 队列大小警告阈值（百分比）
    'queue_size_critical': 95,  # 队列大小严重阈值（百分比）
    'task_failure_rate_warning': 10,  # 任务失败率警告（百分比）
    'task_failure_rate_critical': 25,  # 任务失败率严重（百分比）
    'processing_time_warning': 300,  # 处理时间警告（秒）
    'processing_time_critical': 600,  # 处理时间严重（秒）
}

def get_celery_config() -> Dict[str, Any]:
    """获取Celery配置"""
    return CELERY_CONFIG

def get_queue_priority(task_type: str) -> int:
    """根据任务类型获取队列优先级"""
    priority_map = {
        'urgent': Priority.URGENT,
        'high': Priority.HIGH,
        'medium': Priority.MEDIUM,
        'low': Priority.LOW,
        'background': Priority.BACKGROUND,
    }
    return priority_map.get(task_type, Priority.MEDIUM)