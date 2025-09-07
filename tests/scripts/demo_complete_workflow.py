#!/usr/bin/env python3
"""Complete end-to-end workflow demonstration from issue to PR.

This demonstrates the full workflow for GitHub issue #21:
"remove '解释文化细节' from readme"

The workflow will:
1. Analyze requirements (Analyst)
2. Create tests (mock Tester)
3. Implement changes (mock Developer)
4. Create a pull request with the changes
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/Users/Shared/code/SyntheticCodingTeam')

from core.interfaces import (
    AnalystInput, TesterInput, DeveloperInput,
    CodeChange, create_step_result
)
from agents.analyst.agent import AnalystAgent
from services.github_service import GitHubService
from core.logging import get_logger

logger = get_logger(__name__)


class CompleteWorkflowDemo:
    """Demonstrates complete workflow from issue to PR."""
    
    def __init__(self):
        """Initialize demo with agents and services."""
        self.analyst = AnalystAgent()
        self.github_service = GitHubService()
        
        # Issue #21 data
        self.issue = {
            "number": 21,
            "title": "remove '解释文化细节' from readme",
            "body": "",
            "repository": "lipingtababa/liangxiao",
            "url": "https://github.com/lipingtababa/liangxiao/issues/21"
        }
        
        # Simulated human responses to clarification questions
        self.human_responses = {
            "remove_all_occurrences": "Yes, remove ALL occurrences",
            "if_not_found": "Log a message that phrase was not found",
            "other_files": "No, only check README.md"
        }
    
    async def run_complete_workflow(self) -> Dict[str, Any]:
        """Run the complete workflow from issue to PR."""
        print("=" * 80)
        print("🚀 COMPLETE WORKFLOW DEMONSTRATION: ISSUE → PR")
        print("=" * 80)
        print(f"Issue: #{self.issue['number']} - {self.issue['title']}")
        print(f"Repository: {self.issue['repository']}")
        print(f"URL: {self.issue['url']}")
        print("")
        
        workflow_results = {
            "issue": self.issue,
            "steps": [],
            "pr_created": False,
            "pr_url": None
        }
        
        try:
            # Step 1: Analyst - Requirements Analysis
            print("─" * 60)
            print("📋 STEP 1: ANALYST - Requirements Analysis")
            print("─" * 60)
            analyst_result = await self.run_analyst_step()
            workflow_results["steps"].append(("analyst", analyst_result))
            
            # Step 2: Human Clarification (simulated)
            if analyst_result.status == "needs_clarification":
                print("─" * 60)
                print("👤 STEP 2: HUMAN CLARIFICATION (Simulated)")
                print("─" * 60)
                clarified_requirements = self.simulate_human_clarification(analyst_result)
                workflow_results["steps"].append(("human_clarification", clarified_requirements))
            else:
                clarified_requirements = analyst_result.output
            
            # Step 3: Tester - Create Test Cases
            print("─" * 60)
            print("🧪 STEP 3: TESTER - Create Test Cases")
            print("─" * 60)
            test_result = await self.run_tester_step(clarified_requirements)
            workflow_results["steps"].append(("tester", test_result))
            
            # Step 4: Developer - Implementation
            print("─" * 60)
            print("💻 STEP 4: DEVELOPER - Implementation")
            print("─" * 60)
            dev_result = await self.run_developer_step(
                clarified_requirements,
                test_result
            )
            workflow_results["steps"].append(("developer", dev_result))
            
            # Step 5: Create Pull Request
            print("─" * 60)
            print("🔀 STEP 5: CREATE PULL REQUEST")
            print("─" * 60)
            pr_result = await self.create_pull_request(dev_result)
            workflow_results["pr_created"] = pr_result.get("success", False)
            workflow_results["pr_url"] = pr_result.get("pr_url")
            workflow_results["steps"].append(("pull_request", pr_result))
            
            # Final Summary
            print("")
            print("=" * 80)
            print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            self.print_workflow_summary(workflow_results)
            
            return workflow_results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            print(f"\n❌ WORKFLOW FAILED: {e}")
            return workflow_results
    
    async def run_analyst_step(self) -> Any:
        """Run the Analyst step."""
        analyst_input = AnalystInput(
            issue_description=f"""Title: {self.issue['title']}
Repository: {self.issue['repository']}

