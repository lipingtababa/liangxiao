# System Design Document: WeChat Article Translation & Publishing System

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  WeChat Article │────>│ Translation      │────>│  magong.se      │
│      URLs       │     │    Pipeline      │     │   (Vercel)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │                         │
        │                       ▼                         │
        │               ┌──────────────────┐             │
        └──────────────>│  Local Storage   │<────────────┘
                        │  - Articles      │
                        │  - Images        │
                        └──────────────────┘
```

## System Components

### 1. Translation Pipeline (`scripts/translate.py`)

#### Purpose
Main script that orchestrates the entire translation and publishing process.

#### Design Decisions
- **Single Entry Point**: One script handles the entire workflow for simplicity
- **Modular Functions**: Separate functions for extraction, translation, and publishing
- **Error Recovery**: Each step can fail independently without breaking the entire pipeline
- **Idempotency**: Running the same URL twice won't create duplicates

#### Core Modules

```python
# Module structure
translate.py
├── ArticleExtractor     # Fetches and parses WeChat articles
├── ContentTranslator    # Handles translation logic
├── ImageProcessor       # Downloads and optimizes images
├── MarkdownGenerator    # Creates markdown files
└── GitPublisher        # Commits and pushes to GitHub
```

#### Data Flow

```
URL Input → Fetch HTML → Extract Content → Translate Text → Process Images 
    → Generate Markdown → Save Locally → Git Commit → Push to GitHub
```

### 2. Blog Application (Next.js)

#### Technology Choice: Next.js
- **Static Site Generation (SSG)**: Pre-builds pages for optimal performance
- **Markdown Support**: Native support for markdown content
- **Image Optimization**: Built-in image optimization
- **Vercel Integration**: Seamless deployment with Vercel

#### Directory Structure

```
liangxiao/
├── pages/
│   ├── index.js           # Homepage with article list
│   ├── posts/
│   │   └── [slug].js      # Dynamic article pages
│   └── _app.js            # App wrapper with global styles
├── posts/                 # Markdown articles (data)
│   ├── 2025-01-15-article-title.md
│   └── ...
├── public/
│   ├── images/           # Article images
│   │   └── [hash]/       # Organized by article
│   └── favicon.ico
├── lib/
│   └── posts.js          # Post data fetching utilities
├── styles/
│   └── globals.css       # Global styles
└── scripts/
    └── translate.py      # Translation pipeline
```

#### Page Components

1. **Homepage (`pages/index.js`)**
   - Lists all articles in reverse chronological order
   - Shows title, excerpt, date, and original title
   - Responsive grid layout

2. **Article Page (`pages/posts/[slug].js`)**
   - Renders markdown content as HTML
   - Shows metadata (date, original link, reading time)
   - Responsive typography optimized for reading

3. **Layout Components**
   - Header with site title and navigation
   - Footer with attribution and links
   - Sidebar for future enhancements

### 3. Data Models

#### Article Metadata (Frontmatter)

```yaml
---
title: "English Title Here"
originalTitle: "中文标题"
date: "2025-01-15"
author: "瑞典马工"
excerpt: "Brief description of the article"
originalUrl: "https://mp.weixin.qq.com/s/xxxxx"
images: 
  - "/images/article-hash/image1.jpg"
  - "/images/article-hash/image2.jpg"
tags: ["sweden", "technology", "culture"]
readingTime: 5
---
```

#### File Naming Convention

```
Format: YYYY-MM-DD-slug-from-title.md
Example: 2025-01-15-swedish-tech-innovation.md
```

### 4. Translation Strategy

#### Translation Service: Google Translate API

```python
class ContentTranslator:
    def translate(self, text, source='zh-CN', target='en'):
        # Chunk text if > 5000 characters
        # Preserve formatting markers
        # Apply glossary replacements
        # Return translated text
