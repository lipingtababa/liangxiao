#!/usr/bin/env python3
"""
队列系统测试脚本
验证队列管理系统的各项功能
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# 添加脚本目录到路径
sys.path.append(str(Path(__file__).parent))

def test_basic_submission():
    """测试基本任务提交"""
    print("\n=== 测试基本任务提交 ===")
    from queue.manager import QueueManager

    manager = QueueManager()

    # 提交测试任务
    test_url = "https://mp.weixin.qq.com/s/test_article_123"
    task_id = manager.submit_task(
        url=test_url,
        priority="medium",
        metadata={"test": True}
    )

    print(f"✓ 任务已提交: {task_id}")
    return task_id

def test_priority_submission():
    """测试不同优先级任务"""
    print("\n=== 测试优先级任务 ===")
    from queue.manager import QueueManager

    manager = QueueManager()
    task_ids = []

    priorities = ["urgent", "high", "medium", "low", "background"]
    for priority in priorities:
        task_id = manager.submit_task(
            url=f"https://mp.weixin.qq.com/s/test_{priority}",
            priority=priority,
            metadata={"priority_test": priority}
        )
        task_ids.append(task_id)
        print(f"✓ {priority.upper()} 任务已提交: {task_id}")

    return task_ids

def test_scheduled_task():
    """测试调度任务"""
    print("\n=== 测试调度任务 ===")
    from queue.scheduler import get_scheduler

    scheduler = get_scheduler()
    scheduler.start()

    # 调度任务在5分钟后执行
    publish_at = datetime.utcnow() + timedelta(minutes=5)
    task_id = scheduler.schedule_article(
        url="https://mp.weixin.qq.com/s/scheduled_test",
        publish_at=publish_at,
        priority="high",
        metadata={"scheduled": True}
    )

    print(f"✓ 任务已调度: {task_id}")
    print(f"  发布时间: {publish_at}")

    # 获取调度状态
    status = scheduler.get_schedule_status()
    print(f"✓ 调度器状态: {status['scheduler_running']}")
    print(f"  总调度任务: {status['total_scheduled']}")

    return task_id

def test_batch_processing():
    """测试批处理"""
    print("\n=== 测试批处理 ===")
    from queue.manager import QueueManager

    manager = QueueManager()

    # 创建测试URL列表
    urls = [
        f"https://mp.weixin.qq.com/s/batch_test_{i}"
        for i in range(5)
    ]

    # 提交批处理任务
    batch_id = manager.submit_batch(
        urls=urls,
        priority="medium",
        batch_name="测试批处理",
        interval_minutes=0  # 并发执行
    )

    print(f"✓ 批处理已创建: {batch_id}")
    print(f"  包含 {len(urls)} 个任务")

    return batch_id

def test_monitoring():
    """测试监控功能"""
    print("\n=== 测试监控功能 ===")
    from queue.monitor import get_monitor

    monitor = get_monitor()

    # 获取实时状态
    status = monitor.get_realtime_status()
    print("✓ 实时状态:")
    for queue_name, info in status.get('queues', {}).items():
        print(f"  {queue_name}: {info.get('size', 0)}/{info.get('capacity', 0)}")

    # 获取统计信息
    stats = monitor.get_statistics(hours=1)
    print("\n✓ 统计信息（最近1小时）:")
    print(f"  完成: {stats['completed']['count']}")
    print(f"  失败: {stats['failed']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")

    # 健康检查
    health = monitor.generate_health_report()
    print("\n✓ 健康报告:")
    print(f"  状态: {health['overall_health']}")
    print(f"  分数: {health['score']}/100")

    return health

def test_reporting():
    """测试报告生成"""
    print("\n=== 测试报告生成 ===")
    from queue.reporting import get_reporter

    reporter = get_reporter()

    # 生成日报
    daily_report = reporter.generate_daily_report()
    print("✓ 日报已生成")
    print(f"  日期: {daily_report['date']}")

    if 'summary' in daily_report:
        print(f"  总任务: {daily_report['summary'].get('total_tasks', 0)}")
        print(f"  完成: {daily_report['summary'].get('completed', 0)}")

    # 导出报告
    output_file = reporter.export_report(
        daily_report,
        format='json',
        output_path='test_report.json'
    )
    print(f"✓ 报告已导出: {output_file}")

    return daily_report

def test_queue_management():
    """测试队列管理功能"""
    print("\n=== 测试队列管理 ===")
    from queue.manager import QueueManager

    manager = QueueManager()

    # 提交一个测试任务
    task_id = manager.submit_task(
        url="https://mp.weixin.qq.com/s/management_test",
        priority="low"
    )
    print(f"✓ 测试任务已提交: {task_id}")

    # 更改优先级
    success = manager.change_priority(task_id, "high")
    print(f"✓ 优先级已更改: {success}")

    # 暂停任务（如果是调度任务）
    # success = manager.pause_task(task_id)
    # print(f"✓ 任务已暂停: {success}")

    # 导出队列
    queue_data = manager.export_queue("high_priority")
    print(f"✓ 队列已导出: {queue_data['total_tasks']} 个任务")

    return task_id

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    from queue.manager import QueueManager

    manager = QueueManager()

    # 提交一个会失败的任务（无效URL）
    task_id = manager.submit_task(
        url="invalid_url",
        priority="low",
        metadata={"error_test": True}
    )
    print(f"✓ 错误测试任务已提交: {task_id}")

    # 等待任务处理
    time.sleep(2)

    # 重试失败的任务
    # success = manager.retry_task(task_id)
    # print(f"✓ 任务重试: {success}")

    return task_id

def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("队列管理系统功能测试")
    print("=" * 50)

    results = {}

    try:
        # 基本功能测试
        results['basic'] = test_basic_submission()
        time.sleep(1)

        # 优先级测试
        results['priority'] = test_priority_submission()
        time.sleep(1)

        # 调度测试
        results['scheduled'] = test_scheduled_task()
        time.sleep(1)

        # 批处理测试
        results['batch'] = test_batch_processing()
        time.sleep(1)

        # 监控测试
        results['monitoring'] = test_monitoring()
        time.sleep(1)

        # 报告测试
        results['reporting'] = test_reporting()
        time.sleep(1)

        # 管理功能测试
        results['management'] = test_queue_management()
        time.sleep(1)

        # 错误处理测试
        results['error'] = test_error_handling()

        print("\n" + "=" * 50)
        print("✅ 所有测试完成")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """清理测试数据"""
    print("\n清理测试数据...")
    from queue.models import DatabaseManager, ArticleTask

    with DatabaseManager.get_session() as session:
        # 删除测试任务
        test_tasks = session.query(ArticleTask).filter(
            ArticleTask.url.like('%test%')
        ).all()

        for task in test_tasks:
            session.delete(task)

        session.commit()
        print(f"✓ 已删除 {len(test_tasks)} 个测试任务")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='队列系统测试')
    parser.add_argument('--cleanup', action='store_true', help='清理测试数据')
    parser.add_argument('--test', help='运行特定测试', choices=[
        'basic', 'priority', 'scheduled', 'batch',
        'monitoring', 'reporting', 'management', 'error'
    ])

    args = parser.parse_args()

    if args.cleanup:
        cleanup_test_data()
    elif args.test:
        # 运行特定测试
        test_functions = {
            'basic': test_basic_submission,
            'priority': test_priority_submission,
            'scheduled': test_scheduled_task,
            'batch': test_batch_processing,
            'monitoring': test_monitoring,
            'reporting': test_reporting,
            'management': test_queue_management,
            'error': test_error_handling
        }
        test_functions[args.test]()
    else:
        # 运行所有测试
        success = run_all_tests()
        sys.exit(0 if success else 1)