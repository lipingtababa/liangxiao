"""Workflow orchestrator for managing issue processing workflows."""

import asyncio
from typing import Optional, Dict, List
from datetime import datetime

from core.logging import get_logger, set_request_context, LogContext
from models.github import IssueEvent
from workflows.issue_workflow import (
    create_issue_workflow,
    get_workflow_config,
    format_workflow_summary
)
from workflows.workflow_state import (
    IssueWorkflowState,
    create_initial_state,
    WorkflowStatus
)

logger = get_logger(__name__)


class WorkflowOrchestrator:
    """
    Orchestrates issue processing workflows using LangGraph.
    
    Manages workflow lifecycle, state persistence, and monitoring.
    """
    
    def __init__(self, checkpoint_db_path: str = "data/workflows.db"):
        """
        Initialize the orchestrator.
        
        Args:
            checkpoint_db_path: Path to SQLite database for workflow checkpointing
        """
        self.checkpoint_db_path = checkpoint_db_path
        self.workflow = create_issue_workflow(checkpoint_db_path)
        self.active_workflows: Dict[str, str] = {}  # workflow_id -> status
        self.workflow_metadata: Dict[str, dict] = {}  # workflow_id -> metadata
        self.workflow_start_times: Dict[str, datetime] = {}  # Track start times
        
        logger.info("="*60)
        logger.info("Workflow Orchestrator Initialization")
        logger.info(f"Checkpoint DB: {checkpoint_db_path}")
        logger.info(f"Workflow engine: LangGraph")
        logger.info("="*60)
    
    def _generate_workflow_id(self, issue_event: IssueEvent) -> str:
        """Generate unique workflow ID for an issue."""
        return f"issue-{issue_event.repository.full_name.replace('/', '-')}-{issue_event.issue.number}"
    
    async def start_workflow(
        self,
        issue_event: IssueEvent,
        force_restart: bool = False
    ) -> str:
        """
        Start a new workflow for an issue with comprehensive logging.
        
        Args:
            issue_event: GitHub issue event that triggered the workflow
            force_restart: Whether to restart if workflow already exists
        
        Returns:
            Workflow ID for tracking
        
        Raises:
            ValueError: If workflow already exists and force_restart is False
        """
        workflow_id = self._generate_workflow_id(issue_event)
        
        # Set context for this workflow
        with LogContext(
            workflow_id=workflow_id,
            issue_number=issue_event.issue.number,
            repository=issue_event.repository.full_name
        ):
            logger.info("Starting new workflow")
            logger.debug(f"Workflow ID: {workflow_id}")
            logger.debug(f"Force restart: {force_restart}")
        
            # Check if workflow already exists
            if workflow_id in self.active_workflows and not force_restart:
                current_status = self.active_workflows[workflow_id]
                logger.warning(f"Workflow already exists with status: {current_status}")
                logger.debug(f"Existing workflow metadata: {self.workflow_metadata.get(workflow_id, {})}")
                raise ValueError(f"Workflow already exists: {workflow_id}")
        
            logger.info(f"Initializing workflow for issue #{issue_event.issue.number}")
            logger.debug(
                f"Issue details: title='{issue_event.issue.title[:50]}', "
                f"labels={[l.name for l in issue_event.issue.labels]}, "
                f"assignees={[a.login for a in issue_event.issue.assignees]}"
            )
        
            # Create initial state
            logger.debug("Creating initial workflow state...")
            initial_state = create_initial_state(
                issue_number=issue_event.issue.number,
                issue_title=issue_event.issue.title,
                issue_body=issue_event.issue.body or "",
                issue_url=issue_event.issue.html_url,
                repository=issue_event.repository.full_name,
                issue_labels=[label.name for label in issue_event.issue.labels],
                issue_assignees=[assignee.login for assignee in issue_event.issue.assignees]
            )
            logger.debug("✓ Initial state created")
        
            # Store workflow metadata
            created_at = datetime.utcnow()
            self.workflow_metadata[workflow_id] = {
                "created_at": created_at,
                "issue_event": issue_event.model_dump(),
                "repository": issue_event.repository.full_name,
                "issue_number": issue_event.issue.number,
                "issue_title": issue_event.issue.title
            }
            self.workflow_start_times[workflow_id] = created_at
            logger.debug(f"Workflow metadata stored at {created_at.isoformat()}")
        
            # Mark as starting
            self.active_workflows[workflow_id] = "starting"
            logger.debug("Workflow marked as 'starting'")
            
            # Start workflow asynchronously
            task = asyncio.create_task(
                self._run_workflow(workflow_id, initial_state)
            )
            logger.info(f"✓ Workflow started successfully (task_id={id(task)})")
            logger.debug(f"Background task created for workflow execution")
            
            return workflow_id
    
    async def _run_workflow(self, workflow_id: str, initial_state: IssueWorkflowState):
        """
        Run workflow to completion with detailed logging.
        
        Args:
            workflow_id: Unique workflow identifier
            initial_state: Initial workflow state
        """
        with LogContext(workflow_id=workflow_id, phase="execution"):
            logger.info(f"Beginning workflow execution: {workflow_id}")
            
            config = get_workflow_config(workflow_id)
            logger.debug("Workflow configuration loaded")
        
            try:
                start_time = datetime.utcnow()
                self.active_workflows[workflow_id] = "running"
                logger.info("Workflow status: running")
                logger.debug(f"Execution started at {start_time.isoformat()}")
            
                # Execute workflow
                logger.info("Invoking LangGraph workflow engine...")
                final_state = await self.workflow.ainvoke(initial_state, config)
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"Workflow execution completed in {execution_time:.2f} seconds")
            
                # Determine final status
                workflow_status = final_state.get("status", WorkflowStatus.FAILED)
                
                if workflow_status == WorkflowStatus.COMPLETED:
                    self.active_workflows[workflow_id] = "completed"
                    pr_url = final_state.get('pr_url', 'N/A')
                    logger.info("✓ Workflow completed successfully")
                    logger.info(f"Pull Request: {pr_url}")
                    logger.debug(f"Final state keys: {list(final_state.keys())}")
                else:
                    self.active_workflows[workflow_id] = "failed"
                    errors = final_state.get("errors", [])
                    logger.error(f"✗ Workflow failed with status: {workflow_status}")
                    logger.error(f"Number of errors: {len(errors)}")
                    for i, error in enumerate(errors[:5], 1):  # Log first 5 errors
                        logger.error(f"  Error {i}: {error}")
            
                # Update metadata
                completed_at = datetime.utcnow()
                if workflow_id in self.workflow_metadata:
                    self.workflow_metadata[workflow_id].update({
                        "completed_at": completed_at,
                        "final_status": workflow_status,
                        "summary": format_workflow_summary(final_state),
                        "execution_time_seconds": execution_time
                    })
                    logger.debug(f"Workflow metadata updated at {completed_at.isoformat()}")
        
            except Exception as e:
                logger.error(f"✗ Workflow failed with exception: {type(e).__name__}: {e}")
                logger.error("Exception details:", exc_info=True)
                self.active_workflows[workflow_id] = "error"
            
                # Update metadata with error info
                if workflow_id in self.workflow_metadata:
                    error_time = datetime.utcnow()
                    execution_time = (error_time - self.workflow_start_times.get(workflow_id, error_time)).total_seconds()
                    self.workflow_metadata[workflow_id].update({
                        "completed_at": error_time,
                        "final_status": "error",
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "execution_time_seconds": execution_time
                    })
                    logger.debug(f"Error metadata stored at {error_time.isoformat()}")
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[IssueWorkflowState]:
        """
        Retrieve current workflow state with logging.
        
        Args:
            workflow_id: Workflow identifier
        
        Returns:
            Current workflow state or None if not found
        """
        logger.debug(f"Retrieving state for workflow: {workflow_id}")
        
        try:
            config = get_workflow_config(workflow_id)
            state_snapshot = await self.workflow.aget_state(config)
            
            if state_snapshot and state_snapshot.values:
                logger.debug(f"✓ State retrieved for workflow {workflow_id}")
                logger.debug(f"State keys: {list(state_snapshot.values.keys()) if hasattr(state_snapshot.values, 'keys') else 'N/A'}")
                return state_snapshot.values
            else:
                logger.warning(f"No state found for workflow {workflow_id}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to get state for workflow {workflow_id}: {e}", exc_info=True)
            return None
    
    async def get_workflow_summary(self, workflow_id: str) -> Optional[dict]:
        """
        Get a summary of workflow execution.
        
        Args:
            workflow_id: Workflow identifier
        
        Returns:
            Workflow summary or None if not found
        """
        state = await self.get_workflow_state(workflow_id)
        if not state:
            return None
        
        summary = format_workflow_summary(state)
        
        # Add metadata if available
        if workflow_id in self.workflow_metadata:
            metadata = self.workflow_metadata[workflow_id]
            summary.update({
                "created_at": metadata.get("created_at"),
                "repository": metadata.get("repository")
            })
        
        return summary
    
    def get_active_workflows(self) -> Dict[str, dict]:
        """
        Get information about all active workflows.
        
        Returns:
            Dict mapping workflow ID to workflow info
        """
        workflows = {}
        
        for workflow_id, status in self.active_workflows.items():
            workflow_info = {
                "status": status,
                "workflow_id": workflow_id
            }
            
            # Add metadata if available
            if workflow_id in self.workflow_metadata:
                metadata = self.workflow_metadata[workflow_id]
                workflow_info.update({
                    "created_at": metadata.get("created_at"),
                    "repository": metadata.get("repository"),
                    "issue_number": metadata.get("issue_number"),
                    "issue_title": metadata.get("issue_title")
                })
            
            workflows[workflow_id] = workflow_info
        
        return workflows
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow with logging.
        
        Args:
            workflow_id: Workflow to cancel
        
        Returns:
            True if successfully cancelled
        """
        logger.info(f"Attempting to cancel workflow: {workflow_id}")
        
        if workflow_id not in self.active_workflows:
            logger.warning(f"Cannot cancel - workflow not found: {workflow_id}")
            return False
        
        current_status = self.active_workflows[workflow_id]
        logger.debug(f"Current workflow status: {current_status}")
        
        if current_status in ["completed", "failed", "error", "cancelled"]:
            logger.warning(f"Cannot cancel - workflow already in terminal state: {current_status}")
            return False
        
        # Mark as cancelled
        self.active_workflows[workflow_id] = "cancelled"
        logger.info(f"✓ Workflow {workflow_id} marked as cancelled")
        
        # Update metadata
        if workflow_id in self.workflow_metadata:
            self.workflow_metadata[workflow_id].update({
                "cancelled_at": datetime.utcnow(),
                "final_status": "cancelled"
            })
        
        return True
    
    def cleanup_completed_workflows(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed workflows from memory with logging.
        
        Args:
            max_age_hours: Maximum age in hours for completed workflows
        
        Returns:
            Number of workflows cleaned up
        """
        logger.debug(f"Starting workflow cleanup (max_age={max_age_hours} hours)")
        
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        cleaned_count = 0
        
        # Find workflows to clean up
        to_remove = []
        for workflow_id, status in self.active_workflows.items():
            if status in ["completed", "failed", "error", "cancelled"]:
                metadata = self.workflow_metadata.get(workflow_id, {})
                completed_at = metadata.get("completed_at")
                
                if completed_at and completed_at.timestamp() < cutoff_time:
                    to_remove.append(workflow_id)
        
        # Remove old workflows
        for workflow_id in to_remove:
            logger.debug(f"Removing old workflow: {workflow_id}")
            del self.active_workflows[workflow_id]
            if workflow_id in self.workflow_metadata:
                del self.workflow_metadata[workflow_id]
            if workflow_id in self.workflow_start_times:
                del self.workflow_start_times[workflow_id]
            cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"✓ Cleaned up {cleaned_count} old workflows")
        else:
            logger.debug("No workflows to clean up")
        
        return cleaned_count
    
    def get_stats(self) -> dict:
        """
        Get orchestrator statistics with enhanced details.
        
        Returns:
            Dict with various statistics
        """
        status_counts = {}
        for status in self.active_workflows.values():
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate average execution time
        execution_times = []
        for metadata in self.workflow_metadata.values():
            if 'execution_time_seconds' in metadata:
                execution_times.append(metadata['execution_time_seconds'])
        
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        stats = {
            "total_workflows": len(self.active_workflows),
            "status_counts": status_counts,
            "checkpoint_db_path": self.checkpoint_db_path,
            "metadata_count": len(self.workflow_metadata),
            "average_execution_time_seconds": round(avg_execution_time, 2),
            "oldest_workflow": min(self.workflow_start_times.values()).isoformat() if self.workflow_start_times else None
        }
        
        logger.debug(f"Orchestrator stats: {stats}")
        return stats