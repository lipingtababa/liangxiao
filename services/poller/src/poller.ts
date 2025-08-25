import { Octokit } from '@octokit/rest';
import axios from 'axios';
import { logger } from '../shared/logger';

interface PollerConfig {
  githubToken: string;
  owner: string;
  repo: string;
  webhookUrl: string;
  webhookSecret: string;
  pollInterval: number; // milliseconds
}

export class GitHubPoller {
  private octokit: Octokit;
  private config: PollerConfig;
  private lastChecked: Date;
  private isRunning = false;

  constructor(config: PollerConfig) {
    this.config = config;
    this.octokit = new Octokit({ auth: config.githubToken });
    this.lastChecked = new Date();
  }

  async start() {
    if (this.isRunning) return;
    
    this.isRunning = true;
    logger.info(`🔄 Starting GitHub poller for ${this.config.owner}/${this.config.repo}`);
    logger.info(`📡 Polling every ${this.config.pollInterval / 1000}s`);
    
    // Start polling (don't await to not block)
    this.poll().catch(error => {
      logger.error('💥 Polling loop crashed:', error);
    });
  }

  stop() {
    this.isRunning = false;
    logger.info('🛑 Stopping GitHub poller');
  }

  private async poll() {
    while (this.isRunning) {
      try {
        logger.info('🔄 Starting polling cycle...');
        await this.checkForNewIssues();
        logger.info(`⏰ Waiting ${this.config.pollInterval / 1000}s until next check...`);
      } catch (error) {
        logger.error('❌ Polling error:', error);
      }

      await this.sleep(this.config.pollInterval);
    }
  }

  private async checkForNewIssues() {
    try {
      logger.info('🔍 Checking for assigned issues...');
      const { data: issues } = await this.octokit.issues.listForRepo({
        owner: this.config.owner,
        repo: this.config.repo,
        state: 'open',
        sort: 'created',
        direction: 'desc'
      });

      const assignedIssues = issues.filter(issue => 
        !issue.pull_request && // Exclude PRs
        issue.assignee?.login === 'lipingtababa' // Only issues assigned to Ma Chi
      );

      if (assignedIssues.length > 0) {
        logger.info(`🔍 Found ${assignedIssues.length} issue(s) assigned to Ma Chi (lipingtababa)`);
        
        for (const issue of assignedIssues) {
          await this.triggerWebhook(issue);
        }
      }

      this.lastChecked = new Date();
    } catch (error) {
      logger.error('Failed to check for assigned issues:', error);
    }
  }

  private async triggerWebhook(issue: any) {
    try {
      const payload = {
        action: 'opened',
        issue: issue,
        repository: {
          id: issue.repository?.id,
          name: this.config.repo,
          full_name: `${this.config.owner}/${this.config.repo}`,
          owner: {
            login: this.config.owner
          }
        }
      };

      logger.info(`📤 Triggering webhook for issue #${issue.number}: ${issue.title}`);

      await axios.post(this.config.webhookUrl, payload, {
        headers: {
          'Content-Type': 'application/json',
          'X-GitHub-Event': 'issues',
          'X-Hub-Signature-256': this.generateSignature(JSON.stringify(payload))
        },
        timeout: 30000
      });

      logger.info(`✅ Webhook triggered successfully for issue #${issue.number}`);
    } catch (error) {
      logger.error(`❌ Failed to trigger webhook for issue #${issue.number}:`, error);
    }
  }

  private generateSignature(payload: string): string {
    const crypto = require('crypto');
    return 'sha256=' + crypto
      .createHmac('sha256', this.config.webhookSecret)
      .update(payload, 'utf8')
      .digest('hex');
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}