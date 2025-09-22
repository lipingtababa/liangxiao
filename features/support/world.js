/**
 * Cucumber World - 测试环境配置
 * 提供测试上下文和共享工具
 */

const { setWorldConstructor, After, Before, BeforeAll, AfterAll } = require('@cucumber/cucumber');
const { chromium } = require('playwright');
const chai = require('chai');
const fs = require('fs').promises;
const path = require('path');

class CustomWorld {
  constructor(options) {
    // Handle both old and new Cucumber API
    if (options && options.attach) {
      this.attach = options.attach;
    }

    this.expect = chai.expect;
    this.testData = {};
    this.browser = null;
    this.page = null;
    this.context = null;

    // 测试配置
    this.config = {
      baseUrl: process.env.BASE_URL || 'http://localhost:3000',
      apiUrl: process.env.API_URL || 'http://localhost:3000/api',
      screenshotDir: 'test-results/screenshots',
      timeout: 30000,
      headless: process.env.HEADLESS !== 'false'
    };

    // 测试数据目录
    this.testDataDir = path.join(__dirname, '..', 'test-data');
  }

  /**
   * 启动浏览器
   */
  async launchBrowser() {
    if (!this.browser) {
      this.browser = await chromium.launch({
        headless: this.config.headless,
        slowMo: process.env.SLOW_MO ? parseInt(process.env.SLOW_MO) : 0
      });
    }
    this.context = await this.browser.newContext({
      viewport: { width: 1280, height: 720 },
      ignoreHTTPSErrors: true,
      locale: 'zh-CN'
    });
    this.page = await this.context.newPage();
  }

  /**
   * 关闭浏览器
   */
  async closeBrowser() {
    if (this.page) await this.page.close();
    if (this.context) await this.context.close();
    if (this.browser) await this.browser.close();
    this.page = null;
    this.context = null;
    this.browser = null;
  }

  /**
   * 截图并附加到报告
   */
  async takeScreenshot(name) {
    if (this.page) {
      const screenshotPath = path.join(this.config.screenshotDir, `${name}-${Date.now()}.png`);
      await fs.mkdir(path.dirname(screenshotPath), { recursive: true });
      const screenshot = await this.page.screenshot({ path: screenshotPath, fullPage: true });
      this.attach(screenshot, 'image/png');
      return screenshotPath;
    }
  }

  /**
   * 等待并获取元素
   */
  async waitForElement(selector, options = {}) {
    const timeout = options.timeout || this.config.timeout;
    return await this.page.waitForSelector(selector, { timeout, ...options });
  }

  /**
   * 执行Python脚本
   */
  async executePythonScript(scriptName, args = []) {
    const { exec } = require('child_process');
    const util = require('util');
    const execPromise = util.promisify(exec);

    const scriptPath = path.join(process.cwd(), 'scripts', scriptName);
    const command = `python3 ${scriptPath} ${args.join(' ')}`;

    try {
      const { stdout, stderr } = await execPromise(command);
      if (stderr && !stderr.includes('WARNING')) {
        console.error('Python script stderr:', stderr);
      }
      return stdout;
    } catch (error) {
      console.error('Python script error:', error);
      throw error;
    }
  }

  /**
   * 读取测试数据文件
   */
  async loadTestData(filename) {
    const filePath = path.join(this.testDataDir, filename);
    const content = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(content);
  }

  /**
   * 保存测试结果
   */
  async saveTestResult(filename, data) {
    const resultDir = path.join(process.cwd(), 'test-results', 'data');
    await fs.mkdir(resultDir, { recursive: true });
    const filePath = path.join(resultDir, filename);
    await fs.writeFile(filePath, JSON.stringify(data, null, 2));
    return filePath;
  }

  /**
   * 验证文件存在
   */
  async fileExists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * 清理测试文件
   */
  async cleanupTestFiles(pattern) {
    const glob = require('glob');
    const files = glob.sync(pattern);
    for (const file of files) {
      await fs.unlink(file).catch(() => {});
    }
  }
}

setWorldConstructor(CustomWorld);

// 全局钩子
BeforeAll(async function() {
  console.log('🚀 开始运行验收测试...');
  // 确保测试目录存在
  await fs.mkdir('test-results', { recursive: true });
  await fs.mkdir('test-results/screenshots', { recursive: true });
});

AfterAll(async function() {
  console.log('✅ 验收测试完成');
});

// 场景钩子
Before(async function(scenario) {
  console.log(`📝 场景: ${scenario.pickle.name}`);
  this.scenarioName = scenario.pickle.name;
});

After(async function(scenario) {
  if (scenario.result.status === 'FAILED') {
    // 失败时自动截图
    if (this.page) {
      await this.takeScreenshot(`failed-${this.scenarioName}`);
    }
    console.log(`❌ 场景失败: ${this.scenarioName}`);
  } else {
    console.log(`✅ 场景通过: ${this.scenarioName}`);
  }

  // 清理浏览器
  await this.closeBrowser();
});

module.exports = CustomWorld;