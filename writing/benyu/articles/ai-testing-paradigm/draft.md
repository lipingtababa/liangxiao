# AI Coding and Engineering Costs: The Bottleneck Shifts away from Implementation 

**Almost every engineering problem is a cost problem in disguise.** The best practices of traditional software engineering are optimization solutions derived under the constraint of high labor costs. AI has reduced the cost of writing code by an order of magnitude. The assumptions underlying these best practices no longer hold.


---

## What Got Cheaper

### Writing Code

A friend messaged me recently: "Hey, I need a localized monitoring system with WeChat, DingTalk, email, and SMS alerts. Want to do it as a practice project?"

A monitoring system with multi-channel alerting. As a "practice project." Five years ago this was a product roadmap requiring a team and quarters of work. Now it's a casual ask—something you might knock out over a weekend. The cost of attempting something collapsed.

Even maintaining old projects: need to change 20 references? Grep and replace them all. With regression tests in place, there's no code you're afraid to touch.

The old instinct was to modify carefully, preserve what works, minimize changes. That instinct came from an era of expensive labor. Now writing code is cheap, and the rational approach flips: rewrite aggressively, test thoroughly.

### Writing Tests: From Luxury to Baseline

According to [SQLite's official documentation](https://sqlite.org/testing.html), SQLite has a 590:1 ratio of test code to application code. 155,000 lines of business logic, 92 million lines of tests. That used to look insane. Now it looks like a target.

I'm working on a banking integration. To test my system against bank APIs, I built a mock bank that simulates every Swedish bank's API. To verify the mock bank itself, I wrote tests for the mock. Mock bank tests business code, test code tests mock bank. Pre-AI, my boss would never have approved that budget. Now I just did it without asking.

MockBank.io exists as a commercial product precisely because this was a real industry pain point—too expensive for most teams. AI changed that calculation.

### Documentation: Near Zero Cost

Traditional documentation starts going stale the moment you finish writing it. Code changes, docs don't, docs become lies. So people stop writing them.

AI tools can trigger documentation updates automatically when code changes. Maintenance cost approaches zero.

Actually, most documentation doesn't need to exist anymore—LLMs read code directly. What becomes more valuable is decision documentation: why we chose this approach, what alternatives we rejected, what tradeoffs we accepted. That context doesn't live in code. It lives in commit messages, design docs, and conversations.

### MVPs and Prototypes: Months → Hours

Validating an idea used to cost tens of thousands of dollars and months of engineering time. Now it costs a hundred bucks and an afternoon. Lovable can do it. You don't need Figma.

Product decisions that used to require engineering sign-off can now be prototyped by sales teams directly. The feedback loop from idea to validation compresses from months to days.

---

## What Got More Expensive (The New Bottlenecks)

### Defining Requirements

AI can write code, but doesn't know what to write. AI can write tests, but doesn't know what "passing" means.

GitHub studied 2,500+ agent configuration files. Most failures came from vague specifications. Fuzzy requirements produce wrong code. This was true before AI; it's still true now.

My experience: time spent writing code shrank dramatically. Time spent defining product specifications didn't. AI can organize and record requirements, but can't define them. Defining requirements means understanding the business, making tradeoffs, taking responsibility. AI doesn't do that.

Code iteration got faster. Requirements iteration didn't.

### Code Review: The New Bottleneck

AI produces code far faster than humans can review it.

A colleague: "AI gave me five PRs. Three were unusable. I might as well have written the code myself." He wasn't saying AI writes bad code. He was saying review cost is too high.

Traditional development: writing code was the bottleneck, review was a checkpoint. Now reversed. Writing code is no longer the bottleneck. Review is. Human review speed hasn't changed. Volume of code to review exploded.

### Architecture Design

AI knows design patterns. AI knows architecture principles. AI draws beautiful architecture diagrams. But AI is a pushover—agrees with whatever you say.

Architecture decisions are tradeoffs under constraints: performance vs. cost, flexibility vs. complexity, short-term delivery vs. long-term maintenance. No standard answers. Requires taking risks and making choices. AI won't say "this requirement is unreasonable, cut it." It just implements whatever you ask for.

A good architect pushes back. AI doesn't.

### Stakeholder Alignment

Some bottlenecks aren't technical.

I'm working on Open Banking integrations. To connect to Swedish banks, you need QWAC and QSEAL certificates—electronic credentials proving your company is authorized to access banking APIs. Technical integration? AI writes that in an afternoon. Certificate application? Weeks of paperwork, legal review, compliance sign-offs, back-and-forth with certificate authorities. Bottleneck moved from "can we build it" to "are we allowed to build it."

This pattern repeats everywhere. Security review. Legal approval. Partner coordination. Vendor contracts. Regulatory compliance. These processes were designed when code was slow. Nobody optimized them—they were never on the critical path.

Now they are. They're not getting faster.

Traditional project management assumed engineering was the constraint—add more engineers, parallelize work, optimize the build pipeline. When code generation becomes near-instantaneous, the constraint shifts to sequential human processes that can't be parallelized. Can't throw more lawyers at a contract review to make it faster. Can't split a compliance approval across multiple regulators.

This creates organizational debt. Teams that don't redesign approval workflows will find AI-accelerated development bottlenecked by 1990s-era governance processes. Code ready in hours. Approval takes months.

---

## What Got More Important

### CI/CD: The New Quality Enforcement Layer

Traditional operations tolerated ambiguity. Installation manuals were outdated, contradictory, incomplete. Experienced engineers improvised—knew which steps to skip, which warnings to ignore, which undocumented dependencies to install first. Tacit knowledge lived in people's heads.

AI agents don't have tacit knowledge. Follow instructions literally. Hand an AI a broken deployment script, it breaks things confidently and repeatedly. Messiness that humans navigated through intuition becomes catastrophic failure at scale.

CI/CD pipelines formalize what was previously informal. Automated tests, linting, security scans, staging deployments, E2E validation—explicit specification of "what correct looks like." Pipeline is the contract. Pass the pipeline, meet the standard. Don't pass, don't meet.

Deeper consequence: when AI generates code at high velocity, quality gates in your pipeline become the de facto definition of quality. Whatever your pipeline doesn't check, AI will eventually break. Whatever your pipeline enforces, AI will eventually learn to satisfy.

Pipeline isn't about deployment anymore. It's the specification language for AI-assisted development.

---

The core shift: **"What to build" became harder than "how to build it."**

The new scarce resource isn't coding ability. It's the ability to define what "correct" means. Tests are specifications. Requirements are constraints. The team that can clearly articulate what success looks like will outperform the team with better AI tools but fuzzy goals.

---

## What I'm Doing About It

**TDD is back.** In 2014, DHH declared "TDD is Dead" and many teams abandoned test-first development. Made sense: writing tests before code was expensive, return wasn't always worth the investment.

Cost structure flipped. Writing tests is cheap now. Tests serve a new purpose beyond catching bugs—they constrain AI output. Well-written test suite is a specification AI can iterate against. Without tests, reviewing every line of AI-generated code manually. With tests, verifying code satisfies explicit requirements. Kent Beck now calls TDD a "superpower" when working with AI agents. Economics changed, practice makes sense again.

**The Golden Triangle.** Restructuring around three roles: product owner, lead engineer, quality controller.

Product owner defines requirements and acceptance criteria—what "done" looks like. Lead engineer works with AI to generate and iterate on code. Quality controller validates output against specifications, maintains test infrastructure.

Traditional teams conflated these roles because one person did all the work. Developer understood the requirement, wrote the code, verified it worked. Made sense when implementation was the bottleneck. Now bottleneck is specification clarity and quality assurance. Separating roles forces explicit handoffs: product owner must articulate requirements clearly enough for engineer to translate into tests. Quality controller must define acceptance criteria precisely enough to be automated.

**PRD-based fast iteration.** Front-loading documentation. Detailed PRD before coding seems old-fashioned—waterfall thinking. AI changes the calculus.

Vague PRD meant developers filled gaps with their judgment during implementation. Worked because developers were expensive and documentation was overhead. Now AI fills gaps with its judgment, often wrong in subtle ways. Precise PRD, translated into test cases, becomes the specification AI iterates against. Iteration cycle shrinks from weeks to hours: PRD → tests → AI generates code → tests fail → AI fixes → tests pass → human review.

Documentation isn't overhead anymore. It's the control mechanism.

**Rethinking code review.** My colleague: "Marcus, if you've already read the code that Claude generated, what's the point of me reviewing it again?"

Traditional code review served multiple purposes: catching bugs, knowledge transfer, enforcing standards. When AI generates code, some purposes become redundant (AI doesn't need knowledge transfer), others become more critical (humans verify AI understood the intent). Shifting review focus from "is this code correct" to "does this code match the specification" and "are tests comprehensive enough."

None of this is settled. Old playbook optimized for a world where writing code was expensive and human attention was cheap. That world is gone.

If you're running similar experiments, I'd like to hear what's working—especially if you think I'm wrong.
