---
title: 'Beyond the Alpha Wolf: Building AI-Native Dev Teams That Scale'
date: '2026-01-26'
author: MaGong
category: AI Coding
tags: []
description: >
  The alpha-wolf model of AI coding works brilliantly — if you can find a
  unicorn. Product Tri-Ownership offers a replicable alternative.
excerpt: >
  The alpha-wolf model of AI coding works brilliantly — if you can find a
  unicorn. Product Tri-Ownership offers a replicable alternative.
lastModified: '2026-01-26'
---

This is a response to Ed Huang's recent essay "Vibe Engineering 2026.1". Ed is the CTO of PingCAP, makers of TiDB. If you haven't read it, I'd recommend it.

His core observation: top models with mainstream tools already exceed most senior engineers. He used AI to rewrite TiDB's PostgreSQL compatibility layer, and the code quality was "near production-grade." But the human bottleneck shifted to acceptance — he spends 90% of his time evaluating AI output, not writing code.

His prediction for the future of software teams:

> This way of working is like an alpha wolf leading a pack of agents, cultivating its own territory. But a territory can't accommodate two alpha wolves — that makes 1+1 < 2.

PingCAP is one of China's best infrastructure companies. Ed Huang is one of China's best engineers. So how transferable is this approach? If you and I copy it directly, are we learning from the best — or just cargo-culting?

## The Alpha Wolf Is an Elite Strategy

Ed's "alpha wolf + pack" model puts a single superstar engineer in end-to-end control of a product.

Qiniu Cloud, a Chinese cloud storage company, tried something similar — a **product architect** role where one person owns PRD, architecture, implementation, and testing. Their CEO's evaluation standard was blunt:

> If you can't handle end-to-end ownership within a set timeframe, you're out. We'll find someone who can.

But a product architect needs the combined skills of a traditional PM, architect, lead developer, and test lead. People who come close to that profile are extraordinarily rare. Most teams at most companies simply can't find them. I run the Agent Management Forum, a community focused on AI coding methodology — even there, only three people would credibly claim to meet this bar.

And even if you find one, how do you know they won't leave to start their own company next month? All three of those people are CEOs. None of them work for someone else.

The fatal flaw of the elite strategy: **it depends on a talent market that barely exists.**

## Decomposing the Super-Individual: Product Tri-Ownership

Outside software, civil engineering solved a similar problem long ago. They don't rely on super-individuals. They use role separation to guarantee quality. The architect defines the space, the structural engineer designs the load-bearing system, the independent inspector verifies compliance, and the contractor builds. Four roles, four specialisations, mutual accountability.

Borrowing from this model, my colleagues and I developed the Product Tri-Ownership (PTO) framework.

PTO decomposes the super-individual's work:

**Alpha wolf / super-individual** (one person does everything end-to-end) splits into:

| Product Owner | Quality Owner | Tech Owner |
|---|---|---|
| Owns *what* to build | Owns *what correct looks like* | Owns *how* to build it |
| Architect | Inspector | Structural engineer |

The attentive reader will ask: where's the contractor?

The contractor is AI. Agents write code, run tests, generate docs — just as contractors lay bricks to blueprints. They don't get authorship credit.

### Product Owner: What to Build

The PO merges traditional PM and product owner roles: defining product vision and business value, having the courage to say no, managing user stories and acceptance criteria, planning release cadence, and handling stakeholder communication.

The PO is **accountable for outcomes**, not output. They're not a requirements secretary — they're the person deciding what's worth building. Without a competent PO as the first quality gate, the entire downstream quality chain breaks down.

### Tech Owner: How to Build It

The TO owns technical implementation, leading multiple AI agents to produce correct software. They handle detailed design, code review reports (not the code itself), and tooling decisions. But their most important job is **orchestrating multi-agent workflows**.

Ed Huang observed:

> Current coding agents start struggling to solve problems in one shot once a single module exceeds roughly 50,000 lines of code. Agents typically don't proactively manage project structure or module boundaries.

Here's a workflow one of our TOs designed:

- `/story` — generate detailed design from user story
- `tester` — TDD red phase (write failing tests)
- `coder` — TDD green phase (make tests pass)
- `/qc` — quality check and commit
- `deployer` — monitor CI/CD through staging and production

Different task types need different workflows. Bug fixes differ from new features. Greenfield differs from brownfield. The TO builds, observes, and optimises the right workflow for each situation — and handles exceptions when things go sideways.

### Quality Owner: Is It Correct?

