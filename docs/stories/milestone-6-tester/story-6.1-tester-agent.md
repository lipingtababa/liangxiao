# Story 6.1: Tester Agent Implementation ✅ COMPLETED

## Story Details
- **ID**: 6.1
- **Title**: Build Test Generation Agent
- **Milestone**: Milestone 6 - Tester Agent
- **Points**: 8
- **Priority**: P1 (Essential)
- **Dependencies**: Story 5.1 (Analyst Agent), Story 4.1 (Developer Agent)
- **Status**: ✅ COMPLETED - Implementation available at `services/orchestrator/agents/tester/`

## Description

### Overview
Implement the Tester Agent that generates comprehensive test cases based on requirements and validates implementations. The Tester ensures code quality through automated testing, catching issues that manual review might miss.

### Why This Is Important
- Validates that implementations meet requirements
- Catches edge cases and error conditions
- Provides regression protection for future changes
- Ensures code quality through automated verification
- Prevents bugs from reaching production

### Context
Even with Navigator review, bugs can slip through. The Tester Agent creates comprehensive test suites that verify implementations work correctly, handle edge cases, and fail gracefully when expected.

## Acceptance Criteria

### Required
- [ ] Tester Agent class implemented with LangChain
- [ ] Generates unit tests from requirements specifications
- [ ] Creates integration tests for component interactions
- [ ] Handles various programming languages and frameworks
- [ ] Tests cover normal cases, edge cases, and error conditions
- [ ] Generated tests are syntactically correct and executable
- [ ] Test coverage analysis and reporting
- [ ] Clear test documentation and descriptions
- [ ] Integration with existing test frameworks
- [ ] Validates implementation against requirements

## Technical Details

