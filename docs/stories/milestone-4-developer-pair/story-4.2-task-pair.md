# Story 4.2: Task Pair Execution System ✅ COMPLETED

## Story Details
- **ID**: 4.2
- **Title**: Implement Developer-Navigator Pair Pattern
- **Milestone**: Milestone 4 - Developer Agent & First Task Pair
- **Points**: 13
- **Priority**: P0 (Critical Path)
- **Dependencies**: Story 4.1 (Developer Agent), Story 3.1 (Navigator Agent)
- **Status**: ✅ COMPLETED - Implementation available at `services/orchestrator/agents/pairs/`

## Description

### Overview
Implement the revolutionary Task Pair execution system where a Developer (Tasker) works with a Navigator (Quality Partner) to produce high-quality code through iteration and review. This is the cure for our current disaster where a single agent produces garbage like PR #23.

### Why This Is Important
- This is THE key innovation that ensures quality
- Prevents bad code from ever reaching PRs
- Implements pair programming best practices
- Enables iteration based on feedback
- Catches errors before they become problems

### Context
Traditional pair programming has a driver (who codes) and a navigator (who reviews and guides). We're implementing this pattern with AI agents. The Developer writes code, the Navigator reviews it, provides feedback, and the Developer iterates. This continues until the Navigator approves or max iterations are reached.

## Acceptance Criteria

### Required
- [ ] TaskPair class orchestrates Developer-Navigator collaboration
- [ ] Developer generates initial solution for task
- [ ] Navigator reviews and provides specific, actionable feedback
- [ ] Developer can iterate based on feedback (max 3 iterations)
- [ ] Each iteration is saved as a separate artifact
- [ ] Navigator can approve, request changes, or reject
- [ ] Feedback is incorporated into next iteration attempt
- [ ] Clear logging of each iteration and decision
- [ ] State properly updated throughout execution
- [ ] Handles both success and failure cases gracefully

## Technical Details

