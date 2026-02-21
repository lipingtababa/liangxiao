---
description: Review article against the active persona's style guide checklist
---

You are reviewing a 微信公众号 article against the established style guide.

# Step 1 — Detect persona

Walk up the directory tree from the current working directory looking for a `.persona` file. Read the first line — that is the persona (`benyu` or `hushi`).

Fallback (if no `.persona` file found):
- If `benyu` appears in the current path → persona = `benyu`
- If `hushi` appears in the current path → persona = `hushi`
- Otherwise → ask the user which persona to use

# Step 2 — Read style guide

Read `{persona}/style_guide.md` (from repo root). Then read `writing/templates/article-structures/PRINCIPLES.md`.

# Instructions

1. **Detect persona and read style guide** (Steps 1–2 above)

2. **Get the article**: Read `draft.md` in the current directory (or ask for the file path if it doesn't exist)

3. **Perform comprehensive review** using the checklist below

---

## Data Authenticity Check (CRITICAL — Check First)
- [ ] All examples are from real sources (not fabricated)
- [ ] All quotes are actual quotes (not invented)
- [ ] All statistics have verifiable sources
- [ ] All company/product names are real (not made up)
- [ ] No "某公司", vague invented scenarios
- [ ] **NO fake "朋友" attributions** — user's own chat messages must NOT be attributed to fictional "朋友说"
- [ ] User's ideas stated directly in first person, NOT through fake third-person personas

**If ANY data appears fabricated OR fake attributions found, FAIL the review immediately and list all violations.**

---

## Evidence & Specificity Check
- [ ] Named at least 3–5 specific companies/products
- [ ] Included at least 1 URL/reference
- [ ] Used concrete numbers/metrics
- [ ] At least 2–3 concrete examples supporting the argument

---

## 6 Principles Check

**If benyu:**
- [ ] **标题即半篇文章** — 读者看了会不会想反驳？具体、刺痛、不是公式化
- [ ] **首段必须抓人** — 前两句有冲突/张力吗？还是"今天我们聊聊X"？
- [ ] **具体数字触发情绪** — 有"四千多人"、"$3"这样的数字吗？还是"很多"、"一些"？
- [ ] **听起来可操作** — 有"怎么办"部分吗？还是只有批评？
- [ ] **打大公司/权威** — 点名批评了哪个大公司？还是"某些公司"？
- [ ] **读者焦虑** — 读者的焦虑是什么？文章有没有回应？

**If hushi:**
- [ ] **标题精准** — Precise title stating question/thesis (NOT clickbait, NOT provocative)
- [ ] **首段有智识张力** — Opening has paradox, observation, or data (NOT conflict/attack)
- [ ] **具体数字和证据** — Concrete facts and data with sources
- [ ] **有框架可借鉴** — Offers thinking frameworks, not just criticism
- [ ] **点名分析** — Companies named for analysis (NOT for attacking)
- [ ] **回应读者关切** — Addresses reader questions with honest analysis

---

## Argumentation Check
- [ ] Clear thesis or question stated early
- [ ] Theoretical foundation provided (benyu: physics/CS principles; hushi: formal frameworks like Goodhart's Law, CAP theorem)
- [ ] Evidence builds progressively
- [ ] Counterarguments addressed
- [ ] Conclusions follow from evidence

---

## Tone Check

**If benyu:**
- [ ] Conversational, opinionated, sarcasm used effectively
- [ ] Personal voice evident ("我", experience references)
- [ ] At least one memorable analogy (永动机, 大巴司机 style)
- [ ] At least one rhetorical question
- [ ] Does NOT use "这不是X，是Y" pattern — just states Y directly

**If hushi:**
- [ ] **No sarcasm** — No "所谓专家们", "跳大神", "美其名曰"
- [ ] **No mockery** — No "老师傅", "劳什子", dismissive terminology
- [ ] **No emotional provocation** — No "恕我直言", "说句难听的"
- [ ] Intellectual generosity — other viewpoints treated fairly
- [ ] Honest about uncertainty — "我还不确定" where appropriate
- [ ] At least one structural analogy from engineering/science/economics

---

## Style Check (Both Personas)
- [ ] **Concise and professional** — no verbosity, every sentence adds value
- [ ] Natural flowing prose — NOT bullet-point listings with bold labels
- [ ] Mix of Chinese and English terminology (natural)
- [ ] ZERO emoji
- [ ] No corporate jargon: "赋能", "降本增效"

---

## Structure Check
- [ ] Sufficient depth (doesn't skim surface)
- [ ] Progressive argument building
- [ ] Used subheadings if complex topic
- [ ] Blockquotes for cited content
- [ ] Clear conclusion or synthesis

---

## Engagement Check

**If benyu:**
- [ ] Ends with provocative reversal or discussion prompt
- [ ] "来骂我吧" energy in closing
- [ ] Memorable final line

**If hushi:**
- [ ] Ends with synthesis of what we know/don't know
- [ ] Discussion invitation — measured, not provocative
- [ ] Forward-looking element

---

## Link Check
- [ ] **《》symbols converted to links** — For each 《term》, search for a Wikipedia or authoritative reference and convert to markdown: `[term](url)`

---

4. **Provide detailed feedback** in this format:

### Strengths
List what the article does well, with specific examples

### Issues Found
List problems organised by category (Data Authenticity, Evidence, Principles, Tone, Structure, Engagement)

### Specific Recommendations
Provide concrete suggestions:
- Missing examples or frameworks to add
- Tone adjustments needed (especially flagging tone-slip between personas)
- Structural improvements
- Specific text snippets showing how to apply style guide patterns

### Checklist Score
Show which checklist items passed/failed

5. **Suggest revisions**: For any failed items, provide specific text suggestions using the active persona's style guide patterns.

# Important

- Be thorough and specific in your review
- The most common issue for hushi: tone slipping into provocative/benyu mode — flag this aggressively
- The most common issue for benyu: vague claims without named companies or concrete numbers — flag this
- Reference the style guide patterns and examples
- Don't just say "add more examples" — suggest WHAT examples
- Provide actual text snippets showing how to apply style guide patterns
