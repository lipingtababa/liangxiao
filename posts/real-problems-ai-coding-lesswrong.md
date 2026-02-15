---
title: The Core Problems of AI Coding
date: '2024-12-15'
author: MaGong
category: AI Coding
tags: []
description: >-
  After five months of building production systems with AI coding tools, I've
  identified three core problems that actually matter. This post focuses on
  ensuring q
excerpt: >
  After five months of building production systems with AI coding tools, I've
  identified three core problems that actually matter. This post focuses on
  ensuring quality and building effective human/LLM hybrid teams.
lastModified: '2024-12-15'
---

# The Core Problems of AI Coding

**TL;DR**: After five months of building production systems with AI coding tools, I've identified three core problems: (1) ensuring outputs match intentions, (2) maintaining trustworthy quality in AI deliverables, and (3) structuring effective human/LLM hybrid teams. This post focuses primarily on problems 2 and 3, with insights from deploying microservices using LLM-assisted development. Problem 1 will be explored in a future post.

---

In July, I wrote an article titled "Pseudo-Problems and Core Problems in AI Coding." Five months of practice later, I reread my old article and realized my understanding has leveled up.

I now believe the core problems of AI coding are:

1. How do you make sure AI coding actually gives you what you want?
2. How do you make sure the quality is trustworthy?
3. How do you build a supersonic human/LLM hybrid team?

## Making Sure AI Deliverables Are Actually Good

Let's start with the second question. My friend Xu Keqian pointed out something important:

> The paradox of continuously working agents is that each step might proceed to the next without proper quality control.
>
> For the same code, using different prompts, starting new sessions, or cross-testing with multiple agents produces different results. What conditions require further testing, when cross-testing is needed, whether to fix the problem or the original design, or something else entirely - having agents judge among all these variations is still unreliable at this stage.

This insight comes from expensive real-world experience. If you see someone claiming their AI agents work continuously for 48 hours, just treat them like someone claiming they invented a perpetual motion machine. You don't need to analyze further.

Some people say context engineering - feeding all the context to the LLM - solves this. In practice, too much context makes LLM output worse, like how your manager rambling too much kills your productivity. The best way to select context is still direct human prompting.

Others suggest multi-agent verification as a substitute for human review. I've tried this. Cross-validation helps a bit, but there's a fundamental problem: LLMs share blind spots. For reasons I don't fully understand, LLM common sense differs from human common sense. Multiple LLMs sitting together still make the same stupid mistakes.

Luckily, unreliable quality isn't an LLM-specific problem - humans are just as unreliable. Software engineering has good solutions already. Here's what I use:

1. **Task decomposition** - Don't give AI big tasks you can't verify
2. **Platform engineering** - Humans own the framework, AI handles tedious business logic
3. **High-density testing** - For one microservice, I built five test layers: unit, component, API, integration, and E2E
4. **DevOps integration** - Deploy right after development, use canary releases
5. **Iterative development** - Don't build what you haven't figured out; when you have, don't fear rewrites
6. **Observability and runbooks** - Stop AI from guessing randomly at failure causes

None of this is new. But pushing this in human teams used to be expensive, slow, and practically impossible. AI makes it actually doable.

Still, as Xu Keqian said:

> For the same goal, I only dare release after repeated multi-angle cross-testing, including verification from multiple user perspectives. Every change reveals new problems. So directly proceeding to the next round after passing detection is very unreliable.

My approach has limited effectiveness. Still exploring.

## Building a Supersonic Human/LLM Team

This problem is undervalued. I see many big companies' R&D departments pushing tools and measuring success by coverage rates - aiming for 98% adoption. Here's the paradox: If your tool makes one person 5x productive, why do you need everyone using it? If your business didn't grow but workload increased 5x, that's bad news, not success.

There's an even more absurd metric: code adoption rate. This is as ridiculous as outsourcing companies using Lines of Code to measure output. Even the worst outsourcing shops dropped LoC years ago, but some AI coding teams have dusted off this ancient metric and wear it like vintage fashion.

In practice, human-to-human communication costs way more than human-to-AI communication, with more distortion. A better approach: forget universal rollout. Build a few AI-human hybrid teams and use them like special forces.

My friend Wang Jinyin and I have the **Xiaolongbao Theory**: your team's appetite shouldn't exceed one serving of xiaolongbao (soup dumplings). One serving is typically about 6-8 dumplings, enough for roughly three people to share - small enough that everyone can communicate directly without coordination overhead. My current structure follows this: one lead engineer, one test engineer, and we collaborate with different product owners per project. Progress is very fast, attrition very low, feedback surprisingly good.

## Making Sure AI Gives You What You Actually Want

This is the hardest and most valuable question. I'll discuss it next time.

---

*Translated from Chinese by the author*
