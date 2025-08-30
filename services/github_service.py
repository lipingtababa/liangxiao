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
    
    def setup_git_workspace(self, issue_id: Union[str, int], issue_data: Optional[Dict[str, Any]] = None, base_branch: str = "main") -> bool:
        """
        Complete Git workspace setup: clone repo + create feature branch.
        
        Args:
            issue_id: Issue ID (GitHub number or Jira ticket)
            issue_data: Optional issue metadata
            base_branch: Base branch to create from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clone repository to workspace
            clone_success = self.clone_to_workspace(issue_id, issue_data)
            if not clone_success:
                return False
            
            # Create feature branch
            branch_success = self.create_feature_branch(issue_id, base_branch)
            if not branch_success:
                logger.warning("Failed to create feature branch, using default branch")
            
            logger.info(f"Git workspace ready for development: {self.current_workspace.repo_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Git workspace: {e}")
            return False
    
    def create_feature_branch(self, issue_id: Union[str, int], base_branch: str = "main") -> bool:
        """
        Create a feature branch for the issue in the current workspace.
        
        Args:
            issue_id: Issue ID (GitHub number or Jira ticket)
            base_branch: Base branch to create from (default: main)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.current_workspace or not self.current_workspace.repo_exists:
            logger.error("No workspace or repository available for branch creation")
            return False
            
        try:
            # Generate branch name
            issue_str = str(issue_id)
            if issue_str.isdigit():
                branch_name = f"feature/issue-{issue_str}"
            else:
                # For Jira tickets like SOT-123
                branch_name = f"feature/{issue_str.lower()}"
            
            repo_path = self.current_workspace.repo_path
            logger.info(f"Creating feature branch '{branch_name}' from '{base_branch}' in {repo_path}")
            
            # Fetch latest changes
            result = subprocess.run([
                "git", "fetch", "origin"
            ], capture_output=True, text=True, cwd=repo_path, check=False)
            
            if result.returncode != 0:
                logger.warning(f"Git fetch warning: {result.stderr}")
            
            # Create and checkout new branch
            result = subprocess.run([
                "git", "checkout", "-b", branch_name, f"origin/{base_branch}"
            ], capture_output=True, text=True, cwd=repo_path, check=False)
            
            if result.returncode == 0:
                logger.info(f"Feature branch '{branch_name}' created successfully")
                # Store branch name in workspace metadata
                if self.current_workspace:
                    workspace_data = self.current_workspace.load_workflow_state() or {}
                    workspace_data.update({
                        "feature_branch": branch_name,
                        "base_branch": base_branch,
                        "branch_created_at": datetime.now().isoformat()
                    })
                    self.current_workspace.save_workflow_state(workspace_data)
                return True
            else:
                logger.error(f"Failed to create feature branch: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating feature branch: {e}")
            return False
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """
        Commit changes in the current workspace repository.
        
        Args:
            message: Commit message
            files: Optional list of specific files to commit (default: all changes)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.current_workspace or not self.current_workspace.repo_exists:
            logger.error("No workspace or repository available for committing")
            return False
            
        try:
            repo_path = self.current_workspace.repo_path
            
            # Add files to staging
            if files:
                for file_path in files:
                    result = subprocess.run([
                        "git", "add", file_path
                    ], capture_output=True, text=True, cwd=repo_path, check=False)
                    
                    if result.returncode != 0:
                        logger.error(f"Failed to add file {file_path}: {result.stderr}")
                        return False
            else:
                # Add all changes
                result = subprocess.run([
                    "git", "add", "-A"
                ], capture_output=True, text=True, cwd=repo_path, check=False)
                
                if result.returncode != 0:
                    logger.error(f"Failed to add changes: {result.stderr}")
                    return False
            
            # Commit changes
            result = subprocess.run([
                "git", "commit", "-m", message
            ], capture_output=True, text=True, cwd=repo_path, check=False)
            
            if result.returncode == 0:
                logger.info(f"Changes committed successfully: {message}")
                return True
            else:
                logger.error(f"Failed to commit changes: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return False
    
    def push_branch(self) -> bool:
        """
        Push the current branch to origin.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.current_workspace or not self.current_workspace.repo_exists:
            logger.error("No workspace or repository available for pushing")
            return False
            
        try:
            repo_path = self.current_workspace.repo_path
            
            # Get current branch name
            result = subprocess.run([
                "git", "branch", "--show-current"
            ], capture_output=True, text=True, cwd=repo_path, check=False)
            
            if result.returncode != 0:
                logger.error(f"Failed to get current branch: {result.stderr}")
                return False
                
            branch_name = result.stdout.strip()
            logger.info(f"Pushing branch '{branch_name}' to origin")
            
            # Push branch
            result = subprocess.run([
                "git", "push", "-u", "origin", branch_name
            ], capture_output=True, text=True, cwd=repo_path, check=False)
            
            if result.returncode == 0:
                logger.info(f"Branch '{branch_name}' pushed successfully")
                return True
            else:
                logger.error(f"Failed to push branch: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing branch: {e}")
            return False
    
    def write_file_to_workspace(self, file_path: str, content: str) -> bool:
        """
        Write content directly to a file in the workspace repository.
        
        Args:
            file_path: Relative path within the repository
            content: File content to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self.current_workspace or not self.current_workspace.repo_exists:
            logger.error("No workspace or repository available for file writing")
            return False
            
        try:
            full_path = self.current_workspace.repo_path / file_path
            
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"File written to workspace: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    def read_file_from_workspace(self, file_path: str) -> Optional[str]:
        """
        Read file content from the workspace repository.
        
        Args:
            file_path: Relative path within the repository
            
        Returns:
            File content if successful, None otherwise
        """
        if not self.current_workspace or not self.current_workspace.repo_exists:
            logger.error("No workspace or repository available for file reading")
            return None
            
        try:
            full_path = self.current_workspace.repo_path / file_path
            
            if not full_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return None
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.debug(f"File read from workspace: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
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