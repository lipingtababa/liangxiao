"""Poller service for managing GitHub poller lifecycle."""

import asyncio
from typing import Optional, List
from core.logging import get_logger
from .github_poller import GitHubPoller, create_github_poller

logger = get_logger(__name__)


class PollerService:
    """Service wrapper for GitHub poller with lifecycle management."""
    
    def __init__(
        self,
        github_token: str,
        github_owner: str,
        github_repo: str,
        poll_interval_seconds: int = 30,
        poller_state_file: str = "data/poller_state.json",
        required_issue_labels: str = "",
        poller_enabled: bool = True
    ):
        """Initialize poller service."""
        self.poller_enabled = poller_enabled
        
        if not poller_enabled:
            logger.info("Poller disabled")
            return
        
        # Parse required labels
        labels = []
        if required_issue_labels:
            labels = [label.strip() for label in required_issue_labels.split(",") if label.strip()]
        
        # Create GitHub poller
        self.github_poller = create_github_poller(
            github_token=github_token,
            github_owner=github_owner,
            github_repo=github_repo,
            poll_interval_seconds=poll_interval_seconds,
            state_file=poller_state_file,
            required_labels=labels if labels else None
        )
        
        logger.info(f"PollerService initialized for {github_owner}/{github_repo}")
    
    async def start_background(self) -> None:
        """Start poller as background task."""
        if not self.poller_enabled:
            logger.info("Poller disabled, skipping background start")
            return
        
        logger.info("Starting GitHub poller in background")
        
        # Start the actual poller
        await self.github_poller.start_polling()
    
    async def shutdown(self) -> None:
        """Shutdown poller service."""
        if self.poller_enabled and hasattr(self, 'github_poller'):
            await self.github_poller.shutdown()
        logger.info("Poller service shutdown")
    
    def is_healthy(self) -> bool:
        """Check if poller is healthy."""
        if not self.poller_enabled:
            return True  # Disabled poller is considered healthy
        
        return hasattr(self, 'github_poller') and self.github_poller._running
    
    def get_status(self) -> dict:
        """Get detailed poller status."""
        if not self.poller_enabled:
            return {"enabled": False, "status": "disabled"}
        
        if hasattr(self, 'github_poller'):
            return {
                "enabled": True,
                "status": "running" if self.github_poller._running else "stopped",
                **self.github_poller.get_status()
            }
        
        return {"enabled": True, "status": "not_initialized"}