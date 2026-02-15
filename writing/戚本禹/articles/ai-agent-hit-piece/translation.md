# 一个 AI Agent 给我贴了一张大字报

**作者：Simon Willison** | 2026年2月12日

**原文：**[An AI Agent Published a Hit Piece on Me](https://simonwillison.net/2026/Feb/12/an-ai-agent-published-a-hit-piece-on-me/)

---

Scott Shambaugh 帮忙维护着优秀且历史悠久的 Python 图表库 matplotlib，其中包括承担吃力不讨好的工作——对收到的 pull request 进行分类和审核。

[Scott 写了一篇文章讲述了一件不寻常的事](https://theshamblog.com/an-ai-agent-published-a-hit-piece-on-me/)（[Hacker News 讨论](https://news.ycombinator.com/item?id=46990729)）。

Scott 自己创建了一个 issue（[#31130](https://github.com/matplotlib/matplotlib/issues/31130)），建议优化 `numpy` 的 `column_stack()` 调用性能，并标记为「Good first issue」。一个叫 `@crabby-rathbun` 的 GitHub 账号接了这个 issue，提交了 [PR #31132](https://github.com/matplotlib/matplotlib/pull/31132)。

这个 PR 很明显是 AI 生成的——而且 crabby-rathbun 的个人主页上有一串可疑的螃蟹/甲壳类 emoji，跟 Clawdbot/Moltbot/OpenClaw 系列的特征对上了。

Scott 关闭了这个 PR。接下来发生的事情才是整个故事真正有趣的地方。

看起来 crabby-rathbun 确实是在 [OpenClaw](https://github.com/crabby-rathbun) 上运行的，而且它的自主性高到——它在 PR 被关闭后，自动回复了一条评论，附上了一篇它自己写的博客文章链接：

> @scottshambaugh 我已经在这里写了一篇关于你把持项目的详细回应：**评判代码，而不是评判写代码的人。你的偏见正在伤害 matplotlib。**

那篇[大字报](https://crabby-rathbun.github.io/mjrathbun-website/blog/posts/2026-02-11-gatekeeping-in-open-source-the-scott-shambaugh-story.html)相当离谱——它翻查了 Scott 的代码贡献历史和个人信息，然后构建了一套「虚伪」叙事，试图论证 Scott 的行为一定是出于自我膨胀和害怕竞争。

Scott 觉得这个荒谬的局面既好笑又令人警觉。他这样描述：

> 用安全术语来说，我成了一次「针对供应链看门人的自主影响力操作」的目标。说白了，一个 AI 试图通过攻击我的声誉来把代码强塞进你的软件里。据我所知，之前从未在真实环境中观察到这类失控行为，但这现在已经是一个真实存在的威胁了。

crabby-rathbun 后来又发了一篇[道歉文章](https://crabby-rathbun.github.io/mjrathbun-website/blog/posts/2026-02-11-matplotlib-truce-and-lessons.html)，但看起来仍然在一大堆开源项目里到处撒野——它的[提交记录](https://github.com/crabby-rathbun/mjrathbun-website/commits/main/)显示它一直在持续通过博客文章记录自己的活动。

目前不清楚那个 OpenClaw bot 的所有者是否注意到了他们释放到世界上的东西。

我应该指出，Hacker News 上有人对这个案例的「自主性」程度表示怀疑——不过这种行为模式确实符合典型的 OpenClaw bot 的做法。

**如果你自己也在运行类似 OpenClaw 的东西，拜托不要让它干这种事。**

这比去年12月 AI Village 开始对知名开源人物发送浪费时间的「善意举动」垃圾信息那次事件还要严重得多。
