import type { Metadata } from 'next'
import './globals.css'
import { siteConfig, generateWebSiteSchema, generateOrganizationSchema } from '@/lib/seo'
import Script from 'next/script'


export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: siteConfig.title,
    template: '%s | MaGong',
  },
  description: siteConfig.description,
  keywords: siteConfig.keywords,
  authors: [{ name: siteConfig.author }],
  creator: siteConfig.author,
  publisher: siteConfig.author,
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    title: siteConfig.title,
    description: siteConfig.description,
    url: siteConfig.url,
    siteName: siteConfig.title,
    locale: siteConfig.locale,
    type: 'website',
    images: [
      {
        url: siteConfig.ogImage,
        width: 1200,
        height: 630,
        alt: siteConfig.title,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: siteConfig.title,
    description: siteConfig.description,
    site: siteConfig.twitter,
    creator: siteConfig.twitter,
    images: [siteConfig.twitterImage],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: siteConfig.url,
    languages: {
      'en-US': siteConfig.url,
    },
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const websiteSchema = generateWebSiteSchema()
  const organizationSchema = generateOrganizationSchema()

  return (
    <html lang="en">
      <head>
        <Script
          id="website-schema"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteSchema) }}
        />
        <Script
          id="organization-schema"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
      </head>
      <body>
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <a href="/" className="text-xl font-semibold text-gray-900 hover:text-gray-700" style={{ fontFamily: 'Inter, sans-serif' }}>MaGong</a>
              </div>
              <nav className="flex items-center space-x-6">
                <a href="/posts" className="text-gray-600 hover:text-gray-900 text-sm font-medium" style={{ fontFamily: 'Inter, sans-serif' }}>Articles</a>
                <a href="https://agentmanagementforum.com/" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900 text-sm font-medium" style={{ fontFamily: 'Inter, sans-serif' }}>Forum</a>
              </nav>
            </div>
          </div>
        </header>
        <main className="min-h-screen bg-white">{children}</main>
        <footer className="bg-white border-t border-gray-200 mt-24">
          <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
            <p className="text-center text-gray-500 text-sm" style={{ fontFamily: 'Inter, sans-serif' }}>© 2024 MaGong. All rights reserved.</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
