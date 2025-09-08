import Link from 'next/link'

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          欢迎来到瑞典马工
        </h2>
        <p className="text-lg text-gray-600">
          分享瑞典生活经验，传递实用信息
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-2">最新文章</h3>
          <p className="text-gray-600 mb-4">
            浏览最新发布的文章和资讯
          </p>
          <Link href="/posts" className="text-blue-600 hover:text-blue-800">
            查看所有文章 →
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-2">生活指南</h3>
          <p className="text-gray-600 mb-4">
            瑞典生活实用信息和建议
          </p>
          <Link href="/guides" className="text-blue-600 hover:text-blue-800">
            浏览指南 →
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-2">关于我们</h3>
          <p className="text-gray-600 mb-4">
            了解瑞典马工的故事
          </p>
          <Link href="/about" className="text-blue-600 hover:text-blue-800">
            了解更多 →
          </Link>
        </div>
      </div>

      <div className="mt-12 bg-blue-50 rounded-lg p-8">
        <h3 className="text-2xl font-semibold mb-4">翻译工具</h3>
        <p className="text-gray-700 mb-4">
          使用我们的翻译工具将微信文章转换为英文版本
        </p>
        <Link 
          href="/translate" 
          className="inline-block bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
        >
          开始翻译
        </Link>
      </div>
    </div>
  )
}