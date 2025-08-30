# Story 1.2: GitHub Webhook Migration ✅ COMPLETED

## Story Details
- **ID**: 1.2
- **Title**: Replace TypeScript Webhook with FastAPI Endpoint
- **Milestone**: Milestone 1 - Foundation & Basic Workflow
- **Points**: 5
- **Priority**: P0 (Critical Path)
- **Dependencies**: Story 1.1 (Python Project Setup)
- **Status**: ✅ COMPLETED - FastAPI webhooks implemented at `api/webhooks.py` with signature validation

## Description

### Overview
Migrate the webhook receiving functionality from the current TypeScript Express server to a new Python FastAPI endpoint. This webhook will receive GitHub issue events and trigger the multi-agent workflow. The endpoint must validate webhook signatures for security and handle various GitHub event types.

### Why This Is Important
- Entry point for all automated issue processing
- Security through signature validation prevents abuse
- FastAPI provides better async handling than Express
- Foundation for the entire workflow system

### Context
The current TypeScript webhook in `services/agent/src/webhook.ts` receives GitHub events but passes them to a broken single agent. We need to recreate this in Python with proper validation and error handling, preparing for the new multi-agent workflow.

## Acceptance Criteria

### Required
- [ ] POST endpoint at `/webhook/github` that accepts GitHub webhook payloads
- [ ] Webhook signature validation (X-Hub-Signature-256) implemented
- [ ] Handles 'issues' event with actions: opened, edited, labeled, assigned
- [ ] Handles 'issue_comment' event for future interaction
- [ ] Returns appropriate HTTP status codes (200 OK, 400 Bad Request, 401 Unauthorized)
- [ ] Logs all incoming webhooks with timestamp and event type
- [ ] Validates JSON payload structure using Pydantic models
- [ ] Queues events for processing (initially just logs them)
- [ ] Handles errors gracefully without exposing internal details
- [ ] Includes webhook setup instructions in documentation

## Technical Details

### Webhook Endpoint Structure
```python
# api/webhooks.py
from fastapi import APIRouter, Header, HTTPException, Request
from typing import Optional
import hmac
import hashlib
import json
from models.github import GitHubWebhookPayload, IssueEvent
from core.logging import logger

router = APIRouter()

@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """
    Receive and process GitHub webhook events.
    
    Validates signature, parses payload, and queues for processing.
    """
    # Implementation details below
```

### Pydantic Models for GitHub Events
```python
# models/github.py
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class GitHubUser(BaseModel):
    login: str
    id: int
    type: str = "User"

class GitHubLabel(BaseModel):
    name: str
    color: str
    description: Optional[str] = None

class GitHubIssue(BaseModel):
    number: int
    title: str
    body: Optional[str] = None
    state: Literal["open", "closed"]
    labels: List[GitHubLabel] = []
    assignee: Optional[GitHubUser] = None
    created_at: datetime
    updated_at: datetime
    html_url: str

class GitHubRepository(BaseModel):
    name: str
    full_name: str
    owner: GitHubUser
    private: bool

class IssueEvent(BaseModel):
    action: Literal["opened", "edited", "closed", "reopened", "assigned", "labeled"]
    issue: GitHubIssue
    repository: GitHubRepository
    sender: GitHubUser

class GitHubWebhookPayload(BaseModel):
    """Base class for webhook payloads"""
    pass
```

### Signature Validation
```python
# core/webhook_security.py
import hmac
import hashlib
from typing import Optional

def verify_webhook_signature(
    payload: bytes,
    signature: Optional[str],
    secret: str
) -> bool:
    """
    Verify GitHub webhook signature.
    
    Args:
        payload: Raw request body bytes
        signature: X-Hub-Signature-256 header value
        secret: Webhook secret from configuration
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not signature:
        return False
    
    # Remove 'sha256=' prefix
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    # Calculate expected signature
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected, signature)
```

### Complete Webhook Handler
```python
# api/webhooks.py (full implementation)
@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None)
):
    """Process GitHub webhook events."""
    
    # Get raw body for signature validation
    body = await request.body()
    
    # Validate signature
    if not verify_webhook_signature(
        body,
        x_hub_signature_256,
        settings.github_webhook_secret
    ):
        logger.warning(f"Invalid webhook signature from {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Log event
    logger.info(
        f"Received GitHub webhook: event={x_github_event}, "
        f"delivery={x_github_delivery}"
    )
    
    # Handle different event types
    if x_github_event == "issues":
        return await handle_issue_event(payload)
    elif x_github_event == "issue_comment":
        return await handle_comment_event(payload)
    else:
        logger.info(f"Ignoring event type: {x_github_event}")
        return {"status": "ignored", "event": x_github_event}

async def handle_issue_event(payload: dict):
    """Handle issue events."""
    try:
        event = IssueEvent.model_validate(payload)
        
        # Only process certain actions
        if event.action not in ["opened", "edited", "labeled", "assigned"]:
            return {"status": "ignored", "action": event.action}
        
        # TODO: Queue for processing (Story 1.3 will implement)
        logger.info(
            f"Issue event ready for processing: "
            f"#{event.issue.number} - {event.issue.title}"
        )
        
        return {
            "status": "queued",
            "issue": event.issue.number,
            "action": event.action
        }
        
    except Exception as e:
        logger.error(f"Failed to process issue event: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")
```

