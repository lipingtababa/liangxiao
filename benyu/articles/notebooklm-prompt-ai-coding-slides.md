# NotebookLM Prompt: AI Coding Presentation

## CONTEXT

### Speaker Profile
**Name**: 瑞典马工 (Swedish Software Engineer)
**Background**: Former Huawei R&D and solutions expert, deep software engineering experience
**Style**: Direct, evidence-based, no-nonsense. "激进布道者" (radical evangelist) but goal is to open eyes, not shock
**Credibility**: Runs "Agent管理学论坛" (Agent Management Forum), practices what he preaches with 13 AI agents + 7 skills in production

### Talk Details
**Title**: AI Coding: Good Practices from the Trenches
**Duration**: 45-60 minutes
**Audience**: Half-professional software engineers (mid-level, some AI exposure but not deep)
**Goal**: Open their eyes with real experience + concrete practices they can use tomorrow
**Tone**: Professional but direct, backed by real data and first-hand experience

---

## PRESENTATION OUTLINE

### I. Reality Check: Where Are You Actually? (8-10 min)

**Opening hook**: Interactive poll - where do they think they are?

**The 7-Layer AI Adoption Funnel**:
1. Rejection: "It's just probability statistics"
2. Shallow use: 1.7 questions per session, <5 minutes (like Google search)
3. Collecting: Save prompt templates, watch tutorials, "葵花宝典 mentality"
4. Paying: Subscribe to ChatGPT Plus/Claude Pro, buy courses, still seeking "secrets"
5. Autonomous exploration: Realize templates don't work, build own workflows
6. Sharing: Write articles, give demos, actually most uncertain
7. Carbon-Silicon hybrid teams: AI as team members, systematic collaboration

**Key statistic**: Average ChatGPT user = 1.7 questions per session, 41% use <5 minutes

**The dishwasher analogy**:
- Shallow (Layer 2): "Dishwasher not working" → generic checklist (same as Baidu)
- Deep (Layer 5): "Bosch SMS46, start button no response, indicator light on" + "started last week" + upload photo + iterate → specific diagnosis (door lock sensor)

**First revelation**: "Most people think they're using AI. They're actually just asking it one question."

---

### II. What I Was Blind To (12-15 min)

**A. The Marcus Incident: Real numbers from production**

Real PR I submitted:
- 6,996 lines added
- 487 lines deleted
- 67 files changed
- 3 modules

Marcus (code quality master) reviewed, found 2 problems:
1. Logged sensitive information
2. DB migration in one file instead of series

**The revelation**: Both problems were my direct interventions. The 6,996 lines AI wrote? Marcus found no major issues.

Quote from friend Dylan: "AI: 马工, you're writing bugs again!"

**Insight**: My AI agents write better code than me. My interference lowers quality.

**B. The Cost Inversion**

**What got 10-100x cheaper**:
- **Writing code**: Monitoring system with WeChat/DingTalk/Email/SMS alerts used to be team + quarters, now weekend project
- **Writing tests**: SQLite has 590:1 test-to-code ratio (155K lines code, 92M lines tests) - used to be insane, now achievable
- **Documentation**: LLMs read code directly, only need decision docs (why/what alternatives/what tradeoffs)
- **MVPs**: Months + tens of thousands → hours + hundred bucks (Lovable can do it)

**What became MORE expensive (new bottlenecks)**:
- **Defining requirements**: AI writes code but doesn't know WHAT to write. GitHub study: most agent failures = vague specs
- **Code review**: AI produces faster than humans review. Quote: "5 PRs from AI, 3 unusable, might as well write myself"
- **Architecture design**: AI knows patterns but is "pushover" - won't say "this requirement is unreasonable"
- **Stakeholder alignment**: Swedish bank integration example - code = 1 afternoon, QWAC certificates = weeks of paperwork

**Core shift**: "What to build" became harder than "how to build it"

Scarce resource isn't coding ability - it's ability to define what "correct" means.

**C. The 4-Hour Debugging Paradox**

Survey of developers using AI - top complaints about time spent:

