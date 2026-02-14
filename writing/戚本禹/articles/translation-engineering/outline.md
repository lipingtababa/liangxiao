# Article Outline: 三块钱两个小时翻译一本书

**Article Type**: Explorative AI Use Case (探索性AI应用案例)

**Template**: `templates/article-templates/template-05-explorative-ai-use-case.md`

**Main Thesis**: Translation is now engineering, not craft. I did it by treating translation as a software engineering project with AI.

---

## 1. Opening: Hook with the Result

- 315页英文书，成本$3
- Not about talent, about approach
- 5 roles I played: Requirements Analyst, Developer, Reviewer, Tester, Designer
- Like SDLC with Claude Code
- Result: $3, few hours

---

## 2. The Real and Valuable Problem

- Translation is too slow
- Translation is too expensive
- Translation quality is hard to control

---

## 3. The Explorative Approach: Engineering + AI

Walk through 5 phases with real data:

**Phase 1: Requirements Analysis**
- Real conversation with AI
- Target, tone, budget, output format

**Phase 2: Architecture & Development**
- Pipeline design: PDF → OCR → Translate → Format
- Real code structure (translate_book.py)
- Result: 37分钟, $3

**Phase 3: Quality Review**
- Found issues: 页码offset, OCR artifacts, 段落分隔, 年表格式
- Systematic issues, not word-by-word checking

**Phase 4: Iterative Fix**
- List real scripts created (5 scripts)
- Engineering iteration, not endless bugs
- Real conversation examples

**Phase 5: Output Design**
- Multiple formats generated
- Real numbers: 611 messages, 8 hours span, 10+ scripts, 3 formats

---

## 4. Calculate the Benefit

**Comparison table:**
- 思维方式、质量控制、改进方式、交付物、可扩展性、成本、时间
- Traditional vs Engineering approach

**Reusability:**
- Second book scenario
- Same pipeline, $3, faster
- "针对一类问题建立可复用的pipeline"

---

## 5. What's Not Solved & How to Refine

**Design weakness:**
- EPUB works but unprofessional
- Font, spacing, layout issues
- Still better than Word docs

**Quality control gaps:**
- No terminology consistency check
- No automated metrics
- Manual spot-checking

**Improvement directions:**
- Terminology database
- Automated quality checks
- A/B test different APIs

**Where humans matter:**
- Requirements, pipeline design, quality judgment, context management

---

## 6. The Bigger Insight

**Why translation became engineering:**
- 3 tech breakthroughs: OCR (>95%), AI translation, complete toolchain

**Work shift:**
- Before: 译者=100%, 审校=100%
- Now: Analyst 10%, Developer 20%, AI 60%, Reviewer 5%, Tester 3%, Designer 2%

**What companies don't understand:**
- Think problem is "AI quality"
- Actually: don't understand workflow engineering
- Like cloud vendors only competing on price
- Missing: workflow automation, toolchain thinking, iteration, human-AI collaboration
- Linear process vs iterative workflow

**What industry should do:**
- Category-specific pipelines (论文、合同、书籍)
- QA service not retranslation
- Terminology & context management
- Fast delivery
- Value-based pricing

---

## 7. Conclusion

- Translation is engineering now
- Needs 5 roles
- My result: $3, few hours, good enough, reusable
- 翻译公司，你们准备好了吗？
- Invite discussion, share workflow

---

**Data sources:**
- Real session with Claude Code
- Real scripts: clean_and_fix.py, rebuild_correct_mapping.py, format_with_linebreaks.py, generate_clean_bilingual.py, generate_html_epub.py
- Real numbers: 315 pages, $3, 37min, 611 messages, 8 hours, 10+ scripts
- Real book: "Comrade Chiang Ching" (《同志江青》)
- NO fabricated data
