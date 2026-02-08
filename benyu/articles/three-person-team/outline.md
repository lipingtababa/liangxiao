# Outline: Product Tri-Ownership：AI原生开发团队的最小可行规模

**定位**：延续黄东旭《Vibe Engineering 2026.1》，补充落地路线图
**目标字数**：灵活，内容完整即可
**核心论点**："头狼"/"产品架构师"模式虽好，但人才稀缺；Product Tri-Ownership把"不可能的超级个体"拆成"三个可培养的专业角色"

---

## 1. 开场：黄东旭的AI原生开发实验（300字）

**黄东旭的成就**：

黄东旭（PingCAP CTO）在《Vibe Engineering 2026.1》中展示了惊人的AI原生开发成果：

- 用AI重构了TiDB的整个Kafka Connector，效果出奇地好
- 一个人+AI完成了以前需要整个团队的工作量

**我的立场**：我基本同意黄东旭的观察。AI确实改变了开发模式，头狼带狼群确实有效。

**但有一个问题**：黄东旭描述的是他自己的实践。**其他公司怎么复制这个模式？**

---

## 2. 现有方案：产品架构师/头狼（300字）

pingcap
- 他的"头狼+狼群"模式：顶级工程师带着一群AI Agents，在自己的领地耕耘
- 90%时间花在验收——人的价值在于评估AI的工作

qiniu cloud 尝试了**产品架构师**的方案——一个人端到端负责产品。

逻辑很简单："如果一定时间内做不到端到端负责，就淘汰，换能做到的人来。"

**产品架构师 = 黄东旭的头狼**：
- 都是一个人端到端负责
- 都需要产品 + 架构 + 工程的综合能力
- 都是"精英路线"

**但精英路线有致命问题**：

产品架构师这个岗位的要求太高了——需要产品经理 + 架构师 + Lead Engineer的能力。在任何工程师社区里，能接近这个定位的人都是凤毛麟角。

- 这种人本来就稀缺，AI没有凭空创造他们
- "做不到就淘汰"——淘汰完了人从哪来？
- 大多数公司的大多数团队，**找不到这样的人**
- 找到了，他们也是one person company

---

## 3. 我的理论：Product Tri-Ownership（800字）- 主菜
 

**核心思路**：既然找不到"超级个体"，就把超级个体的工作拆开

**Product Tri-Ownership的定义**：

```
产品架构师/头狼（一个人做所有事）
        │
        │ 拆分
        ▼
┌───────────────┬───────────────┬───────────────┐
│ Product Owner │ Quality Owner │  Tech Owner   │
│  (产品负责人)  │  (质量负责人)  │  (技术负责人)  │
├───────────────┼───────────────┼───────────────┤
│ owns 做什么    │ owns 什么是对的│ owns 怎么做   │
└───────────────┴───────────────┴───────────────┘
```

---

### 3.1 Product Owner：owns 做什么

**职责**：PRD、用户故事、功能边界、业务价值

**关键洞察**：没有合格的PO做第一层质控，后面的质量链条都会出问题。AI不能替代PO——AI不知道业务该做什么、不该做什么。

**PO的核心职责**：
- 不仅仅是定义"做什么"，也要明确"不做什么"
- 迭代管理，掌握进度节奏
- 连接产品和商业团队
- 协调外部stakeholders

**常见痛点**：
1. 产品经理想偷懒，说"不写PRD了，照着原来写"，导致下游一片混乱。PO必须拥有对"成功标准"的定义权。
2. 模糊的需求不可接受，但可以接受简单的需求，后续迭代完善


---

### 3.2 Quality Owner：owns 什么是对的

**职责**：集成测试框架、验收标准、端到端测试、对抗式验证

**与PO协作定义验收标准**：QO不是被动等PO交活，而是主动参与验收标准的制定。PO说"做什么"，QO说"怎么算做对了"。

- 质量控制是AI原生开发的**关键瓶颈**

