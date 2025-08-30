# Story 7.1: End-to-End Workflow

## Story Details
- **ID**: 7.1
- **Title**: Integrate All Agents in Complete Workflow
- **Milestone**: Milestone 7 - Full Workflow Integration
- **Points**: 13
- **Priority**: P0 (Critical Path)
- **Dependencies**: Stories 2.1 (PM), 3.1 (Navigator), 4.1 (Developer), 5.1 (Analyst), 6.1 (Tester), 4.2 (Task Pair)

## Description

### Overview
Integrate all agents (PM, Analyst, Developer, Tester, Navigator) into a complete, production-ready workflow that processes GitHub issues from start to finish. This story creates the orchestrated system that prevents disasters like PR #23 through proper task decomposition and quality gates.

### Why This Is Important
- This is the culmination of all previous work
- Proves the multi-agent system works end-to-end
- Replaces the broken single-agent system
- Delivers the quality improvement we've been building towards
- Enables confident production deployment

### Context
We've built individual agents and the task pair system. Now we need to orchestrate them into a complete workflow that can handle any GitHub issue with high quality output. The workflow must be robust, observable, and produce consistently good results.

## Acceptance Criteria

### Required
- [ ] Complete workflow processes issues from webhook to PR creation
- [ ] PM Agent analyzes issues and creates task breakdown
- [ ] Each task executed by appropriate agent pair (Analyst+Navigator, Developer+Navigator, Tester+Navigator)
- [ ] Task dependencies respected (Analyst → Developer → Tester)
- [ ] Iteration cycles work for all agent pairs
- [ ] Navigator reviews prevent bad code from progressing
- [ ] Failed tasks handled gracefully without breaking workflow
- [ ] All artifacts (code, tests, docs) collected and integrated
- [ ] PR created with comprehensive description and all changes
- [ ] Issue commented with progress updates throughout
- [ ] Workflow state persisted and recoverable
- [ ] Complete workflow completes in <10 minutes for typical issues


## Technical Details

### Enhanced Workflow States
```python
# workflows/issue_workflow.py (complete version)
from langgraph.graph import StateGraph, END
from datetime import datetime
from typing import TypedDict, List, Optional, Dict, Any
from enum import Enum

class WorkflowStatus(str, Enum):
    RECEIVED = "RECEIVED"           # Issue just received
    PM_ANALYZING = "PM_ANALYZING"   # PM analyzing issue
    PLANNING = "PLANNING"           # PM creating task plan
    TASKS_QUEUED = "TASKS_QUEUED"  # Tasks ready for execution
    ANALYZING = "ANALYZING"         # Analyst working
    DEVELOPING = "DEVELOPING"       # Developer working
    TESTING = "TESTING"             # Tester working
    REVIEWING = "REVIEWING"         # Navigator reviewing
    ITERATING = "ITERATING"         # Agent responding to feedback
    INTEGRATING = "INTEGRATING"     # Combining all work
    PR_CREATING = "PR_CREATING"     # Creating pull request
    COMPLETED = "COMPLETED"         # All done successfully
    FAILED = "FAILED"              # Workflow failed
    BLOCKED = "BLOCKED"            # Waiting for external input

class IssueWorkflowState(TypedDict):
    # Issue Information
    issue_number: int
    issue_title: str
    issue_body: str
    issue_url: str
    repository: str
    
    # Workflow Control
    status: WorkflowStatus
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    should_continue: bool
    
    # PM Analysis
    issue_analysis: Optional[Dict[str, Any]]  # PM's issue analysis
    task_breakdown: List[Dict[str, Any]]      # List of tasks from PM
    execution_plan: List[str]                 # Task execution order
    
    # Task Execution
    current_task_index: int                   # Which task we're on
    current_task: Optional[Dict[str, Any]]    # Current task details
    completed_tasks: List[str]                # IDs of completed tasks
    failed_tasks: List[str]                   # IDs of failed tasks
    task_results: List[Dict[str, Any]]        # Results from each task
    
    # Artifacts and Results
    analysis_artifacts: List[Dict[str, Any]]  # Requirements, docs
    code_artifacts: List[Dict[str, Any]]      # Generated code
    test_artifacts: List[Dict[str, Any]]      # Generated tests
    all_artifacts: List[Dict[str, Any]]       # Combined artifacts
    
    # Progress Tracking
    progress_percentage: float                # 0.0 to 1.0
    current_step_description: str            # Human readable current step
    errors: List[str]                        # Error messages
    warnings: List[str]                      # Warning messages
    
    # Final Results
    pr_number: Optional[int]                 # Created PR number
    pr_url: Optional[str]                    # PR URL
    success_summary: Optional[str]           # What was accomplished
```

