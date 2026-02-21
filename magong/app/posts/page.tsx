import PostsClient from '@/components/PostsClient'
import { getSortedPostsData } from '@/lib/posts'

export default function PostsPage() {
  const posts = getSortedPostsData() as any[]

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* Page title */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-4" style={{ fontFamily: 'Inter, sans-serif', letterSpacing: '-0.02em' }}>All Articles</h1>
          <p className="text-lg text-gray-600" style={{ fontFamily: 'Inter, sans-serif' }}>Browse and search all published articles</p>
        </div>

        {/* Client component for interactions */}
        <PostsClient posts={posts} />
      </div>
    </div>
  )
}
