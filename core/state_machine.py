"""Issue State Machine Implementation for Dynamic PM System.

This module implements the complete state machine for issue processing
with Navigator states frozen/commented out to reduce complexity while
maintaining PM intelligence for workflow control.

Based on: docs/architecture/issue-state-machine.md
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from core.logging import get_logger

logger = get_logger(__name__)


class IssueState(Enum):
    """
    Sequential states for issue processing.
    Each state represents exactly one type of work being performed by one agent type.
    
    Navigator states are FROZEN/COMMENTED to reduce workflow complexity.
    """
    
    # Initial Reception
    RECEIVED = "received"  # Issue just arrived, needs initial triage
    
    # Requirements Analysis States  
    ANALYZING_REQUIREMENTS = "analyzing_requirements"        # Analyst investigating requirements
    REQUIREMENTS_UNCLEAR = "requirements_unclear"           # Requirements need clarification
    WAITING_FOR_REQUIREMENTS_CLARIFICATION = "waiting_for_requirements_clarification"  # PM posted questions, waiting for human response
    REQUIREMENTS_CLARIFIED = "requirements_clarified"       # Human provided clarification, ready to continue
    
    # Planning States
    PLANNING_APPROACH = "planning_approach"           # PM deciding implementation strategy
    
    # Testing States
    CREATING_TESTS = "creating_tests"                 # Tester creating test suite
    UPDATING_TESTS = "updating_tests"                 # Tester updating existing tests  
    RUNNING_TESTS = "running_tests"                   # Tester executing tests
    
    # Implementation States
    IMPLEMENTING = "implementing"                     # Developer implementing solution
    FIXING_ISSUES = "fixing_issues"                   # Developer fixing identified problems
    REFACTORING = "refactoring"                       # Developer improving code structure
    
    # Code Quality States (Navigator FROZEN for now - removing complexity)
    # REVIEWING_CODE = "reviewing_code"                 # Navigator reviewing implementation  
    # REVIEWING_ARCHITECTURE = "reviewing_architecture" # Navigator reviewing system design
    # REVIEWING_INTEGRATION = "reviewing_integration"   # Navigator checking integration points
    
    # Quality Assurance States
    VALIDATING_SOLUTION = "validating_solution"       # Final validation before PR
    ADDRESSING_FEEDBACK = "addressing_feedback"       # Incorporating review feedback
    
    # Completion States
    CREATING_PR = "creating_pr"                       # Creating pull request
    COMPLETED = "completed"                           # Issue successfully resolved
    
    # Human Interaction States
    WAITING_FOR_HUMAN_INPUT = "waiting_for_human_input"         # PM posted questions/requests, waiting for human response
    HUMAN_INPUT_RECEIVED = "human_input_received"               # Human provided input, ready to continue
    
    # Error States  
    FAILED = "failed"                                           # Unrecoverable failure
    BLOCKED = "blocked"                                         # Waiting for external dependencies
    REQUIRES_HUMAN_INTERVENTION = "requires_human_intervention"  # Complex issue needs human judgment


class StateTransitionRule:
    """Defines valid state transitions and which agent handles each state."""
    
    # Map each state to the agent type that handles it
    STATE_AGENT_MAPPING = {
        IssueState.RECEIVED: "pm",
        IssueState.ANALYZING_REQUIREMENTS: "analyst", 
        IssueState.REQUIREMENTS_UNCLEAR: "pm",  # PM decides next step
        IssueState.WAITING_FOR_REQUIREMENTS_CLARIFICATION: None,  # Waiting state - no agent
        IssueState.REQUIREMENTS_CLARIFIED: "pm",  # PM processes human input
        IssueState.PLANNING_APPROACH: "pm",
        IssueState.CREATING_TESTS: "tester",
        IssueState.UPDATING_TESTS: "tester", 
        IssueState.RUNNING_TESTS: "tester",
        IssueState.IMPLEMENTING: "developer",
        IssueState.FIXING_ISSUES: "developer",
        IssueState.REFACTORING: "developer", 
        # Navigator states FROZEN - removing complexity
        # IssueState.REVIEWING_CODE: "navigator",        
        # IssueState.REVIEWING_ARCHITECTURE: "navigator", 
        # IssueState.REVIEWING_INTEGRATION: "navigator",  
        IssueState.VALIDATING_SOLUTION: "tester",
        IssueState.ADDRESSING_FEEDBACK: "developer",
        IssueState.CREATING_PR: "pm",  # PM orchestrates PR creation
        IssueState.COMPLETED: None,   # Terminal state
        IssueState.FAILED: None,      # Terminal state  
        IssueState.WAITING_FOR_HUMAN_INPUT: None,  # Waiting state - no agent
        IssueState.HUMAN_INPUT_RECEIVED: "pm",  # PM processes human input
        IssueState.BLOCKED: "pm",     # PM handles blocked states
        IssueState.REQUIRES_HUMAN_INTERVENTION: None  # Terminal state
    }
    
    # Valid state transitions (from -> [to_states])
    # Navigator review states REMOVED to eliminate complexity
    VALID_TRANSITIONS = {
        IssueState.RECEIVED: [
            IssueState.ANALYZING_REQUIREMENTS,
            IssueState.CREATING_TESTS,  # For very simple issues
            IssueState.FAILED
        ],
        
        IssueState.ANALYZING_REQUIREMENTS: [
            IssueState.REQUIREMENTS_UNCLEAR,      # Need clarification  
            IssueState.CREATING_TESTS,             # Requirements clear, start testing
            IssueState.IMPLEMENTING,               # Skip tests for simple fixes
            IssueState.FAILED
        ],
        
        IssueState.REQUIREMENTS_UNCLEAR: [
            IssueState.WAITING_FOR_REQUIREMENTS_CLARIFICATION,  # PM posts questions to GitHub
            IssueState.ANALYZING_REQUIREMENTS,     # Send back to Analyst for more analysis
            IssueState.BLOCKED,                     # External dependency
            IssueState.REQUIRES_HUMAN_INTERVENTION
        ],
        
        IssueState.WAITING_FOR_REQUIREMENTS_CLARIFICATION: [
            IssueState.REQUIREMENTS_CLARIFIED,     # Human provided clarification
            IssueState.BLOCKED,                    # Extended wait time
            IssueState.FAILED                     # Timeout or abandonment
        ],
        
        IssueState.REQUIREMENTS_CLARIFIED: [
            IssueState.CREATING_TESTS,             # Requirements now clear, proceed
            IssueState.ANALYZING_REQUIREMENTS,     # Need Analyst to process clarification
            IssueState.IMPLEMENTING,               # Simple enough to skip testing
            IssueState.FAILED
        ],
        
        IssueState.PLANNING_APPROACH: [
            IssueState.CREATING_TESTS,
            IssueState.IMPLEMENTING, 
            IssueState.ANALYZING_REQUIREMENTS,     # Need more info
            IssueState.FAILED
        ],
        
        IssueState.CREATING_TESTS: [
            IssueState.IMPLEMENTING,               # Tests ready, start implementation
            IssueState.UPDATING_TESTS,             # Tests need refinement
            IssueState.ANALYZING_REQUIREMENTS,     # Tests revealed requirement gaps
            IssueState.FAILED
        ],
        
        IssueState.UPDATING_TESTS: [
            IssueState.IMPLEMENTING,               # Tests now ready
            IssueState.CREATING_TESTS,             # Major test changes needed
            IssueState.FAILED
        ],
        
        IssueState.RUNNING_TESTS: [
            IssueState.IMPLEMENTING,               # Tests pass, continue
            IssueState.FIXING_ISSUES,              # Tests fail, need fixes
            IssueState.UPDATING_TESTS,             # Tests themselves need changes
            IssueState.COMPLETED,                  # All tests pass, done
            IssueState.FAILED
        ],
        
        # KEY CHANGE: NAVIGATOR REVIEW STATES BYPASSED
        # Implementation goes directly to testing or PR creation
        IssueState.IMPLEMENTING: [
            IssueState.RUNNING_TESTS,              # Run tests on implementation (SKIP Navigator review)
            IssueState.CREATING_PR,                # Simple implementations can go direct to PR  
            IssueState.FIXING_ISSUES,              # Self-identified issues
            IssueState.ANALYZING_REQUIREMENTS,     # Implementation revealed requirement gaps
            IssueState.FAILED
        ],
        
        IssueState.FIXING_ISSUES: [
            IssueState.RUNNING_TESTS,              # Test the fixes (SKIP Navigator review)
            IssueState.CREATING_PR,                # Fixes complete, ready for PR
            IssueState.IMPLEMENTING,               # More implementation needed
            IssueState.REFACTORING,                # Code needs restructuring
            IssueState.FAILED
        ],
        
        IssueState.REFACTORING: [
            IssueState.RUNNING_TESTS,              # Test refactored code (SKIP Navigator review)
            IssueState.CREATING_PR,                # Refactoring complete, ready for PR
            IssueState.IMPLEMENTING,               # More work needed
            IssueState.FAILED
        ],
        
        # Navigator states FROZEN - removing all Navigator review complexity
        # IssueState.REVIEWING_CODE: [...],
        # IssueState.REVIEWING_ARCHITECTURE: [...],
        # IssueState.REVIEWING_INTEGRATION: [...],
        
        IssueState.VALIDATING_SOLUTION: [
            IssueState.CREATING_PR,                # Validation passed
            IssueState.FIXING_ISSUES,              # Validation failed
            IssueState.UPDATING_TESTS,             # Tests need adjustment
            IssueState.FAILED
        ],
        
        IssueState.ADDRESSING_FEEDBACK: [
            IssueState.RUNNING_TESTS,              # Test feedback changes (SKIP Navigator re-review)
            IssueState.CREATING_PR,                # Feedback addressed, ready for PR
            IssueState.FAILED
        ],
        
        IssueState.CREATING_PR: [
            IssueState.COMPLETED,                  # PR created successfully
            IssueState.WAITING_FOR_HUMAN_INPUT,    # Need approval or input for PR
            IssueState.FAILED                      # PR creation failed
        ],
        
        # Human interaction states
        IssueState.WAITING_FOR_HUMAN_INPUT: [
            IssueState.HUMAN_INPUT_RECEIVED,       # Human provided input
            IssueState.BLOCKED,                    # Extended wait time
            IssueState.FAILED                     # Timeout or abandonment
        ],
        
        IssueState.HUMAN_INPUT_RECEIVED: [
            # Can transition to any appropriate state based on input (Navigator FROZEN)
            IssueState.ANALYZING_REQUIREMENTS,
            IssueState.CREATING_TESTS,
            IssueState.IMPLEMENTING,
            # Navigator states REMOVED
            IssueState.CREATING_PR,
            IssueState.COMPLETED,
            IssueState.FAILED
        ],
        
        # Terminal states - no transitions out
        IssueState.COMPLETED: [],
        IssueState.FAILED: [],
        IssueState.BLOCKED: [
            # Can transition out of blocked when dependency resolves
            IssueState.ANALYZING_REQUIREMENTS,
            IssueState.IMPLEMENTING,
            IssueState.CREATING_TESTS,
            IssueState.WAITING_FOR_HUMAN_INPUT,
            IssueState.REQUIRES_HUMAN_INTERVENTION
        ],
        IssueState.REQUIRES_HUMAN_INTERVENTION: []
    }

    @classmethod
    def is_valid_transition(cls, from_state: IssueState, to_state: IssueState) -> bool:
        """Check if state transition is valid."""
        return to_state in cls.VALID_TRANSITIONS.get(from_state, [])
    
    @classmethod  
    def get_responsible_agent(cls, state: IssueState) -> Optional[str]:
        """Get the agent type responsible for handling this state."""
        return cls.STATE_AGENT_MAPPING.get(state)
    
    @classmethod
    def get_valid_next_states(cls, from_state: IssueState) -> List[IssueState]:
        """Get all valid next states from current state."""
        return cls.VALID_TRANSITIONS.get(from_state, [])
    
    @classmethod
    def is_terminal_state(cls, state: IssueState) -> bool:
        """Check if state is terminal (no valid transitions out)."""
        return len(cls.VALID_TRANSITIONS.get(state, [])) == 0
    
    @classmethod
    def is_waiting_state(cls, state: IssueState) -> bool:
        """Check if state is a waiting state (no agent assigned)."""
        return cls.STATE_AGENT_MAPPING.get(state) is None and not cls.is_terminal_state(state)


class StateTransition(BaseModel):
    """Records a state transition with context."""
    from_state: IssueState
    to_state: IssueState
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: str = ""
    triggered_by: Optional[str] = None  # Agent or system that triggered transition
    iteration: int = 0


class WorkflowContext(BaseModel):
    """Enhanced context for PM decision making with state tracking."""
    issue_number: int
    issue_title: str = ""
    issue_description: str = ""
    repository: str = ""
    
    # State tracking
    current_state: IssueState = IssueState.RECEIVED
    previous_states: List[IssueState] = Field(default_factory=list)
    state_transitions: List[StateTransition] = Field(default_factory=list)
    
    # Agent tracking
    current_agent: Optional[str] = None
    iteration_count: int = 0
    max_iterations: int = 10
    
    # Quality and progress tracking
    confidence_threshold: float = 0.7
    quality_gates_passed: List[str] = Field(default_factory=list)
    blocking_issues: List[str] = Field(default_factory=list)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def transition_to_state(
        self, 
        new_state: IssueState, 
        reason: str = "", 
        triggered_by: Optional[str] = None
    ) -> bool:
        """Transition to new state with validation."""
        if not StateTransitionRule.is_valid_transition(self.current_state, new_state):
            error_msg = f"Invalid state transition: {self.current_state.value} -> {new_state.value}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Record state change  
        self.previous_states.append(self.current_state)
        
        transition = StateTransition(
            from_state=self.current_state,
            to_state=new_state,
            reason=reason,
            triggered_by=triggered_by,
            iteration=self.iteration_count
        )
        self.state_transitions.append(transition)
        
        # Update state
        self.current_state = new_state
        self.current_agent = StateTransitionRule.get_responsible_agent(new_state)
        self.iteration_count += 1
        self.updated_at = datetime.utcnow()
        
        # Mark completion time for terminal states
        if StateTransitionRule.is_terminal_state(new_state):
            self.completed_at = datetime.utcnow()
        
        logger.info(
            f"Issue #{self.issue_number} transitioned: "
            f"{transition.from_state.value} -> {transition.to_state.value} "
            f"(reason: {reason})"
        )
        
        return True
    
    def is_in_loop(self, max_same_state_visits: int = 3) -> bool:
        """Detect if workflow is stuck in a loop."""
        if len(self.previous_states) < max_same_state_visits:
            return False
            
        recent_states = self.previous_states[-max_same_state_visits:]
        return len(set(recent_states)) <= 2  # Only 2 or fewer distinct states
    
    def get_current_responsible_agent(self) -> Optional[str]:
        """Get agent responsible for current state."""
        return StateTransitionRule.get_responsible_agent(self.current_state)
    
    def is_terminal_state(self) -> bool:
        """Check if workflow is in a terminal state."""
        return StateTransitionRule.is_terminal_state(self.current_state)
    
    def is_waiting_for_human(self) -> bool:
        """Check if workflow is waiting for human input."""
        return self.current_state in [
            IssueState.WAITING_FOR_REQUIREMENTS_CLARIFICATION,
            IssueState.WAITING_FOR_HUMAN_INPUT
        ]
    
    def get_state_duration(self, state: IssueState) -> Optional[float]:
        """Get how long was spent in a specific state (in seconds)."""
        transitions_in = [t for t in self.state_transitions if t.to_state == state]
        transitions_out = [t for t in self.state_transitions if t.from_state == state]
        
        if not transitions_in:
            return None
            
        enter_time = transitions_in[0].timestamp
        exit_time = transitions_out[0].timestamp if transitions_out else datetime.utcnow()
        
        return (exit_time - enter_time).total_seconds()
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get a summary of the workflow execution."""
        return {
            "issue_number": self.issue_number,
            "current_state": self.current_state.value,
            "total_iterations": self.iteration_count,
            "states_visited": len(set(self.previous_states + [self.current_state])),
            "is_terminal": self.is_terminal_state(),
            "is_waiting_for_human": self.is_waiting_for_human(),
            "blocking_issues": self.blocking_issues,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_duration_seconds": (
                (self.completed_at or datetime.utcnow()) - self.created_at
            ).total_seconds()
        }


