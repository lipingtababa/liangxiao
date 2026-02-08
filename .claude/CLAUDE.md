# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **微信公众号 (WeChat Official Account) article writing system** - a monorepo with **two author personas** sharing infrastructure but with completely separate styles and voices.

The system enforces **strict data authenticity** - never fabricate examples, quotes, statistics, or attributions. All data must be real, sourced, and verifiable.

## Two Personas

### Benyu (笨鱼) - Provocative Voice
- **Directory**: `benyu/`
- **Style guide**: `benyu/style_guide.md`
- **Tone**: Confrontational, sarcastic, opinionated, challenges authority
- **Companies**: Named to challenge and attack
- **Analogies**: Vivid, everyday, mocking (永动机, 农贸市场卖豆腐)
- **Conclusions**: Provocative reversal, "来骂我吧" energy

### Vannevar - Serious/Analytical Voice
- **Directory**: `vannevar/`
- **Style guide**: `vannevar/style_guide.md`
- **Tone**: Analytical, measured, evidence-first, forward-looking
- **Companies**: Named to cite and analyse (not attack)
- **Analogies**: Structural, scientific, from engineering/economics
- **Conclusions**: Synthesis + open questions, "一起研究" energy
- **Named after**: Vannevar Bush, who wrote "As We May Think" (1945)

## Monorepo Architecture

### How Commands Work

Commands are **layered** - Claude Code walks up the directory tree, with nested commands taking precedence over root commands.

**Shared commands** (work from anywhere):
- `/brainstorm` - Research and material discovery
- `/convert` - Markdown to WeChat HTML conversion
- `/pick-chat` - Extract topics from WeChat chat data

**Persona-specific commands** (activated by working directory):
- `cd benyu && /outline` → benyu's provocative outline command
- `cd benyu && /draft` → benyu's provocative draft command
- `cd benyu && /review` → benyu's provocative review checklist
- `cd vannevar && /outline` → vannevar's analytical outline command
- `cd vannevar && /draft` → vannevar's analytical draft command
- `cd vannevar && /review` → vannevar's analytical review checklist

### Directory Structure

