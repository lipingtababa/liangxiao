# Story 2.1: PM Agent Core Implementation ✅ COMPLETED

## Story Details
- **ID**: 2.1
- **Title**: Build Project Manager Agent with LangChain
- **Milestone**: Milestone 2 - Project Manager Agent  
- **Points**: 8
- **Priority**: P0 (Critical Path)
- **Dependencies**: Stories 1.1-1.3 (Foundation complete)
- **Status**: ✅ COMPLETED - Implementation available at `services/orchestrator/agents/pm/`

## Description

### Overview
Implement the Project Manager (PM) Agent using LangChain. This agent is the brain of our multi-agent system, responsible for analyzing GitHub issues, breaking them down into tasks, and orchestrating the workflow. The PM Agent must be smarter than the current monolithic agent that produces disasters like PR #23.

### Why This Is Important
- PM Agent prevents the chaos of unstructured development
- Breaks complex issues into manageable tasks
- Ensures each task has clear requirements
- Coordinates which agents work on what
- Makes go/no-go decisions on quality

### Context
The current system has no intelligence about task decomposition - it tries to solve everything in one shot and fails. The PM Agent will analyze issues intelligently, understand what type of problem it is, and create a structured plan that specialized agents can execute.

## Acceptance Criteria

### Required
- [ ] PM Agent class implemented using LangChain
- [ ] Can analyze GitHub issues and identify type (bug, feature, story, etc.)
- [ ] Generates task breakdown with clear subtasks
- [ ] Each task includes: description, acceptance criteria, assigned agent type
- [ ] Determines task dependencies and ordering
- [ ] Provides complexity estimation for issues
- [ ] Uses GPT-5/Sonnet/Opus models with structured output (JSON)
- [ ] Handles various issue formats and quality levels
- [ ] Logs reasoning for task breakdown decisions
- [ ] Returns structured response that workflow can use
- [ ] Suggested timeline for tasks

## Technical Details

### PM Agent Structure
```python
# agents/project_manager/agent.py
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import json

class Task(BaseModel):
    """Individual task in the breakdown."""
    id: str = Field(description="Unique task identifier")
    title: str = Field(description="Short task title")
    description: str = Field(description="Detailed task description")
    type: Literal["analysis", "implementation", "testing", "documentation"]
    assigned_agent: Literal["analyst", "developer", "tester"]
    dependencies: List[str] = Field(description="IDs of tasks this depends on")
    acceptance_criteria: List[str] = Field(description="What must be true for task completion")
    estimated_complexity: Literal["trivial", "simple", "medium", "complex", "very_complex"]

class IssueAnalysis(BaseModel):
    """Complete analysis of a GitHub issue."""
    issue_type: Literal["bug_fix", "feature", "enhancement", "documentation", "refactor"]
    summary: str = Field(description="Brief summary of what needs to be done")
    complexity: Literal["trivial", "simple", "medium", "complex", "very_complex"]
    risks: List[str] = Field(description="Potential risks or challenges")
    assumptions: List[str] = Field(description="Assumptions made during analysis")
    questions: List[str] = Field(description="Clarifications needed from user")
    
class TaskBreakdown(BaseModel):
    """Complete task breakdown for an issue."""
    analysis: IssueAnalysis
    tasks: List[Task]
    execution_order: List[str] = Field(description="Task IDs in execution order")
    total_estimated_hours: float
    recommended_approach: str

class ProjectManagerAgent:
    """PM Agent that analyzes issues and creates task breakdowns."""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.2,  # Low temperature for consistency
            model_kwargs={"response_format": {"type": "json_object"}}
        )
        self.output_parser = PydanticOutputParser(pydantic_object=TaskBreakdown)
        
    def analyze_issue(self, issue: dict) -> IssueAnalysis:
        """Analyze a GitHub issue to understand what needs to be done."""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are an expert Project Manager for an AI coding team.
                Analyze the GitHub issue and provide a structured analysis.
                
                Consider:
                1. What type of issue is this?
                2. What is the core problem to solve?
                3. How complex is this task?
                4. What risks or challenges exist?
                5. What assumptions are we making?
                6. What questions need clarification?
                
                Be thorough but concise. Remember that simple AI agents will implement this,
                so clarity is crucial.
                
                {format_instructions}
                """
            ),
            ("human", "Issue #{number}: {title}\n\n{body}\n\nLabels: {labels}")
        ])
        
        formatted_prompt = prompt.format_messages(
            format_instructions=self.output_parser.get_format_instructions(),
            number=issue["number"],
            title=issue["title"],
            body=issue.get("body", "No description provided"),
            labels=", ".join([l["name"] for l in issue.get("labels", [])])
        )
        
        response = self.llm(formatted_prompt)
        return self.output_parser.parse(response.content)
    
    def create_task_breakdown(self, issue: dict, analysis: IssueAnalysis) -> TaskBreakdown:
        """Create detailed task breakdown based on analysis."""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are an expert Project Manager creating a task breakdown.
                
                Based on the issue analysis, break down the work into specific tasks.
                Each task should be:
                1. Small enough for one agent to complete
                2. Have clear acceptance criteria
                3. Be assigned to the right agent type
                4. Have dependencies identified
                
                Agent Types:
                - analyst: Requirements, research, documentation
                - developer: Code implementation, bug fixes
                - tester: Test creation, validation
                
                Important: Tasks will be reviewed by a Navigator agent, so include
                review cycles in your planning.
                
                Current issue analysis:
                {analysis}
                
                Create a complete task breakdown that ensures HIGH QUALITY output.
                Remember: we're fixing the problem where our current agent creates
                terrible PRs. Quality over speed!
                
                {format_instructions}
                """
            ),
            ("human", "Create task breakdown for Issue #{number}: {title}")
        ])
        
        formatted_prompt = prompt.format_messages(
            format_instructions=self.output_parser.get_format_instructions(),
            analysis=json.dumps(analysis.model_dump(), indent=2),
            number=issue["number"],
            title=issue["title"]
        )
        
        response = self.llm(formatted_prompt)
        breakdown = self.output_parser.parse(response.content)
        breakdown.analysis = analysis  # Include original analysis
        
        return breakdown
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[str]:
        """Determine optimal task execution order."""
        # Topological sort based on dependencies
        # Implementation details...
        pass
    
    def estimate_complexity(self, issue: dict) -> str:
        """Quick complexity estimation for an issue."""
        # Quick assessment without full analysis
        # Useful for filtering or quick decisions
        pass
```

