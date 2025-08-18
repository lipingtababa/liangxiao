import Link from 'next/link'
import { getSortedPostsData } from '../lib/posts'
import { format } from 'date-fns'

// 组件类型定义
interface Post {
  id: string
  date: string
  title: string
  excerpt?: string
  originalTitle?: string
}

export default async function Home() {
  // 在 App Router 中，我们可以直接在组件中获取数据
  const allPostsData: Post[] = getSortedPostsData()

  return (
    <div className="container-custom">
      <main>
        <header className="text-center py-16 border-b border-gray-200">
          <h1 className="text-5xl font-bold mb-3 text-gray-800">
            Swedish Ma Gong
          </h1>
          <p className="text-xl text-gray-600">
            瑞典马工 - Insights from Sweden for International Readers
          </p>
        </header>

        <section className="py-10">
          {allPostsData.length === 0 ? (
            <p className="text-center text-gray-600 text-lg py-10">
              No articles yet. Check back soon!
            </p>
          ) : (
            <ul className="space-y-10">
              {allPostsData.map(({ id, date, title, excerpt, originalTitle }) => (
                <li key={id} className="pb-10 border-b border-gray-200 last:border-b-0">
                  <Link 
                    href={`/posts/${id}`}
                    className="block hover:transform hover:scale-[1.02] transition-transform duration-200"
                  >
                    <h2 className="text-3xl font-semibold mb-3 text-gray-800 hover:text-primary transition-colors">
                      {title}
                    </h2>
                    {originalTitle && (
                      <p className="text-sm text-gray-500 mb-4">
                        Original: {originalTitle}
                      </p>
                    )}
                    {excerpt && (
                      <p className="text-gray-700 leading-relaxed mb-4">
                        {excerpt}
                      </p>
                    )}
                    <time className="text-sm text-gray-500">
                      {format(new Date(date), 'MMMM d, yyyy')}
                    </time>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>

      <footer className="text-center py-16 border-t border-gray-200">
        <p className="text-gray-600">
          Translated from{' '}
          <a 
            href="https://mp.weixin.qq.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            瑞典马工 WeChat Official Account
          </a>
        </p>
      </footer>
    </div>
  )
}