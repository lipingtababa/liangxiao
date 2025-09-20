# 队列管理系统使用指南

## 概述

队列管理系统为文章处理提供了高级的调度和管理功能，支持优先级队列、定时发布、批处理、监控和报告等功能。

## 系统架构

### 核心组件

1. **Celery** - 分布式任务队列
2. **Redis** - 消息代理和缓存
3. **PostgreSQL** - 任务持久化存储
4. **APScheduler** - 高级调度功能
5. **Flower** - Web监控界面
6. **Prometheus** - 指标收集

### 队列优先级

系统支持5个优先级级别：
- **URGENT (10)** - 紧急任务，立即处理
- **HIGH (8)** - 高优先级任务
- **MEDIUM (5)** - 中等优先级（默认）
- **LOW (3)** - 低优先级任务
- **BACKGROUND (1)** - 后台任务

## 安装和配置

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装系统依赖（macOS）
brew install redis postgresql

# 安装系统依赖（Ubuntu）
apt-get install redis-server postgresql
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/article_queue

# Flower配置
FLOWER_BASIC_AUTH=admin:password
```

### 3. 初始化数据库

```bash
python -c "from scripts.queue.models import DatabaseManager; DatabaseManager.create_tables()"
```

## 启动系统

### 快速启动

```bash
# 启动所有组件
./scripts/start_queue_system.sh

# 不启动Flower监控界面
./scripts/start_queue_system.sh --no-flower
```

### 手动启动各组件

```bash
# 启动Redis
redis-server

# 启动Celery Worker
celery -A scripts.queue.celery_app worker --loglevel=info

# 启动Celery Beat（调度器）
celery -A scripts.queue.celery_app beat --loglevel=info

# 启动Flower监控
celery -A scripts.queue.celery_app flower --port=5555
```

## 使用方法

### 命令行接口

#### 提交任务

```bash
# 提交单个任务
python scripts/queue/manager.py submit https://mp.weixin.qq.com/s/xxx --priority high

# 调度发布
python scripts/queue/manager.py submit https://mp.weixin.qq.com/s/xxx --schedule "2024-12-25 10:00:00"

# 批量提交
python scripts/queue/manager.py batch urls.txt --priority medium --interval 30
```

#### 管理任务

```bash
# 查看队列状态
python scripts/queue/manager.py status

# 健康检查
python scripts/queue/manager.py health

# 取消任务
python scripts/queue/manager.py cancel task_123456

# 重试失败任务
python scripts/queue/manager.py retry task_123456
```

#### 导入导出

```bash
# 导出队列
python scripts/queue/manager.py export --queue high_priority --output queue_backup.json

# 导入队列
python scripts/queue/manager.py import queue_backup.json
```

### Python API

```python
from scripts.queue import QueueManager, get_scheduler, get_monitor

# 创建管理器
manager = QueueManager()

# 提交任务
task_id = manager.submit_task(
    url="https://mp.weixin.qq.com/s/xxx",
    priority="high",
    metadata={"author": "作者名"}
)

# 批量提交
batch_id = manager.submit_batch(
    urls=["url1", "url2", "url3"],
    priority="medium",
    batch_name="每日文章",
    interval_minutes=30
)

# 调度发布
from datetime import datetime, timedelta

scheduler = get_scheduler()
scheduler.schedule_article(
    url="https://mp.weixin.qq.com/s/xxx",
    publish_at=datetime.now() + timedelta(hours=2),
    priority="high"
)

# 监控状态
monitor = get_monitor()
status = monitor.get_realtime_status()
print(f"队列状态: {status}")

# 生成报告
from scripts.queue import get_reporter

reporter = get_reporter()
daily_report = reporter.generate_daily_report()
reporter.export_report(daily_report, format='html', output_path='report.html')
```

## 监控和报告

### Web监控界面

访问 Flower 监控界面：
- URL: http://localhost:5555
- 用户名: admin
- 密码: password

### Prometheus指标

系统自动导出以下指标：
- `queue_size` - 队列大小
- `tasks_processed_total` - 处理任务总数
- `task_duration_seconds` - 任务处理时长
- `task_failure_rate` - 任务失败率
- `queue_health_score` - 队列健康分数

### 生成报告

```python
from scripts.queue import get_reporter
from datetime import datetime

reporter = get_reporter()

# 日报
daily = reporter.generate_daily_report()

# 周报
weekly = reporter.generate_weekly_report()

# 月报
monthly = reporter.generate_monthly_report(2024, 12)

