"""Task Pair Execution System.

This module implements the revolutionary Task Pair execution system where a 
Tasker agent (Developer, Analyst, or Tester) works with a Navigator agent
to produce high-quality work through iteration and review cycles.

This is THE key innovation that prevents disasters like PR #23 by implementing
pair programming patterns with AI agents.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum

from pydantic import BaseModel, Field

from agents.navigator.agent import NavigatorAgent, ReviewFeedback as NavReviewFeedback, ReviewDecision

logger = logging.getLogger(__name__)


class IterationResult(BaseModel):
    """Result of one iteration in the task pair cycle."""
    iteration_number: int = Field(description="Iteration number (1-based)")
    tasker_output: Dict[str, Any] = Field(description="The work produced by the tasker")
    navigator_feedback: NavReviewFeedback = Field(description="Structured feedback from navigator")
    duration_seconds: float = Field(description="Time taken for this iteration")
    success: bool = Field(description="Whether this iteration was successful")
    error: Optional[str] = Field(default=None, description="Error message if iteration failed")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class TaskPairResult(BaseModel):
    """Final result of task pair execution."""
    task_id: str = Field(description="Task identifier")
    success: bool = Field(description="Whether the task pair execution succeeded")
    iterations: List[IterationResult] = Field(description="All iteration results")
    final_output: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Final approved output from the tasker"
    )
    total_duration_seconds: float = Field(description="Total execution time")
    failure_reason: Optional[str] = Field(
        default=None, 
        description="Reason for failure if task failed"
    )
    max_iterations_reached: bool = Field(
        default=False, 
        description="Whether max iterations was reached without approval"
    )
    tokens_used: int = Field(default=0, description="Total tokens used across iterations")
    
    # Metrics and diagnostics
    final_quality_score: float = Field(default=0.0, description="Final quality score from navigator")
    disaster_prevention_score: float = Field(
        default=0.0, 
        description="Score indicating disaster prevention effectiveness"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the task pair execution."""
        status = "SUCCESS" if self.success else "FAILED"
        duration = f"{self.total_duration_seconds:.1f}s"
        iterations = f"{len(self.iterations)} iteration{'s' if len(self.iterations) != 1 else ''}"
        
        if self.final_output:
            artifacts_count = len(self.final_output.get('artifacts', []))
            artifacts_info = f", {artifacts_count} artifacts" if artifacts_count > 0 else ""
        else:
            artifacts_info = ""
        
        return (
            f"TaskPair[{self.task_id}]: {status} in {iterations} ({duration})"
            f"{artifacts_info}, quality: {self.final_quality_score:.1f}/10"
        )


