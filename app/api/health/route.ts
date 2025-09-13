/**
 * 健康检查 API
 * 用于监控服务状态
 */

import { NextRequest, NextResponse } from 'next/server'
import { withErrorHandler } from '@/lib/api-handler'
import { logger } from '@/lib/logger'

export const GET = withErrorHandler(async (request: NextRequest) => {
  const startTime = Date.now()

  // 检查各项服务状态
  const checks = {
    server: 'healthy',
    database: 'healthy', // 实际项目中检查数据库连接
    cache: 'healthy',    // 实际项目中检查缓存连接
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    environment: process.env.NODE_ENV,
  }

  // 计算响应时间
  const responseTime = Date.now() - startTime

  // 记录健康检查
  logger.info('健康检查完成', {
    metadata: {
      responseTime,
      checks,
    },
  })

  return NextResponse.json({
    status: 'healthy',
    checks,
    responseTime: `${responseTime}ms`,
  }, {
    status: 200,
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
    },
  })
})