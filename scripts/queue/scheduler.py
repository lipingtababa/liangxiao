"""
调度器管理模块
处理文章的定时发布和调度
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from sqlalchemy.orm import Session

from .models import DatabaseManager, ArticleTask, TaskStatus, TaskPriority
from .tasks import process_article_high, process_article_medium, process_article_low, scheduled_publish
from .config import DATABASE_URL, SCHEDULE_CONFIG

class ArticleScheduler:
    """文章调度器"""

    def __init__(self):
        # 配置作业存储
        jobstores = {
            'default': SQLAlchemyJobStore(url=DATABASE_URL)
        }

        # 配置执行器
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }

        # 调度器配置
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 60
        }

        # 创建调度器
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=SCHEDULE_CONFIG['timezone']
        )

        self.db_manager = DatabaseManager()

    def start(self):
        """启动调度器"""
        self.scheduler.start()
        print("调度器已启动")

        # 恢复未完成的调度任务
        self._restore_scheduled_tasks()

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        print("调度器已停止")

    def schedule_article(
        self,
        url: str,
        publish_at: datetime,
        priority: str = 'medium',
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        调度文章发布

        Args:
            url: 文章URL
            publish_at: 发布时间
            priority: 优先级
            metadata: 元数据

        Returns:
            任务ID
        """
        # 创建任务ID
        task_id = f"article_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(url)}"

        # 保存到数据库
        with self.db_manager.get_session() as session:
            task = ArticleTask(
                task_id=task_id,
                url=url,
                status=TaskStatus.SCHEDULED,
                priority=priority,
                scheduled_at=publish_at,
                publish_at=publish_at,
                metadata=metadata or {}
            )
            session.add(task)
            session.commit()

            # 根据优先级选择任务
            task_func = self._get_task_by_priority(priority)

            # 添加到调度器
            job = self.scheduler.add_job(
                func=self._execute_scheduled_task,
                trigger=DateTrigger(run_date=publish_at),
                args=[task_id, url, priority, metadata],
                id=task_id,
                name=f"Publish article: {url}",
                replace_existing=True
            )

            print(f"文章已调度: {task_id}, 发布时间: {publish_at}")
            return task_id

    def schedule_batch(
        self,
        articles: List[Dict[str, Any]],
        interval_minutes: int = 30
    ) -> List[str]:
        """
        批量调度文章

        Args:
            articles: 文章列表，每个包含url, priority, metadata
            interval_minutes: 发布间隔（分钟）

        Returns:
            任务ID列表
        """
        task_ids = []
        base_time = datetime.utcnow() + timedelta(minutes=10)  # 10分钟后开始

        for idx, article in enumerate(articles):
            publish_at = base_time + timedelta(minutes=interval_minutes * idx)
            task_id = self.schedule_article(
                url=article['url'],
                publish_at=publish_at,
                priority=article.get('priority', 'medium'),
                metadata=article.get('metadata', {})
            )
            task_ids.append(task_id)

        return task_ids

    def schedule_recurring(
        self,
        url_source: str,
        cron_expression: str,
        priority: str = 'medium'
    ) -> str:
        """
        创建循环调度任务

        Args:
            url_source: URL来源（可以是文件路径或API端点）
            cron_expression: Cron表达式
            priority: 优先级

        Returns:
            作业ID
        """
        job_id = f"recurring_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # 解析Cron表达式
        # 格式: "分 时 日 月 周"
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("无效的Cron表达式")

        trigger = CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
            timezone=SCHEDULE_CONFIG['timezone']
        )

        # 添加到调度器
        job = self.scheduler.add_job(
            func=self._execute_recurring_task,
            trigger=trigger,
            args=[url_source, priority],
            id=job_id,
            name=f"Recurring: {url_source}",
            replace_existing=True
        )

        print(f"循环任务已创建: {job_id}, Cron: {cron_expression}")
        return job_id

    def reschedule_article(self, task_id: str, new_publish_at: datetime) -> bool:
        """
        重新调度文章

        Args:
            task_id: 任务ID
            new_publish_at: 新的发布时间

        Returns:
            是否成功
        """
        try:
            # 更新数据库
            with self.db_manager.get_session() as session:
                task = session.query(ArticleTask).filter_by(task_id=task_id).first()
                if not task:
                    return False

                task.scheduled_at = new_publish_at
                task.publish_at = new_publish_at
                session.commit()

            # 更新调度器中的作业
            self.scheduler.reschedule_job(
                job_id=task_id,
                trigger=DateTrigger(run_date=new_publish_at)
            )

            print(f"文章已重新调度: {task_id}, 新时间: {new_publish_at}")
            return True

        except Exception as e:
            print(f"重新调度失败: {e}")
            return False

    def cancel_scheduled(self, task_id: str) -> bool:
        """
        取消调度任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功
        """
        try:
            # 更新数据库状态
            with self.db_manager.get_session() as session:
                task = session.query(ArticleTask).filter_by(task_id=task_id).first()
                if not task:
                    return False

                task.status = TaskStatus.CANCELLED
                session.commit()

            # 从调度器删除
            self.scheduler.remove_job(task_id)

            print(f"调度任务已取消: {task_id}")
            return True

        except Exception as e:
            print(f"取消调度失败: {e}")
            return False

    def pause_scheduled(self, task_id: str) -> bool:
        """暂停调度任务"""
        try:
            self.scheduler.pause_job(task_id)
            print(f"调度任务已暂停: {task_id}")
            return True
        except Exception as e:
            print(f"暂停失败: {e}")
            return False

    def resume_scheduled(self, task_id: str) -> bool:
        """恢复调度任务"""
        try:
            self.scheduler.resume_job(task_id)
            print(f"调度任务已恢复: {task_id}")
            return True
        except Exception as e:
            print(f"恢复失败: {e}")
            return False

    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """获取所有调度任务"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'pending': job.pending,
                'coalesce': job.coalesce
            })
        return jobs

    def get_schedule_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        with self.db_manager.get_session() as session:
            scheduled_count = session.query(ArticleTask).filter_by(
                status=TaskStatus.SCHEDULED
            ).count()

            upcoming = session.query(ArticleTask).filter(
                ArticleTask.status == TaskStatus.SCHEDULED,
                ArticleTask.scheduled_at <= datetime.utcnow() + timedelta(hours=24)
            ).all()

            return {
                'scheduler_running': self.scheduler.running,
                'total_scheduled': scheduled_count,
                'upcoming_24h': len(upcoming),
                'jobs': self.get_scheduled_jobs()
            }

    def optimize_schedule(self, task_ids: List[str], target_window: Dict[str, Any]):
        """
        优化发布调度

        Args:
            task_ids: 任务ID列表
            target_window: 目标时间窗口 {'start': datetime, 'end': datetime, 'max_per_hour': int}
        """
        start_time = target_window['start']
        end_time = target_window['end']
        max_per_hour = target_window.get('max_per_hour', 2)

        # 计算时间间隔
        total_hours = (end_time - start_time).total_seconds() / 3600
        total_tasks = len(task_ids)

        if total_tasks > total_hours * max_per_hour:
            print(f"警告: 任务数量({total_tasks})超过时间窗口容量({total_hours * max_per_hour})")

        # 重新分配发布时间
        interval_minutes = int((total_hours * 60) / total_tasks)
        current_time = start_time

        for task_id in task_ids:
            self.reschedule_article(task_id, current_time)
            current_time += timedelta(minutes=interval_minutes)

        print(f"已优化 {total_tasks} 个任务的发布调度")

    def _get_task_by_priority(self, priority: str):
        """根据优先级获取任务函数"""
        if priority == 'high':
            return process_article_high
        elif priority == 'low':
            return process_article_low
        else:
            return process_article_medium

    def _execute_scheduled_task(
        self,
        task_id: str,
        url: str,
        priority: str,
        metadata: Dict[str, Any]
    ):
        """执行调度任务"""
        print(f"执行调度任务: {task_id}")

        # 更新数据库状态
        with self.db_manager.get_session() as session:
            task = session.query(ArticleTask).filter_by(task_id=task_id).first()
            if task:
                task.status = TaskStatus.QUEUED
                session.commit()

        # 提交到Celery队列
        task_func = self._get_task_by_priority(priority)
        task_func.apply_async(
            args=[url, metadata],
            task_id=task_id
        )

    def _execute_recurring_task(self, url_source: str, priority: str):
        """执行循环任务"""
        print(f"执行循环任务: {url_source}")

        # 从源获取URL列表
        urls = self._fetch_urls_from_source(url_source)

        # 为每个URL创建任务
        for url in urls:
            task_id = f"recurring_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(url)}"
            task_func = self._get_task_by_priority(priority)
            task_func.apply_async(
                args=[url, {}],
                task_id=task_id
            )

    def _fetch_urls_from_source(self, source: str) -> List[str]:
        """从源获取URL列表"""
        urls = []

        # 这里可以根据source类型实现不同的获取逻辑
        # 例如：从文件读取、从API获取等

        if source.startswith('file://'):
            # 从文件读取
            file_path = source[7:]
            try:
                with open(file_path, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"读取URL源失败: {e}")

        elif source.startswith('http'):
            # 从API获取
            import requests
            try:
                response = requests.get(source, timeout=30)
                urls = response.json().get('urls', [])
            except Exception as e:
                print(f"获取URL失败: {e}")

        return urls

    def _restore_scheduled_tasks(self):
        """恢复未完成的调度任务"""
        with self.db_manager.get_session() as session:
            tasks = session.query(ArticleTask).filter_by(
                status=TaskStatus.SCHEDULED
            ).all()

            for task in tasks:
                if task.scheduled_at > datetime.utcnow():
                    # 重新添加到调度器
                    task_func = self._get_task_by_priority(task.priority)
                    self.scheduler.add_job(
                        func=self._execute_scheduled_task,
                        trigger=DateTrigger(run_date=task.scheduled_at),
                        args=[task.task_id, task.url, task.priority, task.metadata],
                        id=task.task_id,
                        name=f"Restored: {task.url}",
                        replace_existing=True
                    )
                    print(f"恢复调度任务: {task.task_id}")

# 全局调度器实例
scheduler = ArticleScheduler()

def get_scheduler() -> ArticleScheduler:
    """获取调度器实例"""
    return scheduler