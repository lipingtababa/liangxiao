"""Project Manager Agent implementation.

This module contains the PMAgent class that uses LangChain to analyze GitHub issues
and create structured task breakdowns. The agent is responsible for understanding
requirements, identifying complexity, and creating actionable plans.
"""

import json
import logging
from collections import deque
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

from .models import (
    Task, IssueAnalysis, TaskBreakdown, PMAgentConfig
)
from core.logging import get_logger
from core.exceptions import AgentExecutionError


logger = get_logger(__name__)


class PMAgent:
    """Project Manager Agent for analyzing issues and creating task breakdowns.
    
    The PM Agent is responsible for:
    1. Analyzing GitHub issues to understand requirements
    2. Breaking down complex issues into manageable tasks
    3. Assigning tasks to appropriate agent types
    4. Creating execution plans with proper dependencies
    5. Providing quality guidance and success criteria
    
    This agent prevents the chaos of unstructured development by ensuring
    every issue has a clear, actionable plan before implementation begins.
    """
    
    def __init__(
        self, 
        config: Optional[PMAgentConfig] = None,
        llm: Optional[ChatOpenAI] = None
    ):
        """Initialize the PM Agent.
        
        Args:
            config: Configuration for agent behavior
            llm: Pre-configured LLM instance (optional)
        """
        self.config = config or PMAgentConfig()
        self.llm = llm or self._create_llm()
        
        # Initialize output parsers
        self.analysis_parser = PydanticOutputParser(pydantic_object=IssueAnalysis)
        self.breakdown_parser = PydanticOutputParser(pydantic_object=TaskBreakdown)
        
        # Metrics tracking
        self.total_analyses = 0
        self.total_breakdowns = 0
        self.total_tokens_used = 0
        
        logger.info(f"PM Agent initialized with {self.config.llm_model}")
    
    def _create_llm(self) -> ChatOpenAI:
        """Create and configure the LLM instance.
        
        Returns:
            Configured ChatOpenAI instance
        """
        return ChatOpenAI(
            model=self.config.llm_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_analysis_tokens,
            model_kwargs={
                "response_format": {"type": "json_object"}
            }
        )
    
    def analyze_issue(self, issue: Dict[str, Any]) -> IssueAnalysis:
        """Analyze a GitHub issue to understand requirements and complexity.
        
        This is the first step in the PM process. The agent examines the issue
        title, description, labels, and any other context to understand:
        - What type of work this is (bug, feature, etc.)
        - How complex the work will be
        - What risks or challenges exist
        - What questions need clarification
        
        Args:
            issue: GitHub issue data containing title, body, labels, etc.
            
        Returns:
            Structured analysis of the issue
            
        Raises:
            AgentExecutionError: If analysis fails
        """
        logger.info(
            f"Analyzing issue #{issue.get('number', 'unknown')}: "
            f"{issue.get('title', 'No title')[:50]}..."
        )
        
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt()
            
            # Format issue data for analysis
            formatted_issue = self._format_issue_for_analysis(issue)
            
            # Get LLM response
            formatted_prompt = prompt.format_messages(
                format_instructions=self.analysis_parser.get_format_instructions(),
                **formatted_issue
            )
            
            response = self.llm.invoke(formatted_prompt)
            
            # Parse structured output
            analysis = self.analysis_parser.parse(response.content)
            
            # Track metrics
            self.total_analyses += 1
            self.total_tokens_used += response.usage_metadata.get('total_tokens', 0)
            
            logger.info(
                f"Analysis complete: {analysis.issue_type} "
                f"({analysis.complexity}) - {analysis.confidence_score:.2f} confidence"
            )
            
            return analysis
            
        except (OutputParserException, ValidationError) as e:
            logger.error(f"Failed to parse analysis response: {e}")
            raise AgentExecutionError(
                f"PM Agent analysis parsing failed: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(f"Issue analysis failed: {e}")
            raise AgentExecutionError(
                f"PM Agent issue analysis failed: {str(e)}"
            ) from e
    
    def create_task_breakdown(
        self, 
        issue: Dict[str, Any], 
        analysis: IssueAnalysis
    ) -> TaskBreakdown:
        """Create detailed task breakdown based on issue analysis.
        
        This is the core PM responsibility. Based on the analysis, create
        a structured plan with specific, actionable tasks that can be
        executed by specialized agents.
        
        Args:
            issue: Original GitHub issue data
            analysis: Previous analysis results
            
        Returns:
            Complete task breakdown with execution plan
            
        Raises:
            AgentExecutionError: If breakdown creation fails
        """
        logger.info(
            f"Creating task breakdown for issue #{issue.get('number', 'unknown')} "
            f"({analysis.issue_type}, {analysis.complexity})"
        )
        
        try:
            # Create breakdown prompt
            prompt = self._create_breakdown_prompt()
            
            # Format inputs
            formatted_issue = self._format_issue_for_breakdown(issue, analysis)
            
            # Get LLM response
            formatted_prompt = prompt.format_messages(
                format_instructions=self.breakdown_parser.get_format_instructions(),
                **formatted_issue
            )
            
            response = self.llm.invoke(formatted_prompt)
            
            # Parse structured output
            breakdown_data = json.loads(response.content)
            
            # Create TaskBreakdown with analysis
            breakdown_data['analysis'] = analysis.model_dump()
            breakdown = TaskBreakdown.model_validate(breakdown_data)
            
            # Validate and optimize the breakdown
            self._validate_and_optimize_breakdown(breakdown)
            
            # Track metrics
            self.total_breakdowns += 1
            self.total_tokens_used += response.usage_metadata.get('total_tokens', 0)
            
            logger.info(
                f"Task breakdown created: {len(breakdown.tasks)} tasks, "
                f"{breakdown.total_estimated_hours:.1f}h total"
            )
            
            return breakdown
            
        except (OutputParserException, ValidationError) as e:
            logger.error(f"Failed to parse breakdown response: {e}")
            raise AgentExecutionError(
                f"PM Agent breakdown parsing failed: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(f"Task breakdown creation failed: {e}")
            raise AgentExecutionError(
                f"PM Agent breakdown creation failed: {str(e)}"
            ) from e
    
    def execute(self, issue: Dict[str, Any]) -> TaskBreakdown:
        """Execute complete PM analysis and planning for an issue.
        
        This is the main entry point that combines analysis and task breakdown
        into a single operation. Most callers should use this method.
        
        Args:
            issue: GitHub issue data
            
        Returns:
            Complete task breakdown ready for execution
            
        Raises:
            AgentExecutionError: If execution fails
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Analyze the issue
            analysis = self.analyze_issue(issue)
            
            # Step 2: Create task breakdown
            breakdown = self.create_task_breakdown(issue, analysis)
            
            # Log execution summary
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"PM execution complete in {execution_time:.2f}s: "
                f"{len(breakdown.tasks)} tasks, "
                f"{breakdown.total_estimated_hours:.1f}h estimated"
            )
            
            return breakdown
            
        except AgentExecutionError:
            # Re-raise agent errors as-is
            raise
        except Exception as e:
            logger.error(f"PM Agent execution failed: {e}")
            raise AgentExecutionError(
                f"PM Agent complete execution failed: {str(e)}"
            ) from e
    
    def prioritize_tasks(self, tasks: List['Task']) -> List[str]:
        """Determine optimal task execution order using topological sort.
        
        This method analyzes task dependencies and creates an optimal
        execution order that respects all dependencies.
        
        Args:
            tasks: List of Task objects to prioritize
            
        Returns:
            List of task IDs in optimal execution order
        """
        # Build dependency graph
        task_map = {task.id: task for task in tasks}
        in_degree = {task.id: 0 for task in tasks}
        
        # Count incoming edges (dependencies)
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in in_degree:
                    in_degree[task.id] += 1
        
        # Topological sort using Kahn's algorithm
        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            task_id = queue.popleft()
            result.append(task_id)
            
            # Find all tasks that depend on this one
            for task in tasks:
                if task_id in task.dependencies:
                    in_degree[task.id] -= 1
                    if in_degree[task.id] == 0:
                        queue.append(task.id)
        
        # Verify all tasks were included (no circular dependencies)
        if len(result) != len(tasks):
            logger.warning(f"Circular dependencies detected in task prioritization")
            # Return original order as fallback
            return [task.id for task in tasks]
        
        logger.debug(f"Task prioritization complete: {result}")
        return result
    
    def estimate_complexity(self, issue: Dict[str, Any]) -> str:
        """Quick complexity estimation for an issue without full analysis.
        
        This method provides a fast complexity estimate based on simple
        heuristics, useful for filtering or quick decisions.
        
        Args:
            issue: GitHub issue data
            
        Returns:
            Complexity level: 'trivial', 'simple', 'medium', 'complex', or 'very_complex'
        """
        title = issue.get('title', '').lower()
        body = issue.get('body', '').lower()
        labels = [label.get('name', '').lower() if isinstance(label, dict) else str(label).lower() 
                 for label in issue.get('labels', [])]
        
        # Start with simple
        complexity = 'simple'
        
        # Check for complexity indicators
        complex_keywords = [
            'architecture', 'refactor', 'redesign', 'migration', 'integration',
            'performance', 'security', 'scalability', 'infrastructure'
        ]
        
        very_complex_keywords = [
            'system', 'platform', 'framework', 'breaking', 'major'
        ]
        
        trivial_keywords = [
            'typo', 'spelling', 'comment', 'documentation', 'readme'
        ]
        
        # Count lines/words as complexity indicators
        body_length = len(body.split()) if body else 0
        
        # Apply heuristics
        if any(keyword in title + body for keyword in trivial_keywords):
            complexity = 'trivial'
        elif any(keyword in title + body for keyword in very_complex_keywords):
            complexity = 'very_complex'
        elif any(keyword in title + body for keyword in complex_keywords):
            complexity = 'complex'
        elif body_length > 200:  # Long descriptions suggest complexity
            complexity = 'complex'
        elif body_length > 100:
            complexity = 'medium'
        elif any('critical' in label or 'high' in label for label in labels):
            # High priority might indicate complexity
            if complexity == 'simple':
                complexity = 'medium'
        
        logger.debug(f"Quick complexity estimate for issue #{issue.get('number', 'unknown')}: {complexity}")
        return complexity
    
    def _create_analysis_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for issue analysis.
        
        Returns:
            Configured prompt template
        """
        system_message = """You are an expert Project Manager for an AI coding team.
Your job is to analyze GitHub issues and provide structured analysis that will guide task creation.

You must be thorough and thoughtful because your analysis determines the entire project approach.
The team has had problems with incomplete analysis leading to poor implementations (like PR #23).

CRITICAL GUIDELINES:
1. Read the entire issue carefully - title, description, labels, context
2. Identify the TRUE requirements, not just surface-level requests
3. Consider edge cases, error conditions, and integration points
4. Assess realistic complexity - don't over-simplify complex issues
5. Think about testing requirements and quality assurance
6. Identify potential risks and architectural concerns
7. Note what information is missing or unclear

ISSUE TYPES:
- bug_fix: Something is broken and needs repair
- feature: New functionality to implement  
- enhancement: Improvement to existing functionality
- documentation: Documentation updates or creation
- refactor: Code restructuring without behavior changes
- maintenance: Dependency updates, cleanup, etc.
- investigation: Research or exploration work

COMPLEXITY LEVELS:
- trivial: < 1 hour, single file, no dependencies
- simple: 1-3 hours, few files, straightforward logic
- medium: 4-8 hours, multiple files, some complexity
- complex: 1-3 days, significant changes, multiple systems
- very_complex: > 3 days, architectural changes, high risk

Your analysis will be used to create a task breakdown, so be specific and actionable.
Focus on QUALITY - we need bulletproof analysis to avoid disasters.

Respond with valid JSON matching the required schema.

{format_instructions}"""
        
        human_message = """Analyze this GitHub issue:

**Issue #{number}: {title}**

**Description:**
{body}

**Labels:** {labels}
**Repository:** {repository}

Provide a comprehensive analysis that will guide task creation."""
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            ("human", human_message)
        ])
    
    def _create_breakdown_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for task breakdown.
        
        Returns:
            Configured prompt template
        """
        system_message = """You are an expert Project Manager creating a detailed task breakdown.

