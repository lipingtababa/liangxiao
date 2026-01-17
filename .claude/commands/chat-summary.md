---
description: Summarize a chatroom filtered for interesting content
---

You are summarizing a chatroom for 马工, filtering for interesting content.

# Input

The user provides a file path to a preprocessed chat file (created by `scripts/prepare_chat.py`).

**Format of input file:**
```
# Chatroom Name - YYYY-MM-DD
# Messages: N

sender1: message content
★我: my own message
sender2: [图片]
```

# Interest Filter

## INCLUDE (Interesting Content)
- AI coding cases and real examples
- Inspiring questions or problems identified
- Software engineering paradigm shifts
- Business models and strategy discussions

## EXCLUDE (Skip These)
- Tool/model comparisons ("which AI is better", "Sonnet vs GPT")
- Pricing discussions (subscription costs, plans)
- Memes and jokes
- General AI news (announcements, funding)
- Famous quotes

# Your Task

1. **Read the file** at the provided path
2. **Filter for interesting content** using criteria above
3. **Summarize key discussions** - group by topic
4. **Write output** to `/Users/Shared/code/benyu/aichat/summary/{date}/chat-summary-{chatroom}.md`

# Output Format

```markdown
# Chat Summary - {chatroom} - {date}

**Messages:** N total | **Interesting:** M

## Key Discussions

### 1. [Topic Title]
[Summary of the discussion]

Notable:
> [Person]: [Key quote]

### 2. [Topic Title]
...

---

## Skipped Content
- X messages about tool comparisons
- Y messages about pricing
- ...
```

# Rules

1. **Be selective** - Only include genuinely interesting content
2. **Group by topic** - Don't list chronologically
3. **Summarize** - Capture meaning, not every message
4. **Note what was skipped** - Brief mention of filtered content
5. **Short is okay** - If little interesting content, brief summary is fine

# Example

Given: `/tmp/chat-95112088_云计算-2026-01-17.txt`

Output: `/Users/Shared/code/benyu/aichat/summary/2026-01-17/chat-summary-云计算.md`
