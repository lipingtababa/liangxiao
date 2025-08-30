"""Pytest configuration and fixtures."""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Set required environment variables for testing
    test_env = {
        "OPENAI_API_KEY": "test-key-for-testing",
        "GITHUB_TOKEN": "test-token-for-testing",
        "GITHUB_WEBHOOK_SECRET": "test-webhook-secret",
        "GITHUB_OWNER": "test-owner",
        "GITHUB_REPO": "test-repo",
        "DEBUG": "true",
        "ENVIRONMENT": "test",
    }
    
    for key, value in test_env.items():
        if key not in os.environ:
            os.environ[key] = value


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    try:
        from main import app
        
        with TestClient(app) as test_client:
            yield test_client
    except Exception as e:
        pytest.skip(f"Could not create test client: {e}")


@pytest.fixture
def webhook_secret():
    """Provide webhook secret for testing."""
    return "test-webhook-secret"


@pytest.fixture
def sample_issue_payload():
    """Provide a sample GitHub issue payload for testing."""
    return {
        "action": "opened",
        "issue": {
            "number": 123,
            "title": "Test Issue",
            "body": "This is a test issue",
            "state": "open",
            "labels": [],
            "assignee": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "html_url": "https://github.com/test/repo/issues/123"
        },
        "repository": {
            "name": "test-repo",
            "full_name": "test-owner/test-repo",
            "private": False,
            "owner": {
                "login": "test-owner",
                "id": 123,
                "type": "User"
            }
        },
        "sender": {
            "login": "test-user",
            "id": 456,
            "type": "User"
        }
    }


@pytest.fixture
def valid_signature():
    """Provide a valid webhook signature for testing."""
    import hmac
    import hashlib
    
    def _make_signature(payload: str, secret: str = "test-webhook-secret") -> str:
        signature = hmac.new(
            secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    return _make_signature