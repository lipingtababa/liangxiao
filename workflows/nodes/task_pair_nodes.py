"""Task Pair workflow nodes.

This module contains workflow nodes that use the revolutionary TaskPair system
to execute tasks through pair programming patterns between Tasker and Navigator
agents.

This is THE key innovation that prevents disasters like PR #23 by implementing
proper review cycles before accepting work.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from core.logging import get_logger
from workflows.workflow_state import (
    IssueWorkflowState,
    WorkflowStatus,
    update_state_timestamp,
    add_error,
    add_warning
)

# Import TaskPair system
from agents.pairs.task_pair import TaskPair, create_task_pair
from agents.navigator.agent import NavigatorAgent
from agents.analyst.agent import AnalystAgent  
from agents.tester.agent import TesterAgent
from agents.developer.agent import DeveloperAgent

logger = get_logger(__name__)


async def execute_task_with_pair_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """
    Execute current task using TaskPair system with pair programming.
    
    This is the revolutionary replacement for execute_task_node that implements
    the pair programming pattern to prevent disasters like PR #23.
    
    The system works as:
    1. Determine appropriate Tasker agent (Developer/Analyst/Tester) 
    2. Create specialized Navigator agent for review
    3. Create TaskPair to orchestrate collaboration
    4. Execute with iteration cycles until approved or max iterations
    5. Update state with comprehensive results
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated workflow state with task pair results
    """
    current_task = state.get("current_task")
    if not current_task:
        logger.warning(f"No current task for issue #{state['issue_number']}")
        state = add_warning(state, "No current task to execute")
        state["should_continue"] = False
        return update_state_timestamp(state)
    
    task_id = current_task.get('id', 'unknown')
    task_type = current_task.get('task_type', current_task.get('type', 'implementation'))
    assigned_agent = current_task.get('assigned_agent', 'developer')
    
    logger.info(
        f"🚀 Executing task {task_id} with TaskPair: "
        f"type={task_type}, agent={assigned_agent}"
    )
    
    state["status"] = WorkflowStatus.DEVELOPING
    state["current_iteration"] = state.get("current_iteration", 0) + 1
    state["agent_interactions"] = state.get("agent_interactions", 0) + 1
    
    try:
        # Step 1: Create appropriate Tasker agent
        tasker_agent = await _create_tasker_agent(assigned_agent, task_type, state)
        if not tasker_agent:
            error_msg = f"Failed to create tasker agent: {assigned_agent}"
            logger.error(error_msg)
            state = add_error(state, error_msg)
            state["should_continue"] = False
            return update_state_timestamp(state)
        
        # Step 2: Determine Navigator specialty based on task type
        navigator_specialty = _determine_navigator_specialty(task_type, assigned_agent)
        
        logger.info(f"Creating TaskPair: {assigned_agent} + Navigator[{navigator_specialty}]")
        
        # Step 3: Create TaskPair with appropriate configuration
        max_iterations = state.get("max_iterations", 3)
        task_pair = create_task_pair(
            tasker_agent=tasker_agent,
            navigator_specialty=navigator_specialty,
            max_iterations=max_iterations,
            require_approval=True  # Always require approval for quality
        )
        
        # Step 4: Prepare execution context
        context = _prepare_execution_context(state)
        
        # Step 5: Execute task with pair programming
        logger.info(f"Starting TaskPair execution for {task_id}")
        pair_result = await task_pair.execute_task(current_task, context)
        
        # Step 6: Process results and update state
        state = _process_pair_result(state, pair_result, task_pair)
        
        # Step 7: Log execution summary
        logger.info(f"TaskPair execution complete: {pair_result.get_summary()}")
        
        # Step 8: Determine next workflow step
        if pair_result.success:
            logger.info(f"✅ Task {task_id} completed successfully with TaskPair")
            state["next_step"] = "continue"
        else:
            logger.error(f"❌ Task {task_id} failed with TaskPair: {pair_result.failure_reason}")
            state = add_error(state, f"TaskPair execution failed: {pair_result.failure_reason}")
            state["next_step"] = "error"
        
    except Exception as e:
        logger.error(f"💥 TaskPair execution failed for {task_id}: {e}", exc_info=True)
        state = add_error(state, f"TaskPair system error: {str(e)}")
        state["next_step"] = "error"
    
    return update_state_timestamp(state)


async def _create_tasker_agent(assigned_agent: str, task_type: str, state: IssueWorkflowState) -> Any:
    """
    Create appropriate Tasker agent based on assignment and task type.
    
    Args:
        assigned_agent: The assigned agent type (developer/analyst/tester)
        task_type: The type of task to execute
        state: Current workflow state for context
        
    Returns:
        Configured agent instance or None if creation failed
    """
    try:
        github_service = state.get("github_service")  # If available
        
        if assigned_agent == "developer":
            return DeveloperAgent(
                model="gpt-4-turbo-preview",
                temperature=0.2,
                github_service=github_service
            )
        
        elif assigned_agent == "analyst":
            return AnalystAgent(
                github_service=github_service,
                max_files_to_analyze=15
            )
        
        elif assigned_agent == "tester":
            return TesterAgent(
                model="gpt-4-turbo-preview",
                temperature=0.2
            )
        
        else:
            logger.error(f"Unknown assigned agent type: {assigned_agent}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to create tasker agent {assigned_agent}: {e}")
        return None


def _determine_navigator_specialty(task_type: str, assigned_agent: str) -> str:
    """
    Determine appropriate Navigator specialty based on task type and assigned agent.
    
    Args:
        task_type: The type of task being executed
        assigned_agent: The assigned agent type
        
    Returns:
        Navigator specialty string
    """
    # Map task types and agents to Navigator specialties
    
    if task_type in ["analysis", "investigation", "requirements"] or assigned_agent == "analyst":
        return "requirements_review"
    
    elif task_type in ["testing", "test"] or assigned_agent == "tester":
        return "test_review"
    
    else:  # implementation, bug_fix, feature, etc. or developer
        return "code_review"


def _prepare_execution_context(state: IssueWorkflowState) -> Dict[str, Any]:
    """
    Prepare execution context for TaskPair from workflow state.
    
    Args:
        state: Current workflow state
        
    Returns:
        Context dictionary for TaskPair execution
    """
    context = {
        # Issue information
        "issue": {
            "number": state.get("issue_number"),
            "title": state.get("issue_title"),
            "body": state.get("issue_body"),
            "labels": state.get("issue_labels", [])
        },
        
        # Repository context
        "repository": state.get("repository"),
        
        # Previous work context
        "completed_tasks": state.get("completed_tasks", []),
        "task_results": state.get("task_results", []),
        "artifacts": state.get("artifacts", []),
        
        # Analysis context (if available)
        "analysis": state.get("analysis"),
        
        # Iteration management
        "max_iterations": state.get("max_iterations", 3),
        "current_iteration": state.get("current_iteration", 1),
        
        # GitHub service (if configured)
        "github_service": state.get("github_service")
    }
    
    return context


def _process_pair_result(
    state: IssueWorkflowState, 
    pair_result: Any,  # TaskPairResult
    task_pair: TaskPair
) -> IssueWorkflowState:
    """
    Process TaskPair execution result and update workflow state.
    
    Args:
        state: Current workflow state
        pair_result: TaskPairResult from pair execution
        task_pair: The TaskPair that executed the task
        
    Returns:
        Updated workflow state
    """
    current_task = state.get("current_task")
    task_id = current_task.get('id', 'unknown') if current_task else 'unknown'
    
    # Initialize collections if needed
    if "task_results" not in state:
        state["task_results"] = []
    if "artifacts" not in state:
        state["artifacts"] = []
    if "pair_execution_history" not in state:
        state["pair_execution_history"] = []
    
    # Store comprehensive TaskPair result
    pair_execution_record = {
        "task_id": task_id,
        "tasker_type": task_pair.tasker_type,
        "navigator_specialty": task_pair.navigator_specialty,
        "success": pair_result.success,
        "iterations": len(pair_result.iterations),
        "total_duration": pair_result.total_duration_seconds,
        "final_quality_score": pair_result.final_quality_score,
        "disaster_prevention_score": pair_result.disaster_prevention_score,
        "max_iterations_reached": pair_result.max_iterations_reached,
        "failure_reason": pair_result.failure_reason,
        "executed_at": datetime.utcnow().isoformat()
    }
    
    state["pair_execution_history"].append(pair_execution_record)
    
    # Store task result in existing format for compatibility
    task_result = {
        "task_id": task_id,
        "success": pair_result.success,
        "pair_programming": True,  # Mark as using pair programming
        "iterations": len(pair_result.iterations),
        "final_quality_score": pair_result.final_quality_score,
        "execution_summary": pair_result.get_summary(),
        "completed_at": datetime.utcnow().isoformat()
    }
    
    state["task_results"].append(task_result)
    
    # Add artifacts if task succeeded
    if pair_result.success and pair_result.final_output:
        final_artifacts = pair_result.final_output.get("artifacts", [])
        state["artifacts"].extend(final_artifacts)
        
        logger.info(f"Added {len(final_artifacts)} artifacts from TaskPair execution")
    
    # Update task status
    if current_task:
        current_task["status"] = "completed" if pair_result.success else "failed"
        current_task["completed_at"] = datetime.utcnow().isoformat()
        current_task["pair_execution"] = True
        current_task["quality_score"] = pair_result.final_quality_score
        current_task["iterations"] = len(pair_result.iterations)
    
    # Track comprehensive metrics
    state["tokens_used"] = state.get("tokens_used", 0) + pair_result.tokens_used
    state["total_pair_executions"] = state.get("total_pair_executions", 0) + 1
    
    # Store detailed iteration history for analysis
    state["detailed_iterations"] = state.get("detailed_iterations", [])
    for iteration in pair_result.iterations:
        iteration_record = {
            "task_id": task_id,
            "iteration_number": iteration.iteration_number,
            "duration_seconds": iteration.duration_seconds,
            "navigator_decision": iteration.navigator_feedback.decision.value,
            "quality_score": iteration.navigator_feedback.quality_score,
            "issues_count": len(iteration.navigator_feedback.issues),
            "success": iteration.success,
            "error": iteration.error
        }
        state["detailed_iterations"].append(iteration_record)
    
    # Add warnings if quality concerns exist
    if pair_result.max_iterations_reached:
        state = add_warning(
            state, 
            f"Task {task_id} reached max iterations without full approval"
        )
    
    if pair_result.final_quality_score < 7.0:
        state = add_warning(
            state,
            f"Task {task_id} has below-average quality score: {pair_result.final_quality_score:.1f}/10"
        )
    
    # Add success indicators for high-quality completions
    if pair_result.success and pair_result.final_quality_score >= 8.0:
        logger.info(f"🌟 High-quality completion for task {task_id}: {pair_result.final_quality_score:.1f}/10")
    
    if pair_result.disaster_prevention_score >= 80.0:
        logger.info(f"🛡️ Excellent disaster prevention score for task {task_id}: {pair_result.disaster_prevention_score:.1f}/100")
    
    return state


# Integration functions to support different workflow patterns
async def analyze_issue_with_pair_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """
    Analyze issue using Analyst-Navigator pair.
    
    This is a specialized version of execute_task_with_pair_node for analysis tasks.
    """
    # Create a synthetic analysis task
    analysis_task = {
        "id": f"analysis-{state['issue_number']}",
        "description": f"Analyze issue #{state['issue_number']}: {state['issue_title']}",
        "task_type": "analysis",
        "assigned_agent": "analyst",
        "acceptance_criteria": [
            "Root cause identified",
            "Requirements clearly understood", 
            "Solution approach documented",
            "Risk assessment completed"
        ]
    }
    
    # Set as current task and execute
    original_task = state.get("current_task")
    state["current_task"] = analysis_task
    
    try:
        state = await execute_task_with_pair_node(state)
        
        # Extract analysis results for compatibility
        if state.get("task_results"):
            latest_result = state["task_results"][-1]
            if latest_result.get("success"):
                # Create analysis summary for workflow compatibility
                state["analysis"] = {
                    "issue_type": "analyzed_with_pair_programming",
                    "summary": "Issue analyzed using Analyst-Navigator pair",
                    "pair_execution": True,
                    "quality_score": latest_result.get("final_quality_score", 7.0),
                    "analyzed_at": datetime.utcnow().isoformat()
                }
        
    finally:
        # Restore original task
        state["current_task"] = original_task
    
    return state


async def test_with_pair_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """
    Test solution using Tester-Navigator pair.
    
    This is a specialized version for testing tasks.
    """
    current_task = state.get("current_task")
    if not current_task:
        logger.warning("No current task for testing")
        return state
    
    # Create a testing task based on current task
    test_task = {
        "id": f"test-{current_task.get('id', 'unknown')}",
        "description": f"Create comprehensive tests for: {current_task.get('description', 'current task')}",
        "task_type": "testing",
        "assigned_agent": "tester",
        "acceptance_criteria": [
            "Unit tests created and passing",
            "Integration tests added if needed", 
            "Test coverage meets project standards",
            "Edge cases and error conditions tested"
        ]
    }
    
    # Temporarily replace current task
    original_task = state.get("current_task")
    state["current_task"] = test_task
    
    try:
        state = await execute_task_with_pair_node(state)
        
        # Process test results for workflow compatibility
        if state.get("task_results"):
            latest_result = state["task_results"][-1]
            if latest_result.get("success"):
                # Add to test results for compatibility
                if "test_results" not in state:
                    state["test_results"] = []
                
                test_result = {
                    "test_suite": "pair_generated_tests",
                    "success": True,
                    "pair_execution": True,
                    "quality_score": latest_result.get("final_quality_score", 7.0),
                    "tested_at": datetime.utcnow().isoformat()
                }
                state["test_results"].append(test_result)
        
    finally:
        # Restore original task
        state["current_task"] = original_task
    
    return state


def get_pair_execution_metrics(state: IssueWorkflowState) -> Dict[str, Any]:
    """
    Get comprehensive metrics about TaskPair executions in this workflow.
    
    Args:
        state: Workflow state containing pair execution history
        
    Returns:
        Dictionary of metrics and statistics
    """
    history = state.get("pair_execution_history", [])
    iterations = state.get("detailed_iterations", [])
    
    if not history:
        return {"message": "No TaskPair executions in this workflow"}
    
    # Calculate summary statistics
    total_executions = len(history)
    successful_executions = sum(1 for exec in history if exec["success"])
    total_iterations = sum(exec["iterations"] for exec in history)
    total_duration = sum(exec["total_duration"] for exec in history)
    
    avg_quality = sum(exec["final_quality_score"] for exec in history) / total_executions
    avg_disaster_prevention = sum(exec["disaster_prevention_score"] for exec in history) / total_executions
    
    # Task type breakdown
    tasker_types = {}
    navigator_specialties = {}
    
    for exec in history:
        tasker = exec["tasker_type"]
        navigator = exec["navigator_specialty"]
        
        tasker_types[tasker] = tasker_types.get(tasker, 0) + 1
        navigator_specialties[navigator] = navigator_specialties.get(navigator, 0) + 1
    
    return {
        "total_executions": total_executions,
        "success_rate": successful_executions / total_executions,
        "total_iterations": total_iterations,
        "avg_iterations_per_task": total_iterations / total_executions,
        "total_duration_seconds": total_duration,
        "avg_duration_per_task": total_duration / total_executions,
        "avg_quality_score": avg_quality,
        "avg_disaster_prevention_score": avg_disaster_prevention,
        "tasker_type_distribution": tasker_types,
        "navigator_specialty_distribution": navigator_specialties,
        "max_iterations_reached_count": sum(1 for exec in history if exec["max_iterations_reached"])
    }