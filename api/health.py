"""Enhanced health check endpoints with comprehensive logging."""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import psutil
import os
import sys

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
    Enhanced health check endpoint with detailed system info.
    
    Returns:
        Dict with health status and comprehensive system information
    """
    logger.debug("Health check requested")
    check_start = datetime.now()
    
    # Check LangChain imports
    logger.debug("Checking LangChain status...")
    try:
        import langchain
        langchain_status = "healthy"
        langchain_version = langchain.__version__
        logger.debug(f"✓ LangChain: {langchain_version}")
    except ImportError as e:
        langchain_status = "unhealthy"
        langchain_version = None
        logger.warning(f"✗ LangChain import failed: {e}")
    
    logger.debug("Checking LangGraph status...")
    try:
        import langgraph
        langgraph_status = "healthy"
        langgraph_version = "imported"  # LangGraph doesn't have __version__
        logger.debug("✓ LangGraph: imported")
    except ImportError as e:
        langgraph_status = "unhealthy"
        langgraph_version = None
        logger.warning(f"✗ LangGraph import failed: {e}")
    
    # Check OpenAI connectivity (basic import check)
    logger.debug("Checking OpenAI SDK status...")
    try:
        import openai
        openai_status = "healthy"
        openai_version = openai.__version__
        logger.debug(f"✓ OpenAI: {openai_version}")
    except ImportError as e:
        openai_status = "unhealthy"
        openai_version = None
        logger.warning(f"✗ OpenAI import failed: {e}")
    
    # Check poller service status
    logger.debug("Checking poller service status...")
    poller_status = "not_initialized"
    poller_health = None
    if _poller_service:
        try:
            if _poller_service.poller_enabled:
                poller_health = await _poller_service.get_health()
                if poller_health.get("healthy"):
                    poller_status = "healthy"
                    logger.debug("✓ Poller service: healthy")
                else:
                    poller_status = "unhealthy"
                    error_msg = poller_health.get('message', 'unknown error')
                    logger.warning(f"✗ Poller service unhealthy: {error_msg}")
            else:
                poller_status = "disabled"
                logger.debug("Poller service: disabled")
        except Exception as e:
            poller_status = "error"
            logger.error(f"✗ Poller service check failed: {e}")
    else:
        logger.debug("Poller service: not initialized")
    
    # Get system resource information
    logger.debug("Collecting system resource information...")
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        system_resources = {
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory_info.percent, 2),
            "memory_available_gb": round(memory_info.available / (1024**3), 2),
            "disk_percent": round(disk_info.percent, 2),
            "disk_free_gb": round(disk_info.free / (1024**3), 2)
        }
        logger.debug(f"System resources: CPU={cpu_percent}%, MEM={memory_info.percent}%")
    except Exception as e:
        logger.warning(f"Failed to get system resources: {e}")
        system_resources = {"error": "Failed to retrieve system resources"}
    
    # Calculate check duration
    check_duration_ms = (datetime.now() - check_start).total_seconds() * 1000
    
    response = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AI Orchestrator",
        "version": "0.1.0",
        "uptime_seconds": int((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()),
        "check_duration_ms": round(check_duration_ms, 2),
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "pid": os.getpid()
        },
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
        },
        "system_resources": system_resources
    }
    
    # Overall status based on dependencies
    unhealthy_deps = [name for name, dep in response["dependencies"].items() 
                      if dep.get("status") != "healthy"]
    
    if unhealthy_deps:
        response["status"] = "degraded"
        response["unhealthy_dependencies"] = unhealthy_deps
        logger.warning(f"Health check: DEGRADED - unhealthy dependencies: {unhealthy_deps}")
    else:
        logger.info(f"Health check: HEALTHY (duration={check_duration_ms:.2f}ms)")
    
    return response


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Enhanced readiness check endpoint.
    
    Returns:
        Dict indicating if service is ready to handle requests
    """
    logger.debug("Readiness check requested")
    
    # Perform health check
    health_response = await health_check()
    
    # Additional readiness criteria
    ready = health_response["status"] == "healthy"
    ready_checks = {
        "dependencies": health_response["status"] == "healthy",
        "poller_service": health_response["services"]["poller"]["status"] in ["healthy", "disabled"],
        "system_resources": health_response.get("system_resources", {}).get("error") is None
    }
    
    # Check if all readiness criteria are met
    all_ready = all(ready_checks.values())
    
    if all_ready:
        logger.info("✓ Readiness check: READY")
    else:
        failed_checks = [check for check, status in ready_checks.items() if not status]
        logger.warning(f"✗ Readiness check: NOT READY - failed checks: {failed_checks}")
    
    return {
        "ready": all_ready,
        "status": health_response["status"],
        "timestamp": health_response["timestamp"],
        "checks": ready_checks,
        "check_duration_ms": health_response.get("check_duration_ms")
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Simple liveness check endpoint.
    
    Returns:
        Dict indicating if service is alive
    """
    logger.debug("Liveness check requested")
    
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid()
    }