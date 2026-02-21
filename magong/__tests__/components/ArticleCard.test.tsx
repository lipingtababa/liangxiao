import { render, screen } from '@testing-library/react'
import ArticleCard from '@/components/ArticleCard'

describe('ArticleCard', () => {
  const mockPost = {
    id: 'test-post',
    title: 'Test Article Title',
    date: '2024-01-15',
    category: 'Tech',
    description: 'This is a test article description for the card component.',
  }

  it('渲染文章卡片的所有内容', () => {
    render(<ArticleCard {...mockPost} />)

    expect(screen.getByText('Test Article Title')).toBeInTheDocument()
    expect(screen.getByText('Tech')).toBeInTheDocument()
    expect(
      screen.getByText('This is a test article description for the card component.')
    ).toBeInTheDocument()
  })

  it('正确生成文章链接', () => {
    render(<ArticleCard {...mockPost} />)

    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/posts/test-post')
  })

  it('没有分类时不显示分类', () => {
    const postWithoutCategory = { ...mockPost, category: undefined }
    render(<ArticleCard {...postWithoutCategory} />)

    expect(screen.queryByText('Tech')).not.toBeInTheDocument()
  })

  it('没有描述时不显示描述', () => {
    const postWithoutDescription = { ...mockPost, description: undefined }
    render(<ArticleCard {...postWithoutDescription} />)

    expect(
      screen.queryByText('This is a test article description for the card component.')
    ).not.toBeInTheDocument()
  })

  it('description 优先于 excerpt 显示', () => {
    const postWithBoth = {
      ...mockPost,
      description: 'Description text',
      excerpt: 'Excerpt text',
    }
    render(<ArticleCard {...postWithBoth} />)

    expect(screen.getByText('Description text')).toBeInTheDocument()
    expect(screen.queryByText('Excerpt text')).not.toBeInTheDocument()
  })
})
