/**
 * 错误监控和性能追踪配置
 * 可集成 Sentry、LogRocket 等服务
 */

import { logger } from './logger'

interface MonitoringConfig {
  enabled: boolean
  dsn?: string
  environment?: string
  tracesSampleRate?: number
}

class MonitoringService {
  private config: MonitoringConfig

  constructor() {
    this.config = {
      enabled: process.env.NODE_ENV === 'production',
      dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
      environment: process.env.NODE_ENV,
      tracesSampleRate: 0.1,
    }
  }

  /**
   * 初始化监控服务
   */
  async initialize(): Promise<void> {
    if (!this.config.enabled || !this.config.dsn) {
      logger.info('监控服务未启用')
      return
    }

    try {
      // 动态导入 Sentry（示例）
      // const Sentry = await import('@sentry/nextjs')
      //
      // Sentry.init({
      //   dsn: this.config.dsn,
      //   environment: this.config.environment,
      //   tracesSampleRate: this.config.tracesSampleRate,
      //   integrations: [
      //     new Sentry.BrowserTracing(),
      //   ],
      //   beforeSend(event, hint) {
      //     // 过滤敏感信息
      //     if (event.request?.cookies) {
      //       delete event.request.cookies
      //     }
      //     return event
      //   },
      // })

      logger.info('监控服务初始化成功')
    } catch (error) {
      logger.error('监控服务初始化失败', {
        error: error as Error,
      })
    }
  }

  /**
   * 报告错误
   */
  reportError(error: Error, context?: Record<string, any>): void {
    if (!this.config.enabled) return

    try {
      // 发送到监控服务
      // if (typeof window !== 'undefined' && window.Sentry) {
      //   window.Sentry.captureException(error, {
      //     extra: context,
      //   })
      // }

      // 同时记录到日志
      logger.error('监控服务捕获错误', {
        error,
        metadata: context,
      })
    } catch (err) {
      logger.error('监控服务报告错误失败', {
        error: err as Error,
      })
    }
  }

  /**
   * 记录自定义事件
   */
  trackEvent(eventName: string, data?: Record<string, any>): void {
    if (!this.config.enabled) return

    try {
      // 发送到分析服务
      // if (typeof window !== 'undefined' && window.gtag) {
      //   window.gtag('event', eventName, data)
      // }

      logger.info('自定义事件', {
        metadata: {
          event: eventName,
          data,
        },
      })
    } catch (error) {
      logger.error('记录事件失败', {
        error: error as Error,
        metadata: { eventName, data },
      })
    }
  }

  /**
   * 性能监控
   */
  measurePerformance(name: string, fn: () => void | Promise<void>): void {
    const startTime = performance.now()

    const complete = () => {
      const duration = performance.now() - startTime

      logger.performance(name, duration)

      if (duration > 3000) {
        this.reportError(
          new Error(`性能问题: ${name} 耗时 ${duration}ms`),
          { operation: name, duration }
        )
      }
    }

    const result = fn()

    if (result instanceof Promise) {
      result.finally(complete)
    } else {
      complete()
    }
  }

  /**
   * 用户反馈收集
   */
  collectFeedback(feedback: {
    message: string
    email?: string
    name?: string
    metadata?: Record<string, any>
  }): void {
    try {
      // 发送用户反馈
      // if (typeof window !== 'undefined' && window.Sentry) {
      //   const user = { email: feedback.email, name: feedback.name }
      //   window.Sentry.captureMessage(feedback.message, {
      //     level: 'info',
      //     user,
      //     extra: feedback.metadata,
      //   })
      // }

      logger.info('用户反馈', {
        metadata: feedback,
      })
    } catch (error) {
      logger.error('收集反馈失败', {
        error: error as Error,
      })
    }
  }
}

// 导出单例
export const monitoring = new MonitoringService()

// 浏览器端初始化
if (typeof window !== 'undefined') {
  monitoring.initialize()
}