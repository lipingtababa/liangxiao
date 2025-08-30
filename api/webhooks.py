"""GitHub webhook endpoints."""

from fastapi import APIRouter, Header, HTTPException, Request
from typing import Optional, Dict, Any
import json
from datetime import datetime

from core.logging import get_logger
from core.webhook_security import (
    verify_webhook_signature,
    validate_webhook_headers,
    is_webhook_replay
)
from models.github import (
    IssueEvent,
    IssueCommentEvent,
    PingEvent
)
from config import Settings
from workflows.orchestrator import WorkflowOrchestrator

logger = get_logger(__name__)
settings = Settings()
router = APIRouter()

# Initialize workflow orchestrator
orchestrator = WorkflowOrchestrator()


@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
    x_hub_signature: Optional[str] = Header(None)  # Legacy signature header
) -> Dict[str, Any]:
    """
    Process GitHub webhook events.
    
    Validates signature, parses payload, and queues events for processing.
    
    Returns:
        Dict containing processing status and event information
    """
    # Get raw body for signature validation
    body = await request.body()
    
    # Validate required headers
    if not validate_webhook_headers(
        x_hub_signature_256,
        x_github_event,
        x_github_delivery
    ):
        raise HTTPException(
            status_code=400,
            detail="Missing required webhook headers"
        )
    
    # Validate signature
    if not verify_webhook_signature(
        body,
        x_hub_signature_256,
        settings.github_webhook_secret
    ):
        logger.warning(
            f"Invalid webhook signature from {request.client.host if request.client else 'unknown'} "
            f"for delivery {x_github_delivery}"
        )
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Check for replay attacks
    if is_webhook_replay(x_hub_signature, settings.webhook_replay_window_seconds):
        logger.warning(f"Potential replay attack detected for delivery {x_github_delivery}")
        raise HTTPException(status_code=401, detail="Request too old")
    
    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Log incoming webhook
    logger.info(
        f"Received GitHub webhook: "
        f"event={x_github_event}, "
        f"delivery={x_github_delivery}, "
        f"timestamp={datetime.utcnow().isoformat()}"
    )
    
    # Handle different event types
    try:
        if x_github_event == "ping":
            return await handle_ping_event(payload)
        elif x_github_event == "issues":
            return await handle_issue_event(payload)
        elif x_github_event == "issue_comment":
            return await handle_comment_event(payload)
        else:
            logger.info(f"Ignoring unsupported event type: {x_github_event}")
            return {
                "status": "ignored",
                "event": x_github_event,
                "message": "Event type not supported"
            }
    except Exception as e:
        logger.error(f"Failed to process webhook event: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing webhook"
        )


async def handle_ping_event(payload: dict) -> Dict[str, Any]:
    """
    Handle GitHub webhook ping events.
    
    Args:
        payload: Webhook payload dictionary
    
    Returns:
        Response indicating successful ping
    """
    try:
        event = PingEvent.model_validate(payload)
        logger.info(f"Webhook ping received for repository: {event.repository.full_name}")
        
        return {
            "status": "ok",
            "event": "ping",
            "message": "Webhook is configured correctly",
            "repository": event.repository.full_name
        }
    except Exception as e:
        logger.error(f"Failed to process ping event: {e}")
        raise HTTPException(status_code=400, detail="Invalid ping event payload")


async def handle_issue_event(payload: dict) -> Dict[str, Any]:
    """
    Handle GitHub issue events by starting a workflow.
    
    Args:
        payload: Webhook payload dictionary
    
    Returns:
        Response indicating workflow start status
    """
    try:
        event = IssueEvent.model_validate(payload)
        
        # Only process certain actions
        supported_actions = ["opened", "edited", "labeled", "assigned"]
        if event.action not in supported_actions:
            logger.info(f"Ignoring issue action: {event.action}")
            return {
                "status": "ignored",
                "action": event.action,
                "message": f"Action '{event.action}' not processed"
            }
        
        logger.info(
            f"Starting workflow for issue event: "
            f"#{event.issue.number} - {event.issue.title} "
            f"[{event.action}] in {event.repository.full_name}"
        )
        
        # Start workflow
        try:
            workflow_id = await orchestrator.start_workflow(event)
            
            return {
                "status": "workflow_started",
                "event": "issues",
                "action": event.action,
                "workflow_id": workflow_id,
                "issue": {
                    "number": event.issue.number,
                    "title": event.issue.title,
                    "url": event.issue.html_url
                },
                "repository": event.repository.full_name,
                "message": "Workflow started successfully"
            }
        
        except ValueError as e:
            # Workflow already exists
            logger.warning(f"Workflow already exists for issue #{event.issue.number}: {e}")
            return {
                "status": "workflow_exists",
                "event": "issues",
                "action": event.action,
                "issue": {
                    "number": event.issue.number,
                    "title": event.issue.title,
                    "url": event.issue.html_url
                },
                "repository": event.repository.full_name,
                "message": "Workflow already running for this issue"
            }
        
    except Exception as e:
        logger.error(f"Failed to process issue event: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid issue event payload")


async def handle_comment_event(payload: dict) -> Dict[str, Any]:
    """
    Handle GitHub issue comment events.
    
    Args:
        payload: Webhook payload dictionary
    
    Returns:
        Response indicating event processing status
    """
    try:
        event = IssueCommentEvent.model_validate(payload)
        
        # Only process comment creation for now
        if event.action != "created":
            logger.info(f"Ignoring comment action: {event.action}")
            return {
                "status": "ignored",
                "action": event.action,
                "message": f"Comment action '{event.action}' not processed"
            }
        
        logger.info(
            f"Comment event received: "
            f"Issue #{event.issue.number} in {event.repository.full_name} "
            f"by {event.sender.login}"
        )
        
        # TODO: Process comment for agent communication (future stories)
        # For now, we just acknowledge receipt
        
        return {
            "status": "received",
            "event": "issue_comment",
            "action": event.action,
            "issue": event.issue.number,
            "repository": event.repository.full_name,
            "message": "Comment received"
        }
        
    except Exception as e:
        logger.error(f"Failed to process comment event: {e}")
        raise HTTPException(status_code=400, detail="Invalid comment event payload")


@router.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """
    Get the status of a workflow.
    
    Args:
        workflow_id: Workflow identifier
    
    Returns:
        Workflow status and summary
    """
    try:
        # Get workflow summary
        summary = await orchestrator.get_workflow_summary(workflow_id)
        
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow not found: {workflow_id}"
            )
        
        return {
            "workflow_id": workflow_id,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve workflow status"
        )


@router.get("/workflows")
async def get_active_workflows() -> Dict[str, Any]:
    """
    Get information about all active workflows.
    
    Returns:
        List of active workflows with their status
    """
    try:
        workflows = orchestrator.get_active_workflows()
        stats = orchestrator.get_stats()
        
        return {
            "workflows": workflows,
            "stats": stats,
            "total": len(workflows)
        }
        
    except Exception as e:
        logger.error(f"Failed to get active workflows: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve workflows"
        )