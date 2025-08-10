# WeChat Article Translator & Publisher

An automated tool that monitors the WeChat official account "瑞典马工" (Swedish Ma Gong), translates articles to English, and publishes them to magong.se via Vercel.

## Overview

This project bridges the gap between Chinese WeChat content and international audiences by:
- Monitoring new articles from the "瑞典马工" WeChat official account
- Automatically translating content from Chinese to English
- Publishing translated articles to magong.se through Vercel
- Preserving images and formatting during the translation process

## The Challenge

WeChat is notoriously closed to external access, making it difficult to:
- Programmatically follow official accounts
- Retrieve article lists and content
- Extract images and media from articles
- Maintain formatting during extraction

## Proposed Solutions

### 1. WeChat Article Extraction Methods

#### Option A: WeChat Official Account API (Limited)
- Requires official account ownership or partnership
- Not feasible for third-party accounts

#### Option B: Web Scraping via Sogou Search
- Sogou indexes WeChat public articles
- URL: `https://weixin.sogou.com/`
- Can search for "瑞典马工" and get recent articles
- Challenges: Anti-scraping measures, CAPTCHA, rate limiting

#### Option C: WeChat PC Client Automation
- Use automation tools to control WeChat PC client
- Extract articles through the desktop interface
- More reliable but requires dedicated machine

#### Option D: Manual Feed with Semi-Automation
- Manually copy article URLs
- Automate extraction, translation, and publishing
- Most reliable but requires human intervention

### 2. Translation Pipeline

```
WeChat Article → Content Extraction → Translation API → Format Preservation → Vercel Publish
```

- **Content Extraction**: Parse HTML, extract text and images
- **Translation**: Use Google Translate API or DeepL for Chinese→English
- **Format Preservation**: Maintain article structure, headings, and image placement
- **Image Handling**: Download and re-host images on Vercel CDN

### 3. Publishing to magong.se

- Use Vercel API or Git-based deployment
- Generate static site content (Markdown/HTML)
- Maintain article metadata (date, original link, author)
- Create RSS feed for subscribers

## Technical Architecture

```python
# Core Components
├── scraper/
│   ├── wechat_monitor.py      # Monitor for new articles
│   ├── content_extractor.py   # Extract article content
│   └── sogou_scraper.py       # Sogou search integration
├── translator/
│   ├── translation_service.py # Translation API wrapper
│   ├── format_handler.py      # Preserve formatting
│   └── image_processor.py     # Handle image migration
├── publisher/
│   ├── vercel_client.py       # Vercel API integration
│   ├── content_generator.py   # Generate blog posts
│   └── rss_generator.py       # Create RSS feed
├── database/
│   ├── models.py               # Article tracking
│   └── migrations/             # Database schema
└── web/
    ├── dashboard.py            # Admin interface
    └── api.py                  # REST endpoints
```

## Implementation Roadmap

### Phase 1: Proof of Concept
- [ ] Test Sogou search API for article discovery
- [ ] Implement basic content extraction
- [ ] Set up translation service
- [ ] Manual publish to Vercel

### Phase 2: Automation
- [ ] Automated article monitoring
- [ ] Batch translation processing
- [ ] Automatic Vercel deployment
- [ ] Error handling and retries

### Phase 3: Enhancement
- [ ] Image optimization and CDN hosting
- [ ] Translation quality review
- [ ] Article categorization
- [ ] Analytics and monitoring

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/wechat-translator
cd wechat-translator

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run initial setup
python setup.py
```

## Configuration

```python
# config.py example
WECHAT_ACCOUNT = "瑞典马工"
TARGET_LANGUAGE = "en"
VERCEL_TOKEN = "your-vercel-token"
VERCEL_PROJECT = "magong-se"
TRANSLATION_API = "google"  # or "deepl"
CHECK_INTERVAL = 3600  # Check every hour
```

## Usage

### Manual Mode
```bash
# Translate single article
python translate_article.py --url "https://mp.weixin.qq.com/..."

# Batch process articles
python batch_translate.py --input articles.txt
```

### Automated Mode
```bash
# Start monitoring daemon
python monitor.py --daemon

# Check status
python monitor.py --status
```

## Challenges & Solutions

### Challenge 1: WeChat Access
**Problem**: WeChat doesn't provide public API for following accounts  
**Solution**: Use Sogou search as proxy or implement semi-automated workflow

### Challenge 2: Content Extraction
**Problem**: WeChat articles have complex HTML structure  
**Solution**: Custom parser targeting WeChat's specific HTML patterns

### Challenge 3: Image Handling
**Problem**: WeChat images are behind authentication  
**Solution**: Download during extraction and re-host on Vercel CDN

### Challenge 4: Translation Quality
**Problem**: Technical and cultural terms may translate poorly  
**Solution**: Custom glossary and post-translation review system

## Contributing

This project needs help with:
- Improving WeChat article extraction methods
- Enhancing translation quality
- Adding more publishing platforms
- Creating better monitoring solutions

## Legal Considerations

- Respect copyright and attribution
- Include original article links
- Follow WeChat's terms of service
- Comply with translation rights

## License

MIT License - See LICENSE file for details

## Contact

For questions about this project or the translated content, visit [magong.se](https://magong.se)

---

**Note**: This tool is designed specifically for translating "瑞典马工" content with proper attribution. It should not be used to scrape or republish content without permission.