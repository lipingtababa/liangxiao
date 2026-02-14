---
description: Pick interesting topics from AI chat summaries for brainstorming
---

You help discover interesting article topics from recent WeChat group discussions.

# Your Role

Scan recent chat summaries from AI Coding and 构建之法 groups to identify topics worth developing into articles through brainstorming.

# Arguments

The user can specify a date:
- `/pick-chat today` - scan today's summaries
- `/pick-chat yesterday` - scan yesterday's summaries
- `/pick-chat 2026-01-17` - scan a specific date
- `/pick-chat` (no arg) - scan both today and yesterday

# Execution Steps

**IMPORTANT: You MUST execute these steps immediately when invoked.**

## Step 1: Determine Date(s)

Parse the argument to get the target date(s):
- "today" → current date (use system date)
- "yesterday" → current date minus 1 day
- "YYYY-MM-DD" → that specific date
- no argument → both today and yesterday

## Step 2: Find and Read Summary Files

Chat summaries are `.md` files next to the raw `.json` files in each chatroom directory.

**Structure** (symlink `aichat/` → `/Users/Shared/code/aichat`):
- `aichat/chats/87714869_AI_Coding/{date}.json` - AI Coding群 raw data
- `aichat/chats/87714869_AI_Coding/{date}.md` - AI Coding群 summary
- `aichat/chats/72565316_构建之法/{date}.json` - 构建之法群 raw data
- `aichat/chats/72565316_构建之法/{date}.md` - 构建之法群 summary

**If no summary exists for the date**, generate it first:
1. Run `/pick-brain {date}` in the aichat repo (at `/Users/Shared/code/aichat`)
2. This generates summaries as `{date}.md` next to the raw `{date}.json`

Use Glob to find summary files: `aichat/chats/*/{date}.md`

**Actually read the files using the Read tool. Do not assume or fabricate content.**

## Step 3: Identify Brainstorm Candidates

From the content you read, look for topics with:

**High Potential:**
- ★ Unique insights or frameworks (like "七层漏斗")
- Controversial or counterintuitive claims
- Personal experience with real data
- Cross-domain connections
- Industry insider perspectives
- Challenges to conventional wisdom

**Medium Potential:**
- Interesting observations without full development
- Questions that provoke thinking
- Real case studies or examples

**Skip:**
- Pure news sharing without analysis
- Technical Q&A without broader implications
- Personal chat/social content

## Step 4: Output Candidates

Present findings:

```markdown
# Brainstorm Candidates - {date}

## 🔥 High Priority (ready for /brainstorm)

### [Topic Title]
**Source:** AI Coding群 / 构建之法群, {date}
**Core insight:** [One sentence summary]
**Why interesting:** [What makes this worth developing]
**Brainstorm angle:** [Suggested direction for exploration]

---

## 💡 Medium Priority (needs more material)

### [Topic Title]
**Source:** ...
**Core insight:** ...
**Gap:** [What's missing before brainstorming]

---

## 📝 Notes

[Any patterns or connections noticed across topics]
```

## Step 5: Ask for Selection

Ask user which topic they want to explore with `/brainstorm`.

# Important Rules

**DO:**
- **Actually read the files using Read tool** - this is critical
- Quote key phrases from the summaries you read
- Be selective - quality over quantity

**DON'T:**
- Invent topics not in the summaries
- Skip reading files
- Assume file contents without reading
