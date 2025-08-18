# 开发指南 / Development Guide

## 项目结构 / Project Structure

```
liangxiao/
├── app/                    # Next.js App Router 页面
│   ├── globals.css         # 全局样式文件
│   ├── layout.tsx          # 根布局组件
│   ├── page.tsx            # 主页面
│   └── posts/              # 文章页面
│       └── [id]/
│           └── page.tsx    # 动态文章页面
├── components/             # 可复用组件
│   └── ui/                 # UI 组件库
│       ├── Button.tsx
│       └── index.ts
├── lib/                    # 工具函数
│   └── posts.ts           # 文章数据处理
├── posts/                  # Markdown 文章文件
├── scripts/                # Python 翻译脚本
└── public/                 # 静态资源
```

## 技术栈 / Tech Stack

- **Next.js 14** - React 框架，使用 App Router
- **TypeScript** - 类型安全
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Gray-matter** - Markdown 前置数据解析
- **Remark** - Markdown 到 HTML 转换
- **Date-fns** - 日期格式化

## 开发命令 / Development Commands

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm run start

# 运行 ESLint 检查
npm run lint

# 运行 TypeScript 类型检查
npm run typecheck

# 运行翻译脚本
npm run translate
```

## 文章格式 / Article Format

文章使用 Markdown 格式，包含以下前置数据：

```markdown
---
title: 'English Title'
originalTitle: '中文原标题'
date: '2025-08-18'
excerpt: 'Article excerpt for preview'
originalUrl: 'https://mp.weixin.qq.com/...'
---

# Article Content

Your article content here...
```

## 开发规范 / Development Standards

1. **代码风格**：使用 ESLint 和 TypeScript 严格模式
2. **组件命名**：使用 PascalCase
3. **文件命名**：使用 kebab-case
4. **提交规范**：使用语义化提交信息

## 部署 / Deployment

项目使用 Vercel 自动部署：
- `main` 分支 → 生产环境
- 功能分支 → 预览环境