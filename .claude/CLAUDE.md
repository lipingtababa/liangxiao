# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **combined monorepo** with two systems:

1. **magong.se website** — Next.js English blog translating WeChat articles for international readers
2. **Writing system** — Dual-persona WeChat article factory (戚本禹 provocative + 胡适 analytical)

The pipeline: **write (Chinese)** → **translate** → **publish (English)**

The writing system enforces **strict data authenticity** — never fabricate examples, quotes, statistics, or attributions. All data must be real, sourced, and verifiable.

## Two Personas (Writing System)

### 戚本禹 - Provocative Voice
- **Directory**: `writing/戚本禹/`
- **Style guide**: `writing/戚本禹/style_guide.md`
- **Tone**: Confrontational, sarcastic, opinionated, challenges authority
- **Companies**: Named to challenge and attack
- **Analogies**: Vivid, everyday, mocking (永动机, 农贸市场卖豆腐)
- **Conclusions**: Provocative reversal, "来骂我吧" energy
- **Named after**: 戚本禹 (1931-2016)，毛泽东时代政论家，中央文革小组成员，以犀利的政论文章闻名，被编辑黎澍称赞为"能成为新中国的梁启超，笔端常带感情"

### 胡适 - Serious/Analytical Voice
- **Directory**: `writing/胡适/`
- **Style guide**: `writing/胡适/style_guide.md`
- **Tone**: Analytical, measured, evidence-first, forward-looking
- **Companies**: Named to cite and analyse (not attack)
- **Analogies**: Structural, scientific, from engineering/economics
- **Conclusions**: Synthesis + open questions, "一起研究" energy
- **Named after**: 胡适 (1891-1962)，中国新文化运动领袖，提倡白话文、科学方法和实证精神

## Monorepo Architecture

### How Commands Work

Commands are **layered** — Claude Code walks up the directory tree, with nested commands taking precedence over root commands.

**Shared commands** (work from anywhere):
- `/brainstorm` — Research and material discovery
- `/convert` — Markdown to WeChat HTML conversion
- `/pick-chat` — Extract topics from WeChat chat data

**Persona-specific commands** (activated by working directory):
- `cd writing/戚本禹 && /outline` → 戚本禹's provocative outline command
- `cd writing/戚本禹 && /draft` → 戚本禹's provocative draft command
- `cd writing/戚本禹 && /review` → 戚本禹's provocative review checklist
- `cd writing/胡适 && /outline` → 胡适's analytical outline command
- `cd writing/胡适 && /draft` → 胡适's analytical draft command
- `cd writing/胡适 && /review` → 胡适's analytical review checklist

### Directory Structure

```
liangxiao/                          # repo root
├── .claude/
│   ├── CLAUDE.md                   # THIS FILE
│   └── commands/
│       ├── brainstorm.md           # shared — material discovery
│       ├── convert.md              # shared — HTML conversion
│       └── pick-chat.md            # shared — chat topic extraction
│
├── app/                            # Next.js website
├── components/                     # React components
├── lib/                            # posts.ts, seo.ts
├── posts/                          # Published English articles
├── public/                         # Static assets
├── __tests__/                      # Jest tests
│
├── writing/                        # Article writing system
│   ├── README.md
│   ├── 戚本禹/                      # PROVOCATIVE persona
│   │   ├── .claude/commands/       # /outline, /draft, /review
│   │   ├── style_guide.md
│   │   ├── brainstorm.md
│   │   └── articles/
│   ├── 胡适/                   # SERIOUS persona
│   │   ├── .claude/commands/       # /outline, /draft, /review
│   │   ├── style_guide.md
│   │   └── articles/
│   └── templates/                  # Article structure templates
│       ├── article-structures/     # 5 structure types + PRINCIPLES.md
│       ├── wechat_styles.css
│       └── wechat_template.html
│
├── scripts/
│   ├── website/                    # Website scripts (extraction, SEO)
│   └── writing/                    # Writing scripts (HTML conversion, chat analysis)
│
├── aichat -> /Users/machi/aichat   # Symlink (gitignored)
└── requirements.txt
```

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

### 2. Article Writing Workflow

**Standard sequence** (same for both personas):
1. `/brainstorm` — Research topic using WebSearch, collect 10+ interesting findings
2. `/outline` — Select article structure, generate detailed framework
3. `/draft` — Write following the active persona's style_guide.md
4. `/review` — Check against the active persona's checklist
5. `/convert` — Generate WeChat-compatible HTML

**All commands MUST write output to files:**
- `brainstorm.md` — Research findings
- `outline.md` — Article structure
- `draft.md` or `final.md` — Article content
- `wechat.html` — HTML for publishing

### 3. Persona-Aware Style Enforcement

**Determine the active persona from working directory:**
- Working in `writing/戚本禹/` or `writing/戚本禹/articles/*` → read `writing/戚本禹/style_guide.md`
- Working in `writing/胡适/` or `writing/胡适/articles/*` → read `writing/胡适/style_guide.md`

