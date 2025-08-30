"""Pydantic models for Analyst Agent.

This module defines the data structures used by the Analyst Agent to perform
requirements analysis, codebase analysis, and create technical specifications.
These models ensure structured output and type safety.
"""

from datetime import datetime
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class RequirementSpec(BaseModel):
    """Individual requirement specification.
    
    Represents a single, clear requirement that must be fulfilled.
    Each requirement should be specific, measurable, and testable.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    id: str = Field(
        description="Unique requirement ID",
        min_length=1,
        pattern=r"^req-\d+$"
    )
    
    description: str = Field(
        description="Clear requirement description",
        min_length=10,
        max_length=500
    )
    
    priority: Literal["critical", "high", "medium", "low"] = Field(
        description="Priority level of this requirement"
    )
    
    acceptance_criteria: List[str] = Field(
        min_length=1,
        description="How to verify completion - specific, measurable criteria"
    )
    
    dependencies: List[str] = Field(
        default_factory=list,
        description="What this requirement depends on"
    )
    
    category: Literal[
        "functional", "non_functional", "technical", "business", "quality"
    ] = Field(
        default="functional",
        description="Category of requirement"
    )
    
    source: str = Field(
        default="issue_analysis",
        description="Source of this requirement (issue, existing code, etc.)"
    )
    
    def __str__(self) -> str:
        return f"Requirement {self.id}: {self.description[:50]}..."


class CodebaseAnalysis(BaseModel):
    """Analysis of existing codebase.
    
    Contains detailed information about the current state of the codebase
    relevant to the issue being analyzed. This prevents disasters like PR #23
    by ensuring agents understand what exists before making changes.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    relevant_files: List[str] = Field(
        description="Files that need to be read/modified for this issue"
    )
    
    current_behavior: str = Field(
        description="How the system currently works in the relevant area",
        min_length=20,
        max_length=2000
    )
    
    architecture_notes: str = Field(
        description="Relevant architectural patterns and design decisions",
        min_length=10,
        max_length=1500
    )
    
    dependencies: List[str] = Field(
        default_factory=list,
        description="External dependencies, libraries, or services identified"
    )
    
    potential_impacts: List[str] = Field(
        description="What might be affected by changes - files, features, integrations"
    )
    
    existing_tests: List[str] = Field(
        default_factory=list,
        description="Existing test files that cover the relevant functionality"
    )
    
    technical_debt: List[str] = Field(
        default_factory=list,
        description="Technical debt or issues found in the relevant code"
    )
    
    configuration_files: List[str] = Field(
        default_factory=list,
        description="Configuration files that might need updates"
    )
    
    documentation_files: List[str] = Field(
        default_factory=list,
        description="Documentation files that might need updates"
    )
    
    data_models: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Data models or schemas relevant to the changes"
    )
    
    api_endpoints: List[Dict[str, str]] = Field(
        default_factory=list,
        description="API endpoints that might be affected"
    )
    
    def __str__(self) -> str:
        return f"Codebase Analysis: {len(self.relevant_files)} files analyzed"


