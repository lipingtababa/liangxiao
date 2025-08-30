"""Navigator Agent - Quality review agent with progressive leniency.

This agent acts as the "navigator" in pair programming, reviewing work from
tasker agents and providing specific, actionable feedback. It implements
progressive leniency to prevent infinite iteration loops while ensuring quality.
"""

import logging
from datetime import datetime
from typing import List, Optional, Literal, Dict, Any, Union
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ReviewDecision(str, Enum):
    """Possible review decisions."""
    APPROVED = "approved"
    NEEDS_CHANGES = "needs_changes"
    REJECTED = "rejected"


class CodeIssue(BaseModel):
    """Specific issue found during review."""
    severity: Literal["critical", "major", "minor", "suggestion"] = Field(
        description="Severity level of the issue"
    )
    category: Literal["bug", "security", "performance", "style", "logic", "maintainability"] = Field(
        description="Category of the issue"
    )
    location: str = Field(
        description="File and line number if applicable (e.g., 'src/main.py:42')"
    )
    description: str = Field(
        description="Clear description of what's wrong"
    )
    suggestion: str = Field(
        description="Specific, actionable suggestion for how to fix it"
    )


class ReviewFeedback(BaseModel):
    """Complete structured feedback from Navigator Agent."""
    
    # Core decision
    decision: ReviewDecision = Field(
        description="The review decision: approved, needs_changes, or rejected"
    )
    overall_assessment: str = Field(
        description="High-level assessment of the work"
    )
    
    # Detailed feedback
    issues: List[CodeIssue] = Field(
        default=[],
        description="Specific problems found in the work"
    )
    required_changes: List[str] = Field(
        default=[],
        description="Changes that must be made before approval"
    )
    suggestions: List[str] = Field(
        default=[],
        description="Optional improvements that would enhance quality"
    )
    positive_aspects: List[str] = Field(
        default=[],
        description="Things that were done well"
    )
    
    # Quality scoring (0-10 scale)
    quality_score: int = Field(
        ge=0, le=10,
        description="Overall quality score from 0-10"
    )
    completeness_score: int = Field(
        ge=0, le=10,
        description="How complete the work is from 0-10"
    )
    correctness_score: int = Field(
        ge=0, le=10,
        description="How correct the work is from 0-10"
    )
    
    # Reasoning and metadata
    reasoning: str = Field(
        description="Detailed explanation of why this decision was made"
    )
    iteration_number: int = Field(
        description="Which iteration this review is for"
    )
    adjusted_strictness: float = Field(
        description="The strictness level used for this review"
    )
    reviewer: str = Field(
        default="navigator_agent",
        description="The reviewing agent identifier"
    )
    reviewed_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp when review was completed"
    )


