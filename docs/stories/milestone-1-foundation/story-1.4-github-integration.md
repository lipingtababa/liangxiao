# Story 1.4: GitHub CLI Integration ✅ COMPLETED

## Story Details
- **ID**: 1.4
- **Title**: Create GitHub CLI Service Wrapper
- **Milestone**: Milestone 1 - Foundation & Basic Workflow
- **Points**: 5
- **Priority**: P1 (Essential)
- **Dependencies**: Stories 1.1-1.3 (Python setup, webhook, workflow)
- **Status**: ✅ COMPLETED - Implementation available at `services/orchestrator/services/github_service.py`

## Description

### Overview
Create a comprehensive GitHub service wrapper in Python that uses the GitHub CLI (`gh`) under the hood for all GitHub operations. This approach leverages the official GitHub CLI tool which handles authentication, rate limiting, and API changes automatically, while providing a clean Python interface.

### Why This Is Important
- Essential for reading existing code (prevents disasters like PR #23)
- Required for creating pull requests with our solutions
- Enables issue commenting for progress updates
- Foundation for all GitHub operations
- GitHub CLI handles authentication and API complexities automatically

### Context
The current TypeScript system has basic GitHub integration but often fails to read files properly before modifying them. Using GitHub CLI (`gh`) provides a more reliable, officially supported way to interact with GitHub that automatically handles authentication, rate limiting, and API changes.

## Acceptance Criteria

### Required
- [ ] GitHub CLI (`gh`) installed and configured in Docker environment
- [ ] Python GitHub service wrapper that uses `gh` CLI commands
- [ ] Authentication handled via GitHub CLI (token or OAuth)
- [ ] Read files from repository (with error handling for non-existent files)
- [ ] Create and update branches using `gh` commands
- [ ] Create pull requests with proper descriptions via `gh pr create`
- [ ] Post comments on issues using `gh issue comment`
- [ ] Add labels to issues via `gh issue edit`
- [ ] Get repository information using `gh repo view`
- [ ] Handle command failures gracefully with proper error parsing
- [ ] Comprehensive error handling and logging of CLI operations
- [ ] Installation documentation for GitHub CLI setup

## Technical Details

### GitHub CLI Installation and Setup

#### Docker Integration
```dockerfile
# Add to Dockerfile
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh
```

#### Authentication Setup
```bash
# Authentication via token (for production)
echo $GITHUB_TOKEN | gh auth login --with-token

# Or interactive OAuth (for development)
gh auth login
```

### GitHub Service Implementation
```python
# services/github_service.py
import subprocess
import json
import logging
import tempfile
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubCLIError(Exception):
    """Custom exception for GitHub CLI errors."""
    def __init__(self, message: str, returncode: int, stderr: str):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr

class GitHubService:
    """
    GitHub CLI service wrapper.
    
    Handles all GitHub operations using the GitHub CLI (`gh`) tool
    with proper error handling and logging.
    """
    
    def __init__(self, owner: str, repo_name: str):
        """
        Initialize GitHub service.
        
        Args:
            owner: Repository owner (user or org)
            repo_name: Repository name
        """
        self.owner = owner
        self.repo_name = repo_name
        self.repo_full_name = f"{owner}/{repo_name}"
        
        # Verify gh CLI is available and authenticated
        self._verify_gh_cli()
    
    def _verify_gh_cli(self):
        """Verify GitHub CLI is installed and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                raise GitHubCLIError(
                    "GitHub CLI not authenticated. Run 'gh auth login'",
                    result.returncode,
                    result.stderr
                )
            logger.info("GitHub CLI authentication verified")
        except FileNotFoundError:
            raise GitHubCLIError(
                "GitHub CLI not found. Install with: apt-get install gh",
                1,
                "gh command not found"
            )
    
    def _run_gh_command(
        self,
        args: List[str],
        capture_output: bool = True,
        check: bool = True,
        input_data: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        """Run a GitHub CLI command with error handling."""
        
        cmd = ["gh"] + args
        logger.debug(f"Running gh command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=check,
                input=input_data
            )
            
            if result.returncode != 0 and check:
                raise GitHubCLIError(
                    f"GitHub CLI command failed: {' '.join(cmd)}",
                    result.returncode,
                    result.stderr
                )
            
            return result
            
        except subprocess.CalledProcessError as e:
            raise GitHubCLIError(
                f"GitHub CLI command failed: {' '.join(cmd)}",
                e.returncode,
                e.stderr if hasattr(e, 'stderr') else str(e)
            )
    
    # File Operations
    
    def read_file(self, path: str, ref: str = "main") -> Optional[str]:
        """
        Read file content from repository using GitHub CLI.
        
        Args:
            path: File path in repository
            ref: Branch, tag, or commit SHA (default: main)
            
        Returns:
            File content as string, or None if not found
        """
        try:
            logger.info(f"Reading file: {path} from {ref}")
            
            # Use gh api to get file content
            result = self._run_gh_command([
                "api", "repos/{owner}/{repo}/contents/{path}".format(
                    owner=self.owner,
                    repo=self.repo_name,
                    path=path
                ),
                "--jq", ".content",
                "-H", "Accept: application/vnd.github.v3+json"
            ])
            
            if result.returncode == 0 and result.stdout.strip():
                # Decode base64 content
                import base64
                content_b64 = result.stdout.strip().replace('"', '')
                content = base64.b64decode(content_b64).decode('utf-8')
                logger.info(f"Successfully read {len(content)} characters from {path}")
                return content
            
            return None
            
        except GitHubCLIError as e:
            if "Not Found" in e.stderr:
                logger.warning(f"File not found: {path}")
                return None
            else:
                logger.error(f"Error reading file {path}: {e}")
                raise
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        draft: bool = False
    ) -> Optional[str]:
        """
        Create a pull request using GitHub CLI.
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch (default: main)
            draft: Whether to create as draft
            
        Returns:
            PR URL or None if failed
        """
        try:
            logger.info(f"Creating PR: {title} ({head_branch} -> {base_branch})")
            
            cmd = [
                "pr", "create",
                "--repo", self.repo_full_name,
                "--title", title,
                "--body", body,
                "--head", head_branch,
                "--base", base_branch
            ]
            
            if draft:
                cmd.append("--draft")
            
            result = self._run_gh_command(cmd)
            
            if result.returncode == 0 and result.stdout.strip():
                pr_url = result.stdout.strip()
                logger.info(f"Created PR: {pr_url}")
                return pr_url
            
            return None
            
        except GitHubCLIError as e:
            logger.error(f"Error creating PR: {e}")
            return None
    
    def create_issue_comment(self, issue_number: int, comment: str) -> bool:
        """
        Post a comment on an issue using GitHub CLI.
        
        Args:
            issue_number: Issue number
            comment: Comment text (supports markdown)
            
        Returns:
            True if successful
        """
        try:
            result = self._run_gh_command([
                "issue", "comment", str(issue_number),
                "--repo", self.repo_full_name,
                "--body", comment
            ])
            
            logger.info(f"Posted comment on issue #{issue_number}")
            return True
            
        except GitHubCLIError as e:
            logger.error(f"Error commenting on issue #{issue_number}: {e}")
            return False
        """
        Read file content from repository.
        
        Args:
            path: File path in repository
            ref: Branch, tag, or commit SHA (default: main)
            
        Returns:
            File content as string, or None if not found
        """
        try:
            logger.info(f"Reading file: {path} from {ref}")
            file_content = self.repo.get_contents(path, ref=ref)
            
            if file_content.encoding == "base64":
                content = base64.b64decode(file_content.content).decode('utf-8')
            else:
                content = file_content.content
                
            logger.info(f"Successfully read {len(content)} characters from {path}")
            return content
            
        except GithubException as e:
            if e.status == 404:
                logger.warning(f"File not found: {path}")
                return None
            else:
                logger.error(f"Error reading file {path}: {e}")
                raise
    
    def get_file_tree(self, path: str = "", ref: str = "main") -> List[str]:
        """
        Get list of files in directory.
        
        Args:
            path: Directory path (empty for root)
            ref: Branch reference
            
        Returns:
            List of file paths
        """
        try:
            contents = self.repo.get_contents(path, ref=ref)
            files = []
            
            for content in contents:
                if content.type == "file":
                    files.append(content.path)
                elif content.type == "dir":
                    # Recursively get files in subdirectory
                    files.extend(self.get_file_tree(content.path, ref))
                    
            return files
            
        except GithubException as e:
            logger.error(f"Error getting file tree at {path}: {e}")
            return []
    
    def file_exists(self, path: str, ref: str = "main") -> bool:
        """Check if file exists in repository."""
        return self.read_file(path, ref) is not None
    
    # Branch Operations
    
    def create_branch(self, branch_name: str, from_ref: str = "main") -> bool:
        """
        Create a new branch.
        
        Args:
            branch_name: Name for new branch
            from_ref: Source branch/commit (default: main)
            
        Returns:
            True if created successfully
        """
        try:
            logger.info(f"Creating branch: {branch_name} from {from_ref}")
            
            # Get source reference
            source = self.repo.get_branch(from_ref)
            
            # Create new branch
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source.commit.sha
            )
            
            logger.info(f"Branch {branch_name} created successfully")
            return True
            
        except GithubException as e:
            if e.status == 422:  # Branch already exists
                logger.warning(f"Branch {branch_name} already exists")
                return True
            else:
                logger.error(f"Error creating branch {branch_name}: {e}")
                return False
    
    def update_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: str,
        create: bool = True
    ) -> bool:
        """
        Update or create file in repository.
        
        Args:
            path: File path
            content: New file content
            message: Commit message
            branch: Target branch
            create: Whether to create if doesn't exist
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Updating file: {path} on branch {branch}")
            
            # Try to get existing file
            try:
                file = self.repo.get_contents(path, ref=branch)
                # Update existing file
                self.repo.update_file(
                    path=path,
                    message=message,
                    content=content,
                    sha=file.sha,
                    branch=branch
                )
                logger.info(f"Updated existing file: {path}")
                
            except GithubException as e:
                if e.status == 404 and create:
                    # Create new file
                    self.repo.create_file(
                        path=path,
                        message=message,
                        content=content,
                        branch=branch
                    )
                    logger.info(f"Created new file: {path}")
                else:
                    raise
                    
            return True
            
        except GithubException as e:
            logger.error(f"Error updating file {path}: {e}")
            return False
    
    def delete_file(self, path: str, message: str, branch: str) -> bool:
        """Delete file from repository."""
        try:
            file = self.repo.get_contents(path, ref=branch)
            self.repo.delete_file(
                path=path,
                message=message,
                sha=file.sha,
                branch=branch
            )
            logger.info(f"Deleted file: {path}")
            return True
            
        except GithubException as e:
            logger.error(f"Error deleting file {path}: {e}")
            return False
    
    # Pull Request Operations
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        draft: bool = False
    ) -> Optional[PullRequest]:
        """
        Create a pull request.
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch (default: main)
            draft: Whether to create as draft
            
        Returns:
            PullRequest object or None if failed
        """
        try:
            logger.info(f"Creating PR: {title} ({head_branch} -> {base_branch})")
            
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch,
                draft=draft
            )
            
            logger.info(f"Created PR #{pr.number}: {pr.html_url}")
            return pr
            
        except GithubException as e:
            logger.error(f"Error creating PR: {e}")
            return None
    
    def update_pull_request(
        self,
        pr_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None
    ) -> bool:
        """Update existing pull request."""
        try:
            pr = self.repo.get_pull(pr_number)
            
            if title:
                pr.edit(title=title)
            if body:
                pr.edit(body=body)
            if state:
                pr.edit(state=state)
                
            logger.info(f"Updated PR #{pr_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Error updating PR #{pr_number}: {e}")
            return False
    
    # Issue Operations
    
    def create_issue_comment(self, issue_number: int, comment: str) -> bool:
        """
        Post a comment on an issue.
        
        Args:
            issue_number: Issue number
            comment: Comment text (supports markdown)
            
        Returns:
            True if successful
        """
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_comment(comment)
            logger.info(f"Posted comment on issue #{issue_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Error commenting on issue #{issue_number}: {e}")
            return False
    
    def add_issue_labels(self, issue_number: int, labels: List[str]) -> bool:
        """Add labels to an issue."""
        try:
            issue = self.repo.get_issue(issue_number)
            issue.add_to_labels(*labels)
            logger.info(f"Added labels {labels} to issue #{issue_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Error adding labels to issue #{issue_number}: {e}")
            return False
    
    def get_issue(self, issue_number: int) -> Optional[Issue]:
        """Get issue object."""
        try:
            return self.repo.get_issue(issue_number)
        except GithubException as e:
            logger.error(f"Error getting issue #{issue_number}: {e}")
            return None
    
    # Rate Limiting
    
    def check_rate_limit(self) -> Dict[str, Any]:
        """Check current rate limit status."""
        rate_limit = self.github.get_rate_limit()
        core = rate_limit.core
        
        return {
            "limit": core.limit,
            "remaining": core.remaining,
            "reset_time": core.reset.isoformat(),
            "used": core.limit - core.remaining
        }
    
    def wait_for_rate_limit(self):
        """Wait if approaching rate limit."""
        rate_limit = self.check_rate_limit()
        
        if rate_limit["remaining"] < 10:
            reset_time = datetime.fromisoformat(rate_limit["reset_time"])
            wait_seconds = (reset_time - datetime.now()).total_seconds() + 10
            
            if wait_seconds > 0:
                logger.warning(f"Rate limit low, waiting {wait_seconds}s")
                time.sleep(wait_seconds)
    
    # Batch Operations
    
    def apply_file_changes(
        self,
        branch: str,
        changes: List[Dict[str, Any]],
        commit_message: str
    ) -> bool:
        """
        Apply multiple file changes in one commit.
        
        Args:
            branch: Target branch
            changes: List of dicts with 'path', 'content', 'action'
            commit_message: Commit message
            
        Returns:
            True if all changes applied successfully
        """
        success = True
        
        for change in changes:
            action = change.get("action", "update")
            path = change["path"]
            
            if action == "create" or action == "update":
                success &= self.update_file(
                    path=path,
                    content=change["content"],
                    message=commit_message,
                    branch=branch,
                    create=(action == "create")
                )
            elif action == "delete":
                success &= self.delete_file(
                    path=path,
                    message=commit_message,
                    branch=branch
                )
                
        return success
```

### Integration with Workflow
```python
# workflows/github_integration.py
from services.github_service import GitHubService
from config import settings

# Global GitHub service instance
github_service = GitHubService(
    token=settings.github_token,
    owner=settings.github_owner,
    repo_name=settings.github_repo
)

async def create_pr_node(state: IssueWorkflowState) -> IssueWorkflowState:
    """Create PR with all artifacts."""
    
    # Create branch
    branch_name = f"fix-issue-{state['issue_number']}"
    github_service.create_branch(branch_name)
    
    # Apply all file changes
    changes = []
    for artifact in state["artifacts"]:
        if artifact["type"] == "code":
            changes.append({
                "path": artifact["path"],
                "content": artifact["content"],
                "action": "create" if artifact.get("new") else "update"
            })
    
    # Commit changes
    github_service.apply_file_changes(
        branch=branch_name,
        changes=changes,
        commit_message=f"Fix issue #{state['issue_number']}: {state['issue_title']}"
    )
    
    # Create PR
    pr = github_service.create_pull_request(
        title=f"Fix: {state['issue_title']} (#{state['issue_number']})",
        body=generate_pr_description(state),
        head_branch=branch_name
    )
    
    if pr:
        state["pr_number"] = pr.number
        state["pr_url"] = pr.html_url
        
        # Comment on issue
        github_service.create_issue_comment(
            state["issue_number"],
            f"🤖 Created PR #{pr.number} to fix this issue"
        )
    
    return state
```

## Testing Requirements

### Unit Tests
```python
# tests/test_github_service.py
import pytest
from unittest.mock import Mock, patch
from services.github_service import GitHubService

def test_read_existing_file():
    """Test reading an existing file."""
    service = GitHubService("token", "owner", "repo")
    
    with patch.object(service.repo, 'get_contents') as mock_get:
        mock_get.return_value.content = base64.b64encode(b"file content")
        mock_get.return_value.encoding = "base64"
        
        content = service.read_file("README.md")
        assert content == "file content"

def test_read_missing_file():
    """Test reading a non-existent file returns None."""
    service = GitHubService("token", "owner", "repo")
    
    with patch.object(service.repo, 'get_contents') as mock_get:
        mock_get.side_effect = GithubException(404, "Not found")
        
        content = service.read_file("missing.md")
        assert content is None

def test_create_branch():
    """Test branch creation."""
    # Test successful creation
    # Test handling existing branch
    pass

def test_rate_limiting():
    """Test rate limit checking and waiting."""
    # Test rate limit check
    # Test waiting when limit low
    pass
```

### Integration Tests
```python
# tests/integration/test_github_integration.py
@pytest.mark.integration
async def test_full_pr_creation():
    """Test complete PR creation flow."""
    # Read file
    # Create branch
    # Update file
    # Create PR
    # Verify all steps
    pass
```

## Dependencies & Risks

### Prerequisites
- GitHub token with repo scope
- PyGithub library installed
- Understanding of Git concepts

### Risks
- **Rate limiting**: API calls might be throttled
- **Token permissions**: Insufficient permissions cause failures
- **Network issues**: API calls might timeout
- **Large files**: Base64 encoding might fail

### Mitigations
- Implement rate limit checking
- Validate token permissions on startup
- Add retry logic with exponential backoff
- Stream large files if needed

## Definition of Done

1. ✅ GitHubService class implemented
2. ✅ All required operations working
3. ✅ Comprehensive error handling
4. ✅ Rate limiting handled
5. ✅ File operations tested
6. ✅ PR creation working
7. ✅ Issue commenting working
8. ✅ Unit tests passing
9. ✅ Integration with workflow

## Implementation Notes for AI Agents

### DO
- Always check if file exists before updating
- Use try/except for all GitHub operations
- Log all operations for debugging
- Handle 404 errors gracefully
- Check rate limits periodically

### DON'T
- Don't assume files exist
- Don't ignore API errors
- Don't make unnecessary API calls
- Don't hardcode branch names
- Don't skip error handling

### Common Pitfalls to Avoid
1. Not handling missing files (causes crashes)
2. Not checking rate limits (causes throttling)
3. Assuming main branch (might be master)
4. Not encoding file content properly
5. Creating duplicate branches

## Success Example

Proper file reading prevents disasters:
```python
# Current system (TypeScript): Doesn't read file, deletes everything ❌

# New system (Python):
content = github_service.read_file("README.md")
if content:
    # Make targeted change
    new_content = content.replace("unwanted phrase", "")
    github_service.update_file("README.md", new_content, "Remove phrase", branch)
else:
    logger.error("README.md not found!")
# Result: Targeted change, not wholesale deletion ✅
```

## Next Story
Once this story is complete, proceed to [Milestone 2: PM Agent Stories](../milestone-2-pm-agent/story-2.1-pm-core.md)