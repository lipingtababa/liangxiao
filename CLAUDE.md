# Project Instructions for Claude Code

## Article Writing Rules (CRITICAL - READ FIRST)

### NEVER Fabricate Data

**This is the most important rule. Violating it invalidates all work.**

**NEVER fabricate:**
- ❌ Examples, quotes, statistics, or comparisons
- ❌ Company pricing or quotes ("某翻译公司报价¥36,000")
- ❌ "Friend told me" scenarios unless real
- ❌ Invented dialogue or conversations
- ❌ Made-up metrics or cost comparisons
- ❌ Estimated numbers presented as facts

**ONLY use:**
- ✅ Real data from user's actual work/sessions
- ✅ Published statistics with source URLs
- ✅ User-provided examples and experiences
- ✅ Documented facts from codebase/files

**If you lack real data:**
1. **ASK the user for it**
2. Leave clear placeholders: `[需要真实例子: 翻译公司报价]`
3. **DO NOT** invent examples to fill gaps
4. **Better to have NO example than a FAKE example**

**When in doubt:**
- Verify the source with the user
- Check session history for actual data
- Read actual files rather than assuming content

### Examples of Violations:

**❌ BAD** (Fabricated):
```
某翻译公司A报价：¥0.18/字，总价¥36,000
朋友在某出版社透露：版权费$8,000，翻译费¥38,000
某用户反馈说："这个工具太难用了"
```

**✅ GOOD** (Real Data):
```
从我的session中：
- 315页PDF
- 成本$3（Google Cloud APIs）
- 611条对话消息
- 实际运行时间37分钟

或者明确标注需要补充：
[用户：请提供实际翻译公司报价]
```

---

## File Permissions

- While creating files, ensure group users have write permissions (both vivi and machi might operate)
- Use `chmod g+w` on created files and directories
