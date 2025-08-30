# Story 3.1: Navigator Agent Core ✅ COMPLETED

## Story Details
- **ID**: 3.1
- **Title**: Implement Navigator Quality Review Agent
- **Milestone**: Milestone 3 - Navigator Agent & Quality System
- **Points**: 8
- **Priority**: P0 (Critical Path)
- **Dependencies**: Story 2.1 (PM Agent for task structure)
- **Status**: ✅ COMPLETED - Implementation available at `services/orchestrator/agents/navigator/`

## Description

### Overview
Implement the Navigator Agent - the quality guardian that reviews all work produced by tasker agents (Developer, Analyst, Tester). The Navigator provides specific, actionable feedback and decides whether work meets quality standards. This agent is critical for preventing disasters like PR #23.

### Why This Is Important
- Navigator is the quality gatekeeper preventing bad code
- Provides specific, actionable feedback for improvement
- Enables the iteration cycle that produces quality
- Catches errors before they reach production
- Teaches tasker agents to improve over time

### Context
Named after the "navigator" in pair programming who reviews while the driver codes. Our Navigator Agent reviews work from all tasker agents, providing expert guidance specific to the type of work (code review, requirements review, test review).

## Acceptance Criteria

### Required
- [ ] Navigator Agent class with specialized review modes
- [ ] Can review code and identify specific issues
- [ ] Can review requirements for completeness and clarity
- [ ] Can review tests for coverage and validity
- [ ] Provides structured feedback with specific issues and suggestions
- [ ] Makes clear approval/needs-changes/rejection decisions
- [ ] Assigns quality scores (0-10) to work
- [ ] Becomes progressively more lenient with iterations
- [ ] Logs reasoning behind all decisions
- [ ] Returns structured ReviewFeedback objects

## Technical Details

