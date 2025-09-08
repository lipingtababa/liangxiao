export default function GuidesPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">生活指南</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-3">居住许可</h2>
          <p className="text-gray-600">申请和续签瑞典居住许可的完整指南</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-3">医疗保健</h2>
          <p className="text-gray-600">了解瑞典医疗系统和就医流程</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-3">教育系统</h2>
          <p className="text-gray-600">瑞典教育体系介绍和入学指南</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-3">工作求职</h2>
          <p className="text-gray-600">在瑞典找工作的技巧和资源</p>
        </div>
      </div>
    </div>
  )
}