# Writing Style Guide

This guide captures the analyzed patterns from 4 published 微信公众号 articles to maintain consistency in writing style and tone.

**Articles analyzed:**
1. AI Coding的永动机项目
2. AI Coding领域的伪问题和真问题
3. 为什么云厂商销售只会打折？
4. 基础架构部，还有必要吗？

---

## Tone & Voice

### Overall Character
- **Conversational and casual**: Write as if talking to a friend or colleague over coffee
- **Highly opinionated**: Take strong stances, don't hedge unnecessarily
- **Critical but constructive**: Point out problems bluntly, but offer solutions or alternatives
- **Self-referential**: Use "我" frequently, mention personal experience
- **Self-aware humor**: Occasional self-deprecation and parenthetical asides

### Voice Characteristics
- Direct and confrontational when challenging popular opinions
- Mix technical authority with accessible language
- Use humor and sarcasm to make points memorable
- Show frustration with industry hype and buzzwords
- Maintain credibility through specific examples and theory
- Not afraid to name names (companies, people, products)

### Examples of Conversational Tone

**Acknowledging then countering criticism:**
> "有朋友说我:'马工，你天天说人家一句话建站不行，但是人家能拿到预算，能拿到投资，能在桔子酒店开发布会，你只能在微信叽叽歪歪。事实胜于雄辩，错的肯定是你的理论，而不是人家的真金白银。'
>
> 这位朋友逻辑严密，很有道理。如资本主义社会谚语所说: Money speaks louder。不过我们工程师不管这么多，我们只看一个指标: 这玩意真的有用吗？"

**Self-aware humor:**
> "试举一例，牛马管理系统会半夜把牛马叫起来干活，但是高端人才系统肯定不能这样做，不然高端人才会骂人的，（等等，我说反了吗？）"

**Frustrated but frank assessment:**
> "这技术含量还不如农贸市场卖豆腐的。买豆腐的要讲清楚水豆腐，油豆腐和攸县香干的区别；要提供客家酿豆腐菜谱；还要发明西汉淮南王制豆腐的故事。相比之下，卖云计算的所谓专家们只需要做一个事：把目录价格乘以从0.2到0.95不等的折扣数，所需要的全部技能是小学四年级算术。"

**Casual self-identification:**
> "作为AI Coding的狂热信仰者，我每天都在动手探索，也和同好积极交流。"

**Personal experience as authority:**
> "我从事软件开发20年，从来没见过一个软件开发项目是因为Demo写不出来而失败的。"

**Sarcastic criticism:**
> "这个案例里，都基于 Nginx 了，还自研个啥？估计自研了个安装脚本。"

> "说句难听的，基本就是神棍们在跳大神。"

**Vivid comparisons:**
> "从业务单元的视角来看，其状非常幼稚，类似两个初中男生在比拼'你只能尿两米，我能尿三米'。"

---

## Structure Patterns

### Article Organization

**Opening (引入):**
- Start with a concrete, recent example or anecdote
- Often begins with "前两天..." or "最近..." or direct observation
- Introduce the topic through something specific, not abstract
- Hook with controversy or a surprising observation

**Examples of strong openings:**

> "前两天有个朋友发了个AI Coding工具发布会的材料。如往常一样，这个工具又在宣扬一句话建站。"

> "作为AI Coding的狂热信仰者，我每天都在动手探索，也和同好积极交流。这个过程中，我发现很多聪明的朋友花时间研究一些伪问题和一些不太重要的问题，我斗胆列出来，和同好们交流。"

> "从事 IT 行业的朋友们，都有一个很具体的感受，云厂商的销售们手里没什么武器，无非就是三样：降价，打折扣，给优惠券。"

> "过去二十年，中国互联网公司取得了巨大的成就。基础架构部（或者技术平台部，或者运维开发部，或者架构平台部）作为互联网公司的技术底座维护者，贡献巨大。但是随着技术的进步，此类部门的老经验在云时代，越来越不适用..."

**Body (展开):**
- Build argument through multiple specific examples
- Use analogies to illustrate abstract concepts
- Include imagined dialogue or Q&A to address counterarguments
- Layer technical details progressively
- Use subheadings or numbered lists for complex topics
- Cite specific companies, products, URLs

**Example of progressive argument building:**
1. State the problem theoretically
2. Use analogy to make it concrete (永动机)
3. Show real-world failures
4. Contrast with success case
5. Draw conclusion

**Conclusion (总结):**
- Provide actionable alternatives or recommendations
- End with a call to action or invitation for discussion
- Sometimes end with a provocative statement or reversal
- May include engagement prompt

**Examples of conclusions:**

> "换句话说，一句话建站是胡扯，一百句话建站可能就是革命真理！"

> "有兴趣研究这个问题的同好，欢迎在公众号给我留言，我们一起交流讨论。"