### Navigator Agent Architecture
```python
# agents/navigator/agent.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ReviewDecision(str, Enum):
    APPROVED = "approved"
    NEEDS_CHANGES = "needs_changes"
    REJECTED = "rejected"

class CodeIssue(BaseModel):
    """Specific issue found in code."""
    severity: Literal["critical", "major", "minor", "suggestion"]
    category: Literal["bug", "security", "performance", "style", "logic", "maintainability"]
    location: str = Field(description="File and line number if applicable")
    description: str = Field(description="What's wrong")
    suggestion: str = Field(description="How to fix it")

class ReviewFeedback(BaseModel):
    """Complete feedback from Navigator."""
    decision: ReviewDecision
    overall_assessment: str = Field(description="High-level assessment")
    
    # Issues and suggestions
    issues: List[CodeIssue] = Field(description="Specific problems found")
    required_changes: List[str] = Field(description="Must fix before approval")
    suggestions: List[str] = Field(description="Recommended improvements")
    positive_aspects: List[str] = Field(description="What was done well")
    
    # Scoring
    quality_score: int = Field(ge=0, le=10, description="Overall quality 0-10")
    completeness_score: int = Field(ge=0, le=10, description="How complete 0-10")
    correctness_score: int = Field(ge=0, le=10, description="How correct 0-10")
    
    # Reasoning
    reasoning: str = Field(description="Why this decision was made")

class NavigatorAgent:
    """
    Navigator agent that reviews and guides all work.
    
    Specializes in different types of review based on context.
    """
    
    def __init__(
        self,
        specialty: Literal["code_review", "requirements_review", "test_review"] = "code_review",
        strictness: float = 1.0  # 1.0 = normal, 0.5 = lenient, 1.5 = strict
    ):
        self.specialty = specialty
        self.strictness = strictness
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3  # Consistent reviews
        )
        self.parser = PydanticOutputParser(pydantic_object=ReviewFeedback)
    
    async def review(
        self,
        task: Dict[str, Any],
        work_output: Dict[str, Any],
        context: Dict[str, Any],
        iteration_number: int = 1
    ) -> ReviewFeedback:
        """
        Review work and provide feedback.
        
        Args:
            task: The task that was executed
            work_output: The output from the tasker agent
            context: Additional context (repo, issue, etc.)
            iteration_number: Which iteration this is (affects leniency)
            
        Returns:
            Structured feedback with decision and specifics
        """
        
        # Adjust strictness based on iteration
        adjusted_strictness = self._calculate_adjusted_strictness(
            iteration_number,
            self.strictness
        )
        
        if self.specialty == "code_review":
            return await self._review_code(
                task, work_output, context, adjusted_strictness
            )
        elif self.specialty == "requirements_review":
            return await self._review_requirements(
                task, work_output, context, adjusted_strictness
            )
        else:  # test_review
            return await self._review_tests(
                task, work_output, context, adjusted_strictness
            )
    
    def _calculate_adjusted_strictness(
        self,
        iteration_number: int,
        base_strictness: float
    ) -> float:
        """
        Become more lenient with iterations.
        
        Iteration 1: Full strictness
        Iteration 2: 80% strictness
        Iteration 3+: 60% strictness
        """
        if iteration_number == 1:
            return base_strictness
        elif iteration_number == 2:
            return base_strictness * 0.8
        else:
            return base_strictness * 0.6
    
    async def _review_code(
        self,
        task: Dict[str, Any],
        work_output: Dict[str, Any],
        context: Dict[str, Any],
        strictness: float
    ) -> ReviewFeedback:
        """Review code implementation."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert code reviewer (Navigator in pair programming).
            
            Your role is to review code and provide specific, actionable feedback.
            You should catch bugs, security issues, and quality problems.
            
            Strictness level: {strictness} (0.5=lenient, 1.0=normal, 1.5=strict)
            
            Review criteria:
            1. Correctness - Does it solve the problem?
            2. Security - Any vulnerabilities?
            3. Performance - Any obvious inefficiencies?
            4. Maintainability - Is it clean and readable?
            5. Best practices - Follows language conventions?
            
            For issues, categorize by severity:
            - critical: Will break production or security vulnerability
            - major: Significant problem that needs fixing
            - minor: Should be fixed but not blocking
            - suggestion: Nice to have improvement
            
            Be specific! Don't say "improve error handling", say "Add try/catch around API call on line 42"
            
            {format_instructions}
            """),
            ("human", """Task: {task_description}
            Requirements: {requirements}
            
            Code to review:
            ```
            {code}
            ```
            
            Context:
            - This is iteration {iteration} of the task
            - Original issue: {issue_context}
            
            Provide your review:""")
        ])
        
        # Extract code from work_output
        code_artifacts = work_output.get("artifacts", [])
        code_content = "\n\n".join([
            f"// File: {a['path']}\n{a['content']}"
            for a in code_artifacts if a.get("type") == "code"
        ])
        
        formatted = prompt.format_messages(
            strictness=strictness,
            format_instructions=self.parser.get_format_instructions(),
            task_description=task.get("description", ""),
            requirements=task.get("acceptance_criteria", []),
            code=code_content or work_output.get("code", "No code provided"),
            iteration=context.get("iteration_number", 1),
            issue_context=f"Issue #{context.get('issue', {}).get('number', 'Unknown')}"
        )
        
        response = await self.llm.ainvoke(formatted)
        feedback = self.parser.parse(response.content)
        
        # Log decision
        logger.info(
            f"Navigator review: {feedback.decision}, "
            f"Quality: {feedback.quality_score}/10, "
            f"Issues: {len(feedback.issues)}"
        )
        
        return feedback
    
    async def _review_requirements(
        self,
        task: Dict[str, Any],
        work_output: Dict[str, Any],
        context: Dict[str, Any],
        strictness: float
    ) -> ReviewFeedback:
        """Review requirements analysis."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are reviewing requirements documentation.
            
            Check for:
            1. Completeness - All aspects covered?
            2. Clarity - Unambiguous and specific?
            3. Feasibility - Can this be implemented?
            4. Testability - Can we verify completion?
            5. Consistency - No contradictions?
            
            Strictness: {strictness}
            
            {format_instructions}
            """),
            ("human", """Task: {task}
            
            Requirements document:
            {requirements}
            
            Review and provide feedback:""")
        ])
        
        # Review requirements...
        # Similar structure to code review
        pass
    
    async def _review_tests(
        self,
        task: Dict[str, Any],
        work_output: Dict[str, Any],
        context: Dict[str, Any],
        strictness: float
    ) -> ReviewFeedback:
        """Review test cases and test code."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are reviewing test cases and test code.
            
            Check for:
            1. Coverage - All scenarios tested?
            2. Validity - Tests actually test the right things?
            3. Independence - Tests don't depend on each other?
            4. Clarity - Test names describe what they test?
            5. Assertions - Proper assertions used?
            
            Strictness: {strictness}
            
            {format_instructions}
            """),
            ("human", """Task: {task}
            
            Test code:
            {tests}
            
            Review and provide feedback:""")
        ])
        
        # Review tests...
        # Similar structure to code review
        pass
    
    def provide_iteration_guidance(
        self,
        previous_feedback: ReviewFeedback,
        iteration_number: int
    ) -> str:
        """
        Provide guidance for the next iteration.
        
        This helps the tasker agent understand what to focus on.
        """
        if iteration_number >= 3:
            # On third iteration, focus only on critical issues
            critical_issues = [
                issue for issue in previous_feedback.issues
                if issue.severity == "critical"
            ]
            
            if critical_issues:
                return f"Focus ONLY on fixing these critical issues: {critical_issues}"
            else:
                return "Focus on the required changes listed. Minor issues can be ignored."
        else:
            # Earlier iterations, comprehensive fixes
            return "Address all issues marked as critical and major. Try to fix minor issues too."
```

