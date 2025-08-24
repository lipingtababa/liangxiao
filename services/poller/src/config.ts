import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment config
const envFile = process.env.NODE_ENV === 'production' 
  ? '.env.production' 
  : '.env';

dotenv.config({ path: path.resolve(process.cwd(), envFile) });

export const config = {
  githubToken: process.env.GITHUB_PERSONAL_ACCESS_TOKEN!,
  owner: process.env.GITHUB_OWNER || 'lipingtababa',
  repo: process.env.GITHUB_REPO || 'liangxiao', 
  webhookUrl: process.env.WEBHOOK_URL || 'http://localhost:3000/webhook',
  webhookSecret: process.env.GITHUB_WEBHOOK_SECRET!,
  pollInterval: parseInt(process.env.POLL_INTERVAL || '30000') // 30 seconds default
};