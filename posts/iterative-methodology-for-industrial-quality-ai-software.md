---
title: Iterative Methodology for Industrial-Quality AI Software
date: '2025-07-26'
author: MaGong
category: AI Coding
tags: []
description: >-
  I keep hearing people complain that AI-written code is unusable. I think the
  reason is simple: they're not applying iteration as a methodology. Iteration
  means ...
excerpt: >
  AI won't deliver working software from a single prompt. Three iteration loops
  make it work.
lastModified: '2025-07-26'
---

I keep hearing people complain that AI-written code is unusable. I think the reason is simple: they're not applying iteration as a methodology.

Iteration means converging on a fixed target through repeated attempts. In software development, it applies to nearly every stage. Let's start with requirements.

## Requirements Have Three Common Problems

1. **The requirement itself is garbage.** "Build me a women's fashion e-commerce site" tells you nothing actionable.
2. **Sender and receiver have different mental models.** They share different contexts, so the same words mean different things.
3. **Requirements shift.** Someone asks for Android, macOS, and Windows builds compatible with Windows XP. After learning the cost, they say "just make it a web app."

All three problems improve through iteration. My Requirements Analyst role makes a decision on each requirement:

- **Nonsensical** -- No further action. The requirement was filed against the wrong project, or it's "make me a plan to get rich while lying on the couch."
- **Clear** -- Summarise the understanding and action plan, post it as a comment on the issue tracker (Linear or GitHub Issues). This document becomes the reference for every downstream role: developer, troubleshooter, security engineer.
- **Meaningful but unclear** -- The AI asks clarifying questions and sets the ticket status to "Awaiting Clarification." The requester answers via issue comments. This back-and-forth can iterate multiple times, with each round bringing both sides closer to shared understanding.

The third case is textbook iterative convergence. The first two are exit conditions. With this process in place, we avoid a great deal of wasted work. This iteration happens between AI and product manager.

## From Natural Language to Test Cases

When we say a requirement is "clear," we mean clear to a human reading natural language. But natural language is not executable. So my Synthetic Engineering Team has another step: translating requirements into test cases. The Analyst handles this. After writing the test case code, it goes straight into a pull request. The human developer reviews it, focusing on one question: do the test cases, expressed in code, match the requirement expressed in natural language? If not, the ticket moves to "Test Cases Refining" with feedback. The AI Analyst revises accordingly.

This iteration happens between AI and human developer.

## Implementation Through AI-AI Iteration

Once test cases are locked, the AI Developer role starts work. The task is unambiguous: pass the tests. In my experience, even on familiar projects, the first implementation almost never passes. There are always issues. That's when the Troubleshooter steps in -- analysing the test cases, the changed code, and the error messages to produce a diagnosis, recorded in `troubleshooting.md`. The Developer then fixes based on that document. This back-and-forth can run several rounds.

This iteration happens between AI and AI. Currently I try to keep humans out of this loop, though I may add human checkpoints later.

## AI Is Not Aladdin's Lamp

AI won't grant your wishes from a single incantation. It's more accurate to think of AI as a colleague who is smart, knowledgeable, impatient, and occasionally lazy -- just like a human. Organising a team of these AI agents to build software requires the same thing as organising human engineers: sound software engineering methodology.

---

*Originally written in Chinese. Translated by the author.*