### Complete Workflow Definition
```python
def create_complete_issue_workflow():
    """Create the complete end-to-end workflow."""
    
    workflow = StateGraph(IssueWorkflowState)
    
    # Add all nodes
    workflow.add_node("receive_issue", receive_issue_node)
    workflow.add_node("pm_analyze", pm_analyze_node)
    workflow.add_node("pm_plan_tasks", pm_plan_tasks_node)
    workflow.add_node("execute_task_pair", execute_task_pair_node)
    workflow.add_node("check_task_completion", check_task_completion_node)
    workflow.add_node("integrate_artifacts", integrate_artifacts_node)
    workflow.add_node("create_pr", create_pr_node)
    workflow.add_node("handle_failure", handle_failure_node)
    workflow.add_node("complete_workflow", complete_workflow_node)
    
    # Linear flow for main path
    workflow.add_edge("receive_issue", "pm_analyze")
    workflow.add_edge("pm_analyze", "pm_plan_tasks")
    workflow.add_edge("pm_plan_tasks", "execute_task_pair")
    
    # Task execution loop
    workflow.add_conditional_edges(
        "execute_task_pair",
        after_task_execution,
        {
            "next_task": "execute_task_pair",     # More tasks to do
            "all_complete": "check_task_completion", # All tasks done
            "task_failed": "handle_failure"       # Task failed critically
        }
    )
    
    # After all tasks
    workflow.add_conditional_edges(
        "check_task_completion",
        check_overall_success,
        {
            "success": "integrate_artifacts",
            "partial": "integrate_artifacts",  # Use what we have
            "failure": "handle_failure"
        }
    )
    
    workflow.add_edge("integrate_artifacts", "create_pr")
    workflow.add_edge("create_pr", "complete_workflow")
    workflow.add_edge("complete_workflow", END)
    workflow.add_edge("handle_failure", END)
    
    workflow.set_entry_point("receive_issue")
    
    # Add checkpointing
    checkpointer = SqliteSaver.from_conn_string("data/workflows.db")
    return workflow.compile(checkpointer=checkpointer)
```

