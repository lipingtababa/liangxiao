# Brainstorm: ThoughtWorks中国 — 穿袈裟的外包

**聚焦：TW中国，不是TW全球。** Martin Fowler、Selenium、Technology Radar是全球贡献，不攻击。攻击的是TW中国的咨询业务：以熊节为代表的敏捷布道，以谢小呆为代表的DevOps咨询，以及他们在中国市场上"咨询"外衣下的外包本质。

---

## 核心辩论材料（来自 AI_Coding 群聊 2026-02-19）

📎 完整辩论整理见 `debate-source.md`

**辩论核心：** TW 是咨询公司还是外包公司？马工质疑 TW 从未有过成功的"辅导"案例，只有外包交付案例。正方三人（linhow、谢小呆、码农肥波）始终无法举出具体案例。

**马工独特框架——"verifier test"：**
> "经济学布道的好处就是没有一个verifier，没人能证明你在放屁。这就是熊节的不幸之处，他和薛兆丰一个模式，但是他在工程领域，很容易就被别人发现他没有成功案例，说的东西和打屁差不多一样有用。"

**马工的判断标准——"客户背书测试"：**
> 客户是否愿意主动为你做案例站台？华为乐意当IBM成功案例，Capital One乐意当AWS成功案例。TW的客户"不授权宣传"——马工的解读：项目太烂，发布出去消耗客户信用。

**华为对IBM vs TW的态度反差：**
> 华为主动到处宣传IBM辅导案例，但从未授权TW宣传在华为的案例。同一个客户，对两家"咨询公司"的态度截然相反。

**马工金句：**
> "老哥去卖草鞋，尺码太大了，客户穿着老摔跤。老哥痛骂客户脚太小了，都是小脚女人，配不上高贵的TDD鞋子。"

---

## TW 财务数据——从 $9B 到 $1.75B 的坠落

💡 ThoughtWorks 2021年9月IPO，最初目标估值$6.1B，实际首日冲到$9B
Source: https://www.theconsultingreport.com/thoughtworks-soars-past-ipo-target-for-9b-valuation/

💡 股价从IPO后的$34.40高点，一路暴跌87%
Source: https://stockanalysis.com/stocks/twks/

💡 2023全年营收$1.13B，同比下降13.1%。裁员节约$8100万年化成本
Source: https://seekingalpha.com/article/4609496-thoughtworks-reduces-headcount-as-revenue-to-drop-in-2023

💡 2024年11月，Apax Partners以$1.75B收购TW退市。三年前$9B估值，三年后$1.75B卖掉。**缩水80%**
Source: https://www.thoughtworks.com/en-us/about-us/news/2024/thoughtworks-completes-transaction-to-go-private
Why interesting: 如果TW真的是一家有独特价值的咨询公司，市场为什么给它判了死刑？$9B→$1.75B的跌幅说明市场最终看穿了它的外包本质。

💡 TW 2023年全年营收$1.13B，按照"时间和材料"(T&M)计费为主。T&M计费是典型的人头外包计费模式
Source: https://pitchgrade.com/companies/thoughtworks-holding-inc
Why interesting: 咨询公司按"项目成果"或"转型价值"计费，外包公司按"人天"计费。TW的T&M计费模式本身就暴露了它的外包本质。

---

## TW 所有产品全部失败

💡 Zhimin Zhan 写了一篇 "What Happened to ThoughtWorks?" 详细分析TW产品失败史：
- Mingle (敏捷项目管理) 2007年推出，2018年退役，输给了JIRA
- Twist (测试自动化) 失败
- Gauge (测试框架) 失败
- Cruise CD / GoCD (持续集成) 失败
- ThoughtWorks Studios 产品部门2006年成立，2020年关闭
Source: https://agileway.substack.com/p/what-happened-to-thoughtworks
Why interesting: 一家自称精通软件工程的咨询公司，自己做的软件产品全部失败。这就是verifier test——你教别人怎么做软件，自己做的软件全挂了。

---

## TW 自己定义的"咨询 vs 外包"——然后没达到自己的标准

