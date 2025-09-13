import { getPostData, getAllPostIds } from '@/lib/posts'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import Link from 'next/link'

export async function generateStaticParams() {
  const posts = getAllPostIds()
  return posts.map((post) => ({
    id: post.params.id,
  }))
}

export default async function PostPage({ params }: { params: { id: string } }) {
  const postData = (await getPostData(params.id)) as any

  return (
    <article className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* 返回按钮 */}
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
          返回文章列表
        </Link>

        {/* 文章头部 */}
        <header className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            {postData.category && (
              <span className="inline-block px-3 py-1 text-sm font-medium text-blue-600 bg-blue-100 rounded-full">
                {postData.category}
              </span>
            )}
            <time className="text-gray-500" dateTime={postData.date}>
              {format(new Date(postData.date), 'yyyy年MM月dd日', { locale: zhCN })}
            </time>
          </div>

          <h1 className="text-4xl font-bold text-gray-900 mb-4">{postData.title}</h1>

          {postData.author && <p className="text-gray-600">作者：{postData.author}</p>}

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

        {/* 文章内容 */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div
            className="prose prose-lg max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-a:text-blue-600 prose-strong:text-gray-900"
            dangerouslySetInnerHTML={{ __html: postData.contentHtml }}
          />
        </div>

        {/* 底部导航 */}
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
            返回文章列表
          </Link>
        </div>
      </div>
    </article>
  )
}
