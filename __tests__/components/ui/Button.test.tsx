import { render, screen, fireEvent } from '@testing-library/react'
import Button from '../../../components/ui/Button'

describe('Button Component', () => {
  it('应该渲染按钮文本', () => {
    render(<Button>点击我</Button>)
    expect(screen.getByText('点击我')).toBeInTheDocument()
  })

  it('应该应用默认的primary样式', () => {
    render(<Button>测试按钮</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-blue-600')
  })

  it('应该应用secondary样式', () => {
    render(<Button variant="secondary">次要按钮</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-gray-600')
  })

  it('应该应用outline样式', () => {
    render(<Button variant="outline">轮廓按钮</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('border', 'border-gray-300')
  })

  it('应该应用不同的尺寸', () => {
    const { rerender } = render(<Button size="sm">小按钮</Button>)
    let button = screen.getByRole('button')
    expect(button).toHaveClass('px-3', 'py-1.5', 'text-sm')

    rerender(<Button size="md">中按钮</Button>)
    button = screen.getByRole('button')
    expect(button).toHaveClass('px-4', 'py-2')

    rerender(<Button size="lg">大按钮</Button>)
    button = screen.getByRole('button')
    expect(button).toHaveClass('px-6', 'py-3', 'text-lg')
  })

  it('应该处理点击事件', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>点击测试</Button>)

    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('应该支持disabled状态', () => {
    render(<Button disabled>禁用按钮</Button>)
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('应该支持自定义className', () => {
    render(<Button className="custom-class">自定义类</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('custom-class')
  })

  it('应该传递其他HTML属性', () => {
    render(
      <Button data-testid="custom-button" aria-label="测试按钮">
        测试
      </Button>
    )
    const button = screen.getByTestId('custom-button')
    expect(button).toHaveAttribute('aria-label', '测试按钮')
  })
})
