# On Intelligence — Jeff Hawkins & Sandra Blakeslee
*Read: 2026-02-22*

## Why this book matters for MaGong's writing

Hawkins argues that intelligence is fundamentally about prediction, not behaviour — a framework that cuts directly against how most people think about AI, LLMs, and "smart" machines. The book offers a rigorous counter-narrative to the hype cycle: real intelligence requires memory, hierarchy, and time, none of which current AI systems have in the way brains do.

---

## Key findings

### 1. Intelligence is prediction, not behaviour — and this changes everything about how we evaluate AI

**The claim**: The defining characteristic of intelligence is the ability to make predictions about the future based on memory of the past. Behaviour is a *by-product* of prediction, not the definition of it.

**The evidence**: Hawkins uses the "altered door" thought experiment — if someone changes any one of a thousand things about your front door, you will immediately notice. Not because you have a database of door properties, but because your brain continuously predicts what it expects to sense, and deviation triggers attention. He also cites the "one hundred-step rule": the brain can perform complex tasks like recognising a cat in a photo in under half a second, which means at most 100 sequential neuron firings. Computers need billions of steps for the same task. Therefore the brain cannot be computing — it must be retrieving from memory and comparing against predictions.

**Writing angle**: This is the killer argument against "if LLMs pass the Turing Test they are intelligent." Hawkins directly addresses Turing: behavioural equivalence is not intelligence. A system can produce any output without understanding anything. For **benyu**: "The Turing Test was wrong from the start, and the entire AI industry spent 50 years running in the wrong direction because of it." For **hushi**: "The distinction between prediction-as-understanding versus pattern-matching-as-output is exactly the question that matters for evaluating AI coding tools."

---

### 2. The brain is a memory system, not a computer — and this distinction is not semantic

**The claim**: Neurons are five million times slower than silicon transistors, so the brain cannot compete computationally. It works instead by storing sequences of patterns and retrieving them — recognising the present by matching it to stored experience, then projecting what comes next.