```
benyu/                              # repo root
├── .claude/
│   ├── CLAUDE.md                   # THIS FILE - shared project instructions
│   └── commands/
│       ├── brainstorm.md           # shared - material discovery
│       ├── convert.md              # shared - HTML conversion
│       └── pick-chat.md            # shared - chat topic extraction
│
├── templates/                      # SHARED
│   ├── article-structures/         # 5 structure types + PRINCIPLES.md
│   │   ├── PRINCIPLES.md           # 6 universal writing principles
│   │   ├── debunking/
│   │   ├── raising-valuable-question/
│   │   ├── case-and-product-study/
│   │   ├── exploration-and-hypothesis/
│   │   └── prediction-and-trend/
│   ├── wechat_styles.css
│   └── wechat_template.html
│
├── scripts/                        # SHARED
│   ├── html_converter.py           # Markdown → WeChat HTML
│   ├── prepare_chat.py             # Chat JSON → text
│   ├── analyze_topics.py
│   ├── analyze_daily_messages.py
│   └── extract_style.py
│
├── benyu/                          # PROVOCATIVE persona
│   ├── .claude/
│   │   └── commands/
│   │       ├── outline.md          # provocative outline
│   │       ├── draft.md            # provocative draft
│   │       └── review.md           # provocative review checklist
│   ├── style_guide.md              # ⭐ benyu style reference
│   └── articles/
│       ├── three-person-team/
│       ├── you_write_bugs_again/
│       └── ... (all provocative articles)
│
├── vannevar/                       # SERIOUS persona
│   ├── .claude/
│   │   └── commands/
│   │       ├── outline.md          # analytical outline
│   │       ├── draft.md            # analytical draft
│   │       └── review.md           # analytical review checklist
│   ├── style_guide.md              # ⭐ vannevar style reference
│   └── articles/
│       └── e2e-testing/
│
├── Examples/                       # SHARED - original published articles (HTML)
├── requirements.txt                # markdown>=3.5, beautifulsoup4>=4.12.0
└── .gitignore
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
1. `/brainstorm` - Research topic using WebSearch, collect 10+ interesting findings
2. `/outline` - Select article structure, generate detailed framework
3. `/draft` - Write following the active persona's style_guide.md
4. `/review` - Check against the active persona's checklist
5. `/convert` - Generate WeChat-compatible HTML

**All commands MUST write output to files:**
- `brainstorm.md` - Research findings
- `outline.md` - Article structure
- `draft.md` or `final.md` - Article content
- `wechat.html` - HTML for publishing

### 3. Persona-Aware Style Enforcement

**Determine the active persona from working directory:**
- Working in `benyu/` or `benyu/articles/*` → read `benyu/style_guide.md`
- Working in `vannevar/` or `vannevar/articles/*` → read `vannevar/style_guide.md`

**Six universal principles** (from `templates/article-structures/PRINCIPLES.md`) apply to BOTH personas, but interpreted differently:

| Principle | Benyu | Vannevar |
|-----------|-------|----------|
| 标题即半篇文章 | Provocative, makes you want to argue | Precise, states the thesis |
| 首段必须抓人 | Conflict, tension | Paradox, surprising observation |
| 具体事实和数字 | Trigger emotions | Support analysis |
| 听起来可操作 | "Here's what's wrong AND what to do" | "Here's a framework to think about this" |
| 打大公司/权威 | Challenge and attack | Cite and analyse |
| 读者焦虑 | Poke the wound | Offer honest analysis |

### 4. Article Structure Types

Choose from 5 patterns in `templates/article-structures/`:

1. **Debunking (驳斥)** - X is believed → X is wrong → here's reality
2. **Raising Valuable Question (提出问题)** - Reframe definition → challenge assumptions
3. **Case and Product Study (案例与产品研究)** - What happened → what it reveals
4. **Exploration & Hypothesis (探索与假说)** - Problem → experiment → framework
5. **Prediction/Trend Analysis (趋势预测)** - Current state → forces → future

### 5. WeChat Conversion Requirements

**Before running `/convert`:**
1. Extract all markdown links `[text](url)` from article
2. Replace inline links with plain text (WeChat doesn't support hyperlinks in body)
3. Add **引用来源** section at end with numbered list of URLs

**Conversion process:**
```bash
python scripts/html_converter.py benyu/articles/[name]/final.md
# or
python scripts/html_converter.py vannevar/articles/[name]/final.md
```

## Common Development Tasks

### Write a New Benyu Article

```bash
cd benyu
mkdir -p articles/my-new-article
cd articles/my-new-article

/brainstorm [topic]    # shared command, works everywhere
/outline               # picks up benyu/.claude/commands/outline.md
/draft                 # picks up benyu/.claude/commands/draft.md
/review                # picks up benyu/.claude/commands/review.md
/convert               # shared command
```

### Write a New Vannevar Article

```bash
cd vannevar
mkdir -p articles/my-new-article
cd articles/my-new-article

/brainstorm [topic]    # shared command, works everywhere
/outline               # picks up vannevar/.claude/commands/outline.md
/draft                 # picks up vannevar/.claude/commands/draft.md
/review                # picks up vannevar/.claude/commands/review.md
/convert               # shared command
```

### Extract Topics from WeChat Chats

```bash
python scripts/prepare_chat.py <chatroom_dir> [date]
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
- `aichat/chats/<id>_<name>/` - each chatroom has a directory with daily JSON files and `_metadata.json`
- `_metadata.json` contains `media_dir` pointing to Google Drive path where images are stored
- Images path pattern: `/Users/machi/Library/CloudStorage/GoogleDrive-hellomarch@gmail.com/My Drive/wechat-images/<chatroom_name>/`

**During /brainstorm**: Always search aichat for relevant chatroom data, including images from Google Drive.

**CRITICAL**: User's own chat messages are their OWN ideas - NEVER attribute to fictional "朋友说" or "我朋友"

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

Required: `markdown>=3.5`, `beautifulsoup4>=4.12.0`

## Important Notes

- **Style guide is persona-specific**: `benyu/style_guide.md` or `vannevar/style_guide.md`
- **File output is mandatory**: All slash commands MUST write to files
- **Article directory context**: Commands assume you're in `{persona}/articles/[name]/`
- **No emoji policy**: Zero emoji in published articles for both personas
- **Data authenticity overrides everything**: Better to ask user or leave placeholder than fabricate

## Quick Reference

**Benyu style guide**: `benyu/style_guide.md`
**Vannevar style guide**: `vannevar/style_guide.md`
**Shared principles**: `templates/article-structures/PRINCIPLES.md`

**Standard workflow**: `/brainstorm` → `/outline` → `/draft` → `/review` → `/convert`

**Article length target**: 2500-3500 characters (Chinese) for both personas

**Conversion**: `python scripts/html_converter.py {persona}/articles/[name]/final.md`

**Publishing**: Open `wechat.html` in browser → Select all → Copy → Paste into WeChat editor
