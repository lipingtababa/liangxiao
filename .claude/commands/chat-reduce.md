---
description: Reduce multiple chat summaries into fewer based on content quality
---

You are consolidating multiple chat summaries into fewer sections.

# Input

The user provides one or more file paths to existing summary files.

Example: `/chat-reduce summary1.md summary2.md summary3.md`

# Logic

**Goal:** Reduce the number of summaries while preserving quality content.

**Reduction rules:**
1. **Shorter summaries** → More likely to be merged into a "Miscellaneous" section
2. **Low-content summaries** (mostly skipped/filtered content) → Absorb into misc
3. **High-quality summaries** (substantial discussions) → Keep as separate sections
4. **Similar topics across files** → Merge into single topic section

**Threshold guidance:**
- Summary < 500 chars of actual content → Candidate for merging
- Summary with < 3 discussion topics → Candidate for merging
- Summary with substantial unique insights → Keep separate

# Your Task

1. **Read all provided summary files**
2. **Assess each summary's content quality and length**
3. **Decide which to keep separate, which to merge**
4. **Write consolidated output** to `/Users/Shared/code/benyu/aichat/summary/{date}/chat-reduced.md`

# Output Format

```markdown
# Consolidated Chat Summary - {date}

## High-Quality Discussions

### From [Chatroom 1]: [Topic]
[Preserved summary content]

### From [Chatroom 2]: [Topic]
[Preserved summary content]

---

## Miscellaneous

Brief notes from chatrooms with limited interesting content:

**[Chatroom A]:** [One-liner summary or "No interesting content"]

**[Chatroom B]:** [Brief note]

---

## Sources
- summary1.md (kept: 2 sections)
- summary2.md (merged into misc)
- summary3.md (kept: 1 section)
```

# Rules

1. **Preserve quality** - Don't lose interesting content during reduction
2. **Be aggressive with low-content** - One-liner is fine for empty summaries
3. **Merge similar topics** - If two chatrooms discussed same thing, combine
4. **Track sources** - Note which original files contributed what
5. **Shorter output** - Goal is reduction, not aggregation

# Example

Input files:
- `chat-summary-云计算-2026-01-17.md` (3 topics, 800 chars) → Keep separate
- `chat-summary-AI编程-2026-01-17.md` (1 topic, 200 chars) → Merge to misc
- `chat-summary-LangGPT-2026-01-17.md` (0 topics, 50 chars) → One-liner in misc

Output: Consolidated file with 3 quality sections + misc section
