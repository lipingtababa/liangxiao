# 微信文章翻译发布系统

一个自动化工具，用于监控微信公众号"瑞典马工"，将文章翻译成英文并发布到 magong.se（通过 Vercel）。

## 项目概述

本项目通过提供"瑞典马工"文章的高质量英文翻译，逃离张小龙的独立王国

## 需求说明

### 功能需求

#### 1. 文章输入

- **手动URL输入**：用户手动提供微信文章URL
- **批量处理**：支持一次处理多个URL
- **文章元数据**：提取标题、作者、日期和原始URL

#### 2. 内容提取

- **文本提取**：从微信HTML中提取文章主体文本
- **图片处理**：下载并存储文章中的所有图片
- **格式保留**：保持段落结构、标题、列表
- **特殊元素**：保留引用、代码块、表格（如果存在）

#### 3. 翻译

- **语言**：中文（简体/繁体）→ 英文
- **质量**：使用可靠的翻译服务（Google Translate API）
- **适配**：为国际受众调整内容：
  - 为中国特定内容添加背景说明
  - 解释文化细节
  - 本地化习语和表达
- **词汇表**：保持一致的翻译：
  - "瑞典马工" → "Engineer Ma"
  - 技术术语
  - 专有名词

#### 4. 发布

- **平台**：通过 Vercel 部署到 magong.se
- **格式**：带有 frontmatter 的 Markdown 文件
- **URL结构**：`/posts/[日期]-[标题]`
- **图片**：托管在 `/public/images/`
- **署名**：始终包含原文链接和原作者（注意有些文章是瑞典马工转载的）

#### 5. 博客功能

- **首页**：按时间顺序列出所有文章
- **文章页面**：显示单篇文章，包含：
  - 标题（英文）
  - 发布日期
  - 预计阅读时间
  - 翻译内容
- **移动端响应式**：适配所有设备
- **SEO友好**：元标签、结构化数据

### 非功能需求

#### 性能

- 页面加载时间 < 3秒
- 图片针对网页优化
- 静态站点生成，快速交付

#### 可用性

- 清晰、易读的排版
- 简单的导航
- 无障碍设计（WCAG 2.1 AA合规）

#### 可靠性

- 优雅处理翻译失败
- 图片下载失败时的备用方案
- 错误日志和报告

## 挑战

微信是出了名的封闭系统，这使得以下操作变得困难：

- 程序化关注公众号
- 获取文章列表和内容
- 提取图片和媒体文件
- 提取时保持格式

## 解决方案

### 提取方法：手动输入 + 半自动化

- 手动复制文章URL
- 自动化提取、翻译和发布
- 考虑到微信的限制，这是最可靠的方法

### 翻译流程

```
微信文章 → 内容提取 → 翻译API → 格式保留 → Vercel发布
```

- **内容提取**：解析HTML，提取文本和图片
- **翻译**：使用Google Translate API进行中英翻译
- **格式保留**：保持文章结构、标题和图片位置
- **图片处理**：下载并在Vercel CDN上重新托管图片

## 技术架构

```
liangxiao/
├── scripts/
│   └── translate.py           # 主翻译脚本
├── posts/                     # Markdown文章
│   └── YYYY-MM-DD-标题.md
├── public/
│   └── images/               # 文章图片
├── pages/
│   ├── index.js              # 首页
│   └── posts/
│       └── [slug].js         # 文章页面
├── lib/
│   └── posts.js              # 文章工具函数
├── package.json              # Node依赖
├── requirements.txt          # Python依赖
└── design.md                 # 详细设计文档
```

## 安装说明

```bash
# 克隆仓库
git clone https://github.com/lipingtababa/liangxiao
cd liangxiao

# 安装Python依赖
pip install -r requirements.txt

# 安装Node依赖
npm install

# 配置环境
cp .env.example .env
# 编辑.env文件，添加你的API密钥
```

## 配置

```python
# config.py 示例
WECHAT_ACCOUNT = "瑞典马工"
TARGET_LANGUAGE = "en"
VERCEL_TOKEN = "your-vercel-token"
VERCEL_PROJECT = "magong-se"
TRANSLATION_API = "google"
```

## 使用方法

### 翻译单篇文章

```bash
python scripts/translate.py "https://mp.weixin.qq.com/s/xxxxx"
```

### 批量处理文章

```bash
python scripts/translate.py --batch articles.txt
```

### 本地开发

```bash
# 运行开发服务器
npm run dev
# 在 http://localhost:3000 查看
```

### 部署到Vercel

```bash
# 提交更改
git add .
git commit -m "添加新文章"
git push

# Vercel从GitHub自动部署
```

## 技术栈

### 前端

- **框架**：Next.js 14
- **语言**：JavaScript/React
- **样式**：CSS-in-JS
- **Markdown**：gray-matter, remark

### 后端/脚本

- **语言**：Python 3.9+
- **翻译**：googletrans
- **网页抓取**：beautifulsoup4, requests
- **图片处理**：Pillow

### 基础设施

- **代码仓库**：GitHub (lipingtababa/liangxiao)
- **托管**：Vercel
- **域名**：magong.se

## 限制条件

### 法律

- 尊重版权 - 始终注明原始来源
- 包含翻译免责声明
- 遵守微信服务条款

### 技术

- 微信的封闭生态系统（无官方API访问）
- Google Translate API限制
- Vercel构建时间限制

### 资源

- 单人开发
- 初期没有付费翻译API预算
- 手动文章选择流程

## 成功标准

1. **功能成功**
   - 成功翻译和发布文章
   - 保留文章格式和图片
   - 保持可读、准确的翻译

2. **用户体验**
   - 文章易于查找和阅读
   - 网站加载快速
   - 移动端友好设计

3. **运营成功**
   - 添加新文章的简单工作流程
   - 最少的人工干预
   - 易于维护和更新

## 实施路线图

### 第一阶段：MVP（当前）

- [x] 需求和设计文档
- [ ] 基础翻译脚本
- [ ] Next.js博客设置
- [ ] 手动文章处理
- [ ] Vercel部署

### 第二阶段：增强

- [ ] 批量处理
- [ ] 图片优化
- [ ] 翻译质量改进
- [ ] 错误处理和日志

### 第三阶段：高级功能

- [ ] RSS订阅生成
- [ ] 邮件通讯
- [ ] 搜索功能
- [ ] 分类和标签
- [ ] 分析仪表板

## 贡献

本项目需要以下方面的帮助：

- 改进微信文章提取方法
- 提高翻译质量
- 添加更多发布平台
- 创建更好的监控解决方案

## 许可证

MIT许可证 - 详见LICENSE文件

## 联系方式

有关本项目或翻译内容的问题，请访问 [magong.se](https://magong.se)

---

**注意**：此工具专门用于翻译"瑞典马工"的内容并注明出处。未经许可，不应用于抓取或重新发布内容。
