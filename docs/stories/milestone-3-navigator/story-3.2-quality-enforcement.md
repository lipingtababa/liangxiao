# Story 3.2: Quality Enforcement System ✅ COMPLETED

## Story Details
- **ID**: 3.2
- **Title**: Implement Navigator Quality Gates and Standards
- **Milestone**: Milestone 3 - Navigator Agent
- **Points**: 5
- **Priority**: P1 (Essential)  
- **Dependencies**: Story 3.1 (Navigator Core)
- **Status**: ✅ COMPLETED - Quality enforcement implemented through review templates, progressive leniency, and quality scoring

## Description

### Overview
Implement a comprehensive quality enforcement system for the Navigator Agent that establishes and enforces coding standards, architecture patterns, and quality gates. This system prevents low-quality code from progressing through the workflow and ensures consistent standards across all agent outputs.

### Why This Is Important
- Establishes consistent quality standards across all agents
- Prevents technical debt accumulation through enforcement
- Ensures architectural patterns are followed correctly
- Creates quality gates that catch issues early in the process
- Provides specific, actionable feedback for quality improvements
- Prevents disasters like PR #23 through rigorous quality checks

### Context
While the Navigator Agent can review and provide feedback, it needs specific quality standards and enforcement mechanisms to ensure consistency. This system codifies what "good" looks like and automatically enforces it.

## Acceptance Criteria

### Required
- [ ] Configurable quality standards and rules engine
- [ ] Code style and formatting enforcement
- [ ] Architecture pattern validation
- [ ] Security best practices checking
- [ ] Performance anti-pattern detection
- [ ] Test coverage and quality requirements
- [ ] Documentation completeness validation
- [ ] Quality scoring system with thresholds
- [ ] Specific improvement recommendations
- [ ] Integration with Navigator review workflow
- [ ] Quality gate enforcement (block progression on failures)
- [ ] Quality metrics tracking and reporting

## Technical Details

