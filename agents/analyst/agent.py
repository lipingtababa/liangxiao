"""Simplified Analyst Agent implementation.

This module contains the AnalystAgent class that converts GitHub issues into
clear acceptance criteria. Focuses on business requirements, not technical details.
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

import openai

from core.interfaces import (
    StepResult, AnalystInput, AnalystOutput, 
    create_step_result, WorkflowStates
)
from core.unified_logging import get_unified_logger, log_agent_start, log_agent_complete, log_agent_error
from core.exceptions import AgentExecutionError
from .persona import get_analyst_persona


logger = get_unified_logger(__name__)


class AnalystAgent:
    """
    Simplified Analyst agent focused on requirements analysis.
    
    Converts GitHub issues into clear acceptance criteria and identifies
    questions that need stakeholder clarification. Does NOT do technical
    analysis - that's the Developer's job.
    
    Key Features:
    - Creates clear acceptance criteria from issues
    - Identifies business rule clarifications needed
    - Assesses implementation complexity
    - Estimates effort required
    """
    
    def __init__(self, openai_client: Optional[openai.OpenAI] = None):
        """Initialize the Analyst Agent.
        
        Args:
            openai_client: OpenAI client for API calls
        """
        self.openai_client = openai_client or openai.OpenAI()
        self.total_analyses = 0
        self.total_tokens_used = 0
        
        logger.info("Simplified Analyst Agent initialized")
    
    async def execute(self, analyst_input: AnalystInput) -> StepResult:
        """Execute requirements analysis.
        
        Args:
            analyst_input: Input containing issue description
            
        Returns:
            StepResult containing AnalystOutput
        """
        start_time = datetime.utcnow()
        log_agent_start(logger, "Analyst Agent", analyst_input.issue_description)
        
        try:
            # Analyze requirements
            analysis = await self._analyze_requirements(analyst_input.issue_description)
            
            # Track metrics
            self.total_analyses += 1
            
            # Determine status based on clarification questions
            status = "needs_clarification" if analysis.clarification_questions else "success"
            
            # Calculate confidence based on clarity
            confidence = 0.9 if not analysis.clarification_questions else 0.6
            
            # Create result
            result = create_step_result(
                agent="analyst",
                status=status,
                output_data=analysis.model_dump(),
                confidence=confidence,
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_agent_complete(logger, "Analyst Agent", f"in {duration:.2f}s, status: {status}")
            
            return result
            
        except Exception as e:
            log_agent_error(logger, "Analyst Agent", str(e))
            return create_step_result(
                agent="analyst",
                status="failed",
                output_data={"error": str(e)},
                confidence=0.0,
            )
    
    async def _analyze_requirements(self, issue_description: str) -> AnalystOutput:
        """Analyze issue and create acceptance criteria.
        
        Args:
            issue_description: The GitHub issue text
            
        Returns:
            Requirements analysis with acceptance criteria
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""Analyze this GitHub issue and create acceptance criteria:

**Issue Description:**
{issue_description}

Return JSON with:
- acceptance_criteria: List of specific, testable criteria
- clarification_questions: Questions needing stakeholder input
- complexity: "simple", "medium", or "complex"  
- effort_estimate: Time estimate like "2 hours" or "1 day"
"""
                }
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.1,
                max_tokens=1500
            )
            
            # Track token usage
            if hasattr(response, 'usage'):
                self.total_tokens_used += response.usage.total_tokens
            
            # Parse response
            result_data = json.loads(response.choices[0].message.content)
            
            return AnalystOutput(
                acceptance_criteria=result_data.get("acceptance_criteria", []),
                clarification_questions=result_data.get("clarification_questions", []),
                complexity=result_data.get("complexity", "medium"),
                effort_estimate=result_data.get("effort_estimate", "unknown")
            )
            
        except Exception as e:
            logger.error(f"Requirements analysis failed: {e}")
            raise AgentExecutionError(f"Requirements analysis failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for requirements analysis."""
        return get_analyst_persona() + """

FOCUS ON:
1. Business requirements - What does the user/business need?
2. Acceptance criteria - How will we know it's done correctly?
3. Edge cases - What unusual scenarios must be handled?
4. Clarification questions - What's unclear that needs stakeholder input?

AVOID:
- Technical implementation details
- Code architecture decisions
- File-level specifications
- Low-level technical analysis

ACCEPTANCE CRITERIA GUIDELINES:
- Be specific and measurable
- Use "Given/When/Then" format when helpful
- Focus on user behavior and outcomes
- Include error cases and edge scenarios

CLARIFICATION QUESTIONS:
- Ask about business rules that are unclear
- Identify missing requirements
- Highlight conflicting or ambiguous statements
- Focus on policy decisions only stakeholders can make

COMPLEXITY ASSESSMENT:
- simple: Clear requirements, standard patterns, low risk
- medium: Some ambiguity, standard complexity, moderate risk  
- complex: High ambiguity, custom solutions needed, high risk

Always return valid JSON format."""
    
    def _get_next_suggestions(self, analysis: AnalystOutput) -> List[str]:
        """Get suggestions for next steps based on analysis.
        
        Args:
            analysis: The analysis output
            
        Returns:
            List of suggested next steps
        """
        suggestions = []
        
        if analysis.clarification_questions:
            suggestions.append("post_github_questions")
            suggestions.append("wait_for_stakeholder_input")
        else:
            suggestions.append("create_tests")
            if analysis.complexity == "simple":
                suggestions.append("implement_directly")
            else:
                suggestions.append("technical_planning")
        
        return suggestions
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            "total_analyses": self.total_analyses,
            "total_tokens_used": self.total_tokens_used,
            "average_tokens_per_analysis": (
                self.total_tokens_used / max(self.total_analyses, 1)
            )
        }


def create_analyst_agent(**kwargs):
    """Factory function to create an Analyst Agent."""
    # Use Claude Code implementation by default (no OpenAI dependency)
    from .claude_code_agent import ClaudeCodeAnalystAgent
    return ClaudeCodeAnalystAgent(**kwargs)