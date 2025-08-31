#!/usr/bin/env python3
"""
Demo script for GitHub poller functionality.

This demonstrates the simple GitHub issue polling system for environments
without public IP addresses for webhooks.
"""

import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.github_poller import create_github_poller
from services.poller_service import PollerService
from config import Settings


async def demo_github_poller():
    """Demonstrate GitHub polling functionality."""
    print("📡 GITHUB POLLER DEMO")
    print("=" * 50)
    print("Testing GitHub issue polling for no-public-IP environments")
    print()
    
    try:
        # Load configuration
        settings = Settings()
        print("✅ Configuration loaded")
        print(f"   Repository: {settings.github_owner}/{settings.github_repo}")
        print(f"   Poll interval: {settings.poll_interval_seconds} seconds")
        print(f"   Poller enabled: {settings.poller_enabled}")
        print()
        
        # Create GitHub poller directly
        print("🔧 Creating GitHub poller...")
        github_poller = create_github_poller(
            github_token=settings.github_token,
            github_owner=settings.github_owner,
            github_repo=settings.github_repo,
            poll_interval_seconds=10,  # Fast for demo
            state_file="demo_poller_state.json"
        )
        
        print("✅ GitHub poller created")
        print(f"   Status: {github_poller.get_status()}")
        print()
        
        # Show what the poller would do
        print("🎯 POLLER WORKFLOW:")
        print("1. Poll GitHub API every 10 seconds")
        print("2. Check for new issues in lipingtababa/liangxiao")
        print("3. Compare with last seen issue ID")
        print("4. Process any new issues found")
        print("5. Update state in demo_poller_state.json")
        print()
        
        # Test poller state management
        print("📊 Testing state management...")
        
        # Show initial state
        initial_state = github_poller.state
        print(f"Initial state: {json.dumps(initial_state, indent=2)}")
        
        # Simulate processing an issue
        github_poller.state["last_issue_id"] = 5
        github_poller.state["processed_issues"] = [1, 2, 3, 4, 5]
        github_poller._save_state()
        print("✅ State updated and saved")
        
        # Test PollerService wrapper
        print()
        print("🔧 Testing PollerService wrapper...")
        poller_service = PollerService(
            github_token=settings.github_token,
            github_owner=settings.github_owner,
            github_repo=settings.github_repo,
            poll_interval_seconds=10,
            poller_state_file="demo_service_state.json",
            poller_enabled=True
        )
        
        print("✅ PollerService created")
        print(f"   Healthy: {poller_service.is_healthy()}")
        print(f"   Status: {poller_service.get_status()}")
        print()
        
        print("⚡ WOULD START POLLING:")
        print("   → Poll lipingtababa/liangxiao every 10 seconds")
        print("   → Detect new issues automatically")
        print("   → Trigger Claude Code agent workflow")
        print("   → Create feature branches and PRs")
        print()
        
        print("📁 STATE FILES CREATED:")
        print("   → demo_poller_state.json (issue tracking)")
        print("   → workspaces/liangxiao/{issue_id}/ (when processing)")
        print()
        
        print("🎉 GitHub poller demo COMPLETED!")
        print("✅ Ready for production polling without webhooks!")
        
    except Exception as e:
        print(f"❌ Demo FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_github_poller())