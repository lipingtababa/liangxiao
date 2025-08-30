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
    color: str
    description: Optional[str] = None
    id: Optional[int] = None
    url: Optional[str] = None


class GitHubIssue(BaseModel):
    """GitHub issue representation."""
    number: int
    title: str
    body: Optional[str] = None
    state: Literal["open", "closed"]
    labels: List[GitHubLabel] = []
    assignee: Optional[GitHubUser] = None
    assignees: List[GitHubUser] = []
    created_at: datetime
    updated_at: datetime
    html_url: str
    id: int
    url: str
    user: GitHubUser
    locked: bool = False
    draft: Optional[bool] = None


class GitHubRepository(BaseModel):
    """GitHub repository representation."""
    name: str
    full_name: str
    owner: GitHubUser
    private: bool
    id: int
    html_url: str
    description: Optional[str] = None
    default_branch: str = "main"


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