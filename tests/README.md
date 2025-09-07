# SyntheticCodingTeam Test Suite

This directory contains all tests for the SyntheticCodingTeam project, organized following Python testing best practices.

## Directory Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interactions
├── e2e/           # End-to-end tests for complete workflows
├── fixtures/      # Shared test fixtures and data
├── scripts/       # Helper scripts for running tests
└── conftest.py    # Pytest configuration and shared fixtures
```

## Test Categories

### Unit Tests (`tests/unit/`)
Tests for individual components in isolation:
- `test_analyst.py` - Analyst agent unit tests
- `test_developer_agent.py` - Developer agent unit tests
- `test_pm_agent.py` - PM agent unit tests
- `test_tester_agent.py` - Tester agent unit tests
- `test_navigator.py` - Navigator component unit tests
- `test_pm_nodes.py` - PM nodes unit tests
- `test_health.py` - Health check unit tests
- `test_workspace.py` - Workspace unit tests
- `test_workspace_simple.py` - Simple workspace unit tests
- `test_github_cli_service.py` - GitHub CLI service unit tests
- `test_webhook.py` - Webhook handler unit tests
- `test_enhanced_logging.py` - Enhanced logging unit tests
- `test_interfaces.py` - Interface definition tests

### Integration Tests (`tests/integration/`)
Tests for component interactions:
- `test_analyst_navigator_pair.py` - Analyst-Navigator pair integration
- `test_github_integration.py` - GitHub API integration
- `test_github_poller.py` - GitHub poller integration ⚠️ OUTDATED - poller moved to separate repo
- `test_github_workspace.py` - GitHub workspace integration
- `test_navigator_integration.py` - Navigator integration
- `test_pm_integration.py` - PM agent integration
- `test_poller_integration.py` - Poller service integration ⚠️ OUTDATED - poller moved to separate repo
- `test_poller_service.py` - Poller service tests ⚠️ OUTDATED - poller moved to separate repo
- `test_task_pair.py` - Task pair integration
- `test_task_pair_integration.py` - Task pair integration tests
- `test_workflow.py` - Workflow integration
- `test_git_workflow.py` - Git workflow integration
- `test_navigator_freeze_pm_flexible.py` - Navigator freeze prevention
- `test_analyst_direct.py` - Direct analyst integration
- `test_auth_fix.py` - Authentication fix integration
- `test_mock_workflow.py` - Mock workflow tests
- `test_pr_validation.py` - PR validation tests
- `test_simple_workflow.py` - Simple workflow tests

### End-to-End Tests (`tests/e2e/`)
Complete system tests:
- `test_complete_end_to_end.py` - Complete E2E workflow test
- `test_issue_21_e2e.py` - Real issue #21 E2E test (disaster prevention)
- `test_blackbox_e2e.py` - Black box E2E test
- `test_navigator_freeze_issue_23_e2e.py` - Navigator freeze prevention E2E
- `test_e2e_bypass_navigator.py` - E2E test bypassing Navigator
- `test_e2e_create_pr.py` - E2E PR creation test
- `test_e2e_with_starter.py` - E2E test with starter
- `test_end_to_end.py` - Basic E2E test
- `test_end_to_end_workflow.py` - E2E workflow test
- `test_blackbox_simple.py` - Simple black box test

### Test Scripts (`tests/scripts/`)
Helper scripts for running specific tests:
- `trigger_issue_21_e2e.py` - Trigger issue #21 E2E test
- `trigger_issue_processing.py` - Trigger issue processing
- `trigger_real_issue.py` - Trigger real issue processing
- `run_e2e_issue_21.py` - Run issue #21 E2E test ⚠️ OUTDATED - uses removed poller service

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only  
pytest tests/integration/

# E2E tests only
pytest tests/e2e/
```

### Run tests by marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only E2E tests
pytest -m e2e

# Skip slow tests
pytest -m "not slow"

# Run tests requiring GitHub API
pytest -m requires_github

# Run tests requiring OpenAI API
pytest -m requires_openai
```

### Run specific test file
```bash
pytest tests/unit/test_analyst.py
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

## Important Tests

### test_issue_21_e2e.py
This is the most critical E2E test that validates the disaster prevention system by processing the actual issue #21 from the liangxiao repository - the same issue that previously caused the PR #23 disaster. This test ensures the system can safely handle complex authentication requirements without breaking existing functionality.

## Test Configuration

Test configuration is defined in:
- `pytest.ini` - Main pytest configuration
- `tests/conftest.py` - Shared fixtures and pytest plugins
- `pyproject.toml` - Project-wide configuration including test settings

## Environment Variables

Many tests require environment variables to be set:
- `GITHUB_TOKEN` or `GITHUB_PERSONAL_ACCESS_TOKEN` - GitHub API access
- `OPENAI_API_KEY` - OpenAI API access
- `TEST_MODE` - Enable test mode for certain components

## Writing New Tests

When adding new tests:
1. Place unit tests in `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Place E2E tests in `tests/e2e/`
4. Use appropriate pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`)
5. Add any required fixtures to `tests/conftest.py`
6. Document any special requirements or setup needed

## Continuous Integration

The test suite is designed to run in CI environments. E2E tests that require external services should be marked appropriately and may be skipped in certain CI configurations.