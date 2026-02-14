#!/usr/bin/env node

// 批量处理现有文章的SEO元数据增强脚本

const fs = require('fs')
const path = require('path')
// 使用相对路径导入
const matter = require(path.join(process.cwd(), 'node_modules', 'gray-matter'))

const postsDirectory = path.join(process.cwd(), 'posts')

// SEO增强配置
const seoEnhancements = {
  // 默认描述长度
  descriptionLength: 160,

  // 关键词映射
  keywordMapping: {
    斯德哥尔摩: ['Stockholm', '瑞典首都', 'Swedish capital'],
    瑞典: ['Sweden', 'Sverige', '北欧'],
    生活: ['life', 'living', '日常'],
    工作: ['work', 'career', '职业'],
    教育: ['education', 'school', '学习'],
    医疗: ['healthcare', 'medical', '健康'],
    房产: ['housing', 'real estate', '住房'],
    文化: ['culture', 'tradition', '传统'],
  },

  // 分类到标签的映射
  categoryTags: {
    生活: ['瑞典生活', '海外生活', '北欧生活'],
    工作: ['瑞典工作', '职场文化', '工作签证'],
    教育: ['瑞典教育', '留学瑞典', '教育体系'],
    文化: ['瑞典文化', '北欧文化', '文化差异'],
    科技: ['科技创新', '创业', '技术'],
    环保: ['可持续发展', '环保', '绿色生活'],
  },
}

// 生成描述文本
function generateDescription(content, existingDescription) {
  if (existingDescription && existingDescription.length >= 100) {
    return existingDescription.substring(0, seoEnhancements.descriptionLength)
  }

  // 从内容中提取描述
  const cleanContent = content
    .replace(/^#+\s.+$/gm, '') // 移除标题
    .replace(/!\[.*?\]\(.*?\)/g, '') // 移除图片
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // 移除链接
    .replace(/[*_~`]/g, '') // 移除格式符号
    .replace(/\n+/g, ' ') // 替换换行
    .trim()

  const firstParagraph = cleanContent.match(/^[^。！？]{50,}[。！？]/)
  if (firstParagraph) {
    return firstParagraph[0].substring(0, seoEnhancements.descriptionLength)
  }

  return cleanContent.substring(0, seoEnhancements.descriptionLength) + '...'
}

// 增强标签
function enhanceTags(existingTags = [], title = '', category = '') {
  const tags = new Set(existingTags)

  // 添加分类相关标签
  if (category && seoEnhancements.categoryTags[category]) {
    seoEnhancements.categoryTags[category].forEach((tag) => tags.add(tag))
  }

  // 从标题中提取关键词
  Object.keys(seoEnhancements.keywordMapping).forEach((keyword) => {
    if (title.includes(keyword)) {
      tags.add(keyword)
      // 添加相关的英文标签
      seoEnhancements.keywordMapping[keyword].forEach((relatedTag) => {
        if (tags.size < 10) {
          // 限制标签数量
          tags.add(relatedTag)
        }
      })
    }
  })

  return Array.from(tags).slice(0, 10) // 最多10个标签
}

// 生成excerpt（摘要）
function generateExcerpt(content, description) {
  if (description) {
    return description
  }

  const cleanContent = content
    .replace(/^#+\s.+$/gm, '') // 移除标题
    .replace(/!\[.*?\]\(.*?\)/g, '') // 移除图片
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // 移除链接
    .replace(/[*_~`]/g, '') // 移除格式符号
    .replace(/\n+/g, ' ') // 替换换行
    .trim()

  return cleanContent.substring(0, 200) + '...'
}

// 处理单个文章文件
function processPost(filePath) {
  const fileContents = fs.readFileSync(filePath, 'utf8')
  const { data, content } = matter(fileContents)

  // 记录原始数据
  const originalData = { ...data }

  // 增强元数据
  const enhancedData = {
    ...data,
    // 确保有标题
    title: data.title || path.basename(filePath, '.md'),

    // 确保有日期
    date: data.date || new Date().toISOString().split('T')[0],

    // 生成或优化描述
    description: generateDescription(content, data.description),

    // 生成摘要
    excerpt: data.excerpt || generateExcerpt(content, data.description),

    // 增强标签
    tags: enhanceTags(data.tags, data.title, data.category),

    // 确保有作者
    author: data.author || '瑞典马工',

    // 添加更新时间
    lastModified: data.lastModified || data.date || new Date().toISOString().split('T')[0],
  }

  // 检查是否有变化
  const hasChanges = JSON.stringify(originalData) !== JSON.stringify(enhancedData)

  if (hasChanges) {
    // 更新文件
    const newContent = matter.stringify(content, enhancedData)
    fs.writeFileSync(filePath, newContent)
    return { filePath, status: 'updated', changes: enhancedData }
  }

  return { filePath, status: 'unchanged' }
}

// 主函数
function main() {
  console.log('开始批量处理文章SEO元数据...\n')

  // 确保posts目录存在
  if (!fs.existsSync(postsDirectory)) {
    console.error('错误：posts目录不存在')
    process.exit(1)
  }

  // 获取所有markdown文件
  const files = fs.readdirSync(postsDirectory).filter((file) => file.endsWith('.md'))

  if (files.length === 0) {
    console.log('没有找到任何文章文件')
    return
  }

  console.log(`找到 ${files.length} 篇文章\n`)

  const results = {
    updated: [],
    unchanged: [],
    errors: [],
  }

  // 处理每个文件
  files.forEach((file) => {
    const filePath = path.join(postsDirectory, file)
    console.log(`处理: ${file}`)

    try {
      const result = processPost(filePath)

      if (result.status === 'updated') {
        results.updated.push(file)
        console.log(`  ✓ 已更新`)

        // 显示主要变化
        if (result.changes) {
          if (result.changes.description) {
            console.log(`    - 添加/更新描述`)
          }
          if (result.changes.tags && result.changes.tags.length > 0) {
            console.log(`    - 标签: ${result.changes.tags.join(', ')}`)
          }
        }
      } else {
        results.unchanged.push(file)
        console.log(`  - 无需更新`)
      }
    } catch (error) {
      results.errors.push({ file, error: error.message })
      console.error(`  ✗ 错误: ${error.message}`)
    }

    console.log()
  })

  // 显示汇总
  console.log('\n处理完成！')
  console.log('================')
  console.log(`✓ 更新: ${results.updated.length} 篇`)
  console.log(`- 未变: ${results.unchanged.length} 篇`)
  console.log(`✗ 错误: ${results.errors.length} 篇`)

  if (results.updated.length > 0) {
    console.log('\n已更新的文章:')
    results.updated.forEach((file) => console.log(`  - ${file}`))
  }

  if (results.errors.length > 0) {
    console.log('\n处理失败的文章:')
    results.errors.forEach(({ file, error }) => {
      console.log(`  - ${file}: ${error}`)
    })
  }

  // 生成报告文件
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: files.length,
      updated: results.updated.length,
      unchanged: results.unchanged.length,
      errors: results.errors.length,
    },
    files: {
      updated: results.updated,
      unchanged: results.unchanged,
      errors: results.errors,
    },
  }

  const reportPath = path.join(process.cwd(), 'seo-enhancement-report.json')
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2))
  console.log(`\n报告已保存到: ${reportPath}`)
}

// 运行脚本
if (require.main === module) {
  main()
}
