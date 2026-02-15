# 项目规则

详细的 Claude Code 指令见 `.claude/CLAUDE.md`。本文件补充项目级别的通用规则。

## 语言规则

- **文档用中文**：README、设计文档、需求文档、代码注释
- **Commit messages 用英文**，类型前缀：`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`
- **Claude Code 指令用英文**（`.claude/` 目录下的文件）
- **文章内容**：中文写作、英文翻译，各自保持语言一致

## 代码规范

- Python：PEP 8，snake_case
- JavaScript/TypeScript：ESLint + Prettier，camelCase
- 文件命名：kebab-case

## Git 规范

- 直接在 main 分支工作
- 绝对不能伪造数据 — 所有数据必须真实、有来源、可验证
- 发布文章前检查：格式正确、图片正常、链接可访问、移动端适配

## 开发原则

1. 简单优先
2. 手动控制（文章选择和质量由人工把关）
3. 渐进改进
