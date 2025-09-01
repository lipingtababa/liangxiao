"""Developer Agent implementation.

This module contains the DeveloperAgent class that generates code solutions
based on requirements from the AnalystAgent and works in pair programming
with the NavigatorAgent for quality review and iteration.
"""

import logging
import re
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path

from core.tools.ai_interface import AITool
from core.tools.factory import create_ai_tool
from pydantic import ValidationError

from core.interfaces import (
    StepResult as StandardStepResult, DeveloperInput as StandardDeveloperInput,
    DeveloperOutput as StandardDeveloperOutput, CodeChange,
    create_step_result, create_quality_metrics
)

from .models import (
    CodeArtifact, ImplementationResult, FileModification, CodeSolution,
    DeveloperContext, ArtifactType, ModificationType, ImplementationStatus,
    ProgrammingLanguage
)
from .exceptions import (
    DeveloperError, CodeGenerationError, SyntaxValidationError,
    FileOperationError, DisasterPreventionError, RequirementsInsufficientError,
    GitHubIntegrationError, ImplementationTimeoutError, ArtifactValidationError,
    validate_developer_context, validate_file_path_safety,
    validate_code_modification_safety, assess_implementation_risk
)
from services.github_service import GitHubService, GitHubCLIError
from core.logging import get_logger
from core.exceptions import AgentExecutionError

logger = get_logger(__name__)


