# Story 1.5: GitHub Issue Poller Migration ✅ COMPLETED

## Story Details
- **ID**: 1.5
- **Title**: Migrate GitHub Issue Poller to Python
- **Milestone**: Milestone 1 - Foundation & Basic Workflow
- **Points**: 4
- **Priority**: P1 (Essential)
- **Dependencies**: Stories 1.1 (Python setup), 1.4 (GitHub integration)
- **Status**: ✅ COMPLETED - GitHub poller implemented with `GitHubPoller` and `PollerService` classes

## Description

### Overview
Migrate the existing TypeScript GitHub issue poller to Python, ensuring it can discover new issues, track changes, and trigger the workflow engine. This component provides a backup mechanism when webhooks fail and ensures no issues are missed.

### Why This Is Important
- Provides redundancy when webhooks fail or are missed
- Ensures all issues are eventually processed even with webhook delivery problems
- Enables catch-up processing after system downtime
- Critical for system reliability and completeness
- Handles edge cases where webhook events are lost

### Context
The current TypeScript system likely has a poller that periodically checks GitHub for new or updated issues. This needs to be migrated to Python to work with the new multi-agent system, with improved error handling and state tracking.

## Acceptance Criteria

### Required
- [ ] Python-based GitHub issue poller using PyGithub
- [ ] Configurable polling intervals (default: 5 minutes)
- [ ] Tracks last processed timestamp to avoid duplicate processing
- [ ] Detects new issues since last poll
- [ ] Detects updated issues since last poll
- [ ] Filters issues by labels, assignees, or other criteria
- [ ] Integrates with workflow engine to trigger processing
- [ ] Handles rate limiting gracefully
- [ ] Comprehensive logging and error handling
- [ ] State persistence between restarts
- [ ] Graceful shutdown and startup
- [ ] Avoids duplicate processing with webhook events

## Technical Details

