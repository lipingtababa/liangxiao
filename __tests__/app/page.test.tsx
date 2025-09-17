import { render, screen } from '@testing-library/react'
import Home from '../../app/page'

jest.mock('../../lib/posts', () => ({
  getSortedPostsData: () => [
    {
      id: 'test-post-1',
      title: 'Test Article 1',
      date: '2024-01-10',
      category: 'Culture',
      author: '瑞典马工',
      description: 'This is a test article description',
    },
    {
      id: 'test-post-2',
      title: 'Test Article 2',
      date: '2024-01-09',
      category: 'Life',
      author: '瑞典马工',
      description: 'Another test article description',
    },
  ],
}))

describe('Home Page', () => {
  it('应该渲染主页标题', () => {
    render(<Home />)

    const heading = screen.getByText('Articles from 瑞典马工')
    expect(heading).toBeInTheDocument()
  })

  it('应该显示副标题', () => {
    render(<Home />)

    const subtitle = screen.getByText('English translations of Swedish life experiences')
    expect(subtitle).toBeInTheDocument()
  })

  it('应该显示文章列表', () => {
    render(<Home />)

    expect(screen.getByText('Test Article 1')).toBeInTheDocument()
    expect(screen.getByText('Test Article 2')).toBeInTheDocument()
  })

  it('应该显示文章元数据', () => {
    render(<Home />)

    expect(screen.getByText('2024-01-10')).toBeInTheDocument()
    expect(screen.getByText('Culture')).toBeInTheDocument()
    expect(screen.getAllByText('瑞典马工').length).toBeGreaterThan(0)
  })

  it('应该包含文章链接', () => {
    render(<Home />)

    const readMoreLinks = screen.getAllByText('Read more →')
    expect(readMoreLinks).toHaveLength(2)
    expect(readMoreLinks[0].closest('a')).toHaveAttribute('href', '/posts/test-post-1')
    expect(readMoreLinks[1].closest('a')).toHaveAttribute('href', '/posts/test-post-2')
  })
})
