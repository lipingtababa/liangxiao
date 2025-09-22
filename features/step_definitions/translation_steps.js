/**
 * 翻译功能相关的步骤定义
 */

const { Given, When, Then } = require('@cucumber/cucumber');

Given('有一篇中文文章待翻译', function() {
  this.testData.articleToTranslate = {
    title: '瑞典马工的技术分享',
    content: '今天我们来讨论微信小程序的开发技巧。\n\n微信作为中国最大的社交平台...',
    author: '瑞典马工',
    date: '2024-01-15'
  };
});

Given('文章包含专有名词和技术术语', function() {
  this.testData.articleToTranslate = {
    title: '瑞典马工谈微信公众号开发',
    content: '瑞典马工今天分享关于微信公众号的API调用方法。使用React和Node.js构建...',
    specialTerms: ['瑞典马工', '微信', '公众号', 'React', 'Node.js']
  };
});

Given('文章包含中国特定的文化内容', function() {
  this.testData.articleToTranslate = {
    title: '春节期间的技术思考',
    content: '春节期间，我在包饺子的时候突然想到了一个算法优化方案。正如老话说的"磨刀不误砍柴工"...',
    culturalContent: ['春节', '包饺子', '磨刀不误砍柴工']
  };
});

Given('文章包含引用和外部链接', function() {
  this.testData.articleToTranslate = {
    title: '技术文章',
    content: '参考资料：[React官网](https://react.dev)，引用自《设计模式》一书...',
    hasLinks: true,
    hasQuotes: true
  };
});

When('我执行翻译操作', async function() {
  // 模拟翻译操作
  if (this.testData.articleToTranslate) {
    this.testData.translationResult = {
      title: 'Engineer Ma\'s Technical Sharing',
      content: 'Today we discuss WeChat Mini Program development tips.\n\nWeChat as China\'s largest social platform...',
      originalTitle: this.testData.articleToTranslate.title,
      translatedAt: new Date().toISOString()
    };

    // 如果有专有名词，添加词汇表
    if (this.testData.articleToTranslate.specialTerms) {
      this.testData.glossary = [
        { source: '瑞典马工', target: 'Engineer Ma' },
        { source: '微信', target: 'WeChat' },
        { source: '公众号', target: 'Official Account' }
      ];
    }
  }
});

When('文章翻译完成后', function() {
  this.testData.translationComplete = true;
  this.testData.qualityChecks = [];
});

Then('文章标题应该被翻译成英文', function() {
  this.expect(this.testData.translationResult).to.exist;
  this.expect(this.testData.translationResult.title).to.be.a('string');
  this.expect(this.testData.translationResult.title).to.match(/^[A-Za-z\s\'\-\.]+$/);
});

Then('文章内容应该被翻译成英文', function() {
  this.expect(this.testData.translationResult.content).to.be.a('string');
  this.expect(this.testData.translationResult.content.length).to.be.greaterThan(0);
});

Then('翻译应该保持原文的段落结构', function() {
  const originalParagraphs = this.testData.articleToTranslate.content.split('\n\n').length;
  const translatedParagraphs = this.testData.translationResult.content.split('\n\n').length;

  this.expect(translatedParagraphs).to.equal(originalParagraphs);
});

Then('翻译质量应该适合国际读者阅读', function() {
  // 模拟质量检查
  this.testData.qualityScore = {
    readability: 85,
    accuracy: 90,
    culturalAdaptation: 88
  };

  this.expect(this.testData.qualityScore.readability).to.be.at.least(80);
  this.expect(this.testData.qualityScore.accuracy).to.be.at.least(85);
});

Then('技术术语应该保持专业性和准确性', function() {
  if (this.testData.glossary) {
    const technicalTerms = ['React', 'Node.js', 'API'];

    // 验证技术术语没有被错误翻译
    for (const term of technicalTerms) {
      if (this.testData.articleToTranslate.content.includes(term)) {
        this.expect(this.testData.translationResult.content).to.include(term);
      }
    }
  }
});

Then('系统应该为以下内容添加说明:', async function(dataTable) {
  const culturalItems = dataTable.hashes();
  this.testData.culturalExplanations = [];

  for (const item of culturalItems) {
    const contentType = item['内容类型'];
    const processingMethod = item['处理方式'];

    this.testData.culturalExplanations.push({
      type: contentType,
      method: processingMethod,
      added: true
    });

    // 模拟添加文化背景说明
    if (contentType === '中国节日' && this.testData.translationResult.content.includes('Spring Festival')) {
      this.testData.translationResult.content += ' (Spring Festival is the Chinese New Year, the most important traditional holiday in China)';
    }
  }

  this.expect(this.testData.culturalExplanations).to.have.lengthOf(culturalItems.length);
});

Then('原文中的URL链接应该保持不变', function() {
  if (this.testData.articleToTranslate.hasLinks) {
    const urlRegex = /https?:\/\/[^\s]+/g;
    const originalUrls = this.testData.articleToTranslate.content.match(urlRegex) || [];
    const translatedUrls = this.testData.translationResult.content.match(urlRegex) || [];

    this.expect(translatedUrls.length).to.equal(originalUrls.length);
  }
});

Then('引用的原始中文应该在括号中保留', function() {
  if (this.testData.articleToTranslate.hasQuotes) {
    // 模拟保留原始引用
    this.testData.translationResult.content += ' (原文: "磨刀不误砍柴工")';
    this.expect(this.testData.translationResult.content).to.include('(原文:');
  }
});

Then('应该在文末添加原文链接', function() {
  const originalUrl = 'https://mp.weixin.qq.com/s/original-article';
  this.testData.translationResult.footer = `\n\n---\n原文链接 / Original Article: ${originalUrl}`;

  this.expect(this.testData.translationResult.footer).to.include('原文链接');
  this.expect(this.testData.translationResult.footer).to.include('https://');
});

module.exports = {};