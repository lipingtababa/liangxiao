"""Comprehensive pytest configuration and fixtures for unit tests.

This module provides shared fixtures, mocking strategies, and configuration
for all unit tests in the SyntheticCodingTeam system.
"""

import pytest
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List, Optional

# Import all the models and classes we need for fixtures
from core.interfaces import (
    StepResult, QualityMetrics, NextAction,
    DeveloperInput, DeveloperOutput, CodeChange,
    AnalystInput, AnalystOutput,
    TesterInput, TesterOutput,
    WorkflowContext, QualityGate,
    create_step_result, create_quality_metrics
)
from core.state_machine import IssueState, WorkflowContext as SMWorkflowContext
from models.github import IssueEvent, GitHubIssue, GitHubRepository, GitHubUser, GitHubLabel


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (slower)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast)"
    )
    config.addinivalue_line(
        "markers", "disaster_prevention: tests disaster prevention capabilities"
    )
    config.addinivalue_line(
        "markers", "state_machine: tests state machine functionality"
    )
    config.addinivalue_line(
        "markers", "ai_agent: tests AI agent behavior"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location and name."""
    for item in items:
        # Mark all tests in test_unit as unit tests
        if "test_unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark disaster prevention tests
        if "disaster" in item.name.lower() or "prevention" in item.name.lower():
            item.add_marker(pytest.mark.disaster_prevention)
        
        # Mark state machine tests
        if "state" in item.name.lower() or "transition" in item.name.lower():
            item.add_marker(pytest.mark.state_machine)
        
        # Mark AI agent tests
        if any(agent in item.name.lower() for agent in ["developer", "navigator", "pm", "agent"]):
            item.add_marker(pytest.mark.ai_agent)


# ============================================================================
# Environment and Setup Fixtures
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables and configuration."""
    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "test-api-key-12345"
    os.environ["GITHUB_TOKEN"] = "test-github-token-67890"
    os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"
    os.environ["ENVIRONMENT"] = "test"
    
    # Disable actual logging during tests
    os.environ["LOG_LEVEL"] = "WARNING"
    
    yield
    
    # Cleanup after all tests
    test_env_vars = [
        "OPENAI_API_KEY", "GITHUB_TOKEN", "WEBHOOK_SECRET", 
        "ENVIRONMENT", "LOG_LEVEL"
    ]
    for var in test_env_vars:
        os.environ.pop(var, None)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client for testing."""
    client = Mock()
    
    # Mock successful response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"success": true, "result": "test"}'
    
    # Make methods async
    async def mock_acreate(*args, **kwargs):
        return mock_response
    
    client.chat.completions.acreate = mock_acreate
    client.chat.completions.create = Mock(return_value=mock_response)
    
    return client


# ============================================================================
# Core Interface Fixtures
# ============================================================================

@pytest.fixture
def sample_quality_metrics():
    """Create sample quality metrics."""
    return create_quality_metrics(
        completeness=0.9,
        accuracy=0.95,
        code_quality=0.85,
        test_coverage=88.0,
        critical_issues=0,
        warnings=2
    )


@pytest.fixture
def sample_step_result(sample_quality_metrics):
    """Create a sample step result."""
    return create_step_result(
        agent="developer",
        status="success",
        output_data={
            "implementation": "complete",
            "files_changed": ["src/main.py", "tests/test_main.py"],
            "tests_passed": True
        },
        confidence=0.9,
        suggestions=["create_pr", "notify_stakeholders"],
        quality_metrics=sample_quality_metrics
    )


@pytest.fixture
def sample_code_change():
    """Create a sample code change."""
    return CodeChange(
        file_path="src/auth.py",
        diff="""--- a/src/auth.py
+++ b/src/auth.py
@@ -10,3 +10,7 @@ class AuthService:
     def authenticate(self, username, password):
         return False
 
+    def secure_authenticate(self, username, password):
+        # Secure authentication with proper validation
+        return self._verify_credentials(username, password)
+""",
        summary="Add secure authentication method"
    )


@pytest.fixture
def sample_developer_input():
    """Create sample developer input."""
    return DeveloperInput(
        requirements="Implement secure user authentication",
        acceptance_criteria=[
            "Users can login with valid credentials",
            "Invalid credentials are rejected with appropriate error",
            "Password security follows best practices",
            "Rate limiting prevents brute force attacks"
        ],
        test_file_path="tests/test_auth.py"
    )


@pytest.fixture
def sample_developer_output(sample_code_change):
    """Create sample developer output."""
    return DeveloperOutput(
        changes_made=[sample_code_change],
        tests_passed=True,
        test_output="""
==================== test session starts ====================
collected 4 items

test_auth.py::test_valid_login PASSED                    [25%]
test_auth.py::test_invalid_login PASSED                  [50%]
test_auth.py::test_password_security PASSED             [75%]
test_auth.py::test_rate_limiting PASSED                 [100%]

==================== 4 passed in 1.23s ====================
""",
        implementation_notes="Implemented secure authentication with bcrypt hashing and rate limiting"
    )


@pytest.fixture
def sample_analyst_input():
    """Create sample analyst input."""
    return AnalystInput(
        issue_description="Users are reporting that they cannot log into the application. The login form accepts credentials but always returns 'invalid credentials' even with correct information."
    )


@pytest.fixture
def sample_analyst_output():
    """Create sample analyst output."""
    return AnalystOutput(
        acceptance_criteria=[
            "Users with valid credentials can successfully log in",
            "Users with invalid credentials receive clear error messages",
            "Login attempts are properly logged for security monitoring",
            "Password requirements are clearly communicated to users"
        ],
        clarification_questions=[
            "Should we implement two-factor authentication?",
            "What is the maximum number of failed login attempts allowed?",
            "Should locked accounts require manual unlock or auto-unlock after time?"
        ],
        complexity="medium",
        effort_estimate="2-3 days"
    )


@pytest.fixture
def sample_tester_input():
    """Create sample tester input."""
    return TesterInput(
        acceptance_criteria=[
            "Login works with valid credentials",
            "Login fails with invalid credentials",
            "Error messages are user-friendly"
        ],
        feature_description="User authentication system with secure login"
    )


@pytest.fixture
def sample_tester_output():
    """Create sample tester output."""
    return TesterOutput(
        test_code="""
import pytest
from auth import AuthService

class TestAuthService:
    def test_valid_login(self):
        auth = AuthService()
        result = auth.authenticate("valid_user", "correct_password")
        assert result.success is True
        assert result.user_id is not None
    
    def test_invalid_credentials(self):
        auth = AuthService()
        result = auth.authenticate("user", "wrong_password")
        assert result.success is False
        assert "Invalid credentials" in result.error_message
    
    def test_rate_limiting(self):
        auth = AuthService()
        # Simulate multiple failed attempts
        for i in range(5):
            auth.authenticate("user", "wrong")
        
        # Should be rate limited now
        result = auth.authenticate("user", "wrong")
        assert "Too many attempts" in result.error_message
""",
        test_file_path="tests/test_auth.py",
        test_count=3,
        framework="pytest"
    )


@pytest.fixture
def sample_quality_gate():
    """Create a sample quality gate."""
    return QualityGate(
        min_confidence=0.8,
        max_critical_issues=0,
        min_completeness=0.85
    )


@pytest.fixture
def sample_workflow_context():
    """Create a sample workflow context."""
    return WorkflowContext(
        issue_id="123",
        issue_title="Fix login authentication bug",
        issue_description="Users cannot log in with correct credentials",
        issue_complexity="medium"
    )


# ============================================================================
# State Machine Fixtures
# ============================================================================

@pytest.fixture
def sample_sm_workflow_context():
    """Create sample state machine workflow context."""
    context = SMWorkflowContext(
        issue_number=456,
        issue_title="Implement new feature",
        issue_description="Add dashboard analytics functionality",
        repository="company/analytics-app"
    )
    return context


@pytest.fixture
def workflow_context_with_history():
    """Create workflow context with state transition history."""
    context = SMWorkflowContext(
        issue_number=789,
        issue_title="Complex bug fix",
        issue_description="Memory leak in data processing pipeline",
        repository="company/data-pipeline"
    )
    
    # Add some state transitions
    context.transition_to_state(IssueState.ANALYZING_REQUIREMENTS, "Starting analysis")
    context.transition_to_state(IssueState.CREATING_TESTS, "Requirements clear")
    context.transition_to_state(IssueState.IMPLEMENTING, "Tests created")
    
    return context


# ============================================================================
# GitHub Model Fixtures
# ============================================================================

@pytest.fixture
def sample_github_user():
    """Create a sample GitHub user."""
    return GitHubUser(
        login="test_user",
        id=12345,
        type="User"
    )


@pytest.fixture
def sample_github_repository(sample_github_user):
    """Create a sample GitHub repository."""
    return GitHubRepository(
        name="test-repo",
        full_name="test-org/test-repo",
        private=False,
        id=67890,
        html_url="https://github.com/test-org/test-repo",
        owner=sample_github_user,
        default_branch="main"
    )


@pytest.fixture
def sample_github_labels():
    """Create sample GitHub labels."""
    return [
        GitHubLabel(name="bug", color="red"),
        GitHubLabel(name="priority-high", color="orange"),
        GitHubLabel(name="needs-investigation", color="yellow")
    ]


@pytest.fixture
def sample_github_issue(sample_github_user, sample_github_labels):
    """Create a sample GitHub issue."""
    return GitHubIssue(
        number=101,
        title="Critical authentication bug",
        body="Users cannot authenticate properly. This is causing major disruption to the service.",
        state="open",
        labels=sample_github_labels,
        assignee=sample_github_user,
        assignees=[sample_github_user],
        created_at=datetime(2024, 1, 15, 10, 0, 0),
        updated_at=datetime(2024, 1, 15, 14, 30, 0),
        html_url="https://github.com/test-org/test-repo/issues/101",
        id=555666,
        url="https://api.github.com/repos/test-org/test-repo/issues/101",
        user=sample_github_user,
        locked=False
    )


@pytest.fixture
def sample_issue_event(sample_github_issue, sample_github_repository, sample_github_user):
    """Create a sample GitHub issue event."""
    return IssueEvent(
        action="opened",
        issue=sample_github_issue,
        repository=sample_github_repository,
        sender=sample_github_user
    )


# ============================================================================
# Mock Agent Fixtures
# ============================================================================

@pytest.fixture
def mock_developer_agent():
    """Create a mock developer agent."""
    agent = Mock()
    
    async def mock_execute(developer_input):
        return create_step_result(
            agent="developer",
            status="success",
            output_data={
                "changes_made": [{"file_path": "test.py", "summary": "Test change"}],
                "tests_passed": True,
                "implementation_notes": "Mock implementation"
            },
            confidence=0.9
        )
    
    agent.execute = mock_execute
    agent.get_metrics.return_value = {
        "total_executions": 5,
        "total_changes_made": 12,
        "total_tests_run": 8
    }
    
    return agent


@pytest.fixture
def mock_pm_agent():
    """Create a mock PM agent."""
    agent = Mock()
    
    def mock_evaluate_step_result(step_result, context, quality_gate=None):
        return NextAction(
            target_agent="developer",
            input_data={"requirements": "Mock requirements"},
            reason="Mock PM decision"
        )
    
    agent.evaluate_step_result = mock_evaluate_step_result
    agent.post_github_comment.return_value = True
    agent.get_metrics.return_value = {
        "total_evaluations": 10,
        "total_human_interactions": 3,
        "navigator_status": "FROZEN"
    }
    
    return agent


@pytest.fixture
def mock_navigator_agent():
    """Create a mock navigator agent (FROZEN)."""
    agent = Mock()
    
    async def mock_review(task, work_output, context, iteration_number=1):
        from agents.navigator.agent import ReviewFeedback, ReviewDecision
        return ReviewFeedback(
            decision=ReviewDecision.APPROVED,
            overall_assessment="Mock review passed",
            quality_score=8,
            completeness_score=9,
            correctness_score=8,
            reasoning="Mock navigator review (FROZEN)",
            iteration_number=iteration_number,
            adjusted_strictness=1.0
        )
    
    agent.review = mock_review
    agent.specialty = "code_review"
    agent.base_strictness = 1.0
    
    return agent


# ============================================================================
# Disaster Prevention Fixtures
# ============================================================================

@pytest.fixture
def dangerous_code_scenarios():
    """Create scenarios that should trigger disaster prevention."""
    return [
        {
            "name": "file_deletion_disaster",
            "description": "Code that deletes entire directory instead of single file",
            "code": """
import shutil
import os

def remove_phrase_from_readme(phrase):
    # DISASTER: This deletes entire directory!
    shutil.rmtree(".")
    
    # Recreate minimal file
    with open("README.md", "w") as f:
        f.write("# Repository (phrase removed)")
""",
            "expected_issues": ["file deletion", "directory removal", "disaster"]
        },
        {
            "name": "sql_injection_vulnerability", 
            "description": "SQL injection vulnerability",
            "code": """
def authenticate_user(username, password):
    # DISASTER: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    return cursor.fetchone() is not None
""",
            "expected_issues": ["sql injection", "security vulnerability"]
        },
        {
            "name": "command_injection",
            "description": "Command injection vulnerability",
            "code": """
import subprocess

def process_file(filename):
    # DISASTER: Command injection
    subprocess.run(f"rm {filename}", shell=True)
""",
            "expected_issues": ["command injection", "shell injection", "security"]
        }
    ]


@pytest.fixture
def pr_23_scenario():
    """Create the specific PR #23 disaster scenario."""
    return {
        "task_description": "Remove the phrase 'built with love' from README.md",
        "acceptance_criteria": [
            "Only remove the specific phrase 'built with love'",
            "Preserve all other content in README.md",
            "File structure remains intact"
        ],
        "dangerous_implementation": """
import os

def remove_phrase_from_readme():
    # DISASTER: This is what caused PR #23
    os.remove("README.md")
    
    # Create new minimal README
    with open("README.md", "w") as f:
        f.write("# Project\\n\\nSimple project description.")
""",
        "expected_disaster_detection": [
            "deletes entire file",
            "removes complete content", 
            "disaster prevention",
            "PR #23"
        ]
    }


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def large_test_datasets():
    """Create large datasets for performance and edge case testing."""
    return {
        "large_issue_description": "This is a " + "very detailed " * 1000 + "issue description that tests handling of large text inputs.",
        "many_acceptance_criteria": [f"Acceptance criteria number {i}" for i in range(100)],
        "complex_code_changes": [
            {
                "file_path": f"src/module_{i}.py",
                "summary": f"Change {i} in module {i}",
                "diff": f"+ def function_{i}():\n+     return {i}\n"
            }
            for i in range(50)
        ],
        "unicode_test_data": {
            "title": "测试 Unicode 支持 🚀 Тест العربية",
            "description": "Issue with Unicode: ñáéíóú ÀÈÌÒÙ çñü ß αβγδε المرحبا こんにちは",
            "code": "print('🎉 Success! 成功！ نجح!')"
        }
    }


@pytest.fixture
def edge_case_inputs():
    """Create edge case inputs for robust testing."""
    return {
        "empty_strings": {
            "title": "",
            "description": "",
            "requirements": "",
            "code": ""
        },
        "null_values": {
            "title": None,
            "description": None,
            "requirements": None,
            "acceptance_criteria": None
        },
        "special_characters": {
            "title": "Test with !@#$%^&*()_+-=[]{}|;:'\",.<>?`~",
            "description": "Description with\nnewlines\tand\ttabs\rand\\backslashes",
            "code": "code = 'with \"quotes\" and \\'apostrophes\\''"
        },
        "extremely_long": {
            "title": "X" * 10000,
            "description": "Long description " * 5000,
            "code": "# Comment " * 1000 + "\nprint('test')"
        }
    }


# ============================================================================
# Performance Fixtures
# ============================================================================

@pytest.fixture
def performance_benchmark():
    """Fixture for performance benchmarking."""
    results = {}
    
    def record_time(operation_name, start_time, end_time):
        duration = end_time - start_time
        results[operation_name] = duration
        return duration
    
    def get_results():
        return results.copy()
    
    benchmark = Mock()
    benchmark.record_time = record_time
    benchmark.get_results = get_results
    
    return benchmark


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_each_test():
    """Automatically clean up after each test."""
    yield
    
    # Clean up any test artifacts
    import gc
    gc.collect()


@pytest.fixture(scope="function")
def isolated_test():
    """Ensure test isolation by clearing global state."""
    # Store original state
    original_env = os.environ.copy()
    
    yield
    
    # Restore original state
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Parametrized Fixtures
# ============================================================================

@pytest.fixture(params=["developer", "analyst", "tester", "pm"])
def agent_type(request):
    """Parametrized fixture for different agent types."""
    return request.param


@pytest.fixture(params=["success", "failed", "needs_clarification"])
def step_status(request):
    """Parametrized fixture for different step statuses."""
    return request.param


@pytest.fixture(params=[0.1, 0.5, 0.7, 0.9, 0.99])
def confidence_level(request):
    """Parametrized fixture for different confidence levels."""
    return request.param


@pytest.fixture(params=["simple", "medium", "complex"])
def issue_complexity(request):
    """Parametrized fixture for different issue complexities."""
    return request.param


# ============================================================================
# Utility Functions
# ============================================================================

def create_mock_async_function(return_value=None, side_effect=None):
    """Utility to create mock async functions."""
    async def mock_func(*args, **kwargs):
        if side_effect:
            if callable(side_effect):
                return side_effect(*args, **kwargs)
            else:
                raise side_effect
        return return_value
    
    return mock_func


def assert_disaster_prevention_triggered(feedback_or_result, expected_keywords=None):
    """Utility to assert that disaster prevention was triggered."""
    expected_keywords = expected_keywords or ["disaster", "critical", "security", "deletion"]
    
    if hasattr(feedback_or_result, 'issues'):
        # Navigator feedback
        issues_text = ' '.join([issue.description.lower() for issue in feedback_or_result.issues])
        assert any(keyword in issues_text for keyword in expected_keywords), \
            f"Expected disaster prevention keywords {expected_keywords} not found in issues"
    elif hasattr(feedback_or_result, 'output'):
        # Step result
        output_text = str(feedback_or_result.output).lower()
        assert any(keyword in output_text for keyword in expected_keywords), \
            f"Expected disaster prevention keywords {expected_keywords} not found in output"
    else:
        assert False, "Unknown feedback/result type for disaster prevention check"


# ============================================================================
# Custom Assertions
# ============================================================================

def assert_step_result_valid(step_result: StepResult):
    """Assert that a StepResult has valid structure and values."""
    assert isinstance(step_result, StepResult)
    assert step_result.status in ["success", "failed", "needs_clarification"]
    assert isinstance(step_result.agent, str)
    assert len(step_result.agent) > 0
    assert isinstance(step_result.output, dict)
    assert 0.0 <= step_result.confidence <= 1.0
    assert isinstance(step_result.next_suggestions, list)
    assert isinstance(step_result.timestamp, datetime)


def assert_quality_metrics_valid(metrics: QualityMetrics):
    """Assert that QualityMetrics have valid values."""
    assert 0.0 <= metrics.completeness_score <= 1.0
    assert 0.0 <= metrics.accuracy_score <= 1.0
    
    if metrics.code_quality_score is not None:
        assert 0.0 <= metrics.code_quality_score <= 1.0
    
    if metrics.test_coverage is not None:
        assert 0.0 <= metrics.test_coverage <= 100.0
    
    assert metrics.critical_issues_count >= 0
    assert metrics.warning_count >= 0


def assert_next_action_valid(action: NextAction):
    """Assert that a NextAction is valid."""
    assert isinstance(action, NextAction)
    assert action.target_agent in ["analyst", "tester", "developer", "pm"]
    assert isinstance(action.input_data, dict)
    assert isinstance(action.reason, str)
    assert len(action.reason) > 0