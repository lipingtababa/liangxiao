---
title: 'Forward Deployed Engineer: Silicon Valley''s Rebranded Delivery Engineer'
date: '2025-12-15'
author: MaGong
category: AI Thinking
tags: []
description: >
  Silicon Valley is hyping Forward Deployed Engineers as innovation. I've seen
  this movie before — it's called zhongtai.
excerpt: >
  Silicon Valley is hyping Forward Deployed Engineers as innovation. I've seen
  this movie before — it's called zhongtai.
lastModified: '2025-12-15'
---

In 2025, Silicon Valley discovered Forward Deployed Engineers. OpenAI plans to hire 50 by year-end. Anthropic, Databricks, Google DeepMind — all recruiting. FDE job postings on LinkedIn surged 800%. Industry media crowned it "the hottest role of the AI era."

My first reaction: isn't this just a delivery engineer? On-site implementation, post-sales support, technical pre-sales — slap an English name on it and suddenly it's "innovation"?

Then I looked into Palantir, where the concept originated. Their former CFO Colin Anderson publicly called FDE "lighting equity on fire," describing "spectacular pyres of time and treasure and travel expenses that amounted to nothing."

When your own CFO can't stand it, how does this become the industry's next big thing?

This story reminds me of China's "zhongtai" (middle platform) craze. In 2015, Alibaba launched the zhongtai concept — a kind of enterprise-level capability reuse platform. Within five years, every major tech company followed. The industry mantra was "build zhongtai or die." Then in 2023, Alibaba itself abandoned the strategy.

I'll make a prediction: Forward Deployed Engineer is the next zhongtai — a buzzword that looks beautiful, is riddled with problems, and will eventually be abandoned.

## The Emperor's New Clothes

Here's Palantir's official description of FDE work:

> "Most weeks, I spend a couple of days working at the customer premises, some of that time in meetings with technical or business stakeholders, and the rest of the time monitoring, debugging, deploying, or configuring our software for that customer."

In plain English: go to the client site 2-3 days a week. Attend meetings. Debug. Deploy. Configure. Back at the office, write minor code changes and answer emails.

This is a delivery engineer. An on-site implementation consultant. A post-sales support engineer. Every enterprise software company has them. Kingdee and UFIDA, China's biggest ERP vendors, deploy armies of implementation consultants through partner networks. But you've never seen them rebrand "ERP Implementation Consultant" as a revolutionary new role and watch LinkedIn postings surge 800%.

Because it's a normal job. Not worth the hype.

Here's a test I'd like to propose — call it the Spreadsheet Test:

If I sell you Excel, you can use it. If I sell you an "Excel Platform" but you need my engineer on-site 3 days a week to make spreadsheets, I don't have a product — I have a very expensive spreadsheet consulting service.

Same logic: if your "AI platform" or "data platform" requires permanently embedded engineers to function, you're not selling a product. You're selling engineering hours.

## The Data Behind Palantir

Here's a fact few people mention: until 2016, Palantir had more FDEs than software engineers.

What kind of software company has more field consultants than developers?

The 2024 numbers are revealing too. Palantir had 3,936 employees, with 1,383 in engineering (44%). But they no longer disclose the FDE-to-SWE ratio. I'll let you guess why.

Revenue composition tells a story. In 2024, Palantir's total revenue was $2.9B — 55% from government ($1.57B), 45% commercial ($1.30B). The trend matters more: government revenue share grew from 46.5% in 2019 to 55% in 2024. They market their commercial success while becoming increasingly dependent on government contracts. In a normal commercial market, the FDE model struggles.

FDE median compensation is $221K versus $195K for regular software engineers. Looks like FDEs are worth more? That's only a 13% premium for:

- 3-4 days per week at client sites
- Heavy travel
- Glassdoor reviews citing "bad work-life balance"
- Internal descriptions of the development approach as "jungle combat: quick-and-dirty code"

Thirteen percent more pay for significantly worse quality of life and mounting technical debt. Good deal?

## Why FDE Thrives in Defence Procurement

If the model is this problematic, why does Palantir keep winning contracts?

The revolving door.

In 2022, the top 20 US defence contractors employed 672 recently retired Pentagon officials. Former Joint Chiefs Chairman Joseph Dunford joined Lockheed Martin's board five months after retirement. Pentagon's own audits found defence contractors achieving 40-50% profit margins through waste and corruption.

Palantir fits this ecosystem perfectly. Founded in 2003, when traditional VCs refused to invest, the CIA's venture arm In-Q-Tel became an early backer. Intelligence agencies didn't just invest — they "helped design the product" through nearly three years of "iterative collaboration."

CIA funded it. CIA designed it. CIA became the customer. Textbook government contracting.

A friend put it well: "Not even Huawei — China's most connected tech company — could walk into PetroChina and say 'I don't know what we can do for you, but let me embed an engineer, look at your data, take up your time, build an MVP, and you can decide later. Oh, and you're paying from day one.' That would be insane."

It's insane in a normal market. It works in US defence procurement because there's enough institutional corruption to sustain it.

In commercial markets, buyers demand clear deliverables, comparable quotes, and the ability to switch vendors. FDE is lock-in by design — once your team depends on embedded Palantir engineers, switching becomes nearly impossible. This works in defence because decision-makers aren't spending their own money. In commercial markets, CFOs do the maths.

## When FDE Meets Reality: The NHS Disaster

Let's see how FDE performs in a relatively transparent market.

In November 2023, Britain's NHS signed a 7-year, GBP 330 million contract with Palantir for a national data platform.

