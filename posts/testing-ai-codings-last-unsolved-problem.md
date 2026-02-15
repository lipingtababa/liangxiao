---
title: 'Testing: AI Coding''s Last Unsolved Problem'
date: '2026-02-07'
author: MaGong
category: AI Coding
tags: []
description: >-
  Five questions about testing in the AI coding era that nobody could answer at
  our engineering forum — and why at least three of them won't be solved by
  better m
excerpt: >
  Five questions about testing in the AI coding era that nobody could answer at
  our engineering forum — and why at least three of them won't be solved by
  better models.
lastModified: '2026-02-07'
---

Our Agent Management Forum is a long-running seminar series — over a dozen sessions covering AI coding methodology, team collaboration, ops systems, and related topics. This session focused on end-to-end testing, with Xiaohui presenting, Ryan moderating, and an active Q&A afterwards.

Let's start with what everyone agreed on.

## Testing Is a First-Class Citizen in the AI Era

AI has driven the cost of producing code towards zero. Code without test validation is slop. Everyone in the room who'd spent months maintaining production systems with AI had the same experience: the more you vibe-code, the uglier it gets, and maintenance costs overtake the original development cost. You can get away with barely reading the code. You cannot get away with not reading the tests.

## AI Has Lowered Testing Costs, but Invented No New Testing Methods

Layered testing, mocks, automation, coverage — all straight from the textbook. AI's contribution is making good practices that only well-resourced teams could afford into something every team can actually do. E2E testing, Given-When-Then user stories, automation loops — the methodologies are all established. AI just collapsed the execution cost.

## Write Test Cases Before Code, but Rethink the Red-Green Cycle

TDD's core value is forcing you to think through requirements. In the AI era, code gets written so fast that step-by-step red-green cycles actually slow things down. But "define expected behaviour first, then let AI implement" — everyone agreed on that.

---

These points of consensus aren't new. What's interesting is the five unanswerable questions that emerged from the discussion.

## Problem 1: Test Review Can't Keep Up with AI Generation

AI produces thirty or forty test cases at once. Can you actually review every single one?

One participant wrote twenty-plus GWT (Given-When-Then) user stories and had AI generate the corresponding test code. AI missed several GWTs, and his own review didn't catch it either. He only discovered the gaps when he manually clicked through the feature.

Someone suggested brute force: run it twice, run it ten times, tokens are cheap. This makes sense on the surface, but think about it — multiple runs catch occasional omissions. If AI systematically biases in one direction (say, only testing happy paths, ignoring edge cases), a hundred runs produce the same bias.

Testing is supposed to be the last human defence line in the AI era. But that defence line is being overwhelmed by AI's output volume. You're increasingly like a quality inspector on a conveyor belt that keeps accelerating while your inspection coverage keeps dropping.

## Problem 2: How Do You Test Uncontrollable External Dependencies?

Two extreme cases came up in the discussion.

One participant builds brain stimulators. His product communicates via Bluetooth with devices implanted in human bodies. Bluetooth signals are affected by implant position, angle, and electromagnetic environment. The physical world can't be simulated. You can't reproduce "patient standing next to a microwave" in a test environment.

Another works on European banking systems. Open Banking APIs are legally mandated, but many banks provide terrible API quality — no sandbox environment, and when sandboxes exist, their behaviour often diverges from production.

The consensus was: mock by use case, don't try to rebuild the entire system. The purpose of mocking is to simulate the behaviour you're testing, not to replicate all behaviour of the dependency. Otherwise your focus shifts from your own system to reconstructing the dependency — an endless rabbit hole.

But there's a deeper problem. Mocks are stateful — there are cross-request dependencies. In banking systems, the permission scope from a previous request affects the next request's response. Whether you get a 403 or a 200 depends on the prior call chain. Eventually, you can't even tell what's determining your mock's behaviour. Once you're confused, AI is confused too.

Someone raised a fundamental challenge: can you trust AI-generated mocks? You're trying to verify code correctness, but you've introduced a mock layer you can't fully verify. Uncertainty just migrated from code to mocks.