### Tester Agent Implementation
```python
# agents/tester/agent.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
import logging
import re

logger = logging.getLogger(__name__)

class TestCase(BaseModel):
    """Individual test case."""
    name: str = Field(description="Descriptive test name")
    description: str = Field(description="What this test validates")
    category: Literal["unit", "integration", "edge_case", "error_handling", "performance"]
    priority: Literal["critical", "high", "medium", "low"]
    test_code: str = Field(description="Complete test implementation")
    expected_outcome: str = Field(description="What should happen when test runs")
    requirements_coverage: List[str] = Field(description="Which requirements this test validates")

class TestSuite(BaseModel):
    """Complete test suite."""
    test_cases: List[TestCase]
    framework: str = Field(description="Testing framework used")
    setup_code: Optional[str] = Field(description="Test setup/initialization code")
    teardown_code: Optional[str] = Field(description="Test cleanup code")
    coverage_analysis: Dict[str, float] = Field(description="Coverage percentages")
    total_tests: int = Field(description="Total number of tests")

class TesterAgent:
    """
    Tester agent that generates comprehensive test suites.
    
    Creates tests based on requirements and validates implementations.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.2  # Low temperature for consistent test generation
        )
        self.parser = PydanticOutputParser(pydantic_object=TestSuite)
    
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute testing task.
        
        Args:
            task: Testing task definition
            context: Requirements, implementation, and repository context
            
        Returns:
            Test artifacts and coverage analysis
        """
        logger.info(f"Tester executing task: {task['id']}")
        
        try:
            # Extract context
            requirements = self._extract_requirements(context)
            implementation = self._extract_implementation(context)
            
            # Determine testing framework
            framework = self._detect_testing_framework(context)
            
            # Generate comprehensive test suite
            test_suite = await self._generate_test_suite(
                requirements=requirements,
                implementation=implementation,
                framework=framework,
                task=task
            )
            
            # Create test files
            test_artifacts = await self._create_test_artifacts(test_suite, context)
            
            return {
                "success": True,
                "artifacts": test_artifacts,
                "test_summary": {
                    "total_tests": test_suite.total_tests,
                    "framework": test_suite.framework,
                    "coverage": test_suite.coverage_analysis
                },
                "summary": f"Generated {test_suite.total_tests} tests with {framework} framework"
            }
            
        except Exception as e:
            logger.error(f"Tester execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "artifacts": []
            }
    
    def _extract_requirements(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract requirements from context."""
        # Look for requirements from Analyst
        completed_tasks = context.get("completed_tasks", [])
        for task_result in completed_tasks:
            if task_result.get("type") == "analysis":
                return task_result.get("artifacts", {})
        
        # Fallback to issue information
        return {
            "requirements": [context.get("issue", {}).get("body", "")],
            "acceptance_criteria": []
        }
    
    def _extract_implementation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract implementation details from context."""
        # Look for code from Developer
        completed_tasks = context.get("completed_tasks", [])
        for task_result in completed_tasks:
            if task_result.get("type") == "implementation":
                return task_result.get("artifacts", {})
        
        return {"code": "", "files": []}
    
    def _detect_testing_framework(self, context: Dict[str, Any]) -> str:
        """Detect appropriate testing framework."""
        repository = context.get("repository", "")
        
        # Analyze repository structure or package.json/requirements.txt
        # For now, default to common frameworks
        if "python" in repository.lower():
            return "pytest"
        elif "javascript" in repository.lower() or "typescript" in repository.lower():
            return "jest"
        else:
            return "pytest"  # Default
    
    async def _generate_test_suite(
        self,
        requirements: Dict[str, Any],
        implementation: Dict[str, Any],
        framework: str,
        task: Dict[str, Any]
    ) -> TestSuite:
        """Generate comprehensive test suite."""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are an expert Test Engineer who creates comprehensive test suites.
                
                Your goal is to generate tests that:
                1. Validate all requirements are met
                2. Cover normal use cases and edge cases
                3. Test error handling and boundary conditions
                4. Are maintainable and well-documented
                5. Use best practices for the testing framework
                
                Testing framework: {framework}
                
                Test categories to include:
                - Unit tests: Test individual components/functions
                - Integration tests: Test component interactions  
                - Edge cases: Boundary values, empty inputs, etc.
                - Error handling: Invalid inputs, error conditions
                
                Write tests that would have caught disasters like PR #23
                (where entire file was deleted instead of targeted change).
                
                {format_instructions}
                """
            ),
            ("human", """Create comprehensive tests for this implementation:

Requirements:
{requirements}

Implementation:
{implementation}

Task: {task_description}

Generate a complete test suite:""")
        ])
        
        formatted_prompt = prompt.format_messages(
            framework=framework,
            format_instructions=self.parser.get_format_instructions(),
            requirements=self._format_requirements(requirements),
            implementation=self._format_implementation(implementation),
            task_description=task.get("description", "")
        )
        
        response = await self.llm.ainvoke(formatted_prompt)
        test_suite = self.parser.parse(response.content)
        
        return test_suite
    
    def _format_requirements(self, requirements: Dict[str, Any]) -> str:
        """Format requirements for prompt."""
        if isinstance(requirements.get("requirements"), list):
            return "\n".join([
                f"- {req.get('description', req)}" 
                for req in requirements["requirements"]
            ])
        return str(requirements)
    
    def _format_implementation(self, implementation: Dict[str, Any]) -> str:
        """Format implementation for prompt."""
        code_parts = []
        for file in implementation.get("files", []):
            code_parts.append(f"File: {file.get('path', 'unknown')}\n{file.get('content', '')}")
        
        return "\n\n".join(code_parts) or implementation.get("code", "No implementation provided")
    
    async def _create_test_artifacts(self, test_suite: TestSuite, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create test file artifacts."""
        artifacts = []
        
        # Group tests by category for organization
        test_files = self._organize_tests_into_files(test_suite)
        
        for file_name, tests in test_files.items():
            test_content = self._generate_test_file_content(
                tests, 
                test_suite.framework,
                test_suite.setup_code,
                test_suite.teardown_code
            )
            
            artifacts.append({
                "type": "test",
                "path": file_name,
                "content": test_content,
                "framework": test_suite.framework,
                "test_count": len(tests)
            })
        
        # Add test configuration files if needed
        config_artifact = self._create_test_config(test_suite.framework)
        if config_artifact:
            artifacts.append(config_artifact)
        
        return artifacts
    
    def _organize_tests_into_files(self, test_suite: TestSuite) -> Dict[str, List[TestCase]]:
        """Organize tests into appropriate files."""
        files = {
            "tests/test_unit.py": [],
            "tests/test_integration.py": [],
            "tests/test_edge_cases.py": []
        }
        
        for test in test_suite.test_cases:
            if test.category == "unit":
                files["tests/test_unit.py"].append(test)
            elif test.category == "integration":
                files["tests/test_integration.py"].append(test)
            else:
                files["tests/test_edge_cases.py"].append(test)
        
        # Remove empty files
        return {k: v for k, v in files.items() if v}
    
    def _generate_test_file_content(
        self,
        tests: List[TestCase],
        framework: str,
        setup_code: Optional[str],
        teardown_code: Optional[str]
    ) -> str:
        """Generate complete test file content."""
        
        content = f"""# Generated test file
# Framework: {framework}

import pytest
from unittest.mock import Mock, patch
"""
        
        if setup_code:
            content += f"\n# Setup\n{setup_code}\n"
        
        for test in tests:
            content += f"""

def {self._sanitize_test_name(test.name)}():
    \"\"\"
    {test.description}
    
    Category: {test.category}
    Priority: {test.priority}
    Expected: {test.expected_outcome}
    \"\"\"
    {self._format_test_code(test.test_code)}
"""
        
        if teardown_code:
            content += f"\n# Teardown\n{teardown_code}\n"
        
        return content
    
    def _sanitize_test_name(self, name: str) -> str:
        """Sanitize test name for function naming."""
        # Convert to valid Python function name
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
        if not sanitized.startswith('test_'):
            sanitized = f"test_{sanitized}"
        return sanitized
    
    def _format_test_code(self, test_code: str) -> str:
        """Format test code with proper indentation."""
        lines = test_code.split('\n')
        indented_lines = [f"    {line}" if line.strip() else "" for line in lines]
        return '\n'.join(indented_lines)
    
    def _create_test_config(self, framework: str) -> Optional[Dict[str, Any]]:
        """Create test configuration file if needed."""
        if framework == "pytest":
            return {
                "type": "config",
                "path": "pytest.ini",
                "content": """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = --verbose --tb=short --cov=src --cov-report=html
"""
            }
        elif framework == "jest":
            return {
                "type": "config", 
                "path": "jest.config.js",
                "content": """module.exports = {
  testEnvironment: 'node',
  collectCoverageFrom: ['src/**/*.js'],
  coverageDirectory: 'coverage',
  verbose: true
};
"""
            }
        return None
```

