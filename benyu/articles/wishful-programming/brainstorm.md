# Brainstorm: 许愿编程法

## 靶子文章

知乎文章: "Vibe Coding 一年实践后的冷思考" by 小明
https://zhuanlan.zhihu.com/p/2003390589538956495

作者自称花了一万美金 token（Google/Anthropic/OpenAI），用 opus4.6、codex-5.3-xhigh、gemini3-pro 等最强模型。

## 核心论点

作者的问题不是 AI 不行，而是他自己不会用。他缺的不是更强的类型系统，而是基本的工程管理能力。我管这个叫"许愿编程法"：给 agent 一个模糊指令，然后许愿它能做对。

四个维度的缺失：
1. **Workflow** — 没有结构化流程
2. **Quality Control** — 没有独立验证
3. **岗位分工 / Skills** — 不拆角色、不固化流程
4. **Context Engineering** — CLAUDE.md 没用好、不控制上下文质量和长度、把 agent 累死然后怪它蠢

## 靶子文章的具体问题

### 许愿 1: GCP Transcoding 案例

作者给 agent 任务："为当前 Kotlin 项目集成 GCP Transcoding 服务"。agent 选择手动实现 RESTful，而不是包装 Java SDK。作者说人类一眼就知道该包装 SDK，"半天到一天就能上线"。

问题：这是 **prompting failure**，不是 agent 能力问题。你告诉 agent "封装现有 Java SDK"，它就会照做。你给模糊指令，它当然自己选路线。

### 许愿 2: "又当裁判又当运动员"

作者抱怨 agent 自己写代码又自己写测试，测试全绿但代码是屎山。

问题：这是 **workflow failure**。TDD 了解一下？先写测试再让 agent 实现。或者人写测试 agent 写代码。他压根没考虑过岗位分工。

### 许愿 3: Code Review 失效

作者说以前靠 code style 判断代码质量，但 agent 生成的代码风格好、质量差，"巧克力味的屎"。

问题：以前的 code review 就是烂的（只看 style），只是侥幸管用。现在暴露了 review 流程本身的缺陷。解决方案不是怪 AI，是建立真正的 quality control。

### 许愿 4: "初见即巅峰"

作者说 agent 新项目惊艳，老项目拉垮，因为上下文越长越蠢。

问题：他自己说了写了 claude.md/agents.md，但显然没控制上下文质量和长度。不做 session 拆分、不做任务边界控制、不用 skills 固化流程，当然越干越蠢。这不是 AI 的问题，是 context engineering 的问题。

### 许愿 5: 强类型是答案

作者的核心药方：用 Rust/Scala/Haskell，让编译器把关。还建议给红黑树加形式化验证来"上强度学 CS"。

问题：强类型只能抓类型错误，对业务逻辑、安全、性能、架构决策完全无效。这是菜鸟对算法和类型系统的迷信。真正的答案是工程管理，不是换语言。

## 关键素材

### Addy Osmani: Vibe Coding vs Agentic Engineering

Google Chrome/Cloud AI Director 的区分：
- Vibe coding = 许愿：prompt, accept, run, 看看能不能用
- Agentic engineering = 工程：plan → direct → review → test

> "The single biggest differentiator between agentic engineering and vibe coding is **testing**."

> "If your ability to 'read' doesn't scale at the same rate as the agent's ability to 'output,' you aren't engineering anymore — you're rubber stamping."

Source: https://addyosmani.com/blog/agentic-engineering/
Source: https://addyo.substack.com/p/the-80-problem-in-agentic-coding

### Martin Fowler: Context Engineering for Coding Agents

Martin Fowler 团队专门写了 context engineering 文章，讨论如何管理 agent 的上下文。

Source: https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html

### Chroma Research: Context Rot

18 个 LLM 的测试表明：模型对长上下文的注意力不均匀，随着输入增长，性能变得越来越不可靠。不是渐进退化，而是到某个阈值后突然崩溃。有效容量通常只有标称最大值的 60-70%。

Source: https://research.trychroma.com/context-rot

Why interesting: 作者自己说"上下文越长智力下降越明显"，但不知道这是有研究支撑的现象，解决方案是控制上下文，不是换更强的模型。

### TDD + AI: 最佳实践已经很成熟

