import { GitHubPoller } from './poller';
import { config } from './config';
import { logger } from '../../../shared/logger';

// Validate required config
if (!config.githubToken || !config.webhookSecret) {
  logger.error('Missing required environment variables: GITHUB_PERSONAL_ACCESS_TOKEN, GITHUB_WEBHOOK_SECRET');
  process.exit(1);
}

logger.info('🚀 Starting GitHub Issue Poller Service');
logger.info(`📋 Repository: ${config.owner}/${config.repo}`);
logger.info(`🎯 Webhook URL: ${config.webhookUrl}`);

const poller = new GitHubPoller(config);

// Handle graceful shutdown
process.on('SIGTERM', () => {
  logger.info('Received SIGTERM, shutting down gracefully');
  poller.stop();
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('Received SIGINT, shutting down gracefully');
  poller.stop();
  process.exit(0);
});

// Start the poller
poller.start().catch(error => {
  logger.error('Failed to start poller:', error);
  process.exit(1);
});