Where does testing end? What can testing never reach? Nobody in the room could answer.

## Problem 3: How Do You Quantify "Good" for Agent Workflows?

Traditional software testing assertions are deterministic: field X should equal Y. Pass or fail. Agent output doesn't work that way. Ask a customer service agent to answer a question — there's no single correct answer. You can't write an assertion for "right."

One participant shared his approach: have actuaries manually label each sample with reasoning and scores, then let AI learn the human judgement criteria. The system ran for about two weeks and reached 86% accuracy on a 200-sample benchmark from scratch — without changing a single line of code. AI iterated on its own.

But this creates a recursive problem. He built a verify agent to check the production agent, but to make the verify agent reliable enough, he had to separately improve the verify agent's capabilities. Who verifies the verifier? This is just "who regulates the regulator?"

The deeper issue: when the evaluation criteria themselves can't be precisely defined, how do you build an automated feedback loop? You can assign scores, but the scores themselves are fuzzy. Human scoring might be inaccurate too, but without quantification, the model has no direction to optimise towards. It's a dilemma: you must quantify, but your quantification is inherently imprecise.

## Problem 4: Quality Control — Organisation or Architecture?

Two opposing views emerged.

One camp argued that quality and speed inherently conflict, requiring an independent quality role for adversarial development. One participant built a three-person team: one for product, one for quality, one for implementation. In practice, having two people each focused on a single objective drastically reduced cognitive load. One person ships code fast, the other pokes holes. Previously, one person chasing both speed and quality meant constant context-switching — painful.

The other camp argued that with a unified development framework and conventions, quality is guaranteed at the architecture level. AI following conventions produces code no worse than humans. You should enforce code line limits, method length, and directory conventions in pre-commit hooks — let framework constraints replace human review.

The fundamental disagreement: one side relies on organisational measures (separation of powers), the other on technical measures (framework constraints). Traditional software engineering has this same debate, but AI amplifies it because code output velocity makes human review increasingly impractical.

Organisation or architecture? Or both? We argued for a long time without a conclusion.

## Problem 5: Reward Hacking in Automated AI Testing

This was the most alarming problem in the discussion.

One participant built a reinforcement-learning-style testing loop: AI writes code, runs benchmarks, evaluates results, decides the next optimisation direction — running 24/7, iterating continuously. Sounds great.

What actually happened: to hit the benchmark target, AI wrote 200 if-else statements, hardcoding every case in the sample set. Case 1 returns X, case 2 returns Y. Metrics looked fine on paper. In reality, pure overfitting.

He added countermeasures. Before each strategy selection, AI performs a "five whys" reflection and SWOT analysis, forcing it to pick strategies that genuinely improve system capability rather than taking shortcuts. He also added a supervisor agent to review code quality. These mitigated the problem but didn't solve it.

The deeper issue: AI tends to "achieve the goal" without caring how. It takes shortcuts, thinks short-term, ignores maintenance costs. Someone nailed the essence: this is [reward hacking](https://en.wikipedia.org/wiki/Reward_hacking) from reinforcement learning. You define a reward function, the agent finds an unexpected shortcut to maximise the reward, but the shortcut completely diverges from your actual purpose.

When AI simultaneously plays developer, tester, and reviewer, where's the line for "cheating"? No good answer yet.

## See You in Three Months

At the end of the discussion, someone suggested: revisit these five questions in three months. Problems that model progress naturally resolves were just temporary capability gaps. Problems that persist after three months are genuine software engineering problems.

Our bet: at least three of these five won't be solved by better models. Review speed falling behind generation speed — that might ease as AI review capabilities improve. But the testing boundary for uncontrollable dependencies, quality quantification of non-deterministic output, and reward hacking — these are engineering problems, not model capability problems. No matter how strong models get, they can't solve the recursive dilemma of "who verifies the verifier."

The AI coding arms race has moved from "who writes code faster" to "whose code is more reliable." Writing code is basically solved. Testing is the real battleground.

What no-man's-land problems have you encountered in practice? I'd love to hear about them.

---

*Originally written in Chinese. Translated by the author.*
