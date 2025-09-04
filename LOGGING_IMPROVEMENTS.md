# SCT Service Logging Enhancements

## Overview
Comprehensive logging improvements have been implemented to make the SCT service easier to debug and monitor, especially addressing issues with black box E2E tests and service startup debugging.

## Key Improvements

### 1. Enhanced Logging Configuration (`core/logging.py`)
- **Structured Logging**: JSON-formatted logs for better parsing and analysis
- **Colored Console Output**: Color-coded log levels for better readability
- **Request Tracking**: Context-aware logging with request IDs
- **Dual Log Files**: Separate production and debug log files
- **Log Context Manager**: Scoped logging context for better traceability

### 2. Comprehensive Startup Logging (`main.py`)
- Detailed startup sequence logging with visual indicators
- Component initialization status (LangChain, OpenAI, etc.)
- Configuration logging with sensitive data masking
- Service readiness indicators with URLs
- Graceful shutdown logging

### 3. Enhanced Webhook Processing (`api/webhooks.py`)
- Request ID tracking for all webhook requests
- Detailed payload validation logging
- Webhook history tracking (last 100 requests)
- Success/failure status tracking
- Performance metrics (processing time)

### 4. Workflow Orchestrator Logging (`workflows/orchestrator.py`)
- Workflow lifecycle logging (start, execution, completion)
- Performance metrics (execution time)
- Error tracking with detailed context
- State change notifications
- Resource cleanup logging

### 5. Health Check Enhancements (`api/health.py`)
- System resource monitoring (CPU, memory, disk)
- Dependency health checks
- Service uptime tracking
- Performance metrics (check duration)
- Separate liveness and readiness endpoints

### 6. Debug API Endpoints (`api/debug.py`)

#### `/api/debug/status`
Comprehensive service status including:
- Service uptime and configuration
- Active workflows and statistics
- Recent webhook requests
- System resources
- Logging configuration

#### `/api/debug/logs`
Query recent log entries with:
- Line count control
- Log level filtering
- Text search capability
- Structured log parsing

#### `/api/debug/log-level`
Dynamically change log levels without restart

#### `/api/debug/metrics`
Service metrics for monitoring systems:
- Process metrics (CPU, memory, threads)
- Workflow statistics
- Webhook success rates

### 7. Request Tracking Middleware
- Automatic request ID generation
- Request/response timing
- Method and path logging
- Error tracking with duration
- Context propagation to all logs

## Log Levels and Usage

### DEBUG
- Detailed diagnostic information
- Variable values and state changes
- Function entry/exit points
- Configuration details

### INFO
- Normal operation events
- Successful completions
- Service state changes
- Important milestones

### WARNING
- Recoverable errors
- Performance issues
- Deprecated usage
- Unusual but handled conditions

### ERROR
- Unrecoverable errors
- Failed operations
- Exception details
- Service degradation

## Configuration

### Environment Variables
```bash
# Set debug mode for verbose logging
DEBUG=true

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=DEBUG
```

### Log Files
- **Production Log**: `logs/orchestrator.log`
- **Debug Log**: `logs/debug_orchestrator.log` (always DEBUG level)
- **Structured Format**: JSON for easy parsing

## Usage Examples

### Starting the Service
```bash
python main.py
```

The service will output comprehensive startup information:
```
============================================================
AI Orchestrator v0.1.0 Starting
============================================================
  environment: DEBUG
  port: 8000
  github_token: ghp_****************************wxyz (masked)
  ...
============================================================
✓ APPLICATION STARTUP COMPLETED SUCCESSFULLY
✓ Service is ready at http://0.0.0.0:8000
✓ API Documentation: http://0.0.0.0:8000/docs
✓ Health Check: http://0.0.0.0:8000/health
✓ Webhook Endpoint: http://0.0.0.0:8000/api/webhook/github
============================================================
```

### Checking Service Status
```bash
curl http://localhost:8000/api/debug/status
```

### Viewing Recent Logs
```bash
curl "http://localhost:8000/api/debug/logs?lines=50&level=ERROR"
```

### Changing Log Level
```bash
curl -X POST http://localhost:8000/api/debug/log-level -d "level=DEBUG"
```

## Benefits for Debugging

1. **Clear Startup Sequence**: Easy to identify where service startup fails
2. **Request Tracing**: Follow requests through the entire system
3. **Performance Monitoring**: Identify slow operations
4. **Error Context**: Detailed error information with full context
5. **Resource Monitoring**: Track memory and CPU usage
6. **Webhook History**: Debug webhook processing issues
7. **Dynamic Configuration**: Change log levels without restart

## Testing

Run the comprehensive test suite:
```bash
python test_enhanced_logging.py
```

The test suite covers:
- Basic logging functionality
- Request tracking
- Context managers
- Startup logging
- Structured logging
- Async logging
- Sensitive data masking
- Log file verification

## Best Practices

1. **Use Request Context**: Always set request context for traceability
2. **Log at Appropriate Levels**: Use DEBUG for details, INFO for operations
3. **Include Timing**: Log duration for performance-critical operations
4. **Mask Sensitive Data**: Never log passwords, tokens, or secrets
5. **Use Structured Logging**: Include metadata as structured fields
6. **Monitor Resources**: Regular health checks for system resources
7. **Clean Up Old Logs**: Implement log rotation for production

## Troubleshooting

### Service Won't Start
- Check startup logs for component initialization failures
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check configuration in `.env` file

### Webhook Processing Issues
- Check `/api/debug/status` for recent webhook errors
- Review webhook history for patterns
- Verify signature validation in logs

### Performance Issues
- Check `/api/debug/metrics` for resource usage
- Review execution times in workflow logs
- Monitor system resources via health endpoint

### Missing Logs
- Verify log directory exists and is writable
- Check log level configuration
- Ensure logging handlers are properly configured

## Dependencies Added
- `psutil>=5.9.0` - System resource monitoring

## Files Modified/Created
- `/Users/Shared/code/SyntheticCodingTeam/core/logging.py` - Enhanced logging system
- `/Users/Shared/code/SyntheticCodingTeam/main.py` - Startup logging and middleware
- `/Users/Shared/code/SyntheticCodingTeam/api/webhooks.py` - Webhook tracking
- `/Users/Shared/code/SyntheticCodingTeam/api/health.py` - Health monitoring
- `/Users/Shared/code/SyntheticCodingTeam/api/debug.py` - Debug endpoints (NEW)
- `/Users/Shared/code/SyntheticCodingTeam/workflows/orchestrator.py` - Workflow logging
- `/Users/Shared/code/SyntheticCodingTeam/test_enhanced_logging.py` - Test suite (NEW)
- `/Users/Shared/code/SyntheticCodingTeam/requirements.txt` - Added psutil