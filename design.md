# 系统设计文档：微信文章翻译发布系统

## 架构概览

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  微信文章URLs   │────>│   翻译流水线     │────>│  magong.se      │
└─────────────────┘     └──────────────────┘     │   (Vercel)      │
        │                       │                 └─────────────────┘
        │                       ▼                         │
        │               ┌──────────────────┐             │
        └──────────────>│   本地存储       │<────────────┘
                        │  - 文章          │
                        │  - 图片          │
                        └──────────────────┘
```

## 系统组件

### 1. 翻译流水线 (`scripts/translate.py`)

#### 目的
主脚本，协调整个翻译和发布流程。

#### 设计决策
- **单一入口**：一个脚本处理整个工作流程，保持简单
- **模块化函数**：提取、翻译、发布功能分离
- **错误恢复**：每个步骤独立失败，不影响整个流程
- **幂等性**：重复运行同一URL不会创建重复内容

#### 核心模块

```python
# 模块结构
translate.py
├── ArticleExtractor     # 获取和解析微信文章
├── ContentTranslator    # 处理翻译逻辑
├── ImageProcessor       # 下载和优化图片
├── MarkdownGenerator    # 创建markdown文件
└── GitPublisher        # 提交并推送到GitHub
```

#### 数据流

```
URL输入 → 获取HTML → 提取内容 → 翻译文本 → 处理图片 
    → 生成Markdown → 本地保存 → Git提交 → 推送到GitHub
```

### 2. 博客应用 (Next.js)

#### 技术选择：Next.js
- **静态站点生成 (SSG)**：预构建页面，性能最优
- **Markdown支持**：原生支持markdown内容
- **图片优化**：内置图片优化功能
- **Vercel集成**：与Vercel无缝部署

#### 目录结构

```
liangxiao/
├── pages/
│   ├── index.js           # 首页，文章列表
│   ├── posts/
│   │   └── [slug].js      # 动态文章页面
│   └── _app.js            # 应用包装器，全局样式
├── posts/                 # Markdown文章（数据）
│   ├── 2025-01-15-文章标题.md
│   └── ...
├── public/
│   ├── images/           # 文章图片
│   │   └── [hash]/       # 按文章组织
│   └── favicon.ico
├── lib/
│   └── posts.js          # 文章数据获取工具
├── styles/
│   └── globals.css       # 全局样式
└── scripts/
    └── translate.py      # 翻译流水线
```

#### 页面组件

1. **首页 (`pages/index.js`)**
   - 按时间倒序列出所有文章
   - 显示标题、摘要、日期和原始标题
   - 响应式网格布局

2. **文章页面 (`pages/posts/[slug].js`)**
   - 将markdown渲染为HTML
   - 显示元数据（日期、原文链接、阅读时间）
   - 为阅读优化的响应式排版

3. **布局组件**
   - 带有站点标题和导航的页头
   - 带有署名和链接的页脚
   - 为未来增强预留的侧边栏

### 3. 数据模型

#### 文章元数据 (Frontmatter)

```yaml
---
title: "英文标题"
originalTitle: "中文原标题"
date: "2025-01-15"
author: "瑞典马工"
excerpt: "文章简要描述"
originalUrl: "https://mp.weixin.qq.com/s/xxxxx"
images: 
  - "/images/article-hash/image1.jpg"
  - "/images/article-hash/image2.jpg"
tags: ["瑞典", "技术", "文化"]
readingTime: 5
---
```

#### 文件命名规范

```
格式: YYYY-MM-DD-标题-slug.md
示例: 2025-01-15-swedish-tech-innovation.md
```

### 4. 翻译策略

#### 翻译服务：Google Translate API

```python
class ContentTranslator:
    def translate(self, text, source='zh-CN', target='en'):
        # 如果文本超过5000字符则分块
        # 保留格式标记
        # 应用词汇表替换
        # 返回翻译后的文本