class TechnicalSpecification(BaseModel):
    """Complete technical specification for implementing an issue.
    
    This is the comprehensive output of the Analyst Agent that provides
    everything a developer needs to implement the requirements correctly.
    It includes requirements, codebase analysis, and implementation guidance.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    # Core Analysis Components
    requirements: List[RequirementSpec] = Field(
        min_length=1,
        description="All requirements that must be fulfilled"
    )
    
    codebase_analysis: CodebaseAnalysis = Field(
        description="Analysis of existing codebase"
    )
    
    # Implementation Guidance
    implementation_approach: str = Field(
        description="Recommended approach for implementation",
        min_length=50,
        max_length=2000
    )
    
    step_by_step_plan: List[str] = Field(
        min_length=3,
        description="Detailed step-by-step implementation plan"
    )
    
    # Quality Assurance
    testing_strategy: str = Field(
        description="How to test the changes - unit, integration, e2e",
        min_length=20,
        max_length=1000
    )
    
    risk_assessment: List[str] = Field(
        description="Potential risks and their mitigations"
    )
    
    success_criteria: List[str] = Field(
        min_length=1,
        description="How to measure success - specific, testable criteria"
    )
    
    # Quality Gates and Validation
    validation_checklist: List[str] = Field(
        min_length=3,
        description="Checklist to validate implementation before PR"
    )
    
    rollback_plan: str = Field(
        description="Plan for rolling back changes if issues arise",
        min_length=20,
        max_length=500
    )
    
    # Additional Context
    assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions made during analysis"
    )
    
    open_questions: List[str] = Field(
        default_factory=list,
        description="Questions that need clarification"
    )
    
    alternative_approaches: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Alternative implementation approaches considered"
    )
    
    # Learning from Past Issues
    lessons_learned: List[str] = Field(
        default_factory=list,
        description="Lessons from similar past issues (like PR #23)"
    )
    
    similar_patterns: List[str] = Field(
        default_factory=list,
        description="Similar patterns in the codebase to learn from"
    )
    
    # Metadata
    issue_number: Optional[int] = Field(
        default=None,
        description="GitHub issue number this spec addresses"
    )
    
    repository: str = Field(
        description="Repository this specification is for"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this specification was created"
    )
    
    analyst_version: str = Field(
        default="1.0",
        description="Version of Analyst Agent that created this spec"
    )
    
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        default=0.8,
        description="Confidence in the specification accuracy (0.0 to 1.0)"
    )
    
    def validate_completeness(self) -> List[str]:
        """Validate that the specification is complete and actionable.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check requirements have acceptance criteria
        for req in self.requirements:
            if not req.acceptance_criteria:
                errors.append(f"Requirement {req.id} missing acceptance criteria")
        
        # Check codebase analysis has essential information
        if not self.codebase_analysis.relevant_files:
            errors.append("No relevant files identified in codebase analysis")
        
        if not self.codebase_analysis.current_behavior.strip():
            errors.append("Current behavior not documented")
        
        # Check implementation guidance is actionable
        if len(self.step_by_step_plan) < 3:
            errors.append("Implementation plan needs at least 3 steps")
        
        if not self.testing_strategy.strip():
            errors.append("Testing strategy is required")
        
        # Check quality measures
        if not self.success_criteria:
            errors.append("Success criteria are required")
        
        if len(self.validation_checklist) < 3:
            errors.append("Validation checklist needs at least 3 items")
        
        return errors
    
    def get_critical_requirements(self) -> List[RequirementSpec]:
        """Get all critical priority requirements.
        
        Returns:
            List of critical requirements
        """
        return [req for req in self.requirements if req.priority == "critical"]
    
    def get_files_to_modify(self) -> List[str]:
        """Get list of files that will need modification.
        
        Returns:
            List of file paths that need changes
        """
        return self.codebase_analysis.relevant_files
    
    def get_files_to_test(self) -> List[str]:
        """Get list of test files that need attention.
        
        Returns:
            List of test file paths
        """
        test_files = []
        test_files.extend(self.codebase_analysis.existing_tests)
        
        # Infer additional test files based on implementation files
        for file_path in self.codebase_analysis.relevant_files:
            if file_path.endswith('.py'):
                # Convert implementation file to test file name
                if '/src/' in file_path:
                    test_path = file_path.replace('/src/', '/tests/test_')
                elif file_path.startswith('src/'):
                    test_path = 'tests/test_' + file_path[4:]
                else:
                    # Default pattern
                    test_path = 'tests/test_' + file_path.replace('/', '_')
                test_files.append(test_path)
        
        return list(set(test_files))  # Remove duplicates
    
    def __str__(self) -> str:
        return (
            f"TechnicalSpecification: {len(self.requirements)} requirements, "
            f"{len(self.codebase_analysis.relevant_files)} files, "
            f"confidence {self.confidence_score:.2f}"
        )