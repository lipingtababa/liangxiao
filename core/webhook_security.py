"""Security utilities for webhook validation."""

import hmac
import hashlib
import time
from typing import Optional
from core.logging import get_logger

logger = get_logger(__name__)


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
        logger.warning("No signature provided in webhook")
        return False
    
    # Remove 'sha256=' prefix if present
    if signature.startswith('sha256='):
        signature = signature[7:]
    
    # Calculate expected signature
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison to prevent timing attacks
    is_valid = hmac.compare_digest(expected, signature)
    
    if not is_valid:
        logger.warning("Invalid webhook signature")
    
    return is_valid


def is_webhook_replay(
    timestamp: Optional[str],
    tolerance_seconds: int = 300
) -> bool:
    """
    Check if webhook is a replay attack based on timestamp.
    
    Args:
        timestamp: X-Hub-Signature header timestamp
        tolerance_seconds: Maximum age in seconds
    
    Returns:
        True if webhook is too old (potential replay)
    """
    if not timestamp:
        # If no timestamp, we can't validate, so assume it's valid
        return False
    
    try:
        webhook_time = int(timestamp)
        current_time = int(time.time())
        age = current_time - webhook_time
        
        if age > tolerance_seconds:
            logger.warning(f"Webhook is too old: {age} seconds")
            return True
        
        return False
    except (ValueError, TypeError):
        logger.warning(f"Invalid timestamp format: {timestamp}")
        return False


def validate_webhook_headers(
    signature: Optional[str],
    event_type: Optional[str],
    delivery_id: Optional[str]
) -> bool:
    """
    Validate required webhook headers are present.
    
    Args:
        signature: X-Hub-Signature-256 header
        event_type: X-GitHub-Event header
        delivery_id: X-GitHub-Delivery header
    
    Returns:
        True if all required headers are present
    """
    missing_headers = []
    
    if not signature:
        missing_headers.append("X-Hub-Signature-256")
    
    if not event_type:
        missing_headers.append("X-GitHub-Event")
    
    if not delivery_id:
        missing_headers.append("X-GitHub-Delivery")
    
    if missing_headers:
        logger.warning(f"Missing required headers: {', '.join(missing_headers)}")
        return False
    
    return True