# 自定义报告
custom = reporter.generate_custom_report(
    start_date=datetime(2024, 12, 1),
    end_date=datetime(2024, 12, 31),
    metrics=['summary', 'error_analysis', 'queue_utilization']
)

# 导出报告
reporter.export_report(daily, format='html', output_path='daily_report.html')
reporter.export_report(weekly, format='pdf', output_path='weekly_report.pdf')
```

## 高级功能

### 1. 优先级调度

```python
# 紧急任务 - 立即处理
manager.submit_task(url, priority="urgent")

# 设置自定义优先级分数
task = ArticleTask(priority_score=15)  # 更高的分数 = 更高优先级
```

### 2. 批处理优化

```python
# 并发批处理
manager.submit_batch(urls, interval_minutes=0)  # 所有任务并发执行

# 顺序批处理
manager.submit_batch(urls, interval_minutes=30)  # 每30分钟处理一个
```

### 3. 循环调度

```python
# 每天上午10点执行
scheduler.schedule_recurring(
    url_source="file://daily_urls.txt",
    cron_expression="0 10 * * *",
    priority="high"
)

# 每小时执行
scheduler.schedule_recurring(
    url_source="http://api.example.com/urls",
    cron_expression="0 * * * *",
    priority="medium"
)
```

### 4. 队列容量管理

```python
# 更新队列配置
manager.update_queue_config('high_priority', {
    'max_size': 200,
    'rate_limit': '150/h',
    'task_timeout': 600
})

# 优化调度窗口
scheduler.optimize_schedule(
    task_ids=['task1', 'task2', 'task3'],
    target_window={
        'start': datetime(2024, 12, 25, 8, 0),
        'end': datetime(2024, 12, 25, 18, 0),
        'max_per_hour': 5
    }
)
```

### 5. 死信队列管理

```python
# 查看死信队列
dead_letters = monitor.get_dead_letter_queue(limit=50)

# 从死信队列恢复
new_task_id = manager.resurrect_from_dead_letter(dead_letter_id=123)

# 清理过期死信
cleanup_dead_letter_queue.apply_async()
```

## 故障排除

### 常见问题

1. **Redis连接失败**
   ```bash
   # 检查Redis是否运行
   redis-cli ping

   # 启动Redis
   redis-server
   ```

2. **数据库连接失败**
   ```bash
   # 检查PostgreSQL状态
   pg_isready

   # 创建数据库
   createdb article_queue
   ```

3. **任务积压**
   ```bash
   # 增加Worker数量
   celery -A scripts.queue.celery_app worker --concurrency=16

   # 清空队列
   python scripts/queue/manager.py clear-queue medium_priority
   ```

4. **内存不足**
   ```python
   # 限制任务内存使用
   task.memory_limit = 512  # MB
   ```

### 日志位置

- Celery Worker: `logs/celery-*.log`
- Celery Beat: `logs/celery-beat.log`
- Flower: `logs/flower.log`
- 应用日志: `logs/queue_system.log`

## 性能优化

### 1. Worker配置

```bash
# 高并发配置
celery worker --concurrency=16 --pool=gevent

# CPU密集型任务
celery worker --concurrency=4 --pool=prefork

# IO密集型任务
celery worker --concurrency=100 --pool=eventlet
```

### 2. 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_task_status_priority ON article_tasks(status, priority_score);
CREATE INDEX idx_task_scheduled ON article_tasks(scheduled_at, status);

-- 定期清理
DELETE FROM queue_statistics WHERE timestamp < NOW() - INTERVAL '30 days';
```

### 3. Redis优化

```bash
# 配置持久化
redis-cli CONFIG SET save "900 1 300 10 60 10000"

# 设置最大内存
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 安全建议

1. **更改默认密码**
   - Flower认证
   - Redis密码
   - 数据库密码

2. **限制访问**
   - 使用防火墙规则
   - 配置IP白名单

3. **加密传输**
   - 使用SSL/TLS
   - 配置HTTPS

4. **审计日志**
   - 记录所有操作
   - 定期审查

## 维护

### 日常维护

```bash
# 清理过期任务
python scripts/queue/maintenance.py cleanup --days 30

# 备份数据库
pg_dump article_queue > backup_$(date +%Y%m%d).sql

# 监控磁盘空间
df -h /var/log
```

### 升级

```bash
# 备份当前配置
cp -r scripts/queue scripts/queue.backup

# 更新代码
git pull

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启系统
./scripts/stop_queue_system.sh
./scripts/start_queue_system.sh
```

## 联系支持

如有问题，请查看：
- 项目文档: `/docs/queue_system_guide.md`
- 日志文件: `/logs/`
- GitHub Issues: https://github.com/your-repo/issues