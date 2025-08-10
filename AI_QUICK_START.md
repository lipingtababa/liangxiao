# AI开发者快速上手指南

如果你是AI开发者，这是你开始开发liangxiao项目的最快路径。

## 🎯 项目目标
将微信公众号"瑞典马工"的文章翻译成英文并发布到magong.se网站。

## 🚀 立即开始（3分钟上手）

### 步骤1: 了解你的环境
运行调试工具了解GitHub Actions环境：

```yaml
# 进入Actions -> debug-ai-env.yml -> Run workflow
# 不需要输入任何参数，直接运行
```

### 步骤2: 创建第一个脚本
复制并修改starter代码：

```bash
# 复制起始文件
cp scripts/extract_content_starter.py scripts/extract_content.py
```

### 步骤3: 测试你的代码
运行验证工作流：

```yaml
# 进入Actions -> validate-ai-implementation.yml -> Run workflow
# 这会给你的实现打分并提供反馈
```

## 📁 核心文件结构

你需要实现这些文件：

```
scripts/
├── extract_content.py      # 从微信文章提取内容
├── translate.py           # 翻译中文到英文
└── generate_markdown.py   # 生成Markdown文件
```

## 🧪 测试数据

所有测试都使用mock数据，无需真实的微信URL：

- **Mock文章**: `.github/test-data/mock-wechat-article.html`
- **测试URL**: `articles.txt` (包含测试URL)

## 💡 开发技巧

### 1. 使用starter代码
不要从零开始，使用 `extract_content_starter.py` 作为模板：

```python
# 已经包含了：
# - 命令行参数处理
# - 错误处理
# - 日志输出
# - GitHub Actions适配
# 你只需要填充TODO部分
```

### 2. 在线调试
使用 `debug-ai-env.yml` 工作流：

```yaml
# 检查文件
check_file: "scripts/extract_content.py"

# 测试Python代码
python_test: "import json; print('OK')"

# 执行命令
command: "ls -la scripts/"
```

### 3. 验证进度
`validate-ai-implementation.yml` 会给你的实现打分（满分100分）：

- 内容提取器: 40分
- 翻译器: 30分
- Markdown生成器: 30分

## 📋 实现检查清单

### 内容提取器 (`extract_content.py`)
- [ ] 能解析HTML提取标题
- [ ] 能提取作者和日期
- [ ] 能提取正文内容
- [ ] 能找到图片URL
- [ ] 支持 `--mock` 参数测试
- [ ] 输出标准JSON格式

### 翻译器 (`translate.py`)
- [ ] 能读取提取器的JSON输出
- [ ] 能翻译标题和内容
- [ ] 处理API密钥（如果有）
- [ ] 输出翻译后的JSON

### Markdown生成器 (`generate_markdown.py`)  
- [ ] 读取翻译后的JSON
- [ ] 生成YAML frontmatter
- [ ] 转换内容为Markdown
- [ ] 处理图片引用
- [ ] 保存到指定目录

## 🔧 调试常见问题

### 问题1: 找不到文件
```bash
# 使用debug-ai-env.yml检查
command: "find . -name '*.py'"
```

### 问题2: 导入错误
```bash
# 测试导入
python_test: "import requests; print('requests OK')"
```

### 问题4: 翻译API不工作
检查API密钥是否正确配置：
- 在GitHub Secrets中应该有 `GOOGLE_GEMINI_API_KEY`
- 使用环境变量: `os.environ.get('GOOGLE_API_KEY')`
- 只使用Google翻译，保持简单

### 问题3: 脚本不执行
```bash
# 检查权限和语法
command: "python scripts/extract_content.py --help"
```

## 🎓 成功标准

你的实现成功当：

1. **验证工作流得分 >= 70分**
2. **生成的文件格式正确**
3. **能处理mock数据**
4. **代码包含适当的错误处理**

## 📚 详细文档

如需详细信息，查看：
- `AI_DEVELOPER_GUIDE.md` - 完整开发指南
- `.github/test-data/README.md` - 测试数据说明
- GitHub Issues - 具体任务要求

## ⚡ 快速命令参考

```bash
# 测试内容提取器
python scripts/extract_content.py --mock --output test.json

# 检查输出格式
python scripts/test/validate_extraction.py test.json

# 调试环境
# 使用 debug-ai-env.yml 工作流
```

记住：你在GitHub Actions中工作，每次运行都是全新环境。使用工作流进行测试和调试，而不是尝试本地开发。

开始编码吧！🚀