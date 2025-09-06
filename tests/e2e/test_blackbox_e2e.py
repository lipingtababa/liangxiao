#!/usr/bin/env python3
"""
BLACK BOX END-TO-END TEST for SyntheticCodingTeam

This test treats SCT as a complete black box:
1. Starts the SCT service (API server)
2. Sends a webhook callback (simulating GitHub)
3. Polls GitHub API to check if a PR was created
4. Validates the PR submission

No internal SCT components are imported or mocked.
"""

import asyncio
import subprocess
import time
import json
import requests
import sys
import os
from datetime import datetime, timedelta
from github import Github
from typing import Optional, Dict, Any


class SCTBlackBoxTest:
    """Black box E2E test for SyntheticCodingTeam."""
    
    def __init__(self, github_token: str, test_repo: str = "lipingtababa/liangxiao"):
        """
        Initialize the black box test.
        
        Args:
            github_token: GitHub personal access token
            test_repo: Repository to test with (format: owner/repo)
        """
        self.github_token = github_token
        self.github = Github(github_token)
        self.test_repo = test_repo
        self.sct_process = None
        self.port = 8001  # Use 8001 to avoid conflicts
        self.sct_url = f"http://localhost:{self.port}"
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "98jsdifem2ijTFE")  # From .env
        
    def start_sct_service(self) -> bool:
        """Start the SCT service as a subprocess."""
        print("🚀 Starting SyntheticCodingTeam service...")
        
        try:
            # Set required environment variables
            env = os.environ.copy()
            env["GITHUB_TOKEN"] = self.github_token
            env["GITHUB_PERSONAL_ACCESS_TOKEN"] = self.github_token
            env["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
            env["GITHUB_WEBHOOK_SECRET"] = self.webhook_secret
            env["GITHUB_OWNER"] = self.test_repo.split('/')[0]
            env["GITHUB_REPO"] = self.test_repo.split('/')[1]
            
            # Kill any existing process on the port
            subprocess.run(f"lsof -ti:{self.port} | xargs kill -9", shell=True, capture_output=True)
            time.sleep(1)
            
            # Start the SCT service using main.py with uvicorn
            self.sct_process = subprocess.Popen(
                ["python", "-m", "uvicorn", "main:app", "--port", str(self.port)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for service to be ready
            max_wait = 30  # seconds
            start_time = time.time()
            
            print(f"   Waiting for service at {self.sct_url}/health...")
            while time.time() - start_time < max_wait:
                try:
                    response = requests.get(f"{self.sct_url}/health")
                    if response.status_code == 200:
                        print(f"✅ SCT service started successfully at {self.sct_url}")
                        return True
                except Exception as e:
                    # Check if process died
                    if self.sct_process.poll() is not None:
                        stdout, stderr = self.sct_process.communicate()
                        print(f"❌ Service died. Exit code: {self.sct_process.returncode}")
                        print(f"STDERR: {stderr[:500]}")
                        return False
                    if time.time() - start_time > 5:
                        # Print progress every 5 seconds after initial wait
                        if int(time.time() - start_time) % 5 == 0:
                            print(f"   Still waiting... ({int(time.time() - start_time)}s)")
                time.sleep(1)
                
            print("❌ SCT service failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"❌ Error starting SCT service: {e}")
            return False
    
    def stop_sct_service(self):
        """Stop the SCT service."""
        if self.sct_process:
            print("🛑 Stopping SCT service...")
            self.sct_process.terminate()
            time.sleep(2)
            if self.sct_process.poll() is None:
                self.sct_process.kill()
            print("✅ SCT service stopped")
    
    def simulate_github_webhook(self, issue_number: int) -> bool:
        """
        Simulate a GitHub webhook for an issue.
        
        Args:
            issue_number: The issue number to simulate
            
        Returns:
            True if webhook was accepted, False otherwise
        """
        print(f"\n📡 Simulating GitHub webhook for issue #{issue_number}...")
        
        try:
            # Fetch the real issue from GitHub
            repo = self.github.get_repo(self.test_repo)
            issue = repo.get_issue(issue_number)
            
            # Build webhook payload (GitHub issue opened event)
            webhook_payload = {
                "action": "opened",
                "issue": {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body or "",
                    "state": issue.state,
                    "labels": [{"name": label.name, "color": "000000", "id": 1} for label in issue.labels],
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "html_url": issue.html_url,
                    "id": issue.id,
                    "url": f"https://api.github.com/repos/{repo.full_name}/issues/{issue.number}",
                    "locked": False,
                    "user": {
                        "login": issue.user.login,
                        "id": issue.user.id,
                        "type": "User",
                        "html_url": f"https://github.com/{issue.user.login}"
                    }
                },
                "repository": {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "private": repo.private,
                    "id": repo.id,
                    "html_url": repo.html_url,
                    "description": repo.description,
                    "default_branch": repo.default_branch,
                    "owner": {
                        "login": repo.owner.login,
                        "id": repo.owner.id,
                        "type": repo.owner.type,
                        "html_url": f"https://github.com/{repo.owner.login}"
                    }
                },
                "sender": {
                    "login": issue.user.login,
                    "id": issue.user.id,
                    "type": "User",
                    "html_url": f"https://github.com/{issue.user.login}"
                }
            }
            
            # Generate webhook signature (if needed)
            import hmac
            import hashlib
            payload_bytes = json.dumps(webhook_payload).encode('utf-8')
            signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # Send webhook to SCT
            import uuid
            headers = {
                "Content-Type": "application/json",
                "X-GitHub-Event": "issues",
                "X-GitHub-Delivery": str(uuid.uuid4()),
                "X-Hub-Signature-256": f"sha256={signature}"
            }
            
            response = requests.post(
                f"{self.sct_url}/api/webhook/github",  # Correct API path
                json=webhook_payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Webhook accepted by SCT (status: {response.status_code})")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Webhook rejected by SCT (status: {response.status_code})")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error simulating webhook: {e}")
            return False
    
    def poll_for_pr(self, issue_number: int, timeout_minutes: int = 5) -> Optional[Dict[str, Any]]:
        """
        Poll GitHub for a PR related to the issue.
        
        Args:
            issue_number: The issue number to check for PRs
            timeout_minutes: Maximum time to wait for PR
            
        Returns:
            PR details if found, None otherwise
        """
        print(f"\n🔍 Polling GitHub for PR related to issue #{issue_number}...")
        
        repo = self.github.get_repo(self.test_repo)
        start_time = datetime.now()
        timeout = timedelta(minutes=timeout_minutes)
        poll_interval = 10  # seconds
        
        # Remember existing PRs to detect new ones
        existing_prs = set()
        for pr in repo.get_pulls(state='all'):
            existing_prs.add(pr.number)
        
        while datetime.now() - start_time < timeout:
            try:
                # Check for new PRs
                for pr in repo.get_pulls(state='open'):
                    if pr.number not in existing_prs:
                        # Check if PR is related to our issue
                        if f"#{issue_number}" in pr.title or f"#{issue_number}" in (pr.body or ""):
                            print(f"✅ Found PR #{pr.number} related to issue #{issue_number}")
                            return {
                                "number": pr.number,
                                "title": pr.title,
                                "url": pr.html_url,
                                "branch": pr.head.ref,
                                "files_changed": pr.changed_files,
                                "additions": pr.additions,
                                "deletions": pr.deletions,
                                "created_at": pr.created_at
                            }
                
                elapsed = (datetime.now() - start_time).seconds
                remaining = (timeout_minutes * 60) - elapsed
                print(f"   ⏳ No PR yet... ({elapsed}s elapsed, {remaining}s remaining)")
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"   ⚠️ Error polling GitHub: {e}")
                time.sleep(poll_interval)
        
        print(f"❌ No PR found within {timeout_minutes} minutes")
        return None
    
    def validate_pr(self, pr_details: Dict[str, Any]) -> bool:
        """
        Validate that the PR meets quality standards.
        
        Args:
            pr_details: PR information from GitHub
            
        Returns:
            True if PR is valid, False otherwise
        """
        print(f"\n📊 Validating PR #{pr_details['number']}...")
        
        validations = []
        
        # Check PR was created
        if pr_details['number']:
            print(f"✅ PR exists: #{pr_details['number']}")
            validations.append(True)
        else:
            print(f"❌ No PR number")
            validations.append(False)
        
        # Check for reasonable changes (not a disaster)
        if pr_details['deletions'] > 100:
            print(f"❌ Too many deletions: {pr_details['deletions']} lines")
            print(f"   🚨 This could be a disaster like PR #23!")
            validations.append(False)
        else:
            print(f"✅ Reasonable deletions: {pr_details['deletions']} lines")
            validations.append(True)
        
        # Check that changes were made
        if pr_details['files_changed'] > 0:
            print(f"✅ Files changed: {pr_details['files_changed']}")
            validations.append(True)
        else:
            print(f"❌ No files changed")
            validations.append(False)
        
        # Overall validation
        is_valid = all(validations)
        
        if is_valid:
            print(f"\n✅✅✅ PR VALIDATION: PASSED")
            print(f"   PR #{pr_details['number']} meets all quality standards")
        else:
            print(f"\n❌❌❌ PR VALIDATION: FAILED")
            print(f"   PR #{pr_details['number']} has quality issues")
        
        return is_valid
    
    async def run_test(self, issue_number: int = 21) -> bool:
        """
        Run the complete black box E2E test.
        
        Args:
            issue_number: Issue number to test with
            
        Returns:
            True if test passed, False otherwise
        """
        print("=" * 60)
        print("🎯 BLACK BOX E2E TEST FOR SYNTHETICCODINGTEAM")
        print("=" * 60)
        print(f"Testing with issue #{issue_number} from {self.test_repo}")
        print("This test treats SCT as a complete black box")
        print()
        
        success = False
        
        try:
            # Step 1: Start SCT service
            if not self.start_sct_service():
                print("❌ Failed to start SCT service")
                return False
            
            # Give service time to fully initialize
            await asyncio.sleep(5)
            
            # Step 2: Send webhook
            if not self.simulate_github_webhook(issue_number):
                print("❌ Failed to send webhook to SCT")
                return False
            
            # Step 3: Poll for PR
            pr_details = self.poll_for_pr(issue_number, timeout_minutes=5)
            
            if pr_details:
                # Step 4: Validate PR
                success = self.validate_pr(pr_details)
                
                if success:
                    print(f"\n🎉 BLACK BOX TEST: SUCCESS!")
                    print(f"   1. ✅ SCT service started")
                    print(f"   2. ✅ Webhook processed") 
                    print(f"   3. ✅ PR #{pr_details['number']} created")
                    print(f"   4. ✅ PR validated (no disasters)")
                    print(f"\n   🔗 PR URL: {pr_details['url']}")
            else:
                print(f"\n⚠️ BLACK BOX TEST: NO PR CREATED")
                print(f"   SCT processed the webhook but did not create a PR")
                print(f"   This may indicate Navigator prevented risky changes")
                
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Always stop the service
            self.stop_sct_service()
        
        print("\n" + "=" * 60)
        print("📊 TEST COMPLETE")
        print("=" * 60)
        
        return success


async def main():
    """Main entry point for the black box test."""
    
    # Load credentials from .env file
    from pathlib import Path
    env_file = Path(".env")
    
    if env_file.exists():
        print("📄 Loading credentials from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        print("✅ Credentials loaded from .env")
    
    # Load GitHub token
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token:
        print("❌ No GitHub token found")
        print("   Check .env file for GITHUB_PERSONAL_ACCESS_TOKEN")
        return False
    
    # Check OpenAI key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Warning: No OPENAI_API_KEY found")
        print("   SCT may not function properly without it")
    
    # Get test repo from env or use default
    test_repo = os.getenv("GITHUB_OWNER", "lipingtababa") + "/" + os.getenv("GITHUB_REPO", "liangxiao")
    
    # Create and run test
    test = SCTBlackBoxTest(github_token, test_repo)
    success = await test.run_test(issue_number=21)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())