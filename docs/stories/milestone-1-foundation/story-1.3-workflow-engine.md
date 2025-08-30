# Story 1.3: LangGraph Workflow Engine Setup ✅ COMPLETED

## Story Details
- **ID**: 1.3  
- **Title**: Implement Basic LangGraph Workflow Engine
- **Milestone**: Milestone 1 - Foundation & Basic Workflow
- **Points**: 8
- **Priority**: P0 (Critical Path)
- **Dependencies**: Story 1.1 (Python Setup), Story 1.2 (Webhook)
- **Status**: ✅ COMPLETED - Implementation available at `services/orchestrator/workflows/`

## Description

### Overview
Implement the core workflow orchestration engine using LangGraph that will manage the entire issue processing lifecycle. This engine will handle state transitions, checkpointing, and coordination between different agents. It forms the backbone of our multi-agent system.

### Why This Is Important
- Provides structured state management for complex workflows
- Enables workflow persistence and recovery
- Allows clear tracking of issue processing stages
- Foundation for agent coordination and task distribution

### Context
Unlike the current monolithic agent that tries to do everything at once (and fails spectacularly - see PR #23), this workflow engine will orchestrate multiple specialized agents through defined states, ensuring quality at each step.

## Acceptance Criteria

### Required
- [ ] LangGraph workflow with defined states (PENDING, ANALYZING, DEVELOPING, etc.)
- [ ] SQLite checkpointing configured for state persistence
- [ ] State transitions follow defined rules (can't skip states)
- [ ] Workflow can be started from webhook payload
- [ ] Workflow state can be retrieved by issue number
- [ ] Checkpointing saves state after each node execution
- [ ] Support for conditional edges based on state
- [ ] Basic workflow can complete end-to-end (even if nodes are stubs)
- [ ] Workflow execution is async and non-blocking
- [ ] Error states handled appropriately

## Technical Details

### Workflow State Definition
```python
# workflows/issue_workflow.py
from typing import TypedDict, List, Optional, Literal
from langgraph.graph import StateGraph, END
from datetime import datetime

class WorkflowStatus(str, Enum):
    """Clear, descriptive workflow status names."""
    PENDING = "PENDING"                       # Issue received, waiting to start
    ANALYZING = "ANALYZING"                   # PM Agent analyzing requirements  
    PLANNING = "PLANNING"                     # Creating implementation plan
    DEVELOPING = "DEVELOPING"                 # Developer Agent implementing solution
    REVIEWING = "REVIEWING"                   # Navigator Agent reviewing work
    NEEDS_REVISION = "NEEDS_REVISION"        # Needs changes based on review
    TESTING = "TESTING"                      # Tester Agent creating/running tests
    PR_CREATING = "PR_CREATING"              # Creating pull request
    COMPLETED = "COMPLETED"                  # Successfully completed
    FAILED = "FAILED"                        # Failed with unrecoverable error

class IssueWorkflowState(TypedDict):
    # Issue Information
    issue_number: int
    issue_title: str
    issue_body: str
    issue_url: str
    repository: str
    
    # Workflow Status
    status: WorkflowStatus
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    # Processing Data
    analysis: Optional[dict]  # PM analysis result
    tasks: List[dict]  # Task breakdown
    current_task: Optional[dict]  # Currently executing task
    current_iteration: int  # Iteration count for current task
    max_iterations: int  # Maximum allowed iterations
    
    # Results
    artifacts: List[dict]  # Generated code, tests, docs
    errors: List[str]  # Error messages
    pr_number: Optional[int]  # Created PR number
    
    # Control Flow
    next_step: Optional[str]  # Directive for next node
    should_continue: bool  # Whether to continue processing
```

### Workflow Graph Definition
```python
# workflows/issue_workflow.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import os

def create_issue_workflow():
    """Create the main issue processing workflow."""
    
    # Initialize workflow with state class
    workflow = StateGraph(IssueWorkflowState)
    
    # Add nodes (these will be stubs initially, replaced in later stories)
    workflow.add_node("receive_issue", receive_issue_node)
    workflow.add_node("analyze_issue", analyze_issue_node)
    workflow.add_node("plan_tasks", plan_tasks_node)
    workflow.add_node("execute_task", execute_task_node)
    workflow.add_node("review_task", review_task_node)
    workflow.add_node("test_solution", test_solution_node)
    workflow.add_node("create_pr", create_pr_node)
    workflow.add_node("handle_error", handle_error_node)
    
    # Add edges - linear flow initially
    workflow.add_edge("receive_issue", "analyze_issue")
    workflow.add_edge("analyze_issue", "plan_tasks")
    workflow.add_edge("plan_tasks", "execute_task")
    workflow.add_edge("execute_task", "review_task")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "review_task",
        review_decision,  # Function that returns next node
        {
            "iterate": "execute_task",  # Need more work
            "continue": "test_solution",  # Move forward
            "error": "handle_error"  # Something went wrong
        }
    )
    
    workflow.add_edge("test_solution", "create_pr")
    workflow.add_edge("create_pr", END)
    workflow.add_edge("handle_error", END)
    
    # Set entry point
    workflow.set_entry_point("receive_issue")
    
    # Add checkpointing
    checkpointer = SqliteSaver.from_conn_string("data/workflows.db")
    
    # Compile workflow with checkpointing
    return workflow.compile(checkpointer=checkpointer)
```

### Node Implementations (Stubs for Now)
```python
# workflows/nodes/__init__.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def receive_issue_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Receive and validate issue."""
    logger.info(f"Receiving issue #{state['issue_number']}")
    state["status"] = WorkflowStatus.TODO
    state["started_at"] = datetime.now()
    state["updated_at"] = datetime.now()
    state["should_continue"] = True
    return state

async def analyze_issue_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Analyze issue (stub - will be PM agent)."""
    logger.info(f"Analyzing issue #{state['issue_number']}")
    state["status"] = WorkflowStatus.ANALYZING
    state["updated_at"] = datetime.now()
    
    # Stub analysis
    state["analysis"] = {
        "type": "bug_fix",
        "complexity": "medium",
        "requires_agents": ["developer", "tester"]
    }
    return state

async def plan_tasks_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Create task plan (stub - will be PM agent)."""
    logger.info(f"Planning tasks for issue #{state['issue_number']}")
    state["status"] = WorkflowStatus.PLANNING
    state["updated_at"] = datetime.now()
    
    # Stub task plan
    state["tasks"] = [
        {
            "id": "task-1",
            "type": "implementation",
            "description": "Fix the bug",
            "agent": "developer"
        }
    ]
    state["current_task"] = state["tasks"][0] if state["tasks"] else None
    return state

async def execute_task_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Execute current task (stub - will call agent pairs)."""
    logger.info(f"Executing task for issue #{state['issue_number']}")
    state["status"] = WorkflowStatus.DEVELOPING
    state["updated_at"] = datetime.now()
    state["current_iteration"] += 1
    
    # Stub execution
    state["artifacts"].append({
        "type": "code",
        "content": "# Fixed the bug",
        "iteration": state["current_iteration"]
    })
    return state

async def review_task_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Review task results (stub - will be Navigator)."""
    logger.info(f"Reviewing task for issue #{state['issue_number']}")
    state["status"] = WorkflowStatus.IN_REVIEW
    state["updated_at"] = datetime.now()
    
    # Stub review - always pass for now
    state["next_step"] = "continue"
    return state

def review_decision(state: IssueWorkflowState) -> str:
    """Decide next step based on review."""
    if state.get("next_step") == "iterate" and state["current_iteration"] < state["max_iterations"]:
        return "iterate"
    elif state.get("next_step") == "error":
        return "error"
    else:
        return "continue"
```

### Workflow Orchestrator
```python
# workflows/orchestrator.py
from typing import Optional
import asyncio
from workflows.issue_workflow import create_issue_workflow
from models.github import IssueEvent
import logging

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """Orchestrates issue processing workflows."""
    
    def __init__(self):
        self.workflow = create_issue_workflow()
        self.active_workflows = {}
    
    async def start_workflow(self, issue_event: IssueEvent) -> str:
        """Start a new workflow for an issue."""
        workflow_id = f"issue-{issue_event.issue.number}"
        
        # Initialize state
        initial_state = IssueWorkflowState(
            issue_number=issue_event.issue.number,
            issue_title=issue_event.issue.title,
            issue_body=issue_event.issue.body or "",
            issue_url=issue_event.issue.html_url,
            repository=issue_event.repository.full_name,
            status=WorkflowStatus.TODO,
            started_at=datetime.now(),
            updated_at=datetime.now(),
            completed_at=None,
            analysis=None,
            tasks=[],
            current_task=None,
            current_iteration=0,
            max_iterations=3,
            artifacts=[],
            errors=[],
            pr_number=None,
            next_step=None,
            should_continue=True
        )
        
        # Start workflow asynchronously
        config = {"configurable": {"thread_id": workflow_id}}
        
        # Run in background
        asyncio.create_task(self._run_workflow(workflow_id, initial_state, config))
        
        logger.info(f"Started workflow {workflow_id}")
        return workflow_id
    
    async def _run_workflow(self, workflow_id: str, state: dict, config: dict):
        """Run workflow to completion."""
        try:
            self.active_workflows[workflow_id] = "running"
            result = await self.workflow.ainvoke(state, config)
            logger.info(f"Workflow {workflow_id} completed successfully")
            self.active_workflows[workflow_id] = "completed"
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            self.active_workflows[workflow_id] = "failed"
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[dict]:
        """Retrieve current workflow state."""
        config = {"configurable": {"thread_id": workflow_id}}
        state = await self.workflow.aget_state(config)
        return state.values if state else None
```

### Integration with Webhook
```python
# api/webhooks.py (update)
from workflows.orchestrator import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()

async def handle_issue_event(payload: dict):
    """Handle issue events with workflow."""
    try:
        event = IssueEvent.model_validate(payload)
        
        if event.action not in ["opened", "edited", "labeled", "assigned"]:
            return {"status": "ignored", "action": event.action}
        
        # Start workflow
        workflow_id = await orchestrator.start_workflow(event)
        
        return {
            "status": "workflow_started",
            "workflow_id": workflow_id,
            "issue": event.issue.number
        }
        
    except Exception as e:
        logger.error(f"Failed to start workflow: {e}")
        raise HTTPException(status_code=500, detail="Workflow failed to start")
```

## Testing Requirements

### Unit Tests
```python
# tests/test_workflow.py
import pytest
from workflows.issue_workflow import create_issue_workflow

@pytest.mark.asyncio
async def test_workflow_creation():
    """Test workflow can be created."""
    workflow = create_issue_workflow()
    assert workflow is not None

@pytest.mark.asyncio  
async def test_workflow_execution():
    """Test basic workflow execution."""
    workflow = create_issue_workflow()
    
    initial_state = {
        "issue_number": 1,
        "issue_title": "Test Issue",
        "issue_body": "Test body",
        # ... other required fields
    }
    
    result = await workflow.ainvoke(initial_state)
    assert result["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]

@pytest.mark.asyncio
async def test_workflow_checkpointing():
    """Test state persistence."""
    workflow = create_issue_workflow()
    config = {"configurable": {"thread_id": "test-1"}}
    
    # Run partial workflow
    # Retrieve state
    # Verify state persisted
```

### Manual Testing Checklist
- [ ] Start workflow from webhook
- [ ] Verify SQLite database created
- [ ] Check state persisted between nodes
- [ ] Verify workflow completes end-to-end
- [ ] Test workflow recovery after error
- [ ] Check conditional branching works

## Dependencies & Risks

### Prerequisites
- Story 1.1 and 1.2 completed
- SQLite available (comes with Python)
- Basic understanding of state machines

### Risks
- **State corruption**: Improper checkpointing could lose state
- **Infinite loops**: Conditional edges might create loops
- **Memory leaks**: Long-running workflows might accumulate state
- **Checkpoint size**: Large artifacts could bloat database

### Mitigations
- Transaction boundaries for checkpoint writes
- Maximum iteration limits
- State cleanup after completion
- Artifact storage separate from state

## Definition of Done

1. ✅ All acceptance criteria met
2. ✅ Workflow executes from start to end
3. ✅ State persisted in SQLite
4. ✅ Conditional branching works
5. ✅ Can retrieve workflow state
6. ✅ Error handling in place
7. ✅ Unit tests pass
8. ✅ Integrated with webhook
9. ✅ Logging provides visibility

## Implementation Notes for AI Agents

### DO
- Keep nodes small and focused
- Always update state timestamps
- Log state transitions
- Handle exceptions in nodes
- Use type hints for state

### DON'T
- Don't put business logic in edge functions
- Don't modify state outside nodes
- Don't skip checkpointing
- Don't create infinite loops
- Don't block on long operations

### Common Pitfalls to Avoid
1. Forgetting to return state from nodes
2. Modifying state in place without returning
3. Not handling async properly
4. Circular dependencies in conditional edges
5. Not setting initial state properly

## Success Example

When complete:
```python
# Workflow processes issue automatically
POST /webhook/github -> Workflow starts -> Nodes execute -> State persisted

# Check workflow state
workflow_id = "issue-123"
state = await orchestrator.get_workflow_state(workflow_id)
print(f"Status: {state['status']}")
print(f"Current task: {state['current_task']}")
```

## Next Story
Once this story is complete, proceed to [Story 1.4: GitHub API Integration](story-1.4-github-integration.md)