### Example Test Generation
```python
# Example for README phrase removal (preventing PR #23)

test_suite = TestSuite(
    test_cases=[
        TestCase(
            name="test_remove_specific_phrase_only",
            description="Verify only the target phrase is removed, not entire file",
            category="unit",
            priority="critical",
            test_code="""
# Read original README
with open('README.md', 'r') as f:
    original_content = f.read()

# Apply the change
result = remove_phrase_from_readme('解释文化细节')

# Verify phrase is gone
assert '解释文化细节' not in result
# Verify file is not empty (prevent PR #23!)
assert len(result) > 100
# Verify other content preserved
assert 'Project Overview' in result
assert 'Installation' in result
""",
            expected_outcome="Phrase removed, other content preserved",
            requirements_coverage=["Remove phrase", "Preserve other content"]
        ),
        TestCase(
            name="test_phrase_not_found_handling",
            description="Handle case where phrase doesn't exist",
            category="edge_case",
            priority="medium",
            test_code="""
# Test with README that doesn't contain target phrase
content_without_phrase = "Some other content"
result = remove_phrase_from_readme('non_existent_phrase', content_without_phrase)

# Should return original content unchanged
assert result == content_without_phrase
""",
            expected_outcome="Original content returned unchanged",
            requirements_coverage=["Handle missing phrase gracefully"]
        ),
        TestCase(
            name="test_multiple_phrase_occurrences",
            description="Handle multiple occurrences of target phrase",
            category="edge_case", 
            priority="high",
            test_code="""
# Test with multiple occurrences
content_with_multiple = "Text 解释文化细节 more text 解释文化细节 end"
result = remove_phrase_from_readme('解释文化细节', content_with_multiple)

# All occurrences should be removed
assert '解释文化细节' not in result
# Other text should remain
assert 'Text' in result and 'more text' in result and 'end' in result
""",
            expected_outcome="All phrase occurrences removed",
            requirements_coverage=["Handle multiple occurrences"]
        )
    ],
    framework="pytest",
    total_tests=3
)
```

