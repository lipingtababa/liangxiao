"""Main issue processing workflow using LangGraph."""

import os
from typing import Optional

from langgraph.graph import StateGraph, END
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    # Fallback for older LangGraph versions
    from langgraph.checkpoint.memory import MemorySaver as SqliteSaver

from core.logging import get_logger
from workflows.workflow_state import IssueWorkflowState, WorkflowStatus
from workflows.nodes import (
    receive_issue_node,
    analyze_issue_node,
    plan_tasks_node,
    execute_task_node,
    review_task_node,
    test_solution_node,
    create_pr_node,
    handle_error_node,
    review_decision,
    should_continue_decision,
    error_recovery_decision
)

logger = get_logger(__name__)


def create_issue_workflow(
    checkpoint_db_path: str = "data/workflows.db"
) -> StateGraph:
    """
    Create the main issue processing workflow.
    
    Args:
        checkpoint_db_path: Path to SQLite database for checkpointing
    
    Returns:
        Compiled LangGraph workflow with checkpointing
    """
    logger.info("Creating issue processing workflow")
    
    # Initialize workflow with state class
    workflow = StateGraph(IssueWorkflowState)
    
    # Add all nodes
    workflow.add_node("receive_issue", receive_issue_node)
    workflow.add_node("analyze_issue", analyze_issue_node)
    workflow.add_node("plan_tasks", plan_tasks_node)
    workflow.add_node("execute_task", execute_task_node)
    workflow.add_node("review_task", review_task_node)
    workflow.add_node("test_solution", test_solution_node)
    workflow.add_node("create_pr", create_pr_node)
    workflow.add_node("handle_error", handle_error_node)
    
    # Set entry point
    workflow.set_entry_point("receive_issue")
    
    # Add linear edges for main flow
    workflow.add_edge("receive_issue", "analyze_issue")
    workflow.add_edge("analyze_issue", "plan_tasks")
    workflow.add_edge("plan_tasks", "execute_task")
    workflow.add_edge("execute_task", "review_task")
    
    # Add conditional edge for review decision
    workflow.add_conditional_edges(
        "review_task",
        review_decision,
        {
            "iterate": "execute_task",      # Need more work on current task
            "continue": "test_solution",    # Move to testing
            "error": "handle_error"         # Something went wrong
        }
    )
    
    # Add edges from testing
    workflow.add_conditional_edges(
        "test_solution",
        lambda state: "create_pr" if state.get("next_step") == "continue" else "handle_error",
        {
            "create_pr": "create_pr",
            "handle_error": "handle_error"
        }
    )
    
    # Terminal nodes
    workflow.add_edge("create_pr", END)
    workflow.add_edge("handle_error", END)
    
    # Set up checkpointing
    logger.info(f"Setting up checkpointing with database: {checkpoint_db_path}")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(checkpoint_db_path), exist_ok=True)
    
    # Create checkpointer (SQLite if available, otherwise memory)
    try:
        checkpointer = SqliteSaver.from_conn_string(checkpoint_db_path)
    except AttributeError:
        # Fallback to memory checkpointer for older LangGraph versions
        checkpointer = SqliteSaver()
    
    # Compile workflow with checkpointing
    compiled_workflow = workflow.compile(checkpointer=checkpointer)
    
    logger.info("Issue processing workflow created successfully")
    return compiled_workflow


def create_simple_workflow() -> StateGraph:
    """
    Create a simplified workflow without checkpointing for testing.
    
    Returns:
        Compiled LangGraph workflow without checkpointing
    """
    logger.info("Creating simple workflow (no checkpointing)")
    
    workflow = StateGraph(IssueWorkflowState)
    
    # Add minimal nodes for testing
    workflow.add_node("receive_issue", receive_issue_node)
    workflow.add_node("analyze_issue", analyze_issue_node)
    workflow.add_node("create_pr", create_pr_node)
    workflow.add_node("handle_error", handle_error_node)
    
    # Simple linear flow
    workflow.set_entry_point("receive_issue")
    workflow.add_edge("receive_issue", "analyze_issue")
    workflow.add_edge("analyze_issue", "create_pr")
    workflow.add_edge("handle_error", END)
    workflow.add_edge("create_pr", END)
    
    # Compile without checkpointing
    return workflow.compile()


def get_workflow_config(thread_id: str) -> dict:
    """
    Get configuration for workflow execution.
    
    Args:
        thread_id: Unique identifier for workflow thread
    
    Returns:
        Configuration dict for LangGraph
    """
    return {
        "configurable": {
            "thread_id": thread_id
        }
    }


async def get_workflow_history(
    workflow: StateGraph,
    thread_id: str,
    limit: Optional[int] = None
) -> list:
    """
    Get execution history for a workflow.
    
    Args:
        workflow: Compiled workflow instance
        thread_id: Workflow thread ID
        limit: Maximum number of history items to return
    
    Returns:
        List of workflow execution states
    """
    try:
        config = get_workflow_config(thread_id)
        history = []
        
        # Get state history from checkpointer
        async for state in workflow.aget_state_history(config):
            history.append({
                "timestamp": state.created_at,
                "node": state.metadata.get("source", "unknown"),
                "status": state.values.get("status", "unknown"),
                "values": state.values
            })
            
            if limit and len(history) >= limit:
                break
        
        return history
    
    except Exception as e:
        logger.error(f"Failed to get workflow history for {thread_id}: {e}")
        return []


def format_workflow_summary(state: IssueWorkflowState) -> dict:
    """
    Create a summary of workflow execution.
    
    Args:
        state: Current workflow state
    
    Returns:
        Summary dictionary with key metrics
    """
    return {
        "issue_number": state.get("issue_number"),
        "status": state.get("status"),
        "started_at": state.get("started_at"),
        "updated_at": state.get("updated_at"),
        "completed_at": state.get("completed_at"),
        "iterations": state.get("current_iteration", 0),
        "tokens_used": state.get("tokens_used", 0),
        "agent_interactions": state.get("agent_interactions", 0),
        "artifacts_generated": len(state.get("artifacts", [])),
        "errors": len(state.get("errors", [])),
        "warnings": len(state.get("warnings", [])),
        "pr_number": state.get("pr_number"),
        "pr_url": state.get("pr_url")
    }