---
title: "Pseudo-Problems and Core Problems in AI Coding"
date: "2024-07-15"
author: "MaGong"
category: "AI Coding"
tags: []
description: >
  As an AI coding enthusiast, I've noticed many smart people spending time on pseudo-problems. Here's what actually matters.
---

# Pseudo-Problems and Core Problems in AI Coding

As an AI coding enthusiast, I spend every day hands-on exploring and actively exchanging ideas with fellow enthusiasts. In this process, I've noticed many smart people spending time on pseudo-problems and less important issues. I'll list them here for discussion.

## Pseudo-Problem #1: One-Command Software Generation

The first pseudo-problem is "how to generate complete software from a single sentence." For example, ByteDance's Trae team tried to generate an e-commerce site from one command when launching Solo. This approach is theoretically impossible. For details, see Da Ming's article "After 30 Years of Experience, I'll Tell You Why 'One-Command Website Building' Will Likely Only Create a 'Shit Mountain'."

In Da Ming's plain words: for any such product, I would give this one sentence:

> "Make me a website that earns $1000 daily, starting today. Go do it."

Such products fail at the goal-setting level, and their actual implementation is absurd. After Trae released their one-command e-commerce demo, users tried it and found it completely unworkable. Trae's official response actually undermined their "one-command website" slogan.

Lovable is currently the hottest no-code building tool for beginners. Their tutorial for beauty industry users doesn't promote "one-command building" either. Instead, they work in stages, gradually adding features and adjusting approaches.

Promoting this theoretically impossible "software perpetual motion machine" only misleads non-professional users and damages the industry's reputation.

## Pseudo-Problem #2: Getting Code Right in One Shot

The second pseudo-problem is "writing code correctly the first time." Amazon's Kiro team represents this approach. They built in a software development process: first generate specs, then review specs, generate design and tasks, implement each task one by one, then summarize and deliver successfully.

This sounds good and applies the divide-and-conquer methodology common in software engineering. Many friends even ported this to Claude Code. But experienced software veterans can immediately see that Kiro's approach is typical waterfall development. It assumes:

1. Customers know exactly what they want from the start
2. Architects (human and AI) can accurately translate requirements into code tasks
3. Developers (AI) can strictly follow the architect's design
4. If each small task is completed, the entire system will work as expected

No need to elaborate - none of these assumptions hold. Friends who practiced this method all found that what Kiro delivered wasn't what they wanted, or even what was described in design.md. I discuss the reasons for failures and solutions in another article: "Using Iterative Methodology to Let AI Deliver Industrial-Quality Software."

## Low-Value Real Problem: Claude Code Tips and Tricks

There's a real but low-value problem: "Claude Code usage tips." This problem is practical, and many shared tips are useful. But frankly, AI will definitely replace humans as the main force in SDLC; humans will be marginalized. Researching how AI assists humans in writing code only has short-term value.

## Boring Problem: How to Save Money

Another very boring problem is "how to save money." I see many friends spending tons of time researching cost savings. Actually, Claude Code Max plan is only $200, less than minimum wage per month. You hired a 985-graduate-level programmer who knows all languages for minimum wage - you got a great deal. Why would you want to cut their salary?

## The Core Problem That Actually Matters

I personally believe the most important problem now is: **How do you build a synthetic software development team using humans and AI based on current LLM capabilities?**

Specifically:

1. **Treat both humans and AI as engineers** - Understand their strengths and weaknesses
2. **Assign different roles** - Such as requirements analyst, coder, troubleshooter, etc.
3. **Define appropriate control points** - Design inputs and outputs for each stage. For example, a coder's input needs a requirements specification, and output includes code and test cases
4. **Create a flexible combination method** - For different projects, or even different stages of the same project, freely combine the above stages. For example, financial companies' SDLC needs personal information protection review stages, while Pinduoduo's projects don't

Fellow enthusiasts interested in researching this problem, feel free to leave me a message on the official account. Let's exchange ideas and discuss together.

---

*Originally written in Chinese. Translated by the author.*
