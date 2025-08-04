# WOPE - Write Once, Publish Everywhere

A Python web application that allows you to write articles once in Markdown and automatically publish them to multiple platforms.

## Overview

WOPE (Write Once, Publish Everywhere) is designed for content creators who want to streamline their publishing workflow. Write your articles in Markdown format and publish them simultaneously to:

- **WeChat** (Official Accounts)
- **RedNote** (小红书)
- **LinkedIn**
- **Personal Blog** (via Vercel)

## Features

- 📝 Write in Markdown format
- 🎯 Multi-platform publishing
- 🖼️ Intelligent image management and generation
- 🔐 Secure credential management
- ⚡ Local storage for fast performance
- 🔄 Automatic content transformation for each platform

## Architecture

The application uses a **Publisher Adapter Pattern** with platform-specific implementations:

```python
class Publisher(ABC):
    @abstractmethod
    async def publish(self, article: Article) -> PublishResult:
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        pass
```

### Supported Platforms

1. **LinkedIn Publisher** - OAuth 2.0 + REST API
2. **WeChat Publisher** - Official Account API
3. **RedNote Publisher** - Web automation (Playwright)  
4. **Vercel Publisher** - Git deployment or API

## Tech Stack

- **Backend**: Python (Flask/FastAPI)
- **Frontend**: Web UI for article management
- **Storage**: Local SQLite database
- **Authentication**: Per-platform credential management
- **Automation**: Playwright for platforms without APIs

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure platform credentials
4. Start writing and publishing!

## Platform Setup

### WeChat Official Account
- Register at WeChat Official Account platform
- Configure IP whitelist
- Get AppID and AppSecret for API access

### LinkedIn
- Create LinkedIn App for OAuth 2.0
- Configure redirect URLs
- Obtain client credentials

### RedNote (小红书)
- Set up session management for web automation
- Configure anti-bot strategies

### Personal Blog (Vercel)
- Connect GitHub repository
- Configure Vercel deployment settings

## Contributing

This project is in active development. Contributions are welcome!

## License

MIT License