// SEO配置和工具函数

export const siteConfig = {
  url: process.env.NEXT_PUBLIC_SITE_URL || 'https://magong.se',
  title: '瑞典马工 - Swedish Ma Gong',
  description: '瑞典生活经验分享，为海外华人提供实用的瑞典生活指南、文化介绍和经验分享',
  author: '瑞典马工',
  language: 'zh-CN',
  locale: 'zh_CN',
  twitter: '@magong_se',
  keywords: [
    '瑞典生活',
    '瑞典工作',
    '瑞典移民',
    '瑞典留学',
    '斯德哥尔摩',
    '北欧生活',
    '海外华人',
    '瑞典文化',
    'Swedish life',
    'Living in Sweden',
  ],
  ogImage: '/og-image.jpg',
  twitterImage: '/twitter-image.jpg',
}

// 生成JSON-LD结构化数据
export function generateArticleSchema({
  title,
  description,
  author,
  datePublished,
  dateModified,
  image,
  url,
  keywords,
}: {
  title: string
  description: string
  author?: string
  datePublished: string
  dateModified?: string
  image?: string
  url: string
  keywords?: string[]
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: title,
    description: description,
    author: {
      '@type': 'Person',
      name: author || siteConfig.author,
    },
    datePublished: datePublished,
    dateModified: dateModified || datePublished,
    publisher: {
      '@type': 'Organization',
      name: siteConfig.title,
      logo: {
        '@type': 'ImageObject',
        url: `${siteConfig.url}/logo.png`,
      },
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': url,
    },
    image: image ? `${siteConfig.url}${image}` : `${siteConfig.url}${siteConfig.ogImage}`,
    keywords: keywords?.join(', '),
  }
}

// 生成网站Schema
export function generateWebSiteSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    url: siteConfig.url,
    name: siteConfig.title,
    description: siteConfig.description,
    publisher: {
      '@type': 'Organization',
      name: siteConfig.title,
    },
    potentialAction: {
      '@type': 'SearchAction',
      target: `${siteConfig.url}/search?q={search_term_string}`,
      'query-input': 'required name=search_term_string',
    },
  }
}

// 生成BreadcrumbList Schema
export function generateBreadcrumbSchema(items: { name: string; url: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: `${siteConfig.url}${item.url}`,
    })),
  }
}

// 生成组织Schema
export function generateOrganizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: siteConfig.title,
    url: siteConfig.url,
    logo: `${siteConfig.url}/logo.png`,
    sameAs: [
      'https://twitter.com/magong_se',
      'https://www.facebook.com/magong.se',
      'https://www.instagram.com/magong_se',
    ],
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'customer service',
      availableLanguage: ['Chinese', 'Swedish', 'English'],
    },
  }
}

// 处理和优化元描述
export function processMetaDescription(description?: string, content?: string): string {
  if (description) {
    return description.substring(0, 160)
  }
  if (content) {
    // 移除Markdown语法并截取
    const cleanContent = content
      .replace(/#{1,6}\s/g, '') // 移除标题
      .replace(/\*\*/g, '') // 移除粗体
      .replace(/\*/g, '') // 移除斜体
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // 移除链接
      .replace(/\n+/g, ' ') // 替换换行
      .trim()
    return cleanContent.substring(0, 160)
  }
  return siteConfig.description
}

// 生成完整的页面URL
export function generatePageUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${siteConfig.url}${cleanPath}`
}
