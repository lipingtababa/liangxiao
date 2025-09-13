'use client'

import { useState, useMemo } from 'react'
import ArticleCard from '@/components/ArticleCard'

const POSTS_PER_PAGE = 6

interface Post {
  id: string
  title: string
  date: string
  category: string
  tags?: string[]
  excerpt: string
  author?: string
}

interface PostsClientProps {
  posts: Post[]
}

export default function PostsClient({ posts }: PostsClientProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('全部')
  const [currentPage, setCurrentPage] = useState(1)

  // 获取所有唯一分类
  const categories = useMemo(() => {
    const cats = new Set(['全部'])
    posts.forEach((post) => {
      if (post.category) cats.add(post.category)
    })
    return Array.from(cats)
  }, [posts])

  // 过滤文章
  const filteredPosts = useMemo(() => {
    return posts.filter((post) => {
      const matchesSearch =
        searchTerm === '' ||
        post.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.excerpt?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.tags?.some((tag: string) => tag.toLowerCase().includes(searchTerm.toLowerCase()))

      const matchesCategory = selectedCategory === '全部' || post.category === selectedCategory

      return matchesSearch && matchesCategory
    })
  }, [posts, searchTerm, selectedCategory])

  // 分页
  const totalPages = Math.ceil(filteredPosts.length / POSTS_PER_PAGE)
  const paginatedPosts = filteredPosts.slice(
    (currentPage - 1) * POSTS_PER_PAGE,
    currentPage * POSTS_PER_PAGE
  )

  // 重置页码当过滤条件改变
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
      {/* 搜索和筛选栏 */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 搜索框 */}
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
              搜索文章
            </label>
            <input
              type="text"
              id="search"
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="输入关键词搜索..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
            />
          </div>

          {/* 分类筛选 */}
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
              分类筛选
            </label>
            <select
              id="category"
              value={selectedCategory}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
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

      {/* 文章列表 */}
      {paginatedPosts.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {paginatedPosts.map((post) => (
              <ArticleCard
                key={post.id}
                id={post.id}
                title={post.title}
                date={post.date}
                category={post.category}
                tags={post.tags}
                excerpt={post.excerpt}
                author={post.author}
              />
            ))}
          </div>

          {/* 分页控件 */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                上一页
              </button>

              <div className="flex space-x-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                  // 显示逻辑：始终显示第一页、最后一页、当前页及其前后页
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
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    )
                  } else if (page === currentPage - 2 || page === currentPage + 2) {
                    return (
                      <span key={page} className="px-2 py-1 text-gray-500">
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
              >
                下一页
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">
            {searchTerm || selectedCategory !== '全部' ? '没有找到符合条件的文章' : '暂无文章'}
          </p>
        </div>
      )}

      {/* 文章统计信息 */}
      <div className="mt-8 text-center text-sm text-gray-500">
        共 {filteredPosts.length} 篇文章
        {filteredPosts.length !== posts.length && ` (总计 ${posts.length} 篇)`}
      </div>
    </>
  )
}
