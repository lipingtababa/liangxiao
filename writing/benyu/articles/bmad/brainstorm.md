# Brainstorm: BMAD 实战与 AI Native 开发的未来

来源材料：Agent管理论坛第9期录音稿 - Nick讲BMAD实战 (2026-01-22)

---

## 核心发现：来自实战访谈的洞察

### 💡 为什么别人玩不转BMAD，Nick却能玩得转？

**答案：Scrum Master背景**

Nick在保利威担任Scrum Master，对整个敏捷流程非常熟悉。BMAD的每个环节（写用户故事、详细设计、开发、测试、上线）他都"一拿来用就比较顺手"。

> "我看到它是一个完整的Scrum流程，因为它里面的所有环节，包括写用户故事、从用户故事到写详细设计、再到开发、测试、上线，整个流程我都很熟悉。"

**有趣的矛盾**：BMAD里的"Scrum Master"角色其实定位错误——真正的Scrum Master是教练角色，不写用户故事；BMAD的SM更像架构设计师。

**潜在文章角度**：
- "为什么程序员学不会BMAD？因为你没学过敏捷"
- "BMAD的入门门槛不是AI，是软件工程基础"
- "敏捷死了吗？不，它变成了BMAD的入场券"

---

### 💡 "三人团队"的未来软件公司架构

Nick描述的理想团队配置：

1. **Product Owner** - 产品拍板人，决定做什么
2. **UX Designer** - 交互设计师，和v0/lovable合作出UI Kit
3. **技术拍板人** (Nick自己) - review详细设计，不写代码

> "如果你真的想要最大化效率，那就没必要分前后端了。也不是什么研发工程师，就是一个'技术拍板人'。"

**惊人数据**：Nick一个人可以同时应付2-3个项目，"还有时间上微信"。

**潜在文章角度**：
- "800人开发团队的末日：淘汰750人，剩50个技术拍板人"
- "未来的软件公司只需要三个人"
- "AI时代的'技术拍板人'：不写代码，只做决策"

来源: 访谈录音稿

---

### 💡 "棕地项目"的困境 vs "绿地项目"的机遇

访谈中多次出现的核心矛盾：

**棕地项目（Brownfield）困境**：
- 复杂的老项目需要补大量文档
- AI无法理解原有架构的"为什么"
- Claude经常困惑：听以前代码的，还是听新文档的？

**解决方案：把中地项目当绿地项目做**

> "我根本不想重构它的代码。我就从PRD开始，先整理一个PRD，然后把旧项目所需的功能都用自然语言表达出来，然后我把它当做一个'绿地'项目来做。原来的代码对我来说只是一个参考。"

**关键洞察**：代码变便宜了，重写比重构更划算

> "传统上为什么我们要做'棕地'项目？因为代码很宝贵。那现在代码很便宜，我重写代码很便宜，我不需要原来的代码，我需要的是原来的产品设计。"

来源: 访谈录音稿, MIT Sloan Management Review

---

### 💡 "不看代码，只看Code Review Report"的工作模式

Nick的惊人工作流：

1. 详细设计文档 → AI写代码
2. AI做对抗式Code Review
3. Nick只看Code Review的3-5个问题报告
4. 复杂的故事用GPT-5.2再review一遍

> "我现在对他有信心。我对它帮我code_review的能力有信心。因为只要我检查了那个详细设计是OK的，它那个code_review的流程就能帮我把实现中与详细设计不符的地方列出来。"

**关键**：信心来自详细设计的质量，不是代码本身

**潜在文章角度**：
- "告别Code Review：从看代码到看报告"
- "详细设计是新的代码"
- "技术Leader的新技能：review AI的review"

来源: 访谈录音稿

---

## 来自Web搜索的发现

### 💡 AI编程的"盲盒效应"与Context Collapse

**数据支撑**：
- 多轮对话中，LLM性能平均下降39%
- 错误率因"可靠性崩溃"飙升112%
- GPT-5等新模型发展出更隐蔽的失败模式——表面上运行正常但实际功能错误

