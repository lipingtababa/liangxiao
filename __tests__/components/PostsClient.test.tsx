import { render, screen, fireEvent } from '@testing-library/react'
import PostsClient from '@/components/PostsClient'

describe('PostsClient', () => {
  const mockPosts = [
    {
      id: 'post-1',
      title: '第一篇文章',
      date: '2024-01-20',
      category: '科技',
      tags: ['前端', 'React'],
      excerpt: '第一篇文章的摘要',
      author: '作者1',
    },
    {
      id: 'post-2',
      title: '第二篇文章',
      date: '2024-01-15',
      category: '生活',
      tags: ['日常', '分享'],
      excerpt: '第二篇文章的摘要',
      author: '作者2',
    },
    {
      id: 'post-3',
      title: '第三篇文章',
      date: '2024-01-10',
      category: '科技',
      tags: ['后端', 'Node.js'],
      excerpt: '第三篇文章的摘要',
      author: '作者3',
    },
  ]

  it('渲染所有文章', () => {
    render(<PostsClient posts={mockPosts} />)

    expect(screen.getByText('第一篇文章')).toBeInTheDocument()
    expect(screen.getByText('第二篇文章')).toBeInTheDocument()
    expect(screen.getByText('第三篇文章')).toBeInTheDocument()
  })

  it('搜索功能正常工作', () => {
    render(<PostsClient posts={mockPosts} />)

    const searchInput = screen.getByPlaceholderText('输入关键词搜索...')
    fireEvent.change(searchInput, { target: { value: '第一篇' } })

    expect(screen.getByText('第一篇文章')).toBeInTheDocument()
    expect(screen.queryByText('第二篇文章')).not.toBeInTheDocument()
    expect(screen.queryByText('第三篇文章')).not.toBeInTheDocument()
  })

  it('分类筛选功能正常工作', () => {
    render(<PostsClient posts={mockPosts} />)

    const categorySelect = screen.getByLabelText('分类筛选')
    fireEvent.change(categorySelect, { target: { value: '科技' } })

    expect(screen.getByText('第一篇文章')).toBeInTheDocument()
    expect(screen.queryByText('第二篇文章')).not.toBeInTheDocument()
    expect(screen.getByText('第三篇文章')).toBeInTheDocument()
  })

  it('搜索标签时能找到相应文章', () => {
    render(<PostsClient posts={mockPosts} />)

    const searchInput = screen.getByPlaceholderText('输入关键词搜索...')
    fireEvent.change(searchInput, { target: { value: 'React' } })

    expect(screen.getByText('第一篇文章')).toBeInTheDocument()
    expect(screen.queryByText('第二篇文章')).not.toBeInTheDocument()
    expect(screen.queryByText('第三篇文章')).not.toBeInTheDocument()
  })

  it('显示文章统计信息', () => {
    render(<PostsClient posts={mockPosts} />)

    expect(screen.getByText('共 3 篇文章')).toBeInTheDocument()
  })

  it('过滤后显示正确的统计信息', () => {
    render(<PostsClient posts={mockPosts} />)

    const categorySelect = screen.getByLabelText('分类筛选')
    fireEvent.change(categorySelect, { target: { value: '科技' } })

    expect(screen.getByText(/共 2 篇文章/)).toBeInTheDocument()
    expect(screen.getByText(/总计 3 篇/)).toBeInTheDocument()
  })

  it('没有匹配文章时显示提示信息', () => {
    render(<PostsClient posts={mockPosts} />)

    const searchInput = screen.getByPlaceholderText('输入关键词搜索...')
    fireEvent.change(searchInput, { target: { value: '不存在的内容' } })

    expect(screen.getByText('没有找到符合条件的文章')).toBeInTheDocument()
  })

  it('没有文章时显示提示信息', () => {
    render(<PostsClient posts={[]} />)

    expect(screen.getByText('暂无文章')).toBeInTheDocument()
  })
})
