# Improved SCT Startup and Testing Guide

## Overview

We've significantly improved the SyntheticCodingTeam (SCT) service with comprehensive logging, simplified startup tools, and robust E2E testing capabilities.

## Key Improvements

### 1. Enhanced Logging System

The Python developer agent added comprehensive logging throughout the codebase:

- **Structured JSON logging** for better parsing and analysis
- **Request ID tracking** across all operations
- **Colored console output** for development
- **Sensitive data masking** for security
- **Context-aware logging** with performance metrics

Key files:
- `core/logging.py` - Enhanced logging configuration
- `api/debug.py` - Debug endpoints for monitoring

### 2. Debug API Endpoints

New endpoints for monitoring and debugging:

- `/api/debug/status` - Complete service status with metrics
- `/api/debug/logs` - Query recent log entries
- `/api/debug/log-level` - Dynamically change log levels
- `/api/debug/metrics` - Service performance metrics

### 3. Simplified Startup Tools

#### Quick Start Script (`start.sh`)

```bash
# Start locally
./start.sh

# Start with Docker
./start.sh --docker

# Start with Docker Compose
./start.sh --docker-compose

# Start on custom port
./start.sh --port 8001
```

#### Python Starter Helper (`scripts/start_sct.py`)

```bash
# Start with monitoring
python scripts/start_sct.py --monitor

# Start with Docker
python scripts/start_sct.py --docker

# Start on custom port
python scripts/start_sct.py --port 8001
```

### 4. Docker Support

- **Dockerfile**: Multi-stage build for production and development
- **docker-compose.yml**: Complete stack with Redis and PostgreSQL
- **Health checks**: Automatic service health monitoring
- **Volume mounts**: Persistent data and logs

### 5. Black Box E2E Testing

#### PR Validation Test (`test_pr_validation.py`)

Pure validation test that checks GitHub for PRs:

```bash
python test_pr_validation.py
```

This test:
- Searches for PRs related to issue #21
- Validates PR quality (checks for disasters)
- Works without starting SCT service

#### Complete E2E Test (`test_blackbox_e2e.py`)

Full black box test that:
1. Starts SCT service
2. Sends webhook to `/api/webhook/github`
3. Polls GitHub for PR creation
4. Validates PR quality

```bash
python test_blackbox_e2e.py
```

#### E2E with Improved Starter (`test_e2e_with_starter.py`)

Uses the new startup helper for reliable testing:

```bash
python test_e2e_with_starter.py
```

## How to Use

### 1. Basic Setup

Ensure your `.env` file contains:
```env
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...
OPENAI_API_KEY=sk-...
GITHUB_WEBHOOK_SECRET=...
GITHUB_OWNER=lipingtababa
GITHUB_REPO=liangxiao
```

### 2. Start the Service

Choose your preferred method:

```bash
# Quick and easy
./start.sh

# With monitoring
python scripts/start_sct.py --monitor

# Production with Docker
./start.sh --docker-compose
```

### 3. Monitor Service

Check service status:
```bash
# Health check
curl http://localhost:8000/health

# Debug status
curl http://localhost:8000/api/debug/status

# Recent logs
curl http://localhost:8000/api/debug/logs?limit=10

# View documentation
open http://localhost:8000/docs
```

### 4. Run E2E Tests

Validate PR submission:
```bash
# Check if PR exists for issue #21
python test_pr_validation.py

# Full E2E test
python test_blackbox_e2e.py

# E2E with improved starter
python test_e2e_with_starter.py
```

## Key Benefits

1. **Easy Debugging**: Comprehensive logging shows exactly what's happening
2. **Simple Startup**: One command to start the entire system
3. **Docker Support**: Consistent deployment across environments
4. **Robust Testing**: Black box E2E tests validate actual GitHub integration
5. **Monitoring**: Debug endpoints provide real-time insights

## Troubleshooting

### Service Won't Start

1. Check port availability:
```bash
lsof -i:8000
```

2. Check logs:
```bash
tail -f sct.log  # Local
docker-compose logs -f orchestrator  # Docker Compose
```

3. Verify environment:
```bash
python -c "from config import Settings; s=Settings(); print(s)"
```

### Webhook Not Processing

1. Check webhook history:
```bash
curl http://localhost:8000/api/debug/status | jq .recent_webhooks
```

2. Verify signature:
- Ensure `GITHUB_WEBHOOK_SECRET` matches GitHub settings

3. Check logs:
```bash
curl "http://localhost:8000/api/debug/logs?level=ERROR"
```

### PR Not Created

1. Run validation test:
```bash
python test_pr_validation.py
```

2. Check workflow status:
```bash
curl http://localhost:8000/api/workflows
```

3. Monitor agents:
- Check logs for agent processing
- Verify GitHub token has necessary permissions

## Summary

The improvements make SCT much easier to:
- **Start**: Simple commands with clear feedback
- **Debug**: Comprehensive logging and monitoring
- **Test**: Black box E2E validation of PR submission
- **Deploy**: Docker support for consistent environments

The system now provides full visibility into operations and reliable startup/testing procedures.