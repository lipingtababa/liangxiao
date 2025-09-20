"""
队列统计和报告系统
生成各种统计报告和分析
"""

import json
import csv
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from .models import (
    DatabaseManager, ArticleTask, TaskStatus, TaskPriority,
    QueueStatistics, DeadLetterQueue, TaskBatch
)

class QueueReporter:
    """队列报告生成器"""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """生成日报"""
        if not date:
            date = datetime.utcnow().date()
        else:
            date = date.date()

        start_time = datetime.combine(date, datetime.min.time())
        end_time = datetime.combine(date, datetime.max.time())

        with self.db_manager.get_session() as session:
            report = {
                'date': date.isoformat(),
                'summary': self._get_period_summary(session, start_time, end_time),
                'hourly_distribution': self._get_hourly_distribution(session, start_time, end_time),
                'priority_breakdown': self._get_priority_breakdown(session, start_time, end_time),
                'performance_metrics': self._get_performance_metrics(session, start_time, end_time),
                'top_errors': self._get_top_errors(session, start_time, end_time),
                'batch_performance': self._get_batch_performance(session, start_time, end_time)
            }

        return report

    def generate_weekly_report(self, week_start: Optional[datetime] = None) -> Dict[str, Any]:
        """生成周报"""
        if not week_start:
            today = datetime.utcnow().date()
            week_start = today - timedelta(days=today.weekday())
        else:
            week_start = week_start.date()

        week_end = week_start + timedelta(days=6)

        start_time = datetime.combine(week_start, datetime.min.time())
        end_time = datetime.combine(week_end, datetime.max.time())

        with self.db_manager.get_session() as session:
            report = {
                'week': f"{week_start.isoformat()} to {week_end.isoformat()}",
                'summary': self._get_period_summary(session, start_time, end_time),
                'daily_trends': self._get_daily_trends(session, start_time, end_time),
                'priority_trends': self._get_priority_trends(session, start_time, end_time),
                'performance_comparison': self._get_performance_comparison(session, start_time, end_time),
                'capacity_utilization': self._get_capacity_utilization(session, start_time, end_time),
                'recommendations': self._generate_recommendations(session, start_time, end_time)
            }

        return report

    def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """生成月报"""
        import calendar

        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

        with self.db_manager.get_session() as session:
            report = {
                'month': f"{year}-{month:02d}",
                'summary': self._get_period_summary(session, first_day, last_day),
                'weekly_breakdown': self._get_weekly_breakdown(session, first_day, last_day),
                'growth_metrics': self._get_growth_metrics(session, first_day, last_day),
                'efficiency_analysis': self._get_efficiency_analysis(session, first_day, last_day),
                'cost_analysis': self._get_cost_analysis(session, first_day, last_day),
                'year_over_year': self._get_year_over_year(session, year, month)
            }

        return report

    def generate_custom_report(
        self,
        start_date: datetime,
        end_date: datetime,
        metrics: List[str]
    ) -> Dict[str, Any]:
        """生成自定义报告"""
        report = {
            'period': f"{start_date.isoformat()} to {end_date.isoformat()}",
            'requested_metrics': metrics
        }

        with self.db_manager.get_session() as session:
            metric_functions = {
                'summary': lambda: self._get_period_summary(session, start_date, end_date),
                'priority_breakdown': lambda: self._get_priority_breakdown(session, start_date, end_date),
                'performance_metrics': lambda: self._get_performance_metrics(session, start_date, end_date),
                'error_analysis': lambda: self._get_error_analysis(session, start_date, end_date),
                'queue_utilization': lambda: self._get_queue_utilization(session, start_date, end_date),
                'worker_efficiency': lambda: self._get_worker_efficiency(session, start_date, end_date),
                'sla_compliance': lambda: self._get_sla_compliance(session, start_date, end_date)
            }

            for metric in metrics:
                if metric in metric_functions:
                    report[metric] = metric_functions[metric]()

        return report

    def export_report(
        self,
        report: Dict[str, Any],
        format: str = 'json',
        output_path: Optional[str] = None
    ) -> str:
        """导出报告"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        if format == 'json':
            content = json.dumps(report, indent=2, ensure_ascii=False)
            filename = output_path or f"queue_report_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

        elif format == 'csv':
            filename = output_path or f"queue_report_{timestamp}.csv"
            self._export_to_csv(report, filename)

        elif format == 'html':
            filename = output_path or f"queue_report_{timestamp}.html"
            self._export_to_html(report, filename)

        elif format == 'pdf':
            filename = output_path or f"queue_report_{timestamp}.pdf"
            self._export_to_pdf(report, filename)

        return filename

    def generate_visualization(
        self,
        data_type: str,
        period: Dict[str, datetime],
        output_path: Optional[str] = None
    ) -> str:
        """生成可视化图表"""
        fig, ax = plt.subplots(figsize=(12, 6))

        with self.db_manager.get_session() as session:
            if data_type == 'throughput':
                self._plot_throughput(session, period, ax)
            elif data_type == 'latency':
                self._plot_latency(session, period, ax)
            elif data_type == 'error_rate':
                self._plot_error_rate(session, period, ax)
            elif data_type == 'queue_size':
                self._plot_queue_size(session, period, ax)
            elif data_type == 'priority_distribution':
                self._plot_priority_distribution(session, period, ax)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = output_path or f"queue_chart_{data_type}_{timestamp}.png"
        plt.savefig(filename)
        plt.close()

        return filename

    # === 内部方法：数据获取 ===

    def _get_period_summary(self, session: Session, start: datetime, end: datetime) -> Dict[str, Any]:
        """获取时段摘要"""
        total_tasks = session.query(ArticleTask).filter(
            ArticleTask.created_at >= start,
            ArticleTask.created_at <= end
        ).count()

        completed = session.query(ArticleTask).filter(
            ArticleTask.status == TaskStatus.COMPLETED,
            ArticleTask.completed_at >= start,
            ArticleTask.completed_at <= end
        ).count()

        failed = session.query(ArticleTask).filter(
            ArticleTask.status == TaskStatus.FAILED,
            ArticleTask.failed_at >= start,
            ArticleTask.failed_at <= end
        ).count()

        avg_processing = session.query(func.avg(ArticleTask.processing_time)).filter(
            ArticleTask.processing_time.isnot(None),
            ArticleTask.completed_at >= start,
            ArticleTask.completed_at <= end
        ).scalar()

        return {
            'total_tasks': total_tasks,
            'completed': completed,
            'failed': failed,
            'success_rate': (completed / (completed + failed) * 100) if (completed + failed) > 0 else 0,
            'avg_processing_time': float(avg_processing) if avg_processing else 0,
            'throughput': completed / ((end - start).total_seconds() / 3600) if (end - start).total_seconds() > 0 else 0
        }

    def _get_hourly_distribution(self, session: Session, start: datetime, end: datetime) -> List[Dict]:
        """获取小时分布"""
        hourly = []
        current_hour = start.replace(minute=0, second=0, microsecond=0)

        while current_hour < end:
            next_hour = current_hour + timedelta(hours=1)

            completed = session.query(ArticleTask).filter(
                ArticleTask.status == TaskStatus.COMPLETED,
                ArticleTask.completed_at >= current_hour,
                ArticleTask.completed_at < next_hour
            ).count()

            failed = session.query(ArticleTask).filter(
                ArticleTask.status == TaskStatus.FAILED,
                ArticleTask.failed_at >= current_hour,
                ArticleTask.failed_at < next_hour
            ).count()

            hourly.append({
                'hour': current_hour.strftime('%H:00'),
                'completed': completed,
                'failed': failed,
                'total': completed + failed
            })

            current_hour = next_hour

        return hourly

    def _get_priority_breakdown(self, session: Session, start: datetime, end: datetime) -> Dict[str, Any]:
        """获取优先级分解"""
        breakdown = {}

        for priority in ['urgent', 'high', 'medium', 'low', 'background']:
            tasks = session.query(ArticleTask).filter(
                ArticleTask.priority == priority,
                ArticleTask.created_at >= start,
                ArticleTask.created_at <= end
            )

            total = tasks.count()
            completed = tasks.filter(ArticleTask.status == TaskStatus.COMPLETED).count()
            failed = tasks.filter(ArticleTask.status == TaskStatus.FAILED).count()

            avg_time = session.query(func.avg(ArticleTask.processing_time)).filter(
                ArticleTask.priority == priority,
                ArticleTask.processing_time.isnot(None),
                ArticleTask.completed_at >= start,
                ArticleTask.completed_at <= end
            ).scalar()

            breakdown[priority] = {
                'total': total,
                'completed': completed,
                'failed': failed,
                'pending': total - completed - failed,
                'avg_processing_time': float(avg_time) if avg_time else 0
            }

        return breakdown

    def _get_performance_metrics(self, session: Session, start: datetime, end: datetime) -> Dict[str, Any]:
        """获取性能指标"""
        metrics = session.query(
            func.min(ArticleTask.processing_time).label('min'),
            func.avg(ArticleTask.processing_time).label('avg'),
            func.max(ArticleTask.processing_time).label('max'),
            func.stddev(ArticleTask.processing_time).label('stddev')
        ).filter(
            ArticleTask.processing_time.isnot(None),
            ArticleTask.completed_at >= start,
            ArticleTask.completed_at <= end
        ).first()

        # 计算百分位数
        processing_times = session.query(ArticleTask.processing_time).filter(
            ArticleTask.processing_time.isnot(None),
            ArticleTask.completed_at >= start,
            ArticleTask.completed_at <= end
        ).all()

        times = sorted([t[0] for t in processing_times])
        percentiles = {}

        if times:
            percentiles = {
                'p50': times[len(times) // 2],
                'p75': times[int(len(times) * 0.75)],
                'p90': times[int(len(times) * 0.90)],
                'p95': times[int(len(times) * 0.95)],
                'p99': times[int(len(times) * 0.99)] if len(times) > 100 else times[-1]
            }

        return {
            'min': float(metrics.min) if metrics.min else 0,
            'avg': float(metrics.avg) if metrics.avg else 0,
            'max': float(metrics.max) if metrics.max else 0,
            'stddev': float(metrics.stddev) if metrics.stddev else 0,
            'percentiles': percentiles
        }

    def _get_top_errors(self, session: Session, start: datetime, end: datetime, limit: int = 10) -> List[Dict]:
        """获取主要错误"""
        errors = session.query(
            ArticleTask.error_message,
            func.count(ArticleTask.id).label('count')
        ).filter(
            ArticleTask.status == TaskStatus.FAILED,
            ArticleTask.failed_at >= start,
            ArticleTask.failed_at <= end,
            ArticleTask.error_message.isnot(None)
        ).group_by(
            ArticleTask.error_message
        ).order_by(
            func.count(ArticleTask.id).desc()
        ).limit(limit).all()

        return [{
            'error': error.error_message[:100],
            'count': error.count,
            'percentage': (error.count / sum(e.count for e in errors) * 100) if errors else 0
        } for error in errors]

    def _get_batch_performance(self, session: Session, start: datetime, end: datetime) -> Dict[str, Any]:
        """获取批处理性能"""
        batches = session.query(TaskBatch).filter(
            TaskBatch.created_at >= start,
            TaskBatch.created_at <= end
        ).all()

        if not batches:
            return {'total_batches': 0}

        completed_batches = [b for b in batches if b.status == TaskStatus.COMPLETED]

        avg_completion_time = 0
        if completed_batches:
            completion_times = [
                (b.completed_at - b.created_at).total_seconds()
                for b in completed_batches
                if b.completed_at and b.created_at
            ]
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

        return {
            'total_batches': len(batches),
            'completed': len(completed_batches),
            'avg_batch_size': sum(b.total_tasks for b in batches) / len(batches),
            'avg_completion_time': avg_completion_time,
            'success_rate': (
                sum(b.completed_tasks for b in batches) /
                sum(b.total_tasks for b in batches) * 100
            ) if sum(b.total_tasks for b in batches) > 0 else 0
        }

    def _get_daily_trends(self, session: Session, start: datetime, end: datetime) -> List[Dict]:
        """获取每日趋势"""
        trends = []
        current_date = start.date()

        while current_date <= end.date():
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())

            summary = self._get_period_summary(session, day_start, day_end)
            trends.append({
                'date': current_date.isoformat(),
                **summary
            })

            current_date += timedelta(days=1)

        return trends

    def _generate_recommendations(self, session: Session, start: datetime, end: datetime) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 分析失败率
        summary = self._get_period_summary(session, start, end)
        if summary['success_rate'] < 90:
            recommendations.append(f"任务成功率较低 ({summary['success_rate']:.1f}%)，建议检查错误日志并优化处理逻辑")

        # 分析处理时间
        if summary['avg_processing_time'] > 300:
            recommendations.append(f"平均处理时间较长 ({summary['avg_processing_time']:.0f}秒)，考虑优化算法或增加并发")

        # 分析队列积压
        pending = session.query(ArticleTask).filter(
            ArticleTask.status == TaskStatus.PENDING
        ).count()

        if pending > 100:
            recommendations.append(f"待处理任务积压 ({pending}个)，建议增加Worker数量或提高处理速度")

        # 分析优先级使用
        priority_breakdown = self._get_priority_breakdown(session, start, end)
        if priority_breakdown['urgent']['total'] > priority_breakdown['medium']['total']:
            recommendations.append("紧急任务过多，建议重新评估优先级标准")

        return recommendations

    # === 导出方法 ===

    def _export_to_csv(self, report: Dict[str, Any], filename: str):
        """导出为CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # 写入摘要
            writer.writerow(['报告摘要'])
            if 'summary' in report:
                for key, value in report['summary'].items():
                    writer.writerow([key, value])

            writer.writerow([])  # 空行

            # 写入其他数据表
            for section, data in report.items():
                if section == 'summary':
                    continue

                writer.writerow([section])

                if isinstance(data, list) and data:
                    # 写入表头
                    headers = list(data[0].keys())
                    writer.writerow(headers)

                    # 写入数据
                    for row in data:
                        writer.writerow([row.get(h, '') for h in headers])

                elif isinstance(data, dict):
                    for key, value in data.items():
                        writer.writerow([key, value])

                writer.writerow([])  # 空行

    def _export_to_html(self, report: Dict[str, Any], filename: str):
        """导出为HTML"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>队列报告 - {report.get('date', report.get('period', ''))}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metric {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; }}
        .success {{ color: green; }}
        .warning {{ color: orange; }}
        .error {{ color: red; }}
    </style>
</head>
<body>
    <h1>队列系统报告</h1>
    <div class="metric">
        <p><strong>报告时间:</strong> {datetime.utcnow().isoformat()}</p>
        <p><strong>报告周期:</strong> {report.get('date', report.get('period', ''))}</p>
    </div>
"""

        # 添加摘要
        if 'summary' in report:
            html_content += "<h2>摘要</h2><div class='metric'>"
            for key, value in report['summary'].items():
                if isinstance(value, float):
                    html_content += f"<p><strong>{key}:</strong> {value:.2f}</p>"
                else:
                    html_content += f"<p><strong>{key}:</strong> {value}</p>"
            html_content += "</div>"

        # 添加其他部分
        for section, data in report.items():
            if section == 'summary':
                continue

            html_content += f"<h2>{section}</h2>"

            if isinstance(data, list) and data:
                html_content += "<table>"
                # 表头
                headers = list(data[0].keys())
                html_content += "<tr>"
                for header in headers:
                    html_content += f"<th>{header}</th>"
                html_content += "</tr>"

                # 数据行
                for row in data:
                    html_content += "<tr>"
                    for header in headers:
                        value = row.get(header, '')
                        if isinstance(value, float):
                            html_content += f"<td>{value:.2f}</td>"
                        else:
                            html_content += f"<td>{value}</td>"
                    html_content += "</tr>"
                html_content += "</table>"

            elif isinstance(data, dict):
                html_content += "<div class='metric'>"
                for key, value in data.items():
                    if isinstance(value, dict):
                        html_content += f"<p><strong>{key}:</strong></p><ul>"
                        for k, v in value.items():
                            html_content += f"<li>{k}: {v}</li>"
                        html_content += "</ul>"
                    else:
                        html_content += f"<p><strong>{key}:</strong> {value}</p>"
                html_content += "</div>"

        html_content += "</body></html>"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _export_to_pdf(self, report: Dict[str, Any], filename: str):
        """导出为PDF（需要额外的库）"""
        # 这里可以使用reportlab或者weasyprint等库
        # 为了简化，先生成HTML然后转换为PDF
        html_file = filename.replace('.pdf', '.html')
        self._export_to_html(report, html_file)

        # 使用weasyprint转换（需要安装: pip install weasyprint）
        try:
            from weasyprint import HTML
            HTML(filename=html_file).write_pdf(filename)
        except ImportError:
            print("需要安装weasyprint库来生成PDF: pip install weasyprint")

    # === 可视化方法 ===

    def _plot_throughput(self, session: Session, period: Dict[str, datetime], ax):
        """绘制吞吐量图表"""
        # 获取每小时的完成任务数
        data = []
        current = period['start']

        while current < period['end']:
            next_hour = current + timedelta(hours=1)
            count = session.query(ArticleTask).filter(
                ArticleTask.status == TaskStatus.COMPLETED,
                ArticleTask.completed_at >= current,
                ArticleTask.completed_at < next_hour
            ).count()

            data.append((current, count))
            current = next_hour

        times, counts = zip(*data) if data else ([], [])

        ax.plot(times, counts, marker='o')
        ax.set_xlabel('时间')
        ax.set_ylabel('每小时完成任务数')
        ax.set_title('任务吞吐量')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:00'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.xticks(rotation=45)

    def _plot_error_rate(self, session: Session, period: Dict[str, datetime], ax):
        """绘制错误率图表"""
        data = []
        current = period['start']

        while current < period['end']:
            next_hour = current + timedelta(hours=1)

            completed = session.query(ArticleTask).filter(
                ArticleTask.status == TaskStatus.COMPLETED,
                ArticleTask.completed_at >= current,
                ArticleTask.completed_at < next_hour
            ).count()

            failed = session.query(ArticleTask).filter(
                ArticleTask.status == TaskStatus.FAILED,
                ArticleTask.failed_at >= current,
                ArticleTask.failed_at < next_hour
            ).count()

            error_rate = (failed / (completed + failed) * 100) if (completed + failed) > 0 else 0
            data.append((current, error_rate))

            current = next_hour

        times, rates = zip(*data) if data else ([], [])

        ax.plot(times, rates, marker='o', color='red')
        ax.set_xlabel('时间')
        ax.set_ylabel('错误率 (%)')
        ax.set_title('任务错误率趋势')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:00'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plt.xticks(rotation=45)

# 创建全局报告器实例
reporter = QueueReporter()

def get_reporter() -> QueueReporter:
    """获取报告器实例"""
    return reporter