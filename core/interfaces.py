"""Universal interface models for the Dynamic PM system.

This module contains all the standardized input/output models used by agents
to communicate with each other and with the PM orchestrator.

Based on the simplified step-interfaces.md specification.
"""

from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Universal Interfaces (Used by All Agents)
# ============================================================================

class QualityMetrics(BaseModel):
    """Quality assessment of step output."""
    completeness_score: float = Field(
        ge=0.0, le=1.0,
        description="How complete the output is (0.0 to 1.0)"
    )
    accuracy_score: float = Field(
        ge=0.0, le=1.0,
        description="How accurate the output is (0.0 to 1.0)"
    )
    code_quality_score: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Code quality score for code-related steps"
    )
    test_coverage: Optional[float] = Field(
        default=None, ge=0.0, le=100.0,
        description="Test coverage percentage for testing steps"
    )
    critical_issues_count: int = Field(
        default=0,
        description="Number of critical issues found"
    )
    warning_count: int = Field(
        default=0,
        description="Number of warnings found"
    )


class StepResult(BaseModel):
    """Universal output format for all agents."""
    status: Literal["success", "failed", "needs_clarification"]
    agent: str  # Which agent produced this
    output: Dict[str, Any]  # Agent-specific output data
    confidence: float = Field(ge=0.0, le=1.0)
    next_suggestions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    quality_metrics: Optional[QualityMetrics] = Field(
        default=None,
        description="Quality assessment of the step output"
    )


class NextAction(BaseModel):
    """PM's decision about what to do next."""
    target_agent: Literal["analyst", "tester", "developer", "pm"]
    input_data: Dict[str, Any]
    reason: str  # Why this decision was made


# ============================================================================
# Analyst Agent Interfaces
# ============================================================================

class AnalystInput(BaseModel):
    """Input for Analyst agent."""
    issue_description: str  # The GitHub issue text
    

class AnalystOutput(BaseModel):
    """Output from Analyst agent."""
    acceptance_criteria: List[str]  # What needs to work
    clarification_questions: List[str] = Field(default_factory=list)  # What's unclear
    complexity: Literal["simple", "medium", "complex"]
    effort_estimate: str  # e.g., "2 hours", "1 day"


# ============================================================================
# Tester Agent Interfaces
# ============================================================================

class TesterInput(BaseModel):
    """Input for Tester agent."""
    acceptance_criteria: List[str]  # From Analyst
    feature_description: str  # Brief summary
    

class TesterOutput(BaseModel):
    """Output from Tester agent."""
    test_code: str  # The actual test code
    test_file_path: str  # Where to save it (e.g., "tests/test_login.py")
    test_count: int  # Number of test cases created
    framework: str  # e.g., "pytest", "jest", "unittest"


# ============================================================================
# Developer Agent Interfaces
# ============================================================================

class CodeChange(BaseModel):
    """A single file change."""
    file_path: str
    diff: str  # Unified diff format (like git diff)
    summary: str  # One-line description


class DeveloperInput(BaseModel):
    """Input for Developer agent."""
    requirements: str  # What to implement
    acceptance_criteria: List[str]  # What must pass
    test_file_path: Optional[str] = None  # Tests to run after implementation
    

class DeveloperOutput(BaseModel):
    """Output from Developer agent."""
    changes_made: List[CodeChange]  # File changes as diffs
    tests_passed: bool  # Did the tests pass?
    test_output: str  # Test execution output
    implementation_notes: str  # Brief summary of what was done


# ============================================================================
# PM Agent Interfaces
# ============================================================================

class WorkflowContext(BaseModel):
    """Context maintained by PM throughout workflow execution."""
    issue_id: str
    issue_title: str
    issue_description: str
    issue_complexity: Literal["simple", "medium", "complex"] = "medium"
    current_state: str = "analyzing_requirements"
    step_history: List[StepResult] = Field(default_factory=list)
    human_interactions: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def add_step_result(self, result: StepResult) -> None:
        """Add a step result to the history."""
        self.step_history.append(result)
    
    def get_latest_step(self) -> Optional[StepResult]:
        """Get the most recent step result."""
        return self.step_history[-1] if self.step_history else None


