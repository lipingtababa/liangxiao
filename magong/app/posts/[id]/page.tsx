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
    <article className="min-h-screen bg-white">
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
      <div className="max-w-3xl mx-auto px-6 py-12">
        {/* Breadcrumb */}
        <nav className="mb-8">
          <Link
            href="/posts"
            className="text-sm text-gray-500 hover:text-gray-700 font-medium"
            style={{ fontFamily: 'Inter, sans-serif' }}
          >
            ← All Articles
          </Link>
        </nav>

        {/* Article header */}
        <header className="mb-12">
          <h1 className="text-4xl font-bold mb-6 leading-tight" style={{ fontFamily: 'Inter, sans-serif', letterSpacing: '-0.02em' }}>
            {postData.title}
          </h1>

          <div className="flex items-center gap-1 text-sm text-gray-600 mb-6" style={{ fontFamily: 'Inter, sans-serif' }}>
            {postData.author && (
              <>
                <span className="font-medium text-gray-900">{postData.author}</span>
                <span className="mx-2">·</span>
              </>
            )}
            {postData.date && (
              <time dateTime={postData.date}>
                {(() => {
                  try {
                    const date = new Date(postData.date)
                    if (isNaN(date.getTime())) {
                      return postData.date
                    }
                    return format(date, 'MMM d, yyyy')
                  } catch {
                    return postData.date
                  }
                })()}
              </time>
            )}
            {postData.category && (
              <>
                <span className="mx-2">·</span>
                <span className="text-gray-900">{postData.category}</span>
              </>
            )}
          </div>

          {postData.tags && postData.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {postData.tags.map((tag: string) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-1 text-gray-600 bg-gray-100 rounded"
                  style={{ fontFamily: 'Inter, sans-serif' }}
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </header>

        {/* Cover image */}
        {postData.image && (
          <div className="mb-12 -mx-6">
            <ImageWithFallback
              src={postData.image}
              alt={postData.title}
              width={1200}
              height={630}
              className="w-full rounded-lg"
              priority
            />
          </div>
        )}

        {/* Article content */}
        <div className="prose-content">
          <MarkdownRenderer content={postData.content || ''} />
        </div>


        {/* Original link */}
        {postData.originalUrl && (
          <div className="mt-12 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600" style={{ fontFamily: 'Inter, sans-serif' }}>
              Original article:
              <a
                href={postData.originalUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 ml-1"
              >
                {postData.originalUrl}
              </a>
            </p>
          </div>
        )}

        {/* Bottom navigation */}
        <div className="mt-16 pt-8 border-t border-gray-200">
          <Link
            href="/posts"
            className="text-sm text-gray-500 hover:text-gray-700 font-medium"
            style={{ fontFamily: 'Inter, sans-serif' }}
          >
            ← Back to all articles
          </Link>
        </div>
      </div>
    </article>
  )
}