> "作者一直在互联网公司的基础架构部/架构平台工作，批评的对象当然包括我自己。十几年来，我总在思考这类部门的价值，目前有初步结论。但是用什么替换此类部门，答案仍然不清晰。此文纯属抛砖引玉，希望激发从业者参与，热切的盼望各位读者转发，点赞和评论，尤其盼望坦率和具体的批评。"

### Typical Length
- Long-form articles (2000-4000+ characters)
- Depth over brevity
- Multiple sections with clear progression
- Willing to write extensively when needed

### Section Techniques
- Use rhetorical questions as transitions
- Numbered lists for multiple related points (see "伪问题" pattern)
- Subheadings (especially in longer articles about cloud vendors)
- Progressive revelation (简单 → 复杂)
- Blockquotes for cited content

---

## Content Elements

### Examples Usage - Always Be Specific

**Name real companies and products:**
- "字节的Trae团队在发布solo的时候就试图一句话生成电商"
- "Amazon 的Kiro"
- "Lovable是目前最热门的小白建站工具"
- "腾讯云负载均衡 CLB"
- "阿里AliSQL"
- "Clickhouse"
- "Snowflake/BigQuery/Athena"
- "Hadoop", "Impala", "Presto", "Spark streaming", "Storm"

**Name real people:**
- "我的朋友Nick的开源项目"
- "用大铭的大白话来说"
- "我的朋友冯若航非常巧妙的填补了这个真空"
- "阿里云的张瓅玶先生提出"
- "SealOS 的方海涛主张"
- "ClapDB 的李令辉主张"

**Include specific URLs:**
- https://github.com/terryso/polyv-live-cli
- https://github.com/bmad-code-org/BMAD-METHOD
- Link to documentation, articles, repos

**Mix positive and negative examples:**

Positive (what works):
> "在这个意义上，我建议大家去看一下我的朋友Nick的开源项目 保利威直播云CLI
>
> https://github.com/terryso/polyv-live-cli
>
> 他这个项目的代码基本是Claude Code的写的。他采用Bmad方法论，用了bmad内置的persona，生成PRD，再生成stories，再让AI生成代码和测试用例。
>
> 这个软件不仅完成了，而且被用户用起来了，走过了软件开发生命周期的主要部分。换句话说，这是个可以验证的成功案例，不是做着好玩的娱乐项目。"