```

#### Content Adaptation Rules

1. **Cultural Context**
   ```
   Original: "春节期间" 
   Direct: "During Spring Festival"
   Adapted: "During Spring Festival (Chinese New Year)"
   ```

2. **Measurements**
   ```
   Original: "100公里"
   Adapted: "100 kilometers (62 miles)"
   ```

3. **Proper Nouns**
   - Keep original Chinese names with pinyin
   - Add explanations for institutions/places

#### Translation Glossary

```python
GLOSSARY = {
    "瑞典马工": "Swedish Ma Gong",
    "斯德哥尔摩": "Stockholm",
    "微信": "WeChat",
    # Add more terms as needed
}
```

### 5. Image Processing

#### Image Pipeline

```python
class ImageProcessor:
    def process(self, image_url, article_hash):
        # Download image from WeChat CDN
        # Generate unique filename
        # Optimize for web (compress, resize)
        # Save to public/images/[article_hash]/
        # Return local path
```

#### Image Optimization
- Max width: 1200px
- Format: WebP with JPEG fallback
- Compression: 85% quality
- Lazy loading enabled

### 6. Deployment Architecture

#### GitHub Repository
```
Repository: lipingtababa/liangxiao
Branch: main (production)
```

#### Vercel Configuration

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "devCommand": "npm run dev",
  "installCommand": "npm install"
}
```

#### Deployment Flow
1. Developer runs `python scripts/translate.py [URL]`
2. Script generates markdown and images
3. Git commit and push to main branch
4. Vercel detects push and triggers build
5. Site updates at magong.se

### 7. Error Handling

#### Error Categories

1. **Extraction Errors**
   - Invalid URL
   - Network timeout
   - Content parsing failure
   - **Recovery**: Log error, skip article

2. **Translation Errors**
   - API rate limit
   - Service unavailable
   - **Recovery**: Retry with exponential backoff

3. **Publishing Errors**
   - Git conflicts
   - Build failures
   - **Recovery**: Manual intervention required

#### Logging Strategy

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation.log'),
        logging.StreamHandler()
    ]
)
```

## Security Considerations

1. **API Keys**
   - Store in environment variables
   - Never commit to repository
   - Use `.env.local` for local development

2. **Content Sanitization**
   - Sanitize HTML to prevent XSS
   - Validate image URLs
   - Escape special characters

3. **Rate Limiting**
   - Implement delays between API calls
   - Cache translations locally
   - Monitor API usage

## Performance Optimization

1. **Static Generation**
   - Pre-build all pages at build time
   - Incremental Static Regeneration for updates

2. **Image Optimization**
   - Lazy loading
   - Modern formats (WebP)
   - Responsive images

3. **Caching**
   - CDN caching via Vercel
   - Browser caching headers
   - Local translation cache

## Testing Strategy

1. **Unit Tests**
   - Translation functions
   - Markdown generation
   - Image processing

2. **Integration Tests**
   - Full pipeline test
   - Deployment verification

3. **Manual Testing**
   - Visual review of translated articles
   - Mobile responsiveness
   - Cross-browser compatibility

## Monitoring & Maintenance

1. **Monitoring**
   - Vercel analytics
   - Build status notifications
   - Error logging

2. **Maintenance Tasks**
   - Update dependencies monthly
   - Review translation quality
   - Clean up old images
   - Backup articles

## Development Workflow

1. **Adding New Article**
   ```bash
   # 1. Get article URL
   # 2. Run translation script
   python scripts/translate.py "https://mp.weixin.qq.com/s/xxxxx"
   
   # 3. Review generated markdown
   cat posts/2025-01-15-article-title.md
   
   # 4. Make manual adjustments if needed
   
   # 5. Commit and deploy
   git add .
   git commit -m "Add article: [title]"
   git push
   ```

2. **Local Development**
   ```bash
   # Install dependencies
   npm install
   
   # Run development server
   npm run dev
   
   # View at http://localhost:3000
   ```

## Future Enhancements

### Phase 2
- Implement RSS feed
- Add search functionality
- Create category pages
- Implement related articles

### Phase 3
- Add commenting system
- Implement newsletter
- Create admin dashboard
- Add analytics

## Conclusion

This design provides a simple, maintainable solution for translating and publishing WeChat articles. The manual process ensures quality control while the automated publishing reduces repetitive work. The system is designed to be extended as needs grow.