### Enhanced Node Implementations
```python
# workflows/nodes/complete_nodes.py
import logging
from datetime import datetime
from agents.project_manager.agent import ProjectManagerAgent
from agents.pairs.task_pair import TaskPair
from agents.analyst.agent import AnalystAgent
from agents.developer.agent import DeveloperAgent
from agents.tester.agent import TesterAgent
from agents.navigator.agent import NavigatorAgent
from services.github_service import github_service

logger = logging.getLogger(__name__)

pm_agent = ProjectManagerAgent()

async def pm_analyze_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """PM Agent analyzes the issue completely."""
    logger.info(f"PM analyzing issue #{state['issue_number']}")
    
    state["status"] = WorkflowStatus.PM_ANALYZING
    state["current_step_description"] = "Project Manager analyzing issue"
    state["updated_at"] = datetime.now()
    
    try:
        # Create issue dict for PM
        issue_data = {
            "number": state["issue_number"],
            "title": state["issue_title"],
            "body": state["issue_body"],
            "url": state["issue_url"]
        }
        
        # PM analyzes issue
        analysis = await pm_agent.analyze_issue(issue_data)
        state["issue_analysis"] = analysis.model_dump()
        
        # Update progress
        state["progress_percentage"] = 0.1
        
        # Comment on issue with analysis
        await github_service.create_issue_comment(
            state["issue_number"],
            f"🤖 **Analysis Complete**\n\n"
            f"**Type**: {analysis.issue_type}\n"
            f"**Complexity**: {analysis.complexity}\n"
            f"**Summary**: {analysis.summary}\n\n"
            f"Creating task plan..."
        )
        
        logger.info(f"Analysis complete: {analysis.issue_type}, {analysis.complexity}")
        
    except Exception as e:
        logger.error(f"PM analysis failed: {e}")
        state["errors"].append(f"PM analysis failed: {str(e)}")
        state["status"] = WorkflowStatus.FAILED
        state["should_continue"] = False
    
    return state

async def pm_plan_tasks_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """PM Agent creates comprehensive task plan."""
    logger.info(f"PM planning tasks for issue #{state['issue_number']}")
    
    state["status"] = WorkflowStatus.PLANNING
    state["current_step_description"] = "Creating task breakdown"
    state["updated_at"] = datetime.now()
    
    try:
        issue_data = {
            "number": state["issue_number"],
            "title": state["issue_title"],
            "body": state["issue_body"]
        }
        
        analysis = IssueAnalysis.model_validate(state["issue_analysis"])
        breakdown = await pm_agent.create_task_breakdown(issue_data, analysis)
        
        # Store task plan
        state["task_breakdown"] = [task.model_dump() for task in breakdown.tasks]
        state["execution_plan"] = breakdown.execution_order
        state["current_task_index"] = 0
        
        # Set first task
        if breakdown.tasks:
            state["current_task"] = breakdown.tasks[0].model_dump()
        
        state["progress_percentage"] = 0.2
        state["status"] = WorkflowStatus.TASKS_QUEUED
        
        # Comment with task plan
        task_list = "\n".join([
            f"{i+1}. **{task.title}** ({task.assigned_agent})"
            for i, task in enumerate(breakdown.tasks)
        ])
        
        await github_service.create_issue_comment(
            state["issue_number"],
            f"📋 **Task Plan Created**\n\n"
            f"{task_list}\n\n"
            f"**Estimated time**: {breakdown.total_estimated_hours} hours\n"
            f"Starting execution..."
        )
        
        logger.info(f"Created {len(breakdown.tasks)} tasks")
        
    except Exception as e:
        logger.error(f"Task planning failed: {e}")
        state["errors"].append(f"Planning failed: {str(e)}")
        state["status"] = WorkflowStatus.FAILED
    
    return state

async def execute_task_pair_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Execute current task with appropriate agent pair."""
    
    if not state["current_task"]:
        logger.warning("No current task to execute")
        return state
    
    current_task = state["current_task"]
    task_id = current_task["id"]
    agent_type = current_task["assigned_agent"]
    
    logger.info(f"Executing task {task_id} with {agent_type} pair")
    
    # Update status based on agent type
    status_map = {
        "analyst": WorkflowStatus.ANALYZING,
        "developer": WorkflowStatus.DEVELOPING,
        "tester": WorkflowStatus.TESTING
    }
    state["status"] = status_map.get(agent_type, WorkflowStatus.DEVELOPING)
    state["current_step_description"] = f"Agent pair working on: {current_task['title']}"
    
    try:
        # Create appropriate pair
        if agent_type == "analyst":
            tasker = AnalystAgent()
            navigator = NavigatorAgent(specialty="requirements_review")
        elif agent_type == "developer":
            tasker = DeveloperAgent()
            navigator = NavigatorAgent(specialty="code_review")
        else:  # tester
            tasker = TesterAgent()
            navigator = NavigatorAgent(specialty="test_review")
        
        # Create task pair
        pair = TaskPair(
            tasker_agent=tasker,
            navigator_agent=navigator,
            max_iterations=3
        )
        
        # Execute task
        result = await pair.execute_task(
            task=current_task,
            context={
                "repository": state["repository"],
                "issue": {
                    "number": state["issue_number"],
                    "title": state["issue_title"],
                    "body": state["issue_body"]
                },
                "completed_tasks": state["completed_tasks"],
                "analysis": state["issue_analysis"]
            }
        )
        
        # Store result
        state["task_results"].append(result.model_dump())
        
        if result.success:
            # Task succeeded
            state["completed_tasks"].append(task_id)
            
            # Store artifacts by type
            if result.final_output:
                artifacts = result.final_output.get("artifacts", [])
                for artifact in artifacts:
                    if artifact.get("type") == "requirements":
                        state["analysis_artifacts"].append(artifact)
                    elif artifact.get("type") == "code":
                        state["code_artifacts"].append(artifact)
                    elif artifact.get("type") == "test":
                        state["test_artifacts"].append(artifact)
                    
                    state["all_artifacts"].append(artifact)
            
            logger.info(f"Task {task_id} completed successfully in {len(result.iterations)} iterations")
            
        else:
            # Task failed
            state["failed_tasks"].append(task_id)
            state["errors"].append(f"Task {task_id} failed: {result.failure_reason}")
            logger.error(f"Task {task_id} failed after {len(result.iterations)} iterations")
        
        # Update progress
        completed_count = len(state["completed_tasks"])
        total_count = len(state["task_breakdown"])
        state["progress_percentage"] = 0.2 + (completed_count / total_count * 0.6)
        
        state["updated_at"] = datetime.now()
        
    except Exception as e:
        logger.error(f"Task pair execution failed: {e}")
        state["errors"].append(f"Task execution failed: {str(e)}")
        state["failed_tasks"].append(task_id)
    
    return state

def after_task_execution(state: IssueWorkflowState) -> str:
    """Decide what to do after task execution."""
    
    current_index = state["current_task_index"]
    total_tasks = len(state["task_breakdown"])
    
    # Check if current task failed critically
    if state["current_task"] and state["current_task"]["id"] in state["failed_tasks"]:
        # Check if this was a critical task that blocks others
        if state["current_task"].get("critical", False):
            return "task_failed"
    
    # Move to next task
    next_index = current_index + 1
    
    if next_index >= total_tasks:
        return "all_complete"
    
    # Set up next task
    state["current_task_index"] = next_index
    state["current_task"] = state["task_breakdown"][next_index]
    
    return "next_task"

def check_overall_success(state: IssueWorkflowState) -> str:
    """Check if workflow succeeded overall."""
    
    total_tasks = len(state["task_breakdown"])
    completed_tasks = len(state["completed_tasks"])
    failed_tasks = len(state["failed_tasks"])
    
    if completed_tasks == total_tasks:
        return "success"
    elif completed_tasks > 0 and failed_tasks < total_tasks / 2:
        return "partial"  # Some success
    else:
        return "failure"

async def integrate_artifacts_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Combine all artifacts into coherent solution."""
    logger.info(f"Integrating artifacts for issue #{state['issue_number']}")
    
    state["status"] = WorkflowStatus.INTEGRATING
    state["current_step_description"] = "Integrating all work products"
    state["progress_percentage"] = 0.85
    
    # Group artifacts by type
    code_files = []
    test_files = []
    docs = []
    
    for artifact in state["all_artifacts"]:
        if artifact["type"] == "code":
            code_files.append(artifact)
        elif artifact["type"] == "test":
            test_files.append(artifact)
        else:
            docs.append(artifact)
    
    logger.info(f"Integrated {len(code_files)} code files, {len(test_files)} test files, {len(docs)} docs")
    
    state["updated_at"] = datetime.now()
    return state

async def create_pr_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Create pull request with all changes."""
    logger.info(f"Creating PR for issue #{state['issue_number']}")
    
    state["status"] = WorkflowStatus.PR_CREATING
    state["current_step_description"] = "Creating pull request"
    state["progress_percentage"] = 0.9
    
    try:
        # Create branch
        branch_name = f"ai-fix-issue-{state['issue_number']}"
        github_service.create_branch(branch_name)
        
        # Apply all file changes
        changes = []
        for artifact in state["all_artifacts"]:
            if artifact.get("path"):
                changes.append({
                    "path": artifact["path"],
                    "content": artifact["content"],
                    "action": artifact.get("action", "update")
                })
        
        if changes:
            github_service.apply_file_changes(
                branch=branch_name,
                changes=changes,
                commit_message=f"AI Fix: {state['issue_title']} (#{state['issue_number']})"
            )
            
            # Generate comprehensive PR description
            pr_description = generate_comprehensive_pr_description(state)
            
            # Create PR
            pr = github_service.create_pull_request(
                title=f"Fix: {state['issue_title']} (#{state['issue_number']})",
                body=pr_description,
                head_branch=branch_name
            )
            
            if pr:
                state["pr_number"] = pr.number
                state["pr_url"] = pr.html_url
                state["success_summary"] = f"Created PR #{pr.number} with {len(changes)} file changes"
                
                logger.info(f"Created PR #{pr.number}: {pr.html_url}")
            else:
                raise Exception("Failed to create pull request")
        else:
            raise Exception("No changes to commit")
        
    except Exception as e:
        logger.error(f"PR creation failed: {e}")
        state["errors"].append(f"PR creation failed: {str(e)}")
        state["status"] = WorkflowStatus.FAILED
    
    return state

def generate_comprehensive_pr_description(state: IssueWorkflowState) -> str:
    """Generate detailed PR description."""
    
    description = f"""## 🤖 AI-Generated Solution

**Closes**: #{state['issue_number']}

### Summary
{state['issue_analysis'].get('summary', 'Automated fix for reported issue')}

### Changes Made
"""
    
    # Add changes by type
    code_count = len([a for a in state["all_artifacts"] if a["type"] == "code"])
    test_count = len([a for a in state["all_artifacts"] if a["type"] == "test"])
    doc_count = len([a for a in state["all_artifacts"] if a["type"] == "documentation"])
    
    if code_count:
        description += f"- 🔧 **{code_count} code files** modified/created\n"
    if test_count:
        description += f"- ✅ **{test_count} test files** added\n"
    if doc_count:
        description += f"- 📚 **{doc_count} documentation** updates\n"
    
    description += f"""
### Task Execution Summary
- **Total tasks**: {len(state['task_breakdown'])}
- **Completed**: {len(state['completed_tasks'])}
- **Failed**: {len(state['failed_tasks'])}

### Quality Assurance
- All changes reviewed by Navigator AI
- Iterative improvement process applied
- Code meets project standards

---
🤖 Generated by SyntheticCodingTeam
"""
    
    return description
```

