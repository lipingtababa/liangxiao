"""Complete PM integration nodes for end-to-end workflow.

This module provides comprehensive PM Agent integration that implements the complete
workflow as specified in Story 7.1, with proper issue analysis, task breakdown,
and integration with the TaskPair system.
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
from agents.pm.agent import PMAgent
from agents.pm.models import IssueAnalysis, TaskBreakdown
from services.github_service import GitHubService

logger = get_logger(__name__)


async def pm_analyze_issue_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """
    PM Agent analyzes the issue comprehensively.
    
    This node implements the first phase of Story 7.1 where the PM Agent
    performs deep analysis of the GitHub issue to understand requirements,
    complexity, and create the foundation for task breakdown.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated workflow state with comprehensive issue analysis
    """
    logger.info(f"PM analyzing issue #{state['issue_number']}: {state['issue_title']}")
    
    # Update workflow status
    state["status"] = WorkflowStatus.PM_ANALYZING
    state["current_step_description"] = "Project Manager analyzing issue requirements"
    state["progress_percentage"] = 0.05
    state = update_state_timestamp(state)
    
    try:
        # Initialize PM Agent
        pm_agent = PMAgent()
        
        # Prepare issue data for PM analysis
        issue_data = {
            "number": state["issue_number"],
            "title": state["issue_title"],
            "body": state["issue_body"],
            "url": state["issue_url"],
            "labels": state.get("issue_labels", []),
            "assignees": state.get("issue_assignees", []),
            "repository": state["repository"]
        }
        
        logger.info(f"Starting PM analysis for issue #{issue_data['number']}")
        
        # Execute PM analysis
        analysis_result = pm_agent.analyze_issue(issue_data)
        
        # Store comprehensive analysis results
        state["issue_analysis"] = analysis_result.model_dump()
        
        # Update legacy compatibility field
        state["analysis"] = {
            "issue_type": analysis_result.issue_type,
            "complexity": analysis_result.complexity,
            "summary": analysis_result.summary,
            "confidence_score": analysis_result.confidence_score,
            "pm_analysis": True,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        # Update progress tracking
        state["progress_percentage"] = 0.15
        state["agent_interactions"] = state.get("agent_interactions", 0) + 1
        
        # Track metrics
        pm_metrics = pm_agent.get_metrics()
        state["tokens_used"] = state.get("tokens_used", 0) + pm_metrics.get("total_tokens_used", 0)
        
        logger.info(
            f"PM analysis complete: {analysis_result.issue_type} "
            f"({analysis_result.complexity}) with {analysis_result.confidence_score:.2f} confidence"
        )
        
        # Update issue with analysis (if GitHub service available)
        try:
            github_service = GitHubService()  # This might not be available in all contexts
            await _post_analysis_comment(github_service, state, analysis_result)
        except Exception as e:
            logger.warning(f"Could not post analysis comment: {e}")
            # Don't fail the workflow for GitHub comment issues
        
        # Set success indicators
        state["should_continue"] = True
        state["next_step"] = "plan_tasks"
        
    except Exception as e:
        logger.error(f"PM analysis failed for issue #{state['issue_number']}: {e}", exc_info=True)
        
        # Record error but continue with fallback analysis
        error_msg = f"PM analysis failed: {str(e)}"
        state = add_error(state, error_msg)
        
        # Create fallback analysis to allow workflow continuation
        state = _create_fallback_analysis(state)
        state = add_warning(state, "Using fallback analysis due to PM analysis failure")
    
    return update_state_timestamp(state)


async def pm_plan_tasks_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """
    PM Agent creates comprehensive task breakdown and execution plan.
    
    This node implements the task planning phase of Story 7.1 where the PM Agent
    breaks down the analyzed issue into specific, actionable tasks with proper
    dependencies and agent assignments.
    
    Args:
        state: Current workflow state with completed analysis
        
    Returns:
        Updated workflow state with complete task breakdown
    """
    logger.info(f"PM planning tasks for issue #{state['issue_number']}")
    
    # Update workflow status
    state["status"] = WorkflowStatus.PLANNING
    state["current_step_description"] = "Creating comprehensive task breakdown"
    state["progress_percentage"] = 0.2
    state = update_state_timestamp(state)
    
    try:
        # Validate analysis exists
        if not state.get("issue_analysis"):
            raise ValueError("No issue analysis found - cannot create task breakdown")
        
        # Initialize PM Agent
        pm_agent = PMAgent()
        
        # Reconstruct analysis and issue data
        analysis_data = state["issue_analysis"]
        analysis = IssueAnalysis.model_validate(analysis_data)
        
        issue_data = {
            "number": state["issue_number"],
            "title": state["issue_title"],
            "body": state["issue_body"],
            "repository": state["repository"],
            "labels": state.get("issue_labels", [])
        }
        
        logger.info(f"Creating task breakdown for {analysis.issue_type} ({analysis.complexity})")
        
        # Execute task breakdown
        breakdown_result = pm_agent.create_task_breakdown(issue_data, analysis)
        
        # Store comprehensive task breakdown
        state["task_breakdown"] = [task.model_dump() for task in breakdown_result.tasks]
        state["execution_plan"] = breakdown_result.execution_order.copy()
        
        # Set initial task execution state
        if breakdown_result.tasks:
            state["current_task_index"] = 0
            state["current_task"] = breakdown_result.tasks[0].model_dump()
            state["completed_tasks"] = []
            state["failed_tasks"] = []
            state["task_results"] = []
            
            logger.info(f"First task set: {breakdown_result.tasks[0].title}")
        else:
            raise ValueError("No tasks created in breakdown")
        
        # Update legacy compatibility
        state["tasks"] = state["task_breakdown"].copy()
        
        # Update progress tracking
        state["progress_percentage"] = 0.25
        state["agent_interactions"] = state.get("agent_interactions", 0) + 1
        
        # Track comprehensive metrics
        pm_metrics = pm_agent.get_metrics()
        state["tokens_used"] = state.get("tokens_used", 0) + pm_metrics.get("total_tokens_used", 0)
        
        logger.info(
            f"Task breakdown created: {len(breakdown_result.tasks)} tasks, "
            f"{breakdown_result.total_estimated_hours:.1f}h estimated, "
            f"execution order: {breakdown_result.execution_order}"
        )
        
        # Update issue with task plan (if possible)
        try:
            github_service = GitHubService()
            await _post_task_plan_comment(github_service, state, breakdown_result)
        except Exception as e:
            logger.warning(f"Could not post task plan comment: {e}")
        
        # Set workflow transition
        state["status"] = WorkflowStatus.TASKS_QUEUED
        state["current_step_description"] = f"Ready to execute {len(breakdown_result.tasks)} tasks"
        state["should_continue"] = True
        state["next_step"] = "execute_tasks"
        
    except Exception as e:
        logger.error(f"PM task planning failed for issue #{state['issue_number']}: {e}", exc_info=True)
        
        error_msg = f"Task planning failed: {str(e)}"
        state = add_error(state, error_msg)
        
        # Try fallback task creation
        state = _create_fallback_task_breakdown(state)
        state = add_warning(state, "Using fallback task breakdown due to planning failure")
    
    return update_state_timestamp(state)


def advance_to_next_task_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """
    Advance workflow to the next task in the execution plan.
    
    This node handles task progression logic as specified in Story 7.1,
    respecting dependencies and managing the task execution queue.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with next task set or completion status
    """
    current_index = state.get("current_task_index", 0)
    task_breakdown = state.get("task_breakdown", [])
    execution_plan = state.get("execution_plan", [])
    
    logger.info(f"Advancing from task index {current_index} of {len(task_breakdown)}")
    
    # Check if we have more tasks
    next_index = current_index + 1
    
    if next_index >= len(task_breakdown):
        # All tasks processed
        logger.info("All tasks processed - moving to integration phase")
        state["current_task"] = None
        state["current_task_index"] = next_index
        state["should_continue"] = True
        state["next_step"] = "integrate_artifacts"
        state["current_step_description"] = "All tasks complete - integrating results"
        return update_state_timestamp(state)
    
    # Set next task
    if next_index < len(execution_plan):
        next_task_id = execution_plan[next_index]
        
        # Find task by ID
        next_task = None
        for task_data in task_breakdown:
            if task_data.get("id") == next_task_id:
                next_task = task_data
                break
        
        if next_task:
            state["current_task_index"] = next_index
            state["current_task"] = next_task
            state["current_step_description"] = f"Ready to execute: {next_task.get('title', 'Next task')}"
            
            # Update progress
            progress = 0.25 + (next_index / len(task_breakdown) * 0.6)  # 25% to 85%
            state["progress_percentage"] = min(progress, 0.85)
            
            logger.info(f"Next task set: {next_task.get('title')} ({next_task.get('assigned_agent')})")
        else:
            logger.warning(f"Could not find task with ID: {next_task_id}")
            # Skip to next
            return advance_to_next_task_node(state)
    else:
        logger.warning(f"Execution plan shorter than task breakdown")
        # Use task breakdown order as fallback
        state["current_task_index"] = next_index
        state["current_task"] = task_breakdown[next_index] if next_index < len(task_breakdown) else None
    
    state["should_continue"] = True
    state["next_step"] = "execute_task_pair"
    
    return update_state_timestamp(state)


def check_task_completion_status_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """
    Check overall task completion and determine workflow progression.
    
    This node implements the completion logic from Story 7.1, determining
    whether the workflow can proceed to artifact integration or needs
    additional handling.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with completion assessment
    """
    task_breakdown = state.get("task_breakdown", [])
    completed_tasks = state.get("completed_tasks", [])
    failed_tasks = state.get("failed_tasks", [])
    
    total_tasks = len(task_breakdown)
    completed_count = len(completed_tasks)
    failed_count = len(failed_tasks)
    
    logger.info(
        f"Task completion status: {completed_count}/{total_tasks} completed, "
        f"{failed_count} failed"
    )
    
    # Calculate completion metrics
    completion_rate = completed_count / max(total_tasks, 1)
    failure_rate = failed_count / max(total_tasks, 1)
    
    # Determine workflow status
    if completed_count == total_tasks:
        # Perfect completion
        state["next_step"] = "integrate_artifacts"
        state["current_step_description"] = "All tasks completed successfully"
        state["progress_percentage"] = 0.85
        logger.info("✅ All tasks completed successfully")
        
    elif completion_rate >= 0.8 and failure_rate <= 0.2:
        # Good enough completion (80% success, <= 20% failure)
        state["next_step"] = "integrate_artifacts"
        state["current_step_description"] = "Sufficient tasks completed - proceeding with integration"
        state["progress_percentage"] = 0.8
        state = add_warning(state, f"Proceeding with partial completion: {completed_count}/{total_tasks} tasks")
        logger.info(f"✅ Sufficient completion: {completion_rate:.1%} success rate")
        
    elif completion_rate >= 0.5:
        # Partial success - try to integrate what we have
        state["next_step"] = "integrate_artifacts"
        state["current_step_description"] = "Partial completion - integrating available results"
        state["progress_percentage"] = 0.7
        state = add_warning(state, f"Partial completion: {completed_count}/{total_tasks} tasks completed")
        logger.warning(f"⚠️ Partial completion: {completion_rate:.1%} success rate")
        
    else:
        # Too many failures
        state["next_step"] = "handle_workflow_failure"
        state["current_step_description"] = "Too many task failures - workflow failed"
        error_msg = f"Workflow failed: only {completed_count}/{total_tasks} tasks completed"
        state = add_error(state, error_msg)
        logger.error(f"❌ Workflow failure: {completion_rate:.1%} success rate")
    
    # Store completion metrics
    state["completion_metrics"] = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_count,
        "failed_tasks": failed_count,
        "completion_rate": completion_rate,
        "failure_rate": failure_rate,
        "assessed_at": datetime.utcnow().isoformat()
    }
    
    return update_state_timestamp(state)


async def _post_analysis_comment(
    github_service: GitHubService,
    state: IssueWorkflowState,
    analysis: IssueAnalysis
) -> None:
    """Post PM analysis results as issue comment."""
    try:
        comment_body = f"""🤖 **AI Project Manager Analysis Complete**

