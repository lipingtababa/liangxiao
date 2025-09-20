# 文章调度和队列管理系统

## 概述

文章调度和队列管理系统提供了完整的文章发布流程管理功能，包括：
- 文章队列管理
- 自动调度
- 发布状态跟踪
- 优先级管理
- 历史记录

## 核心组件

### 1. SchedulingManager (scheduling_manager.py)

主要的调度管理器，负责：
- 管理文章队列
- 调度文章发布
- 跟踪发布状态
- 维护历史记录

### 2. ArticleProcessor (article_processor.py)

集成处理器，将调度系统与内容提取流程连接：
- 批量处理文章
- 自动工作流
- 状态同步

## 文章状态流程

```
添加到队列 (QUEUED) → 调度 (SCHEDULED) → 处理中 (PROCESSING) → 已发布 (PUBLISHED)
                                                        ↓
                                                    失败 (FAILED)
                                                        ↓
                                                    取消 (CANCELLED)
```

## 使用方法

### 基本命令行操作

#### 查看状态

```bash
# 查看队列状态
python scheduling_manager.py --status

# 查看队列中的文章
python scheduling_manager.py --queue

# 查看已调度的文章
python scheduling_manager.py --scheduled

# 查看待发布的文章
python scheduling_manager.py --pending

# 查看未来7天的发布计划
python scheduling_manager.py --upcoming 7
```

#### 调度操作

```bash
# 自动调度队列中的所有文章
python scheduling_manager.py --auto-schedule

# 使用自定义调度文件
python scheduling_manager.py --file my_schedule.json --status
```

### 使用 ArticleProcessor

#### 添加文章到队列

```bash
# 添加单篇文章
python article_processor.py --add "https://mp.weixin.qq.com/s/xxxxx"

# 设置优先级（low, normal, high, urgent）
python article_processor.py --add "https://mp.weixin.qq.com/s/xxxxx" --priority high

# 批量添加文章（从文件）
python article_processor.py --batch-add articles.txt
```

#### 处理和调度

```bash
# 处理待发布的文章
python article_processor.py --process

# 调度下一批文章
python article_processor.py --schedule

# 执行自动工作流（处理+调度）
python article_processor.py --auto
```

### Python API 使用

```python
from scheduling_manager import SchedulingManager, PublishPriority

# 初始化管理器
manager = SchedulingManager("my_schedule.json")

# 添加文章到队列
article_data = {
    'url': 'https://mp.weixin.qq.com/s/article1',
    'title': '文章标题',
    'author': '作者名称',
    'content': '文章内容',
    'images': ['img1.jpg', 'img2.jpg']
}

# 添加普通优先级文章
queue_id = manager.add_to_queue(article_data, PublishPriority.NORMAL)

# 添加高优先级文章
urgent_id = manager.add_to_queue(urgent_article, PublishPriority.URGENT)

# 调度文章
manager.schedule_article(queue_id)

# 自动调度所有队列中的文章
manager.auto_schedule_queue()

# 获取待发布文章
pending = manager.get_pending_articles(limit=5)

# 标记文章为已发布
manager.mark_as_published(queue_id, published_url="https://magong.se/posts/article1")

# 获取队列状态
status = manager.get_queue_status()
print(f"队列大小: {status['queue_size']}")
print(f"已调度: {status['scheduled_count']}")
```

## 配置选项

调度系统的默认设置可以通过 `update_settings` 方法修改：

```python
manager.update_settings(
    default_interval_hours=48,      # 发布间隔（小时）
    max_queue_size=200,             # 最大队列大小
    auto_publish=True,              # 自动发布
    publish_time="14:00",           # 默认发布时间
    timezone="Europe/Stockholm"     # 时区
)
```

## 文件格式

### 调度文件结构 (JSON)

