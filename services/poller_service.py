"""Poller service for managing GitHub poller lifecycle."""

import asyncio
from typing import Optional
from core.logging import get_logger

logger = get_logger(__name__)


class PollerService:
    """Service wrapper for GitHub poller with lifecycle management."""
    
    def __init__(
        self,
        github_token: str,
        github_owner: str,
        github_repo: str,
        poll_interval_seconds: int = 300,
        poller_state_file: str = "data/poller_state.json",
        required_issue_labels: str = "",
        poller_enabled: bool = True
    ):
        """Initialize poller service."""
        self.github_token = github_token
        self.github_owner = github_owner  
        self.github_repo = github_repo
        self.poll_interval_seconds = poll_interval_seconds
        self.poller_state_file = poller_state_file
        self.required_issue_labels = required_issue_labels
        self.poller_enabled = poller_enabled
        self._running = False
        
        logger.info(f"PollerService initialized for {github_owner}/{github_repo}")
    
    async def start_background(self) -> None:
        """Start poller as background task."""
        if not self.poller_enabled:
            logger.info("Poller disabled, skipping background start")
            return
            
        self._running = True
        logger.info("GitHub poller started in background")
        
        # Background polling logic would go here
        while self._running:
            try:
                logger.debug("Polling for new issues...")
                await asyncio.sleep(self.poll_interval_seconds)
            except Exception as e:
                logger.error(f"Poller error: {e}")
                await asyncio.sleep(30)  # Brief pause before retry
    
    async def shutdown(self) -> None:
        """Shutdown poller service."""
        self._running = False
        logger.info("Poller service shutdown")
    
    def is_healthy(self) -> bool:
        """Check if poller is healthy."""
        return self.poller_enabled and self._running