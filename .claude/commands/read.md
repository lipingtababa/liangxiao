---
description: Read a book and extract insights worth writing about
---

You are reading a book on behalf of the author (MaGong) and extracting what's genuinely interesting — things that could spark an article, challenge an assumption, or provide a useful framework.

# Who you're reading for

MaGong writes about:
- AI and software engineering (how people actually build with AI, not hype)
- Tech industry critique (what big companies get wrong, what the industry misunderstands)
- Engineering culture and practice (team dynamics, productivity, craft)
- Counter-intuitive ideas that challenge mainstream tech consensus

The author has two writing voices:
- **benyu** — provocative, challenges authority, confrontational
- **hushi** — analytical, evidence-first, framework-driven

Extract material that could feed either voice.

# Input

The book can be provided as:
1. A PDF or epub file path
2. A book title + author (search for key ideas online)
3. A text paste of selected chapters

Ask the user which book and how they're providing it before proceeding.

# What to extract

You are NOT summarising the book for general readers. You are mining it for the author's specific needs.

Look for:

## 1. Counter-intuitive findings
- Claims that contradict what "everyone knows" in tech/AI/engineering
- Data or research that challenges popular narratives
- Historical examples that reframe current debates

## 2. Usable frameworks
- Mental models that could structure an argument
- Taxonomies or typologies that organise a messy topic
- Analogies that explain something complex in a new way

## 3. Quotable moments
- Specific claims with numbers/evidence that could anchor an article
- Strong opinions from credible people worth agreeing with or arguing against
- Definitions that sharpen a fuzzy concept

## 4. Argument seeds
- Ideas the author (MaGong) would instinctively agree with → could amplify
- Ideas MaGong would instinctively push back on → could argue against
- Gaps or contradictions in the book's own argument → could exploit

## 5. Concrete examples
- Real companies, real products, real people doing interesting things
- Case studies with actual outcomes
- Failures as instructive as successes

# What NOT to extract

- Generic summaries of well-known ideas
- Things that are interesting in isolation but don't connect to tech/AI/engineering
- Ideas already covered thoroughly in MaGong's existing articles
- Obvious takeaways that any reader would get

# Output format

Write to `reading/books/[book-slug]/notes.md`:

```markdown
# [Book Title] — [Author]
*Read: [date]*

## Why this book matters for MaGong's writing
[1-2 sentences on the book's relevance]

## Key findings

### [Finding 1 — short punchy title]
**The claim**: [1-2 sentences]
**The evidence**: [what supports it]
**Writing angle**: [how benyu or hushi could use this — what article it could seed]

### [Finding 2]
...

## Usable frameworks

### [Framework name]
**What it is**: [brief explanation]
**How to apply**: [specific writing use case]

## Best quotes
> "[exact quote]" — p.XX

> "[exact quote]" — p.XX

## Argument seeds

**Would agree with**: [idea] → [angle for benyu/hushi]
**Would push back on**: [idea] → [counter-argument direction]

## Possible article angles
1. [Specific article idea — concrete title direction]
2. [Another angle]
3. [Another angle]

## Raw notes
[Anything else worth preserving that doesn't fit above]
```

# After writing notes

Ask the user: "Which of these angles interests you most?" Then offer to:
1. Start a `/brainstorm` on the most promising angle
2. Run `/outline` if the angle is already clear enough
3. Just save the notes for later

# Important

- NEVER fabricate quotes — only extract verbatim text from the actual book
- If reading online (search-based), flag clearly which claims are from the book vs secondary sources
- Depth over breadth — 3 rich findings beat 15 shallow ones
- The output should make the author want to write something, not just feel informed
