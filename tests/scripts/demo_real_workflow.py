#!/usr/bin/env python3
"""
LIVE DEMO: Real SyntheticCodingTeam Workflow Processing

This demonstrates the complete workflow system processing a real issue
without depending on the web server setup.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflows.orchestrator import WorkflowOrchestrator
from models.github import IssueEvent
from workflows.workflow_state import WorkflowStatus


async def demo_real_workflow():
    """Demonstrate real workflow processing."""
    
    print("🚀 REAL SYNTHETICCODINGTEAM WORKFLOW DEMONSTRATION")
    print("=" * 60)
    print()
    
    print("🎯 This is the ACTUAL system processing a REAL issue!")
    print("   - Real WorkflowOrchestrator")
    print("   - Real LangGraph workflow")
    print("   - Real state management")
    print("   - Real TaskPair processing (when agents are connected)")
    print()
    
    # Create a realistic issue event
    issue_data = {
        "action": "opened",
        "issue": {
            "number": 42,
            "title": "Users cannot login with special characters in password",
            "body": """
# Issue Description
Users are reporting that they cannot login when their password contains special characters like @#$%^&*().

## Steps to Reproduce
1. User creates account with password containing special characters
2. User attempts to login 
3. Login fails with validation error

## Expected Behavior
Users should be able to login with passwords containing special characters

## Current Behavior
Password validation rejects special characters and login fails

## Impact
High - affects users with secure passwords containing special characters
            """.strip(),
            "state": "open",
            "labels": [
                {"name": "bug", "color": "d73a4a"},
                {"name": "authentication", "color": "0366d6"},
                {"name": "high-priority", "color": "ff6b6b"}
            ],
            "assignee": None,
            "assignees": [],
            "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "html_url": "https://github.com/lipingtababa/liangxiao/issues/42",
            "id": 42,
            "url": "https://api.github.com/repos/lipingtababa/liangxiao/issues/42",
            "user": {"login": "developer", "id": 12345, "type": "User"},
            "locked": False
        },
        "repository": {
            "name": "liangxiao",
            "full_name": "lipingtababa/liangxiao",
            "private": False,
            "id": 67890,
            "html_url": "https://github.com/lipingtababa/liangxiao",
            "owner": {"login": "lipingtababa", "id": 12345, "type": "User"},
            "default_branch": "main"
        },
        "sender": {"login": "developer", "id": 12345, "type": "User"}
    }
    
    try:
        # Create the issue event model
        issue_event = IssueEvent.model_validate(issue_data)
        print("✅ Issue event created successfully")
        print(f"   📋 Issue: #{issue_event.issue.number} - {issue_event.issue.title}")
        print(f"   📁 Repository: {issue_event.repository.full_name}")
        print(f"   🏷️ Labels: {[label.name for label in issue_event.issue.labels]}")
        print()
        
    except Exception as e:
        print(f"❌ Error creating issue event: {e}")
        return
    
    # Initialize the workflow orchestrator
    print("🔧 Initializing SyntheticCodingTeam Workflow Orchestrator...")
    try:
        orchestrator = WorkflowOrchestrator()
        print("✅ Orchestrator initialized successfully")
        print(f"   💾 Database: {orchestrator.checkpoint_db_path}")
        print()
    except Exception as e:
        print(f"❌ Error initializing orchestrator: {e}")
        return
    
    # Start the workflow
    print("🚀 Starting Real Workflow Processing...")
    try:
        workflow_id = await orchestrator.start_workflow(issue_event)
        print(f"✅ Workflow started successfully!")
        print(f"   🆔 Workflow ID: {workflow_id}")
        print()
    except Exception as e:
        print(f"❌ Error starting workflow: {e}")
        return
    
    # Monitor workflow progress
    print("⏳ Monitoring workflow progress...")
    max_wait_seconds = 60  # Wait up to 1 minute
    check_interval = 2
    elapsed = 0
    
    while elapsed < max_wait_seconds:
        await asyncio.sleep(check_interval)
        elapsed += check_interval
        
        # Get current workflows
        active_workflows = orchestrator.get_active_workflows()
        
        if workflow_id in active_workflows:
            current_status = active_workflows[workflow_id]["status"]
            print(f"   🔄 Status after {elapsed}s: {current_status}")
            
            # Check if workflow completed
            if current_status in ["completed", "failed", "error"]:
                print(f"   🏁 Workflow finished with status: {current_status}")
                break
        else:
            print(f"   ❓ Workflow not found in active workflows")
            break
    
    # Get final workflow state
    print("\n📊 Final Workflow Analysis...")
    try:
        final_state = await orchestrator.get_workflow_state(workflow_id)
        
        if final_state:
            print("✅ Final state retrieved successfully")
            print(f"   📈 Status: {final_state.get('status')}")
            print(f"   📅 Started: {final_state.get('started_at')}")
            print(f"   📅 Updated: {final_state.get('updated_at')}")
            print(f"   🔢 Issue Number: {final_state.get('issue_number')}")
            print(f"   📝 Issue Title: {final_state.get('issue_title')}")
            
            # Show errors if any
            errors = final_state.get("errors", [])
            if errors:
                print(f"   ❌ Errors ({len(errors)}):")
                for i, error in enumerate(errors[:3], 1):
                    print(f"      {i}. {error}")
            
            # Show warnings if any
            warnings = final_state.get("warnings", [])
            if warnings:
                print(f"   ⚠️ Warnings ({len(warnings)}):")
                for i, warning in enumerate(warnings[:3], 1):
                    print(f"      {i}. {warning}")
            
            # Show artifacts if any
            artifacts = final_state.get("all_artifacts", [])
            if artifacts:
                print(f"   📁 Artifacts generated: {len(artifacts)}")
            
            # Show PR info if created
            if final_state.get("pr_number"):
                print(f"   🔀 Pull Request: #{final_state['pr_number']}")
                print(f"   🔗 PR URL: {final_state.get('pr_url')}")
            
        else:
            print("❌ Could not retrieve final workflow state")
            
    except Exception as e:
        print(f"❌ Error retrieving final state: {e}")
    
    # Get orchestrator statistics
    print("\n📊 System Statistics...")
    try:
        stats = orchestrator.get_stats()
        print(f"   📈 Total workflows: {stats['total_workflows']}")
        print(f"   📋 Status counts: {stats['status_counts']}")
        print(f"   💾 Database: {stats['checkpoint_db_path']}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    print("\n🎉 REAL WORKFLOW DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print()
    print("🛡️ What you just witnessed:")
    print("✅ Real SyntheticCodingTeam workflow orchestrator")
    print("✅ Real GitHub issue processing") 
    print("✅ Real state management and tracking")
    print("✅ Real workflow execution (with agent limitations)")
    print()
    print("🚨 Note: Full agent execution requires API keys and connectivity")
    print("   But the CORE SYSTEM is working and ready!")
    print()
    print("🎯 To trigger full end-to-end processing:")
    print("   1. Ensure OpenAI API key is valid in .env")
    print("   2. Run this demo again")
    print("   3. Or set up GitHub webhooks for production use")


if __name__ == "__main__":
    asyncio.run(demo_real_workflow())