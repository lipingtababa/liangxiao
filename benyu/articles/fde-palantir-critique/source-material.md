# Source Material: FDE & Palantir Critique

## 原始素材来源
从微信聊天记录提取 (2025-10-06)
马工对Forward Deployed Engineer概念和Palantir公司的批判性分析

---

## 核心观点

### 1. FDE的本质：交付工程师，不是什么创新模式

**时间：** 2025-10-06 02:31-08:37

> fde没那么高级。按照palantir描述的，fde入场的时候，连自己要建设什么都不知道，全靠现场调研做个mvp。乙方能让甲方为这种不确定性买单，一定是有极强的客户关系，甚至是甲方ceo无法拒绝的关系。

> 中国最强关系华为公司，也不能对着中石油说"我他妈的也不知道能给你做什么，我先派个fde入场，查看你的数据，占用你的时间，然后做个mvp给你看看，你到时候再决定。当然，你第一天就要付费"。这不神经病么。

> 就是典型的交付工程师，售后，驻场

> 交付工程师没有自己的problem space，用户需要什么就干什么，完全的ad hoc

### 2. FDE只能存在于高腐败行业

**时间：** 2025-10-06 02:34

> fde只能存在于国防工业这种高腐败行业

**时间：** 2025-10-06 08:47

> 你又意淫了， 你在硅谷找出一家比palantir和国防部关系更好的公司出来？

**时间：** 2025-10-06 09:07

> 中国人一眼看穿这种在产品页上挂国旗的公司玩的什么游戏

**时间：** 2025-10-06 09:07

> 就是美国的中科红旗

### 3. Palantir的产品问题：没有真正的产品

**时间：** 2025-10-06 08:31

Palantir官方数据：
> Until 2016, Palantir had more FDEs (which it called "Deltas") than software engineers. No other company has shaped this role more than the secretive tech company.

马工评论：
> 这是哪门子的软件公司？
> 这不就是中国的金蝶软件么？

**时间：** 2025-10-06 08:40

> 让实施工程师去commit fixes to the platform，估计这帮人根本就没有产品

**时间：** 2025-10-06 08:59

> 这公司从产品看，几乎一无是处。全是对着热门词语造一个自己的轮子
> 业界流行的概念，palantir都能弄一个home made的劣质平台出来
> 难怪要这么多实施工程师

**时间：** 2025-10-06 09:00

Palantir产品描述示例：
> Interactive Digital Twin. Integrate the full range of data and models across the enterprise into a unified, governed, and dynamic representation of the organization. Scale your existing investments and power decision-making for non-technical users in a language they understand.

马工评论：
> 都是废话，说了跟没说一样

### 4. 对Palantir的整体评价

**时间：** 2025-10-06 08:52

> palantir算ai公司的话，老子就是国画艺术家了

**时间：** 2025-10-06 09:01

> 如果川普下台的时候，他的股票还有这么高，我就做空他
> 垃圾公司，美国毒瘤

**时间：** 2025-10-06 02:40

> peter thiel一看就是个恶棍

### 5. FDE在硅谷被过度包装

**时间：** 2025-10-06 09:35

> 最近这个公司向社会输送的人才正在到处吹一个forward deployed engineer岗位，在硅谷造出了声势。我打算打个假

**时间：** 2025-10-06 09:36

> 我在中国云计算打假打了不少南郭先生，去美国ai届试一下能不能弄点声音出来

**时间：** 2025-10-06 08:47

> openai的 fde，就是售前嘛
> 这个概念和中国的中台一样混乱

**时间：** 2025-10-06 10:05

> 中国军工信息化公司又没有把军代表岗位取个backward deployed manager，然后宣传这是世界先进模式

### 6. 与其他人的论战素材

**时间：** 2025-10-06 09:03

> 韭菜怼palantir一无所知，懂的比我还少，天天吹palantir
> 英文韭菜并不比中文韭菜高级

