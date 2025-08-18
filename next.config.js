/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['mmbiz.qpic.cn', 'mmbiz.qlogo.cn'], // WeChat image domains
  },
  typescript: {
    // 在生产构建时运行类型检查
    ignoreBuildErrors: false,
  },
  eslint: {
    // 在生产构建时运行 ESLint
    ignoreDuringBuilds: false,
  },
}

module.exports = nextConfig