"""
队列监控模块
提供实时监控和统计功能
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    start_http_server, generate_latest
)
from celery import current_app
from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import (
    DatabaseManager, ArticleTask, TaskStatus,
    QueueStatistics, DeadLetterQueue, TaskBatch
)
from .config import MONITORING_CONFIG, ALERT_THRESHOLDS, QUEUE_CAPACITY

# Prometheus指标定义
queue_size = Gauge('queue_size', 'Current queue size', ['queue_name'])
tasks_processed = Counter('tasks_processed_total', 'Total processed tasks', ['status', 'priority'])
task_duration = Histogram('task_duration_seconds', 'Task processing duration', ['priority'])
failure_rate = Gauge('task_failure_rate', 'Task failure rate percentage')
queue_health = Gauge('queue_health_score', 'Queue health score (0-100)')

class QueueMonitor:
    """队列监控器"""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.celery_app = current_app

        # 启动Prometheus服务器
        if MONITORING_CONFIG['enable_prometheus']:
            start_http_server(MONITORING_CONFIG['prometheus_port'])
            print(f"Prometheus监控已启动，端口: {MONITORING_CONFIG['prometheus_port']}")

    def get_realtime_status(self) -> Dict[str, Any]:
        """获取实时队列状态"""
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'queues': {},
            'workers': {},
            'tasks': {},
            'alerts': []
        }

        # 获取Celery队列信息
        inspect = self.celery_app.control.inspect()

        # 活动任务
        active_tasks = inspect.active()
        if active_tasks:
            for worker, tasks in active_tasks.items():
                status['workers'][worker] = {
                    'active_tasks': len(tasks),
                    'tasks': [self._format_task(t) for t in tasks]
                }

        # 预定任务
        scheduled_tasks = inspect.scheduled()
        if scheduled_tasks:
            status['scheduled_count'] = sum(len(tasks) for tasks in scheduled_tasks.values())

        # 保留任务
        reserved_tasks = inspect.reserved()
        if reserved_tasks:
            status['reserved_count'] = sum(len(tasks) for tasks in reserved_tasks.values())

        # 从数据库获取任务统计
        with self.db_manager.get_session() as session:
            # 各状态任务数量
            for status_type in TaskStatus:
                count = session.query(ArticleTask).filter_by(status=status_type.value).count()
                status['tasks'][status_type.value] = count

            # 队列大小
            for queue_name in ['high_priority', 'medium_priority', 'low_priority']:
                queue_count = session.query(ArticleTask).filter(
                    ArticleTask.status == TaskStatus.QUEUED,
                    ArticleTask.priority == queue_name.split('_')[0]
                ).count()
                status['queues'][queue_name] = {
                    'size': queue_count,
                    'capacity': QUEUE_CAPACITY[queue_name],
                    'usage_percent': (queue_count / QUEUE_CAPACITY[queue_name]) * 100
                }

                # 更新Prometheus指标
                queue_size.labels(queue_name=queue_name).set(queue_count)

            # 检查告警条件
            status['alerts'] = self._check_alerts(session)

        return status

    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """获取队列统计信息"""
        since = datetime.utcnow() - timedelta(hours=hours)

        with self.db_manager.get_session() as session:
            # 任务完成统计
            completed = session.query(
                func.count(ArticleTask.id).label('count'),
                func.avg(ArticleTask.processing_time).label('avg_time')
            ).filter(
                ArticleTask.status == TaskStatus.COMPLETED,
                ArticleTask.completed_at >= since
            ).first()

            # 任务失败统计
            failed = session.query(func.count(ArticleTask.id)).filter(
                ArticleTask.status == TaskStatus.FAILED,
                ArticleTask.failed_at >= since
            ).scalar()

            # 优先级分布
            priority_dist = session.query(
                ArticleTask.priority,
                func.count(ArticleTask.id).label('count')
            ).filter(
                ArticleTask.created_at >= since
            ).group_by(ArticleTask.priority).all()

            # 平均等待时间
            avg_queue_time = session.query(
                func.avg(ArticleTask.queue_time)
            ).filter(
                ArticleTask.queue_time.isnot(None),
                ArticleTask.created_at >= since
            ).scalar()

            # 死信队列统计
            dead_letter_count = session.query(DeadLetterQueue).filter(
                DeadLetterQueue.created_at >= since
            ).count()

            return {
                'period': f'Last {hours} hours',
                'completed': {
                    'count': completed.count if completed else 0,
                    'avg_processing_time': float(completed.avg_time) if completed and completed.avg_time else 0
                },
                'failed': failed or 0,
                'success_rate': (completed.count / (completed.count + failed) * 100) if completed and (completed.count + failed) > 0 else 0,
                'priority_distribution': {p.priority: p.count for p in priority_dist},
                'avg_queue_time': float(avg_queue_time) if avg_queue_time else 0,
                'dead_letter_count': dead_letter_count
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'throughput': {},
            'latency': {},
            'resource_usage': {}
        }

        with self.db_manager.get_session() as session:
            # 吞吐量计算（最近1小时）
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            completed_last_hour = session.query(ArticleTask).filter(
                ArticleTask.status == TaskStatus.COMPLETED,
                ArticleTask.completed_at >= one_hour_ago
            ).count()

            metrics['throughput']['tasks_per_hour'] = completed_last_hour
            metrics['throughput']['tasks_per_minute'] = completed_last_hour / 60

            # 延迟统计
            latencies = session.query(
                func.min(ArticleTask.processing_time).label('min'),
                func.avg(ArticleTask.processing_time).label('avg'),
                func.max(ArticleTask.processing_time).label('max'),
                func.percentile_cont(0.5).within_group(ArticleTask.processing_time).label('p50'),
                func.percentile_cont(0.95).within_group(ArticleTask.processing_time).label('p95'),
                func.percentile_cont(0.99).within_group(ArticleTask.processing_time).label('p99')
            ).filter(
                ArticleTask.processing_time.isnot(None),
                ArticleTask.completed_at >= one_hour_ago
            ).first()

            if latencies:
                metrics['latency'] = {
                    'min': float(latencies.min) if latencies.min else 0,
                    'avg': float(latencies.avg) if latencies.avg else 0,
                    'max': float(latencies.max) if latencies.max else 0,
                    'p50': float(latencies.p50) if latencies.p50 else 0,
                    'p95': float(latencies.p95) if latencies.p95 else 0,
                    'p99': float(latencies.p99) if latencies.p99 else 0
                }

            # 更新Prometheus指标
            if metrics['latency'].get('avg'):
                task_duration.observe(metrics['latency']['avg'])

        return metrics

    def get_worker_stats(self) -> List[Dict[str, Any]]:
        """获取Worker统计信息"""
        inspect = self.celery_app.control.inspect()
        stats = inspect.stats()

        worker_list = []
        if stats:
            for worker_name, worker_stats in stats.items():
                worker_list.append({
                    'name': worker_name,
                    'status': 'online',
                    'pool': worker_stats.get('pool', {}),
                    'total_tasks': worker_stats.get('total', {}),
                    'clock': worker_stats.get('clock', 0),
                    'uptime': worker_stats.get('uptime', 0)
                })

        return worker_list

    def get_queue_trends(self, days: int = 7) -> Dict[str, Any]:
        """获取队列趋势数据"""
        trends = {
            'period': f'Last {days} days',
            'daily': []
        }

        with self.db_manager.get_session() as session:
            for i in range(days):
                date = datetime.utcnow().date() - timedelta(days=i)
                start_time = datetime.combine(date, datetime.min.time())
                end_time = datetime.combine(date, datetime.max.time())

                # 当日统计
                completed = session.query(ArticleTask).filter(
                    ArticleTask.status == TaskStatus.COMPLETED,
                    ArticleTask.completed_at >= start_time,
                    ArticleTask.completed_at <= end_time
                ).count()

                failed = session.query(ArticleTask).filter(
                    ArticleTask.status == TaskStatus.FAILED,
                    ArticleTask.failed_at >= start_time,
                    ArticleTask.failed_at <= end_time
                ).count()

                trends['daily'].append({
                    'date': date.isoformat(),
                    'completed': completed,
                    'failed': failed,
                    'total': completed + failed
                })

        trends['daily'].reverse()  # 按时间正序
        return trends

    def get_batch_status(self, batch_id: Optional[str] = None) -> Dict[str, Any]:
        """获取批处理状态"""
        with self.db_manager.get_session() as session:
            if batch_id:
                batch = session.query(TaskBatch).filter_by(batch_id=batch_id).first()
                if batch:
                    return self._format_batch(batch)
                return {'error': 'Batch not found'}

            # 获取所有活动批次
            active_batches = session.query(TaskBatch).filter(
                TaskBatch.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
            ).all()

            return {
                'active_batches': [self._format_batch(b) for b in active_batches],
                'total_active': len(active_batches)
            }

    def get_dead_letter_queue(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取死信队列内容"""
        with self.db_manager.get_session() as session:
            dead_letters = session.query(DeadLetterQueue).order_by(
                DeadLetterQueue.created_at.desc()
            ).limit(limit).all()

            return [{
                'id': dl.id,
                'task_id': dl.original_task_id,
                'failure_reason': dl.failure_reason,
                'failure_count': dl.failure_count,
                'created_at': dl.created_at.isoformat(),
                'expires_at': dl.expires_at.isoformat() if dl.expires_at else None,
                'can_retry': dl.can_retry
            } for dl in dead_letters]

    def generate_health_report(self) -> Dict[str, Any]:
        """生成健康报告"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_health': 'healthy',
            'score': 100,
            'components': {}
        }

        issues = []

        with self.db_manager.get_session() as session:
            # 检查队列大小
            for queue_name in ['high_priority', 'medium_priority', 'low_priority']:
                queue_count = session.query(ArticleTask).filter(
                    ArticleTask.status == TaskStatus.QUEUED,
                    ArticleTask.priority == queue_name.split('_')[0]
                ).count()

                usage_percent = (queue_count / QUEUE_CAPACITY[queue_name]) * 100

                component_health = 'healthy'
                if usage_percent >= ALERT_THRESHOLDS['queue_size_critical']:
                    component_health = 'critical'
                    issues.append(f"{queue_name} queue critically full")
                    report['score'] -= 30
                elif usage_percent >= ALERT_THRESHOLDS['queue_size_warning']:
                    component_health = 'warning'
                    issues.append(f"{queue_name} queue filling up")
                    report['score'] -= 10

                report['components'][queue_name] = {
                    'status': component_health,
                    'usage': f"{usage_percent:.1f}%"
                }

            # 检查失败率
            total_recent = session.query(ArticleTask).filter(
                ArticleTask.created_at >= datetime.utcnow() - timedelta(hours=1)
            ).count()

            failed_recent = session.query(ArticleTask).filter(
                ArticleTask.status == TaskStatus.FAILED,
                ArticleTask.failed_at >= datetime.utcnow() - timedelta(hours=1)
            ).count()

            if total_recent > 0:
                failure_rate = (failed_recent / total_recent) * 100

                if failure_rate >= ALERT_THRESHOLDS['task_failure_rate_critical']:
                    report['components']['failure_rate'] = {
                        'status': 'critical',
                        'rate': f"{failure_rate:.1f}%"
                    }
                    issues.append(f"High failure rate: {failure_rate:.1f}%")
                    report['score'] -= 25
                elif failure_rate >= ALERT_THRESHOLDS['task_failure_rate_warning']:
                    report['components']['failure_rate'] = {
                        'status': 'warning',
                        'rate': f"{failure_rate:.1f}%"
                    }
                    issues.append(f"Elevated failure rate: {failure_rate:.1f}%")
                    report['score'] -= 10
                else:
                    report['components']['failure_rate'] = {
                        'status': 'healthy',
                        'rate': f"{failure_rate:.1f}%"
                    }

                # 更新Prometheus指标
                failure_rate_gauge.set(failure_rate)

        # 检查Worker状态
        inspect = self.celery_app.control.inspect()
        active_workers = inspect.active_queues()
        if not active_workers:
            report['components']['workers'] = {'status': 'critical', 'count': 0}
            issues.append("No active workers")
            report['score'] -= 50
        else:
            report['components']['workers'] = {
                'status': 'healthy',
                'count': len(active_workers)
            }

        # 确定整体健康状态
        if report['score'] <= 50:
            report['overall_health'] = 'critical'
        elif report['score'] <= 80:
            report['overall_health'] = 'warning'

        report['issues'] = issues

        # 更新Prometheus健康分数
        queue_health.set(report['score'])

        return report

    def _format_task(self, task_info: Dict) -> Dict[str, Any]:
        """格式化任务信息"""
        return {
            'id': task_info.get('id'),
            'name': task_info.get('name'),
            'args': str(task_info.get('args', []))[:100],
            'time_start': task_info.get('time_start'),
            'worker': task_info.get('hostname')
        }

    def _format_batch(self, batch: TaskBatch) -> Dict[str, Any]:
        """格式化批处理信息"""
        progress = (batch.completed_tasks / batch.total_tasks * 100) if batch.total_tasks > 0 else 0

        return {
            'batch_id': batch.batch_id,
            'name': batch.name,
            'status': batch.status,
            'progress': f"{progress:.1f}%",
            'total_tasks': batch.total_tasks,
            'completed_tasks': batch.completed_tasks,
            'failed_tasks': batch.failed_tasks,
            'created_at': batch.created_at.isoformat() if batch.created_at else None,
            'completed_at': batch.completed_at.isoformat() if batch.completed_at else None
        }

    def _check_alerts(self, session: Session) -> List[Dict[str, Any]]:
        """检查并生成告警"""
        alerts = []

        # 检查长时间运行的任务
        long_running = session.query(ArticleTask).filter(
            ArticleTask.status == TaskStatus.IN_PROGRESS,
            ArticleTask.started_at <= datetime.utcnow() - timedelta(
                seconds=ALERT_THRESHOLDS['processing_time_warning']
            )
        ).all()

        for task in long_running:
            duration = (datetime.utcnow() - task.started_at).total_seconds()
            level = 'critical' if duration >= ALERT_THRESHOLDS['processing_time_critical'] else 'warning'

            alerts.append({
                'level': level,
                'type': 'long_running_task',
                'task_id': task.task_id,
                'duration': duration,
                'message': f'Task {task.task_id} running for {duration:.0f} seconds'
            })

        # 检查死信队列大小
        dead_letter_count = session.query(DeadLetterQueue).count()
        if dead_letter_count > 100:
            alerts.append({
                'level': 'warning',
                'type': 'dead_letter_queue',
                'count': dead_letter_count,
                'message': f'Dead letter queue has {dead_letter_count} items'
            })

        return alerts

# 全局监控器实例
monitor = QueueMonitor()

def get_monitor() -> QueueMonitor:
    """获取监控器实例"""
    return monitor