class DeveloperAgent:
    """
    Developer agent that generates comprehensive code solutions.
    
    This agent acts as the "tasker" in pair programming with the Navigator,
    generating code implementations based on requirements from the Analyst.
    It focuses on preventing disasters like PR #23 by reading existing files
    before making modifications.
    
    Key Features:
    - Generates code in multiple programming languages
    - Reads existing codebase to understand context
    - Creates structured artifacts with proper metadata
    - Implements disaster prevention through safety checks
    - Integrates with GitHub service for file operations
    - Handles feedback and iteration from Navigator
    - Supports incremental and comprehensive implementations
    """
    
    def __init__(
        self,
        agent_type: str = "developer",
        github_service: Optional[GitHubService] = None,
        ai_tool: Optional[AITool] = None,
        timeout_seconds: int = 300,
        max_artifacts_per_solution: int = 10
    ):
        """Initialize the Developer Agent.
        
        Args:
            agent_type: Type of agent for tool selection (default: developer)
            github_service: GitHub service for repository operations
            ai_tool: Pre-configured AI tool instance (optional)
            timeout_seconds: Timeout for implementation operations
            max_artifacts_per_solution: Maximum artifacts per solution
        """
        self.agent_type = agent_type
        self.github_service = github_service
        self.timeout_seconds = timeout_seconds
        self.max_artifacts_per_solution = max_artifacts_per_solution
        
        # Initialize AI tool (Claude Code or OpenAI based on config)
        self.ai_tool = ai_tool or create_ai_tool(agent_type)
        
        # Language-specific configurations
        self.language_configs = self._initialize_language_configs()
        
        # Metrics tracking
        self.total_implementations = 0
        self.total_artifacts_created = 0
        self.total_files_read = 0
        self.disaster_prevention_triggers = 0
        
        logger.info(f"Developer Agent initialized with {self.ai_tool.tool_type} tool")
    
    def _initialize_language_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize language-specific configurations.
        
        Returns:
            Dictionary mapping languages to their configurations
        """
        return {
            "python": {
                "file_extension": ".py",
                "comment_style": "#",
                "import_style": "import",
                "class_keyword": "class",
                "function_keyword": "def",
                "common_imports": ["import os", "import sys", "from typing import"],
                "linting_tools": ["flake8", "pylint", "mypy"],
                "testing_framework": "pytest"
            },
            "javascript": {
                "file_extension": ".js",
                "comment_style": "//",
                "import_style": "import/require",
                "class_keyword": "class",
                "function_keyword": "function",
                "common_imports": ["const", "import"],
                "linting_tools": ["eslint", "jshint"],
                "testing_framework": "jest"
            },
            "typescript": {
                "file_extension": ".ts",
                "comment_style": "//",
                "import_style": "import",
                "class_keyword": "class",
                "function_keyword": "function",
                "common_imports": ["import", "interface", "type"],
                "linting_tools": ["tslint", "eslint"],
                "testing_framework": "jest"
            },
            "java": {
                "file_extension": ".java",
                "comment_style": "//",
                "import_style": "import",
                "class_keyword": "public class",
                "function_keyword": "public",
                "common_imports": ["import java.util.*", "import java.io.*"],
                "linting_tools": ["checkstyle", "spotbugs"],
                "testing_framework": "junit"
            }
        }
    
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute development task and generate code solution.
        
        Args:
            task: Task definition containing:
                - id: Task identifier
                - description: Task description
                - type: Should be 'implementation'
                - requirements: Optional requirements list
            context: Execution context containing:
                - issue: GitHub issue data
                - repository: Repository identifier
                - completed_tasks: Previous task results
                - navigator_feedback: Feedback from Navigator (if iteration)
                
        Returns:
            Implementation result with artifacts and status
        """
        start_time = datetime.utcnow()
        task_id = task.get('id', 'unknown')
        
        logger.info(f"Developer executing task: {task_id}")
        
        try:
            # Validate and prepare context
            validate_developer_context(context)
            dev_context = await self._prepare_developer_context(task, context)
            
            # Check for timeout
            async with asyncio.timeout(self.timeout_seconds):
                # Generate code solution
                solution = await self._generate_code_solution(dev_context)
                
                # Validate solution safety
                await self._validate_solution_safety(solution, dev_context)
                
                # Create artifacts with GitHub integration
                artifacts_created = await self._create_artifacts(solution, dev_context)
                
                # Calculate execution metrics
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Create implementation result
                result = ImplementationResult(
                    status=ImplementationStatus.COMPLETED,
                    success=True,
                    solution=solution,
                    artifacts_created=artifacts_created,
                    execution_time_seconds=execution_time,
                    tokens_used=self._get_tokens_used(),
                    safety_checks_performed=self._get_safety_checks_performed(solution),
                    files_read_from_repo=self._get_files_read(),
                    summary=f"Generated {len(artifacts_created)} artifacts implementing {solution.description}",
                    iteration_number=dev_context.get_iteration_number(),
                    addressed_previous_feedback=self._get_addressed_feedback(dev_context)
                )
                
                # Update metrics
                self.total_implementations += 1
                self.total_artifacts_created += len(artifacts_created)
                
                logger.info(
                    f"Developer task completed successfully: {len(artifacts_created)} artifacts, "
                    f"{execution_time:.2f}s, iteration {dev_context.get_iteration_number()}"
                )
                
                return {
                    "success": True,
                    "artifacts": [artifact.model_dump() for artifact in artifacts_created],
                    "solution_summary": solution.model_dump(),
                    "implementation_result": result.model_dump(),
                    "summary": result.summary,
                    "execution_time": execution_time,
                    "iteration_number": dev_context.get_iteration_number(),
                    "disaster_prevention_score": self._calculate_disaster_prevention_score(solution)
                }
                
        except asyncio.TimeoutError:
            error = ImplementationTimeoutError(
                f"Implementation timed out after {self.timeout_seconds} seconds",
                timeout_seconds=self.timeout_seconds,
                elapsed_seconds=(datetime.utcnow() - start_time).total_seconds()
            )
            logger.error(f"Developer task timeout: {error}")
            return self._create_error_response(error, task_id)
            
        except DeveloperError as e:
            logger.error(f"Developer-specific error: {e}")
            return self._create_error_response(e, task_id)
            
        except Exception as e:
            logger.error(f"Unexpected error in Developer execution: {e}", exc_info=True)
            wrapped_error = DeveloperError(f"Unexpected error: {str(e)}", {"task_id": task_id})
            return self._create_error_response(wrapped_error, task_id)
    
    async def _prepare_developer_context(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> DeveloperContext:
        """Prepare comprehensive developer context from task and execution context.
        
        Args:
            task: Task definition
            context: Execution context
            
        Returns:
            Prepared developer context
        """
        # Extract repository information
        repository = context.get("repository", "")
        if not repository:
            raise DeveloperError("Repository not specified in context")
        
        # Extract requirements from completed tasks (usually from Analyst)
        requirements = self._extract_requirements_from_context(context)
        
        # Extract previous iterations and Navigator feedback
        previous_iterations = self._extract_previous_iterations(context)
        navigator_feedback = context.get("navigator_feedback")
        
        # Get existing repository files if GitHub service is available
        existing_files = []
        project_language = None
        frameworks_used = []
        
        if self.github_service:
            try:
                existing_files = await self._get_repository_files(repository)
                project_language = self._detect_project_language(existing_files)
                frameworks_used = await self._detect_frameworks(existing_files, repository)
            except Exception as e:
                logger.warning(f"Could not retrieve repository information: {e}")
        
        return DeveloperContext(
            task=task,
            requirements=requirements,
            repository=repository,
            existing_files=existing_files,
            project_language=project_language,
            frameworks_used=frameworks_used,
            previous_iterations=previous_iterations,
            navigator_feedback=navigator_feedback,
            github_service_available=self.github_service is not None
        )
    
    async def execute_standardized(self, developer_input: StandardDeveloperInput) -> StandardStepResult:
        """
        Execute developer with standardized interface for Dynamic PM system.
        
        Args:
            developer_input: Standardized input for developer
            
        Returns:
            Standardized StepResult with implementation output
        """
        start_time = datetime.utcnow()
        
        try:
            # Convert standardized input to legacy format for existing execute method
            task = {
                "id": f"implementation_{datetime.utcnow().timestamp()}",
                "type": "implementation",
                "description": developer_input.requirements
            }
            
            context = {
                "requirements": {
                    "acceptance_criteria": developer_input.acceptance_criteria,
                    "implementation_requirements": developer_input.requirements
                },
                "testing": {
                    "test_file_path": developer_input.test_file_path
                }
            }
            
            # Execute using existing method
            legacy_result = await self.execute(task, context)
            
            # Convert to standardized format
            if legacy_result.get("success", False):
                # Extract implementation information
                artifacts = legacy_result.get("artifacts", [])
                changes_made = []
                implementation_notes = legacy_result.get("summary", "Implementation completed")
                tests_passed = legacy_result.get("test_results", {}).get("all_passed", False)
                test_output = legacy_result.get("test_results", {}).get("output", "")
                
                # Convert artifacts to CodeChange format
                for artifact in artifacts:
                    if artifact.get("type") == "code_file":
                        # Create a diff representation
                        file_path = artifact.get("path", "")
                        content = artifact.get("content", "")
                        
                        # Simple diff representation (in real implementation, would generate proper diff)
                        diff = f"--- a/{file_path}\n+++ b/{file_path}\n" + \
                               f"@@ -0,0 +{len(content.split())} @@\n" + \
                               "\n".join(f"+{line}" for line in content.split('\n')[:10])  # Truncate for display
                        
                        changes_made.append(CodeChange(
                            file_path=file_path,
                            diff=diff,
                            summary=artifact.get("description", f"Modified {file_path}")
                        ))
                
                # Create standardized output
                output_data = StandardDeveloperOutput(
                    changes_made=changes_made,
                    tests_passed=tests_passed,
                    test_output=test_output,
                    implementation_notes=implementation_notes
                ).model_dump()
                
                # Calculate confidence based on test results and implementation quality
                test_score = 0.4 if tests_passed else 0.0
                impl_score = min(0.6, len(changes_made) / 3 * 0.6)  # More changes might be better implementation
                confidence = test_score + impl_score
                
                # Create quality metrics
                quality_metrics = create_quality_metrics(
                    completeness=0.9 if tests_passed else 0.6,
                    accuracy=confidence,
                    code_quality=legacy_result.get("code_quality_score", 0.8),
                    critical_issues=len([issue for issue in legacy_result.get("validation_errors", []) 
                                       if issue.get("severity") == "critical"]),
                    warnings=len(legacy_result.get("warnings", []))
                )
                
                status = "success"
                suggestions = ["run_integration_tests", "review_code_quality"] if tests_passed else ["fix_failing_tests"]
                
            else:
                # Handle failure case
                output_data = {
                    "error": legacy_result.get("error", "Implementation failed"),
                    "error_details": legacy_result.get("error_details", {}),
                    "changes_made": [],
                    "tests_passed": False,
                    "test_output": "",
                    "implementation_notes": "Implementation failed"
                }
                
                confidence = 0.0
                quality_metrics = create_quality_metrics(
                    completeness=0.0,
                    accuracy=0.0,
                    critical_issues=1,
                    warnings=1
                )
                
                status = "failed"
                suggestions = ["retry_implementation", "simplify_requirements"]
            
            return create_step_result(
                agent="developer",
                status=status,
                output_data=output_data,
                confidence=confidence,
                suggestions=suggestions,
                quality_metrics=quality_metrics
            )
            
        except Exception as e:
            logger.error(f"Standardized developer execution failed: {e}")
            
            return create_step_result(
                agent="developer",
                status="failed",
                output_data={
                    "error": str(e),
                    "changes_made": [],
                    "tests_passed": False,
                    "test_output": "",
                    "implementation_notes": "Implementation failed due to error"
                },
                confidence=0.0,
                suggestions=["retry_implementation", "escalate_to_human"],
                quality_metrics=create_quality_metrics(
                    completeness=0.0,
                    accuracy=0.0,
                    critical_issues=1,
                    warnings=0
                )
            )
    
    def _extract_requirements_from_context(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract requirements from completed tasks, typically from Analyst."""
        completed_tasks = context.get("completed_tasks", [])
        
        for task_result in completed_tasks:
            if task_result.get("type") == "analysis":
                # Look for Analyst requirements
                artifacts = task_result.get("artifacts", [])
                for artifact in artifacts:
                    if artifact.get("type") == "requirements":
                        return {
                            "specification": artifact.get("specification", {}),
                            "requirements": artifact.get("specification", {}).get("requirements", []),
                            "implementation_approach": artifact.get("specification", {}).get("implementation_approach", ""),
                            "step_by_step_plan": artifact.get("specification", {}).get("step_by_step_plan", [])
                        }
        
        # Fallback to issue information
        issue = context.get("issue", {})
        if issue:
            return {
                "requirements": [issue.get("body", "")],
                "issue_title": issue.get("title", ""),
                "issue_number": issue.get("number")
            }
        
        return None
    
    def _extract_previous_iterations(self, context: Dict[str, Any]) -> List[ImplementationResult]:
        """Extract previous implementation iterations from context."""
        # This would contain previous Developer iterations in a real system
        # For now, we'll return empty list but structure is ready
        return []
    
    async def _get_repository_files(self, repository: str) -> List[str]:
        """Get list of files in the repository.
        
        Args:
            repository: Repository identifier
            
        Returns:
            List of file paths in the repository
        """
        try:
            if hasattr(self.github_service, 'get_file_tree'):
                return await self.github_service.get_file_tree()
            else:
                logger.warning("GitHub service does not support get_file_tree")
                return []
        except Exception as e:
            logger.error(f"Failed to get repository files: {e}")
            return []
    
    def _detect_project_language(self, file_paths: List[str]) -> Optional[ProgrammingLanguage]:
        """Detect primary programming language from file paths.
        
        Args:
            file_paths: List of file paths in repository
            
        Returns:
            Detected programming language or None
        """
        if not file_paths:
            return None
        
        # Count file extensions
        extension_counts = {}
        for file_path in file_paths:
            if '.' in file_path:
                ext = file_path.split('.')[-1].lower()
                extension_counts[ext] = extension_counts.get(ext, 0) + 1
        
        # Map extensions to languages
        extension_to_language = {
            'py': ProgrammingLanguage.PYTHON,
            'js': ProgrammingLanguage.JAVASCRIPT,
            'ts': ProgrammingLanguage.TYPESCRIPT,
            'java': ProgrammingLanguage.JAVA,
            'go': ProgrammingLanguage.GO,
            'rs': ProgrammingLanguage.RUST,
            'cpp': ProgrammingLanguage.CPP,
            'cs': ProgrammingLanguage.CSHARP,
            'sh': ProgrammingLanguage.SHELL
        }
        
        # Find most common language extension
        if extension_counts:
            most_common_ext = max(extension_counts, key=extension_counts.get)
            return extension_to_language.get(most_common_ext)
        
        return None
    
    async def _detect_frameworks(self, file_paths: List[str], repository: str) -> List[str]:
        """Detect frameworks used in the project.
        
        Args:
            file_paths: List of file paths in repository  
            repository: Repository identifier
            
        Returns:
            List of detected frameworks
        """
        frameworks = []
        
        # Check for common configuration files
        framework_indicators = {
            'package.json': ['react', 'vue', 'angular', 'express', 'nest'],
            'requirements.txt': ['django', 'flask', 'fastapi', 'pandas'],
            'pyproject.toml': ['django', 'flask', 'fastapi', 'poetry'],
            'Cargo.toml': ['tokio', 'actix-web', 'warp'],
            'pom.xml': ['spring', 'spring-boot'],
            'build.gradle': ['spring', 'android']
        }
        
        # Look for configuration files and try to read them
        for file_path in file_paths:
            filename = file_path.split('/')[-1]
            if filename in framework_indicators and self.github_service:
                try:
                    content = self.github_service.read_file(file_path)
                    if content:
                        # Simple framework detection based on content
                        content_lower = content.lower()
                        for framework in framework_indicators[filename]:
                            if framework in content_lower:
                                frameworks.append(framework)
                        
                        # Break after first config file to avoid too many reads
                        break
                except Exception as e:
                    logger.warning(f"Could not read {file_path} for framework detection: {e}")
        
        return list(set(frameworks))  # Remove duplicates
    
    async def _generate_code_solution(self, dev_context: DeveloperContext) -> CodeSolution:
        """Generate comprehensive code solution based on developer context.
        
        Args:
            dev_context: Developer context with requirements and repository info
            
        Returns:
            Generated code solution with artifacts
            
        Raises:
            CodeGenerationError: If code generation fails
        """
        logger.info("Generating code solution")
        
        try:
            # Read existing relevant files for context
            existing_code_context = await self._read_existing_code_context(dev_context)
            
            # Create generation prompt
            prompt = self._create_code_generation_prompt()
            
            # Format prompt with all context
            formatted_inputs = {
                "format_instructions": self.parser.get_format_instructions(),
                "task_description": dev_context.task.get("description", ""),
                "task_type": dev_context.task.get("type", "implementation"),
                "requirements": self._format_requirements(dev_context.requirements),
                "repository": dev_context.repository,
                "project_language": dev_context.project_language or "unknown",
                "frameworks_used": ", ".join(dev_context.frameworks_used) if dev_context.frameworks_used else "none detected",
                "existing_files": self._format_existing_files(dev_context.existing_files),
                "existing_code_context": existing_code_context,
                "iteration_number": dev_context.get_iteration_number(),
                "previous_feedback": self._format_navigator_feedback(dev_context.navigator_feedback),
                "disaster_prevention_guidance": self._get_disaster_prevention_guidance(),
                "language_config": self._get_language_config_guidance(dev_context.project_language),
                "max_artifacts": self.max_artifacts_per_solution
            }
            
            # Generate solution using unified AI tool interface
            full_prompt = self._format_unified_prompt(formatted_inputs)
            
            context = {
                "timeout": self.timeout_seconds,
                "files": existing_code_context,
                "language": formatted_inputs.get("project_language"),
                "frameworks": formatted_inputs.get("frameworks_used")
            }
            
            response_content = await self.ai_tool.execute(
                prompt=full_prompt,
                context=context,
                system_prompt="You are an expert software developer focused on code generation and disaster prevention."
            )
            
            # Parse structured output
            try:
                # For now, create a simple parser - can be enhanced later
                solution = self._parse_ai_response(response_content, dev_context)
            except (OutputParserException, ValidationError) as e:
                logger.warning(f"Failed to parse structured solution, creating fallback: {e}")
                solution = self._create_fallback_solution(dev_context, response.content)
            
            # Set solution metadata
            solution.issue_number = dev_context.requirements.get("issue_number") if dev_context.requirements else None
            
            logger.info(f"Generated solution with {solution.get_total_artifacts()} artifacts")
            return solution
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise CodeGenerationError(
                f"Failed to generate code solution: {str(e)}",
                language=str(dev_context.project_language) if dev_context.project_language else None,
                requirements=dev_context.requirements.get("requirements", []) if dev_context.requirements else [],
                context={"task_id": dev_context.task.get("id"), "repository": dev_context.repository}
            ) from e
    
    async def _read_existing_code_context(self, dev_context: DeveloperContext) -> str:
        """Read existing code files to provide context for generation.
        
        Args:
            dev_context: Developer context
            
        Returns:
            Formatted string with existing code context
        """
        if not self.github_service or not dev_context.existing_files:
            return "No existing code context available"
        
        # Get most relevant files
        relevant_files = dev_context.get_relevant_existing_files(max_files=5)
        
        code_context_parts = []
        files_read = 0
        
        for file_path in relevant_files:
            try:
                content = self.github_service.read_file(file_path)
                if content:
                    # Limit content size
                    if len(content) > 2000:
                        content = content[:2000] + "\n... [truncated]"
                    
                    code_context_parts.append(f"=== {file_path} ===\n{content}\n")
                    files_read += 1
                    self.total_files_read += 1
                    
            except Exception as e:
                logger.warning(f"Could not read {file_path} for context: {e}")
        
        logger.info(f"Read {files_read} files for code generation context")
        return "\n".join(code_context_parts) if code_context_parts else "No existing code context available"
    
    def _create_code_generation_prompt(self) -> str:
        """Create the comprehensive code generation prompt.
        
        Returns:
            Configured prompt template for code generation
        """
        system_message = '''You are an expert software developer who generates high-quality code implementations.

Your job is to create complete, working code solutions based on requirements while
preventing disasters like PR #23 (where a developer deleted an entire README when 
asked to remove just one phrase).

CRITICAL PRINCIPLES:
1. READ FIRST - Always understand existing code before making changes
2. PRESERVE CONTENT - Never delete entire files when only small changes needed
3. BE SURGICAL - Make targeted modifications, not wholesale replacements
4. VALIDATE SYNTAX - Generate syntactically correct code
5. FOLLOW CONVENTIONS - Use appropriate language/framework patterns
6. DOCUMENT CHANGES - Explain what you're doing and why
7. SAFETY CHECKS - Include disaster prevention measures

CODE GENERATION REQUIREMENTS:
- Generate complete, executable code
- Use appropriate language/framework conventions
- Include proper error handling
- Add comprehensive comments and documentation
- Follow established project patterns
- Create tests when appropriate
- Include configuration files if needed

DISASTER PREVENTION MEASURES:
- When modifying existing files, preserve important content
- Use targeted replacements instead of complete rewrites
- Include safety checks in file modifications
- Document what content should be preserved
- Create backups for critical modifications

ARTIFACT TYPES TO CREATE:
- code: Main implementation files
- test: Test files for the implementation
- documentation: README updates, API docs
- configuration: Config files, environment setup
- migration: Database migrations, data updates

Language: {project_language}
Frameworks: {frameworks_used}
Max Artifacts: {max_artifacts}

{disaster_prevention_guidance}

{language_config}

{format_instructions}'''
        
        human_message = '''Create a complete code solution for this task:

**Task:** {task_description}
**Type:** {task_type}
**Repository:** {repository}
**Iteration:** {iteration_number}

**Requirements:**
{requirements}

**Existing Project Files:**
{existing_files}

**Existing Code Context:**
{existing_code_context}

{previous_feedback}

Generate a comprehensive CodeSolution with appropriate artifacts. Focus on:
1. Addressing all requirements completely
2. Following project conventions and patterns  
3. Creating clean, maintainable code
4. Including appropriate tests and documentation
5. Implementing disaster prevention measures
6. Preserving existing important content when modifying files

Be specific about what each artifact does and why it's needed.'''
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_message),
            ("human", human_message)
        ])
    
    def _format_requirements(self, requirements: Optional[Dict[str, Any]]) -> str:
        """Format requirements for prompt inclusion.
        
        Args:
            requirements: Requirements dictionary from Analyst
            
        Returns:
            Formatted requirements string
        """
        if not requirements:
            return "No specific requirements provided - implement based on task description"
        
        parts = []
        
        # Add structured requirements if available
        if "requirements" in requirements:
            reqs = requirements["requirements"]
            if isinstance(reqs, list):
                parts.append("Specific Requirements:")
                for i, req in enumerate(reqs, 1):
                    if isinstance(req, dict):
                        desc = req.get("description", str(req))
                        priority = req.get("priority", "unknown")
                        parts.append(f"{i}. [{priority}] {desc}")
                    else:
                        parts.append(f"{i}. {str(req)}")
        
        # Add implementation approach if available
        if "implementation_approach" in requirements:
            approach = requirements["implementation_approach"]
            if approach:
                parts.append(f"\nImplementation Approach:\n{approach}")
        
        # Add step-by-step plan if available
        if "step_by_step_plan" in requirements:
            plan = requirements["step_by_step_plan"]
            if isinstance(plan, list) and plan:
                parts.append("\nImplementation Steps:")
                for i, step in enumerate(plan, 1):
                    parts.append(f"{i}. {step}")
        
        return "\n".join(parts) if parts else "No specific requirements provided"
    
    def _format_existing_files(self, existing_files: List[str]) -> str:
        """Format existing files list for prompt.
        
        Args:
            existing_files: List of existing file paths
            
        Returns:
            Formatted files string
        """
        if not existing_files:
            return "No existing files information available"
        
        # Organize by type
        code_files = []
        config_files = []
        doc_files = []
        test_files = []
        
        for file_path in existing_files[:20]:  # Limit to first 20
            filename = file_path.split('/')[-1].lower()
            if any(ext in filename for ext in ['.py', '.js', '.ts', '.java', '.go', '.rs']):
                code_files.append(file_path)
            elif any(ext in filename for ext in ['.json', '.yml', '.yaml', '.toml', '.ini']):
                config_files.append(file_path)
            elif any(ext in filename for ext in ['.md', '.txt', '.rst']):
                doc_files.append(file_path)
            elif 'test' in filename:
                test_files.append(file_path)
        
        parts = []
        if code_files:
            parts.append(f"Code files: {', '.join(code_files[:5])}")
        if config_files:
            parts.append(f"Config files: {', '.join(config_files[:3])}")
        if doc_files:
            parts.append(f"Documentation: {', '.join(doc_files[:3])}")
        if test_files:
            parts.append(f"Tests: {', '.join(test_files[:3])}")
        
        return "\n".join(parts) if parts else "File structure analysis not available"
    
    def _format_navigator_feedback(self, navigator_feedback: Optional[Dict[str, Any]]) -> str:
        """Format Navigator feedback for prompt inclusion.
        
        Args:
            navigator_feedback: Feedback from Navigator agent
            
        Returns:
            Formatted feedback string
        """
        if not navigator_feedback:
            return ""
        
        parts = ["\n**Previous Navigator Feedback:**"]
        
        # Extract key feedback elements
        decision = navigator_feedback.get("decision", "unknown")
        parts.append(f"Decision: {decision}")
        
        overall_assessment = navigator_feedback.get("overall_assessment")
        if overall_assessment:
            parts.append(f"Assessment: {overall_assessment}")
        
        required_changes = navigator_feedback.get("required_changes", [])
        if required_changes:
            parts.append("Required Changes:")
            for change in required_changes:
                parts.append(f"- {change}")
        
        issues = navigator_feedback.get("issues", [])
        if issues:
            parts.append("Issues to Address:")
            for issue in issues:
                if isinstance(issue, dict):
                    severity = issue.get("severity", "unknown")
                    description = issue.get("description", "")
                    suggestion = issue.get("suggestion", "")
                    parts.append(f"- [{severity}] {description}")
                    if suggestion:
                        parts.append(f"  Suggestion: {suggestion}")
                else:
                    parts.append(f"- {str(issue)}")
        
        return "\n".join(parts)
    
    def _get_disaster_prevention_guidance(self) -> str:
        """Get disaster prevention guidance for the prompt.
        
        Returns:
            Disaster prevention guidance text
        """
        return '''DISASTER PREVENTION CHECKLIST:

1. **File Modification Safety:**
   - Read existing file content first before modifying
   - Preserve important sections (headers, licenses, key functions)
   - Use targeted replacements instead of complete rewrites
   - Document what content must be preserved

2. **Content Preservation:**
   - Never delete entire README files when only removing phrases
   - Preserve copyright notices, licenses, and attribution
   - Keep existing imports and dependencies unless changing them
   - Maintain existing directory structure unless specifically required

3. **Surgical Changes:**
   - Identify specific sections to modify
   - Use precise string replacements
   - Add new content without removing existing content
   - Document the scope of each change

4. **Safety Checks:**
   - Validate syntax before generating artifacts
   - Check that modifications align with stated requirements
   - Ensure file operations are reversible
   - Include rollback instructions'''
    
    def _get_language_config_guidance(self, language: Optional[ProgrammingLanguage]) -> str:
        """Get language-specific configuration guidance.
        
        Args:
            language: Detected programming language
            
        Returns:
            Language-specific guidance
        """
        if not language:
            return "LANGUAGE: Not detected - use appropriate conventions for the task"
        
        config = self.language_configs.get(str(language).split('.')[-1].lower(), {})
        
        if not config:
            return f"LANGUAGE: {language} - use appropriate conventions"
        
        return f'''LANGUAGE CONFIG FOR {language.upper()}:

File Extension: {config.get("file_extension", "unknown")}
Comment Style: {config.get("comment_style", "unknown")}
Function Keyword: {config.get("function_keyword", "unknown")}
Testing Framework: {config.get("testing_framework", "unknown")}

Common Imports:
{chr(10).join(f"- {imp}" for imp in config.get("common_imports", []))}

Follow {language} conventions for:
- Code formatting and style
- Naming conventions
- Error handling patterns
- Documentation standards'''
    
    def _create_fallback_solution(
        self,
        dev_context: DeveloperContext,
        llm_response: str
    ) -> CodeSolution:
        """Create fallback solution when structured parsing fails.
        
        Args:
            dev_context: Developer context
            llm_response: Raw LLM response
            
        Returns:
            Fallback code solution
        """
        logger.warning("Creating fallback solution due to parsing failure")
        
        # Extract basic information
        task_desc = dev_context.task.get("description", "Implementation task")
        language = dev_context.project_language or ProgrammingLanguage.PYTHON
        
        # Create basic artifact from LLM response
        fallback_artifact = CodeArtifact(
            type=ArtifactType.CODE,
            path=f"src/main{self.language_configs.get(str(language).split('.')[-1].lower(), {}).get('file_extension', '.py')}",
            content=llm_response[:5000],  # Limit content size
            language=language,
            description="Fallback implementation - manual review required",
            modification_type=ModificationType.CREATE,
            safety_checks=["fallback_generation"],
            disaster_prevention_notes=["Generated as fallback - requires manual validation"]
        )
        
        return CodeSolution(
            solution_id=f"fallback-{dev_context.task.get('id', 'unknown')}",
            description=f"Fallback solution for: {task_desc}",
            requirements_addressed=dev_context.requirements.get("requirements", []) if dev_context.requirements else [],
            primary_language=language,
            artifacts=[fallback_artifact],
            test_strategy="Manual testing required for fallback solution",
            disaster_prevention_measures=["Fallback generation due to parsing issues"],
            rollback_plan="Remove generated files and retry implementation",
            estimated_complexity="medium"
        )
    
    async def _validate_solution_safety(
        self,
        solution: CodeSolution,
        dev_context: DeveloperContext
    ) -> None:
        """Validate that the solution is safe to implement.
        
        Args:
            solution: Generated code solution
            dev_context: Developer context
            
        Raises:
            DisasterPreventionError: If solution appears dangerous
        """
        logger.info("Validating solution safety")
        
        # Check for dangerous file operations
        modified_files = solution.get_modified_files()
        
        for artifact in modified_files:
            # Validate file path safety
            validate_file_path_safety(artifact.path)
            
            # Check if we have existing content context for modifications
            if artifact.modification_type == ModificationType.UPDATE:
                if not artifact.existing_content_preserved and not artifact.safety_checks:
                    self.disaster_prevention_triggers += 1
                    raise DisasterPreventionError(
                        f"Unsafe file modification detected for {artifact.path}",
                        dangerous_operation="modify_without_reading_existing",
                        file_path=artifact.path,
                        prevention_check="read_existing_content_first",
                        context={"artifact_type": artifact.type, "task_id": dev_context.task.get("id")}
                    )
        
        # Check overall implementation risk
        risk_assessment = assess_implementation_risk(
            [artifact.model_dump() for artifact in solution.artifacts],
            [mod.model_dump() for mod in solution.file_modifications]
        )
        
        if risk_assessment["risk_level"] == "very_high":
            logger.warning(f"High-risk implementation detected: {risk_assessment}")
            # Don't block, but log for monitoring
        
        logger.info(f"Solution safety validation passed, risk level: {risk_assessment['risk_level']}")
    
    async def _create_artifacts(
        self,
        solution: CodeSolution,
        dev_context: DeveloperContext
    ) -> List[CodeArtifact]:
        """Create artifacts with GitHub integration and safety checks.
        
        Args:
            solution: Code solution to implement
            dev_context: Developer context
            
        Returns:
            List of successfully created artifacts
        """
        logger.info(f"Creating {len(solution.artifacts)} artifacts")
        
        created_artifacts = []
        
        for artifact in solution.artifacts:
            try:
                # Validate artifact safety
                await self._validate_artifact_safety(artifact, dev_context)
                
                # Perform GitHub integration if available
                if self.github_service and artifact.modification_type == ModificationType.UPDATE:
                    await self._prepare_artifact_for_modification(artifact, dev_context)
                
                # Validate syntax if possible
                self._validate_artifact_syntax(artifact)
                
                created_artifacts.append(artifact)
                
            except Exception as e:
                logger.error(f"Failed to create artifact {artifact.path}: {e}")
                # Continue with other artifacts
                continue
        
        logger.info(f"Successfully created {len(created_artifacts)} out of {len(solution.artifacts)} artifacts")
        return created_artifacts
    
    async def _validate_artifact_safety(
        self,
        artifact: CodeArtifact,
        dev_context: DeveloperContext
    ) -> None:
        """Validate that an individual artifact is safe to create.
        
        Args:
            artifact: Artifact to validate
            dev_context: Developer context
            
        Raises:
            ArtifactValidationError: If artifact is invalid or unsafe
        """
        validation_errors = []
        
        # Basic validation
        if not artifact.path or not artifact.content:
            validation_errors.append("Artifact missing path or content")
        
        # Path safety validation
        try:
            validate_file_path_safety(artifact.path)
        except DisasterPreventionError as e:
            validation_errors.append(f"Unsafe file path: {e}")
        
        # Content validation
        if len(artifact.content) < 10:
            validation_errors.append("Artifact content too short (may be truncated)")
        
        # Safety checks validation
        if artifact.modification_type == ModificationType.UPDATE:
            if not artifact.safety_checks:
                validation_errors.append("File modification without safety checks")
        
        if validation_errors:
            raise ArtifactValidationError(
                f"Artifact validation failed: {'; '.join(validation_errors)}",
                artifact_path=artifact.path,
                validation_errors=validation_errors
            )
    
    async def _prepare_artifact_for_modification(
        self,
        artifact: CodeArtifact,
        dev_context: DeveloperContext
    ) -> None:
        """Prepare artifact for safe file modification by reading existing content.
        
        Args:
            artifact: Artifact that will modify existing file
            dev_context: Developer context
        """
        if not self.github_service:
            return
        
        try:
            existing_content = self.github_service.read_file(artifact.path)
            if existing_content:
                # Store existing content for safety
                artifact.existing_content_preserved = existing_content[:500]  # First 500 chars
                
                # Add safety checks
                artifact.safety_checks.extend([
                    "read_existing_file_first",
                    "existing_content_retrieved",
                    "modification_scope_validated"
                ])
                
                # Validate modification safety
                validate_code_modification_safety(
                    file_path=artifact.path,
                    original_content=existing_content,
                    new_content=artifact.content,
                    intended_change=artifact.description
                )
                
                logger.info(f"Prepared safe modification for {artifact.path}")
                
        except GitHubCLIError as e:
            logger.warning(f"Could not read existing file {artifact.path}: {e}")
            # File might not exist yet, which is OK for some modifications
        except Exception as e:
            logger.error(f"Error preparing artifact modification: {e}")
            raise FileOperationError(
                f"Failed to prepare modification for {artifact.path}",
                operation="read_for_modification",
                file_path=artifact.path,
                underlying_error=e
            )
    
    def _validate_artifact_syntax(self, artifact: CodeArtifact) -> None:
        """Validate artifact syntax if possible.
        
        Args:
            artifact: Artifact to validate
        """
        if not artifact.language:
            return
        
        # Basic syntax validation for known languages
        try:
            if artifact.language == ProgrammingLanguage.PYTHON:
                compile(artifact.content, artifact.path, 'exec')
                artifact.syntax_validated = True
            elif artifact.language in [ProgrammingLanguage.JAVASCRIPT, ProgrammingLanguage.TYPESCRIPT]:
                # Basic JavaScript/TypeScript syntax checks
                if artifact.content.count('{') != artifact.content.count('}'):
                    raise SyntaxError("Unmatched braces")
                artifact.syntax_validated = True
            # Add more language validations as needed
            
        except SyntaxError as e:
            logger.warning(f"Syntax validation failed for {artifact.path}: {e}")
            raise SyntaxValidationError(
                f"Syntax error in generated code: {e}",
                file_path=artifact.path,
                syntax_errors=[str(e)],
                language=str(artifact.language)
            )
    
    def _get_tokens_used(self) -> int:
        """Get total tokens used in this execution (placeholder).
        
        Returns:
            Total tokens used
        """
        # In a real implementation, this would track tokens from the current execution
        return 0
    
    def _get_safety_checks_performed(self, solution: CodeSolution) -> List[str]:
        """Get list of safety checks performed.
        
        Args:
            solution: Generated solution
            
        Returns:
            List of safety checks performed
        """
        checks = ["solution_safety_validation", "artifact_path_validation"]
        
        for artifact in solution.artifacts:
            checks.extend(artifact.safety_checks)
        
        return list(set(checks))  # Remove duplicates
    
    def _format_unified_prompt(self, inputs: Dict[str, Any]) -> str:
        """Format prompt for unified AI tool interface."""
        parts = [
            f"Task: {inputs.get('task_description', '')}",
            f"Type: {inputs.get('task_type', 'implementation')}",
        ]
        
        if inputs.get('requirements'):
            parts.append(f"Requirements: {inputs['requirements']}")
        
        if inputs.get('existing_files'):
            parts.append(f"Existing Files: {inputs['existing_files']}")
        
        if inputs.get('previous_feedback'):
            parts.append(f"Previous Feedback: {inputs['previous_feedback']}")
        
        parts.append(f"Language: {inputs.get('project_language', 'python')}")
        parts.append(f"Max Artifacts: {inputs.get('max_artifacts', 5)}")
        
        return "\n\n".join(parts)
    
    def _parse_ai_response(self, response: str, dev_context) -> CodeSolution:
        """Parse AI response into CodeSolution (simplified for now)."""
        # Create a basic solution from the response
        # This can be enhanced later with proper parsing
        artifact = CodeArtifact(
            type=ArtifactType.CODE,
            path="src/generated.py",
            content=response[:2000],  # Limit content
            language=ProgrammingLanguage.PYTHON,
            description="Generated from AI response",
            modification_type=ModificationType.CREATE,
            safety_checks=["basic_validation"],
            disaster_prevention_notes=["Generated via unified AI interface"]
        )
        
        return CodeSolution(
            solution_id=f"unified-{dev_context.task.get('id', 'unknown')}",
            description="Code generated via unified AI interface",
            requirements_addressed=[],
            primary_language=ProgrammingLanguage.PYTHON,
            artifacts=[artifact],
            test_strategy="Manual testing required",
            disaster_prevention_measures=["Unified AI tool interface"],
            rollback_plan="Remove generated files",
            estimated_complexity="medium"
        )
    
    def _get_files_read(self) -> List[str]:
        """Get list of files read from repository (placeholder).
        
        Returns:
            List of file paths read
        """
        # In a real implementation, this would track files read during execution
        return []
    
    def _get_addressed_feedback(self, dev_context: DeveloperContext) -> List[str]:
        """Get list of Navigator feedback that was addressed.
        
        Args:
            dev_context: Developer context
            
        Returns:
            List of addressed feedback items
        """
        if not dev_context.navigator_feedback:
            return []
        
        # Extract feedback items that were addressed
        addressed = []
        feedback = dev_context.navigator_feedback
        
        if "required_changes" in feedback:
            addressed.extend(feedback["required_changes"])
        
        if "issues" in feedback:
            for issue in feedback["issues"]:
                if isinstance(issue, dict):
                    addressed.append(issue.get("description", str(issue)))
                else:
                    addressed.append(str(issue))
        
        return addressed
    
    def _calculate_disaster_prevention_score(self, solution: CodeSolution) -> float:
        """Calculate disaster prevention score for the solution.
        
        Args:
            solution: Generated solution
            
        Returns:
            Disaster prevention score (0-100)
        """
        score = 0.0
        total_possible = 100.0
        
        # Check for safety measures
        if solution.disaster_prevention_measures:
            score += 30.0  # Has disaster prevention measures
        
        # Check artifact safety
        safe_artifacts = sum(1 for artifact in solution.artifacts if artifact.is_safe_to_create())
        if solution.artifacts:
            score += (safe_artifacts / len(solution.artifacts)) * 40.0
        
        # Check for rollback plan
        if solution.rollback_plan:
            score += 20.0
        
        # Check for quality checks
        if solution.quality_checks:
            score += 10.0
        
        return min(score, total_possible)
    
    def _create_error_response(self, error: Exception, task_id: str) -> Dict[str, Any]:
        """Create standardized error response.
        
        Args:
            error: Exception that occurred
            task_id: Task identifier
            
        Returns:
            Error response dictionary
        """
        error_details = {"error_type": type(error).__name__, "task_id": task_id}
        
        if hasattr(error, 'get_diagnostic_info'):
            error_details.update(error.get_diagnostic_info())
        
        return {
            "success": False,
            "error": str(error),
            "error_details": error_details,
            "artifacts": [],
            "summary": f"Implementation failed: {str(error)}",
            "disaster_prevention_score": 0.0
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Developer Agent performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        return {
            'total_implementations': self.total_implementations,
            'total_artifacts_created': self.total_artifacts_created,
            'total_files_read': self.total_files_read,
            'total_tokens_used': self.total_tokens_used,
            'disaster_prevention_triggers': self.disaster_prevention_triggers,
            'average_artifacts_per_implementation': (
                self.total_artifacts_created / max(self.total_implementations, 1)
            ),
            'average_tokens_per_implementation': (
                self.total_tokens_used / max(self.total_implementations, 1)
            ),
            'model': self.model,
            'temperature': self.temperature,
            'supported_languages': list(self.language_configs.keys()),
            'max_artifacts_per_solution': self.max_artifacts_per_solution
        }
    
    def __str__(self) -> str:
        """String representation of the Developer Agent."""
        return f"DeveloperAgent({self.model}, implementations={self.total_implementations})"
    
    async def execute_git_workflow(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute development task using Git-based workflow in workspace.
        
        This method works directly in the cloned repository with proper Git operations:
        1. Setup Git workspace (clone + feature branch)
        2. Read existing files for context
        3. Generate and write code directly to files
        4. Prepare for Git commit and review
        
        Args:
            task: Task definition
            context: Execution context including issue data
            
        Returns:
            Result with Git operations summary
        """
        start_time = datetime.now()
        task_id = task.get('id', 'unknown')
        issue_id = context.get("issue", {}).get("number", task_id)
        
        logger.info(f"Developer executing Git workflow for task: {task_id}")
        
        try:
            # 1. Setup Git workspace
            if self.github_service:
                workspace_success = self.github_service.setup_git_workspace(
                    issue_id=issue_id,
                    issue_data=context.get("issue")
                )
                if not workspace_success:
                    raise GitHubIntegrationError("Failed to setup Git workspace")
            
            # 2. Build development context
            dev_context = await self._prepare_developer_context(task, context)
            
            # 3. Read existing files from workspace
            existing_files = {}
            if self.github_service and self.github_service.get_current_workspace():
                for file_path in dev_context.existing_files:
                    content = self.github_service.read_file_from_workspace(file_path)
                    if content:
                        existing_files[file_path] = content
                        logger.debug(f"Read existing file: {file_path}")
            
            # 4. Generate code solution
            solution = await self._generate_code_solution(dev_context)
            
            # 5. Write files directly to workspace
            files_modified = []
            for artifact in solution.artifacts:
                if self.github_service:
                    success = self.github_service.write_file_to_workspace(
                        artifact.path,
                        artifact.content
                    )
                    if success:
                        files_modified.append(artifact.path)
                        logger.info(f"Modified file: {artifact.path}")
            
            # 6. Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 7. Return Git-aware result
            result = {
                "success": True,
                "git_workflow": True,
                "files_modified": files_modified,
                "workspace_path": str(self.github_service.get_current_workspace().repo_path) if self.github_service else None,
                "feature_branch": self.github_service.get_current_workspace().load_workflow_state().get("feature_branch") if self.github_service else None,
                "solution_summary": solution.summary,
                "execution_time": execution_time,
                "ready_for_commit": len(files_modified) > 0,
                "ready_for_review": True,
                "quality_notes": [
                    f"Modified {len(files_modified)} files in Git workspace",
                    "Changes ready for Git commit and Navigator review",
                    "Working in proper feature branch for safe development"
                ]
            }
            
            logger.info(f"Git workflow completed: {len(files_modified)} files modified in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Git workflow failed for task {task_id}: {e}")
            return {
                "success": False,
                "git_workflow": True,
                "error": str(e),
                "files_modified": [],
                "quality_notes": [f"Git workflow failed: {e}"]
            }


def create_developer_agent(**kwargs) -> DeveloperAgent:
    """Factory function to create a Developer Agent with proper configuration.
    
    Args:
        **kwargs: Configuration parameters for the agent
        
    Returns:
        Configured Developer Agent instance
    """
    return DeveloperAgent(**kwargs)