**Issue Type**: {analysis.issue_type}
**Complexity**: {analysis.complexity}
**Confidence**: {analysis.confidence_score:.1f}/10

**Summary**: {analysis.summary}

**Key Requirements**:
{chr(10).join(f"- {req}" for req in analysis.key_requirements)}

**Estimated Effort**: {analysis.estimated_effort}

Creating detailed task plan..."""

        await github_service.create_issue_comment(
            issue_number=state["issue_number"],
            body=comment_body
        )
        logger.info(f"Posted analysis comment to issue #{state['issue_number']}")
    except Exception as e:
        logger.warning(f"Failed to post analysis comment: {e}")


async def _post_task_plan_comment(
    github_service: GitHubService,
    state: IssueWorkflowState,
    breakdown: TaskBreakdown
) -> None:
    """Post task plan as issue comment."""
    try:
        task_list = "\n".join([
            f"{i+1}. **{task.title}** ({task.assigned_agent}) - {task.estimated_hours:.1f}h"
            for i, task in enumerate(breakdown.tasks)
        ])

        comment_body = f"""📋 **Task Execution Plan Created**

**Total Tasks**: {len(breakdown.tasks)}
**Estimated Time**: {breakdown.total_estimated_hours:.1f} hours

**Task Breakdown**:
{task_list}