```

#### 内容适配规则

1. **文化背景**
   ```
   原文: "春节期间" 
   直译: "During Spring Festival"
   适配: "During Spring Festival (Chinese New Year)"
   ```

2. **度量单位**
   ```
   原文: "100公里"
   适配: "100 kilometers (62 miles)"
   ```

3. **专有名词**
   - 保留原始中文名称并加拼音
   - 为机构/地点添加解释

#### 翻译词汇表

```python
GLOSSARY = {
    "瑞典马工": "Swedish Ma Gong",
    "斯德哥尔摩": "Stockholm",
    "微信": "WeChat",
    # 根据需要添加更多术语
}
```

### 5. 图片处理

#### 图片流水线

```python
class ImageProcessor:
    def process(self, image_url, article_hash):
        # 从微信CDN下载图片
        # 生成唯一文件名
        # 为网页优化（压缩、调整大小）
        # 保存到 public/images/[article_hash]/
        # 返回本地路径
```

#### 图片优化
- 最大宽度：1200px
- 格式：WebP，JPEG作为备用
- 压缩：85%质量
- 启用延迟加载

### 6. 部署架构

#### GitHub仓库
```
仓库: lipingtababa/liangxiao
分支: main (生产环境)
```

#### Vercel配置

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "devCommand": "npm run dev",
  "installCommand": "npm install"
}
```

#### 部署流程
1. 开发者运行 `python scripts/translate.py [URL]`
2. 脚本生成markdown和图片
3. Git提交并推送到main分支
4. Vercel检测到推送并触发构建
5. 网站在magong.se更新

### 7. 错误处理

#### 错误类别

1. **提取错误**
   - 无效的URL
   - 网络超时
   - 内容解析失败
   - **恢复**：记录错误，跳过文章

2. **翻译错误**
   - API速率限制
   - 服务不可用
   - **恢复**：指数退避重试

3. **发布错误**
   - Git冲突
   - 构建失败
   - **恢复**：需要人工干预

#### 日志策略

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation.log'),
        logging.StreamHandler()
    ]
)
```

## 安全考虑

1. **API密钥**
   - 存储在环境变量中
   - 永不提交到仓库
   - 本地开发使用`.env.local`

2. **内容净化**
   - 净化HTML以防止XSS
   - 验证图片URL
   - 转义特殊字符

3. **速率限制**
   - 在API调用之间实施延迟
   - 本地缓存翻译
   - 监控API使用情况

## 性能优化

1. **静态生成**
   - 构建时预构建所有页面
   - 增量静态重新生成用于更新

2. **图片优化**
   - 延迟加载
   - 现代格式（WebP）
   - 响应式图片

3. **缓存**
   - 通过Vercel的CDN缓存
   - 浏览器缓存头
   - 本地翻译缓存

## 测试策略

1. **单元测试**
   - 翻译函数
   - Markdown生成
   - 图片处理

2. **集成测试**
   - 完整流水线测试
   - 部署验证

3. **人工测试**
   - 翻译文章的视觉审查
   - 移动端响应性
   - 跨浏览器兼容性

## 监控和维护

1. **监控**
   - Vercel分析
   - 构建状态通知
   - 错误日志

2. **维护任务**
   - 每月更新依赖
   - 审查翻译质量
   - 清理旧图片
   - 备份文章

## 开发工作流程

1. **添加新文章**
   ```bash
   # 1. 获取文章URL
   # 2. 运行翻译脚本
   python scripts/translate.py "https://mp.weixin.qq.com/s/xxxxx"
   
   # 3. 审查生成的markdown
   cat posts/2025-01-15-文章标题.md
   
   # 4. 如需要进行手动调整
   
   # 5. 提交并部署
   git add .
   git commit -m "添加文章: [标题]"
   git push
   ```

2. **本地开发**
   ```bash
   # 安装依赖
   npm install
   
   # 运行开发服务器
   npm run dev
   
   # 在 http://localhost:3000 查看
   ```

## 未来增强

### 第二阶段
- 实现RSS订阅
- 添加搜索功能
- 创建分类页面
- 实现相关文章

### 第三阶段
- 添加评论系统
- 实现通讯订阅
- 创建管理仪表板
- 添加分析功能

## 结论

这个设计提供了一个简单、可维护的解决方案来翻译和发布微信文章。手动流程确保质量控制，而自动化发布减少了重复工作。系统设计为随着需求增长而扩展。