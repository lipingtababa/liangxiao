/**
 * 日志系统配置
 * 提供结构化的日志记录功能
 */

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
  FATAL = 'fatal',
}

export interface LogContext {
  userId?: string
  requestId?: string
  path?: string
  method?: string
  statusCode?: number
  duration?: number
  error?: Error
  metadata?: Record<string, any>
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === 'development'
  private isProduction = process.env.NODE_ENV === 'production'

  private formatMessage(
    level: LogLevel,
    message: string,
    context?: LogContext
  ): string {
    const timestamp = new Date().toISOString()
    const logEntry = {
      timestamp,
      level,
      message,
      ...context,
      error: context?.error
        ? {
            name: context.error.name,
            message: context.error.message,
            stack: this.isDevelopment ? context.error.stack : undefined,
          }
        : undefined,
    }

    if (this.isDevelopment) {
      // 开发环境：格式化输出
      return JSON.stringify(logEntry, null, 2)
    } else {
      // 生产环境：单行JSON
      return JSON.stringify(logEntry)
    }
  }

  private log(level: LogLevel, message: string, context?: LogContext): void {
    const formattedMessage = this.formatMessage(level, message, context)

    switch (level) {
      case LogLevel.DEBUG:
        if (this.isDevelopment) {
          console.debug(formattedMessage)
        }
        break
      case LogLevel.INFO:
        console.info(formattedMessage)
        break
      case LogLevel.WARN:
        console.warn(formattedMessage)
        break
      case LogLevel.ERROR:
      case LogLevel.FATAL:
        console.error(formattedMessage)
        // 在生产环境中，这里可以集成错误监控服务
        if (this.isProduction && context?.error) {
          this.reportToMonitoring(context.error, context)
        }
        break
    }
  }

  private reportToMonitoring(error: Error, context: LogContext): void {
    // 预留接口：集成 Sentry、LogRocket 等监控服务
    // 示例：
    // if (typeof window !== 'undefined' && window.Sentry) {
    //   window.Sentry.captureException(error, {
    //     extra: context,
    //   })
    // }
  }

  debug(message: string, context?: LogContext): void {
    this.log(LogLevel.DEBUG, message, context)
  }

  info(message: string, context?: LogContext): void {
    this.log(LogLevel.INFO, message, context)
  }

  warn(message: string, context?: LogContext): void {
    this.log(LogLevel.WARN, message, context)
  }

  error(message: string, context?: LogContext): void {
    this.log(LogLevel.ERROR, message, context)
  }

  fatal(message: string, context?: LogContext): void {
    this.log(LogLevel.FATAL, message, context)
  }

  // 性能日志
  performance(operation: string, duration: number, context?: LogContext): void {
    const level = duration > 3000 ? LogLevel.WARN : LogLevel.INFO
    this.log(level, `Performance: ${operation}`, {
      ...context,
      duration,
      metadata: {
        ...context?.metadata,
        operation,
      },
    })
  }

  // API 请求日志
  api(
    method: string,
    path: string,
    statusCode: number,
    duration: number,
    context?: LogContext
  ): void {
    const level = statusCode >= 500 ? LogLevel.ERROR : statusCode >= 400 ? LogLevel.WARN : LogLevel.INFO
    this.log(level, `API ${method} ${path} - ${statusCode}`, {
      ...context,
      method,
      path,
      statusCode,
      duration,
    })
  }
}

// 导出单例
export const logger = new Logger()