"""Custom exceptions for the application."""

from typing import Optional, Any


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class ConfigurationError(OrchestratorError):
    """Raised when configuration is invalid or missing."""
    pass


class GitHubError(OrchestratorError):
    """Raised when GitHub operations fail."""
    pass


class WorkflowError(OrchestratorError):
    """Raised when workflow operations fail."""
    pass


class ValidationError(OrchestratorError):
    """Raised when input validation fails."""
    pass


class RateLimitError(OrchestratorError):
    """Raised when rate limits are exceeded."""
    pass


class AgentExecutionError(OrchestratorError):
    """Raised when agent execution fails."""
    pass