import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Swedish Ma Gong - 瑞典马工',
  description: 'Translated articles from 瑞典马工 WeChat official account for international readers',
  keywords: ['Sweden', 'Ma Gong', '瑞典马工', 'translation', 'blog'],
  authors: [{ name: 'Swedish Ma Gong' }],
  openGraph: {
    title: 'Swedish Ma Gong - 瑞典马工',
    description: 'Translated articles from 瑞典马工 WeChat official account for international readers',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-white text-gray-900">
        {children}
      </body>
    </html>
  )
}