## Testing Requirements

### Integration Tests
```python
# tests/integration/test_end_to_end.py
import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_workflow():
    """Test complete workflow end-to-end."""
    
    # Create test issue
    issue_event = create_test_issue_event(
        title="Fix button not working",
        body="The submit button doesn't work on mobile"
    )
    
    # Start workflow
    orchestrator = WorkflowOrchestrator()
    workflow_id = await orchestrator.start_workflow(issue_event)
    
    # Wait for completion (with timeout)
    result = await wait_for_workflow_completion(workflow_id, timeout=600)
    
    # Verify success
    assert result["status"] == WorkflowStatus.COMPLETED
    assert result["pr_number"] is not None
    assert len(result["all_artifacts"]) > 0
    assert len(result["completed_tasks"]) > 0

@pytest.mark.integration 
async def test_prevents_pr_23_disaster():
    """Test that workflow prevents PR #23 type disasters."""
    
    # Issue that caused PR #23
    issue_event = create_test_issue_event(
        title="Remove phrase from README",
        body="Remove '解释文化细节' from README.md"
    )
    
    result = await run_complete_workflow(issue_event)
    
    # Should succeed
    assert result["status"] == WorkflowStatus.COMPLETED
    
    # Check that README wasn't completely deleted
    readme_changes = [
        a for a in result["all_artifacts"] 
        if a["path"] == "README.md"
    ]
    assert len(readme_changes) == 1
    readme_content = readme_changes[0]["content"]
    
    # Should have most content preserved
    assert len(readme_content) > 100  # Not empty!
    assert "解释文化细节" not in readme_content  # Phrase removed
```

