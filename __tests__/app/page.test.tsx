import { render, screen } from '@testing-library/react'
import Home from '../../app/page'

jest.mock('../../lib/posts', () => ({
  getSortedPostsData: () => [
    {
      id: 'test-post-1',
      title: 'Test Article 1',
      date: '2024-01-10',
      category: 'Culture',
      description: 'This is a test article description',
    },
    {
      id: 'test-post-2',
      title: 'Test Article 2',
      date: '2024-01-09',
      category: 'Life',
      description: 'Another test article description',
    },
  ],
}))

describe('Home Page', () => {
  it('应该渲染主页标题', () => {
    render(<Home />)

    const heading = screen.getByText('MaGong')
    expect(heading).toBeInTheDocument()
  })

  it('应该显示副标题', () => {
    render(<Home />)

    const subtitle = screen.getByText(
      'Insights on AI, coding, and tech from a software engineer perspective'
    )
    expect(subtitle).toBeInTheDocument()
  })

  it('应该显示文章列表', () => {
    render(<Home />)

    expect(screen.getByText('Test Article 1')).toBeInTheDocument()
    expect(screen.getByText('Test Article 2')).toBeInTheDocument()
  })

  it('应该显示文章元数据', () => {
    render(<Home />)

    expect(screen.getByText('Culture')).toBeInTheDocument()
    expect(screen.getByText('This is a test article description')).toBeInTheDocument()
  })

  it('应该包含文章链接', () => {
    render(<Home />)

    const links = screen.getAllByRole('link')
    const postLinks = links.filter((l) => l.getAttribute('href')?.startsWith('/posts/'))
    expect(postLinks.length).toBeGreaterThanOrEqual(2)
  })
})
