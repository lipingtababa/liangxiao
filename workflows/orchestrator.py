"""Workflow orchestrator for managing issue processing workflows."""

import asyncio
from typing import Optional, Dict, List
from datetime import datetime

from core.logging import get_logger
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
        
        logger.info(f"Workflow orchestrator initialized with checkpoint DB: {checkpoint_db_path}")
    
    def _generate_workflow_id(self, issue_event: IssueEvent) -> str:
        """Generate unique workflow ID for an issue."""
        return f"issue-{issue_event.repository.full_name.replace('/', '-')}-{issue_event.issue.number}"
    
    async def start_workflow(
        self,
        issue_event: IssueEvent,
        force_restart: bool = False
    ) -> str:
        """
        Start a new workflow for an issue.
        
        Args:
            issue_event: GitHub issue event that triggered the workflow
            force_restart: Whether to restart if workflow already exists
        
        Returns:
            Workflow ID for tracking
        
        Raises:
            ValueError: If workflow already exists and force_restart is False
        """
        workflow_id = self._generate_workflow_id(issue_event)
        
        # Check if workflow already exists
        if workflow_id in self.active_workflows and not force_restart:
            current_status = self.active_workflows[workflow_id]
            logger.warning(
                f"Workflow {workflow_id} already exists with status: {current_status}"
            )
            raise ValueError(f"Workflow already exists: {workflow_id}")
        
        logger.info(
            f"Starting workflow {workflow_id} for issue #{issue_event.issue.number} "
            f"in {issue_event.repository.full_name}"
        )
        
        # Create initial state
        initial_state = create_initial_state(
            issue_number=issue_event.issue.number,
            issue_title=issue_event.issue.title,
            issue_body=issue_event.issue.body or "",
            issue_url=issue_event.issue.html_url,
            repository=issue_event.repository.full_name,
            issue_labels=[label.name for label in issue_event.issue.labels],
            issue_assignees=[assignee.login for assignee in issue_event.issue.assignees]
        )
        
        # Store workflow metadata
        self.workflow_metadata[workflow_id] = {
            "created_at": datetime.utcnow(),
            "issue_event": issue_event.model_dump(),
            "repository": issue_event.repository.full_name,
            "issue_number": issue_event.issue.number,
            "issue_title": issue_event.issue.title
        }
        
        # Mark as starting
        self.active_workflows[workflow_id] = "starting"
        
        # Start workflow asynchronously
        asyncio.create_task(
            self._run_workflow(workflow_id, initial_state)
        )
        
        logger.info(f"Workflow {workflow_id} started successfully")
        return workflow_id
    
    async def _run_workflow(self, workflow_id: str, initial_state: IssueWorkflowState):
        """
        Run workflow to completion.
        
        Args:
            workflow_id: Unique workflow identifier
            initial_state: Initial workflow state
        """
        config = get_workflow_config(workflow_id)
        
        try:
            logger.info(f"Executing workflow {workflow_id}")
            self.active_workflows[workflow_id] = "running"
            
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state, config)
            
            # Determine final status
            workflow_status = final_state.get("status", WorkflowStatus.FAILED)
            if workflow_status == WorkflowStatus.COMPLETED:
                self.active_workflows[workflow_id] = "completed"
                logger.info(
                    f"Workflow {workflow_id} completed successfully. "
                    f"PR: {final_state.get('pr_url', 'N/A')}"
                )
            else:
                self.active_workflows[workflow_id] = "failed"
                errors = final_state.get("errors", [])
                logger.error(
                    f"Workflow {workflow_id} failed with status: {workflow_status}. "
                    f"Errors: {len(errors)}"
                )
            
            # Update metadata
            if workflow_id in self.workflow_metadata:
                self.workflow_metadata[workflow_id].update({
                    "completed_at": datetime.utcnow(),
                    "final_status": workflow_status,
                    "summary": format_workflow_summary(final_state)
                })
        
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed with exception: {e}", exc_info=True)
            self.active_workflows[workflow_id] = "error"
            
            # Update metadata with error info
            if workflow_id in self.workflow_metadata:
                self.workflow_metadata[workflow_id].update({
                    "completed_at": datetime.utcnow(),
                    "final_status": "error",
                    "error": str(e)
                })
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[IssueWorkflowState]:
        """
        Retrieve current workflow state.
        
        Args:
            workflow_id: Workflow identifier
        
        Returns:
            Current workflow state or None if not found
        """
        try:
            config = get_workflow_config(workflow_id)
            state_snapshot = await self.workflow.aget_state(config)
            
            if state_snapshot and state_snapshot.values:
                logger.debug(f"Retrieved state for workflow {workflow_id}")
                return state_snapshot.values
            else:
                logger.warning(f"No state found for workflow {workflow_id}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to get state for workflow {workflow_id}: {e}")
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
        Cancel a running workflow.
        
        Args:
            workflow_id: Workflow to cancel
        
        Returns:
            True if successfully cancelled
        """
        if workflow_id not in self.active_workflows:
            logger.warning(f"Cannot cancel unknown workflow: {workflow_id}")
            return False
        
        current_status = self.active_workflows[workflow_id]
        
        if current_status in ["completed", "failed", "error", "cancelled"]:
            logger.warning(f"Cannot cancel workflow {workflow_id} with status: {current_status}")
            return False
        
        # Mark as cancelled
        self.active_workflows[workflow_id] = "cancelled"
        
        # Update metadata
        if workflow_id in self.workflow_metadata:
            self.workflow_metadata[workflow_id].update({
                "cancelled_at": datetime.utcnow(),
                "final_status": "cancelled"
            })
        
        logger.info(f"Workflow {workflow_id} marked as cancelled")
        return True
    
    def cleanup_completed_workflows(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed workflows from memory.
        
        Args:
            max_age_hours: Maximum age in hours for completed workflows
        
        Returns:
            Number of workflows cleaned up
        """
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
            del self.active_workflows[workflow_id]
            if workflow_id in self.workflow_metadata:
                del self.workflow_metadata[workflow_id]
            cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old workflows")
        
        return cleaned_count
    
    def get_stats(self) -> dict:
        """
        Get orchestrator statistics.
        
        Returns:
            Dict with various statistics
        """
        status_counts = {}
        for status in self.active_workflows.values():
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_workflows": len(self.active_workflows),
            "status_counts": status_counts,
            "checkpoint_db_path": self.checkpoint_db_path
        }