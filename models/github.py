"""GitHub webhook and API data models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any, Dict
from datetime import datetime


class GitHubUser(BaseModel):
    """GitHub user representation."""
    login: str
    id: int
    type: str = "User"
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None


class GitHubLabel(BaseModel):
    """GitHub issue label representation."""
    name: str
    color: Optional[str] = None  # Make color optional as it's not always in webhook payload
    description: Optional[str] = None
    id: Optional[int] = None
    url: Optional[str] = None


class GitHubIssue(BaseModel):
    """GitHub issue representation following official webhook schema."""
    url: str  # API URL
    number: int
    state: Literal["open", "closed"]
    title: str
    body: Optional[str] = None
    user: GitHubUser
    labels: List[GitHubLabel] = []
    assignees: List[GitHubUser] = []
    milestone: Optional[Dict[str, Any]] = None
    comments: int = 0
    created_at: datetime
    updated_at: datetime
    # Additional fields that may be present but not in minimal schema
    html_url: Optional[str] = None
    id: Optional[int] = None
    assignee: Optional[GitHubUser] = None
    locked: Optional[bool] = False
    draft: Optional[bool] = None


class GitHubRepository(BaseModel):
    """GitHub repository representation following official webhook schema."""
    id: int
    full_name: str
    owner: GitHubUser
    private: bool
    name: str
    # Optional fields not required in minimal webhook payload
    html_url: Optional[str] = None
    description: Optional[str] = None
    default_branch: Optional[str] = None


class GitHubComment(BaseModel):
    """GitHub issue comment representation."""
    id: int
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    html_url: str


class IssueEvent(BaseModel):
    """GitHub issue webhook event."""
    action: Literal["opened", "edited", "closed", "reopened", "assigned", "unassigned", "labeled", "unlabeled"]
    issue: GitHubIssue
    repository: GitHubRepository
    sender: GitHubUser
    assignee: Optional[GitHubUser] = None
    label: Optional[GitHubLabel] = None


class IssueCommentEvent(BaseModel):
    """GitHub issue comment webhook event."""
    action: Literal["created", "edited", "deleted"]
    comment: GitHubComment
    issue: GitHubIssue
    repository: GitHubRepository
    sender: GitHubUser


class GitHubWebhookPayload(BaseModel):
    """Base class for webhook payloads."""
    zen: Optional[str] = None  # Zen message in ping events
    hook_id: Optional[int] = None  # Webhook ID
    hook: Optional[Dict[str, Any]] = None  # Webhook configuration


class PingEvent(GitHubWebhookPayload):
    """GitHub webhook ping event."""
    zen: str
    hook_id: int
    hook: Dict[str, Any]
    repository: GitHubRepository