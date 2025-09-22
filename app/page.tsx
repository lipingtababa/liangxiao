import Link from 'next/link'
import { getSortedPostsData } from '@/lib/posts'

export default function Home() {
  const posts = getSortedPostsData()

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Swedish Ma Gong Articles</h1>
        <p className="text-gray-600">English translations of Swedish life experiences</p>
      </div>

      <div className="space-y-6">
        {posts.length > 0 ? (
          posts.map((post) => (
            <article key={post.id} className="bg-white rounded-lg shadow p-6">
              <Link href={`/posts/${post.id}`}>
                <h2 className="text-xl font-semibold mb-2 hover:text-blue-600 cursor-pointer">
                  {post.title}
                </h2>
              </Link>
              <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                <span>{post.date}</span>
                {post.category && (
                  <>
                    <span>•</span>
                    <span>{post.category}</span>
                  </>
                )}
                {post.author && (
                  <>
                    <span>•</span>
                    <span>{post.author}</span>
                  </>
                )}
              </div>
              {post.description && (
                <p className="text-gray-700 mb-3 line-clamp-3">{post.description}</p>
              )}
              <Link
                href={`/posts/${post.id}`}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Read more →
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