```json
{
  "version": "1.0.0",
  "created_at": "2025-09-21T10:00:00",
  "last_updated": "2025-09-21T10:00:00",
  "settings": {
    "default_interval_hours": 24,
    "max_queue_size": 100,
    "auto_publish": false,
    "publish_time": "09:00",
    "timezone": "Europe/Stockholm"
  },
  "queue": [
    {
      "id": "uuid",
      "url": "https://...",
      "title": "文章标题",
      "priority": 2,
      "status": "queued",
      "added_at": "2025-09-21T10:00:00"
    }
  ],
  "scheduled": {
    "uuid": {
      "id": "uuid",
      "title": "文章标题",
      "status": "scheduled",
      "scheduled_at": "2025-09-22T09:00:00"
    }
  },
  "history": [],
  "statistics": {
    "total_queued": 0,
    "total_scheduled": 0,
    "total_published": 0,
    "total_failed": 0,
    "total_cancelled": 0
  }
}
```

### 批量添加文件格式

创建一个文本文件 `articles.txt`，每行一个URL：

```
https://mp.weixin.qq.com/s/article1
https://mp.weixin.qq.com/s/article2
# 注释行会被忽略
https://mp.weixin.qq.com/s/article3
```

## 优先级系统

系统支持4个优先级级别：

1. **URGENT (4)** - 紧急文章，最高优先级
2. **HIGH (3)** - 高优先级
3. **NORMAL (2)** - 普通优先级（默认）
4. **LOW (1)** - 低优先级

队列中的文章会按照优先级从高到低排序。

## 自动化工作流

### 定时任务设置（cron）

可以设置定时任务自动执行处理流程：

```bash
# 每天早上9点执行自动工作流
0 9 * * * cd /path/to/project && python scripts/article_processor.py --auto

# 每6小时检查并处理待发布文章
0 */6 * * * cd /path/to/project && python scripts/article_processor.py --process
```

### GitHub Actions 集成

```yaml
name: Process Articles

on:
  schedule:
    - cron: '0 9 * * *'  # 每天UTC时间9点
  workflow_dispatch:      # 允许手动触发

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run auto workflow
        run: python scripts/article_processor.py --auto

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add -A
          git commit -m "Auto-process articles" || echo "No changes"
          git push
```

## 错误处理

系统会自动处理以下情况：

1. **网络错误** - 文章会被标记为失败，可以手动重试
2. **队列已满** - 拒绝添加新文章，需要先处理现有队列
3. **重复文章** - 通过状态管理器检测，避免重复处理
4. **文件锁定** - 使用文件锁确保并发安全

## 统计和报告

系统自动跟踪以下统计信息：

- 总加入队列数
- 总调度数
- 总发布数
- 总失败数
- 总取消数

查看统计：

```python
status = manager.get_queue_status()
stats = status['statistics']
print(f"总发布: {stats['total_published']}")
print(f"总失败: {stats['total_failed']}")
```

## 故障排除

### 常见问题

1. **队列已满**
   - 增加 `max_queue_size` 设置
   - 处理现有队列中的文章

2. **调度时间冲突**
   - 调整 `default_interval_hours` 设置
   - 手动设置特定的发布时间

3. **文件锁定错误**
   - 确保没有其他进程在访问调度文件
   - 检查文件权限

## 测试

运行测试套件：

```bash
# 运行单元测试和集成测试
python scripts/test_scheduling.py

# 测试特定功能
python -m unittest test_scheduling.TestSchedulingManager.test_add_to_queue
```

## 最佳实践

1. **定期备份** - 备份 `article_schedule.json` 文件
2. **监控队列** - 定期检查队列状态，避免积压
3. **优先级管理** - 合理使用优先级，避免所有文章都设为紧急
4. **错误处理** - 定期检查失败的文章，分析失败原因
5. **批量处理** - 使用批量添加功能提高效率

## 扩展开发

系统设计为可扩展的，可以轻松添加新功能：

- 自定义发布策略
- 集成其他发布平台
- 添加通知系统
- 实现更复杂的调度算法

## 相关文档

- [状态管理系统](state-management.md)
- [Markdown生成器](markdown-generator.md)
- [项目结构说明](../PROJECT_STRUCTURE.md)