class StateMachine:
    """State machine manager for issue workflow."""
    
    def __init__(self):
        """Initialize state machine."""
        self.active_workflows: Dict[int, WorkflowContext] = {}
        logger.info("State machine initialized with Navigator states FROZEN")
    
    def create_workflow(
        self, 
        issue_number: int, 
        issue_title: str = "", 
        issue_description: str = "",
        repository: str = ""
    ) -> WorkflowContext:
        """Create a new workflow for an issue."""
        if issue_number in self.active_workflows:
            logger.warning(f"Workflow for issue #{issue_number} already exists")
            return self.active_workflows[issue_number]
        
        context = WorkflowContext(
            issue_number=issue_number,
            issue_title=issue_title,
            issue_description=issue_description,
            repository=repository
        )
        
        self.active_workflows[issue_number] = context
        
        logger.info(
            f"Created workflow for issue #{issue_number}: {issue_title} "
            f"(Navigator FROZEN - simplified workflow)"
        )
        
        return context
    
    def get_workflow(self, issue_number: int) -> Optional[WorkflowContext]:
        """Get existing workflow context."""
        return self.active_workflows.get(issue_number)
    
    def transition_workflow(
        self, 
        issue_number: int, 
        new_state: IssueState, 
        reason: str = "",
        triggered_by: Optional[str] = None
    ) -> bool:
        """Transition workflow to new state."""
        context = self.get_workflow(issue_number)
        if not context:
            logger.error(f"No workflow found for issue #{issue_number}")
            return False
        
        try:
            return context.transition_to_state(new_state, reason, triggered_by)
        except ValueError as e:
            logger.error(f"State transition failed for issue #{issue_number}: {e}")
            return False
    
    def complete_workflow(self, issue_number: int, reason: str = "Workflow completed") -> bool:
        """Mark workflow as completed and remove from active tracking."""
        context = self.get_workflow(issue_number)
        if not context:
            return False
        
        # Transition to completed state if not already there
        if context.current_state != IssueState.COMPLETED:
            context.transition_to_state(IssueState.COMPLETED, reason)
        
        # Remove from active tracking
        del self.active_workflows[issue_number]
        
        logger.info(f"Workflow completed for issue #{issue_number}")
        return True
    
    def get_active_workflows(self) -> List[WorkflowContext]:
        """Get all active workflow contexts."""
        return list(self.active_workflows.values())
    
    def get_workflows_by_state(self, state: IssueState) -> List[WorkflowContext]:
        """Get all workflows in a specific state."""
        return [ctx for ctx in self.active_workflows.values() if ctx.current_state == state]
    
    def get_waiting_workflows(self) -> List[WorkflowContext]:
        """Get all workflows waiting for human input."""
        return [ctx for ctx in self.active_workflows.values() if ctx.is_waiting_for_human()]


# Global state machine instance
_state_machine = StateMachine()


def get_state_machine() -> StateMachine:
    """Get the global state machine instance."""
    return _state_machine


# ============================================================================
# Export List
# ============================================================================

__all__ = [
    "IssueState",
    "StateTransitionRule", 
    "StateTransition",
    "WorkflowContext",
    "StateMachine",
    "get_state_machine"
]