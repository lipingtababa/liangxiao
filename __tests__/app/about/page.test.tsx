import { render, screen } from '@testing-library/react'
import AboutPage from '../../../app/about/page'

describe('About Page', () => {
  it('应该渲染关于页面标题', () => {
    render(<AboutPage />)
    
    const heading = screen.getByText('关于瑞典马工')
    expect(heading).toBeInTheDocument()
    expect(heading.tagName).toBe('H1')
  })

  it('应该显示介绍文本', () => {
    render(<AboutPage />)
    
    expect(screen.getByText(/专门为在瑞典生活的华人提供实用信息/)).toBeInTheDocument()
    expect(screen.getByText(/帮助新来瑞典的朋友更快地适应当地生活/)).toBeInTheDocument()
  })

  it('应该显示服务列表', () => {
    render(<AboutPage />)
    
    expect(screen.getByText('我们提供什么')).toBeInTheDocument()
    expect(screen.getByText('最新的瑞典生活资讯')).toBeInTheDocument()
    expect(screen.getByText('实用的生活指南和建议')).toBeInTheDocument()
    expect(screen.getByText('文化交流和经验分享')).toBeInTheDocument()
    expect(screen.getByText('中英文双语内容服务')).toBeInTheDocument()
  })
})