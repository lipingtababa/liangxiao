// Mock remark modules before importing posts
jest.mock('remark', () => ({
  remark: jest.fn(() => ({
    use: jest.fn().mockReturnThis(),
    process: jest.fn((content) =>
      Promise.resolve({
        toString: () => `<h1>Test Content</h1>\n<p>This is a test paragraph.</p>`,
      })
    ),
  })),
}))

jest.mock('remark-html', () => jest.fn())

import fs from 'fs'
import path from 'path'
import { getSortedPostsData, getAllPostIds, getPostData } from '../../lib/posts'

// Mock fs module
jest.mock('fs')

describe('Posts Library', () => {
  const mockPostsDir = path.join(process.cwd(), 'posts')

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks()
  })

  describe('getSortedPostsData', () => {
    it('应该返回空数组当posts目录不存在时', () => {
      fs.existsSync.mockReturnValue(false)
      fs.mkdirSync.mockImplementation(() => {})

      const result = getSortedPostsData()

      expect(fs.mkdirSync).toHaveBeenCalledWith(mockPostsDir, { recursive: true })
      expect(result).toEqual([])
    })

    it('应该返回按日期排序的文章列表', () => {
      fs.existsSync.mockReturnValue(true)
      fs.readdirSync.mockReturnValue(['post1.md', 'post2.md', 'readme.txt'])

      fs.readFileSync.mockImplementation((filePath) => {
        if (filePath.includes('post1.md')) {
          return `---
title: Post 1
date: '2024-01-01'
---
Content 1`
        }
        if (filePath.includes('post2.md')) {
          return `---
title: Post 2
date: '2024-01-02'
---
Content 2`
        }
      })

      const result = getSortedPostsData()

      expect(result).toHaveLength(2)
      expect(result[0].id).toBe('post2')
      expect(result[0].title).toBe('Post 2')
      expect(result[1].id).toBe('post1')
      expect(result[1].title).toBe('Post 1')
    })
  })

  describe('getAllPostIds', () => {
    it('应该返回空数组当posts目录不存在时', () => {
      fs.existsSync.mockReturnValue(false)

      const result = getAllPostIds()

      expect(result).toEqual([])
    })

    it('应该返回所有文章ID的参数对象', () => {
      fs.existsSync.mockReturnValue(true)
      fs.readdirSync.mockReturnValue(['post1.md', 'post2.md', 'readme.txt'])

      const result = getAllPostIds()

      expect(result).toHaveLength(2)
      expect(result[0]).toEqual({ params: { id: 'post1' } })
      expect(result[1]).toEqual({ params: { id: 'post2' } })
    })
  })

  describe('getPostData', () => {
    it('应该返回处理后的文章数据和HTML内容', async () => {
      const mockContent = `---
title: Test Post
date: '2024-01-01'
author: Test Author
---

# Test Content

This is a test paragraph.`

      fs.readFileSync.mockReturnValue(mockContent)

      const result = await getPostData('test-post')

      expect(result.id).toBe('test-post')
      expect(result.title).toBe('Test Post')
      expect(result.date).toBe('2024-01-01')
      expect(result.author).toBe('Test Author')
      expect(result.contentHtml).toContain('<h1>Test Content</h1>')
      expect(result.contentHtml).toContain('<p>This is a test paragraph.</p>')
    })
  })
})
