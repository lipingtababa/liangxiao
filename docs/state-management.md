# 文章状态管理系统文档

## 概述

文章状态管理系统用于跟踪已处理的微信文章，避免重复处理，支持增量更新。系统通过维护一个JSON格式的状态文件来记录所有处理过的文章信息。

## 核心功能

### 1. 状态跟踪

- 记录每篇文章的处理状态（完成/错误）
- 保存文章元数据（标题、作者、发布日期等）
- 记录处理时间和处理次数
- 使用内容哈希检测文章更新

### 2. 增量处理

- 自动跳过已处理的文章
- 检测文章内容变化并重新处理
- 支持强制更新模式
- 批量处理URL列表

### 3. 版本控制

- 状态文件包含版本信息
- 支持向后兼容
- 状态文件可被Git忽略（避免提交敏感信息）

## 使用方法

### 基本命令

#### 1. 处理单个文章

```bash
python scripts/extract_content_with_state.py --url https://mp.weixin.qq.com/s/xxx
```

#### 2. 批量处理文章

```bash
python scripts/extract_content_with_state.py --input articles.txt
```

#### 3. 强制更新所有文章

```bash
python scripts/extract_content_with_state.py --input articles.txt --force-update
```

#### 4. 跳过状态管理（传统模式）

```bash
python scripts/extract_content_with_state.py --url https://... --skip-state
```

#### 5. 查看处理统计

```bash
python scripts/extract_content_with_state.py --stats
```

### 状态管理器命令

#### 查看统计信息

```bash
python scripts/state_manager.py --status
```

#### 检查特定URL状态

```bash
python scripts/state_manager.py --check https://mp.weixin.qq.com/s/xxx
```

#### 列出所有已处理文章

```bash
python scripts/state_manager.py --list
```

#### 清理旧记录

```bash
# 清理30天前的记录
python scripts/state_manager.py --cleanup 30
```

## 状态文件格式

状态文件 `processed_articles.json` 的结构：

```json
{
  "version": "1.0.0",
  "created_at": "2024-01-01T10:00:00",
  "last_updated": "2024-01-15T15:30:00",
  "articles": {
    "https://mp.weixin.qq.com/s/xxx": {
      "url": "https://mp.weixin.qq.com/s/xxx",
      "title": "文章标题",
      "author": "瑞典马工",
      "publish_date": "2024-01-01",
      "content_hash": "sha256哈希值",
      "word_count": 1500,
      "image_count": 5,
      "first_processed_at": "2024-01-01T10:00:00",
      "last_processed_at": "2024-01-15T15:30:00",
      "process_count": 2,
      "status": "completed",
      "error": null
    }
  },
  "statistics": {
    "total_processed": 10,
    "total_updated": 3,
    "total_errors": 1
  }
}
```

## 工作流程

### 增量处理流程

1. **读取URL列表**
   - 从文件或命令行参数获取URL

2. **状态检查**
   - 检查每个URL是否已处理
   - 检测内容是否有更新

3. **选择性处理**
   - 跳过未变化的文章
   - 处理新文章和更新的文章

4. **更新状态**
   - 记录处理结果
   - 更新统计信息

### 内容更新检测

系统使用SHA256哈希算法计算文章内容的指纹：

1. 提取文章纯文本内容
2. 计算内容的SHA256哈希
3. 与状态文件中的哈希对比
4. 如果不同，标记为需要更新

## 配置选项

### 命令行参数

| 参数             | 说明             | 默认值                    |
| ---------------- | ---------------- | ------------------------- |
| `--state-file`   | 状态文件路径     | `processed_articles.json` |
| `--force-update` | 强制更新所有文章 | False                     |
| `--skip-state`   | 跳过状态管理     | False                     |
| `--output`       | 输出文件路径     | `extracted.json`          |

### 环境变量

- `GITHUB_ACTIONS`: 在GitHub Actions环境中自动使用mock数据

## 最佳实践

### 1. 定期清理

建议定期清理旧的处理记录，保持状态文件大小合理：

```bash
# 每月清理一次，保留最近30天的记录
python scripts/state_manager.py --cleanup 30
```

### 2. 备份状态文件

虽然状态文件可以重建，但建议定期备份：

```bash
cp processed_articles.json processed_articles.backup.json
```

### 3. 处理错误

检查并重新处理错误的文章：

```bash
# 查看所有文章状态
python scripts/state_manager.py --list

# 强制重新处理特定文章
python scripts/extract_content_with_state.py --url https://... --force-update
```

### 4. Git忽略

状态文件已在`.gitignore`中，避免提交到版本控制：

```gitignore
processed_articles.json
*.tmp
```

## 故障排除

### 问题1: 状态文件损坏

**症状**: JSON解析错误
**解决方案**: 删除状态文件，系统会自动创建新的

```bash
rm processed_articles.json
```

### 问题2: 文章重复处理

**症状**: 已处理的文章被重复处理
**解决方案**: 检查内容是否真的有变化，或使用`--skip-state`跳过检查

### 问题3: 并发冲突

**症状**: 多个进程同时写入状态文件
**解决方案**: 系统已实现文件锁，但建议避免并行运行多个实例

## API参考

### ArticleStateManager类

主要方法：

```python
# 初始化
manager = ArticleStateManager("processed_articles.json")

# 检查文章是否已处理
is_processed = manager.is_article_processed(url)

# 检查是否需要更新
needs_update = manager.needs_update(url, content)

# 添加/更新文章
manager.add_article(url, article_data)

# 标记错误
manager.mark_article_error(url, error_message)

# 获取未处理的URL
unprocessed = manager.get_unprocessed_urls(url_list)

# 获取统计信息
stats = manager.get_statistics()

# 清理旧条目
removed_count = manager.cleanup_old_entries(days=30)
```

## 测试

运行完整测试套件：

```bash
python scripts/test_state_management.py
```

测试覆盖：

- 基本CRUD操作
- 增量处理逻辑
- 内容更新检测
- 版本控制
- 并发安全性
- 清理功能

## 未来改进

1. **数据库支持**: 考虑使用SQLite替代JSON文件
2. **分布式锁**: 支持多机器环境
3. **自动备份**: 定期自动备份状态文件
4. **Web界面**: 提供可视化管理界面
5. **通知系统**: 文章更新时发送通知
