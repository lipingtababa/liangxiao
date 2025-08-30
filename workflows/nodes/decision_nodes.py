"""Decision nodes for workflow conditional edges."""

from typing import Literal

from core.logging import get_logger
from workflows.workflow_state import IssueWorkflowState, WorkflowStatus

logger = get_logger(__name__)

# Type aliases for decision outcomes
ReviewDecision = Literal["iterate", "continue", "error"]
ContinueDecision = Literal["continue", "stop"]
ErrorRecoveryDecision = Literal["retry", "fail", "human_intervention"]


def review_decision(state: IssueWorkflowState) -> ReviewDecision:
    """
    Decide next step based on review results.
    
    Args:
        state: Current workflow state
    
    Returns:
        "iterate" - Need to revise and try again
        "continue" - Review passed, move to next stage
        "error" - Unrecoverable error occurred
    """
    issue_number = state.get("issue_number", "unknown")
    next_step = state.get("next_step")
    current_iteration = state.get("current_iteration", 0)
    max_iterations = state.get("max_iterations", 3)
    
    logger.debug(
        f"Review decision for issue #{issue_number}: "
        f"next_step={next_step}, iteration={current_iteration}/{max_iterations}"
    )
    
    # Check for explicit error condition
    if next_step == "error":
        logger.info(f"Review decision: error for issue #{issue_number}")
        return "error"
    
    # Check if we should iterate
    if next_step == "iterate":
        if current_iteration < max_iterations:
            logger.info(
                f"Review decision: iterate for issue #{issue_number} "
                f"(iteration {current_iteration}/{max_iterations})"
            )
            return "iterate"
        else:
            logger.warning(
                f"Max iterations reached for issue #{issue_number}, treating as error"
            )
            return "error"
    
    # Default to continue
    logger.info(f"Review decision: continue for issue #{issue_number}")
    return "continue"


def should_continue_decision(state: IssueWorkflowState) -> ContinueDecision:
    """
    Decide if workflow should continue processing.
    
    Args:
        state: Current workflow state
    
    Returns:
        "continue" - Keep processing
        "stop" - Stop workflow (success or failure)
    """
    should_continue = state.get("should_continue", True)
    status = state.get("status", WorkflowStatus.PENDING)
    issue_number = state.get("issue_number", "unknown")
    
    # Stop if explicitly marked
    if not should_continue:
        logger.info(f"Workflow stopping for issue #{issue_number} (should_continue=False)")
        return "stop"
    
    # Stop if in final state
    if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
        logger.info(f"Workflow stopping for issue #{issue_number} (final status: {status})")
        return "stop"
    
    # Stop if human intervention required
    if state.get("requires_human_input", False):
        logger.info(f"Workflow stopping for issue #{issue_number} (human input required)")
        return "stop"
    
    logger.debug(f"Workflow continuing for issue #{issue_number}")
    return "continue"


def error_recovery_decision(state: IssueWorkflowState) -> ErrorRecoveryDecision:
    """
    Decide how to handle errors in the workflow.
    
    Args:
        state: Current workflow state
    
    Returns:
        "retry" - Retry the failed operation
        "fail" - Mark workflow as failed
        "human_intervention" - Require human input
    """
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)
    errors = state.get("errors", [])
    issue_number = state.get("issue_number", "unknown")
    
    logger.debug(
        f"Error recovery decision for issue #{issue_number}: "
        f"retry_count={retry_count}/{max_retries}, errors={len(errors)}"
    )
    
    # If no errors, nothing to recover from
    if not errors:
        logger.warning(f"Error recovery called with no errors for issue #{issue_number}")
        return "fail"
    
    # Check if we can retry
    if retry_count < max_retries:
        # Check if error is retryable
        latest_error = errors[-1] if errors else ""
        
        # Don't retry validation errors or configuration errors
        non_retryable_keywords = [
            "validation", "configuration", "permission", "authentication",
            "missing required field", "invalid format"
        ]
        
        if any(keyword in latest_error.lower() for keyword in non_retryable_keywords):
            logger.info(
                f"Error recovery: non-retryable error for issue #{issue_number}: {latest_error}"
            )
            return "fail"
        
        logger.info(
            f"Error recovery: retry for issue #{issue_number} "
            f"(attempt {retry_count + 1}/{max_retries})"
        )
        return "retry"
    
    # Max retries exceeded - check if human intervention might help
    if len(errors) > 3 or any("human" in error.lower() for error in errors):
        logger.info(f"Error recovery: human intervention needed for issue #{issue_number}")
        return "human_intervention"
    
    # Default to failure
    logger.info(f"Error recovery: marking as failed for issue #{issue_number}")
    return "fail"


def task_completion_decision(state: IssueWorkflowState) -> Literal["next_task", "complete", "error"]:
    """
    Decide what to do after completing a task.
    
    Args:
        state: Current workflow state
    
    Returns:
        "next_task" - Move to next task in the list
        "complete" - All tasks completed
        "error" - Error in task completion
    """
    tasks = state.get("tasks", [])
    current_task = state.get("current_task")
    issue_number = state.get("issue_number", "unknown")
    
    if not tasks:
        logger.warning(f"No tasks defined for issue #{issue_number}")
        return "error"
    
    if not current_task:
        logger.warning(f"No current task for issue #{issue_number}")
        return "error"
    
    # Find current task index
    current_task_id = current_task.get("id")
    current_index = -1
    
    for i, task in enumerate(tasks):
        if task.get("id") == current_task_id:
            current_index = i
            break
    
    if current_index == -1:
        logger.error(f"Current task not found in task list for issue #{issue_number}")
        return "error"
    
    # Check if there are more tasks
    if current_index < len(tasks) - 1:
        # Move to next task
        next_task = tasks[current_index + 1]
        state["current_task"] = next_task
        state["current_iteration"] = 0  # Reset iteration for new task
        
        logger.info(
            f"Moving to next task for issue #{issue_number}: {next_task['id']}"
        )
        return "next_task"
    
    # All tasks completed
    logger.info(f"All tasks completed for issue #{issue_number}")
    return "complete"