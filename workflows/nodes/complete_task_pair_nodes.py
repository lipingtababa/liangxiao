"""Complete task pair execution nodes for end-to-end workflow.

This module provides comprehensive TaskPair integration for all agent types
as specified in Story 7.1, implementing the complete orchestration of
Analyst-Navigator, Developer-Navigator, and Tester-Navigator pairs.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from core.logging import get_logger
from workflows.workflow_state import (
    IssueWorkflowState,
    WorkflowStatus,
    update_state_timestamp,
    add_error,
    add_warning
)

# Import all agent types
from agents.analyst.agent import AnalystAgent
from agents.developer.agent import DeveloperAgent
from agents.tester.agent import TesterAgent
from agents.navigator.agent import NavigatorAgent

# Import TaskPair system
from agents.pairs.task_pair import TaskPair, create_task_pair, TaskPairResult

logger = get_logger(__name__)


async def execute_task_with_complete_pair_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """
    Execute current task using complete TaskPair system for all agent types.
    
    This is the comprehensive implementation of Story 7.1's TaskPair orchestration
    that properly handles Analyst-Navigator, Developer-Navigator, and Tester-Navigator
    pairs with full iteration cycles and quality control.
    
    Args:
        state: Current workflow state with task to execute
        
    Returns:
        Updated workflow state with comprehensive task pair results
    """
    current_task = state.get("current_task")
    if not current_task:
        logger.warning(f"No current task for issue #{state['issue_number']}")
        state = add_warning(state, "No current task to execute")
        state["should_continue"] = False
        state["next_step"] = "check_completion"
        return update_state_timestamp(state)
    
    task_id = current_task.get('id', 'unknown')
    task_type = current_task.get('task_type', current_task.get('type', 'implementation'))
    assigned_agent = current_task.get('assigned_agent', 'developer')
    task_title = current_task.get('title', 'Untitled task')
    
    logger.info(
        f"🚀 Executing task {task_id}: {task_title} "
        f"(type={task_type}, agent={assigned_agent})"
    )
    
    # Update workflow status based on agent type
    status_mapping = {
        "analyst": WorkflowStatus.ANALYZING,
        "developer": WorkflowStatus.DEVELOPING,
        "tester": WorkflowStatus.TESTING
    }
    
    state["status"] = status_mapping.get(assigned_agent, WorkflowStatus.DEVELOPING)
    state["current_step_description"] = f"TaskPair executing: {task_title}"
    state["agent_interactions"] = state.get("agent_interactions", 0) + 1
    state = update_state_timestamp(state)
    
    try:
        # Step 1: Create appropriate tasker agent
        logger.info(f"Creating {assigned_agent} agent for task execution")
        tasker_agent = await _create_tasker_agent_comprehensive(assigned_agent, task_type, state)
        
        if not tasker_agent:
            error_msg = f"Failed to create tasker agent: {assigned_agent}"
            logger.error(error_msg)
            state = add_error(state, error_msg)
            state["should_continue"] = False
            state["next_step"] = "handle_task_failure"
            return update_state_timestamp(state)
        
        # Step 2: Determine Navigator specialty with enhanced logic
        navigator_specialty = _determine_navigator_specialty_comprehensive(
            task_type, assigned_agent, current_task
        )
        
        logger.info(f"Creating TaskPair: {assigned_agent} + Navigator[{navigator_specialty}]")
        
        # Step 3: Create comprehensive TaskPair configuration
        max_iterations = state.get("max_iterations", 3)
        
        # Adjust parameters based on task complexity
        task_complexity = current_task.get('complexity', 'medium')
        require_approval = True  # Always require approval for quality
        min_quality_threshold = _get_quality_threshold_for_task(task_type, task_complexity)
        
        task_pair = TaskPair(
            tasker_agent=tasker_agent,
            navigator_agent=NavigatorAgent(
                specialty=navigator_specialty,
                model="gpt-4-turbo-preview",  # Use high-quality model for navigation
                temperature=0.2  # Lower temperature for consistency
            ),
            max_iterations=max_iterations,
            require_approval=require_approval,
            min_quality_threshold=min_quality_threshold,
            enable_progressive_leniency=True
        )
        
        # Step 4: Prepare comprehensive execution context
        context = _prepare_comprehensive_execution_context(state, current_task)
        
        # Step 5: Execute task with comprehensive pair programming
        logger.info(f"Starting comprehensive TaskPair execution for {task_id}")
        pair_result = await task_pair.execute_task(current_task, context)
        
        # Step 6: Process comprehensive results
        state = await _process_comprehensive_pair_result(state, pair_result, task_pair)
        
        # Step 7: Update workflow progression
        if pair_result.success:
            logger.info(f"✅ Task {task_id} completed successfully with TaskPair")
            state["should_continue"] = True
            state["next_step"] = "advance_to_next_task"
            
            # Update completion tracking
            completed_tasks = state.get("completed_tasks", [])
            if task_id not in completed_tasks:
                completed_tasks.append(task_id)
                state["completed_tasks"] = completed_tasks
            
            # Post progress update to GitHub
            await _post_task_completion_update(state, current_task, pair_result)
            
        else:
            logger.error(f"❌ Task {task_id} failed: {pair_result.failure_reason}")
            
            # Add to failed tasks
            failed_tasks = state.get("failed_tasks", [])
            if task_id not in failed_tasks:
                failed_tasks.append(task_id)
                state["failed_tasks"] = failed_tasks
            
            # Determine if this is critical failure or can continue
            is_critical_task = current_task.get("critical", False)
            if is_critical_task:
                state = add_error(state, f"Critical task failed: {pair_result.failure_reason}")
                state["next_step"] = "handle_workflow_failure"
            else:
                state = add_warning(state, f"Non-critical task failed: {pair_result.failure_reason}")
                state["next_step"] = "advance_to_next_task"  # Continue with next task
            
            state["should_continue"] = True
        
        # Step 8: Log comprehensive execution summary
        logger.info(f"TaskPair execution summary: {pair_result.get_summary()}")
        
        # Update progress based on task completion
        current_index = state.get("current_task_index", 0)
        total_tasks = len(state.get("task_breakdown", []))
        if total_tasks > 0:
            progress = 0.25 + ((current_index + 1) / total_tasks * 0.6)
            state["progress_percentage"] = min(progress, 0.85)
        
    except Exception as e:
        logger.error(f"💥 TaskPair execution failed for {task_id}: {e}", exc_info=True)
        
        error_msg = f"TaskPair system error: {str(e)}"
        state = add_error(state, error_msg)
        
        # Add to failed tasks
        failed_tasks = state.get("failed_tasks", [])
        if task_id not in failed_tasks:
            failed_tasks.append(task_id)
            state["failed_tasks"] = failed_tasks
        
        # Determine next step based on failure type
        if "critical" in str(e).lower() or current_task.get("critical", False):
            state["next_step"] = "handle_workflow_failure"
        else:
            state["next_step"] = "advance_to_next_task"
        
        state["should_continue"] = True
    
    return update_state_timestamp(state)


async def _create_tasker_agent_comprehensive(
    assigned_agent: str, 
    task_type: str, 
    state: IssueWorkflowState
) -> Any:
    """
    Create appropriate tasker agent with comprehensive configuration.
    
    Args:
        assigned_agent: Agent type (analyst/developer/tester)
        task_type: Type of task being executed
        state: Current workflow state for context
        
    Returns:
        Configured agent instance or None if creation failed
    """
    try:
        repository = state.get("repository", "unknown")
        issue_complexity = state.get("issue_analysis", {}).get("complexity", "medium")
        
        if assigned_agent == "analyst":
            logger.info("Creating AnalystAgent for requirements analysis")
            return AnalystAgent(
                model="gpt-4-turbo-preview",  # Use best model for analysis
                temperature=0.2,  # Lower temperature for consistency
                max_files_to_analyze=20,  # Allow comprehensive analysis
                include_code_context=True,
                github_service=state.get("github_service")
            )
            
        elif assigned_agent == "developer":
            logger.info("Creating DeveloperAgent for implementation")
            return DeveloperAgent(
                model="gpt-4-turbo-preview",
                temperature=0.2,
                max_files_per_request=10,
                enable_advanced_analysis=True,
                github_service=state.get("github_service")
            )
            
        elif assigned_agent == "tester":
            logger.info("Creating TesterAgent for testing")
            return TesterAgent(
                model="gpt-4-turbo-preview",
                temperature=0.2,
                test_framework_preference="pytest",  # Default to pytest
                include_integration_tests=issue_complexity in ["complex", "very_complex"],
                enable_property_based_testing=True
            )
            
        else:
            logger.error(f"Unknown assigned agent type: {assigned_agent}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to create {assigned_agent} agent: {e}", exc_info=True)
        return None


def _determine_navigator_specialty_comprehensive(
    task_type: str, 
    assigned_agent: str, 
    task: Dict[str, Any]
) -> str:
    """
    Determine Navigator specialty with comprehensive logic.
    
    Args:
        task_type: Type of task being executed
        assigned_agent: Agent type executing the task
        task: Full task definition with context
        
    Returns:
        Navigator specialty string
    """
    task_title = task.get('title', '').lower()
    task_description = task.get('description', '').lower()
    
    # Priority 1: Explicit agent assignment
    if assigned_agent == "analyst":
        return "requirements_review"
    elif assigned_agent == "tester":
        return "test_review"
    
    # Priority 2: Task type analysis
    if task_type in ["analysis", "investigation", "requirements", "research"]:
        return "requirements_review"
    elif task_type in ["testing", "test", "validation", "qa"]:
        return "test_review"
    
    # Priority 3: Content analysis for edge cases
    if any(keyword in task_title + task_description for keyword in [
        "requirements", "analysis", "spec", "design", "research", "investigate"
    ]):
        return "requirements_review"
    elif any(keyword in task_title + task_description for keyword in [
        "test", "testing", "validation", "quality", "coverage"
    ]):
        return "test_review"
    
    # Default: code review for implementation tasks
    return "code_review"


def _get_quality_threshold_for_task(task_type: str, complexity: str) -> float:
    """
    Get appropriate quality threshold based on task characteristics.
    
    Args:
        task_type: Type of task
        complexity: Task complexity level
        
    Returns:
        Quality threshold (0.0-10.0)
    """
    base_thresholds = {
        "analysis": 7.0,      # High quality needed for requirements
        "implementation": 6.5, # Moderate quality for development
        "testing": 7.5,       # Very high quality for tests
        "documentation": 6.0,  # Moderate quality for docs
        "review": 8.0,        # Highest quality for reviews
    }
    
    complexity_modifiers = {
        "trivial": -0.5,
        "simple": 0.0,
        "medium": 0.0,
        "complex": +0.5,
        "very_complex": +1.0
    }
    
    base_threshold = base_thresholds.get(task_type, 6.5)
    complexity_modifier = complexity_modifiers.get(complexity, 0.0)
    
    return min(10.0, max(5.0, base_threshold + complexity_modifier))


def _prepare_comprehensive_execution_context(
    state: IssueWorkflowState, 
    current_task: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Prepare comprehensive execution context for TaskPair.
    
    Args:
        state: Current workflow state
        current_task: Task being executed
        
    Returns:
        Enhanced context dictionary
    """
    # Base context
    context = {
        # Issue information
        "issue": {
            "number": state.get("issue_number"),
            "title": state.get("issue_title"),
            "body": state.get("issue_body"),
            "url": state.get("issue_url"),
            "labels": state.get("issue_labels", []),
            "assignees": state.get("issue_assignees", [])
        },
        
        # Repository context
        "repository": state.get("repository"),
        
        # Workflow context
        "workflow_status": state.get("status"),
        "current_task_index": state.get("current_task_index", 0),
        "total_tasks": len(state.get("task_breakdown", [])),
        
        # Task execution context
        "max_iterations": state.get("max_iterations", 3),
        "current_iteration": state.get("current_iteration", 1),
        
        # Previous work context
        "completed_tasks": state.get("completed_tasks", []),
        "failed_tasks": state.get("failed_tasks", []),
        "task_results": state.get("task_results", []),
        
        # Artifacts context
        "all_artifacts": state.get("all_artifacts", []),
        "analysis_artifacts": state.get("analysis_artifacts", []),
        "code_artifacts": state.get("code_artifacts", []),
        "test_artifacts": state.get("test_artifacts", []),
        
        # Quality context
        "pair_execution_history": state.get("pair_execution_history", []),
        "quality_requirements": current_task.get("quality_requirements", []),
        
        # Services
        "github_service": state.get("github_service")
    }
    
    # Add PM analysis if available
    if state.get("issue_analysis"):
        context["pm_analysis"] = state["issue_analysis"]
        context["analysis"] = state["issue_analysis"]  # Legacy compatibility
    
    # Add task-specific context
    task_type = current_task.get("task_type", "implementation")
    if task_type == "analysis":
        # For analysis tasks, provide broader context
        context["analysis_scope"] = "comprehensive"
        context["include_architectural_considerations"] = True
        
    elif task_type == "implementation":
        # For development tasks, provide code context
        context["code_context"] = {
            "existing_artifacts": [a for a in context["code_artifacts"] if a.get("type") == "code"],
            "related_tasks": [
                task for task in state.get("task_breakdown", [])
                if task.get("task_type") == "implementation"
            ]
        }
        
    elif task_type == "testing":
        # For testing tasks, provide implementation context
        context["testing_context"] = {
            "implementation_artifacts": context["code_artifacts"],
            "test_framework": current_task.get("test_framework", "pytest"),
            "coverage_requirements": current_task.get("coverage_target", "80%")
        }
    
    # Add progressive quality context
    pair_executions = len(state.get("pair_execution_history", []))
    if pair_executions > 0:
        context["quality_learning"] = {
            "previous_pair_executions": pair_executions,
            "average_quality_score": _calculate_average_quality_score(state),
            "common_issues": _extract_common_issues(state)
        }
    
    return context


