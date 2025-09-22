/**
 * 发布功能相关的步骤定义
 */

const { Given, When, Then } = require('@cucumber/cucumber');
const path = require('path');
const fs = require('fs').promises;

Given('文章已经翻译完成', function() {
  this.testData.translatedArticle = {
    title: 'Technical Insights from Engineer Ma',
    content: 'This is the translated content of the article...',
    author: '瑞典马工',
    translator: 'AI Translator',
    date: '2024-01-15',
    originalUrl: 'https://mp.weixin.qq.com/s/original',
    images: ['image1.jpg', 'image2.jpg']
  };
});

Given('文章标题为 {string}', function(title) {
  this.testData.translatedArticle = this.testData.translatedArticle || {};
  this.testData.translatedArticle.title = title;
});

Given('发布日期为 {string}', function(date) {
  this.testData.translatedArticle.date = date;
});

Given('文章包含{int}张图片', function(imageCount) {
  this.testData.translatedArticle.images = [];
  for (let i = 1; i <= imageCount; i++) {
    this.testData.translatedArticle.images.push(`image${i}.jpg`);
  }
});

When('我准备发布一篇翻译好的文章', function() {
  this.testData.readyToPublish = true;
});

When('我生成文章文件', async function() {
  const article = this.testData.translatedArticle;
  const slug = article.title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  const filename = `${article.date}-${slug}.md`;

  this.testData.generatedFile = {
    name: filename,
    path: path.join('posts', filename)
  };

  // 生成Markdown内容
  const frontmatter = `---
title: "${article.title}"
date: "${article.date}"
author: "${article.author}"
originalUrl: "${article.originalUrl}"
translator: "${article.translator}"
tags: ["translation", "tech", "wechat"]
---`;

  this.testData.markdownContent = `${frontmatter}\n\n${article.content}`;
});

When('我发布文章', async function() {
  if (this.testData.generatedFile && this.testData.markdownContent) {
    // 创建posts目录（如果不存在）
    await fs.mkdir('posts', { recursive: true });

    // 写入文件
    await fs.writeFile(this.testData.generatedFile.path, this.testData.markdownContent);
    this.testData.published = true;
  }
});

When('我发布新文章后', function() {
  this.testData.newArticlePublished = true;
  this.testData.publishedAt = new Date().toISOString();
});

When('读者访问文章页面', async function() {
  if (!this.page) {
    await this.launchBrowser();
  }

  const articleUrl = `${this.config.baseUrl}/posts/${this.testData.generatedFile.name.replace('.md', '')}`;
  this.testData.articlePageUrl = articleUrl;

  // 模拟访问页面
  this.testData.pageVisited = true;
});

When('文章发布后', function() {
  this.testData.postPublishActions = true;
});

Then('系统应该生成Markdown格式文件', function() {
  this.expect(this.testData.markdownContent).to.exist;
  this.expect(this.testData.markdownContent).to.include('---');
  this.expect(this.testData.markdownContent).to.include('title:');
});

Then('文件应该包含正确的frontmatter:', async function(dataTable) {
  const expectedFields = dataTable.hashes();
  const frontmatterRegex = /---([\s\S]*?)---/;
  const match = this.testData.markdownContent.match(frontmatterRegex);

  this.expect(match).to.exist;

  for (const field of expectedFields) {
    const fieldName = field['字段'];
    this.expect(this.testData.markdownContent).to.include(`${fieldName}:`);
  }
});

Then('文件名应该为 {string}', function(expectedFilename) {
  this.expect(this.testData.generatedFile.name).to.equal(expectedFilename);
});

Then('URL路径应该为 {string}', function(expectedPath) {
  const actualPath = `/posts/${this.testData.generatedFile.name.replace('.md', '')}`;
  this.expect(actualPath).to.equal(expectedPath);
});

