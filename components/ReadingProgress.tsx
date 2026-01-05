'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { usePathname } from 'next/navigation'

interface ReadingProgressProps {
  postId: string
  children: React.ReactNode
}

export default function ReadingProgress({ postId, children }: ReadingProgressProps) {
  const [showContinueReading, setShowContinueReading] = useState(false)
  const [savedPosition, setSavedPosition] = useState<number | null>(null)
  const pathname = usePathname()
  const scrollTimeoutRef = useRef<NodeJS.Timeout>()
  const hasRestoredRef = useRef(false)

  // 获取存储键名
  const getStorageKey = () => `reading-progress-${postId}`

  // 保存滚动位置
  const saveScrollPosition = useCallback(() => {
    const scrollPercentage = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
    const storageKey = getStorageKey()

    // 只有当滚动位置大于5%时才保存，避免误触
    if (scrollPercentage > 5) {
      localStorage.setItem(storageKey, JSON.stringify({
        percentage: scrollPercentage,
        scrollY: window.scrollY,
        timestamp: Date.now()
      }))
    }
  }, [postId])

  // 恢复滚动位置
  const restoreScrollPosition = useCallback(() => {
    const storageKey = getStorageKey()
    const savedData = localStorage.getItem(storageKey)

    if (savedData) {
      const { percentage, scrollY } = JSON.parse(savedData)

      // 滚动到保存的位置
      window.scrollTo({
        top: scrollY,
        behavior: 'smooth'
      })

      setShowContinueReading(false)
      hasRestoredRef.current = true
    }
  }, [postId])

  // 检查是否有保存的阅读位置
  useEffect(() => {
    const storageKey = getStorageKey()
    const savedData = localStorage.getItem(storageKey)

    if (savedData && !hasRestoredRef.current) {
      const { percentage, scrollY, timestamp } = JSON.parse(savedData)

      // 只有在7天内的阅读记录才显示继续阅读按钮
      const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000)

      if (timestamp > sevenDaysAgo && percentage > 10 && percentage < 95) {
        setSavedPosition(scrollY)
        setShowContinueReading(true)
      }
    }
  }, [postId])

  // 监听滚动事件，定期保存位置
  useEffect(() => {
    const handleScroll = () => {
      // 清除之前的定时器
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current)
      }

      // 设置新的定时器，在用户停止滚动500ms后保存位置
      scrollTimeoutRef.current = setTimeout(() => {
        saveScrollPosition()
      }, 500)
    }

    window.addEventListener('scroll', handleScroll)

    return () => {
      window.removeEventListener('scroll', handleScroll)

      // 清理定时器
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current)
      }
    }
  }, [saveScrollPosition])

  // 页面卸载时保存位置
  useEffect(() => {
    const handleBeforeUnload = () => {
      saveScrollPosition()
    }

    window.addEventListener('beforeunload', handleBeforeUnload)

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [saveScrollPosition])

  return (
    <>
      {/* 继续阅读提示条 */}
      {showContinueReading && savedPosition && (
        <div className="fixed top-0 left-0 right-0 bg-gradient-to-r from-blue-600 to-blue-500 text-white py-3 px-4 shadow-lg z-50 animate-slide-down">
          <div className="max-w-3xl mx-auto flex items-center justify-between">
            <span className="text-sm font-medium" style={{ fontFamily: 'Inter, sans-serif' }}>
              欢迎回来！您上次阅读到了这篇文章的中间位置
            </span>
            <div className="flex gap-3">
              <button
                onClick={restoreScrollPosition}
                className="px-4 py-1.5 bg-white text-blue-600 text-sm font-medium rounded-lg hover:bg-blue-50 transition-colors"
                style={{ fontFamily: 'Inter, sans-serif' }}
              >
                继续阅读
              </button>
              <button
                onClick={() => setShowContinueReading(false)}
                className="px-3 py-1.5 text-white/90 hover:text-white text-sm font-medium transition-colors"
                style={{ fontFamily: 'Inter, sans-serif' }}
              >
                从头开始
              </button>
            </div>
          </div>
        </div>
      )}

      {children}
    </>
  )
}