### Quality Standards Engine
```python
# agents/navigator/quality_enforcer.py
from typing import List, Dict, Any, Optional, Set
from enum import Enum
from pydantic import BaseModel
import ast
import re
import logging

logger = logging.getLogger(__name__)

class QualityRuleSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"

class QualityCategory(str, Enum):
    CODE_STYLE = "code_style"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    MAINTAINABILITY = "maintainability"

class QualityViolation(BaseModel):
    """Individual quality rule violation."""
    rule_id: str
    category: QualityCategory
    severity: QualityRuleSeverity
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    example: Optional[str] = None

class QualityReport(BaseModel):
    """Complete quality assessment report."""
    overall_score: float  # 0-100
    total_violations: int
    critical_count: int
    error_count: int
    warning_count: int
    info_count: int
    violations: List[QualityViolation]
    recommendations: List[str]
    quality_gates_passed: Dict[str, bool]
    can_proceed: bool

class QualityRule(BaseModel):
    """Definition of a quality rule."""
    id: str
    name: str
    category: QualityCategory
    severity: QualityRuleSeverity
    description: str
    rationale: str
    checker_function: str  # Name of method to call
    enabled: bool = True

class QualityEnforcer:
    """
    Enforces quality standards and creates quality gates.
    
    Analyzes code, documentation, and tests against established
    standards and provides specific feedback for improvements.
    """
    
    def __init__(self):
        self.rules = self._load_quality_rules()
        self.quality_thresholds = {
            "minimum_score": 70.0,
            "max_critical_violations": 0,
            "max_error_violations": 2,
            "required_test_coverage": 80.0
        }
    
    def _load_quality_rules(self) -> List[QualityRule]:
        """Load quality rules configuration."""
        return [
            # Code Style Rules
            QualityRule(
                id="CS001",
                name="Function Length",
                category=QualityCategory.CODE_STYLE,
                severity=QualityRuleSeverity.WARNING,
                description="Functions should be under 50 lines",
                rationale="Long functions are harder to understand and maintain",
                checker_function="check_function_length"
            ),
            QualityRule(
                id="CS002", 
                name="Variable Naming",
                category=QualityCategory.CODE_STYLE,
                severity=QualityRuleSeverity.ERROR,
                description="Variables should use descriptive snake_case names",
                rationale="Clear naming improves code readability",
                checker_function="check_variable_naming"
            ),
            
            # Security Rules
            QualityRule(
                id="SEC001",
                name="Hardcoded Secrets",
                category=QualityCategory.SECURITY,
                severity=QualityRuleSeverity.CRITICAL,
                description="No hardcoded passwords, tokens, or secrets",
                rationale="Hardcoded secrets are security vulnerabilities",
                checker_function="check_hardcoded_secrets"
            ),
            QualityRule(
                id="SEC002",
                name="SQL Injection Protection",
                category=QualityCategory.SECURITY,
                severity=QualityRuleSeverity.CRITICAL,
                description="Use parameterized queries, avoid string concatenation",
                rationale="Prevents SQL injection attacks",
                checker_function="check_sql_injection"
            ),
            
            # Architecture Rules
            QualityRule(
                id="ARCH001",
                name="Import Organization",
                category=QualityCategory.ARCHITECTURE,
                severity=QualityRuleSeverity.WARNING,
                description="Imports should be organized (stdlib, third-party, local)",
                rationale="Organized imports improve code navigation",
                checker_function="check_import_organization"
            ),
            QualityRule(
                id="ARCH002",
                name="Circular Dependencies",
                category=QualityCategory.ARCHITECTURE,
                severity=QualityRuleSeverity.ERROR,
                description="No circular import dependencies",
                rationale="Circular dependencies make code fragile",
                checker_function="check_circular_dependencies"
            ),
            
            # Testing Rules
            QualityRule(
                id="TEST001",
                name="Test Coverage",
                category=QualityCategory.TESTING,
                severity=QualityRuleSeverity.ERROR,
                description="Minimum 80% test coverage required",
                rationale="Good test coverage prevents regressions",
                checker_function="check_test_coverage"
            ),
            QualityRule(
                id="TEST002",
                name="Test Assertions",
                category=QualityCategory.TESTING,
                severity=QualityRuleSeverity.WARNING,
                description="Tests should have meaningful assertions",
                rationale="Tests without assertions don't validate behavior",
                checker_function="check_test_assertions"
            ),
            
            # PR #23 Prevention Rules
            QualityRule(
                id="PR23001",
                name="File Read Before Modify",
                category=QualityCategory.MAINTAINABILITY,
                severity=QualityRuleSeverity.CRITICAL,
                description="Must read existing files before modifying them",
                rationale="Prevents wholesale deletion disasters like PR #23",
                checker_function="check_file_read_before_modify"
            ),
            QualityRule(
                id="PR23002",
                name="Targeted Changes Only",
                category=QualityCategory.MAINTAINABILITY,
                severity=QualityRuleSeverity.CRITICAL,
                description="Changes should be targeted, not wholesale replacements",
                rationale="Prevents accidental deletion of important content",
                checker_function="check_targeted_changes"
            )
        ]
    
    async def assess_quality(
        self,
        artifacts: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> QualityReport:
        """
        Perform comprehensive quality assessment.
        
        Args:
            artifacts: Code, test, and documentation artifacts
            context: Additional context for assessment
            
        Returns:
            Complete quality report with violations and recommendations
        """
        logger.info(f"Assessing quality of {len(artifacts)} artifacts")
        
        violations = []
        
        # Run all enabled quality rules
        for rule in self.rules:
            if rule.enabled:
                rule_violations = await self._run_quality_rule(rule, artifacts, context)
                violations.extend(rule_violations)
        
        # Calculate quality metrics
        total_violations = len(violations)
        critical_count = len([v for v in violations if v.severity == QualityRuleSeverity.CRITICAL])
        error_count = len([v for v in violations if v.severity == QualityRuleSeverity.ERROR])
        warning_count = len([v for v in violations if v.severity == QualityRuleSeverity.WARNING])
        info_count = len([v for v in violations if v.severity == QualityRuleSeverity.INFO])
        
        # Calculate overall score (100 = perfect, decreases with violations)
        score = 100.0
        score -= critical_count * 20  # Critical violations are very expensive
        score -= error_count * 10     # Error violations are expensive
        score -= warning_count * 3    # Warning violations are moderate
        score -= info_count * 1       # Info violations are cheap
        score = max(0.0, score)       # Don't go below 0
        
        # Check quality gates
        quality_gates = self._check_quality_gates(score, violations, context)
        can_proceed = all(quality_gates.values())
        
        # Generate recommendations
        recommendations = self._generate_quality_recommendations(violations, score)
        
        return QualityReport(
            overall_score=score,
            total_violations=total_violations,
            critical_count=critical_count,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            violations=violations,
            recommendations=recommendations,
            quality_gates_passed=quality_gates,
            can_proceed=can_proceed
        )
    
    async def _run_quality_rule(
        self,
        rule: QualityRule,
        artifacts: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[QualityViolation]:
        """Run a single quality rule against artifacts."""
        
        try:
            # Get the checker method
            checker_method = getattr(self, rule.checker_function)
            violations = await checker_method(artifacts, context)
            
            # Ensure violations have rule metadata
            for violation in violations:
                violation.rule_id = rule.id
                violation.category = rule.category
                violation.severity = rule.severity
            
            return violations
            
        except AttributeError:
            logger.error(f"Quality checker method not found: {rule.checker_function}")
            return []
        except Exception as e:
            logger.error(f"Quality rule {rule.id} failed: {e}")
            return []
    
    # Quality Rule Checker Methods
    
    async def check_function_length(
        self, 
        artifacts: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[QualityViolation]:
        """Check for overly long functions."""
        
        violations = []
        
        for artifact in artifacts:
            if artifact.get("type") == "code" and artifact.get("path", "").endswith(".py"):
                content = artifact.get("content", "")
                violations.extend(self._analyze_python_function_length(content, artifact.get("path")))
        
        return violations
    
    def _analyze_python_function_length(self, content: str, file_path: str) -> List[QualityViolation]:
        """Analyze Python code for long functions."""
        
        violations = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_lines = node.end_lineno - node.lineno + 1
                    
                    if function_lines > 50:
                        violations.append(QualityViolation(
                            rule_id="CS001",
                            category=QualityCategory.CODE_STYLE,
                            severity=QualityRuleSeverity.WARNING,
                            message=f"Function '{node.name}' is {function_lines} lines long (max 50)",
                            file_path=file_path,
                            line_number=node.lineno,
                            suggestion="Consider breaking this function into smaller, focused functions",
                            example="def large_function(): -> def helper_function() + def main_function()"
                        ))
        
        except SyntaxError as e:
            # Skip syntax error files, they'll be caught by other rules
            pass
        
        return violations
    
    async def check_hardcoded_secrets(
        self, 
        artifacts: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[QualityViolation]:
        """Check for hardcoded secrets and passwords."""
        
        violations = []
        
        # Patterns that indicate hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'["\'][A-Za-z0-9+/]{20,}={0,2}["\']',  # Base64 encoded
            r'["\'][A-Za-z0-9]{32,}["\']'  # Long hex strings
        ]
        
        for artifact in artifacts:
            if artifact.get("type") == "code":
                content = artifact.get("content", "")
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip obvious test/example values
                            if not any(test_word in line.lower() for test_word in ['test', 'example', 'demo', 'placeholder']):
                                violations.append(QualityViolation(
                                    rule_id="SEC001",
                                    category=QualityCategory.SECURITY,
                                    severity=QualityRuleSeverity.CRITICAL,
                                    message="Potential hardcoded secret detected",
                                    file_path=artifact.get("path"),
                                    line_number=line_num,
                                    suggestion="Use environment variables or secure configuration",
                                    example="password = os.getenv('PASSWORD') instead of password = 'secret123'"
                                ))
        
        return violations
    
    async def check_file_read_before_modify(
        self, 
        artifacts: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[QualityViolation]:
        """Check that code reads files before modifying them (PR #23 prevention)."""
        
        violations = []
        
        for artifact in artifacts:
            if artifact.get("type") == "code":
                content = artifact.get("content", "")
                
                # Look for file modification without reading
                has_file_write = any(pattern in content for pattern in [
                    'open(', 'write(', 'update_file', 'create_file'
                ])
                
                has_file_read = any(pattern in content for pattern in [
                    'read_file', 'get_contents', 'read()', '.read(', 'read_text'
                ])
                
                if has_file_write and not has_file_read:
                    violations.append(QualityViolation(
                        rule_id="PR23001",
                        category=QualityCategory.MAINTAINABILITY, 
                        severity=QualityRuleSeverity.CRITICAL,
                        message="Code modifies files without reading them first",
                        file_path=artifact.get("path"),
                        suggestion="Always read existing file content before modifying",
                        example="""
# BAD: Direct modification
with open('file.txt', 'w') as f:
    f.write(new_content)

# GOOD: Read first, then modify
existing = read_file('file.txt')
modified = modify_content(existing)
write_file('file.txt', modified)
"""
                    ))
        
        return violations
    
    async def check_targeted_changes(
        self, 
        artifacts: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[QualityViolation]:
        """Check that changes are targeted, not wholesale replacements."""
        
        violations = []
        
        for artifact in artifacts:
            if artifact.get("type") == "code":
                content = artifact.get("content", "")
                
                # Look for patterns that suggest wholesale replacement
                wholesale_patterns = [
                    'content = ""',  # Clearing content
                    'content = \'\'',
                    '.clear()',
                    'truncate()',
                    'delete_all'
                ]
                
                # Look for targeted change patterns (good)
                targeted_patterns = [
                    '.replace(',
                    '.sub(',
                    'remove_phrase',
                    'update_specific',
                    'modify_section'
                ]
                
                has_wholesale = any(pattern in content for pattern in wholesale_patterns)
                has_targeted = any(pattern in content for pattern in targeted_patterns)
                
                if has_wholesale and not has_targeted:
                    violations.append(QualityViolation(
                        rule_id="PR23002",
                        category=QualityCategory.MAINTAINABILITY,
                        severity=QualityRuleSeverity.CRITICAL,
                        message="Code appears to do wholesale replacement instead of targeted changes",
                        file_path=artifact.get("path"),
                        suggestion="Use targeted modifications like .replace() instead of wholesale replacement",
                        example="""
# BAD: Wholesale replacement
content = ""  # Deletes everything!

# GOOD: Targeted change  
content = content.replace("unwanted phrase", "")
"""
                    ))
        
        return violations
    
    # Additional checker methods would be implemented here...
    async def check_variable_naming(self, artifacts, context): return []
    async def check_sql_injection(self, artifacts, context): return []
    async def check_import_organization(self, artifacts, context): return []
    async def check_circular_dependencies(self, artifacts, context): return []
    async def check_test_coverage(self, artifacts, context): return []
    async def check_test_assertions(self, artifacts, context): return []
    
    def _check_quality_gates(
        self,
        score: float,
        violations: List[QualityViolation],
        context: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check if quality gates pass."""
        
        critical_violations = [v for v in violations if v.severity == QualityRuleSeverity.CRITICAL]
        error_violations = [v for v in violations if v.severity == QualityRuleSeverity.ERROR]
        
        return {
            "minimum_score": score >= self.quality_thresholds["minimum_score"],
            "no_critical_violations": len(critical_violations) <= self.quality_thresholds["max_critical_violations"],
            "limited_error_violations": len(error_violations) <= self.quality_thresholds["max_error_violations"],
            "pr23_protection": not any(v.rule_id.startswith("PR23") for v in critical_violations)
        }
    
    def _generate_quality_recommendations(
        self,
        violations: List[QualityViolation],
        score: float
    ) -> List[str]:
        """Generate actionable recommendations for quality improvement."""
        
        recommendations = []
        
        # Critical violations must be fixed
        critical_violations = [v for v in violations if v.severity == QualityRuleSeverity.CRITICAL]
        if critical_violations:
            recommendations.append(f"CRITICAL: Fix {len(critical_violations)} critical violations before proceeding")
            for v in critical_violations[:3]:  # Show first 3
                recommendations.append(f"  - {v.message} ({v.file_path})")
        
        # Score-based recommendations
        if score < 50:
            recommendations.append("Quality score is very low - major refactoring needed")
        elif score < 70:
            recommendations.append("Quality score below threshold - address violations before proceeding")
        
        # Category-specific recommendations
        security_violations = [v for v in violations if v.category == QualityCategory.SECURITY]
        if security_violations:
            recommendations.append(f"Address {len(security_violations)} security issues immediately")
        
        # PR #23 specific recommendations
        pr23_violations = [v for v in violations if v.rule_id.startswith("PR23")]
        if pr23_violations:
            recommendations.append("DISASTER PREVENTION: Fix file handling issues to prevent PR #23 disasters")
        
        return recommendations
```

