import { getPostData, getAllPostIds, PostData } from '@/lib/posts'
import { format } from 'date-fns'
import { enUS, zhCN } from 'date-fns/locale'
import Link from 'next/link'
import { Metadata } from 'next'
import MarkdownRenderer from '@/components/MarkdownRenderer'
import SocialShare from '@/components/SocialShare'
import ImageWithFallback from '@/components/ImageWithFallback'
import {
  generateArticleSchema,
  generateBreadcrumbSchema,
  processMetaDescription,
  generatePageUrl,
  siteConfig,
} from '@/lib/seo'
import Script from 'next/script'

export async function generateStaticParams() {
  const posts = getAllPostIds()
  return posts.map((post) => ({
    id: post.params.id,
  }))
}

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const postData = getPostData(params.id)
  const description = processMetaDescription(postData.description, postData.content)
  const url = generatePageUrl(`/posts/${params.id}`)
  const imageUrl = postData.image
    ? `${siteConfig.url}${postData.image}`
    : `${siteConfig.url}${siteConfig.ogImage}`

  return {
    title: postData.title,
    description: description,
    keywords: postData.tags,
    authors: postData.author ? [{ name: postData.author }] : [{ name: siteConfig.author }],
    openGraph: {
      title: postData.title,
      description: description,
      type: 'article',
      publishedTime: postData.date,
      modifiedTime: postData.date,
      authors: postData.author ? [postData.author] : [siteConfig.author],
      tags: postData.tags,
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: postData.title,
        },
      ],
      url: url,
      siteName: siteConfig.title,
      locale: siteConfig.locale,
    },
    twitter: {
      card: 'summary_large_image',
      title: postData.title,
      description: description,
      images: [imageUrl],
      site: siteConfig.twitter,
      creator: siteConfig.twitter,
    },
    alternates: {
      canonical: url,
    },
    robots: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
      'max-snippet': -1,
      'max-video-preview': -1,
    },
  }
}

export default async function PostPage({ params }: { params: { id: string } }) {
  const postData = getPostData(params.id)

  // Generate structured data
  const articleSchema = generateArticleSchema({
    title: postData.title,
    description: processMetaDescription(postData.description, postData.content),
    author: postData.author,
    datePublished: postData.date,
    image: postData.image,
    url: generatePageUrl(`/posts/${params.id}`),
    keywords: postData.tags,
  })

  const breadcrumbSchema = generateBreadcrumbSchema([
    { name: 'Home', url: '/' },
    { name: 'Articles', url: '/posts' },
    { name: postData.title, url: `/posts/${params.id}` },
  ])

  return (
    <article className="min-h-screen bg-gray-50">
      <Script
        id="article-schema"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />
      <Script
        id="breadcrumb-schema"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back button */}
        <Link
          href="/posts"
          className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-8"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Articles
        </Link>

        {/* Article header */}
        <header className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            {postData.category && (
              <span className="inline-block px-3 py-1 text-sm font-medium text-blue-600 bg-blue-100 rounded-full">
                {postData.category}
              </span>
            )}
            {postData.date && (
              <time className="text-gray-500" dateTime={postData.date}>
                {(() => {
                  try {
                    const date = new Date(postData.date)
                    if (isNaN(date.getTime())) {
                      return postData.date // 返回原始字符串如果日期无效
                    }
                    return format(date, 'yyyy年MM月dd日', { locale: zhCN })
                  } catch {
                    return postData.date // 如果格式化失败，返回原始字符串
                  }
                })()}
              </time>
            )}
          </div>

          <h1 className="text-4xl font-bold text-gray-900 mb-4">{postData.title}</h1>

          {postData.author && <p className="text-gray-600">By {postData.author}</p>}

          {postData.tags && postData.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4">
              {postData.tags.map((tag: string) => (
                <span
                  key={tag}
                  className="text-sm px-3 py-1 text-gray-600 bg-gray-100 rounded-full"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </header>

        {/* Cover image */}
        {postData.image && (
          <div className="mb-8">
            <ImageWithFallback
              src={postData.image}
              alt={postData.title}
              width={1200}
              height={630}
              className="w-full"
              priority
            />
          </div>
        )}

        {/* Article content */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          <MarkdownRenderer content={postData.content || ''} />
        </div>

        {/* Social sharing */}
        <div className="mt-8 p-6 bg-white rounded-lg shadow-sm">
          <SocialShare
            title={postData.title}
            url={typeof window !== 'undefined' ? window.location.href : ''}
          />
        </div>

        {/* Original link */}
        {postData.originalUrl && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-600">
              Original article:
              <a
                href={postData.originalUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline ml-1"
              >
                {postData.originalUrl}
              </a>
            </p>
          </div>
        )}

        {/* Bottom navigation */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <Link
            href="/posts"
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Articles
          </Link>
        </div>
      </div>
    </article>
  )
}
