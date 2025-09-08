import { render, screen } from '@testing-library/react'
import Home from '../../app/page'

describe('Home Page', () => {
  it('应该渲染主页标题', () => {
    render(<Home />)
    
    const heading = screen.getByText('欢迎来到瑞典马工')
    expect(heading).toBeInTheDocument()
  })

  it('应该显示副标题', () => {
    render(<Home />)
    
    const subtitle = screen.getByText('分享瑞典生活经验，传递实用信息')
    expect(subtitle).toBeInTheDocument()
  })

  it('应该渲染三个功能卡片', () => {
    render(<Home />)
    
    expect(screen.getByText('最新文章')).toBeInTheDocument()
    expect(screen.getByText('生活指南')).toBeInTheDocument()
    expect(screen.getByText('关于我们')).toBeInTheDocument()
  })

  it('应该包含正确的导航链接', () => {
    render(<Home />)
    
    const postsLink = screen.getByRole('link', { name: /查看所有文章/ })
    expect(postsLink).toHaveAttribute('href', '/posts')
    
    const guidesLink = screen.getByRole('link', { name: /浏览指南/ })
    expect(guidesLink).toHaveAttribute('href', '/guides')
    
    const aboutLink = screen.getByRole('link', { name: /了解更多/ })
    expect(aboutLink).toHaveAttribute('href', '/about')
  })

  it('应该显示翻译工具部分', () => {
    render(<Home />)
    
    expect(screen.getByText('翻译工具')).toBeInTheDocument()
    expect(screen.getByText('使用我们的翻译工具将微信文章转换为英文版本')).toBeInTheDocument()
    
    const translateLink = screen.getByRole('link', { name: '开始翻译' })
    expect(translateLink).toHaveAttribute('href', '/translate')
  })
})