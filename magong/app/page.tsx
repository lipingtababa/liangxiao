import { getSortedPostsData } from '@/lib/posts'
import ArticleCard from '@/components/ArticleCard'

export default function Home() {
  const posts = getSortedPostsData()

  return (
    <div className="max-w-6xl mx-auto px-6 py-16">
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4" style={{ fontFamily: 'Inter, sans-serif', letterSpacing: '-0.02em' }}>MaGong</h1>
        <p className="text-lg text-gray-600" style={{ fontFamily: 'Inter, sans-serif' }}>Insights on AI, coding, and tech from a software engineer perspective</p>
      </div>

      {posts.length > 0 ? (
        <div className="columns-1 sm:columns-2 lg:columns-3 gap-6">
          {posts.map((post) => (
            <ArticleCard
              key={post.id}
              id={post.id}
              title={post.title}
              date={post.date}
              category={post.category}
              description={post.description}
            />
          ))}
        </div>
      ) : (
        <p className="text-gray-600">No articles available yet.</p>
      )}
    </div>
  )
}
