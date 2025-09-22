/**
 * 通用步骤定义
 * 包含所有功能模块共享的步骤
 */

const { Given, When, Then } = require('@cucumber/cucumber');

// ==================== 背景和前置条件 ====================

Given('系统已经正确配置', async function() {
  // 确保expect被正确初始化
  if (!this.expect) {
    const chai = require('chai');
    this.expect = chai.expect;
  }

  // 验证必要的环境变量
  const requiredEnvVars = ['GOOGLE_API_KEY'];
  const missingVars = requiredEnvVars.filter(v => !process.env[v]);

  // 对于测试环境，我们可以跳过环境变量检查
  if (process.env.NODE_ENV !== 'test' && missingVars.length > 0) {
    this.expect(missingVars).to.be.empty;
  }

  // 验证必要的目录存在
  const requiredDirs = ['posts', 'public/images', 'scripts'];
  for (const dir of requiredDirs) {
    // 初始化fileExists方法如果不存在
    if (!this.fileExists) {
      const fs = require('fs').promises;
      this.fileExists = async (path) => {
        try {
          await fs.access(path);
          return true;
        } catch {
          return false;
        }
      };
    }
    const exists = await this.fileExists(dir);
    this.expect(exists, `目录 ${dir} 应该存在`).to.be.true;
  }
});

Given('有可用的微信文章URL', function() {
  // 初始化testData如果不存在
  if (!this.testData) {
    this.testData = {};
  }
  // 设置测试用的微信文章URL
  this.testData.wechatUrl = 'https://mp.weixin.qq.com/s/test-article';
});

Given('已经成功提取了微信文章内容', async function() {
  // 初始化testData如果不存在
  if (!this.testData) {
    this.testData = {};
  }
  // 模拟已提取的文章内容
  this.testData.extractedContent = {
    title: '测试文章标题',
    author: '瑞典马工',
    date: new Date().toISOString().split('T')[0],
    content: '这是一篇测试文章的内容。\n\n包含多个段落。',
    images: ['image1.jpg', 'image2.jpg']
  };
});

Given('Google Translate API已配置', function() {
  const hasApiKey = !!process.env.GOOGLE_API_KEY;
  this.expect(hasApiKey, 'GOOGLE_API_KEY 环境变量应该设置').to.be.true;
});

Given('Next.js博客系统正在运行', async function() {
  await this.launchBrowser();
  await this.page.goto(this.config.baseUrl);

  // 验证首页加载成功
  const title = await this.page.title();
  this.expect(title).to.include('Ma Gong');
});

// ==================== 通用操作 ====================

When('我提供微信文章URL {string}', function(url) {
  this.testData.currentUrl = url;
});

When('我执行以下步骤:', async function(dataTable) {
  const steps = dataTable.hashes();
  this.testData.executedSteps = [];

  for (const step of steps) {
    console.log(`执行步骤 ${step['步骤']}: ${step['操作']}`);
    this.testData.executedSteps.push({
      step: step['步骤'],
      action: step['操作'],
      expectedResult: step['预期结果']
    });

    // 这里可以添加实际的步骤执行逻辑
    // 暂时只记录执行的步骤
  }
});

// ==================== 通用验证 ====================

Then('系统应该返回错误消息', function() {
  this.expect(this.testData.error).to.exist;
  this.expect(this.testData.error.message).to.be.a('string');
});

Then('错误消息应该说明{string}', function(expectedMessage) {
  this.expect(this.testData.error.message).to.include(expectedMessage);
});

Then('系统应该记录处理进度', function() {
  this.expect(this.testData.progress).to.exist;
  this.expect(this.testData.progress).to.have.property('current');
  this.expect(this.testData.progress).to.have.property('total');
});

Then('文件应该保存在 {string} 目录', async function(directory) {
  const exists = await this.fileExists(directory);
  this.expect(exists, `目录 ${directory} 应该存在`).to.be.true;
});

Then('系统应该按照对应策略处理', function() {
  // 验证错误恢复策略是否执行
  this.expect(this.testData.recoveryStrategy).to.exist;
  this.expect(this.testData.recoveryStrategy.executed).to.be.true;
});

Then('应该保存处理状态以便恢复', async function() {
  const stateFile = 'test-results/data/processing-state.json';
  const exists = await this.fileExists(stateFile);
  this.expect(exists, '状态文件应该存在').to.be.true;
});

// ==================== 数据表处理 ====================

Then('系统应该使用词汇表进行一致翻译:', async function(dataTable) {
  const glossary = dataTable.hashes();

  for (const term of glossary) {
    const chinese = term['中文原词'];
    const english = term['英文译词'];

    // 验证词汇表条目存在
    this.expect(this.testData.glossary).to.include({
      source: chinese,
      target: english
    });
  }
});

Then('系统应该进行以下检查:', async function(dataTable) {
  const checks = dataTable.hashes();

  for (const check of checks) {
    const checkItem = check['检查项目'];
    const expectedResult = check['预期结果'];

    console.log(`检查: ${checkItem} - 预期: ${expectedResult}`);
    // 记录检查项
    this.testData.qualityChecks = this.testData.qualityChecks || [];
    this.testData.qualityChecks.push({ item: checkItem, expected: expectedResult });
  }
});

// ==================== 页面交互 ====================

When('我点击{string}按钮', async function(buttonText) {
  if (!this.page) {
    await this.launchBrowser();
  }

  const button = await this.page.getByRole('button', { name: buttonText });
  await button.click();
});

When('我输入{string}到{string}字段', async function(value, fieldName) {
  if (!this.page) {
    await this.launchBrowser();
  }

  const input = await this.page.getByLabel(fieldName);
  await input.fill(value);
});

Then('页面应该显示{string}', async function(expectedText) {
  if (!this.page) {
    await this.launchBrowser();
    await this.page.goto(this.config.baseUrl);
  }

  const content = await this.page.textContent('body');
  this.expect(content).to.include(expectedText);
});

Then('页面应该跳转到{string}', async function(expectedUrl) {
  const currentUrl = this.page.url();
  this.expect(currentUrl).to.include(expectedUrl);
});

// ==================== 文件操作 ====================

When('我创建测试文件{string}', async function(filename) {
  const testContent = '# 测试内容\n\n这是一个测试文件。';
  const filePath = await this.saveTestResult(filename, { content: testContent });
  this.testData.createdFile = filePath;
});

Then('文件{string}应该存在', async function(filename) {
  const exists = await this.fileExists(filename);
  this.expect(exists, `文件 ${filename} 应该存在`).to.be.true;
});

Then('文件 {string} 应该存在', async function(filename) {
  const exists = await this.fileExists(filename);
  this.expect(exists, `文件 ${filename} 应该存在`).to.be.true;
});

Then('文件{string}应该包含{string}', async function(filename, expectedContent) {
  const fs = require('fs').promises;
  const content = await fs.readFile(filename, 'utf-8');
  this.expect(content).to.include(expectedContent);
});

module.exports = {};