import { render, screen } from '@testing-library/react'
import RootLayout from '../../app/layout'

// Mock Next.js font loading
jest.mock('next/font/google', () => ({
  Inter: () => ({
    className: 'inter-font-class',
  }),
}))

describe('Root Layout', () => {
  it('应该渲染导航栏', () => {
    render(
      <RootLayout>
        <div>测试内容</div>
      </RootLayout>
    )

    const navTitle = screen.getByText('瑞典马工')
    expect(navTitle).toBeInTheDocument()
  })

  it('应该渲染页脚', () => {
    render(
      <RootLayout>
        <div>测试内容</div>
      </RootLayout>
    )

    const footer = screen.getByText(/© 2024 瑞典马工/)
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
    expect(htmlElement).toHaveAttribute('lang', 'zh')
  })

  it('应该应用字体类名', () => {
    const { container } = render(
      <RootLayout>
        <div>测试</div>
      </RootLayout>
    )

    const bodyElement = container.querySelector('body')
    expect(bodyElement).toHaveClass('inter-font-class')
  })
})
