# Requirements Document: WeChat Article Translation & Publishing System

## Project Overview
A system to translate articles from the WeChat official account "瑞典马工" (Swedish Ma Gong) to English and publish them to magong.se via Vercel.

## Business Requirements

### Primary Goal
Bridge the language gap between Chinese WeChat content and international audiences by providing high-quality English translations of articles from "瑞典马工".

### Target Audience
- International readers interested in Swedish-Chinese perspectives
- English-speaking professionals and academics
- People interested in cross-cultural content about Sweden

## Functional Requirements

### 1. Article Input
- **Manual URL Input**: User provides WeChat article URLs manually
- **Batch Processing**: Support for processing multiple URLs at once
- **Article Metadata**: Extract title, author, date, and original URL

### 2. Content Extraction
- **Text Extraction**: Extract main article text from WeChat HTML
- **Image Handling**: Download and store all images from articles
- **Format Preservation**: Maintain paragraph structure, headings, lists
- **Special Elements**: Preserve quotes, code blocks, tables if present

### 3. Translation
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

### 4. Publishing
- **Platform**: Deploy to magong.se via Vercel
- **Format**: Markdown files with frontmatter
- **URL Structure**: `/posts/[date]-[slug]`
- **Images**: Hosted in `/public/images/`
- **Attribution**: Always include link to original article

### 5. Blog Features
- **Homepage**: List all articles chronologically
- **Article Page**: Display individual articles with:
  - Title (English and original Chinese)
  - Publication date
  - Reading time estimate
  - Original article link
  - Translated content
- **Mobile Responsive**: Work on all devices
- **SEO Friendly**: Meta tags, structured data

## Non-Functional Requirements

### Performance
- Page load time < 3 seconds
- Image optimization for web
- Static site generation for fast delivery

### Usability
- Clean, readable typography
- Simple navigation
- Accessible design (WCAG 2.1 AA compliance)

### Reliability
- Graceful handling of translation failures
- Image fallbacks if download fails
- Error logging and reporting

### Maintainability
- Clear code structure
- Documentation for all scripts
- Easy to add new features

## Technical Requirements

### Development Environment
- Python 3.9+ for translation script
- Node.js 18+ for Next.js
- Git for version control

### Dependencies
- **Frontend**: Next.js, React, gray-matter, remark
- **Translation**: googletrans, beautifulsoup4, requests
- **Image Processing**: Pillow
- **Deployment**: Vercel CLI

### Infrastructure
- GitHub repository (lipingtababa/liangxiao)
- Vercel hosting with custom domain (magong.se)
- Local development environment

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

## Out of Scope

- Automatic article detection from WeChat
- Comments system
- User accounts/authentication
- Analytics tracking (initially)
- Multiple language support beyond English
- Real-time translation

## Future Enhancements

1. **Phase 2**
   - RSS feed generation
   - Email newsletter integration
   - Search functionality
   - Categories and tags

2. **Phase 3**
   - Automatic article detection
   - Translation quality review system
   - Reader feedback mechanism
   - Analytics dashboard

## Acceptance Criteria

The system is considered complete when:
1. Translation script can process WeChat URLs
2. Blog displays articles correctly
3. Vercel deployment is configured
4. At least one article is successfully published
5. Documentation is complete