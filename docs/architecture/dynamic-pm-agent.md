# Dynamic PM Agent Architecture

## Overview

The Dynamic PM Agent replaces the current static LangChain-based workflow with an intelligent, adaptive system where the PM agent evaluates every step result and dynamically decides the next action. This eliminates rigid workflow graphs in favor of contextual, data-driven routing.

## Current Problems with LangChain Approach

### Static Workflow Issues
```python
# Current: Fixed LangGraph workflow
analyze_issue → plan_tasks → execute_task → review_task → test_solution → create_pr
```

**Problems:**
- **No adaptability**: Same path regardless of results
- **Blind transitions**: Steps don't know what previous steps produced
- **No quality gates**: Bad outputs propagate through workflow
- **PM powerlessness**: PM creates plan but can't control execution
- **LangChain overhead**: Complex abstractions for simple operations

### LangChain Complexity vs Benefits

**Current LangChain Usage:**
```python
# 50+ lines for simple LLM call
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate  
from langchain_core.output_parsers import PydanticOutputParser

prompt = ChatPromptTemplate.from_messages([...])
llm = ChatOpenAI(model="gpt-4", temperature=0.2)
parser = PydanticOutputParser(pydantic_object=TaskBreakdown)
response = llm.invoke(prompt.format_messages(...))
result = parser.parse(response.content)
```

**Equivalent Direct Approach:**
```python
# 10 lines for same functionality
response = openai.chat.completions.create(
    model="gpt-4",
    temperature=0.2,
    messages=[{"role": "system", "content": system_prompt}, 
              {"role": "user", "content": user_prompt}]
)
result = TaskBreakdown.model_validate(json.loads(response.choices[0].message.content))
```

## Dynamic PM Agent Design

### Core Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Issue  │    │  Step Result     │    │  PM Evaluation  │
│                 │───▶│                  │───▶│                 │
│ - Title         │    │ - Status         │    │ - Quality Check │
│ - Description   │    │ - Output Data    │    │ - Route Decision│
│ - Labels        │    │ - Quality Metrics│    │ - Next Action   │
└─────────────────┘    │ - Issues Found   │    └─────────────────┘
                       │ - Confidence     │             │
                       └──────────────────┘             │
                                                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Agent Input    │    │  Next Action    │
                       │                  │◀───│                 │
                       │ - Task Type      │    │ - Target Agent  │
                       │ - Context Data   │    │ - Input Data    │
                       │ - Quality Reqs   │    │ - Priority      │
                       └──────────────────┘    └─────────────────┘
```

### Dynamic PM Controller

```python
class DynamicPMAgent:
    """PM Agent that evaluates every step and decides next actions dynamically."""
    
    def evaluate_step_result(self, step_result: StepResult, context: WorkflowContext) -> NextAction:
        """
        Core decision engine: PM evaluates step result and decides what happens next.
        
        This replaces the fixed LangGraph workflow with intelligent, adaptive routing.
        """
        # Quality Gate Assessment
        if not self._passes_quality_gates(step_result):
            return self._handle_quality_failure(step_result, context)
        
        # Context-Aware Routing  
        routing_decision = self._analyze_routing_options(step_result, context)
        
        # Dynamic Strategy Adaptation
        if self._should_adapt_strategy(step_result, context):
            return self._create_strategy_change(step_result, context)
            
        # Standard progression
        return self._route_to_next_agent(routing_decision)
    
    def _passes_quality_gates(self, result: StepResult) -> bool:
        """Enforce quality standards before allowing progression."""
        return (
            result.status == "success" and
            result.confidence_score >= 0.7 and
            len([i for i in result.issues_found if i.severity == "critical"]) == 0
        )
    
    def _analyze_routing_options(self, result: StepResult, context: WorkflowContext) -> RoutingDecision:
        """Analyze multiple factors to determine optimal next step."""
        factors = {
            'output_type': result.output_data.get('type'),
            'quality_level': result.confidence_score,
            'issue_complexity': context.issue_complexity,
            'previous_steps': context.step_history,
            'remaining_work': context.estimate_remaining_effort()
        }
        
        # Use simple rules engine instead of complex LLM calls
        return self.routing_engine.decide(factors)
```

### Quality Gates System

```python
class QualityGate:
    """Enforces quality standards at each step."""
    
    def __init__(self, min_confidence: float = 0.7, max_critical_issues: int = 0):
        self.min_confidence = min_confidence
        self.max_critical_issues = max_critical_issues
    
    def evaluate(self, step_result: StepResult) -> QualityGateResult:
        """Evaluate if step result meets quality standards."""
        failures = []
        
        if step_result.confidence_score < self.min_confidence:
            failures.append(f"Low confidence: {step_result.confidence_score:.2f} < {self.min_confidence}")
        
        critical_issues = [i for i in step_result.issues_found if i.severity == "critical"]
        if len(critical_issues) > self.max_critical_issues:
            failures.append(f"Critical issues found: {len(critical_issues)}")
        
        return QualityGateResult(
            passed=len(failures) == 0,
            failures=failures,
            recommendation="fix_issues" if failures else "continue"
        )
