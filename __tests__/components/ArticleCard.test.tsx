import { render, screen } from '@testing-library/react'
import ArticleCard from '@/components/ArticleCard'

describe('ArticleCard', () => {
  const mockPost = {
    id: 'test-post',
    title: '测试文章标题',
    date: '2024-01-15',
    category: '科技',
    tags: ['测试', '开发', '前端'],
    excerpt: '这是一篇测试文章的摘要内容，用于展示文章卡片组件的功能。',
    author: '测试作者',
  }

  it('渲染文章卡片的所有内容', () => {
    render(<ArticleCard {...mockPost} />)

    expect(screen.getByText('测试文章标题')).toBeInTheDocument()
    expect(screen.getByText('科技')).toBeInTheDocument()
    expect(
      screen.getByText('这是一篇测试文章的摘要内容，用于展示文章卡片组件的功能。')
    ).toBeInTheDocument()
    expect(screen.getByText('作者：测试作者')).toBeInTheDocument()
    expect(screen.getByText('#测试')).toBeInTheDocument()
    expect(screen.getByText('#开发')).toBeInTheDocument()
    expect(screen.getByText('#前端')).toBeInTheDocument()
  })

  it('正确生成文章链接', () => {
    render(<ArticleCard {...mockPost} />)

    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/posts/test-post')
  })

  it('没有作者时不显示作者信息', () => {
    const postWithoutAuthor = { ...mockPost, author: undefined }
    render(<ArticleCard {...postWithoutAuthor} />)

    expect(screen.queryByText(/作者：/)).not.toBeInTheDocument()
  })

  it('没有标签时不显示标签', () => {
    const postWithoutTags = { ...mockPost, tags: undefined }
    render(<ArticleCard {...postWithoutTags} />)

    expect(screen.queryByText(/#/)).not.toBeInTheDocument()
  })

  it('最多显示3个标签', () => {
    const postWithManyTags = {
      ...mockPost,
      tags: ['标签1', '标签2', '标签3', '标签4', '标签5'],
    }
    render(<ArticleCard {...postWithManyTags} />)

    expect(screen.getByText('#标签1')).toBeInTheDocument()
    expect(screen.getByText('#标签2')).toBeInTheDocument()
    expect(screen.getByText('#标签3')).toBeInTheDocument()
    expect(screen.queryByText('#标签4')).not.toBeInTheDocument()
    expect(screen.queryByText('#标签5')).not.toBeInTheDocument()
  })
})
