import { notFound } from 'next/navigation'
import { getPostData, getAllPostIds } from '../../../lib/posts'
import { format } from 'date-fns'

interface PostData {
  id: string
  title: string
  date: string
  contentHtml: string
  originalTitle?: string
  originalUrl?: string
}

// 生成静态路径
export async function generateStaticParams() {
  const paths = getAllPostIds()
  return paths.map((path) => ({
    id: path.params.id,
  }))
}

// 生成页面元数据
export async function generateMetadata({ params }: { params: { id: string } }) {
  try {
    const postData: PostData = await getPostData(params.id)
    return {
      title: `${postData.title} - Swedish Ma Gong`,
      description: postData.title,
    }
  } catch {
    return {
      title: 'Post Not Found - Swedish Ma Gong',
    }
  }
}

export default async function Post({ params }: { params: { id: string } }) {
  let postData: PostData

  try {
    postData = await getPostData(params.id)
  } catch {
    notFound()
  }

  return (
    <div className="container-custom">
      <article className="py-12">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-4 text-gray-800">
            {postData.title}
          </h1>
          {postData.originalTitle && (
            <p className="text-lg text-gray-600 mb-4">
              原文标题: {postData.originalTitle}
            </p>
          )}
          <time className="text-gray-500">
            {format(new Date(postData.date), 'MMMM d, yyyy')}
          </time>
        </header>

        <div 
          className="prose prose-lg max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-a:text-primary hover:prose-a:underline"
          dangerouslySetInnerHTML={{ __html: postData.contentHtml }} 
        />

        {postData.originalUrl && (
          <footer className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              原文链接:{' '}
              <a 
                href={postData.originalUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                {postData.originalUrl}
              </a>
            </p>
          </footer>
        )}
      </article>

      <nav className="py-8 border-t border-gray-200">
        <a 
          href="/"
          className="inline-flex items-center text-primary hover:underline"
        >
          ← Back to Home
        </a>
      </nav>
    </div>
  )
}