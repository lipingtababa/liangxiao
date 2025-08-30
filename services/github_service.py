"""GitHub CLI service wrapper for multi-agent system.

This service provides a comprehensive Python interface to GitHub operations
using the GitHub CLI (gh) tool. It focuses on preventing disasters like PR #23
by ensuring proper file reading before modifications.

Key features:
- Uses official GitHub CLI for reliable API interactions
- Comprehensive error handling and logging
- Authentication handled by GitHub CLI
- Production-ready with defensive programming practices
- Workspace organization for multiple repositories and issues
"""

import subprocess
import json
import base64
import logging
import tempfile
import shutil
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod

from core.workspace_manager import WorkspaceManager, Workspace, create_workspace_manager

logger = logging.getLogger(__name__)


class GitHubCLIError(Exception):
    """Custom exception for GitHub CLI errors with detailed context."""
    
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


class GitHubService:
    """
    GitHub service for repository operations with workspace support.
    
    Provides comprehensive GitHub operations with proper error handling and logging.
    Includes workspace organization for multiple repositories and issues.
    
    Attributes:
        owner: Repository owner (user or organization)
        repo_name: Repository name
        repo_full_name: Full repository name (owner/repo)
        workspace_manager: Workspace manager for organized directory structure
        current_workspace: Current active workspace
    """
    
    def __init__(self, owner: str, repo_name: str, working_dir: Optional[str] = None, workspace_manager: Optional[WorkspaceManager] = None):
        """
        Initialize GitHub service with workspace support.
        
        Args:
            owner: Repository owner (user or org)
            repo_name: Repository name
            working_dir: Optional working directory for git operations (legacy)
            workspace_manager: Optional workspace manager for organized directory structure
            
        Raises:
            GitHubCLIError: If GitHub CLI is not available or not authenticated
        """
        self.owner = owner
        self.repo_name = repo_name
        self.repo_full_name = f"{owner}/{repo_name}"
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.workspace_manager = workspace_manager or create_workspace_manager()
        self.current_workspace: Optional[Workspace] = None
        
        # Verify gh CLI is available and authenticated
        self._verify_gh_cli()
        
        logger.info(f"GitHubService initialized for {self.repo_full_name} with workspace support")
    
    def _verify_gh_cli(self) -> None:
        """Verify GitHub CLI is installed and authenticated."""
        try:
            # Check if gh is installed
            result = subprocess.run(
                ["gh", "--version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if result.returncode != 0:
                raise GitHubCLIError(
                    "GitHub CLI not found. Install with: brew install gh",
                    result.returncode,
                    result.stderr or "",
                    ["gh", "--version"]
                )
                
            # Check authentication
            auth_result = subprocess.run(
                ["gh", "auth", "status"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if auth_result.returncode != 0:
                logger.warning("GitHub CLI not authenticated. Some operations may fail.")
                
        except Exception as e:
            raise GitHubCLIError(
                f"Failed to verify GitHub CLI: {e}",
                1,
                str(e),
                ["gh", "--version"]
            )
    
    def setup_workspace(self, issue_id: Union[str, int], issue_data: Optional[Dict[str, Any]] = None) -> Workspace:
        """
        Set up workspace for an issue.
        
        Args:
            issue_id: Issue ID (GitHub number or Jira ticket like SOT-123)
            issue_data: Optional issue metadata
            
        Returns:
            Workspace instance
        """
        workspace = self.workspace_manager.create_workspace(
            repo_name=self.repo_name,
            issue_id=issue_id,
            issue_data=issue_data
        )
        self.current_workspace = workspace
        
        logger.info(f"Workspace setup complete for {self.repo_name}#{issue_id}: {workspace.workspace_path}")
        return workspace
    
    def clone_to_workspace(self, issue_id: Union[str, int], issue_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Clone repository to organized workspace structure.
        
        Creates: workspaces/{repo_name}/{issue_id}/{repo_name}/
        And: workspaces/{repo_name}/{issue_id}/.SyntheticCodingTeam/
        
        Args:
            issue_id: Issue ID (GitHub number or Jira ticket)
            issue_data: Optional issue metadata to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Setup workspace
            workspace = self.setup_workspace(issue_id, issue_data)
            
            # Clone repository to workspace
            if not workspace.repo_exists:
                logger.info(f"Cloning {self.repo_full_name} to workspace: {workspace.repo_path}")
                
                result = subprocess.run([
                    "gh", "repo", "clone", self.repo_full_name, str(workspace.repo_path)
                ], capture_output=True, text=True, check=False)
                
                if result.returncode == 0:
                    logger.info(f"Successfully cloned repository to workspace: {workspace.repo_path}")
                    # Update working directory to use workspace
                    self.working_dir = workspace.repo_path
                    return True
                else:
                    logger.error(f"Failed to clone repository to workspace: {result.stderr}")
                    return False
            else:
                logger.info(f"Repository already exists in workspace: {workspace.repo_path}")
                self.working_dir = workspace.repo_path
                return True
                
        except Exception as e:
            logger.error(f"Error setting up workspace for issue {issue_id}: {e}")
            return False
    
    def get_current_workspace(self) -> Optional[Workspace]:
        """Get the current workspace if set."""
        return self.current_workspace
    
    def read_file(self, path: str, ref: str = "main") -> Optional[str]:
        """Read file content from repository using GitHub CLI."""
        try:
            result = subprocess.run([
                "gh", "api", f"/repos/{self.repo_full_name}/contents/{path}",
                "--jq", ".content"
            ], capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                # Decode base64 content
                encoded_content = result.stdout.strip().strip('"')
                content = base64.b64decode(encoded_content).decode('utf-8')
                return content
            else:
                logger.error(f"Failed to read file {path}: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return None


# Factory function for easy instantiation
def create_github_service(owner: str, repo_name: str, working_dir: Optional[str] = None, workspace_manager: Optional[WorkspaceManager] = None) -> GitHubService:
    """
    Factory function to create GitHubService instance.
    
    Args:
        owner: Repository owner
        repo_name: Repository name
        working_dir: Optional working directory (legacy)
        workspace_manager: Optional workspace manager for organized structure
        
    Returns:
        Configured GitHubService instance
        
    Raises:
        GitHubCLIError: If service initialization fails
    """
    try:
        service = GitHubService(owner, repo_name, working_dir, workspace_manager)
        logger.info(f"Created GitHubService for {owner}/{repo_name} with workspace support")
        return service
    except Exception as e:
        logger.error(f"Failed to create GitHubService: {e}")
        raise


# Export main classes and functions
__all__ = [
    "GitHubService",
    "GitHubCLIError", 
    "create_github_service"
]