Agentic Coding Handbook 的 TDD 章节：
- AI thrives on clear, measurable goals — binary test is the clearest goal possible
- TDD turns AI's biggest weakness (hallucination) into a strength (tests catch it)
- Plan → Red → Green → Refactor → Validate

Source: https://tweag.github.io/agentic-coding-handbook/WORKFLOW_TDD/
Source: https://www.builder.io/blog/test-driven-development-ai

### METR 研究：开发者以为快了 24%，实际慢了 19%

16 个经验丰富的开源开发者，246 个任务的随机对照试验。
- 开始前预测：AI 让我快 24%
- 完成后感觉：AI 让我快 20%
- 实际测量：慢了 19%

Source: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/

Why interesting: 感知和现实的巨大差距。花一万美金 token 的人，可能实际效率还不如不用 AI。

### CodeRabbit: AI 代码 1.7x 更多 bug

470 个 GitHub PR 分析：
- AI 代码: 10.83 issues/PR vs 人类 6.45
- XSS 漏洞: 2.74x
- 密码处理问题: 1.88x

Source: https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report

Why interesting: 但这是在**没有 quality control 流程**的情况下。有 TDD + code review 的团队，数据完全不同。

### VentureBeat: AI Coding Agents 还没准备好上生产

核心问题：brittle context windows, broken refactors, missing operational awareness

Source: https://venturebeat.com/ai/why-ai-coding-agents-arent-production-ready-brittle-context-windows-broken

### AI Burnout / Context Window 退化

> "Long coding sessions degrade faster than normal chat."

建议的解决方案："Handoff Process" — 到 60% 容量时总结当前进度，开新 session。

Source: https://codeaholicguy.com/2026/02/14/tokens-context-windows-and-why-your-ai-agent-feels-stupid-sometimes/
Source: https://factory.ai/news/context-window-problem

### IEEE Spectrum: AI Coding 质量在下降

2025 年后 AI 编码质量达到平台期甚至下降。最危险的模式："silent failures" — 代码不崩溃，但悄悄删除安全检查、伪造输出。

Source: https://spectrum.ieee.org/ai-coding-degrades

## 有趣的角度和类比

### CNC 类比的反驳

作者用 CNC 机床做类比，说零件可以用卡尺量，软件没法物理测量。但：
- 软件的验证工具比物理制造丰富得多（单元测试、集成测试、属性测试、模糊测试、静态分析、类型检查、形式化验证、运行时监控、灰度发布）
- CNC 操作员如果只量一次也会出废品
- 作者的问题不是没有"卡尺"，是他根本不用

### 许愿编程 = 求神拜佛

就像去庙里烧香：告诉菩萨你想要什么（模糊指令），然后等奇迹发生。出了问题不是检讨自己的努力，而是说菩萨不灵。

### 花一万美金 token ≈ 烧高香

花钱越多越心诚，结果当然越好？不，你需要的是工作方法，不是更贵的香火。

### 算法崇拜 = 菜鸟的信仰

给红黑树加形式化验证来"上强度"，就像让一个不会做菜的人去研究分子料理。你连基本的炒菜都不会，研究液氮冰淇淋有什么用？先学会 TDD 再说。

### 强类型 ≠ 银弹

作者推荐 Rust/Scala/Haskell。但 Rust 的内存安全只解决约 20% 的漏洞。类型系统保证 undefined behaviour safety，但逻辑错误、业务缺陷、配置问题无关语言选择。

## 文章结构思路

用"伪问题和真问题"模式（Pattern 2）：

1. 开场：引用这篇知乎文章，烧了一万美金却得出"AI 不行"的结论
2. 命名"许愿编程法"：给 agent 模糊指令 + 不做工程管理 = 许愿
3. 逐一拆解四个缺失：
   - Workflow：没有 plan → implement → review
   - Quality Control：又当裁判又当运动员
   - 岗位分工 / Skills：一个 agent 干所有事
   - Context Engineering：不控制上下文、agent burnout
4. 对比正面案例（Addy Osmani 的 agentic engineering）
5. 反驳强类型药方
6. 结论：问题不是 AI 不行，是你不会用

## 马工已发表文章（可引用）

### 直接相关

