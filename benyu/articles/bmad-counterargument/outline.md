# Outline: BMAD是AI编程从手艺走向工程的第一步

## 模板：驳斥（Debunking）— 永动机模式

## 核心论点
工程和手艺的分水岭，在于产出的可靠性是否依赖从业者的天赋。BMAD是AI编程从手艺走向工程的第一步。

## 标题
BMAD是AI编程从手艺走向工程的第一步

## 读者焦虑
AI编程高手们担心流程会拖慢自己。但真正的焦虑是：如果流程比直觉更可靠，那"高手"的护城河在哪里？

## 骨架：Shaw的手艺→工程三阶段

全文用Shaw的三阶段模型（手艺→商业→专业工程）作为主线。每一段回答主线上的一个问题：

1. AI编程现在处于什么阶段？→ **手艺阶段**（开场）
2. 手艺阶段有什么问题？→ **直觉是噪音源，专家更甚**（Kahneman + Gawande）
3. 从手艺到工程的分水岭是什么？→ **编纂**（化学工程 unit operations）
4. BMAD是不是编纂？→ **拆开看机制**（层级约束级联 + 质量门）
5. 结尾：回扣Shaw

## 结构

### 1. 开场：AI编程还在手艺阶段
- 群聊引入：大年初三的BMAD辩论，反对方最强音——"我不需要流程"
- 这句话换个说法就是：我的经验和直觉足够好，流程只会拖慢我
- 反对者全是高水平开发者（胥克谦和马工都有20年研发经验）
- Mary Shaw（CMU）研究了土木工程和化学工程的演化史，提出三阶段模型：手艺→商业→专业工程
- 手艺阶段的标志：产出质量取决于从业者的天赋，知识靠师傅带徒弟传递，不可复制
- "我不需要流程"是手艺人宣言。AI编程今天就在手艺阶段。

### 2. 手艺的问题：你的直觉是噪音源
- Kahneman，1955年，21岁，以色列国防军，改革面试流程
- 非结构化面试的预测效度只有0.20，结构化是它的3倍
- 更致命的发现（Kausel et al.）：给面试官客观数据后，再加上非结构化判断，预测反而变差。专家直觉不是中性的，是有毒的。
- 面试官恨这个改革，觉得被剥夺了判断力。以色列军队用了这套系统68年。
- 不止面试。Gawande：手术安全清单降低死亡率超过1/3，受益最大的是资深外科医生，不是新手。
- Gawande区分两种错误：无知之错（不知道怎么做）和无能之错（知道怎么做但没做到）。专家的主要问题是后者。
- 陈明的实证："第一次用bmad就发现了架构师的局限，这个局限从业很多年一直没意识到"
- 手艺阶段的根本问题：做好了不知道为什么好，做砸了不知道为什么砸。直觉不可审计。

### 3. 分水岭：编纂
- Shaw的结论：从手艺到工程的分水岭是知识的编纂（codification）——把个人经验变成可复制的规范
- Shaw的原型案例：化学工程。1915年之前没有"化学工程师"，只有"制碱的人"、"炼油的人"，知识不可迁移。Arthur D. Little提出unit operations，把千行百业的化工经验编纂成通用基本操作（蒸馏、过滤、结晶...），写成教科书。从此你不需要跟师傅十年才能炼油。
- 编纂不是说师傅的经验没用。编纂是说：经验必须被结构化、可传授、可审计，才能成为工程。
- Deming："85%的失败是系统和流程的缺陷，不是员工的问题"。把质量归咎于个人天赋，是手艺思维；把质量归因于系统，是工程思维。
- 定义：当一个领域的可靠性不再取决于从业者的天赋，而取决于流程和规范的质量时，这个领域就从手艺变成了工程。

### 4. BMAD是编纂
- BMAD的四阶段：Analysis → Planning → Solutioning → Implementation
- 每个阶段产出带版本号的约束文档：brainstorming-report → PRD（带唯一ID如FR-01） → architecture.md（含ADR） → epic/story文件
- 层级约束级联：每一层的输出成为下一层的binding spec。PRD约束架构，架构约束story，story约束实现。你不能跳过PRD直接画架构，就像Kahneman不允许面试官跳过维度评分直接给全局印象。
- Implementation Readiness Gate = 延迟全局判断：所有维度评判完毕后，才做"能不能开始写代码"的全局决策。PASS/CONCERNS/FAIL。
- TEA（adversarial review）：独立于开发者的质量审查，问题分级Blocker/Major/Minor。这是编纂的质量保障机制。
- 前一篇文章说BMAD是"Scrum还魂"——但Scrum的角色分工解决的是人际政治问题。BMAD的agent链条是Kahneman结构化决策的工程化变体，是编纂，不是仪式。
- 前一篇文章说"用抗生素治骨折"——但BMAD治的不是感染也不是骨折，治的是噪音。

### 5. 结尾
- 回扣Shaw：化学工程从手艺到工程用了一代人，软件工程从1990年Shaw写论文到今天还没完成这个转变
- AI编程让这个问题更紧迫：LLM放大了手艺阶段的所有问题（不可审计、不可复制、质量靠运气）
- BMAD不完美——但它的方向是编纂，编纂是从手艺到工程的唯一道路
- 反对者看到的成本是真实的。但编纂的成本永远低于不编纂的代价。化学工程师不会说"unit operations太麻烦了，我还是跟师傅学吧"
- 邀请讨论

## 论证骨架
Shaw三阶段是主线（贯穿1-3-4-5）：
- 第1段：定义手艺阶段（AI编程现状）
- 第3段：定义分水岭（编纂）+ 化学工程案例
- 第4段：BMAD是编纂的具体实现
- 第5段：回扣，编纂是唯一道路

Kahneman + Gawande合体（第2段）：
- Kahneman：直觉是噪音源（理论）
- Gawande：清单降低死亡率，受益最大的是专家（实证）
- 陈明：BMAD发现架构师盲区（AI编程实例）

## 引用来源
- Mary Shaw, "Prospects for an Engineering Discipline of Software" (1990), IEEE Software
- Arthur D. Little, "Unit Operations" (1915), 化学工程编纂的起点
- Daniel Kahneman,《Noise: A Flaw in Human Judgment》(2021)
- Kausel et al., "Overconfidence in personnel selection", Organizational Behavior and Human Decision Processes
- Atul Gawande,《The Checklist Manifesto》
- W. Edwards Deming, quality management principles
- Nathan & Petrosino (2003), Expert Blind Spot, American Educational Research Journal
- BMAD-METHOD: https://github.com/bmad-code-org/BMAD-METHOD
- 群聊讨论原始素材（AI_Coding 群 2026-02-19）
