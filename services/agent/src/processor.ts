import { IssueEvent } from '../shared/types';
import { CodingAgent } from './agent';
import { GitHubManager } from './github';
import { StateManager, IssueState } from './state';
import { logger } from '../shared/logger';

const agent = new CodingAgent();
const github = new GitHubManager();
const state = new StateManager();

export async function processIssue(issue: IssueEvent) {
  const issueNumber = issue.issue.number;
  const { owner, name: repo } = issue.repository;
  
  try {
    // Check if already processing
    if (await state.isProcessing(issueNumber)) {
      logger.info(`Issue #${issueNumber} is already being processed`);
      return;
    }

    // Check retry limit
    if (!(await state.shouldRetry(issueNumber))) {
      logger.warn(`Issue #${issueNumber} has exceeded retry limit`);
      return;
    }

    // Update state to WORKING
    await state.setState(issueNumber, IssueState.WORKING);
    await state.incrementAttempts(issueNumber);

    // Post initial comment
    await github.createComment(
      owner,
      repo,
      issueNumber,
      '🤖 AI Agent is analyzing this issue...'
    );

    // Add label
    await github.addLabel(owner, repo, issueNumber, 'ai-processing');

    // Agent analyzes and implements solution
    logger.info(`Agent processing issue #${issueNumber}`);
    const solution = await agent.implementSolution(issue);

    if (!solution.success) {
      throw new Error(solution.error || 'Failed to generate solution');
    }

    // Post analysis comment
    await github.createComment(
      owner,
      repo,
      issueNumber,
      `## 🔍 Analysis Complete\n\n**Understanding:** ${solution.understanding}\n\n**Approach:** ${solution.approach}\n\n📝 Creating pull request with ${solution.files.length} files...`
    );

    // Create pull request
    const pr = await github.createPullRequest(issue, solution);

    // Update state to DONE
    await state.setState(issueNumber, IssueState.DONE, {
      prNumber: pr.number
    });

    // Post success comment
    await github.createComment(
      owner,
      repo,
      issueNumber,
      `✅ **Solution Implemented!**\n\nPull Request: #${pr.number}\n\nFiles changed:\n${solution.files.map(f => `- \`${f.path}\``).join('\n')}\n\nTests added:\n${solution.tests.map(t => `- \`${t.path}\``).join('\n') || '- None'}`
    );

    // Update labels
    await github.addLabel(owner, repo, issueNumber, 'ai-completed');
    
    logger.info(`Successfully processed issue #${issueNumber}, created PR #${pr.number}`);

  } catch (error) {
    logger.error(`Failed to process issue #${issueNumber}:`, error);
    
    // Update state to FAILED
    await state.setState(issueNumber, IssueState.FAILED, {
      error: error instanceof Error ? error.message : 'Unknown error'
    });

    // Post error comment
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    await github.createComment(
      owner,
      repo,
      issueNumber,
      `❌ **Processing Failed**\n\nError: ${errorMessage}\n\nThe AI agent encountered an issue. A human developer may need to review this.`
    );

    // Add failure label
    await github.addLabel(owner, repo, issueNumber, 'ai-failed');
  }
}