**The evidence**: Four properties of neocortical memory that have no parallel in computers: (1) it stores *sequences* of patterns, not static data; (2) it recalls by partial match — auto-associative recall; (3) it stores *invariant* representations (you recognise your friend's face at any angle, distance, or lighting); (4) it is organised in a *hierarchy* that mirrors the hierarchical structure of the world. The most striking demonstration: you cannot recite the alphabet backwards because your memory of it is a sequence, not a lookup table. The same is true of everything you know.

**Writing angle**: Every engineering team building "AI" on top of LLMs is building a database with better search. It is not a memory-prediction system. The gap between what current AI does and what brains do is architectural, not a matter of compute or data. For **benyu**: attack the "just add more compute" argument as fundamentally confused about what kind of system would produce intelligence. For **hushi**: framework for comparing different AI architectures — which ones actually encode temporal structure? Which learn invariant representations?

---

### 3. Mountcastle's principle: one algorithm, all functions

**The claim**: The neocortex looks structurally identical everywhere — vision, hearing, motor control, language, all use the same six-layer cortical tissue. Therefore, the cortex runs one universal algorithm across all tasks. What makes vision visual and language linguistic is *what the regions are connected to*, not what they do.

**The evidence**: Ferrets surgically rewired so visual input goes to auditory cortex — they develop functioning *visual* pathways in auditory tissue. Blind people use visual cortex to read braille. Congenitally deaf people process visual information in areas that would normally handle sound. The cortex does not care what the input is — it runs the same pattern-learning algorithm on anything.

**Writing angle**: This is the scientific basis for a brutal critique of AI architecture. The brain doesn't have a "vision module" and a "language module" and a "reasoning module." Modularity is an artifact of what the regions are connected to, not a design principle. Current AI systems are all modular by design. For **hushi**: "The lesson from Mountcastle is that if you build the right underlying algorithm, it generalises. Building separate models for each task is not scaling — it is refusing to solve the actual problem."

---

### 4. Expertise is memory moving down the hierarchy — not rules being added up

**The claim**: When you learn something, the memory representation starts high in the cortical hierarchy (requiring conscious effort and full attention). With practice, it moves *down* the hierarchy, freeing the top for higher-order patterns. This is what makes an expert.

**The evidence**: A child learning to read first recognises individual letters with effort. Then words. Then phrases. An experienced reader no longer "sees" individual letters — recognition happens low in the hierarchy, automatically, and the top of the cortex is free to parse meaning, irony, structure. Same with music, chess, driving. This is not metaphor — Hawkins argues the physical representations literally re-form at lower cortical levels through repetition.

**Writing angle**: This reframes the question of AI skill development entirely. Current models don't have this. They don't develop *automaticity* — the way a junior developer laboriously looks up syntax while a senior just types. For **hushi**: "What does it mean for an AI coding assistant to become an expert? Can it? The hierarchy model suggests the answer is architectural — not about more training data." For **benyu**: attack the idea that prompt engineering is expertise. Prompting an LLM is not analogous to a skilled practitioner's automaticity — it is the opposite.

---

### 5. Creativity is prediction by analogy — not a special faculty

**The claim**: Creativity is not a separate ability that some people have. It is an inherent property of every cortical region. Creativity = making predictions by analogy to past experience. Every act of perception is a creative act.

**The evidence**: Playing a melody you know on an unfamiliar instrument is creative — your brain maps the structure of one instrument onto another. A mathematician solving a new problem by recognising it is analogous to an old one is exercising the same faculty. Shakespeare's metaphors ("there's daggers in men's smiles") are creative because they chain two unusual analogies. The neural mechanism is identical across all cases: invariant pattern matching across domains.

**Writing angle**: This deflates both the "AI will never be creative" argument and the "AI is already creative" argument. Both sides misunderstand what creativity is. For **benyu**: "Calling LLM outputs creative is like calling a record player musical. It plays back patterns. It does not predict by analogy from a model of the world." For **hushi**: the framework suggests that AI systems that only interpolate within their training distribution are fundamentally different from human creativity, which extrapolates by analogy.

---

## Usable frameworks

### The memory-prediction framework

**What it is**: Intelligence = a hierarchical memory system that stores sequences of patterns and uses those sequences to predict future inputs. The brain does not compute — it predicts. When predictions succeed, we experience understanding. When they fail, we experience surprise and pay attention.

**How to apply**: Any time you want to evaluate whether an AI system is "intelligent," ask: does it have a model of the world that generates predictions? Can it detect when its predictions are wrong? Does it store invariant representations that generalise across variations? If the answer is no, then no matter how impressive the outputs, it is not intelligent in the Hawkins sense.

---

### The hierarchy of sequences

**What it is**: The world has nested hierarchical structure. Notes combine into phrases, phrases into songs. Letters combine into words, words into sentences. Objects combine into scenes. The cortex mirrors this hierarchy — lower regions handle fast-changing small-scale patterns, higher regions maintain stable large-scale representations. This is why you can understand a face while your eyes are jumping around looking at individual features.

**How to apply**: When writing about AI systems, ask whether they model the world's hierarchical structure or whether they treat all tokens as equally local. The fact that transformers are essentially flat (every token attending to every other token) is a concrete architectural distinction from the brain's hierarchy. This is not a bug fixed by adding layers — it is a different approach to the problem.

---

### The one hundred-step rule

**What it is**: The brain can only use chains of 100 neuron firings for any task that takes under half a second. Since neurons fire at 200hz, and the brain performs complex tasks in 0.5s, the solution cannot be serial computation — it must be memory retrieval. This is why brains work so differently from computers.

**How to apply**: Use as a thought experiment when explaining why "just scale it up" doesn't produce intelligence. More transistors running the same computation faster hits limits the brain bypassed by using a completely different architecture.

---

## Best quotes

> "Complexity is a symptom of confusion, not a cause."

> "The biggest mistake is the belief that intelligence is defined by intelligent behavior."

> "Intelligence is not just a matter of acting or behaving intelligently. Behavior is a manifestation of intelligence, but not the central characteristic or primary definition of being intelligent. A moment's reflection proves this: You can be intelligent just lying in the dark, thinking and understanding."

> "The brain is not a computer, supplying by rote an output for each input it receives. Instead, it is a memory system that stores experiences in a way that reflects the true structure of the world, remembering sequences of events and their nested relationships and making predictions based on those memories."

> "Prediction is not just one of the things your brain does. It is the primary function of the neocortex, and the foundation of intelligence. The cortex is an organ of prediction."

> "The neocortex stores patterns in an invariant form... Memories are stored in a form that captures the essence of relationships, not the details of the moment."

> "To know something means that you can make predictions about it."

> "We have been bringing the full force of our species' considerable cleverness to trying to program intelligence into computers. In the process we've come up with word processors, databases, video games, the Internet, mobile phones, and convincing computer-animated dinosaurs. But intelligent machines still aren't anywhere in the picture."

> "You can become expert by practice, but there certainly is a genetic component to talent and genius too... If you study a particular set of objects over and over, your cortex re-forms memory representations for those objects down the hierarchy. This frees up the top for learning more subtle, more complex relationships. According to the theory, this is what makes an expert."

> "Our brains hate unpredictability, which is why people hate traditional handwriting recognition systems."

---

## Argument seeds

**Would agree with**: AI tools like Copilot are useful pattern matchers → angle: acknowledge usefulness while insisting we are clear-eyed about what they are not. They are powerful autocomplete. They are not understanding.

**Would push back on**: "LLMs understand language" → counter: Hawkins' framework makes understanding a precise technical concept. Understanding means having a predictive model that can detect when predictions fail. LLMs have none of this. They have no model of the world. They have sophisticated compression of what followed what in their training data.

**Would agree with**: The hype cycle around AI is built on the Turing Test confusion — if it looks intelligent, it is intelligent → angle: Hawkins gives us the tools to explain exactly why this is wrong, with neuroscience backing.

**Would push back on**: "Bigger models will eventually be intelligent" → counter: the architecture difference between a cortical hierarchy and a transformer is not a difference of scale. A transistor radio and a computer are both made of transistors, but you cannot get a computer by making a bigger transistor radio.

**Would agree with**: Coding expertise is not just knowing syntax — it is pattern recognition at multiple levels of abstraction, built through experience → angle: senior engineers have representations that have moved down their hierarchy. They see architectural problems immediately because the lower-level mechanics are automatic. AI tools that don't have this hierarchy cannot substitute for this kind of expertise.

---

## Possible article angles

1. **"LLMs 没有理解，只有预测 — 但这两件事为什么不一样"** (hushi): Use the Hawkins framework to draw a precise technical distinction between the brain's memory-prediction system and LLM next-token prediction. Not the same thing. The brain predicts because it has a *model of the world* that it checks predictions against. LLMs predict because statistical patterns in training data say what comes next. The test: can the system notice when its predictions are wrong? LLMs cannot.

2. **"图灵测试错了五十年"** (benyu): Hawkins spent the first chapter of his career getting rejected by AI labs for saying the right thing. MIT rejected his application because he wanted to study real brains. The AI establishment spent 50 years building the wrong thing. Use Hawkins as the authority to make the argument: behaviour equivalence is not intelligence, and every product that claims to be "AI" but is really pattern matching is a comfortable lie.

3. **"工程师的专业知识是如何形成的，以及 AI 为什么无法复制它"** (hushi): The hierarchy model of expertise. Senior engineers have automaticity at low levels, which frees the top of their hierarchy for architectural thinking. Junior engineers have everything in the wrong place. AI tools are stuck at a different level entirely — they have enormous breadth but no hierarchy. What does this mean for AI-assisted development? For team structure? For what skills humans should develop?

4. **"预测是理解的本质 — 这对你用 AI 的方式意味着什么"** (hushi): Practical piece. The best use of AI coding tools is not to replace understanding but to handle the parts of the hierarchy that you *have* automated — the syntax, the boilerplate, the lookup. If you use AI for the parts that require understanding, you are outsourcing the part that makes you better. Framed through Hawkins.

5. **"错误才是学习的真正信号"** (either): Hawkins: when predictions succeed, you experience understanding. When they fail, you pay attention and learn. Correct predictions result in understanding; incorrect predictions result in attention. This is the mechanism of learning. It has direct implications for how to use AI in development — mistakes are not bugs to be avoided, they are the mechanism by which your hierarchy improves. A workflow that eliminates all errors eliminates all learning.

---

## Raw notes

- Hawkins was rejected by MIT AI lab in 1981, rejected by Intel before that, and only founded Redwood Neuroscience Institute in 2002 after creating PalmPilot. The book is partly autobiography of someone who was right before anyone believed him.

- The Deep Blue chess computer is a great example: "Deep Blue didn't win by being smarter than a human; it won by being millions of times faster than a human. Deep Blue had no intuition. An expert human player looks at a board position and immediately sees what areas of play are most likely to be fruitful or dangerous, whereas a computer has no innate sense of what is important and must explore many more options."

- The rubber hand illusion: someone strokes a fake hand and your real hand in sync, and after a while you feel sensations in the fake hand. This demonstrates that the brain's model of the body is just another model, built from patterns — not hardwired.

- The blind spot: you have a blind spot in each eye where the optic nerve exits. You do not experience a hole in your visual field because your cortex fills it in with predictions. "We see what we expect to see as often as we see what we really see."

- On stereotyping: "You could substitute the word stereotype for invariant memory without substantially altering the meaning. Prediction by analogy is pretty much the same as judgment by stereotype." Stereotyping is not a moral failure — it is how the cortex works. The way to reduce harm from stereotypes is critical thinking and skepticism, not pretending they don't exist.

- The hippocampus as top of the cortical hierarchy: novel experiences that propagate all the way up the hierarchy without matching any stored sequence end up in the hippocampus. This is why you remember surprising events and forget the expected ones. "The more you know, the less you remember" — because known patterns are handled low in the hierarchy and never reach the hippocampus.

- On consciousness: "Consciousness is simply what it feels like to have a cortex." The two components: (1) everyday awareness, which Hawkins equates with forming declarative memories; (2) qualia — why different senses *feel* different, which he admits he cannot fully explain.

- Intelligent machines will not be humanoid robots. They will not have emotions or personal ambition. The fear of machine takeover is based on the false analogy that intelligence implies human emotional drives. It does not. "Intelligent machines will not have anything resembling human emotion unless we painstakingly design them to."

- On the appropriate use of intelligent machines: "The strongest applications of intelligent machines will be where the human intellect has difficulty, areas in which our senses are inadequate, or in activities we find boring."

- Hawkins proposes a weather-sensing intelligent machine as an example: distribute sensors across a continent the way retinal cells cover the retina. The machine would learn to predict weather the way we learn to recognise objects — by finding invariant structure in the patterns. Not by computing fluid dynamics. A totally different approach.
