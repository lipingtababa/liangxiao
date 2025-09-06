"""GitHub webhook endpoints."""

from fastapi import APIRouter, Header, HTTPException, Request
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

from core.logging import get_logger, set_request_id, set_request_context, LogContext
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
from workflows.dynamic_orchestrator import DynamicOrchestrator

logger = get_logger(__name__)
settings = Settings()
router = APIRouter()

# Lazy-loaded dynamic orchestrator (replaces broken LangGraph system)
# This is initialized on first use to avoid environment variable issues during import
orchestrator = None

def get_orchestrator():
    """Get or create the dynamic orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        # Ensure env variables are loaded (happens at import time via core.env_loader)
        orchestrator = DynamicOrchestrator()
    return orchestrator

# Track recent webhook requests for debugging
recent_webhooks = []  # Will store last 100 webhook requests
MAX_WEBHOOK_HISTORY = 100


@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
    x_hub_signature: Optional[str] = Header(None)  # Legacy signature header
) -> Dict[str, Any]:
    """
    Process GitHub webhook events with comprehensive logging.
    
    Validates signature, parses payload, and queues events for processing.
    
    Returns:
        Dict containing processing status and event information
    """
    # Set up request tracking
    request_id = set_request_id(x_github_delivery or None)
    set_request_context(
        event_type=x_github_event,
        delivery_id=x_github_delivery,
        source_ip=request.client.host if request.client else "unknown"
    )
    
    # Log incoming webhook
    logger.info(f"Webhook received: {x_github_event} event")
    logger.debug(f"Headers: event={x_github_event}, delivery={x_github_delivery}, signature_present={bool(x_hub_signature_256)}")
    
    # Get raw body for signature validation
    body = await request.body()
    logger.debug(f"Payload size: {len(body)} bytes")
    
    # Validate required headers
    logger.debug("Validating webhook headers...")
    if not validate_webhook_headers(
        x_hub_signature_256,
        x_github_event,
        x_github_delivery
    ):
        logger.error("Missing required webhook headers")
        logger.debug(f"Headers received: event={x_github_event}, delivery={x_github_delivery}, signature={bool(x_hub_signature_256)}")
        
        # Track failed request
        _track_webhook_request(
            x_github_delivery or "unknown",
            x_github_event or "unknown",
            "failed",
            "Missing required headers"
        )
        
        raise HTTPException(
            status_code=400,
            detail="Missing required webhook headers"
        )
    
    # Validate signature
    logger.debug("Verifying webhook signature...")
    if not verify_webhook_signature(
        body,
        x_hub_signature_256,
        settings.github_webhook_secret
    ):
        logger.warning("Invalid webhook signature")
        logger.debug(f"Signature verification failed for delivery {x_github_delivery}")
        
        # Track failed request
        _track_webhook_request(
            x_github_delivery,
            x_github_event,
            "failed",
            "Invalid signature"
        )
        
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    logger.debug("✓ Signature verified successfully")
    
    # Check for replay attacks
    logger.debug("Checking for replay attacks...")
    if is_webhook_replay(x_hub_signature, settings.webhook_replay_window_seconds):
        logger.warning("Potential replay attack detected")
        
        # Track failed request
        _track_webhook_request(
            x_github_delivery,
            x_github_event,
            "failed",
            "Potential replay attack"
        )
        
        raise HTTPException(status_code=401, detail="Request too old")
    
    logger.debug("✓ Replay check passed")
    
    # Parse JSON payload
    logger.debug("Parsing webhook payload...")
    try:
        payload = json.loads(body)
        logger.debug(f"✓ Payload parsed successfully (keys: {list(payload.keys())[:5]}...)")
        
        # Add payload info to context
        if 'repository' in payload:
            set_request_context(repository=payload['repository'].get('full_name', 'unknown'))
        if 'issue' in payload:
            set_request_context(
                issue_number=payload['issue'].get('number'),
                issue_title=payload['issue'].get('title', '')[:50]
            )
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        
        # Track failed request
        _track_webhook_request(
            x_github_delivery,
            x_github_event,
            "failed",
            f"Invalid JSON: {str(e)}"
        )
        
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Track webhook request
    _track_webhook_request(
        x_github_delivery,
        x_github_event,
        "processing",
        None,
        payload
    )
    
    # Handle different event types
    try:
        logger.info(f"Processing {x_github_event} event...")
        
        if x_github_event == "ping":
            result = await handle_ping_event(payload)
            _update_webhook_status(x_github_delivery, "success", result)
            return result
            
        elif x_github_event == "issues":
            result = await handle_issue_event(payload)
            _update_webhook_status(x_github_delivery, "success", result)
            return result
            
        elif x_github_event == "issue_comment":
            result = await handle_comment_event(payload)
            _update_webhook_status(x_github_delivery, "success", result)
            return result
            
        else:
            logger.info(f"Ignoring unsupported event type: {x_github_event}")
            result = {
                "status": "ignored",
                "event": x_github_event,
                "message": "Event type not supported"
            }
            _update_webhook_status(x_github_delivery, "ignored", result)
            return result
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Failed to process webhook event: {e}", exc_info=True)
        
        # Track failed request
        _update_webhook_status(x_github_delivery, "failed", {"error": str(e)})
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing webhook"
        )


def _track_webhook_request(
    delivery_id: str,
    event_type: str,
    status: str,
    error: Optional[str] = None,
    payload: Optional[dict] = None
) -> None:
    """Track webhook request for debugging."""
    global recent_webhooks
    
    webhook_info = {
        "delivery_id": delivery_id,
        "event_type": event_type,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "error": error
    }
    
    # Add limited payload info
    if payload:
        if 'repository' in payload:
            webhook_info['repository'] = payload['repository'].get('full_name')
        if 'issue' in payload:
            webhook_info['issue_number'] = payload['issue'].get('number')
        if 'action' in payload:
            webhook_info['action'] = payload['action']
    
    recent_webhooks.append(webhook_info)
    
    # Keep only last N webhooks
    if len(recent_webhooks) > MAX_WEBHOOK_HISTORY:
        recent_webhooks = recent_webhooks[-MAX_WEBHOOK_HISTORY:]


def _update_webhook_status(delivery_id: str, status: str, result: Optional[dict] = None) -> None:
    """Update the status of a tracked webhook."""
    global recent_webhooks
    
    for webhook in recent_webhooks:
        if webhook['delivery_id'] == delivery_id:
            webhook['status'] = status
            webhook['completed_at'] = datetime.utcnow().isoformat()
            if result:
                webhook['result'] = result
            break


def get_recent_webhooks() -> List[Dict[str, Any]]:
    """Get list of recent webhook requests."""
    return recent_webhooks.copy()


async def handle_ping_event(payload: dict) -> Dict[str, Any]:
    """
    Handle GitHub webhook ping events with logging.
    
    Args:
        payload: Webhook payload dictionary
    
    Returns:
        Response indicating successful ping
    """
    try:
        event = PingEvent.model_validate(payload)
        logger.info(f"✓ Webhook ping validated for repository: {event.repository.full_name}")
        
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
    Handle GitHub issue events by starting a workflow with detailed logging.
    
    Args:
        payload: Webhook payload dictionary
    
    Returns:
        Response indicating workflow start status
    """
    with LogContext(
        issue_number=payload.get('issue', {}).get('number'),
        action=payload.get('action')
    ):
        try:
            logger.debug("Validating issue event payload...")
            event = IssueEvent.model_validate(payload)
            logger.debug(f"✓ Issue event validated: #{event.issue.number} - {event.action}")
        
            # Only process certain actions
            supported_actions = ["opened", "edited", "labeled", "assigned"]
            if event.action not in supported_actions:
                logger.info(f"Ignoring unsupported issue action: {event.action}")
                logger.debug(f"Supported actions: {supported_actions}")
                return {
                    "status": "ignored",
                    "action": event.action,
                    "message": f"Action '{event.action}' not processed"
                }
        
            logger.info(
                f"Processing issue event: #{event.issue.number} - "
                f"{event.issue.title[:50]}{'...' if len(event.issue.title) > 50 else ''}"
            )
            logger.debug(
                f"Issue details: action={event.action}, "
                f"labels={[l.name for l in event.issue.labels]}, "
                f"assignees={[a.login for a in event.issue.assignees]}"
            )
        
            # Start workflow
            logger.info("Initiating workflow for issue...")
            try:
                workflow_id = await get_orchestrator().start_workflow(event)
                logger.info(f"✓ Workflow started successfully: {workflow_id}")
            except Exception as e:
                logger.error(f"Failed to start workflow: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to start workflow: {str(e)}"
                )
            
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
        
        except Exception as e:
            logger.error(f"Failed to process issue event: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail="Invalid issue event payload")


async def handle_comment_event(payload: dict) -> Dict[str, Any]:
    """
    Handle GitHub issue comment events with logging.
    
    Args:
        payload: Webhook payload dictionary
    
    Returns:
        Response indicating event processing status
    """
    with LogContext(
        issue_number=payload.get('issue', {}).get('number'),
        comment_action=payload.get('action')
    ):
        try:
            logger.debug("Validating issue comment event...")
            event = IssueCommentEvent.model_validate(payload)
            logger.debug(f"✓ Comment event validated: Issue #{event.issue.number}")
        
            # Only process comment creation for now
            if event.action != "created":
                logger.info(f"Ignoring non-creation comment action: {event.action}")
                return {
                    "status": "ignored",
                    "action": event.action,
                    "message": f"Comment action '{event.action}' not processed"
                }
        
            logger.info(
                f"Processing comment from {event.sender.login} on issue #{event.issue.number}"
            )
            logger.debug(
                f"Comment preview: {event.comment.body[:100]}{'...' if len(event.comment.body) > 100 else ''}"
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
            logger.error(f"Failed to process comment event: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail="Invalid comment event payload")


@router.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """
    Get the status of a workflow with logging.
    
    Args:
        workflow_id: Workflow identifier
    
    Returns:
        Workflow status and summary
    """
    logger.debug(f"Retrieving workflow status for: {workflow_id}")
    
    try:
        # Get workflow summary
        summary = await get_orchestrator().get_workflow_summary(workflow_id)
        
        if not summary:
            logger.warning(f"Workflow not found: {workflow_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Workflow not found: {workflow_id}"
            )
        
        logger.debug(f"Retrieved workflow summary: status={summary.get('status')}")
        
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
    Get information about all active workflows with logging.
    
    Returns:
        List of active workflows with their status
    """
    logger.debug("Retrieving active workflows...")
    
    try:
        workflows = get_orchestrator().get_active_workflows()
        stats = get_orchestrator().get_stats()
        
        logger.debug(f"Found {len(workflows)} active workflows")
        logger.debug(f"Stats: {stats}")
        
        return {
            "workflows": workflows,
            "stats": stats,
            "total": len(workflows)
        }
        
    except Exception as e:
        logger.error(f"Failed to get active workflows: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve workflows"
        )


@router.post("/webhook/github/test")
async def github_webhook_test(request: Request) -> Dict[str, Any]:
    """
    Test webhook endpoint that bypasses signature verification.
    
    For testing purposes only - allows workflow testing without valid signatures.
    """
    logger.info("Test webhook endpoint called (bypassing signature verification)")
    
    try:
        # Get raw body
        body = await request.body()
        payload = json.loads(body)
        
        logger.info(f"Test webhook payload: action={payload.get('action')}, issue={payload.get('issue', {}).get('number')}")
        
        # Process directly without signature verification  
        if payload.get("action") == "opened" and "issue" in payload:
            # Create event and start workflow
            try:
                event = IssueEvent.model_validate(payload)
                workflow_id = await get_orchestrator().start_workflow(event)
                
                logger.info(f"Test workflow started: {workflow_id}")
                
                return {
                    "status": "workflow_started",
                    "workflow_id": workflow_id,
                    "issue": payload["issue"]["number"],
                    "message": "Test workflow started (bypassed signature verification)"
                }
                
            except Exception as e:
                logger.error(f"Failed to start test workflow: {e}", exc_info=True)
                return {
                    "status": "failed", 
                    "error": str(e),
                    "message": "Test workflow failed to start"
                }
        
        return {
            "status": "ignored", 
            "action": payload.get("action"),
            "message": "Test endpoint - action not processed"
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in test webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    except Exception as e:
        logger.error(f"Test webhook processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Test webhook processing failed")