```

### Adaptive Routing Engine

```python
class AdaptiveRoutingEngine:
    """Routes workflow based on context and results, not fixed graph."""
    
    def decide_next_step(self, result: StepResult, context: WorkflowContext) -> NextAction:
        """Make intelligent routing decisions based on actual results."""
        
        # Route based on output type and quality
        if result.output_data['type'] == 'code_analysis':
            return self._route_after_analysis(result, context)
        elif result.output_data['type'] == 'code_implementation':  
            return self._route_after_implementation(result, context)
        elif result.output_data['type'] == 'code_review':
            return self._route_after_review(result, context)
        elif result.output_data['type'] == 'test_suite':
            return self._route_after_testing(result, context)
        
        return self._default_routing(result, context)
    
    def _route_after_implementation(self, result: StepResult, context: WorkflowContext) -> NextAction:
        """Dynamic routing after Developer completes implementation."""
        
        if result.confidence_score > 0.9 and len(result.issues_found) == 0:
            # High quality code - might skip Navigator review for simple changes
            if context.issue_complexity == 'trivial':
                return NextAction("create_tests", "tester", result.output_data)
            else:
                return NextAction("review_code", "navigator", result.output_data)
        
        elif result.confidence_score < 0.6:
            # Low confidence - need analysis or different approach
            return NextAction("analyze_implementation", "analyst", {
                "code_changes": result.output_data,
                "concerns": result.issues_found
            })
        
        else:
            # Standard path - send to Navigator
            return NextAction("review_code", "navigator", result.output_data)
```

## Data Flow Architecture

### Standardized Step Interface

```python
@dataclass
class StepResult:
    """Standardized output from every workflow step."""
    status: Literal["success", "partial", "failed", "blocked"]
    output_data: Dict[str, Any]  # The actual work product
    quality_metrics: QualityMetrics
    issues_found: List[Issue]
    confidence_score: float  # 0.0 to 1.0
    estimated_remaining_effort: str
    recommendations: List[str]
    step_metadata: StepMetadata

@dataclass  
class QualityMetrics:
    """Quality assessment of step output."""
    completeness_score: float  # 0.0 to 1.0
    accuracy_score: float
    code_quality_score: Optional[float]  # For code-related steps
    test_coverage: Optional[float]  # For testing steps
    critical_issues_count: int
    warning_count: int

@dataclass
class NextAction:
    """PM's decision about what to do next."""
    action: str  # "implement", "review", "test", "analyze", etc.
    target_agent: str  # "developer", "navigator", "tester", "analyst" 
    input_data: Dict[str, Any]  # Data to send to next agent
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    quality_requirements: Optional[QualityGate] = None
    context_notes: Optional[str] = None
```

### Agent-Specific Input/Output Schemas

```python
# Developer Agent
class DeveloperInput(BaseModel):
    task_type: Literal["implement", "fix_issues", "refactor"]
    requirements: List[str]
    code_context: Dict[str, str]  # Existing files and their content
    constraints: List[str] 
    test_requirements: Optional[TestRequirements]
    
class DeveloperOutput(BaseModel):
    files_modified: List[FileChange]
    implementation_approach: str
    test_coverage_impact: float
    potential_integration_points: List[str]
    security_considerations: List[str]

# Navigator Agent  
class NavigatorInput(BaseModel):
    review_type: Literal["code_review", "architecture_review", "integration_review"]
    code_changes: List[FileChange]
    quality_standards: QualityStandards
    focus_areas: List[str]
    
class NavigatorOutput(BaseModel):
    review_status: Literal["approved", "needs_changes", "rejected"]
    code_quality_assessment: CodeQualityScore
    issues_by_severity: Dict[str, List[Issue]]
    refactoring_suggestions: List[RefactoringRecommendation]
    integration_risks: List[IntegrationRisk]

# Similar patterns for Tester and Analyst...
```

## Implementation Strategy

### Phase 1: Core PM Engine
1. **Remove LangChain dependencies**
   - Replace `ChatOpenAI` with direct OpenAI client
   - Replace `ChatPromptTemplate` with f-string templates
   - Replace `PydanticOutputParser` with `json.loads()` + validation

2. **Implement StepResult standardization**
   - Create base `StepResult` class  
   - Update all agent outputs to use standard format
   - Add quality metrics to every step

3. **Create PM evaluation engine**
   - `evaluate_step_result()` method
   - Quality gates system
   - Adaptive routing logic

### Phase 2: Dynamic Workflow Control
1. **Replace LangGraph fixed workflow** 
   - Remove static workflow definition
   - Implement PM-controlled execution loop
   - Add context preservation across steps

2. **Agent coordination system**
   - Parallel task execution
   - Dependency management
   - Progress tracking

## Benefits over LangChain Approach

### Simplicity
- **75% less code** for equivalent functionality
- **Direct control** instead of abstraction layers
- **Easier debugging** with transparent data flow

### Intelligence 
- **Adaptive routing** based on actual results
- **Quality-driven decisions** instead of predetermined paths  
- **Context awareness** throughout workflow

### Maintainability
- **Clear data contracts** between steps
- **Modular agent design** with standard interfaces
- **Explicit decision logic** instead of hidden LangChain behavior

### Performance
- **Fewer dependencies** and faster startup
- **Direct API calls** instead of LangChain wrapper overhead
- **Efficient routing** without graph traversal complexity

## Migration Path

1. **Parallel implementation**: Build new PM system alongside existing LangChain workflow
2. **Agent-by-agent migration**: Update one agent type at a time to new interface
3. **Incremental switchover**: Route new issues to new system while finishing old ones
4. **LangChain removal**: Remove LangChain dependencies once migration complete

This approach provides a smooth transition while immediately delivering the benefits of intelligent, adaptive workflow control.