# GitHub CLI Integration

This document describes the GitHub CLI integration for the multi-agent coding system.

## Overview

The GitHub integration uses the official GitHub CLI (`gh`) tool to provide reliable GitHub operations. This approach prevents disasters like PR #23 by ensuring files are always read before modification.

## Key Features

- **Disaster Prevention**: Always reads files before modifying them
- **Official GitHub CLI**: Uses `gh` CLI for reliable API interactions  
- **Comprehensive Error Handling**: Proper exception handling with detailed context
- **Production Ready**: Designed for production deployment with defensive programming

## Authentication Setup

### Prerequisites

1. GitHub CLI must be installed in the Docker environment (already included in Dockerfile)
2. Authentication must be configured

### Authentication Methods

#### Option 1: GitHub Token (Recommended for Production)
```bash
export GITHUB_TOKEN=your_personal_access_token
echo $GITHUB_TOKEN | gh auth login --with-token
```

#### Option 2: Interactive OAuth (Development)
```bash
gh auth login
# Follow interactive prompts
```

### Verify Authentication
```bash
gh auth status
```

## Configuration

The service is configured via environment variables in `.env`:

```env
GITHUB_TOKEN=your_github_token
GITHUB_OWNER=your_username_or_org
GITHUB_REPO=your_repository_name
```

## Usage

### Basic File Operations

```python
from services.github_service import create_github_service

# Create service instance
service = create_github_service("owner", "repo")

# Read file (critical for preventing disasters)
content = service.read_file("README.md")
if content:
    print(f"File exists with {len(content)} characters")
else:
    print("File does not exist")

# Check if file exists
exists = service.file_exists("src/main.py")
```

### Pull Request Operations

```python
# Create pull request
pr_url = service.create_pull_request(
    title="Fix: Critical bug in authentication",
    body="## Summary\n\nFixed the authentication bug...",
    head_branch="fix/auth-bug",
    base_branch="main",
    draft=False
)

if pr_url:
    print(f"Created PR: {pr_url}")
```

### Issue Operations

```python
# Comment on issue
success = service.create_issue_comment(
    issue_number=123,
    comment="🤖 Working on this issue..."
)

# Add labels to issue
success = service.add_issue_labels(
    issue_number=123,
    labels=["bug", "automated-fix"]
)
```

### Repository Operations

```python
# Get repository information
repo_info = service.get_repository_info()
if repo_info:
    print(f"Repository: {repo_info['name']}")
    print(f"Default branch: {repo_info['defaultBranch']}")

# Clone repository (if working locally)
success = service.clone_repository()
```

## Workflow Integration

### Automatic PR Creation

The workflow automatically creates pull requests using:

```python
from workflows.github_integration import create_pull_request_from_state

# Create PR from workflow state
success = await create_pull_request_from_state(state)
```

This function:
1. Creates a new branch for the issue
2. Generates comprehensive PR description
3. Creates pull request via GitHub CLI
4. Comments on the original issue
5. Adds appropriate labels

### Reading Repository Files

```python
from workflows.github_integration import read_repository_file

# Read file content safely
content = await read_repository_file("src/main.py", "main")
if content:
    # Safe to proceed with modifications
    pass
```

## Error Handling

The service provides comprehensive error handling:

```python
from services.github_service import GitHubCLIError

try:
    content = service.read_file("missing.txt")
except GitHubCLIError as e:
    print(f"GitHub operation failed: {e}")
    print(f"Return code: {e.returncode}")
    print(f"Command: {' '.join(e.command)}")
    print(f"Error output: {e.stderr}")
```

## Disaster Prevention

The key principle is **always read before modify**:

```python
# ❌ BAD: Modifying without reading
service.create_pull_request(...)  # Could overwrite files

# ✅ GOOD: Read first, then modify
content = service.read_file("README.md")
if content:
    # File exists, safe to modify
    new_content = content + "\n\nNew section"
    # ... proceed with changes
else:
    # File doesn't exist, handle appropriately
    print("File not found!")
```

This prevents disasters like PR #23 where files were deleted because the system didn't verify their existence.

## Testing

### Unit Tests

Run the GitHub service tests:

```bash
python -m pytest tests/test_github_cli_service.py -v
```

### Integration Tests

Run the GitHub integration tests:

```bash
python -m pytest tests/test_github_integration.py::TestGitHubServiceManagement -v
```

### Manual Testing

Test authentication and basic operations:

```bash
# Test authentication
gh auth status

# Test API access
gh api user

# Test repository access
gh repo view owner/repo
```

## Production Deployment

### Environment Variables

Ensure these are set in production:

```env
GITHUB_TOKEN=<production_token_with_repo_scope>
GITHUB_OWNER=<repository_owner>
GITHUB_REPO=<repository_name>
```

### Docker Configuration

The GitHub CLI is already installed in the Docker image. Just ensure authentication:

```dockerfile
# Already included in Dockerfile:
RUN apt-get update && apt-get install -y gh
```

### Health Checks

Verify the service is working:

```python
from workflows.github_integration import verify_repository_access

access_ok = await verify_repository_access()
if access_ok:
    print("✅ GitHub access verified")
else:
    print("❌ GitHub access failed")
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   ```
   Error: GitHub CLI not authenticated
   ```
   Solution: Run `gh auth login` or set `GITHUB_TOKEN`

2. **Permission Denied**
   ```
   Error: HTTP 403: Forbidden
   ```
   Solution: Ensure token has `repo` scope

3. **Rate Limiting**
   ```
   Error: API rate limit exceeded
   ```
   Solution: Wait or use authenticated token for higher limits

4. **File Not Found**
   ```
   Error: HTTP 404: Not Found
   ```
   This is expected for non-existent files. The service returns `None` for missing files.

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('services.github_service').setLevel(logging.DEBUG)
```

## Security Considerations

- Never commit tokens to version control
- Use environment variables for all secrets
- Ensure tokens have minimal required permissions
- Rotate tokens regularly
- Monitor for unauthorized usage

## Next Steps

This GitHub integration enables:
- Story 2.1: PM Agent (can read files to understand codebase)
- Story 2.2: Developer Agent (can create branches and PRs)
- Story 2.3: Tester Agent (can read test files and run tests)
- Future enhancements for multi-repository support