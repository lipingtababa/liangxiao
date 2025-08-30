"""Abstract AI tool interface for unified agent integration.

This module provides a clean abstraction for different AI tools (OpenAI API, Claude Code CLI)
with a single `execute` method that adapts to each tool's natural paradigm.
"""

import subprocess
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class AIToolError(Exception):
    """Base exception for AI tool errors."""
    
    def __init__(self, message: str, tool_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.tool_type = tool_type
        self.details = details or {}


class AITool(ABC):
    """
    Abstract base class for AI tools.
    
    Provides unified interface for different AI tools (OpenAI, Claude Code, etc.)
    through a single `execute` method.
    """
    
    def __init__(self, tool_type: str):
        """
        Initialize AI tool.
        
        Args:
            tool_type: Type identifier for this tool
        """
        self.tool_type = tool_type
        self.total_requests = 0
        self.total_errors = 0
        
    @abstractmethod
    async def execute(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Execute AI operation with unified interface.
        
        Args:
            prompt: Main prompt/instruction for the AI
            context: Additional context data (includes timeout, files, etc.)
            system_prompt: System-level instructions
            max_tokens: Maximum tokens in response
            
        Returns:
            AI response as string
            
        Raises:
            AIToolError: If execution fails
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics for this tool."""
        return {
            "tool_type": self.tool_type,
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "success_rate": (self.total_requests - self.total_errors) / max(self.total_requests, 1)
        }
    
    def _increment_stats(self, success: bool = True) -> None:
        """Track usage statistics."""
        self.total_requests += 1
        if not success:
            self.total_errors += 1


class OpenAITool(AITool):
    """OpenAI API tool implementation using LangChain."""
    
    def __init__(self, model: str = "gpt-5", temperature: float = 0.2, api_key: Optional[str] = None):
        """
        Initialize OpenAI tool.
        
        Args:
            model: OpenAI model to use
            temperature: Sampling temperature
            api_key: Optional API key (uses environment if not provided)
        """
        super().__init__("openai")
        self.model = model
        self.temperature = temperature
        
        # Import here to avoid dependency if not using OpenAI
        from langchain_openai import ChatOpenAI
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key
        )
        
        logger.info(f"OpenAI tool initialized: {model}, temp={temperature}")
    
    async def execute(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Execute using OpenAI API via LangChain."""
        try:
            # Build messages for chat completion
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add context to prompt if provided
            full_prompt = prompt
            if context:
                context_str = self._format_context(context)
                full_prompt = f"{prompt}\n\n{context_str}"
            
            messages.append({"role": "user", "content": full_prompt})
            
            # Set up generation parameters
            generation_kwargs = {}
            if max_tokens:
                generation_kwargs["max_tokens"] = max_tokens
            
            # Get timeout from context
            timeout = context.get("timeout") if context else None
            if timeout:
                generation_kwargs["request_timeout"] = timeout
            
            # Execute OpenAI call
            response = await self.llm.ainvoke(messages, **generation_kwargs)
            
            self._increment_stats(success=True)
            logger.debug(f"OpenAI execution successful")
            
            return response.content
            
        except Exception as e:
            self._increment_stats(success=False)
            logger.error(f"OpenAI execution failed: {e}")
            raise AIToolError(f"OpenAI execution failed: {e}", "openai", {"error": str(e)})
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context data for OpenAI prompt."""
        parts = []
        
        if "files" in context:
            parts.append("## Existing Files:")
            for file_path, content in context["files"].items():
                parts.append(f"### {file_path}:\n```\n{content}\n```")
        
        if "requirements" in context:
            parts.append(f"## Requirements:\n{context['requirements']}")
        
        if "previous_feedback" in context:
            parts.append(f"## Previous Feedback:\n{context['previous_feedback']}")
        
        return "\n\n".join(parts) if parts else ""


class ClaudeCodeTool(AITool):
    """Claude Code CLI tool implementation."""
    
    def __init__(self, command: str = "claude", default_timeout: int = 120, max_retries: int = 2):
        """
        Initialize Claude Code tool.
        
        Args:
            command: Claude CLI command
            default_timeout: Default timeout for operations
            max_retries: Maximum retry attempts
        """
        super().__init__("claude")
        self.command = command
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        
        # Verify Claude CLI is available
        self._verify_claude_cli()
        
        logger.info(f"Claude Code tool initialized: {command}")
    
    def _verify_claude_cli(self) -> None:
        """Verify Claude CLI is available."""
        try:
            result = subprocess.run(
                [self.command, "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10
            )
            
            if result.returncode != 0:
                raise AIToolError(
                    f"Claude CLI not available: {result.stderr}",
                    "claude",
                    {"command": self.command}
                )
                
        except Exception as e:
            raise AIToolError(f"Claude CLI verification failed: {e}", "claude")
    
    async def execute(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None  # Ignored - Claude CLI doesn't support
    ) -> str:
        """Execute using Claude Code CLI."""
        try:
            # Get timeout from context
            timeout = context.get("timeout", self.default_timeout) if context else self.default_timeout
            
            # Build full prompt
            full_prompt = self._build_claude_prompt(prompt, context, system_prompt)
            
            # Execute Claude CLI with retries
            for attempt in range(self.max_retries + 1):
                try:
                    logger.debug(f"Claude CLI attempt {attempt + 1}")
                    
                    result = subprocess.run([
                        self.command, "-p", full_prompt, "--output-format", "text"
                    ], 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout,
                    check=False)
                    
                    if result.returncode == 0:
                        self._increment_stats(success=True)
                        logger.debug("Claude CLI execution successful")
                        return result.stdout.strip()
                    
                    logger.warning(f"Claude attempt {attempt + 1} failed: {result.stderr}")
                    
                except subprocess.TimeoutExpired:
                    logger.warning(f"Claude attempt {attempt + 1} timed out")
            
            # All attempts failed
            self._increment_stats(success=False)
            raise AIToolError(
                f"Claude CLI failed after {self.max_retries + 1} attempts",
                "claude",
                {"last_error": result.stderr if 'result' in locals() else "timeout"}
            )
            
        except Exception as e:
            self._increment_stats(success=False)
            logger.error(f"Claude CLI execution error: {e}")
            raise AIToolError(f"Claude CLI execution failed: {e}", "claude")
    
    def _build_claude_prompt(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Build prompt for Claude CLI."""
        parts = []
        
        if system_prompt:
            parts.append(f"System Instructions: {system_prompt}")
        
        parts.append(f"Task: {prompt}")
        
        if context:
            if "files" in context:
                parts.append("Existing Files:")
                for file_path, content in context["files"].items():
                    parts.append(f"{file_path}:\n{content}")
            
            if "requirements" in context:
                parts.append(f"Requirements: {context['requirements']}")
        
        return "\n\n".join(parts)


# Factory function
def create_ai_tool(tool_type: str, **config) -> AITool:
    """Create AI tool based on type and configuration."""
    if tool_type == "openai":
        return OpenAITool(**config)
    elif tool_type == "claude":
        return ClaudeCodeTool(**config)
    else:
        raise ValueError(f"Unknown tool type: {tool_type}")


# Export classes and functions
__all__ = [
    "AITool",
    "AIToolError", 
    "OpenAITool",
    "ClaudeCodeTool",
    "create_ai_tool"
]