import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '瑞典马工 - Swedish Ma Gong',
  description: '瑞典生活经验分享 - Swedish life experience sharing',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body className={inter.className}>
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold">瑞典马工</h1>
              </div>
            </div>
          </div>
        </nav>
        <main className="min-h-screen bg-gray-50">{children}</main>
        <footer className="bg-white border-t mt-auto">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <p className="text-center text-gray-500 text-sm">© 2024 瑞典马工. 保留所有权利。</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