### Review Examples and Templates
```python
# agents/navigator/review_templates.py

CODE_REVIEW_EXAMPLES = [
    {
        "issue": "Missing error handling",
        "specific_feedback": "Add try/catch block around database call on line 45-52. Handle connection errors and return appropriate error response.",
        "not_helpful": "Improve error handling"  # Too vague!
    },
    {
        "issue": "SQL injection vulnerability",
        "specific_feedback": "Line 23: Use parameterized queries instead of string concatenation. Replace f'SELECT * FROM users WHERE id = {user_id}' with prepared statement.",
        "not_helpful": "Security issue found"  # Not actionable!
    },
    {
        "issue": "Performance problem",
        "specific_feedback": "Line 67-89: This nested loop is O(n²). Use a Set for lookups instead, reducing to O(n). See example in utils/performance.py",
        "not_helpful": "Code is slow"  # Doesn't help fix it!
    }
]

PROGRESSIVE_LENIENCY_RULES = {
    1: {  # First iteration - be thorough
        "critical": "must_fix",
        "major": "must_fix",  
        "minor": "should_fix",
        "suggestion": "mention"
    },
    2: {  # Second iteration - focus on important
        "critical": "must_fix",
        "major": "should_fix",
        "minor": "mention",
        "suggestion": "ignore"
    },
    3: {  # Third iteration - only blockers
        "critical": "must_fix",
        "major": "mention",
        "minor": "ignore",
        "suggestion": "ignore"
    }
}
```

### Integration Example
```python
# Example of Navigator in action preventing PR #23 disaster

# Original issue: "Remove '解释文化细节' from README"

# Developer's first attempt:
work_output = {
    "artifacts": [{
        "type": "code",
        "path": "README.md",
        "content": ""  # Developer deleted everything!
    }]
}

# Navigator review:
feedback = await navigator.review(task, work_output, context, iteration=1)

# Navigator catches the disaster:
feedback.decision = ReviewDecision.NEEDS_CHANGES
feedback.issues = [
    CodeIssue(
        severity="critical",
        category="logic",
        location="README.md",
        description="Entire file content deleted instead of removing specific phrase",
        suggestion="Read the original file and remove only '解释文化细节', preserving all other content"
    )
]
feedback.required_changes = [
    "Restore all original README content",
    "Remove ONLY the phrase '解释文化细节'",
    "Preserve all other text, formatting, and structure"
]
feedback.quality_score = 0  # Complete failure!

# Developer gets specific feedback and fixes in iteration 2 ✅
```