The QO owns delivery quality. Unlike a traditional tester, the QO designs the quality process and manages it across the entire lifecycle.

An independent QO solves several AI coding problems:

**Offloading the bottleneck.** In PingCAP's practice, Ed spent 90% of his time on acceptance. He could handle it because he's exceptionally capable. For most people, this becomes a chokepoint. PTO creates a dedicated role for it.

**Adversarial testing.** Anyone with AI coding experience knows LLMs are excellent at gaming the system. If they can't pass a test case after several attempts, they'll comment it out to make the suite green. NASA established its Independent Verification & Validation (IV&V) programme after the Challenger disaster — the core principle being that software verification must be performed by an organisation independent of both the developer and the buyer. We borrow this thinking. The QO's agents provide a degree of adversarial independence from the TO's agents.

**Full-lifecycle quality control.** The QO participates in every phase of the SDLC, embedding layered testing (unit, integration, end-to-end) at each stage. When the PO writes requirements, the QO co-authors acceptance criteria to ensure they're verifiable. In our projects, we use Makefile as the test entry point for Go projects, forbidding Claude Code from calling `go test` directly, and embed `make test` in git commit hooks and CI workflows to catch problems early. The alpha-wolf model concentrates all quality pressure at final acceptance. PTO distributes it across the entire pipeline, lowering the skill threshold required.

## One Story Per Day

At full cadence, a PTO team should complete **one user story per day**.

A typical day: the PO finishes the user story in the morning while the QO defines acceptance criteria. Before lunch, AI agents complete the detailed design, the TO reviews and approves, triggering the dev workflow. Over lunch, AI delivers a first pass of code and tests. In the afternoon, the TO reviews code review reports through possibly several iterations. Before end of day, CI triggers end-to-end validation, and the QO signs off for merge.

Why this fast? The heaviest work — coding — is handled by multiple AI agents. The three owners work in parallel. The QO's test framework is pre-built, not ad hoc. Automated workflows eliminate handoff delays. And the agents doing the heaviest lifting don't need lunch breaks.

**One rule: the three owners must sit together.** Physically co-located, problems discussed instantly, no scheduling meetings. Daily standups aren't enough — iteration speed demands decision frequency that can't wait until tomorrow's standup.

If a story takes more than a day, it's too big. Split it. Stories in the AI era should be much smaller than in traditional development.

### Traditional Practices Become Bottlenecks

Many teams see no speed improvement after adopting AI because legacy processes drag them back:

- **Four-eyes code review**: every line needs two reviewers. When AI finishes a feature in a day, waiting for two people to schedule their review takes three days.
- **Change Advisory Boards**: every release needs committee approval. AI can deploy ten times a day; the CAB meets once a week.
- **Manual deployment**: AI finishes code, then waits for ops to schedule a manual deploy.

## Supporting Roles

Beyond the three owners, you need:

**Sponsor**: provides resources and resolves conflicts. First priority: adequate token budget and suitable hardware — AI-native development bottlenecks are often token cost, not headcount. The sponsor also makes final calls when the three owners disagree.

**Architect**: defines system architecture, module boundaries, interface contracts, coding standards, and tech stack. If agents struggle beyond 50K lines per module, the architect pre-decomposes the system to keep each module within AI-manageable scope. In smaller projects, the TO can fill this role.

**Platform Engineer**: owns production operations, monitoring, security compliance, and cost optimisation. Should also help the QO build and optimise the CI/CD pipeline.

**Specialist Experts**: consulted as needed, not full-time. A friend building a consumer service needed a UI/UX designer — the designer doesn't code but collaborates with AI tools like Lovable to produce a UI kit for the TO. Security specialists, DBAs, and similar roles follow the same pattern: engage when needed, no full-time headcount required.

## The Next Core Problem in AI Coding

Individual AI pair programming is mature practice. Claude Code, Cursor, and similar tools have proven this. But how do *teams* collaborate with AI agents?

The next core problem: after AI agents have driven implementation costs towards zero, how do you systematically build human-AI teams that sustainably guarantee delivery quality — and convert that productivity into competitive advantage?

Ed Huang's alpha-wolf exploration proved AI-native development is viable. But alpha wolves are too scarce.

Product Tri-Ownership offers a replicable framework: decompose "the impossible super-individual" into "three trainable specialist roles," making AI-native development accessible to ordinary teams.

What does your company's AI-native team structure look like? What problems have you hit? I'd love to hear about them.

---

*Originally written in Chinese. Translated by the author.*