**Execution Order**: {' → '.join(breakdown.execution_order)}

Starting task execution with AI agent pairs..."""

        await github_service.create_issue_comment(
            issue_number=state["issue_number"],
            body=comment_body
        )
        logger.info(f"Posted task plan comment to issue #{state['issue_number']}")
    except Exception as e:
        logger.warning(f"Failed to post task plan comment: {e}")


def _create_fallback_analysis(state: IssueWorkflowState) -> IssueWorkflowState:
    """Create fallback analysis when PM analysis fails."""
    logger.info("Creating fallback analysis")
    
    # Simple heuristic-based analysis
    title = state["issue_title"].lower()
    body = state.get("issue_body", "").lower()
    
    # Determine issue type
    if any(word in title for word in ["bug", "fix", "error", "broken"]):
        issue_type = "bug_fix"
    elif any(word in title for word in ["feature", "add", "implement"]):
        issue_type = "feature"
    elif any(word in title for word in ["doc", "readme", "documentation"]):
        issue_type = "documentation"
    else:
        issue_type = "enhancement"
    
    # Determine complexity
    if len(body) > 500 or any(word in title + body for word in ["complex", "major", "architecture"]):
        complexity = "complex"
    elif len(body) > 200:
        complexity = "medium"
    else:
        complexity = "simple"
    
    fallback_analysis = {
        "issue_type": issue_type,
        "complexity": complexity,
        "summary": f"Fallback analysis: {issue_type} task with {complexity} complexity",
        "key_requirements": [
            "Address the issue described in the title",
            "Follow project coding standards",
            "Include appropriate tests"
        ],
        "estimated_effort": "2-4 hours" if complexity == "simple" else "4-8 hours",
        "confidence_score": 5.0,
        "fallback": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    state["issue_analysis"] = fallback_analysis
    state["analysis"] = fallback_analysis.copy()
    
    return state


def _create_fallback_task_breakdown(state: IssueWorkflowState) -> IssueWorkflowState:
    """Create fallback task breakdown when PM planning fails."""
    logger.info("Creating fallback task breakdown")
    
    analysis = state.get("issue_analysis") or state.get("analysis", {})
    issue_type = analysis.get("issue_type", "enhancement")
    
    # Create basic tasks based on issue type
    tasks = []
    
    # Always start with analysis
    tasks.append({
        "id": "fallback-analysis",
        "title": "Analyze requirements and approach",
        "description": f"Understand the requirements for this {issue_type} task",
        "task_type": "analysis",
        "assigned_agent": "analyst",
        "estimated_hours": 1.0,
        "acceptance_criteria": [
            "Requirements clearly understood",
            "Solution approach identified"
        ],
        "dependencies": [],
        "priority": "high"
    })
    
    # Add implementation task
    tasks.append({
        "id": "fallback-implementation", 
        "title": f"Implement {issue_type} solution",
        "description": f"Implement the solution for this {issue_type}",
        "task_type": "implementation",
        "assigned_agent": "developer",
        "estimated_hours": 3.0,
        "acceptance_criteria": [
            "Solution implemented according to requirements",
            "Code follows project standards"
        ],
        "dependencies": ["fallback-analysis"],
        "priority": "high"
    })
    
    # Add testing if not documentation
    if issue_type != "documentation":
        tasks.append({
            "id": "fallback-testing",
            "title": "Create tests for implementation", 
            "description": "Create comprehensive tests for the implemented solution",
            "task_type": "testing",
            "assigned_agent": "tester",
            "estimated_hours": 1.5,
            "acceptance_criteria": [
                "Tests cover main functionality",
                "Tests pass successfully"
            ],
            "dependencies": ["fallback-implementation"],
            "priority": "medium"
        })
    
    # Set task breakdown state
    state["task_breakdown"] = tasks
    state["execution_plan"] = [task["id"] for task in tasks]
    state["current_task_index"] = 0
    state["current_task"] = tasks[0] if tasks else None
    state["completed_tasks"] = []
    state["failed_tasks"] = []
    state["task_results"] = []
    
    # Legacy compatibility
    state["tasks"] = tasks.copy()
    
    logger.info(f"Created fallback breakdown with {len(tasks)} tasks")
    
    return state