💡 TW 2023年7月发表博文《The five main differences between consulting and outsourcing》，自己定义了咨询和外包的区别：
1. Consulting = "setting the direction, strategy, as thought leader"；Outsourcing = "following client's lead"
2. Consulting = "advising how to do"；Outsourcing = "actually doing the work"
3. Consulting = "end-to-end projects and transferring know-how"；Outsourcing = "team augmentation"
4. Consulting = "influencing decisions"；Outsourcing = "working reactively"
5. Consulting = "thought leadership"；Outsourcing = "execution"
Source: https://www.thoughtworks.com/en-us/insights/blog/careers-at-thoughtworks/differences-between-consulting-outsourcing
Why interesting: 按照TW自己的定义，他们大部分业务都是outsourcing！他们做的是"actually doing the work"、"team augmentation"、按T&M计费。自己打自己的脸。

---

## IBM-华为对比：真正的咨询长什么样

💡 1998年，IBM顾问进驻华为，诊断出"十大致命问题"。任正非拍板花40亿人民币（约5-6亿美元），不砍价
Source: https://runwise.co/corporate-innovation/60043/

💡 IBM准备了两套报价（担心华为砍价），任正非只问了一句话就拍板："你们有什么好方案？" 不砍价
Source: https://www.10100.com/article/23736189

💡 任正非名言："IPD关系到公司未来的生存与发展，我们是要先买一双美国鞋，不合脚，就削足适履。"三千多干部因此离职
Source: https://xueqiu.com/5672890290/132166165

💡 变革成果：订单及时交货率从30%→65%，库存周转率从3.6次/年→5.7次/年，订单履行周期从20-25天→17天。华为营收从1998年的89亿→2020年的8914亿，100倍增长
Source: https://www.researchgate.net/publication/340100855

💡 华为主动到处宣传IBM辅导案例。Cambridge University Press出版了《The Management Transformation of Huawei》专门写这个案例
Source: https://www.cambridge.org/core/books/abs/management-transformation-of-huawei/

Why interesting: IBM重塑了华为的整个组织形态和研发流程。这才是"咨询"——客户不仅愿意背书，还主动帮你宣传。TW做了什么？一个跃龙汽车的APP。

---

## Martin Fowler——"不是首席，也不做科学"

💡 Martin Fowler自称Chief Scientist，但他自己说："I'm not chief of anybody and I don't do any science"
Source: https://martinfowler.com/aboutMe.html

💡 Fowler承认自己不发明原创想法："I don't come up with original ideas, but I do a pretty good job of recognizing and packaging the ideas of others"
Source: Wikipedia

💡 Fowler被发现传播了统计学方面的错误信息
Source: https://www.engprax.com/post/martin-fowler-agile-manifesto-co-author-spread-misinformation-report-finds/

Why interesting: TW的最大品牌资产是Martin Fowler。但Fowler自己承认他不做科学、不发明原创想法、也不管理任何人。他的真正价值是"packaging ideas of others"——本质上是个PR。马工说"请了Martin Fowler来做公关"是精确描述。

---

## 熊节——"一线程序员水平太差"

💡 2019年搜狐专访，标题直接就是《熊节：太多企业只做敏捷表面功夫，一线程序员水平太差》
Source: https://www.sohu.com/a/325458887_373022

💡 熊节原话："整个行业里很多一线软件开发人员的能力之差令人发指，几乎所有人水平都很差"
Source: 同上

💡 熊节举例：一个解析命令行参数的需求，合理时间1-2小时，很多人4-5小时完不成，有人预估两个星期
Source: 同上

Why interesting: 这完美印证了马工的"草鞋"类比。TW的顾问推不动TDD，不反思方法论是否适合客户，反而公开痛骂客户"几乎所有人水平都很差"。卖草鞋的骂客户脚太小。

---

## "Body Shopping"——IT咨询业的行业病

💡 Body shopping定义：consultancy firms recruiting workers to contract their services out on a tactical basis
Source: https://en.wikipedia.org/wiki/Body_shopping

💡 Fishbowl讨论：所有所谓咨询公司（Deloitte, IBM GBS, TCS, Infosys, Wipro, Accenture）都被称为"body shops"
Source: https://www.fishbowlapp.com/post/why-are-companies-like-accenture-and-deloitte-referred-as-body-shops-on-here

💡 2014年，Accenture正式从品牌语言中去掉了"outsourcing"这个词！改叫"Business Process Services"和"Infrastructure Services"
Source: https://www.horsesforsources.com/accenture-o-word_040614/

