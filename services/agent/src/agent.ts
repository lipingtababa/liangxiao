import OpenAI from 'openai';
import { config } from './config';
import { logger } from './logger';
import { IssueEvent, AgentResponse } from './types';

const openai = new OpenAI({
  apiKey: config.openai.apiKey,
});

export class CodingAgent {
  async analyzeIssue(issue: IssueEvent): Promise<AgentResponse> {
    try {
      const systemPrompt = `You are an expert software developer. Analyze the GitHub issue and provide:
1. A clear understanding of what needs to be done
2. The files that need to be created or modified
3. The actual code implementation
4. Any tests that should be included

Respond in JSON format with this structure:
{
  "understanding": "Brief summary of the task",
  "approach": "How you'll solve it",
  "files": [
    {
      "path": "relative/path/to/file.ts",
      "action": "create" or "modify",
      "content": "Full file content"
    }
  ],
  "tests": [
    {
      "path": "relative/path/to/test.ts",
      "content": "Test file content"
    }
  ],
  "prTitle": "Title for the pull request",
  "prDescription": "Description for the pull request"
}`;

      const userPrompt = `
Repository: ${issue.repository.full_name}
Issue #${issue.issue.number}: ${issue.issue.title}

Description:
${issue.issue.body}

Labels: ${issue.issue.labels.join(', ')}
`;

      const response = await openai.chat.completions.create({
        model: config.openai.model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.7,
        response_format: { type: 'json_object' }
      });

      const result = JSON.parse(response.choices[0]?.message?.content || '{}');
      
      return {
        success: true,
        understanding: result.understanding,
        approach: result.approach,
        files: result.files || [],
        tests: result.tests || [],
        prTitle: result.prTitle || `Fix issue #${issue.issue.number}`,
        prDescription: result.prDescription || `Automated fix for issue #${issue.issue.number}: ${issue.issue.title}`
      };

    } catch (error) {
      logger.error('Agent analysis failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        understanding: '',
        approach: '',
        files: [],
        tests: [],
        prTitle: '',
        prDescription: ''
      };
    }
  }

  async implementSolution(issue: IssueEvent): Promise<AgentResponse> {
    logger.info(`Agent implementing solution for issue #${issue.issue.number}`);
    
    // Analyze the issue
    const analysis = await this.analyzeIssue(issue);
    
    if (!analysis.success) {
      return analysis;
    }

    // Validate the solution has actual implementations
    if (analysis.files.length === 0) {
      return {
        ...analysis,
        success: false,
        error: 'No implementation files generated'
      };
    }

    logger.info(`Generated ${analysis.files.length} files and ${analysis.tests.length} tests`);
    
    return analysis;
  }
}