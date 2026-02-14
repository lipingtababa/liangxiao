# Vibe Coding是专供程序员的成年人童话

自从AI在软件工程的应用流行起来，很多投机分子开始乱造新词，其中以Andrej Karpathy（卡帕西） 的Vibe Coding一词流毒最广。

Vibe Coding 是一个专供软件工程师的成年人童话。相信它的从业者都应该被工信部吊销软件开发从业资格。

从基础理论上来说，任何严肃的工程项目，不管是软件工程还是土木工程，都是一个在复杂和严格的限制下追求最优方案的过程，必然充斥预算超支，人手不足，需求变动频繁，市场反响冷淡，安全漏洞，可用性故障，隔壁部门那个吊总监又抢先给领导汇报了等等工程问题，根本谈不上Vibe。就算不在乎人间繁华能抵挡硅谷金钱崇拜的 Linus  Torvalds，维护 Linux 内核也让他时不时的情绪失控。

吹vibe的卡帕西，在维基百科上的介绍仍然是"前Tesla AI总监"，类似我们在中国见过的大量"Ex-Amazoner"和"前阿里大神"。实际上，他2022年就离职了，今天的正式头衔是AI培训课程LLM101s的创始人。换句话说，他就是个主打AI在线培训的美国李一舟。李一舟如果能说服时代杂志把他自己列为什么影响AI的一百人，就完全和卡帕西构成了太平洋两岸的镜像。

卡帕西是如此流行，逼得严肃的从业者不得不捍卫行业荣誉。GitHub在九月份提出Spec Driven Development。直接指出Vibe Coding只能用于瞎胡闹：

> This "vibe-coding" approach can be great for quick prototypes, but less reliable when building serious, mission-critical applications or working with existing codebases
> https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/

高考英语分数高但是对美国文化不熟悉的读者会和我较真："嘿，GitHub这不是说了vibe coding can be great了吗？"这里就涉及到美国职场的说话艺术了。任何有but的句子，你可以直接跳过but之前的部分--那都是为了礼貌；只看but后面的部分--那才是对方想说的内容。GitHub这段话，翻译成现代白话，就是

> 这vibe coding不能用于构建严肃的，生产级的应用，也不能用于现有的代码库。
> 马工的翻译

Spec Driven Development 和Vibe Coding 的区别，主要在于路线： Vibe Coding天真的把LLM当做阿拉丁神灯，我只需要用心流许愿，神灯就会满足我的愿望。而SDD非常务实的把LLM当做一个结对编程的同事，这个和马工七月份提出的观点是一致的：

> 我的建议是，把cc当做一个懂得所有编程语言，极为耐操，天资中等偏上，一天工作16小时，春节不休假，学习能力超强的985毕业生。换句话说，本来去华为的应届生跑到你公司来了，并且只需要 1500 人民币一个月的工资，并且一次来了一百个。
> 公众号：瑞典马工
>
> 把Claude Code当员工用！它不是个工具！

但是Spec Driven Development 也很初级。作为一个AI 商业 coding 的积极实践者，瑞典马工（怎么又是这个人？）提出了AI Coding的三个待解决问题：

> 1.怎么确保ai coding出来的东西是你想要的？
> 2.怎么确保ai coding交付物的质量是可信赖的？
> 3.怎么构建一个超音速人/LLM混合团队？
> 公众号：瑞典马工
>
> AI Coding领域的真问题

Spec Driven Development 试图解决第二个问题，但是几乎完全彻底的忽视了另外两个问题。

比如在他们的宣言里，主语总是同一个"You"，You写需求，You做测试，You做架构，You拆解任务，而我们知道，任何一个严肃的工程项目不可能只有一个"You"，必然还有Me, He, She,They甚至It。我合理的怀疑宣言的作者Den Delimarsky 其实没有组建过严肃的人/LLM混合团队。

即使在他们试图解决的第二个问题上，SDD也做得很肤浅。

一个最简单的问题：什么是Spec？

Spec宣言里，spec可以是产品需求规格书Product Requirements Description，也可以是架构设计书，也可以去项目计划。最让人无法忍受的是，他们建议把非功能需求塞进设计文档，而不是产品需求规格书。这种外行做法让他们和试图替换的Vibe Coding的心理距离更近而不是更远了。

然后在Spec Kit的Readme里，他们宣称： Specifications become executable。如果说Task is executable 还可以理解的话，需求规格书怎么可能execute？Delimarsky先生能不能当众表演下这个魔术？

这种悖论来源于一个很简单的事实：不论是GitHub还是亚马逊都说不清什么是Spec。

作为商业一线AI Coding的探索者，瑞典马工对文档做了一个初步的分类。

**第一类，需求和约束（Requirements and Constraints ）**。这部分文档描述甲方对项目的期望。除了传统的PRD，还有各种合规要求，非功能要求，SLA以及老登领导对前端界面大红色按钮的独特爱偏好。它是真值的来源，如果软件行为和这部分文档不一致，应该修改的是软件。实践中，这个文档往往由非开发者主导。

**第二类，外部契约（External Contracts）** 。最典型的就是OpenAPI文档和Linux Syscall接口。现代软件几乎没有独立运行的，都是更大一个系统的一个模块。任何对契约的单方面修改都会增大上层系统的摩擦阻力。如果软件行为和契约不一致，应该修改的也是系统，而不是文档。用博士们最喜欢的词来说，就是外部契约具备规范性Nomartive。

**第三类，可执行真相（Executable Truth）**。在代码之外，还包括基础设施，CI/CD，配置，数据库，值班安排。这部分毋庸赘言。

**第四类，派生视图（Derived Views ）**。这部分包括程序员们最常谈及的架构图，流程图，部署指南，readme，遗留问题等等。这部分文档由可执行真相派生出来，权威性显然低于代码或者参数。有些人说"AI时代不要写文档了，不然容易因为文档过时而误导AI"，他们说的就是这部分文档，而不是PRD。派生视图是为了降低token消耗而对解释性投影做的一个cache，它的管理办法，显然和需求&约束的管理办法不一样。比如说，我们可以让LLM生成两个版本，一个老师傅李令辉专用，一句废话都没有，一个菜鸟专用，把每一个命令行都写好了供菜鸟复制。

**第五类，用户知识文档（User Knowledge ）**。这是传统的文档工程师的领域。根据Diataxis框架，可以分tutorials, guides , explanation and reference。这也是国内软件厂商一直被人鄙视的地方。这部分文档的读者会从人类移动到AI Agents，以后也要有很大的变化。

**第六类，过程性记录（Ephemeral Records ）**。主要是开发计划，还包括troubleshooting 记录，technical decisions，会议纪要，故障复盘等等。此类文档只具备短时间的价值，在生产完成后，就只具备教育意义了。SDD的Tasks算在此处。实践中，有的团队把这个check in到git，有的放在notion，有的放在jira/linear，都无关紧要，只要达成共识就好了。

每个中学生都要学习的动植物分类法，门纲目科属种，是瑞典科学家林奈在18世纪发明的。林奈的分类让博物学从收集珍奇物种进化到系统性的研究生物的阶段，促进了生物学作为一个学科的成立。

现在AI Coding也刚刚进入启蒙阶段，瑞典马工愿和各位探索者一起讨论交流，让我们一起把软件工程从依靠手艺的作坊作业提升到可以用人月计量的正经工程学。
