import PostsClient from '@/components/PostsClient'
import { getSortedPostsData } from '@/lib/posts'

export default function PostsPage() {
  const posts = getSortedPostsData() as any[]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* 页面标题 */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">所有文章</h1>
          <p className="text-lg text-gray-600">探索瑞典生活、文化、科技等精彩内容</p>
        </div>

        {/* 客户端组件处理交互 */}
        <PostsClient posts={posts} />
      </div>
    </div>
  )
}