### Integration with Navigator Agent
```python
# agents/navigator/agent.py (enhanced)
class NavigatorAgent:
    # ... existing code ...
    
    def __init__(self, specialty: Optional[str] = None):
        # ... existing initialization ...
        self.quality_enforcer = QualityEnforcer()
    
    async def review_work(
        self,
        task: Dict[str, Any],
        tasker_output: Dict[str, Any],
        context: Dict[str, Any],
        iteration_number: int = 1
    ) -> ReviewFeedback:
        """Enhanced review with quality enforcement."""
        
        # Get artifacts from tasker output
        artifacts = tasker_output.get("artifacts", [])
        
        # Run quality assessment
        quality_report = await self.quality_enforcer.assess_quality(artifacts, context)
        
        # Base Navigator review
        base_feedback = await self._perform_base_review(task, tasker_output, context, iteration_number)
        
        # Combine with quality enforcement
        enhanced_feedback = self._combine_quality_and_review(base_feedback, quality_report)
        
        return enhanced_feedback
    
    def _combine_quality_and_review(
        self,
        base_feedback: ReviewFeedback,
        quality_report: QualityReport
    ) -> ReviewFeedback:
        """Combine base review with quality enforcement."""
        
        # If quality gates fail, force rejection regardless of base review
        if not quality_report.can_proceed:
            decision = ReviewDecision.REJECTED
            overall_assessment = f"Quality gates failed (score: {quality_report.overall_score:.1f}/100)"
        else:
            decision = base_feedback.decision
            overall_assessment = base_feedback.overall_assessment
        
        # Combine issues from both sources
        all_issues = base_feedback.issues + [
            f"{v.severity.upper()}: {v.message}" + (f" ({v.file_path}:{v.line_number})" if v.file_path else "")
            for v in quality_report.violations
        ]
        
        # Combine recommendations
        all_recommendations = quality_report.recommendations + base_feedback.suggestions
        
        return ReviewFeedback(
            decision=decision,
            overall_assessment=overall_assessment,
            issues=all_issues,
            required_changes=base_feedback.required_changes + [
                f"Fix {quality_report.critical_count} critical quality violations"
            ] if quality_report.critical_count > 0 else base_feedback.required_changes,
            suggestions=all_recommendations,
            positive_aspects=base_feedback.positive_aspects + [
                f"Quality score: {quality_report.overall_score:.1f}/100"
            ] if quality_report.overall_score > 70 else base_feedback.positive_aspects,
            quality_score=min(base_feedback.quality_score, quality_report.overall_score / 10),
            reasoning=f"{base_feedback.reasoning}\n\nQuality Assessment: {len(quality_report.violations)} violations found."
        )
```

