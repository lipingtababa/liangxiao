# WeChat Chat Summary - 2026-01-17

## Section 1: 马工's Brainstorm Material

Your own messages from today, organized by theme. These are your raw thoughts worth revisiting for article ideas.

### AI Coding Workflow & Limitations

**AI troubleshooting requires human-AI collaboration:**
> 如果你只给AI说"给我搞定这个问题"，那肯定行不通。我看sonnet 4.5像个傻逼一样，opus 4.5也没好很多。但是如果你和它两个并肩作战，互相补充，就能搞定

**Sonnet's logical failures - a concrete example:**
> sonnet真的太傻逼了。比如最开始chatlog会长时间占用cpu 300+%，这是它在遍历一个巨大的列表查找正确的key。sonnet就修改代码，只遍历列表最前面50个。我说"如果正确的key在前50个里，那么你改不改代码，所需要的时间都是一样的。如果正确的key不在前50个，那么你退出就必然失败，所以你的修改没有意义"

### AI Adoption Funnel Model

**Seven stages of AI adoption:**
> 漏斗模型
> 1. 不愿意接触新事物
> 2. 接触新事物，然后说"这不就是我十五年前做的XYZ换个皮吗？"
> 3. 认识到新事物得不一样，但是"太麻烦了，还不如我古法方便"
> 4. 找到了不麻烦的方法，但是停留在问问chatgpt的程度
> 5. 收集各种秘诀，试图找个提升AI水平的葵花宝典
> 6. 发现没有葵花宝典，自己动手总结经验
> 7. 发表经验，接受挑战，不停的迭代经验

### Software Testing in AI Era

**Testing engineer as the new protagonist:**
> 我在去年六月份就相信测试工程师会取代开发工程师成为ai为中心的软件工程的主角，但是那时候我只有直觉。六个月过去了，我已经有项目经验支撑这个论断了，所以我积极的探索

**Seeking updated testing frameworks:**
> 我需要的是一个比较up to date的软件工程师测试课本，这个课本覆盖了当前软件工程行业所总结的实践经验，good practice and bad practice。这样我就比较少走弯路，而不用靠着自己那三杆枪在河里摸石头

**Old testing knowledge obsoleted:**
> 工业届很多测试课本，花了大量的篇幅讲述测试团队的组织架构，测试团队的文化建设，质量意识的灌输。而这些经验在ai agent时代都失效了，我的ai developer不需要我去厕所里贴纸条说服他们测试很重要。测试总监或者qa vp也不再需要了。今天还有效的测试知识应该是关于软件本身特性的。

**Cost structure shift in testing:**
> 几乎所有工程问题都可以换成造价问题。传统的软件工程中，人力成本是最高的一部分，而其他部分相对较低，因此软件测试会以节省人力为目标。AI Testing把人力成本急剧的降低了，那么其他成本就会成为新的bottleneck。

**Mock bank case study - "reckless" investment now possible:**
> 为了测试我和银行的集成，我直接写了个mock bank，模拟瑞典所有银行的api，然后用这个mock银行来测试我的系统。如果没有AI，这个mock银行的开发成本是不可接受的，我老板会坚决的拒绝我的提议。但是有了AI，我招呼都不用打，就直接开干了。

**Nested testing paradox:**
> 为了开发这个mock，我也写了一些测试代码来测试它。所以我这么一个项目：集成银行的aisp是目标 → 为了测试aisp，写了个mock bank → 为了测试mock bank，又写了测试代码。这种不顾成本的做法，在pre-ai的时代，会被公司直接开除

**Questioning unit testing's value:**
> 我对单元测试的重要性有点怀疑。我的理论是，单元测试是为了保护函数这种小单元的，而ai coding时代，我们几乎不重用函数，直接都重写了。如果需要修改20处引用，那就直接grep全给它改了。那么单元测试的保护也就没有很多价值了。

### Industry Observations

**Product managers as obsolete as 2008 Gome trainees:**
> 都是过去式了，现在的互联网产品经理相当于2008年的国美门店管培生，确实是懂很多零售业知识，但是京东淘宝不需要这批人了

**Mobile internet strengthened monopolies:**
> 移动互联网没有这种奇迹，在移动互联网时代，巨头的垄断被加强了。互联网时代有这种奇迹，因为早期从业者并没有认识到互联网的革命性。移动互联网还没开始，马化腾就定下来要拿一张船票，马云也all in移动互联网

**Zhu Xiaohu's insights:**
> 朱小虎有几个说法：
> - 现在的大模型已经足够用了，几十亿美元进一步开发最先进的sota然后六个月之后被人赶上，不太划算
> - Anthropic的api生意很糟糕，用户毫无忠诚度，你失去技术领先就会失去用户
> - ai只会让大公司更大，小公司很难超越他们，只能在大公司的缝隙里寻找生存空间

### Misc Observations

**Sales jobs being replaced:**
> https://www.youtube.com/watch?v=I-R1bc1rlFs 销售的初级岗位也被替代了

**Silicon Valley title inflation - everyone is "engineer":**
> 为什么硅谷现在这些头衔都是engineer？sales engineer，gotomarket engineer

---

## Section 2: AI Coding Chatroom Summary

**Date:** 2026-01-17 | **Messages:** 213 total, 196 text

### Key Discussions

