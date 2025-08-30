"""Requirements Navigator - Specialized navigator for requirements review.

This module provides the RequirementsNavigator class that extends the NavigatorAgent
to specialize in reviewing requirements documentation for quality, completeness,
and clarity. It prevents implementation disasters like PR #23 by ensuring
requirements are thorough and unambiguous before development begins.
"""

import logging
import json
from typing import List, Dict, Any, Literal
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from .agent import NavigatorAgent, ReviewFeedback, ReviewDecision
from core.logging import get_logger

logger = get_logger(__name__)


class RequirementsIssue(BaseModel):
    """Specific issue found in requirements review."""
    
    category: Literal["clarity", "completeness", "testability", "specificity", "consistency"] = Field(
        description="Category of the requirements issue"
    )
    severity: Literal["critical", "major", "minor"] = Field(
        description="Severity level of the issue"
    )
    location: str = Field(
        description="Where in requirements document this issue occurs"
    )
    description: str = Field(
        description="Clear description of what's wrong with the requirements"
    )
    suggestion: str = Field(
        description="Specific, actionable suggestion for how to improve"
    )


class RequirementsReviewFeedback(ReviewFeedback):
    """Specialized feedback for requirements review.
    
    Extends the base ReviewFeedback with requirements-specific metrics
    and issue tracking to ensure comprehensive requirements quality review.
    """
    
    # Requirements-specific issues
    requirements_issues: List[RequirementsIssue] = Field(
        default=[],
        description="Specific requirements problems identified"
    )
    
    # Requirements quality dimensions
    missing_elements: List[str] = Field(
        default=[],
        description="What's missing from the requirements document"
    )
    completeness_score: int = Field(
        ge=0, le=10,
        description="How complete the requirements are (0-10 scale)"
    )
    clarity_score: int = Field(
        ge=0, le=10,
        description="How clear and unambiguous the requirements are (0-10 scale)"
    )
    testability_score: int = Field(
        ge=0, le=10,
        description="How testable and measurable the requirements are (0-10 scale)"
    )


