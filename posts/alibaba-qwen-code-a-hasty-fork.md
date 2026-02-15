---
title: 'Alibaba''s Qwen Code: A Hasty Fork'
date: '2025-08-09'
author: MaGong
category: AI Coding
tags: []
description: >-
  Alibaba's qwen-code CLI is a fork of Google's Gemini CLI. The licence is
  Apache 2.0, so legally there's nothing wrong with this. But legality aside,
  the problem
excerpt: >
  Alibaba forked Google's Gemini CLI to create qwen-code. Legally fine.
  Strategically questionable.
lastModified: '2025-08-09'
---

Alibaba's [qwen-code](https://github.com/QwenLM/qwen-code) CLI is a fork of Google's [Gemini CLI](https://github.com/google-gemini/gemini-cli). The licence is Apache 2.0, so legally there's nothing wrong with this. But legality aside, the problems pile up fast.

## Sloppy Execution

Users quickly discovered that qwen-code's `/init` command generates a `GEMINI.md` file instead of `QWEN.md`. A leftover from an incomplete find-and-replace during the fork.

> What happened?
> While exploring the CLI, I noticed that the /init command generates a GEMINI.md file.
> What did you expect to happen?
> The /init command should ideally generate a QWEN.md
>
> [QwenLM/qwen-code#231](https://github.com/QwenLM/qwen-code/issues/231)

## The Fork Dilemma

Google's Gemini CLI is open-source in licence but not in governance. The top contributors are all Google employees, and external contributions are rarely accepted. This means Gemini CLI will never accommodate non-Google models.

Alibaba now faces a lose-lose choice: either invest heavily to maintain a diverging fork, or follow Google's roadmap and accept being a second-class citizen on their own CLI. The first option defeats the cost-saving purpose of forking. The second is unacceptable for a company positioning Qwen as a leading model.

## Brand Damage

When a major company builds its client tool on a codebase it doesn't control, users naturally ask: does this mean they lack the resources, or simply don't care enough to invest?

On X, [@mkw3dd](https://x.com/mkw3dd) dug through the qwen-code repository and found Gemini references scattered across multiple files -- README, gitignore templates, package configs, even a privacy notice component for the Gemini API. His verdict was blunt:

> "If you fork Gemini CLI into qwen-code but can't even clean out the Gemini references, I'm not going to take your ambitions seriously."

![X thread showing leftover Gemini references in qwen-code repository](/images/posts/alibaba-qwen-code-a-hasty-fork/twitter-thread.jpg)

## A Better Path

Gemini CLI itself isn't great -- its issue tracker is flooded with bug reports. Google's models aren't competitive in the coding space either, so the CLI is unlikely to become a de facto standard. Forking it is like choosing poor foundations and then renovating -- an unnecessary detour.

If Alibaba genuinely didn't want to build a CLI from scratch (which, with AI assistance, wouldn't even cost that much), the smarter move would have been to sponsor a community-led project. [OpenCode](https://github.com/opencode-ai/opencode) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code) both demonstrate what a well-executed AI coding CLI looks like. Any of them would have been a better starting point than Gemini CLI.

---

*Originally written in Chinese. Translated by the author.*

