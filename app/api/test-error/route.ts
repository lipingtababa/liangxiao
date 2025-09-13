/**
 * 测试错误处理 API
 * 仅用于开发环境测试
 */

import { NextRequest, NextResponse } from 'next/server'
import { withErrorHandler, withRateLimit } from '@/lib/api-handler'
import {
  ValidationError,
  NotFoundError,
  UnauthorizedError,
  ExternalServiceError
} from '@/lib/errors'

// 添加速率限制
const handler = withRateLimit(5, 60000)(
  withErrorHandler(async (request: NextRequest) => {
    // 仅在开发环境启用
    if (process.env.NODE_ENV === 'production') {
      throw new NotFoundError('API endpoint')
    }

    const { searchParams } = new URL(request.url)
    const errorType = searchParams.get('type')

    switch (errorType) {
      case 'validation':
        throw new ValidationError('测试数据验证错误', {
          fields: {
            email: '邮箱格式不正确',
            password: '密码长度必须大于8位',
          },
        })

      case 'notfound':
        throw new NotFoundError('测试资源')

      case 'unauthorized':
        throw new UnauthorizedError('测试未授权访问')

      case 'external':
        throw new ExternalServiceError('WeChat API', new Error('Connection timeout'))

      case 'runtime':
        throw new Error('测试运行时错误')

      case 'async':
        await new Promise((_, reject) => {
          setTimeout(() => reject(new Error('异步操作失败')), 100)
        })
        break

      default:
        return NextResponse.json({
          message: '错误处理测试端点',
          usage: '添加 ?type=validation|notfound|unauthorized|external|runtime|async 来触发不同类型的错误',
          availableTypes: [
            'validation - 400 验证错误',
            'notfound - 404 资源未找到',
            'unauthorized - 401 未授权',
            'external - 503 外部服务错误',
            'runtime - 500 运行时错误',
            'async - 500 异步错误',
          ],
        })
    }

    // This should never be reached but TypeScript needs it
    return NextResponse.json({ error: 'Unknown error type' }, { status: 500 })
  })
)

export const GET = handler