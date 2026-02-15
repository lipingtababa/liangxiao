# liangxiao

magong.se 的 monorepo — 英文博客 + 微信公众号写作系统。

## 这是什么

两个系统，一条流水线：

1. **写作系统** (`writing/`) — 用 Claude Code 的 slash commands 写微信公众号文章，双人格：戚本禹（犀利）和胡适（分析）
2. **magong.se 网站** — Next.js 英文博客，翻译已发布的中文文章给国际读者

流水线：**写作（中文）→ 翻译 → 发布（英文）**

## 项目结构

```
liangxiao/
├── app/                    # Next.js App Router 页面
├── components/             # React 组件（ArticleCard, MarkdownRenderer 等）
├── lib/                    # posts.ts（文章读取）、seo.ts
├── posts/                  # 已发布英文文章（12篇）
├── public/images/          # 文章图片
├── __tests__/              # Jest 测试
│
├── writing/                # 微信文章写作系统
│   ├── 戚本禹/             # 犀利人格（20篇文章）
│   ├── 胡适/               # 分析人格（3篇文章）
│   ├── templates/          # 文章结构模板 + WeChat CSS
│   └── translation/        # 翻译工作区
│
├── scripts/
│   ├── website/            # 网站脚本（内容提取、SEO增强）
│   └── writing/            # 写作脚本（HTML转换、聊天分析）
│
├── .claude/
│   ├── CLAUDE.md           # Claude Code 详细指令
│   └── commands/           # 共享 slash commands
│
└── aichat -> ...           # 微信聊天数据（符号链接，gitignored）
```

## 快速开始

### 安装

```bash
npm install           # Next.js 依赖
pip install -r requirements.txt  # Python 依赖
```

### 本地开发

```bash
npm run dev           # http://localhost:3000
```

### 质量检查

```bash
npm run check         # lint + format + typecheck + test
```

## 写文章

用 Claude Code 的 slash commands，在对应人格目录下工作：

```bash
# 戚本禹风格（犀利挑衅）
cd writing/戚本禹/articles/
mkdir my-topic && cd my-topic
# /brainstorm → /outline → /draft → /review → /convert

# 胡适风格（分析严谨）
cd writing/胡适/articles/
mkdir my-topic && cd my-topic
# /brainstorm → /outline → /draft → /review → /convert
```

每个 slash command 自动输出文件：`brainstorm.md` → `outline.md` → `draft.md` → `wechat.html`

## 翻译发布

```bash
# 翻译中文文章为英文
/english              # 从 writing/ 中的文章生成 posts/ 中的英文 markdown

# 发布到网站
/publish              # 验证 + 构建 + 部署
```

## 技术栈

- **网站**: Next.js 14, React, TypeScript, Tailwind CSS
- **脚本**: Python 3.9+（beautifulsoup4, markdown, googletrans）
- **部署**: Vercel
- **域名**: magong.se

## 写作人格

| | 戚本禹 | 胡适 |
|---|---|---|
| 风格 | 犀利、讽刺、挑战权威 | 分析、严谨、证据导向 |
| 公司 | 点名批评 | 点名分析 |
| 类比 | 生活化、嘲讽（永动机、卖豆腐） | 结构化、科学（工程、经济学） |
| 结论 | 挑衅反转，"来骂我吧" | 综合 + 开放问题，"一起研究" |
| 命名 | 戚本禹（1931-2016），犀利政论家 | 胡适（1891-1962），新文化运动领袖 |
