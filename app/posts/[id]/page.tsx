import { getPostData, getAllPostIds, PostData } from '@/lib/posts'
import { format } from 'date-fns'
import Link from 'next/link'
import { Metadata } from 'next'
import MarkdownRenderer from '@/components/MarkdownRenderer'
import ImageWithFallback from '@/components/ImageWithFallback'
import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
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

export async function generateMetadata({
  params
}: {
  params: { id: string }
}): Promise<Metadata> {
  const { id } = params
  console.log('[generateMetadata] Called with id:', id)

  // Load the post data directly
  let postData: PostData
  try {
    const postsDirectory = path.join(process.cwd(), 'posts')
    const fullPath = path.join(postsDirectory, `${id}.md`)

    if (fs.existsSync(fullPath)) {
      const fileContents = fs.readFileSync(fullPath, 'utf8')
      const matterResult = matter(fileContents)

      const stats = fs.statSync(fullPath)
      const fallbackDate = stats.mtime.toISOString().split('T')[0]

      postData = {
        id,
        title: matterResult.data.title || '',
        date: matterResult.data.date || fallbackDate,
        author: matterResult.data.author,
        category: matterResult.data.category,
        tags: matterResult.data.tags,
        description: matterResult.data.description,
        image: matterResult.data.image,
        originalUrl: matterResult.data.originalUrl,
        content: matterResult.content || '',
        contentHtml: matterResult.content || '',
      }
    } else {
      postData = {
        id,
        title: 'Post Not Found',
        date: new Date().toISOString().split('T')[0],
        content: 'The post you are looking for does not exist.',
      }
    }
  } catch (error) {
    postData = {
      id,
      title: 'Error Loading Post',
      date: new Date().toISOString().split('T')[0],
      content: `Error: ${error}`,
    }
  }

  console.log('[generateMetadata] Got postData:', { title: postData?.title })
  const description = processMetaDescription(postData.description, postData.content)
  const url = generatePageUrl(`/posts/${id}`)
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

export default function PostPage({
  params
}: {
  params: { id: string }
}) {
  const { id } = params
  console.log('[PostPage] Rendering post with id:', id)
  console.log('[PostPage] getPostData function:', typeof getPostData)

  // Load the post data directly
  let postData: PostData
  try {
    console.log('[PostPage] Loading post directly with id:', id)

    const postsDirectory = path.join(process.cwd(), 'posts')
    const fullPath = path.join(postsDirectory, `${id}.md`)

    if (fs.existsSync(fullPath)) {
      const fileContents = fs.readFileSync(fullPath, 'utf8')
      const matterResult = matter(fileContents)

      const stats = fs.statSync(fullPath)
      const fallbackDate = stats.mtime.toISOString().split('T')[0]

      postData = {
        id,
        title: matterResult.data.title || '',
        date: matterResult.data.date || fallbackDate,
        author: matterResult.data.author,
        category: matterResult.data.category,
        tags: matterResult.data.tags,
        description: matterResult.data.description,
        image: matterResult.data.image,
        originalUrl: matterResult.data.originalUrl,
        content: matterResult.content || '',
        contentHtml: matterResult.content || '',
      }

      console.log('[PostPage] Post loaded successfully:', {
        title: postData.title,
        contentLength: postData.content?.length
      })
    } else {
      console.error('[PostPage] Post file not found:', fullPath)
      postData = {
        id,
        title: 'Post Not Found',
        date: new Date().toISOString().split('T')[0],
        content: 'The post you are looking for does not exist.',
      }
    }
  } catch (error) {
    console.error('[PostPage] Error loading post:', error)
    postData = {
      id,
      title: 'Error Loading Post',
      date: new Date().toISOString().split('T')[0],
      content: `Error: ${error}`,
    }
  }

  console.log('[PostPage] PostData loaded:', { title: postData.title, hasContent: !!postData.content, contentLength: postData.content?.length })

  // Generate structured data
  const articleSchema = generateArticleSchema({
    title: postData.title,
    description: processMetaDescription(postData.description, postData.content),
    author: postData.author,
    datePublished: postData.date,
    image: postData.image,
    url: generatePageUrl(`/posts/${id}`),
    keywords: postData.tags,
  })

  const breadcrumbSchema = generateBreadcrumbSchema([
    { name: 'Home', url: '/' },
    { name: 'Articles', url: '/posts' },
    { name: postData.title, url: `/posts/${id}` },
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
                    return format(date, 'yyyy年MM月dd日')
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