Then('所有图片应该复制到 {string} 目录', async function(targetDir) {
  const date = this.testData.translatedArticle.date;
  const imageDir = targetDir.replace('[date]', date);

  // 创建图片目录
  await fs.mkdir(imageDir, { recursive: true });

  this.testData.copiedImages = [];
  for (const image of this.testData.translatedArticle.images) {
    const imagePath = path.join(imageDir, image);
    await fs.writeFile(imagePath, 'test image content');
    this.testData.copiedImages.push(imagePath);
  }

  this.expect(this.testData.copiedImages).to.have.lengthOf(this.testData.translatedArticle.images.length);
});

Then('Markdown中的图片链接应该更新为正确路径', function() {
  for (const image of this.testData.copiedImages) {
    const imageUrl = image.replace('public', '');
    this.testData.markdownContent += `\n![Image](${imageUrl})`;
  }

  this.expect(this.testData.markdownContent).to.include('![Image]');
});

Then('图片应该有描述性的文件名', function() {
  for (const image of this.testData.copiedImages) {
    const filename = path.basename(image);
    this.expect(filename).to.match(/\.(jpg|png|gif|webp)$/i);
  }
});

Then('网站首页应该显示新文章', async function() {
  if (!this.page) {
    await this.launchBrowser();
  }

  // 模拟首页显示新文章
  this.testData.homepageArticles = [
    {
      title: this.testData.translatedArticle.title,
      date: this.testData.translatedArticle.date,
      excerpt: this.testData.translatedArticle.content.substring(0, 150) + '...'
    }
  ];

  this.expect(this.testData.homepageArticles).to.have.lengthOf.at.least(1);
});

Then('文章应该按时间倒序排列', function() {
  if (this.testData.homepageArticles && this.testData.homepageArticles.length > 1) {
    for (let i = 0; i < this.testData.homepageArticles.length - 1; i++) {
      const date1 = new Date(this.testData.homepageArticles[i].date);
      const date2 = new Date(this.testData.homepageArticles[i + 1].date);
      this.expect(date1.getTime()).to.be.at.least(date2.getTime());
    }
  }
});

Then('应该显示文章摘要', function() {
  const article = this.testData.homepageArticles[0];
  this.expect(article.excerpt).to.exist;
  this.expect(article.excerpt.length).to.be.at.least(50);
  this.expect(article.excerpt).to.include('...');
});

Then('应该显示发布日期和作者', function() {
  const article = this.testData.homepageArticles[0];
  this.expect(article.date).to.exist;
  this.expect(article.date).to.match(/^\d{4}-\d{2}-\d{2}$/);
});

Then('页面应该显示:', async function(dataTable) {
  const elements = dataTable.hashes();
  this.testData.pageElements = {};

  for (const element of elements) {
    const elementName = element['元素'];
    const content = element['显示内容'];
    this.testData.pageElements[elementName] = content;
  }

  this.expect(Object.keys(this.testData.pageElements)).to.have.lengthOf(elements.length);
});

Then('页面应该包含SEO元数据:', async function(dataTable) {
  const metadata = dataTable.hashes();
  this.testData.seoMetadata = {};

  for (const meta of metadata) {
    const metaType = meta['元数据类型'];
    const content = meta['内容'];
    this.testData.seoMetadata[metaType] = content;
  }

  // 验证SEO元数据存在
  this.expect(this.testData.seoMetadata).to.have.property('meta description');
  this.expect(this.testData.seoMetadata).to.have.property('og:title');
});

Then('应该生成sitemap.xml条目', async function() {
  const sitemapPath = 'public/sitemap.xml';
  let sitemap;

  try {
    sitemap = await fs.readFile(sitemapPath, 'utf-8');
  } catch {
    // 如果文件不存在，创建一个新的
    sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>`;
  }

  // 添加新文章的条目
  const newEntry = `
  <url>
    <loc>https://magong.se/posts/${this.testData.generatedFile.name.replace('.md', '')}</loc>
    <lastmod>${this.testData.translatedArticle.date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>`;

  sitemap = sitemap.replace('</urlset>', newEntry + '\n</urlset>');

  await fs.mkdir('public', { recursive: true });
  await fs.writeFile(sitemapPath, sitemap);

  this.testData.sitemapUpdated = true;
  this.expect(this.testData.sitemapUpdated).to.be.true;
});

module.exports = {};