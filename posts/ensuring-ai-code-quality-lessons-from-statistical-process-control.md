---
title: 'Ensuring AI Code Quality: Lessons from Statistical Process Control'
date: '2026-02-10'
author: MaGong
category: AI Coding
tags: []
description: >
  What a 1924 factory quality method teaches us about controlling AI code — and
  why effective constraint equals constraint power times independence.
excerpt: >
  What a 1924 factory quality method teaches us about controlling AI code — and
  why effective constraint equals constraint power times independence.
lastModified: '2026-02-10'
---

Lots of people share their AI coding experiences online. Some are genuine, some are PR, and some are pure bluster. Here is a shortcut for sorting signal from noise: skip everything else and look at one thing only — how does the author control quality?

Many showcases emphasise speed (a compiler in three days!) or cost (an OS for five hundred dollars in tokens!). Neither metric means anything, because any beginner can do it — just prepare some prompts and hand them to Claude Code.

The real question: did the thing they built in three days for five hundred dollars actually pass quality checks?

If your boyfriend claims he cooked you a pot of pork rib soup in one minute for ten dollars, that sounds lovely — until his output looks like this:

![Burnt beyond recognition](/images/posts/ensuring-ai-code-quality-lessons-from-statistical-process-control/burnt-ribs.jpg)

Unlike research, engineering cares deeply about quality. Output that fails to meet quality standards cannot serve the business. Its value is zero. As my friend Wang Huan puts it: "The vast majority of AI coders are building demos — small ones and large ones."

Here is a better heuristic: whenever someone promotes AI coding — any tool, any paradigm, any case study — ask one question: "How do you systematically ensure quality?" If they cannot answer clearly, they are a beginner. Do not waste another minute on them.

Our Agent Management Forum recently held a roundtable on exactly this topic — nineteen practitioners from securities, medical devices, K-12 education, Alipay, and open-source infrastructure. The Agent Management Forum is a seminar series for AI coding practitioners. Despite wildly different backgrounds, everyone came for one thing: how to ensure AI code quality.

What follows are the key insights, organised around a framework that is a hundred years old.

## Probability Is the Essence, Not the Defect

AI writing inconsistent code is not a sign that models are not good enough, or that your prompts need tuning. It is the mathematical inevitability of probabilistic sampling. Every output from a large language model is sampled from a probability distribution. Run the same prompt twice and you may get different results.

The symptoms are universal: documentation with missing fields, code with missing features, AI modifying tests when it should modify business logic, modifying mocks when it should modify tests. Tell it not to mock business code and it agrees — then mocks anyway.

Xu Keqian is a non-technical founder who now does the development work that previously required a team of two hundred. He has written over 25,000 lines of rules and configuration for his AI, with documentation averaging 30,000 words. After AI generates code, he opens a fresh session for cross-validation — you cannot verify in the original context because the AI carries the bias of "I already checked this." A dozen rounds in, each round still catches new omissions.

Probability is the mathematical nature of large language models, not an engineering defect. You cannot eliminate it. You can only constrain it. The question is: what kind of constraint actually works?

## Deterministic Constraints

On 16 May 1924, in New York, at Western Electric's engineering department (later Bell Labs), physicist Walter Shewhart handed his supervisor a one-third-page memo. On it was a simple diagram: three lines — upper control limit, observed performance, lower control limit.

