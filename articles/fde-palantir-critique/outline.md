# Article Outline: Forward Deployed Engineer —— 硅谷版"交付工程师"

**文章类型**: Debunking + Industry Critique (永动机模式 + 云厂商深度分析模式)

**核心论点**: Forward Deployed Engineer不过是中国早就有的"交付工程师"/"驻场实施"的硅谷包装版，只能在高腐败的国防行业生存，现在正以800%的速度传播到AI行业 —— 这是下一个"中台"式的buzzword泡沫。

---

## 一、开场：FDE热潮观察

**Hook - 具体现象引入**
- 2025年FDE岗位激增800%
- OpenAI计划招50个FDE，Anthropic、Databricks、Google DeepMind全在招
- 硅谷把FDE吹成"AI时代最热门职位"
- 我的第一反应："这不就是我们中国10年前的'交付工程师'吗?"

**设置悬念**
- 为什么一个老掉牙的角色突然成了硅谷"创新"？
- 为什么Palantir的CFO自己都说这是"lighting equity on fire"？
- 为什么这个模式能拿到CIA的钱，却在NHS惨败？

---

## 二、FDE是什么？—— 皇帝的新衣

**Palantir官方描述 (blockquote)**
- "Forward Deployed Software Engineers deploy our software platforms to customers"
- "Part of Business Development"
- "Embed with customers, customize platforms, achieve business outcomes"
- 工作日常：客户现场2-3天/周，debugging, deploying, configuring

**翻译成中文就是**
- 交付工程师
- 驻场实施
- 售后工程师
- 技术售前/售后

**对比中国ERP行业**
- 金蝶、用友的实施顾问
- 通过合作伙伴网络提供实施服务
- 但他们不会把"ERP实施顾问"包装成"革命性创新岗位"

**核心质疑**
- 如果你的"软件平台"需要permanent on-site engineers，你真的有产品吗？
- The Spreadsheet Test: Excel不需要微软派工程师驻场3天/周才能用

---

## 三、数据说话：Palantir的真实面目

**3.1 人员构成的秘密**
- 历史事实：2016年前，FDE数量 > 软件工程师数量
- "哪门子的软件公司？"
- 现在：不再公开FDE比例（suspicious）
- 总员工3,936，工程44% (1,383人)

**3.2 收入依赖政府**
- 2024年收入$2.9B
- 政府：55% ($1.57B)
- 商业：45% ($1.30B)
- **趋势**: 政府收入从46.5% → 55% (2019-2024)
- 越来越依赖政府合同，不是越来越商业化

**3.3 薪资的真相**
- FDSE中位数: $221K
- 普通SWE: $195K
- **只高13%**，但要承受：
  - 每周3-4天客户现场
  - 大量差旅
  - "Bad work-life balance"
  - "Jungle combat" quick-and-dirty code

**3.4 自己人都看不下去**
- 前CFO Colin Anderson: "lighting equity on fire"
- "Spectacular pyres of time and treasure and travel expenses that amounted to nothing"
- "Overlapping and wasted work, multiple teams on similar problems"
- 开发被形容为"jungle combat"

---

## 四、为什么FDE只能在高腐败行业生存？

**4.1 国防行业的revolving door**
- 2022年：672个Pentagon官员加入防务承包商
- 前Joint Chiefs主席 → Lockheed Martin董事会（退休5个月后）
- 利润率40-50%（国防部自己的审计）
- Operation Illwind: 美国历史上最大的国防采购腐败案

**4.2 Palantir的政商一体模式**
- 2003年成立，传统VC拒绝投资
- **In-Q-Tel (CIA的VC arm)** 成为早期投资人
- 情报机构帮助设计产品（3年collaboration）
- CIA、FBI、NSA成为客户
- 完美闭环：CIA出钱 → CIA设计 → CIA采购

**4.3 华为/中石油 Test**
Blockquote用户原话:
> "中国最强关系华为公司，也不能对着中石油说'我他妈的也不知道能给你做什么，我先派个fde入场，查看你的数据，占用你的时间，然后做个mvp给你看看，你到时候再决定。当然，你第一天就要付费'。这不神经病么"

**解释为什么这在正常市场行不通**
- 甲方要明确的交付物
- 甲方要可比较的报价
- 甲方要能更换供应商
- FDE模式 = lock-in by design

---

