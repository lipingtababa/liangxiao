import { render, screen, fireEvent } from '@testing-library/react'
import PostsClient from '@/components/PostsClient'

describe('PostsClient', () => {
  const mockPosts = [
    {
      id: 'post-1',
      title: 'First Article',
      date: '2024-01-20',
      category: 'Tech',
      tags: ['Frontend', 'React'],
      excerpt: 'First article excerpt',
      author: 'Author1',
    },
    {
      id: 'post-2',
      title: 'Second Article',
      date: '2024-01-15',
      category: 'Life',
      tags: ['Daily', 'Sharing'],
      excerpt: 'Second article excerpt',
      author: 'Author2',
    },
    {
      id: 'post-3',
      title: 'Third Article',
      date: '2024-01-10',
      category: 'Tech',
      tags: ['Backend', 'Node.js'],
      excerpt: 'Third article excerpt',
      author: 'Author3',
    },
  ]

  it('渲染所有文章', () => {
    render(<PostsClient posts={mockPosts} />)

    expect(screen.getByText('First Article')).toBeInTheDocument()
    expect(screen.getByText('Second Article')).toBeInTheDocument()
    expect(screen.getByText('Third Article')).toBeInTheDocument()
  })

  it('搜索功能正常工作', () => {
    render(<PostsClient posts={mockPosts} />)

    const searchInput = screen.getByPlaceholderText('Search articles...')
    fireEvent.change(searchInput, { target: { value: 'First' } })

    expect(screen.getByText('First Article')).toBeInTheDocument()
    expect(screen.queryByText('Second Article')).not.toBeInTheDocument()
    expect(screen.queryByText('Third Article')).not.toBeInTheDocument()
  })

  it('分类筛选功能正常工作', () => {
    render(<PostsClient posts={mockPosts} />)

    const categorySelect = screen.getByRole('combobox')
    fireEvent.change(categorySelect, { target: { value: 'Tech' } })

    expect(screen.getByText('First Article')).toBeInTheDocument()
    expect(screen.queryByText('Second Article')).not.toBeInTheDocument()
    expect(screen.getByText('Third Article')).toBeInTheDocument()
  })

  it('搜索标签时能找到相应文章', () => {
    render(<PostsClient posts={mockPosts} />)

    const searchInput = screen.getByPlaceholderText('Search articles...')
    fireEvent.change(searchInput, { target: { value: 'React' } })

    expect(screen.getByText('First Article')).toBeInTheDocument()
    expect(screen.queryByText('Second Article')).not.toBeInTheDocument()
    expect(screen.queryByText('Third Article')).not.toBeInTheDocument()
  })

  it('显示文章统计信息', () => {
    render(<PostsClient posts={mockPosts} />)

    expect(screen.getByText('Total 3 articles')).toBeInTheDocument()
  })

  it('过滤后显示正确的统计信息', () => {
    render(<PostsClient posts={mockPosts} />)

    const categorySelect = screen.getByRole('combobox')
    fireEvent.change(categorySelect, { target: { value: 'Tech' } })

    expect(screen.getByText(/Total 2 articles/)).toBeInTheDocument()
    expect(screen.getByText(/out of 3 total/)).toBeInTheDocument()
  })

  it('没有匹配文章时显示提示信息', () => {
    render(<PostsClient posts={mockPosts} />)

    const searchInput = screen.getByPlaceholderText('Search articles...')
    fireEvent.change(searchInput, { target: { value: 'nonexistent content' } })

    expect(screen.getByText('No articles found matching your criteria')).toBeInTheDocument()
  })

  it('没有文章时显示提示信息', () => {
    render(<PostsClient posts={[]} />)

    expect(screen.getByText('No articles available yet')).toBeInTheDocument()
  })
})
