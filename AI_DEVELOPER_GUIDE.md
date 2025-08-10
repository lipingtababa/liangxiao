# AI开发者指南 - GitHub Actions开发环境

本指南专门为在GitHub Actions环境中工作的AI开发者编写。

## 快速开始

### 第一步：创建开发分支
```yaml
# 你需要通过PR创建新分支
# 在你的代码中创建一个新文件触发PR
```

### 第二步：初始化项目结构
```yaml
- name: 初始化项目
  run: |
    python scripts/scaffold.py
```

### 第三步：运行自测试
使用 `ai-self-test.yml` 工作流验证你的代码

## 开发工作流

### 1. 理解你的环境

你在GitHub Actions runner中工作，这意味着：
- **无法交互式调试** - 使用print语句和日志
- **无法使用本地工具** - 只能使用runner中的工具
- **每次运行都是全新环境** - 没有持久状态
- **2小时超时限制** - 保持操作简洁

### 2. 可用的工具

#### 调试工具
- `debug-helper.yml` - 检查环境、运行命令、测试导入
- `ai-self-test.yml` - 测试你的代码更改

#### 测试工具  
- `test-extractor.yml` - 测试内容提取
- `test-translator.yml` - 测试翻译
- `test-markdown-generator.yml` - 测试Markdown生成
- `test-full-pipeline.yml` - 端到端测试
- `validate-output.yml` - 验证输出格式

### 3. 开发模式

#### 模式A：增量开发
1. 实现 `extract_content.py`
2. 运行 `test-extractor.yml` 测试
3. 实现 `translate.py`
4. 运行 `test-translator.yml` 测试
5. 实现 `generate_markdown.py`
6. 运行 `test-markdown-generator.yml` 测试
7. 运行 `test-full-pipeline.yml` 验证集成

#### 模式B：测试驱动开发
1. 先运行测试查看失败
2. 实现最小功能使测试通过
3. 迭代改进

### 4. 代码结构要求

#### 必需的文件结构
```
scripts/
├── extract_content.py      # 微信内容提取器
├── translate.py            # 翻译器
├── generate_markdown.py    # Markdown生成器
├── process_images.py       # 图片处理器
└── main_pipeline.py        # 主流水线
```

#### 每个脚本必需的接口
```python
# 必须支持命令行参数
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    # ... 参数定义
    args = parser.parse_args()
    main(args)
```

### 5. 数据格式规范

#### 提取数据格式 (extract_content.py 输出)
```json
{
  "title": "文章标题",
  "author": "作者",
  "publish_date": "YYYY-MM-DD",
  "original_url": "https://...",
  "content": {
    "text": "纯文本内容",
    "html": "HTML内容"
  },
  "images": [
    {
      "src": "图片URL",
      "alt": "替代文本",
      "local_filename": "本地文件名"
    }
  ]
}
```

#### 翻译数据格式 (translate.py 输出)
- 继承提取数据的所有字段
- 内容已翻译成英文
- 添加 `translation_metadata` 字段

#### Markdown格式 (generate_markdown.py 输出)
```markdown
---
title: "标题"
date: "YYYY-MM-DD"
author: "作者"
tags: ["tag1", "tag2"]
---

# 标题

正文内容...
```

### 6. 错误处理

#### 必须处理的错误情况
1. 网络请求失败 - 重试3次
2. 解析错误 - 记录并跳过
3. API限制 - 等待并重试
4. 文件I/O错误 - 确保目录存在

#### 错误报告格式
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 你的代码
except Exception as e:
    logger.error(f"错误描述: {e}")
    # 不要静默失败，要明确报告
    raise
```

### 7. 性能优化

#### 必须遵守的限制
- 单个文件处理时间 < 30秒
- 内存使用 < 1GB
- 避免下载大于10MB的图片
- 使用批处理而非循环单个处理

### 8. 测试你的代码

#### 使用debug-helper.yml调试
```yaml
# 测试导入
输入 test_import: scripts.extract_content

# 运行Python代码片段（base64编码）
输入 python_code: cHJpbnQoIkhlbGxvIFdvcmxkIik=

# 检查文件
输入 inspect_file: scripts/extract_content.py
```

#### 使用ai-self-test.yml自测
```yaml
# 全面测试
输入 test_scope: all
输入 auto_fix: true

# 单组件测试
输入 test_scope: extractor
```

### 9. 常见问题解决

#### Q: 如何查看当前环境？
A: 运行 `debug-helper.yml` 不带参数

#### Q: 如何测试模块导入？
A: 使用 `debug-helper.yml` 的 `test_import` 参数

#### Q: 如何查看文件内容？
A: 使用 `debug-helper.yml` 的 `inspect_file` 参数

#### Q: 如何修复代码格式？
A: 运行 `ai-self-test.yml` 并启用 `auto_fix`

#### Q: 如何处理secrets？
A: 永远不要在日志中打印secrets，使用环境变量：
```python
import os
api_key = os.environ.get('GOOGLE_API_KEY', '')  # 映射到 GOOGLE_GEMINI_API_KEY
if not api_key:
    raise ValueError("API密钥未配置")
```

**重要**: GitHub Secrets中的密钥名为 `GOOGLE_GEMINI_API_KEY`，但在代码中使用 `GOOGLE_API_KEY` 环境变量。

### 10. 提交规范

#### Commit消息格式
```
feat: 实现微信内容提取器
fix: 修复图片下载错误
test: 添加单元测试
docs: 更新文档
```

#### PR描述模板
```markdown
## 实现的功能
- [ ] 内容提取
- [ ] 翻译
- [ ] Markdown生成

## 测试结果
- 运行了哪些测试工作流
- 测试通过率

## 已知问题
- 列出尚未解决的问题
```

### 11. 工作流技巧

#### 批量处理
```python
# 好的做法 - 批量处理
urls = read_urls()
results = process_batch(urls)

# 不好的做法 - 逐个处理
for url in urls:
    result = process_single(url)  # 效率低
```

#### 日志输出
```python
# 好的做法 - 结构化日志
print(f"[INFO] 处理文章: {url}")
print(f"[SUCCESS] 提取完成: {title}")
print(f"[ERROR] 失败: {error}")

# 不好的做法 - 无结构日志
print("done")
print(result)
```

#### 使用环境变量
```python
# 好的做法
import os
debug = os.environ.get('DEBUG', 'false').lower() == 'true'

# 不好的做法
debug = True  # 硬编码
```

### 12. 必须记住的要点

1. **你不能SSH进入runner** - 所有调试通过日志
2. **你不能安装系统包** - 只能用pip
3. **你不能保存状态** - 每次运行都是新的
4. **你必须在2小时内完成** - 优化你的代码
5. **你的代码将被其他AI审查** - 保持清晰

### 13. 获取帮助

当遇到问题时：
1. 先运行 `debug-helper.yml` 了解环境
2. 使用 `ai-self-test.yml` 检查代码
3. 查看测试工作流的输出和artifacts
4. 在PR中详细描述问题

### 14. 成功标准

你的实现成功的标志：
- [ ] `test-full-pipeline.yml` 完全通过
- [ ] 所有验证脚本无错误
- [ ] 生成的Markdown可以被Next.js正确渲染
- [ ] 图片都已下载并正确引用
- [ ] 处理10篇文章用时 < 5分钟

---

记住：你是在为其他AI开发者编写代码。保持代码简单、清晰、可测试。