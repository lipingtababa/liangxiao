// SEO configuration and utility functions

export const siteConfig = {
  url: process.env.NEXT_PUBLIC_SITE_URL || 'https://magong.se',
  title: 'MaGong',
  description: 'Insights on AI, coding, and tech from a software engineer perspective',
  author: 'MaGong',
  language: 'en-US',
  locale: 'en_US',
  twitter: '@magong_se',
  keywords: [
    'AI Coding',
    'Software Engineering',
    'LLM',
    'AI Development',
    'Programming',
    'Tech Insights',
    'AI Tools',
    'Development Practices',
    'Software Quality',
    'Team Building',
  ],
  ogImage: '/og-image.jpg',
  twitterImage: '/twitter-image.jpg',
}

// Generate JSON-LD structured data
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

// Generate Website Schema
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

// Generate BreadcrumbList Schema
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

// Generate Organization Schema
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

// Process and optimize meta description
export function processMetaDescription(description?: string, content?: string): string {
  if (description) {
    return description.substring(0, 160)
  }
  if (content) {
    // Remove Markdown syntax and truncate
    const cleanContent = content
      .replace(/#{1,6}\s/g, '') // Remove headings
      .replace(/\*\*/g, '') // Remove bold
      .replace(/\*/g, '') // Remove italic
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links
      .replace(/\n+/g, ' ') // Replace line breaks
      .trim()
    return cleanContent.substring(0, 160)
  }
  return siteConfig.description
}

// Generate complete page URL
export function generatePageUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${siteConfig.url}${cleanPath}`
}
