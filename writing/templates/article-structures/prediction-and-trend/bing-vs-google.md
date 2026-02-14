# Bing问答对Google的降维打击

## 摘要

用户不必向Bing提供关键词，而是可以用自然语言，尽量的向Bing提供自己能够记起的所有细节，Bing会充分的利用这些细节信息，尽力找出满足客户描述的答案。这种交互更符合人类大脑工作的方式，相比基于关键词的搜索，是革命性的进步。

## 用户场景

我和朋友们谈论起Linus的经历，我记得他当时还是一个大学生，受到一个操作系统的启发，但是我忘了作者或者OS的名字了，只记得如下信息：

- 它不是一个工业产品，而是为一本教材服务的。
- 它是一个较为简单的对Unix的实现。
- 它启发了当时还是大学生的Linus。

## Bing问答质量远高于Google搜索

所以我分别问了一下Google和Bing。用的查询语句是

> 哪个操作系统是一本教科书的附录，是对unix的简单实现，并且启发了Linus

如下图所示，Bing马上理解了我的意图，并且给出了正确的答案：Andrew S. Tanenbaum的Minix。

与此同时，Google给出的链接几乎完全不相干。

## 结果差异和语言无关

有朋友指出，这种质量的差别有可能是因为Bing有翻译能力，它可能把我的问题翻译成英文，搜索出结果，再翻译回中文，而Google直接使用内容比较贫乏的中文互联网内容，处于劣势。

于是我用英文再试一了一遍：

> what OS is implemented as a side project for a text book and inspired Linus?

如下图所示，Bing还是正确的回答了问题，而Google仍然给出了两个不相干的链接，在第三个Quora链接才间接的提及了答案。

## Google搜索质量依赖于用户具体的用词

如果稍微换一个翻译，使用下列语句

> which os was a simple implementation of unix in a textbook that inspired Linux

就会发现Google表现很不稳定，连刚才那个提供间接答案的Quora链接都没有了。

而Bing还是给出了正确答案。

## ChatGPT表现一样稳定

如下图所示，ChatGPT也理解了问题，给出了MINIX的答案。

我试着忽悠ChatGPT，告诉它Google并不同意他的回答。ChatGPT会马上道歉，反省自己说法不严谨的地方，但仍然坚持正确的答案：MINIX。

## 总结

从上面的例子可以看出，基于自然语言的Bing问答，相对传统基于关键词的Google搜索，能力和稳定性都得到了质的提升。如果没有特别的必要，基本上可以取代Google成为你的默认知识管理助手。

本文是《ChatGPT会怎么杀死Google/百度》一文的后续。

## 附录

上述Bing问答使用MicroSoft Edge Dev的sidebar的chat功能完成的。具体怎么开通这个预览版的服务，您可能还是需要Google来搜索，关键词可以是"new bing 资格"。
