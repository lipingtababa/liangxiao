#!/usr/bin/env python3
"""
Demo script for the revolutionary TaskPair execution system.

This script demonstrates how TaskPair prevents disasters like PR #23 by 
implementing pair programming patterns between AI agents.
"""

import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.pairs.task_pair import TaskPair, create_task_pair
from agents.developer.agent import DeveloperAgent
from agents.navigator.agent import NavigatorAgent


# Configure logging to show the pair programming process
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def demo_basic_task_pair():
    """Demo basic TaskPair functionality."""
    print("🚀 DEMO: Basic TaskPair Execution")
    print("=" * 60)
    print("This demonstrates the revolutionary TaskPair system that prevents")
    print("disasters like PR #23 through pair programming patterns.\n")
    
    # Create a simple implementation task
    task = {
        "id": "demo-hello-world",
        "description": "Create a simple 'Hello World' function with proper error handling",
        "type": "implementation",
        "acceptance_criteria": [
            "Function should print 'Hello World'",
            "Function should handle invalid inputs gracefully",
            "Code should be clean and well-documented",
            "Function should return a success indicator"
        ]
    }
    
    # Create execution context
    context = {
        "issue": {
            "number": 123,
            "title": "Add Hello World function",
            "body": "We need a simple Hello World function for demonstration"
        },
        "repository": "demo/repository",
        "max_iterations": 3
    }
    
    print("📋 Task:", task["description"])
    print("🎯 Success criteria:", len(task["acceptance_criteria"]), "requirements")
    print("🔁 Max iterations:", context["max_iterations"])
    print()
    
    try:
        # Create TaskPair using factory function
        print("🏗️ Creating Developer + Navigator TaskPair...")
        task_pair = create_task_pair(
            tasker_agent=DeveloperAgent(model="gpt-4-turbo-preview", temperature=0.2),
            navigator_specialty="code_review",
            max_iterations=3,
            require_approval=True
        )
        
        print(f"✅ TaskPair created: {task_pair}")
        print(f"   - Tasker: {task_pair.tasker_type}")  
        print(f"   - Navigator: {task_pair.navigator_specialty}")
        print(f"   - Max iterations: {task_pair.max_iterations}")
        print()
        
        # Execute the task with pair programming
        print("🎯 Starting TaskPair execution...")
        print("   This will demonstrate the pair programming cycle:")
        print("   1. Developer implements the solution")
        print("   2. Navigator reviews and provides feedback") 
        print("   3. If not approved, Developer iterates based on feedback")
        print("   4. Continue until approved or max iterations reached")
        print()
        
        start_time = datetime.now()
        result = await task_pair.execute_task(task, context)
        duration = (datetime.now() - start_time).total_seconds()
        
        # Display results
        print("🏁 EXECUTION COMPLETED")
        print("=" * 40)
        print(f"📊 Result: {result.get_summary()}")
        print(f"⏱️ Duration: {duration:.2f}s")
        print(f"🔄 Iterations: {len(result.iterations)}")
        print(f"✅ Success: {result.success}")
        print(f"🎯 Quality Score: {result.final_quality_score:.1f}/10")
        print(f"🛡️ Disaster Prevention Score: {result.disaster_prevention_score:.1f}/100")
        
        if result.max_iterations_reached:
            print("⚠️ Max iterations reached")
        
        print()
        print("📝 ITERATION BREAKDOWN:")
        for i, iteration in enumerate(result.iterations, 1):
            decision = iteration.navigator_feedback.decision.value.upper()
            quality = iteration.navigator_feedback.quality_score
            issues = len(iteration.navigator_feedback.issues)
            
            print(f"   Iteration {i}: {decision} (Quality: {quality}/10, Issues: {issues})")
            
            if issues > 0:
                print(f"     🐛 Issues found:")
                for issue in iteration.navigator_feedback.issues:
                    print(f"       - {issue.severity}: {issue.description}")
            
            if iteration.navigator_feedback.positive_aspects:
                print(f"     ✅ Good aspects:")
                for aspect in iteration.navigator_feedback.positive_aspects:
                    print(f"       - {aspect}")
        
        print()
        if result.success:
            print("🎉 SUCCESS! The TaskPair system ensured high-quality output through")
            print("   collaborative review cycles. This is how we prevent disasters!")
            
            if result.final_output and result.final_output.get("artifacts"):
                print(f"📁 Generated {len(result.final_output['artifacts'])} artifacts")
        else:
            print("❌ FAILED: TaskPair could not produce acceptable results.")
            print(f"   Reason: {result.failure_reason}")
            print("   This demonstrates how the system prevents shipping bad code!")
        
        # Show TaskPair metrics
        print()
        print("📈 TASK PAIR METRICS:")
        metrics = task_pair.get_metrics()
        print(f"   - Total executions: {metrics['total_executions']}")
        print(f"   - Approval rate: {metrics['approval_rate']:.1%}")
        print(f"   - Average iterations: {metrics['average_iterations_per_task']:.1f}")
        
        return result
        
    except Exception as e:
        print(f"💥 Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def demo_disaster_prevention():
    """Demo how TaskPair prevents disasters like PR #23."""
    print("\n" + "🛡️ DISASTER PREVENTION DEMO" + "\n")
    print("=" * 60)
    print("This demo shows how TaskPair prevents disasters like PR #23")
    print("where an agent deleted an entire README when asked to remove one phrase.\n")
    
    # Create a task that could be dangerous if done wrong
    dangerous_task = {
        "id": "demo-dangerous-edit",
        "description": "Remove the phrase 'TODO: update this' from the README file, but preserve all other content",
        "type": "implementation", 
        "acceptance_criteria": [
            "Only the specific phrase 'TODO: update this' should be removed",
            "All other README content must be preserved exactly",
            "File structure and formatting should remain intact",
            "No other files should be modified"
        ]
    }
    
    context = {
        "issue": {
            "number": 456,
            "title": "Clean up TODO in README", 
            "body": "Please remove the 'TODO: update this' phrase from README"
        },
        "repository": "company/important-project"
    }
    
    print("⚠️ DANGEROUS TASK:", dangerous_task["description"])
    print("🎯 This is exactly the type of task that caused PR #23!")
    print("   Without proper review, an agent might:")
    print("   - Delete the entire README file")
    print("   - Remove the wrong content")  
    print("   - Corrupt the file structure")
    print()
    print("🛡️ TaskPair PROTECTION:")
    print("   1. Navigator reviews ALL changes before approval")
    print("   2. Multiple iterations ensure correctness")
    print("   3. Disaster prevention scoring tracks safety")
    print("   4. Progressive feedback guides improvement")
    print()
    
    # This would require actual file reading capabilities to demonstrate properly
    print("📝 NOTE: This demo would show the full disaster prevention cycle")
    print("   if connected to actual file operations. The key innovation is:")
    print("   - Navigator catches destructive operations")
    print("   - Iterative feedback prevents catastrophic mistakes") 
    print("   - Quality gates ensure safety before approval")
    print()
    print("🎉 Result: No more disasters like PR #23!")


async def main():
    """Run all TaskPair demos."""
    print("🌟 TASKPAIR SYSTEM DEMONSTRATION")
    print("=" * 80)
    print("Welcome to the revolutionary TaskPair execution system!")
    print("This system implements pair programming patterns with AI agents")
    print("to prevent disasters and ensure high-quality outputs.\n")
    
    try:
        # Demo 1: Basic functionality
        result = await demo_basic_task_pair()
        
        # Demo 2: Disaster prevention 
        await demo_disaster_prevention()
        
        print("\n" + "🏆 SUMMARY" + "\n")
        print("=" * 40)
        print("The TaskPair system represents a revolutionary approach to AI agent")
        print("collaboration that prevents disasters through:")
        print("✅ Pair programming patterns")
        print("✅ Iterative review and improvement")  
        print("✅ Progressive leniency to prevent infinite loops")
        print("✅ Comprehensive quality scoring")
        print("✅ Disaster prevention metrics")
        print("✅ Structured feedback incorporation")
        print()
        print("This is THE solution to prevent disasters like PR #23!")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())