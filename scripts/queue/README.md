# 队列管理系统

## 概述

高级文章处理队列管理系统，提供优先级调度、定时发布、批处理、监控和报告功能。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动系统

```bash
./scripts/start_queue_system.sh
```

### 3. 提交任务

```bash
# 单个任务
python scripts/queue/manager.py submit https://mp.weixin.qq.com/s/xxx --priority high

# 批量任务
python scripts/queue/manager.py batch urls.txt --priority medium
```

### 4. 监控

访问 http://localhost:5555 查看Flower监控界面

## 系统架构

```
队列管理系统
├── celery_app.py      # Celery应用配置
├── config.py          # 系统配置
├── models.py          # 数据库模型
├── tasks.py           # 任务定义
├── scheduler.py       # 调度器
├── monitor.py         # 监控模块
├── manager.py         # 管理接口
└── reporting.py       # 报告生成
```

## 主要功能

### 优先级队列

- **URGENT (10)** - 紧急任务
- **HIGH (8)** - 高优先级
- **MEDIUM (5)** - 中等优先级
- **LOW (3)** - 低优先级
- **BACKGROUND (1)** - 后台任务

### 调度功能

- 定时发布
- 循环任务
- 批量调度
- 时间窗口优化

### 监控和报告

- 实时状态监控
- 性能指标跟踪
- 健康检查
- 日报/周报/月报生成

### 队列管理

- 任务提交/取消/重试
- 批量操作
- 优先级调整
- 死信队列管理

## API使用

```python
from scripts.queue import QueueManager, get_scheduler, get_monitor

# 提交任务
manager = QueueManager()
task_id = manager.submit_task(url, priority="high")

# 调度发布
scheduler = get_scheduler()
scheduler.schedule_article(url, publish_at=datetime.now() + timedelta(hours=2))

# 监控状态
monitor = get_monitor()
status = monitor.get_realtime_status()
```

## 命令行工具

```bash
# 状态查看
python scripts/queue/manager.py status

# 健康检查
python scripts/queue/manager.py health

# 导出队列
python scripts/queue/manager.py export --output backup.json

# 导入队列
python scripts/queue/manager.py import backup.json
```

## 配置

环境变量（`.env`文件）：

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
DATABASE_URL=postgresql://user:pass@localhost:5432/queue
FLOWER_BASIC_AUTH=admin:password
```

## 测试

```bash
# 运行测试
python scripts/test_queue_system.py

# 运行特定测试
python scripts/test_queue_system.py --test monitoring

# 清理测试数据
python scripts/test_queue_system.py --cleanup
```

## 故障排除

### Redis连接问题

```bash
redis-cli ping
redis-server
```

### 数据库连接问题

```bash
pg_isready
createdb article_queue
```

### 查看日志

```bash
tail -f logs/celery-*.log
tail -f logs/flower.log
```

## 性能优化

- 调整Worker并发数
- 配置任务超时
- 设置速率限制
- 使用批处理

## 详细文档

完整文档请查看：[队列系统使用指南](../../docs/queue_system_guide.md)