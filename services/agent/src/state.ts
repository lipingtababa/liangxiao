import { promises as fs } from 'fs';
import * as path from 'path';
import { config } from './config';
import { logger } from '../shared/logger';

export enum IssueState {
  TODO = 'TODO',
  WORKING = 'WORKING',
  DONE = 'DONE',
  FAILED = 'FAILED'
}

export interface IssueStateData {
  issueNumber: number;
  state: IssueState;
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
  attempts: number;
  lastAttempt?: Date;
  prNumber?: number;
}

export class StateManager {
  private dataPath: string;

  constructor() {
    this.dataPath = config.storage.path;
    // Only ensure directory in non-production (DO handles this)
    if (process.env.NODE_ENV !== 'production') {
      this.ensureDataDir();
    }
  }

  private async ensureDataDir() {
    try {
      await fs.mkdir(this.dataPath, { recursive: true });
    } catch (error) {
      logger.error('Failed to create data directory:', error);
    }
  }

  private getFilePath(issueNumber: number): string {
    return path.join(this.dataPath, `issue-${issueNumber}.json`);
  }

  async getState(issueNumber: number): Promise<IssueStateData | null> {
    try {
      const filePath = this.getFilePath(issueNumber);
      const data = await fs.readFile(filePath, 'utf-8');
      return JSON.parse(data);
    } catch (error) {
      return null;
    }
  }

  async setState(issueNumber: number, state: IssueState, metadata?: Partial<IssueStateData>) {
    try {
      const existing = await this.getState(issueNumber);
      
      const data: IssueStateData = {
        issueNumber,
        state,
        attempts: existing?.attempts || 0,
        ...metadata
      };

      if (state === IssueState.WORKING && !existing?.startedAt) {
        data.startedAt = new Date();
      }

      if (state === IssueState.DONE || state === IssueState.FAILED) {
        data.completedAt = new Date();
      }

      const filePath = this.getFilePath(issueNumber);
      await fs.writeFile(filePath, JSON.stringify(data, null, 2));
      
      logger.info(`State updated for issue #${issueNumber}: ${state}`);
    } catch (error) {
      logger.error('Failed to save state:', error);
      throw error;
    }
  }

  async incrementAttempts(issueNumber: number) {
    const state = await this.getState(issueNumber);
    if (state) {
      await this.setState(issueNumber, state.state, {
        ...state,
        attempts: state.attempts + 1,
        lastAttempt: new Date()
      });
    }
  }

  async isProcessing(issueNumber: number): Promise<boolean> {
    const state = await this.getState(issueNumber);
    return state?.state === IssueState.WORKING;
  }

  async shouldRetry(issueNumber: number): Promise<boolean> {
    const state = await this.getState(issueNumber);
    if (!state) return true;
    
    return state.attempts < config.agent.maxRetries && 
           state.state !== IssueState.DONE;
  }
}