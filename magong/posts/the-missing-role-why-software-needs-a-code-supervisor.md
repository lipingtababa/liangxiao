---
title: 'The Missing Role: Why Software Needs a Code Supervisor'
date: '2026-02-08'
author: MaGong
category: AI Coding
tags: []
description: >
  Civil engineering has independent supervisors with veto power. Software
  doesn't. AI finally makes this role affordable.
excerpt: >
  Civil engineering has independent supervisors with veto power. Software
  doesn't. AI finally makes this role affordable.
lastModified: '2026-02-08'
---

Lovable is valued in the billions and called "Europe's fastest-growing company." Then a security researcher spent 47 minutes poking around its apps and extracted users' debt amounts, home addresses, and API keys.

If 10% of rooms in a building could collapse at any moment, nobody would call it a success. But in software, we do.

Software engineering has product managers, architects, developers, testers, ops. Looks complete. But there is one role that civil engineering has and software engineering does not -- an independent party with veto power who inspects against standards.

In civil engineering, this role is called the *supervisor* (jianli). It has no equivalent in software.

This idea came out of a discussion I had with Li Xuetao at the [Agent Management Forum](https://mp.weixin.qq.com/s/sWONCv2gAzjq3HZLUhY50A).

![Agent Management Forum Episode 13: Learning Engineering from Civil Construction](/images/posts/the-missing-role-why-software-needs-a-code-supervisor/agent-management-forum.jpg)

## What Is a Construction Supervisor?

A construction supervisor is an independent third party -- separate from both the designer and the builder. They belong to no execution team. Their job is to inspect each phase of work against established standards. No sign-off, no moving to the next phase.

Li shared a case: a foundation pit was designed to be 8 metres deep. The construction crew dug 7.5 metres and tried to move on. The supervisor measured it, refused to approve, and held up the project until they dug the remaining half metre.

Why can a supervisor be this uncompromising? Because their signature carries legal liability. Signing off on a shortcut means personal consequences -- potentially prison.

Civil engineering has over 1,100 ISO standards. Even hard hat colours have national specifications. When a supervisor inspects, there is always a standard to inspect against.

## Why Software Has No Supervisor

On the surface, software has similar roles: QA, code review, security audit. But they are fundamentally different.

QA belongs to the same project team. Their interests are aligned with the developers. When a deadline looms, the QA who insists "we can't ship until this is fixed" gets overruled.

Code review is advisory, not a binding veto.

Security audits are typically post-hoc spot checks, not gate reviews for every phase.

The deeper problem: software has no legal accountability framework.

This is the textbook principal-agent problem. When the executor's incentives diverge from the stakeholder's interests, quality cannot be guaranteed without independent oversight. Civil engineering solved this with the supervisor role. Software never did.

In November 2023, Didi, the Chinese ride-hailing giant, botched a Kubernetes upgrade and went down for 10 hours. A platform handling 31.3 million rides per day, completely paralysed. Over 400 million yuan in lost transactions. Legal consequences? Zero.

When scaffolding collapses on a construction site, the supervisor, the builder, and the design firm can all face criminal charges. When software collapses? A few days of online outrage, then everyone moves on.

## The Cost of Having No Supervisor

Veracode's 2025 report found that 45% of AI-generated code contains security vulnerabilities. Java code failure rates hit 72%.

Out of Lovable's 1,645 apps examined, 170 allowed anyone to access user data. Lovable's built-in security scanner only caught 66% of the issues.

And this is not new. Just a few years ago, companies were still storing passwords in plaintext. Nobody stopped them.

## The AI Opportunity

There was always a practical reason for not doing rigorous phase-by-phase inspection in software: cost. Reviewing every step would destroy velocity. Staffing an independent inspection team was prohibitively expensive. And human QA could be gamed -- those who lacked technical depth could only perform superficial checks, while those with deep expertise tended to sympathise with the developers.

AI changes this equation.

Li put it well: "AI's compliance is better than humans'. Run it multiple times, have five AIs review each other -- the enforcement rate is remarkably high."

The cost of enforcing standards drops to near zero. Running extra review passes costs a few tokens. AI does not get pressured by a manager to let things slide.

Standards are also making a comeback. GitHub open-sourced Spec Kit, pushing a "spec first, code second" approach. This is essentially the software equivalent of civil engineering's blueprints and specifications.

## What a Code Supervisor Should Look Like

Borrowing from civil engineering, several elements are non-negotiable.

**Independence.** It cannot belong to the development team. It cannot be hostage to the project timeline. It could be a standalone agent or service, but it must not be "one of us."

**Veto power.** Not "I suggest you fix this" but "this does not pass, therefore it does not merge and does not deploy." Enforced by process, not goodwill.

**Standards-based inspection.** A code supervisor does not need to understand business logic. It inspects against codified standards, item by item. A construction supervisor does not need to know how to lay bricks -- they need to know how to measure.

**Traceability.** Every inspection is recorded. When something goes wrong, there is an audit trail.

We already have fragments: pre-commit hooks, CI checks, security scanners. But they are all optional. None carry veto power. A real code supervisor would integrate these into a hard constraint -- a gate that cannot be bypassed.

## Conclusion

Software engineering is missing a role: an independent inspector with veto power who verifies against standards. Civil engineering has it. Software does not. So quality depends on luck.

AI makes this role economically viable for the first time. What was too expensive before is now nearly free.

But open questions remain. What should software "standards" look like? Who defines them? Without legal accountability, how do you make veto power actually stick?

In your team, who plays the supervisor role? Or does nobody?

---

*Originally written in Chinese. Translated by the author.*
