# 错误处理和日志系统文档

## 概述

本项目实现了完整的错误处理机制和结构化日志系统，确保系统稳定性和可维护性。

## 核心功能

### 1. 错误处理体系

#### 自定义错误类型
- `AppError` - 基础应用错误类
- `ValidationError` - 400 验证错误
- `NotFoundError` - 404 资源未找到
- `UnauthorizedError` - 401 未授权
- `ForbiddenError` - 403 禁止访问
- `RateLimitError` - 429 请求限流
- `ExternalServiceError` - 503 外部服务错误

#### 错误页面
- `/app/error.tsx` - 页面级错误处理
- `/app/global-error.tsx` - 全局错误处理
- `/app/not-found.tsx` - 404页面

### 2. 日志系统

#### 日志级别
- `DEBUG` - 调试信息（仅开发环境）
- `INFO` - 一般信息
- `WARN` - 警告信息
- `ERROR` - 错误信息
- `FATAL` - 致命错误

#### 使用示例

```typescript
import { logger } from '@/lib/logger'

// 基础日志
logger.info('用户登录成功', {
  userId: '123',
  metadata: { ip: '192.168.1.1' }
})

// 错误日志
logger.error('数据库连接失败', {
  error: new Error('Connection timeout'),
  metadata: { database: 'postgres' }
})

// 性能日志
logger.performance('数据查询', 150, {
  metadata: { query: 'SELECT * FROM users' }
})

// API日志
logger.api('GET', '/api/posts', 200, 120)
```

### 3. API错误处理

#### 错误处理包装器

```typescript
import { withErrorHandler } from '@/lib/api-handler'

export const GET = withErrorHandler(async (request) => {
  // 你的API逻辑
  // 抛出的错误会被自动捕获和处理
})
```

#### 速率限制

```typescript
import { withRateLimit } from '@/lib/api-handler'

// 限制每分钟5次请求
export const GET = withRateLimit(5, 60000)(handler)
```

### 4. 中间件

全局中间件功能：
- 请求日志记录
- 请求ID生成
- 安全响应头设置
- 性能监控

### 5. 监控集成

预留了与第三方监控服务的集成接口：
- Sentry错误追踪
- Google Analytics事件追踪
- 自定义监控服务

## 配置

### 环境变量

在 `.env.local` 中配置：

```env
# 日志级别
LOG_LEVEL=INFO

# 监控服务（可选）
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
SENTRY_AUTH_TOKEN=your_auth_token

# API限流
API_RATE_LIMIT=100
API_RATE_WINDOW_MS=60000
```

### Vercel部署配置

`vercel.json` 包含了：
- 构建和部署命令
- 函数超时设置
- 安全响应头
- URL重写和重定向规则

## 测试

### 错误处理测试

开发环境下访问：
- `/api/test-error?type=validation` - 测试验证错误
- `/api/test-error?type=notfound` - 测试404错误
- `/api/test-error?type=unauthorized` - 测试401错误
- `/api/test-error?type=external` - 测试外部服务错误
- `/api/test-error?type=runtime` - 测试运行时错误
- `/api/test-error?type=async` - 测试异步错误

### 健康检查

访问 `/api/health` 查看系统状态

## 最佳实践

1. **始终使用自定义错误类**
   ```typescript
   throw new ValidationError('Invalid input', { field: 'email' })
   ```

2. **API路由使用错误处理包装器**
   ```typescript
   export const GET = withErrorHandler(handler)
   ```

3. **记录关键操作**
   ```typescript
   logger.info('关键操作完成', { userId, action: 'delete_post' })
   ```

4. **组件使用ErrorBoundary**
   ```tsx
   <ErrorBoundary>
     <YourComponent />
   </ErrorBoundary>
   ```

5. **异步操作使用重试机制**
   ```typescript
   await withRetry(fetchData, { maxRetries: 3 })
   ```

## 故障排查

1. 检查日志输出 - 开发环境在控制台，生产环境在Vercel日志
2. 查看请求ID - 每个请求都有唯一的 `X-Request-Id`
3. 检查错误详情 - 开发环境会显示完整错误栈
4. 监控服务 - 生产环境错误会发送到配置的监控服务

## 维护

定期检查：
- 错误日志趋势
- API响应时间
- 速率限制触发情况
- 外部服务可用性