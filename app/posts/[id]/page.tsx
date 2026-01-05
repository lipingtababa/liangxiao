import { getPostData, getAllPostIds, PostData } from '@/lib/posts'
import { Metadata } from 'next'
import ArticleContent from '@/components/ArticleContent'
import Script from 'next/script'
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
    <>
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
      <ArticleContent postData={postData} />
    </>
  )
}
