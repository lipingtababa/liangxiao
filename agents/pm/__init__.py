"""Project Manager Agent package.

This package contains the PM Agent that analyzes GitHub issues and creates
structured task breakdowns for the multi-agent system.
"""

from .agent import PMAgent
from .models import Task, IssueAnalysis, TaskBreakdown, PMAgentConfig

__all__ = ["PMAgent", "PMAgentConfig", "Task", "IssueAnalysis", "TaskBreakdown"]