/**
 * 自定义错误类和错误处理工具
 */

import { logger } from './logger'

// 基础应用错误类
export class AppError extends Error {
  public readonly statusCode: number
  public readonly isOperational: boolean
  public readonly details?: any

  constructor(
    message: string,
    statusCode: number = 500,
    isOperational: boolean = true,
    details?: any
  ) {
    super(message)
    this.statusCode = statusCode
    this.isOperational = isOperational
    this.details = details

    Object.setPrototypeOf(this, AppError.prototype)
    Error.captureStackTrace(this, this.constructor)
  }
}

// 具体错误类型
export class ValidationError extends AppError {
  constructor(message: string, details?: any) {
    super(message, 400, true, details)
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} 未找到`, 404, true)
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = '未授权访问') {
    super(message, 401, true)
  }
}

export class ForbiddenError extends AppError {
  constructor(message: string = '禁止访问') {
    super(message, 403, true)
  }
}

export class RateLimitError extends AppError {
  constructor(message: string = '请求过于频繁，请稍后再试') {
    super(message, 429, true)
  }
}

export class ExternalServiceError extends AppError {
  constructor(service: string, originalError?: Error) {
    super(`外部服务错误: ${service}`, 503, false, { originalError })
  }
}

// 错误处理工具函数
export function isOperationalError(error: Error): boolean {
  if (error instanceof AppError) {
    return error.isOperational
  }
  return false
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return '发生未知错误'
}

export function getErrorStatusCode(error: unknown): number {
  if (error instanceof AppError) {
    return error.statusCode
  }
  return 500
}

// 错误序列化（用于API响应）
export function serializeError(error: unknown) {
  const isDevelopment = process.env.NODE_ENV === 'development'

  if (error instanceof AppError) {
    return {
      error: {
        message: error.message,
        statusCode: error.statusCode,
        details: isDevelopment ? error.details : undefined,
        stack: isDevelopment ? error.stack : undefined,
      },
    }
  }

  if (error instanceof Error) {
    return {
      error: {
        message: isDevelopment ? error.message : '服务器内部错误',
        statusCode: 500,
        stack: isDevelopment ? error.stack : undefined,
      },
    }
  }

  return {
    error: {
      message: '发生未知错误',
      statusCode: 500,
    },
  }
}

// 异步错误包装器
export function asyncHandler<T extends (...args: any[]) => Promise<any>>(fn: T): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await fn(...args)
    } catch (error) {
      logger.error('异步操作失败', {
        error: error as Error,
        metadata: {
          function: fn.name,
          args: process.env.NODE_ENV === 'development' ? args : undefined,
        },
      })
      throw error
    }
  }) as T
}

// 重试机制
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number
    delay?: number
    backoff?: number
    onRetry?: (error: Error, attempt: number) => void
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    delay = 1000,
    backoff = 2,
    onRetry,
  } = options

  let lastError: Error

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error

      if (attempt === maxRetries) {
        logger.error('重试失败，已达最大次数', {
          error: lastError,
          metadata: { attempts: maxRetries },
        })
        throw lastError
      }

      const waitTime = delay * Math.pow(backoff, attempt - 1)

      logger.warn(`操作失败，${waitTime}ms 后重试`, {
        error: lastError,
        metadata: { attempt, maxRetries, waitTime },
      })

      if (onRetry) {
        onRetry(lastError, attempt)
      }

      await new Promise(resolve => setTimeout(resolve, waitTime))
    }
  }

  throw lastError!
}