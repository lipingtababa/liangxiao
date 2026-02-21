# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **combined monorepo** with two systems:

1. **magong.se website** — Next.js English blog translating WeChat articles for international readers
2. **Writing system** — Dual-persona WeChat article factory (benyu provocative + hushi analytical)

The pipeline: **write (Chinese)** → **convert (all formats + images)** → **publish (WeChat + XHS + Zhihu + magong.se)**

The writing system enforces **strict data authenticity** — never fabricate examples, quotes, statistics, or attributions. All data must be real, sourced, and verifiable.

## Directory Structure

```
liangxiao/                              # repo root
├── .claude/
│   ├── CLAUDE.md                       # THIS FILE
│   └── commands/
│       ├── brainstorm.md               # shared — material discovery
│       ├── outline.md                  # shared — persona-aware outline (reads .persona file)
│       ├── draft.md                    # shared — persona-aware draft (reads .persona file)
│       ├── review.md                   # shared — persona-aware review (reads .persona file)
│       ├── convert.md                  # shared — all 4 formats + Imagen 4 images
│       ├── english.md                  # shared — translate Chinese → English (used by /convert)
│       ├── pick-chat.md               # shared — chat topic extraction
│       └── publish.md                  # shared — publish to WeChat, XHS, Zhihu, magong.se
│
├── app/                                # Next.js App Router
│   ├── page.tsx                        # Home — Pinterest-style article grid
│   ├── posts/[slug]/page.tsx           # Article page
│   ├── layout.tsx                      # Root layout
│   └── globals.css
├── components/                         # React components
│   ├── ArticleCard.tsx                 # Card for home grid
│   ├── MarkdownRenderer.tsx            # Article body renderer
│   ├── PostsClient.tsx                 # Client-side post list
│   ├── ImageWithFallback.tsx
│   └── SocialShare.tsx
├── lib/
│   ├── posts.ts                        # Read/sort posts from posts/ directory
│   └── seo.ts                          # SEO metadata helpers
├── posts/                              # Published English articles (markdown + frontmatter)
├── public/images/                      # Article images
├── __tests__/                          # Jest tests
│
├── benyu/                              # PROVOCATIVE persona (戚本禹)
│   ├── .persona                        # contains: "benyu" — persona detection for shared commands
│   ├── style_guide.md
│   ├── brainstorm.md
│   └── articles/
├── hushi/                              # ANALYTICAL persona (胡适)
│   ├── .persona                        # contains: "hushi" — persona detection for shared commands
│   ├── style_guide.md
│   └── articles/
├── reading/                            # Book reading → article output
│   ├── .claude/commands/read.md        # /read command
│   └── books/                          # One subdir per book, notes.md inside
│
├── writing/                            # Shared writing resources
│   ├── templates/                      # Article structure templates
│   │   ├── article-structures/         # 5 structure types + PRINCIPLES.md
│   │   ├── wechat_styles.css
│   │   └── wechat_template.html
│   └── translation/                    # Translation workspace
│
├── scripts/
│   ├── website/                        # Website scripts (extraction, SEO)
│   └── writing/                        # Writing scripts (HTML conversion, chat analysis)
│
├── aichat -> /Users/machi/aichat       # WeChat chat data (symlink, gitignored)
└── requirements.txt
```

## Two Personas (Writing System)

### benyu - Provocative Voice
- **Directory**: `benyu/`
- **Style guide**: `benyu/style_guide.md`
- **Tone**: Confrontational, sarcastic, opinionated, challenges authority
- **Companies**: Named to challenge and attack
- **Analogies**: Vivid, everyday, mocking (永动机, 农贸市场卖豆腐)
- **Conclusions**: Provocative reversal, "来骂我吧" energy
- **Named after**: 戚本禹 (1931-2016)，毛泽东时代政论家，中央文革小组成员，以犀利的政论文章闻名，被编辑黎澍称赞为"能成为新中国的梁启超，笔端常带感情"

### hushi - Serious/Analytical Voice
- **Directory**: `hushi/`
- **Style guide**: `hushi/style_guide.md`
- **Tone**: Analytical, measured, evidence-first, forward-looking
- **Companies**: Named to cite and analyse (not attack)
- **Analogies**: Structural, scientific, from engineering/economics
- **Conclusions**: Synthesis + open questions, "一起研究" energy
- **Named after**: 胡适 (1891-1962)，中国新文化运动领袖，提倡白话文、科学方法和实证精神

## Critical Rules

### 1. NEVER Fabricate Data (Highest Priority)

**This rule overrides ALL other instructions.**

NEVER invent:
- Examples, quotes, statistics, comparisons
- Company pricing ("某翻译公司报价¥36,000")
- "Friend told me" scenarios
- Attributing user's chat messages to fictional "朋友说" or "我朋友"
- Dialogue, metrics, cost comparisons, estimated numbers presented as facts

ONLY use:
- Real data from user's actual work/sessions
- Published statistics with source URLs
- User-provided examples
- Documented facts from codebase files

