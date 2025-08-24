import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment-specific config
const envFile = process.env.NODE_ENV === 'production' 
  ? '.env.production' 
  : '.env';

dotenv.config({ path: path.resolve(process.cwd(), envFile) });

export const config = {
  port: process.env.PORT || 3000,
  github: {
    token: process.env.GITHUB_PERSONAL_ACCESS_TOKEN!,
    webhookSecret: process.env.GITHUB_WEBHOOK_SECRET!,
  },
  openai: {
    apiKey: process.env.OPENAI_API_KEY!,
    model: process.env.OPENAI_MODEL || 'gpt-4-turbo-preview',
  },
  storage: {
    path: process.env.STORAGE_PATH || './data',
  },
  agent: {
    maxRetries: parseInt(process.env.MAX_RETRIES || '3'),
    timeout: parseInt(process.env.TIMEOUT || '300000'), // 5 minutes
  }
};

export function validateConfig() {
  const required = [
    'GITHUB_PERSONAL_ACCESS_TOKEN',
    'GITHUB_WEBHOOK_SECRET', 
    'OPENAI_API_KEY'
  ];
  
  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
}