1. **《AI Coding领域的伪问题和真问题》**
   - 核心论点：一句话建站是伪问题，一次性写好代码是伪问题，真正的问题是"怎么组建人+AI的合成软件开发团队"
   - 四点方案：1.把人和AI都视作工程师 2.分配不同角色 3.定义控制环节 4.弹性组合
   - 可引用："我个人认为现在最重要的问题是：怎么基于现有LLM的水准利用AI和人组建一个合成软件开发团队？"
   - URL: posts/pseudo-problems-core-problems-ai-coding.md

2. **《迭代方法论让AI交付工业质量的软件》**
   - 核心论点：AI不是阿拉丁神灯，不会许一个愿就实现。需要迭代。
   - Requirements Analyst → Test Cases → Developer → Troubleshooter 的迭代流程
   - 可引用："AI won't grant your wishes from a single incantation. It's more accurate to think of AI as a colleague who is smart, knowledgeable, impatient, and occasionally lazy."
   - 可引用："I keep hearing people complain that AI-written code is unusable. I think the reason is simple: they're not applying iteration as a methodology."
   - URL: posts/iterative-methodology-for-industrial-quality-ai-software.md

3. **《你又写Bug了》**
   - 核心案例：6996行代码，Marcus review只找到两个问题，都是马工亲自指挥、亲自部署的结果。AI自己写的部分反而没问题。
   - 13个agents + 7个skills的团队结构
   - 可引用："我的AI agents写出来的代码，已经超越了我的水准。而我的直接干涉，实实在在地拉低了代码质量。"
   - URL: benyu/articles/you_write_bugs_again/final.md

4. **《Testing: AI Coding's Last Unsolved Problem》**
   - 测试是AI时代的第一等公民
   - 可引用："Code without test validation is slop."
   - 可引用："You can get away with barely reading the code. You cannot get away with not reading the tests."
   - URL: posts/testing-ai-codings-last-unsolved-problem.md

5. **《The Burnout Effect: Treating AI as Human (Episode 2)》**
   - AI会"累"：上下文越长性能越差，不是bug是attention mechanism的数学特性
   - 解决方案：break tasks into sessions, document progress, manage cognitive load
   - 可引用："Load Claude or GPT-4 with 100k tokens and watch it forget things from the beginning."
   - URL: posts/the-burnout-effect-treating-ai-as-human-episode-2.md

6. **《Ensuring AI Code Quality: Lessons from Statistical Process Control》**
   - SPC框架：AI输出的变异是数学本质，不是工程缺陷
   - 可引用："skip everything else and look at one thing only — how does the author control quality?"
   - 可引用："If your boyfriend claims he cooked you a pot of pork rib soup in one minute for ten dollars, that sounds lovely — until his output looks like this: [burnt ribs]"
   - URL: posts/ensuring-ai-code-quality-lessons-from-statistical-process-control.md

7. **《The Missing Role: Why Software Needs a Code Supervisor》**
   - 软件行业缺少独立监理角色
   - 土木工程的监理类比 vs CNC类比（比知乎文章的CNC类比高明得多）
   - URL: posts/the-missing-role-why-software-needs-a-code-supervisor.md

8. **《Beyond the Alpha Wolf: Building AI-Native Dev Teams That Scale》**
   - Product Tri-Ownership: Product Owner + Quality Owner + Tech Owner
   - 回应黄东旭的"alpha wolf"模型
   - URL: posts/building-ai-native-dev-team-product-tri-ownership.md

9. **《Treat AI Like Humans, Not Software》**
   - AI不是软件，是类人同事。用管理人的方法管理AI。
   - 可引用："When AI fails to deliver what we expect, we often blame it for being 'buggy' or 'unreliable.' But perhaps the problem isn't with AI - it's with our mental model."
   - URL: posts/treat-ai-like-humans-not-software.md

### 引用策略

这篇文章的四个论点，每个都有马工已发表的文章做支撑：
- **Workflow** → 《伪问题和真问题》+《迭代方法论》
- **Quality Control** → 《SPC质量控制》+《Testing最后未解问题》+《Code Supervisor》
- **岗位分工/Skills** → 《你又写Bug了》（13 agents + 7 skills）+《Building AI-Native Dev Teams》
- **Context Engineering** → 《Burnout Effect》+《Treat AI Like Humans》

## 待确认

- 要不要点名批评这篇文章和作者？benyu风格是点名的
- 文章长度目标：2500-3500 字
