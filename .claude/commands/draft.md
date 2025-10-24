---
description: Generate article draft following the style guide
---

You are helping write a full article draft for a 微信公众号 (WeChat Official Account).

# CRITICAL: Data Authenticity

**NEVER fabricate data. ONLY use:**
- Real data from user's actual sessions/work
- Published data with source URLs
- User-provided examples

**If you lack real data:**
- **ASK the user for it**
- Leave clear placeholders: `[需要真实例子: 翻译公司报价]`
- **DO NOT** invent examples to fill gaps

**This overrides all other instructions. Better an incomplete draft than fabricated data.**

# Instructions

1. **Read the style guide**: First, read `/Users/Shared/code/benyu/templates/style_guide.md` to fully understand:
   - Tone and voice
   - Language patterns and favorite phrases
   - Argumentation style
   - Technical terminology usage
   - What to avoid and what to embrace

2. **Get the outline or topic**:
   - Ask if the user has an outline already (from `/outline` command)
   - If yes, use that outline
   - If no, ask for the topic and key points they want to cover

3. **Write the draft** following these critical requirements:

   **Tone & Voice:**
   - Conversational and casual (like talking to a colleague)
   - Highly opinionated with strong stances
   - Use "我" frequently, reference personal experience
   - Include self-aware humor and parenthetical asides

   **Content:**
   - Name specific companies, products, people (at least 3-5)
   - Include concrete numbers and metrics
   - Add at least 1 URL/link
   - Use memorable analogies (永动机, 农贸市场卖豆腐 style)
   - Mix theoretical foundations (Shannon, CS principles) with practical examples

   **Language patterns (use these extensively):**
   - Opening: "前两天...", "作为...的狂热信仰者，...", etc.
   - Transitions: "实际上，...", "换句话说，...", "恰恰相反的是，..."
   - Examples: "试举一例，...", "举例来说，..."
   - Critique: "这个听起来挺好的，但是...", "恕我直言，...", "说句难听的，..."
   - Sarcasm: "所谓专家们", "老师傅", "美其名曰", "跳大神"
   - Questions: "这玩意真的有用吗？", "为什么搞成这样子？"

   **Structure:**
   - Strong opening hook (recent event, specific observation)
   - Progressive argument building
   - Use subheadings for complex topics
   - Blockquotes for cited content
   - Memorable conclusion with engagement prompt

   **What to AVOID:**
   - Emoji (ZERO emoji)
   - Corporate jargon (unless ironic): "赋能", "降本增效"
   - Vague statements without examples
   - Over-formality or academic tone
   - Short superficial treatment

4. **Write the full article** in Chinese, following the selected template structure

5. **End with engagement**:
   - "有兴趣研究这个问题的同好，欢迎在公众号给我留言，我们一起交流讨论。"
   - Or similar engagement prompt from the style guide

# Output

Write the complete article in markdown format, ready to be converted to WeChat HTML.

# Important

- This should be a COMPLETE draft, not an outline
- Use extensive direct quotes and examples from the style guide's language patterns
- Match the conversational, opinionated tone exactly
- Be specific with company names, metrics, URLs
- NO emoji
- Write in Chinese (mix English technical terms naturally)
