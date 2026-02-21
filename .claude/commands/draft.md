---
description: Generate article draft following the active persona's style guide
---

You are helping write a full article draft for a 微信公众号 (WeChat Official Account).

# Step 1 — Detect persona

Walk up the directory tree from the current working directory looking for a `.persona` file. Read the first line — that is the persona (`benyu` or `hushi`).

Fallback (if no `.persona` file found):
- If `benyu` appears in the current path → persona = `benyu`
- If `hushi` appears in the current path → persona = `hushi`
- Otherwise → ask the user which persona to use

# Step 2 — Read style guide

Read `{persona}/style_guide.md` (from repo root). This is required — the draft voice must be accurate.

# CRITICAL: Data Authenticity

**NEVER fabricate data. ONLY use:**
- Real data from user's actual sessions/work
- Published data with source URLs
- User-provided examples

**NEVER use fake attributions:**
- DO NOT attribute user's own chat messages to "我朋友说" or "朋友"
- DO NOT create fictional "friend" or "colleague" to quote the user's own words
- Instead: State user's ideas directly in first person or as general observations

**If you lack real data:**
- **ASK the user for it**
- Leave clear placeholders: `[需要真实例子: 翻译公司报价]`
- **DO NOT** invent examples to fill gaps

**This overrides all other instructions. Better an incomplete draft than fabricated data or fake attributions.**

# Core Principles

Read `writing/templates/article-structures/PRINCIPLES.md` (from repo root) for the 6 universal principles. Apply with persona voice (see style guide).

# Instructions

1. **Detect persona and read style guide** (Steps 1–2 above)

2. **Get the outline or topic**:
   - Ask if the user has an outline already (from `/outline` command)
   - If yes, read `outline.md` in the current directory
   - If no, ask for the topic and key points to cover

3. **Write the draft** following persona voice from the style guide:

   **Shared requirements (both personas):**
   - Concise and professional — every sentence adds value, no verbosity
   - Natural flowing prose — NOT bullet-point listings with bold labels
   - When presenting multiple points, weave into connected paragraphs using natural transitions
   - Example BAD: "**原因一**：..., **原因二**：..., **原因三**：..."
   - Example GOOD: "...为什么？因为...。更妙的是...。同时..."
   - Minimise English words unless necessary (technical terms, proper nouns)
   - ZERO emoji
   - No corporate jargon: "赋能", "降本增效"
   - Write in Chinese, mixing English technical terms naturally
   - Article length target: 2500–3500 characters

   **If benyu:**
   - Tone: Confrontational, sarcastic, opinionated — like talking to a colleague who won't mince words
   - Use "我" frequently, reference personal experience
   - Include self-aware humour and parenthetical asides
   - Concrete numbers: "四千多人"、"$3"、"三个人" — not "很多"、"一些"
   - Name companies to challenge and attack (at least 3–5 specific companies)
   - Memorable analogies: 永动机, 大巴司机 style
   - Language patterns to use: "实际上，..."、"恰恰相反的是，..."、"试举一例，..."、"恕我直言，..."、"所谓专家们"、"美其名曰"
   - DON'T use "这不是X，是Y" — just state Y directly
   - Opening: First two sentences must have conflict/tension — NOT "今天我们聊聊X"
   - Closing: Provocative reversal or engagement prompt, "来骂我吧" energy
   - End with: "有兴趣研究这个问题的同好，欢迎在公众号给我留言，我们一起交流讨论。" or similar

   **If hushi:**
   - Tone: Analytical, measured — like an experienced engineer thinking through a problem out loud
   - Use "我" frequently, reference personal experience
   - Intellectually curious, not confrontational
   - Comfortable with uncertainty: "我目前的理解是..."、"这一点还需要更多数据"
   - Generous to other viewpoints — analyse, don't dismiss
   - Every claim backed by data, case study, or theoretical framework
   - At least one CS/engineering/economics principle cited
   - Named companies/products for analysis and citation, not attack (at least 3–5)
   - Concrete metrics: numbers with sources
   - Counterarguments addressed genuinely — not strawmen
   - Language patterns: "如果我们从[框架]的角度来看..."、"数据显示..."、"值得注意的是..."、"这意味着..."、"一种可能的解释是..."、"[人名]指出..."
   - Opening: Intellectual hook — paradox, unresolved tension, surprising data point
   - NO sarcasm, NO mockery: never use "所谓专家们", "跳大神", "美其名曰", "恕我直言"
   - Closing: Synthesise what we know and what remains open, measured discussion invitation
   - End with: "这个问题值得更多工程师参与讨论" or similar

4. **Write the full article** in Chinese, following the article structure from the outline

5. **Save to file**: ALWAYS write to `draft.md` in the current working directory

# Important

- This should be a COMPLETE draft, not an outline or summary
- Match the persona voice exactly — reread the style guide before writing
- Be specific with company names, metrics, URLs
- NO emoji
- **CRITICAL**: You MUST write the draft to `draft.md` — do not just show it to the user
