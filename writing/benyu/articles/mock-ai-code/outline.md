# 文章大纲：嘲笑AI代码的人，没出息

## 核心论点
嘲笑AI代码烂的人，其实是在嘲笑自己的无能 — 因为那些烂代码是vibe coder搞出来的，不是AI的问题。

**Template**: Debunking Article (永动机模式)

---

## 1. Opening: "没出息"的程序员

**Hook: 用"没出息"梗**
- 最近看到很多程序员在网上嘲笑AI代码
- 配上王世坚的"连滚带爬、没出息"
- 但真正"没出息"的是谁？

**具体现象（引用真实数据）：**
- 微软吹嘘"AI写了30%的代码"，同时"每个patch Tuesday都是数字末日"
- Vibe Coding现象（2025年2月爆发）
- ProgrammerHumor.io的吐槽："凌晨2点让AI做todo app，花3小时调试它的幻觉"

**Thesis：**
不是AI不行，是vibe coder搞砸了 → 毁了AI名声 → 让人以为AI不可靠 → 开始嘲笑AI代码

---

## 2. Define: 什么是Vibe Coding？

**定义（引用Andrej Karpathy）：**
- OpenAI联合创始人创造的词
- 依赖AI助手（Cursor等）生成代码，自己不写也不理解
- 2025年2月网友观察："vibe coders无法管理、理解或调试自己的代码"

**典型特征：**
- 让AI生成完整代码，不review直接用
- 出问题了怪AI："AI代码不行"
- 没有测试，没有质量控制
- [User: 你观察到的其他vibe coding特征？]

---

## 3. Prove: 真实灾难 — PR #23 Disaster

**我的亲身经历（SyntheticCodingTeam项目）：**

### 灾难发生
- **任务**：删除README中的短语"解释文化细节"
- **期望**：只删除那个短语
- **实际**：AI删除了整个README文件
- **原因**：Vibe coding - 没有测试保护，AI误解要求

### 灾难证据
- 保留了出问题的版本：`SyntheticCodingTeam_corrupt`
- README从388行变成空文件
- [User: 补充更多当时的细节？]

### 问题根源
- 没有E2E测试验证
- 没有文件完整性检查
- 直接让AI改，没有review机制
- **这就是vibe coding**

---

## 4. Explain: 为什么会这样？行业还在蛮荒时代

### 根本原因：缺乏成熟的best practice

**历史类比：早期软件工程**
- 当初没有经过行业培训的码农，写的代码也是一塌糊涂
- 没有流程和质量控制，直接在生产环境改代码
- 后来发展出了软件工程：测试、staging环境、code review

**AI Coding也在经历同样的过程：**
- 目前没有人告诉大家要怎么做
- Average从业者只能用自己的直觉
- 然后怒斥AI

### 早期的各种Myths：睁眼说瞎话

**随意归因的典型案例（真实观察）：**

**案例1：微软老哥睁眼说瞎话**
- 现象：自己不会用AI，导致代码质量很差
- 归因："AI不会写C++"
- 追问："能具体指出AI在C++上的能力不足吗？"
- 答案：给不出具体例子，但坚持"AI不行"
- **这就是睁眼说瞎话**

**案例2：其他老哥也在睁眼说瞎话**
- "AI不会维护brownfield项目"
- "AI不会维护infra项目"
- 失败了 → 随意找个归因 → 从不怀疑自己
- **都是睁眼说瞎话**

**睁眼说瞎话的本质：**
- 就像早期程序员说"测试没用"、"直接改生产环境更快"
- 自己不行 → 怪工具不行 → 生成myths
- **最没出息的表现**

---

## 5. Counter-example: 正确的做法 — 怎么救回来的？

### 救援措施：E2E测试

**实施的测试（真实代码）：**
```python
def test_targeted_phrase_removal():
    """Ensure only target phrase removed, not entire file."""
    # Critical assertions that would catch PR #23
    assert '解释文化细节' not in result  # Phrase removed
    assert len(result) > 50  # File not empty!
    assert "Long README" in result  # Content preserved
    assert result != ""  # Not completely deleted
```

**测试分类：**
- 文件完整性测试
- 内容保留测试
- 定向修改测试

**结果：**
- 从`SyntheticCodingTeam_corrupt` → 正常版本
- 建立了disaster prevention系统
- 文档：`improved-startup-and-testing.md`

---

## 6. Broader Framework: 把AI当团队成员管理

**引用鸭哥文章（https://yage.ai/ai-management-2-en.html）：**

### 核心观点
- **错误**：把AI当工具
- **正确**：把AI当实习生/团队成员

### 关键引用
> "Your value is no longer in pressing pedals but in being its navigator: you plan the route, anticipate risks, and absorb the complexities it can't handle."

> "You wouldn't expect every piece of data from your intern to be perfect. You would build trust over time."

### IC到管理者的转变
- 高手不擅长授权 → 但管理者要让影响力倍增
- 不是review每行代码 → 而是建立自动化测试和CI/CD