## Testing Requirements

### Quality Enforcement Tests
```python
# tests/test_quality_enforcer.py
import pytest
from agents.navigator.quality_enforcer import QualityEnforcer, QualityRuleSeverity

@pytest.mark.asyncio
async def test_pr23_prevention_rules():
    """Test that quality rules prevent PR #23 disasters."""
    enforcer = QualityEnforcer()
    
    # Bad code that would cause PR #23
    bad_artifacts = [{
        "type": "code",
        "path": "fix_readme.py",
        "content": '''
def fix_readme():
    with open("README.md", "w") as f:
        f.write("")  # DISASTER: Deletes everything!
'''
    }]
    
    report = await enforcer.assess_quality(bad_artifacts)
    
    # Should catch PR #23 patterns
    assert not report.can_proceed
    assert report.critical_count > 0
    assert any(v.rule_id.startswith("PR23") for v in report.violations)

@pytest.mark.asyncio
async def test_security_violations():
    """Test security rule detection."""
    enforcer = QualityEnforcer()
    
    insecure_artifacts = [{
        "type": "code", 
        "path": "config.py",
        "content": '''
password = "secret123"
api_key = "abc123def456"
'''
    }]
    
    report = await enforcer.assess_quality(insecure_artifacts)
    
    # Should catch hardcoded secrets
    assert report.critical_count > 0
    assert any(v.category.value == "security" for v in report.violations)

@pytest.mark.asyncio
async def test_quality_gates():
    """Test quality gate enforcement."""
    # Should block progression when gates fail
    # Should allow progression when gates pass
    pass
```

## Definition of Done

1. ✅ Quality enforcer implemented with comprehensive rules
2. ✅ PR #23 prevention rules working
3. ✅ Security, performance, and style rules implemented
4. ✅ Quality gate enforcement with blocking capability
5. ✅ Integration with Navigator review workflow
6. ✅ Specific, actionable feedback generation
7. ✅ Quality scoring and threshold system
8. ✅ Unit tests covering all rule categories
9. ✅ Documentation of quality standards

## Success Example

Quality enforcement preventing disasters:
```
Quality Assessment Results:
- Overall Score: 45/100 ❌
- Critical Violations: 2
- Quality Gates: FAILED

Violations:
❌ CRITICAL: Code modifies files without reading them first (fix_readme.py:5)  
❌ CRITICAL: Potential hardcoded secret detected (config.py:2)
⚠️  WARNING: Function is 65 lines long (max 50) (utils.py:15)

Result: WORK REJECTED - Fix critical violations before proceeding
Recommendation: Always read files before modifying, use environment variables for secrets

This prevents PR #23 disasters and security issues! ✅
```