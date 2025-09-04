"""Enhanced logging configuration with structured logging and request tracking."""

import logging
import sys
import json
import uuid
import contextvars
from typing import Optional, Dict, Any, Union
from datetime import datetime
from pathlib import Path


# Context variables for request tracking
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('request_id', default=None)
request_context_var: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar('request_context', default={})


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with JSON output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Get base log data
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data['request_id'] = request_id
        
        # Add request context if available
        request_context = request_context_var.get()
        if request_context:
            log_data['context'] = request_context
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                         'levelname', 'levelno', 'lineno', 'module', 'msecs',
                         'message', 'pathname', 'process', 'processName',
                         'relativeCreated', 'thread', 'threadName', 'exc_info',
                         'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """Enhanced console formatter with colors and better readability."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and context."""
        # Get color for level
        color = self.COLORS.get(record.levelname, '')
        
        # Build timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Build message parts
        parts = [
            f"{timestamp}",
            f"{color}{self.BOLD}[{record.levelname:8s}]{self.RESET}",
            f"{self.BOLD}{record.name}{self.RESET}"
        ]
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            parts.append(f"[{request_id[:8]}]")
        
        # Add function context
        parts.append(f"({record.module}.{record.funcName}:{record.lineno})")
        
        # Add message
        parts.append(f"- {record.getMessage()}")
        
        # Join base message
        formatted = " ".join(parts)
        
        # Add context if available
        request_context = request_context_var.get()
        if request_context:
            formatted += f"\n  Context: {json.dumps(request_context, indent=2)}"
        
        # Add exception if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging(level: str = "INFO", log_file: Optional[str] = None, structured: bool = False) -> None:
    """
    Setup enhanced application logging configuration.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to log to (in addition to console)
        structured: Whether to use structured JSON logging for file output
    """
    # Create formatters
    console_formatter = ColoredConsoleFormatter()
    file_formatter = StructuredFormatter() if structured else logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        defaults={'request_id': 'no-request'}
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO if level == "DEBUG" else getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(getattr(logging, level.upper()))
        root_logger.addHandler(file_handler)
        
        # Also create a debug log file for detailed debugging
        if level != "DEBUG":
            debug_file = log_path.parent / f"debug_{log_path.name}"
            debug_handler = logging.FileHandler(debug_file)
            debug_handler.setFormatter(StructuredFormatter())
            debug_handler.setLevel(logging.DEBUG)
            root_logger.addHandler(debug_handler)
    
    # Set levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    
    # Log startup info
    logger = logging.getLogger(__name__)
    logger.info(f"Logging system initialized")
    logger.info(f"Log level: {level}")
    logger.info(f"Console output: Enabled (colored)")
    if log_file:
        logger.info(f"File output: {log_file} (structured={structured})")
        if level != "DEBUG":
            debug_file = Path(log_file).parent / f"debug_{Path(log_file).name}"
            logger.info(f"Debug file: {debug_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    return logging.getLogger(name)


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set or generate a request ID for the current context.
    
    Args:
        request_id: Optional request ID to use, generates one if not provided
    
    Returns:
        The request ID that was set
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """Get the current request ID from context."""
    return request_id_var.get()


def set_request_context(**kwargs: Any) -> None:
    """Set additional context for the current request.
    
    Args:
        **kwargs: Key-value pairs to add to the request context
    """
    current_context = request_context_var.get() or {}
    current_context.update(kwargs)
    request_context_var.set(current_context)


def clear_request_context() -> None:
    """Clear the request context."""
    request_id_var.set(None)
    request_context_var.set({})


class LogContext:
    """Context manager for scoped logging context."""
    
    def __init__(self, request_id: Optional[str] = None, **context: Any):
        """Initialize log context.
        
        Args:
            request_id: Optional request ID
            **context: Additional context key-value pairs
        """
        self.request_id = request_id
        self.context = context
        self.previous_id = None
        self.previous_context = None
    
    def __enter__(self):
        """Enter the context."""
        self.previous_id = request_id_var.get()
        self.previous_context = request_context_var.get()
        
        set_request_id(self.request_id)
        if self.context:
            set_request_context(**self.context)
        
        return self
    
    def __exit__(self, *args):
        """Exit the context."""
        request_id_var.set(self.previous_id)
        request_context_var.set(self.previous_context)


def log_startup_info(logger: logging.Logger, service_name: str, version: str, **info: Any) -> None:
    """Log comprehensive startup information.
    
    Args:
        logger: Logger instance to use
        service_name: Name of the service
        version: Service version
        **info: Additional startup info to log
    """
    logger.info("="*60)
    logger.info(f"{service_name} v{version} Starting")
    logger.info("="*60)
    
    for key, value in info.items():
        if 'secret' in key.lower() or 'password' in key.lower() or 'token' in key.lower():
            # Mask sensitive information
            if value:
                masked_value = value[:4] + "*" * (len(str(value)) - 8) + value[-4:] if len(str(value)) > 8 else "****"
                logger.info(f"  {key}: {masked_value} (masked)")
            else:
                logger.info(f"  {key}: Not configured")
        else:
            logger.info(f"  {key}: {value}")
    
    logger.info("="*60)