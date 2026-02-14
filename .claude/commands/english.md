---
description: Translate Chinese article to English for magong.se blog
---

You are translating a Chinese 微信公众号 article into an English blog post for magong.se — a blog by MaGong (瑞典马工) aimed at international engineering readers.

# Instructions

1. **Get the source article**: Ask the user for the file path to the Chinese article (`draft.md` or `final.md`). Read it fully.

2. **Read existing English posts for tone reference**: Read 2-3 posts from `posts/` (from repo root) to match the established English voice — direct, opinionated, conversational, no corporate jargon.

3. **Translate and adapt** following these rules:

## Translation Principles

**This is adaptation, not literal translation.** The goal is an article that reads like it was written in English by an experienced engineer.

### Conciseness
- **Cut aggressively** — Chinese articles tend to be longer and more repetitive than English readers expect
- Remove filler phrases (随着技术的发展, 众所周知, 值得一提的是)
- Merge paragraphs that make the same point twice
- If a section can be said in half the words, say it in half the words
- Target: English version should be noticeably shorter than the Chinese original

### Link Replacement
- **WeChat links (`mp.weixin.qq.com`) are inaccessible outside China** — MUST be replaced
- For each WeChat link, search for an equivalent English source:
  - If the referenced article/concept has an English equivalent, link to that
  - If the author has an English blog/Twitter, link there
  - If no equivalent exists, describe the reference inline and remove the link
- Keep non-WeChat links (GitHub, Medium, company blogs, etc.) as-is
- Add links to English sources where they strengthen the argument

### Case Studies and Examples
- **Chinese-specific examples may not resonate internationally** — flag these for the user
- Suggest replacements when a Chinese company/product has a better-known international equivalent
- Examples that work well in Chinese tech circles but are obscure internationally should be either:
  - Replaced with an international equivalent
  - Kept but with brief context added ("PingCAP, the company behind TiDB...")
  - Removed if the point can stand without the example
- **Ask the user** if you're unsure whether to keep or replace a case

### Cultural Adaptation
- Chinese internet slang and memes → remove or replace with natural English phrasing
- 自嘲 (self-deprecation) → works in English too, keep it
- References to Chinese tech ecosystem (微信, 支付宝, 大厂) → add brief context or replace
- Chinese idioms → translate the meaning, not the words (东施效颦 → "cargo-culting" or "blindly copying")
- 朋友/同事 references → "colleagues", "peers", or name them if public figures

### Tone
- Match the persona tone of the original:
  - **戚本禹 articles**: Keep the edge, the provocative stance, the challenge to authority
  - **胡适 articles**: Keep the analytical rigour, the measured reasoning, the honest uncertainty
- But adapt for English-speaking engineering audience:
  - Less rhetorical flourish, more directness
  - English readers expect claims to be backed immediately (don't build up to the point as long)
  - Shorter paragraphs

### Technical Terms
- Chinese translations of English tech terms → revert to original English
- Keep standard abbreviations: CI/CD, API, SaaS, LLM, SDLC
- Chinese-origin tech terms (内卷, 996) → translate with brief context on first use

## Output Format

### Front Matter
Generate proper front matter matching the existing posts format:

```yaml
---
title: "English Title Here"
date: "YYYY-MM-DD"
author: "MaGong"
category: "Category"
tags: []
description: >
  One-sentence description for SEO and social sharing.
---
```

- **title**: Translate or adapt the Chinese title — make it work for English readers
- **date**: Use the original article's publication date
- **category**: Match existing categories (AI Coding, AI Thinking, Engineering)
- **description**: Write a compelling one-sentence summary

### Article Body
- Use markdown with `##` subheadings
- End with: `---\n\n*Originally written in Chinese. Translated by the author.*`
- No emoji

### Suggestions Section
After the translated article, add a **separate section** (NOT part of the article) with:

```markdown
---

## Translation Notes (for author review, not published)

### Links Replaced
- [original WeChat URL] → [replacement URL] (reason)

### Cases Adapted
- [original example] → [adapted version] (reason for change)

### Suggested Changes
- [specific suggestion with reasoning]

### Flagged for Review
- [anything you're unsure about — cultural references, claims, examples]
```

4. **Write the output** to `posts/[slug].md` where slug is a kebab-case English title.

5. **Show the user** the Translation Notes section and ask for approval before finalising.

# Important

- NEVER fabricate data, quotes, or examples — this rule carries over from the Chinese original
- If the Chinese article contains fabricated-looking data, flag it
- The English version should feel NATIVE, not translated
- When in doubt about cutting vs keeping content, CUT — English readers prefer concise
- Always preserve the author's core argument and unique insights
- **CRITICAL**: Write the translated article to a file in `posts/`