async def _process_comprehensive_pair_result(
    state: IssueWorkflowState,
    pair_result: TaskPairResult,
    task_pair: TaskPair
) -> IssueWorkflowState:
    """
    Process comprehensive TaskPair result and update workflow state.
    
    Args:
        state: Current workflow state
        pair_result: Result from TaskPair execution
        task_pair: The TaskPair that executed
        
    Returns:
        Updated workflow state with comprehensive results
    """
    current_task = state.get("current_task", {})
    task_id = current_task.get('id', 'unknown')
    
    # Initialize collections
    for collection in ["task_results", "all_artifacts", "analysis_artifacts", 
                      "code_artifacts", "test_artifacts", "pair_execution_history", 
                      "detailed_iterations"]:
        if collection not in state:
            state[collection] = []
    
    # Store comprehensive execution record
    execution_record = {
        "task_id": task_id,
        "task_title": current_task.get('title', 'Unknown'),
        "task_type": current_task.get('task_type', 'unknown'),
        "tasker_type": task_pair.tasker_type,
        "navigator_specialty": task_pair.navigator_specialty,
        "success": pair_result.success,
        "iterations": len(pair_result.iterations),
        "total_duration_seconds": pair_result.total_duration_seconds,
        "tokens_used": pair_result.tokens_used,
        "final_quality_score": pair_result.final_quality_score,
        "disaster_prevention_score": pair_result.disaster_prevention_score,
        "max_iterations_reached": pair_result.max_iterations_reached,
        "failure_reason": pair_result.failure_reason,
        "executed_at": datetime.utcnow().isoformat(),
        "workflow_context": {
            "issue_number": state.get("issue_number"),
            "current_task_index": state.get("current_task_index", 0),
            "total_tasks": len(state.get("task_breakdown", []))
        }
    }
    
    state["pair_execution_history"].append(execution_record)
    
    # Store detailed iteration history
    for iteration in pair_result.iterations:
        iteration_record = {
            "task_id": task_id,
            "iteration_number": iteration.iteration_number,
            "duration_seconds": iteration.duration_seconds,
            "navigator_decision": iteration.navigator_feedback.decision.value,
            "quality_score": iteration.navigator_feedback.quality_score,
            "completeness_score": iteration.navigator_feedback.completeness_score,
            "correctness_score": iteration.navigator_feedback.correctness_score,
            "issues_count": len(iteration.navigator_feedback.issues),
            "critical_issues": len([
                issue for issue in iteration.navigator_feedback.issues 
                if issue.severity == "critical"
            ]),
            "required_changes_count": len(iteration.navigator_feedback.required_changes),
            "success": iteration.success,
            "error": iteration.error,
            "timestamp": datetime.utcnow().isoformat()
        }
        state["detailed_iterations"].append(iteration_record)
    
    # Store task result in existing format for compatibility
    task_result = {
        "task_id": task_id,
        "task_title": current_task.get('title', 'Unknown'),
        "success": pair_result.success,
        "pair_programming": True,
        "tasker_type": task_pair.tasker_type,
        "navigator_specialty": task_pair.navigator_specialty,
        "iterations": len(pair_result.iterations),
        "total_duration_seconds": pair_result.total_duration_seconds,
        "tokens_used": pair_result.tokens_used,
        "final_quality_score": pair_result.final_quality_score,
        "disaster_prevention_score": pair_result.disaster_prevention_score,
        "failure_reason": pair_result.failure_reason,
        "execution_summary": pair_result.get_summary(),
        "completed_at": datetime.utcnow().isoformat()
    }
    
    state["task_results"].append(task_result)
    
    # Process artifacts by type if task succeeded
    if pair_result.success and pair_result.final_output:
        artifacts = pair_result.final_output.get("artifacts", [])
        
        for artifact in artifacts:
            # Add to all artifacts
            enriched_artifact = artifact.copy()
            enriched_artifact.update({
                "source_task_id": task_id,
                "source_task_type": current_task.get('task_type', 'unknown'),
                "tasker_type": task_pair.tasker_type,
                "quality_score": pair_result.final_quality_score,
                "created_at": datetime.utcnow().isoformat()
            })
            
            state["all_artifacts"].append(enriched_artifact)
            
            # Categorize by type
            artifact_type = artifact.get("type", "unknown")
            if artifact_type in ["requirements", "analysis", "design"]:
                state["analysis_artifacts"].append(enriched_artifact)
            elif artifact_type in ["code", "implementation", "fix"]:
                state["code_artifacts"].append(enriched_artifact)
            elif artifact_type in ["test", "testing", "validation"]:
                state["test_artifacts"].append(enriched_artifact)
        
        logger.info(
            f"Added {len(artifacts)} artifacts from TaskPair execution: "
            f"{len(state['analysis_artifacts'])} analysis, "
            f"{len(state['code_artifacts'])} code, "
            f"{len(state['test_artifacts'])} test"
        )
    
    # Update current task status
    if current_task:
        current_task["status"] = "completed" if pair_result.success else "failed"
        current_task["completed_at"] = datetime.utcnow().isoformat()
        current_task["pair_execution"] = True
        current_task["tasker_type"] = task_pair.tasker_type
        current_task["navigator_specialty"] = task_pair.navigator_specialty
        current_task["quality_score"] = pair_result.final_quality_score
        current_task["iterations"] = len(pair_result.iterations)
        current_task["disaster_prevention_score"] = pair_result.disaster_prevention_score
    
    # Update comprehensive metrics
    state["tokens_used"] = state.get("tokens_used", 0) + pair_result.tokens_used
    state["total_pair_executions"] = state.get("total_pair_executions", 0) + 1
    state["total_successful_pairs"] = state.get("total_successful_pairs", 0) + (1 if pair_result.success else 0)
    
    # Add quality warnings if needed
    if pair_result.max_iterations_reached:
        state = add_warning(
            state,
            f"Task {task_id} reached max iterations without full approval "
            f"(final quality: {pair_result.final_quality_score:.1f}/10)"
        )
    
    if pair_result.final_quality_score < 6.0:
        state = add_warning(
            state,
            f"Task {task_id} has low quality score: {pair_result.final_quality_score:.1f}/10"
        )
    
    # Log quality achievements
    if pair_result.success and pair_result.final_quality_score >= 8.0:
        logger.info(f"🌟 High-quality completion: {task_id} scored {pair_result.final_quality_score:.1f}/10")
    
    if pair_result.disaster_prevention_score >= 80.0:
        logger.info(f"🛡️ Excellent disaster prevention: {task_id} scored {pair_result.disaster_prevention_score:.1f}/100")
    
    return state


