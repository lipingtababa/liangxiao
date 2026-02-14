# Brainstorm: 10X Engineers vs Organisational Bottlenecks

## 用户原始观点 (Your Original Argument)

来源: 产品化群 2026-01-31

> "我感觉每个人都是10X程序员的路子是错的。每个人都10x，从哪里来10x业务，必然会让狼群互相撕咬。"

> "工程师10x了，法务销售交付没有10x的话，也是巨大的问题"

> "我现在就感觉到了在我司，工程师效率并非瓶颈所在，我提高再多，如果销售和产品跟不上，并不能把效率转化为商业竞争力"

> "我正在积极搜索能把工程师效率直接翻译成市场竞争力的公司"

刘连响's analogy: "CPU计算瓶颈在网络，GPU计算瓶颈可能在CPU和GPU之间的通信。这个最低消的瓶颈制约了系统的瓶颈，而不是最快的那个引领"

linhow's estimate: "在一个100人团队的生产存量生产项目中，我觉得提升一倍的效率，已经是26年比较乐观的目标了"

---

## 💡 Theory of Constraints - 瓶颈会移动

Source: [Forte Labs - Theory of Constraints 101](https://fortelabs.com/blog/theory-of-constraints-101/)

核心原则: Every process has a single constraint and total process throughput can only be improved when the constraint is improved. **Spending time optimizing non-constraints will not provide significant benefits.**

瓶颈转移实例 (from [The Agile Mindset](https://www.theagilemindset.co.uk/2025/10/07/the-theory-of-constraints-in-software-development-finding-and-fixing-the-real-bottleneck/)):

> "Once you remove one bottleneck, another will emerge. Fix the manual deployment process, and suddenly, test data creation becomes the constraint. Streamline QA automation, and the constraint shifts to UX design capacity."

工厂案例: 瓶装厂自动化了托盘装载后，瓶颈转移到了仓库——货物出产线太快，仓库空间不够了。

**为什么有意思**: 这完美解释了你的观察。工程效率提升后，瓶颈必然转移到其他地方（销售、法务、交付）。

---

## 💡 AI Coding Productivity Paradox - 生产力悖论

Source: [Faros AI Research Report](https://www.faros.ai/blog/ai-software-engineering)

**75% of engineers use AI tools—yet most organizations see no measurable performance gains.**

惊人发现:
- Developers on teams with high AI adoption complete 21% more tasks and merge 98% more pull requests
- BUT PR review time increases 91% - 人工审批成为瓶颈

Source: [METR Study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)

**更惊人的发现**: Developers using AI were on average **19% slower**. Yet they were **convinced** they had been faster.

> "Before starting, they predicted AI would make them 24% faster. After finishing, even with slower results, they still believed AI had sped them up by ~20%."

Source: [CIO - AI Productivity Trap](https://www.cio.com/article/4124515/the-ai-productivity-trap-why-your-best-engineers-are-getting-slower.html)

Gartner data: AI saves average of 5.7 hours/week per employee, but only 1.7 hours spent on high-value work. **0.8 hours spent correcting AI errors**.

**Productivity Leakage**: 效率提升在个人层面，不能转化为业务价值。

**为什么有意思**: 即使AI真的提升了coding速度，这些提升也被系统其他部分吸收了。要么堆积在PR review，要么变成闲置产能，要么被AI错误消耗。

---

## 💡 10X Engineer神话的批判

Source: [Stack Overflow Blog](https://stackoverflow.blog/2024/12/25/the-real-10x-developer-makes-their-whole-team-better/)

> "Individual engineers don't own software; engineering teams own software. It doesn't matter how fast an individual engineer can write software. What matters is how fast the **team** can collectively write, test, review, ship, maintain, refactor, extend, architect, and revise."

Source: [Medium Analysis](https://medium.com/@harish852958/the-myth-of-the-10x-engineer-a-corporate-fairy-tale-8b799c963f86)

2024 analysis数据: A "10x engineer" showed only ~1.6x individual productivity but had a **net negative impact on team productivity (-0.8x)** due to creating more team conflicts.

Source: [IEEE Spectrum](https://spectrum.ieee.org/10x-engineer)

> "Having a tiny percentage of high-performing engineers is often a symptom of bigger organizational issues like siloing or imbalance in power and responsibility."

**为什么有意思**: 10X engineer的存在本身可能就是组织问题的症状，而不是解决方案。

---

## 💡 McKinsey Developer Productivity争议

Source: [Dan North's Review](https://dannorth.net/blog/mckinsey-review/)

Kent Beck评价: "The report is so absurd and naive that it makes no sense to critique it in detail."

Dave Farley评价: "Apart from the use of DORA metrics in this model, the rest is pretty much astrology."

Source: [Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/measuring-developer-productivity)

核心批评: McKinsey只测量effort/output，不测量outcomes/impact。这是reductionist思维——把软件开发当成工厂装配线。

**为什么有意思**: 咨询公司想把知识工作量化成工厂指标，本身就是category error。

---

## 💡 Idle Capacity问题 - 闲置产能

Source: [Test Double - Never Staff to the Peak](https://testdouble.com/insights/never-staff-to-the-peak)

**残酷现实**:

> "No VP of Engineering in history has successfully won an argument with the line, 'it would be better to keep our very expensive engineers sitting idle than implement this unimportant work you're asking us to do.'"

结果: Hiring too many people and retaining them to the point that they're tasked with **make-work** doesn't just make technology worse, it has corrosive knock-on effects on human relationships.

Source: [Crunchbase - Tech Layoffs](https://news.crunchbase.com/startups/tech-layoffs/)

2022-2023年科技公司layoffs: **428,449人**
2024年: **141,467人**
2025年: **127,000人**

很多layoffs的岗位本来就不应该存在: "Many of these layoffs never had to happen, because a huge number of the roles being eliminated never made sense as long-term, full-time positions to begin with."

**为什么有意思**: 大规模layoffs可能不是"经济下行"的问题，而是overstaffing的correction。工程师效率提升 → 更明显的idle capacity → 裁员压力。

---

## 💡 哪些公司能把工程效率转化为竞争力？

### Product-Led Growth vs Sales-Led Growth

Source: [ProductLed](https://productled.com/blog/product-led-growth-vs-sales-led-growth)

**PLG公司** (Stripe, Figma, Vercel):
- 用户自助注册使用
- 开发速度直接影响用户体验
- 20-30% faster growth due to lower customer acquisition costs
- Engineering speed = competitive advantage

**SLG公司** (Enterprise B2B):
- 销售周期3-18个月
- 6-10个决策者参与采购
- 安全审查、合规流程、采购流程
- Engineering speed被下游瓶颈吸收

Source: [General Catalyst](https://www.generalcatalyst.com/stories/sales-led-vs-product-led-growth)

> "Enterprise clients often have longer buying cycles, multiple stakeholders, and significant budgets. These scenarios justify the investment in a skilled sales team to navigate the intricate buying process."

**为什么有意思**: 你在寻找的"工程效率直接转化为竞争力"的公司，本质上就是PLG公司。如果你司是SLG模式，工程效率再高也会被销售周期限速。

---

## 💡 B2B销售周期数据

Source: [Aexus](https://aexus.com/how-long-is-the-average-b2b-software-sales-cycle/)

| 客户类型 | 销售周期 |
|---------|---------|
| SMB (自助) | 分钟到小时 |
| Mid-market | 1-3个月 |
| Enterprise | 6-18个月 |

Source: [Databox](https://databox.com/b2b-sales-cycle-length)

Enterprise win rate: 20-25% (vs SMB 39%)

**为什么有意思**: 即使你的工程团队能在1周内交付feature，enterprise客户的销售周期还是6-18个月。工程速度在这里完全irrelevant。

---

## 💡 为什么销售/法务不能像工程一样被AI加速？

Source: [Integrity Solutions](https://www.integritysolutions.com/blog/ai-in-sales/)

> "Bots will never take the place of an excellent salesperson. Trust is built through meaningful conversations and emotional connections that are required in any sale — all of which bots cannot facilitate. Bots facilitate transactions."

Source: [Crunchbase - B2B Sales Human Interaction](https://news.crunchbase.com/ai/b2b-sales-human-interaction-landsman-sharebite/)

> "Fully automated sales motions may win early with volume, but they often lose late. Without empathy, deals stall. Without rapport, onboardings fail. Without trust, renewals disappear."

Source: [ScienceDirect - AI Salesperson vs Human](https://www.sciencedirect.com/science/article/abs/pii/S0148296322004155)

B2B销售特点: "deals with various members of the organizational buying center across the whole sales process, relying heavily on contextual understanding, interactive communication, and relationship building."

**为什么有意思**: 代码是deterministic的，可以被AI优化。但信任、关系、谈判是non-deterministic的。这就是为什么工程可以10X而销售不行。

---

## 💡 法务合同审核的AI进展

Source: [Virtasant - AI Contract Management](https://www.virtasant.com/ai-today/ai-contract-mangement-legal)

- 法务部门预计到2025年技术投资增长3倍
- AI合同审核节省70-85%时间
- 年处理500份合同的团队可节省200个工作日

BUT:

Source: [Ironclad - Legal AI](https://ironcladapp.com/resources/articles/best-legal-ai-software)

> "Non-legal teams handling contracts—procurement managers, sales contract teams, compliance officers—use AI to ensure consistent adherence to company standards."

**为什么有意思**: 法务AI在进步，但它优化的是合同审核速度，不是决策速度。最终签字还是需要人。

---

## 💡 Stripe/Vercel/Figma的工程速度优势

Source: [Wildfire Labs - AI Architecture Gap](https://wildfirelabs.substack.com/p/the-ai-architecture-gap-why-vercel)

**Stripe数据**:
- 使用AI+技术架构师的团队: feature速度提升35%，质量保持
- 无架构师监督使用AI的团队: 9个月内技术债务拖慢开发速度27%

**Vercel数据**: AI方法带来41% feature开发速度提升

**Figma数据**: 28% feature开发速度提升

Source: [Vercel Blog - Config 2023](https://vercel.com/blog/iterating-from-design-to-deploy)

> "Blurring traditional lines between design and engineering means that all team members can work side-by-side to bring highly creative products to life."

**为什么有意思**: 这些都是PLG公司，用户直接用产品，不需要sales cycle。工程速度在这里真的等于竞争力。

---

## 🤔 Provocative Questions

1. **如果工程效率提升只是创造idle capacity，那我们应该裁员还是找新的事情让他们做？**

2. **"人人10X"的叙事谁在推动？是工程师的ego，还是AI工具公司的marketing？**

3. **如果瓶颈在销售而不是工程，为什么所有AI投资都在coding tools而不是sales tools？**
   - 可能答案: 因为工程师是buyer，工程师喜欢解决技术问题

4. **linhow说的"100人团队提升一倍已经很乐观"——这个一倍提升最终去哪了？**
   - 更多feature？更少工作时间？更少人？

5. **你说在"积极搜索能把工程师效率直接翻译成市场竞争力的公司"——如果找不到呢？这说明什么？**
   - 说明大多数公司的竞争力根本不在工程？

6. **为什么developer tools公司（Stripe, Vercel, Figma）能做到工程=竞争力？**
   - 因为他们的客户是开发者，不需要传统销售？
   - 因为product IS the engineering？

7. **Lunatic take: 也许10X engineer narrative是AI时代的精神鸦片——让工程师觉得自己还有价值，而实际上bottleneck已经不在他们身上了？**

---

## 🔍 Patterns & Contradictions

### Pattern 1: 效率悖论
- 微观层面: AI让个人coding更快
- 宏观层面: 组织throughput没有显著提升
- Gap在哪里: PR review, testing, deployment, 以及最重要的——非工程环节

### Pattern 2: 测量什么得到什么
- McKinsey测量lines of code, commits, Jira tickets
- 结果: 工程师优化这些指标，而不是优化business outcome
- Kent Beck: "Measure the system, not the people"

### Pattern 3: 瓶颈转移是必然的
- Goldratt: 解决一个瓶颈，瓶颈就转移到下一个环节
- 工程不再是瓶颈 → 瓶颈转移到销售/法务/产品
- 这些环节没有同等的AI加速

### Contradiction: PLG公司 vs 大多数公司
- PLG: 工程速度 = 用户体验 = 竞争力
- SLG: 工程速度 → 堆积在销售周期前 → idle capacity

---

## 📎 Gaps - 没找到的东西

1. **具体公司数据**: 哪家公司因为工程效率提升而真正获得了市场份额？
2. **反例**: 有没有传统enterprise公司成功把工程效率转化为竞争力的案例？
3. **中国市场数据**: 国内企业的工程效率vs销售效率对比
4. **历史先例**: 历史上有没有其他行业经历过类似的"生产效率提升但竞争力不变"的情况？

---

## 🌀 Wild Ideas

1. **也许正确的问题不是"如何让工程师10X"，而是"如何让整个组织10X"——这需要重新设计业务流程，不只是写代码更快**

2. **也许AI coding tools的真正价值不是让现有工程师更快，而是让非工程师能做工程师的工作（vibe coding）——这样瓶颈就不存在了**

3. **也许未来不是"每个人都是10X工程师"，而是"每个人都不需要工程师"**

4. **最cynical的take: 10X engineer narrative是科技行业的"内卷叙事"——让工程师互相竞争，而不是质疑为什么他们的效率提升没有转化为更好的待遇或更少的工作时间**

---

## Sources

- [Forte Labs - Theory of Constraints 101](https://fortelabs.com/blog/theory-of-constraints-101/)
- [The Agile Mindset - TOC in Software Development](https://www.theagilemindset.co.uk/2025/10/07/the-theory-of-constraints-in-software-development-finding-and-fixing-the-real-bottleneck/)
- [Faros AI - AI Productivity Paradox](https://www.faros.ai/blog/ai-software-engineering)
- [METR Study - AI Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- [CIO - AI Productivity Trap](https://www.cio.com/article/4124515/the-ai-productivity-trap-why-your-best-engineers-are-getting-slower.html)
- [Stack Overflow - The Real 10x Developer](https://stackoverflow.blog/2024/12/25/the-real-10x-developer-makes-their-whole-team-better/)
- [IEEE Spectrum - Normal Engineers](https://spectrum.ieee.org/10x-engineer)
- [Dan North - McKinsey Review](https://dannorth.net/blog/mckinsey-review/)
- [Pragmatic Engineer - Measuring Developer Productivity](https://newsletter.pragmaticengineer.com/p/measuring-developer-productivity)
- [Test Double - Never Staff to the Peak](https://testdouble.com/insights/never-staff-to-the-peak)
- [Crunchbase - Tech Layoffs](https://news.crunchbase.com/startups/tech-layoffs/)
- [ProductLed - PLG vs SLG](https://productled.com/blog/product-led-growth-vs-sales-led-growth)
- [Aexus - B2B Sales Cycle](https://aexus.com/how-long-is-the-average-b2b-software-sales-cycle/)
- [Integrity Solutions - AI in Sales](https://www.integritysolutions.com/blog/ai-in-sales/)
- [Crunchbase - B2B Sales Human Interaction](https://news.crunchbase.com/ai/b2b-sales-human-interaction-landsman-sharebite/)
- [Virtasant - AI Contract Management](https://www.virtasant.com/ai-today/ai-contract-mangement-legal)
- [Wildfire Labs - AI Architecture Gap](https://wildfirelabs.substack.com/p/the-ai-architecture-gap-why-vercel)
- [Vercel Blog - Design to Deploy](https://vercel.com/blog/iterating-from-design-to-deploy)