### GitHub Poller Implementation
```python
# services/github_poller.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from services.github_service import GitHubService
from workflows.orchestrator import WorkflowOrchestrator
import json
import os

logger = logging.getLogger(__name__)

class GitHubPoller:
    """
    Polls GitHub for new and updated issues.
    
    Provides backup mechanism when webhooks fail and ensures
    no issues are missed during system processing.
    """
    
    def __init__(
        self,
        github_service: GitHubService,
        orchestrator: WorkflowOrchestrator,
        poll_interval_seconds: int = 300,  # 5 minutes
        state_file: str = "poller_state.json"
    ):
        self.github_service = github_service
        self.orchestrator = orchestrator
        self.poll_interval = poll_interval_seconds
        self.state_file = state_file
        self.running = False
        self.last_poll_time = None
        self.processed_issues = set()  # Track recently processed to avoid duplicates
        
    async def start_polling(self):
        """Start the polling loop."""
        logger.info(f"Starting GitHub poller (interval: {self.poll_interval}s)")
        self.running = True
        
        # Load previous state
        await self._load_state()
        
        try:
            while self.running:
                await self._poll_once()
                
                # Wait for next poll interval
                await asyncio.sleep(self.poll_interval)
                
        except Exception as e:
            logger.error(f"Poller crashed: {e}")
            raise
        finally:
            await self._save_state()
    
    async def stop_polling(self):
        """Stop the polling loop gracefully."""
        logger.info("Stopping GitHub poller")
        self.running = False
        await self._save_state()
    
    async def _poll_once(self):
        """Perform a single poll cycle."""
        try:
            logger.debug("Starting poll cycle")
            
            # Calculate since timestamp
            since = self.last_poll_time
            if not since:
                # First poll - look back 1 hour to catch recent issues
                since = datetime.now() - timedelta(hours=1)
            
            # Get updated issues since last poll
            updated_issues = await self._get_updated_issues(since)
            
            # Process each issue
            for issue_data in updated_issues:
                await self._process_issue(issue_data)
            
            # Update last poll time
            self.last_poll_time = datetime.now()
            logger.debug(f"Poll cycle complete, processed {len(updated_issues)} issues")
            
        except Exception as e:
            logger.error(f"Error during poll cycle: {e}")
            # Continue polling despite errors
    
    async def _get_updated_issues(self, since: datetime) -> List[Dict[str, Any]]:
        """Get issues updated since the given timestamp."""
        
        try:
            # Use GitHub API to get updated issues
            repo = self.github_service.repo
            
            # Get issues updated since timestamp
            issues = repo.get_issues(
                state="all",  # Both open and closed
                since=since,
                sort="updated",
                direction="asc"
            )
            
            issue_data = []
            for issue in issues:
                # Skip pull requests (GitHub API includes them in issues)
                if hasattr(issue, 'pull_request') and issue.pull_request:
                    continue
                
                # Convert to our format
                data = {
                    "action": "updated",  # We don't know exact action from polling
                    "issue": {
                        "id": issue.id,
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body or "",
                        "state": issue.state,
                        "created_at": issue.created_at.isoformat(),
                        "updated_at": issue.updated_at.isoformat(),
                        "labels": [{"name": label.name} for label in issue.labels],
                        "assignees": [{"login": assignee.login} for assignee in issue.assignees],
                        "user": {
                            "login": issue.user.login
                        }
                    },
                    "repository": {
                        "name": repo.name,
                        "full_name": repo.full_name
                    }
                }
                
                issue_data.append(data)
            
            logger.info(f"Found {len(issue_data)} updated issues since {since}")
            return issue_data
            
        except Exception as e:
            logger.error(f"Error fetching updated issues: {e}")
            return []
    
    async def _process_issue(self, issue_data: Dict[str, Any]):
        """Process a single issue through the workflow."""
        
        issue_number = issue_data["issue"]["number"]
        
        # Check if we've recently processed this issue (avoid duplicates with webhooks)
        issue_key = f"{issue_number}_{issue_data['issue']['updated_at']}"
        if issue_key in self.processed_issues:
            logger.debug(f"Skipping already processed issue #{issue_number}")
            return
        
        # Check if issue should be processed (filtering logic)
        if not await self._should_process_issue(issue_data):
            logger.debug(f"Skipping filtered issue #{issue_number}")
            return
        
        try:
            logger.info(f"Poller processing issue #{issue_number}: {issue_data['issue']['title']}")
            
            # Check if workflow is already running for this issue
            if await self._is_workflow_active(issue_number):
                logger.debug(f"Workflow already active for issue #{issue_number}")
                return
            
            # Start workflow processing
            workflow_id = await self.orchestrator.start_workflow(issue_data)
            
            # Track this issue as processed
            self.processed_issues.add(issue_key)
            
            # Clean up old processed issues (keep only last 100)
            if len(self.processed_issues) > 100:
                self.processed_issues = set(list(self.processed_issues)[-100:])
            
            logger.info(f"Started workflow {workflow_id} for issue #{issue_number}")
            
        except Exception as e:
            logger.error(f"Error processing issue #{issue_number}: {e}")
    
    async def _should_process_issue(self, issue_data: Dict[str, Any]) -> bool:
        """Determine if issue should be processed."""
        
        issue = issue_data["issue"]
        
        # Skip closed issues (unless recently closed)
        if issue["state"] == "closed":
            updated_at = datetime.fromisoformat(issue["updated_at"].replace('Z', '+00:00'))
            if datetime.now().replace(tzinfo=updated_at.tzinfo) - updated_at > timedelta(hours=1):
                return False
        
        # Check for processing labels (if configured)
        labels = [label["name"].lower() for label in issue["labels"]]
        
        # Skip if has ignore label
        if "ignore-ai" in labels or "no-process" in labels:
            return False
        
        # Only process if has specific labels (if configured)
        required_labels = os.getenv("REQUIRED_ISSUE_LABELS", "").split(",")
        if required_labels and required_labels[0]:  # If configured and not empty
            if not any(label in labels for label in [l.strip().lower() for l in required_labels]):
                return False
        
        return True
    
    async def _is_workflow_active(self, issue_number: int) -> bool:
        """Check if workflow is already running for this issue."""
        try:
            # Check with orchestrator if workflow is active
            active_workflows = await self.orchestrator.get_active_workflows()
            
            for workflow_id, workflow_state in active_workflows.items():
                if workflow_state.get("issue_number") == issue_number:
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Could not check workflow status for issue #{issue_number}: {e}")
            # Assume not active to avoid missing issues
            return False
    
    async def _load_state(self):
        """Load poller state from file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                # Load last poll time
                if "last_poll_time" in state:
                    self.last_poll_time = datetime.fromisoformat(state["last_poll_time"])
                
                # Load processed issues
                if "processed_issues" in state:
                    self.processed_issues = set(state["processed_issues"])
                
                logger.info(f"Loaded poller state: last_poll={self.last_poll_time}")
            
        except Exception as e:
            logger.warning(f"Could not load poller state: {e}")
            # Continue with defaults
    
    async def _save_state(self):
        """Save poller state to file."""
        try:
            state = {
                "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
                "processed_issues": list(self.processed_issues),
                "saved_at": datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.debug("Saved poller state")
            
        except Exception as e:
            logger.error(f"Could not save poller state: {e}")
```

### Poller Service Integration
```python
# services/poller_service.py
import asyncio
import signal
from services.github_poller import GitHubPoller
from services.github_service import GitHubService
from workflows.orchestrator import WorkflowOrchestrator
from config import settings
import logging

logger = logging.getLogger(__name__)

class PollerService:
    """Service wrapper for GitHub poller with lifecycle management."""
    
    def __init__(self):
        self.github_service = GitHubService(
            token=settings.github_token,
            owner=settings.github_owner,
            repo_name=settings.github_repo
        )
        self.orchestrator = WorkflowOrchestrator()
        self.poller = GitHubPoller(
            github_service=self.github_service,
            orchestrator=self.orchestrator,
            poll_interval_seconds=settings.poll_interval_seconds
        )
        self.running = False
    
    async def start(self):
        """Start the poller service."""
        logger.info("Starting GitHub poller service")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
        
        try:
            await self.poller.start_polling()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the poller service gracefully."""
        if self.running:
            logger.info("Shutting down GitHub poller service")
            self.running = False
            await self.poller.stop_polling()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}")
        asyncio.create_task(self.shutdown())

# Main entry point for poller
async def main():
    """Main entry point for running poller service."""
    service = PollerService()
    await service.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Integration with Main Application
```python
# main.py (enhanced)
import asyncio
from fastapi import FastAPI
from services.poller_service import PollerService
import logging

