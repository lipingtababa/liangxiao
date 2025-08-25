export interface IssueEvent {
  action: string;
  issue: {
    id: number;
    number: number;
    title: string;
    body: string;
    user: string;
    labels: string[];
    created_at: string;
  };
  repository: {
    name: string;
    owner: string;
    full_name: string;
  };
}

export interface FileChange {
  path: string;
  action: 'create' | 'modify';
  content: string;
}

export interface TestFile {
  path: string;
  content: string;
}

export interface AgentResponse {
  success: boolean;
  error?: string;
  understanding: string;
  approach: string;
  files: FileChange[];
  tests: TestFile[];
  prTitle: string;
  prDescription: string;
}