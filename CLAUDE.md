# Claude 项目规则 / Claude Project Rules

## 重要规则 / Important Rules

### 1. 文档语言规则 / Documentation Language Rule

**所有文档必须用中文编写** / All documentation must be written in Chinese

- README.md - 用中文
- 设计文档 - 用中文
- 需求文档 - 用中文
- 代码注释 - 用中文
- commit messages - 可以用英文，但描述详情用中文

### 2. 项目目标 / Project Goal

这是一个合并的 monorepo，包含两个系统：

1. **magong.se 网站** — Next.js 英文博客，翻译微信文章给国际读者
2. **写作系统** — 双人格微信文章工厂（benyu 犀利 + vannevar 分析），位于 `writing/` 目录

流水线：**写作（中文）** → **翻译** → **发布（英文）**

### 3. 工作流程 / Workflow

**网站发布流程：**
1. 用户手动提供微信文章URL
2. 系统自动提取文章内容和图片
3. 将中文翻译成英文（为国际读者调整内容）
4. 发布到 magong.se

**文章写作流程（writing/ 目录）：**
1. `/brainstorm` — 研究话题
2. `/outline` — 生成大纲
3. `/draft` — 撰写草稿
4. `/review` — 审查校对
5. `/convert` — 转换为微信HTML

**关键规则：绝对不能伪造数据。** 所有数据必须真实、有来源、可验证。

### 4. 技术栈 / Tech Stack

- **前端**: Next.js, React
- **翻译脚本**: Python 3.9+
- **部署**: GitHub + Web 托管服务
- **翻译服务**: Google Translate API

### 5. 代码规范 / Code Standards

- Python 代码：遵循 PEP 8
- JavaScript 代码：使用 ESLint 配置
- 文件命名：使用小写字母和连字符（kebab-case）
- 变量命名：
  - Python: snake_case
  - JavaScript: camelCase

### 6. Git 规范 / Git Conventions

- 分支策略：直接在 main 分支工作（小项目）
- Commit 格式：`<类型>: <描述>`
  - 类型：feat, fix, docs, style, refactor, test, chore
  - 例子：`feat: 添加文章翻译功能`

### 7. 项目结构 / Project Structure

```
liangxiao/
├── app/              # Next.js 页面
├── components/       # React 组件
├── lib/              # 工具函数
├── posts/            # 已发布英文文章
├── public/           # 静态资源
├── docs/             # 项目文档
├── writing/          # 文章写作系统
│   ├── benyu/        # 犀利人格
│   ├── vannevar/     # 分析人格
│   └── templates/    # 文章结构模板
├── scripts/
│   ├── website/      # 网站脚本（提取、SEO）
│   └── writing/      # 写作脚本（HTML转换、聊天分析）
└── aichat -> ...     # 符号链接（gitignored）
```

### 8. 开发原则 / Development Principles

1. **简单优先**：选择最简单可行的解决方案
2. **手动控制**：文章选择和质量控制由人工完成
3. **渐进改进**：先实现基本功能，再逐步优化
4. **文档先行**：先写文档，再写代码

### 9. 特殊注意事项 / Special Notes

- WeChat 是封闭系统，不要依赖官方 API
- 所有翻译内容必须注明原文出处
- 尊重版权，遵守相关法律法规
- 图片需要下载并重新托管

### 10. 测试要求 / Testing Requirements

- 每个新功能必须先在本地测试
- 翻译质量需要人工审核
- 部署前检查：
  - [ ] 文章格式正确
  - [ ] 图片正常显示
  - [ ] 链接可访问
  - [ ] 移动端适配

---

**记住：所有文档用中文写！** / Remember: Write all docs in Chinese!
