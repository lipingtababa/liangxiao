"""FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Settings
from core.logging import setup_logging, get_logger
from core.exceptions import OrchestratorError
from api.health import router as health_router, set_poller_service
from api.webhooks import router as webhooks_router
from services.poller_service import PollerService

# Initialize settings
try:
    settings = Settings()
except Exception as e:
    print(f"Failed to load settings: {e}")
    sys.exit(1)

# Setup logging
setup_logging(
    level="DEBUG" if settings.debug else "INFO",
    log_file="logs/orchestrator.log" if os.path.exists("logs") else None
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
    """Application startup event."""
    logger.info(f"Starting {settings.app_name} v0.1.0")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Port: {settings.port}")
    
    # Verify LangChain imports work
    try:
        import langchain
        import langgraph
        logger.info(f"LangChain: {langchain.__version__}")
        logger.info("LangGraph imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import LangChain/LangGraph: {e}")
        raise
    
    # Verify OpenAI import
    try:
        import openai
        logger.info(f"OpenAI: {openai.__version__}")
    except ImportError as e:
        logger.error(f"Failed to import OpenAI: {e}")
        raise
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Initialize and start poller service
    global poller_service
    if settings.poller_enabled:
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
            
            # Start poller as background task
            asyncio.create_task(poller_service.start_background())
            
            # Register poller service with health endpoint
            set_poller_service(poller_service)
            
            logger.info("GitHub poller service started as background task")
        except Exception as e:
            logger.error(f"Failed to start poller service: {e}", exc_info=True)
            # Continue without poller - webhooks will still work
    else:
        logger.info("GitHub poller is disabled")
    
    logger.info("Application startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down application")
    
    # Shutdown poller service
    global poller_service
    if poller_service:
        try:
            await poller_service.shutdown()
            logger.info("Poller service shutdown complete")
        except Exception as e:
            logger.error(f"Error shutting down poller service: {e}", exc_info=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    logger.info(f"Starting server on port {settings.port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )