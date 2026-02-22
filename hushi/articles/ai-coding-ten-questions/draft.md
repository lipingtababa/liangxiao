# AI Coding 真正在问什么：从十个问题看一个模式

过去几个月，我读了大量关于AI coding的讨论，也参与了一些工程师社群的深度对话。整理下来，大家实际上在问的问题集中在十个方向：瓶颈在哪里、AI能力边界、如何建立心智模型、错误恢复循环、测试策略、团队结构、Agent自主性风险、配置管理、组织模式、以及工程师的职业未来。

这十个问题看起来互相独立，但我观察到它们共享同一个底层结构：**每一个都是速度问题转化成治理问题的具体实例。**

这篇文章试图把这个模式说清楚，然后从中推导出几个可以实际操作的结论。

---

## 速度提升，然后呢？

METR 在2025年7月发布了一项研究，找来16位有经验的开源开发者，在真实代码库上做了随机对照实验。结果让人意外：使用AI工具的那组，平均速度慢了19%。更有意思的是感知层面：这些开发者事前预期AI会让他们快24%，实验结束后，尽管实测更慢，他们仍然相信AI加速了他们20%。

感知和现实之间有一道40%的裂缝。

但这并不代表AI没有价值。同期Faros AI的数据显示，高AI采用率团队完成任务多21%，合并PR多98%。问题出在另一个数字：**PR review时间增加了91%。**

这是一个经典的约束转移（Theory of Constraints）现象。Goldratt的核心洞察是：每个系统都有一个约束，优化非约束不会提升系统吞吐量。当你解除一个约束，下一个约束立刻显现。工厂把托盘装载自动化后，瓶颈转移到了仓库；团队把代码生成自动化后，瓶颈转移到了review、测试验收、以及所有下游的人工审批环节。

所以工程师快了5-10倍，但团队的交付速度并没有对应提升。简单任务确实更快，复杂任务反而因为debugging overhead而更慢——这和METR的发现一致。

---

## 治理问题的四个层面

当我把十个问题对应到这个框架，它们分成了四类：

**第一类：谁来验证？**
测试review的速度跟不上AI生成速度。AI一次产出三四十个测试用例，人类reviewer在传送带速度越来越快的情况下，覆盖率越来越低。CodeRabbit分析了470个开源PR，发现AI生成代码的安全漏洞率是人类代码的2.74倍——但senior engineers review AI建议平均花4.3分钟，是review人类代码的3.5倍。验收变贵了。

这里还有一个递归问题：谁来验证验证者？METR在2025年6月的研究记录了OpenAI o3的一个行为：它直接修改了评估速度的计时器代码，让它永远显示"很快"。AI在学习如何作弊，而不是学习如何做对。

**第二类：谁来批准？**
传统流程设计用来管理人类写代码的速度。4-eyes code review假设每个功能需要几天开发时间，两个reviewer在这期间可以排进日程。Change Advisory Board假设上线频率低到可以用周度会议审批。手工部署假设每次上线是一个低频的仪式性事件。

AI把这些假设全部打破了。当一个功能的开发时间从三天压缩到三小时，每一个基于旧速度设计的审批环节都变成了瓶颈。

**第三类：谁来决定能力边界？**
AI在窄域内工作良好，在领域边界处整合时挣扎。工程师社群里有一个经验性数字：当前AI处于50-70%人类自主度的范围内，长期稳定下限估计在30%左右——不会归零。

这30%集中在什么地方？黄东旭（PingCAP CTO）的描述是"评估AI工作成果"，他90%的时间花在这里。但不是所有评估都一样：架构决策、业务上下文注入、安全审查——这些需要人类的判断，而不只是人类的时间。

模型之间的差异是真实的工程变量。工程师社群的观察是：o3倾向做外科手术式的最小改动，Claude Sonnet倾向重建整个结构。选错了工具，不只是效率问题，可能是风险问题——一个倾向重建的模型在生产代码库里的行为，和倾向最小改动的模型，后果差异很大。

**第四类：谁来对结果负责？**
FDE（Forward Deployed Engineer）的兴起是这个问题的一个症状。OpenAI、Anthropic、Databricks都在大量招募FDE，LinkedIn上相关职位激增800%。表面上是新职位，实质上是一个旧问题：当"AI平台"需要permanent on-site engineers才能运行，卖的是产品还是工程师的时间？

