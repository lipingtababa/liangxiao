# 许愿编程法：花一万美金烧高香，然后怪菩萨不灵

## 文章结构：驳斥（Debunking）

**靶子**：知乎文章 "Vibe Coding 一年实践后的冷思考" by 小明
**核心论点**：作者花了一万美金token得出"AI不行，要用强类型语言"的结论。问题不是AI不行，是他根本不会管理AI。我管这种做法叫"许愿编程法"：给agent一个模糊指令，不做工程管理，然后许愿它能做对。
**读者焦虑**：我也花了很多钱用AI coding，效果也不好，是不是AI真的不行？
**目标字数**：2500-3500字

---

## 一、开场：一万美金的许愿

- 知乎有篇文章，作者自称花了一万美金token，用了opus4.6、codex-5.3-xhigh、gemini3-pro等最强模型，结论是AI不行，要用Rust/Haskell
- 点名批评：这不是冷思考，这是花一万美金烧高香，然后怪菩萨不灵
- 提出核心概念"许愿编程法"：给agent模糊指令 + 不做工程管理 = 去庙里许愿
- METR研究数据：开发者以为快了24%，实际慢了19%。花一万美金token的人，可能实际效率还不如不用AI

## 二、什么是许愿编程？

- Addy Osmani（Google Chrome/Cloud AI Director）的区分：vibe coding vs agentic engineering
  - 许愿 = prompt, accept, run, 看看能不能用
  - 工程 = plan, direct, review, test
- 引用 Addy Osmani: "The single biggest differentiator between agentic engineering and vibe coding is **testing**."
- 作者的每一个失败案例，都是许愿而不是工程

## 三、逐一拆解四个许愿

### 许愿一：GCP Transcoding — 不说清楚就怪AI瞎猜

- 作者给agent："为当前Kotlin项目集成GCP Transcoding服务"，agent选择手动RESTful而不是包装SDK
- 你告诉agent"封装现有Java SDK"，它就会照做。模糊指令得到模糊结果，这是prompting failure
- 类比：你跟新来的985毕业生说"把这个功能做了"，他也会自己选路线。你得告诉他用什么方案

### 许愿二：又当裁判又当运动员 — 不拆角色就怪AI自嗨

- 作者抱怨agent自己写代码又自己写测试，测试全绿但代码是屎山
- TDD了解一下？先写测试再让agent实现。或者人写测试agent写代码
- 引用马工自己的实践：13个agents + 7个skills的团队结构，"我的AI agents写出来的代码，已经超越了我的水准"
- 引用 Addy Osmani: "If your ability to 'read' doesn't scale at the same rate as the agent's ability to 'output,' you aren't engineering anymore — you're rubber stamping."

### 许愿三：Code Review失效 — 以前就烂，现在暴露了

- 作者说AI代码"巧克力味的屎"：风格好、质量差
- 以前靠code style判断质量，这种review本来就是烂的，只是侥幸管用
- CodeRabbit数据：AI代码1.7x更多bug，XSS漏洞2.74x。但这是在没有quality control的情况下
- 解决方案不是怪AI，是建立真正的独立质量验证

### 许愿四：初见即巅峰 — 不控制上下文就怪AI变蠢

- 作者说新项目惊艳、老项目拉垮，上下文越长越蠢
- Chroma Research数据：模型到某个阈值后突然崩溃，有效容量只有标称最大值的60-70%
- 这不是AI的问题，是context engineering的问题。不做session拆分、不做任务边界控制，当然越干越蠢
- 引用马工文章《Burnout Effect》的观点

## 四、强类型不是答案

- 作者的核心药方：Rust/Scala/Haskell + 形式化验证
- 强类型只能抓类型错误，对业务逻辑、安全、性能、架构决策完全无效
- 类比：给红黑树加形式化验证来"上强度"，就像让一个不会做菜的人去研究分子料理。你连基本的TDD都不会，研究Haskell有什么用？
- CNC类比的反驳：作者说软件没法像零件用卡尺量。但软件的验证工具比物理制造丰富得多，作者的问题不是没有"卡尺"，是他根本不用

## 五、结论：问题不是AI不行，是你不会用

- 回扣"许愿编程法"：花钱越多越心诚，结果当然越好？不，你需要的是工作方法，不是更贵的香火
- Addy Osmani的总结、Martin Fowler团队的context engineering文章，都指向同一个方向：把AI当工程问题管理，而不是当许愿池
- 引用马工旧文：AI不是阿拉丁神灯，不会许一个愿就实现
- 结尾邀请讨论

---

## 标题备选

1. **许愿编程法：花一万美金烧高香，然后怪菩萨不灵** （主选）
2. **花一万美金Token的人，可能还不如不用AI**
3. **Vibe Coding一年，你练的是许愿术**

## 关键引用来源

- 知乎原文：https://zhuanlan.zhihu.com/p/2003390589538956495
- Addy Osmani: https://addyosmani.com/blog/agentic-engineering/
- METR研究：https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
- Chroma Research: https://research.trychroma.com/context-rot
- CodeRabbit: https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
- Martin Fowler: https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html
- Agentic Coding Handbook TDD: https://tweag.github.io/agentic-coding-handbook/WORKFLOW_TDD/
- 马工旧文：《伪问题和真问题》《迭代方法论》《你又写Bug了》《Testing最后未解问题》《Burnout Effect》《SPC质量控制》
