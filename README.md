# 🤖 Synthetic Coding Team

An AI-powered multi-agent system that automatically processes GitHub issues and creates high-quality code solutions through intelligent task decomposition and specialized agent collaboration.

## 🎯 Overview

The Synthetic Coding Team replaces traditional single-agent approaches with a sophisticated multi-agent architecture where specialized AI agents work together to deliver production-ready code:

- **Project Manager Agent**: Analyzes issues and creates task breakdowns
- **Developer + Navigator Pairs**: Implements solutions with quality oversight  
- **Analyst Agent**: Performs requirements analysis and documentation
- **Tester Agent**: Generates and validates comprehensive tests

## 🏗️ Architecture

### Multi-Agent System (Python/LangChain)
```
GitHub Issue → Project Manager → Task Breakdown
                    ↓
            Specialized Agent Pairs
            (Developer + Navigator)
                    ↓
            Quality Gates & Review → GitHub PR
```

## 📁 Project Structure

```
├── agents/             # AI agents (Developer, Navigator, Analyst, Tester)
├── workflows/          # LangGraph workflow orchestration
├── api/               # FastAPI endpoints and webhooks
├── core/              # Core utilities and workspace manager
├── models/            # Data models and schemas
├── tests/             # Comprehensive test suite
├── docs/              # Implementation roadmap & user stories
├── workspaces/        # Repository clones and artifacts (gitignored)
├── data/              # Application state
├── logs/              # Application logs
└── main.py           # FastAPI application entry point
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose  
- GitHub Personal Access Token with repo permissions
- OpenAI API Key
- (Optional) LangChain API Key for tracing

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd synthetic-coding-team

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
```

Required environment variables:
```bash
OPENAI_API_KEY=your_openai_key_here
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_OWNER=your_username
GITHUB_REPO=your_repository_name
```

### 2. Installation & Development

#### Docker Compose (Recommended)
```bash
# Start the orchestrator service
docker-compose up --build

# View logs  
docker-compose logs -f orchestrator
```

#### Manual Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the orchestrator
python main.py     # FastAPI server on port 8000
```

### 3. GitHub Webhook Configuration

Add a webhook to your GitHub repository:
- **URL**: `https://your-domain.com/api/webhook` 
- **Content Type**: `application/json`
- **Secret**: Same as `GITHUB_WEBHOOK_SECRET` in your .env
- **Events**: Select "Issues" and "Pull requests"

## 🧪 Testing

### Local Testing
```bash
# Run orchestrator tests
pytest

# Test individual agents
python demo_task_pair.py
python demo_navigator.py

# Check service health
curl http://localhost:8000/health
```

### Create Test Issues
1. Start the services: `docker-compose up`
2. Create an issue in your configured GitHub repository
3. Watch the logs to see the agent process the issue
4. Check for the created pull request

## 🔧 How It Works

### Multi-Agent Workflow (Python/LangChain)
1. **Issue Analysis**: Project Manager breaks down requirements into tasks
2. **Task Assignment**: Specialized agent pairs handle implementation
3. **Quality Assurance**: Navigator agents review and iterate on solutions
4. **Integration Testing**: Tester agents validate solutions comprehensively
5. **PR Generation**: High-quality code with tests and documentation

### Workspace Organization
```
workspaces/
├── {repo_name}/
│   ├── {issue_id}/              # GitHub issue # or Jira ticket (SOT-123)
│   │   ├── {repo_name}/         # Cloned repository
│   │   └── .SyntheticCodingTeam/ # SCT metadata and artifacts
│   │       ├── artifacts/       # Generated code
│   │       ├── iterations/      # Review iterations
│   │       ├── logs/           # Process logs
│   │       ├── issue.json      # Issue details
│   │       └── workflow.json   # Workflow state
```

## 📊 Services

### Orchestrator Service (Port 8000)
- **Purpose**: Multi-agent LangChain/LangGraph system for intelligent code generation
- **Technology**: Python, FastAPI, LangChain, LangGraph, OpenAI
- **Key Components**: 
  - `agents/` - Specialized AI agents (Developer, Navigator, Analyst, Tester)
  - `workflows/` - LangGraph workflow orchestration
  - `api/` - FastAPI webhooks and health endpoints
  - Built-in GitHub issue polling and webhook handling

## 🎯 Capabilities

### Multi-Agent System Handles:
- ✅ Complex multi-file refactoring
- ✅ Intelligent task decomposition  
- ✅ Quality-assured code generation
- ✅ Comprehensive test suites
- ✅ Documentation generation
- ✅ Architecture improvements
- ✅ Code review and iteration cycles
- ✅ Multi-agent collaboration patterns

## 📈 Monitoring & Debugging

### Logs
```bash
# View real-time logs
docker-compose logs -f orchestrator

# Log files (if volume mounted)
tail -f logs/orchestrator.log
```

### State Management
Issue processing state is stored using LangGraph checkpointing:
- **Workflow State**: SQLite database with persistent checkpoints
- **Artifacts**: Organized in workspace directories

### Health Checks
```bash
# Check orchestrator service
curl http://localhost:8000/health

# Check webhook endpoint  
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"action":"ping"}'
```

## 🚨 Troubleshooting

### Common Issues

**Webhook Not Receiving Events**
- Verify webhook URL is accessible from internet
- Check `GITHUB_WEBHOOK_SECRET` matches GitHub configuration
- Ensure firewall/NAT allows incoming connections

**Agent Timeouts**  
- Check OpenAI API rate limits
- Increase timeout settings in configuration
- Monitor retry settings

**PR Creation Fails**
- Verify GitHub token has repository write permissions
- Check token hasn't expired
- Ensure repository exists and is accessible

**Build Failures**
- Confirm Python version ≥3.11
- Run `pytest` to identify issues
- Check all environment variables are set
- Ensure all dependencies in requirements.txt are installed

### Debug Mode
```bash
# Enable verbose logging
DEBUG=true docker-compose up

# Run orchestrator with debug
DEBUG=true python main.py
```

## 🛣️ Roadmap

### Phase 1: Multi-Agent Foundation ✅
- [x] Python/LangChain/LangGraph architecture
- [x] Basic agent implementations (Developer, Navigator)  
- [x] GitHub integration with polling and webhooks
- [x] FastAPI service with health monitoring
- [x] Workspace organization system

### Phase 2: Advanced Agents 🚧
See detailed roadmap in `docs/stories/overview.md`:
- [x] Navigator quality assurance system
- [x] Developer agent pairs  
- [ ] Analyst agent for requirements analysis
- [ ] Tester agent for comprehensive validation
- [ ] Project Manager orchestration

### Phase 3: Production & Scale
- Performance optimization
- Advanced monitoring and observability
- Production deployment automation

## 🤝 Contributing

### Development Workflow
1. Read the relevant story in `docs/stories/`
2. Follow the dependency chain outlined in the overview
3. Implement changes incrementally
4. Test thoroughly before marking complete
5. Update documentation as needed

### Quality Standards
- All code must pass Python type checking and tests
- New features require comprehensive test coverage
- Follow existing code patterns and conventions  
- Document any architectural decisions
- Use pre-commit hooks for code quality

## 📝 License

**Commercial Software** - All rights reserved. This software is proprietary and confidential.

See [COPYRIGHT.md](COPYRIGHT.md) for complete license terms and restrictions.

## 🔗 Resources

- [Implementation Documentation](docs/implementation/)
- [System Architecture](docs/architecture/multi-agent-system.md)
- [Implementation Stories](docs/stories/overview.md)  
- [Deployment Guide](DEPLOY.md)

---

**Built for intelligence. Designed for quality. Engineered for scale.** 🎯