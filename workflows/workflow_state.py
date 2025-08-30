"""Workflow state definitions for issue processing."""

from typing import TypedDict, List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class WorkflowStatus(str, Enum):
    """Enhanced workflow status for complete end-to-end processing."""
    RECEIVED = "RECEIVED"                     # Issue just received
    PM_ANALYZING = "PM_ANALYZING"             # PM analyzing issue
    PLANNING = "PLANNING"                     # PM creating task plan
    TASKS_QUEUED = "TASKS_QUEUED"             # Tasks ready for execution
    ANALYZING = "ANALYZING"                   # Analyst working
    DEVELOPING = "DEVELOPING"                 # Developer working
    TESTING = "TESTING"                      # Tester working
    REVIEWING = "REVIEWING"                   # Navigator reviewing
    ITERATING = "ITERATING"                  # Agent responding to feedback
    INTEGRATING = "INTEGRATING"               # Combining all work
    PR_CREATING = "PR_CREATING"               # Creating pull request
    COMPLETED = "COMPLETED"                   # All done successfully
    FAILED = "FAILED"                        # Workflow failed
    BLOCKED = "BLOCKED"                       # Waiting for external input


class IssueWorkflowState(TypedDict, total=False):
    """Complete state structure for end-to-end issue processing workflow.
    
    Using total=False to allow partial state updates in nodes.
    """
    # Issue Information
    issue_number: int
    issue_title: str
    issue_body: str
    issue_url: str
    repository: str
    issue_labels: List[str]
    issue_assignees: List[str]
    
    # Workspace Information
    workspace_path: Optional[str]  # workspaces/repo_name/issue_id/
    repo_path: Optional[str]       # workspaces/repo_name/issue_id/repo_name/
    sct_path: Optional[str]        # workspaces/repo_name/issue_id/.SyntheticCodingTeam/
    issue_id: Optional[str]        # Normalized issue ID (GitHub number or Jira ticket)
    
    # Workflow Control
    status: WorkflowStatus
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    should_continue: bool
    
    # PM Analysis Results
    issue_analysis: Optional[Dict[str, Any]]  # PM's issue analysis
    task_breakdown: List[Dict[str, Any]]      # List of tasks from PM
    execution_plan: List[str]                 # Task execution order
    
    # Task Execution State
    current_task_index: int                   # Which task we're on
    current_task: Optional[Dict[str, Any]]    # Current task details
    completed_tasks: List[str]                # IDs of completed tasks
    failed_tasks: List[str]                   # IDs of failed tasks
    task_results: List[Dict[str, Any]]        # Results from each task
    
    # Artifacts and Results by Type
    analysis_artifacts: List[Dict[str, Any]]  # Requirements, docs
    code_artifacts: List[Dict[str, Any]]      # Generated code
    test_artifacts: List[Dict[str, Any]]      # Generated tests
    all_artifacts: List[Dict[str, Any]]       # Combined artifacts
    
    # TaskPair Execution History
    pair_execution_history: List[Dict[str, Any]]  # Detailed pair execution records
    detailed_iterations: List[Dict[str, Any]]     # Per-iteration details
    total_pair_executions: int                    # Count of pair executions
    
    # Progress Tracking
    progress_percentage: float                # 0.0 to 1.0
    current_step_description: str            # Human readable current step
    
    # Error Handling
    errors: List[str]  # Error messages
    warnings: List[str]  # Warning messages
    retry_count: int  # Number of retries attempted
    max_retries: int  # Maximum retries allowed
    
    # Final Results
    pr_number: Optional[int]  # Created PR number
    pr_url: Optional[str]  # PR URL
    branch_name: Optional[str]  # Working branch name
    success_summary: Optional[str]  # What was accomplished
    
    # Control Flow
    next_step: Optional[str]  # Directive for next node
    requires_human_input: bool  # Whether human intervention is needed
    
    # Metrics and Observability
    tokens_used: int  # Total LLM tokens consumed
    execution_time_seconds: float  # Total execution time
    agent_interactions: int  # Number of agent calls
    max_iterations: int  # Maximum allowed iterations per task
    current_iteration: int  # Current iteration count
    
    # Legacy compatibility fields
    analysis: Optional[Dict[str, Any]]  # For backwards compatibility
    tasks: List[Dict[str, Any]]  # For backwards compatibility
    artifacts: List[Dict[str, Any]]  # For backwards compatibility
    test_results: List[Dict[str, Any]]  # For backwards compatibility
    review_feedback: List[Dict[str, Any]]  # For backwards compatibility


def create_initial_state(
    issue_number: int,
    issue_title: str,
    issue_body: str,
    issue_url: str,
    repository: str,
    issue_labels: Optional[List[str]] = None,
    issue_assignees: Optional[List[str]] = None
) -> IssueWorkflowState:
    """Create initial workflow state from issue data for complete end-to-end processing."""
    current_time = datetime.utcnow()
    
    return IssueWorkflowState(
        # Issue Information
        issue_number=issue_number,
        issue_title=issue_title,
        issue_body=issue_body,
        issue_url=issue_url,
        repository=repository,
        issue_labels=issue_labels or [],
        issue_assignees=issue_assignees or [],
        
        # Workflow Control
        status=WorkflowStatus.RECEIVED,
        started_at=current_time,
        updated_at=current_time,
        completed_at=None,
        should_continue=True,
        
        # PM Analysis (initially empty)
        issue_analysis=None,
        task_breakdown=[],
        execution_plan=[],
        
        # Task Execution State
        current_task_index=0,
        current_task=None,
        completed_tasks=[],
        failed_tasks=[],
        task_results=[],
        
        # Artifacts by Type
        analysis_artifacts=[],
        code_artifacts=[],
        test_artifacts=[],
        all_artifacts=[],
        
        # TaskPair History
        pair_execution_history=[],
        detailed_iterations=[],
        total_pair_executions=0,
        
        # Progress Tracking
        progress_percentage=0.0,
        current_step_description="Issue received, waiting to start processing",
        
        # Error Handling
        errors=[],
        warnings=[],
        retry_count=0,
        max_retries=2,
        
        # Results
        pr_number=None,
        pr_url=None,
        branch_name=None,
        success_summary=None,
        
        # Control Flow
        next_step=None,
        requires_human_input=False,
        
        # Metrics
        tokens_used=0,
        execution_time_seconds=0.0,
        agent_interactions=0,
        max_iterations=3,
        current_iteration=0,
        
        # Legacy compatibility
        analysis=None,
        tasks=[],
        artifacts=[],
        test_results=[],
        review_feedback=[]
    )


def update_state_timestamp(state: IssueWorkflowState) -> IssueWorkflowState:
    """Update the state timestamp."""
    state["updated_at"] = datetime.utcnow()
    return state


def add_error(state: IssueWorkflowState, error_message: str) -> IssueWorkflowState:
    """Add an error message to the state."""
    if "errors" not in state:
        state["errors"] = []
    state["errors"].append(error_message)
    state["updated_at"] = datetime.utcnow()
    return state


def add_warning(state: IssueWorkflowState, warning_message: str) -> IssueWorkflowState:
    """Add a warning message to the state."""
    if "warnings" not in state:
        state["warnings"] = []
    state["warnings"].append(warning_message)
    state["updated_at"] = datetime.utcnow()
    return state


def is_final_state(status: WorkflowStatus) -> bool:
    """Check if the workflow status is a final state."""
    return status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]