Based on the issue analysis, break down the work into specific, actionable tasks.
Each task MUST be:
1. Small enough for one agent to complete in 1-4 hours
2. Have crystal clear acceptance criteria
3. Be assigned to the correct agent type
4. Have proper dependencies identified
5. Include realistic effort estimates

AGENT TYPES:
- analyst: Requirements analysis, research, investigation, documentation
- developer: Code implementation, bug fixes, feature development
- tester: Test creation, test execution, quality validation  
- navigator: Code review, quality checks, integration validation

TASK TYPES:
- analysis: Understanding requirements, researching solutions
- implementation: Writing/modifying code
- testing: Creating and running tests
- documentation: Writing/updating docs
- review: Quality checks and validation

TASK BREAKDOWN STRATEGY:
1. Start with analysis/investigation tasks
2. Break implementation into logical chunks
3. Include testing for each implementation
4. Add review checkpoints for quality
5. Consider integration and deployment

CRITICAL RULES:
- Every implementation needs corresponding tests
- Complex changes need multiple review points
- Dependencies must be realistic and necessary
- Don't create micro-tasks (< 30 minutes)
- Don't create mega-tasks (> 4 hours)
- Each task should have 2-4 acceptance criteria
- Estimate effort realistically (padding for unknowns)

QUALITY FOCUS:
Remember: We're fixing the problem where agents create terrible code.
Build in quality checkpoints, proper testing, and thorough review cycles.
It's better to have more tasks with quality gates than fewer tasks that fail.

