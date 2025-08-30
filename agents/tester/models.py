"""Pydantic models for the Tester Agent.

This module defines the data structures used by the Tester Agent
for representing test cases, test suites, and related metadata.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal, Set
from pydantic import BaseModel, Field, field_validator, model_validator
import re


class TestCase(BaseModel):
    """Individual test case with comprehensive validation."""
    
    name: str = Field(
        ...,
        description="Descriptive test name (will be converted to valid function name)",
        min_length=3,
        max_length=200
    )
    description: str = Field(
        ...,
        description="What this test validates",
        min_length=10,
        max_length=1000
    )
    category: Literal["unit", "integration", "edge_case", "error_handling", "performance"] = Field(
        ...,
        description="Test category for organization and prioritization"
    )
    priority: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="Test priority level"
    )
    test_code: str = Field(
        ...,
        description="Complete test implementation code",
        min_length=20
    )
    expected_outcome: str = Field(
        ...,
        description="What should happen when test runs",
        min_length=5,
        max_length=500
    )
    requirements_coverage: List[str] = Field(
        default_factory=list,
        description="Which requirements this test validates"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Additional tags for test organization"
    )
    timeout: Optional[float] = Field(
        None,
        description="Test timeout in seconds",
        ge=0.1,
        le=300.0
    )
    skip_reason: Optional[str] = Field(
        None,
        description="Reason for skipping test (if applicable)"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate test name is suitable for function naming."""
        if not v or not isinstance(v, str):
            raise ValueError("Test name must be a non-empty string")
        
        # Check for basic validity
        if len(v.strip()) < 3:
            raise ValueError("Test name must be at least 3 characters after stripping")
        
        return v.strip()
    
    @field_validator('test_code')
    @classmethod
    def validate_test_code(cls, v):
        """Validate test code has basic structure."""
        if not v or not isinstance(v, str):
            raise ValueError("Test code must be a non-empty string")
        
        # Check for basic test indicators
        test_indicators = ['assert', 'assertEqual', 'expect', 'should', 'toBe', 'toEqual']
        if not any(indicator in v for indicator in test_indicators):
            raise ValueError("Test code should contain assertions or expectations")
        
        return v.strip()
    
    @field_validator('requirements_coverage')
    @classmethod
    def validate_requirements_coverage(cls, v):
        """Validate requirements coverage list."""
        if not isinstance(v, list):
            return []
        
        # Remove empty strings and duplicates
        cleaned = list(set(req.strip() for req in v if req and req.strip()))
        return cleaned
    
    def get_function_name(self) -> str:
        """Convert test name to valid Python function name."""
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', self.name.lower())
        
        # Ensure it starts with test_
        if not sanitized.startswith('test_'):
            sanitized = f"test_{sanitized}"
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove trailing underscores
        sanitized = sanitized.rstrip('_')
        
        return sanitized
    
    def is_critical(self) -> bool:
        """Check if this is a critical test."""
        return self.priority == "critical"
    
    def model_dump_summary(self) -> Dict[str, Any]:
        """Get a summary representation of the test case."""
        return {
            "name": self.name,
            "category": self.category,
            "priority": self.priority,
            "requirements_covered": len(self.requirements_coverage),
            "has_timeout": self.timeout is not None,
            "function_name": self.get_function_name()
        }


class CoverageAnalysis(BaseModel):
    """Test coverage analysis data."""
    
    statement_coverage: float = Field(
        0.0,
        description="Statement coverage percentage",
        ge=0.0,
        le=100.0
    )
    branch_coverage: float = Field(
        0.0,
        description="Branch coverage percentage",
        ge=0.0,
        le=100.0
    )
    function_coverage: float = Field(
        0.0,
        description="Function coverage percentage",
        ge=0.0,
        le=100.0
    )
    line_coverage: float = Field(
        0.0,
        description="Line coverage percentage",
        ge=0.0,
        le=100.0
    )
    requirements_coverage: float = Field(
        0.0,
        description="Requirements coverage percentage",
        ge=0.0,
        le=100.0
    )
    uncovered_lines: List[int] = Field(
        default_factory=list,
        description="Line numbers not covered by tests"
    )
    coverage_gaps: List[str] = Field(
        default_factory=list,
        description="Areas lacking test coverage"
    )
    
    def get_overall_coverage(self) -> float:
        """Calculate overall coverage score."""
        # Weighted average of different coverage metrics
        weights = {
            'statement': 0.3,
            'branch': 0.25,
            'function': 0.2,
            'line': 0.15,
            'requirements': 0.1
        }
        
        overall = (
            self.statement_coverage * weights['statement'] +
            self.branch_coverage * weights['branch'] +
            self.function_coverage * weights['function'] +
            self.line_coverage * weights['line'] +
            self.requirements_coverage * weights['requirements']
        )
        
        return round(overall, 2)
    
    def is_acceptable_coverage(self, threshold: float = 80.0) -> bool:
        """Check if coverage meets acceptable threshold."""
        return self.get_overall_coverage() >= threshold


