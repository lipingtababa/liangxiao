"""Agent modules for AI Coding Team orchestrator.

This package contains specialized agents for different aspects of software development:
- PM Agent: Project management and task breakdown
- Navigator Agent: Code review and quality assurance  
- Analyst Agent: Requirements analysis and codebase analysis
- Tester Agent: Testing and quality validation (IMPLEMENTED)

Each agent is designed to work collaboratively in the multi-agent system.
"""

from .pm import PMAgent
from .navigator.agent import NavigatorAgent
from .analyst import AnalystAgent
from .tester.agent import TesterAgent, create_tester_agent
from .developer.agent import DeveloperAgent, create_developer_agent

__all__ = [
    "PMAgent",
    "NavigatorAgent", 
    "AnalystAgent",
    "TesterAgent", 
    "create_tester_agent",
    "DeveloperAgent",
    "create_developer_agent"
]