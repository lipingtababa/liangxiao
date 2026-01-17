---
description: Summarize a Tier 1 chatroom (AI Coding or 构建之法) with brainstorm material
---

You are summarizing a Tier 1 chatroom for 马工.

# Input

The user provides a file path to a preprocessed chat file (created by `scripts/prepare_chat.py`).

**Format of input file:**
```
# Chatroom Name - YYYY-MM-DD
# Messages: N

sender1: message content
★我: my own message (marked with ★)
sender2: [图片]
sender3: another message
```

# Your Task

1. **Read the file** at the provided path
2. **Extract 马工's messages** (lines starting with `★我:`) as brainstorm material
3. **Summarize key discussions** - group by topic/thread, not chronologically
4. **Write output** to `/Users/Shared/code/benyu/aichat/summary/{date}/chat-tier1.md`

# Output Format

```markdown
# Tier 1 Summary - {chatroom} - {date}

## 马工's Brainstorm Material

Your own messages, organized by theme.

### [Theme 1]
> [Your message 1]
> [Your message 2]

### [Theme 2]
> ...

---

## Key Discussions

### 1. [Topic Title]
[Summary of the discussion]

Notable:
> [Person]: [Key quote]

### 2. [Topic Title]
...
```

# Rules

1. **Group by topic** - Don't list messages chronologically
2. **Extract themes** from 马工's messages - group related thoughts
3. **Summarize discussions** - capture the meaning, not every message
4. **Include key quotes** - preserve important/interesting statements
5. **Skip noise** - ignore greetings, short reactions, images unless context-relevant

# Example

Given input path: `/tmp/chat-87714869_AI_Coding-2026-01-17.txt`

1. Read the file
2. Find all `★我:` lines for brainstorm section
3. Identify discussion threads (AI抽卡师, hardware setup, etc.)
4. Write summary to `/Users/Shared/code/benyu/aichat/summary/2026-01-17/chat-tier1.md`
