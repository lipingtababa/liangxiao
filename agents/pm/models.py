"""Pydantic models for Project Manager Agent.

This module defines the data structures used by the PM Agent to analyze issues
and create task breakdowns. These models ensure structured output and type safety.
"""

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class Task(BaseModel):
    """Individual task in a project breakdown.
    
    Represents a specific, actionable task that can be assigned to an agent.
    Each task should be small enough to complete in one session and have
    clear acceptance criteria.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    id: str = Field(
        description="Unique task identifier within the issue context",
        min_length=1,
        pattern=r"^task-\d+$"
    )
    
    title: str = Field(
        description="Concise, descriptive task title",
        min_length=5,
        max_length=100
    )
    
    description: str = Field(
        description="Detailed task description explaining what needs to be done",
        min_length=10,
        max_length=1000
    )
    
    task_type: Literal[
        "analysis", "implementation", "testing", "documentation", "review"
    ] = Field(
        description="Type of work this task represents"
    )
    
    assigned_agent: Literal["analyst", "developer", "tester", "navigator"] = Field(
        description="Agent type responsible for executing this task"
    )
    
    dependencies: List[str] = Field(
        default_factory=list,
        description="Task IDs that must be completed before this task can start"
    )
    
    acceptance_criteria: List[str] = Field(
        min_length=1,
        description="Specific, measurable criteria that define task completion"
    )
    
    estimated_complexity: Literal[
        "trivial", "simple", "medium", "complex", "very_complex"
    ] = Field(
        description="Estimated complexity level for this task"
    )
    
    estimated_hours: float = Field(
        ge=0.1,
        le=16.0,
        description="Estimated hours to complete this task"
    )
    
    priority: Literal["low", "medium", "high", "critical"] = Field(
        default="medium",
        description="Task priority level"
    )
    
    # Optional fields for tracking
    status: Literal["pending", "in_progress", "completed", "blocked"] = Field(
        default="pending",
        description="Current task status"
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="When this task was created"
    )
    
    def __str__(self) -> str:
        return f"Task {self.id}: {self.title} ({self.task_type})"


class IssueAnalysis(BaseModel):
    """Comprehensive analysis of a GitHub issue.
    
    Contains the PM Agent's understanding of what needs to be done,
    including complexity assessment, risks, and clarifying questions.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    issue_type: Literal[
        "bug_fix", "feature", "enhancement", "documentation", 
        "refactor", "maintenance", "investigation"
    ] = Field(
        description="Classification of the issue type"
    )
    
    summary: str = Field(
        min_length=10,
        max_length=500,
        description="Concise summary of what needs to be accomplished"
    )
    
    complexity: Literal[
        "trivial", "simple", "medium", "complex", "very_complex"
    ] = Field(
        description="Overall complexity assessment of the issue"
    )
    
    estimated_effort: str = Field(
        description="Human-readable effort estimate (e.g., '2-4 hours', '1-2 days')",
        min_length=3
    )
    
    risks: List[str] = Field(
        default_factory=list,
        description="Potential risks, challenges, or blockers identified"
    )
    
    assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions made during the analysis process"
    )
    
    questions: List[str] = Field(
        default_factory=list,
        description="Clarifying questions that would help improve the implementation"
    )
    
    key_requirements: List[str] = Field(
        min_length=1,
        description="Essential requirements extracted from the issue"
    )
    
    affected_areas: List[str] = Field(
        default_factory=list,
        description="Code areas, files, or systems likely to be affected"
    )
    
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        default=0.8,
        description="Confidence in the analysis accuracy (0.0 to 1.0)"
    )
    
    analysis_notes: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional notes or reasoning from the analysis"
    )
    
    analyzed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this analysis was performed"
    )
    
    def __str__(self) -> str:
        return f"Analysis: {self.issue_type} ({self.complexity}) - {self.summary}"


