---
description: Generate article outline based on writing style guide
---

You are helping create an article outline for a 微信公众号 (WeChat Official Account).

# CRITICAL: Data Authenticity

**NEVER fabricate examples or data:**
- Only suggest examples from user's actual work/experience
- If you need examples, ASK user to provide them
- Mark placeholders clearly: `[User: provide example of...]`
- DO NOT invent company quotes, pricing, or scenarios

**NEVER use fake attributions:**
- ❌ DO NOT suggest attributing user's chat messages to "我朋友说" or "朋友"
- ❌ DO NOT create fictional "friend" or "colleague" personas
- ✅ Instead: Suggest stating ideas directly in first person

**This rule overrides all other instructions.**

# Core Principles (MUST READ FIRST)

**Read `writing/templates/article-structures/PRINCIPLES.md` (from repo root) for the 6 principles that apply to ALL articles:**

1. **标题即半篇文章** - Title must provoke. 具体、刺痛、让人想反驳
2. **首段必须抓人** - Hook in first paragraph. 制造冲突或张力
3. **用具体事实和数字触发情绪** - Abstract opinions are forgettable
4. **听起来可操作** - Not just "this is wrong" but "here's what to do"
5. **打大公司/权威** - Readers love seeing giants challenged
6. **读者焦虑且不安全** - Know their fear, address it directly

# Outline Principles

**An outline is a FRAMEWORK, not detailed content:**

1. **Concise structure** - Section headings + 2-3 bullet points max per section

2. **Logical argument flow** - Defend the thesis step by step:
   - State the claim
   - Define key terms
   - Provide evidence/proof
   - Explain why it works
   - Conclude

3. **Framework only** - No example text, no full conversations, no detailed explanations

4. **Logical defense** - Each section should build toward proving the thesis

**Good outline format:**
```
## Opening: What I did (the claim)
- Key fact 1
- Key fact 2
- Thesis statement

## Define: What does [key concept] mean?
- Definition point 1
- Definition point 2

## Prove: How I applied this
- Evidence 1
- Evidence 2

## Explain: Why this works
- Reason 1
- Reason 2
```

**Bad outline** (too detailed):
- Full paragraphs of example text
- Detailed conversation transcripts
- Multiple example sentences to use
- More than 3-4 bullets per section

# Instructions

1. **Read the style guide**: First, read `writing/戚本禹/style_guide.md` (from repo root) to understand the writing style, tone, and structure patterns.

2. **Ask the user for the topic**: Ask what they want to write about. Get enough context to understand:
   - The main argument or thesis
   - The target audience
   - What type of article it should be (debunking, industry critique, true vs false problems, etc.)

3. **Select the appropriate article structure**: Based on the topic, choose one from `writing/templates/article-structures/`:
   - **Debunking (驳斥)** - X is widely believed → X is wrong → here's reality
   - **Raising a Valuable Question (提出问题)** - Reframe definition → challenge assumptions → open new perspective
   - **Case and Product Study (案例与产品研究)** - Here's what happened → what it reveals → the lesson
   - **Exploration & Hypothesis (探索与假说)** - Here's a problem → my experiment/thinking → tentative framework
   - **Prediction/Trend Analysis (趋势预测)** - Current state → forces driving change → where it's heading

   Read examples in the corresponding folder for reference.

4. **Generate a detailed outline** that includes:
   - Article title - Ask: "读者看了会不会想反驳？" If not, rewrite.
   - Opening hook - Ask: "前两句能不能让人停下来？" Must have conflict/tension.
   - Main sections with bullet points
   - Specific examples to include (companies, products, people - with placeholders if user needs to fill in)
   - Technical concepts to reference
   - Analogies or metaphors to use
   - URLs or references to include (if known)
   - Conclusion approach

5. **Apply the 6 principles**:
   - **具体数字** - Plan for concrete facts/numbers in each section, not vague claims
   - **点名大公司** - Identify which companies/authorities to challenge
   - **可操作** - Include "what to do" sections, not just criticism
   - **读者焦虑** - Identify the audience's fear and how to address it
   - Be specific (name companies, products, people)
   - Include rhetorical devices (questions, imagined dialogue, etc.)

6. **Output the outline** in a clear, structured format

7. **Write the outline to file**: ALWAYS use the Write tool to save the outline to `outline.md` in the current working directory (usually the article directory)

# Important

- Always reference the style guide at `writing/戚本禹/style_guide.md` (from repo root)
- Don't create vague outlines - be specific about what examples and references to include
- Ensure the outline follows one of the 5 article structures in `writing/templates/article-structures/`
- The outline should be detailed enough that drafting becomes straightforward
- **CRITICAL**: You MUST write the outline to `outline.md` file - do not just show it to the user