## Testing Requirements

### Unit Tests
```python
# tests/test_navigator.py
import pytest
from agents.navigator.agent import NavigatorAgent, ReviewDecision

@pytest.mark.asyncio
async def test_navigator_catches_bad_code():
    """Test that Navigator catches obvious errors."""
    navigator = NavigatorAgent(specialty="code_review")
    
    bad_code = {
        "code": "def divide(a, b): return a / b"  # No zero check!
    }
    
    feedback = await navigator.review(
        task={"description": "Create safe division function"},
        work_output=bad_code,
        context={},
        iteration_number=1
    )
    
    assert feedback.decision == ReviewDecision.NEEDS_CHANGES
    assert any("zero" in issue.description.lower() 
              for issue in feedback.issues)

@pytest.mark.asyncio
async def test_progressive_leniency():
    """Test that Navigator becomes more lenient."""
    navigator = NavigatorAgent(strictness=1.0)
    
    # First iteration - strict
    feedback1 = await navigator.review(
        task={}, work_output={}, context={}, iteration_number=1
    )
    
    # Third iteration - lenient
    feedback3 = await navigator.review(
        task={}, work_output={}, context={}, iteration_number=3
    )
    
    # Should be more lenient in iteration 3
    assert navigator._calculate_adjusted_strictness(3, 1.0) < 1.0
```

## Dependencies & Risks

### Prerequisites
- LangChain configured
- Understanding of code review best practices
- Clear task definitions from PM Agent

### Risks
- **Over-critical reviews**: Might never approve
- **Under-specific feedback**: Tasker can't improve
- **Inconsistent standards**: Different decisions for similar code
- **API costs**: Multiple review calls expensive

### Mitigations
- Progressive leniency algorithm
- Specific feedback templates
- Consistent review criteria
- Cache review patterns

## Definition of Done

1. ✅ Navigator Agent class implemented
2. ✅ All review specialties working (code, requirements, tests)
3. ✅ Provides specific, actionable feedback
4. ✅ Progressive leniency implemented
5. ✅ Clear decision making (approve/changes/reject)
6. ✅ Quality scoring system works
7. ✅ Integration with Task Pair system
8. ✅ Unit tests passing
9. ✅ Catches obvious errors like PR #23

## Implementation Notes for AI Agents

### DO
- Be specific about locations and fixes
- Provide actionable suggestions
- Acknowledge what was done well
- Focus on critical issues in later iterations
- Include code examples when helpful

### DON'T
- Don't be vague ("improve this")
- Don't reject without explanation
- Don't be overly pedantic
- Don't ignore critical issues
- Don't approve broken code

### Common Pitfalls to Avoid
1. Vague feedback that doesn't help improvement
2. Being too strict on iteration 3
3. Missing critical security issues
4. Focusing on style over substance
5. Not reading the actual requirements

## Success Example

Navigator preventing disasters:
```python
# Issue: "Fix button on mobile"

# Iteration 1: Developer deletes entire button component
# Navigator: "CRITICAL: Don't delete the button! Add touch event handling"

# Iteration 2: Developer adds touch handling but breaks desktop
# Navigator: "MAJOR: Desktop clicks now broken. Use both click AND touch"

# Iteration 3: Developer fixes both
# Navigator: "APPROVED: Works on all devices. Good job!" ✅
```

## Next Story
Once this story is complete, proceed to [Story 3.2: Feedback System](story-3.2-feedback-system.md)