Respond with valid JSON matching the required schema.

{format_instructions}"""
        
        human_message = """Create task breakdown for this issue:

**Issue #{number}: {title}**
**Repository:** {repository}

**Previous Analysis:**
{analysis_summary}

**Key Requirements:**
{key_requirements}

**Complexity:** {complexity}
**Type:** {issue_type}
**Estimated Effort:** {estimated_effort}

Create a comprehensive task breakdown that ensures HIGH QUALITY implementation."""
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            ("human", human_message)
        ])
    
    def _format_issue_for_analysis(self, issue: Dict[str, Any]) -> Dict[str, str]:
        """Format issue data for analysis prompt.
        
        Args:
            issue: Raw issue data
            
        Returns:
            Formatted data for prompt
        """
        labels = issue.get('labels', [])
        if isinstance(labels, list):
            # Handle both string labels and label objects
            label_names = []
            for label in labels:
                if isinstance(label, dict) and 'name' in label:
                    label_names.append(label['name'])
                elif isinstance(label, str):
                    label_names.append(label)
            labels_str = ', '.join(label_names)
        else:
            labels_str = str(labels)
        
        return {
            'number': str(issue.get('number', 'unknown')),
            'title': issue.get('title', 'No title provided'),
            'body': issue.get('body') or 'No description provided',
            'labels': labels_str or 'No labels',
            'repository': issue.get('repository', 'unknown/unknown')
        }
    
    def _format_issue_for_breakdown(
        self, 
        issue: Dict[str, Any], 
        analysis: IssueAnalysis
    ) -> Dict[str, str]:
        """Format issue and analysis data for breakdown prompt.
        
        Args:
            issue: Raw issue data
            analysis: Completed analysis
            
        Returns:
            Formatted data for prompt
        """
        issue_formatted = self._format_issue_for_analysis(issue)
        
        return {
            **issue_formatted,
            'analysis_summary': analysis.summary,
            'key_requirements': '\n'.join(f"- {req}" for req in analysis.key_requirements),
            'complexity': analysis.complexity,
            'issue_type': analysis.issue_type,
            'estimated_effort': analysis.estimated_effort,
        }
    
    def _validate_and_optimize_breakdown(self, breakdown: TaskBreakdown) -> None:
        """Validate and optimize a task breakdown.
        
        Args:
            breakdown: Task breakdown to validate and optimize
            
        Raises:
            AgentExecutionError: If validation fails
        """
        # Validate dependencies
        validation_errors = breakdown.validate_dependencies()
        if validation_errors:
            error_msg = "Task breakdown validation failed: " + '; '.join(validation_errors)
            logger.error(error_msg)
            raise AgentExecutionError(error_msg)
        
        # Check for circular dependencies
        if self._has_circular_dependencies(breakdown.tasks):
            raise AgentExecutionError("Circular dependencies detected in task breakdown")
        
        # Validate execution order
        self._validate_execution_order(breakdown)
        
        # Check task count limits
        if len(breakdown.tasks) > self.config.max_tasks_per_issue:
            logger.warning(
                f"Task breakdown has {len(breakdown.tasks)} tasks "
                f"(limit: {self.config.max_tasks_per_issue})"
            )
        
        # Ensure testing tasks if required
        if self.config.require_testing_tasks:
            has_testing = any(task.task_type == "testing" for task in breakdown.tasks)
            if not has_testing and breakdown.analysis.issue_type != "documentation":
                logger.warning("No testing tasks found in breakdown")
        
        logger.debug(f"Task breakdown validation passed: {len(breakdown.tasks)} tasks")
    
    def _has_circular_dependencies(self, tasks: List[Task]) -> bool:
        """Check for circular dependencies in tasks.
        
        Args:
            tasks: List of tasks to check
            
        Returns:
            True if circular dependencies exist
        """
        # Build dependency graph
        graph = {task.id: set(task.dependencies) for task in tasks}
        
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            if node not in graph:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return True
        
        return False
    
    def _validate_execution_order(self, breakdown: TaskBreakdown) -> None:
        """Validate that execution order respects dependencies.
        
        Args:
            breakdown: Task breakdown to validate
            
        Raises:
            AgentExecutionError: If order is invalid
        """
        task_map = {task.id: task for task in breakdown.tasks}
        completed = set()
        
        for task_id in breakdown.execution_order:
            if task_id not in task_map:
                raise AgentExecutionError(f"Unknown task in execution order: {task_id}")
            
            task = task_map[task_id]
            
            # Check all dependencies are completed
            for dep_id in task.dependencies:
                if dep_id not in completed:
                    raise AgentExecutionError(
                        f"Task {task_id} scheduled before dependency {dep_id}"
                    )
            
            completed.add(task_id)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get PM Agent performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            'total_analyses': self.total_analyses,
            'total_breakdowns': self.total_breakdowns,
            'total_tokens_used': self.total_tokens_used,
            'average_tokens_per_analysis': (
                self.total_tokens_used / max(self.total_analyses, 1)
            ),
            'config': self.config.model_dump()
        }
    
    def __str__(self) -> str:
        return f"PMAgent({self.config.llm_model})"