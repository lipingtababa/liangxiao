'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] px-4">
      <h2 className="text-2xl font-bold mb-4">出错了！</h2>
      <p className="text-gray-600 mb-8">抱歉，发生了一些错误。</p>
      <button
        onClick={() => reset()}
        className="px-6 py-2 bg-primary text-white rounded-md hover:bg-blue-600 transition-colors"
      >
        重试
      </button>
    </div>
  )
}
