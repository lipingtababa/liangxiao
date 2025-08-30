"""Analyst Agent implementation.

This module contains the AnalystAgent class that performs thorough requirements
analysis, codebase analysis, and technical specification creation. The agent
prevents implementation disasters by reading existing code first and creating
specific, unambiguous requirements.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

from .models import RequirementSpec, CodebaseAnalysis, TechnicalSpecification
from services.github_service import GitHubService, GitHubCLIError
from core.logging import get_logger
from core.exceptions import AgentExecutionError


logger = get_logger(__name__)


class AnalystAgent:
    """
    Analyst agent that gathers requirements and analyzes codebase.
    
    Responsible for thorough analysis before implementation begins.
    This agent prevents disasters like PR #23 by reading existing code
    first and creating clear, specific requirements.
    
    Key responsibilities:
    1. Read and analyze existing codebase files
    2. Extract clear requirements from GitHub issues
    3. Create detailed technical specifications  
    4. Identify file dependencies and relationships
    5. Document current system behavior
    6. Provide context for other agents
    7. Create implementation guidelines
    8. Handle various issue types (bugs, features, improvements)
    9. Return structured analysis artifacts
    """
    
    def __init__(
        self, 
        github_service: Optional[GitHubService] = None,
        llm: Optional[ChatOpenAI] = None,
        max_files_to_analyze: int = 15,
        max_file_size_chars: int = 50000
    ):
        """Initialize the Analyst Agent.
        
        Args:
            github_service: GitHub service for reading repository files
            llm: Pre-configured LLM instance (optional)
            max_files_to_analyze: Maximum number of files to analyze
            max_file_size_chars: Maximum characters per file to analyze
        """
        self.github_service = github_service
        self.llm = llm or self._create_llm()
        self.max_files_to_analyze = max_files_to_analyze
        self.max_file_size_chars = max_file_size_chars
        
        # Initialize output parser
        self.parser = PydanticOutputParser(pydantic_object=TechnicalSpecification)
        
        # Metrics tracking
        self.total_analyses = 0
        self.total_files_read = 0
        self.total_tokens_used = 0
        
        logger.info("Analyst Agent initialized")
    
    def _create_llm(self) -> ChatOpenAI:
        """Create and configure the LLM instance.
        
        Returns:
            Configured ChatOpenAI instance
        """
        return ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,  # Very low temperature for consistent analysis
            max_tokens=4000
        )
    
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analysis task with support for iterative improvement.
        
        This method now supports feedback integration from Navigator agents
        to improve requirements through iterative refinement cycles.
        
        Args:
            task: Task definition from PM containing:
                - id: Task identifier
                - description: Task description
                - type: Task type (should be 'analysis')
            context: Issue and repository context containing:
                - issue: GitHub issue data
                - repository: Repository identifier
                - previous_feedback: Feedback from previous iteration (if any)
                - iteration_number: Current iteration number
                - iteration_guidance: Specific guidance for this iteration
                
        Returns:
            Analysis artifacts including:
                - success: Whether analysis succeeded
                - artifacts: List of generated artifacts
                - summary: Analysis summary
                - error: Error message if failed
                - iteration_info: Information about iteration handling
        """
        logger.info(f"Analyst executing task: {task.get('id', 'unknown')}")
        
        # Check if this is an iteration with feedback
        iteration_number = context.get('iteration_number', 1)
        previous_feedback = context.get('previous_feedback')
        iteration_guidance = context.get('iteration_guidance')
        
        logger.info(f"Analyst iteration {iteration_number}: has_feedback={previous_feedback is not None}")
        
        try:
            # Extract issue information
            issue = context.get("issue", {})
            repository = context.get("repository", "")
            
            # Validate inputs
            if not issue:
                raise AgentExecutionError("No issue provided in context")
            if not repository:
                raise AgentExecutionError("No repository provided in context") 
            
            # Perform analysis (incorporating feedback if available)
            if iteration_number > 1 and previous_feedback:
                spec = await self._analyze_with_feedback_integration(
                    issue=issue,
                    repository=repository,
                    task_description=task.get("description", ""),
                    previous_feedback=previous_feedback,
                    iteration_guidance=iteration_guidance,
                    iteration_number=iteration_number
                )
            else:
                spec = await self._analyze_issue_thoroughly(
                    issue=issue,
                    repository=repository,
                    task_description=task.get("description", "")
                )
            
            # Create documentation
            documentation = await self._create_documentation(spec, issue)
            
            # Track metrics
            self.total_analyses += 1
            
            return {
                "success": True,
                "artifacts": [
                    {
                        "type": "requirements",
                        "path": f"analysis/requirements-{issue.get('number', 'unknown')}.md",
                        "content": documentation,
                        "specification": spec.model_dump()
                    }
                ],
                "summary": (
                    f"Analyzed {len(spec.requirements)} requirements, "
                    f"{len(spec.codebase_analysis.relevant_files)} files, "
                    f"confidence {spec.confidence_score:.2f} (iteration {iteration_number})"
                ),
                "specification": spec,
                "iteration_info": {
                    "iteration_number": iteration_number,
                    "incorporated_feedback": previous_feedback is not None,
                    "had_guidance": iteration_guidance is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Analyst execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "artifacts": [],
                "iteration_info": {
                    "iteration_number": iteration_number,
                    "incorporated_feedback": False,
                    "error": str(e)
                }
            }
    
    async def _analyze_issue_thoroughly(
        self,
        issue: Dict[str, Any],
        repository: str,
        task_description: str
    ) -> TechnicalSpecification:
        """Perform thorough issue analysis.
        
        This is the core analysis method that combines issue analysis with
        codebase analysis to create a comprehensive technical specification.
        
        Args:
            issue: GitHub issue data
            repository: Repository identifier
            task_description: Task description from PM
            
        Returns:
            Complete technical specification
            
        Raises:
            AgentExecutionError: If analysis fails
        """
        logger.info(f"Starting thorough analysis of issue #{issue.get('number', 'unknown')}")
        
        try:
            # Step 1: Identify relevant files from the repository
            relevant_files = await self._identify_relevant_files(issue, repository)
            logger.info(f"Identified {len(relevant_files)} relevant files")
            
            # Step 2: Read relevant files from codebase
            codebase_content = await self._read_relevant_files(relevant_files)
            self.total_files_read += len(relevant_files)
            
            # Step 3: Create comprehensive analysis prompt
            prompt = self._create_analysis_prompt()
            
            # Step 4: Format inputs for analysis
            formatted_inputs = {
                "format_instructions": self.parser.get_format_instructions(),
                "issue_number": issue.get("number", "unknown"),
                "title": issue.get("title", "No title"),
                "body": issue.get("body", "No description"),
                "repository": repository,
                "task_description": task_description,
                "codebase_content": codebase_content,
                "relevant_files": "\\n".join(f"- {file}" for file in relevant_files)
            }
            
            # Step 5: Get LLM analysis
            formatted_prompt = prompt.format_messages(**formatted_inputs)
            response = await self.llm.ainvoke(formatted_prompt)
            
            # Track token usage
            if hasattr(response, 'usage_metadata'):
                self.total_tokens_used += response.usage_metadata.get('total_tokens', 0)
            
            # Step 6: Parse structured output
            specification = self.parser.parse(response.content)
            
            # Step 7: Validate and enhance specification
            specification.repository = repository
            specification.issue_number = issue.get("number")
            
            # Validate completeness
            validation_errors = specification.validate_completeness()
            if validation_errors:
                logger.warning(f"Specification validation warnings: {validation_errors}")
            
            logger.info(
                f"Analysis complete: {len(specification.requirements)} requirements, "
                f"confidence {specification.confidence_score:.2f}"
            )
            
            return specification
            
        except (OutputParserException, ValidationError) as e:
            logger.error(f"Failed to parse analysis response: {e}")
            raise AgentExecutionError(f"Analysis parsing failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Issue analysis failed: {e}")
            raise AgentExecutionError(f"Issue analysis failed: {str(e)}") from e
    
    async def _analyze_with_feedback_integration(
        self,
        issue: Dict[str, Any],
        repository: str,
        task_description: str,
        previous_feedback: Any,
        iteration_guidance: Optional[str],
        iteration_number: int
    ) -> TechnicalSpecification:
        """Perform analysis incorporating feedback from previous iteration.
        
        This method refines the analysis based on Navigator feedback to address
        identified issues and improve requirements quality. It focuses on the
        specific areas highlighted by the Navigator.
        
        Args:
            issue: GitHub issue data
            repository: Repository identifier  
            task_description: Task description from PM
            previous_feedback: Feedback from previous Navigator review
            iteration_guidance: Specific guidance for this iteration
            iteration_number: Current iteration number
            
        Returns:
            Improved technical specification incorporating feedback
            
        Raises:
            AgentExecutionError: If feedback integration fails
        """
        logger.info(f"Integrating Navigator feedback for iteration {iteration_number}")
        
        try:
            # First, get the base analysis
            base_spec = await self._analyze_issue_thoroughly(
                issue=issue,
                repository=repository,
                task_description=task_description
            )
            
            # Extract feedback details for incorporation
            feedback_summary = self._extract_feedback_summary(previous_feedback)
            
            # Create enhanced analysis prompt that addresses feedback
            prompt = self._create_feedback_integration_prompt()
            
            # Format inputs for feedback-enhanced analysis
            formatted_inputs = {
                "format_instructions": self.parser.get_format_instructions(),
                "issue_number": issue.get("number", "unknown"),
                "title": issue.get("title", "No title"),
                "body": issue.get("body", "No description"),
                "repository": repository,
                "task_description": task_description,
                "iteration_number": iteration_number,
                "previous_feedback": feedback_summary,
                "iteration_guidance": iteration_guidance or "No specific guidance provided",
                "base_specification": base_spec.model_dump_json(indent=2),
                "improvement_focus": self._determine_improvement_focus(previous_feedback)
            }
            
            # Get LLM analysis with feedback integration
            formatted_prompt = prompt.format_messages(**formatted_inputs)
            response = await self.llm.ainvoke(formatted_prompt)
            
            # Parse improved specification
            improved_spec = self.parser.parse(response.content)
            
            # Set metadata
            improved_spec.repository = repository
            improved_spec.issue_number = issue.get("number")
            
            # Add learning notes from feedback
            if not improved_spec.lessons_learned:
                improved_spec.lessons_learned = []
            
            improved_spec.lessons_learned.append(
                f"Iteration {iteration_number}: Addressed Navigator feedback on {self._get_main_feedback_areas(previous_feedback)}"
            )
            
            logger.info(
                f"Feedback integration complete for iteration {iteration_number}: "
                f"{len(improved_spec.requirements)} requirements, "
                f"confidence {improved_spec.confidence_score:.2f}"
            )
            
            return improved_spec
            
        except Exception as e:
            logger.error(f"Feedback integration failed: {e}")
            raise AgentExecutionError(f"Feedback integration failed: {str(e)}") from e
    
    async def _identify_relevant_files(
        self,
        issue: Dict[str, Any],
        repository: str
    ) -> List[str]:
        """Identify files that need to be analyzed for this issue.
        
        Uses intelligent analysis to determine which files in the repository
        are relevant to the issue being analyzed. This is critical for
        preventing PR #23 type disasters.
        
        Args:
            issue: GitHub issue data
            repository: Repository identifier
            
        Returns:
            List of relevant file paths
        """
        logger.info("Identifying relevant files for analysis")
        
        if not self.github_service:
            logger.warning("No GitHub service available, cannot identify files")
            return []
        
        try:
            # Get repository file tree
            file_tree = await self._get_repository_file_tree()
            if not file_tree:
                logger.warning("Could not get repository file tree")
                return self._get_fallback_file_patterns(issue)
            
            # Use LLM to identify relevant files
            identification_prompt = self._create_file_identification_prompt()
            
            formatted_inputs = {
                "issue_title": issue.get("title", ""),
                "issue_body": issue.get("body", ""),
                "issue_labels": self._format_labels(issue.get("labels", [])),
                "file_tree": "\\n".join(file_tree[:200]),  # First 200 files
                "repository": repository
            }
            
            formatted_prompt = identification_prompt.format_messages(**formatted_inputs)
            response = await self.llm.ainvoke(formatted_prompt)
            
            # Parse file paths from response
            relevant_files = self._parse_file_paths_from_response(response.content, file_tree)
            
            # Limit to max files and prioritize by relevance
            relevant_files = relevant_files[:self.max_files_to_analyze]
            
            logger.info(f"Identified {len(relevant_files)} relevant files")
            return relevant_files
            
        except Exception as e:
            logger.error(f"Failed to identify relevant files: {e}")
            # Return some default patterns as fallback
            return self._get_fallback_file_patterns(issue)
    
    async def _get_repository_file_tree(self) -> List[str]:
        """Get the repository file tree.
        
        Returns:
            List of file paths in the repository
        """
        try:
            if hasattr(self.github_service, 'get_file_tree'):
                return self.github_service.get_file_tree()
            else:
                # Fallback - try to get common file patterns
                logger.warning("GitHub service does not support get_file_tree")
                return []
        except Exception as e:
            logger.error(f"Failed to get file tree: {e}")
            return []
    
    def _get_fallback_file_patterns(self, issue: Dict[str, Any]) -> List[str]:
        """Get fallback file patterns based on issue content.
        
        Args:
            issue: GitHub issue data
            
        Returns:
            List of likely relevant file paths
        """
        patterns = []
        title = (issue.get("title", "") + " " + issue.get("body", "")).lower()
        
        # Common important files
        patterns.extend([
            "README.md",
            "package.json",
            "requirements.txt",
            "pyproject.toml"
        ])
        
        # Based on content
        if "readme" in title:
            patterns.append("README.md")
        if "test" in title:
            patterns.extend(["tests/", "test/", "**/*test*.py"])
        if "config" in title:
            patterns.extend(["config/", "*.config.js", "*.yml", "*.yaml"])
        if "api" in title:
            patterns.extend(["api/", "routes/", "endpoints/"])
        
        return patterns[:5]  # Limit fallback patterns
    
    async def _read_relevant_files(self, file_paths: List[str]) -> str:
        """Read content of relevant files from the repository.
        
        This is critical for preventing PR #23 disasters - we MUST read
        existing files before making any recommendations.
        
        Args:
            file_paths: List of file paths to read
            
        Returns:
            Concatenated file contents with headers
        """
        logger.info(f"Reading {len(file_paths)} relevant files")
        
        if not self.github_service:
            logger.warning("No GitHub service available, cannot read files")
            return "No file content available - GitHub service not configured"
        
        file_contents = []
        files_read = 0
        
        for file_path in file_paths:
            try:
                logger.debug(f"Reading file: {file_path}")
                content = self.github_service.read_file(file_path)
                
                if content:
                    # Truncate very large files
                    if len(content) > self.max_file_size_chars:
                        content = content[:self.max_file_size_chars] + "\\n\\n[File truncated due to size]"
                    
                    file_contents.append(f"=== {file_path} ===\\n{content}\\n")
                    files_read += 1
                else:
                    file_contents.append(f"=== {file_path} === (File not found or empty)\\n")
                    
            except GitHubCLIError as e:
                logger.warning(f"Could not read {file_path}: {e}")
                file_contents.append(f"=== {file_path} === (Error: {str(e)})\\n")
            except Exception as e:
                logger.error(f"Unexpected error reading {file_path}: {e}")
                file_contents.append(f"=== {file_path} === (Unexpected error)\\n")
        
        logger.info(f"Successfully read {files_read} out of {len(file_paths)} files")
        return "\\n".join(file_contents)
    
    def _create_analysis_prompt(self) -> ChatPromptTemplate:
        """Create the comprehensive analysis prompt.
        
        Returns:
            Configured prompt template for issue analysis
        """
        system_message = '''You are an expert Business Analyst and System Analyst.

Your job is to thoroughly analyze requirements and existing codebase
to create clear, unambiguous specifications for developers.

CRITICAL IMPORTANCE: You are preventing disasters like PR #23 where an agent
deleted an entire README instead of removing one phrase because they didn't 
read the existing content first!

KEY PRINCIPLES:
1. READ FIRST - Always understand what exists before proposing changes
2. BE SPECIFIC - Vague requirements lead to wrong implementations  
3. IDENTIFY DEPENDENCIES - What might be affected by changes?
4. THINK ABOUT TESTING - How will we verify success?
5. ASSESS RISKS - What could go wrong?
6. PRESERVE CONTEXT - What should NOT be changed?
7. CREATE ACTIONABLE STEPS - Developers need clear guidance

ANALYSIS METHODOLOGY:
1. Understand the issue thoroughly
2. Analyze existing codebase to understand current state
3. Extract specific, measurable requirements
4. Identify exactly what needs to change vs. what to preserve
5. Create step-by-step implementation guidance
6. Define comprehensive testing approach
7. Assess risks and create mitigation strategies

REMEMBER: Your analysis will directly guide implementation. If you're vague
or incomplete, developers will make assumptions that lead to disasters.

Focus on QUALITY and PRECISION over speed.

{format_instructions}'''
        
        human_message = '''Analyze this GitHub issue and codebase:

**Issue #{issue_number}: {title}**
Repository: {repository}

**Issue Description:**
{body}

**Task Description:** {task_description}

**Relevant Files Identified:**
{relevant_files}

**Existing Codebase Content:**
{codebase_content}

Create a comprehensive technical specification that ensures developers have 
everything they need to implement this correctly without causing disasters.

Focus on:
1. What exactly needs to be done (specific requirements)
2. What exists now (current behavior analysis) 
3. What should be preserved (critical for preventing PR #23 scenarios)
4. How to implement safely (step-by-step guidance)
5. How to validate success (testing strategy)
6. What could go wrong (risk assessment)'''
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            ("human", human_message)
        ])
    
    def _create_file_identification_prompt(self) -> ChatPromptTemplate:
        """Create prompt for identifying relevant files.
        
        Returns:
            Configured prompt template for file identification
        """
        system_message = '''You are an expert code analyst. Your job is to identify
which files in a repository are relevant to a GitHub issue.

Consider:
1. Files mentioned explicitly in the issue
2. Files likely affected by the proposed changes
3. Configuration files that might need updates
4. Test files that might need attention
5. Documentation files that might need updates
6. Dependencies and related components

Be thorough but focused - include files that are directly relevant.
Exclude files that are clearly unrelated.

Return a list of specific file paths from the provided file tree.'''
        
        human_message = '''Based on this GitHub issue, identify relevant files:

**Issue:** {issue_title}
**Description:** {issue_body}
**Labels:** {issue_labels}
**Repository:** {repository}

**Available files:**
{file_tree}

Return a prioritized list of file paths that should be analyzed for this issue.
Format as a simple list, one file path per line, most important first.'''
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            ("human", human_message)
        ])
    
    def _parse_file_paths_from_response(
        self, 
        response: str, 
        file_tree: List[str]
    ) -> List[str]:
        """Parse file paths from LLM response.
        
        Args:
            response: LLM response containing file paths
            file_tree: Available files to validate against
            
        Returns:
            List of valid file paths
        """
        file_paths = []
        file_tree_set = set(file_tree)
        
        # Split response into lines and extract file paths
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Remove common formatting but preserve file paths
            line = line.replace('`', '').strip()
            if line.startswith('- '):
                line = line[2:].strip()
            elif line.startswith('* '):
                line = line[2:].strip()
            elif line.startswith('+ '):
                line = line[2:].strip()
            
            # Skip empty lines and lines that don't look like paths
            if not line or line.startswith('#') or len(line) < 3:
                continue
            
            # First check if it's an exact match (direct file path)
            if line in file_tree_set:
                file_paths.append(line)
            
            # Check if this looks like a file path
            elif any(line.endswith(ext) for ext in [
                '.md', '.py', '.js', '.ts', '.tsx', '.jsx', '.json', 
                '.yml', '.yaml', '.txt', '.cfg', '.ini', '.toml'
            ]) or '/' in line:
                
                # Try to find partial matches
                matches = [f for f in file_tree if line in f or f.endswith(line)]
                if matches:
                    file_paths.extend(matches[:2])  # Add up to 2 matches
            
            # Check if the line contains any known file names
            for file_name in file_tree:
                if file_name in line and file_name not in file_paths:
                    # Make sure it's not a substring of another word
                    words = line.split()
                    for word in words:
                        word = word.strip('.,!?:;')
                        if word == file_name:
                            file_paths.append(file_name)
                            break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_paths = []
        for path in file_paths:
            if path not in seen:
                seen.add(path)
                unique_paths.append(path)
        
        return unique_paths
    
    async def _create_documentation(
        self,
        specification: TechnicalSpecification,
        issue: Dict[str, Any]
    ) -> str:
        """Create comprehensive documentation for the analysis.
        
        Args:
            specification: Technical specification to document
            issue: Original GitHub issue
            
        Returns:
            Formatted markdown documentation
        """
        issue_number = issue.get('number', 'Unknown')
        
        # Build documentation sections
        doc_parts = []
        
        # Header
        doc_parts.append(f"# Requirements Analysis - Issue #{issue_number}")
        doc_parts.append("")
        doc_parts.append("## Issue Summary")
        doc_parts.append(f"**Title**: {issue.get('title', 'No title')}")
        doc_parts.append(f"**Repository**: {specification.repository}")
        doc_parts.append(f"**Description**: {issue.get('body', 'No description')}")
        doc_parts.append(f"**Analysis Date**: {specification.created_at.strftime('%Y-%m-%d %H:%M UTC')}")
        doc_parts.append(f"**Confidence Score**: {specification.confidence_score:.2f}/1.0")
        doc_parts.append("")
        
        # Requirements
        doc_parts.append("## Requirements")
        doc_parts.append("")
        for i, req in enumerate(specification.requirements, 1):
            doc_parts.append(f"### Requirement {i}: {req.description}")
            doc_parts.append(f"- **ID**: {req.id}")
            doc_parts.append(f"- **Priority**: {req.priority}")
            doc_parts.append(f"- **Category**: {req.category}")
            doc_parts.append("- **Acceptance Criteria**:")
            for criteria in req.acceptance_criteria:
                doc_parts.append(f"  - {criteria}")
            if req.dependencies:
                doc_parts.append(f"- **Dependencies**: {', '.join(req.dependencies)}")
            doc_parts.append("")
        
        # Codebase Analysis
        doc_parts.append("## Codebase Analysis")
        doc_parts.append("")
        
        doc_parts.append("### Relevant Files")
        for file_path in specification.codebase_analysis.relevant_files:
            doc_parts.append(f"- `{file_path}`")
        doc_parts.append("")
        
        doc_parts.append("### Current Behavior")
        doc_parts.append(specification.codebase_analysis.current_behavior)
        doc_parts.append("")
        
        doc_parts.append("### Architecture Notes")
        doc_parts.append(specification.codebase_analysis.architecture_notes)
        doc_parts.append("")
        
        if specification.codebase_analysis.dependencies:
            doc_parts.append("### Dependencies")
            for dep in specification.codebase_analysis.dependencies:
                doc_parts.append(f"- {dep}")
            doc_parts.append("")
        
        doc_parts.append("### Potential Impacts")
        for impact in specification.codebase_analysis.potential_impacts:
            doc_parts.append(f"- {impact}")
        doc_parts.append("")
        
        # Implementation Guidance
        doc_parts.append("## Implementation Approach")
        doc_parts.append(specification.implementation_approach)
        doc_parts.append("")
        
        doc_parts.append("### Step-by-Step Plan")
        for i, step in enumerate(specification.step_by_step_plan, 1):
            doc_parts.append(f"{i}. {step}")
        doc_parts.append("")
        
        # Testing Strategy
        doc_parts.append("## Testing Strategy")
        doc_parts.append(specification.testing_strategy)
        doc_parts.append("")
        
        # Quality Assurance
        doc_parts.append("## Quality Assurance")
        doc_parts.append("")
        
        doc_parts.append("### Validation Checklist")
        for item in specification.validation_checklist:
            doc_parts.append(f"- [ ] {item}")
        doc_parts.append("")
        
        doc_parts.append("### Success Criteria")
        for criteria in specification.success_criteria:
            doc_parts.append(f"- {criteria}")
        doc_parts.append("")
        
        # Risk Assessment
        doc_parts.append("## Risk Assessment")
        for risk in specification.risk_assessment:
            doc_parts.append(f"- {risk}")
        doc_parts.append("")
        
        # Rollback Plan
        doc_parts.append("## Rollback Plan")
        doc_parts.append(specification.rollback_plan)
        doc_parts.append("")
        
        # Additional Information
        if specification.assumptions:
            doc_parts.append("## Assumptions")
            for assumption in specification.assumptions:
                doc_parts.append(f"- {assumption}")
            doc_parts.append("")
        
        if specification.open_questions:
            doc_parts.append("## Open Questions")
            for question in specification.open_questions:
                doc_parts.append(f"- {question}")
            doc_parts.append("")
        
        if specification.lessons_learned:
            doc_parts.append("## Lessons Learned")
            for lesson in specification.lessons_learned:
                doc_parts.append(f"- {lesson}")
            doc_parts.append("")
        
        # Footer
        doc_parts.append("---")
        doc_parts.append(f"*Generated by Analyst Agent v{specification.analyst_version}*")
        doc_parts.append(f"*Analysis completed at {specification.created_at.strftime('%Y-%m-%d %H:%M UTC')}*")
        
        return "\\n".join(doc_parts)
    
    def _format_labels(self, labels: List[Any]) -> str:
        """Format issue labels for display.
        
        Args:
            labels: List of label objects or strings
            
        Returns:
            Formatted label string
        """
        if not labels:
            return "No labels"
        
        label_names = []
        for label in labels:
            if isinstance(label, dict) and 'name' in label:
                label_names.append(label['name'])
            elif isinstance(label, str):
                label_names.append(label)
            else:
                label_names.append(str(label))
        
        return ', '.join(label_names) if label_names else "No labels"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Analyst Agent performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            'total_analyses': self.total_analyses,
            'total_files_read': self.total_files_read,
            'total_tokens_used': self.total_tokens_used,
            'average_tokens_per_analysis': (
                self.total_tokens_used / max(self.total_analyses, 1)
            ),
            'average_files_per_analysis': (
                self.total_files_read / max(self.total_analyses, 1)
            ),
            'max_files_to_analyze': self.max_files_to_analyze,
            'max_file_size_chars': self.max_file_size_chars
        }
    
    def _extract_feedback_summary(self, previous_feedback: Any) -> str:
        """Extract a summary from Navigator feedback for integration.
        
        Args:
            previous_feedback: Feedback from Navigator review
            
        Returns:
            Formatted feedback summary
        """
        try:
            if not previous_feedback:
                return "No previous feedback available"
            
            # Handle different feedback formats
            if hasattr(previous_feedback, 'overall_assessment'):
                summary_parts = [
                    f"Overall Assessment: {previous_feedback.overall_assessment}",
                    f"Decision: {previous_feedback.decision}",
                ]
                
                # Add specific requirements issues if available
                if hasattr(previous_feedback, 'requirements_issues') and previous_feedback.requirements_issues:
                    summary_parts.append("Requirements Issues:")
                    for issue in previous_feedback.requirements_issues[:5]:  # Limit to top 5
                        summary_parts.append(f"  - {issue.severity}: {issue.description}")
                
                # Add required changes
                if hasattr(previous_feedback, 'required_changes') and previous_feedback.required_changes:
                    summary_parts.append("Required Changes:")
                    for change in previous_feedback.required_changes[:5]:
                        summary_parts.append(f"  - {change}")
                
                # Add scores if available
                if hasattr(previous_feedback, 'completeness_score'):
                    summary_parts.append(
                        f"Quality Scores: Completeness={previous_feedback.completeness_score}/10, "
                        f"Clarity={previous_feedback.clarity_score}/10, "
                        f"Testability={previous_feedback.testability_score}/10"
                    )
                
                return "\\n".join(summary_parts)
            else:
                return str(previous_feedback)
                
        except Exception as e:
            logger.warning(f"Could not extract feedback summary: {e}")
            return f"Feedback available but could not be parsed: {str(e)}"
    
    def _determine_improvement_focus(self, previous_feedback: Any) -> str:
        """Determine what areas need improvement based on feedback.
        
        Args:
            previous_feedback: Feedback from Navigator review
            
        Returns:
            Focus areas for improvement
        """
        try:
            if not previous_feedback:
                return "General requirements improvement"
            
            focus_areas = []
            
            # Check scores to identify weak areas
            if hasattr(previous_feedback, 'completeness_score'):
                if previous_feedback.completeness_score < 7:
                    focus_areas.append("completeness")
                if previous_feedback.clarity_score < 7:
                    focus_areas.append("clarity")
                if previous_feedback.testability_score < 7:
                    focus_areas.append("testability")
            
            # Check for critical issues
            if hasattr(previous_feedback, 'requirements_issues'):
                critical_issues = [
                    issue for issue in previous_feedback.requirements_issues 
                    if issue.severity == "critical"
                ]
                if critical_issues:
                    focus_areas.append("critical issues")
            
            # Check for missing elements
            if hasattr(previous_feedback, 'missing_elements') and previous_feedback.missing_elements:
                focus_areas.append("missing elements")
            
            if focus_areas:
                return ", ".join(focus_areas)
            else:
                return "general quality improvements"
                
        except Exception as e:
            logger.warning(f"Could not determine improvement focus: {e}")
            return "general requirements improvement"
    
    def _get_main_feedback_areas(self, previous_feedback: Any) -> str:
        """Get the main areas highlighted in feedback.
        
        Args:
            previous_feedback: Feedback from Navigator review
            
        Returns:
            Main feedback areas
        """
        try:
            if not previous_feedback:
                return "unknown areas"
            
            if hasattr(previous_feedback, 'requirements_issues') and previous_feedback.requirements_issues:
                categories = set()
                for issue in previous_feedback.requirements_issues:
                    categories.add(issue.category)
                return ", ".join(sorted(categories))
            else:
                return "general requirements quality"
                
        except Exception as e:
            logger.warning(f"Could not extract main feedback areas: {e}")
            return "feedback processing"
    
    def _create_feedback_integration_prompt(self) -> ChatPromptTemplate:
        """Create prompt for feedback integration analysis.
        
        Returns:
            Configured prompt template for feedback integration
        """
        system_message = '''You are an expert Business Analyst improving requirements based on Navigator feedback.

Your job is to take the base requirements analysis and enhance it by addressing specific feedback from the Navigator agent. The Navigator has reviewed your work and identified areas that need improvement to prevent implementation disasters like PR #23.

CRITICAL IMPORTANCE: You are in iteration {iteration_number} of the requirements refinement process. The Navigator has provided specific feedback that you MUST address to create implementable, disaster-proof requirements.

FEEDBACK INTEGRATION APPROACH:
1. UNDERSTAND THE FEEDBACK - Analyze what the Navigator found lacking
2. IDENTIFY ROOT CAUSES - Why were the original requirements insufficient?
3. TARGETED IMPROVEMENTS - Address each specific issue raised
4. ENHANCE QUALITY - Improve the areas that scored poorly
5. MAINTAIN STRENGTHS - Keep what was already good
6. VALIDATE COMPLETENESS - Ensure all feedback is addressed

IMPROVEMENT FOCUS: {improvement_focus}

NAVIGATOR GUIDANCE: {iteration_guidance}

KEY PRINCIPLES:
- Be MORE SPECIFIC than before (address vagueness)
- Add MISSING ELEMENTS identified by Navigator
- Improve CLARITY where Navigator found confusion
- Enhance TESTABILITY with measurable criteria
- Fix any CONSISTENCY issues noted
- Address COMPLETENESS gaps

Remember: The Navigator is trying to prevent disasters. Their feedback is designed to catch what could go wrong during implementation. Take it seriously and address every point.

{format_instructions}'''
        
        human_message = '''FEEDBACK INTEGRATION REQUEST - Iteration {iteration_number}

**Original Issue #{issue_number}: {title}**
Repository: {repository}
Task: {task_description}

**NAVIGATOR FEEDBACK FROM PREVIOUS ITERATION:**
{previous_feedback}

**ITERATION GUIDANCE:**
{iteration_guidance}

**BASE SPECIFICATION (to be improved):**
{base_specification}

**IMPROVEMENT INSTRUCTIONS:**
Please create an improved technical specification that directly addresses all the Navigator feedback. Focus specifically on {improvement_focus}.

Make the requirements more specific, complete, and implementable. Address every concern raised by the Navigator. The goal is to create requirements so clear that no developer could misunderstand them and cause a disaster like PR #23.'''
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            ("human", human_message)
        ])
    
    def __str__(self) -> str:
        return f"AnalystAgent(analyses={self.total_analyses}, files_read={self.total_files_read})"