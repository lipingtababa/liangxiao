'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { format } from 'date-fns'

const POSTS_PER_PAGE = 10

interface Post {
  id: string
  title: string
  date: string
  category: string
  tags?: string[]
  description?: string
  excerpt?: string
  author?: string
}

interface PostsClientProps {
  posts: Post[]
}

export default function PostsClient({ posts }: PostsClientProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [currentPage, setCurrentPage] = useState(1)

  // Get all unique categories
  const categories = useMemo(() => {
    const cats = new Set(['All'])
    posts.forEach((post) => {
      if (post.category) cats.add(post.category)
    })
    return Array.from(cats)
  }, [posts])

  // Filter articles
  const filteredPosts = useMemo(() => {
    return posts.filter((post) => {
      const matchesSearch =
        searchTerm === '' ||
        post.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.excerpt?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.tags?.some((tag: string) => tag.toLowerCase().includes(searchTerm.toLowerCase()))

      const matchesCategory = selectedCategory === 'All' || post.category === selectedCategory

      return matchesSearch && matchesCategory
    })
  }, [posts, searchTerm, selectedCategory])

  // Pagination
  const totalPages = Math.ceil(filteredPosts.length / POSTS_PER_PAGE)
  const paginatedPosts = filteredPosts.slice(
    (currentPage - 1) * POSTS_PER_PAGE,
    currentPage * POSTS_PER_PAGE
  )

  // Reset page when filter conditions change
  const handleSearch = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(1)
  }

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    setCurrentPage(1)
  }

  return (
    <>
      {/* Search and filter bar */}
      <div className="mb-8 pb-8 border-b border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search box */}
          <div>
            <input
              type="text"
              id="search"
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search articles..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              style={{ fontFamily: 'Inter, sans-serif' }}
            />
          </div>

          {/* Category filter */}
          <div>
            <select
              id="category"
              value={selectedCategory}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              style={{ fontFamily: 'Inter, sans-serif' }}
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Article list */}
      {paginatedPosts.length > 0 ? (
        <>
          <div className="space-y-8">
            {paginatedPosts.map((post) => (
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
                {(post.description || post.excerpt) && (
                  <p className="text-gray-700 mb-4 line-clamp-3 leading-relaxed">{post.description || post.excerpt}</p>
                )}
                <Link
                  href={`/posts/${post.id}`}
                  className="text-sm font-medium text-gray-500 hover:text-gray-700" style={{ fontFamily: 'Inter, sans-serif' }}
                >
                  Continue reading →
                </Link>
              </article>
            ))}
          </div>

          {/* Pagination controls */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2 mt-12">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                style={{ fontFamily: 'Inter, sans-serif' }}
              >
                Previous
              </button>

              <div className="flex space-x-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                  // Display logic: always show first page, last page, current page and adjacent pages
                  if (
                    page === 1 ||
                    page === totalPages ||
                    (page >= currentPage - 1 && page <= currentPage + 1)
                  ) {
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`px-3 py-1 text-sm font-medium rounded-lg transition ${
                          currentPage === page
                            ? 'bg-gray-900 text-white'
                            : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                        }`}
                        style={{ fontFamily: 'Inter, sans-serif' }}
                      >
                        {page}
                      </button>
                    )
                  } else if (page === currentPage - 2 || page === currentPage + 2) {
                    return (
                      <span key={page} className="px-2 py-1 text-gray-500" style={{ fontFamily: 'Inter, sans-serif' }}>
                        ...
                      </span>
                    )
                  }
                  return null
                })}
              </div>

              <button
                onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                style={{ fontFamily: 'Inter, sans-serif' }}
              >
                Next
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg" style={{ fontFamily: 'Inter, sans-serif' }}>
            {searchTerm || selectedCategory !== 'All' ? 'No articles found matching your criteria' : 'No articles available yet'}
          </p>
        </div>
      )}

      {/* Article statistics */}
      <div className="mt-8 text-center text-sm text-gray-500" style={{ fontFamily: 'Inter, sans-serif' }}>
        Total {filteredPosts.length} articles
        {filteredPosts.length !== posts.length && ` (out of ${posts.length} total)`}
      </div>
    </>
  )
}