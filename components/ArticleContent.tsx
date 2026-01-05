'use client'

import { format } from 'date-fns'
import Link from 'next/link'
import MarkdownRenderer from '@/components/MarkdownRenderer'
import ImageWithFallback from '@/components/ImageWithFallback'
import ReadingProgress from '@/components/ReadingProgress'
import { PostData } from '@/lib/posts'

interface ArticleContentProps {
  postData: PostData
}

export default function ArticleContent({ postData }: ArticleContentProps) {
  return (
    <ReadingProgress postId={postData.id}>
      <article className="min-h-screen bg-white">
        <div className="max-w-3xl mx-auto px-6 py-12">
          {/* 面包屑导航 */}
          <nav className="mb-8">
            <Link
              href="/posts"
              className="text-sm text-gray-500 hover:text-gray-700 font-medium"
              style={{ fontFamily: 'Inter, sans-serif' }}
            >
              ← 所有文章
            </Link>
          </nav>

          {/* 文章标题 */}
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

          {/* 封面图片 */}
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

          {/* 文章内容 */}
          <div className="prose-content">
            <MarkdownRenderer content={postData.content || ''} />
          </div>

          {/* 原文链接 */}
          {postData.originalUrl && (
            <div className="mt-12 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <p className="text-sm text-gray-600" style={{ fontFamily: 'Inter, sans-serif' }}>
                原文链接：
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

          {/* 底部导航 */}
          <div className="mt-16 pt-8 border-t border-gray-200">
            <Link
              href="/posts"
              className="text-sm text-gray-500 hover:text-gray-700 font-medium"
              style={{ fontFamily: 'Inter, sans-serif' }}
            >
              ← 返回所有文章
            </Link>
          </div>
        </div>
      </article>
    </ReadingProgress>
  )
}