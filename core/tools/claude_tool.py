"""Claude Code CLI tool wrapper for agent integration.

This module provides a wrapper around the Claude Code CLI to replace OpenAI API calls
with Claude Code for all agent operations (Developer, Navigator, Analyst).
"""

import subprocess
import json
import tempfile
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ClaudeCodeError(Exception):
    """Custom exception for Claude Code CLI errors."""
    
    def __init__(self, message: str, returncode: int, stderr: str, command: List[str]):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr
        self.command = command
        
    def __str__(self) -> str:
        return (
            f"{super().__str__()} "
            f"(return code: {self.returncode}, "
            f"command: {' '.join(self.command)})"
        )


class ClaudeCodeTool:
    """
    Wrapper for Claude Code CLI that replaces OpenAI API calls.
    
    Provides a unified interface for all agents (Developer, Navigator, Analyst)
    to use Claude Code instead of OpenAI API.
    """
    
    def __init__(
        self, 
        command: str = "claude",
        timeout: int = 120,
        max_retries: int = 2,
        working_directory: Optional[str] = None
    ):
        """
        Initialize Claude Code tool.
        
        Args:
            command: Claude CLI command (default: "claude")
            timeout: Timeout in seconds for Claude operations
            max_retries: Maximum number of retries for failed operations
            working_directory: Working directory for Claude operations
        """
        self.command = command
        self.timeout = timeout
        self.max_retries = max_retries
        self.working_directory = Path(working_directory) if working_directory else Path.cwd()
        
        # Verify Claude CLI is available
        self._verify_claude_cli()
        
        logger.info(f"ClaudeCodeTool initialized: {command}, timeout={timeout}s")
    
    def _verify_claude_cli(self) -> None:
        """Verify Claude CLI is installed and available."""
        try:
            result = subprocess.run(
                [self.command, "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10
            )
            
            if result.returncode != 0:
                raise ClaudeCodeError(
                    f"Claude CLI not found or not working. Install with: pip install claude-cli",
                    result.returncode,
                    result.stderr or "",
                    [self.command, "--version"]
                )
                
            logger.info(f"Claude CLI verified: {result.stdout.strip()}")
            
        except subprocess.TimeoutExpired:
            raise ClaudeCodeError(
                "Claude CLI verification timed out",
                1,
                "Timeout",
                [self.command, "--version"]
            )
        except Exception as e:
            raise ClaudeCodeError(
                f"Failed to verify Claude CLI: {e}",
                1,
                str(e),
                [self.command, "--version"]
            )
    
    async def generate_code(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        file_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate code using Claude Code CLI.
        
        Args:
            prompt: The development prompt for Claude
            context: Optional context information
            file_context: Optional existing file contents for context
            
        Returns:
            Generated response from Claude
            
        Raises:
            ClaudeCodeError: If Claude operation fails
        """
        try:
            # Format prompt for Claude Code
            formatted_prompt = self._format_prompt_for_claude(prompt, context, file_context)
            
            # Execute Claude CLI with retries
            for attempt in range(self.max_retries + 1):
                try:
                    logger.debug(f"Claude Code generation attempt {attempt + 1}/{self.max_retries + 1}")
                    
                    # Use temporary file for complex prompts
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
                        temp_file.write(formatted_prompt)
                        temp_file_path = temp_file.name
                    
                    try:
                        # Execute Claude with the prompt file
                        result = subprocess.run([
                            self.command, 
                            "--file", temp_file_path
                        ], 
                        capture_output=True, 
                        text=True, 
                        check=False,
                        timeout=self.timeout,
                        cwd=self.working_directory)
                        
                        if result.returncode == 0:
                            logger.info("Claude Code generation successful")
                            return result.stdout.strip()
                        else:
                            logger.warning(f"Claude attempt {attempt + 1} failed: {result.stderr}")
                            if attempt == self.max_retries:
                                raise ClaudeCodeError(
                                    f"Claude Code generation failed after {self.max_retries + 1} attempts",
                                    result.returncode,
                                    result.stderr or "",
                                    [self.command, "--file", temp_file_path]
                                )
                                
                    finally:
                        # Clean up temp file
                        try:
                            Path(temp_file_path).unlink()
                        except:
                            pass
                            
                except subprocess.TimeoutExpired:
                    logger.warning(f"Claude attempt {attempt + 1} timed out")
                    if attempt == self.max_retries:
                        raise ClaudeCodeError(
                            f"Claude Code timed out after {self.timeout}s",
                            1,
                            "Timeout",
                            [self.command]
                        )
                        
        except Exception as e:
            logger.error(f"Claude Code generation error: {e}")
            raise
    
    async def review_code(
        self,
        code: str,
        review_prompt: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Review code using Claude Code CLI.
        
        Args:
            code: Code content to review
            review_prompt: Review instructions for Claude
            file_path: Optional file path for context
            context: Optional additional context
            
        Returns:
            Review response from Claude
        """
        try:
            # Format review prompt
            formatted_prompt = f"""# Code Review Task

{review_prompt}

## Code to Review:
File: {file_path or 'Unknown'}

```
{code}
```

## Additional Context:
{json.dumps(context, indent=2) if context else 'None'}

Please provide a detailed review focusing on:
1. Code quality and correctness
2. Security considerations
3. Performance implications
4. Maintainability
5. Disaster prevention (avoiding issues like deleting entire files)
"""
            
            return await self.generate_code(formatted_prompt)
            
        except Exception as e:
            logger.error(f"Claude Code review error: {e}")
            raise
    
    async def analyze_requirements(
        self,
        issue_description: str,
        repository_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Analyze requirements using Claude Code CLI.
        
        Args:
            issue_description: Issue description to analyze
            repository_context: Optional repository context
            
        Returns:
            Analysis response from Claude
        """
        try:
            formatted_prompt = f"""# Requirements Analysis Task

Analyze the following issue and provide detailed requirements:

## Issue Description:
{issue_description}

## Repository Context:
{json.dumps(repository_context, indent=2) if repository_context else 'None'}

Please provide:
1. Detailed requirements breakdown
2. Technical approach recommendations
3. File modification strategy
4. Risk assessment
5. Implementation plan
"""
            
            return await self.generate_code(formatted_prompt)
            
        except Exception as e:
            logger.error(f"Claude Code analysis error: {e}")
            raise
    
    def _format_prompt_for_claude(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        file_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Format prompt for Claude Code with proper context.
        
        Args:
            prompt: Base prompt
            context: Optional context data
            file_context: Optional file contents
            
        Returns:
            Formatted prompt for Claude
        """
        formatted_parts = [prompt]
        
        if context:
            formatted_parts.append(f"\n## Context:\n{json.dumps(context, indent=2)}")
        
        if file_context:
            formatted_parts.append("\n## Existing Files:")
            for file_path, content in file_context.items():
                formatted_parts.append(f"\n### {file_path}:\n```\n{content}\n```")
        
        formatted_parts.append(f"\n---\nGenerated at: {datetime.now().isoformat()}")
        
        return "\n".join(formatted_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics."""
        return {
            "tool": "claude_code",
            "command": self.command,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "working_directory": str(self.working_directory)
        }


def create_claude_tool(**kwargs) -> ClaudeCodeTool:
    """
    Factory function to create Claude Code tool.
    
    Args:
        **kwargs: Configuration parameters
        
    Returns:
        Configured ClaudeCodeTool instance
    """
    return ClaudeCodeTool(**kwargs)


# Export main classes
__all__ = [
    "ClaudeCodeTool",
    "ClaudeCodeError", 
    "create_claude_tool"
]