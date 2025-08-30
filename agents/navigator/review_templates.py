"""Review templates and examples for Navigator Agent.

This module contains examples of good vs bad feedback, progressive leniency rules,
and templates for consistent review quality across different types of work.
"""

from typing import Dict, List, Literal, Any
from enum import Enum


class SeverityLevel(str, Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    MAJOR = "major"  
    MINOR = "minor"
    SUGGESTION = "suggestion"


class ReviewAction(str, Enum):
    """Actions to take based on severity and iteration."""
    MUST_FIX = "must_fix"
    SHOULD_FIX = "should_fix"
    MENTION = "mention"
    IGNORE = "ignore"


# Progressive leniency rules based on iteration number
PROGRESSIVE_LENIENCY_RULES = {
    1: {  # First iteration - be thorough and comprehensive
        SeverityLevel.CRITICAL: ReviewAction.MUST_FIX,
        SeverityLevel.MAJOR: ReviewAction.MUST_FIX,
        SeverityLevel.MINOR: ReviewAction.SHOULD_FIX,
        SeverityLevel.SUGGESTION: ReviewAction.MENTION
    },
    2: {  # Second iteration - focus on important issues
        SeverityLevel.CRITICAL: ReviewAction.MUST_FIX,
        SeverityLevel.MAJOR: ReviewAction.SHOULD_FIX,
        SeverityLevel.MINOR: ReviewAction.MENTION,
        SeverityLevel.SUGGESTION: ReviewAction.IGNORE
    },
    3: {  # Third+ iteration - only critical blockers
        SeverityLevel.CRITICAL: ReviewAction.MUST_FIX,
        SeverityLevel.MAJOR: ReviewAction.MENTION,
        SeverityLevel.MINOR: ReviewAction.IGNORE,
        SeverityLevel.SUGGESTION: ReviewAction.IGNORE
    }
}


def get_leniency_rules(iteration_number: int) -> Dict[SeverityLevel, ReviewAction]:
    """
    Get leniency rules for a given iteration number.
    
    Args:
        iteration_number: Current iteration (1-based)
        
    Returns:
        Dictionary mapping severity levels to review actions
    """
    if iteration_number <= 2:
        return PROGRESSIVE_LENIENCY_RULES[iteration_number]
    else:
        # Use iteration 3 rules for all subsequent iterations
        return PROGRESSIVE_LENIENCY_RULES[3]


def should_block_approval(
    issues: List[Dict[str, Any]], 
    iteration_number: int
) -> bool:
    """
    Determine if issues should block approval based on iteration number.
    
    Args:
        issues: List of issue dictionaries with 'severity' field
        iteration_number: Current iteration number
        
    Returns:
        True if any blocking issues exist, False otherwise
    """
    rules = get_leniency_rules(iteration_number)
    
    for issue in issues:
        severity = SeverityLevel(issue.get("severity", "minor"))
        action = rules.get(severity, ReviewAction.IGNORE)
        
        if action == ReviewAction.MUST_FIX:
            return True
    
    return False


# Code review examples demonstrating specific vs vague feedback
CODE_REVIEW_EXAMPLES = [
    {
        "issue_type": "Missing error handling",
        "bad_feedback": "Improve error handling",
        "good_feedback": "Add try/catch block around database call on lines 45-52. Handle ConnectionError and return appropriate HTTP 500 response with error message.",
        "why_better": "Specific location, exact error type, and clear solution provided"
    },
    {
        "issue_type": "SQL injection vulnerability", 
        "bad_feedback": "Security issue found",
        "good_feedback": "Line 23: Use parameterized queries instead of string concatenation. Replace f'SELECT * FROM users WHERE id = {user_id}' with cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
        "why_better": "Exact line number, specific vulnerability, and code example provided"
    },
    {
        "issue_type": "Performance problem",
        "bad_feedback": "Code is slow",
        "good_feedback": "Lines 67-89: Nested loop creates O(n²) complexity. Use a Set for user_ids lookup instead: user_set = set(user_ids); if user.id in user_set. This reduces complexity to O(n).",
        "why_better": "Specific lines, complexity analysis, and alternative solution with explanation"
    },
    {
        "issue_type": "Logic error",
        "bad_feedback": "Wrong logic",
        "good_feedback": "Line 15: Condition 'if x > 0' should be 'if x >= 0' to handle zero case. Current code incorrectly excludes zero values which are valid according to requirements.",
        "why_better": "Exact location, correct condition, and business context explained"
    },
    {
        "issue_type": "Missing validation",
        "bad_feedback": "Add validation",
        "good_feedback": "Function process_user() needs input validation. Add: 1) Check if email is valid format using regex, 2) Validate age is positive integer, 3) Ensure name is not empty string. Example: if not email or '@' not in email: raise ValueError('Invalid email')",
        "why_better": "Specific validation requirements with examples and error handling"
    },
    {
        "issue_type": "Incorrect file operation",
        "bad_feedback": "Fix file handling", 
        "good_feedback": "Lines 34-40: File is opened but never closed, causing resource leak. Use context manager: 'with open(filename, 'r') as f:' instead of 'f = open(filename, 'r')' to ensure automatic cleanup.",
        "why_better": "Identifies specific problem, explains consequences, provides exact solution"
    }
]


# PR #23 disaster prevention examples
DISASTER_PREVENTION_EXAMPLES = [
    {
        "scenario": "README deletion disaster (PR #23)",
        "task": "Remove '解释文化细节' from README",
        "bad_implementation": {
            "artifacts": [{
                "type": "code",
                "path": "README.md", 
                "content": ""  # Developer deleted everything!
            }]
        },
        "navigator_response": {
            "decision": "rejected",
            "issues": [{
                "severity": "critical",
                "category": "logic",
                "location": "README.md",
                "description": "Entire file content deleted instead of removing specific phrase",
                "suggestion": "Read the original file and remove ONLY '解释文化细节', preserving all other content"
            }],
            "required_changes": [
                "Restore all original README content",
                "Remove ONLY the phrase '解释文化细节'", 
                "Preserve all other text, formatting, and structure"
            ],
            "quality_score": 0,
            "reasoning": "Task was to remove specific phrase, not delete entire file. This would destroy all documentation."
        }
    },
    {
        "scenario": "Database migration disaster",
        "task": "Add new column to users table",
        "bad_implementation": {
            "artifacts": [{
                "type": "code",
                "path": "migrations/001_add_column.sql",
                "content": "DROP TABLE users; CREATE TABLE users (id INT, name VARCHAR(100), new_column VARCHAR(50));"
            }]
        },
        "navigator_response": {
            "decision": "rejected",
            "issues": [{
                "severity": "critical",
                "category": "logic", 
                "location": "migrations/001_add_column.sql",
                "description": "Migration drops entire table, destroying all existing data",
                "suggestion": "Use ALTER TABLE ADD COLUMN instead: ALTER TABLE users ADD COLUMN new_column VARCHAR(50);"
            }],
            "quality_score": 0,
            "reasoning": "Dropping table would cause data loss. Migration should only add column."
        }
    },
    {
        "scenario": "API endpoint deletion disaster",
        "task": "Fix authentication bug in /login endpoint",
        "bad_implementation": {
            "artifacts": [{
                "type": "code",
                "path": "routes/auth.py",
                "content": "# Removed buggy login endpoint"
            }]
        },
        "navigator_response": {
            "decision": "rejected", 
            "issues": [{
                "severity": "critical",
                "category": "logic",
                "location": "routes/auth.py",
                "description": "Login endpoint completely removed instead of fixing bug",
                "suggestion": "Fix the authentication logic bug while keeping endpoint functional"
            }],
            "quality_score": 0,
            "reasoning": "Removing endpoint breaks functionality. Bug should be fixed, not endpoint deleted."
        }
    }
]


# Requirements review templates
REQUIREMENTS_REVIEW_CRITERIA = {
    "completeness": {
        "description": "All aspects of the issue are covered",
        "check_items": [
            "Functional requirements identified",
            "Non-functional requirements considered", 
            "Edge cases and error scenarios included",
            "Acceptance criteria defined",
            "Dependencies and constraints noted"
        ]
    },
    "clarity": {
        "description": "Requirements are unambiguous and specific",
        "check_items": [
            "Clear, specific language used",
            "No ambiguous terms like 'better', 'improved', 'user-friendly'",
            "Measurable criteria defined",
            "Examples provided where helpful",
            "Technical terms properly defined"
        ]
    },
    "feasibility": {
        "description": "Requirements can actually be implemented",
        "check_items": [
            "Technical constraints considered",
            "Resource requirements reasonable",
            "Timeline realistic",
            "Dependencies available",
            "No conflicting requirements"
        ]
    },
    "testability": {
        "description": "Can verify when requirements are met",
        "check_items": [
            "Observable, measurable outcomes defined",
            "Test scenarios identifiable",
            "Success criteria clear",
            "Validation methods specified",
            "Error conditions testable"
        ]
    }
}


# Test review templates  
TEST_REVIEW_CRITERIA = {
    "coverage": {
        "description": "All important scenarios are tested",
        "check_items": [
            "Happy path scenarios covered",
            "Edge cases tested",
            "Error conditions handled",
            "Boundary values checked",
            "Integration points tested"
        ]
    },
    "validity": {
        "description": "Tests actually verify the right behavior",
        "check_items": [
            "Tests match requirements",
            "Assertions verify expected outcomes",
            "Test data is realistic",
            "Mock objects used appropriately",
            "Tests fail when they should"
        ]
    },
    "independence": {
        "description": "Tests don't depend on each other",
        "check_items": [
            "Tests can run in any order",
            "No shared mutable state",
            "Proper setup/teardown",
            "No dependencies between test methods",
            "Isolated test data"
        ]
    },
    "clarity": {
        "description": "Tests are clear and maintainable",
        "check_items": [
            "Test names describe what they test",
            "Arrange/Act/Assert pattern followed",
            "Test code is readable",
            "Helper methods used appropriately",
            "Comments explain complex scenarios"
        ]
    }
}


def get_review_criteria(review_type: Literal["code", "requirements", "tests"]) -> Dict[str, Any]:
    """
    Get review criteria for a specific type of review.
    
    Args:
        review_type: Type of review being conducted
        
    Returns:
        Dictionary of criteria and check items
    """
    if review_type == "requirements":
        return REQUIREMENTS_REVIEW_CRITERIA
    elif review_type == "tests":
        return TEST_REVIEW_CRITERIA
    else:
        # For code reviews, return general quality criteria
        return {
            "correctness": {
                "description": "Code solves the problem correctly",
                "check_items": [
                    "Logic implements requirements",
                    "Edge cases handled",
                    "Error conditions managed",
                    "Return values correct",
                    "Side effects controlled"
                ]
            },
            "security": {
                "description": "No security vulnerabilities",
                "check_items": [
                    "Input validation present",
                    "SQL injection prevented",
                    "XSS protection implemented",
                    "Authentication/authorization correct",
                    "Sensitive data protected"
                ]
            },
            "performance": {
                "description": "Efficient implementation",
                "check_items": [
                    "Algorithms have reasonable complexity",
                    "Database queries optimized",
                    "Resource usage controlled",
                    "Caching used appropriately",
                    "Memory leaks prevented"
                ]
            },
            "maintainability": {
                "description": "Code is readable and maintainable", 
                "check_items": [
                    "Clear variable names",
                    "Functions have single responsibility",
                    "Code is well-structured",
                    "Documentation is adequate",
                    "Best practices followed"
                ]
            }
        }


def format_feedback_example(example: Dict[str, Any]) -> str:
    """
    Format a feedback example for display or training purposes.
    
    Args:
        example: Example dictionary from CODE_REVIEW_EXAMPLES
        
    Returns:
        Formatted string showing good vs bad feedback
    """
    return f"""
Issue: {example['issue_type']}

❌ BAD: {example['bad_feedback']}
✅ GOOD: {example['good_feedback']}

Why the good example is better: {example['why_better']}
"""


def get_disaster_prevention_guidance() -> List[str]:
    """
    Get guidance for preventing common disasters.
    
    Returns:
        List of disaster prevention guidelines
    """
    return [
        "Always read existing files before modifying them",
        "Verify the scope of changes matches the task requirements",
        "Never delete entire files when asked to remove specific content",
        "Don't drop database tables when adding columns",
        "Don't remove functionality when fixing bugs", 
        "Preserve existing working code when making changes",
        "Test changes in isolation before applying broadly",
        "Consider the impact on existing users and systems",
        "Ask clarifying questions if task scope is unclear",
        "Implement the minimal change that addresses the requirement"
    ]


if __name__ == "__main__":
    # Example usage
    print("Progressive Leniency Rules:")
    for iteration in [1, 2, 3, 4]:
        rules = get_leniency_rules(iteration)
        print(f"Iteration {iteration}: {rules}")
    
    print("\nCode Review Examples:")
    for example in CODE_REVIEW_EXAMPLES:
        print(format_feedback_example(example))
    
    print("\nDisaster Prevention Guidance:")
    for guideline in get_disaster_prevention_guidance():
        print(f"- {guideline}")