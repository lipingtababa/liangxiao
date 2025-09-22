import Link from 'next/link'
import { getSortedPostsData } from '@/lib/posts'
import { format } from 'date-fns'

export default function Home() {
  const posts = getSortedPostsData()

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4" style={{ fontFamily: 'Inter, sans-serif', letterSpacing: '-0.02em' }}>Swedish Ma Gong Articles</h1>
        <p className="text-lg text-gray-600" style={{ fontFamily: 'Inter, sans-serif' }}>English translations of Swedish life experiences</p>
      </div>

      <div className="space-y-8">
        {posts.length > 0 ? (
          posts.map((post) => (
            <article key={post.id} className="pb-8 border-b border-gray-200 last:border-b-0">
              <Link href={`/posts/${post.id}`} className="block group">
                <h2 className="text-2xl font-semibold mb-3 group-hover:text-blue-600 transition-colors" style={{ fontFamily: 'Inter, sans-serif', letterSpacing: '-0.01em' }}>
                  {post.title}
                </h2>
              </Link>
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-3" style={{ fontFamily: 'Inter, sans-serif' }}>
                {post.author && (
                  <>
                    <span className="font-medium text-gray-900">{post.author}</span>
                    <span className="text-gray-400">·</span>
                  </>
                )}
                <span>
                  {(() => {
                    try {
                      const date = new Date(post.date)
                      if (isNaN(date.getTime())) {
                        return post.date
                      }
                      return format(date, 'MMM d, yyyy')
                    } catch {
                      return post.date
                    }
                  })()}
                </span>
                {post.category && (
                  <>
                    <span className="text-gray-400">·</span>
                    <span>{post.category}</span>
                  </>
                )}
              </div>
              {post.description && (
                <p className="text-gray-700 mb-4 line-clamp-3 leading-relaxed">{post.description}</p>
              )}
              <Link
                href={`/posts/${post.id}`}
                className="text-sm font-medium text-gray-500 hover:text-gray-700" style={{ fontFamily: 'Inter, sans-serif' }}
              >
                Continue reading →
              </Link>
            </article>
          ))
        ) : (
          <p className="text-gray-600">No articles available yet.</p>
        )}
      </div>
    </div>
  )
}