### Performance Tests
```python
@pytest.mark.performance
async def test_workflow_completion_time():
    """Test workflow completes within reasonable time."""
    start_time = time.time()
    
    result = await run_simple_workflow()
    
    duration = time.time() - start_time
    assert duration < 600  # 10 minutes max
    assert result["status"] == WorkflowStatus.COMPLETED
```

## Dependencies & Risks

### Prerequisites
- All individual agents implemented and tested
- Task Pair system working
- GitHub service functional
- Workflow engine stable

### Risks
- **Complexity**: Many moving parts could fail
- **Performance**: Long execution times
- **API costs**: Full workflow uses many tokens
- **Reliability**: Any single agent failure breaks workflow

### Mitigations
- Comprehensive error handling at each step
- Progress tracking and recovery
- Circuit breakers for failed components
- Fallback modes for partial success

## Definition of Done

1. ✅ Complete workflow processes real GitHub issues
2. ✅ All agent types working together
3. ✅ Task dependencies respected
4. ✅ Navigator reviews preventing bad code
5. ✅ PR created with comprehensive changes
6. ✅ Issue updated with progress
7. ✅ Workflow completes in reasonable time
8. ✅ Integration tests passing
9. ✅ Ready for production deployment

## Implementation Notes for AI Agents

### DO
- Test each workflow step thoroughly
- Add comprehensive logging
- Handle partial failures gracefully
- Keep user informed with issue comments
- Save all work even if workflow fails

### DON'T
- Don't skip error handling
- Don't assume previous steps succeeded
- Don't create PRs with no changes
- Don't exceed reasonable time limits
- Don't lose artifacts between steps

### Common Pitfalls to Avoid
1. Not preserving state between nodes
2. Losing artifacts during workflow
3. Not handling agent failures
4. Creating empty or broken PRs
5. Not updating issue progress

## Success Example

The complete workflow prevents PR #23:
```
1. Issue: "Remove phrase from README"
2. PM: "Simple text removal task" 
3. Analyst: "Read current README, identify phrase location"
4. Developer: "Remove only the specific phrase"
5. Navigator: "Verify phrase removed, content preserved"
6. Tester: "No tests needed for documentation change"
7. PR: Targeted change, README preserved ✅
```

## Next Story
Once this story is complete, proceed to [Story 7.2: PR Generation System](story-7.2-pr-generation.md)