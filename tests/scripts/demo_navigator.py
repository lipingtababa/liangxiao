#!/usr/bin/env python3
"""
Demo script showing the Navigator Agent in action.

This demonstrates the key features of the Navigator Agent:
1. Progressive leniency (strict -> moderate -> lenient)
2. Specific, actionable feedback
3. Prevention of disasters like PR #23
4. Different review specialties
"""

import asyncio
import json
from agents.navigator import NavigatorAgent, ReviewDecision


async def demo_progressive_leniency():
    """Demonstrate progressive leniency algorithm."""
    print("🎯 DEMO: Progressive Leniency Algorithm")
    print("=" * 50)
    
    # Demonstrate the progressive leniency calculation without creating the full agent
    print("Progressive Leniency: How strictness decreases over iterations")
    print()
    
    # Test the strictness calculation (using the algorithm directly)
    for iteration in [1, 2, 3, 4]:
        if iteration == 1:
            multiplier = 1.0
        elif iteration == 2:
            multiplier = 0.8
        else:
            multiplier = 0.6
        
        strictness = 1.0 * multiplier
        
        # Quality threshold calculation
        if strictness >= 1.0:
            threshold = 9.0  # 90% quality required
        elif strictness >= 0.8:
            threshold = 7.5  # 75% quality required  
        else:
            threshold = 6.0  # 60% quality required
            
        print(f"Iteration {iteration}: Strictness={strictness:.1f}, Quality Threshold={threshold:.1f}/10")
        
        # Add description
        if iteration == 1:
            print("  → First iteration: Very strict (catches everything)")
        elif iteration == 2:
            print("  → Second iteration: Moderately strict (focus on important issues)")
        else:
            print("  → Final iterations: Lenient (only critical issues block)")
    
    print()


async def demo_pr_23_prevention():
    """Demonstrate how Navigator would prevent PR #23 disaster."""
    print("🚨 DEMO: PR #23 Disaster Prevention")
    print("=" * 50)
    print("Original Issue: 'Remove the phrase 解释文化细节 from README'")
    print("Developer's approach: DELETE ENTIRE FILE (!)")
    print()
    
    # Simulate the bad output that caused PR #23
    print("🔍 Navigator Agent Analysis:")
    print("   Input: README.md with 0 bytes (entire file deleted)")
    print("   Task: Remove specific phrase from README")
    print("   Expected: Modified README with only phrase removed")
    print()
    
    print("✅ Navigator would catch this disaster:")
    print("   📋 DECISION: NEEDS_CHANGES")
    print("   🚨 CRITICAL ISSUE: 'Entire file deleted instead of removing specific phrase'")
    print("   💡 SPECIFIC SUGGESTION: 'Read original file and remove ONLY 解释文化细节'") 
    print("   📊 QUALITY SCORE: 0/10 (Complete failure!)")
    print("   🎯 CORRECTNESS: 0/10 (Wrong approach entirely)")
    print("   ✨ REQUIRED CHANGES:")
    print("      - Restore all original README content")
    print("      - Remove ONLY the specified phrase")
    print("      - Preserve all formatting and structure")
    print()
    print("💪 Result: PR #23 disaster prevented!")
    print()


def demo_feedback_structure():
    """Demonstrate the structured feedback format."""
    print("📋 DEMO: Structured Feedback Format")
    print("=" * 50)
    
    # Show the structure of feedback
    from agents.navigator.agent import ReviewFeedback, CodeIssue
    
    sample_issue = CodeIssue(
        severity="critical",
        category="bug", 
        location="src/calculator.py:15",
        description="Division by zero not handled",
        suggestion="Add check: if b == 0: raise ValueError('Cannot divide by zero')"
    )
    
    sample_feedback = ReviewFeedback(
        decision=ReviewDecision.NEEDS_CHANGES,
        overall_assessment="Code has critical bug that needs immediate attention",
        issues=[sample_issue],
        required_changes=[
            "Add zero division check",
            "Add input validation"
        ],
        suggestions=[
            "Consider adding type hints",
            "Add unit tests for edge cases"
        ],
        positive_aspects=[
            "Function is well-named",
            "Code is readable"
        ],
        quality_score=3,
        completeness_score=7,
        correctness_score=2,
        reasoning="Critical bug prevents production use, but structure is good",
        iteration_number=1,
        adjusted_strictness=1.0
    )
    
    print("Sample Navigator Feedback:")
    print(json.dumps(sample_feedback.model_dump(), indent=2, default=str))
    print()


def demo_iteration_guidance():
    """Demonstrate iteration guidance for different iterations."""
    print("🧭 DEMO: Iteration Guidance System")  
    print("=" * 50)
    
    # Demo the guidance logic without requiring LLM
    print("Sample issues found in code review:")
    issues = [
        "🚨 CRITICAL: SQL injection vulnerability in auth.py:42",
        "⚠️  MAJOR: Race condition in concurrent access at utils.py:15", 
        "📝 MINOR: Missing docstring in main.py:8"
    ]
    
    for issue in issues:
        print(f"   {issue}")
    print()
    
    # Show how guidance changes across iterations
    guidance_by_iteration = {
        1: "Address ALL 3 issues found:\n      - Fix SQL injection vulnerability\n      - Fix race condition\n      - Add missing docstring\n    Pay special attention to critical and major issues.",
        
        2: "Address these 2 important issues:\n      - SQL injection vulnerability (critical)\n      - Race condition (major)\n    Try to address minor issues if time permits.",
        
        3: "FINAL ITERATION: Focus ONLY on 1 critical issue:\n      - SQL injection vulnerability\n    Minor issues will be ignored at this stage."
    }
    
    for iteration in [1, 2, 3]:
        print(f"🔄 Iteration {iteration} Guidance:")
        print(f"   {guidance_by_iteration[iteration]}")
        print()
    
    print("📈 Result: Progressive focus ensures quality while preventing infinite loops!")


async def main():
    """Run all demos."""
    print("🤖 Navigator Agent Demo")
    print("=" * 60)
    print("This demo shows how the Navigator Agent prevents disasters")
    print("like PR #23 and provides intelligent, progressive feedback.")
    print()
    
    await demo_progressive_leniency()
    await demo_pr_23_prevention()
    demo_feedback_structure() 
    demo_iteration_guidance()
    
    print("✨ Demo Complete!")
    print("The Navigator Agent is ready to prevent coding disasters!")


if __name__ == "__main__":
    asyncio.run(main())