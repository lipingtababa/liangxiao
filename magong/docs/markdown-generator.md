# Markdown文件生成器文档

## 概述

Markdown生成器 (`scripts/markdown_generator.py`) 将提取和翻译的文章内容转换为符合Next.js要求的Markdown文件，包含完整的YAML frontmatter元数据。

## 功能特性

### 1. YAML Frontmatter生成
- 自动生成符合Next.js要求的frontmatter
- 包含标题、日期、作者、类别、标签等元数据
- 支持SEO优化字段（description, excerpt）
- 记录翻译信息（如果是翻译文章）

### 2. 智能内容处理
- 自动格式化文章内容为标准Markdown
- 保留原文的段落结构
- 智能插入图片到合适位置
- 处理特殊字符和HTML实体

### 3. 自动分类和标签
- 基于内容自动判断文章类别
- 智能生成相关标签（中英文双语）
- 关键词匹配和权重计算

### 4. URL Slug生成
- 从标题生成URL友好的slug
- 支持中文字符
- 自动处理特殊字符
- 长度限制和截断处理

## 使用方法

### 命令行接口

```bash
# 单个文件处理
python scripts/website/markdown_generator.py --input article.json --output-dir posts

# 批量处理
python scripts/website/markdown_generator.py --input articles.json --output-dir posts

# 干运行（只显示内容，不创建文件）
python scripts/website/markdown_generator.py --input article.json --dry-run

# 生成后验证格式
python scripts/website/markdown_generator.py --input article.json --validate
```

### Python API

```python
from scripts.website.markdown_generator import generate_markdown

# 准备文章数据
article_data = {
    "title": "文章标题",
    "author": "作者名",
    "publish_date": "2024-01-20",
    "original_url": "https://example.com/article",
    "content": {
        "text": "文章内容...",
        "html": "<p>HTML内容...</p>"
    },
    "images": [
        {
            "src": "https://example.com/image.jpg",
            "alt": "图片描述",
            "local_path": "/path/to/local/image.jpg"
        }
    ]
}

# 生成Markdown
result = generate_markdown(article_data, output_dir=Path("posts"))

if result['success']:
    print(f"生成成功: {result['file_path']}")
else:
    print(f"生成失败: {result['errors']}")
```

## 输入数据格式

### 必需字段
- `title`: 文章标题
- `content.text`: 文章文本内容

### 可选字段
- `author`: 作者名（默认：瑞典马工）
- `publish_date`: 发布日期（默认：当天）
- `original_url`: 原文链接
- `images`: 图片数组
- `is_translated`: 是否为翻译文章
- `original_language`: 原文语言
- `translated_at`: 翻译时间

## 输出格式

### 文件命名
```
YYYY-MM-DD-{slug}.md
```
例如：`2024-01-20-瑞典生活指南.md`

### Frontmatter示例
```yaml
---
title: 瑞典生活：如何在斯德哥尔摩找房
date: '2024-01-20'
category: 生活
tags:
  - 瑞典
  - Sweden
  - 斯德哥尔摩
  - Stockholm
  - 生活
  - Life
excerpt: 在斯德哥尔摩找房子可能是每个新来瑞典的人...
author: 瑞典马工
description: 详细介绍在斯德哥尔摩找房的经验...
lastModified: '2024-01-20'
originalUrl: https://mp.weixin.qq.com/s/xxx
translated: true
originalLanguage: zh-CN
translatedAt: '2024-01-20T10:30:00'
---
```

## 自动分类规则

系统会根据文章内容自动判断类别：

- **生活**: 包含"生活"、"日常"、"居住"、"超市"、"购物"等关键词
- **工作**: 包含"工作"、"职场"、"求职"、"面试"、"公司"等关键词
- **教育**: 包含"教育"、"学校"、"大学"、"学习"、"孩子"等关键词
- **科技**: 包含"科技"、"技术"、"创业"、"互联网"、"IT"等关键词
- **文化**: 包含"文化"、"节日"、"传统"、"习俗"、"艺术"等关键词
- **旅游**: 包含"旅游"、"景点"、"游玩"、"度假"、"风景"等关键词
- **美食**: 包含"美食"、"餐厅"、"烹饪"、"食物"、"饮食"等关键词
- **其他**: 无法匹配以上类别时使用

## 标签生成规则

系统会自动生成相关标签：
1. 检测文章中的关键词
2. 添加中英文双语标签
3. 最多生成8个标签
4. 优先级：地点 > 主题 > 通用标签

## 图片处理

### 图片插入策略
- 每3个段落插入一张图片
- 保持内容的阅读流畅性
- 优先使用本地图片路径
- 回退到原始URL（如果本地图片不可用）

### 图片Markdown格式
```markdown
![图片描述](images/filename.jpg)
```

## 错误处理

生成器会处理以下错误情况：
- 缺少必需字段
- 无效的日期格式
- 特殊字符处理
- 文件已存在警告
- 图片路径错误

## 测试

### 单元测试
```bash
python scripts/test_markdown_generator.py
```

### 集成测试
```bash
python scripts/test_integration.py
```

### 格式验证
```bash
python scripts/test/validate_markdown.py posts/
```

## 性能优化

- 使用缓存避免重复计算
- 批量处理支持
- 异步图片下载（如需要）
- 增量更新支持

## 故障排除

### 常见问题

1. **生成的slug包含乱码**
   - 确保输入文本编码为UTF-8
   - 检查特殊字符处理逻辑

2. **frontmatter格式错误**
   - 验证YAML语法
   - 检查特殊字符转义

3. **图片路径错误**
   - 确认图片目录存在
   - 检查相对路径设置

4. **分类不准确**
   - 可以手动指定category字段
   - 调整关键词权重

## 扩展开发

### 添加新的分类
在 `determine_category()` 函数中添加新的类别和关键词：
```python
categories = {
    '新类别': ['关键词1', '关键词2', ...]
}
```

### 自定义frontmatter字段
在 `generate_frontmatter()` 函数中添加新字段：
```python
frontmatter['custom_field'] = value
```

### 修改图片插入策略
调整 `format_content_to_markdown()` 函数中的图片插入逻辑。

## 依赖关系

- Python 3.9+
- pyyaml: YAML处理
- beautifulsoup4: HTML解析（可选）
- pathlib: 文件路径处理

## 相关模块

- `wechat_extractor.py`: 内容提取器
- `translate.py`: 翻译引擎（待实现）
- `validate_markdown.py`: 格式验证器

## 版本历史

- v1.0.0 (2024-01-20): 初始版本
  - 基本Markdown生成功能
  - YAML frontmatter支持
  - 自动分类和标签
  - 图片处理