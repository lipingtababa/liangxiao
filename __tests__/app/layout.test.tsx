import { render, screen } from '@testing-library/react'
import RootLayout from '../../app/layout'

// Mock Next.js Script component
jest.mock('next/script', () => ({
  __esModule: true,
  default: ({ id }: { id: string }) => <script id={id} />,
}))

describe('Root Layout', () => {
  it('应该渲染导航栏', () => {
    render(
      <RootLayout>
        <div>测试内容</div>
      </RootLayout>
    )

    const navTitle = screen.getByText('MaGong')
    expect(navTitle).toBeInTheDocument()
  })

  it('应该渲染页脚', () => {
    render(
      <RootLayout>
        <div>测试内容</div>
      </RootLayout>
    )

    const footer = screen.getByText(/© 2024 MaGong/)
    expect(footer).toBeInTheDocument()
  })

  it('应该渲染子组件', () => {
    render(
      <RootLayout>
        <div data-testid="child-content">子组件内容</div>
      </RootLayout>
    )

    const childContent = screen.getByTestId('child-content')
    expect(childContent).toBeInTheDocument()
    expect(screen.getByText('子组件内容')).toBeInTheDocument()
  })

  it('应该设置正确的语言属性', () => {
    const { container } = render(
      <RootLayout>
        <div>测试</div>
      </RootLayout>
    )

    const htmlElement = container.querySelector('html')
    expect(htmlElement).toHaveAttribute('lang', 'en')
  })

  it('应该渲染导航链接', () => {
    render(
      <RootLayout>
        <div>测试</div>
      </RootLayout>
    )

    const articlesLink = screen.getByText('Articles')
    expect(articlesLink).toBeInTheDocument()
  })
})