## Testing Requirements

### Unit Tests
```python
# tests/test_tester_agent.py
import pytest
from agents.tester.agent import TesterAgent

@pytest.mark.asyncio
async def test_tester_generates_comprehensive_tests():
    """Test that tester creates comprehensive test suites."""
    tester = TesterAgent()
    
    task = {
        "id": "test-1",
        "description": "Create tests for README modification"
    }
    
    context = {
        "issue": {
            "body": "Remove specific phrase from README"
        },
        "completed_tasks": [
            {
                "type": "implementation",
                "artifacts": {
                    "code": "def remove_phrase(text, phrase): return text.replace(phrase, '')"
                }
            }
        ]
    }
    
    result = await tester.execute(task, context)
    
    assert result["success"]
    assert len(result["artifacts"]) > 0
    assert result["test_summary"]["total_tests"] > 0
    
    # Should have different types of tests
    test_content = result["artifacts"][0]["content"]
    assert "test_" in test_content
    assert "def " in test_content

@pytest.mark.asyncio
async def test_prevents_pr_23_with_tests():
    """Test that generated tests would catch PR #23 type disasters."""
    tester = TesterAgent()
    
    # Simulate PR #23 scenario
    context = {
        "issue": {"body": "Remove phrase from README"},
        "completed_tasks": [{
            "type": "implementation", 
            "artifacts": {
                "code": "def remove_phrase(): return ''"  # Disaster code!
            }
        }]
    }
    
    result = await tester.execute({}, context)
    
    # Should generate tests that catch empty file returns
    test_content = result["artifacts"][0]["content"]
    assert "len(" in test_content  # Length checks
    assert "assert" in test_content  # Assertions
```

## Dependencies & Risks

### Prerequisites
- Requirements from Analyst Agent
- Implementation from Developer Agent  
- Understanding of testing frameworks

### Risks
- **Generated tests don't compile**: Syntax errors in generated code
- **Tests don't actually test anything**: Weak assertions
- **Framework compatibility**: Tests don't work with project setup
- **Over-testing**: Too many redundant tests

### Mitigations
- Syntax validation before saving tests
- Strong assertion requirements
- Framework detection and adaptation
- Test categorization and prioritization

## Definition of Done

1. ✅ Tester Agent class implemented
2. ✅ Generates syntactically correct tests
3. ✅ Covers unit, integration, and edge cases
4. ✅ Tests validate requirements compliance
5. ✅ Framework-appropriate test generation
6. ✅ Test coverage analysis
7. ✅ Integration with Task Pair system
8. ✅ Unit tests passing
9. ✅ Would catch PR #23 type disasters

## Implementation Notes for AI Agents

### DO
- Generate tests that actually test the requirements
- Include edge cases and error conditions  
- Use appropriate assertions and checks
- Follow framework conventions
- Add clear test descriptions

### DON'T
- Don't generate tests that always pass
- Don't ignore edge cases
- Don't use incorrect framework syntax
- Don't create redundant tests
- Don't skip error handling tests

### Common Pitfalls to Avoid
1. Tests that don't actually validate requirements
2. Missing edge case coverage
3. Syntax errors in generated test code
4. Tests that are too generic
5. Not testing error conditions

## Success Example

Tests preventing PR #23:
```python
def test_targeted_phrase_removal():
    """Ensure only target phrase removed, not entire file."""
    original = "Long README with much content and 解释文化细节 phrase"
    result = remove_phrase(original, '解释文化细节')
    
    # Critical assertions that would catch PR #23
    assert '解释文化细节' not in result  # Phrase removed
    assert len(result) > 50  # File not empty!
    assert "Long README" in result  # Content preserved
    assert result != ""  # Not completely deleted

# This test would FAIL with PR #23 code, catching the disaster! ✅
```

## Next Story
Once this story is complete, proceed to [Story 6.2: Test Validation System](story-6.2-test-validation.md)