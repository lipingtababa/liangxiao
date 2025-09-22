import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

const postsDirectory = path.join(process.cwd(), 'posts')

export interface PostData {
  id: string
  title: string
  date: string
  content?: string
  contentHtml?: string
  category?: string
  author?: string
  tags?: string[]
  description?: string
  image?: string
  originalUrl?: string
}

export function getSortedPostsData(): PostData[] {
  if (!fs.existsSync(postsDirectory)) {
    fs.mkdirSync(postsDirectory, { recursive: true })
    return []
  }

  const fileNames = fs.readdirSync(postsDirectory).filter((fn) => fn.endsWith('.md'))

  const allPostsData = fileNames.map((fileName) => {
    const id = fileName.replace(/\.md$/, '')
    const fullPath = path.join(postsDirectory, fileName)
    const fileContents = fs.readFileSync(fullPath, 'utf8')
    const matterResult = matter(fileContents)

    return {
      id,
      ...matterResult.data,
    } as PostData
  })

  return allPostsData.sort((a, b) => {
    if (a.date < b.date) {
      return 1
    } else {
      return -1
    }
  })
}

export function getAllPostIds() {
  if (!fs.existsSync(postsDirectory)) {
    return []
  }

  const fileNames = fs.readdirSync(postsDirectory).filter((fn) => fn.endsWith('.md'))

  return fileNames.map((fileName) => {
    return {
      params: {
        id: fileName.replace(/\.md$/, ''),
      },
    }
  })
}

export function getPostData(id: string): PostData {
  const fullPath = path.join(postsDirectory, `${id}.md`)
  const fileContents = fs.readFileSync(fullPath, 'utf8')
  const matterResult = matter(fileContents)

  // 直接返回结果，确保 content 字段设置正确
  return {
    id,
    title: matterResult.data.title || '',
    date: matterResult.data.date || '',
    author: matterResult.data.author,
    category: matterResult.data.category,
    tags: matterResult.data.tags,
    description: matterResult.data.description,
    image: matterResult.data.image,
    originalUrl: matterResult.data.originalUrl,
    // 重要：确保 content 和 contentHtml 都设置为 markdown 内容
    content: matterResult.content || '',
    contentHtml: matterResult.content || '',
  }
}
