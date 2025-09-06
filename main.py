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
from core.logging import (
    setup_logging, get_logger, log_startup_info,
    set_request_id, set_request_context, clear_request_context,
    LogContext
)
from core.exceptions import OrchestratorError
from api.health import router as health_router, set_poller_service
from api.webhooks import router as webhooks_router
from api.debug import router as debug_router
from services.poller_service import PollerService

# Initialize settings
try:
    settings = Settings()
except Exception as e:
    print(f"Failed to load settings: {e}")
    sys.exit(1)

# Setup enhanced logging with structured output
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

setup_logging(
    level="DEBUG" if settings.debug else "INFO",
    log_file=f"{log_dir}/orchestrator.log",
    structured=True
)

logger = get_logger(__name__)

# Initialize poller service
poller_service = None


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
    """Application startup event with comprehensive logging."""
    
    # Set startup context
    with LogContext(request_id="startup", phase="initialization"):
        
        # Log comprehensive startup information
        log_startup_info(
            logger,
            service_name=settings.app_name,
            version="0.1.0",
            environment="DEBUG" if settings.debug else "PRODUCTION",
            port=settings.port,
            host="0.0.0.0",
            github_owner=settings.github_owner,
            github_repo=settings.github_repo,
            webhook_secret=settings.github_webhook_secret,
            github_token=settings.github_token,
            poller_enabled=settings.poller_enabled,
            poll_interval=f"{settings.poll_interval_seconds}s",
            required_labels=settings.required_issue_labels or "None",
            workspace_root=settings.workspace_root,
            max_concurrent_workspaces=settings.max_concurrent_workspaces,
            ai_tools=settings.agent_tools,
            log_level="DEBUG" if settings.debug else "INFO"
        )
        
        logger.info("Starting service initialization sequence...")
    
        # Verify LangChain imports work
        logger.info("Verifying LangChain dependencies...")
        try:
            import langchain
            import langgraph
            logger.info(f"✓ LangChain version: {langchain.__version__}")
            logger.info("✓ LangGraph: Imported successfully")
            set_request_context(langchain_version=langchain.__version__)
        except ImportError as e:
            logger.error(f"✗ Failed to import LangChain/LangGraph: {e}")
            raise
    
        # Verify OpenAI import
        logger.info("Verifying OpenAI SDK...")
        try:
            import openai
            logger.info(f"✓ OpenAI SDK version: {openai.__version__}")
            set_request_context(openai_version=openai.__version__)
        except ImportError as e:
            logger.error(f"✗ Failed to import OpenAI: {e}")
            raise
    
        # Create required directories
        logger.info("Setting up directory structure...")
        directories = ["data", "logs", settings.workspace_root]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"✓ Directory ensured: {directory}")
    
        # Initialize and start poller service
        global poller_service
        if settings.poller_enabled:
            logger.info("Initializing GitHub poller service...")
            try:
                poller_service = PollerService(
                    github_token=settings.github_token,
                    github_owner=settings.github_owner,
                    github_repo=settings.github_repo,
                    poll_interval_seconds=settings.poll_interval_seconds,
                    poller_state_file=settings.poller_state_file,
                    required_issue_labels=settings.required_issue_labels,
                    poller_enabled=settings.poller_enabled
                )
                
                logger.debug(f"Poller configuration: owner={settings.github_owner}, repo={settings.github_repo}, interval={settings.poll_interval_seconds}s")
                
                # Start poller as background task
                task = asyncio.create_task(poller_service.start_background())
                logger.info(f"✓ GitHub poller service started (task_id={id(task)})")
                
                # Register poller service with health endpoint
                set_poller_service(poller_service)
                logger.debug("✓ Poller service registered with health endpoint")
                
                set_request_context(poller_status="active", poller_task_id=id(task))
                
            except Exception as e:
                logger.error(f"✗ Failed to start poller service: {e}", exc_info=True)
                logger.warning("Continuing without poller - webhooks will still work")
                set_request_context(poller_status="failed", poller_error=str(e))
        else:
            logger.info("GitHub poller is disabled by configuration")
            set_request_context(poller_status="disabled")
    
        # Log final startup status
        logger.info("="*60)
        logger.info("✓ APPLICATION STARTUP COMPLETED SUCCESSFULLY")
        logger.info(f"✓ Service is ready at http://0.0.0.0:{settings.port}")
        logger.info(f"✓ API Documentation: http://0.0.0.0:{settings.port}/docs")
        logger.info(f"✓ Health Check: http://0.0.0.0:{settings.port}/health")
        logger.info(f"✓ Webhook Endpoint: http://0.0.0.0:{settings.port}/api/webhook/github")
        logger.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event with detailed logging."""
    
    with LogContext(request_id="shutdown", phase="cleanup"):
        logger.info("="*60)
        logger.info("Initiating application shutdown sequence...")
    
        # Shutdown poller service
        global poller_service
        if poller_service:
            logger.info("Shutting down GitHub poller service...")
            try:
                await poller_service.shutdown()
                logger.info("✓ Poller service shutdown complete")
            except Exception as e:
                logger.error(f"✗ Error shutting down poller service: {e}", exc_info=True)
        
        logger.info("✓ SHUTDOWN SEQUENCE COMPLETED")
        logger.info("="*60)

# Add request tracking middleware
@app.middleware("http")
async def request_tracking_middleware(request: Request, call_next):
    """Track all incoming requests with unique IDs and timing."""
    
    # Generate or extract request ID
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    
    # Set request context for logging
    set_request_id(request_id)
    set_request_context(
        method=request.method,
        path=request.url.path,
        client_host=request.client.host if request.client else "unknown"
    )
    
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
        # Clear request context
        clear_request_context()


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