**黄东旭自己承认**：
> "我90%的时间和精力都花在了这个阶段：也就是如何评估AI的工作成果"
>
> "There's a test, there's a feature，你只要知道如何评估和测试你要的东西，AI就一定能把东西给你做出来。"
>
> "我在完成大目标前，我一定会先和AI一起做一个方便的**集成测试框架**，并提前准备好测试的基础设施"

**这正是QO的工作！** 黄东旭一个人扛了90%的验收工作，这就是他的瓶颈。铁三角让QO专职负责。

**对抗式测试的必要性**：自己检查自己的工作，总会有懒惰心理——"差不多了，挺好的了"。有一个人专门找茬，专门说"这不行、那不行"——效率反而更高。

**QO的技能要求**：
- QO需要能架构、能写代码——不是传统的手工测试人员
- 设计多层测试体系：单元测试 → 集成测试 → E2E测试
- 搭建测试工具链，与CI/CD集成
- 测试流程要全面、快速、自动化
- E2E测试是核心——这是AI最难自动验证的部分
- 代码review的责任delegate to TO

**角色灵活性**：QO和Tech Owner可以在不同项目中互换角色。两者都需要架构和编码能力，区别在于ownership重心不同。

**NASA IV&V的启示**：挑战者号灾难后，NASA于1993年建立了[独立验证与确认（IV&V）项目](https://www.nasa.gov/ivv-overview/)。核心原则：软件验证必须由**既不是开发者也不是采购方**的独立组织执行。NASA定义了三个维度的独立性：技术独立、管理独立、财务独立。IV&V团队不开发——他们只验证。这和QO的定位完全一致。

**QO设计质量流程，而不是独自承担质量**：

QO的核心工作不是自己做所有测试，而是**设计质量控制流程**，让其他stakeholders参与质量保障：

```
PO owns PRD/Story → Tech Owner review详细设计 → AI写代码 → AI Code Review → Tech Owner看报告 → QO验收
       ↑                    ↑                                      ↑                    ↑
     质控1                质控2                                   质控3               质控4
```

- **质控1（PO）**：需求质量——PRD是否清晰、完整、可验收
- **质控2（Tech Owner）**：设计质量——详细设计是否合理、可实现
- **质控3（Tech Owner）**：实现质量——AI Code Review报告是否显示与设计一致
- **质控4（QO）**：最终验收——E2E测试、集成测试、用户场景验证

**关键洞察**：头狼模式把所有质量压力集中在最后验收（黄东旭说的90%）。Tri-Ownership模式把质量分散到每个环节。QO的价值不是自己验收，而是设计这套让所有人参与的质量流程。

---

### 3.3 Tech Owner：owns 怎么做

**职责**：详细设计、代码review报告（不是代码本身）、架构决策

**最重要的职责：编排多个Agent的工作流**

Tech Owner不只是review设计，更要设计和维护AI Agent的工作流程：

```
标准开发流程
├── story → 生成详细设计
├── tester → TDD红阶段（写失败测试）
├── coder → TDD绿阶段（让测试通过）
├── reviewer → 对抗式Review
├── qc → 质量检查+提交
└── deployer → 部署
```

**不同任务类型需要不同的工作流**：
- Bug fix流程：定位 → 写回归测试 → 修复 → 验证
- 新功能流程：设计 → TDD → Review → 集成测试
- 绿地项目流程：架构设计 → 脚手架 → 模块开发
- 棕地项目流程：理解现有代码 → 增量修改 → 回归测试
- 客户支持流程：复现 → 诊断 → 修复 → 验证
- 基础设施变更：影响分析 → 变更 → 回滚计划
- 数据库迁移：备份 → 迁移脚本 → 验证 → 回滚测试

- 黄东旭承认："Agent通常不会主动去做项目结构和模块边界的治理"
- 黄东旭承认："当前的Coding Agent在面对单一模块复杂度超过大约5万行代码之后，就开始很难在1-shot里把问题一次性解决掉"

Tri-Ownership+编排：自动化工作流，每个Story走同样流程，可重复、不遗漏

**工作方式**：
- Review详细设计文档：验收标准、任务、子任务、代码分层
- 设计通过后，触发开发工作流
- AI写完代码、AI做Code Review后，Tech Owner审核AI的Code Review报告
- AI生成的Code Review发现准确率约80%；通常3-5个问题需要审核——很快就能过完

**这解决了"code review瓶颈"**：不是亲自review代码，而是让AI做第一轮筛查，人只看report。

---

### 3.4 三个Owner如何协作：以天为单位的快速迭代

**传统模式**：需求评审 → 排期 → 开发 → 测试 → 上线，一个功能几周甚至几个月

**Tri-Ownership模式**：以天为单位迭代

```
Day 1 上午：PO写完User Story，QO同步定义验收标准
Day 1 下午：Tech Owner完成详细设计，触发AI开发流程
Day 2 上午：AI完成代码+测试，Tech Owner审核Code Review报告
Day 2 下午：QO执行E2E验收，通过则合并上线
```

**为什么能这么快？**
- PO和QO同时工作，不是串行等待
- Tech Owner review设计而不是代码，AI处理实现细节
- QO提前准备好测试框架，验收不需要临时搭建
- 自动化工作流减少人工交接的等待时间

**关键：三个Owner必须坐在一起**
- 物理上坐在一起，有问题随时讨论，不需要预约会议
- 每日站会不够——迭代速度快意味着决策频率高，等到明天站会就太晚了
- Story级别的交付：不是等一个Sprint结束才交付，而是每个Story完成就验收

**对比传统Scrum**：
- Scrum以Sprint（2周）为交付单位
- Tri-Ownership以Story（1-2天）为交付单位
- AI让实现成本趋近于零，瓶颈变成了人的决策和验收速度

**警惕：传统"最佳实践"成为瓶颈**

很多团队引入AI后速度没有提升，因为传统流程拖后腿：

- **4-eyes code review**：每行代码必须两人审核——当AI一天能写完一个功能，等两个人排期review就要三天。我的CTO都抱怨这个机制拖慢了他自己用AI生成的代码合并
- **Change Advisory Board**：每次上线都要开会审批——AI可以一天部署十次，CAB一周才开一次
- **详细的技术文档**：AI写代码很快，但要求写完整技术文档——文档比代码还费时间
- **测试覆盖率硬指标**：要求90%覆盖率才能合并——AI写的测试可能形式上达标但实际无效

**Tri-Ownership的解决方案**：
- Code review → AI做第一轮筛查，Tech Owner只看报告，不逐行审代码
- CAB → QO的E2E测试通过即可上线，出问题一键回滚
- 技术文档 → 详细设计文档在开发前写，代码本身由AI生成不需要额外文档
- 测试覆盖率 → QO关注E2E场景覆盖，不追求行覆盖率数字

---

## 4. Product Tri-Ownership为什么可行

**组合比寻找更容易**：

找一个产品架构师 → 极难

找三个各自领域的专家 → 可行：
- 好的Product Owner：传统PM转型，学会写清楚需求
- 好的Quality Owner：QA背景，学会构建测试框架和写代码
- 好的Tech Owner：Senior Engineer，学会review设计而不是代码

**培养比筛选更可持续**：
- "做不到就淘汰" → 淘汰完了人从哪来？
- Tri-Ownership：明确每个角色的职责 → 可以针对性培养

**风险分散**：
- 头狼离开 → 项目崩溃（bus factor = 1）
- Tri-Ownership一人离开 → 另外两人可以暂时cover

**建筑行业的验证**：

Product Tri-Ownership不是新发明——建筑行业早就有一个高度对应的成熟模式：

| 建筑角色 | 职责 | 对应Tri-Ownership |
|----------|------|-------------------|
| **Architect（建筑师）** | 理解客户需求、定义功能、空间设计 | **Product Owner** |
| **Civil Engineer（土木工程师）** | 结构设计、技术实现方案、确保安全 | **Tech Owner** |
| **Supervisor（监理）** | 质量监督、验收 | **Quality Owner** |
| Contractor（施工方） | 执行施工 | AI Coder |

根据[Indeed](https://www.indeed.com/career-advice/finding-a-job/architecture-vs-civil-engineering)的解释："Architects are responsible for kicking off the project and creating the initial design ideas"，而"A civil engineer steps in to analyze the design and work out how it can be brought to life"。

**Architect定义"做什么"，Civil Engineer定义"怎么做"，Supervisor验证"对不对"。** 施工方只是执行者——和AI Coder一样。

在中国，重大建筑项目依法必须有独立的[监理](https://chambers.com/articles/international-comparative-legal-guide-construction-engineering-law-2021-china-chapter-ii)负责质量。建筑行业几十年前就发现：设计、施工、验收必须分离。自己设计自己施工自己验收，质量无法保证。AI原生软件开发也不应该例外。

---

## 5. 支撑角色（400字）

**Tri-Ownership之外的支撑角色**：

**Sponsor（决策者）**：
- 当三个Owner之间发生冲突时，做最终决策
- 通常是产品线负责人或技术VP
- 不参与日常工作，只在关键分歧时介入

**Architect（架构师）**：
- 职责：拆分微服务边界，定义系统架构
- 解决方案：Architect预先拆分，让每个模块保持在AI可处理的规模
- 小项目可由Tech Owner兼任

**Platform Engineer（平台工程师）**：
- 职责：构建AI可调用的CI/CD pipeline
- 黄东旭说"唯一瓶颈是人工code review和无法自动化的线上运维"
- 如果CI/CD不是AI-ready的，AI写完代码还要人工部署
- Platform Engineer的产出：AI可调用的测试pipeline、自动化部署、一键回滚


**Specialty Expert（领域专家）**：

按需咨询，不参与日常开发：

- **UX Designer**：新开一个面向C端的产品线，需要从零设计用户流程
- **Hardware Engineer**：银行项目需要对接加密机、U盾等硬件设备
- **Security + Legal/Compliance**：Fintech项目上线前的安全审计和金融牌照合规审查
- **DBA**：系统从MySQL迁移到TiDB，需要评估兼容性和性能影响
---

## 6. 另一种方法：培训模式（300字）

**不是所有公司都能重组团队结构**。一个更温和的替代方案：

**培训模式的特点**：
- 不动组织结构
- 高手定制skills/agents/workflows
- 实施团队按流程执行
- 用便宜的模型降低成本门槛
- 硬推（强制执行）

**优点**：门槛低，不需要组织变革
**缺点**：没有触及ownership问题——谁为PRD质量负责？
---

## 7. 结尾：三条路线的选择（200字）

**总结**：

| 路线 | 方法 | 适用 |
|------|------|------|
| 精英路线 | 找超级个体 | 有顶尖人才的团队 |
| 中间路线 | Tri-Ownership——重组ownership | 愿意变革的团队 |
| 温和路线 | 定制工具+硬推 | 暂时无法变革的团队 |

**核心观点**：

AI时代的核心问题，是**在AI agent极大地降低成本之后，如何系统性地构建人机协作团队，以可持续的方式保证交付质量，并且将生产力的提升转换为市场竞争力**。

Product Tri-Ownership的价值：提供一个可复制的框架，把"不可能的超级个体"拆成"三个可培养的专业角色"，让普通团队也能实现AI原生开发。

**讨论邀请**：

你们公司的AI原生团队是什么结构？遇到了什么问题？欢迎留言讨论。

---

## 引用来源

- 黄东旭《Vibe Engineering 2026.1》：https://www.infoq.cn/article/k05gRzGFhz4QerCz4ARl
- NASA IV&V Program: https://www.nasa.gov/ivv-overview/
- Architecture vs Civil Engineering: https://www.indeed.com/career-advice/finding-a-job/architecture-vs-civil-engineering
- China Construction Supervision Law: https://chambers.com/articles/international-comparative-legal-guide-construction-engineering-law-2021-china-chapter-ii

---

## Checklist

- [x] 字数灵活，内容完整即可
- [x] 7个section，逻辑递进
- [x] 核心论点清晰：Product Tri-Ownership is the path suitable for most companies
- [x] 独特角度：人才稀缺问题
- [x] 跨行业验证（建筑行业 Architect-Engineer-Supervisor）
- [x] 框架清晰，可翻译成英文
- [x] 结尾有讨论邀请