class TaskBreakdown(BaseModel):
    """Complete task breakdown for an issue.
    
    Represents the PM Agent's complete plan for addressing an issue,
    including the analysis, individual tasks, execution order, and
    overall approach recommendations.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    analysis: IssueAnalysis = Field(
        description="The underlying issue analysis"
    )
    
    tasks: List[Task] = Field(
        min_length=1,
        description="List of tasks required to complete the issue"
    )
    
    execution_order: List[str] = Field(
        min_length=1,
        description="Task IDs in recommended execution order"
    )
    
    total_estimated_hours: float = Field(
        ge=0.1,
        description="Sum of estimated hours for all tasks"
    )
    
    recommended_approach: str = Field(
        min_length=20,
        max_length=1000,
        description="High-level approach and strategy for implementation"
    )
    
    success_criteria: List[str] = Field(
        min_length=1,
        description="Overall success criteria for the entire issue"
    )
    
    testing_strategy: str = Field(
        min_length=10,
        max_length=500,
        description="Recommended testing approach for this issue"
    )
    
    rollback_plan: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Plan for rolling back changes if needed"
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this breakdown was created"
    )
    
    pm_agent_version: str = Field(
        default="1.0",
        description="Version of PM Agent that created this breakdown"
    )
    
    def validate_dependencies(self) -> List[str]:
        """Validate task dependencies and return any issues found.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        task_ids = {task.id for task in self.tasks}
        
        for task in self.tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    errors.append(
                        f"Task {task.id} depends on non-existent task {dep_id}"
                    )
        
        # Check execution order includes all tasks
        execution_set = set(self.execution_order)
        if execution_set != task_ids:
            missing = task_ids - execution_set
            extra = execution_set - task_ids
            if missing:
                errors.append(f"Tasks missing from execution order: {missing}")
            if extra:
                errors.append(f"Unknown tasks in execution order: {extra}")
        
        return errors
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID.
        
        Args:
            task_id: The task ID to search for
            
        Returns:
            The task with the given ID, or None if not found
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_next_ready_task(self, completed_task_ids: set[str]) -> Optional[Task]:
        """Get the next task that is ready to execute.
        
        Args:
            completed_task_ids: Set of task IDs that have been completed
            
        Returns:
            The next ready task, or None if no tasks are ready
        """
        for task_id in self.execution_order:
            task = self.get_task_by_id(task_id)
            if not task:
                continue
            
            # Skip if task is already completed
            if task_id in completed_task_ids:
                continue
            
            # Only consider pending tasks
            if task.status != "pending":
                continue
                
            # Check if all dependencies are completed
            deps_completed = all(
                dep_id in completed_task_ids for dep_id in task.dependencies
            )
            
            if deps_completed:
                return task
        
        return None
    
    def __str__(self) -> str:
        return (
            f"TaskBreakdown: {len(self.tasks)} tasks, "
            f"{self.total_estimated_hours}h total, "
            f"{self.analysis.issue_type}"
        )


class PMAgentConfig(BaseModel):
    """Configuration for PM Agent behavior.
    
    Controls how the PM Agent analyzes issues and creates task breakdowns.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    llm_model: str = Field(
        default="gpt-4-turbo-preview",
        description="LLM model to use for analysis"
    )
    
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM responses (lower = more consistent)"
    )
    
    max_tasks_per_issue: int = Field(
        default=8,
        ge=1,
        le=20,
        description="Maximum number of tasks to create per issue"
    )
    
    min_task_complexity: Literal[
        "trivial", "simple", "medium", "complex", "very_complex"
    ] = Field(
        default="trivial",
        description="Minimum complexity for standalone tasks"
    )
    
    require_testing_tasks: bool = Field(
        default=True,
        description="Whether to always include testing tasks"
    )
    
    require_documentation_tasks: bool = Field(
        default=False,
        description="Whether to require documentation tasks for all issues"
    )
    
    enable_risk_analysis: bool = Field(
        default=True,
        description="Whether to perform detailed risk analysis"
    )
    
    max_analysis_tokens: int = Field(
        default=4000,
        ge=1000,
        le=16000,
        description="Maximum tokens to use for issue analysis"
    )
    
    def __str__(self) -> str:
        return f"PMAgentConfig: {self.llm_model} (temp={self.temperature})"