"""Configuration management using Pydantic settings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, Any


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "AI Orchestrator"
    debug: bool = False
    port: int = 8000
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-5"
    
    # GitHub
    github_token: str = Field(alias="GITHUB_PERSONAL_ACCESS_TOKEN")
    github_webhook_secret: str
    github_owner: str = "test"  # Default for testing
    github_repo: str = "test"   # Default for testing
    
    # LangChain
    langchain_tracing_v2: bool = True
    langchain_api_key: Optional[str] = None
    
    # Poller configuration (for future stories)
    poll_interval_seconds: int = 300  # 5 minutes
    poller_enabled: bool = True
    required_issue_labels: str = ""  # Comma-separated
    poller_state_file: str = "data/poller_state.json"
    
    # Security
    webhook_replay_window_seconds: int = 300
    
    # Workspace Configuration
    workspace_root: str = "workspaces"
    workspace_cleanup_days: int = 30  # Clean up workspaces older than 30 days
    max_concurrent_workspaces: int = 10  # Limit concurrent workspaces
    
    # AI Tool Configuration
    agent_tools: Dict[str, str] = {
        "developer": "claude",
        "navigator": "claude", 
        "analyst": "claude"
    }
    
    # OpenAI Settings
    openai_settings: Dict[str, Any] = {
        "model": "gpt-5",
        "temperature": 0.2
    }
    
    # Claude Settings  
    claude_settings: Dict[str, Any] = {
        "command": "claude",
        "default_timeout": 120,
        "max_retries": 2
    }

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}