class QualityGate(BaseModel):
    """Quality requirements that must be met to proceed."""
    min_confidence: float = Field(
        default=0.7, ge=0.0, le=1.0,
        description="Minimum confidence score required"
    )
    max_critical_issues: int = Field(
        default=0, ge=0,
        description="Maximum allowed critical issues"
    )
    min_completeness: float = Field(
        default=0.8, ge=0.0, le=1.0,
        description="Minimum completeness score required"
    )
    
    def evaluate(self, step_result: StepResult) -> bool:
        """Check if step result passes quality gates."""
        if step_result.confidence < self.min_confidence:
            return False
        
        if step_result.quality_metrics:
            metrics = step_result.quality_metrics
            if metrics.critical_issues_count > self.max_critical_issues:
                return False
            if metrics.completeness_score < self.min_completeness:
                return False
        
        return True


class PMEvaluation(BaseModel):
    """PM's evaluation of a step result."""
    step_result: StepResult
    workflow_state: str  # Current state in the workflow
    workflow_context: Optional[WorkflowContext] = None
    quality_gate: Optional[QualityGate] = None
    
    def decide_next_action(self) -> NextAction:
        """Decide what to do next based on the step result."""
        # This will be implemented in the PM agent
        raise NotImplementedError("Implemented in PM agent")
    
    def needs_human_input(self) -> bool:
        """Check if human clarification is needed."""
        return self.step_result.status == "needs_clarification"
    
    def passes_quality_gate(self) -> bool:
        """Check if the step result passes quality requirements."""
        if not self.quality_gate:
            return True
        return self.quality_gate.evaluate(self.step_result)
    
    def create_github_comment(self) -> str:
        """Create a comment for the GitHub issue."""
        # This will be implemented in the PM agent
        raise NotImplementedError("Implemented in PM agent")


# ============================================================================
# Helper Functions
# ============================================================================

def create_step_result(
    agent: str, 
    status: Literal["success", "failed", "needs_clarification"],
    output_data: Dict[str, Any],
    confidence: float = 0.8,
    suggestions: List[str] = None,
    quality_metrics: QualityMetrics = None
) -> StepResult:
    """Helper function to create a StepResult."""
    return StepResult(
        status=status,
        agent=agent,
        output=output_data,
        confidence=confidence,
        next_suggestions=suggestions or [],
        quality_metrics=quality_metrics
    )


def create_quality_metrics(
    completeness: float = 1.0,
    accuracy: float = 1.0,
    code_quality: Optional[float] = None,
    test_coverage: Optional[float] = None,
    critical_issues: int = 0,
    warnings: int = 0
) -> QualityMetrics:
    """Helper function to create QualityMetrics."""
    return QualityMetrics(
        completeness_score=completeness,
        accuracy_score=accuracy,
        code_quality_score=code_quality,
        test_coverage=test_coverage,
        critical_issues_count=critical_issues,
        warning_count=warnings
    )


def create_next_action(
    target_agent: Literal["analyst", "tester", "developer", "pm"],
    input_data: Dict[str, Any],
    reason: str
) -> NextAction:
    """Helper function to create a NextAction."""
    return NextAction(
        target_agent=target_agent,
        input_data=input_data,
        reason=reason
    )


# ============================================================================
# Workflow States (Simple String Constants)
# ============================================================================

class WorkflowStates:
    """Simple string constants for workflow states."""
    ANALYZING_REQUIREMENTS = "analyzing_requirements"
    CREATING_TESTS = "creating_tests"
    IMPLEMENTING = "implementing"
    WAITING_FOR_HUMAN_INPUT = "waiting_for_human_input"
    READY_FOR_PR = "ready_for_pr"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Type Aliases for Convenience
# ============================================================================

AgentInput = AnalystInput | TesterInput | DeveloperInput
AgentOutput = AnalystOutput | TesterOutput | DeveloperOutput


# ============================================================================
# Export List
# ============================================================================

__all__ = [
    # Universal interfaces
    "QualityMetrics",
    "StepResult",
    "NextAction",
    
    # Analyst interfaces
    "AnalystInput",
    "AnalystOutput",
    
    # Tester interfaces
    "TesterInput",
    "TesterOutput",
    
    # Developer interfaces
    "CodeChange",
    "DeveloperInput",
    "DeveloperOutput",
    
    # PM interfaces
    "WorkflowContext",
    "QualityGate",
    "PMEvaluation",
    
    # Workflow states
    "WorkflowStates",
    
    # Helper functions
    "create_step_result",
    "create_quality_metrics",
    "create_next_action",
    
    # Type aliases
    "AgentInput",
    "AgentOutput",
]