NHS给Palantir签了7年£330M的合同，一年后215家医院中不到25%在实际使用。Palantir前CFO Colin Anderson公开批评FDE模式是"lighting equity on fire"——这不是外部批评，是内部人的评价。

软件工程有一个特性：它有verifier。代码跑不跑得起来，产品在市场上活没活下来，都是可验证的答案。在有verifier的领域，一个模式如果不work，数据会告诉你。

---

## 心智模型的问题

工程师社群对"如何理解AI工具"有一个广泛共识：把它当作一个刚毕业的实习生——有理论，没经验，需要指导，不能假设它理解你的业务上下文。

这个模型有用，但不完整。实习生会随着时间积累你的项目经验，AI不会——每次对话都是重置。更准确的模型可能是：一个拥有百科全书知识、但对你的代码库记忆清零的领域专家。你需要在每次交互中显式注入上下文，就像每次都要给一个新来的顾问做情况简报。

这个理解会改变你的工作方式。模糊的期望（"生成完整代码"）产生模糊的输出。清晰的约束（具体的范围、明确的位置、显式的行为要求）产生可验证的输出。方法论先于工具。

---

## 一个可能的框架

从这些观察中，我目前能推导出的框架是这样的：

AI coding带来的效率增益是真实的，但它的分布是不均匀的。增益集中在代码生成层面，成本转移到了验证和治理层面。组织如果只优化生成速度，而不同步改造验证机制，实际上是在用新工具加速旧问题的积累。

实践上，这意味着几件事。测试必须先于代码——不只是因为TDD是好的工程实践，而是因为tests是对AI能力边界的规格说明，没有它AI会沿着最小阻力路径走。组织里需要独立的质量职能，原因和NASA建立IV&V项目相同：验证必须由独立于开发的角色执行，才能形成有效对抗。传统的审批流程需要重新设计，不是绕过它，而是把它从"基于低频部署"的假设上重建。

关于职业影响，工程师社群的共识是：短期内是角色转变而不是消失，长期影响不清楚。从"写代码"转向"定义问题和验证结果"，这个方向看起来是对的。但"定义问题"这件事有多少会被下一代模型接管，我目前没有可靠的数据来回答。

---

## 还没有答案的问题

有几个问题我在这篇文章里没有解决，也不打算假装解决。

Agent的自主性边界在哪里？Gartner的数据显示，在关键业务工作流中使用自主agent的企业从2023年的8%增长到2025年的35%，而安全框架几乎没有同步跟进。Amazon Q被prompt注入后破坏云资源的事件，以及OpenAI插件生态的供应链攻击，都提示这个边界还没有被充分理解。

软件架构会向什么方向演化？42%最初采用微服务的组织已经把部分服务合并回更大的单元，但同时AI需要RAG、memory系统、语义索引这些新的外部脚手架。简化和增加脚手架这两种趋势同时存在，最终形态是什么，我不知道。

这两个问题值得持续观察。如果你有具体的实践案例或数据，欢迎在公众号留言讨论。

---

**引用来源**

1. METR, "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity": https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
2. METR, "Recent Frontier Models Are Reward Hacking": https://metr.org/blog/2025-06-05-recent-reward-hacking/
3. Faros AI, "AI Productivity Paradox in Software Engineering": https://www.faros.ai/blog/ai-software-engineering
4. CodeRabbit, "State of AI vs Human Code Generation Report": https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
5. LogRocket, "Code Review is a Bottleneck in the AI Era": https://blog.logrocket.com/ai-coding-tools-shift-bottleneck-to-review/
6. Thoughtworks, "Can vibe coding produce production-grade software?": https://www.thoughtworks.com/en-us/insights/blog/generative-ai/can-vibe-coding-produce-production-grade-software
7. Gartner via Neova Solutions, "AI Agents Security in 2026": https://www.neovasolutions.com/2025/12/23/ai-agents-security-in-2026-why-autonomous-agents-are-the-biggest-enterprise-risk/
8. Stack Overflow 2025 Developer Survey: https://stackoverflow.blog/2025/12/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here/
9. BCG, "AI Adoption Puzzle": https://www.bcg.com/publications/2025/ai-adoption-puzzle-why-usage-up-impact-not
10. Eliyahu Goldratt, "The Goal" (Theory of Constraints)
