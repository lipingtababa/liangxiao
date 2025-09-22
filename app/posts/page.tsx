import PostsClient from '@/components/PostsClient'
import { getSortedPostsData } from '@/lib/posts'

export default function PostsPage() {
  const posts = getSortedPostsData() as any[]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Page title */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">All Articles</h1>
          <p className="text-lg text-gray-600">Explore Swedish life, culture, technology and more</p>
        </div>

        {/* Client component for interactions */}
        <PostsClient posts={posts} />
      </div>
    </div>
  )
}