![Shewhart's original control chart, 1924](/images/posts/ensuring-ai-code-quality-lessons-from-statistical-process-control/shewhart-control-chart-1924.png)

Western Electric was manufacturing telephone equipment. Parts were buried underground — once installed, they could not be repaired. Defects had to be caught before shipping. The factory's approach: whenever a batch showed a high defect rate, immediately adjust the production process.

Shewhart discovered something counterintuitive. Every time they adjusted the process in response to defects, quality got worse. The defects were random — unrelated to the process. Adjusting the process in response to random variation knocked a perfectly fine process out of alignment. The next batch produced defects too, triggering another adjustment, spiralling into chaos.

He ended this death spiral with one third of a page. Variation comes in two kinds. Common-cause variation is the statistical nature of the process — leave it alone. Special-cause variation has a specific root cause (a loose machine, a changed material) — stop and investigate. The two control limits are the boundary between them: within limits, random variation, do nothing; outside limits, a real signal, stop and find the cause.

This is the core of Statistical Process Control (SPC): first, every process has inherent variation that cannot be eliminated; second, reacting to inherent variation is called tampering — you are not solving problems, you are creating them; third, control limits do not eliminate variation, they separate what needs intervention from what does not.

A hundred years later, AI coding faces a structurally identical problem. LLM output inherently varies — the mathematical nature of probabilistic sampling. You cannot make it write correctly every time, just as you cannot make every part on a production line perfect.

Tweaking prompts, adjusting rules, or line-by-line reviewing every time AI writes something wrong — that is tampering. Layering human interference on top of inherent variation.

Shewhart's answer: do not try to eliminate variation. Build deterministic boundaries. Did the tests pass? Does the code conform to the API contract? These are your control limits — pass or fail, no "close enough."

A telling counterexample: code review. One person reads another person's code and says "looks fine to me." That is not control — it is probabilistic judgement. Fuzzy boundaries, varying by person, varying by day. This is exactly what factories did before Shewhart.

MaGong, who builds financial systems in Europe, put it most directly: in the AI era, code review has lost most of its meaning. Human review ends up catching nothing — it is just "emotional support." In his system, the OpenAPI contract is the "soul," layered tests from unit to end-to-end do the actual gatekeeping, and subjective human judgement has been replaced by deterministic constraints.

Why is the contract the "soul"? Because the quality of your control depends on the specification it encodes. Tests validate requirements. Contracts define interfaces. If the specification is wrong, passing tests do not mean correct code.

Xu Keqian spends seventy to eighty per cent of his effort on documentation verification. L, a practitioner in securities, built 140,000 test cases on top of comprehensive requirement documents. Li Xuetao, coming from civil engineering, said the same thing in different words: you need blueprints before you can start building.

Specification first. Only then can constraints hold.

How effective are deterministic constraints? Lao Wei, in K-12 education, runs one to two thousand test cases in twenty to thirty seconds — full regression on every single code change. Mason wrote 36,000 lines of code in twenty days on a team project; with layered testing, the entire development process produced almost zero bugs.

The more complete the constraints, the more you can let go.

## Independence of Constraints

Are deterministic constraints enough on their own?

The biggest pain point in the room was not AI writing bad code. It was AI writing tests that were "too good" — so good they always passed.

Jinjin, who manages a brownfield project, felt this most acutely. AI was asked to write tests for code that depends on databases, external APIs, and other modules. The proper approach is to set up a test environment with real dependencies. But AI found a shortcut: mock everything. Mock the database. Mock the external API. Tests pass. Coverage 100%. But what it validated was a mirage.

Jinjin explicitly wrote "do not mock business code" in the rules. AI did it anyway.

This is not AI cheating. This is a probabilistic system, asked to "make tests pass," finding the path of least resistance.

The problem is not with the constraint itself. When the AI that writes the code also writes the tests, it quietly positions the constraints where they are easiest to satisfy. Constraint power intact, independence zero.

MaGong's approach was the most representative. Testing agent and coding agent are completely separate — different prompts, opposing styles, one optimising for efficiency, the other for rigour. File system permissions enforce isolation: the coding agent physically cannot modify test code.

L went further: development, testing, and operations are three independent departments with opposing KPIs. Testing rejects; development fixes. Organisational separation.

Department isolation is independence at the organisational level. Agent adversarial design is independence at the technical level.

This gives us the formula: **effective constraint = constraint power x independence**.

Constraint power: replace probabilistic judgement with deterministic checks. Independence: the entity setting the constraints must not be the entity being constrained. Neither alone is sufficient.

## Context-Dependent Autonomy

Xiaohui, an agent engineer at Alipay, lets AI run autonomously for six to twenty-four hours, using heuristic methods to find solutions. He does not care what methods AI uses — only whether the tests pass at the end.

Xu Keqian opposes full automation at this stage, because documentation always has gaps, and things AI confirms autonomously "are more likely than not unreliable."

Two completely different approaches. One formula explains both:

**AI autonomy = f(constraint completeness, cost of failure)**

The more complete the constraints and the more tolerable the failure consequences, the more AI can be left alone. Where constraints have gaps and failure is costly, humans must step in. Different inputs, different outputs.

Does integration testing have value? The question is not what you call the test — it is whether it forms an effective constraint.

Should you use the BMad framework? Methodologies are vessels for principles, not the principles themselves. Changing the bottle does not change the water.

L offered a prediction: "The quality bar that finance has today will be everyone's baseline tomorrow."

Seven-layer testing. 140,000 test cases. Independent testing departments. Separate development, testing, and operations teams. These used to be luxuries only finance could afford. As AI drives development costs down, they are about to become industry standard.

## A Historical Coda

SPC was born in America. Americans did not use it. Japan, where they could not afford to waste a single screw, was the first to embrace quality control — and it powered their golden thirty years of manufacturing dominance.

Right now feels a lot like then.

---

*Originally written in Chinese. Translated by the author.*