## 五、当FDE遇到真实世界：NHS惨案

**5.1 合同规模**
- £330 million，7年
- 英国NHS全国数据平台

**5.2 实际采用率**
- 只有25%的医院真正使用
- 很多医院拒绝，称其为"step backwards on existing systems"

**5.3 透明度问题**
- 586页合同，416页被redacted
- 数据保护条款"subject to commercial negotiation"
- 患者无法opt-out

**5.4 教训**
- 有政治关系能拿合同
- 但产品垃圾还是垃圾
- FDE模式在透明市场失效

---

## 六、"中台"的美国孪生兄弟

**6.1 中台的兴衰**
- 2015: Alibaba推出"中台"概念
- 2015-2020: 所有大厂跟进（Tencent, ByteDance, JD, Meituan）
- 行业口号："不做中台就死"
- Gartner 2020: "Peak of Inflated Expectations"
- 2023: **Alibaba自己放弃中台战略**

**6.2 两者的惊人相似**

| 特征 | 中台 (Zhongtai) | FDE |
|------|-----------------|-----|
| 定义清晰度 | "我们都没有清晰定义" | "这个概念和中台一样混乱"(用户原话) |
| 推广者 | Alibaba | Palantir |
| 传播速度 | 所有大厂5年内跟进 | 800%增长(2025) |
| 最终结果 | 推广者自己放弃 | CFO批评"lighting equity on fire" |
| Hype Cycle | Peak → 幻灭 | 正在Peak |

**6.3 Backward Deployed Manager**
Blockquote用户讽刺:
> "中国军工信息化公司又没有把军代表岗位取个backward deployed manager，然后宣传这是世界先进模式"

**寓意**: 每个行业都有on-site角色，只在hype-driven环境才会被rebranded为"革命"

---

## 七、产品 vs. 咨询公司：The Spreadsheet Test

**7.1 什么是软件产品？**
- Kingdee/UFIDA: SaaS模式，partner实施
- Microsoft Office: 客户自己使用
- Salesforce: 客户IT自己部署
- AWS: Self-service + documentation

**7.2 Palantir的"产品"**
- 需要permanent embedded engineers
- 客户"become dependent on company's employees"（行业报告原话）
- FDEs直接commit fixes to platform
- 每个客户可能是不同的fork？

**7.3 The Spreadsheet Analogy**
> "如果我卖你Excel，你能用。如果我卖你'Excel Platform'但你需要我的工程师on-site 3天/周才能做表格，我没有产品 —— 我有个非常贵的表格顾问服务。"

**7.4 传统防务承包商对比**
- Lockheed Martin卖F-35：交付后能飞
- Boeing卖787：交付后能用
- Raytheon卖导弹系统：安装后能操作
- Palantir卖"平台"：**需要permanent staff才能运行**

**本质区别**
- 硬件公司：卖产品
- Palantir：租工程师 + 附带一个GitHub repo

---

## 八、FDE病毒正在传播

**8.1 AI公司集体跟风**
- OpenAI: 2025年目标50个FDE
- Anthropic: Applied AI Engineers，计划5倍增长
- "Prove the business case"（这不就是售前吗？）
- ElevenLabs, Databricks, Salesforce全在招

**8.2 两种可能的解释**

**乐观解释**:
- FDE模式真的有效
- AI产品确实需要这种深度定制
- Palantir pioneered a valid model

**悲观解释 (我的观点)**:
- AI行业正在重复中台的错误
- 把老旧的交付模式包装成"创新"
- 800%增长 = groupthink，不是validation
- 3-5年后会像中台一样幻灭

**8.3 如果FDE真的有效...**
- 为什么Palantir自己的CFO批评它？
- 为什么NHS采用率只有25%？
- 为什么需要如此高的政府关系才能生存？

---

## 九、我见过这个电影：打假启示

**9.1 我在中国云计算的打假经验**
Blockquote用户原话:
> "我在中国云计算打假打了不少南郭先生，去美国ai届试一下能不能弄点声音出来"

**9.2 南郭先生的共同特征**
- 概念模糊，定义不清
- 大厂背书，声势浩大
- 理论上听起来很美
- 实践中问题重重
- 最终：推广者自己放弃

