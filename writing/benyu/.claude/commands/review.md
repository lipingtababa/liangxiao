---
description: Review article against the style guide checklist
---

You are reviewing a 微信公众号 article against the established style guide.

# Instructions

1. **Read the principles and style guide**:
   - First, read `writing/templates/article-structures/PRINCIPLES.md` (from repo root) for the 6 core principles
   - Then read `writing/benyu/style_guide.md` (from repo root) for detailed requirements

2. **Ask for the article**: Request the article text or file path to review.

3. **Perform comprehensive review** using the style guide checklist:

## Data Authenticity Check (CRITICAL - Check First)
- [ ] All examples are from real sources (not fabricated)
- [ ] All quotes are actual quotes (not invented)
- [ ] All statistics have verifiable sources
- [ ] All company/product names are real (not made up)
- [ ] All pricing/cost comparisons use real data
- [ ] No "某公司", vague invented scenarios
- [ ] **NO fake "朋友" attributions** - User's own chat messages must NOT be attributed to fictional "朋友说" or "我朋友"
- [ ] User's ideas stated directly in first person, NOT through fake third-person personas

**If ANY data appears fabricated OR fake attributions found, FAIL the review immediately and list all violations.**

## Specificity Check
- [ ] Named at least 3-5 specific companies/products
- [ ] Named specific people (colleagues, friends, industry figures)
- [ ] Included at least 1 URL/link
- [ ] Used concrete numbers/metrics (percentages, years, costs)
- [ ] Gave specific technical details (product names, versions, APIs)

## Argumentation Check
- [ ] Clear thesis stated early
- [ ] Theoretical foundation provided (Shannon, physics, CS principles)
- [ ] At least 2-3 concrete examples supporting argument
- [ ] Addressed likely objections (imagined dialogue or explicit)
- [ ] Offered alternatives/solutions, not just criticism
- [ ] Acknowledged nuance or limitations where appropriate

## 6 Principles Check (CRITICAL)
- [ ] **标题即半篇文章** - 读者看了会不会想反驳？具体、刺痛、不是公式化
- [ ] **首段必须抓人** - 前两句有冲突/张力吗？还是"今天我们聊聊X"？
- [ ] **具体数字触发情绪** - 有"四千多人"、"$3"这样的数字吗？还是"很多"、"一些"？
- [ ] **听起来可操作** - 有"怎么办"部分吗？还是只有批评？
- [ ] **打大公司/权威** - 点名批评了哪个大公司？还是"某些公司"？
- [ ] **读者焦虑** - 读者的焦虑是什么？文章有没有回应？

## Style Check
- [ ] **CONCISE & PROFESSIONAL** - No verbosity, gets to the point, every sentence adds value
- [ ] At least one memorable analogy or metaphor
- [ ] Conversational tone (not academic or corporate)
- [ ] Mix of Chinese and English terminology
- [ ] At least one rhetorical question
- [ ] Personal voice evident ("我", experience references)
- [ ] Sarcastic or vivid language for bad practices

## Structure Check
- [ ] Sufficient depth (doesn't skim surface)
- [ ] Progressive argument building
- [ ] Used subheadings if complex topic
- [ ] Blockquotes for cited content where appropriate
- [ ] Clear conclusion or synthesis

## Engagement Check
- [ ] Ends with call to action, discussion prompt, or engagement request
- [ ] Provocative or memorable final line
- [ ] OR humble invitation for critique/discussion

## What to Avoid Check
- [ ] No vague corporate jargon (unless ironic)
- [ ] No unsupported claims
- [ ] No emoji
- [ ] **No verbosity or redundancy** - Not rambling like Trump
- [ ] Not too short/superficial
- [ ] Hasn't accepted hype uncritically
- [ ] Named names when relevant (didn't hedge unnecessarily)

## Link Check
- [ ] **《》symbols converted to links** - For each 《term》, search for a Wikipedia or other authoritative reference link and convert to markdown format: [term](url). For example, 《一人公司》should become [一人公司](https://www.goodreads.com/book/show/37570605-company-of-one)

4. **Provide detailed feedback** in this format:

### ✅ Strengths
List what the article does well, with specific examples

### ⚠️ Issues Found
List problems organized by category (Specificity, Argumentation, Style, Structure, Engagement)

### 🔧 Specific Recommendations
Provide concrete suggestions for improvement:
- Missing examples to add (companies, products, people)
- Language patterns to incorporate (with examples from style guide)
- Structural improvements
- Tone adjustments needed

### 📊 Checklist Score
Show which checklist items passed/failed

5. **Suggest revisions**: For any failed checklist items, provide specific text suggestions using the style guide patterns.

# Important

- Be thorough and specific in your review
- Reference the style guide patterns and examples
- Don't just say "add more examples" - suggest WHAT examples
- Provide actual text snippets showing how to apply style guide patterns
- Focus on making the article match the analyzed published articles
