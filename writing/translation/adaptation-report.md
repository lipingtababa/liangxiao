# Adaptation Report: WeChat Articles for magong.se

This report analyses 14 extracted WeChat articles from 瑞典马工 (MaGong) and recommends an adaptation strategy for magong.se — an English blog serving as a "display window" for international readers.

---

## 1. Article Inventory

### Category: China AI (2 articles)

**Article C1: 阿里的qwen code太草率了**
- Suggested English title: "Alibaba's Qwen Code: A Hasty Fork"
- Category: china-ai
- Word count: ~800 Chinese characters (short)
- Date: 2025-08-09
- Key themes: Alibaba forking Google's Gemini CLI, product management failures, brand damage, open-source strategy
- Images: 2 (GitHub issue screenshot showing Chinese users mocking qwen-code stagnation; Twitter/X thread showing user @mkw3dd calling out leftover Gemini references)
- Overlap with published posts: None direct. Tangentially related to pseudo-problems post (criticising tooling choices)
- International relevance: **3/5** — Interesting for those following Chinese AI ecosystem, but narrow scope. The "fork vs. build" debate has universal appeal.

**Article C2: Solo不是个严肃的AI Coding工具**
- Suggested English title: "Solo Is Not a Serious AI Coding Tool"
- Category: china-ai
- Word count: ~1,200 Chinese characters
- Date: 2025-07-21
- Key themes: ByteDance Solo launch critique, requirement analysis failures, superficial human review, absent quality control, no backend demo
- Images: 1 (screenshot of article)
- Overlap with published posts: **HIGH overlap with `pseudo-problems-core-problems-ai-coding.md`** — the published post already references Solo's "one-command website" failure and cites "Da Ming's article." Also overlaps with the iterative methodology article (QC-1/Ops-1).
- International relevance: **2/5** — ByteDance Solo is primarily a Chinese product. The arguments are already covered in published posts.

### Category: USA AI (1 article)

**Article U1: Forward Deployed Engineer — 硅谷版"交付工程师"**
- Suggested English title: "Forward Deployed Engineer: Silicon Valley's Delivery Engineer Dressed in New Clothes"
- Category: usa-ai
- Word count: ~4,500 Chinese characters (very long)
- Date: 2025-12-15
- Key themes: Palantir FDE model critique, comparison to China's "中台" hype cycle, revolving door corruption in US defence, NHS contract failure, product vs. consulting company debate, Spreadsheet Test
- Images: 0
- Overlap with published posts: None. Completely new territory — not about AI coding methodology.
- International relevance: **5/5** — Directly about Silicon Valley companies (Palantir, OpenAI, Anthropic). The China-US cross-cultural comparison angle is unique and compelling. Very strong piece.

### Category: AI Software Engineering (4 articles + 1 duplicate)

**Article SE1: IDE和人类程序员一起被淘汰**
- Suggested English title: "IDEs Will Be Obsolete — Along with Human Programmers"
- Category: ai-software-engineering
- Word count: ~600 Chinese characters (very short)
- Date: 2025-07-15
- Key themes: AI doesn't need IDEs, humans don't need to be in the loop, "unmanned software factory" vision
- Images: 0
- Overlap with published posts: Tangential overlap with the "treat AI like humans" thesis. The "unmanned software factory" claim is bold but under-argued.
- International relevance: **3/5** — Provocative thesis but too short to stand alone. Better as a section within a longer piece.

**Article SE2: AI Coding领域的真问题**
- Suggested English title: "The Real Problems of AI Coding"
- Category: ai-software-engineering
- Word count: ~1,500 Chinese characters
- Date: 2025-12-14
- Key themes: Three core problems (getting what you want, quality assurance, building hybrid teams), Xiaolongbao Theory, critique of adoption metrics
- Images: 0
- Overlap with published posts: **ALREADY PUBLISHED as `real-problems-ai-coding-lesswrong.md`**. The existing English post is a faithful translation of this article.
- International relevance: N/A — already published.

