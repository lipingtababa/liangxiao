# 项目结构

## Next.js 13+ App Router 结构

```
liangxiao/
├── app/                      # App Router 目录
│   ├── layout.tsx           # 根布局文件
│   ├── page.tsx             # 首页
│   ├── globals.css          # 全局样式（含Tailwind）
│   ├── loading.tsx          # 全局加载状态
│   ├── error.tsx            # 全局错误处理
│   ├── not-found.tsx        # 404页面
│   ├── about/               # 关于页面
│   │   └── page.tsx
│   ├── posts/               # 文章列表页
│   │   └── page.tsx
│   ├── guides/              # 指南页面
│   │   └── page.tsx
│   ├── translate/           # 翻译功能页
│   │   └── page.tsx
│   └── api/                 # API路由
│       └── (待实现)
│
├── components/              # React组件
│   └── ui/                  # UI组件库
│
├── lib/                     # 工具函数和库
│   ├── posts.js            # 文章处理功能
│   └── utils/              # 通用工具函数
│
├── public/                  # 静态资源
│
├── scripts/                 # Python脚本
│   ├── translate.py        # 文章翻译脚本
│   └── ...
│
├── posts/                   # Markdown文章存储
│
├── styles/                  # 其他样式文件（如需要）
│
├── .next/                   # Next.js构建输出（已忽略）
├── node_modules/            # NPM依赖（已忽略）
│
├── package.json            # NPM配置
├── tsconfig.json           # TypeScript配置
├── tailwind.config.js      # Tailwind CSS配置
├── postcss.config.js       # PostCSS配置
├── next.config.js          # Next.js配置
└── .eslintrc.json          # ESLint配置
```

## 技术栈配置完成

✅ **Next.js 14.0+** - 使用App Router
✅ **TypeScript 5.9+** - 类型安全
✅ **Tailwind CSS 3.4+** - 样式框架
✅ **ESLint** - 代码规范
✅ **React 18.2+** - UI框架

## 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm start

# 运行翻译脚本
npm run translate
```

## 验收标准完成情况

- ✅ Next.js项目初始化完成
- ✅ 基本目录结构创建
- ✅ 开发服务器可以正常启动（构建成功）
- ✅ TypeScript和ESLint配置正确
