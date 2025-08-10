import Head from 'next/head'
import Link from 'next/link'
import { getSortedPostsData } from '../lib/posts'
import { format } from 'date-fns'

export default function Home({ allPostsData }) {
  return (
    <div className="container">
      <Head>
        <title>Swedish Ma Gong - 瑞典马工</title>
        <meta name="description" content="Translated articles from 瑞典马工 WeChat official account for international readers" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <header className="header">
          <h1 className="title">Swedish Ma Gong</h1>
          <p className="subtitle">瑞典马工 - Insights from Sweden for International Readers</p>
        </header>

        <section className="posts">
          {allPostsData.length === 0 ? (
            <p className="no-posts">No articles yet. Check back soon!</p>
          ) : (
            <ul className="post-list">
              {allPostsData.map(({ id, date, title, excerpt, originalTitle }) => (
                <li key={id} className="post-item">
                  <Link href={`/posts/${id}`}>
                    <h2>{title}</h2>
                    {originalTitle && (
                      <p className="original-title">Original: {originalTitle}</p>
                    )}
                    {excerpt && <p className="excerpt">{excerpt}</p>}
                    <time className="date">
                      {format(new Date(date), 'MMMM d, yyyy')}
                    </time>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>
          Translated from <a href="https://mp.weixin.qq.com" target="_blank" rel="noopener noreferrer">瑞典马工 WeChat Official Account</a>
        </p>
      </footer>

      <style jsx>{`
        .container {
          max-width: 800px;
          margin: 0 auto;
          padding: 0 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }

        .header {
          text-align: center;
          padding: 60px 0 40px;
          border-bottom: 1px solid #eee;
        }

        .title {
          font-size: 3rem;
          margin: 0 0 10px;
          color: #333;
        }

        .subtitle {
          font-size: 1.2rem;
          color: #666;
          margin: 0;
        }

        .posts {
          padding: 40px 0;
        }

        .no-posts {
          text-align: center;
          color: #666;
          font-size: 1.1rem;
          padding: 40px 0;
        }

        .post-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .post-item {
          margin-bottom: 40px;
          padding-bottom: 40px;
          border-bottom: 1px solid #eee;
        }

        .post-item:last-child {
          border-bottom: none;
        }

        .post-item a {
          text-decoration: none;
          color: inherit;
          display: block;
        }

        .post-item h2 {
          font-size: 1.8rem;
          margin: 0 0 10px;
          color: #333;
          transition: color 0.2s;
        }

        .post-item a:hover h2 {
          color: #0066cc;
        }

        .original-title {
          font-size: 0.9rem;
          color: #999;
          margin: 5px 0 15px;
        }

        .excerpt {
          color: #666;
          line-height: 1.6;
          margin: 15px 0;
        }

        .date {
          color: #999;
          font-size: 0.9rem;
        }

        .footer {
          text-align: center;
          padding: 40px 0 60px;
          border-top: 1px solid #eee;
          color: #666;
        }

        .footer a {
          color: #0066cc;
          text-decoration: none;
        }

        .footer a:hover {
          text-decoration: underline;
        }

        @media (max-width: 600px) {
          .title {
            font-size: 2rem;
          }
          
          .subtitle {
            font-size: 1rem;
          }
          
          .post-item h2 {
            font-size: 1.4rem;
          }
        }
      `}</style>
    </div>
  )
}

export async function getStaticProps() {
  const allPostsData = getSortedPostsData()
  return {
    props: {
      allPostsData,
    },
  }
}