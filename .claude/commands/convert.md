---
description: Convert article to all platform formats + generate images
---

You are converting a finished Chinese article into all publishing formats.

# What this command produces

```
articles/[name]/
├── weixin.html        ← WeChat HTML (script-generated)
├── zhihu.md           ← Zhihu article (script-generated)
├── xhs.md             ← Xiaohongshu note (LLM-generated)
├── english.md         ← English translation (LLM-generated)
└── images/
    ├── cover-xhs.jpg     3:4  portrait  (Imagen 4)
    ├── cover-weixin.jpg  16:9 landscape (Imagen 4)
    ├── section-1.jpg     1:1  square    (Imagen 4)
    ├── section-2.jpg     1:1  square    (Imagen 4)
    ├── section-3.jpg     1:1  square    (Imagen 4)
    └── manifest.json
```

# Instructions

## Step 1 — Locate the article

Detect article directory from current working directory or ask the user.
Detect persona — try in this order:
1. Walk up the directory tree looking for a `.persona` file; read its first line
2. Path contains `benyu` → persona = `benyu`; path contains `hushi` → persona = `hushi`
3. Ask the user

Verify `draft.md` (or `final.md`) exists. Read it fully — you'll need it for the LLM steps.

## Step 2 — Run all scripts (do this first, in parallel where possible)

### 2a — Images
```bash
python scripts/writing/image_generator.py <article_dir> --persona <persona>
```
Generates 5 images into `<article_dir>/images/`. Runs independently.

### 2b — WeChat HTML
```bash
python scripts/writing/article_converter.py weixin <article_dir>
```
Extracts links → reference list, runs html_converter, writes `weixin.html`.

### 2c — Zhihu markdown
```bash
python scripts/writing/article_converter.py zhihu <article_dir>
```
Cleans markdown, adds footer, writes `zhihu.md`.

Run 2a, 2b, 2c. Report any errors before continuing.

## Step 3 — XHS condensation (LLM)

Read `writing/templates/platform-adapters/xhs-adapter.md` for full rules.

Condense the article into an XHS note:
- **Title**: ≤20 chars — sharpest hook from the article
- **Body**: 300-600 chars — 3-5 punchy paragraphs, no links, no headings, first-person "分享" energy
- **Hashtags**: 5-8 tags at end (2-3 topic, 2-3 niche, 1-2 emotion/behaviour)

Write to `<article_dir>/xhs.md`.

## Step 4 — English translation (LLM)

Follow all rules in `.claude/commands/english.md`.

Key rules:
- Aggressive cutting — English version noticeably shorter
- Replace WeChat links with English sources
- Adapt Chinese-specific examples for international readers
- Proper frontmatter (title, date, author: MaGong, category, description)
- End with: `---\n\n*Originally written in Chinese. Translated by the author.*`

Write to `<article_dir>/english.md` (NOT to `posts/` — `/publish` copies it over).

## Step 5 — Report

```
✓ Conversion complete: [article title]

Scripts ran:
  weixin.html    — WeChat HTML, [N] links moved to references
  zhihu.md       — [N] chars
  images/        — [N] images generated (cover-xhs 3:4, cover-weixin 16:9, section-N 1:1)

LLM outputs:
  xhs.md         — [N] chars, [N] hashtags
  english.md     — [N] words, [N] WeChat links replaced

Run /publish to distribute.
```

# Important

- Scripts must run successfully before LLM steps — if a script fails, diagnose and fix
- NEVER fabricate data in any adapted version
- `english.md` goes to the article directory, not `posts/`
- If `images/` generation fails on some images, note it but continue — partial image sets are fine