### Task Pair Architecture
```python
# agents/pairs/task_pair.py
from typing import Optional, Tuple, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ReviewDecision(str, Enum):
    APPROVED = "approved"
    NEEDS_CHANGES = "needs_changes"  
    REJECTED = "rejected"

class ReviewFeedback(BaseModel):
    """Navigator's feedback on work."""
    decision: ReviewDecision
    overall_assessment: str
    specific_issues: List[str] = Field(description="Specific problems found")
    suggestions: List[str] = Field(description="Specific improvement suggestions")
    positive_aspects: List[str] = Field(description="What was done well")
    required_changes: List[str] = Field(description="Must fix before approval")
    code_quality_score: int = Field(ge=0, le=10, description="Quality score 0-10")

class IterationResult(BaseModel):
    """Result of one iteration."""
    iteration_number: int
    tasker_output: dict  # The work produced
    navigator_feedback: ReviewFeedback
    duration_seconds: float
    success: bool

class TaskPairResult(BaseModel):
    """Final result of pair execution."""
    task_id: str
    success: bool
    iterations: List[IterationResult]
    final_output: Optional[dict]
    total_duration_seconds: float
    failure_reason: Optional[str]

class TaskPair:
    """
    Orchestrates collaboration between a Tasker and Navigator.
    
    This implements the pair programming pattern where the Tasker does
    the work and the Navigator reviews and guides.
    """
    
    def __init__(
        self,
        tasker_agent,  # Developer, Analyst, or Tester
        navigator_agent,  # Always Navigator, specialized for task type
        max_iterations: int = 3,
        require_approval: bool = True
    ):
        self.tasker = tasker_agent
        self.navigator = navigator_agent
        self.max_iterations = max_iterations
        self.require_approval = require_approval
        
    async def execute_task(self, task: dict, context: dict) -> TaskPairResult:
        """
        Execute task with iteration cycle.
        
        Args:
            task: Task definition from PM
            context: Additional context (repo, existing code, etc.)
            
        Returns:
            TaskPairResult with all iterations and final output
        """
        start_time = datetime.now()
        iterations = []
        current_task = task.copy()
        
        logger.info(f"Starting pair execution for task {task['id']}")
        
        for iteration_num in range(1, self.max_iterations + 1):
            logger.info(f"Iteration {iteration_num} of {self.max_iterations}")
            
            # Execute one iteration
            iteration_result = await self._execute_iteration(
                current_task,
                context,
                iteration_num,
                iterations
            )
            iterations.append(iteration_result)
            
            # Check if approved
            if iteration_result.navigator_feedback.decision == ReviewDecision.APPROVED:
                logger.info(f"Task approved after {iteration_num} iteration(s)")
                return TaskPairResult(
                    task_id=task["id"],
                    success=True,
                    iterations=iterations,
                    final_output=iteration_result.tasker_output,
                    total_duration_seconds=(datetime.now() - start_time).total_seconds(),
                    failure_reason=None
                )
            
            # Check if rejected
            if iteration_result.navigator_feedback.decision == ReviewDecision.REJECTED:
                logger.warning(f"Task rejected after {iteration_num} iteration(s)")
                return TaskPairResult(
                    task_id=task["id"],
                    success=False,
                    iterations=iterations,
                    final_output=None,
                    total_duration_seconds=(datetime.now() - start_time).total_seconds(),
                    failure_reason="Navigator rejected: " + 
                                 iteration_result.navigator_feedback.overall_assessment
                )
            
            # Prepare for next iteration with feedback
            current_task = self._incorporate_feedback(
                current_task,
                iteration_result.navigator_feedback
            )
        
        # Max iterations reached
        logger.warning(f"Max iterations ({self.max_iterations}) reached without approval")
        
        # Use last iteration output if not requiring strict approval
        final_output = iterations[-1].tasker_output if not self.require_approval else None
        
        return TaskPairResult(
            task_id=task["id"],
            success=not self.require_approval,  # Partial success if not requiring approval
            iterations=iterations,
            final_output=final_output,
            total_duration_seconds=(datetime.now() - start_time).total_seconds(),
            failure_reason="Max iterations reached without approval" if self.require_approval else None
        )
    
    async def _execute_iteration(
        self,
        task: dict,
        context: dict,
        iteration_num: int,
        previous_iterations: List[IterationResult]
    ) -> IterationResult:
        """Execute a single iteration of work and review."""
        iteration_start = datetime.now()
        
        # Tasker does the work
        logger.info(f"Tasker executing task {task['id']}, iteration {iteration_num}")
        
        # Include previous feedback in context if not first iteration
        enhanced_context = context.copy()
        if previous_iterations:
            enhanced_context["previous_feedback"] = [
                iter.navigator_feedback for iter in previous_iterations
            ]
            enhanced_context["previous_attempts"] = [
                iter.tasker_output for iter in previous_iterations
            ]
        
        try:
            tasker_output = await self.tasker.execute(task, enhanced_context)
        except Exception as e:
            logger.error(f"Tasker failed: {e}")
            # Create a failure output
            tasker_output = {
                "error": str(e),
                "failed": True
            }
        
        # Navigator reviews the work
        logger.info(f"Navigator reviewing output for task {task['id']}")
        
        try:
            navigator_feedback = await self.navigator.review(
                task=task,
                work_output=tasker_output,
                context=context,
                iteration_number=iteration_num
            )
        except Exception as e:
            logger.error(f"Navigator failed: {e}")
            # Create a rejection feedback
            navigator_feedback = ReviewFeedback(
                decision=ReviewDecision.REJECTED,
                overall_assessment=f"Review failed: {str(e)}",
                specific_issues=[str(e)],
                suggestions=[],
                positive_aspects=[],
                required_changes=[],
                code_quality_score=0
            )
        
        return IterationResult(
            iteration_number=iteration_num,
            tasker_output=tasker_output,
            navigator_feedback=navigator_feedback,
            duration_seconds=(datetime.now() - iteration_start).total_seconds(),
            success=navigator_feedback.decision == ReviewDecision.APPROVED
        )
    
    def _incorporate_feedback(self, task: dict, feedback: ReviewFeedback) -> dict:
        """
        Update task with feedback for next iteration.
        
        This is crucial - we modify the task description to include
        the feedback so the Tasker knows what to fix.
        """
        enhanced_task = task.copy()
        
        # Add feedback to task description
        feedback_summary = f"""
        PREVIOUS ATTEMPT FEEDBACK:
        Decision: {feedback.decision}
        Assessment: {feedback.overall_assessment}
        
        Issues to fix:
        {chr(10).join(f'- {issue}' for issue in feedback.specific_issues)}
        
        Required changes:
        {chr(10).join(f'- {change}' for change in feedback.required_changes)}
        
        Suggestions:
        {chr(10).join(f'- {suggestion}' for suggestion in feedback.suggestions)}
        
        What was good (keep these):
        {chr(10).join(f'- {good}' for good in feedback.positive_aspects)}
        """
        
        # Append feedback to original description
        enhanced_task["description"] = (
            task.get("description", "") + 
            "\n\n" + 
            feedback_summary
        )
        
        # Update acceptance criteria if navigator specified required changes
        if feedback.required_changes:
            enhanced_task["acceptance_criteria"] = (
                task.get("acceptance_criteria", []) + 
                feedback.required_changes
            )
        
        return enhanced_task
```