class TaskPair:
    """
    Orchestrates collaboration between a Tasker and Navigator agent.
    
    This implements the pair programming pattern where:
    1. Tasker does the work (Developer, Analyst, or Tester)  
    2. Navigator reviews and provides feedback
    3. Iteration continues until approved or max iterations reached
    4. Each iteration is saved with detailed feedback
    5. Progressive leniency prevents infinite loops
    
    This is THE cure for disasters like PR #23 where agents produce garbage
    because they lack proper review cycles.
    """
    
    def __init__(
        self,
        tasker_agent: Any,  # Developer, Analyst, or Tester agent
        navigator_agent: NavigatorAgent,
        max_iterations: int = 3,
        require_approval: bool = True,
        min_quality_threshold: float = 6.0,
        enable_progressive_leniency: bool = True
    ):
        """
        Initialize Task Pair with agents and configuration.
        
        Args:
            tasker_agent: The agent that does the work (Developer/Analyst/Tester)
            navigator_agent: The Navigator agent that reviews work
            max_iterations: Maximum number of iterations before giving up
            require_approval: Whether to require Navigator approval for success
            min_quality_threshold: Minimum quality score to accept (0-10)
            enable_progressive_leniency: Whether to use progressive leniency
        """
        self.tasker = tasker_agent
        self.navigator = navigator_agent  
        self.max_iterations = max_iterations
        self.require_approval = require_approval
        self.min_quality_threshold = min_quality_threshold
        self.enable_progressive_leniency = enable_progressive_leniency
        
        # Track metrics
        self.total_executions = 0
        self.total_iterations = 0
        self.total_approvals = 0
        self.total_rejections = 0
        
        # Get agent type for logging
        self.tasker_type = self._get_agent_type(tasker_agent)
        self.navigator_specialty = getattr(navigator_agent, 'specialty', 'unknown')
        
        logger.info(
            f"TaskPair initialized: {self.tasker_type} + Navigator[{self.navigator_specialty}], "
            f"max_iter={max_iterations}, require_approval={require_approval}"
        )
    
    def _get_agent_type(self, agent: Any) -> str:
        """Get the type of agent for logging purposes."""
        agent_class_name = agent.__class__.__name__
        if 'Developer' in agent_class_name:
            return 'Developer'
        elif 'Analyst' in agent_class_name:
            return 'Analyst' 
        elif 'Tester' in agent_class_name:
            return 'Tester'
        else:
            return agent_class_name
    
    async def execute_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> TaskPairResult:
        """
        Execute task with iteration cycle implementing pair programming.
        
        This is the core method that implements the revolutionary pair programming
        pattern:
        1. Tasker attempts the work
        2. Navigator reviews with specific feedback  
        3. If not approved, incorporate feedback and iterate
        4. Continue until approved or max iterations reached
        
        Args:
            task: Task definition containing:
                - id: Task identifier
                - description: What needs to be done
                - type: Task type (analysis/implementation/testing)
                - acceptance_criteria: Success criteria
            context: Execution context containing:
                - issue: GitHub issue information
                - repository: Repository context
                - previous_tasks: Results from previous tasks
                
        Returns:
            TaskPairResult with all iterations and final outcome
        """
        start_time = datetime.now()
        task_id = task.get('id', 'unknown')
        iterations: List[IterationResult] = []
        current_task = task.copy()
        total_tokens = 0
        
        logger.info(f"🚀 Starting TaskPair execution for {task_id} ({self.tasker_type} + Navigator)")
        
        # Validate inputs
        if not task:
            return self._create_failure_result(
                task_id, iterations, start_time, "No task provided", total_tokens
            )
        
        if not task.get('description'):
            return self._create_failure_result(
                task_id, iterations, start_time, "Task has no description", total_tokens
            )
        
        try:
            # Execute iteration cycle
            for iteration_num in range(1, self.max_iterations + 1):
                logger.info(f"📋 Iteration {iteration_num}/{self.max_iterations} for task {task_id}")
                
                # Execute single iteration
                iteration_result = await self._execute_iteration(
                    current_task=current_task,
                    context=context,
                    iteration_num=iteration_num,
                    previous_iterations=iterations
                )
                
                iterations.append(iteration_result)
                total_tokens += getattr(iteration_result, 'tokens_used', 0)
                self.total_iterations += 1
                
                # Check Navigator's decision
                decision = iteration_result.navigator_feedback.decision
                quality_score = iteration_result.navigator_feedback.quality_score
                
                if decision == ReviewDecision.APPROVED:
                    # Success! Navigator approved the work
                    self.total_approvals += 1
                    logger.info(
                        f"✅ Task {task_id} APPROVED after {iteration_num} iteration(s), "
                        f"quality: {quality_score}/10"
                    )
                    
                    result = TaskPairResult(
                        task_id=task_id,
                        success=True,
                        iterations=iterations,
                        final_output=iteration_result.tasker_output,
                        total_duration_seconds=(datetime.now() - start_time).total_seconds(),
                        failure_reason=None,
                        max_iterations_reached=False,
                        tokens_used=total_tokens,
                        final_quality_score=quality_score,
                        disaster_prevention_score=self._calculate_disaster_prevention_score(iterations)
                    )
                    
                    self.total_executions += 1
                    return result
                
                elif decision == ReviewDecision.REJECTED:
                    # Navigator rejected - this is a hard failure
                    self.total_rejections += 1
                    logger.warning(
                        f"❌ Task {task_id} REJECTED after {iteration_num} iteration(s): "
                        f"{iteration_result.navigator_feedback.overall_assessment}"
                    )
                    
                    result = TaskPairResult(
                        task_id=task_id,
                        success=False,
                        iterations=iterations,
                        final_output=None,
                        total_duration_seconds=(datetime.now() - start_time).total_seconds(),
                        failure_reason=f"Navigator rejected: {iteration_result.navigator_feedback.overall_assessment}",
                        max_iterations_reached=False,
                        tokens_used=total_tokens,
                        final_quality_score=quality_score,
                        disaster_prevention_score=0.0  # Rejection means no disaster prevention
                    )
                    
                    self.total_executions += 1
                    return result
                
                else:  # NEEDS_CHANGES
                    # Prepare for next iteration with feedback
                    if iteration_num < self.max_iterations:
                        logger.info(
                            f"🔄 Task {task_id} needs changes (iteration {iteration_num}), "
                            f"quality: {quality_score}/10, "
                            f"issues: {len(iteration_result.navigator_feedback.issues)}"
                        )
                        
                        # Incorporate feedback into next iteration  
                        current_task = self._incorporate_feedback(
                            current_task, iteration_result.navigator_feedback
                        )
                        
                        # Log key feedback points
                        if iteration_result.navigator_feedback.required_changes:
                            logger.info(
                                f"📝 Required changes: {len(iteration_result.navigator_feedback.required_changes)} items"
                            )
                    else:
                        # This is the last iteration - will be handled below
                        logger.warning(
                            f"⚠️ Max iterations reached for task {task_id}, "
                            f"final quality: {quality_score}/10"
                        )
            
            # Max iterations reached without approval
            final_iteration = iterations[-1] if iterations else None
            final_quality = final_iteration.navigator_feedback.quality_score if final_iteration else 0.0
            
            # Decide if we can accept the work despite not being approved
            can_accept_partial = (
                not self.require_approval and 
                final_quality >= self.min_quality_threshold and
                final_iteration and
                final_iteration.navigator_feedback.decision != ReviewDecision.REJECTED
            )
            
            if can_accept_partial:
                logger.warning(
                    f"⚠️ Task {task_id} accepted with partial success "
                    f"(max iterations reached, quality: {final_quality}/10)"
                )
                
                result = TaskPairResult(
                    task_id=task_id,
                    success=True,  # Partial success
                    iterations=iterations,
                    final_output=final_iteration.tasker_output,
                    total_duration_seconds=(datetime.now() - start_time).total_seconds(),
                    failure_reason=None,
                    max_iterations_reached=True,
                    tokens_used=total_tokens,
                    final_quality_score=final_quality,
                    disaster_prevention_score=self._calculate_disaster_prevention_score(iterations)
                )
            else:
                logger.error(
                    f"❌ Task {task_id} FAILED: max iterations reached without acceptable quality "
                    f"(final quality: {final_quality}/10, threshold: {self.min_quality_threshold}/10)"
                )
                
                result = TaskPairResult(
                    task_id=task_id,
                    success=False,
                    iterations=iterations,
                    final_output=None,
                    total_duration_seconds=(datetime.now() - start_time).total_seconds(),
                    failure_reason=f"Max iterations ({self.max_iterations}) reached without approval",
                    max_iterations_reached=True,
                    tokens_used=total_tokens,
                    final_quality_score=final_quality,
                    disaster_prevention_score=0.0
                )
            
            self.total_executions += 1
            return result
            
        except Exception as e:
            logger.error(f"💥 TaskPair execution failed for {task_id}: {e}", exc_info=True)
            return self._create_failure_result(
                task_id, iterations, start_time, f"Execution error: {str(e)}", total_tokens
            )
    
    async def _execute_iteration(
        self,
        current_task: Dict[str, Any],
        context: Dict[str, Any],
        iteration_num: int,
        previous_iterations: List[IterationResult]
    ) -> IterationResult:
        """
        Execute a single iteration of the Tasker-Navigator cycle.
        
        Args:
            current_task: Task to execute (may include previous feedback)
            context: Execution context
            iteration_num: Current iteration number
            previous_iterations: Results from previous iterations
            
        Returns:
            IterationResult with tasker output and navigator feedback
        """
        iteration_start = datetime.now()
        task_id = current_task.get('id', 'unknown')
        
        logger.info(f"🔧 {self.tasker_type} executing task {task_id}, iteration {iteration_num}")
        
        # Enhance context with previous feedback for iteration
        enhanced_context = context.copy()
        if previous_iterations:
            enhanced_context["previous_feedback"] = [
                iter_result.navigator_feedback for iter_result in previous_iterations
            ]
            enhanced_context["previous_attempts"] = [
                iter_result.tasker_output for iter_result in previous_iterations
            ]
            enhanced_context["iteration_number"] = iteration_num
            
            # Add iteration guidance if available
            latest_feedback = previous_iterations[-1].navigator_feedback
            if hasattr(self.navigator, 'provide_iteration_guidance'):
                guidance = self.navigator.provide_iteration_guidance(latest_feedback, iteration_num)
                enhanced_context["iteration_guidance"] = guidance
        
        # Step 1: Tasker executes the work
        try:
            logger.debug(f"Tasker starting work on task {task_id}")
            tasker_output = await self.tasker.execute(current_task, enhanced_context)
            
            # Validate tasker output
            if not isinstance(tasker_output, dict):
                tasker_output = {"error": "Tasker returned invalid output format", "failed": True}
            
            # Add metadata
            tasker_output.setdefault("iteration", iteration_num)
            tasker_output.setdefault("tasker_type", self.tasker_type)
            
        except Exception as e:
            logger.error(f"Tasker failed on task {task_id}: {e}")
            tasker_output = {
                "error": str(e),
                "failed": True,
                "iteration": iteration_num,
                "tasker_type": self.tasker_type
            }
        
        # Step 2: Navigator reviews the work
        logger.info(f"🔍 Navigator reviewing {self.tasker_type} output for task {task_id}")
        
        try:
            navigator_feedback = await self.navigator.review(
                task=current_task,
                work_output=tasker_output,
                context=context,
                iteration_number=iteration_num
            )
            
            # Validate navigator feedback
            if not isinstance(navigator_feedback, NavReviewFeedback):
                raise ValueError(f"Navigator returned invalid feedback type: {type(navigator_feedback)}")
                
        except Exception as e:
            logger.error(f"Navigator review failed for task {task_id}: {e}")
            # Create fallback rejection feedback
            navigator_feedback = NavReviewFeedback(
                decision=ReviewDecision.REJECTED,
                overall_assessment=f"Review failed: {str(e)}",
                issues=[],
                required_changes=["Fix the error that prevented review"],
                suggestions=[],
                positive_aspects=[],
                quality_score=0,
                completeness_score=0,
                correctness_score=0,
                reasoning=f"Unable to complete review due to error: {str(e)}",
                iteration_number=iteration_num,
                adjusted_strictness=1.0
            )
        
        # Calculate iteration result
        duration_seconds = (datetime.now() - iteration_start).total_seconds()
        success = navigator_feedback.decision == ReviewDecision.APPROVED
        
        logger.info(
            f"Iteration {iteration_num} complete: {navigator_feedback.decision.value}, "
            f"quality={navigator_feedback.quality_score}/10, "
            f"duration={duration_seconds:.1f}s"
        )
        
        return IterationResult(
            iteration_number=iteration_num,
            tasker_output=tasker_output,
            navigator_feedback=navigator_feedback,
            duration_seconds=duration_seconds,
            success=success,
            error=tasker_output.get("error") if tasker_output.get("failed") else None
        )
    
    def _incorporate_feedback(
        self, 
        task: Dict[str, Any], 
        feedback: NavReviewFeedback
    ) -> Dict[str, Any]:
        """
        Incorporate Navigator feedback into the task for the next iteration.
        
        This is crucial - we modify the task description to include specific
        feedback so the Tasker knows exactly what to fix.
        
        Args:
            task: Original task definition
            feedback: Structured feedback from Navigator
            
        Returns:
            Enhanced task with feedback incorporated
        """
        enhanced_task = task.copy()
        
        # Create comprehensive feedback summary
        feedback_sections = []
        
        # Overall assessment
        feedback_sections.append(f"PREVIOUS ITERATION RESULT: {feedback.decision.value.upper()}")
        feedback_sections.append(f"Assessment: {feedback.overall_assessment}")
        feedback_sections.append(f"Quality Score: {feedback.quality_score}/10")
        
        # Critical issues to fix
        if feedback.issues:
            critical_issues = [issue for issue in feedback.issues if issue.severity == "critical"]
            major_issues = [issue for issue in feedback.issues if issue.severity == "major"]
            
            if critical_issues:
                feedback_sections.append("CRITICAL ISSUES (MUST FIX):")
                for issue in critical_issues:
                    feedback_sections.append(f"- {issue.description} (Location: {issue.location})")
                    feedback_sections.append(f"  Solution: {issue.suggestion}")
            
            if major_issues:
                feedback_sections.append("MAJOR ISSUES (SHOULD FIX):")
                for issue in major_issues:
                    feedback_sections.append(f"- {issue.description} (Location: {issue.location})")
                    feedback_sections.append(f"  Solution: {issue.suggestion}")
        
        # Required changes
        if feedback.required_changes:
            feedback_sections.append("REQUIRED CHANGES:")
            for change in feedback.required_changes:
                feedback_sections.append(f"- {change}")
        
        # Suggestions for improvement
        if feedback.suggestions:
            feedback_sections.append("SUGGESTIONS FOR IMPROVEMENT:")
            for suggestion in feedback.suggestions:
                feedback_sections.append(f"- {suggestion}")
        
        # What was done well (to preserve)
        if feedback.positive_aspects:
            feedback_sections.append("KEEP THESE GOOD ASPECTS:")
            for positive in feedback.positive_aspects:
                feedback_sections.append(f"- {positive}")
        
        # Progressive leniency guidance
        if hasattr(feedback, 'iteration_number') and feedback.iteration_number >= 2:
            feedback_sections.append(f"NOTE: This is iteration {feedback.iteration_number}.")
            if feedback.iteration_number >= 3:
                feedback_sections.append("Focus ONLY on critical issues. Minor issues will be overlooked.")
        
        # Append comprehensive feedback to task description
        feedback_summary = "\n".join(feedback_sections)
        enhanced_task["description"] = (
            task.get("description", "") + 
            "\n\n" + 
            "=" * 50 + "\n" +
            "FEEDBACK FROM NAVIGATOR REVIEW:\n" +
            "=" * 50 + "\n" +
            feedback_summary + "\n" +
            "=" * 50
        )
        
        # Update acceptance criteria with required changes
        if feedback.required_changes:
            original_criteria = enhanced_task.get("acceptance_criteria", [])
            if isinstance(original_criteria, list):
                enhanced_task["acceptance_criteria"] = original_criteria + feedback.required_changes
            else:
                enhanced_task["acceptance_criteria"] = feedback.required_changes
        
        # Add feedback metadata  
        enhanced_task["navigator_feedback"] = {
            "iteration": feedback.iteration_number,
            "decision": feedback.decision.value,
            "quality_score": feedback.quality_score,
            "issue_count": len(feedback.issues),
            "critical_issues": len([i for i in feedback.issues if i.severity == "critical"]),
            "adjusted_strictness": feedback.adjusted_strictness
        }
        
        logger.debug(f"Incorporated feedback into task {task.get('id')}: {len(feedback.issues)} issues, {len(feedback.required_changes)} changes")
        
        return enhanced_task
    
    def _calculate_disaster_prevention_score(self, iterations: List[IterationResult]) -> float:
        """
        Calculate how well this task pair prevented disasters.
        
        Higher scores mean better disaster prevention through:
        - Catching errors in early iterations
        - Multiple review cycles
        - High-quality final output
        - Comprehensive feedback
        
        Args:
            iterations: All iteration results
            
        Returns:
            Disaster prevention score (0-100)
        """
        if not iterations:
            return 0.0
        
        score = 0.0
        
        # Base score for having review cycles at all
        score += 30.0
        
        # Bonus for multiple iterations (shows thorough review)
        if len(iterations) > 1:
            score += min(20.0, (len(iterations) - 1) * 10.0)
        
        # Quality improvement over iterations
        if len(iterations) > 1:
            first_quality = iterations[0].navigator_feedback.quality_score
            final_quality = iterations[-1].navigator_feedback.quality_score
            improvement = final_quality - first_quality
            score += max(0, min(20.0, improvement * 2))
        
        # Final quality score contribution
        final_quality = iterations[-1].navigator_feedback.quality_score
        score += final_quality * 3.0  # 0-30 points based on final quality
        
        # Penalty for critical issues in final iteration
        final_issues = iterations[-1].navigator_feedback.issues
        critical_count = len([i for i in final_issues if i.severity == "critical"])
        score -= critical_count * 10.0
        
        # Bonus for comprehensive feedback
        total_feedback_items = sum(
            len(iter_result.navigator_feedback.issues) + 
            len(iter_result.navigator_feedback.required_changes) +
            len(iter_result.navigator_feedback.suggestions)
            for iter_result in iterations
        )
        score += min(10.0, total_feedback_items)
        
        return max(0.0, min(100.0, score))
    
    def _create_failure_result(
        self,
        task_id: str,
        iterations: List[IterationResult],
        start_time: datetime,
        reason: str,
        tokens_used: int
    ) -> TaskPairResult:
        """Create a TaskPairResult for a failed execution."""
        return TaskPairResult(
            task_id=task_id,
            success=False,
            iterations=iterations,
            final_output=None,
            total_duration_seconds=(datetime.now() - start_time).total_seconds(),
            failure_reason=reason,
            max_iterations_reached=False,
            tokens_used=tokens_used,
            final_quality_score=0.0,
            disaster_prevention_score=0.0
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this TaskPair."""
        return {
            'tasker_type': self.tasker_type,
            'navigator_specialty': self.navigator_specialty,
            'total_executions': self.total_executions,
            'total_iterations': self.total_iterations,
            'total_approvals': self.total_approvals,
            'total_rejections': self.total_rejections,
            'max_iterations': self.max_iterations,
            'require_approval': self.require_approval,
            'min_quality_threshold': self.min_quality_threshold,
            'average_iterations_per_task': (
                self.total_iterations / max(self.total_executions, 1)
            ),
            'approval_rate': (
                self.total_approvals / max(self.total_executions, 1)
            ),
            'rejection_rate': (
                self.total_rejections / max(self.total_executions, 1)
            )
        }
    
    def __str__(self) -> str:
        """String representation of TaskPair."""
        return (
            f"TaskPair[{self.tasker_type}+Navigator[{self.navigator_specialty}]]"
            f"(executions={self.total_executions}, "
            f"approval_rate={self.total_approvals}/{self.total_executions})"
        )
    
    def __repr__(self) -> str:
        """Developer representation of TaskPair."""
        return (
            f"TaskPair(tasker={self.tasker_type}, "
            f"navigator_specialty='{self.navigator_specialty}', "
            f"max_iterations={self.max_iterations})"
        )


# Re-export ReviewDecision and ReviewFeedback for convenience
ReviewFeedback = NavReviewFeedback


def create_task_pair(
    tasker_agent: Any,
    navigator_specialty: str = "code_review",
    max_iterations: int = 3,
    require_approval: bool = True,
    **navigator_kwargs
) -> TaskPair:
    """
    Factory function to create a TaskPair with appropriate Navigator.
    
    Args:
        tasker_agent: The agent that will do the work
        navigator_specialty: Navigator specialty (code_review/requirements_review/test_review)
        max_iterations: Maximum iteration cycles
        require_approval: Whether Navigator approval is required for success
        **navigator_kwargs: Additional arguments for Navigator agent
        
    Returns:
        Configured TaskPair ready for execution
    """
    navigator = NavigatorAgent(
        specialty=navigator_specialty,
        **navigator_kwargs
    )
    
    return TaskPair(
        tasker_agent=tasker_agent,
        navigator_agent=navigator,
        max_iterations=max_iterations,
        require_approval=require_approval
    )