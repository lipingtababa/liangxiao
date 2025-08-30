"""Models for the Test Validation System.

This module defines the data structures used by the Test Validation System
for representing test validation results, execution status, and metrics.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class ValidationIssueType(str, Enum):
    """Types of validation issues."""
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    EXECUTION_ERROR = "execution_error"
    ASSERTION_MISSING = "assertion_missing"
    DISASTER_PREVENTION = "disaster_prevention"
    COVERAGE_GAP = "coverage_gap"
    PERFORMANCE_ISSUE = "performance_issue"
    QUALITY_ISSUE = "quality_issue"


class ValidationIssue(BaseModel):
    """Individual validation issue."""
    
    type: ValidationIssueType = Field(description="Type of validation issue")
    severity: str = Field(description="Severity level: critical, major, minor")
    message: str = Field(description="Human-readable issue description")
    location: Optional[str] = Field(None, description="Location where issue was found")
    suggestion: Optional[str] = Field(None, description="Suggested fix for the issue")
    test_name: Optional[str] = Field(None, description="Name of test with the issue")
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        """Validate severity level."""
        valid_severities = {'critical', 'major', 'minor'}
        if v.lower() not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return v.lower()


class TestResult(BaseModel):
    """Result of individual test execution."""
    
    test_id: str = Field(description="Unique identifier for the test")
    test_name: str = Field(description="Human-readable test name")
    status: TestStatus = Field(description="Test execution status")
    execution_time: float = Field(description="Time taken to execute test in seconds")
    
    # Output and error information
    output: str = Field(default="", description="Test output/stdout")
    error_message: Optional[str] = Field(None, description="Error message if test failed")
    traceback: Optional[str] = Field(None, description="Full traceback if available")
    
    # Test quality metrics
    assertions_count: int = Field(default=0, description="Number of assertions in test")
    coverage_percentage: Optional[float] = Field(None, description="Code coverage for this test")
    
    # Metadata
    framework: Optional[str] = Field(None, description="Testing framework used")
    category: Optional[str] = Field(None, description="Test category (unit, integration, etc.)")
    priority: Optional[str] = Field(None, description="Test priority level")
    
    @field_validator('execution_time')
    @classmethod
    def validate_execution_time(cls, v):
        """Validate execution time is non-negative."""
        if v < 0:
            raise ValueError("Execution time cannot be negative")
        return v


class TestValidationResult(BaseModel):
    """Complete validation result for a test suite."""
    
    # Overall status
    overall_success: bool = Field(description="Whether validation passed overall")
    validation_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When validation was performed"
    )
    
    # Test execution summary
    total_tests: int = Field(description="Total number of tests validated")
    passed_tests: int = Field(description="Number of tests that passed")
    failed_tests: int = Field(description="Number of tests that failed")
    error_tests: int = Field(description="Number of tests with errors")
    skipped_tests: int = Field(description="Number of tests that were skipped")
    
    # Performance metrics
    total_execution_time: float = Field(description="Total time to validate all tests")
    average_test_time: float = Field(description="Average time per test")
    
    # Coverage analysis
    overall_coverage_percentage: float = Field(
        default=0.0,
        description="Overall code coverage percentage"
    )
    statement_coverage: Optional[float] = Field(None, description="Statement coverage")
    branch_coverage: Optional[float] = Field(None, description="Branch coverage")
    function_coverage: Optional[float] = Field(None, description="Function coverage")
    
    # Detailed results
    test_results: List[TestResult] = Field(
        default_factory=list,
        description="Individual test results"
    )
    validation_issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="Issues found during validation"
    )
    
    # Recommendations and insights
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )
    quality_score: float = Field(
        default=0.0,
        description="Overall test quality score (0-100)"
    )
    disaster_prevention_score: float = Field(
        default=0.0,
        description="Disaster prevention effectiveness score (0-100)"
    )
    
    # Framework and environment info
    framework_detected: Optional[str] = Field(None, description="Detected testing framework")
    python_version: Optional[str] = Field(None, description="Python version used")
    dependencies_validated: bool = Field(
        default=False,
        description="Whether dependencies were validated"
    )
    
    @field_validator('quality_score', 'disaster_prevention_score', 'overall_coverage_percentage')
    @classmethod
    def validate_percentage(cls, v):
        """Validate percentage values are between 0 and 100."""
        if not (0 <= v <= 100):
            raise ValueError("Percentage values must be between 0 and 100")
        return v
    
    def get_success_rate(self) -> float:
        """Calculate test success rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100.0
    
    def get_critical_issues(self) -> List[ValidationIssue]:
        """Get all critical validation issues."""
        return [issue for issue in self.validation_issues if issue.severity == "critical"]
    
    def has_critical_issues(self) -> bool:
        """Check if there are any critical validation issues."""
        return len(self.get_critical_issues()) > 0
    
    def get_issues_by_type(self, issue_type: ValidationIssueType) -> List[ValidationIssue]:
        """Get validation issues of a specific type."""
        return [issue for issue in self.validation_issues if issue.type == issue_type]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.test_results:
            return {
                "total_time": self.total_execution_time,
                "average_time": 0.0,
                "slowest_test": None,
                "fastest_test": None
            }
        
        times = [result.execution_time for result in self.test_results]
        slowest = max(self.test_results, key=lambda x: x.execution_time)
        fastest = min(self.test_results, key=lambda x: x.execution_time)
        
        return {
            "total_time": self.total_execution_time,
            "average_time": self.average_test_time,
            "slowest_test": {
                "name": slowest.test_name,
                "time": slowest.execution_time
            },
            "fastest_test": {
                "name": fastest.test_name,
                "time": fastest.execution_time
            }
        }
    
    def get_disaster_prevention_analysis(self) -> Dict[str, Any]:
        """Analyze disaster prevention capabilities."""
        pr23_issues = self.get_issues_by_type(ValidationIssueType.DISASTER_PREVENTION)
        
        # Analyze test patterns for disaster prevention
        file_integrity_tests = sum(
            1 for result in self.test_results
            if "file" in result.test_name.lower() and 
               ("integrity" in result.test_name.lower() or "exists" in result.test_name.lower())
        )
        
        content_preservation_tests = sum(
            1 for result in self.test_results
            if any(keyword in result.test_name.lower() 
                  for keyword in ["preserve", "content", "unchanged", "targeted"])
        )
        
        edge_case_tests = sum(
            1 for result in self.test_results
            if result.category == "edge_case"
        )
        
        return {
            "score": self.disaster_prevention_score,
            "pr23_protection_issues": len(pr23_issues),
            "file_integrity_tests": file_integrity_tests,
            "content_preservation_tests": content_preservation_tests,
            "edge_case_tests": edge_case_tests,
            "recommendations": [
                rec for rec in self.recommendations
                if "disaster" in rec.lower() or "pr #23" in rec.lower()
            ]
        }
    
    def model_dump_summary(self) -> Dict[str, Any]:
        """Get a concise summary of validation results."""
        return {
            "success": self.overall_success,
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "errors": self.error_tests,
            "success_rate": self.get_success_rate(),
            "quality_score": self.quality_score,
            "disaster_prevention_score": self.disaster_prevention_score,
            "coverage": self.overall_coverage_percentage,
            "critical_issues": len(self.get_critical_issues()),
            "total_issues": len(self.validation_issues),
            "execution_time": self.total_execution_time,
            "framework": self.framework_detected
        }