If data is missing:
1. ASK the user for it
2. Leave clear placeholders: `[需要真实例子: 翻译公司报价]`
3. **Better NO example than FAKE example**

### 2. No Emoji Policy

Zero emoji in published articles (both personas) and in translated English posts.

## Slash Commands

### Writing Commands

Commands are **layered** — Claude Code walks up the directory tree, with nested commands taking precedence over root commands.

**Shared commands** (work from anywhere, persona-aware via `.persona` file):
- `/brainstorm` — Research and material discovery
- `/outline` — Persona-aware outline (reads `.persona` file, applies benyu or hushi framing)
- `/draft` — Persona-aware draft (reads `.persona` file + `{persona}/style_guide.md`)
- `/review` — Persona-aware review (reads `.persona` file + `{persona}/style_guide.md`)
- `/convert` — Markdown to WeChat HTML conversion (also persona-aware via `.persona` file)
- `/pick-chat` — Extract topics from WeChat chat data
- `/read` — Read a book, extract article-worthy insights → `reading/books/[slug]/notes.md`

**Persona detection order** (for `/outline`, `/draft`, `/review`, `/convert`):
1. Walk up directory tree for `.persona` file → read first line
2. Path contains `benyu` or `hushi` → fallback
3. Ask the user → last resort

### Translation & Publishing Commands

- `/english` — Translate a Chinese article (`draft.md`/`final.md`) into an English blog post for `posts/`
- `/publish` — Publish an English article to magong.se (verify, build, deploy)

## Writing Workflow

### Write a Chinese Article

**Standard sequence** (same for both personas):
1. `/brainstorm` — Research topic using WebSearch, collect 10+ interesting findings
2. `/outline` — Select article structure, generate detailed framework
3. `/draft` — Write following the active persona's style_guide.md
4. `/review` — Check against the active persona's checklist

**All commands MUST write output to files:**
- `brainstorm.md` — Research findings
- `outline.md` — Article structure
- `draft.md` — Article content

**Example:**
```bash
cd benyu
mkdir -p articles/my-new-article && cd articles/my-new-article
/brainstorm [topic]    # shared command
/outline               # shared — detects benyu via .persona file
/draft                 # shared — detects benyu, reads benyu/style_guide.md
/review                # shared — detects benyu, reads benyu/style_guide.md
```

### Convert and Publish to All Platforms

After the article is reviewed:
1. `/convert` — Generate all formats simultaneously:
   - `weixin.html` — WeChat-compatible HTML
   - `xhs.md` — Xiaohongshu note (≤600 chars + hashtags)
   - `zhihu.md` — Zhihu article (full markdown)
   - `english.md` — English translation for magong.se
   - `images/` — Imagen 4 generated cover + section images (3:4, 16:9, 1:1) with "AI生成" badge

2. `/publish` — Distribute to all platforms:
   - **magong.se** — git push → Vercel auto-deploys (fully automated)
   - **WeChat** — Playwright creates draft, you review and click 发布
   - **Xiaohongshu** — xhs-mcp publishes automatically (login once via QR)
   - **Zhihu** — browser opens editor, you paste and publish

### Platform Publishing Infrastructure

- **WeChat session**: `~/.credentials/wechat-session.json` (Playwright cookies, persistent)
- **XHS session**: managed by xhs-mcp (login once: `xhs-mcp login`)
- **Image generator**: `scripts/writing/image_generator.py` (Google Imagen 4, key at `~/.credentials/google.ai.txt`)
- **WeChat publisher**: `scripts/writing/wechat_publisher.py` (Playwright)
- **Platform adapters**: `writing/templates/platform-adapters/` (xhs-adapter.md, zhihu-adapter.md)

### Article Frontmatter Format

Posts in `posts/` use this frontmatter:
```yaml
---
title: 'Article Title'
date: '2026-02-07'
author: MaGong
category: AI Coding
tags: []
description: >-
  One-paragraph description for SEO and article cards.
excerpt: >
  Short excerpt for previews.
lastModified: '2026-02-07'
---
```

### Persona-Aware Style Enforcement

**Determine the active persona from working directory:**
- Working in `benyu/` or `benyu/articles/*` → read `benyu/style_guide.md`
- Working in `hushi/` or `hushi/articles/*` → read `hushi/style_guide.md`

**Six universal principles** (from `writing/templates/article-structures/PRINCIPLES.md`) apply to BOTH personas, but interpreted differently:

| Principle | benyu | hushi |
|-----------|-------|----------|
| 标题即半篇文章 | Provocative, makes you want to argue | Precise, states the thesis |
| 首段必须抓人 | Conflict, tension | Paradox, surprising observation |
| 具体事实和数字 | Trigger emotions | Support analysis |
| 听起来可操作 | "Here's what's wrong AND what to do" | "Here's a framework to think about this" |
| 打大公司/权威 | Challenge and attack | Cite and analyse |
| 读者焦虑 | Poke the wound | Offer honest analysis |

