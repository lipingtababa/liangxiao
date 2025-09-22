# 验收测试实施文档

## 概述

本项目已经实施了基于BDD（行为驱动开发）的验收测试框架，确保系统从用户角度正常工作。

## 已实现的功能

### 1. BDD测试框架设置 ✅

- **框架**: Cucumber.js v11.0.0
- **断言库**: Chai v5.1.2
- **浏览器自动化**: Playwright v1.49.0
- **配置文件**: `cucumber.js`

### 2. 测试场景覆盖 ✅

创建了4个主要功能模块的验收测试：

#### 文章提取测试 (`features/01_article_extraction.feature`)
- 单篇文章提取
- 包含图片的文章处理
- 批量URL处理
- 特殊格式内容保留
- 错误处理

#### 翻译功能测试 (`features/02_translation.feature`)
- 中英文翻译
- 专有名词词汇表
- 文化内容适配
- 引用和链接保留
- 翻译质量检查

#### 发布功能测试 (`features/03_publishing.feature`)
- Markdown文件生成
- 文件命名规范
- 图片资源管理
- 首页文章列表
- SEO优化

#### 端到端工作流测试 (`features/04_end_to_end_workflow.feature`)
- 完整发布流程
- 批量处理
- 文章更新
- 监控和日志
- 错误恢复机制

### 3. 步骤定义实现 ✅

- **通用步骤** (`common_steps.js`): 系统配置、通用操作、验证
- **提取步骤** (`extraction_steps.js`): 文章提取相关操作
- **翻译步骤** (`translation_steps.js`): 翻译功能相关操作
- **发布步骤** (`publishing_steps.js`): 发布流程相关操作

### 4. 测试环境配置 ✅

- **World对象** (`support/world.js`): 提供测试上下文和工具方法
- 浏览器自动化支持
- Python脚本执行支持
- 截图和报告生成

### 5. CI/CD集成 ✅

- GitHub Actions工作流 (`.github/workflows/acceptance-tests.yml`)
- 自动运行测试（push到main/develop分支）
- 测试报告生成和存档
- 失败截图保存

### 6. Git钩子集成 ✅

- Pre-push钩子 (`.husky/pre-push`)
- 推送前自动运行关键测试
- 防止失败的代码进入远程仓库

## 如何运行测试

### 快速开始

```bash
# 安装依赖
npm install

# 运行所有验收测试
npm run test:acceptance

# 运行特定功能测试
npm run test:acceptance features/01_article_extraction.feature

# 监视模式
npm run test:acceptance:watch

# 完整测试流程（包括服务器启动）
./run-acceptance-tests.sh
```

### 验证设置

```bash
# 验证测试环境是否正确设置
./test-acceptance-setup.sh
```

## 测试运行要求

### 必要条件

1. **Node.js 20.x** 或更高版本
2. **Python 3.9+** （用于运行提取和翻译脚本）
3. **Chromium浏览器** （通过Playwright安装）

### 环境变量

```bash
# 可选配置
export BASE_URL=http://localhost:3000
export HEADLESS=true  # 无头模式运行
export NODE_ENV=test  # 测试环境
```

## 测试标签系统

使用标签来组织和筛选测试：

- `@smoke` - 冒烟测试
- `@critical` - 关键功能
- `@e2e` - 端到端测试
- `@wip` - 正在开发中
- `@error-handling` - 错误处理

运行特定标签的测试：

```bash
npm run test:acceptance -- --tags @critical
npm run test:acceptance -- --tags "not @wip"
```

## 测试报告

测试完成后，报告生成在以下位置：

- **HTML报告**: `test-results/cucumber-report.html`
- **JSON报告**: `test-results/cucumber-report.json`
- **失败截图**: `test-results/screenshots/`

## 最佳实践

1. **每次代码修改后运行测试**
   ```bash
   npm run test:acceptance -- --tags @smoke
   ```

2. **推送前运行完整测试**
   ```bash
   npm run test:all
   ```

3. **调试失败的测试**
   ```bash
   HEADLESS=false npm run test:acceptance
   ```

## 扩展测试

### 添加新的测试场景

1. 在 `features/` 目录创建新的 `.feature` 文件
2. 使用中文Gherkin语法编写场景
3. 在 `step_definitions/` 实现步骤定义
4. 运行测试验证

### 示例

```gherkin
# language: zh-CN
功能: 新功能
  场景: 测试场景
    假设 前置条件
    当 执行操作
    那么 预期结果
```

## 故障排除

### 常见问题

1. **测试超时**
   - 增加cucumber.js中的超时时间
   - 检查网络连接

2. **找不到步骤定义**
   - 确保步骤文本完全匹配
   - 检查正则表达式

3. **浏览器启动失败**
   - 运行 `npx playwright install chromium`
   - 检查系统依赖

## 维护指南

### 定期任务

- **每周**: 运行完整测试套件
- **每月**: 更新测试依赖
- **每季度**: 审查和更新测试场景

### 监控

CI/CD管道会自动运行测试并报告结果。查看GitHub Actions标签页了解测试历史。

## 总结

验收测试框架已经完全实施并集成到开发流程中。它确保：

✅ 所有用户故事都有对应的测试场景
✅ 代码更改不会破坏现有功能
✅ 系统从用户角度正常工作
✅ 自动化测试在CI/CD管道中运行

测试框架遵循BDD最佳实践，使用业务友好的语言编写，便于非技术人员理解和参与。