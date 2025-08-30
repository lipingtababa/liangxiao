"""Tester Agent specific exceptions and error handling utilities.

This module provides specialized exceptions and error handling functionality
for the Tester Agent, enabling better error reporting and debugging.
"""

from typing import Optional, Any, List, Dict
from core.exceptions import AgentExecutionError


class TesterError(AgentExecutionError):
    """Base exception for Tester Agent specific errors."""
    pass


class TestGenerationError(TesterError):
    """Raised when test generation fails."""
    
    def __init__(
        self,
        message: str,
        framework: Optional[str] = None,
        requirements: Optional[Dict[str, Any]] = None,
        llm_response: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.framework = framework
        self.requirements = requirements
        self.llm_response = llm_response
        
    def __str__(self) -> str:
        parts = [self.message]
        if self.framework:
            parts.append(f"Framework: {self.framework}")
        return " | ".join(parts)


class TestValidationError(TesterError):
    """Raised when generated test code fails validation."""
    
    def __init__(
        self,
        message: str,
        test_name: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.test_name = test_name
        self.validation_errors = validation_errors or []
        
    def get_detailed_message(self) -> str:
        """Get detailed error message with validation issues."""
        parts = [self.message]
        
        if self.test_name:
            parts.append(f"Test: {self.test_name}")
            
        if self.validation_errors:
            parts.append("Validation errors:")
            parts.extend(f"  - {error}" for error in self.validation_errors)
            
        return "\n".join(parts)


class FrameworkNotSupportedError(TesterError):
    """Raised when an unsupported testing framework is requested."""
    
    def __init__(
        self,
        framework: str,
        supported_frameworks: List[str],
        **kwargs
    ):
        message = (
            f"Framework '{framework}' is not supported. "
            f"Supported frameworks: {', '.join(supported_frameworks)}"
        )
        super().__init__(message, **kwargs)
        self.framework = framework
        self.supported_frameworks = supported_frameworks


class TestSuiteEmpty(TesterError):
    """Raised when no test cases could be generated."""
    
    def __init__(
        self,
        reason: Optional[str] = None,
        requirements_found: bool = False,
        implementation_found: bool = False,
        **kwargs
    ):
        message = "No test cases could be generated"
        if reason:
            message = f"{message}: {reason}"
            
        super().__init__(message, **kwargs)
        self.reason = reason
        self.requirements_found = requirements_found
        self.implementation_found = implementation_found
        
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for troubleshooting."""
        return {
            "reason": self.reason,
            "requirements_found": self.requirements_found,
            "implementation_found": self.implementation_found,
            "suggestions": self._get_suggestions()
        }
        
    def _get_suggestions(self) -> List[str]:
        """Get suggestions for resolving the issue."""
        suggestions = []
        
        if not self.requirements_found:
            suggestions.append(
                "Ensure requirements are available in context from Analyst or PM agents"
            )
            
        if not self.implementation_found:
            suggestions.append(
                "Ensure implementation code is available from Developer agent"
            )
            
        if not suggestions:
            suggestions.append(
                "Check LLM response and prompt formatting for issues"
            )
            
        return suggestions


class DisasterPreventionInsufficient(TesterError):
    """Raised when generated tests don't meet disaster prevention standards."""
    
    def __init__(
        self,
        score: float,
        min_score: float,
        missing_categories: Optional[List[str]] = None,
        **kwargs
    ):
        message = (
            f"Disaster prevention score {score:.1f} is below minimum {min_score:.1f}. "
            f"Generated tests may not prevent catastrophic failures."
        )
        super().__init__(message, **kwargs)
        self.score = score
        self.min_score = min_score
        self.missing_categories = missing_categories or []
        
    def get_improvement_suggestions(self) -> List[str]:
        """Get specific suggestions for improving disaster prevention."""
        suggestions = []
        
        if "file_integrity" in self.missing_categories:
            suggestions.append(
                "Add tests that verify file existence and content length"
            )
            
        if "content_preservation" in self.missing_categories:
            suggestions.append(
                "Add tests that verify important content is preserved"
            )
            
        if "edge_cases" in self.missing_categories:
            suggestions.append(
                "Add edge case tests for boundary conditions"
            )
            
        if "error_handling" in self.missing_categories:
            suggestions.append(
                "Add error handling tests for failure scenarios"
            )
            
        return suggestions


def validate_test_context(context: Dict[str, Any]) -> None:
    """
    Validate that context contains sufficient information for test generation.
    
    Args:
        context: Test generation context
        
    Raises:
        TestGenerationError: If context is insufficient
    """
    if not context:
        raise TestGenerationError("Empty context provided")
        
    # Check for requirements or implementation
    has_requirements = (
        "issue" in context or
        any(task.get("type") == "analysis" for task in context.get("completed_tasks", []))
    )
    
    has_implementation = (
        "code" in context or
        any(task.get("type") == "implementation" for task in context.get("completed_tasks", []))
    )
    
    if not has_requirements and not has_implementation:
        raise TestGenerationError(
            "Context must contain either requirements (from issue/analysis) or implementation code"
        )


def sanitize_test_name(name: str) -> str:
    """
    Sanitize test name to be a valid function identifier.
    
    Args:
        name: Original test name
        
    Returns:
        Sanitized function name
        
    Raises:
        TestValidationError: If name cannot be sanitized
    """
    if not name or not isinstance(name, str):
        raise TestValidationError("Test name must be a non-empty string")
        
    # Remove leading/trailing whitespace
    sanitized = name.strip()
    
    if not sanitized:
        raise TestValidationError("Test name cannot be empty after sanitization")
        
    # Replace invalid characters
    import re
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', sanitized.lower())
    
    # Ensure it starts with test_
    if not sanitized.startswith('test_'):
        sanitized = f"test_{sanitized}"
        
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove trailing underscores
    sanitized = sanitized.rstrip('_')
    
    # Ensure it's not just 'test_'
    if sanitized == 'test_':
        raise TestValidationError(f"Cannot create valid test name from '{name}'")
        
    return sanitized


def validate_test_code_syntax(code: str, framework: str) -> List[str]:
    """
    Perform basic validation of test code syntax.
    
    Args:
        code: Test code to validate
        framework: Testing framework
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not code or not isinstance(code, str):
        errors.append("Test code cannot be empty")
        return errors
        
    code = code.strip()
    
    # Framework-specific validation
    if framework.lower() == "pytest":
        if "assert" not in code and "pytest." not in code:
            errors.append("Pytest test should contain assertions")
            
        # Check for basic Python syntax issues
        try:
            compile(code, '<test>', 'exec')
        except SyntaxError as e:
            errors.append(f"Python syntax error: {e}")
            
    elif framework.lower() == "jest":
        if "expect(" not in code and "test(" not in code:
            errors.append("Jest test should contain expectations")
            
        # Basic checks for JavaScript syntax
        if code.count('(') != code.count(')'):
            errors.append("Mismatched parentheses")
            
        if code.count('{') != code.count('}'):
            errors.append("Mismatched braces")
            
    elif framework.lower() == "unittest":
        if "self.assert" not in code:
            errors.append("unittest test should contain assertions")
            
        try:
            compile(code, '<test>', 'exec')
        except SyntaxError as e:
            errors.append(f"Python syntax error: {e}")
            
    return errors


def assess_disaster_prevention_coverage(test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Assess how well test cases cover disaster prevention scenarios.
    
    Args:
        test_cases: List of test case data
        
    Returns:
        Assessment results with score and recommendations
    """
    score = 0.0
    coverage_areas = {
        'file_integrity': False,
        'content_preservation': False,
        'edge_cases': False,
        'error_handling': False,
        'boundary_testing': False
    }
    
    for test in test_cases:
        test_code = test.get('test_code', '').lower()
        test_desc = test.get('description', '').lower()
        category = test.get('category', '')
        
        # File integrity checks
        if ('len(' in test_code or 'size' in test_code or 'exists' in test_code):
            coverage_areas['file_integrity'] = True
            score += 20.0
            
        # Content preservation
        if ('preserve' in test_desc or 'content' in test_desc):
            coverage_areas['content_preservation'] = True
            score += 15.0
            
        # Edge cases
        if category == 'edge_case':
            coverage_areas['edge_cases'] = True
            score += 15.0
            
        # Error handling
        if category == 'error_handling' or 'raises' in test_code or 'except' in test_code:
            coverage_areas['error_handling'] = True
            score += 20.0
            
        # Boundary testing
        if ('empty' in test_code or 'null' in test_code or 'zero' in test_code):
            coverage_areas['boundary_testing'] = True
            score += 10.0
    
    # Cap the score at 100
    score = min(100.0, score)
    
    missing_areas = [area for area, covered in coverage_areas.items() if not covered]
    
    return {
        'score': score,
        'coverage_areas': coverage_areas,
        'missing_areas': missing_areas,
        'recommendations': _get_disaster_prevention_recommendations(missing_areas)
    }


def _get_disaster_prevention_recommendations(missing_areas: List[str]) -> List[str]:
    """Get recommendations for improving disaster prevention coverage."""
    recommendations = []
    
    area_recommendations = {
        'file_integrity': "Add tests that verify files exist and have expected size/content",
        'content_preservation': "Add tests that verify important content is preserved during operations",
        'edge_cases': "Add tests for boundary conditions (empty inputs, large data, etc.)",
        'error_handling': "Add tests that verify proper error handling and recovery",
        'boundary_testing': "Add tests for edge values (null, empty, zero, max values)"
    }
    
    for area in missing_areas:
        if area in area_recommendations:
            recommendations.append(area_recommendations[area])
    
    return recommendations