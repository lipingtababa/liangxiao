"""Workspace management for organized repository and issue handling.

This module manages workspace directories that organize work by repository and issue:
    workspaces/{repo_name}/{issue_id}/{repo_name}/     # Cloned repository
    workspaces/{repo_name}/{issue_id}/.SyntheticCodingTeam/  # SCT metadata
"""

import os
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WorkspaceManager:
    """Manages workspace directories for repository and issue organization."""
    
    def __init__(self, workspace_root: str = "workspaces"):
        """
        Initialize workspace manager.
        
        Args:
            workspace_root: Root directory for all workspaces
        """
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(exist_ok=True)
        logger.info(f"WorkspaceManager initialized with root: {self.workspace_root}")
    
    def create_workspace(
        self, 
        repo_name: str, 
        issue_id: Union[str, int],
        issue_data: Optional[Dict[str, Any]] = None
    ) -> "Workspace":
        """
        Create a new workspace for a repository and issue.
        
        Args:
            repo_name: Repository name (e.g., 'liangxiao')
            issue_id: Issue ID - can be GitHub issue number (1, 2, 3) or Jira ticket (SOT-123)
            issue_data: Optional issue metadata to store
            
        Returns:
            Workspace instance for the created workspace
        """
        issue_str = str(issue_id)
        workspace_path = self.workspace_root / repo_name / issue_str
        
        logger.info(f"Creating workspace: {workspace_path}")
        
        # Create workspace directories
        workspace_path.mkdir(parents=True, exist_ok=True)
        sct_dir = workspace_path / ".SyntheticCodingTeam"
        sct_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (sct_dir / "artifacts").mkdir(exist_ok=True)
        (sct_dir / "iterations").mkdir(exist_ok=True)
        (sct_dir / "logs").mkdir(exist_ok=True)
        
        # Store issue metadata if provided
        if issue_data:
            issue_file = sct_dir / "issue.json"
            with open(issue_file, 'w') as f:
                json.dump({
                    **issue_data,
                    "created_at": datetime.now().isoformat(),
                    "workspace_created": datetime.now().isoformat()
                }, f, indent=2)
        
        # Create workspace info
        workspace_info = {
            "repo_name": repo_name,
            "issue_id": issue_str,
            "created_at": datetime.now().isoformat(),
            "workspace_path": str(workspace_path),
            "repo_path": str(workspace_path / repo_name),
            "sct_path": str(sct_dir)
        }
        
        info_file = sct_dir / "workspace.json"
        with open(info_file, 'w') as f:
            json.dump(workspace_info, f, indent=2)
        
        logger.info(f"Workspace created successfully: {workspace_path}")
        return Workspace(workspace_path, repo_name, issue_str)
    
    def get_workspace(self, repo_name: str, issue_id: Union[str, int]) -> Optional["Workspace"]:
        """
        Get existing workspace if it exists.
        
        Args:
            repo_name: Repository name
            issue_id: Issue ID
            
        Returns:
            Workspace instance if exists, None otherwise
        """
        issue_str = str(issue_id)
        workspace_path = self.workspace_root / repo_name / issue_str
        
        if workspace_path.exists():
            return Workspace(workspace_path, repo_name, issue_str)
        return None
    
    def list_workspaces(self, repo_name: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """
        List all existing workspaces.
        
        Args:
            repo_name: Optional filter by repository name
            
        Returns:
            Dictionary of workspaces: {repo_name: {issue_id: workspace_path}}
        """
        workspaces = {}
        
        if repo_name:
            repo_dirs = [self.workspace_root / repo_name] if (self.workspace_root / repo_name).exists() else []
        else:
            repo_dirs = [d for d in self.workspace_root.iterdir() if d.is_dir()]
        
        for repo_dir in repo_dirs:
            repo_name_actual = repo_dir.name
            workspaces[repo_name_actual] = {}
            
            for issue_dir in repo_dir.iterdir():
                if issue_dir.is_dir():
                    workspaces[repo_name_actual][issue_dir.name] = str(issue_dir)
        
        return workspaces
    
    def cleanup_workspace(self, repo_name: str, issue_id: Union[str, int]) -> bool:
        """
        Clean up workspace directory.
        
        Args:
            repo_name: Repository name
            issue_id: Issue ID
            
        Returns:
            True if cleanup successful, False otherwise
        """
        issue_str = str(issue_id)
        workspace_path = self.workspace_root / repo_name / issue_str
        
        if workspace_path.exists():
            try:
                shutil.rmtree(workspace_path)
                logger.info(f"Workspace cleaned up: {workspace_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to cleanup workspace {workspace_path}: {e}")
                return False
        return True


class Workspace:
    """Represents a specific workspace for a repository and issue."""
    
    def __init__(self, workspace_path: Path, repo_name: str, issue_id: str):
        """
        Initialize workspace instance.
        
        Args:
            workspace_path: Path to workspace directory
            repo_name: Repository name
            issue_id: Issue ID
        """
        self.workspace_path = workspace_path
        self.repo_name = repo_name
        self.issue_id = issue_id
        self.repo_path = workspace_path / repo_name
        self.sct_path = workspace_path / ".SyntheticCodingTeam"
        
    @property
    def repo_exists(self) -> bool:
        """Check if repository is cloned in workspace."""
        return self.repo_path.exists() and (self.repo_path / ".git").exists()
    
    @property
    def artifacts_dir(self) -> Path:
        """Get artifacts directory path."""
        return self.sct_path / "artifacts"
    
    @property
    def iterations_dir(self) -> Path:
        """Get iterations directory path."""
        return self.sct_path / "iterations"
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory path."""
        return self.sct_path / "logs"
    
    def save_artifact(self, name: str, content: str, artifact_type: str = "code") -> Path:
        """
        Save an artifact to the workspace.
        
        Args:
            name: Artifact name
            content: Artifact content
            artifact_type: Type of artifact (code, documentation, etc.)
            
        Returns:
            Path to saved artifact
        """
        self.artifacts_dir.mkdir(exist_ok=True)
        artifact_path = self.artifacts_dir / f"{name}.{artifact_type}"
        
        with open(artifact_path, 'w') as f:
            f.write(content)
        
        logger.debug(f"Artifact saved: {artifact_path}")
        return artifact_path
    
    def save_iteration(self, iteration_num: int, data: Dict[str, Any]) -> Path:
        """
        Save iteration data.
        
        Args:
            iteration_num: Iteration number
            data: Iteration data
            
        Returns:
            Path to saved iteration file
        """
        self.iterations_dir.mkdir(exist_ok=True)
        iteration_path = self.iterations_dir / f"iteration_{iteration_num:03d}.json"
        
        iteration_data = {
            **data,
            "iteration": iteration_num,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(iteration_path, 'w') as f:
            json.dump(iteration_data, f, indent=2)
        
        logger.debug(f"Iteration data saved: {iteration_path}")
        return iteration_path
    
    def load_issue_data(self) -> Optional[Dict[str, Any]]:
        """Load issue data from workspace."""
        issue_file = self.sct_path / "issue.json"
        if issue_file.exists():
            with open(issue_file, 'r') as f:
                return json.load(f)
        return None
    
    def save_workflow_state(self, state: Dict[str, Any]) -> None:
        """
        Save workflow state to workspace.
        
        Args:
            state: Workflow state data
        """
        workflow_file = self.sct_path / "workflow.json"
        
        workflow_data = {
            **state,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(workflow_file, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        logger.debug(f"Workflow state saved: {workflow_file}")
    
    def load_workflow_state(self) -> Optional[Dict[str, Any]]:
        """Load workflow state from workspace."""
        workflow_file = self.sct_path / "workflow.json"
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                return json.load(f)
        return None
    
    def get_git_status(self) -> Optional[Dict[str, Any]]:
        """
        Get Git status of the repository in workspace.
        
        Returns:
            Git status information if repository exists
        """
        if not self.repo_exists:
            return None
            
        try:
            import subprocess
            
            # Get current branch
            branch_result = subprocess.run([
                "git", "branch", "--show-current"
            ], capture_output=True, text=True, cwd=self.repo_path, check=False)
            
            # Get status
            status_result = subprocess.run([
                "git", "status", "--porcelain"
            ], capture_output=True, text=True, cwd=self.repo_path, check=False)
            
            # Get last commit
            log_result = subprocess.run([
                "git", "log", "-1", "--oneline"
            ], capture_output=True, text=True, cwd=self.repo_path, check=False)
            
            return {
                "current_branch": branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown",
                "has_changes": bool(status_result.stdout.strip()) if status_result.returncode == 0 else False,
                "changed_files": status_result.stdout.strip().split('\n') if status_result.stdout.strip() else [],
                "last_commit": log_result.stdout.strip() if log_result.returncode == 0 else "No commits",
                "repo_path": str(self.repo_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting Git status: {e}")
            return None


def create_workspace_manager(workspace_root: Optional[str] = None) -> WorkspaceManager:
    """
    Factory function to create workspace manager.
    
    Args:
        workspace_root: Optional workspace root directory
        
    Returns:
        Configured WorkspaceManager instance
    """
    if workspace_root is None:
        from config import Settings
        settings = Settings()
        root = settings.workspace_root
    else:
        root = workspace_root
    return WorkspaceManager(root)


def parse_issue_id(issue_id: Union[str, int]) -> str:
    """
    Parse and validate issue ID for workspace naming.
    
    Supports:
    - GitHub issues: 1, 2, 3, "123"
    - Jira tickets: "SOT-123", "PROJ-456"
    - Other formats: "ISSUE-789"
    
    Args:
        issue_id: Issue identifier
        
    Returns:
        Normalized issue ID string
    """
    issue_str = str(issue_id)
    
    # Validate issue ID format
    if not issue_str:
        raise ValueError("Issue ID cannot be empty")
    
    # GitHub issues (numeric)
    if issue_str.isdigit():
        return issue_str
    
    # Jira or other ticket formats (PROJ-123)
    if "-" in issue_str and len(issue_str.split("-")) == 2:
        prefix, number = issue_str.split("-")
        if prefix.isalpha() and number.isdigit():
            return issue_str
    
    # Allow other formats but log warning
    logger.warning(f"Non-standard issue ID format: {issue_str}")
    return issue_str