### Article Structure Types

Choose from 5 patterns in `writing/templates/article-structures/`:

1. **Debunking (驳斥)** — X is believed → X is wrong → here's reality
2. **Raising Valuable Question (提出问题)** — Reframe definition → challenge assumptions
3. **Case and Product Study (案例与产品研究)** — What happened → what it reveals
4. **Exploration & Hypothesis (探索与假说)** — Problem → experiment → framework
5. **Prediction/Trend Analysis (趋势预测)** — Current state → forces → future

### WeChat Conversion Requirements

**Before running `/convert`:**
1. Extract all markdown links `[text](url)` from article
2. Replace inline links with plain text (WeChat doesn't support hyperlinks in body)
3. Add **引用来源** section at end with numbered list of URLs

**Conversion process:**
```bash
python scripts/writing/html_converter.py benyu/articles/[name]/final.md
# or
python scripts/writing/html_converter.py hushi/articles/[name]/final.md
```

## Website Development

### Tech Stack
- Next.js 14 (App Router), React, TypeScript
- Tailwind CSS for styling
- gray-matter + remark for markdown processing
- Deployed on Vercel at magong.se

### Key Files
- `lib/posts.ts` — Reads markdown from `posts/`, parses frontmatter, sorts by date
- `app/page.tsx` — Home page with Pinterest-style waterfall layout
- `app/posts/[slug]/page.tsx` — Individual article page
- `components/ArticleCard.tsx` — Card component for the home grid
- `components/MarkdownRenderer.tsx` — Renders article markdown to HTML

### npm Scripts
- `npm run dev` — Local development server
- `npm run build` — Production build
- `npm run check` — Lint + format + typecheck + test (run before committing)
- `npm test` — Jest tests

## Key Implementation Patterns

### 1. Outline Generation

**Good outline** = Concise framework for logical argument:
- Section headings + 2-3 bullet points max per section
- Framework only, no detailed text or examples

### 2. 理实一线 (Theory-Practice Integration)

Both personas must integrate theory and practice:
- **理** (Theory): Shannon theorem, Goodhart's Law, CAP theorem, first principles
- **实** (Practice): Real companies, concrete metrics, named people

### 3. Data Authenticity Verification

All statistics must be verified with URLs. Flag placeholders for missing data.

### 4. Brainstorming as Material Discovery

`/brainstorm` is persona-agnostic exploratory research:
- Cast wide net with WebSearch
- Follow tangents and rabbit holes
- Collect contradictions and paradoxes
- Write ALL findings to `brainstorm.md`

## Working with WeChat

### Chat Data

**aichat repo**: `aichat/` is a symlink to a separate repo that syncs WeChat chat data. Structure:
- `aichat/chats/<id>_<name>/` — each chatroom has a directory with daily JSON files and `_metadata.json`
- `_metadata.json` contains `media_dir` pointing to Google Drive path where images are stored
- Images path pattern: `/Users/machi/Library/CloudStorage/GoogleDrive-hellomarch@gmail.com/My Drive/wechat-images/<chatroom_name>/`

**During /brainstorm**: Always search aichat for relevant chatroom data, including images from Google Drive.

**CRITICAL**: User's own chat messages are their OWN ideas — NEVER attribute to fictional "朋友说" or "我朋友"

### Accessing WeChat URLs

**WeChat links must use Playwright MCP**: WeChat URLs (mp.weixin.qq.com) are behind restrictions — always use the Playwright MCP browser tools (browser_navigate, browser_snapshot, etc.) to access them, never WebFetch or other regular web tools.

## Git and Permissions

When making commits:
- Use British spelling in all written output
- Commit messages in English, type prefix: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`
- Add co-credit in commit messages:
  ```
  <main commit message>

  Generated with [Claude Code](https://claude.ai/code)
  via [Happy](https://happy.engineering)

  Co-Authored-By: Claude <noreply@anthropic.com>
  Co-Authored-By: Happy <yesreply@happy.engineering>
  ```

## Code Standards

- Python: PEP 8, snake_case
- JavaScript/TypeScript: ESLint + Prettier, camelCase
- File naming: kebab-case

## Quick Reference

| What | Where |
|------|-------|
| benyu style guide | `benyu/style_guide.md` |
| hushi style guide | `hushi/style_guide.md` |
| Shared principles | `writing/templates/article-structures/PRINCIPLES.md` |
| Published articles | `posts/` |
| Article images | `public/images/` |

**Writing workflow**: `/brainstorm` → `/outline` → `/draft` → `/review` → `/convert`

**Publishing workflow**: `/english` → `/publish`

**Article length target**: 2500-3500 characters (Chinese) for both personas

**Conversion**: `python scripts/writing/html_converter.py writing/{persona}/articles/[name]/final.md`

**WeChat publishing**: Open `wechat.html` in browser → Select all → Copy → Paste into WeChat editor
