import { render, screen } from '@testing-library/react'
import Home from '../../app/page'

describe('Home Page', () => {
  it('应该渲染主页标题', () => {
    render(<Home />)

    const heading = screen.getByText('瑞典马工')
    expect(heading).toBeInTheDocument()
  })

  it('应该显示副标题', () => {
    render(<Home />)

    const subtitle = screen.getByText('Swedish life experiences')
    expect(subtitle).toBeInTheDocument()
  })

  it('应该显示欢迎信息', () => {
    render(<Home />)

    const welcome = screen.getByText('Welcome to 瑞典马工')
    expect(welcome).toBeInTheDocument()
  })
})
