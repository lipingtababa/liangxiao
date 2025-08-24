import { Request, Response } from 'express';
import * as crypto from 'crypto';
import { config } from './config';
import { logger } from './logger';
import { processIssue } from './processor';
import { IssueEvent } from './types';

export async function webhookHandler(req: Request, res: Response): Promise<void> {
  try {
    // Verify webhook signature
    if (!verifyWebhookSignature(req)) {
      logger.warn('Invalid webhook signature');
      res.status(401).json({ error: 'Invalid signature' });
      return;
    }

    const event = req.headers['x-github-event'] as string;
    const payload = req.body;

    // Only process issue events
    if (event !== 'issues') {
      logger.info(`Ignoring event: ${event}`);
      res.status(200).json({ message: 'Event ignored' });
      return;
    }

    // Only process opened issues
    if (payload.action !== 'opened') {
      logger.info(`Ignoring issue action: ${payload.action}`);
      res.status(200).json({ message: 'Action ignored' });
      return;
    }

    // Extract issue data
    const issueEvent: IssueEvent = {
      action: payload.action,
      issue: {
        id: payload.issue.id,
        number: payload.issue.number,
        title: payload.issue.title,
        body: payload.issue.body || '',
        user: payload.issue.user.login,
        labels: payload.issue.labels.map((l: any) => l.name),
        created_at: payload.issue.created_at,
      },
      repository: {
        name: payload.repository.name,
        owner: payload.repository.owner.login,
        full_name: payload.repository.full_name,
      }
    };

    logger.info(`Processing issue #${issueEvent.issue.number}: ${issueEvent.issue.title}`);

    // Process asynchronously
    processIssue(issueEvent).catch(error => {
      logger.error('Failed to process issue:', error);
    });

    res.status(200).json({ message: 'Issue processing started' });

  } catch (error) {
    logger.error('Webhook handler error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

function verifyWebhookSignature(req: Request): boolean {
  const signature = req.headers['x-hub-signature-256'] as string;
  
  if (!signature) {
    return false;
  }

  const hmac = crypto.createHmac('sha256', config.github.webhookSecret);
  const digest = 'sha256=' + hmac.update(JSON.stringify(req.body)).digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(digest)
  );
}