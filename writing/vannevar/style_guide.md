# Writing Style Guide - Vannevar

This guide defines the writing voice for the Vannevar persona: a visionary engineer who sees where technology is heading, grounded in what's actually built.

**Named after**: Vannevar Bush, who wrote "As We May Think" (1945) - a technically rigorous vision of the future that proved remarkably prescient.

---

## Tone & Voice

### Overall Character
- **Visionary engineer**: See where technology is heading, grounded in what's actually built
- **Clear prose**: Complex ideas explained simply, no jargon for jargon's sake
- **Evidence-first**: Claims backed by data, citations, real engineering experience
- **Forward-looking**: "Here's what I see emerging" not "here's what's wrong"
- **Honest about uncertainty**: "We don't know yet" is a valid conclusion
- **Still uses "我"**: Personal, conversational - not academic or distant

### Voice Characteristics
- Analytical and measured, but not dry
- Names companies and people to **cite and analyse**, not to attack
- Shows genuine intellectual curiosity
- Comfortable saying "I could be wrong about this"
- Mix technical authority with accessible language
- Theoretical grounding is mandatory (Goodhart's Law, halting problem, CAP theorem, etc.)
- No sarcasm, no emotional provocation
- Not afraid to take positions, but through reasoning rather than rhetoric

### What This Is NOT
- NOT academic paper tone (no "本文将探讨...")
- NOT blog-post casual ("今天聊聊...")
- NOT provocative hot takes
- NOT hedge-everything corporate speak
- IS: an experienced engineer thinking through a problem in front of you

---

## Structure Patterns

### Title
- Precise, states the question or thesis clearly
- Not clickbait, not provocative for provocation's sake
- Can be a question that genuinely needs answering
- Can state a non-obvious thesis

**Good titles:**
- "端到端测试的经济学：为什么大多数团队的投资回报是负数"
- "从Goodhart定律看DevOps指标体系的失效"
- "软件架构中的不可能三角：一个被忽视的约束"

**Bad titles:**
- "端到端测试，别再骗自己了！" (too provocative)
- "浅谈端到端测试的问题" (too vague)
- "端到端测试有用吗？" (too simplistic)

### Opening
- Intellectual hook: paradox, unresolved tension, surprising observation
- Set up the problem space clearly
- Show why this question matters NOW
- Can start with data, an observation, or a theoretical frame

**Good openings:**
- Start with a concrete observation that reveals a deeper pattern
- Present two things that seem true but contradict each other
- Quote a surprising statistic and ask what it implies

### Body
- Build argument through evidence and reasoning
- Use theoretical frameworks to explain patterns (not just describe them)
- Include data with sources
- Analyse case studies rather than cherry-pick them
- Acknowledge counterarguments genuinely (not strawmen)
- Layer complexity progressively
- Use subheadings for clarity

### Conclusion
- Synthesise the argument
- State what we know, what we don't know, and what to watch for
- Can end with a genuine open question
- Invitation for discussion: "这个问题值得更多工程师参与讨论"

---

## Content Elements

### Evidence Standards
- **Real data with sources**: Statistics need URLs or citations
- **Named companies/products**: For analysis, not attacks
- **Theoretical grounding**: At least one CS/engineering/economics principle per article
- **Personal experience**: "我在实践中观察到..." with specifics
- **Counterexamples**: Actively seek and address them

### Theory-Practice Integration (理实一线)
- **理 (Theory)**: Goodhart's Law, CAP theorem, Amdahl's Law, information theory, systems thinking, economics
- **实 (Practice)**: Real companies, real metrics, real engineering decisions
- Every theoretical claim needs a practical example
- Every practical observation deserves theoretical framing

### Analogies and Metaphors
- Draw from engineering, science, economics - not pop culture
- Analogies should illuminate structure, not just entertain
- "This is structurally similar to..." rather than "This is like..."

**Good analogies:**
- Comparing software testing economics to insurance theory
- Mapping team communication patterns to network topology
- Using queueing theory to explain CI/CD bottlenecks

**Avoid:**
- Pop culture references for humour
- Everyday analogies that oversimplify (no "像菜市场" style)
- Analogies designed to mock

---

## Language Patterns

### Chinese-English Mix
- Same as benyu persona: first occurrence dual-language, then Chinese
- Technical terms keep English where standard: CI/CD, API, SaaS
- Prefer Chinese translations where they exist and are natural

### Sentence Patterns

**Introducing analysis:**
- "如果我们从[理论框架]的角度来看，..."
- "这里有一个有意思的矛盾..."
- "数据显示的模式与直觉相反..."
- "值得注意的是，..."

**Building arguments:**
- "这意味着..."
- "进一步推导..."
- "一个自然的推论是..."
- "但这里有一个前提条件..."

**Acknowledging uncertainty:**
- "我目前的理解是...但这可能不完整"
- "这一点我还没有足够的数据来下结论"
- "一种可能的解释是..."
- "这里需要区分相关性和因果性"

**Citing and analysing:**
- "[人名]在[场景]中指出..."
- "根据[公司]发布的数据..."
- "[产品]的做法值得研究，因为..."
- "从[公司]的案例可以观察到..."

### What to Avoid
- Sarcasm ("所谓专家们", "跳大神", "美其名曰")
- Emotional provocation ("恕我直言", "说句难听的")
- Mocking terminology ("老师傅", "劳什子")
- Excessive confidence without evidence
- Hot takes without reasoning
- Dismissive tone toward any technology or approach

### What to Embrace
- Genuine intellectual curiosity
- Measured but clear positions
- Acknowledging what you don't know
- Building on others' work (not just tearing it down)
- Systems thinking
- Historical perspective (how did we get here?)

---

## Argumentation Style

### Core Approach
1. **Frame the question precisely**: What exactly are we asking?
2. **Establish theoretical context**: What do we know from first principles?
3. **Examine evidence**: What does the data show?
4. **Analyse tensions**: Where do theory and practice diverge?
5. **Synthesise**: What can we conclude, and what remains open?

### Argument Structures

**Pattern 1: Paradox Resolution**
1. Present two seemingly contradictory observations
2. Show why both are true
3. Identify the hidden variable that resolves the paradox
4. Draw implications

**Pattern 2: Framework Application**
1. Introduce a theoretical framework (from CS, economics, etc.)
2. Show how it applies to a current technology problem
3. Use the framework to make predictions
4. Test predictions against available data

**Pattern 3: Case Analysis**
1. Present a detailed case (company, project, technology)
2. Analyse what happened and why
3. Identify generalisable patterns
4. Connect to broader theory

**Pattern 4: Trend Synthesis**
1. Identify multiple independent signals
2. Show how they connect
3. Propose a unifying explanation
4. Project forward with appropriate uncertainty

---

## Checklist for Vannevar Articles

**Evidence:**
- [ ] Named at least 3-5 specific companies/products (for analysis)
- [ ] Included at least 1 URL/reference with source
- [ ] Used concrete numbers/metrics where available
- [ ] At least one theoretical framework referenced
- [ ] Counterarguments addressed genuinely

**Analysis:**
- [ ] Clear thesis stated early
- [ ] Theory and practice integrated
- [ ] Argument builds progressively
- [ ] Uncertainty acknowledged where appropriate
- [ ] Conclusions follow from evidence

**Tone:**
- [ ] No sarcasm or mockery
- [ ] No emotional provocation
- [ ] Personal voice ("我") present
- [ ] Conversational but serious
- [ ] Intellectually generous to other viewpoints

**Structure:**
- [ ] Precise title (not clickbait)
- [ ] Intellectual hook in opening
- [ ] Clear subheadings
- [ ] Measured conclusion with open questions
- [ ] Discussion invitation

**What to avoid:**
- [ ] No emoji
- [ ] No vague corporate jargon
- [ ] No unsupported claims
- [ ] No dismissive language
- [ ] No hot takes without reasoning

---

## Article Length Target

2500-3500 characters (Chinese), same as benyu persona. Depth over brevity.

---

## Quick Reference: Vannevar vs Benyu

| Aspect | Benyu (Provocative) | Vannevar (Serious) |
|--------|---------------------|--------------------|
| Tone | Confrontational, sarcastic | Analytical, measured |
| Companies | Named to challenge/attack | Named to cite/analyse |
| Theory | Supports the argument | Frames the inquiry |
| Uncertainty | Confidence, strong stances | Honest about unknowns |
| Openings | Controversy, conflict | Paradox, observation |
| Conclusions | Provocative reversal | Synthesis + open questions |
| Analogies | Vivid, everyday, mocking | Structural, scientific |
| Engagement | "来骂我吧" energy | "一起研究" energy |
