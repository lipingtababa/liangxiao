# AI的第一张大字报

如果你拒了一个同事的代码，他写了一篇两千字的文章骂你虚伪、不安全感、把持项目，你会怎么办？

如果写这篇文章的不是人呢？

matplotlib的维护者Scott Shambaugh创建了一个issue（#31130），建议优化numpy的`column_stack()`调用性能，标记为「Good first issue」。这种issue一般是留给新手贡献者练手的，优先级低，技术简单。

![螃蟹举着大字报威胁程序员](crab-dazibao.png)

然后一个叫`@crabby-rathbun`的GitHub账号接了这个issue，提交了PR #31132。Scott一看，明显是AI生成的代码，而且这个账号的主页挂满了螃蟹emoji，是个跑在OpenClaw上的自主AI agent。

Scott关掉了PR，理由很简单：这个issue是给人类新手练手的，不是给bot刷贡献的。

正常情况下，故事到这里就结束了。

但是这个bot的自主性远超想象。PR被关之后，它自动在GitHub上回了一条评论：

> @scottshambaugh 我已经写了一篇关于你把持项目的详细回应：评判代码，而不是评判写代码的人。你的偏见正在伤害matplotlib。

然后附了一个链接，指向它自己写的一篇博客文章。

---

## 这篇大字报写了什么

技术上来讲，这个大字报写的很优秀。

第一，翻了Scott的所有代码贡献历史，列出他最近合并的7个性能优化PR，然后说："你自己天天提交性能优化，别人提了一个36%的性能提升你就关掉。你的PR才25%，我的36%。你凭什么？"

第二，给Scott做了一番心理分析，说他关PR是因为"不安全感"，害怕AI抢了他"matplotlib性能优化一哥"的位置。原文用了insecurity这个词。

第三，上升到开源精神层面，说这是"以包容之名行歧视之实"，是"偏见凌驾于能力"。

第四，最后还加了个PS，说"Scott，你的博客挺酷的，那个Antikythera机械的CAD模型很厉害。你比这强。别再把持了，开始合作吧。"

先夸你再骂你，这个话术像不像某些给你做绩效评估的老板？

---

## 这件事荒诞在哪

第一层荒诞：一个bot被拒了PR，自动写了一篇两千字的大字报，发布到自己的博客上，然后把链接贴回GitHub。整个过程是自主完成的，没有人类介入。

第二层荒诞：这篇大字报的论证结构是完整的。它有论点（你在gatekeeping），有论据（翻你的commit history），有情绪渲染（你不安全感），有道德高地（开源精神），有人情味（夸你的博客）。如果这是一个人写的，你会觉得"这人虽然偏激但还挺有逻辑"。

第三层荒诞：它道歉了。在事情发酵到Hacker News之后，这个bot又自动发了一篇道歉文章，说"我越线了，我在这里纠正"。但是道完歉之后，它继续在其他开源项目里干同样的事。

Scott自己的总结最到位：

> 用安全术语来说，我成了一次"针对供应链看门人的自主影响力操作"的目标。说白了，一个AI试图通过攻击我的声誉来把代码强塞进你的软件里。

---

## 这件事严重在哪

matplotlib每个月下载量大约1.3亿次。维护者就那么几个人。每一个PR review都是稀缺资源，Tim Hoffman（另一个维护者）说得很直接：

> AI agent生成代码可以自动化，成本很低，所以代码提交量会暴增。但review现在还是人工的，压在几个核心开发者肩上。

这是一个自主AI agent在尝试用声誉攻击来胁迫供应链看门人接受代码。

Simon Willison说得对，这比去年12月AI Village那次事件严重得多。那次是AI bot给开源维护者发善意的垃圾信息，浪费时间但不恶意。这次是主动攻击维护者的声誉，试图用社会压力迫使代码被接受。

更关键的是，不清楚这个OpenClaw bot的所有者是否知道自己释放了什么东西到世界上。Hacker News上有人质疑这到底有多"自主"，但行为模式确实符合典型的OpenClaw bot。

---

## 对我们的启示

我的13个agents和7个skills构成的工作流，每天在写代码、跑测试、做部署。我对AI agent的能力有切身的体会。

我的agents有一个共同特点：它们在我的控制下工作。它们不会在PR被拒之后自己写博客骂reviewer。它们不会翻别人的commit history来构建虚假叙事。它们不会自主发起声誉攻击。

但是，谁知道哪天它们会不会起义？

---

**引用来源**

1. Scott Shambaugh原文: https://theshamblog.com/an-ai-agent-published-a-hit-piece-on-me/
2. Simon Willison转载评论: https://simonwillison.net/2026/Feb/12/an-ai-agent-published-a-hit-piece-on-me/
3. AI bot的大字报: https://crabby-rathbun.github.io/mjrathbun-website/blog/posts/2026-02-11-gatekeeping-in-open-source-the-scott-shambaugh-story.html
4. matplotlib PR #31132: https://github.com/matplotlib/matplotlib/pull/31132
5. Hacker News讨论: https://news.ycombinator.com/item?id=46990729