### Integration with Workflow
```python
# workflows/nodes/pm_agent_nodes.py
from agents.project_manager.agent import ProjectManagerAgent
import logging

logger = logging.getLogger(__name__)
pm_agent = ProjectManagerAgent()

async def analyze_issue_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """PM Agent analyzes the issue."""
    logger.info(f"PM analyzing issue #{state['issue_number']}")
    
    try:
        # Create issue dict for PM agent
        issue_data = {
            "number": state["issue_number"],
            "title": state["issue_title"],
            "body": state["issue_body"],
            "labels": state.get("issue_labels", [])
        }
        
        # Analyze issue
        analysis = pm_agent.analyze_issue(issue_data)
        
        # Store analysis in state
        state["analysis"] = analysis.model_dump()
        state["status"] = WorkflowStatus.ANALYZING
        state["updated_at"] = datetime.now()
        
        logger.info(f"Analysis complete: {analysis.issue_type}, {analysis.complexity}")
        
    except Exception as e:
        logger.error(f"PM analysis failed: {e}")
        state["errors"].append(f"Analysis failed: {str(e)}")
        state["status"] = WorkflowStatus.FAILED
    
    return state

async def plan_tasks_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """PM Agent creates task breakdown."""
    logger.info(f"PM planning tasks for issue #{state['issue_number']}")
    
    try:
        issue_data = {
            "number": state["issue_number"],
            "title": state["issue_title"],
            "body": state["issue_body"]
        }
        
        # Create task breakdown
        analysis = IssueAnalysis.model_validate(state["analysis"])
        breakdown = pm_agent.create_task_breakdown(issue_data, analysis)
        
        # Store tasks in state
        state["tasks"] = [task.model_dump() for task in breakdown.tasks]
        state["task_execution_order"] = breakdown.execution_order
        state["status"] = WorkflowStatus.PLANNING
        state["updated_at"] = datetime.now()
        
        logger.info(f"Created {len(breakdown.tasks)} tasks")
        
        # Set first task as current
        if breakdown.tasks:
            state["current_task"] = breakdown.tasks[0].model_dump()
            state["current_task_index"] = 0
        
    except Exception as e:
        logger.error(f"Task planning failed: {e}")
        state["errors"].append(f"Planning failed: {str(e)}")
        state["status"] = WorkflowStatus.FAILED
    
    return state
```