### Integration with Developer Agent
```python
# agents/developer/agent.py (update)
class DeveloperAgent:
    """Developer agent that implements code."""
    
    async def execute(self, task: dict, context: dict) -> dict:
        """
        Execute a development task.
        
        If context contains previous_feedback, incorporate it.
        """
        # Check for previous feedback
        if "previous_feedback" in context:
            # This is an iteration - be more careful
            return await self._iterate_with_feedback(task, context)
        else:
            # First attempt - standard implementation
            return await self._initial_implementation(task, context)
    
    async def _iterate_with_feedback(self, task: dict, context: dict) -> dict:
        """Implement solution considering previous feedback."""
        
        prompt = f"""
        You are improving code based on review feedback.
        
        Task: {task['description']}
        
        Previous feedback shows what needs to be fixed.
        Focus on addressing the specific issues while keeping what worked.
        
        Be surgical - don't rewrite everything, just fix the problems.
        """
        
        # Generate improved solution...
        # Return artifacts
```

### Integration with Navigator Agent
```python
# agents/navigator/agent.py
class NavigatorAgent:
    """Navigator agent that reviews and guides."""
    
    async def review(
        self,
        task: dict,
        work_output: dict,
        context: dict,
        iteration_number: int
    ) -> ReviewFeedback:
        """
        Review work and provide feedback.
        
        Be specific and actionable. Don't just say "fix this",
        explain HOW to fix it.
        """
        
        prompt = f"""
        You are a senior developer reviewing code (iteration {iteration_number}).
        
        Task requirements: {task['description']}
        Acceptance criteria: {task.get('acceptance_criteria', [])}
        
        Review the implementation thoroughly:
        1. Does it meet all requirements?
        2. Is the code quality good?
        3. Are there bugs or issues?
        4. What specific improvements are needed?
        
        Be constructive - we want to guide improvement, not just criticize.
        If iteration {iteration_number} >= 2, be more lenient unless there are critical issues.
        
        Provide specific, actionable feedback.
        """
        
        # Review and return structured feedback
```

### Workflow Integration
```python
# workflows/nodes/task_execution.py
from agents.pairs.task_pair import TaskPair
from agents.developer.agent import DeveloperAgent
from agents.navigator.agent import NavigatorAgent

async def execute_task_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Execute current task using pair programming."""
    
    current_task = state["current_task"]
    logger.info(f"Executing task {current_task['id']} with pair programming")
    
    # Create appropriate pair based on task type
    if current_task["assigned_agent"] == "developer":
        tasker = DeveloperAgent()
        navigator = NavigatorAgent(specialty="code_review")
    elif current_task["assigned_agent"] == "analyst":
        tasker = AnalystAgent()
        navigator = NavigatorAgent(specialty="requirements_review")
    else:  # tester
        tasker = TesterAgent()
        navigator = NavigatorAgent(specialty="test_review")
    
    # Create pair
    pair = TaskPair(
        tasker_agent=tasker,
        navigator_agent=navigator,
        max_iterations=state.get("max_iterations", 3)
    )
    
    # Execute with pair
    result = await pair.execute_task(
        task=current_task,
        context={
            "repository": state["repository"],
            "issue": {
                "number": state["issue_number"],
                "title": state["issue_title"],
                "body": state["issue_body"]
            },
            "previous_tasks": state.get("completed_tasks", [])
        }
    )
    
    # Update state with result
    state["task_results"] = state.get("task_results", [])
    state["task_results"].append(result.model_dump())
    
    if result.success:
        state["artifacts"].extend(result.final_output.get("artifacts", []))
        state["completed_tasks"] = state.get("completed_tasks", [])
        state["completed_tasks"].append(current_task["id"])
        logger.info(f"Task {current_task['id']} completed successfully")
    else:
        state["errors"].append(f"Task {current_task['id']} failed: {result.failure_reason}")
        logger.error(f"Task {current_task['id']} failed after {len(result.iterations)} iterations")
    
    state["updated_at"] = datetime.now()
    return state
```

