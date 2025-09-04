# Issue State Machine Design

## Core Principle: Single State Execution

**Rule**: Every issue exists in exactly ONE state at any given time. Only ONE agent can work on an issue at a time. The PM agent makes ONE decision to transition to ONE next state.

## State Enum Definition

```python
from enum import Enum

class IssueState(Enum):
    """
    Sequential states for issue processing.
    Each state represents exactly one type of work being performed by one agent type.
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
    
    # Code Quality States (Navigator frozen for now)
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
        # IssueState.REVIEWING_CODE: "navigator",        # Navigator frozen
        # IssueState.REVIEWING_ARCHITECTURE: "navigator", # Navigator frozen
        # IssueState.REVIEWING_INTEGRATION: "navigator",  # Navigator frozen
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
        
        IssueState.IMPLEMENTING: [
            IssueState.RUNNING_TESTS,              # Run tests on implementation (skip Navigator review)
            IssueState.CREATING_PR,                # Simple implementations can go direct to PR
            IssueState.FIXING_ISSUES,              # Self-identified issues
            IssueState.ANALYZING_REQUIREMENTS,     # Implementation revealed requirement gaps
            IssueState.FAILED
        ],
        
        IssueState.FIXING_ISSUES: [
            IssueState.RUNNING_TESTS,              # Test the fixes (skip Navigator review)
            IssueState.CREATING_PR,                # Fixes complete, ready for PR
            IssueState.IMPLEMENTING,               # More implementation needed
            IssueState.REFACTORING,                # Code needs restructuring
            IssueState.FAILED
        ],
        
        IssueState.REFACTORING: [
            IssueState.RUNNING_TESTS,              # Test refactored code (skip Navigator review)
            IssueState.CREATING_PR,                # Refactoring complete, ready for PR
            IssueState.IMPLEMENTING,               # More work needed
            IssueState.FAILED
        ],
        
        # Navigator states frozen for now - removing complexity
        # IssueState.REVIEWING_CODE: [
        #     IssueState.CREATING_PR,                # Review approved
        #     IssueState.FIXING_ISSUES,              # Review found issues
        #     IssueState.REFACTORING,                # Code needs restructuring
        #     IssueState.REVIEWING_ARCHITECTURE,     # Deeper architectural review needed
        #     IssueState.REVIEWING_INTEGRATION,      # Integration concerns found
        #     IssueState.UPDATING_TESTS,             # Tests need changes  
        #     IssueState.ANALYZING_REQUIREMENTS,     # Requirements need clarification
        #     IssueState.FAILED
        # ],
        
        # IssueState.REVIEWING_ARCHITECTURE: [
        #     IssueState.CREATING_PR,                # Architecture approved
        #     IssueState.REFACTORING,                # Architecture needs changes
        #     IssueState.ANALYZING_REQUIREMENTS,     # Requirements conflict
        #     IssueState.FAILED
        # ],
        
        # IssueState.REVIEWING_INTEGRATION: [
        #     IssueState.CREATING_PR,                # Integration approved
        #     IssueState.FIXING_ISSUES,              # Integration issues found
        #     IssueState.ANALYZING_REQUIREMENTS,     # Integration reveals requirement gaps
        #     IssueState.FAILED
        # ],
        
        IssueState.VALIDATING_SOLUTION: [
            IssueState.CREATING_PR,                # Validation passed
            IssueState.FIXING_ISSUES,              # Validation failed
            IssueState.UPDATING_TESTS,             # Tests need adjustment
            IssueState.FAILED
        ],
        
        IssueState.ADDRESSING_FEEDBACK: [
            IssueState.RUNNING_TESTS,              # Test feedback changes (skip Navigator re-review)
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
            # Can transition to any appropriate state based on input (Navigator frozen)
            IssueState.ANALYZING_REQUIREMENTS,
            IssueState.CREATING_TESTS,
            IssueState.IMPLEMENTING,
            # IssueState.REVIEWING_CODE,              # Navigator frozen
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
    def get_responsible_agent(cls, state: IssueState) -> str:
        """Get the agent type responsible for handling this state."""
        return cls.STATE_AGENT_MAPPING.get(state)
    
    @classmethod
    def get_valid_next_states(cls, from_state: IssueState) -> List[IssueState]:
        """Get all valid next states from current state."""
        return cls.VALID_TRANSITIONS.get(from_state, [])


class WorkflowContext(BaseModel):
    """Context for PM decision making with state tracking."""
    issue_number: int
    current_state: IssueState
    previous_states: List[IssueState] = Field(default_factory=list)
    state_history_with_timestamps: List[Dict[str, Any]] = Field(default_factory=list)
    
    current_agent: Optional[str] = None
    iteration_count: int = 0
    max_iterations: int = 10
    
    # Quality and progress tracking
    confidence_threshold: float = 0.85
    quality_gates_passed: List[str] = Field(default_factory=list)
    blocking_issues: List[str] = Field(default_factory=list)
    
    def transition_to_state(self, new_state: IssueState, reason: str = "") -> bool:
        """Transition to new state with validation."""
        if not StateTransitionRule.is_valid_transition(self.current_state, new_state):
            raise ValueError(f"Invalid state transition: {self.current_state} -> {new_state}")
        
        # Record state change  
        self.previous_states.append(self.current_state)
        self.state_history_with_timestamps.append({
            "from_state": self.current_state.value,
            "to_state": new_state.value, 
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "iteration": self.iteration_count
        })
        
        self.current_state = new_state
        self.current_agent = StateTransitionRule.get_responsible_agent(new_state)
        self.iteration_count += 1
        
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
```