### Example Task Breakdown Output
```json
{
  "analysis": {
    "issue_type": "bug_fix",
    "summary": "Button click handler not working on mobile devices",
    "complexity": "medium",
    "risks": ["Cross-browser compatibility", "Touch event handling"],
    "assumptions": ["Issue only affects mobile Safari and Chrome"],
    "questions": ["Which specific mobile devices?", "Any error messages in console?"]
  },
  "tasks": [
    {
      "id": "task-001",
      "title": "Analyze mobile event handling",
      "description": "Research the current button implementation and identify why mobile events fail",
      "type": "analysis",
      "assigned_agent": "analyst",
      "dependencies": [],
      "acceptance_criteria": [
        "Root cause identified",
        "Affected code sections documented",
        "Solution approach recommended"
      ],
      "estimated_complexity": "simple"
    },
    {
      "id": "task-002", 
      "title": "Implement mobile-compatible click handler",
      "description": "Fix the button click handler to work on mobile devices",
      "type": "implementation",
      "assigned_agent": "developer",
      "dependencies": ["task-001"],
      "acceptance_criteria": [
        "Click handler works on iOS Safari",
        "Click handler works on Android Chrome",
        "No regression on desktop browsers",
        "Touch events properly handled"
      ],
      "estimated_complexity": "medium"
    },
    {
      "id": "task-003",
      "title": "Create mobile event handling tests",
      "description": "Write tests to verify mobile click handling works correctly",
      "type": "testing",
      "assigned_agent": "tester",
      "dependencies": ["task-002"],
      "acceptance_criteria": [
        "Unit tests for touch events",
        "Integration tests for button component",
        "Cross-browser test scenarios documented"
      ],
      "estimated_complexity": "simple"
    }
  ],
  "execution_order": ["task-001", "task-002", "task-003"],
  "total_estimated_hours": 4.5,
  "recommended_approach": "Fix the root cause in the event handler, not workarounds"
}
```

## Testing Requirements

### Unit Tests
```python
# tests/test_pm_agent.py
import pytest
from agents.project_manager.agent import ProjectManagerAgent

def test_pm_agent_initialization():
    agent = ProjectManagerAgent()
    assert agent.llm is not None

def test_issue_analysis():
    agent = ProjectManagerAgent()
    issue = {
        "number": 1,
        "title": "Button not working",
        "body": "The submit button doesn't work on mobile",
        "labels": [{"name": "bug"}]
    }
    
    analysis = agent.analyze_issue(issue)
    assert analysis.issue_type in ["bug_fix", "feature", "enhancement"]
    assert analysis.complexity in ["trivial", "simple", "medium", "complex"]

def test_task_breakdown():
    agent = ProjectManagerAgent()
    # Test with sample issue and analysis
    # Verify tasks are created properly
    # Check dependencies are valid
```

### Integration Tests  
```python
# tests/integration/test_pm_workflow.py
async def test_pm_in_workflow():
    """Test PM agent within workflow context."""
    # Create workflow
    # Run PM nodes
    # Verify state updates correctly
```

## Dependencies & Risks

### Prerequisites
- LangChain installed and configured
- OpenAI API key with GPT-4 access
- Workflow engine ready to integrate

### Risks
- **Hallucination**: PM might create unrealistic tasks
- **Over-engineering**: Too many tasks for simple issues
- **Under-specification**: Tasks too vague for agents
- **API costs**: Complex issues might use many tokens

### Mitigations
- Structured output format enforces consistency
- Few-shot examples in prompts
- Validation of task breakdown
- Token limits and prompt optimization

## Definition of Done

1. ✅ PM Agent class implemented
2. ✅ Issue analysis working with real issues
3. ✅ Task breakdown generates valid tasks
4. ✅ Integration with workflow nodes
5. ✅ Structured output parsing works
6. ✅ Error handling for API failures
7. ✅ Unit tests passing
8. ✅ Logs provide clear reasoning
9. ✅ Can handle various issue types

## Implementation Notes for AI Agents

### DO
- Use structured outputs (Pydantic models)
- Include reasoning in responses
- Be specific in task descriptions
- Consider edge cases in analysis
- Validate all dependencies exist

### DON'T
- Don't create circular dependencies
- Don't assign tasks to wrong agent types
- Don't skip error handling
- Don't make tasks too large
- Don't ignore issue context

### Common Pitfalls to Avoid
1. Tasks without clear acceptance criteria
2. Missing dependencies between tasks
3. Assigning coding tasks to analyst agent
4. Creating too many micro-tasks
5. Ignoring issue labels and context

## Success Example

When complete:
```python
# PM analyzes issue and creates tasks
issue = {"number": 23, "title": "Fix README", "body": "Remove one phrase"}
analysis = pm_agent.analyze_issue(issue)
breakdown = pm_agent.create_task_breakdown(issue, analysis)

# Should create simple, clear tasks
assert len(breakdown.tasks) <= 3  # Don't overcomplicate!
assert breakdown.tasks[0].assigned_agent == "analyst"  # Read first!
```

## Next Story
Once this story is complete, proceed to [Story 2.2: PM Decision Framework](story-2.2-pm-decisions.md)