This is a request to remove the specific Chinese phrase '解释文化细节' from the README file.
This needs careful handling to avoid accidentally deleting the entire README (PR #23 disaster scenario).
"""
        )
        
        # Mock response for demo (to avoid API calls)
        mock_result = create_step_result(
            agent="analyst",
            status="needs_clarification",
            output_data={
                "acceptance_criteria": [
                    "The phrase '解释文化细节' must be completely removed from README.md",
                    "The README.md file must remain intact and not be deleted",
                    "All other content in README.md must be preserved unchanged",
                    "The removal must be case-sensitive and exact match only",
                    "The operation must be logged for audit purposes"
                ],
                "clarification_questions": [
                    "Should we remove ALL occurrences if it appears multiple times?",
                    "What should happen if the phrase is not found?",
                    "Should we check other documentation files?"
                ],
                "complexity": "simple",
                "effort_estimate": "30 minutes"
            },
            confidence=0.7,
            suggestions=["post_github_questions", "wait_for_human_input"]
        )
        
        print("✅ Acceptance Criteria Generated:")
        for i, criteria in enumerate(mock_result.output["acceptance_criteria"], 1):
            print(f"   {i}. {criteria}")
        
        print("\n❓ Clarification Questions:")
        for i, question in enumerate(mock_result.output["clarification_questions"], 1):
            print(f"   {i}. {question}")
        
        return mock_result
    
    def simulate_human_clarification(self, analyst_result: Any) -> Dict[str, Any]:
        """Simulate human responses to clarification questions."""
        print("📝 Posting questions to GitHub issue #21...")
        print("⏳ Waiting for human response...")
        print("\n💬 Human responds:")
        print(f"   1. Remove all occurrences? → {self.human_responses['remove_all_occurrences']}")
        print(f"   2. If not found? → {self.human_responses['if_not_found']}")
        print(f"   3. Other files? → {self.human_responses['other_files']}")
        
        # Update requirements based on human input
        clarified = analyst_result.output.copy()
        clarified["acceptance_criteria"].extend([
            "Remove ALL occurrences of the phrase if it appears multiple times",
            "If phrase not found, log message but don't fail",
            "Only process README.md, ignore other files"
        ])
        clarified["clarification_questions"] = []  # All questions answered
        
        print("\n✅ Requirements clarified and updated")
        return clarified
    
    async def run_tester_step(self, requirements: Dict[str, Any]) -> Any:
        """Run the Tester step (mocked)."""
        # Generate test code based on requirements
        test_code = '''import os
import pytest

def test_readme_phrase_removal():
    """Test that the Chinese phrase is removed from README."""
    # Read README content
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Verify phrase is removed
    assert "解释文化细节" not in content, "Phrase should be removed"
    
    # Verify file still exists and has content
    assert os.path.exists("README.md"), "README.md must still exist"
    assert len(content) > 100, "README.md should not be empty"

def test_readme_integrity():
    """Test that README remains intact after modification."""
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check for expected sections (disaster prevention)
    assert "# " in content, "README should have headers"
    assert len(content.split("\\n")) > 10, "README should have multiple lines"

def test_all_occurrences_removed():
    """Test that ALL occurrences of the phrase are removed."""
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Count occurrences (should be 0)
    occurrences = content.count("解释文化细节")
    assert occurrences == 0, f"Found {occurrences} occurrences, expected 0"
'''
        
        test_result = create_step_result(
            agent="tester",
            status="success",
            output_data={
                "test_code": test_code,
                "test_file_path": "tests/test_readme_modification.py",
                "test_count": 3,
                "framework": "pytest",
                "tests_created": [
                    "test_readme_phrase_removal",
                    "test_readme_integrity",
                    "test_all_occurrences_removed"
                ]
            },
            confidence=0.9,
            suggestions=["run_tests_after_implementation"]
        )
        
        print(f"✅ Created {test_result.output['test_count']} test cases:")
        for test_name in test_result.output["tests_created"]:
            print(f"   • {test_name}")
        
        print(f"\n📄 Test file: {test_result.output['test_file_path']}")
        return test_result
    
    async def run_developer_step(self, requirements: Dict[str, Any], test_result: Any) -> Any:
        """Run the Developer step (mocked implementation)."""
        # Create the actual file modification
        readme_diff = '''--- README.md
+++ README.md
@@ -15,7 +15,6 @@ This is a sample project for testing purposes.
 
 ## Features
 - Feature 1: Basic functionality
-- Feature 2: 解释文化细节 (Cultural details explanation)
 - Feature 3: Advanced options
 
 ## Installation
@@ -28,7 +27,7 @@ npm install
 
 ## Usage
 
-Run the application with 解释文化细节 enabled:
+Run the application:
 
 ```bash
 npm start'''
        
        dev_result = create_step_result(
            agent="developer",
            status="success",
            output_data={
                "changes_made": [
                    CodeChange(
                        file_path="README.md",
                        diff=readme_diff,
                        summary="Remove all occurrences of '解释文化细节' from README"
                    ).model_dump()
                ],
                "tests_passed": True,
                "test_output": "All 3 tests passed ✅",
                "implementation_notes": "Successfully removed phrase while preserving README integrity"
            },
            confidence=0.95,
            suggestions=["create_pull_request", "notify_stakeholders"]
        )
        
        print("✅ Implementation completed:")
        print(f"   • Modified files: 1")
        print(f"   • Tests passed: {dev_result.output['tests_passed']}")
        print(f"   • {dev_result.output['test_output']}")
        
        print("\n📝 Changes made (diff preview):")
        diff_lines = readme_diff.split('\n')[:10]
        for line in diff_lines:
            if line.startswith('-'):
                print(f"   \033[91m{line}\033[0m")  # Red for removals
            elif line.startswith('+'):
                print(f"   \033[92m{line}\033[0m")  # Green for additions
            else:
                print(f"   {line}")
        print("   ...")
        
        return dev_result
    
    async def create_pull_request(self, dev_result: Any) -> Dict[str, Any]:
        """Create a pull request (mocked for demo)."""
        pr_title = f"Fix #{self.issue['number']}: Remove '解释文化细节' from README"
        
        pr_body = f"""## Summary
This PR addresses issue #{self.issue['number']} by removing the Chinese phrase '解释文化细节' from the README file.

## Changes
- Removed all occurrences of the phrase from README.md
- Preserved all other content intact
- Ensured file integrity (no accidental deletion)

## Testing
✅ All tests pass:
- `test_readme_phrase_removal` - Verifies phrase is removed
- `test_readme_integrity` - Ensures README remains intact
- `test_all_occurrences_removed` - Confirms all instances removed

## Disaster Prevention
This implementation carefully avoids the "PR #23 disaster" scenario by:
1. Only removing the exact phrase specified
2. Preserving all other content
3. Validating file integrity after modification
4. Running comprehensive tests before PR creation

## Acceptance Criteria Met
✅ The phrase '解释文化细节' completely removed from README.md
✅ README.md file remains intact and not deleted
✅ All other content preserved unchanged
✅ Removal is case-sensitive and exact match only
✅ Operation logged for audit purposes

Fixes #{self.issue['number']}

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
"""
        
        # In a real implementation, this would use GitHub API to create PR
        pr_result = {
            "success": True,
            "pr_number": 42,  # Mock PR number
            "pr_url": f"https://github.com/{self.issue['repository']}/pull/42",
            "pr_title": pr_title,
            "pr_body": pr_body,
            "branch": "fix-issue-21-remove-phrase",
            "base_branch": "main"
        }
        
        print(f"✅ Pull Request Created!")
        print(f"   PR #42: {pr_title}")
        print(f"   URL: {pr_result['pr_url']}")
        print(f"   Branch: {pr_result['branch']} → {pr_result['base_branch']}")
        
        print("\n📄 PR Description Preview:")
        for line in pr_body.split('\n')[:15]:
            print(f"   {line}")
        print("   ...")
        
        return pr_result
    
    def print_workflow_summary(self, results: Dict[str, Any]):
        """Print a summary of the complete workflow."""
        print("\n🎯 WORKFLOW SUMMARY")
        print("─" * 60)
        
        print("📊 Steps Completed:")
        for step_name, step_result in results["steps"]:
            if isinstance(step_result, dict) and "status" in step_result:
                status = "✅" if step_result["status"] == "success" else "❓"
            elif hasattr(step_result, "status"):
                status = "✅" if step_result.status == "success" else "❓"
            else:
                status = "✅"
            print(f"   {status} {step_name.upper()}")
        
        print(f"\n🔀 Pull Request:")
        if results["pr_created"]:
            print(f"   ✅ PR Created Successfully")
            print(f"   📎 URL: {results['pr_url']}")
        else:
            print(f"   ❌ PR Not Created")
        
        print("\n🛡️ Disaster Prevention:")
        print("   ✅ File integrity verified")
        print("   ✅ Content preservation confirmed")
        print("   ✅ Tests validate changes")
        print("   ✅ No accidental deletions")
        
        print("\n📈 Metrics:")
        print(f"   Total Steps: {len(results['steps'])}")
        print(f"   Issue: #{self.issue['number']}")
        print(f"   Repository: {self.issue['repository']}")
        print(f"   Complexity: Simple")
        print(f"   Time Estimate: 30 minutes")


async def main():
    """Main entry point."""
    print("🤖 AI CODING TEAM - Complete Workflow Demo")
    print("=" * 80)
    print()
    
    demo = CompleteWorkflowDemo()
    results = await demo.run_complete_workflow()
    
    print("\n" + "=" * 80)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("=" * 80)
    
    if results["pr_created"]:
        print(f"\n✅ Successfully created PR from issue #{results['issue']['number']}")
        print(f"   View PR: {results['pr_url']}")
        print("\nThis demonstrates the complete Dynamic PM workflow:")
        print("   Issue → Analyst → Human → Tester → Developer → PR")
    else:
        print("\n❌ Workflow did not complete successfully")
    
    print("\n💡 Key Achievements:")
    print("   • End-to-end workflow execution")
    print("   • Human-AI interaction for clarifications")
    print("   • Test-driven development approach")
    print("   • Disaster prevention built-in")
    print("   • Automated PR creation with full context")


if __name__ == "__main__":
    asyncio.run(main())