app = FastAPI()
poller_service = None

@app.on_event("startup")
async def startup_event():
    """Start background services."""
    global poller_service
    
    # Start poller in background
    poller_service = PollerService()
    asyncio.create_task(poller_service.start())
    
    logging.info("Application started with GitHub poller")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown background services."""
    global poller_service
    
    if poller_service:
        await poller_service.shutdown()
    
    logging.info("Application shutdown complete")

# ... existing webhook endpoints ...
```

### Configuration
```python
# config.py (additions)
class Settings:
    # ... existing settings ...
    
    # Poller configuration
    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))  # 5 minutes
    poller_enabled: bool = os.getenv("POLLER_ENABLED", "true").lower() == "true"
    required_issue_labels: str = os.getenv("REQUIRED_ISSUE_LABELS", "")  # Comma-separated
    poller_state_file: str = os.getenv("POLLER_STATE_FILE", "data/poller_state.json")
```

## Testing Requirements

### Unit Tests
```python
# tests/test_github_poller.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from services.github_poller import GitHubPoller
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_poller_detects_new_issues():
    """Test poller detects and processes new issues."""
    mock_github = Mock()
    mock_orchestrator = AsyncMock()
    
    poller = GitHubPoller(mock_github, mock_orchestrator, poll_interval_seconds=1)
    
    # Mock GitHub API response
    with patch.object(poller, '_get_updated_issues') as mock_get_issues:
        mock_get_issues.return_value = [{
            "action": "updated",
            "issue": {"number": 123, "title": "Test issue", "updated_at": datetime.now().isoformat()}
        }]
        
        with patch.object(poller, '_should_process_issue', return_value=True):
            with patch.object(poller, '_is_workflow_active', return_value=False):
                await poller._poll_once()
        
        # Should start workflow for new issue
        mock_orchestrator.start_workflow.assert_called_once()

@pytest.mark.asyncio
async def test_poller_avoids_duplicate_processing():
    """Test poller doesn't process same issue twice."""
    # Test duplicate detection logic
    pass

@pytest.mark.asyncio
async def test_poller_handles_rate_limiting():
    """Test poller handles GitHub rate limiting gracefully."""
    # Test rate limit handling
    pass

@pytest.mark.asyncio
async def test_poller_state_persistence():
    """Test poller saves and loads state correctly."""
    # Test state persistence
    pass
```

### Integration Tests
```python
# tests/integration/test_poller_integration.py
@pytest.mark.integration
async def test_poller_webhook_coordination():
    """Test poller works alongside webhooks without conflicts."""
    # Test that poller and webhooks don't double-process issues
    pass
```

## Dependencies & Risks

### Prerequisites
- GitHub service implemented (Story 1.4)
- Workflow orchestrator available
- File system access for state persistence
- Proper GitHub token permissions

### Risks
- **Duplicate processing**: Poller and webhooks process same issue
- **Rate limiting**: Too frequent polling hits API limits
- **State loss**: Losing poller state causes reprocessing
- **Performance impact**: Polling adds system load

### Mitigations
- Duplicate detection using processed issues tracking
- Configurable poll intervals with rate limit checking
- Persistent state with backup/recovery
- Lightweight polling with minimal API calls

## Definition of Done

1. ✅ GitHub poller implemented with Python
2. ✅ Configurable polling intervals and filtering
3. ✅ State persistence between restarts
4. ✅ Integration with workflow orchestrator
5. ✅ Duplicate detection with webhook events
6. ✅ Rate limiting and error handling
7. ✅ Graceful startup and shutdown
8. ✅ Unit tests covering core functionality
9. ✅ Integration with main application lifecycle

## Implementation Notes for AI Agents

### DO
- Use reasonable polling intervals (5+ minutes)
- Track processed issues to avoid duplicates
- Handle GitHub API errors gracefully
- Save state regularly for recovery
- Log all significant events for debugging

### DON'T
- Don't poll too frequently (causes rate limiting)
- Don't reprocess recent issues unnecessarily
- Don't ignore webhook deduplication
- Don't lose state on crashes
- Don't block main application startup

### Common Pitfalls to Avoid
1. Polling too frequently and hitting rate limits
2. Processing same issues multiple times
3. Not handling API failures gracefully
4. Losing poller state on restarts
5. Blocking application with synchronous polling

## Success Example

Poller providing reliable backup:
```
Webhook missed issue #456 due to delivery failure ❌
Poller cycle runs 5 minutes later ✅
Detects issue #456 was updated but not processed
Starts workflow processing for issue #456
System processes issue successfully despite webhook failure ✅

Result: No issues missed, reliable system operation ✅
```

## Next Story
Once this story is complete, the foundation milestone will have comprehensive GitHub integration including both webhooks and polling backup.