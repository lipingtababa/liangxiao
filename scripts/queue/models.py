"""
数据库模型定义
用于队列任务持久化和管理
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from sqlalchemy import (
    create_engine, Column, String, Integer, DateTime,
    Text, JSON, Boolean, Float, Index, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from .config import DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 任务状态枚举
class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"

# 任务优先级枚举
class TaskPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"

class ArticleTask(Base):
    """文章处理任务模型"""
    __tablename__ = "article_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)

    # 任务基本信息
    url = Column(Text, nullable=False)
    title = Column(String(500))
    author = Column(String(255))

    # 任务状态和优先级
    status = Column(String(50), default=TaskStatus.PENDING, index=True)
    priority = Column(String(50), default=TaskPriority.MEDIUM, index=True)
    priority_score = Column(Integer, default=5, index=True)

    # 调度信息
    scheduled_at = Column(DateTime, index=True)
    publish_at = Column(DateTime)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    queued_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    failed_at = Column(DateTime)

    # 重试信息
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_retry_at = Column(DateTime)
    next_retry_at = Column(DateTime)

    # 错误信息
    error_message = Column(Text)
    error_traceback = Column(Text)

    # 任务结果
    result = Column(JSON)

    # 处理时间统计
    processing_time = Column(Float)  # 秒
    queue_time = Column(Float)  # 秒

    # 元数据
    metadata = Column(JSON, default={})

    # 资源限制
    cpu_limit = Column(Float)
    memory_limit = Column(Integer)  # MB

    # 关联
    batch_id = Column(Integer, ForeignKey('task_batches.id'))
    batch = relationship("TaskBatch", back_populates="tasks")

    # 索引
    __table_args__ = (
        Index('idx_status_priority', 'status', 'priority_score'),
        Index('idx_scheduled', 'scheduled_at', 'status'),
        Index('idx_created_status', 'created_at', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'url': self.url,
            'title': self.title,
            'status': self.status,
            'priority': self.priority,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'retry_count': self.retry_count,
            'error_message': self.error_message,
            'processing_time': self.processing_time,
        }

class TaskBatch(Base):
    """任务批次模型"""
    __tablename__ = "task_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(255), unique=True, index=True, nullable=False)

    # 批次信息
    name = Column(String(255))
    description = Column(Text)

    # 状态
    status = Column(String(50), default=TaskStatus.PENDING, index=True)
    priority = Column(String(50), default=TaskPriority.MEDIUM)

    # 统计
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # 关联
    tasks = relationship("ArticleTask", back_populates="batch")

    # 元数据
    metadata = Column(JSON, default={})

class QueueStatistics(Base):
    """队列统计模型"""
    __tablename__ = "queue_statistics"

    id = Column(Integer, primary_key=True, index=True)

    # 时间戳
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # 队列统计
    queue_name = Column(String(100), index=True)
    queue_size = Column(Integer)

    # 任务统计
    pending_tasks = Column(Integer)
    running_tasks = Column(Integer)
    completed_tasks = Column(Integer)
    failed_tasks = Column(Integer)

    # 性能指标
    avg_processing_time = Column(Float)  # 秒
    avg_queue_time = Column(Float)  # 秒
    success_rate = Column(Float)  # 百分比

    # 资源使用
    cpu_usage = Column(Float)  # 百分比
    memory_usage = Column(Float)  # MB

    # 吞吐量
    tasks_per_minute = Column(Float)
    tasks_per_hour = Column(Float)

    # 索引
    __table_args__ = (
        Index('idx_stats_time_queue', 'timestamp', 'queue_name'),
    )

class DeadLetterQueue(Base):
    """死信队列模型"""
    __tablename__ = "dead_letter_queue"

    id = Column(Integer, primary_key=True, index=True)

    # 原始任务信息
    original_task_id = Column(String(255), index=True)
    original_task_data = Column(JSON)

    # 失败信息
    failure_reason = Column(Text)
    failure_count = Column(Integer)
    last_failure_at = Column(DateTime, default=datetime.utcnow)

    # 状态
    status = Column(String(50), default='dead', index=True)
    can_retry = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)

    # 元数据
    metadata = Column(JSON, default={})

class QueueConfig(Base):
    """队列配置模型"""
    __tablename__ = "queue_configs"

    id = Column(Integer, primary_key=True, index=True)

    # 配置信息
    queue_name = Column(String(100), unique=True, index=True)
    enabled = Column(Boolean, default=True)

    # 容量限制
    max_size = Column(Integer)
    current_size = Column(Integer, default=0)

    # 速率限制
    rate_limit = Column(String(50))  # 例如: "100/h"

    # 优先级配置
    default_priority = Column(Integer, default=5)

    # 重试配置
    max_retries = Column(Integer, default=3)
    retry_delay = Column(Integer, default=60)  # 秒

    # 超时配置
    task_timeout = Column(Integer, default=300)  # 秒

    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 元数据
    metadata = Column(JSON, default={})

# 数据库助手类
class DatabaseManager:
    """数据库管理器"""

    @staticmethod
    def create_tables():
        """创建所有表"""
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def get_session() -> Session:
        """获取数据库会话"""
        return SessionLocal()

    @staticmethod
    def add_task(session: Session, task_data: Dict[str, Any]) -> ArticleTask:
        """添加新任务"""
        task = ArticleTask(**task_data)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def update_task_status(session: Session, task_id: str, status: TaskStatus, **kwargs):
        """更新任务状态"""
        task = session.query(ArticleTask).filter_by(task_id=task_id).first()
        if task:
            task.status = status
            for key, value in kwargs.items():
                setattr(task, key, value)

            # 更新时间戳
            if status == TaskStatus.QUEUED:
                task.queued_at = datetime.utcnow()
            elif status == TaskStatus.IN_PROGRESS:
                task.started_at = datetime.utcnow()
            elif status == TaskStatus.COMPLETED:
                task.completed_at = datetime.utcnow()
                if task.started_at:
                    task.processing_time = (task.completed_at - task.started_at).total_seconds()
            elif status == TaskStatus.FAILED:
                task.failed_at = datetime.utcnow()

            session.commit()

    @staticmethod
    def get_pending_tasks(session: Session, limit: int = 10) -> List[ArticleTask]:
        """获取待处理任务"""
        return session.query(ArticleTask).filter_by(
            status=TaskStatus.PENDING
        ).order_by(
            ArticleTask.priority_score.desc(),
            ArticleTask.created_at
        ).limit(limit).all()

    @staticmethod
    def get_scheduled_tasks(session: Session) -> List[ArticleTask]:
        """获取已调度的任务"""
        now = datetime.utcnow()
        return session.query(ArticleTask).filter(
            ArticleTask.status == TaskStatus.SCHEDULED,
            ArticleTask.scheduled_at <= now
        ).all()

    @staticmethod
    def add_to_dead_letter(session: Session, task: ArticleTask, reason: str):
        """将任务添加到死信队列"""
        from datetime import timedelta

        dead_letter = DeadLetterQueue(
            original_task_id=task.task_id,
            original_task_data=task.to_dict(),
            failure_reason=reason,
            failure_count=task.retry_count,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        session.add(dead_letter)

        # 更新原任务状态
        task.status = TaskStatus.DEAD_LETTER

        session.commit()

    @staticmethod
    def get_queue_statistics(session: Session, queue_name: str = None) -> Dict[str, Any]:
        """获取队列统计信息"""
        query = session.query(QueueStatistics)
        if queue_name:
            query = query.filter_by(queue_name=queue_name)

        stats = query.order_by(QueueStatistics.timestamp.desc()).first()
        if stats:
            return {
                'timestamp': stats.timestamp,
                'queue_size': stats.queue_size,
                'pending_tasks': stats.pending_tasks,
                'running_tasks': stats.running_tasks,
                'completed_tasks': stats.completed_tasks,
                'failed_tasks': stats.failed_tasks,
                'avg_processing_time': stats.avg_processing_time,
                'success_rate': stats.success_rate,
                'tasks_per_hour': stats.tasks_per_hour,
            }
        return {}

# 初始化数据库
if __name__ == "__main__":
    DatabaseManager.create_tables()
    print("数据库表已创建")