One year later? Fewer than 25% of 215 NHS hospital trusts were actually using the system. Many refused deployment outright, calling it a "step backwards on existing systems."

The contract itself was suspicious — 416 of 586 pages were redacted. Data protection terms were still "subject to commercial negotiation" after signing. Patients couldn't opt out of data collection.

This is FDE in a transparent market. Political connections win the contract, but a bad product is still a bad product. Users who don't want it won't use it.

A platform requiring permanently embedded engineers can't scale to 215 hospitals. Station an FDE team at each one? Who pays for that?

The NHS case demonstrates the fundamental flaw: FDE is not a scalable business model.

## Zhongtai's American Twin

The parallel with China's zhongtai is almost too perfect.

| | Zhongtai | FDE |
|---|---|---|
| Clear definition? | "We still don't have one" | Equally confused |
| Promoter | Alibaba | Palantir |
| Spread | All major tech in 5 years | 800% job posting surge in 2025 |
| Internal criticism | CEO admitted failure in 2023 | CFO called it "burning money" |
| Hype cycle | Peak then disillusionment | Currently at peak |

Both are vaguely defined buzzwords. Both were promoted by a major company and copied industry-wide. Both saw the promoter eventually retreat.

A friend made a sharp observation about China's defence industry: "Chinese military-industrial IT companies didn't rebrand the 'military representative' role as 'backward deployed manager' and then market it as a world-leading innovation."

Every industry has on-site roles. That's unremarkable. Only in hype-driven environments do ordinary jobs get rebranded as revolutionary breakthroughs.

## Product Company or Consultancy?

The fundamental question: is Palantir a software company or a consultancy?

A software product should be:

- Usable by customers with reasonable independence
- Deployable through partner networks or the customer's own IT team
- Free of permanent vendor staff on-site
- Bounded by clear functionality and APIs

Microsoft Office, Salesforce, AWS — customers self-serve with documentation, APIs, and partner ecosystems. Even Kingdee and UFIDA deliver through authorised partners, not permanent on-site engineers.

Palantir? Industry reports say customers "become dependent on company's employees." FDEs directly commit fixes to the platform. Each deployment may be a different fork.

The Spreadsheet Test again: if your "platform" needs permanent on-site engineers to function, are you selling a product or labour?

Compare with traditional defence contractors. Lockheed Martin delivers an F-35 — it flies, it has maintenance manuals. Boeing delivers a 787 — airlines operate it themselves. Raytheon delivers missile defence systems — they work after installation, with training and documentation.

Palantir delivers a "data platform" — requires a permanent FDE team or it doesn't work.

The difference: hardware companies sell products. Palantir sells engineering hours plus a GitHub repo.

Palantir's business model is closer to Accenture or Deloitte than to Microsoft or Oracle. But its market cap is valued like a software company. That's the problem.

## The Virus Is Spreading

Ironically, while Palantir's own model shows cracks, Silicon Valley is copying it at speed.

OpenAI formed an FDE team in early 2025, hiring 50 people to "embed with Fortune 500s to actually apply generative AI, fine-tuning models, building new agentic workflows, and proving the business case."

Note the phrase: "proving the business case." That's pre-sales.

Anthropic calls theirs "Applied AI Engineers" and plans a 5x team expansion. ElevenLabs, Databricks, Salesforce, Google DeepMind — all hiring FDEs.

Result: 800% surge in FDE postings. Media celebrates. I see zhongtai all over again.

Alibaba pushed zhongtai in 2015. Gartner called peak hype in 2020. Alibaba abandoned it in 2023. Peak to disillusionment: eight years.

Palantir had more FDEs than SWEs in 2016. Their own CFO criticised it in 2024. The whole industry started copying in 2025. How does this story end?

My optimistic guess: companies like OpenAI and Anthropic learn from Palantir's mistakes and use FDEs as short-term pre-sales and onboarding roles, not permanent embeddings. Sustainable.

My pessimistic guess — and the one I lean towards: the AI industry is repeating zhongtai's mistake. Repackaging an old delivery model as "innovation," riding industry-wide groupthink, then collectively abandoning it in 3-5 years.

Why pessimistic? Because:

- Palantir's own CFO called it burning money. Why do other companies think they'll do better?
- NHS's 25% adoption rate shows the model fails in transparent markets. Why would enterprise AI be different?
- If the model actually worked, why is Palantir shifting towards government contracts, not away from them?

An 800% surge in job postings isn't validation. It might just be groupthink. Remember, every major Chinese tech company followed Alibaba into zhongtai — and the promoter itself walked away.

## Conclusion: Delivery Engineer Is the Honest Name

Forward Deployed Engineer is not innovation. It's a delivery engineer, an on-site implementation consultant, rebranded with a Silicon Valley sheen.

If you have a genuinely good product, customers can use it themselves or deploy through partners. If your "platform" can't function without a permanent on-site team, your product isn't ready — or it isn't a product at all.

Forward Deployed Engineer is the hype. Delivery Engineer is the honest truth. But the honest version doesn't attract VC money or top LinkedIn's trending jobs.

As someone who watched China's cloud computing and zhongtai hype cycles from the inside, I've seen this pattern too many times: concept catches fire, industry piles on, problems surface, promoter walks away.

I predict FDE will join zhongtai as an industry punchline within 3-5 years. If you're an FDE at Palantir or OpenAI — I'd love to hear why this time is different. With data and cases, not buzzwords.

---

*Originally written in Chinese. Translated by the author.*