来源: [IEEE Spectrum - AI Coding Degrades](https://spectrum.ieee.org/ai-coding-degrades), [LogRocket Blog - AI Context Problem](https://blog.logrocket.com/fixing-ai-context-problem/)

**Nick的解决方案**：每个Story都有独立的详细设计文档，Fresh Context

> "他现在的开发流程不是一次性将所有用户故事的详细设计全部写完再开发，而是写一个，开发完一个，再写下一个。"

**潜在文章角度**：
- "Context Collapse是AI编程的癌症"
- "为什么BMAD要把PRD拆成Story？"

---

### 💡 "产能过剩"的荒诞困境

访谈结尾的有趣对话：

> 马驰：所以现在你看到一个非常普遍的情况，就是我们有"屠龙刀"，但是没这么多项目可以做。我们甚至要去从别人手里去抢项目、偷项目来做。
>
> Nick：就是没那么多新项目。啃旧的骨头就是最难的，就要看要不要啃下去。
>
> 马驰：对，产能过剩。<笑声>向全世界去倾销。

**更深层的矛盾**：
- 核心项目靠稳定性赚钱，不需要快速迭代
- 有价值的新项目机会有限
- 技术能力过剩，但商业机会不足

来源: 访谈录音稿

---

### 💡 2025年Tech裁员的AI因素

**惊人数据**：
- 2025年全球科技行业裁员244,851人
- Microsoft报告40%裁员影响开发者
- Microsoft CEO透露30%代码现在由AI编写
- Salesforce CEO称AI完成30-50%工作量
- Accenture裁11,000人，不能"retrain"AI的员工被淘汰

来源: [TechCrunch - Tech Layoffs 2025](https://techcrunch.com/2025/12/22/tech-layoffs-2025-list/), [Network World - 244,000 Layoffs](https://www.networkworld.com/article/4114572/global-tech-sector-layoffs-surpass-244000-in-2025.html)

**潜在文章角度**：
- "不是AI替代程序员，是AI+少数程序员替代大多数程序员"
- "Scrum Master消亡史：从教练到AI的一部分"

---

### 💡 Solo Founder的崛起

**数据支撑**：
- Solo founder创业占比从2015年22.2%上升到2024年38%
- AI让一个人+ChatGPT+Cursor+Vercel = 以前的设计师+2个工程师+1个市场人员
- "一人十亿美元公司"不再是幻想

来源: [Solo Founders in 2025](https://solofounders.com/blog/solo-founders-in-2025-why-one-third-of-all-startups-are-flying-solo/)

**与访谈呼应**：Nick说的"三人团队"可能还保守了

---

### 💡 Vibe Coding的企业批评

**Java创始人James Gosling**：
> "as soon as your [vibe coding] project gets even slightly complicated, they pretty much always blow their brains out"
> "not ready for the enterprise because in the enterprise, [software] has to work every fucking time."

**数据**：
- 45%的AI生成应用包含可利用的OWASP漏洞
- 最常见的QA做法(36%)是跳过QA
- 2025年72%开发者实际并未使用Vibe Coding

来源: [The New Stack - Vibe Coding Fails Enterprise](https://thenewstack.io/vibe-coding-fails-enterprise-reality-check/), [Veracode 2025研究]

**有趣对比**：Nick的BMAD流程恰恰是vibe coding的反面——每个环节都有质量控制

---

### 💡 中国GLM模型的性价比优势

Nick在访谈中透露他主力使用GLM：

> "为什么用GLM？因为它性价比比较高。用Claude的话，那个token自由的打法是另外一套...五个小时很快就用完了。"

**GLM-4.7最新数据**（2025年12月发布）：
- LiveCodeBench得分84.9%，超过Claude Sonnet 4.5
- SWE-bench达73.8%，开源模型最高
- 成本：$3/月（或本地运行免费）

来源: [PRNewswire - Z.ai GLM-4.7](https://www.prnewswire.com/news-releases/zai-releases-glm-4-7-designed-for-real-world-development-environments-cementing-itself-as-chinas-openai-302649821.html)

**潜在文章角度**：
- "$3的中国AI vs $200的美国AI：BMAD实战者的选择"
- "国产大模型的逆袭：不是最强，但够用且便宜"

---

### 💡 AI编程的心理成本：更快但更累

**数据**：
- 使用AI编程工具的开发者任务完成时间反而增加19%
- 67%开发者花更多时间debug AI生成的代码
- 83%开发者职业生涯中经历过burnout
- "Everyone else is becoming 10x, what's wrong with me?"的自我怀疑

来源: [Programming Insider - AI Coding Paradox](https://programminginsider.com/the-ai-coding-paradox-when-productivity-tools-increase-developer-stress/)

**Nick的反例**：他的工作节奏允许"还有时间上微信"

**潜在文章角度**：
- "AI让你更快还是更累？取决于你的流程"
- "BMAD的隐藏价值：结构化带来的心理安全感"

---

### 💡 Product Owner成为新的瓶颈

**Andrew Ng的预测**：开发者:PM比例将从1:4-6反转为2:1

**关键引用**：
> "As coding accelerates exponentially, the bottleneck in product development is no longer engineering; it's product."

来源: [Salesforce Ventures - How Top Product Teams Leverage AI 2025](https://salesforceventures.com/perspectives/how-top-product-teams-are-actually-leveraging-ai-in-2025/)

**访谈呼应**：Nick强调"产品拍板人"的重要性

> "Product Owner是要为这个产品负责的...他能对这个产品的所有事情拍板。"

**马驰的痛点**：产品同事想偷懒，说"你就照着原来写"

---

## 有趣的矛盾和悖论

### 🔄 悖论1：流程越重，效率越高

传统观点：流程是overhead，拖慢速度
BMAD现实：更多的检查点 = 更少的返工 = 更快的交付

> Nick: "我不觉得慢，我觉得挺快的。"
> 简白: "我感觉他确实效果好，但是它的代价就是我需要大量的human-in-the-loop。"

---

### 🔄 悖论2：代码变便宜，但写代码的人更贵

- 代码生成成本趋近于零
- 但能正确使用AI生成代码的人更稀缺
- "技术拍板人"的价值上升

---

### 🔄 悖论3：AI越强大，人类判断越重要

Nick的工作流中，AI做几乎所有execution，但每个关键节点都需要人类judgment：
- PRD质量判断
- 详细设计review
- Code review report审核
- 最终验收

---

### 🔄 悖论4：测试覆盖率高，但端到端信任低

马驰的银行项目困境：
- 单元测试通过 ≠ 集成测试通过
- 沙盒环境 ≠ 生产环境
- 最终还是靠人工测试

---

## 疯狂的想法和角度

### 🚀 "BMAD是最后一个人类主导的开发流程"

如果AI继续进步，未来可能连详细设计都不需要人类review
Nick的工作流可能是人类开发者的"黄昏时代"

---

### 🚀 "Scrum Master复活了，但不是人类"

BMAD本质上是把Scrum的角色全部AI化
讽刺的是，最了解Scrum的人（Nick）反而最容易适应

---

### 🚀 "文档重新成为核心资产"

代码可以重写，但PRD/架构文档是真正的知识资产
这和20年前"代码即文档"的理念完全相反

---

### 🚀 "银行项目是AI编程的照妖镜"

马驰的痛苦恰恰揭示了AI编程的边界：
- 没有API文档
- 沙盒环境不可信
- 依赖外部系统响应
这些场景AI几乎无能为力

---

### 🚀 "中国开发者可能比美国开发者更快适应AI编程"

- 性价比敏感 → 更愿意用GLM等便宜模型
- 996文化 → 对效率工具更渴望
- 技术实用主义 → 不纠结"是否算真正编程"

---

## 尚未找到的信息（需要进一步调研）

- [ ] BMAD在其他中国团队的采用情况
- [ ] GLM vs Claude在BMAD流程中的具体效果对比
- [ ] "三人团队"模式的更多成功案例
- [ ] 银行/金融行业AI编程的真实案例
- [ ] 马驰提到的"/qc"流程的具体设计

---

## 潜在文章标题候选

1. **"BMAD实战：一个Scrum Master的AI原生开发之旅"** - 人物故事角度
2. **"三人团队的未来：Product Owner、UX Designer和技术拍板人"** - 组织架构角度
3. **"代码变便宜了，然后呢？"** - 行业变革角度
4. **"从Code Review到Review Report：AI时代的技术领导力"** - 方法论角度
5. **"棕地项目的终结：当重写比重构更便宜"** - 技术决策角度
6. **"$3的GLM vs $200的Claude：实战者的选择"** - 工具选型角度
7. **"产能过剩的程序员：有屠龙刀，没有龙"** - 讽刺角度
8. **"BMAD的入场券：你需要先学会敏捷"** - 教育角度
9. **"Scrum Master没死，它变成了AI"** - 历史演进角度
10. **"Context Collapse：AI编程的隐形杀手"** - 技术深度角度

---

*收集时间：2026-01-24*
*来源：Agent管理论坛第9期录音稿 + Web搜索*
