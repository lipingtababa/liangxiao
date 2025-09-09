import Link from 'next/link'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

interface ArticleCardProps {
  id: string
  title: string
  date: string
  category: string
  tags?: string[]
  excerpt: string
  author?: string
}

export default function ArticleCard({
  id,
  title,
  date,
  category,
  tags = [],
  excerpt,
  author,
}: ArticleCardProps) {
  return (
    <article className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden">
      <Link href={`/posts/${id}`} className="block p-6">
        <div className="flex items-center justify-between mb-2">
          <span className="inline-block px-3 py-1 text-sm font-medium text-blue-600 bg-blue-100 rounded-full">
            {category}
          </span>
          <time className="text-sm text-gray-500" dateTime={date}>
            {format(new Date(date), 'yyyy年MM月dd日', { locale: zhCN })}
          </time>
        </div>

        <h2 className="text-xl font-bold text-gray-900 mb-2 hover:text-blue-600 transition-colors">
          {title}
        </h2>

        <p className="text-gray-600 mb-4 line-clamp-3">{excerpt}</p>

        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-2">
            {tags.slice(0, 3).map((tag) => (
              <span key={tag} className="text-xs px-2 py-1 text-gray-600 bg-gray-100 rounded">
                #{tag}
              </span>
            ))}
          </div>

          {author && <span className="text-sm text-gray-500">作者：{author}</span>}
        </div>
      </Link>
    </article>
  )
}
