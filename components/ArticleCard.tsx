import Link from 'next/link'
import { format } from 'date-fns'
import { enUS } from 'date-fns/locale'

interface ArticleCardProps {
  id: string
  title: string
  date: string
  category?: string
  description?: string
  excerpt?: string
}

export default function ArticleCard({
  id,
  title,
  date,
  category,
  description,
  excerpt,
}: ArticleCardProps) {
  const displayText = description || excerpt

  return (
    <article className="break-inside-avoid mb-6">
      <Link
        href={`/posts/${id}`}
        className="block bg-white rounded-xl border border-gray-200 p-5 shadow-sm hover:shadow-md transition-shadow duration-200 group"
      >
        {category && (
          <span className="inline-block px-2.5 py-0.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-full mb-3">
            {category}
          </span>
        )}

        <h2
          className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors leading-snug"
          style={{ fontFamily: 'Inter, sans-serif', letterSpacing: '-0.01em' }}
        >
          {title}
        </h2>

        <time
          className="block text-sm text-gray-400 mb-3"
          dateTime={date}
          style={{ fontFamily: 'Inter, sans-serif' }}
        >
          {(() => {
            try {
              const d = new Date(date)
              if (isNaN(d.getTime())) return date
              return format(d, 'MMM d, yyyy', { locale: enUS })
            } catch {
              return date
            }
          })()}
        </time>

        {displayText && (
          <p className="text-sm text-gray-600 leading-relaxed line-clamp-5">
            {displayText}
          </p>
        )}
      </Link>
    </article>
  )
}