class RequirementsNavigator(NavigatorAgent):
    """Navigator specialized for requirements review.
    
    This agent focuses specifically on ensuring requirements documentation
    meets quality standards before development begins. It implements the
    principles learned from PR #23 to prevent vague requirements that lead
    to implementation disasters.
    
    Key Features:
    - Requirements completeness analysis
    - Clarity and specificity checking  
    - Testability verification
    - Consistency validation
    - Progressive leniency across iterations
    """
    
    def __init__(self, base_strictness: float = 1.0):
        """Initialize RequirementsNavigator.
        
        Args:
            base_strictness: Base strictness level for requirements review
        """
        super().__init__(
            specialty="requirements_review",
            base_strictness=base_strictness
        )
        
        # Use specialized parser for requirements feedback
        self.parser = PydanticOutputParser(pydantic_object=RequirementsReviewFeedback)
        
        logger.info("RequirementsNavigator initialized for thorough requirements review")
    
    async def review_requirements(
        self,
        task: Dict[str, Any],
        requirements_output: Dict[str, Any],
        context: Dict[str, Any],
        iteration_number: int = 1
    ) -> RequirementsReviewFeedback:
        """
        Review requirements documentation for quality and completeness.
        
        This is the main entry point for requirements review. It extracts
        the requirements document and performs comprehensive quality analysis
        focusing on preventing implementation disasters.
        
        Args:
            task: The analysis task definition
            requirements_output: Output from Analyst Agent containing requirements
            context: Additional context (issue, repository, etc.)
            iteration_number: Which iteration this is (affects strictness)
            
        Returns:
            Specialized requirements feedback with detailed scoring
        """
        logger.info(f"Navigator reviewing requirements (iteration {iteration_number})")
        
        # Extract requirements document from analyst output
        artifacts = requirements_output.get("artifacts", [])
        requirements_doc = None
        specification = None
        
        # Find requirements artifact
        for artifact in artifacts:
            if artifact.get("type") == "requirements":
                requirements_doc = artifact.get("content", "")
                specification = artifact.get("specification", {})
                break
        
        # Handle case where no requirements document is found
        if not requirements_doc:
            logger.warning("No requirements document found in analyst output")
            return RequirementsReviewFeedback(
                decision=ReviewDecision.REJECTED,
                overall_assessment="No requirements document found in analyst output",
                requirements_issues=[],
                missing_elements=["Requirements document"],
                completeness_score=0,
                clarity_score=0,
                testability_score=0,
                issues=[],
                required_changes=["Generate a proper requirements document"],
                suggestions=[],
                positive_aspects=[],
                quality_score=0,
                correctness_score=0,
                reasoning="Cannot review requirements without a requirements document",
                iteration_number=iteration_number,
                adjusted_strictness=self._calculate_adjusted_strictness(iteration_number, self.base_strictness)
            )
        
        # Perform detailed requirements review
        feedback = await self._perform_detailed_requirements_review(
            requirements_doc,
            specification,
            task,
            context,
            iteration_number
        )
        
        logger.info(
            f"Requirements review complete: {feedback.decision}, "
            f"Completeness: {feedback.completeness_score}/10, "
            f"Clarity: {feedback.clarity_score}/10, "
            f"Testability: {feedback.testability_score}/10"
        )
        
        return feedback
    
    async def _perform_detailed_requirements_review(
        self,
        requirements_doc: str,
        specification: Dict[str, Any],
        task: Dict[str, Any],
        context: Dict[str, Any],
        iteration_number: int
    ) -> RequirementsReviewFeedback:
        """Perform detailed requirements review using LLM analysis.
        
        Args:
            requirements_doc: The requirements document content
            specification: The structured specification data
            task: The analysis task
            context: Additional context
            iteration_number: Current iteration number
            
        Returns:
            Comprehensive requirements feedback
        """
        # Calculate adjusted strictness
        adjusted_strictness = self._calculate_adjusted_strictness(
            iteration_number, 
            self.base_strictness
        )
        
        # Build comprehensive review prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_requirements_review_system_prompt(adjusted_strictness, iteration_number)),
            ("human", self._get_requirements_review_user_prompt())
        ])
        
        # Format prompt with all context
        formatted_prompt = prompt.format_messages(
            iteration_number=iteration_number,
            strictness_description=self._get_strictness_description(adjusted_strictness, iteration_number),
            format_instructions=self.parser.get_format_instructions(),
            task_description=task.get("description", "No task description provided"),
            issue_context=self._format_issue_context(context),
            requirements_doc=requirements_doc,
            specification_data=json.dumps(specification, indent=2) if specification else "No structured specification available"
        )
        
        # Get LLM analysis
        response = await self.llm.ainvoke(formatted_prompt)
        feedback = self.parser.parse(response.content)
        
        # Set metadata
        feedback.iteration_number = iteration_number
        feedback.adjusted_strictness = adjusted_strictness
        
        # Validate and adjust decision based on strictness
        feedback = self._validate_and_adjust_feedback(feedback, adjusted_strictness)
        
        return feedback
    
    def _get_strictness_description(self, adjusted_strictness: float, iteration_number: int) -> str:
        """Get description of current strictness level for prompt.
        
        Args:
            adjusted_strictness: Current adjusted strictness level
            iteration_number: Current iteration number
            
        Returns:
            Description of strictness expectations
        """
        if iteration_number == 1:
            return "strict - thoroughly evaluate all aspects, high standards for approval"
        elif iteration_number == 2:
            return "moderate - focus on critical and major issues, some leniency for minor issues"
        else:
            return "lenient - focus only on critical issues that would cause implementation disasters"
    
    def _get_requirements_review_system_prompt(self, adjusted_strictness: float, iteration_number: int) -> str:
        """Get the system prompt for requirements review.
        
        Args:
            adjusted_strictness: Current strictness level
            iteration_number: Current iteration number
            
        Returns:
            Formatted system prompt for requirements review
        """
        return f"""You are an expert Requirements Reviewer acting as the "Navigator" in pair programming.

Your critical role is to review requirements documentation and prevent disasters like PR #23,
where vague requirements ("remove phrase from readme") led to deletion of entire files
instead of targeted changes.

REVIEW MISSION:
You are the quality gatekeeper ensuring requirements are thorough, clear, and actionable
before any development begins. Your review can prevent costly implementation mistakes.

REVIEW CRITERIA - Evaluate these dimensions:

1. CLARITY (0-10):
   - Are requirements unambiguous and specific?
   - Would a developer understand exactly what to implement?
   - Are technical terms and constraints clearly defined?
   - Is the scope well-bounded?

2. COMPLETENESS (0-10):
   - Are all aspects of the issue addressed?
   - Are edge cases and error scenarios covered?
   - Are dependencies and integrations identified?
   - Are success criteria clearly specified?

3. TESTABILITY (0-10):
   - Can each requirement be verified/tested?
   - Are acceptance criteria specific and measurable?
   - Is it clear when the requirement is "done"?
   - Can success be objectively validated?

4. SPECIFICITY (0-10):
   - Are requirements concrete rather than vague?
   - Are constraints, limits, and boundaries defined?
   - Are data formats and interfaces specified?
   - Is the expected behavior precisely described?

5. CONSISTENCY (0-10):
   - Do requirements contradict each other?
   - Is terminology used consistently?
   - Are priorities and approaches aligned?
   - Do all parts work together coherently?

REVIEW APPROACH (Iteration {iteration_number} - {strictness_description}):

SEVERITY LEVELS for Requirements Issues:
- CRITICAL: Vague/ambiguous requirements that will cause implementation disasters
- MAJOR: Significant gaps or unclear specifications that need fixing
- MINOR: Improvements that enhance quality but aren't blocking

DECISION CRITERIA:
- APPROVED: Requirements are clear, complete, and implementable
- NEEDS_CHANGES: Significant issues that must be addressed
- REJECTED: Requirements are too vague/incomplete to proceed safely

FOCUS AREAS - Prevent PR #23 scenarios:
✓ Verify specific targets are identified (not just "fix the thing")
✓ Ensure preservation requirements are clear (what NOT to change)
✓ Check that validation criteria are measurable
✓ Confirm edge cases and error handling are addressed
✓ Validate that dependencies are identified

Be SPECIFIC in your feedback. Don't say "improve clarity" - say exactly what's unclear and how to fix it.
Provide actionable suggestions that the Analyst can implement.

{{format_instructions}}"""
    
    def _get_requirements_review_user_prompt(self) -> str:
        """Get the user prompt for requirements review.
        
        Returns:
            Formatted user prompt for requirements analysis
        """
        return """REQUIREMENTS REVIEW REQUEST

Task Context:
{task_description}

Issue Context:
{issue_context}

REQUIREMENTS DOCUMENT TO REVIEW:
{requirements_doc}

STRUCTURED SPECIFICATION DATA:
{specification_data}

REVIEW INSTRUCTIONS:
This is iteration {iteration_number}. Please thoroughly review the requirements documentation above.

Focus on preventing implementation disasters by ensuring:
1. Requirements are specific and unambiguous
2. Success criteria are clearly measurable  
3. Edge cases and error scenarios are addressed
4. Dependencies and impacts are identified
5. The scope is well-defined and bounded

Provide detailed feedback with specific, actionable suggestions for improvement.
Remember: Better to be too thorough now than deal with implementation disasters later."""
    
    def _validate_and_adjust_feedback(
        self, 
        feedback: RequirementsReviewFeedback, 
        adjusted_strictness: float
    ) -> RequirementsReviewFeedback:
        """Validate and adjust feedback based on strictness level.
        
        Args:
            feedback: Raw feedback from LLM
            adjusted_strictness: Current strictness level
            
        Returns:
            Validated and adjusted feedback
        """
        # Get quality threshold for this strictness level
        quality_threshold = self._get_quality_threshold(adjusted_strictness)
        
        # Calculate overall quality score from component scores
        overall_quality = (
            feedback.completeness_score + 
            feedback.clarity_score + 
            feedback.testability_score
        ) / 3
        
        # Update quality scores
        feedback.quality_score = int(overall_quality)
        feedback.completeness_score = int(overall_quality)  # Base ReviewFeedback compatibility
        feedback.correctness_score = feedback.testability_score  # Map testability to correctness
        
        # Adjust decision based on strictness and scores
        if adjusted_strictness <= 0.6:  # Lenient mode (iteration 3+)
            # Only reject for critical issues
            critical_issues = [
                issue for issue in feedback.requirements_issues 
                if issue.severity == "critical"
            ]
            if critical_issues and overall_quality < 5.0:
                feedback.decision = ReviewDecision.NEEDS_CHANGES
            else:
                feedback.decision = ReviewDecision.APPROVED
                
        elif overall_quality >= quality_threshold:
            feedback.decision = ReviewDecision.APPROVED
        elif overall_quality >= 4.0:  # Give opportunity for improvement
            feedback.decision = ReviewDecision.NEEDS_CHANGES
        else:
            feedback.decision = ReviewDecision.REJECTED
        
        # Ensure consistent reasoning
        if feedback.decision == ReviewDecision.APPROVED:
            if not feedback.positive_aspects:
                feedback.positive_aspects = [
                    "Requirements meet quality standards for implementation",
                    f"Scoring above threshold: {overall_quality:.1f}/{quality_threshold:.1f}"
                ]
        
        return feedback


def create_requirements_navigator(strictness: float = 1.0) -> RequirementsNavigator:
    """Factory function to create a RequirementsNavigator.
    
    Args:
        strictness: Base strictness level for requirements review
        
    Returns:
        Configured RequirementsNavigator instance
    """
    return RequirementsNavigator(base_strictness=strictness)