#### 1. "抽卡师" - AI's New Job Category
GPT raised an interesting observation about the AI comic/video industry creating new job roles:
- **抽卡师 (Card Puller)**: Workers who use AI models to generate images/videos from scripts, selecting the best outputs
- **Process**: Script → AI generates multiple images → Human selects best → AI generates video → Human selects best → Next stage
- Analogy to coders: "抽卡师他面对的模型在抽图片或视频。那跟程序员面对CC来抽task任务的程序，来抽用户故事的程序，来抽PRD的程序，有什么区别呢"
- 胥克谦 revealed he's an expert in this - his old motto was "三分钟做部动画片"

#### 2. AI Adoption Reality Check
崔富泽 attended a Trae (字节) event in Shijiazhuang:
- People still asking about AI pricing concerns
- One full-stack developer said "AI coding is still in early stage"
- 崔富泽's response: "老哥，现在已经有大厂的技术佬们2小时干完半个月的工作排期了"
- Observation: "本群的常识随意拿出来一个，就是群外的顿悟"

#### 3. DeepSeek Impact on Employment
- DeepSeek's capability improvements are "利空" for workers because "几乎所有老板都知道deepseek"
- When bosses learn DeepSeek can do more at lower cost...

#### 4. AI Tool Limitations
- Windows support for AI coding tools is generally poor
- WSL is a common workaround
- Ubuntu recommended for better compatibility

#### 5. Hardware Discussion
胥克谦 shared AMD setup experience:
- 5000 RMB machine, performance comparable to M3 Max
- Running 10+ parallel AI tasks
- Memory prices "涨疯了" - regrets not getting 128GB

#### 6. Investment Perspective (Zhu Xiaohu Video)
马工 shared Zhu Xiaohu video with key points:
- Current large models are "good enough" - spending billions for SOTA that gets caught up in 6 months isn't worth it
- Anthropic's API business is terrible - zero user loyalty
- AI will make big companies bigger; small companies can only survive in the gaps

---

## Section 3: 构建之法 Chatroom Summary

**Date:** 2026-01-17 | **Messages:** 109 total, 87 text

### Key Discussions

#### 1. Product Managers Discussion (网易)
Deep dive into NetEase product history:
- Discussion of 纯银 (Chunyin/郭子威) - early NetEase PM, created 网易云相册
- 汪源 vs 纯银 debate - 汪源 now recruiting devs at 1万/month (was 3万 a year ago)
- Lofter described as "Web 2.0时代产品经理群体的心中的圣杯"
- 网易云音乐 as "移动互联网时代的圣杯"

**马工's sharp take:**
> 都是过去式了，现在的互联网产品经理相当于2008年的国美门店管培生，确实是懂很多零售业知识，但是京东淘宝不需要这批人了

#### 2. Mobile Internet "Miracles" Debate
郑昀 listed 2013-2017 mobile miracles:
- WhatsApp (55 people → $19B acquisition)
- ByteDance (30 people → $480B)
- Kuaishou, Snapchat, Supercell...

**马工's counter-argument:**
- "移动互联网没有这种奇迹，巨头的垄断被加强了"
- "大公司内部的移动互联网迁移成功案例更多，比如微信，支付宝，携程，qq音乐，百度地图"
- Only ByteDance qualifies as a mobile internet miracle

#### 3. Software Testing Theory (Extended Discussion)
xinz (邹欣) responded to 马工's earlier request for testing theory:

**xinz's framework:**
> 对复杂软件，我们或许无法用数学完备地"证明"一个百万行代码的自动驾驶控制系统绝对正确，但我们可以通过V&V的方法：
> - 需求的双向追溯
> - 覆盖度分析（语句覆盖、分支覆盖、MC/DC覆盖）
> - 故障注入与安全分析（FMEA，FTA）
> - 在环仿真与实景测试（HIL，SIL，VIL，实车路测）

**马工's response:**
- IV&V theory → actively seeking QC engineer to avoid "自己+AI测试自己+AI"
- SQLite test:code ratio is 400:1, his is not even 1:1 → "测试上的投资还是太少了"
- Cost structure shift: AI lowers human cost → other costs become new bottleneck
- Concrete case: Built mock bank to test Swedish banking integration - "pre-AI时代会被公司直接开除"

**Unit testing skepticism:**
> 我的理论是，单元测试是为了保护函数这种小单元的，而ai coding时代，我们几乎不重用函数，直接都重写了。

---

## Section 4: Other Chatrooms Summary

Only 2 other chatrooms had Jan 17 data with minimal relevant content.

### 星尘洞见-ai编程1群 (3 messages)
One interesting point:
> AI一样可以给出架构方案，而且很靠谱

### AI编程经验分享交流 (27 messages)
- Gemini usage stats shared (gemini-3-pro-preview, gemini-3-flash-preview)
- Recommendation to "固定成3-pro就完事了，3flash快虽快，但还是稍微差点"
- Warning about enabling conversation history: "千万不要开对话记录，感觉往里面塞了一堆不知道啥的玩意儿进去"

---

## Article Ideas from Today's Discussions

Based on today's conversations, potential article topics:

1. **AI Testing Cost Revolution** - How AI changes the economics of software testing, enabling "reckless" investments like mock banks that were previously impossible

2. **The Seven-Stage AI Adoption Funnel** - From denial to iteration, a framework for understanding where people are in their AI journey

3. **Unit Testing Obsolescence?** - Provocative take: in AI coding era, do unit tests still protect anything when we rewrite rather than reuse?

4. **抽卡师: AI's Blue Collar Jobs** - New job categories emerging in AI content generation, analogous to factory assembly lines

5. **Mobile Internet Didn't Create Miracles** - Counter-narrative: incumbents won by migrating, only ByteDance was a true startup success

6. **Anthropic's API Business Problem** - Zero loyalty, pure commodity - what this means for AI business models