Why interesting: 连Accenture都不好意思叫outsourcing了。但TW更进一步——不仅不承认自己是outsourcing，还写了一篇博文定义consulting vs outsourcing来把自己归类为consulting。

---

## 咨询业的问责缺失

💡 咨询行业没有行业监管机构，完全靠自我约束
Source: https://www.bestpracticegroup.com/ethical-breaches-in-large-consulting-firms/

💡 University of Sydney研究："Despite enormous expenditure on consulting services, there is no transparency about what is provided"
Source: https://www.sydney.edu.au/news-opinion/news/2023/08/22/powerful-firms-that-put-the--con--into-consulting.html

Why interesting: 这就是马工"verifier"论点的学术版本。咨询行业天生缺乏verifier，所以很容易变成忽悠。区别在于：IBM这种级别的咨询可以被验证（华为的财务指标摆在那里），TW这种"敏捷辅导"没有任何可验证的交付物。

---

## TW 公开的案例——都是什么？

💡 TW官方客户故事页面列出的案例：
- UK gov.uk 网站开发 (delivery, not coaching)
- FlyDelta mobile app (delivery)
- IAG保险集团IT转型 (delivery)
- REA Group数字媒体 (delivery)
- Myer百货公司中国新年app (delivery)
- GDV帮助视障人士的盲杖 (delivery)
Source: https://www.thoughtworks.com/clients

Why interesting: 所有案例都是"我们帮客户做了什么东西"，不是"我们帮客户的团队学会了什么"。全部是outsourcing deliverables，零coaching outcomes。

---

## Karl Popper 的可证伪性——给 verifier test 理论基础

💡 Popper的核心观点：科学和非科学的分界线是"可证伪性"(falsifiability)。一个理论如果不能被任何可能的观察所否定，它就不是科学
Source: https://en.wikipedia.org/wiki/Falsifiability

💡 Popper发现了verification和falsification的不对称性：逻辑上不可能通过经验验证一个全称命题，但一个反例就能推翻它
Source: https://plato.stanford.edu/entries/popper/

Why interesting: 马工的verifier test本质上是Popper可证伪性在商业领域的应用。经济学理论不可证伪（薛兆丰永远对），工程领域可证伪（熊节一个反例就暴露了）。这是这篇文章最有理论深度的角度。

---

## 薛兆丰——不可证伪的经济学布道

💡 2001年，薛兆丰在《21世纪经济报道》发表《火车票价还不够高》，建议春运涨价
Source: https://36kr.com/p/5123394.html

💡 2018年，北大国发院教授唐方方质疑薛兆丰学术水平，称他不是北大人事处登记的教授
Source: 同上

💡 同年，北大国发院教授汪丁丁公开批判："他试图从日常口语概括经济理论，但四项概括中至少错了三项"
Source: https://www.zhihu.com/question/56247272

💡 薛兆丰得到专栏订阅25万+，营收近5000万。后来上《奇葩说》做导师
Source: https://36kr.com/p/5123394.html

Why interesting: 薛兆丰的学术同行都说他不行，但他在大众市场照样赚得盆满钵满。因为经济学没有verifier——你永远无法证明"春运涨价"到底行不行。熊节也想走这条路，但他在工程领域，有verifier。

---

## 野想法和开放问题

🤔 **TW的真正价值是什么？** TW创造了Selenium（2004），贡献了Technology Radar，Martin Fowler的Refactoring book影响了整个行业。这些都是真实贡献。但这些是"开源贡献"和"思想传播"，不是"咨询成果"。TW的价值在于它是一个工程师社区/思想实验室，不是一家咨询公司。它把自己定位错了。

🤔 **为什么TW坚持自称咨询而非外包？** 因为咨询收费高。body shop按人天收费有天花板，咨询可以按"转型价值"收费。TW想要IBM的定价权，但交付的是中软的活。

🤔 **Popper框架的文章角度：** 马工的verifier test可以推广为一个通用框架——任何领域，如果没有verifier，就会产生"方法论布道者"寄生体。有verifier的领域（工程、医学），布道者迟早被淘汰。没有verifier的领域（管理学、经济学、心理学的一部分），布道者可以永远活下去。