class TestEnvironment(BaseModel):
    """Test execution environment configuration."""
    
    temp_directory: str = Field(description="Temporary directory for test execution")
    framework: str = Field(description="Testing framework to use")
    python_executable: str = Field(default="python", description="Python executable path")
    timeout_seconds: int = Field(default=300, description="Global timeout for test execution")
    
    # Framework-specific configurations
    pytest_config: Optional[Dict[str, Any]] = Field(None, description="Pytest configuration")
    jest_config: Optional[Dict[str, Any]] = Field(None, description="Jest configuration")
    coverage_config: Optional[Dict[str, Any]] = Field(None, description="Coverage configuration")
    
    # Dependencies
    required_packages: List[str] = Field(
        default_factory=list,
        description="Required packages for test execution"
    )
    install_command: Optional[str] = Field(None, description="Custom package install command")
    
    # Environment variables
    environment_variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables for test execution"
    )
    
    def get_pytest_args(self) -> List[str]:
        """Get pytest command line arguments."""
        base_args = [
            "--verbose",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results.json"
        ]
        
        # Add coverage if configured
        if self.coverage_config:
            base_args.extend([
                "--cov=src",
                "--cov-report=json",
                "--cov-report=term"
            ])
        
        # Add custom config if provided
        if self.pytest_config:
            for key, value in self.pytest_config.items():
                if isinstance(value, bool) and value:
                    base_args.append(f"--{key}")
                elif value is not None:
                    base_args.extend([f"--{key}", str(value)])
        
        return base_args
    
    def get_jest_config(self) -> Dict[str, Any]:
        """Get Jest configuration object."""
        base_config = {
            "testEnvironment": "node",
            "verbose": True,
            "collectCoverage": True,
            "coverageReporters": ["json", "text"],
            "testTimeout": min(self.timeout_seconds * 1000, 30000),  # Convert to ms
            "reporters": [
                "default",
                ["jest-json-reporter", {"outputFile": "test_results.json"}]
            ]
        }
        
        if self.jest_config:
            base_config.update(self.jest_config)
        
        return base_config


