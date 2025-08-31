"""Simple GitHub poller for issue detection without webhooks.

This module provides a straightforward GitHub issue poller that checks for new issues
periodically and triggers the agent workflow when new issues are detected.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path

from github import Github
from github.Issue import Issue

from core.logging import get_logger

logger = get_logger(__name__)


class GitHubPoller:
    """
    Simple GitHub issue poller using PyGithub.
    
    Polls GitHub repository for new issues and tracks state using JSON files.
    Designed for environments without public IP for webhooks.
    """
    
    def __init__(
        self,
        github_token: str,
        github_owner: str,
        github_repo: str,
        poll_interval_seconds: int = 30,
        state_file: str = "data/poller_state.json",
        required_labels: Optional[List[str]] = None
    ):
        """
        Initialize GitHub poller.
        
        Args:
            github_token: GitHub Personal Access Token
            github_owner: Repository owner (username or org)
            github_repo: Repository name
            poll_interval_seconds: How often to poll (default: 30 seconds)
            state_file: JSON file to store poller state
            required_labels: Optional list of required issue labels
        """
        self.github_token = github_token
        self.github_owner = github_owner
        self.github_repo = github_repo
        self.poll_interval_seconds = poll_interval_seconds
        self.state_file = Path(state_file)
        self.required_labels = required_labels or []
        
        # Initialize GitHub client
        self.github_client = Github(github_token)
        self.repository = self.github_client.get_repo(f"{github_owner}/{github_repo}")
        
        # Create state file directory
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing state
        self.state = self._load_state()
        
        # Control flags
        self._running = False
        self._shutdown_requested = False
        
        logger.info(f"GitHubPoller initialized for {github_owner}/{github_repo}")
        logger.info(f"Polling every {poll_interval_seconds} seconds")
        if self.required_labels:
            logger.info(f"Filtering for labels: {self.required_labels}")
    
    def _load_state(self) -> Dict[str, Any]:
        """Load poller state from JSON file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                logger.info(f"Loaded poller state: last issue {state.get('last_issue_id', 'none')}")
                return state
            except Exception as e:
                logger.error(f"Error loading state file: {e}")
        
        # Default state
        default_state = {
            "last_issue_id": 0,
            "last_poll_time": None,
            "processed_issues": [],
            "total_polls": 0,
            "issues_found": 0
        }
        
        logger.info("Created default poller state")
        return default_state
    
    def _save_state(self) -> None:
        """Save poller state to JSON file."""
        try:
            self.state["last_poll_time"] = datetime.now(timezone.utc).isoformat()
            
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
                
            logger.debug("Poller state saved")
            
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    async def start_polling(self) -> None:
        """Start the polling loop."""
        if self._running:
            logger.warning("Poller already running")
            return
        
        self._running = True
        self._shutdown_requested = False
        
        logger.info("Starting GitHub issue polling...")
        
        while self._running and not self._shutdown_requested:
            try:
                await self._poll_for_issues()
                self.state["total_polls"] += 1
                self._save_state()
                
                # Wait before next poll
                await asyncio.sleep(self.poll_interval_seconds)
                
            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(30)  # Brief pause before retry
        
        logger.info("GitHub polling stopped")
        self._running = False
    
    async def _poll_for_issues(self) -> None:
        """Poll GitHub for new issues."""
        try:
            logger.debug(f"Polling {self.github_owner}/{self.github_repo} for new issues...")
            
            # Get issues sorted by number (newest first)
            issues = self.repository.get_issues(
                state="open",
                sort="created",
                direction="desc"
            )
            
            new_issues = []
            last_seen_id = self.state.get("last_issue_id", 0)
            
            # Check for new issues
            for issue in issues:
                if issue.number <= last_seen_id:
                    break  # No more new issues
                
                # Check label requirements
                if self.required_labels:
                    issue_labels = [label.name for label in issue.labels]
                    if not any(req_label in issue_labels for req_label in self.required_labels):
                        logger.debug(f"Issue #{issue.number} skipped - missing required labels")
                        continue
                
                new_issues.append(issue)
            
            # Process new issues
            if new_issues:
                logger.info(f"Found {len(new_issues)} new issues")
                
                for issue in reversed(new_issues):  # Process oldest first
                    await self._process_new_issue(issue)
                    
                    # Update state
                    self.state["last_issue_id"] = max(self.state["last_issue_id"], issue.number)
                    if issue.number not in self.state["processed_issues"]:
                        self.state["processed_issues"].append(issue.number)
                
                self.state["issues_found"] += len(new_issues)
                logger.info(f"Processed {len(new_issues)} new issues")
            else:
                logger.debug("No new issues found")
                
        except Exception as e:
            logger.error(f"Error polling for issues: {e}")
    
    async def _process_new_issue(self, issue: Issue) -> None:
        """
        Process a newly detected issue.
        
        Args:
            issue: GitHub Issue object
        """
        logger.info(f"Processing new issue #{issue.number}: {issue.title}")
        
        try:
            # Create issue data for agent workflow
            issue_data = {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body or "",
                "state": issue.state,
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees],
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "html_url": issue.html_url,
                "user": {
                    "login": issue.user.login,
                    "id": issue.user.id
                }
            }
            
            # TODO: Trigger agent workflow here
            # This will integrate with the existing agent system
            logger.info(f"Issue #{issue.number} ready for agent processing")
            
            # For now, just log the issue details
            logger.info(f"Issue details: {issue.title}")
            logger.info(f"Labels: {[l.name for l in issue.labels]}")
            
        except Exception as e:
            logger.error(f"Error processing issue #{issue.number}: {e}")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the poller."""
        logger.info("Shutdown requested")
        self._shutdown_requested = True
        
        # Wait for current poll to complete
        for _ in range(10):  # Wait up to 10 seconds
            if not self._running:
                break
            await asyncio.sleep(1)
        
        self._save_state()
        logger.info("Poller shutdown complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get poller status and statistics."""
        return {
            "running": self._running,
            "repository": f"{self.github_owner}/{self.github_repo}",
            "poll_interval": self.poll_interval_seconds,
            "last_issue_id": self.state.get("last_issue_id", 0),
            "total_polls": self.state.get("total_polls", 0),
            "issues_found": self.state.get("issues_found", 0),
            "last_poll_time": self.state.get("last_poll_time"),
            "required_labels": self.required_labels,
            "state_file": str(self.state_file)
        }


def create_github_poller(
    github_token: str,
    github_owner: str, 
    github_repo: str,
    **kwargs
) -> GitHubPoller:
    """Factory function to create GitHub poller."""
    return GitHubPoller(
        github_token=github_token,
        github_owner=github_owner,
        github_repo=github_repo,
        **kwargs
    )


# Export main classes
__all__ = [
    "GitHubPoller",
    "create_github_poller"
]