class NavigatorAgent:
    """
    Navigator agent that reviews and guides all work with progressive leniency.
    
    The Navigator acts as the quality guardian, preventing disasters like PR #23
    by thoroughly reviewing work and providing specific, actionable feedback.
    
    Key Features:
    - Progressive leniency: Starts strict, becomes more lenient
    - Specialized review modes for different types of work
    - Specific, actionable feedback (not vague suggestions)
    - Quality scoring on multiple dimensions
    - Clear approval/revision/rejection decisions
    """
    
    def __init__(
        self,
        specialty: Literal["code_review", "requirements_review", "test_review"] = "code_review",
        base_strictness: float = 1.0,
        model: str = "gpt-4-turbo-preview"
    ):
        """
        Initialize Navigator Agent.
        
        Args:
            specialty: Type of review to specialize in
            base_strictness: Base strictness level (1.0 = normal, 0.5 = lenient, 1.5 = strict)
            model: LLM model to use for reviews
        """
        self.specialty = specialty
        self.base_strictness = base_strictness
        self.model = model
        
        # Initialize LLM with consistent temperature for reliable reviews
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.3,  # Low temperature for consistent reviews
            max_tokens=2000   # Enough for detailed feedback
        )
        
        # Initialize parser for structured output
        self.parser = PydanticOutputParser(pydantic_object=ReviewFeedback)
        
        logger.info(f"Navigator Agent initialized: specialty={specialty}, strictness={base_strictness}")
    
    async def review(
        self,
        task: Dict[str, Any],
        work_output: Dict[str, Any],
        context: Dict[str, Any],
        iteration_number: int = 1
    ) -> ReviewFeedback:
        """
        Review work and provide structured feedback with progressive leniency.
        
        Args:
            task: The task that was executed
            work_output: The output from the tasker agent
            context: Additional context (repo, issue, etc.)
            iteration_number: Which iteration this is (affects leniency)
            
        Returns:
            Structured feedback with decision and specifics
        """
        logger.info(
            f"Reviewing {self.specialty} work for task {task.get('id', 'unknown')}, "
            f"iteration {iteration_number}"
        )
        
        # Calculate adjusted strictness based on iteration
        adjusted_strictness = self._calculate_adjusted_strictness(
            iteration_number, 
            self.base_strictness
        )
        
        logger.debug(
            f"Using adjusted strictness: {adjusted_strictness} "
            f"(base: {self.base_strictness}, iteration: {iteration_number})"
        )
        
        try:
            # Route to appropriate review method
            if self.specialty == "code_review":
                feedback = await self._review_code(
                    task, work_output, context, adjusted_strictness, iteration_number
                )
            elif self.specialty == "requirements_review":
                feedback = await self._review_requirements(
                    task, work_output, context, adjusted_strictness, iteration_number
                )
            else:  # test_review
                feedback = await self._review_tests(
                    task, work_output, context, adjusted_strictness, iteration_number
                )
            
            # Log the review decision
            logger.info(
                f"Review completed: {feedback.decision}, "
                f"quality={feedback.quality_score}/10, "
                f"issues={len(feedback.issues)}, "
                f"strictness={adjusted_strictness}"
            )
            
            return feedback
            
        except Exception as e:
            logger.error(f"Review failed: {e}")
            # Return a safe fallback response
            return self._create_error_feedback(e, iteration_number, adjusted_strictness)
    
    def _calculate_adjusted_strictness(
        self,
        iteration_number: int,
        base_strictness: float
    ) -> float:
        """
        Calculate adjusted strictness with progressive leniency.
        
        Progressive leniency algorithm:
        - Iteration 1: Full strictness (90% quality threshold)
        - Iteration 2: 80% strictness (75% quality threshold) 
        - Iteration 3+: 60% strictness (60% quality threshold)
        
        This prevents infinite iteration loops while maintaining quality.
        
        Args:
            iteration_number: Current iteration number
            base_strictness: Base strictness level
            
        Returns:
            Adjusted strictness level
        """
        if iteration_number == 1:
            # First iteration: be thorough and strict
            multiplier = 1.0
        elif iteration_number == 2:
            # Second iteration: moderately strict
            multiplier = 0.8
        else:
            # Third+ iteration: lenient (focus only on critical issues)
            multiplier = 0.6
        
        adjusted = base_strictness * multiplier
        
        logger.debug(
            f"Strictness adjustment: iteration {iteration_number}, "
            f"multiplier {multiplier}, adjusted {adjusted}"
        )
        
        return adjusted
    
    def _get_quality_threshold(self, adjusted_strictness: float) -> float:
        """Get the quality score threshold for approval based on strictness."""
        # Map strictness to quality thresholds
        # High strictness requires higher quality scores
        if adjusted_strictness >= 1.0:
            return 9.0  # Very strict - 90% quality
        elif adjusted_strictness >= 0.8:
            return 7.5  # Moderately strict - 75% quality
        else:
            return 6.0  # Lenient - 60% quality
    
    async def _review_code(
        self,
        task: Dict[str, Any],
        work_output: Dict[str, Any],
        context: Dict[str, Any],
        strictness: float,
        iteration_number: int
    ) -> ReviewFeedback:
        """Review code implementation with focus on correctness and quality."""
        
        # Extract code content from work output
        code_artifacts = work_output.get("artifacts", [])
        code_content = self._extract_code_content(code_artifacts, work_output)
        
        # Build the review prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_code_review_system_prompt()),
            ("human", self._get_code_review_user_prompt())
        ])
        
        # Format the prompt with all necessary data
        formatted = prompt.format_messages(
            strictness=strictness,
            quality_threshold=self._get_quality_threshold(strictness),
            format_instructions=self.parser.get_format_instructions(),
            task_description=task.get("description", "No description provided"),
            task_type=task.get("type", "unknown"),
            acceptance_criteria=self._format_list(task.get("acceptance_criteria", [])),
            code_content=code_content,
            iteration_number=iteration_number,
            issue_context=self._format_issue_context(context),
            previous_feedback=self._format_previous_feedback(context),
            max_iterations=context.get("max_iterations", 3)
        )
        
        # Get LLM response and parse
        response = await self.llm.ainvoke(formatted)
        feedback = self.parser.parse(response.content)
        
        # Set metadata
        feedback.iteration_number = iteration_number
        feedback.adjusted_strictness = strictness
        
        return feedback
    
    async def _review_requirements(
        self,
        task: Dict[str, Any],
        work_output: Dict[str, Any],
        context: Dict[str, Any],
        strictness: float,
        iteration_number: int
    ) -> ReviewFeedback:
        """Review requirements analysis for completeness and clarity."""
        
        # Extract requirements content
        requirements_content = self._extract_requirements_content(work_output)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_requirements_review_system_prompt()),
            ("human", self._get_requirements_review_user_prompt())
        ])
        
        formatted = prompt.format_messages(
            strictness=strictness,
            quality_threshold=self._get_quality_threshold(strictness),
            format_instructions=self.parser.get_format_instructions(),
            task_description=task.get("description", "No description provided"),
            requirements_content=requirements_content,
            iteration_number=iteration_number,
            issue_context=self._format_issue_context(context)
        )
        
        response = await self.llm.ainvoke(formatted)
        feedback = self.parser.parse(response.content)
        
        feedback.iteration_number = iteration_number
        feedback.adjusted_strictness = strictness
        
        return feedback
    
    async def _review_tests(
        self,
        task: Dict[str, Any],
        work_output: Dict[str, Any],
        context: Dict[str, Any],
        strictness: float,
        iteration_number: int
    ) -> ReviewFeedback:
        """Review test cases and test code for coverage and validity."""
        
        # Extract test content
        test_content = self._extract_test_content(work_output)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_test_review_system_prompt()),
            ("human", self._get_test_review_user_prompt())
        ])
        
        formatted = prompt.format_messages(
            strictness=strictness,
            quality_threshold=self._get_quality_threshold(strictness),
            format_instructions=self.parser.get_format_instructions(),
            task_description=task.get("description", "No description provided"),
            test_content=test_content,
            iteration_number=iteration_number,
            issue_context=self._format_issue_context(context)
        )
        
        response = await self.llm.ainvoke(formatted)
        feedback = self.parser.parse(response.content)
        
        feedback.iteration_number = iteration_number
        feedback.adjusted_strictness = strictness
        
        return feedback
    
    def _validate_feedback(self, feedback: ReviewFeedback) -> None:
        """Validate parsed feedback for consistency and completeness."""
        
        # Check required fields exist and are valid
        if not hasattr(feedback, 'decision') or not feedback.decision:
            raise ValueError("Feedback missing required decision field")
        
        if not hasattr(feedback, 'overall_assessment') or not feedback.overall_assessment:
            raise ValueError("Feedback missing overall assessment")
        
        if not hasattr(feedback, 'reasoning') or not feedback.reasoning:
            raise ValueError("Feedback missing reasoning")
        
        # Validate score ranges
        for score_field in ['quality_score', 'completeness_score', 'correctness_score']:
            if hasattr(feedback, score_field):
                score = getattr(feedback, score_field)
                if not isinstance(score, int) or score < 0 or score > 10:
                    raise ValueError(f"Invalid {score_field}: must be integer 0-10")
        
        # Validate decision logic
        if feedback.decision == ReviewDecision.APPROVED:
            # Approved work shouldn't have critical issues
            if any(issue.severity == "critical" for issue in feedback.issues):
                logger.warning("Approved feedback has critical issues - this may be inconsistent")
        
        elif feedback.decision == ReviewDecision.REJECTED:
            # Rejected work should have low quality scores
            if feedback.quality_score > 5:
                logger.warning(f"Rejected feedback has high quality score ({feedback.quality_score}) - may be inconsistent")
        
        # Validate issues structure
        if hasattr(feedback, 'issues') and feedback.issues:
            for i, issue in enumerate(feedback.issues):
                if not hasattr(issue, 'severity') or not issue.severity:
                    raise ValueError(f"Issue {i} missing severity")
                if not hasattr(issue, 'description') or not issue.description:
                    raise ValueError(f"Issue {i} missing description")
                if not hasattr(issue, 'suggestion') or not issue.suggestion:
                    raise ValueError(f"Issue {i} missing suggestion")
    
    def _get_code_review_system_prompt(self) -> str:
        """Get the system prompt for code review."""
        return """You are an expert code reviewer acting as the "Navigator" in pair programming.

Your role is to review code and provide specific, actionable feedback to prevent disasters like PR #23 (where a developer deleted an entire README when asked to remove one phrase).

CRITICAL RESPONSIBILITIES:
1. Catch bugs, security issues, and logic errors
2. Ensure the solution actually addresses the task requirements
3. Verify files are read before being modified
4. Check for proper error handling and edge cases
5. Ensure code follows best practices and conventions

REVIEW CRITERIA (adjust based on strictness level {strictness}):
- Correctness: Does it solve the problem correctly?
- Security: Are there vulnerabilities or unsafe operations?
- Performance: Any obvious inefficiencies?
- Maintainability: Is the code clean and readable?
- Best practices: Follows language/project conventions?
- Completeness: Addresses all requirements?

SEVERITY LEVELS:
- critical: Will break production, security vulnerability, or completely wrong approach
- major: Significant problem that should be fixed
- minor: Should be fixed but not blocking
- suggestion: Nice to have improvement

QUALITY THRESHOLD: {quality_threshold}/10
- Above threshold: APPROVED
- Below threshold: NEEDS_CHANGES (unless iteration 3+)

PROGRESSIVE LENIENCY:
- Iteration 1: Be thorough, catch everything
- Iteration 2: Focus on critical and major issues  
- Iteration 3+: Only critical issues are blocking

FEEDBACK REQUIREMENTS:
- Be SPECIFIC about locations (file:line)
- Provide ACTIONABLE suggestions, not vague advice
- Don't say "improve error handling", say "Add try/catch around database call on line 45"
- Include code examples when helpful
- Acknowledge what was done well

{format_instructions}"""
    
    def _get_code_review_user_prompt(self) -> str:
        """Get the user prompt for code review."""
        return """TASK TO REVIEW:
Description: {task_description}
Type: {task_type}
Acceptance Criteria:
{acceptance_criteria}

CODE TO REVIEW:
{code_content}

CONTEXT:
- This is iteration {iteration_number} of {max_iterations}
- Issue: {issue_context}
{previous_feedback}

Please review this code and provide structured feedback following the severity guidelines and quality threshold of {quality_threshold}/10."""
    
    def _get_requirements_review_system_prompt(self) -> str:
        """Get the system prompt for requirements review."""
        return """You are reviewing requirements documentation and analysis.

Check for:
1. Completeness - All aspects of the issue covered?
2. Clarity - Unambiguous and specific requirements?
3. Feasibility - Can this actually be implemented?
4. Testability - Can we verify when it's complete?
5. Consistency - No contradictions or conflicts?

Quality threshold: {quality_threshold}/10
Strictness level: {strictness}

Be specific about what's missing or unclear. Provide actionable suggestions for improvement.

{format_instructions}"""
    
    def _get_requirements_review_user_prompt(self) -> str:
        """Get the user prompt for requirements review."""
        return """TASK: {task_description}

REQUIREMENTS DOCUMENT TO REVIEW:
{requirements_content}

CONTEXT:
- Iteration {iteration_number}
- Issue: {issue_context}

Review the requirements for completeness, clarity, and feasibility."""
    
    def _get_test_review_system_prompt(self) -> str:
        """Get the system prompt for test review."""
        return """You are reviewing test cases and test code.

Check for:
1. Coverage - All important scenarios tested?
2. Validity - Tests actually test the right things?
3. Independence - Tests don't depend on each other?
4. Clarity - Test names describe what they test?
5. Assertions - Proper assertions and error handling?
6. Edge cases - Boundary conditions covered?

Quality threshold: {quality_threshold}/10
Strictness level: {strictness}

Be specific about missing test cases or improvements needed.

{format_instructions}"""
    
    def _get_test_review_user_prompt(self) -> str:
        """Get the user prompt for test review."""
        return """TASK: {task_description}

TEST CODE TO REVIEW:
{test_content}

CONTEXT:
- Iteration {iteration_number}
- Issue: {issue_context}

Review the tests for coverage, validity, and completeness."""
    
    def _extract_code_content(self, artifacts: List[Dict], work_output: Dict) -> str:
        """Extract code content from work output with robust error handling."""
        code_parts = []
        
        try:
            # Extract from artifacts
            if artifacts and isinstance(artifacts, list):
                for artifact in artifacts:
                    if not isinstance(artifact, dict):
                        continue
                        
                    if artifact.get("type") == "code":
                        path = artifact.get("path", "unknown")
                        content = artifact.get("content", "")
                        
                        if content and isinstance(content, str):
                            # Sanitize content to prevent issues
                            content_preview = content[:5000]  # Limit size
                            if len(content) > 5000:
                                content_preview += "\n... (content truncated)"
                            code_parts.append(f"// File: {path}\n{content_preview}")
            
            # Fallback to direct code field
            if not code_parts and "code" in work_output:
                code_value = work_output["code"]
                if isinstance(code_value, str) and code_value.strip():
                    code_parts.append(code_value)
            
            # Fallback to content field
            if not code_parts and "content" in work_output:
                content_obj = work_output["content"]
                if isinstance(content_obj, dict) and "code_snippet" in content_obj:
                    code_snippet = content_obj["code_snippet"]
                    if isinstance(code_snippet, str) and code_snippet.strip():
                        code_parts.append(code_snippet)
            
            result = "\n\n".join(code_parts) if code_parts else "No code content found"
            
            # Ensure result is not too large for LLM
            if len(result) > 10000:
                result = result[:10000] + "\n... (content truncated for review)"
                
            return result
            
        except Exception as e:
            logger.error(f"Error extracting code content: {e}")
            return "Error extracting code content - please check work output format"
    
    def _extract_requirements_content(self, work_output: Dict) -> str:
        """Extract requirements content from work output."""
        # Try various fields where requirements might be stored
        if "requirements" in work_output:
            return str(work_output["requirements"])
        
        if "analysis" in work_output:
            return str(work_output["analysis"])
        
        artifacts = work_output.get("artifacts", [])
        for artifact in artifacts:
            if artifact.get("type") in ["requirements", "analysis", "investigation_report"]:
                return str(artifact.get("content", ""))
        
        return "No requirements content found"
    
    def _extract_test_content(self, work_output: Dict) -> str:
        """Extract test content from work output."""
        test_parts = []
        
        # Extract from artifacts
        artifacts = work_output.get("artifacts", [])
        for artifact in artifacts:
            if artifact.get("type") == "tests":
                content = artifact.get("content", "")
                if content:
                    test_parts.append(str(content))
        
        # Fallback to test_results
        if not test_parts and "test_results" in work_output:
            test_parts.append(str(work_output["test_results"]))
        
        return "\\n\\n".join(test_parts) if test_parts else "No test content found"
    
    def _format_list(self, items: List) -> str:
        """Format a list of items as a bulleted string with error handling."""
        try:
            if not items or not isinstance(items, list):
                return "None specified"
            
            formatted_items = []
            for item in items:
                if item is not None:  # Allow empty strings but not None
                    item_str = str(item).strip()
                    if item_str:  # Only add non-empty items
                        formatted_items.append(f"- {item_str}")
            
            return "\n".join(formatted_items) if formatted_items else "None specified"
            
        except Exception as e:
            logger.error(f"Error formatting list: {e}")
            return "Error formatting list items"
    
    def _format_issue_context(self, context: Dict) -> str:
        """Format issue context for the prompt with robust error handling."""
        try:
            if not isinstance(context, dict):
                return "No issue context available"
                
            issue = context.get("issue", {})
            if not isinstance(issue, dict) or not issue:
                return "No issue context available"
            
            number = issue.get('number', 'Unknown')
            title = issue.get('title', 'No title')
            
            # Sanitize title to prevent prompt injection
            if isinstance(title, str):
                title = title.replace('\n', ' ').replace('\r', ' ')[:200]  # Limit length
            
            return f"Issue #{number}: {title}"
            
        except Exception as e:
            logger.error(f"Error formatting issue context: {e}")
            return "Error formatting issue context"
    
    def _format_previous_feedback(self, context: Dict) -> str:
        """Format previous feedback for context."""
        feedback_list = context.get("previous_feedback", [])
        if not feedback_list:
            return ""
        
        latest = feedback_list[-1] if feedback_list else None
        if not latest:
            return ""
        
        return f"\\nPrevious feedback: {latest.get('feedback', 'No previous feedback')}"
    
    def _create_error_feedback(
        self, 
        error: Exception, 
        iteration_number: int, 
        adjusted_strictness: float
    ) -> ReviewFeedback:
        """Create a safe fallback feedback when review fails."""
        return ReviewFeedback(
            decision=ReviewDecision.NEEDS_CHANGES,
            overall_assessment=f"Review failed due to error: {str(error)}",
            issues=[
                CodeIssue(
                    severity="critical",
                    category="logic",
                    location="unknown",
                    description=f"Navigator review failed: {str(error)}",
                    suggestion="Fix the underlying issue and try again"
                )
            ],
            required_changes=["Resolve the error that prevented review"],
            quality_score=0,
            completeness_score=0,
            correctness_score=0,
            reasoning=f"Unable to complete review due to error: {str(error)}",
            iteration_number=iteration_number,
            adjusted_strictness=adjusted_strictness
        )
    
    def provide_iteration_guidance(
        self,
        previous_feedback: ReviewFeedback,
        iteration_number: int
    ) -> str:
        """
        Provide guidance for the next iteration based on previous feedback.
        
        This helps the tasker agent understand what to focus on and implements
        the progressive leniency by focusing on different severity levels.
        
        Args:
            previous_feedback: The feedback from the previous iteration
            iteration_number: Which iteration we're preparing for
            
        Returns:
            Guidance string for the tasker agent
        """
        if iteration_number >= 3:
            # Third+ iteration: Focus only on critical issues
            critical_issues = [
                issue for issue in previous_feedback.issues
                if issue.severity == "critical"
            ]
            
            if critical_issues:
                critical_descriptions = [issue.description for issue in critical_issues]
                return (
                    f"FINAL ITERATION: Focus ONLY on these {len(critical_issues)} critical issues:\\n" +
                    "\\n".join(f"- {desc}" for desc in critical_descriptions) +
                    "\\n\\nMinor issues will be ignored at this stage."
                )
            else:
                return (
                    "FINAL ITERATION: No critical issues remain. "
                    "Focus on the required changes listed. Minor issues can be ignored."
                )
        
        elif iteration_number == 2:
            # Second iteration: Focus on critical and major issues
            important_issues = [
                issue for issue in previous_feedback.issues
                if issue.severity in ["critical", "major"]
            ]
            
            if important_issues:
                return (
                    f"ITERATION {iteration_number}: Address these {len(important_issues)} important issues:\\n" +
                    "\\n".join(f"- {issue.description}" for issue in important_issues) +
                    "\\n\\nTry to address minor issues if time permits."
                )
            else:
                return f"ITERATION {iteration_number}: Address the required changes. Try to fix minor issues too."
        
        else:
            # First iteration: Comprehensive feedback
            total_issues = len(previous_feedback.issues)
            if total_issues > 0:
                return (
                    f"ITERATION {iteration_number}: Address all {total_issues} issues found:\\n" +
                    "\\n".join(f"- {issue.description}" for issue in previous_feedback.issues) +
                    "\\n\\nPay special attention to critical and major issues."
                )
            else:
                return f"ITERATION {iteration_number}: Address the feedback provided and make the required changes."


def create_navigator_agent(
    specialty: Literal["code_review", "requirements_review", "test_review"] = "code_review",
    strictness: float = 1.0
) -> NavigatorAgent:
    """
    Factory function to create a Navigator Agent with proper configuration.
    
    Args:
        specialty: The type of review to specialize in
        strictness: Base strictness level (1.0 = normal)
        
    Returns:
        Configured Navigator Agent instance
    """
    return NavigatorAgent(
        specialty=specialty,
        base_strictness=strictness
    )