**类比：**
- Vibe coder = 放任不管的老板
- 嘲笑AI的人 = 不会带新人的IC
- 正确做法 = 像管理者带团队

---

## 7. Systematic Solution: 需要完整的方法论

**方法论 = 流程 + 分工 + 质量控制**

**流程：**
- 需求分析 → 设计 → 实现 → 测试 → Review

**分工：**
- 人类：战略决策、质量控制、最终责任
- AI：代码生成、模式识别、重复性工作
- 工具：自动化测试、CI/CD、强制规则

**质量控制：**
- E2E测试（像PR #23 prevention）
- Code review
- 自动化检查

**对比：**
| Vibe Coding（没出息） | 正确协作（有出息） |
|-------------------|-------------------|
| 让AI生成，不测试就用 | 生成后先测试 |
| 出问题怪AI | 反思流程问题 |
| 嘲笑AI不行 | 改进协作方式 |
| 连滚带爬 | 从从容容、游刃有余 |

---

## 8. Address Objections: 想象中的反驳

**反驳1："AI确实写了很多烂代码啊"**
- 是的，但那是vibe coder让它写的
- 没给清晰需求，没做测试，没有review
- 换人类实习生一样会写烂代码

**反驳2："我手写比AI快/好"**
- 恭喜你，你比工具快
- 但工人比挖掘机挖得快吗？
- 会计比Excel算得快吗？
- **问题不是速度，是规模和稳定性**

**反驳3："那我不用AI了"**
- 更"没出息"了
- 拒绝用工具 = 拒绝进步
- **应该学会用好工具，不是拒绝工具**

---

## 9. Provocative Conclusion: 真正"没出息"的是谁？

**四种人：**
1. **Vibe coder** - 不懂方法论，搞砸了，连滚带爬（最没出息）
2. **睁眼说瞎话的人** - 自己不行怪AI，"AI不会写C++"、"AI不会做infra"，从不自我怀疑（最没出息）
3. **嘲笑AI的人** - 看到烂代码，以为AI不行，开始比谁手快（也没出息）
4. **会用AI的人** - 有方法论，把AI当团队成员，从从容容、游刃有余（有出息）

**Provocative reversal：**
- 你以为在嘲笑AI？
- 其实是在嘲笑vibe coder
- 更是在嘲笑自己不会管理AI

**换句话说：**
- 和AI比代码 = 和挖掘机比挖坑
- 嘲笑AI代码 = 嘲笑你不会开挖掘机
- **都是"没出息"的表现**

---

## 10. Call to Action

**对vibe coder：**
- 别再vibe了，学方法论
- 加E2E测试、code review、质量控制

**对嘲笑AI的人：**
- 别和工具比了，学会用工具
- 把AI当团队成员管理，不是当敌人

**对所有人：**
- 读鸭哥的文章：https://yage.ai/ai-management-2-en.html
- 学会从IC到管理者的转变
- **有出息的做法：从从容容、游刃有余地用好AI**

**Engagement：**
有兴趣研究这个问题的同好，欢迎在公众号给我留言。如果你也有vibe coding的灾难故事，或者有更好的AI协作经验，也欢迎分享。

这篇文章对你有帮助吗？点赞和转发让更多"没出息"的人看到。

---

## 待补充材料

**需要用户提供真实数据：**
- [ ] PR #23 disaster的更多细节
- [ ] SyntheticCodingTeam_corrupt的具体对比数据
- [ ] 你观察到的vibe coding特征
- [ ] 救援过程的更多技术细节

**可选补充：**
- [ ] 其他程序员嘲笑AI代码的具体例子（Twitter/Reddit截图？）
- [ ] 微软"patch Tuesday数字末日"的具体案例
- [ ] "没出息"梗的音频/视频链接（如果有）

---

## 风格检查清单

**Specificity（具体性）：**
- [x] 具体公司/产品：微软、Cursor、OpenAI
- [x] 具体人物：Andrej Karpathy、鸭哥（yage.ai）
- [x] 具体数字：PR #23、2025年2月、388行README
- [x] 具体URL：https://yage.ai/ai-management-2-en.html
- [x] 具体项目：SyntheticCodingTeam、SyntheticCodingTeam_corrupt

**Argumentation（论证）：**
- [x] 理论基础：管理理论（IC → Manager）
- [x] 类比：挖掘机、实习生、Excel
- [x] 真实案例：PR #23 Disaster
- [x] 对比：vibe coding vs 正确协作

**Style（风格）：**
- [x] 开场hook："没出息"梗
- [x] Sarcastic tone：三种"没出息"的人
- [x] 反问句："真正没出息的是谁？"
- [x] Provocative reversal：你以为在嘲笑AI...
- [x] 中英混用：vibe coding、E2E、IC、Manager

**Engagement（互动）：**
- [x] Call to action：欢迎留言分享
- [x] Provocative ending："让更多没出息的人看到"