**Six universal principles** (from `writing/templates/article-structures/PRINCIPLES.md`) apply to BOTH personas, but interpreted differently:

| Principle | 戚本禹 | 胡适 |
|-----------|-------|----------|
| 标题即半篇文章 | Provocative, makes you want to argue | Precise, states the thesis |
| 首段必须抓人 | Conflict, tension | Paradox, surprising observation |
| 具体事实和数字 | Trigger emotions | Support analysis |
| 听起来可操作 | "Here's what's wrong AND what to do" | "Here's a framework to think about this" |
| 打大公司/权威 | Challenge and attack | Cite and analyse |
| 读者焦虑 | Poke the wound | Offer honest analysis |

### 4. Article Structure Types

Choose from 5 patterns in `writing/templates/article-structures/`:

1. **Debunking (驳斥)** — X is believed → X is wrong → here's reality
2. **Raising Valuable Question (提出问题)** — Reframe definition → challenge assumptions
3. **Case and Product Study (案例与产品研究)** — What happened → what it reveals
4. **Exploration & Hypothesis (探索与假说)** — Problem → experiment → framework
5. **Prediction/Trend Analysis (趋势预测)** — Current state → forces → future

### 5. WeChat Conversion Requirements

**Before running `/convert`:**
1. Extract all markdown links `[text](url)` from article
2. Replace inline links with plain text (WeChat doesn't support hyperlinks in body)
3. Add **引用来源** section at end with numbered list of URLs

**Conversion process:**
```bash
python scripts/writing/html_converter.py writing/戚本禹/articles/[name]/final.md
# or
python scripts/writing/html_converter.py writing/胡适/articles/[name]/final.md
```

## Common Development Tasks

### Write a New 戚本禹 Article

```bash
cd writing/戚本禹
mkdir -p articles/my-new-article
cd articles/my-new-article

/brainstorm [topic]    # shared command, works everywhere
/outline               # picks up writing/戚本禹/.claude/commands/outline.md
/draft                 # picks up writing/戚本禹/.claude/commands/draft.md
/review                # picks up writing/戚本禹/.claude/commands/review.md
/convert               # shared command
```

### Write a New 胡适 Article

```bash
cd writing/胡适
mkdir -p articles/my-new-article
cd articles/my-new-article

/brainstorm [topic]    # shared command, works everywhere
/outline               # picks up writing/胡适/.claude/commands/outline.md
/draft                 # picks up writing/胡适/.claude/commands/draft.md
/review                # picks up writing/胡适/.claude/commands/review.md
/convert               # shared command
```

### Extract Topics from WeChat Chats

```bash
python scripts/writing/prepare_chat.py <chatroom_dir> [date]
/pick-chat
```

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

## Working with WeChat Chat Data

**aichat repo**: `aichat/` is a symlink to a separate repo that syncs WeChat chat data. Structure:
- `aichat/chats/<id>_<name>/` — each chatroom has a directory with daily JSON files and `_metadata.json`
- `_metadata.json` contains `media_dir` pointing to Google Drive path where images are stored
- Images path pattern: `/Users/machi/Library/CloudStorage/GoogleDrive-hellomarch@gmail.com/My Drive/wechat-images/<chatroom_name>/`

**During /brainstorm**: Always search aichat for relevant chatroom data, including images from Google Drive.

**CRITICAL**: User's own chat messages are their OWN ideas — NEVER attribute to fictional "朋友说" or "我朋友"

## Git and Permissions

When making commits:
- Use British spelling in all written output
- Follow project commit message conventions (short, concise)
- Add co-credit in commit messages:
  ```
  <main commit message>

  Generated with [Claude Code](https://claude.ai/code)
  via [Happy](https://happy.engineering)

  Co-Authored-By: Claude <noreply@anthropic.com>
  Co-Authored-By: Happy <yesreply@happy.engineering>
  ```

## Python Dependencies

```bash
pip install -r requirements.txt
```

## Important Notes

- **Style guide is persona-specific**: `writing/戚本禹/style_guide.md` or `writing/胡适/style_guide.md`
- **File output is mandatory**: All slash commands MUST write to files
- **Article directory context**: Commands assume you're in `writing/{persona}/articles/[name]/`
- **No emoji policy**: Zero emoji in published articles for both personas
- **Data authenticity overrides everything**: Better to ask user or leave placeholder than fabricate

## Quick Reference

**戚本禹 style guide**: `writing/戚本禹/style_guide.md`
**胡适 style guide**: `writing/胡适/style_guide.md`
**Shared principles**: `writing/templates/article-structures/PRINCIPLES.md`

**Standard workflow**: `/brainstorm` → `/outline` → `/draft` → `/review` → `/convert`

**Article length target**: 2500-3500 characters (Chinese) for both personas

**Conversion**: `python scripts/writing/html_converter.py writing/{persona}/articles/[name]/final.md`

**Publishing**: Open `wechat.html` in browser → Select all → Copy → Paste into WeChat editor
