/**
 * Next.js 中间件
 * 处理请求日志、错误捕获、性能监控等
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { logger } from './lib/logger'

// 生成请求ID
function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 中间件配置
export function middleware(request: NextRequest) {
  const startTime = Date.now()
  const requestId = generateRequestId()
  const { pathname, search } = request.nextUrl

  // 添加请求ID到响应头
  const response = NextResponse.next()
  response.headers.set('X-Request-Id', requestId)

  // 记录请求日志
  logger.info('收到请求', {
    requestId,
    path: pathname,
    method: request.method,
    metadata: {
      query: search,
      userAgent: request.headers.get('user-agent'),
      referer: request.headers.get('referer'),
      ip: request.ip || request.headers.get('x-forwarded-for'),
    },
  })

  // 添加安全头
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')

  // 添加性能监控
  const duration = Date.now() - startTime
  response.headers.set('X-Response-Time', `${duration}ms`)

  // 记录响应日志
  if (duration > 1000) {
    logger.warn('请求处理时间过长', {
      requestId,
      path: pathname,
      method: request.method,
      duration,
    })
  }

  return response
}

// 配置中间件应用路径
export const config = {
  matcher: [
    // 匹配所有路径，除了静态资源
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
}