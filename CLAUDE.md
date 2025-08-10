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
这个项目是为了将"瑞典马工"微信公众号的文章翻译成英文并发布到 magong.se 网站。

### 3. 工作流程 / Workflow
1. 用户手动提供微信文章URL
2. 系统自动提取文章内容和图片
3. 将中文翻译成英文（为国际读者调整内容）
4. 通过 Vercel 发布到 magong.se

### 4. 技术栈 / Tech Stack
- **前端**: Next.js, React
- **翻译脚本**: Python 3.9+
- **部署**: Vercel + GitHub
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
├── scripts/          # Python 翻译脚本
├── posts/           # Markdown 文章
├── public/          # 静态资源
├── pages/           # Next.js 页面
├── lib/             # 工具函数
└── docs/            # 项目文档
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