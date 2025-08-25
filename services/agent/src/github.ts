import { Octokit } from '@octokit/rest';
import { config } from './config';
import { logger } from '../shared/logger';
import { AgentResponse, IssueEvent } from '../shared/types';

const octokit = new Octokit({
  auth: config.github.token,
});

export class GitHubManager {
  async createComment(owner: string, repo: string, issueNumber: number, body: string) {
    try {
      await octokit.issues.createComment({
        owner,
        repo,
        issue_number: issueNumber,
        body
      });
      logger.info(`Posted comment to issue #${issueNumber} in ${owner}/${repo}`);
    } catch (error) {
      logger.error('Failed to create comment:', error);
      throw error;
    }
  }

  async createPullRequest(issue: IssueEvent, solution: AgentResponse) {
    try {
      const branchName = `ai-fix-issue-${issue.issue.number}`;
      const { owner, name: repo } = issue.repository;
      
      // Get default branch
      const { data: repoData } = await octokit.repos.get({
        owner,
        repo,
      });
      const baseBranch = repoData.default_branch;

      // Get base branch SHA
      const { data: refData } = await octokit.git.getRef({
        owner,
        repo,
        ref: `heads/${baseBranch}`,
      });
      const baseSha = refData.object.sha;

      // Create new branch
      await octokit.git.createRef({
        owner,
        repo,
        ref: `refs/heads/${branchName}`,
        sha: baseSha,
      });

      logger.info(`Created branch: ${branchName} in ${owner}/${repo}`);

      // Get base tree
      const { data: baseTree } = await octokit.git.getTree({
        owner,
        repo,
        tree_sha: baseSha,
      });

      // Create blobs for each file
      const treeItems = [];
      
      for (const file of solution.files) {
        const { data: blob } = await octokit.git.createBlob({
          owner,
          repo,
          content: Buffer.from(file.content).toString('base64'),
          encoding: 'base64',
        });
        
        treeItems.push({
          path: file.path,
          mode: '100644' as const,
          type: 'blob' as const,
          sha: blob.sha,
        });
      }

      // Add test files
      for (const test of solution.tests) {
        const { data: blob } = await octokit.git.createBlob({
          owner,
          repo,
          content: Buffer.from(test.content).toString('base64'),
          encoding: 'base64',
        });
        
        treeItems.push({
          path: test.path,
          mode: '100644' as const,
          type: 'blob' as const,
          sha: blob.sha,
        });
      }

      // Create tree
      const { data: tree } = await octokit.git.createTree({
        owner,
        repo,
        base_tree: baseTree.sha,
        tree: treeItems,
      });

      // Create commit
      const { data: commit } = await octokit.git.createCommit({
        owner,
        repo,
        message: `Fix issue #${issue.issue.number}: ${issue.issue.title}`,
        tree: tree.sha,
        parents: [baseSha],
      });

      // Update branch reference
      await octokit.git.updateRef({
        owner,
        repo,
        ref: `heads/${branchName}`,
        sha: commit.sha,
      });

      // Create pull request
      const { data: pr } = await octokit.pulls.create({
        owner,
        repo,
        title: solution.prTitle,
        body: `${solution.prDescription}\n\nCloses #${issue.issue.number}`,
        head: branchName,
        base: baseBranch,
      });

      logger.info(`Created PR #${pr.number} for issue #${issue.issue.number} in ${owner}/${repo}`);
      
      return pr;

    } catch (error) {
      logger.error('Failed to create pull request:', error);
      throw error;
    }
  }

  async addLabel(owner: string, repo: string, issueNumber: number, label: string) {
    try {
      await octokit.issues.addLabels({
        owner,
        repo,
        issue_number: issueNumber,
        labels: [label],
      });
      logger.info(`Added label ${label} to issue #${issueNumber} in ${owner}/${repo}`);
    } catch (error) {
      logger.error(`Failed to add label ${label}:`, error);
    }
  }
}