Top 8 prompts (from actual survey):
1. "用中文回答我" (Use Chinese to answer)
2. "生成完整代码" (Generate complete code)
3. "还是无法运行" (Still can't run)
4. "帮我修改代码" (Help me modify code)
5. "你的代码还是有问题" (Your code still has problems)
6. "请不要添加不必要的注释" (Don't add unnecessary comments)
7. "只生成我让你生成的部分" (Only generate the part I asked)
8. "都说了参考我之前的代码" (I told you to reference my code)

**Analysis**: Only 2 are reasonable (should be in config). Other 6 are "prayers" not engineering specs.

**Revelation**: Real problem isn't AI stupidity, it's lack of methodology.

Without TDD:
- One-shot "generate complete code"
- Write bunch, discover all wrong
- 4-hour debugging

With TDD:
- Write test → red → AI makes green → refactor
- Code 5 min, debug 5 min

---

### III. Good Practices That Actually Work (20-25 min)

**Practice 1: Put Prompts in the Right Place**

**The problem**: Repeating same instructions every session

**My actual configuration structure**:

User-level CLAUDE.md (`~/.claude/CLAUDE.md`):
- Personal preferences: "用中文回答", "2-space indent", "single quotes"
- Commit message format: Conventional commits

Project-level CLAUDE.md (`/path/to/project/.claude/CLAUDE.md`):
- API paths: Always `/api/v1/` prefix
- Error handling: Reference `src/utils/errorHandler.ts` pattern
- Database queries: Always add timeout (30s)

Slash Commands (`.claude/commands/`):
- `/review` - automated code review workflow
- `/qc` - quality check and commit

Subagents (`.claude/agents/`):
- PM agent: requirements
- Architect agent: design
- Tester agent: write tests (TDD red phase)
- Coder agent: implementation (TDD green phase)
- Quality-checker agent: validation
- Deployer agent: CI/CD monitoring

**My actual setup**: 13 agents + 7 skills in production

**Takeaway**: If you repeat it, you configured it wrong.

---

**Practice 2: TDD Is Back (Economics Changed)**

**Historical context**:
- 2014: DHH declared "TDD is Dead" (too expensive when humans write slowly)
- 2024: Kent Beck says TDD is "superpower" with AI (writing tests ≈ free now)

**My workflow**:
1. Tester agent writes test first
2. Run test - fails (red phase)
3. Coder agent writes code
4. Test passes (green phase)
5. Refactor

**Real example - Bank integration project**:
- Built mock bank simulating every Swedish bank's API
- Wrote tests for the mock bank itself (meta-testing)
- Mock bank tests business code, test code tests mock bank
- Pre-AI: Boss would never approve budget
- Now: Just did it, works perfectly

**Why it works**:
- Tests = specifications AI can iterate against
- Without tests: review every line manually
- With tests: verify code satisfies requirements
- Problems contained to small scope, no 4-hour debugging

**Real result**: Code 5 min, debug 5 min (not 4 hours)

**Takeaway**: Write tests before code, let AI make them pass

---

**Practice 3: Three-Party Delegation Framework**

**The problem**: Unclear who does what (human/AI/tools)

**My framework**:

| Role | Good At | Bad At |
|------|---------|--------|
| **Tools** | Deterministic execution, enforcing rules | Understanding context, flexible judgment |
| **LLM** | Content generation, pattern recognition, context analysis | Remembering rules consistently |
| **Human** | Strategic decisions, final review, responsibility | Repetitive work, high-volume generation |

**Real examples from my projects**:

**Example 1: Test file protection**
- ❌ Education: "Don't modify test files, that's cheating"
  - Result: Mostly follows, sometimes "forgets"
- ✅ Enforcement: `chmod 444 tests/**/*.test.ts`
  - Result: Can't modify even if wants to. Problem solved forever.

**Example 2: Code formatting**
- ❌ Education: "Follow ESLint, 2-space indent, single quotes"
  - Result: Every generated code has different style
- ✅ Enforcement: Pre-commit hook runs `eslint --fix`
  - Result: Auto-formatted before commit regardless of AI output

**Example 3: Git operations**
- ❌ Education: "Don't use git add -A, don't push to main"
  - Result: Occasionally violates
- ✅ Enforcement: Pre-commit hook + GitHub branch protection
  - Result: Can't violate even if wants to

**Takeaway**: Tools for deterministic rules, AI for creative work, humans for decisions

---

**Practice 4: Product Tri-Ownership Team Structure**

**The problem**: PingCAP's "head wolf" model

黄东旭 (PingCAP CTO):
- Rewrote TiDB PostgreSQL layer with AI
- Code quality "approaching production"
- 90% time spent validating, not coding
- Model: "Head wolf + wolf pack (agents)"
- One elite engineer owns product end-to-end

**Challenge**: How many companies have someone like 黄东旭? Elite path not scalable.

**My solution**: Split superhuman into 3 trainable roles

```
Product Architect / Head Wolf / 超级个体
              │
              │ Split into
              ▼
┌──────────────┬──────────────┬──────────────┐
│  Product     │   Quality    │    Tech      │
│   Owner      │    Owner     │   Owner      │
├──────────────┼──────────────┼──────────────┤
│  owns WHAT   │  owns RIGHT  │   owns HOW   │
├──────────────┼──────────────┼──────────────┤
│ ≈ Architect  │ ≈ Supervisor │ ≈ Civil Eng  │
└──────────────┴──────────────┴──────────────┘

施工方 (construction) = AI agents
```

**Product Owner (PO)**:
- Defines requirements and acceptance criteria
- Says "No" to features (not just documenting secretary)
- Accountable for outcomes, not outputs
- First layer of quality control

**Quality Owner (QO)**:
- Designs quality processes (not just final testing)
- Adversarial testing (NASA IV&V principle - independent validation)
- Full SDLC involvement (acceptance criteria → tests → validation)
- Prevents AI from cheating (commenting out failing tests)

**Tech Owner (TO)**:
- Orchestrates AI agent workflows
- Reviews code review reports (not code itself)
- Handles exceptions (e.g., partner didn't provide API, had to construct openapi.yaml)
- Designs different workflows for different tasks (bug fix ≠ new feature ≠ greenfield)

**Real workflow - One user story per day**:
- Morning: PO writes story, QO defines acceptance criteria
- Pre-lunch: AI generates design, TO reviews and approves
- During lunch: AI writes code + tests (AI doesn't eat lunch!)
- Afternoon: TO reviews, iterates to improve quality
- End of day: GitHub Actions runs E2E, QO validates, merge if passes

**Why it works**:
- Don't need superhuman (黄东旭)
- 3 trainable roles instead of 1 impossible role
- Parallel work (3 people can work concurrently)
- Clear separation of concerns
- AI does heavy lifting

**Critical rule**: Three owners must sit together physically. Daily standup not enough - decisions happen multiple times per day.

**Takeaway**: Team structure matters as much as tools

---

**Practice 5: Methodology Over Magic Prompts**

**The problem**: People collect prompt templates like 葵花宝典 (martial arts secret manuals)

**Real case study**: Teaching my 12-year-old maths (Swedish 6th grade)

**Methodology chosen**: Mastery Learning
- Don't teach by schedule, teach by mastery level
- Only advance when current topic mastered
- Defines entire workflow: Assess → Plan → Execute → Feedback

**Three-party delegation in practice**:
- **Human**: Decides learning goals, reviews plans, quality checks, teaches concepts
- **LLM**: Analyses historical data, creates problem-generating plans, generates problems, saves to Notion
- **Tools**: Notion reliably stores records, enforces data structure (standardized topics, required fields)

**Workflow**:
1. Human requests assessment or provides topic
2. LLM analyses Notion history, proposes problem plan
3. Human reviews and approves plan
4. LLM generates problems (English, printable, no answers, hints only)
5. Human prints and teaches
6. After practice, human records results in Notion
7. Feedback loop for next session

**Configuration** (in project CLAUDE.md):
```markdown
# Math Tutoring Project

You are an expert tutor who understands child education psychology.

## Context
Tutoring 12-year-old Swedish child, reviewing grade 6, previewing grade 7 maths.

## Workflow
1. I may ask you to analyse child's level and create problem plan
   - Historical data: https://www.notion.so/xyz123abc
2. Or I may give specific topic for you to create plan
3. Plan must align with Sweden curriculum for grade 6
   - Don't include grade 7 topics not yet taught
4. I'll discuss plan with you, confirm before generating
5. Problem requirements:
   - English language
   - Printable format, sufficient answer space
   - No answers included, one-line hints allowed
6. Save problems in Notion DB under date, give me link
```

**Result after months**:
- Child no longer fears maths
- Actively requests more problems
- Steady mastery progression

**Key insight**: Configuration defines roles + workflow, not just preferences

**Takeaway**: Methodology drives workflow. Prompts are just implementation details.

---

### IV. The Urgency: Why Now? (5-8 min)

**Zhu Rui's Artillery Lesson**

Historical parallel: PLA artillery commander (1945-1948)

**Timeline**:
- September 1945: Arrived Northeast empty-handed
- May 1946: Collected 700+ artillery pieces (8 months)
- October 1946: First Artillery Command HQ established (13 months) - 100+ artillery companies
- December 1947: First major victories with artillery superiority (27 months)
- End 1948: 9,000 artillery pieces total (39 months / 3.25 years)

**Transformation**: 0 to dominant force in **3 years**

**His pledge**: "三个月内,装备训练出四个炮兵团开赴前线打仗"
- "Within 3 months, equip and train 4 artillery regiments for frontline combat"
- Actually delivered on this promise

**His urgency quote**:
> "历史机时,稍纵即逝,不抓是不对的"
> "Historical moments are fleeting, not seizing them is wrong"

**Context**: Northeast China 1945-46 was chaotic, equipment everywhere. If he waited for "proper procedures," opportunity lost. He moved fast, grabbed equipment, built units, proved value.

---

**The 2024-2025 Window**

**Why NOW is the historical moment**:

1. **Technology maturity**: Claude 3.5 Sonnet, GPT-4, Cursor, Claude Code are production-ready
2. **First-mover advantage**: Most companies still figuring out, early adopters building huge lead
3. **Talent availability**: Developers excited to learn, competitive advantage in recruiting
4. **Cost-benefit obvious**: 2-10x productivity gains clearly measurable
5. **Before commoditization**: In 2-3 years, this will be table stakes, no competitive advantage

**The narrow window**:
- **2024-2025**: Build capability, build lead, build organizational muscle
- **2026+**: AI coding is commodity, everyone has it, advantage gone
- **Historical moment**: The next 12-18 months

---

**Zhu Rui's Action Plan Applied to AI Coding**

**Month 1: Pilot**
- Select 3-5 best engineers
- Give them Claude Code + Cursor + budget
- Assign 1 real product feature
- Ship to production in 2 weeks
- Measure: lines of code, time, quality metrics

**Month 2-3: Bootcamp**
- Design 2-week intensive bootcamp
- Week 1: Tool basics, real codebase exercises
- Week 2: Real production feature delivery (learn by doing)
- Train next 10 engineers
- Each must ship 1 production feature in week 2

**Month 4-6: Command Structure**
- Establish AI Coding Centre of Excellence
- Hire/appoint lead (your "Zhu Rui")
- Create 4-standard playbook:
  1. Tools (approved tools, licensing, security)
  2. Workflows (when to use AI, review requirements)
  3. Training (bootcamp criteria, certification levels)
  4. Coordination (how AI teams work with product teams)
- Deploy first 10 specialists to product teams

**Month 7-12: Scale**
- Run bootcamp monthly (10 engineers per batch)
- Deploy specialists to all critical projects
- Measure productivity gains
- Adjust playbook based on learnings

**Year 2: Dominate**
- 100+ engineers with AI coding capability
- Measurable productivity advantage vs competitors
- Use advantage to ship faster, recruit better, win market

---

### V. What You Can Do Tomorrow (3-5 min)

**For Individual Developer** (Layer 2 → 5):

Tomorrow:
- Don't stop at 1 question - ask 3-4 follow-ups
- When AI gives answer, ask "why?", "what if?", "any edge cases?"

This week:
- Pick one real task
- Use TDD: write test first, let AI make it pass
- Document what worked, what didn't

This month:
- Create your first CLAUDE.md (user-level)
- Put your repeated instructions there
- Add one slash command for common workflow

---

**For Team Lead** (Layer 5 → 6):

This week:
- Share one AI coding win with team (show, don't tell)
- Do one 30-minute live demo: "Watch me build feature with AI"
- Get feedback: what confused them? what interested them?

This month:
- Document your workflow
- Make it repeatable (CLAUDE.md + agents/commands)
- Train 3 team members using your workflow

This quarter:
- Measure results (before/after productivity, quality)
- Share learnings with management
- Propose pilot program

---

**For Engineering Manager** (Layer 6 → 7):

This month:
- Identify 3-5 best engineers for pilot
- Secure budget (tools + time)
- Assign 1 real feature, not toy project
- Deadline: 2 weeks to production

Next month:
- Review pilot results (lines of code, time, quality, what worked)
- Design bootcamp based on what actually worked
- Don't copy others' bootcamp - use your learnings

Month 3:
- Run first bootcamp (10 engineers)
- Each ships 1 production feature in week 2
- Measure everything: time, quality, satisfaction

Quarter 2:
- Establish AI Coding Centre of Excellence
- Create playbook (tools, workflows, training, coordination)
- Deploy specialists to critical projects

---

**The Starting Point Everyone Can Do**:

**Create your first CLAUDE.md this week**

Start simple:
```markdown
# My AI Coding Preferences

- Answer in [your language]
- Code style: [your preferences]
- When I say "review", run tests and check for common issues
```

Then iterate:
- Add project-specific rules as you encounter repeated instructions
- Move common workflows to slash commands
- Build up gradually based on real pain points

**Don't wait for perfect plan. Start small, iterate fast.**

---

### VI. Q&A Preparation

**Anticipated challenges and responses**:

**"But AI makes mistakes"**
- Response: Show Marcus example (7000 lines, AI's code was fine, my interference caused bugs)
- Point: Question isn't "does AI make mistakes" but "who makes more mistakes"
- Data: My AI agents pass quality review when I don't interfere

**"Takes too long to review AI code"**
- Response: Show TDD approach
- Without tests: review every line manually = bottleneck
- With tests: verify code passes specs = fast
- My workflow: Code 5 min, debug 5 min (not 4 hours)

**"Can't find superhumans for head wolf model"**
- Response: That's exactly the problem
- Show Tri-Ownership: 3 trainable roles instead of 1 superhuman
- PO + QO + TO can be grown, don't need 黄东旭

**"No budget for tools"**
- Response: Show cost inversion
- Traditional: hire 1 more developer = $100K+/year
- AI tools: Claude Code = $200/month
- Even 10% productivity gain = massive ROI
- Question: Can you afford NOT to invest?

**"Need time to plan properly"**
- Response: Show Zhu Rui urgency
- He didn't wait for perfect plan, collected equipment first
- Proved value, got official structure later
- Start with pilot, learn, iterate
- 3-month sprint better than 6-month planning

**"Our codebase too complex for AI"**
- Response: That's exactly when AI helps most
- My bank integration: complex API, multiple countries
- AI handles complexity humans struggle with
- Question isn't "is it complex" but "have you actually tried"

---

## KEY NUMBERS TO EMPHASIZE

**Real data from speaker's experience**:
- 7,000 lines of code, 2 bugs (both human-caused)
- 13 AI agents + 7 skills in production
- SQLite: 590:1 test-to-code ratio
- Average ChatGPT user: 1.7 questions, <5 minutes
- Swedish bank integration: code = 1 afternoon, certificates = weeks
- One user story per day (with Tri-Ownership)
- Zhu Rui: 0 to 9,000 artillery pieces in 3 years
- Window: 12-18 months (2024-2025)

---

## TONE AND STYLE GUIDANCE

**Do**:
- Use concrete numbers and real examples
- Show actual code/workflows when relevant
- Admit mistakes and learnings ("I was blind to...")
- Be direct but not condescending
- Back claims with evidence

**Don't**:
- Make unsubstantiated claims
- Use too much jargon without explanation
- Preach without showing
- Dismiss audience's current practices (they're doing their best)
- Create fear (window closing ≠ doom, it's opportunity)

**Voice**:
- Professional engineer sharing battle scars
- "Here's what I learned the hard way"
- "This is what actually works in production"
- "You can try this tomorrow"

---

## GENERATE SLIDES WITH THESE PRINCIPLES

1. **Evidence-based**: Every claim backed by real example or data
2. **Actionable**: Clear next steps at each level
3. **Honest**: Show failures and learnings, not just successes
4. **Concrete**: Actual workflows, configurations, numbers
5. **Respectful**: Open eyes, don't preach or condescend
6. **Urgent but not alarmist**: Window is real but it's opportunity not doom

**Slide format preference**:
- Each slide: one key point
- Use visuals where helpful (diagrams for workflows)
- Code snippets when showing actual configuration
- Numbers prominent when using data
- Keep text concise, details in speaker notes

**Length**: 20-25 main content slides + title/closing (target 45-60 min with discussion)