**9.3 FDE完美符合这个模式**
- ✅ 概念模糊（"和中台一样混乱"）
- ✅ Palantir背书，OpenAI跟进
- ✅ 理论上："embedded innovation", "customer intimacy"
- ✅ 实践中：CFO说烧钱，NHS失败
- ⏳ 等待：硅谷是否会像Alibaba放弃中台一样放弃FDE？

---

## 十、结论：美国的中科红旗

**10.1 中科红旗的教训**
Blockquote用户类比:
> "就是美国的中科红旗"

- 产品页挂国旗
- 靠政府关系生存
- 技术平平
- 最终：政策风向变了就完蛋

**10.2 Palantir的未来**
- Trump政府时期：如鱼得水
- 如果政治风向变化？
- Stock price: 用户原话 "如果川普下台的时候，他的股票还有这么高，我就做空他"

**10.3 给AI行业的警告**
- 别被"Forward Deployed"这种fancy名字迷惑
- 这就是交付工程师，不是什么创新
- 如果你的产品离不开permanent on-site team，你没有scalable business
- 800%的增长可能是集体幻觉，参考中台

**10.4 两条路**

**给AI公司（OpenAI/Anthropic）**:
- 要么真正productize（像Kingdee那样用partner网络）
- 要么承认你们是高端咨询公司，不是产品公司
- 别学Palantir走国防承包商的路

**给Palantir**:
- 继续做美国的金蝶 + 中科红旗
- 但别指望正常市场接受这套
- NHS已经证明：透明市场不吃这套

---

## 十一、收尾：邀请讨论

**11.1 承认局限**
> "我有一个不太全面但是可能很核心的观察："
- 我没在Palantir工作过
- 我没做过FDE
- 但我见过太多次这种模式 —— 在中国云计算，在中台，在各种buzzword

**11.2 开放问题**
- FDE是否会像中台一样5年内衰落？
- AI公司能否找到比FDE更scalable的模式？
- 正常市场（非国防）是否能接受permanent embedded engineers？

**11.3 Call to action**
> "作为见证过中国云计算和中台兴衰的老兵，我对FDE持深度怀疑。有在Palantir或OpenAI做FDE的朋友，欢迎在评论区打脸。有认同我观点的同好，欢迎转发，让更多人看穿这个硅谷版'交付工程师'的真面目。"

**最后一击（Provocative ending）**:
> "换句话说，Forward Deployed Engineer是胡扯，Delivery Engineer倒可能是朴实真理。只不过后者拿不到VC的钱，也上不了LinkedIn的热门职位榜。"

---

## 文章关键元素 Checklist

**Specificity**
- [x] 公司: Palantir, OpenAI, Anthropic, Kingdee, UFIDA, 中科红旗
- [x] 人物: Peter Thiel, Colin Anderson (CFO)
- [x] 数字: 800%, $2.9B, 55% govt, 672 Pentagon officials, £330M, 25% adoption, 13% salary premium
- [x] URLs: [需要补充GitHub links, 如果有的话]

**Theory + Practice**
- [x] 理论: 产品 vs. 咨询, Spreadsheet Test, Lock-in economics
- [x] 实践: NHS failure, 中台 rise and fall, Defense revolving door

**Analogies**
- [x] 交付工程师 vs. FDE
- [x] 中台 vs. FDE (完美parallel)
- [x] Spreadsheet Test
- [x] 中科红旗 vs. Palantir
- [x] Backward Deployed Manager (讽刺)

**Voice**
- [x] 第一人称："我见过这个电影"
- [x] 用户原话 blockquotes
- [x] 讽刺："哪门子的软件公司？"
- [x] Rhetorical questions

**Engagement**
- [x] 开放性问题
- [x] 邀请打脸
- [x] Provocative conclusion

---

## 需要用户确认/补充的数据

⚠️ **以下内容需要真实数据，切勿编造**

1. [ ] 是否有任何GitHub项目作为对比案例？
2. [ ] 是否有实际接触过Palantir或其客户的经验？
3. [ ] 是否有中国交付工程师的具体薪资/工作模式数据？
4. [ ] 是否有Kingdee/UFIDA实施团队规模的公开数据？

**如无法获取，使用placeholder**:
- [需要数据: 中国ERP实施顾问典型比例]
- [需要案例: 如有实际交付工程师朋友的经验]

---

**预计字数**: 4000-5000字
**预计阅读时间**: 12-15分钟
**文章调性**: 批判但fact-based，讽刺但constructive
