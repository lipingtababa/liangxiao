# Project Manager Agent

The Project Manager (PM) Agent is a critical component of the AI coding team that prevents disasters by providing intelligent issue analysis and structured task breakdowns.

## Overview

The PM Agent addresses the core problem described in Story 2.1: preventing chaotic, unstructured development that leads to poor implementations like "PR #23 disasters." It serves as the brain of the multi-agent system by:

- **Analyzing GitHub issues** intelligently using LangChain and GPT-4
- **Creating structured task breakdowns** with clear dependencies and execution order
- **Preventing implementation disasters** through proper planning and quality gates
- **Coordinating agent activities** by assigning tasks to appropriate agent types

## Architecture

### Core Components

1. **PMAgent Class** (`agent.py`)
   - Main orchestrator that uses LangChain for analysis
   - Integrates with OpenAI GPT-4 for intelligent reasoning
   - Provides structured output using Pydantic models
   - Includes comprehensive error handling and fallback logic

2. **Pydantic Models** (`models.py`)
   - `Task`: Individual actionable tasks with dependencies and acceptance criteria
   - `IssueAnalysis`: Comprehensive analysis of GitHub issues
   - `TaskBreakdown`: Complete execution plan with validation logic
   - `PMAgentConfig`: Configuration for agent behavior

3. **Workflow Integration** (`pm_nodes.py`)
   - `pm_analyze_issue_node`: Workflow node for issue analysis
   - `pm_plan_tasks_node`: Workflow node for task breakdown creation  
   - `pm_validate_completion_node`: Workflow node for completion validation
   - Fallback integration with existing basic workflow nodes

## Key Features

### Intelligent Issue Analysis

The PM Agent performs deep analysis of GitHub issues to understand:

- **Issue Type**: bug_fix, feature, enhancement, documentation, refactor, maintenance, investigation
- **Complexity Level**: trivial, simple, medium, complex, very_complex
- **Risk Assessment**: Potential challenges and blockers
- **Requirements Extraction**: Clear, actionable requirements
- **Confidence Scoring**: Self-assessment of analysis quality

### Structured Task Breakdown

Creates actionable task plans with:

- **Clear Task Definitions**: Title, description, acceptance criteria
- **Agent Assignment**: analyst, developer, tester, navigator
- **Dependency Management**: Proper task ordering and prerequisites
- **Effort Estimation**: Realistic time estimates for planning
- **Quality Gates**: Testing and review checkpoints

### Quality Assurance

Prevents disasters through:

- **Validation Logic**: Circular dependency detection, execution order validation
- **Comprehensive Testing**: Built-in testing requirements and strategies
- **Review Integration**: Quality checkpoints and navigator agent coordination
- **Fallback Mechanisms**: Graceful degradation when LLM services are unavailable

## Usage Examples

### Basic Usage

```python
from agents.pm import PMAgent, PMAgentConfig

# Configure the agent
config = PMAgentConfig(
    llm_model="gpt-4-turbo-preview",
    temperature=0.2,
    require_testing_tasks=True
)

# Create the agent
pm_agent = PMAgent(config=config)

# Analyze an issue
issue_data = {
    "number": 123,
    "title": "Fix mobile login bug",
    "body": "Login button not working on mobile devices...",
    "labels": [{"name": "bug"}, {"name": "mobile"}],
    "repository": "example/webapp"
}

# Get complete analysis and task breakdown
breakdown = pm_agent.execute(issue_data)

# Access results
print(f"Issue type: {breakdown.analysis.issue_type}")
print(f"Complexity: {breakdown.analysis.complexity}")
print(f"Number of tasks: {len(breakdown.tasks)}")
print(f"Total estimated hours: {breakdown.total_estimated_hours}")

# Get next task to execute
next_task = breakdown.get_next_ready_task(set())
print(f"Next task: {next_task.title}")
```

### Workflow Integration

The PM Agent integrates seamlessly with the existing workflow:

```python
from workflows.nodes.basic_nodes import analyze_issue_node, plan_tasks_node
from workflows.workflow_state import create_initial_state

# Create workflow state
state = create_initial_state(
    issue_number=123,
    issue_title="Fix mobile login bug", 
    issue_body="Login button not working...",
    issue_url="https://github.com/example/webapp/issues/123",
    repository="example/webapp"
)

# Analysis will use PM Agent if available, fall back to basic analysis otherwise
analyzed_state = await analyze_issue_node(state)

# Planning will use PM Agent if available, fall back to basic planning otherwise  
planned_state = await plan_tasks_node(analyzed_state)

# Access structured results
tasks = planned_state['tasks']
execution_order = planned_state['task_execution_order']
```

## Configuration Options

### PMAgentConfig

- `llm_model`: LLM model to use (default: "gpt-4-turbo-preview")
- `temperature`: Response consistency (default: 0.2)
- `max_tasks_per_issue`: Maximum tasks per breakdown (default: 8)
- `require_testing_tasks`: Always include testing tasks (default: True)
- `enable_risk_analysis`: Perform detailed risk analysis (default: True)
- `max_analysis_tokens`: Token limit for analysis (default: 4000)

## Error Handling & Fallbacks

The PM Agent includes robust error handling:

1. **LLM Service Failures**: Graceful degradation to basic analysis
2. **Parsing Errors**: Structured error reporting with context
3. **Validation Failures**: Clear error messages for debugging
4. **API Timeouts**: Retry logic and fallback mechanisms

## Testing

Comprehensive test coverage includes:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Workflow integration validation  
- **Mocking Support**: Tests work without external API calls
- **Error Scenario Testing**: Validates fallback behavior

Run tests with:

```bash
# Run all PM Agent tests
python -m pytest tests/test_pm_agent.py -v

# Run workflow integration tests  
python -m pytest tests/test_pm_nodes.py -v

# Run comprehensive integration tests
python -m pytest tests/test_pm_integration.py -v
```

## Metrics & Monitoring

The PM Agent tracks performance metrics:

- `total_analyses`: Number of issues analyzed
- `total_breakdowns`: Number of task breakdowns created
- `total_tokens_used`: LLM token consumption
- `average_tokens_per_analysis`: Efficiency metrics

Access metrics with:

```python
metrics = pm_agent.get_metrics()
print(f"Analyses performed: {metrics['total_analyses']}")
print(f"Average tokens per analysis: {metrics['average_tokens_per_analysis']}")
```

## Benefits

### For Development Teams

- **Prevents Implementation Disasters**: Structured planning prevents poor implementations
- **Improves Code Quality**: Built-in testing and review requirements
- **Reduces Technical Debt**: Proper architecture planning from the start
- **Increases Predictability**: Realistic estimates and clear success criteria

### For AI Agent Systems

- **Intelligent Coordination**: Smart agent assignment and task orchestration
- **Quality Assurance**: Multiple validation layers and quality gates
- **Extensible Architecture**: Easy to add new agent types and capabilities
- **Robust Error Handling**: Graceful degradation and comprehensive logging

## Future Enhancements

The PM Agent is designed for extensibility:

- **Custom Prompts**: Template customization for specific project needs
- **Agent Type Extensions**: Support for specialized agent types
- **Integration Plugins**: Connect with project management tools
- **Learning Capabilities**: Improve analysis quality over time
- **Metrics Dashboard**: Visual monitoring and reporting

## Conclusion

The PM Agent transforms chaotic development into structured, quality-focused execution. By providing intelligent analysis and planning, it ensures that every issue is approached systematically with clear goals, proper testing, and quality assurance built in from the start.

This prevents the "PR #23 disasters" by making sure every piece of work has a clear plan, proper validation, and quality gates before implementation begins.