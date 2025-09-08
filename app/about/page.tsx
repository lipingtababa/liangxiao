export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">关于瑞典马工</h1>
      <div className="prose prose-lg">
        <p className="text-gray-700 mb-4">
          瑞典马工是一个专门为在瑞典生活的华人提供实用信息和生活经验分享的平台。
        </p>
        <p className="text-gray-700 mb-4">
          我们的使命是帮助新来瑞典的朋友更快地适应当地生活，并为已经在瑞典生活的朋友提供有价值的信息交流平台。
        </p>
        <h2 className="text-2xl font-semibold mt-6 mb-4">我们提供什么</h2>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li>最新的瑞典生活资讯</li>
          <li>实用的生活指南和建议</li>
          <li>文化交流和经验分享</li>
          <li>中英文双语内容服务</li>
        </ul>
      </div>
    </div>
  )
}