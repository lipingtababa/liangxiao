'use client'

import { useEffect } from 'react'
import { logger } from '@/lib/logger'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // 记录全局错误
    logger.fatal('全局错误', {
      error,
      metadata: {
        digest: error.digest,
        pathname: typeof window !== 'undefined' ? window.location.pathname : undefined,
      },
    })
  }, [error])

  return (
    <html>
      <body>
        <div className="flex flex-col items-center justify-center min-h-screen px-4 bg-gray-50">
          <div className="max-w-md w-full text-center">
            <div className="mb-6">
              <svg
                className="w-24 h-24 mx-auto text-red-600"
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
            </div>

            <h1 className="text-3xl font-bold mb-4 text-gray-900">
              系统错误
            </h1>
            <p className="text-gray-600 mb-8">
              非常抱歉，系统遇到了严重错误。我们的团队已经收到通知。
            </p>

            <div className="flex gap-4 justify-center">
              <button
                onClick={() => reset()}
                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                重新加载
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
              >
                返回首页
              </button>
            </div>

            {process.env.NODE_ENV === 'development' && error.message && (
              <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg text-left">
                <p className="text-sm font-mono text-red-800">{error.message}</p>
              </div>
            )}
          </div>
        </div>
      </body>
    </html>
  )
}