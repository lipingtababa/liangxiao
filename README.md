# 🤖 AI Coding Agent - MVP

A lightweight AI agent that automatically processes GitHub issues and creates pull requests with code solutions.

## ✨ What It Does

1. **Receives GitHub Issue** → Webhook catches new issues
2. **AI Analyzes** → GPT-4 understands requirements and generates solution  
3. **Creates Code** → Implements the solution with tests
4. **Opens PR** → Automatically creates pull request
5. **Updates Issue** → Posts progress comments

## 🏗️ Architecture

```
GitHub Issue → Webhook → Agent → GPT-4 → Code Generation → GitHub PR
```

**Simple, focused, reliable.**

## 📁 Project Structure

```
src/
├── index.ts       # Express server
├── webhook.ts     # GitHub webhook handler  
├── agent.ts       # GPT-4 coding agent
├── processor.ts   # Issue processing logic
├── github.ts      # GitHub API operations
├── state.ts       # Simple JSON state tracking
├── config.ts      # Configuration
├── logger.ts      # Winston logging
├── types.ts       # TypeScript interfaces
└── test-local.ts  # Local testing utility
```

**Only 10 files. ~600 lines of code total.**

## 🚀 Quick Start

### 1. Setup Environment

```bash
cp .env.mvp .env
# Edit .env with your credentials
```

Required variables:
- `GITHUB_PERSONAL_ACCESS_TOKEN` - Personal access token with repo scope
- `GITHUB_WEBHOOK_SECRET` - Random secret string
- `GITHUB_OWNER` - Your GitHub username  
- `GITHUB_REPO` - Repository name
- `OPENAI_API_KEY` - OpenAI API key

### 2. Install & Run

```bash
npm install
npm run dev
```

### 3. Setup GitHub Webhook

Add webhook in your repo settings:
- URL: `https://your-domain.com/webhook`
- Content: `application/json`  
- Secret: Same as `GITHUB_WEBHOOK_SECRET`
- Events: `Issues`

## 🧪 Test Locally

```bash
# Test the agent without GitHub
npm run test:local

# Or start server and create a test issue
npm run dev
# Then create an issue in your GitHub repo
```

## 📦 Deploy to Production

```bash
# Automated GitHub Actions deployment
# See: DEPLOY.md

# 1. Setup droplet once
# 2. Configure GitHub secrets  
# 3. Push to deploy
git push origin main
```

Cost: **$6/month** for DigitalOcean droplet

## 🎯 What It Can Handle

The agent can solve:
- ✅ Create new functions/utilities  
- ✅ Add simple features
- ✅ Generate basic tests
- ✅ Create new files
- ✅ Simple bug fixes

## 🔧 How It Works

1. **Webhook** receives GitHub issue events
2. **Agent** parses issue and calls GPT-4
3. **GPT-4** generates code solution with tests
4. **GitHub Manager** creates branch and PR
5. **State Manager** tracks progress in JSON files

## 📊 Dependencies

- **Express** - Web server
- **@octokit/rest** - GitHub API
- **OpenAI** - GPT-4 integration  
- **Winston** - Logging
- **dotenv** - Environment config

That's it. No complex frameworks or libraries.

## 🧱 State Management

Simple JSON files store issue state:
```json
{
  "issueNumber": 42,
  "state": "DONE", 
  "prNumber": 15,
  "attempts": 1,
  "startedAt": "2024-01-01T00:00:00Z",
  "completedAt": "2024-01-01T00:05:00Z"
}
```

## 🚨 Troubleshooting

- **Agent timeouts**: Check OpenAI API rate limits
- **PR not created**: Verify GitHub token has repo permissions  
- **Webhook not working**: Check webhook URL and secret
- **Build fails**: Ensure Node 18+ and all env vars set

## 📈 Scaling

When you outgrow the MVP:
1. Add specialized agents (Analyst, Test, Review)
2. Implement LangGraph state machine
3. Add technical debt tracking
4. Create human approval workflows

But start simple. This MVP handles most use cases.

---

**Built for simplicity. Extended when needed.** 🎯