class ValidationMetrics(BaseModel):
    """Metrics for tracking validation system performance."""
    
    total_validations: int = Field(default=0, description="Total validations performed")
    successful_validations: int = Field(default=0, description="Successful validations")
    failed_validations: int = Field(default=0, description="Failed validations")
    
    # Performance metrics
    total_validation_time: float = Field(default=0.0, description="Total time spent validating")
    average_validation_time: float = Field(default=0.0, description="Average validation time")
    
    # Quality metrics
    average_quality_score: float = Field(default=0.0, description="Average quality score")
    average_disaster_prevention_score: float = Field(
        default=0.0,
        description="Average disaster prevention score"
    )
    
    # Issue tracking
    total_issues_found: int = Field(default=0, description="Total validation issues found")
    critical_issues_found: int = Field(default=0, description="Critical issues found")
    
    # Framework usage
    framework_usage: Dict[str, int] = Field(
        default_factory=dict,
        description="Usage count by framework"
    )
    
    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last time metrics were updated"
    )
    
    def update_with_result(self, result: TestValidationResult) -> None:
        """Update metrics with a new validation result."""
        self.total_validations += 1
        
        if result.overall_success:
            self.successful_validations += 1
        else:
            self.failed_validations += 1
        
        # Update performance metrics
        self.total_validation_time += result.total_execution_time
        self.average_validation_time = self.total_validation_time / self.total_validations
        
        # Update quality metrics
        total_quality = (self.average_quality_score * (self.total_validations - 1) + 
                        result.quality_score)
        self.average_quality_score = total_quality / self.total_validations
        
        total_disaster = (self.average_disaster_prevention_score * (self.total_validations - 1) + 
                         result.disaster_prevention_score)
        self.average_disaster_prevention_score = total_disaster / self.total_validations
        
        # Update issue tracking
        self.total_issues_found += len(result.validation_issues)
        self.critical_issues_found += len(result.get_critical_issues())
        
        # Update framework usage
        if result.framework_detected:
            framework = result.framework_detected
            self.framework_usage[framework] = self.framework_usage.get(framework, 0) + 1
        
        self.last_updated = datetime.utcnow()
    
    def get_success_rate(self) -> float:
        """Get validation success rate as percentage."""
        if self.total_validations == 0:
            return 0.0
        return (self.successful_validations / self.total_validations) * 100.0
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            "validations": {
                "total": self.total_validations,
                "successful": self.successful_validations,
                "failed": self.failed_validations,
                "success_rate": self.get_success_rate()
            },
            "performance": {
                "total_time": self.total_validation_time,
                "average_time": self.average_validation_time
            },
            "quality": {
                "average_quality_score": self.average_quality_score,
                "average_disaster_prevention_score": self.average_disaster_prevention_score
            },
            "issues": {
                "total": self.total_issues_found,
                "critical": self.critical_issues_found,
                "average_per_validation": (
                    self.total_issues_found / max(self.total_validations, 1)
                )
            },
            "frameworks": self.framework_usage,
            "last_updated": self.last_updated.isoformat()
        }