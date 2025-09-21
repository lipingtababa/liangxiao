import { render, screen } from '@testing-library/react'
import Card from '../../../components/ui/Card'

describe('Card Component', () => {
  it('应该渲染子元素', () => {
    render(
      <Card>
        <h2>卡片标题</h2>
        <p>卡片内容</p>
      </Card>
    )

    expect(screen.getByText('卡片标题')).toBeInTheDocument()
    expect(screen.getByText('卡片内容')).toBeInTheDocument()
  })

  it('应该应用默认样式', () => {
    const { container } = render(<Card>测试内容</Card>)

    const card = container.firstChild
    expect(card).toHaveClass('bg-white', 'rounded-lg', 'shadow', 'p-6')
  })

  it('应该支持自定义className', () => {
    const { container } = render(<Card className="custom-card-class">自定义样式卡片</Card>)

    const card = container.firstChild
    expect(card).toHaveClass('custom-card-class')
    // 同时保留默认样式
    expect(card).toHaveClass('bg-white', 'rounded-lg', 'shadow', 'p-6')
  })

  it('应该正确渲染复杂的子元素', () => {
    render(
      <Card>
        <div data-testid="nested-div">
          <button>按钮</button>
          <ul>
            <li>项目1</li>
            <li>项目2</li>
          </ul>
        </div>
      </Card>
    )

    expect(screen.getByTestId('nested-div')).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeInTheDocument()
    expect(screen.getByText('项目1')).toBeInTheDocument()
    expect(screen.getByText('项目2')).toBeInTheDocument()
  })

  it('应该渲染空卡片', () => {
    const { container } = render(<Card>{null}</Card>)
    const card = container.firstChild
    expect(card).toBeInTheDocument()
    expect(card).toHaveClass('bg-white', 'rounded-lg', 'shadow', 'p-6')
  })
})