**Article SE3: 学习PingCAP，打造你公司的AI原生软件开发团队**
- Suggested English title: "Building Your AI-Native Dev Team: Lessons from PingCAP"
- Category: ai-software-engineering
- Word count: ~3,500 Chinese characters (long)
- Date: 2026-01-26
- Key themes: PingCAP CTO's "alpha wolf" model critique, Product Tri-Ownership (PTO) framework (Product Owner / Quality Owner / Tech Owner), civil engineering analogy, "one story per day" velocity, Agent管理学 forum mention
- Images: 0
- Overlap with published posts: Builds on concepts from `real-problems-ai-coding-lesswrong.md` (Xiaolongbao Theory, hybrid teams) and `testing-ai-codings-last-unsolved-problem.md` (quality control debate). This is the **evolution** of those ideas into a concrete framework.
- International relevance: **5/5** — Universal appeal. PingCAP is internationally known. The PTO framework is original and actionable. References NASA IV&V. Strong piece.

**Article SE4: 敏捷方法不适合AI Coding之一：信息不应该透明**
- Suggested English title: "Agile Doesn't Work for AI Coding, Part 1: Information Should Not Be Transparent"
- Category: ai-software-engineering
- Word count: ~1,200 Chinese characters
- Date: 2026-02-05
- Key themes: Why Scrum's transparency principle fails for AI agents, AI's poor decision-making with excess information, context overload, controlled inputs for quality
- Images: 1 (photo of a physical Kanban board — generic stock-style image, not Chinese-specific)
- Overlap with published posts: Extends the "treat AI like humans" thesis from `treat-ai-like-humans-not-software.md` into concrete methodology. Also connects to quality control themes.
- International relevance: **4/5** — Contrarian take on Agile that will resonate with any team using AI coding tools. The Trump/last-person-to-talk analogy is vivid.

**Article SE5: Solo不是个严肃的AI Coding工具 (duplicate)**
- This is an exact duplicate of Article C2 above, captured via a different URL path. Same content, same date.
- **Flag: DUPLICATE — skip entirely.**

### Category: Quality Control (6 articles)

**Article QC1: 运用迭代方法论让AI交付工业质量的软件**
- Suggested English title: "Using Iterative Methodology to Deliver Industrial-Quality AI Software"
- Category: quality-control
- Word count: ~1,200 Chinese characters
- Date: 2025-07-26
- Key themes: Iteration as methodology (requirements iteration, test case iteration, AI-AI iteration), Requirements Analyst role, Synthetic Engineering Team
- Images: 0
- Overlap with published posts: Referenced in `pseudo-problems-core-problems-ai-coding.md` ("I discuss the reasons for failures and solutions in another article"). **Not yet published in English but already teased.**
- International relevance: **4/5** — Practical and actionable. The three types of iteration (AI-human, AI-PM, AI-AI) is a clean framework.

**Article QC2: 测试：AI Coding的终极质量控制手段**
- Suggested English title: "Testing: The Ultimate Quality Control for AI Coding"
- Category: quality-control
- Word count: ~3,000 Chinese characters (long)
- Date: not available (likely late Jan/early Feb 2026)
- Key themes: Five unsolvable testing problems, test review speed, external dependencies, agent output quantification, org vs. architecture for QC, reward hacking
- Images: 1 (Agent管理学论坛 Episode 12 poster — Chinese text, shows speakers 晓灰 and Ryan)
- Overlap with published posts: **ALREADY PUBLISHED as `testing-ai-codings-last-unsolved-problem.md`**. The existing English post covers the same five problems with nearly identical structure.
- International relevance: N/A — already published.

**Article QC3: 向土木学工程：AI带软件走出作坊**
- Suggested English title: "Learning from Civil Engineering: AI Takes Software Out of the Workshop"
- Category: quality-control
- Word count: ~800 Chinese characters (short — this is a forum preview/announcement)
- Date: not available (likely early Feb 2026)
- Key themes: Six questions comparing civil engineering to software engineering (blueprints, change management, acceptance, subcontractors, hidden work, AI automation), Agent管理学 forum Episode 13 preview
- Images: 1 (Agent管理学论坛 Episode 13 poster — Chinese text, shows 锅总 and 马工)
- Overlap with published posts: The themes are developed further in QC4 (Code Supervisor). This is essentially a teaser.
- International relevance: **2/5** — Too short and announcement-like to stand alone. Content is better served by QC4.

