# 你又写Bug了 - Brainstorm Materials

> 来源：AI Coding 群聊
> 日期：2026-01-28

---

## 素材来源

### 图片素材
1. **马工与Marcus合影** - `IMG_20260128_095828.jpg`
   - 办公室场景，两人在工位前合影
   - Marcus竖起大拇指，背后是代码编辑器
   - 背景：Marcus是那个耐心review 69文件PR的"geek"

2. **微信群聊截图** (两张，在对话中提供)
   - 截图1：核心bug故事 (09:57-13:06)
   - 截图2：工作流背景 (13:07-16:28)

### 文字素材
- `chat.md` - 完整对话整理

---

## 核心故事：人类干预 = Bug

### 事件经过

**背景**：马工提交了一个大PR
- 6996行新增代码
- 487行删除
- 修改67个文件
- 涉及3个模块

**Marcus的Code Review**：
> "每次我在slack群里发一个69个文件的大pr，然后看到有人掉了一个look的emoji，我就知道一定是Marcus，只有他这个geek才有耐心读这么多代码"

**发现的两个"问题"**：
1. Log了敏感信息
2. DB migration放在同一个文件而不是一系列文件

### 讽刺的反转

**关键事实**：这两个"问题"都是Claude Code在马工的明确请求下做的！

原因：
- 项目尚未商业上线
- 数据不重要
- 当时就这样处理了

**马工的反思**：
> "也就是说，我的ai agents写出来的代码，已经超越了我的水准。"
>
> "我的直接干涉，其实拉低了代码水平。"

**结论**：
> "两个主要的bug，是我人工干预的结果"

### 群友反应

**linhow**：
> "哈哈哈哈，好像你故意做局，埋了两个bug"

**刘九**：
> "用的claude吗"

**林秋楠Dylan** (绝妙的标题素材)：
> "AI：你怎么又来写BUG"

---

## 大铭的Anti-Micromanagement哲学

> "我要控制自己micro manage的冲动，不要干涉ai agent写代码，而应该着力于培养ai agents的能力"

马工的案例完美验证了这个观点：
- 放手让AI工作 → 高质量代码
- 人类直接干预 → 引入bug

---

## 工作流背景

### 马工的AI Coding设置

> "是claude code，但不是vanilla claude code，我分了角色，设置了一套流程"

**银行集成目标**：
> "我的目标就是集成银行。工作其实很机械化，重要的foundation已经打好了，接下来就是读api，配置新集成银行，然后run测试"
>
> "这个事，人来做的话，非常无聊而且容易出错。AI很合适"

**自定义Orchestrator**：
- `/integrate` slash command作为orchestrator
- 调用planner subagent：阅读银行API，选择auth flow，制定对接计划
- 调用tester和coder subagent：写代码
- tester和coder是项目无关的，只是语言specific

**核心理念**：
> "我的意思不是说bmad不好，而且说每个人都可以定制一套流程+自己的subagent+orchestrator"

---

## 文章角度选项

### 角度1："AI：你怎么又来写BUG"
- 角色反转的喜剧效果
- AI"指责"人类写bug
- 标题来自林秋楠Dylan的金句

### 角度2：Anti-Micromanagement
- 大铭哲学的实践验证
- 培养AI能力 vs 直接干预
- 管理学视角

### 角度3：Trust the Agent
- 什么时候应该override AI
- 什么时候应该放手
- 信任边界的探讨

### 角度4：The New Code Review
- Marcus review AI代码
- 反而发现人类的bug
- 代码审查的新常态

### 角度5：Workflow Design > Direct Coding
- 设计流程比直接写代码更重要
- orchestrator + subagent架构
- 从coder到architect的转变

---

## 金句摘录

### 关于AI代码质量
> "我的ai agents写出来的代码，已经超越了我的水准。"

### 关于人类干预
> "我的直接干涉，其实拉低了代码水平。"
>
> "两个主要的bug，是我人工干预的结果"

### 关于管理哲学
> "我要控制自己micro manage的冲动，不要干涉ai agent写代码，而应该着力于培养ai agents的能力"

### 关于工作流
> "每个人都可以定制一套流程+自己的subagent+orchestrator"
>
> "这个事，人来做的话，非常无聊而且容易出错。AI很合适"

### 群友金句
> "哈哈哈哈，好像你故意做局，埋了两个bug" — linhow
>
> "AI：你怎么又来写BUG" — 林秋楠Dylan

---

## 数据点

| 指标 | 数值 |
|------|------|
| PR新增代码 | 6996行 |
| PR删除代码 | 487行 |
| 修改文件数 | 67个 |
| 涉及模块 | 3个 |
| 发现的问题 | 2个 |
| 人类干预导致的问题 | 2个 (100%) |
| AI自主导致的问题 | 0个 (0%) |

---

## 下一步

- [ ] 确定文章角度
- [ ] 撰写outline
- [ ] 完成draft
