#!/usr/bin/env python3
"""
Demo of the new Git-integrated development workflow.

This demonstrates how the Developer Agent now works directly in Git repositories
instead of generating artifacts.
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from core.workspace_manager import WorkspaceManager
from services.github_service import GitHubService
from agents.developer.agent import DeveloperAgent


async def demo_git_workflow():
    """Demonstrate the Git-integrated development workflow."""
    print("🚀 GIT-INTEGRATED DEVELOPMENT WORKFLOW DEMO")
    print("=" * 70)
    print("This demo shows how SyntheticCodingTeam now works like a real developer:")
    print("• Clones repositories to organized workspaces")
    print("• Creates feature branches for each issue")
    print("• Modifies files directly in the Git repository")
    print("• Commits changes with proper Git workflow")
    print()
    
    try:
        # Create workspace manager
        workspace_manager = WorkspaceManager("demo_workspaces")
        print("✅ Workspace manager created")
        
        # Create GitHub service
        github_service = GitHubService(
            owner="mycompany",
            repo_name="myproject", 
            workspace_manager=workspace_manager
        )
        print("✅ GitHub service created with workspace support")
        
        # Create Developer agent with GitHub integration
        developer = DeveloperAgent(
            model="gpt-5",
            temperature=0.2,
            github_service=github_service
        )
        print("✅ Developer agent created with Git integration")
        
        # Demo workspace setup for different issue types
        test_cases = [
            {
                "issue_id": 123,
                "issue_data": {
                    "number": 123,
                    "title": "Add user authentication",
                    "body": "We need to implement user login and registration"
                },
                "description": "GitHub Issue #123"
            },
            {
                "issue_id": "SOT-456", 
                "issue_data": {
                    "title": "Fix security vulnerability",
                    "body": "Address SQL injection in user queries",
                    "ticket_type": "security"
                },
                "description": "Jira Ticket SOT-456"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📋 PROCESSING: {test_case['description']}")
            print("-" * 50)
            
            # Setup workspace
            workspace = github_service.setup_workspace(
                test_case["issue_id"], 
                test_case["issue_data"]
            )
            print(f"  ✅ Workspace created: {workspace.workspace_path}")
            
            # Show expected workspace structure
            issue_str = str(test_case["issue_id"])
            print(f"  📁 Structure:")
            print(f"    workspaces/myproject/{issue_str}/")
            print(f"    ├── myproject/              # ← Developer works HERE")
            print(f"    │   ├── .git/              # Git repository") 
            print(f"    │   ├── src/               # Source code")
            print(f"    │   └── [repo files]       # All project files")
            print(f"    └── .SyntheticCodingTeam/   # SCT metadata only")
            print(f"        ├── issue.json         # Issue details")
            print(f"        ├── workflow.json      # Git branch info")
            print(f"        ├── iterations/        # Review iterations") 
            print(f"        └── logs/              # Process logs")
            print(f"        # NOTE: No more artifacts/ - code goes in Git!")
            
            # Test file operations
            print(f"\n  🔧 Testing file operations:")
            
            # Write test file
            test_content = f"""# {test_case['description']} Implementation
def solve_issue():
    '''Implementation for {test_case['issue_data']['title']}'''
    return "Feature implemented"
"""
            write_success = github_service.write_file_to_workspace(
                f"src/issue_{issue_str}.py", 
                test_content
            )
            print(f"    {'✅' if write_success else '❌'} File written to workspace")
            
            # Read file back  
            read_content = github_service.read_file_from_workspace(f"src/issue_{issue_str}.py")
            read_success = read_content is not None and "solve_issue" in read_content
            print(f"    {'✅' if read_success else '❌'} File read from workspace")
            
            # Show workflow state
            workflow_state = workspace.load_workflow_state()
            if workflow_state:
                print(f"    📊 Workflow state loaded: {len(workflow_state)} keys")
        
        print(f"\n🎯 KEY DIFFERENCES FROM OLD SYSTEM:")
        print("❌ OLD: Developer creates CodeArtifact objects")
        print("✅ NEW: Developer modifies files directly in Git repository")
        print()
        print("❌ OLD: Artifacts stored in .SyntheticCodingTeam/artifacts/")
        print("✅ NEW: Code changes committed to Git feature branch")
        print()
        print("❌ OLD: Navigator reviews artifact content")
        print("✅ NEW: Navigator reviews actual Git diff")
        print()
        print("❌ OLD: Manual file creation for PR")
        print("✅ NEW: Git push + PR creation from feature branch")
        
        print(f"\n🚀 BENEFITS OF GIT-INTEGRATED WORKFLOW:")
        print("✅ Real version control history")
        print("✅ Proper branching strategy")
        print("✅ Navigator reviews actual changes")
        print("✅ Clean integration with GitHub PRs")
        print("✅ Developer works like a human developer")
        print("✅ Better disaster prevention through Git safeguards")
        
        print(f"\n🎉 Git-integrated workflow demo SUCCESSFUL!")
        
    except Exception as e:
        print(f"❌ Demo FAILED: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        try:
            if Path(temp_workspace).exists():
                shutil.rmtree(temp_workspace)
            if Path(temp_repo).exists():
                shutil.rmtree(temp_repo)
            print("🧹 Demo cleanup completed")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(demo_git_workflow())