class TestSuite(BaseModel):
    """Complete test suite with validation and analysis."""
    
    test_cases: List[TestCase] = Field(
        ...,
        description="List of test cases in the suite",
        min_items=1
    )
    framework: str = Field(
        ...,
        description="Testing framework used (e.g., pytest, jest)",
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]*$"
    )
    setup_code: Optional[str] = Field(
        None,
        description="Test setup/initialization code"
    )
    teardown_code: Optional[str] = Field(
        None,
        description="Test cleanup code"
    )
    coverage_analysis: Optional[CoverageAnalysis] = Field(
        None,
        description="Test coverage analysis"
    )
    total_tests: int = Field(
        ...,
        description="Total number of tests",
        ge=1
    )
    estimated_runtime: Optional[float] = Field(
        None,
        description="Estimated test suite runtime in seconds",
        ge=0.0
    )
    requirements_tested: Set[str] = Field(
        default_factory=set,
        description="Set of requirements covered by tests"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the test suite was created"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    @field_validator('total_tests')
    @classmethod
    def validate_total_tests(cls, v, info):
        """Ensure total_tests matches actual test count."""
        if info.data and 'test_cases' in info.data:
            test_cases = info.data['test_cases']
            actual_count = len(test_cases)
            
            if v != actual_count:
                # Auto-correct the total
                return actual_count
        
        return v
    
    @model_validator(mode='after')
    def validate_test_suite_consistency(self):
        """Validate overall test suite consistency."""
        if not self.test_cases:
            raise ValueError("Test suite must have at least one test case")
        
        # Check for duplicate test names
        test_names = [test.name for test in self.test_cases]
        if len(test_names) != len(set(test_names)):
            raise ValueError("Test suite contains duplicate test names")
        
        # Check for duplicate function names
        function_names = [test.get_function_name() for test in self.test_cases]
        if len(function_names) != len(set(function_names)):
            raise ValueError("Test suite would generate duplicate function names")
        
        # Validate framework compatibility
        if self.framework:
            valid_frameworks = ['pytest', 'jest', 'junit', 'mocha', 'jasmine', 'unittest']
            if self.framework.lower() not in [fw.lower() for fw in valid_frameworks]:
                # Warning but not error - allow custom frameworks
                pass
        
        # Collect requirements coverage
        all_requirements = set()
        for test in self.test_cases:
            all_requirements.update(test.requirements_coverage)
        self.requirements_tested = all_requirements
        
        return self
    
    def get_test_counts_by_category(self) -> Dict[str, int]:
        """Get count of tests by category."""
        counts = {}
        for test in self.test_cases:
            counts[test.category] = counts.get(test.category, 0) + 1
        return counts
    
    def get_test_counts_by_priority(self) -> Dict[str, int]:
        """Get count of tests by priority."""
        counts = {}
        for test in self.test_cases:
            counts[test.priority] = counts.get(test.priority, 0) + 1
        return counts
    
    def get_critical_tests(self) -> List[TestCase]:
        """Get all critical priority tests."""
        return [test for test in self.test_cases if test.is_critical()]
    
    def estimate_total_runtime(self) -> float:
        """Estimate total test suite runtime."""
        if self.estimated_runtime is not None:
            return self.estimated_runtime
        
        # Basic estimation based on test count and type
        base_time = 0.5  # Base time per test in seconds
        category_multipliers = {
            'unit': 1.0,
            'integration': 2.0,
            'edge_case': 1.5,
            'error_handling': 1.2,
            'performance': 3.0
        }
        
        total_time = 0.0
        for test in self.test_cases:
            multiplier = category_multipliers.get(test.category, 1.0)
            test_time = base_time * multiplier
            
            # Add timeout if specified
            if test.timeout:
                test_time = min(test_time, test.timeout)
            
            total_time += test_time
        
        return round(total_time, 2)
    
    def validate_requirements_coverage(self, required_requirements: List[str]) -> List[str]:
        """Validate that required requirements are covered by tests.
        
        Args:
            required_requirements: List of requirements that must be tested
            
        Returns:
            List of requirements not covered by any test
        """
        missing_requirements = []
        
        for req in required_requirements:
            covered = any(
                req in test.requirements_coverage
                for test in self.test_cases
            )
            if not covered:
                missing_requirements.append(req)
        
        return missing_requirements
    
    def get_disaster_prevention_score(self) -> float:
        """Calculate how well this suite prevents disasters like PR #23.
        
        Returns:
            Score from 0-100 indicating disaster prevention capability
        """
        score = 0.0
        
        # Check for file integrity tests
        has_file_integrity = any(
            'file' in test.test_code.lower() and 
            ('length' in test.test_code.lower() or 'size' in test.test_code.lower())
            for test in self.test_cases
        )
        if has_file_integrity:
            score += 25.0
        
        # Check for content preservation tests
        has_content_preservation = any(
            'preserve' in test.description.lower() or
            'content' in test.description.lower()
            for test in self.test_cases
        )
        if has_content_preservation:
            score += 20.0
        
        # Check for edge case coverage
        edge_case_count = len([t for t in self.test_cases if t.category == 'edge_case'])
        if edge_case_count > 0:
            score += min(20.0, edge_case_count * 5)
        
        # Check for error handling tests
        error_handling_count = len([t for t in self.test_cases if t.category == 'error_handling'])
        if error_handling_count > 0:
            score += min(15.0, error_handling_count * 3)
        
        # Check for critical tests
        critical_count = len([t for t in self.test_cases if t.priority == 'critical'])
        if critical_count > 0:
            score += min(20.0, critical_count * 2)
        
        return min(100.0, score)
    
    def model_dump_summary(self) -> Dict[str, Any]:
        """Get a summary representation of the test suite."""
        return {
            "total_tests": self.total_tests,
            "framework": self.framework,
            "categories": self.get_test_counts_by_category(),
            "priorities": self.get_test_counts_by_priority(),
            "requirements_tested": len(self.requirements_tested),
            "estimated_runtime": self.estimate_total_runtime(),
            "disaster_prevention_score": self.get_disaster_prevention_score(),
            "coverage": self.coverage_analysis.model_dump() if self.coverage_analysis else None,
            "created_at": self.created_at.isoformat()
        }


class TestExecutionResult(BaseModel):
    """Results from executing a test suite."""
    
    suite_id: str = Field(..., description="Identifier for the test suite")
    total_tests: int = Field(..., description="Total number of tests executed")
    passed: int = Field(..., description="Number of tests that passed")
    failed: int = Field(..., description="Number of tests that failed")
    skipped: int = Field(..., description="Number of tests that were skipped")
    errors: int = Field(..., description="Number of tests that had errors")
    
    execution_time: float = Field(..., description="Total execution time in seconds")
    framework: str = Field(..., description="Testing framework used")
    
    test_results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Individual test results"
    )
    coverage_report: Optional[Dict[str, Any]] = Field(
        None,
        description="Coverage analysis results"
    )
    
    executed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the tests were executed"
    )
    
    def get_success_rate(self) -> float:
        """Calculate test success rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100.0
    
    def is_successful(self) -> bool:
        """Check if test execution was successful (all tests passed)."""
        return self.failed == 0 and self.errors == 0 and self.passed > 0
    
    def get_failure_summary(self) -> Dict[str, Any]:
        """Get summary of failures and errors."""
        failed_tests = [
            result for result in self.test_results
            if result.get('status') in ['failed', 'error']
        ]
        
        return {
            'total_failures': self.failed + self.errors,
            'failed_tests': failed_tests,
            'common_issues': self._analyze_common_issues(failed_tests)
        }
    
    def _analyze_common_issues(self, failed_tests: List[Dict[str, Any]]) -> List[str]:
        """Analyze common patterns in test failures."""
        # This is a simplified implementation - could be much more sophisticated
        issues = []
        error_messages = [test.get('error', '') for test in failed_tests]
        
        # Check for common error patterns
        if any('AssertionError' in msg for msg in error_messages):
            issues.append("Assertion failures - check test expectations")
        
        if any('ImportError' in msg for msg in error_messages):
            issues.append("Import errors - check dependencies")
        
        if any('timeout' in msg.lower() for msg in error_messages):
            issues.append("Timeout issues - tests running too long")
        
        return issues