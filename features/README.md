# 验收测试文档

## 概述

本项目使用 BDD (Behavior-Driven Development) 方法进行验收测试，确保系统从用户角度正常工作。我们使用 Cucumber.js 作为测试框架，Playwright 进行浏览器自动化测试。

## 目录结构

```
features/
├── 01_article_extraction.feature    # 文章提取功能测试
├── 02_translation.feature           # 翻译功能测试
├── 03_publishing.feature            # 发布功能测试
├── 04_end_to_end_workflow.feature  # 端到端工作流测试
├── step_definitions/                # 步骤定义
│   ├── common_steps.js             # 通用步骤
│   ├── extraction_steps.js         # 提取相关步骤
│   ├── translation_steps.js        # 翻译相关步骤
│   └── publishing_steps.js         # 发布相关步骤
├── support/                         # 支持文件
│   └── world.js                    # 测试环境配置
└── test-data/                      # 测试数据（如需要）
```

## 安装依赖

```bash
# 安装项目依赖
npm install

# 安装 Playwright 浏览器
npx playwright install chromium
```

## 运行测试

### 运行所有验收测试

```bash
npm run test:acceptance
```

### 运行特定功能的测试

```bash
# 只运行文章提取测试
npm run test:acceptance features/01_article_extraction.feature

# 只运行翻译测试
npm run test:acceptance features/02_translation.feature

# 只运行发布测试
npm run test:acceptance features/03_publishing.feature

# 只运行端到端测试
npm run test:acceptance features/04_end_to_end_workflow.feature
```

### 使用标签运行测试

```bash
# 只运行关键测试
npm run test:acceptance -- --tags @critical

# 只运行端到端测试
npm run test:acceptance -- --tags @e2e

# 排除正在开发的测试
npm run test:acceptance -- --tags "not @wip"

# 只运行错误处理测试
npm run test:acceptance -- --tags @error-handling
```

### 监视模式

```bash
npm run test:acceptance:watch
```

## 测试报告

测试完成后，报告会生成在以下位置：

- HTML报告: `test-results/cucumber-report.html`
- JSON报告: `test-results/cucumber-report.json`
- 截图: `test-results/screenshots/`

## 编写新的测试

### 1. 创建Feature文件

在 `features/` 目录下创建新的 `.feature` 文件：

```gherkin
# language: zh-CN
功能: 新功能描述
  作为一个用户角色
  我希望能够执行某个操作
  以便达到某个目标

  场景: 场景描述
    假设 前置条件
    当 执行操作
    那么 预期结果
```

### 2. 实现步骤定义

在 `features/step_definitions/` 目录下创建或更新步骤定义：

```javascript
const { Given, When, Then } = require('@cucumber/cucumber');

Given('前置条件', async function() {
  // 设置测试环境
});

When('执行操作', async function() {
  // 执行被测试的操作
});

Then('预期结果', async function() {
  // 验证结果
  this.expect(actual).to.equal(expected);
});
```

### 3. 使用World对象

World对象提供了测试上下文和工具方法：

```javascript
// 启动浏览器
await this.launchBrowser();

// 访问页面
await this.page.goto(this.config.baseUrl);

// 截图
await this.takeScreenshot('screenshot-name');

// 执行Python脚本
const output = await this.executePythonScript('script.py', ['arg1', 'arg2']);

// 使用断言
this.expect(value).to.be.true;
```

## 环境变量

测试支持以下环境变量：

- `BASE_URL`: 应用基础URL（默认: http://localhost:3000）
- `API_URL`: API基础URL（默认: http://localhost:3000/api）
- `HEADLESS`: 是否无头模式运行（默认: true）
- `SLOW_MO`: 减慢操作速度用于调试（毫秒）
- `GOOGLE_API_KEY`: Google Translate API密钥

## CI/CD 集成

项目包含 GitHub Actions 工作流配置，会在以下情况自动运行测试：

1. 推送到 main 或 develop 分支
2. 创建 Pull Request
3. 手动触发

查看 `.github/workflows/acceptance-tests.yml` 了解详细配置。

## 最佳实践

1. **保持测试独立**: 每个场景应该独立运行，不依赖其他场景
2. **使用清晰的描述**: Feature和场景描述应该业务友好
3. **避免技术细节**: Feature文件应该描述业务行为，而非技术实现
4. **重用步骤定义**: 尽可能重用已有的步骤定义
5. **适当使用标签**: 使用标签组织和筛选测试
6. **及时清理**: 在After钩子中清理测试数据和状态

## 常见问题

### Q: 测试失败但没有明确错误信息？
A: 查看 `test-results/screenshots/` 目录下的失败截图

### Q: 如何调试测试？
A: 设置 `HEADLESS=false` 和 `SLOW_MO=500` 环境变量

### Q: 测试超时？
A: 可以在 `cucumber.js` 配置文件中增加超时时间

### Q: 如何跳过某些测试？
A: 使用 `@wip` 或 `@skip` 标签，并在运行时排除

## 标签说明

- `@critical`: 关键测试，必须通过
- `@e2e`: 端到端测试
- `@smoke`: 冒烟测试，快速验证基本功能
- `@wip`: 正在开发中的测试
- `@manual`: 需要手动执行的测试
- `@flaky`: 不稳定的测试，会自动重试
- `@error-handling`: 错误处理相关测试
- `@seo`: SEO相关测试
- `@monitoring`: 监控相关测试
- `@error-recovery`: 错误恢复相关测试
- `@quality-check`: 质量检查相关测试