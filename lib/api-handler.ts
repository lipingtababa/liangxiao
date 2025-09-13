/**
 * API 路由错误处理包装器
 */

import { NextRequest, NextResponse } from 'next/server'
import { logger } from './logger'
import { AppError, serializeError, getErrorStatusCode } from './errors'

type ApiHandler = (
  request: NextRequest,
  context?: any
) => Promise<NextResponse> | NextResponse

/**
 * 包装 API 路由处理器，提供统一的错误处理
 */
export function withErrorHandler(handler: ApiHandler): ApiHandler {
  return async (request: NextRequest, context?: any) => {
    const startTime = Date.now()
    const { pathname, search } = request.nextUrl
    const requestId = request.headers.get('X-Request-Id') || `api_${Date.now()}`

    try {
      // 记录 API 请求
      logger.info('API 请求开始', {
        requestId,
        path: pathname,
        method: request.method,
        metadata: {
          query: search,
          contentType: request.headers.get('content-type'),
        },
      })

      // 执行处理器
      const response = await handler(request, context)

      // 记录响应
      const duration = Date.now() - startTime
      logger.api(
        request.method,
        pathname,
        response.status,
        duration,
        { requestId }
      )

      // 添加响应头
      response.headers.set('X-Request-Id', requestId)
      response.headers.set('X-Response-Time', `${duration}ms`)

      return response
    } catch (error) {
      const duration = Date.now() - startTime

      // 记录错误
      logger.error('API 请求失败', {
        requestId,
        path: pathname,
        method: request.method,
        error: error as Error,
        duration,
      })

      // 序列化错误响应
      const statusCode = getErrorStatusCode(error)
      const errorResponse = serializeError(error)

      return NextResponse.json(errorResponse, {
        status: statusCode,
        headers: {
          'X-Request-Id': requestId,
          'X-Response-Time': `${duration}ms`,
        },
      })
    }
  }
}

/**
 * 验证请求体
 */
export async function validateRequestBody<T>(
  request: NextRequest,
  schema: {
    validate: (data: any) => { valid: boolean; errors?: string[] }
  }
): Promise<T> {
  try {
    const body = await request.json()
    const validation = schema.validate(body)

    if (!validation.valid) {
      throw new AppError(
        '请求数据验证失败',
        400,
        true,
        { errors: validation.errors }
      )
    }

    return body as T
  } catch (error) {
    if (error instanceof AppError) {
      throw error
    }
    throw new AppError('无效的请求数据', 400, true)
  }
}

/**
 * 速率限制装饰器
 */
const rateLimitMap = new Map<string, { count: number; resetTime: number }>()

export function withRateLimit(
  limit: number = 10,
  windowMs: number = 60000
): (handler: ApiHandler) => ApiHandler {
  return (handler: ApiHandler) => {
    return async (request: NextRequest, context?: any) => {
      const ip = request.ip || request.headers.get('x-forwarded-for') || 'unknown'
      const key = `${ip}:${request.nextUrl.pathname}`
      const now = Date.now()

      const rateLimit = rateLimitMap.get(key)

      if (!rateLimit || now > rateLimit.resetTime) {
        rateLimitMap.set(key, {
          count: 1,
          resetTime: now + windowMs,
        })
      } else if (rateLimit.count >= limit) {
        logger.warn('请求被速率限制', {
          path: request.nextUrl.pathname,
          metadata: { ip, limit, windowMs },
        })

        return NextResponse.json(
          { error: { message: '请求过于频繁，请稍后再试' } },
          {
            status: 429,
            headers: {
              'Retry-After': String(Math.ceil((rateLimit.resetTime - now) / 1000)),
            },
          }
        )
      } else {
        rateLimit.count++
      }

      return handler(request, context)
    }
  }
}