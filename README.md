# WeChat Article Translator & Publisher

An automated tool that monitors the WeChat official account "瑞典马工" (Swedish Ma Gong), translates articles to English, and publishes them to magong.se via Vercel.

## Overview

This project bridges the gap between Chinese WeChat content and international audiences by providing high-quality English translations of articles from "瑞典马工".

### Target Audience
- International readers interested in Swedish-Chinese perspectives
- English-speaking professionals and academics
- People interested in cross-cultural content about Sweden

### Key Features
- Manual article URL input with batch processing support
- Automatic content extraction from WeChat articles
- Chinese to English translation with cultural adaptation
- Publishing to magong.se through Vercel
- Image downloading and optimization
- Mobile-responsive blog design

## Requirements

### Functional Requirements

#### 1. Article Input
- **Manual URL Input**: User provides WeChat article URLs manually
- **Batch Processing**: Support for processing multiple URLs at once
- **Article Metadata**: Extract title, author, date, and original URL

#### 2. Content Extraction
- **Text Extraction**: Extract main article text from WeChat HTML
- **Image Handling**: Download and store all images from articles
- **Format Preservation**: Maintain paragraph structure, headings, lists
- **Special Elements**: Preserve quotes, code blocks, tables if present

#### 3. Translation
- **Language**: Chinese (Simplified/Traditional) → English
- **Quality**: Use reliable translation service (Google Translate API)
- **Adaptation**: Adjust content for international audience:
  - Add context for China-specific references
  - Explain cultural nuances
  - Localize idioms and expressions
- **Glossary**: Maintain consistent translation for:
  - "瑞典马工" → "Swedish Ma Gong"
  - Technical terms
  - Proper nouns

#### 4. Publishing
- **Platform**: Deploy to magong.se via Vercel
- **Format**: Markdown files with frontmatter
- **URL Structure**: `/posts/[date]-[slug]`
- **Images**: Hosted in `/public/images/`
- **Attribution**: Always include link to original article

#### 5. Blog Features
- **Homepage**: List all articles chronologically
- **Article Page**: Display individual articles with:
  - Title (English and original Chinese)
  - Publication date
  - Reading time estimate
  - Original article link
  - Translated content
- **Mobile Responsive**: Work on all devices
- **SEO Friendly**: Meta tags, structured data

### Non-Functional Requirements

#### Performance
- Page load time < 3 seconds
- Image optimization for web
- Static site generation for fast delivery

#### Usability
- Clean, readable typography
- Simple navigation
- Accessible design (WCAG 2.1 AA compliance)

#### Reliability
- Graceful handling of translation failures
- Image fallbacks if download fails
- Error logging and reporting

## The Challenge

WeChat is notoriously closed to external access, making it difficult to:
- Programmatically follow official accounts
- Retrieve article lists and content
- Extract images and media from articles
- Maintain formatting during extraction

## Solution Approach

### Extraction Method: Manual Feed with Semi-Automation
- Manually copy article URLs
- Automate extraction, translation, and publishing
- Most reliable approach given WeChat's restrictions

### Translation Pipeline

```
WeChat Article → Content Extraction → Translation API → Format Preservation → Vercel Publish
```

- **Content Extraction**: Parse HTML, extract text and images
- **Translation**: Use Google Translate API for Chinese→English
- **Format Preservation**: Maintain article structure, headings, and image placement
- **Image Handling**: Download and re-host images on Vercel CDN

## Technical Architecture

```
liangxiao/
├── scripts/
│   └── translate.py           # Main translation script
├── posts/                     # Markdown articles
│   └── YYYY-MM-DD-title.md
├── public/
│   └── images/               # Article images
├── pages/
│   ├── index.js              # Homepage
│   └── posts/
│       └── [slug].js         # Article pages
├── lib/
│   └── posts.js              # Post utilities
├── package.json              # Node dependencies
├── requirements.txt          # Python dependencies
└── design.md                 # Detailed design doc
```

## Installation

```bash
# Clone repository
git clone https://github.com/lipingtababa/liangxiao
cd liangxiao

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

```python
# config.py example
WECHAT_ACCOUNT = "瑞典马工"
TARGET_LANGUAGE = "en"
VERCEL_TOKEN = "your-vercel-token"
VERCEL_PROJECT = "magong-se"
TRANSLATION_API = "google"
```

## Usage

### Translate Single Article
```bash
python scripts/translate.py "https://mp.weixin.qq.com/s/xxxxx"
```

### Batch Process Articles
```bash
python scripts/translate.py --batch articles.txt
```

### Local Development
```bash
# Run development server
npm run dev
# View at http://localhost:3000
```

### Deploy to Vercel
```bash
# Commit changes
git add .
git commit -m "Add new article"
git push

# Vercel auto-deploys from GitHub
```

## Technical Stack

### Frontend
- **Framework**: Next.js 14
- **Language**: JavaScript/React
- **Styling**: CSS-in-JS
- **Markdown**: gray-matter, remark

### Backend/Scripts
- **Language**: Python 3.9+
- **Translation**: googletrans
- **Web Scraping**: beautifulsoup4, requests
- **Image Processing**: Pillow

### Infrastructure
- **Repository**: GitHub (lipingtababa/liangxiao)
- **Hosting**: Vercel
- **Domain**: magong.se

## Constraints

### Legal
- Respect copyright - always attribute original source
- Include disclaimer about translation
- Follow WeChat's terms of service

### Technical
- WeChat's closed ecosystem (no official API access)
- Google Translate API limits
- Vercel's build time limits

### Resource
- Single developer
- No budget for paid translation APIs initially
- Manual article selection process

## Success Criteria

1. **Functional Success**
   - Successfully translate and publish articles
   - Preserve article formatting and images
   - Maintain readable, accurate translations

2. **User Experience**
   - Articles are easy to find and read
   - Site loads quickly
   - Mobile-friendly design

3. **Operational Success**
   - Simple workflow for adding new articles
   - Minimal manual intervention required
   - Easy to maintain and update

## Implementation Roadmap

### Phase 1: MVP (Current)
- [x] Requirements and design documentation
- [ ] Basic translation script
- [ ] Next.js blog setup
- [ ] Manual article processing
- [ ] Vercel deployment

### Phase 2: Enhancement
- [ ] Batch processing
- [ ] Image optimization
- [ ] Translation quality improvements
- [ ] Error handling and logging

### Phase 3: Advanced Features
- [ ] RSS feed generation
- [ ] Email newsletter
- [ ] Search functionality
- [ ] Categories and tags
- [ ] Analytics dashboard

## Contributing

This project needs help with:
- Improving WeChat article extraction methods
- Enhancing translation quality
- Adding more publishing platforms
- Creating better monitoring solutions

## License

MIT License - See LICENSE file for details

## Contact

For questions about this project or the translated content, visit [magong.se](https://magong.se)

---

**Note**: This tool is designed specifically for translating "瑞典马工" content with proper attribution. It should not be used to scrape or republish content without permission.