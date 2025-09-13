'use client'

import React, { Component, ReactNode } from 'react'
import { logger } from '@/lib/logger'
import { monitoring } from '@/lib/monitoring'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // 记录错误到日志系统
    logger.error('组件错误边界捕获错误', {
      error,
      metadata: {
        componentStack: errorInfo.componentStack,
        pathname: typeof window !== 'undefined' ? window.location.pathname : undefined,
      },
    })

    // 报告到监控服务
    monitoring.reportError(error, {
      componentStack: errorInfo.componentStack,
      type: 'react-error-boundary',
    })

    // 调用自定义错误处理器
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  render() {
    if (this.state.hasError) {
      // 自定义错误UI或使用默认
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex flex-col items-center justify-center min-h-[300px] p-8 bg-red-50 rounded-lg">
          <svg
            className="w-16 h-16 text-red-500 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            组件加载错误
          </h3>
          <p className="text-gray-600 text-center mb-4">
            抱歉，这个组件遇到了问题。请刷新页面重试。
          </p>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details className="w-full max-w-lg">
              <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                查看错误详情
              </summary>
              <pre className="mt-2 p-4 bg-gray-100 rounded text-xs overflow-auto">
                {this.state.error.toString()}
              </pre>
            </details>
          )}
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            刷新页面
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook 版本的错误边界包装器
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode
) {
  return function WithErrorBoundaryComponent(props: P) {
    return (
      <ErrorBoundary fallback={fallback}>
        <Component {...props} />
      </ErrorBoundary>
    )
  }
}