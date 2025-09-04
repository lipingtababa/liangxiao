"""Debug endpoints for monitoring and troubleshooting the service."""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import os
import psutil
import sys

from core.logging import get_logger
from config import Settings

logger = get_logger(__name__)
router = APIRouter()
settings = Settings()

# Import webhook tracking functions
from api.webhooks import get_recent_webhooks, orchestrator

# Track service start time
SERVICE_START_TIME = datetime.utcnow()


def mask_sensitive_value(key: str, value: Any) -> Any:
    """Mask sensitive configuration values."""
    sensitive_keys = ['token', 'key', 'secret', 'password', 'credential']
    
    if any(sensitive in key.lower() for sensitive in sensitive_keys):
        if value and isinstance(value, str):
            if len(value) > 8:
                return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"
            else:
                return "*" * len(value)
    
    return value


def get_service_uptime() -> Dict[str, Any]:
    """Get service uptime information."""
    uptime = datetime.utcnow() - SERVICE_START_TIME
    
    return {
        "started_at": SERVICE_START_TIME.isoformat(),
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_human": str(uptime).split('.')[0],
        "current_time": datetime.utcnow().isoformat()
    }


def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    try:
        process = psutil.Process(os.getpid())
        
        # CPU and memory for this process
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_info = process.memory_info()
        
        # System-wide resources
        system_cpu = psutil.cpu_percent(interval=0.1)
        system_memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        return {
            "process": {
                "pid": os.getpid(),
                "cpu_percent": round(cpu_percent, 2),
                "memory_mb": round(memory_info.rss / (1024 * 1024), 2),
                "threads": process.num_threads(),
                "open_files": len(process.open_files())
            },
            "system": {
                "cpu_percent": round(system_cpu, 2),
                "cpu_count": psutil.cpu_count(),
                "memory_percent": round(system_memory.percent, 2),
                "memory_available_gb": round(system_memory.available / (1024**3), 2),
                "disk_percent": round(disk_usage.percent, 2),
                "disk_free_gb": round(disk_usage.free / (1024**3), 2)
            },
            "python": {
                "version": sys.version.split()[0],
                "platform": sys.platform,
                "executable": sys.executable
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {"error": str(e)}


def get_configuration_info() -> Dict[str, Any]:
    """Get sanitized configuration information."""
    config_dict = {}
    
    # Get all settings attributes
    for key in dir(settings):
        if not key.startswith('_'):
            try:
                value = getattr(settings, key)
                
                # Skip methods and complex objects
                if callable(value):
                    continue
                    
                # Handle dictionaries
                if isinstance(value, dict):
                    masked_dict = {}
                    for k, v in value.items():
                        masked_dict[k] = mask_sensitive_value(k, v)
                    config_dict[key] = masked_dict
                else:
                    config_dict[key] = mask_sensitive_value(key, value)
                    
            except Exception as e:
                config_dict[key] = f"<error: {e}>"
    
    return config_dict


def get_logging_info() -> Dict[str, Any]:
    """Get information about logging configuration."""
    root_logger = logging.getLogger()
    
    handlers_info = []
    for handler in root_logger.handlers:
        handler_info = {
            "type": type(handler).__name__,
            "level": logging.getLevelName(handler.level)
        }
        
        if hasattr(handler, 'baseFilename'):
            handler_info["file"] = handler.baseFilename
            
        handlers_info.append(handler_info)
    
    return {
        "root_level": logging.getLevelName(root_logger.level),
        "handlers": handlers_info,
        "log_directory": "logs",
        "log_files": [
            "logs/orchestrator.log",
            "logs/debug_orchestrator.log"
        ]
    }


@router.get("/api/debug/status")
async def debug_status() -> Dict[str, Any]:
    """
    Comprehensive debug status endpoint.
    
    Returns detailed information about:
    - Service status and uptime
    - Active workflows
    - Recent webhook requests
    - System resources
    - Configuration (with secrets masked)
    - Logging setup
    """
    logger.info("Debug status requested")
    
    try:
        # Get workflow information
        workflows = orchestrator.get_active_workflows()
        workflow_stats = orchestrator.get_stats()
        
        # Get recent webhooks
        recent_webhooks = get_recent_webhooks()
        
        # Organize webhooks by status
        webhook_summary = {
            "total": len(recent_webhooks),
            "by_status": {},
            "by_event": {},
            "recent_errors": []
        }
        
        for webhook in recent_webhooks:
            # Count by status
            status = webhook.get("status", "unknown")
            webhook_summary["by_status"][status] = webhook_summary["by_status"].get(status, 0) + 1
            
            # Count by event type
            event_type = webhook.get("event_type", "unknown")
            webhook_summary["by_event"][event_type] = webhook_summary["by_event"].get(event_type, 0) + 1
            
            # Collect recent errors
            if webhook.get("error") and len(webhook_summary["recent_errors"]) < 5:
                webhook_summary["recent_errors"].append({
                    "delivery_id": webhook.get("delivery_id"),
                    "event_type": webhook.get("event_type"),
                    "error": webhook.get("error"),
                    "timestamp": webhook.get("timestamp")
                })
        
        # Build response
        response = {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "service": {
                "name": settings.app_name,
                "version": "0.1.0",
                "environment": "DEBUG" if settings.debug else "PRODUCTION",
                "uptime": get_service_uptime()
            },
            "workflows": {
                "active": workflows,
                "statistics": workflow_stats,
                "summary": {
                    "total_active": len(workflows),
                    "by_status": workflow_stats.get("status_counts", {})
                }
            },
            "webhooks": {
                "recent": recent_webhooks[-10:],  # Last 10 webhooks
                "summary": webhook_summary
            },
            "system": get_system_info(),
            "configuration": get_configuration_info(),
            "logging": get_logging_info(),
            "endpoints": {
                "health": "/health",
                "readiness": "/health/ready",
                "liveness": "/health/live",
                "webhooks": "/api/webhook/github",
                "workflows": "/api/workflows",
                "docs": "/docs",
                "openapi": "/openapi.json"
            }
        }
        
        logger.info(f"Debug status generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate debug status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate debug status: {str(e)}"
        )


@router.get("/api/debug/logs")
async def get_recent_logs(
    lines: int = 100,
    level: Optional[str] = None,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recent log entries.
    
    Args:
        lines: Number of lines to return (default 100, max 1000)
        level: Filter by log level (DEBUG, INFO, WARNING, ERROR)
        search: Search term to filter log lines
    
    Returns:
        Recent log entries matching the criteria
    """
    logger.debug(f"Recent logs requested: lines={lines}, level={level}, search={search}")
    
    # Validate parameters
    lines = min(max(lines, 1), 1000)  # Limit between 1 and 1000
    
    try:
        log_file = "logs/orchestrator.log"
        
        if not os.path.exists(log_file):
            return {
                "error": "Log file not found",
                "log_file": log_file,
                "logs": []
            }
        
        # Read log file
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
        
        # Get last N lines
        recent_lines = all_lines[-lines:]
        
        # Filter by level if specified
        if level and level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            recent_lines = [line for line in recent_lines if level.upper() in line]
        
        # Filter by search term if specified
        if search:
            recent_lines = [line for line in recent_lines if search.lower() in line.lower()]
        
        # Parse structured logs if present
        parsed_logs = []
        for line in recent_lines:
            try:
                # Try to parse as JSON (structured log)
                import json
                log_entry = json.loads(line.strip())
                parsed_logs.append(log_entry)
            except:
                # Fall back to raw line
                parsed_logs.append({"raw": line.strip()})
        
        return {
            "log_file": log_file,
            "total_lines": len(all_lines),
            "returned_lines": len(parsed_logs),
            "filters": {
                "lines": lines,
                "level": level,
                "search": search
            },
            "logs": parsed_logs
        }
        
    except Exception as e:
        logger.error(f"Failed to read logs: {e}", exc_info=True)
        return {
            "error": f"Failed to read logs: {str(e)}",
            "logs": []
        }


@router.post("/api/debug/log-level")
async def set_log_level(level: str) -> Dict[str, Any]:
    """
    Dynamically change the log level.
    
    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Confirmation of log level change
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    if level.upper() not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid log level. Must be one of: {', '.join(valid_levels)}"
        )
    
    try:
        new_level = getattr(logging, level.upper())
        root_logger = logging.getLogger()
        old_level = root_logger.level
        
        root_logger.setLevel(new_level)
        
        # Also update all handlers
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                # Keep console at INFO minimum for production
                if level.upper() == "DEBUG" or settings.debug:
                    handler.setLevel(new_level)
                else:
                    handler.setLevel(logging.INFO)
            else:
                handler.setLevel(new_level)
        
        logger.warning(f"Log level changed from {logging.getLevelName(old_level)} to {level.upper()}")
        
        return {
            "success": True,
            "old_level": logging.getLevelName(old_level),
            "new_level": level.upper(),
            "message": f"Log level changed to {level.upper()}"
        }
        
    except Exception as e:
        logger.error(f"Failed to change log level: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to change log level: {str(e)}"
        )


@router.get("/api/debug/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get service metrics for monitoring.
    
    Returns:
        Service metrics in a format suitable for monitoring systems
    """
    logger.debug("Metrics requested")
    
    try:
        # Get system metrics
        process = psutil.Process(os.getpid())
        
        # Get workflow metrics
        workflow_stats = orchestrator.get_stats()
        
        # Get webhook metrics
        recent_webhooks = get_recent_webhooks()
        webhook_success_count = sum(1 for w in recent_webhooks if w.get("status") == "success")
        webhook_error_count = sum(1 for w in recent_webhooks if w.get("status") == "failed")
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": {
                "uptime_seconds": int((datetime.utcnow() - SERVICE_START_TIME).total_seconds()),
                "version": "0.1.0"
            },
            "process": {
                "cpu_percent": round(process.cpu_percent(interval=0.1), 2),
                "memory_mb": round(process.memory_info().rss / (1024 * 1024), 2),
                "threads": process.num_threads(),
                "open_files": len(process.open_files())
            },
            "workflows": {
                "total_active": workflow_stats.get("total_workflows", 0),
                "running": workflow_stats.get("status_counts", {}).get("running", 0),
                "completed": workflow_stats.get("status_counts", {}).get("completed", 0),
                "failed": workflow_stats.get("status_counts", {}).get("failed", 0),
                "avg_execution_seconds": workflow_stats.get("average_execution_time_seconds", 0)
            },
            "webhooks": {
                "total_recent": len(recent_webhooks),
                "success": webhook_success_count,
                "errors": webhook_error_count,
                "success_rate": round(webhook_success_count / len(recent_webhooks) * 100, 2) if recent_webhooks else 0
            }
        }
        
        logger.debug(f"Metrics generated: {metrics}")
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate metrics: {str(e)}"
        )