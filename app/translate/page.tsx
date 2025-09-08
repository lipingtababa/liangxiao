'use client'

import { useState } from 'react'

export default function TranslatePage() {
  const [url, setUrl] = useState('')
  const [isTranslating, setIsTranslating] = useState(false)

  const handleTranslate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url) return
    
    setIsTranslating(true)
    // TODO: 实现翻译功能
    console.log('翻译URL:', url)
    setTimeout(() => {
      setIsTranslating(false)
      alert('翻译功能正在开发中...')
    }, 1000)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">文章翻译工具</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleTranslate} className="space-y-4">
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
              微信文章URL
            </label>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://mp.weixin.qq.com/..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={isTranslating}
            className={`w-full py-2 px-4 rounded-md text-white font-medium ${
              isTranslating 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isTranslating ? '正在翻译...' : '开始翻译'}
          </button>
        </form>
        
        <div className="mt-6 p-4 bg-blue-50 rounded-md">
          <h3 className="font-semibold text-gray-900 mb-2">使用说明：</h3>
          <ol className="list-decimal list-inside text-sm text-gray-700 space-y-1">
            <li>复制微信公众号文章的链接</li>
            <li>粘贴到上方输入框中</li>
            <li>点击"开始翻译"按钮</li>
            <li>等待系统处理并生成英文版本</li>
          </ol>
        </div>
      </div>
    </div>
  )
}