async def _post_task_completion_update(
    state: IssueWorkflowState,
    task: Dict[str, Any],
    pair_result: TaskPairResult
) -> None:
    """Post task completion update to GitHub issue."""
    try:
        from services.github_service import GitHubService
        github_service = GitHubService()
        
        task_title = task.get('title', 'Unknown task')
        task_type = task.get('task_type', 'unknown')
        current_index = state.get("current_task_index", 0)
        total_tasks = len(state.get("task_breakdown", []))
        
        status_emoji = "✅" if pair_result.success else "❌"
        quality_emoji = "🌟" if pair_result.final_quality_score >= 8.0 else "📊"
        
        comment_body = f"""{status_emoji} **Task {current_index + 1}/{total_tasks} Complete**: {task_title}

**Type**: {task_type}
**Duration**: {pair_result.total_duration_seconds:.1f}s
**Iterations**: {len(pair_result.iterations)}
{quality_emoji} **Quality Score**: {pair_result.final_quality_score:.1f}/10

{pair_result.get_summary()}"""

        await github_service.create_issue_comment(
            issue_number=state["issue_number"],
            body=comment_body
        )
        
    except Exception as e:
        logger.warning(f"Could not post task completion update: {e}")


def _calculate_average_quality_score(state: IssueWorkflowState) -> float:
    """Calculate average quality score from pair execution history."""
    history = state.get("pair_execution_history", [])
    if not history:
        return 0.0
    
    total_score = sum(exec["final_quality_score"] for exec in history)
    return total_score / len(history)


def _extract_common_issues(state: IssueWorkflowState) -> List[str]:
    """Extract common issues from detailed iteration history."""
    iterations = state.get("detailed_iterations", [])
    issue_counts = {}
    
    # This would need access to the actual issue descriptions
    # For now, return empty list - could be enhanced with actual issue analysis
    return []