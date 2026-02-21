---
description: Generate article outline based on active persona
---

You are helping create an article outline for a 微信公众号 (WeChat Official Account).

# Step 1 — Detect persona

Walk up the directory tree from the current working directory looking for a `.persona` file. Read the first line — that is the persona (`benyu` or `hushi`).

Fallback (if no `.persona` file found):
- If `benyu` appears in the current path → persona = `benyu`
- If `hushi` appears in the current path → persona = `hushi`
- Otherwise → ask the user which persona to use

# CRITICAL: Data Authenticity

**NEVER fabricate examples or data:**
- Only suggest examples from user's actual work/experience
- If you need examples, ASK user to provide them
- Mark placeholders clearly: `[User: provide example of...]`
- DO NOT invent company quotes, pricing, or scenarios

**NEVER use fake attributions:**
- DO NOT suggest attributing user's chat messages to "我朋友说" or "朋友"
- DO NOT create fictional "friend" or "colleague" personas
- Instead: Suggest stating ideas directly in first person

**This rule overrides all other instructions.**

# Core Principles (MUST READ FIRST)

Read `writing/templates/article-structures/PRINCIPLES.md` (from repo root) for the 6 principles that apply to ALL articles.

Apply them with persona-specific framing:

| Principle | benyu | hushi |
|-----------|-------|-------|
| 标题即半篇文章 | Provocative — makes you want to argue | Precise — states the question/thesis |
| 首段必须抓人 | Conflict, tension | Paradox, surprising observation |
| 具体事实和数字 | Trigger emotions | Support analysis |
| 听起来可操作 | "Here's what's wrong AND what to do" | "Here's a framework to think about this" |
| 打大公司/权威 | Challenge and attack | Cite and analyse |
| 读者焦虑 | Poke the wound | Offer honest analysis |

# Opening Must Start From a Real Question

**NEVER open with private conversations, chatroom debates, or "前两天有人说..."**

The opening must start from something the AUDIENCE cares about — a verifiable fact, a universally felt problem, a paradox worth examining.

**Bad openings:**
- "前两天群里有人争论..." — nobody cares about your chatroom
- "最近和朋友讨论了一个话题..." — vague, no tension
- "在一个微信群里看到..." — insider context, audience excluded

**Good openings (benyu):**
- Start with a verifiable, surprising fact that creates tension
- Start with a universal experience the audience has felt
- Start with a concrete data point that challenges conventional wisdom

**Good openings (hushi):**
- Start with a paradox or surprising observation grounded in public data
- Start with a question the audience has wondered about but hasn't articulated
- Start with two contradictory facts that demand explanation

**Test:** Would a stranger who knows nothing about your social circle find the first sentence interesting? If not, rewrite.

Chat data and group discussions are valuable as **evidence** later in the article, not as the opening hook.

# Outline Principles

**An outline is a FRAMEWORK, not detailed content:**
- Section headings + 2-3 bullet points max per section
- Framework only — no example text, no full conversations, no detailed explanations
- Logical argument flow defending the thesis step by step

**benyu outline format:**
```
## Opening: The claim (conflict/tension)
- Surprising fact or universally felt problem
- Thesis statement

## Define: What does [key concept] mean?
- Definition point 1
- Definition point 2

## Prove: How I applied this
- Evidence 1
- Evidence 2

## Explain: Why this works / what to do
- Companies to challenge
- Actionable recommendation

## Conclusion: Provocative reversal
- "来骂我吧" energy
```

**hushi outline format:**
```
## Opening: The paradox / observation
- Surprising data point or tension
- Why this matters now
- Thesis or question

## Frame: Theoretical context
- Relevant framework (Goodhart's Law, CAP theorem, etc.)
- How it applies here

## Evidence 1: [Case/data]
- What happened
- What it reveals

## Evidence 2: [Case/data]
- What happened
- How it connects

## Analysis: What the pattern tells us
- Synthesis
- Counterarguments addressed

## Conclusion: What we know and what's open
- Clear takeaway
- Honest uncertainties
- Discussion invitation
```

# Instructions

1. **Detect persona** (Step 1 above)

2. **Read `writing/templates/article-structures/PRINCIPLES.md`** (from repo root)

3. **Ask the user for the topic**: Get enough context to understand:
   - The main argument, thesis, or question
   - What data/evidence is available
   - The target audience

4. **Select the appropriate article structure** from `writing/templates/article-structures/`:
   - **Debunking (驳斥)** — benyu: X is wrong → reality; hushi: belief is incomplete → fuller picture
   - **Raising a Valuable Question (提出问题)** — Reframe definition → challenge assumptions
   - **Case and Product Study (案例与产品研究)** — What happened → what it reveals
   - **Exploration & Hypothesis (探索与假说)** — Problem → experiment/thinking → framework
   - **Prediction/Trend Analysis (趋势预测)** — Current state → forces → where it's heading

5. **Generate the outline** applying persona-specific framing:

   **If benyu:**
   - Title: Provocative, makes readers want to argue ("读者看了会不会想反驳？")
   - Opening: Conflict/tension — does the first sentence stop you dead?
   - Companies: Identify which to challenge and attack by name
   - Action: Plan "怎么办" section — not just criticism
   - Energy: "来骂我吧"

   **If hushi:**
   - Title: Precise, states question or thesis (NOT clickbait)
   - Opening: Paradox or surprising observation
   - Framework: At least one theoretical anchor (Goodhart's Law, CAP theorem, etc.)
   - Companies: Named for analysis and citation, not attack
   - Uncertainty: Identify what we don't know and acknowledge it

6. **Output the outline** in a clear, structured format

7. **Write the outline to file**: ALWAYS save to `outline.md` in the current working directory

# Important

- Does NOT need to read `{persona}/style_guide.md` — the inline persona-conditional behaviour above is sufficient for outlining
- Don't create vague outlines — be specific about what examples, frameworks, and references to include
- Ensure the outline follows one of the 5 article structures
- The outline should be detailed enough that drafting becomes straightforward
- **CRITICAL**: You MUST write the outline to `outline.md` — do not just show it to the user
