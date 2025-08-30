"""Health check endpoints."""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Global reference to poller service for health checks
_poller_service = None

def set_poller_service(poller_service):
    """Set poller service reference for health checks."""
    global _poller_service
    _poller_service = poller_service


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        Dict with health status and system information
    """
    logger.debug("Health check requested")
    
    # Check LangChain imports
    try:
        import langchain
        langchain_status = "ok"
        langchain_version = langchain.__version__
    except ImportError as e:
        langchain_status = f"error: {e}"
        langchain_version = None
    
    try:
        import langgraph
        langgraph_status = "ok"
        langgraph_version = "imported"  # LangGraph doesn't have __version__
    except ImportError as e:
        langgraph_status = f"error: {e}"
        langgraph_version = None
    
    # Check OpenAI connectivity (basic import check)
    try:
        import openai
        openai_status = "ok"
        openai_version = openai.__version__
    except ImportError as e:
        openai_status = f"error: {e}"
        openai_version = None
    
    # Check poller service status
    poller_status = "not_initialized"
    poller_health = None
    if _poller_service:
        try:
            poller_status = "enabled" if _poller_service.poller_enabled else "disabled"
            if _poller_service.poller_enabled:
                poller_health = await _poller_service.get_health()
                if poller_health.get("healthy"):
                    poller_status = "healthy"
                else:
                    poller_status = f"unhealthy: {poller_health.get('message', 'unknown error')}"
        except Exception as e:
            poller_status = f"error: {e}"
    
    response = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AI Orchestrator",
        "version": "0.1.0",
        "dependencies": {
            "langchain": {
                "status": langchain_status,
                "version": langchain_version
            },
            "langgraph": {
                "status": langgraph_status,
                "version": langgraph_version
            },
            "openai": {
                "status": openai_status,
                "version": openai_version
            }
        },
        "services": {
            "poller": {
                "status": poller_status,
                "health": poller_health
            }
        }
    }
    
    # Overall status based on dependencies
    if any("error" in str(dep.get("status", "")) for dep in response["dependencies"].values()):
        response["status"] = "degraded"
    
    return response


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint.
    
    Returns:
        Dict indicating if service is ready to handle requests
    """
    # For now, same as health check
    # In future stories, this will check:
    # - Database connectivity
    # - GitHub API connectivity  
    # - Workflow engine status
    
    health_response = await health_check()
    
    return {
        "ready": health_response["status"] == "healthy",
        "status": health_response["status"],
        "timestamp": health_response["timestamp"]
    }