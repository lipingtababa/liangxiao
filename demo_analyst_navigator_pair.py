#!/usr/bin/env python3
"""Demo script for Analyst-Navigator pair integration.

This script demonstrates the complete Analyst-Navigator pair workflow,
showing how requirements analysis is improved through iterative review.
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from agents.pairs.analyst_navigator_pair import AnalystNavigatorPair
from agents.navigator.requirements_reviewer import RequirementsReviewFeedback, RequirementsIssue
from agents.navigator.agent import ReviewDecision
from agents.analyst.models import TechnicalSpecification, RequirementSpec, CodebaseAnalysis

# Configure logging for demo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_analyst_navigator_pair():
    """Demonstrate Analyst-Navigator pair workflow."""
    print("🔬 Demo: Analyst-Navigator Pair Integration")
    print("=" * 60)
    
    # Create mock agents to simulate the workflow
    mock_analyst = AsyncMock()
    mock_navigator = AsyncMock()
    
    # Sample task and context (like the PR #23 scenario)
    sample_task = {
        "id": "analysis-pr23-prevention",
        "description": "Analyze requirements for README phrase removal",
        "type": "analysis"
    }
    
    sample_context = {
        "issue": {
            "number": 23,
            "title": "Remove phrase from README", 
            "body": "Remove '解释文化细节' from README.md",
            "labels": []
        },
        "repository": "test/repo"
    }
    
    # Mock analyst output - initially vague (like what caused PR #23)
    vague_analyst_output = {
        "success": True,
        "artifacts": [
            {
                "type": "requirements",
                "path": "analysis/requirements-23.md",
                "content": "Remove phrase from README file", # Too vague!
                "specification": {
                    "requirements": [
                        {
                            "id": "req-1",
                            "description": "Remove phrase from README",
                            "priority": "high",
                            "acceptance_criteria": ["Phrase is removed"],
                            "dependencies": [],
                            "category": "functional",
                            "source": "issue_analysis"
                        }
                    ]
                }
            }
        ],
        "summary": "Analyzed 1 requirements, 1 files, confidence 0.60",
        "iteration_info": {
            "iteration_number": 1,
            "incorporated_feedback": False,
            "had_guidance": False
        }
    }
    
    # Mock navigator feedback - catches vague requirements
    critical_feedback = RequirementsReviewFeedback(
        decision=ReviewDecision.NEEDS_CHANGES,
        overall_assessment="CRITICAL: Requirements are too vague and will cause PR #23 scenario",
        requirements_issues=[
            RequirementsIssue(
                category="clarity",
                severity="critical",
                location="requirement req-1",
                description="Which specific phrase needs to be removed? This vagueness led to PR #23 disaster",
                suggestion="Specify exact phrase '解释文化细节' and what to preserve"
            )
        ],
        missing_elements=["Specific phrase identification", "Preservation requirements"],
        completeness_score=3,
        clarity_score=2,
        testability_score=4,
        issues=[],
        required_changes=[
            "Identify specific phrase '解释文化细节'",
            "Add preservation requirements for other content",
            "Define measurable success criteria"
        ],
        suggestions=["Consider edge cases like multiple occurrences"],
        positive_aspects=["Correct file identified"],
        quality_score=3,
        correctness_score=4,
        reasoning="Requirements too vague - high risk of implementation disaster like PR #23",
        iteration_number=1,
        adjusted_strictness=1.0
    )
    
    # Mock improved analyst output after feedback
    improved_analyst_output = {
        "success": True,
        "artifacts": [
            {
                "type": "requirements",
                "path": "analysis/requirements-23.md",
                "content": "Remove ONLY the phrase '解释文化细节' from README.md, preserving all other content",
                "specification": {
                    "requirements": [
                        {
                            "id": "req-1", 
                            "description": "Remove specific phrase '解释文化细节' from README.md",
                            "priority": "high",
                            "acceptance_criteria": [
                                "Phrase '解释文化细节' is completely removed from README.md",
                                "All other content in README.md remains unchanged",
                                "File structure and formatting preserved"
                            ],
                            "dependencies": [],
                            "category": "functional",
                            "source": "issue_analysis_iteration_2"
                        }
                    ]
                }
            }
        ],
        "summary": "Analyzed 1 requirements, 1 files, confidence 0.95 (iteration 2)",
        "iteration_info": {
            "iteration_number": 2,
            "incorporated_feedback": True,
            "had_guidance": True
        }
    }
    
    # Mock navigator approval after improvement  
    approval_feedback = RequirementsReviewFeedback(
        decision=ReviewDecision.APPROVED,
        overall_assessment="Excellent improvement! Requirements are now clear and disaster-proof",
        requirements_issues=[],
        missing_elements=[],
        completeness_score=9,
        clarity_score=9,
        testability_score=9,
        issues=[],
        required_changes=[],
        suggestions=[],
        positive_aspects=[
            "Specific phrase clearly identified",
            "Preservation requirements explicit", 
            "Success criteria measurable",
            "Prevents PR #23 scenario"
        ],
        quality_score=9,
        correctness_score=9,
        reasoning="All Navigator concerns addressed - safe for implementation",
        iteration_number=2,
        adjusted_strictness=0.8
    )
    
    # Configure mock behaviors
    mock_analyst.execute.side_effect = [
        vague_analyst_output,
        improved_analyst_output
    ]
    
    mock_navigator.review.side_effect = [
        critical_feedback,
        approval_feedback
    ]
    
    # Create and run the pair
    print("\n🤝 Creating Analyst-Navigator Pair...")
    pair = AnalystNavigatorPair(
        analyst_agent=mock_analyst,
        navigator_agent=mock_navigator,
        max_iterations=3,
        navigator_strictness=1.0
    )
    
    print("\n📋 Executing Requirements Analysis...")
    print("Task: Analyze requirements for README phrase removal")
    print("Context: Issue #23 - Remove phrase from README")
    print("")
    
    # Execute the analysis
    result = await pair.execute_requirements_analysis(sample_task, sample_context)
    
    # Display results
    print("📊 ANALYSIS RESULTS")
    print("-" * 30)
    print(f"✅ Success: {result['success']}")
    print(f"🔄 Iterations: {result.get('pair_execution_data', {}).get('iterations', 'Unknown')}")
    print(f"📈 Quality Scores:")
    if 'quality_scores' in result:
        scores = result['quality_scores']
        print(f"   - Completeness: {scores.get('completeness', 'N/A')}/10")
        print(f"   - Clarity: {scores.get('clarity', 'N/A')}/10") 
        print(f"   - Testability: {scores.get('testability', 'N/A')}/10")
        print(f"   - Overall: {scores.get('overall', 'N/A')}/10")
    
    print(f"\n📝 Final Decision: {result.get('pair_execution_data', {}).get('navigator_approval', 'Unknown')}")
    
    print("\n🎯 DISASTER PREVENTION SUCCESS!")
    print("The Navigator caught the vague requirements that would have")
    print("caused a PR #23 scenario and guided the Analyst to create")
    print("clear, specific, implementable requirements.")
    
    print(f"\n📋 Analysis Summary:")
    print(result.get('analysis_summary', 'No summary available'))
    
    # Show the iteration improvement
    print(f"\n🔄 ITERATION COMPARISON:")
    print("Iteration 1 (REJECTED): 'Remove phrase from README'")
    print("  ❌ Too vague - which phrase?")
    print("  ❌ No preservation requirements")
    print("  ❌ Could delete entire file")
    print()
    print("Iteration 2 (APPROVED): 'Remove ONLY phrase \"解释文化细节\" from README.md'")
    print("  ✅ Specific phrase identified")
    print("  ✅ Preservation requirements clear")
    print("  ✅ Measurable success criteria")
    print("  ✅ Safe for implementation")
    
    print(f"\n🏆 PAIR METRICS:")
    metrics = pair.get_pair_metrics()
    print(f"   - Pair Type: {metrics.get('pair_type', 'Unknown')}")
    print(f"   - Specialization: {metrics.get('specialization', 'Unknown')}")
    print(f"   - Prevents Disasters: {metrics.get('prevents_disasters', 'Unknown')}")
    print(f"   - Quality Gates: {metrics.get('quality_gates', 'Unknown')}")
    print(f"   - Progressive Leniency: {metrics.get('progressive_leniency', 'Unknown')}")


if __name__ == "__main__":
    print("Starting Analyst-Navigator Pair Demo...")
    asyncio.run(demo_analyst_navigator_pair())
    print("\nDemo completed successfully! 🎉")