## PM Decision Integration

```python
class DynamicPMAgent:
    def evaluate_step_result(
        self, 
        step_result: StepResult, 
        context: WorkflowContext
    ) -> NextAction:
        """
        PM evaluates step result and decides next state transition.
        Enforces single-state principle.
        """
        
        # Quality gate evaluation
        if not self._passes_quality_requirements(step_result, context):
            return self._handle_quality_failure(step_result, context)
        
        # Context-aware state transition decision
        next_state = self._determine_next_state(step_result, context)
        
        # Validate transition is allowed
        if not StateTransitionRule.is_valid_transition(context.current_state, next_state):
            raise ValueError(f"PM attempted invalid transition: {context.current_state} -> {next_state}")
        
        # Create action for next state
        return NextAction(
            action=self._get_action_for_state(next_state),
            target_agent=StateTransitionRule.get_responsible_agent(next_state),
            new_state=next_state,
            input_data=self._prepare_input_for_state(step_result, next_state, context)
        )
    
    def _determine_next_state(self, step_result: StepResult, context: WorkflowContext) -> IssueState:
        """Determine next state based on step result and current context."""
        current_state = context.current_state
        
        if current_state == IssueState.ANALYZING_REQUIREMENTS:
            if step_result.confidence_score < context.confidence_threshold:
                return IssueState.REQUIREMENTS_UNCLEAR
            else:
                return IssueState.CREATING_TESTS
                
        elif current_state == IssueState.CREATING_TESTS:
            if step_result.status == "success":
                return IssueState.IMPLEMENTING
            else:
                return IssueState.ANALYZING_REQUIREMENTS
                
        elif current_state == IssueState.IMPLEMENTING:
            if step_result.confidence_score > 0.9 and len(step_result.issues_found) == 0:
                return IssueState.RUNNING_TESTS  # High quality implementation, test it
            elif step_result.confidence_score > 0.8:
                return IssueState.CREATING_PR     # Good implementation, create PR directly
            else:
                return IssueState.FIXING_ISSUES   # Need to fix issues first
                
        # Navigator states removed - skipping review complexity
                
        # Add more state-specific logic...
        
        return IssueState.FAILED  # Default if no valid transition found
```

## PM as Human-AI Bridge

The PM agent serves as the **exclusive interface** between human stakeholders and AI agents:

### Human Interaction Responsibilities
```python
class PMHumanInterface:
    def post_requirements_questions(self, questions: List[str], issue_number: int) -> bool:
        """
        PM posts clarifying questions to GitHub issue when requirements are unclear.
        Transitions issue to WAITING_FOR_REQUIREMENTS_CLARIFICATION state.
        """
        comment = self._format_requirements_questions(questions)
        self.github_service.create_issue_comment(issue_number, comment)
        return True
    
    def process_human_clarification(self, human_response: str, context: WorkflowContext) -> NextAction:
        """
        PM processes human clarification and decides next step.
        Called when issue transitions from WAITING_FOR_REQUIREMENTS_CLARIFICATION to REQUIREMENTS_CLARIFIED.
        """
        clarified_requirements = self._parse_human_response(human_response)
        
        # PM decides whether to proceed with implementation or need more analysis
        if self._requirements_sufficient(clarified_requirements):
            return NextAction(
                action="create_tests",
                target_agent="tester", 
                new_state=IssueState.CREATING_TESTS,
                input_data={"clarified_requirements": clarified_requirements}
            )
        else:
            return NextAction(
                action="analyze_requirements",
                target_agent="analyst",
                new_state=IssueState.ANALYZING_REQUIREMENTS,
                input_data={"human_clarification": clarified_requirements}
            )
    
    def request_human_approval(self, decision_context: Dict, issue_number: int) -> bool:
        """
        PM requests human approval for complex decisions (architecture changes, etc.).
        Transitions issue to WAITING_FOR_HUMAN_INPUT state.
        """
        approval_request = self._format_approval_request(decision_context)
        self.github_service.create_issue_comment(issue_number, approval_request)
        return True
```

### Human Interaction Flow Examples

**Requirements Clarification Flow:**
1. `ANALYZING_REQUIREMENTS` → Analyst finds unclear requirements
2. `REQUIREMENTS_UNCLEAR` → PM decides human input needed  
3. `WAITING_FOR_REQUIREMENTS_CLARIFICATION` → PM posts questions to GitHub issue, stops processing
4. *Human responds to GitHub issue*
5. `REQUIREMENTS_CLARIFIED` → PM processes human response  
6. `CREATING_TESTS` → PM routes to Tester with clarified requirements

**Approval Request Flow:**
1. `REVIEWING_ARCHITECTURE` → Navigator identifies major architectural change needed
2. `WAITING_FOR_HUMAN_INPUT` → PM requests human approval for architecture change
3. *Human approves via GitHub issue comment*
4. `HUMAN_INPUT_RECEIVED` → PM processes approval
5. `IMPLEMENTING` → PM authorizes Developer to proceed with architectural change

### AI Agent Isolation
- **Other agents never interact with humans directly**
- **All human communication goes through PM**
- **Agents focus purely on their technical expertise**
- **PM translates between human language and technical requirements**

This state machine design ensures:
- **Single state execution**: Issue is always in exactly one state
- **Clear ownership**: Each state maps to one agent type
- **Validated transitions**: PM cannot make invalid state transitions  
- **Loop detection**: Prevents infinite cycles
- **Complete traceability**: Full history of state changes with reasons
- **Human-AI separation**: PM is the exclusive human interface layer