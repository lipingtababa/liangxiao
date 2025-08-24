import express from 'express';
import { webhookHandler } from './webhook';
import { config } from './config';
import { logger } from './logger';

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/health', (_req, res) => {
  res.json({ status: 'healthy', version: '0.1.0-mvp' });
});

app.post('/webhook', webhookHandler);

const PORT = config.port || 3000;

app.listen(PORT, () => {
  logger.info(`MVP AI Coding Agent running on port ${PORT}`);
});

export default app;