"""Unified logging configuration for SyntheticCodingTeam.

This module provides a single, consistent logging setup that should be used
throughout the entire application. All modules should import and use this
logging configuration.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class SCTFormatter(logging.Formatter):
    """Simple, readable formatter for SCT logs."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record in a clean, readable way."""
        # Get timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        
        # Get color for level
        color = self.COLORS.get(record.levelname, '')
        
        # Format: TIME [LEVEL] module.function - message
        formatted = (
            f"{timestamp} "
            f"{color}[{record.levelname:5s}]{self.RESET} "
            f"{record.name}:{record.funcName} - "
            f"{record.getMessage()}"
        )
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_unified_logging(
    level: str = "INFO",
    console: bool = True,
    file_path: Optional[str] = None
) -> None:
    """
    Set up unified logging for the entire application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Whether to log to console
        file_path: Optional file path for file logging
    """
    # Get root logger and clear existing handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = SCTFormatter()
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, level.upper()))
        root_logger.addHandler(console_handler)
    
    # File handler
    if file_path:
        log_path = Path(file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, level.upper()))
        root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info("🚀 Unified logging system initialized")
    logger.info(f"📊 Log level: {level}")
    if console:
        logger.info("🖥️  Console logging: Enabled")
    if file_path:
        logger.info(f"📁 File logging: {file_path}")


def get_unified_logger(name: str) -> logging.Logger:
    """Get a logger instance using the unified configuration."""
    return logging.getLogger(name)


# Global convenience functions for common patterns
def log_agent_start(logger: logging.Logger, agent_name: str, task_description: str) -> None:
    """Log when an agent starts a task."""
    logger.info(f"🚀 {agent_name} starting: {task_description[:100]}...")


def log_agent_complete(logger: logging.Logger, agent_name: str, result_summary: str) -> None:
    """Log when an agent completes a task."""
    logger.info(f"✅ {agent_name} completed: {result_summary}")


def log_agent_error(logger: logging.Logger, agent_name: str, error: str) -> None:
    """Log when an agent encounters an error."""
    logger.error(f"❌ {agent_name} failed: {error}")


def log_workflow_start(logger: logging.Logger, workflow_name: str, context: str = "") -> None:
    """Log when a workflow starts."""
    context_str = f" ({context})" if context else ""
    logger.info(f"🔄 Workflow started: {workflow_name}{context_str}")


def log_workflow_complete(logger: logging.Logger, workflow_name: str, result: str = "") -> None:
    """Log when a workflow completes."""
    result_str = f" - {result}" if result else ""
    logger.info(f"✅ Workflow completed: {workflow_name}{result_str}")


def log_workflow_error(logger: logging.Logger, workflow_name: str, error: str) -> None:
    """Log when a workflow encounters an error."""
    logger.error(f"❌ Workflow failed: {workflow_name} - {error}")