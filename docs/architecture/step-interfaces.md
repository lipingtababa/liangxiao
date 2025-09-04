# Step Interface Specifications (Simplified)

## Overview

Simple, clear interfaces for all agents in the Dynamic PM system. Each agent has a specific role and minimal interface.

**Core Principle**: Keep it simple. No complex nested objects, no unnecessary fields.

## Agent Responsibilities

- **Analyst**: Converts issues into acceptance criteria
- **Tester**: Writes test code from acceptance criteria (does NOT run tests)
- **Developer**: Implements features AND runs tests
- **PM**: Orchestrates workflow and handles human interaction

## Universal Interfaces

### StepResult - Output from Any Agent

```python
from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field

class StepResult(BaseModel):
    """Universal output format for all agents."""
    status: Literal["success", "failed", "needs_clarification"]
    agent: str  # Which agent produced this
    output: Dict[str, Any]  # Agent-specific output data
    confidence: float = Field(ge=0.0, le=1.0)
    next_suggestions: List[str] = Field(default_factory=list)
```

### NextAction - PM Decision

```python
class NextAction(BaseModel):
    """PM's decision about what to do next."""
    target_agent: Literal["analyst", "tester", "developer", "pm"]
    input_data: Dict[str, Any]
    reason: str  # Why this decision was made
```

## Analyst Agent

Converts GitHub issues into clear acceptance criteria.

```python
class AnalystInput(BaseModel):
    """Input for Analyst agent."""
    issue_description: str  # The GitHub issue text
    
class AnalystOutput(BaseModel):
    """Output from Analyst agent."""
    acceptance_criteria: List[str]  # What needs to work
    clarification_questions: List[str] = Field(default_factory=list)  # What's unclear
    complexity: Literal["simple", "medium", "complex"]
    effort_estimate: str  # e.g., "2 hours", "1 day"
```

## Tester Agent

Creates test code from acceptance criteria. Does NOT run tests.

```python
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
```

## Developer Agent

Implements features and runs tests. Shows changes as diffs.

```python
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

class CodeChange(BaseModel):
    """A single file change."""
    file_path: str
    diff: str  # Unified diff format (like git diff)
    summary: str  # One-line description
```

## PM Agent

The PM orchestrates everything and interfaces with humans.

```python
class PMEvaluation(BaseModel):
    """PM's evaluation of a step result."""
    step_result: StepResult
    workflow_state: str  # Current state in the workflow
    
    def decide_next_action(self) -> NextAction:
        """Decide what to do next based on the step result."""
        # PM logic here
        pass
    
    def needs_human_input(self) -> bool:
        """Check if human clarification is needed."""
        return self.step_result.status == "needs_clarification"
    
    def create_github_comment(self) -> str:
        """Create a comment for the GitHub issue."""
        # Format questions/status for humans
        pass
```

## Workflow Example

```python
# 1. Analyst processes issue
analyst_input = AnalystInput(
    issue_description="Users can't login with @ in username"
)
analyst_result = analyst.execute(analyst_input)
# Returns: acceptance_criteria, clarification_questions

# 2. PM evaluates and routes to Tester
if analyst_result.clarification_questions:
    # PM posts to GitHub and waits for human response
    pm.post_github_comment(questions)
else:
    # PM sends to Tester
    tester_input = TesterInput(
        acceptance_criteria=analyst_result.output["acceptance_criteria"],
        feature_description="Login with special characters"
    )
    tester_result = tester.execute(tester_input)
    # Returns: test_code, test_file_path

# 3. PM routes to Developer
developer_input = DeveloperInput(
    requirements="Fix login to accept @ in usernames",
    acceptance_criteria=analyst_result.output["acceptance_criteria"],
    test_file_path=tester_result.output["test_file_path"]
)
developer_result = developer.execute(developer_input)
# Returns: changes_made (with diffs), tests_passed, test_output

# 4. PM evaluates and creates PR if tests pass
if developer_result.output["tests_passed"]:
    pm.create_pull_request(developer_result.output["changes_made"])
```

## Key Benefits

1. **Simple**: ~150 lines vs 400+ lines
2. **Clear**: Each agent has one job with minimal interface
3. **No Complexity**: No nested objects, no file passing
4. **Standard Formats**: Uses unified diff format for code changes
5. **Testable**: Clear inputs and outputs for each agent
6. **Human-Friendly**: PM handles all human interaction

## State Management

The PM maintains workflow state separately. States are simple strings like:
- `analyzing_requirements`
- `creating_tests`
- `implementing`
- `waiting_for_human_input`
- `ready_for_pr`

No complex state machine needed - PM decides transitions based on StepResult.