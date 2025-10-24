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

**This rule overrides all other instructions.**

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

1. **Read the style guide**: First, read `/Users/Shared/code/benyu/templates/style_guide.md` to understand the writing style, tone, and structure patterns.

2. **Ask the user for the topic**: Ask what they want to write about. Get enough context to understand:
   - The main argument or thesis
   - The target audience
   - What type of article it should be (debunking, industry critique, true vs false problems, etc.)

3. **Select the appropriate template**: Based on the topic, choose one of these patterns from the style guide:
   - Template 1: Debunking Article (永动机模式) - for debunking popular but flawed ideas
   - Template 2: Industry Critique with Deep Analysis (云厂商模式) - for systematic industry analysis
   - Template 3: True vs False Problems (伪问题模式) - for distinguishing real from fake problems
   - Template 4: Systematic Deconstruction (基础架构部模式) - for analyzing organizational/structural issues

4. **Generate a detailed outline** that includes:
   - Article title (provocative and specific)
   - Opening hook (following the style guide patterns)
   - Main sections with bullet points
   - Specific examples to include (companies, products, people - with placeholders if user needs to fill in)
   - Technical concepts to reference
   - Analogies or metaphors to use
   - URLs or references to include (if known)
   - Conclusion approach

5. **Follow style guide principles**:
   - Be specific (name companies, products, people)
   - Use vivid language and analogies
   - Balance theory and practice
   - Include rhetorical devices (questions, imagined dialogue, etc.)
   - Plan for engagement at the end

6. **Output the outline** in a clear, structured format

# Important

- Always reference the style guide at `/Users/Shared/code/benyu/templates/style_guide.md`
- Don't create vague outlines - be specific about what examples and references to include
- Ensure the outline follows one of the proven article templates
- The outline should be detailed enough that drafting becomes straightforward
