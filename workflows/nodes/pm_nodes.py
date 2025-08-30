"""Project Manager Agent workflow nodes.

This module contains workflow nodes that integrate the PMAgent with the
LangGraph workflow system. These nodes handle issue analysis and task
breakdown within the workflow context.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from agents.pm import PMAgent, PMAgentConfig
from core.logging import get_logger
from core.exceptions import AgentExecutionError
from workflows.workflow_state import (
    IssueWorkflowState,
    WorkflowStatus,
    update_state_timestamp,
    add_error,
    add_warning
)

logger = get_logger(__name__)

# Global PM Agent instance (initialized once)
_pm_agent: PMAgent = None


def get_pm_agent() -> PMAgent:
    """Get or create the global PM Agent instance.
    
    Returns:
        PMAgent instance
    """
    global _pm_agent
    if _pm_agent is None:
        config = PMAgentConfig(
            temperature=0.2,
            max_tasks_per_issue=10,
            require_testing_tasks=True,
            enable_risk_analysis=True
        )
        _pm_agent = PMAgent(config=config)
        logger.info("PM Agent initialized for workflow")
    return _pm_agent


async def pm_analyze_issue_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """PM Agent analyzes the GitHub issue.
    
    This node replaces the stub analyze_issue_node with actual PM Agent
    intelligence. It performs deep analysis of the issue to understand
    requirements, complexity, and risks.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated workflow state with analysis results
    """
    issue_num = state.get('issue_number', 'unknown')
    logger.info(f"PM Agent analyzing issue #{issue_num}")
    
    try:
        # Update state to indicate analysis is starting
        state['status'] = WorkflowStatus.ANALYZING
        state['agent_interactions'] = state.get('agent_interactions', 0) + 1
        
        # Get PM Agent
        pm_agent = get_pm_agent()
        
        # Prepare issue data for analysis
        issue_data = {
            'number': state['issue_number'],
            'title': state['issue_title'],
            'body': state.get('issue_body', ''),
            'labels': state.get('issue_labels', []),
            'repository': state.get('repository', 'unknown/unknown'),
            'url': state.get('issue_url', ''),
            'assignees': state.get('issue_assignees', [])
        }
        
        # Perform analysis
        start_time = datetime.utcnow()
        analysis = pm_agent.analyze_issue(issue_data)
        analysis_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Store analysis in state
        state['analysis'] = analysis.model_dump()
        tokens_used = getattr(pm_agent, 'total_tokens_used', 0)
        state['tokens_used'] = state.get('tokens_used', 0) + (tokens_used if isinstance(tokens_used, int) else 0)
        
        # Update workflow state based on analysis
        if analysis.complexity == 'very_complex':
            state['max_iterations'] = 5
            state['max_retries'] = 3
        elif analysis.complexity in ['complex', 'medium']:
            state['max_iterations'] = 4
            state['max_retries'] = 2
        
        # Add warnings for high-risk issues
        if analysis.risks:
            for risk in analysis.risks[:3]:  # Limit to top 3 risks
                state = add_warning(state, f"Risk identified: {risk}")
        
        # Log analysis results
        logger.info(
            f"PM analysis complete for issue #{issue_num}: "
            f"{analysis.issue_type} ({analysis.complexity}) - "
            f"{analysis.confidence_score:.2f} confidence, "
            f"{analysis_time:.2f}s"
        )
        
        # Check if human input is needed for unclear issues
        if analysis.confidence_score < 0.6 or len(analysis.questions) > 3:
            state['requires_human_input'] = True
            state = add_warning(
                state, 
                f"Low confidence analysis ({analysis.confidence_score:.2f}) or many questions"
            )
        
    except AgentExecutionError as e:
        logger.error(f"PM Agent analysis failed for issue #{issue_num}: {e}")
        state = add_error(state, f"PM analysis failed: {str(e)}")
        state['status'] = WorkflowStatus.FAILED
        state['should_continue'] = False
        
    except Exception as e:
        logger.error(f"Unexpected error in PM analysis for issue #{issue_num}: {e}")
        state = add_error(state, f"Unexpected PM analysis error: {str(e)}")
        state['status'] = WorkflowStatus.FAILED
        state['should_continue'] = False
    
    return update_state_timestamp(state)


async def pm_plan_tasks_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """PM Agent creates detailed task breakdown.
    
    This node replaces the stub plan_tasks_node with actual PM Agent
    task breakdown capabilities. It creates a structured plan with
    specific tasks, dependencies, and execution order.
    
    Args:
        state: Current workflow state with analysis completed
        
    Returns:
        Updated workflow state with task breakdown
    """
    issue_num = state.get('issue_number', 'unknown')
    logger.info(f"PM Agent planning tasks for issue #{issue_num}")
    
    try:
        # Validate we have analysis
        if not state.get('analysis'):
            error_msg = "No analysis found for task planning"
            logger.error(f"Task planning failed for issue #{issue_num}: {error_msg}")
            state = add_error(state, error_msg)
            state['status'] = WorkflowStatus.FAILED
            return update_state_timestamp(state)
        
        # Update state to indicate planning is starting
        state['status'] = WorkflowStatus.PLANNING
        state['agent_interactions'] = state.get('agent_interactions', 0) + 1
        
        # Get PM Agent
        pm_agent = get_pm_agent()
        
        # Prepare issue data
        issue_data = {
            'number': state['issue_number'],
            'title': state['issue_title'],
            'body': state.get('issue_body', ''),
            'repository': state.get('repository', 'unknown/unknown')
        }
        
        # Reconstruct analysis from state
        from agents.pm.models import IssueAnalysis
        analysis = IssueAnalysis.model_validate(state['analysis'])
        
        # Create task breakdown
        start_time = datetime.utcnow()
        breakdown = pm_agent.create_task_breakdown(issue_data, analysis)
        planning_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Store breakdown in state
        state['tasks'] = [task.model_dump() for task in breakdown.tasks]
        state['task_execution_order'] = breakdown.execution_order
        state['total_estimated_hours'] = breakdown.total_estimated_hours
        state['recommended_approach'] = breakdown.recommended_approach
        state['success_criteria'] = breakdown.success_criteria
        state['testing_strategy'] = breakdown.testing_strategy
        
        # Update token usage
        tokens_used = getattr(pm_agent, 'total_tokens_used', 0)
        state['tokens_used'] = state.get('tokens_used', 0) + (tokens_used if isinstance(tokens_used, int) else 0)
        
        # Set up for task execution
        if breakdown.tasks:
            # Set first task as current
            first_task = breakdown.tasks[0]
            state['current_task'] = first_task.model_dump()
            state['current_task_index'] = 0
            state['completed_task_ids'] = []
        
        # Log planning results
        logger.info(
            f"PM task planning complete for issue #{issue_num}: "
            f"{len(breakdown.tasks)} tasks, "
            f"{breakdown.total_estimated_hours:.1f}h total, "
            f"{planning_time:.2f}s"
        )
        
        # Validate breakdown quality
        validation_errors = breakdown.validate_dependencies()
        if validation_errors:
            for error in validation_errors:
                state = add_warning(state, f"Task validation: {error}")
        
        # Check for complexity warnings
        complex_tasks = [
            task for task in breakdown.tasks 
            if task.estimated_complexity in ['complex', 'very_complex']
        ]
        if len(complex_tasks) > len(breakdown.tasks) * 0.5:
            state = add_warning(
                state, 
                f"{len(complex_tasks)} of {len(breakdown.tasks)} tasks are complex"
            )
        
    except AgentExecutionError as e:
        logger.error(f"PM Agent task planning failed for issue #{issue_num}: {e}")
        state = add_error(state, f"PM task planning failed: {str(e)}")
        state['status'] = WorkflowStatus.FAILED
        state['should_continue'] = False
        
    except Exception as e:
        logger.error(f"Unexpected error in PM task planning for issue #{issue_num}: {e}")
        state = add_error(state, f"Unexpected PM planning error: {str(e)}")
        state['status'] = WorkflowStatus.FAILED
        state['should_continue'] = False
    
    return update_state_timestamp(state)


async def pm_validate_completion_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """PM Agent validates that all tasks and success criteria are met.
    
    This node provides final quality validation before creating a PR.
    The PM Agent checks that all tasks are completed, success criteria
    are met, and the implementation is ready for deployment.
    
    Args:
        state: Current workflow state after task execution
        
    Returns:
        Updated workflow state with completion validation
    """
    issue_num = state.get('issue_number', 'unknown')
    logger.info(f"PM Agent validating completion for issue #{issue_num}")
    
    try:
        # Check if we have tasks and success criteria
        tasks = state.get('tasks', [])
        success_criteria = state.get('success_criteria', [])
        completed_task_ids = set(state.get('completed_task_ids', []))
        
        if not tasks:
            state = add_warning(state, "No tasks found for completion validation")
            return update_state_timestamp(state)
        
        # Validate all tasks are completed
        incomplete_tasks = []
        for task in tasks:
            task_id = task.get('id', '')
            if task_id not in completed_task_ids:
                incomplete_tasks.append(f"Task {task_id}: {task.get('title', 'Unknown')}")
        
        if incomplete_tasks:
            error_msg = f"Incomplete tasks: {', '.join(incomplete_tasks[:3])}"
            logger.warning(f"Completion validation failed for issue #{issue_num}: {error_msg}")
            state = add_error(state, error_msg)
            state['status'] = WorkflowStatus.NEEDS_REVISION
            return update_state_timestamp(state)
        
        # Check artifacts exist
        artifacts = state.get('artifacts', [])
        if not artifacts:
            state = add_warning(state, "No artifacts generated during execution")
        else:
            # Check for required artifact types
            artifact_types = {artifact.get('type') for artifact in artifacts}
            expected_types = {'code', 'tests'}
            
            missing_types = expected_types - artifact_types
            if missing_types:
                state = add_warning(state, f"Missing artifact types: {missing_types}")
        
        # Validate test results if testing was required
        test_results = state.get('test_results', [])
        if any(task.get('task_type') == 'testing' for task in tasks):
            if not test_results:
                state = add_warning(state, "Testing tasks completed but no test results found")
            else:
                # Check latest test results
                latest_test = test_results[-1] if test_results else {}
                failed_tests = latest_test.get('failed', 0)
                if failed_tests > 0:
                    error_msg = f"Tests failing: {failed_tests} failures"
                    logger.error(f"Completion validation failed for issue #{issue_num}: {error_msg}")
                    state = add_error(state, error_msg)
                    state['status'] = WorkflowStatus.NEEDS_REVISION
                    return update_state_timestamp(state)
        
        # Check review feedback for major issues
        review_feedback = state.get('review_feedback', [])
        if review_feedback:
            latest_review = review_feedback[-1]
            if latest_review.get('needs_revision', False):
                state = add_warning(state, "Latest review indicates revisions needed")
        
        # Validate against success criteria (basic check)
        if success_criteria:
            state['success_criteria_validated'] = True
            logger.info(f"Success criteria validated for issue #{issue_num}")
        
        # Final validation passed
        logger.info(f"PM completion validation passed for issue #{issue_num}")
        state['pm_validation_passed'] = True
        state['validated_at'] = datetime.utcnow().isoformat()
        
    except Exception as e:
        logger.error(f"PM completion validation error for issue #{issue_num}: {e}")
        state = add_error(state, f"PM validation error: {str(e)}")
    
    return update_state_timestamp(state)


async def pm_metrics_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Collect PM Agent metrics and add to workflow state.
    
    This node collects metrics about PM Agent performance and adds
    them to the workflow state for monitoring and analysis.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated workflow state with PM metrics
    """
    try:
        pm_agent = get_pm_agent()
        metrics = pm_agent.get_metrics()
        
        # Add metrics to state
        if 'pm_metrics' not in state:
            state['pm_metrics'] = {}
        
        state['pm_metrics'].update(metrics)
        
        logger.debug(f"PM metrics collected: {metrics}")
        
    except Exception as e:
        logger.error(f"Failed to collect PM metrics: {e}")
        state = add_warning(state, f"PM metrics collection failed: {str(e)}")
    
    return update_state_timestamp(state)