## Testing Requirements

### Unit Tests
```python
# tests/test_task_pair.py
import pytest
from agents.pairs.task_pair import TaskPair, ReviewDecision

class MockDeveloper:
    async def execute(self, task, context):
        if "previous_feedback" in context:
            # Improved version
            return {"code": "function fixed() { return true; }"}
        else:
            # Initial version with bug
            return {"code": "function broken() { retrun false; }"}  # Typo!

class MockNavigator:
    async def review(self, task, work_output, context, iteration_number):
        if "retrun" in work_output.get("code", ""):
            return ReviewFeedback(
                decision=ReviewDecision.NEEDS_CHANGES,
                overall_assessment="Found typo in return statement",
                specific_issues=["'retrun' should be 'return'"],
                required_changes=["Fix typo in return statement"],
                suggestions=["Check for other typos"],
                positive_aspects=["Function structure is good"],
                code_quality_score=6
            )
        else:
            return ReviewFeedback(
                decision=ReviewDecision.APPROVED,
                overall_assessment="Code looks good",
                specific_issues=[],
                required_changes=[],
                suggestions=[],
                positive_aspects=["No issues found"],
                code_quality_score=9
            )

@pytest.mark.asyncio
async def test_task_pair_iteration():
    """Test that pair programming iteration works."""
    pair = TaskPair(MockDeveloper(), MockNavigator())
    
    result = await pair.execute_task(
        task={"id": "test-1", "description": "Fix function"},
        context={}
    )
    
    assert result.success
    assert len(result.iterations) == 2  # Should take 2 iterations
    assert result.iterations[0].navigator_feedback.decision == ReviewDecision.NEEDS_CHANGES
    assert result.iterations[1].navigator_feedback.decision == ReviewDecision.APPROVED
```

## Dependencies & Risks

### Prerequisites
- Developer Agent implemented (Story 4.1)
- Navigator Agent implemented (Story 3.1)
- Understanding of pair programming concepts

### Risks
- **Infinite iteration loops**: Mitigated by max_iterations
- **Feedback incorporation failure**: Tasker might not understand feedback
- **Over-critical Navigator**: Might never approve
- **API costs**: Multiple iterations use more tokens

### Mitigations
- Hard limit on iterations
- Clear feedback structure
- Progressive leniency in Navigator
- Cache successful patterns

## Definition of Done

1. ✅ TaskPair class fully implemented
2. ✅ Iteration cycle works correctly
3. ✅ Feedback incorporated into next attempt
4. ✅ Navigator can approve/reject/request changes
5. ✅ All iterations saved as artifacts
6. ✅ Integration with workflow
7. ✅ Comprehensive logging
8. ✅ Unit tests pass
9. ✅ Handles errors gracefully

## Implementation Notes for AI Agents

### DO
- Make feedback specific and actionable
- Save all iterations for learning
- Be progressively more lenient
- Focus on critical issues first
- Celebrate what was done well

### DON'T
- Don't be overly critical
- Don't reject without explanation
- Don't lose previous feedback
- Don't exceed max iterations
- Don't approve broken code

### Common Pitfalls to Avoid
1. Navigator being too vague ("make it better")
2. Tasker ignoring feedback completely
3. Not saving intermediate iterations
4. Feedback not being incorporated
5. Accepting bad code to avoid iterations

## Success Example

This prevents disasters like PR #23:
```python
# Original issue: "Remove phrase from README"

# Without pairs: Agent deletes entire README ❌

# With pairs:
# Iteration 1: Developer deletes whole file
# Navigator: "No! Just remove the phrase, restore the rest"
# Iteration 2: Developer removes just the phrase
# Navigator: "Perfect, approved!" ✅
```

## Next Story
Once this story is complete, proceed to [Story 4.3: Code Artifact Management](story-4.3-artifact-management.md)