### Configuration Updates
```python
# config.py (additions)
class Settings(BaseSettings):
    # ... existing fields ...
    
    # GitHub Webhook
    github_webhook_secret: str
    github_owner: str
    github_repo: str
    
    # Security
    webhook_replay_window_seconds: int = 300
```

## Testing Requirements

### Unit Tests
```python
# tests/test_webhook.py
import pytest
from fastapi.testclient import TestClient
import hmac
import hashlib
import json

def test_webhook_without_signature(client):
    """Test webhook rejection without signature."""
    response = client.post(
        "/webhook/github",
        json={"test": "data"}
    )
    assert response.status_code == 401

def test_webhook_with_valid_signature(client, webhook_secret):
    """Test webhook acceptance with valid signature."""
    payload = json.dumps({"action": "opened", "issue": {...}})
    signature = "sha256=" + hmac.new(
        webhook_secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    response = client.post(
        "/webhook/github",
        content=payload,
        headers={
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "issues"
        }
    )
    assert response.status_code == 200

def test_webhook_invalid_json(client, valid_signature):
    """Test webhook with invalid JSON."""
    response = client.post(
        "/webhook/github",
        content="not json",
        headers={"X-Hub-Signature-256": valid_signature}
    )
    assert response.status_code == 400
```

### Integration Tests
```python
# tests/integration/test_github_webhook.py
async def test_full_issue_flow():
    """Test complete issue webhook flow."""
    # Send webhook
    # Verify logging
    # Check event queued (when queue implemented)
    pass
```

### Manual Testing Checklist
- [ ] Use ngrok to expose local endpoint
- [ ] Configure GitHub webhook in repository settings
- [ ] Create test issue and verify webhook received
- [ ] Check signature validation works
- [ ] Verify all event types handled correctly
- [ ] Test error cases (bad signature, malformed JSON)

## Dependencies & Risks

### Prerequisites
- Story 1.1 completed (FastAPI app running)
- GitHub repository access for webhook configuration
- Webhook secret generated and stored in .env

### Risks
- **Signature validation bugs**: Could allow unauthorized access
- **Payload parsing errors**: Malformed events could crash handler
- **Missing event types**: GitHub might send unexpected events
- **Rate limiting**: Too many webhooks could overwhelm system

### Mitigations
- Thorough testing of signature validation
- Try/catch blocks around all parsing
- Default handler for unknown events
- Consider rate limiting in future stories

## Definition of Done

1. ✅ All acceptance criteria met
2. ✅ Webhook endpoint responds to GitHub
3. ✅ Signature validation working correctly
4. ✅ All specified event types handled
5. ✅ Comprehensive error handling
6. ✅ Unit tests passing
7. ✅ Manual test with real GitHub webhook
8. ✅ Logging provides good observability
9. ✅ Documentation updated with setup instructions

## Implementation Notes for AI Agents

### DO
- Validate everything - never trust external input
- Use Pydantic for strict type validation
- Log all events for debugging
- Return meaningful status codes
- Handle errors gracefully

### DON'T
- Don't process events synchronously (queue them)
- Don't expose internal errors to webhook response
- Don't skip signature validation in any case
- Don't parse JSON manually - use Pydantic
- Don't forget to handle all event actions

### Common Pitfalls to Avoid
1. String vs bytes confusion in signature validation
2. Forgetting to await async request.body()
3. Not handling missing headers gracefully
4. Case sensitivity in event type comparison
5. Exposing sensitive data in error messages

## Success Example

When complete, you should be able to:
```bash
# Start server
python main.py

# Test with curl (with signature)
curl -X POST http://localhost:8000/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: issues" \
  -H "X-Hub-Signature-256: sha256=..." \
  -d '{"action": "opened", "issue": {...}}'

# Or use GitHub's webhook test feature
# 1. Go to Settings > Webhooks in your repo
# 2. Add webhook URL (use ngrok for local)
# 3. Set secret
# 4. Send test event
# 5. Verify 200 response
```

## Next Story
Once this story is complete, proceed to [Story 1.3: LangGraph Workflow Engine Setup](story-1.3-workflow-engine.md)