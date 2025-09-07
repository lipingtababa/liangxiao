#!/usr/bin/env python3
"""Start SCT to process issue #21 from liangxiao repository.

This script configures the Synthetic Coding Team to monitor and process
issue #21: "remove '解释文化细节' from readme" from the liangxiao repository.

⚠️ OUTDATED: This script uses the removed poller service. The poller has been 
moved to a separate repository. Use the main SCT webhook endpoint instead.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

async def start_sct_for_issue_21():
    """Configure and start SCT to process issue #21."""
    
    print("🤖 Starting Synthetic Coding Team for Issue #21")
    print("=" * 60)
    
    # Set required environment variables
    required_env = {
        "OPENAI_API_KEY": "OpenAI API key for AI agents",
        "GITHUB_PERSONAL_ACCESS_TOKEN": "GitHub token (already configured)",
        "GITHUB_WEBHOOK_SECRET": "Webhook secret for security"
    }
    
    print("🔍 Checking environment configuration:")
    missing_vars = []
    
    for var, description in required_env.items():
        if os.getenv(var):
            print(f"   ✅ {var}: Configured")
        else:
            print(f"   ❌ {var}: Missing - {description}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("\nTo fix this, run:")
        for var in missing_vars:
            if var == "OPENAI_API_KEY":
                print(f'   export {var}="your-openai-key-here"')
            elif var == "GITHUB_WEBHOOK_SECRET":
                print(f'   export {var}="your-webhook-secret-here"')
        print()
    
    # Configure for liangxiao repository
    os.environ["GITHUB_OWNER"] = "lipingtababa"
    os.environ["GITHUB_REPO"] = "liangxiao"
    
    print("📋 Target Configuration:")
    print(f"   Repository: {os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}")
    print(f"   Issue: #21 - Remove '解释文化细节' from readme")
    print(f"   URL: https://github.com/lipingtababa/liangxiao/issues/21")
    print()
    
    if missing_vars:
        print("❌ Cannot start SCT without required environment variables")
        return False
    
    try:
        print("🚀 Starting SCT services...")
        
        # Import main services
        from services.poller_service import PollerService
        from workflows.orchestrator import WorkflowOrchestrator
        
        # Create poller service for the liangxiao repo
        poller = PollerService(
            github_token=os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
            github_owner="lipingtababa",
            github_repo="liangxiao",
            poll_interval_seconds=30,  # Check every 30 seconds
            poller_enabled=True
        )
        
        # Create workflow orchestrator
        orchestrator = WorkflowOrchestrator()
        
        print("✅ Services initialized")
        print()
        print("🔄 SCT will now:")
        print("   1. Monitor liangxiao repository for issue #21")
        print("   2. Detect when issue #21 needs processing")
        print("   3. Route to Analyst agent for requirements analysis")
        print("   4. Route to Tester agent for test creation")
        print("   5. Route to Developer agent for implementation")
        print("   6. Create pull request with changes")
        print()
        
        # Start the poller (in real usage, this would run continuously)
        print("🏁 Starting poller service...")
        await poller.start()
        
        # Keep running
        print("✅ SCT is now running and monitoring for issue #21")
        print("   Press Ctrl+C to stop")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping SCT...")
            await poller.stop()
            print("✅ SCT stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start SCT: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("🎯 Synthetic Coding Team - Issue #21 Processor")
    print()
    
    success = asyncio.run(start_sct_for_issue_21())
    
    if success:
        print("\n🎉 SCT processing completed!")
    else:
        print("\n❌ SCT failed to process issue #21")
    
    return success

if __name__ == "__main__":
    main()