**时间：** 2025-10-06 09:26

> 老哥打开过palantir的网站没

**时间：** 2025-10-06 08:43

> 听起来就像是"我养个一个鸡，一个鸡生十个蛋，十个蛋孵出十个鸡，十个鸡生一百个蛋，一百个蛋孵100个鸡，母鸡吃的草不断沉淀为鸡蛋，鸡蛋又成为鸡仔的宝贵蓝图，如此反复，我就成了世界首富"

**时间：** 2025-10-06 08:44

> 这些没有做过产品管理，也没有干过销售的商业艺术家们真能扯

### 7. 讽刺性建议

**时间：** 2025-10-06 09:57

> 中国政府应该去买点这个公司的股票，把他的神话吹的更大，帮助他垄断整个美军的信息化合同

**时间：** 2025-10-06 09:56

> 别慌，fde会从战场带来一手信息，提升产品质量

---

## Palantir官方对FDE的描述 (用于对比批判)

### 官方定义
> "Deltas (Forward Deployed Software Engineers) deploy our software platforms to customers. Deltas are part of Business Development, and their mandate is to achieve technical outcomes for our customers.

> As part of a team that directly supports one customer, a Delta focuses on technology-driven value creation: deploying and customizing Palantir platforms to tackle critical business problems. They measure success in terms of impact on the customer's goal. For example, we work with manufacturers who want to reduce the number of defective products coming off the assembly line. To move the needle on that metric, a Delta uses Palantir products, a variety of languages, open-source tooling, and industry-standard build tooling, and their own creativity to devise a solution."

### FDE日常工作描述
> "Dyon (Abu Dhabi): Most weeks, I spend a couple of days working at the customer premises, some of that time in meetings with technical or business stakeholders, and the rest of the time monitoring, debugging, deploying, or configuring our software for that customer.

> Back in the office, I spend some time writing minor code changes, reviewing pull requests, and researching/planning customer solutions.

> The remainder of my time is spent communicating via email or VTC with our internal support and product development teams, and with my direct reports who are based in a number of remote offices."

### 另一个FDE的描述
> "G.M. (São Paulo): My 'day-to-day' changes month-to-month, which is a cool feature of my role! Some weeks, I spend most of my time developing and reviewing my team's code, like a typical software engineer. Other weeks, I spend most of my time scoping the future of a project with a client, or working with users to make sure the things we've built meet their needs."

---

## 文章角度建议

1. **揭穿硅谷新概念包装术**：FDE不过是中国早就有的"交付工程师""驻场实施""售后工程师"

2. **政商关系的必要性**：为什么这种模式只能存在于国防等高腐败行业

3. **产品公司 vs 交付公司**：一家FDE比软件工程师还多的"软件公司"

4. **中美对比**：中国的金蝶、中科红旗 vs 美国的Palantir

5. **概念营销批判**：像"中台"一样混乱的FDE概念

---

## 需要补充的数据/事实

⚠️ **重要：以下是需要真实数据支持的点，切勿编造**

1. [ ] Palantir的FDE数量 vs 工程师数量（2016年后的数据）
2. [ ] Palantir的主要客户构成（国防/政府 vs 商业）
3. [ ] Palantir的收入构成
4. [ ] 中国交付工程师的典型薪资和工作模式
5. [ ] 金蝶、用友等中国软件公司的实施团队规模
6. [ ] 硅谷其他公司是否有类似FDE的角色

## 可能的反驳观点

1. "FDE模式让客户得到了定制化服务"
   - 反驳：那为什么不直接做咨询公司？为什么要包装成"软件公司"？

2. "Palantir的技术确实先进"
   - 反驳：从产品描述看全是buzzword，没有实质内容

3. "国防行业就是需要这种深度定制"
   - 反驳：为什么华为、波音等公司不需要这种模式？

4. "FDE能够快速响应客户需求"
   - 反驳：这就是传统的驻场实施，不是什么创新