Negative (what doesn't work):
> "Trae发布了一句话电商案例之后，有用户试用，然后发现根本玩不转。而Trae官方回答其实推翻了'一句话建站'的口号。"

### Technical Details - Theory + Practice

**Reference foundational theory:**
> "谁要是能证明一句话建站可行，他就推翻了香农的信息学理论基础，是以后要进课本的人物，可以要清华给他建个独享的办公楼"

> "这种情形和物理学上的永动机一样: 不管你的技术怎么厉害，团队里有多少出来的'大师'，只要你还没推翻整个现代物理学，你就不可能造出一个永动机来！"

**Explain with plain language after using jargon:**
> "工程师要参与整个软件开发生命周期，西人所云Software Development Life Cycle者。用大白话说就是投资人管杀不管埋，工程师管杀也管埋，有时候还要擦屁股。"

**List technical requirements concretely:**
> "你的大数据平台能否自主接入新数据源？
> 你的大数据平台能不能和 BI 工具方便的对接？
> 你的大数据平台有没有精细的访问控制和访问审计？
> 你的大数据平台能不能精确的给业务单元计费？
> 你的大数据平台怎样帮助业务部门做到个人信息保护合规？"

**Give numbered technical details when appropriate:**
> "但是有经验的软件老师傅一样就能看出，Kiro这一套是典型的瀑布式开发流程。它有几个假设
>
> 1.需求方一开始就知道自己想要什么。
> 2.架构师（人和AI）能准确的把需求翻译成代码任务。
> 3.开发者（AI）能严格的遵循架构师的设计。
> 4.只要每个小任务完成，整个系统就能如预期的工作。
>
> 无需多言，这几个假设都不成立。"

### Analogies and Metaphors - Make It Concrete

**Physical world analogies:**
> "这种情形和物理学上的永动机一样"

> "Demo写得快，相当于你跳毛利舞舌头伸得快一样: 让人印象深刻，但是没什么用。"

> "新西兰的毛利人打仗之前，会跳个Haka战舞，大概像这样: [image/video] 你不能说这玩意没用，但是这玩意显然不是战斗业务的主要部分"

**Vivid everyday comparisons:**
> "这技术含量还不如农贸市场卖豆腐的。买豆腐的要讲清楚水豆腐，油豆腐和攸县香干的区别；要提供客家酿豆腐菜谱；还要发明西汉淮南王制豆腐的故事。"

> "从业务单元的视角来看，其状非常幼稚，类似两个初中男生在比拼'你只能尿两米，我能尿三米'。"

**Commodity/market comparisons:**
> "云厂商卖虚拟机和 CDN 的方法，同大宗商品交易所卖小麦的方法，基本差不多：价格取决于并且只取决于规格。巴西的二级小麦和乌克兰的二级小麦没有区别，阿里云的 8C16G 和 火山引擎的 8C16G 也没有区别，都被市场视作同一个SKU。"

**Cultural/political references:**
> "缅北话术"
> "桔子酒店会议厅"
> "可以要清华给他建个独享的办公楼"

**Exaggeration for sarcastic effect:**
> "后面你有地球最强大的AI引擎，银河系最先进的agentic框架，也拯救不回来了。"

> "怎么可能还在苦哈哈的在桔子酒店会议厅发布劳什子Coder 0.1？"

**Job/role metaphors:**
> "我分别称之为调参师傅，魔改师傅和仿造师傅。"

### Evidence Types

**Personal experience:**
> "我从事软件开发20年，从来没见过一个软件开发项目是因为Demo写不出来而失败的。"

> "作者一直在互联网公司的基础架构部/架构平台工作，批评的对象当然包括我自己。"

> "在笔者的经验中，云原生系统的可观测性开销，往往占到云开销的 15%-25%。"

**Theoretical foundations:**
> "香农的信息学理论基础"
> "现代物理学"
> "瀑布式开发流程"
> "DevOps的演进"

**Detailed case studies with specifics:**
The MuseAI case in the cloud vendor article - detailed analysis with specific services mentioned (TDDL, Diamond, Pangu, IDaaS, API Gateway, etc.)

Nick's Polyv CLI project - specific GitHub links and methodology

**Industry patterns:**
> "全国起码有上百个基础架构部（或者大数据平台部，或者数据中台）过去十年就干这些事。"

> "在飞书和钉钉流行之前，中国五百强里起码有两百个企业养了一个团队在研发内部 IM 工具。"

**Counter-examples (what NOT to do):**
Trae's one-sentence e-commerce demo
Kiro's waterfall approach
Companies building internal IM tools
基础架构部's various anti-patterns

---

## Language Patterns

### Common Phrases and Transitions

**Starting arguments:**
> "实际上，大多数互联网公司的技术并非核心竞争力"

> "换句话说，一句话建站是胡扯，一百句话建站可能就是革命真理！"

> "恰恰相反的是，如果业务单元有很多独特的，业界普遍不支持的软件需求，很可能说明他们的软件选型出了问题。"

> "但是有经验的软件老师傅一样就能看出，Kiro这一套是典型的瀑布式开发流程。"

> "无需多言，这几个假设都不成立。"

**Introducing examples:**
> "试举一例，牛马管理系统会半夜把牛马叫起来干活"

> "举例来说， URL https://magong.se/api/todos 的域名 magong.se 可能取决于基础设施代码的 DNS 部分"

> "比如同程公司软件工程师编写了大量软件自动化大家的出行，但是他们的工程师想要一个HBase集群还是在 web 界面上点来点去"

> "典型的显示，即使是是来自阿里集团的云用户，也没能受益于云服务"

**Challenging assumptions:**
> "这个听起来挺好的，也应用了软件工程中常用的分而治之方法论。不少朋友还把这一套搬去了Claude Code。但是..."

> "虽然我不赞同张先生的观点，但是他是阿里云为数不多能够和客户谈论云原生架构 — 请注意，不是念云原生经 — 的专家。"

> "很不幸的，在过去若干年来，我们发现基础架构部在两点上得分越来越低。"

> "恕我直言，AI一定会取代人类成为SDLC的主力，人会被边缘化"

**Expressing opinions/analysis:**
> "我有一个不太全面但是可能很核心的解释："

> "我斗胆列出来，和同好们交流。"

> "我个人认为现在最重要的问题是:"

> "列举上述缺位，笔者无意批评客户。实际上，唯一应该对这种缺位负责的就是云厂商。"

**Concluding/summarizing:**
> "综上所述，云服务绝不只是部署过程才需要关注的虚拟机池子加一个托管数据库"

> "在这个意义上，我建议大家去看一下我的朋友Nick的开源项目"

> "总所周知，中国软件工程师长期处于过劳状态"

> "基本上，这个最佳实践能够覆盖绝大多数负载。"

**Setting up context/explanation:**
> "用大白话说就是投资人管杀不管埋，工程师管杀也管埋，有时候还要擦屁股。"

> "西人所云Software Development Life Cycle者。"

> "所谓专家们只需要做一个事"

### Rhetorical Devices

**Rhetorical questions to reader:**
> "这玩意真的有用吗？"

> "为什么搞成这样子？"

> "基础架构部，真的还有价值吗？"

> "都基于 Nginx 了，还自研个啥？"

> "这和可观测有一毛钱关系吗？"

**Imagined dialogue/objections:**
> "有朋友说我:'马工，你天天说人家一句话建站不行，但是人家能拿到预算，能拿到投资，能在桔子酒店开发布会，你只能在微信叽叽歪歪。事实胜于雄辩，错的肯定是你的理论，而不是人家的真金白银。'
>
> 这位朋友逻辑严密，很有道理。如资本主义社会谚语所说: Money speaks louder。不过我们工程师不管这么多..."

> "你问多几句，对方就会生气的反问：'你处理过双十一吗？你知道我管多少机器吗？你用户有十亿吗？'"

> "很多基础架构部主张自己的价值是：'老板，我是自己人，更懂业务需求！'听上去似乎很有道理。实际上..."

**Sarcastic/mocking terminology:**
> "老师傅" (for people stuck in old practices): "调参师傅，魔改师傅和仿造师傅"

> "大师" (mocking false expertise): "团队里有多少出来的'大师'"

> "劳什子Coder 0.1" (dismissive)

> "跳大神" (charlatan behavior): "说句难听的，基本就是神棍们在跳大神。"

> "所谓专家们" (dismissive of fake expertise)

> "美其名曰" (sarcastically introducing inflated claims): "美其名曰《统一大数据管理平台》"

**Parenthetical asides for humor/commentary:**
> "（等等，我说反了吗？）"

> "（或者技术平台部，或者运维开发部，或者架构平台部）"

> "— 请注意，不是念云原生经 —"

> "— 具体地说是阿里云 —"

**Vivid dismissive phrases:**
> "根本玩不转"

> "烂尾"

> "吃得太饱了"

> "提桶跑路"

> "闷头干一年"

> "凉置了三年"

### Technical Terminology

**Chinese-English Mix - Natural Integration:**

Examples showing natural mixing:
> "工程师要参与整个软件开发生命周期，西人所云Software Development Life Cycle者。"

> "这种 ClickOps 在十五年前是可以接受的，但是业界早就发展出 Infra as Code 理念。"

> "使用支持自动扩容的分布式数据库，必要的时候加缓存。使用 Infra as Code 确保上述系统 immutable"

> "CI/CD 流水线也不支持阿里云"

> "MuseAI 最开始作为一个内部项目开发，只需要服务阿里员工，后来需要服务多个集团用户，团队就不得不做实现多租户系统（Multitenancy[1]）"

**Common English terms used freely:**
- SDLC, CI/CD, DevOps, API, RDS, CDN, SSO, BI
- Scalability, Infra as Code, ClickOps
- BYOCloud, IdP, EBITA
- Demo, spec, design, task

**Explain jargon through ironic contrast:**
> "西人所云Software Development Life Cycle者。用大白话说就是投资人管杀不管埋，工程师管杀也管埋，有时候还要擦屁股。"

> "阿里云为数不多能够和客户谈论云原生架构 — 请注意，不是念云原生经 — 的专家"

**Use "所谓" for sarcasm:**
> "所谓专家们"
> "所谓更适应企业特殊需求的 IM"

### Sentence Patterns

**Listing alternatives/variations:**
> "基础架构部（或者技术平台部，或者运维开发部，或者架构平台部）"

> "一个AI Coding工具，不管它是软件，框架，流程，架构还是任何新发明的高大上词语"

**Contrast patterns (A不是B，而是C):**
> "这些平台和云平台相比，技术差一个时代，本来只应该承载旧业务。不过遗憾的是，尽管云平台的服务远胜于这些自建 PaaS 的服务，但是在惯性驱使下，新业务也继续使用它们。"

**Progressive intensity (越来越):**
> "越来越不适用，而他们又普遍跟不上新问题"

**Hypothetical if-then:**
> "如果你能推翻现代物理学，我相信你也没什么兴趣去做商业产品。"

> "如果一开始 MuseAI 就基于阿里云平台开发，团队就不需要做后续的集团外部署专项改造了，可以节省半年时间。"

**Enumeration with detailed explanation:**
> "怎么基于现有LLM的水准利用AI和人组建一个合成软件开发团队？具体的说:
> 1.把人和AI都视作工程师，了解他们的长处和弱点。
> 2.给这些工程师分配不同的角色
> 3.定义适当的控制环节
> 4.一个弹性的环节组合方法"

---

## Argumentation Style

### Core Approach
1. **Challenge conventional wisdom**: Identify popular but flawed ideas
2. **Use theoretical foundations**: Ground arguments in CS theory, engineering principles
3. **Provide practical evidence**: Real projects, case studies, measurable outcomes
4. **Offer alternatives**: Don't just criticize—show what works
5. **Acknowledge nuance**: Show humility while being confident

**Example of acknowledging nuance:**
> "我有一个不太全面但是可能很核心的解释："

> "作者一直在互联网公司的基础架构部/架构平台工作，批评的对象当然包括我自己。"

### Common Argument Structures

**Pattern 1: Debunk the myth (永动机模式)**

Structure:
1. State the popular but wrong claim
2. Explain why it's theoretically impossible
3. Use physics/math/CS theory analogy
4. Show practical failures
5. Offer correct approach

Example from "AI Coding的永动机项目":
> "一句话建站的可行性，在理论上已经被证明不成立了，和AI能力没关系。" [Claim is wrong]
>
> "这种情形和物理学上的永动机一样: 不管你的技术怎么厉害...你就不可能造出一个永动机来！" [Theoretical impossibility]
>
> "谁要是能证明一句话建站可行，他就推翻了香农的信息学理论基础" [Ground in theory]
>
> [Shows Trae's failure, contrasts with Nick's success] [Practical evidence]
>
> "换句话说，一句话建站是胡扯，一百句话建站可能就是革命真理！" [Correct approach]

**Pattern 2: Progressive critique (多个伪问题模式)**

Structure:
- List multiple related problems
- Label them clearly (第一个伪问题, 第二个伪问题, etc.)
- Examine each with examples
- Build to what the TRUE problem is
- Offer solution

Example from "AI Coding领域的伪问题和真问题":
> "第一个伪问题是怎么让AI从一句话生成一个软件。" [Problem 1]
> [Detailed critique with Trae example]
>
> "第二个伪问题是一次性把代码写好。" [Problem 2]
> [Detailed critique with Kiro example]
>
> "还有一个真实但是低价值的问题是'Claude Code使用小技巧'。" [Problem 3]
>
> "我个人认为现在最重要的问题是: 怎么基于现有LLM的水准利用AI和人组建一个合成软件开发团队？" [The REAL problem]
> [Offers 4-point solution]

**Pattern 3: Deep case study analysis (MuseAI模式)**

Structure:
- Introduce the case with context
- Systematically analyze multiple aspects
- Use subheadings for organization
- Show what services/approaches were missing
- Identify root cause
- Generalize to industry problem

Example from "为什么云厂商销售只会打折？":
- MuseAI case introduced
- Analyzed missing services: IDaaS, API Gateway, observability, security
- Each section shows: what they did, what cloud could have provided, why cloud failed
- Root cause: "云厂商自己的团队也不懂怎么用云"
- Generalizes to commodity problem

**Pattern 4: Systematic deconstruction (基础架构部模式)**

Structure:
- Set up historical context (what WAS valuable)
- Systematically list current problems
- Use specific company examples for each
- Show pattern across industry
- End with call for transformation

Example from "基础架构部，还有必要吗？":
- Historical value acknowledged
- Problem categories: 没有核心技术, 无法交付业务价值, 技术理念落后, etc.
- Each with concrete examples (AliSQL, NWS, Clickhouse, etc.)
- Ends seeking discussion on alternatives

### Establishing Authority

**Years of experience:**
> "我从事软件开发20年，从来没见过一个软件开发项目是因为Demo写不出来而失败的。"

> "作者一直在互联网公司的基础架构部/架构平台工作"

**Specific quantitative knowledge:**
> "在笔者的经验中，云原生系统的可观测性开销，往往占到云开销的 15%-25%。"

> "阿里云作为唯一公开宣称盈利的厂商，2025财年第一季的 EBITA 利润率约为 8%，还不如做空调的美的利润高。"

> "全国起码有上百个基础架构部（或者大数据平台部，或者数据中台）过去十年就干这些事。"

**Name connections:**
> "我的朋友Nick的开源项目"

> "我的朋友冯若航非常巧妙的填补了这个真空"

> "SealOS 的方海涛主张《云本应该就是操作系统》， ClapDB 的李令辉主张《云是一台新电脑》"

**Reference other work:**
> "具体原因可以参见大铭的文章"

> "关于出错的原因和解决办法，我有另外一篇文章加以讨论"

> "有兴趣的朋友可以看下..."

**Detailed technical knowledge:**
- Cite specific products, versions, APIs
- Show understanding of architecture patterns
- Reference academic concepts (Shannon, SDLC, etc.)
- Demonstrate hands-on experience

### Balancing Criticism and Solutions

**Always pair criticism with alternatives:**

Criticism:
> "一句话建站是胡扯"

Solution:
> "一百句话建站可能就是革命真理！" + Nick's example with BMAD

Criticism:
> "此类一次性写好代码是瀑布式开发"

Solution:
> "我有另外一篇文章加以讨论运用迭代方法论让AI交付工业质量的软件"

Criticism:
> "云厂商在客户开发过程中严重缺位"

Solutions throughout article:
- Should use IDaaS for multi-tenancy
- Should promote API Gateway best practices
- Should educate on observability
- Should lead technical direction

**Don't just complain:**
> "此文纯属抛砖引玉，希望激发从业者参与，热切的盼望各位读者转发，点赞和评论，尤其盼望坦率和具体的批评。"

---

## Things to AVOID

❌ **Don't:**

**Vague corporate-speak:**
- Avoid: "赋能", "降本增效", "生态", "闭环" (unless using ironically)
- Avoid: Generic praise like "很好", "先进", "优秀" without specifics
- Avoid: Abstract claims without evidence

**Superficial treatment:**
- DON'T write short takes without depth
- DON'T make claims without examples
- DON'T cite examples without analysis
- DON'T avoid naming names when relevant

**Excessive hedging:**
- Avoid: "可能", "大概", "也许" when you have a strong point
- Avoid: Being overly diplomatic about clearly bad ideas
- But DO acknowledge limitations when appropriate (see nuance examples)

**Over-formality:**
- Don't write like academic papers
- Don't over-explain basic concepts
- Don't use emoji (articles analyzed have ZERO emoji)
- Don't be dry or boring

**Avoid teacher-like explanations (教师爷 voice):**
- Avoid: "不是X，而是Y" format - sounds preachy and mechanical
  - ❌ "但我要说的是：这些平台注定失败，不是因为做得不够好，而是因为这种方式本身就是错的。"
  - ✅ "多数公司都有运维平台。投入不低、系统不少。但运维仍然是瓶颈。"

- Avoid: Explaining "why" things happen (sounds like 教师爷)
  - ❌ "为什么？因为他的控制点在'资源申请'这个后期环节，而开发团队可以在'项目设计'这个前期环节绕过他。"
  - ✅ "管理员有完整的批核权。开发改名重新申请机器。管理员的权力形同虚设。"

- **The pattern**: Tell the story → readers see the contradiction → they understand on their own
- Don't explain "why" - show the pattern and let smart readers connect the dots
- Write as if talking to a peer who already gets it, not teaching someone who needs everything spelled out

**Accepting hype uncritically:**
- Don't repeat vendor marketing claims
- Don't accept "because everyone does it" as reasoning
- Don't ignore theoretical impossibility for trendy ideas

**What the articles NEVER do:**
- Never praise without concrete specifics
- Never use buzzwords unironically
- Never write without real examples
- Never accept conventional wisdom unchallenged
- Never end without engagement or next steps

---

## Things to EMBRACE

✅ **Do:**

**Be specific and concrete:**
> "字节的Trae团队"
> "Amazon 的Kiro"
> "阿里云作为唯一公开宣称盈利的厂商，2025财年第一季的 EBITA 利润率约为 8%"
> "全国起码有上百个基础架构部"

**Name names:**
> "我的朋友Nick"
> "冯若航"
> "张瓅玶先生"
> "SealOS 的方海涛"

**Use numbers and metrics:**
> "20年"
> "15%-25%"
> "0.2到0.95不等的折扣数"
> "半年时间"
> "两百个企业"

**Include URLs:**
- GitHub repos
- Documentation
- Previous articles
- Reference materials

**Use vivid language:**
> "农贸市场卖豆腐"
> "永动机"
> "跳大神"
> "提桶跑路"
> "尿两米，我能尿三米"

**Challenge consensus:**
> "宣扬这种理论上就不可能的软件永动机，只会误导非专业用户"
> "虽然我不赞同张先生的观点"
> "恕我直言，AI一定会取代人类成为SDLC的主力"

**Mix theory and practice:**
- Shannon's information theory + Trae's failure
- Physics (perpetual motion) + AI coding hype
- Software engineering principles + real company examples

**Use rhetorical devices:**
- Imagined dialogue
- Rhetorical questions
- Sarcastic terminology
- Parenthetical asides
- Cultural references

**Show alternatives:**
- Not just "X is bad" but "X is bad, Y works better"
- Not just criticism but constructive solutions
- Reference successful cases

**Write with depth:**
- Long articles are OK (even encouraged)
- Multiple subheadings for complex topics
- Detailed case study analysis
- Thorough examination of each point

**Engage readers:**
> "欢迎在公众号给我留言，我们一起交流讨论。"
> "热切的盼望各位读者转发，点赞和评论，尤其盼望坦率和具体的批评。"

---

## Article Templates

### Template 1: Debunking Article (永动机模式)
Based on "AI Coding的永动机项目":
```
1. Opening: Recent example of the flawed idea (product launch, demo)
2. Quick reference to previous debunking
3. Theoretical foundation: Why it's impossible (永动机, Shannon theory)
4. Concrete analogy to make it memorable
5. Show misunderstanding with specific example
6. Address imagined objection ("but they got funding!")
7. Explain why demos mislead (focus on wrong part of SDLC)
8. Memorable analogy (Haka war dance)
9. Counter-example: What actually works (Nick's project)
10. Specific details of success case with URLs
11. Interview insight from success case
12. Provocative conclusion with reversal
```

### Template 2: Industry Critique with Deep Analysis (云厂商模式)
Based on "为什么云厂商销售只会打折？":
```
1. Opening: Observable, specific phenomenon everyone recognizes
2. Vivid comparison to make problem concrete (selling tofu)
3. Financial evidence showing the problem
4. Root cause hypothesis ("不太全面但是可能很核心")
5. Detailed case study introduction with context
6. Systematic analysis with subheadings:
   - Problem area 1 + what should have been done
   - Problem area 2 + what should have been done
   - Problem area 3 + what should have been done
7. Synthesize root cause
8. Show secondary effects (industry figures filling vacuum)
9. More examples showing pattern
10. Conclude with core diagnosis
```

### Template 3: True vs False Problems (伪问题模式)
Based on "AI Coding领域的伪问题和真问题":
```
1. Opening: Establish credibility and context
2. State purpose: distinguish false from real problems
3. False problem #1:
   - What it is
   - Why it's theoretically impossible
   - Blockquote example
   - Real-world failures
   - What actually works
4. False problem #2:
   - What it is
   - List assumptions that don't hold
   - Why it fails in practice
   - Reference to fuller treatment
5. Low-value problems (quick dismissal with reasoning)
6. The REAL problem:
   - Clear statement
   - Specific, numbered approach
7. Call for engagement and discussion
```

### Template 4: Systematic Deconstruction (基础架构部模式)
Based on "基础架构部，还有必要吗？":
```
1. Opening: Acknowledge historical value
2. Set up tension: past success vs current problems
3. Provocative framing question
4. State what the department should achieve
5. Problem category 1: No core technology
   - Explain pattern (调参/魔改/仿造师傅)
   - Multiple specific company examples with quotes
   - Sarcastic analysis of each
6. Problem category 2: Can't deliver business value
   - What they focus on vs what business needs
   - Vivid comparison (两个初中男生比拼)
   - List real business requirements
   - Show they can't meet modern needs
7. Problem category 3: Outdated mindset
   - Explain the outdated approach
   - Show modern best practices
   - Contrast with their approach
8. Additional problems: ClickOps, blocking DevOps, etc.
9. Conclusion: Self-reflection + call for discussion
```

### Template 5: Explorative AI Use Case (探索性AI应用案例)
**File**: `templates/article-templates/template-05-explorative-ai-use-case.md`

For demonstrating real AI/engineering projects and their implications. See the template file for complete structure and detailed guidance.

---

## Checklist for New Articles

Before publishing, verify:

**Specificity:**
- [ ] Named at least 3-5 specific companies/products
- [ ] Named specific people (colleagues, friends, industry figures)
- [ ] Included at least 1 URL/link
- [ ] Used concrete numbers/metrics (percentages, years, costs)
- [ ] Gave specific technical details (product names, versions, APIs)

**Argumentation:**
- [ ] Clear thesis stated early
- [ ] Theoretical foundation provided (Shannon, physics, CS principles)
- [ ] At least 2-3 concrete examples supporting argument
- [ ] Addressed likely objections (imagined dialogue or explicit)
- [ ] Offered alternatives/solutions, not just criticism
- [ ] Acknowledged nuance or limitations where appropriate

**Style:**
- [ ] At least one memorable analogy or metaphor
- [ ] Conversational tone (not academic or corporate)
- [ ] Mix of Chinese and English terminology
- [ ] At least one rhetorical question
- [ ] Personal voice evident ("我", experience references)
- [ ] Sarcastic or vivid language for bad practices
- [ ] Strong opening hook (recent event, specific observation)

**Structure:**
- [ ] Sufficient depth (don't skim surface)
- [ ] Progressive argument building
- [ ] Used subheadings if complex topic
- [ ] Blockquotes for cited content where appropriate
- [ ] Clear conclusion or synthesis

**Engagement:**
- [ ] Ends with call to action, discussion prompt, or engagement request
- [ ] Provocative or memorable final line
- [ ] OR humble invitation for critique/discussion

**What to double-check:**
- [ ] No vague corporate jargon (unless ironic)
- [ ] No unsupported claims
- [ ] No emoji
- [ ] Not too short/superficial
- [ ] Haven't accepted hype uncritically
- [ ] Named names when relevant (didn't hedge unnecessarily)

---

## Lessons Learned from Published Articles

### Best Practices (Positive Examples)

Based on FDE/Palantir article feedback (Dec 2025):

**1. 英文使用原则 (English Usage)**

✅ **Follow this pattern**:
- **首次双语介绍**: "Forward Deployed Engineer (前置部署工程师，FDE)"
- **后续只用中文**: "前置部署工程师认为..."，"FDE模式的问题..."
- **专有名词保留英文**: Palantir, OpenAI, NHS
- **成熟缩写保留**: CEO, CFO, SaaS, API, AWS
- **技术术语优先中文**: 可扩展 (scalable), 锁定 (lock-in), 从众心理 (groupthink)

**Example (good)**:
> "Forward Deployed Engineer (前置部署工程师，FDE) 是Palantir推出的岗位。这种前置部署工程师需要常驻客户现场，与传统的驻场实施本质相同。"

**2. 篇幅控制 (Length Control)**

✅ **Target**: 2500-3500字
✅ **Structure**: 5-6个section，每个3-4段
✅ **Focus**: 选择2-3个最强论点深入，放弃次要论点

**How to achieve**:
- 每个论点 = 核心陈述 (1段) + 数据/例子 (1-2段)
- 直击要害，删除铺垫和过渡语
- 一段不超过150字
- 问自己: "这段删掉会影响核心论点吗？" 不影响就删

**Example (good)**:
> **Section**: "为什么FDE只能在国防行业生存？"
> - 段1: 陈述观点 (50字)
> - 段2: 数据支撑 "672 Pentagon官员..." (100字)
> - 段3: 生动例子 "华为/中石油..." (120字)
> - 完成！进入下一section

**3. 引用策略 (Quote Usage)**

✅ **Maximum 2-3 blockquotes** per article
✅ **Only quote when**: 语言本身有冲击力/无法用自己的话更好地表达

**What to quote**:
- Shocking statements: CFO说 "lighting equity on fire"
- Vivid user quotes: "华为也不能对中石油说..."
- Self-contradictions: 官方定义 vs 实际表现

**What to paraphrase**:
- 普通的描述性内容
- 数据和统计（直接陈述即可）
- 多个类似的例子（选最强的一个quote，其余转述）

**Example (good)**:
> Palantir的前CFO批评FDE模式是"lighting equity on fire"。他观察到大量重复浪费的工作和失败项目。
>
> [后续用自己的话分析，不需要更多quote]

**4. 结构紧凑 (Tight Structure)**

✅ **Ideal flow**: 5-6 sections
- 开场: 现象 + 核心观点
- 论点1: 最强的论据 (独特视角)
- 论点2: 数据支撑
- 论点3: 案例/对比
- 结论: 预测 + 讨论邀请

**How to merge sections**:
- 相关的论点合并
- 数据和案例放在同一section
- 避免单独的"背景介绍"section

---

### What Worked Well (Validate in Future Articles)

From FDE article success - **keep doing these**:

**独特视角 (Unique Angle)**:
- 中台对比 (Zhongtai parallel) - 别人想不到的角度
- 跨文化观察 - 中美对比，而非单纯批评美国
- Pattern recognition - "我见过这个电影"

**真实数据 (Real Data)**:
- 672 Pentagon官员 (有来源的统计)
- CFO原话 "lighting equity on fire"
- NHS 25%采用率失败
- 政府收入从46.5% → 55%增长

**生动比喻 (Vivid Analogies)**:
- 华为/中石油例子 - 接地气且有力
- The Spreadsheet Test - 可记忆的框架
- "美国的中科红旗" - 一句话点破本质

**强烈观点 (Strong Opinions)**:
- 直接判断: "这是哪门子的软件公司？"
- 预测: "3-5年后会成为笑话"
- 不回避争议

---

### Updated Writing Checklist

Add these to pre-publish checks:

**English usage**:
- [ ] 英文术语首次出现已标注中文
- [ ] 后续段落只用中文，不反复切换
- [ ] 只保留专有名词和成熟缩写的英文

**Length control**:
- [ ] 总字数在2500-3500之间
- [ ] 每个section不超过4段
- [ ] 删除了次要论点和重复例子

**Quote discipline**:
- [ ] Blockquote不超过3处
- [ ] 每个quote都有冲击力（shocking或生动）
- [ ] 其余内容用自己的话转述

**Focus**:
- [ ] 只保留2-3个最强论点
- [ ] 有独特角度（不是人云亦云）
- [ ] 每个论点有真实数据支撑

---

## Quick Reference: Favorite Phrases

**Opening patterns:**
- "前两天..."
- "作为...的狂热信仰者，..."
- "从事 IT 行业的朋友们，都有一个很具体的感受，..."
- "过去二十年，..."

**Transition patterns:**
- "实际上，..."
- "换句话说，..."
- "恰恰相反的是，..."
- "试举一例，..."
- "无需多言，..."

**Critique patterns:**
- "这个听起来挺好的，但是..."
- "很不幸的，..."
- "恕我直言，..."
- "说句难听的，..."

**Conclusion patterns:**
- "综上所述，..."
- "在这个意义上，..."
- "换句话说，..."
- "有兴趣研究这个问题的同好，欢迎在公众号给我留言..."

**Sarcastic labels:**
- "调参师傅，魔改师傅和仿造师傅"
- "所谓专家们"
- "老师傅"
- "劳什子..."
- "美其名曰"
- "跳大神"

---

**Note for slash commands**: This guide is now fully active and packed with examples. Use it as the primary reference for all outline and draft generation. The guide contains extensive quotes and patterns extracted from 4 published articles to ensure consistency in style, tone, structure, and argumentation.