**Article QC4: 软件工程缺失的角色：为什么我们需要"代码监理"**
- Suggested English title: "The Missing Role in Software Engineering: Why We Need a Code Supervisor"
- Category: quality-control
- Word count: ~1,800 Chinese characters
- Date: not available (likely Feb 2026)
- Key themes: Civil engineering's independent supervisor (监理) role, Lovable security vulnerabilities, principal-agent problem, Didi K8s outage, AI making the supervisor role cost-effective, what a "code supervisor" should look like
- Images: 1 (same Agent管理学 Episode 13 poster as QC3)
- Overlap with published posts: Extends `testing-ai-codings-last-unsolved-problem.md` Problem 4 (org vs. architecture). Introduces the civil engineering analogy that also appears in SE3 (PingCAP/PTO article).
- International relevance: **4/5** — The Lovable vulnerability example is internationally known. The civil engineering parallel is fresh. Strong standalone potential.

**Article QC5: 不谈质量控制的AI Coder都是菜鸟**
- Suggested English title: "Any AI Coder Who Ignores Quality Control Is a Rookie"
- Category: quality-control
- Word count: ~500 Chinese characters (very short)
- Date: not available
- Key themes: Quality control as the only meaningful benchmark, critique of speed/cost bragging, burnt food analogy
- Images: 1 (photo of badly burnt food in a wok — humorous, universally understood)
- Overlap with published posts: Thematically overlaps with all quality-control articles. Works as an editorial/opinion fragment.
- International relevance: **3/5** — Fun and punchy but too short alone. Better as an intro/framing section within a larger quality piece.