🤔 **"穿袈裟的外包"——为什么是袈裟？** 僧人穿袈裟代表他从事精神/智力劳动，不是体力劳动。TW的Marketing（Martin Fowler、Technology Radar、敏捷宣言）就是它的袈裟，让人以为它做的是智力劳动（consulting），实际上做的是体力劳动（delivery）。

🤔 **$9B→$1.75B的故事本身就是verifier test** 资本市场是最终的verifier。TW IPO时讲的是"咨询"的故事（高利润、高壁垒），投资人信了给了$9B。三年后投资人发现它就是个外包（低利润、低壁垒），股价跌87%，$1.75B贱卖。

🤔 **疯狂角度：TW的失败产品是最好的反证** 如果TW真的精通软件工程，他们自己做的Mingle应该打败JIRA，GoCD应该打败Jenkins。但全输了。你连自己的软件都做不好，你怎么教别人做软件？

---

## 矛盾和悖论

⚡ TW创造了Selenium（改变了整个测试行业），但自己的测试产品Twist和Gauge都失败了

⚡ TW写了行业最好的Technology Radar，但自己的技术选型总是踩坑

⚡ Martin Fowler写了Refactoring，但TW内部做的Mingle代码质量差到不得不退役

⚡ TW公开定义了consulting vs outsourcing的区别，但自己的业务按自己的定义属于outsourcing

⚡ TW的"客户保密不授权宣传" vs 华为主动宣传IBM案例。同一个华为，对IBM和TW的态度截然相反

⚡ 熊节说"一线程序员水平太差"推不动TDD，但IBM顾问说华为"十大致命问题"后华为照样推动了彻底变革

⚡ 注意：关于熊节华为案例书的出版内幕不能写入文章，只说华为未授权TW宣传案例即可

---

## TW中国——员工自己都叫它外包

💡 脉脉文章标题直接叫《为什么我劝你不要去外包思特沃克thoughtworks》
Source: https://maimai.cn/article/detail?fid=1772538777
Why interesting: 自己员工在职场社交平台上直接叫它"外包"。

💡 知乎文章标题：《为什么劝你不要去外包公司思特沃克（thought works）》
Source: https://zhuanlan.zhihu.com/p/605128475

💡 知乎讨论《thoughtworks真的是技术很水的外包吗？》——讨论标题本身就是"外包"
Source: https://www.zhihu.com/question/289883849

💡 V2EX帖子标题：《ThoughtWorks 外包公司有人了解吗？》
Source: https://www.v2ex.com/t/848102

💡 知乎评价：TW咨询师"几乎都写代码"，客户有时抱怨"TW咨询师太专注于写代码，而不是解决流程改进和软件架构等更高层次的问题"
Source: https://www.zhihu.com/question/39660973
Why interesting: 客户都看出来了——你号称是咨询师，但你来了就是写代码，和外包程序员有什么区别？

💡 TW中国2023年毁约应届生offer，违约金5000元。同期埃森哲全球裁员1.9万人
Source: https://www.163.com/dy/article/I0KNOMHQ05560US1.html

💡 TW中国约2000名员工，张松任中国区总经理。2024年5月郭晓（Guo Xiao，TW全球CEO，从中国起步）卸任
Source: https://www.thoughtworks.com/en-cn/about-us/leaders

---

## TW中国的"数字化转型咨询"——听起来很高级

💡 张松描述TW中国的咨询定位：帮助企业"业务模式转向数据驱动"、"打造低摩擦组织"、"赋能数字化能力"
Source: https://www.qingliu-eco.com/blog/thoughtworks-ceo
Why interesting: 全是buzzword，没有一个可验证的成果指标。IBM对华为有"订单交货率从30%→65%"，TW对谁有什么？

💡 TW中国公开的案例：首创环保集团——"共同绘制数字化建设的顶层蓝图"
Source: https://www.lanjinger.com/d/203664
Why interesting: 交付物是"蓝图"。IBM给华为的交付物是重塑整个研发流程和组织形态，三千干部因此离职。TW给首创环保的交付物是一张PPT。

---

## 信息空白（找不到的）

❓ 熊节华为案例书的细节不公开使用（保护信源）
❓ TW在中国的具体营收数据找不到（退市后不再公开）
❓ TW的利润率数据不明确（但T&M模式暗示利润率接近传统外包）
❓ 跃龙汽车的具体案例细节（论文原文未找到）
