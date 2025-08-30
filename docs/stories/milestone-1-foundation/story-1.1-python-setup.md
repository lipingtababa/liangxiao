# Story 1.1: Python Project Setup ✅ COMPLETED

## Story Details
- **ID**: 1.1
- **Title**: Initialize Python/LangChain Project Structure
- **Milestone**: Milestone 1 - Foundation & Basic Workflow
- **Points**: 3
- **Priority**: P0 (Critical Path)
- **Dependencies**: None (First story)
- **Status**: ✅ COMPLETED - Full Python project structure with Poetry, Docker, and FastAPI implemented

## Description

### Overview
Set up the foundational Python project structure that will replace the current problematic TypeScript single-agent system. This story establishes the development environment, dependency management, and basic project structure for the new LangChain-based multi-agent system.

### Why This Is Important
- The current TypeScript agent produces terrible code (see PR #23 disaster)
- Python/LangChain provides better AI agent support
- Proper foundation prevents future technical debt
- Development environment consistency across team

### Context
We're moving from a monolithic TypeScript agent to a sophisticated Python-based multi-agent system. This first story lays the groundwork for all future development.

## Acceptance Criteria

### Required
- [ ] Docker-first development environment with multi-stage Dockerfile
- [ ] Docker Compose setup for development with hot reloading
- [ ] Python 3.11+ project initialized with proper structure
- [ ] FastAPI application scaffold created with basic health check endpoint
- [ ] LangChain and LangGraph dependencies installed and importable
- [ ] Development environment configured with hot reloading in Docker
- [ ] Basic logging system configured using Python's logging module
- [ ] Configuration management using Pydantic settings
- [ ] `.env.example` file with all required environment variables documented
- [ ] README.md with Docker-based setup instructions
- [ ] Basic error handling middleware configured
- [ ] Type hints used throughout the codebase
- [ ] Basic unit test structure with pytest running in Docker
- [ ] Pre-commit hooks for code formatting (black, isort) in Docker

## Technical Details

### Docker-First Development Setup

#### Multi-stage Dockerfile
```dockerfile
# Dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root

# Production stage
FROM python:3.11-slim as production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM production as development

USER root

# Install development dependencies
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Install development tools
RUN pip install debugpy

USER app

# Override for development with hot reloading
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### Docker Compose for Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  orchestrator:
    build:
      context: .
      target: development
    container_name: orchestrator-dev
    ports:
      - "8000:8000"
      - "5678:5678"  # debugpy port
    volumes:
      - .:/app
      - /app/.venv  # Exclude virtual environment
    environment:
      - PYTHONPATH=/app
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
    env_file:
      - .env
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - redis
      - postgres
    networks:
      - orchestrator-network

  redis:
    image: redis:7-alpine
    container_name: orchestrator-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - orchestrator-network

  postgres:
    image: postgres:15-alpine
    container_name: orchestrator-postgres
    environment:
      POSTGRES_DB: orchestrator
      POSTGRES_USER: orchestrator
      POSTGRES_PASSWORD: orchestrator_password
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - orchestrator-network

volumes:
  redis-data:
  postgres-data:

networks:
  orchestrator-network:
    driver: bridge
```

### Project Structure
```
services/
└── orchestrator/
    ├── __init__.py
    ├── main.py                 # FastAPI application entry point
    ├── config.py               # Pydantic settings configuration
    ├── api/
    │   ├── __init__.py
    │   ├── health.py           # Health check endpoint
    │   └── webhooks.py         # Placeholder for webhook endpoints
    ├── core/
    │   ├── __init__.py
    │   ├── logging.py          # Logging configuration
    │   └── exceptions.py       # Custom exceptions
    ├── agents/                 # Placeholder for agent modules
    │   └── __init__.py
    ├── workflows/              # Placeholder for LangGraph workflows
    │   └── __init__.py
    └── tests/
        ├── __init__.py
        └── test_health.py      # Basic health check test
```

### Key Dependencies (pyproject.toml or requirements.txt)
```python
# Core
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"

# AI/LangChain
langchain = "^0.1.0"
langgraph = "^0.0.20"
langchain-openai = "^0.0.5"
openai = "^1.10.0"

# Utilities
python-dotenv = "^1.0.0"
httpx = "^0.25.0"

# Development
pytest = "^7.4.0"
black = "^23.0.0"
isort = "^5.12.0"
```

### Configuration Schema (config.py)
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    app_name: str = "AI Orchestrator"
    debug: bool = False
    port: int = 8000
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    
    # GitHub
    github_token: str
    github_webhook_secret: str
    
    # LangChain
    langchain_tracing_v2: bool = True
    langchain_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
```

### Basic FastAPI App (main.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Settings
from api.health import router as health_router
import logging

settings = Settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Coding Team Orchestrator",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, tags=["health"])

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name}")
    # Verify LangChain imports work
    from langchain import __version__ as lc_version
    from langgraph import __version__ as lg_version
    logger.info(f"LangChain: {lc_version}, LangGraph: {lg_version}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
```

## Testing Requirements

### Unit Tests
```python
# tests/test_health.py
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_langchain_import():
    from langchain import __version__
    assert __version__ is not None

def test_configuration():
    from config import Settings
    settings = Settings(openai_api_key="test", github_token="test")
    assert settings.app_name == "AI Orchestrator"
```

### Manual Testing Checklist
- [ ] `python main.py` starts the server
- [ ] Health endpoint returns 200 OK
- [ ] Hot reloading works when code changes
- [ ] Environment variables load correctly
- [ ] Logs appear in console
- [ ] LangChain imports successfully

## Dependencies & Risks

### Prerequisites
- Python 3.11+ installed
- Git repository access
- OpenAI API key for testing
- GitHub token for future integration

### Risks
- **Version conflicts**: Ensure LangChain/LangGraph compatibility
- **Environment issues**: Different OS/Python versions may cause issues
- **API keys**: Ensure .env is never committed

### Mitigations
- Use virtual environment (venv or conda)
- Pin exact versions in requirements
- Add .env to .gitignore immediately
- Document system requirements clearly

## Definition of Done

1. ✅ All acceptance criteria met
2. ✅ Code follows Python PEP-8 standards
3. ✅ Type hints on all functions
4. ✅ Basic tests pass
5. ✅ README includes setup instructions
6. ✅ Can run `uvicorn main:app --reload` successfully
7. ✅ Health check endpoint responds
8. ✅ No hardcoded secrets in code
9. ✅ Committed to git with meaningful message

## Implementation Notes for AI Agents

### DO
- Use pathlib for file paths, not string concatenation
- Include proper error handling from the start
- Use async/await for all endpoint handlers
- Follow FastAPI best practices
- Create separate modules for different concerns

### DON'T
- Don't put everything in one file
- Don't skip type hints
- Don't hardcode configuration values
- Don't forget to test imports work
- Don't create unnecessary complexity

### Common Pitfalls to Avoid
1. Wrong Python version - must be 3.11+
2. Missing __init__.py files in packages
3. Circular imports between modules
4. Not using virtual environment
5. Forgetting to add dependencies to requirements

## Success Example

When complete, you should be able to:
```bash
# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python main.py
# Server starts on http://localhost:8000
# Health check at http://localhost:8000/health

# Test
pytest tests/
# All tests pass
```

## Next Story
Once this story is complete, proceed to [Story 1.2: GitHub Webhook Migration](story-1.2-webhook-migration.md)