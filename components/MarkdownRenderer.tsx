'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeRaw from 'rehype-raw'
import 'highlight.js/styles/github.css'

interface MarkdownRendererProps {
  content: string
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw, rehypeHighlight]}
      components={{
        img: ({ node, src, alt, ...props }) => (
          <img
            src={src}
            alt={alt}
            loading="lazy"
            className="rounded-lg shadow-md max-w-full h-auto"
            {...props}
          />
        ),
        a: ({ node, href, children, ...props }) => (
          <a
            href={href}
            target={href?.startsWith('http') ? '_blank' : undefined}
            rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
            className="text-blue-600 hover:text-blue-800 underline"
            {...props}
          >
            {children}
          </a>
        ),
        blockquote: ({ node, children, ...props }) => (
          <blockquote
            className="border-l-4 border-gray-300 pl-4 italic text-gray-700 my-4"
            {...props}
          >
            {children}
          </blockquote>
        ),
        code: ({ className, children, ...props }: any) => {
          const match = /language-(\w+)/.exec(className || '')
          const isInline = !className
          return !isInline ? (
            <div className="relative">
              {match && (
                <span className="absolute top-0 right-0 px-2 py-1 text-xs text-gray-600 bg-gray-100 rounded-bl">
                  {match[1]}
                </span>
              )}
              <code className={className} {...props}>
                {children}
              </code>
            </div>
          ) : (
            <code className="px-1 py-0.5 text-sm bg-gray-100 rounded text-gray-800" {...props}>
              {children}
            </code>
          )
        },
        pre: ({ node, children, ...props }) => (
          <pre className="overflow-x-auto p-4 bg-gray-50 rounded-lg my-4" {...props}>
            {children}
          </pre>
        ),
        table: ({ node, children, ...props }) => (
          <div className="overflow-x-auto my-4">
            <table className="min-w-full divide-y divide-gray-200" {...props}>
              {children}
            </table>
          </div>
        ),
        thead: ({ node, children, ...props }) => (
          <thead className="bg-gray-50" {...props}>
            {children}
          </thead>
        ),
        th: ({ node, children, ...props }) => (
          <th
            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            {...props}
          >
            {children}
          </th>
        ),
        td: ({ node, children, ...props }) => (
          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900" {...props}>
            {children}
          </td>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
