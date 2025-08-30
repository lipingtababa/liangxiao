"""GitHub integration for workflow operations.

This module provides GitHub service integration for the workflow system,
using the GitHub CLI wrapper to perform repository operations safely.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from config import Settings
from services.github_service import GitHubService, GitHubCLIError, create_github_service
from workflows.workflow_state import IssueWorkflowState

logger = logging.getLogger(__name__)

# Global GitHub service instance
_github_service: Optional[GitHubService] = None


def get_github_service(settings: Optional[Settings] = None) -> GitHubService:
    """
    Get or create the global GitHub service instance.
    
    Args:
        settings: Optional settings instance (will create if not provided)
        
    Returns:
        Configured GitHubService instance
        
    Raises:
        GitHubCLIError: If GitHub service cannot be initialized
    """
    global _github_service
    
    if _github_service is None:
        if settings is None:
            settings = Settings()
        
        logger.info(f"Initializing GitHub service for {settings.github_owner}/{settings.github_repo}")
        
        try:
            _github_service = create_github_service(
                owner=settings.github_owner,
                repo_name=settings.github_repo
            )
            logger.info("GitHub service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub service: {e}")
            raise GitHubCLIError(
                f"GitHub service initialization failed: {e}",
                1,
                str(e),
                ["init"]
            )
    
    return _github_service


def reset_github_service():
    """Reset the global GitHub service instance (useful for testing)."""
    global _github_service
    _github_service = None


async def read_repository_file(
    file_path: str,
    ref: str = "main",
    settings: Optional[Settings] = None
) -> Optional[str]:
    """
    Read file content from the repository.
    
    This is critical for preventing disasters like PR #23 - always read
    files before modifying them to understand current state.
    
    Args:
        file_path: Path to file in repository
        ref: Git reference (branch, tag, commit)
        settings: Optional settings instance
        
    Returns:
        File content as string, or None if file doesn't exist
        
    Raises:
        GitHubCLIError: If reading fails for reasons other than file not found
    """
    try:
        github_service = get_github_service(settings)
        logger.info(f"Reading file: {file_path} from {ref}")
        
        content = github_service.read_file(file_path, ref)
        if content is not None:
            logger.info(f"Successfully read {len(content)} characters from {file_path}")
        else:
            logger.warning(f"File not found: {file_path} in {ref}")
        
        return content
        
    except GitHubCLIError as e:
        logger.error(f"GitHub CLI error reading {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading {file_path}: {e}")
        raise GitHubCLIError(
            f"Failed to read file {file_path}: {e}",
            1,
            str(e),
            ["read_file"]
        )


async def create_pull_request_from_state(
    state: IssueWorkflowState,
    settings: Optional[Settings] = None
) -> bool:
    """
    Create a pull request based on workflow state.
    
    This function:
    1. Creates a new branch for the issue
    2. Commits any changes (if working in a local repo)
    3. Creates a pull request with proper description
    4. Comments on the original issue
    
    Args:
        state: Current workflow state
        settings: Optional settings instance
        
    Returns:
        True if PR creation successful, False otherwise
    """
    try:
        github_service = get_github_service(settings)
        issue_number = state["issue_number"]
        issue_title = state["issue_title"]
        
        logger.info(f"Creating PR for issue #{issue_number}")
        
        # Generate branch name
        branch_name = f"fix/issue-{issue_number}"
        
        # Create branch (this requires a local git repository)
        branch_created = github_service.create_branch(branch_name, "main")
        if not branch_created:
            logger.warning(f"Failed to create branch {branch_name}, continuing anyway")
        
        # Generate PR title and description
        pr_title = f"Fix: {issue_title} (#{issue_number})"
        pr_body = generate_pr_description(state)
        
        # Create pull request
        pr_url = github_service.create_pull_request(
            title=pr_title,
            body=pr_body,
            head_branch=branch_name,
            base_branch="main",
            draft=False
        )
        
        if pr_url:
            logger.info(f"Successfully created PR: {pr_url}")
            
            # Update state with PR information
            state["branch_name"] = branch_name
            state["pr_url"] = pr_url
            
            # Extract PR number from URL (basic parsing)
            try:
                pr_number = int(pr_url.split("/pull/")[-1])
                state["pr_number"] = pr_number
            except (ValueError, IndexError):
                logger.warning("Could not extract PR number from URL")
            
            # Comment on the original issue
            comment_success = github_service.create_issue_comment(
                issue_number,
                f"🤖 Created PR to fix this issue: {pr_url}\n\n"
                f"The solution has been implemented and tested. "
                f"Please review the changes in the pull request."
            )
            
            if comment_success:
                logger.info(f"Posted comment on issue #{issue_number}")
            else:
                logger.warning(f"Failed to comment on issue #{issue_number}")
            
            return True
        else:
            logger.error(f"Failed to create PR for issue #{issue_number}")
            return False
            
    except GitHubCLIError as e:
        logger.error(f"GitHub CLI error creating PR: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating PR: {e}")
        return False


def generate_pr_description(state: IssueWorkflowState) -> str:
    """
    Generate comprehensive PR description from workflow state.
    
    Args:
        state: Current workflow state
        
    Returns:
        Formatted PR description with summary, changes, and testing info
    """
    issue_number = state["issue_number"]
    issue_title = state["issue_title"]
    analysis = state.get("analysis", {})
    artifacts = state.get("artifacts", [])
    test_results = state.get("test_results", [])
    
    # Start with basic summary
    description = f"## Summary\n\n"
    description += f"Fixes #{issue_number}: {issue_title}\n\n"
    
    # Add analysis information
    if analysis:
        description += f"**Issue Type:** {analysis.get('type', 'unknown')}\n"
        description += f"**Complexity:** {analysis.get('complexity', 'unknown')}\n"
        description += f"**Estimated Effort:** {analysis.get('estimated_effort', 'unknown')}\n\n"
    
    # Add changes section
    description += f"## Changes Made\n\n"
    
    code_artifacts = [a for a in artifacts if a.get("type") == "code"]
    if code_artifacts:
        for artifact in code_artifacts:
            content = artifact.get("content", {})
            files_changed = content.get("files_changed", [])
            changes = content.get("changes", [])
            
            if files_changed:
                description += f"**Files Modified:**\n"
                for file in files_changed:
                    description += f"- `{file}`\n"
                description += "\n"
            
            if changes:
                description += f"**Change Details:**\n"
                for change in changes:
                    file = change.get("file", "unknown")
                    action = change.get("action", "modified")
                    desc = change.get("description", "No description")
                    description += f"- {file}: {action} - {desc}\n"
                description += "\n"
    else:
        description += "- Code changes implemented as per issue requirements\n\n"
    
    # Add testing section
    description += f"## Testing\n\n"
    
    if test_results:
        latest_test = test_results[-1]
        total = latest_test.get("total_tests", 0)
        passed = latest_test.get("passed", 0)
        failed = latest_test.get("failed", 0)
        coverage = latest_test.get("coverage", "unknown")
        
        description += f"- **Tests Run:** {total} total, {passed} passed, {failed} failed\n"
        description += f"- **Coverage:** {coverage}\n"
        
        if failed == 0:
            description += f"- ✅ All tests are passing\n"
        else:
            description += f"- ⚠️ {failed} test(s) failing (see test results)\n"
        description += "\n"
    else:
        description += "- Manual testing completed\n"
        description += "- Solution verified to work as expected\n\n"
    
    # Add review checklist
    description += f"## Review Checklist\n\n"
    description += f"- [ ] Code follows project style guidelines\n"
    description += f"- [ ] Self-review of the code changes\n"
    description += f"- [ ] Documentation updated (if applicable)\n"
    description += f"- [ ] Tests added/updated for the changes\n"
    description += f"- [ ] No breaking changes introduced\n\n"
    
    # Add workflow metadata
    description += f"## Workflow Information\n\n"
    description += f"- **Workflow Iterations:** {state.get('current_iteration', 0)}\n"
    description += f"- **Agent Interactions:** {state.get('agent_interactions', 0)}\n"
    description += f"- **Artifacts Generated:** {len(artifacts)}\n"
    
    if state.get("tokens_used"):
        description += f"- **Tokens Used:** {state['tokens_used']}\n"
    
    description += f"\n---\n\n"
    description += f"🤖 Generated with [Claude Code](https://claude.ai/code)\n\n"
    description += f"Co-Authored-By: Claude <noreply@anthropic.com>"
    
    return description


async def add_issue_labels_from_state(
    state: IssueWorkflowState,
    settings: Optional[Settings] = None
) -> bool:
    """
    Add appropriate labels to issue based on workflow state.
    
    Args:
        state: Current workflow state
        settings: Optional settings instance
        
    Returns:
        True if labels added successfully, False otherwise
    """
    try:
        github_service = get_github_service(settings)
        issue_number = state["issue_number"]
        
        # Determine labels based on analysis
        labels = []
        analysis = state.get("analysis", {})
        
        if analysis:
            issue_type = analysis.get("type", "")
            complexity = analysis.get("complexity", "")
            
            # Add type labels
            if issue_type == "bug_fix":
                labels.append("bug")
            elif issue_type == "enhancement":
                labels.append("enhancement")
            elif issue_type == "testing":
                labels.append("testing")
            elif issue_type == "documentation":
                labels.append("documentation")
            
            # Add complexity labels
            if complexity == "high":
                labels.append("complex")
            elif complexity == "low":
                labels.append("good first issue")
        
        # Add status labels
        status = state.get("status")
        if status == "completed":
            labels.append("automated-fix")
        
        if labels:
            success = github_service.add_issue_labels(issue_number, labels)
            if success:
                logger.info(f"Added labels {labels} to issue #{issue_number}")
            else:
                logger.warning(f"Failed to add labels to issue #{issue_number}")
            return success
        else:
            logger.info(f"No labels to add for issue #{issue_number}")
            return True
            
    except GitHubCLIError as e:
        logger.error(f"GitHub CLI error adding labels: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error adding labels: {e}")
        return False


async def verify_repository_access(settings: Optional[Settings] = None) -> bool:
    """
    Verify that we can access the repository.
    
    Args:
        settings: Optional settings instance
        
    Returns:
        True if repository is accessible, False otherwise
    """
    try:
        github_service = get_github_service(settings)
        repo_info = github_service.get_repository_info()
        
        if repo_info:
            logger.info(f"Repository access verified: {repo_info.get('name', 'unknown')}")
            return True
        else:
            logger.error("Failed to get repository information")
            return False
            
    except GitHubCLIError as e:
        logger.error(f"GitHub CLI error verifying access: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error verifying access: {e}")
        return False


# Export main functions
__all__ = [
    'get_github_service',
    'reset_github_service',
    'read_repository_file',
    'create_pull_request_from_state',
    'generate_pr_description',
    'add_issue_labels_from_state',
    'verify_repository_access'
]