**Article QC6: 如何确保AI软件工程质量？**
- Suggested English title: "How to Ensure AI Software Engineering Quality"
- Category: quality-control
- Word count: ~2,500 Chinese characters (long)
- Date: February 2026 (author: 莫道远)
- Key themes: Statistical Process Control (SPC) applied to AI coding, Shewhart's 1924 control chart, deterministic vs. probabilistic constraints, independence of constraints (effective constraint = constraint power x independence), AI autonomy formula
- Images: 1 (Shewhart's original 1924 control chart — historical English-language document)
- Overlap with published posts: This is the **theoretical synthesis** of everything in the QC series. References the testing forum (QC2), civil engineering insights (QC3/QC4), and practitioner experiences. Does not directly duplicate any published post.
- International relevance: **5/5** — The SPC framework is universally understood. The formula "effective constraint = constraint power x independence" is original and memorable. The Japan/SPC historical parallel is compelling. Strongest piece in the QC series.

### Category: AI for Operations (1 article)

**Article Ops1: 运用迭代方法论让AI交付工业质量的软件**
- **FLAG: This is the SAME article as QC1.** The original extraction URL redirected to the same underlying WeChat article (resolved URL: `https://mp.weixin.qq.com/s/yOK7U__KNVYDwHMCMbNWVA`). Content is identical.
- **DUPLICATE — skip entirely.**

---

## 2. Duplicate/Overlap Analysis

### Exact Duplicates
| Article | Duplicate of | Reason |
|---------|-------------|--------|
| SE5 (Solo, ai-software-engineering) | C2 (Solo, china-ai) | Same article captured from different URL paths |
| Ops1 (iterative methodology) | QC1 (iterative methodology) | URL redirect — same underlying WeChat article |

### Already Published on magong.se
| Extracted Article | Published Post | Notes |
|-------------------|---------------|-------|
| SE2 (AI Coding领域的真问题) | `real-problems-ai-coding-lesswrong.md` | Faithful translation already exists |
| QC2 (测试：AI Coding的终极质量控制手段) | `testing-ai-codings-last-unsolved-problem.md` | Faithful translation already exists |

### Significant Thematic Overlap Between Extracted Articles
| Articles | Overlap Description |
|----------|-------------------|
| C2 (Solo critique) + QC1 (iterative methodology) | QC1 directly references Solo's "一句话做电商" as a bad example. The Solo critique is subsumed by QC1's broader argument. |
| QC3 (civil engineering preview) + QC4 (code supervisor) | QC3 is a preview/announcement for the forum that produced QC4. QC4 subsumes QC3 entirely. |
| QC5 (rookie editorial) + QC6 (SPC synthesis) | QC5's "quality is the only benchmark" argument is the thesis statement of QC6. QC5 works as an intro to QC6. |
| SE3 (PingCAP/PTO) + QC4 (code supervisor) | Both use civil engineering analogies. SE3's Quality Owner role is the same concept as QC4's "code supervisor." Should cross-reference. |
| SE4 (Agile transparency) + SE3 (PingCAP/PTO) | SE4's "control AI inputs" argument is the operational detail behind SE3's Tech Owner role. |

### Overlap with Already Published Posts
| Extracted Article | Published Post | Nature of Overlap |
|-------------------|---------------|-------------------|
| C2 (Solo critique) | `pseudo-problems-core-problems-ai-coding.md` | Published post already names Solo and its failures |
| QC1 (iterative methodology) | `pseudo-problems-core-problems-ai-coding.md` | Published post teases QC1 ("see my other article") |
| SE3 (PingCAP/PTO) | `real-problems-ai-coding-lesswrong.md` | SE3 is the direct evolution of SE2's "hybrid team" question |
| SE3 (PingCAP/PTO) | `testing-ai-codings-last-unsolved-problem.md` | SE3's PTO framework answers Problem 4 from this post |
| SE4 (Agile transparency) | `treat-ai-like-humans-not-software.md` | SE4 extends the "manage AI like humans" thesis |
| QC4 (code supervisor) | `testing-ai-codings-last-unsolved-problem.md` | QC4 develops Problem 4 (org vs. architecture) |

---

## 3. Content Adaptation Strategy

### SKIP (do not translate)

**C2 — Solo critique**: Already covered in published `pseudo-problems` post. Solo is China-specific. The useful arguments (requirements matter, QC matters) are better served by QC1.

**SE2 — AI Coding真问题**: Already published as `real-problems-ai-coding-lesswrong.md`.

**QC2 — Testing ultimate QC**: Already published as `testing-ai-codings-last-unsolved-problem.md`.

**QC3 — Civil engineering preview**: Announcement-only. Content fully subsumed by QC4.

**SE5 — Solo duplicate**: Exact duplicate of C2.

**Ops1 — Iterative methodology duplicate**: Exact duplicate of QC1.

### TRANSLATE — Priority Articles

**U1 — Forward Deployed Engineer** (Priority: 1)
- What to keep: The entire thesis — FDE as rebranded delivery engineer, Palantir data analysis, NHS case study, China "中台" parallel, Spreadsheet Test, product vs. consulting distinction
- What to cut: Some repetitive "friend said" quotes (there are 5+ instances); the revolving door / corruption section can be condensed significantly (currently ~800 chars on Pentagon corruption alone); the final "中科红旗" comparison is a Chinese reference that needs cultural adaptation
- Cultural adaptation: Explain "中台" (zhongtai/middle platform) briefly for international readers; replace "中科红旗" comparison with a more universally known example of patriotic vaporware; the China military "backward deployed manager" joke can stay — it's funny and self-aware
- Estimated final English length: 2,500-3,000 words (cut from ~4,500 chars)
- Merge potential: Standalone. Too distinctive to merge.

**SE3 — PingCAP / Product Tri-Ownership** (Priority: 2)
- What to keep: PingCAP CTO's alpha wolf model, the PTO framework (PO/QO/TO), civil engineering analogy, "one story per day" rhythm, supporting roles, NASA IV&V reference
- What to cut: The "培训模式" (training mode) alternative section is weak and can go; the Claude Code release cadence comparison ("10 versions in 10 days") is filler; the detailed daily schedule can be condensed
- Cultural adaptation: PingCAP is known internationally — no adaptation needed. The 七牛云 (Qiniu Cloud) CEO quote needs context or can be cut. Agent管理学 forum should be branded consistently (see Section 5).
- Estimated final English length: 2,000-2,500 words
- Merge potential: Could absorb key points from QC4 (code supervisor = Quality Owner)

**QC6 — Ensuring AI SE Quality (SPC synthesis)** (Priority: 3)
- What to keep: The Shewhart/SPC framework, the formula "effective constraint = constraint power x independence", the four sections (probability is essence, deterministic constraints, independence, context-dependent autonomy), the Japan/SPC historical coda
- What to cut: Introductory description of Agent管理学 forum (move to a standard footer); some of the practitioner anecdotes can be condensed (胥克谦's 25,000 lines of rules is important; some others are redundant)
- Cultural adaptation: SPC and Shewhart are Western concepts — minimal adaptation needed. The practitioners' names can be kept (they add authenticity).
- Estimated final English length: 2,000-2,500 words
- Merge potential: Could absorb QC5's "rookie" framing as an opening section

**QC1 — Iterative Methodology** (Priority: 4)
- What to keep: The three types of iteration (AI-PM, AI-human, AI-AI), Requirements Analyst role, the "AI is not Aladdin's lamp" conclusion
- What to cut: The Solo reference (already in published posts); some repetition of iteration concept
- Cultural adaptation: Minimal — concepts are universal
- Estimated final English length: 1,000-1,200 words
- Merge potential: Could be merged into SE3 as a "how the Tech Owner works" section, OR kept standalone as the "methodology" piece that `pseudo-problems` already teases

**QC4 — Code Supervisor** (Priority: 5)
- What to keep: The civil engineering supervisor parallel, Lovable vulnerability example, principal-agent problem framing, Didi outage, what a code supervisor should look like
- What to cut: The QC3-style forum preview content; some repetition of civil engineering basics
- Cultural adaptation: Lovable is European/international — no adaptation needed. Didi is known to tech audiences.
- Estimated final English length: 1,200-1,500 words
- Merge potential: Strong candidate for merging into SE3 (the Quality Owner section could reference the supervisor concept)

**SE4 — Agile Transparency** (Priority: 6)
- What to keep: The four arguments (poor decision-making, manipulation susceptibility, context overload, random info hurts QC), the Trump analogy, the Coder subagent input/output example
- What to cut: The end-of-article "contact me" pitch; the brief mention of 黄东旭's "burn tokens" approach can be shortened
- Cultural adaptation: Scrum/Agile references are universal. The Trump analogy works internationally.
- Estimated final English length: 1,000-1,200 words
- Merge potential: Could be a standalone "Part 1" of a series, or merged into a larger "AI team methodology" piece

### MAYBE TRANSLATE

**C1 — Qwen Code fork**: The "fork vs. build" argument is interesting but niche. Could work as a short blog post if there's appetite for China AI ecosystem coverage. Low priority.

**SE1 — IDEs obsolete**: Too short and under-argued to stand alone. The thesis is bold but needs more evidence. Could be a social media excerpt or a section within another piece. Not recommended as a standalone post.

**QC5 — Rookie editorial**: Too short alone. Best used as the opening paragraphs of QC6 or as a social media excerpt.

---

## 4. Recommended Publication Plan

### Phase 1: Standalone Blockbusters

**Post 1: "Forward Deployed Engineer: Silicon Valley Reinvents the Delivery Engineer"**
- Source: U1
- Why first: Completely different topic from existing posts. Expands magong.se beyond AI coding into tech industry analysis. High viral potential due to Palantir/OpenAI angle.
- Estimated length: 2,500-3,000 words

**Post 2: "Building Your AI-Native Dev Team: The Product Tri-Ownership Framework"**
- Source: SE3 + elements of QC4 (code supervisor as Quality Owner)
- Why second: This is the flagship methodology piece. It builds on already-published posts (which readers can reference) and introduces the PTO framework as the answer.
- Estimated length: 2,500-3,000 words

### Phase 2: Quality Control Series

**Post 3: "How to Ensure AI Code Quality: Lessons from 100 Years of Statistical Process Control"**
- Source: QC6 + QC5 opening
- Why: The SPC framework is the theoretical backbone. Publishing this after the PTO post creates a natural "here's the framework, here's the theory behind it" sequence.
- Estimated length: 2,000-2,500 words

**Post 4: "The Missing Role: Why Software Needs an Independent Code Supervisor"**
- Source: QC4 (expanded, standalone version)
- Why: Follows naturally from QC6's "independence" principle. The Lovable case study gives it news-hook appeal.
- Estimated length: 1,200-1,500 words
- Alternative: Skip if QC4 content is already merged into Post 2.

### Phase 3: Methodology Deep-Dives

**Post 5: "Using Iterative Methodology to Deliver Industrial-Quality AI Software"**
- Source: QC1
- Why: This is already teased in the published `pseudo-problems` post. Fulfils that promise.
- Estimated length: 1,000-1,200 words

**Post 6: "Agile Doesn't Work for AI Coding: Why Information Transparency Hurts"**
- Source: SE4
- Why: Contrarian take on a sacred cow (Agile). Strong standalone post.
- Estimated length: 1,000-1,200 words

### Articles to Skip
| Article | Reason |
|---------|--------|
| C2 (Solo critique) | Already covered in published posts; China-specific product |
| SE2 (Real problems) | Already published |
| QC2 (Testing ultimate QC) | Already published |
| QC3 (Civil engineering preview) | Announcement only; subsumed by QC4 |
| SE5 (Solo duplicate) | Exact duplicate |
| Ops1 (Iterative duplicate) | Exact duplicate |
| SE1 (IDEs obsolete) | Too short; could be a social media excerpt |
| QC5 (Rookie editorial) | Too short; absorbed into Post 3 |
| C1 (Qwen Code fork) | Niche; low priority. Optional short post later. |

### Series Groupings

The six recommended posts naturally form two tracks:

**Track A — Industry Analysis**: Post 1 (FDE)
- Standalone. Positions the author as a cross-cultural tech industry analyst.

**Track B — AI Engineering Methodology**: Posts 2, 3, 4, 5, 6
- A coherent series from framework (Post 2) to theory (Post 3) to specific roles (Post 4) to practices (Posts 5-6).
- Could be branded as "The AI Engineering Series" or connected to the Agent管理学 brand.

---

## 5. Agent管理学 Brand Strategy

### Current Mentions Across Articles

| Article | Mention | Context |
|---------|---------|---------|
| SE3 (PingCAP/PTO) | "笔者运营一个世界一流的AI Coding社区：Agent管理学论坛" | Direct self-promotion — claims "world-class" community |
| QC2 (Testing) | "这也是我们Agent管理学论坛第12期的主题" | Forum episode reference |
| QC3 (Civil engineering) | "本期Agent管理学论坛" | Forum episode reference |
| QC6 (SPC synthesis) | "Agent管理学社区是AI Coding先锋们密集交流的论坛" | Opening description |
| Published: testing post | "Our Agent Management Forum is a long-running seminar series" | Already translated as "Agent Management Forum" |
| Published: music post | "Agent Management Forum Episode 14" | Consistent with above |

### Recommended English Branding

**Primary brand name: "Agent Management Forum"**

This is already established in published posts. Keep it consistent. The full Chinese name "Agent管理学论坛" translates naturally.

**Positioning for international readers:**

Currently, the forum is described differently each time. Standardise to a single boilerplate:

> *The Agent Management Forum is a seminar series for AI coding practitioners. Topics have covered testing methodology, team structure, quality assurance, and cross-disciplinary engineering approaches. [Link to past episodes on magong.se]*

**Recommendations:**
1. Create a dedicated page or tag on magong.se for "Agent Management Forum" content. Posts 2, 3, 4, and 6 all originate from forum discussions.
2. In each translated post sourced from the forum, include a brief standardised attribution line (e.g., "This article originated from Episode 13 of the Agent Management Forum").
3. Avoid the "world-class" self-description in English (SE3). Let the content speak for itself. International readers are allergic to self-promotion.
4. Position the forum as a practitioner community rather than a thought-leadership brand. The strength is that participants are real engineers sharing production experience — not consultants selling frameworks.
5. Consider linking to the WeChat account from the magong.se forum page, with a note like "The forum operates in Chinese via WeChat. English summaries are published here."

---

## 6. Image Assessment

### All Images Across All Articles

| Article | Image | Description | Recommendation |
|---------|-------|-------------|----------------|
| C1 (Qwen Code) | images/1.jpg | GitHub issue screenshot — Chinese title "qwen-code 别停止更新啊" with Chinese comments | **Keep if article is translated** — shows real user frustration. Chinese text adds authenticity per instructions. |
| C1 (Qwen Code) | images/2.jpg | Twitter/X thread — English-language critique of Qwen Code by @mkw3dd showing leftover Gemini references | **Keep if article is translated** — English content, directly supports the argument |
| C1 (Qwen Code) | screenshot.png | WeChat article screenshot | **Remove** — extraction artefact, not for publication |
| C2 (Solo) | screenshot.png | WeChat article screenshot | **Remove** — extraction artefact |
| U1 (FDE) | screenshot.png | WeChat article screenshot | **Remove** — extraction artefact |
| SE1 (IDE obsolete) | screenshot.png | WeChat article screenshot | **Remove** — extraction artefact |
| SE2 (Real problems) | screenshot.png | WeChat article screenshot | **Remove** — already published |
| SE3 (PingCAP) | screenshot.png | WeChat article screenshot | **Remove** — extraction artefact |
| SE4 (Agile transparency) | images/1.jpg | Photo of a physical Kanban board with French/English sticky notes | **Keep** — excellent illustration of Agile transparency. No Chinese text. Universally understood. |
| SE4 (Agile transparency) | screenshot.png | WeChat article screenshot | **Remove** — extraction artefact |
| QC1 (Iterative) | screenshot.png | WeChat article screenshot | **Remove** — extraction artefact |
| QC2 (Testing) | images/1.jpg | Agent管理学论坛 Episode 12 poster — Chinese text, shows speakers 晓灰 and Ryan | **Keep** — branded forum poster. Chinese characters are fine per instructions. Adds authenticity and promotes the Agent Management Forum brand. |
| QC3 (Civil eng.) | images/1.jpg | Agent管理学论坛 Episode 13 poster — Chinese text, shows 锅总 and 马工 | **Keep** — same reasoning as QC2 poster. Shows the author (马工) himself. |
| QC4 (Code supervisor) | images/1.jpg | Same image as QC3 — Agent管理学 Episode 13 poster | **Keep one copy** — deduplicate with QC3 |
| QC5 (Rookie) | images/1.jpg | Photo of badly burnt food (ribs) in a wok | **Keep** — universally funny. No text. Perfect metaphor for "fast but terrible quality." |
| QC6 (SPC synthesis) | images/1.png | Shewhart's original 1924 control chart — historical English document | **Keep** — English text, historically significant, directly supports the SPC argument. Excellent image. |

### Summary

- **Keep**: 7 images (2 from C1 if translated, 1 Kanban board, 2 forum posters deduplicated to 1, 1 burnt food, 1 Shewhart chart)
- **Remove**: 8 images (all screenshot.png extraction artefacts)
- **Chinese-character images that are fine to keep**: QC2 and QC3/QC4 forum posters. These are branded community assets and Chinese text adds authenticity.

---

## Summary

Of 14 extracted articles (minus 2 exact duplicates and 2 already published), **6 articles are recommended for translation** into 6 English posts, grouped into two tracks. The Forward Deployed Engineer piece is the highest-priority standalone, and the PingCAP/PTO framework piece is the flagship methodology article. The quality control series (Posts 3-4) and methodology deep-dives (Posts 5-6) provide depth. The Agent Management Forum brand should be consistently positioned as a practitioner community across all translated posts.
