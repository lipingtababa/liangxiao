export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="space-y-4 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p className="text-gray-600">加载中...</p>
      </div>
    </div>
  )
}
