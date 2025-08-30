"""Analyst Agent module for requirements analysis and codebase analysis.

This module contains the Analyst Agent that performs thorough requirements 
gathering, codebase analysis, and documentation creation to prevent 
implementation disasters like PR #23.

Key Components:
- AnalystAgent: Main agent class for analysis tasks
- RequirementSpec: Individual requirement specification
- CodebaseAnalysis: Analysis of existing codebase 
- TechnicalSpecification: Complete technical specification

The Analyst Agent ensures developers have clear, complete requirements
before coding by reading and understanding existing code first.
"""

from .agent import AnalystAgent
from .models import RequirementSpec, CodebaseAnalysis, TechnicalSpecification

__all__ = [
    "AnalystAgent",
    "RequirementSpec", 
    "CodebaseAnalysis",
    "TechnicalSpecification"
]