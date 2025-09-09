/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['mmbiz.qpic.cn', 'mmbiz.qlogo.cn'], // WeChat image domains
  },
  typescript: {
    // 在开发期间允许构建即使有类型错误
    ignoreBuildErrors: false,
  },
  eslint: {
    // 在构建期间运行ESLint
    ignoreDuringBuilds: false,
  },
}

module.exports = nextConfig
