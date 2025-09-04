#!/usr/bin/env python3
"""
Trigger Real Issue Processing in SyntheticCodingTeam

This script simulates a GitHub webhook to trigger actual issue processing.
"""

import requests
import json
import hashlib
import hmac
from datetime import datetime


def trigger_real_issue():
    """Send a real GitHub issue webhook to the running system."""
    
    print("🚀 TRIGGERING REAL ISSUE PROCESSING")
    print("=" * 50)
    
    # Real GitHub issue payload (simulated)
    issue_payload = {
        "action": "opened",
        "issue": {
            "number": 999,
            "title": "Fix authentication bug with special characters",
            "body": "Users cannot login when their password contains special characters like @#$%^&*(). The system should accept these characters but currently rejects them. This causes login failures for users with secure passwords.",
            "state": "open",
            "labels": [
                {"name": "bug", "color": "d73a4a"},
                {"name": "authentication", "color": "0366d6"}
            ],
            "assignee": None,
            "assignees": [],
            "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "html_url": "https://github.com/lipingtababa/liangxiao/issues/999",
            "id": 999,
            "url": "https://api.github.com/repos/lipingtababa/liangxiao/issues/999",
            "user": {"login": "developer", "id": 12345, "type": "User"},
            "locked": False
        },
        "repository": {
            "name": "liangxiao",
            "full_name": "lipingtababa/liangxiao",
            "private": False,
            "id": 12345,
            "html_url": "https://github.com/lipingtababa/liangxiao",
            "owner": {"login": "lipingtababa", "id": 12345, "type": "User"},
            "default_branch": "main"
        },
        "sender": {"login": "developer", "id": 12345, "type": "User"}
    }
    
    # Convert to JSON
    payload_json = json.dumps(issue_payload, separators=(',', ':'))
    
    # Create webhook signature (using the secret from .env)
    webhook_secret = "98jsdifem2ijTFE"  # From .env file
    signature = hmac.new(
        webhook_secret.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Headers for GitHub webhook
    headers = {
        'Content-Type': 'application/json',
        'X-GitHub-Event': 'issues',
        'X-GitHub-Delivery': f'12345678-1234-1234-1234-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
        'X-Hub-Signature-256': f'sha256={signature}',
        'User-Agent': 'GitHub-Hookshot/abc123'
    }
    
    print(f"📝 Issue Details:")
    print(f"   Title: {issue_payload['issue']['title']}")
    print(f"   Number: #{issue_payload['issue']['number']}")
    print(f"   Repository: {issue_payload['repository']['full_name']}")
    print(f"   Labels: {[label['name'] for label in issue_payload['issue']['labels']]}")
    print()
    
    try:
        print("📡 Sending webhook to SyntheticCodingTeam...")
        
        # Send the webhook
        response = requests.post(
            'http://localhost:8000/webhook/github',
            data=payload_json,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ WEBHOOK ACCEPTED!")
            print("🎉 SyntheticCodingTeam is now processing the issue!")
            print()
            
            try:
                result = response.json()
                print("📋 Processing Details:")
                for key, value in result.items():
                    print(f"   {key}: {value}")
            except:
                print("📋 Response received successfully")
            
            print()
            print("🔄 What happens next:")
            print("1. 🧠 PM Agent analyzes the issue")
            print("2. 📋 Task breakdown is created")
            print("3. 🤖 TaskPair workflows execute:")
            print("   - Analyst + Navigator (requirements)")
            print("   - Developer + Navigator (implementation)")
            print("   - Tester + Navigator (test creation)")
            print("4. 🛡️ Navigator reviews prevent disasters")
            print("5. 🔀 Pull request is created with fixes")
            print()
            print("📊 Monitor progress:")
            print("   - Check logs in the terminal where main.py is running")
            print("   - Watch for workflow state updates")
            print("   - Look for created workspaces in ./workspaces/")
            
        else:
            print(f"❌ WEBHOOK FAILED!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION FAILED!")
        print("Make sure SyntheticCodingTeam is running:")
        print("   python main.py")
        print("   or")
        print("   docker-compose up")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    trigger_real_issue()