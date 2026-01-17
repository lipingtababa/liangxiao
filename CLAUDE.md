# Project Instructions for Claude Code

## Article Writing Rules (CRITICAL - READ FIRST)

### NEVER Fabricate Data

**This is the most important rule. Violating it invalidates all work.**

**NEVER fabricate:**
- ❌ Examples, quotes, statistics, or comparisons
- ❌ Company pricing or quotes ("某翻译公司报价¥36,000")
- ❌ "Friend told me" scenarios unless real
- ❌ **Attributing user's own chat messages to fictional "朋友说" or "我朋友"**
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

**❌ VERY BAD** (Fake Attribution - User's Own Messages as "Friend"):
```
我朋友说过一个很生动的比喻："中国最强关系华为公司，也不能对着中石油说..."
我朋友还有个讽刺性的观察："中国军工信息化公司又没有把军代表岗位..."

(These are the user's OWN WeChat messages, NOT a friend's!)
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

**✅ GOOD** (Direct Attribution of User's Ideas):
```
中国最强关系华为公司，也不能对着中石油说...
(State the observation directly, no need for fake "friend" attribution)
```

---

## Lessons Learned: MySQL vs PostgreSQL Article (Dec 2024)

### Core Discovery: Tech Suite Evolution

**Critical Insight**: Database adoption mechanisms changed fundamentally between 2000s and 2010s-2020s.

**Two Forms of Tech Suite:**

1. **Named Stack Bundling (2000s - LAMP era)**
   - Explicit acronym: LAMP, WAMP, MAMP
   - Complete stack includes OS layer: Linux + Apache + MySQL + PHP
   - Distribution: Shared hosting cPanel one-click installers (70% of hosts)
   - Developer awareness: HIGH - "We're a LAMP shop"
   - **Active choice**: Developer explicitly chose "LAMP stack"

2. **Platform Defaults (2010s-2020s - Cloud era)**
   - **No acronym needed**: Rails uses PostgreSQL, but not called "RHP Stack"
   - No OS layer: Infrastructure abstracted (cloud characteristic)
   - Distribution: Platform defaults + starter templates
   - Developer awareness: LOW - Say "I use Next.js" (database implicit)
   - **Passive inheritance**: Choose framework/platform → database follows automatically

**Why Platform Defaults is MORE POWERFUL than Named Stack Bundling:**
- Lower friction: No active choice needed, reduces decision fatigue
- Stronger lock-in: Platform optimizations favor default database
- No branding needed: Invisible standardization more powerful than explicit branding
- Framework-first identity: Developer says "I use Next.js" (not database name)

**Examples:**
- LAMP (2000s): Active choice "LAMP stack" → MySQL comes with it
- Heroku (2010s): Passive inheritance - Choose Rails + Heroku → PostgreSQL auto-provisioned (Heroku only offered PostgreSQL initially)
- Vercel (2020s): Invisible binding - Use `create-next-app` → PostgreSQL already configured via Prisma

### Three-Factor Theory for Database Dominance

**Theory**: Database market dominance determined by three factors, NOT features or courage:

**Factor 1: Tech Suite** - Deep technology stack binding
- Framework + database integration: native drivers, ORM optimizations, type mapping
- Platform + database integration: deployment scripts, monitoring tools
- Changing database ≈ changing entire tech stack
- Database fate determined by which suite/platform bundles it

**Factor 2: Role Models** - Success cases eliminate decision friction
- Not just technical problem, but organizational politics and risk management
- Three roles:
  1. Technical feasibility proof (Facebook → MySQL can scale)
  2. Lower decision cost ("industry standard" is enough justification)
  3. Talent supply guarantee (engineers learn what big companies use)
- Pattern matching psychology: "If it works for Facebook, it works for us" = rational heuristic
- Political wisdom: Failure = "we followed best practice" (blame distributed), Success = my credit (credit concentrated)

**Factor 3: Ecosystem** - Knowledge and tool network effects
- Quality of database << quality of surrounding ecosystem
- Four layers:
  - Knowledge: Stack Overflow, blogs, books, courses
  - Tools: Monitoring, backup, migration, GUI clients
  - Commercial: Cloud managed services, support contracts, consulting
  - Community: Forums, bug fixes, extensions/plugins
- Network effect: More users → problems already solved → solutions online → more users
- Ecosystem makes technical debt tolerable (MySQL's charset/replication issues have workarounds everywhere)

**Three factors reinforce each other** forming positive feedback loop:
Tech suite brings users → users create role models → role models attract more users → users contribute to ecosystem → ecosystem lowers barrier → attracts more users → cycle continues

### Key Research Finding: Distribution Mechanism Shift

**LAMP Era (2000s):**
- Channel: Shared hosting providers (Bluehost, HostGator)
- Tool: cPanel one-click installers (Softaculous, Fantastico)
- Buyer: Often non-technical website owners
- Decision: "Host recommends LAMP → use LAMP"

**Cloud Era (2010s-2020s):**
- Channel: Platform-as-a-Service (Heroku, Vercel, Netlify)
- Tool: CLI generators (`create-next-app`), GitHub templates, platform integrations
- Buyer: Developers choosing frameworks first
- Decision: "Framework docs/templates use PostgreSQL → use PostgreSQL"

**Key Shift**: From infrastructure-first (choose OS → choose stack) to framework-first (choose framework → inherit stack)

### Forward-Looking: AI Coding Suite Opportunity

**Not Vector Database** (that's for AI application data, pgvector already exists)

**But Database for AI Coding Workflow:**
- Problem reframing: AI coder writes code daily, what data can't LLM manage well?
- LLM good at: Code generation, text processing, pattern matching
- LLM bad at: Structured data persistence, transactional consistency, complex relational queries, schema evolution tracking, data integrity constraints
- **Database should complement LLM**, managing data LLM shouldn't touch

**Potential AI Coding Suite:**
- AI coding assistant (Claude Code, Cursor, etc.)
- + Database optimized for AI-human collaboration
- + Tools for managing session state, user preferences, structured configs, audit logs

**Why this is real opportunity:**
- AI coding is paradigm shift (not incremental like Rust)
- Current databases designed for human coders
- AI + human collaboration workflow needs different data management patterns
- First-mover advantage building this suite = next PostgreSQL

### Writing Process Lessons

**Title Evolution:**
- Started: "MySQL vs PostgreSQL: 无聊的饭圈文化"
- Final: "数据库选型的三要素，兼驳斥PG vs MySQL的饭圈文化"
- Reason: Positive contribution (三要素) + critique, more substantive

**Outline Structure:**
- Opening: State three-factor theory concisely
- Part 1 (MySQL): Prove with three factors, explain Named Stack Bundling in detail
- Part 2 (PostgreSQL): Prove with three factors, explain Platform Defaults in detail, compare two mechanisms
- Part 3 (China): Validate theory with Oracle compatibility strategy
- Part 4 (Future): Apply theory to predict winners, include AI Coding Suite opportunity
- Conclusion: Summarize three factors, call to action

**Key Decision: Detail Level in Opening**
- Wrong: Put detailed comparison of two mechanisms in opening (overwhelms reader)
- Right: Simple examples in opening, detailed comparison in Part 2 when proving PostgreSQL's success
- Principle: Theory → Evidence 1 → Evidence 2 (with comparison) → Validation → Application

**Voice and Tone:**
- User preference: Serious, not cliche
- Avoid套路phrases like "远没有你想象的那么独立"
- Direct statements: "大多数数据库'选择'不是独立决策，而是技术栈的附属品"
- Chinese over English: "理性的启发式策略" instead of "rational heuristic"
- Keep English only when necessary or natural in tech context

### Data Sources and Attribution

**Real Article Referenced:**
- Friend's article: 《MySQL：互联网行业的服从测试》by 老冯
- Used screenshot as concrete hook
- Properly attributed to avoid fabrication

**Research Data (All Verified):**
- Heroku: 2M+ PostgreSQL databases, founded 2007, PostgreSQL as default
- Vercel Postgres: Launched May 2023, powered by Neon
- Stack Overflow: PostgreSQL 58% developers, "most admired"
- Salary gap: PostgreSQL DBAs $133k vs MySQL DBAs $73k
- Migration: 17% on-time, 30% overrun, 4hr downtime = $28k
- WordPress: 40% of web (MySQL-only)
- PostgreSQL streaming replication: 2010 (version 9.0) - 10 year gap vs MySQL

### Files Generated

- `brainstorm.md`: Alternative perspectives on MySQL vs PostgreSQL (10 different angles)
- `brainstorm-reasons.md`: Suite theory with detailed analysis
- `outline.md`: Complete article structure with three-factor framework
- `draft.md`: Opening section (in progress)

### Next Steps for Continuation

1. Complete Part 1: Why MySQL Won (explain Named Stack Bundling mechanism)
2. Complete Part 2: Why PostgreSQL Winning (explain Platform Defaults, compare mechanisms)
3. Complete Part 3: China Oracle compatibility validation
4. Complete Part 4: Future prediction with AI Coding Suite
5. Conclusion: Three factors summary
6. Review against style guide (2500-3500 characters target)
7. Convert to WeChat format using `/convert`

---

