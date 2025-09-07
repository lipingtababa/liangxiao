"""FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import time
import uuid
import logging
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables before any other imports that might need them
import core.env_loader  # This automatically loads .env at import time

from config import Settings
from core.unified_logging import setup_unified_logging, get_unified_logger
from core.exceptions import OrchestratorError
from api.health import router as health_router
from api.webhooks import router as webhooks_router
from api.debug import router as debug_router

# Initialize settings
try:
    settings = Settings()
except Exception as e:
    print(f"Failed to load settings: {e}")
    sys.exit(1)

# Setup unified logging - defaults to stdout + optional file
setup_unified_logging(
    level="DEBUG" if settings.debug else "INFO",
    file_path="logs/sct.log"
)

logger = get_unified_logger(__name__)



# Create FastAPI app  
app = FastAPI(
    title="AI Coding Team Orchestrator",
    description="Multi-agent system for automated coding tasks",
    version="0.1.0",
    debug=settings.debug
)

# Startup and shutdown events using the older API
@app.on_event("startup")
async def startup_event():
    """Simple application startup event."""
    
    # Log startup
    logger.info("=" * 60)
    logger.info(f"{settings.app_name} v0.1.0 Starting")
    logger.info("=" * 60)
    logger.info(f"Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"Host: 0.0.0.0")
    
    # Check configuration
    github_secret = "✓" if settings.github_webhook_secret else "✗"
    openai_key = "✓" if settings.openai_api_key else "✗"
    github_token = "✓" if settings.github_personal_access_token else "✗"
    
    logger.info(f"GitHub Webhook Secret: {github_secret}")
    logger.info(f"OpenAI API Key: {openai_key}")
    logger.info(f"GitHub Token: {github_token}")
    
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(settings.workspace_root, exist_ok=True)
    
    
    # Final status
    logger.info("=" * 60)
    logger.info("✓ APPLICATION STARTUP COMPLETED")
    logger.info(f"✓ Service ready at http://0.0.0.0:{settings.port}")
    logger.info(f"✓ Webhook: http://0.0.0.0:{settings.port}/api/webhook/github")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event with detailed logging."""
    
    # Shutdown logging
    logger.info("="*60)
    logger.info("Initiating application shutdown sequence...")
    
    
    logger.info("✓ SHUTDOWN SEQUENCE COMPLETED")
    logger.info("="*60)

# Add request tracking middleware
@app.middleware("http")
async def request_tracking_middleware(request: Request, call_next):
    """Track all incoming requests with unique IDs and timing."""
    
    # Generate or extract request ID
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    
    # Simple request tracking
    
    # Log incoming request
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    # Track timing
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Add headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = str(round(duration_ms, 2))
        
        # Log completion
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration_ms:.2f}ms"
        )
        
        return response
        
    except Exception as e:
        # Calculate duration even for errors
        duration_ms = (time.time() - start_time) * 1000
        
        # Log error
        logger.error(
            f"Request failed: {request.method} {request.url.path} - "
            f"Error: {type(e).__name__}: {e} - Duration: {duration_ms:.2f}ms",
            exc_info=True
        )
        
        # Re-raise the exception
        raise
        
    finally:
        # Request completed
        pass


# CORS middleware removed - causing FastAPI middleware unpacking error

# Exception handler for our custom exceptions
@app.exception_handler(OrchestratorError)
async def orchestrator_exception_handler(request, exc: OrchestratorError):
    """Handle custom orchestrator exceptions."""
    logger.error(f"Orchestrator error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.message,
            "code": exc.code,
            "type": "orchestrator_error"
        }
    )

# Include routers
app.include_router(health_router, tags=["health"])
app.include_router(webhooks_router, prefix="/api", tags=["webhooks"])
app.include_router(debug_router, tags=["debug"])




@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AI Coding Team Orchestrator",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Log pre-startup info
    logger.info("="*60)
    logger.info("Preparing to start Uvicorn server...")
    logger.info(f"Host: 0.0.0.0")
    logger.info(f"Port: {settings.port}")
    logger.info(f"Auto-reload: {settings.debug}")
    logger.info(f"Log level: {'debug' if settings.debug else 'info'}")
    logger.info("="*60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=True
    )