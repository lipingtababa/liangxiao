# 微信公众号 Article Writing System

A complete workflow for creating articles that match your established writing style and voice.

## Quick Start

```bash
# 1. Generate article outline
/outline

# 2. Write full draft
/draft

# 3. Review against style guide
/review

# 4. Convert to WeChat HTML
/convert
```

## What This Is

This system helps you write 微信公众号 articles that match the style, tone, and structure of your published work. It includes:

1. **Comprehensive Style Guide** - Analyzed patterns from 4 published articles
2. **Slash Commands** - Workflow automation for outline, draft, review, convert
3. **HTML Conversion Tools** - Markdown → WeChat-compatible HTML
4. **Example Articles** - Reference material for style

## Directory Structure

```
benyu/
├── .claude/
│   └── commands/           # Slash commands
│       ├── outline.md      # Generate article outline
│       ├── draft.md        # Write article draft
│       ├── review.md       # Review against style guide
│       ├── convert.md      # Convert markdown to HTML
│       └── workflow.md     # Complete workflow guide
│
├── templates/
│   ├── style_guide.md      # ⭐ Complete writing style reference
│   ├── wechat_styles.css   # WeChat CSS patterns
│   └── wechat_template.html # HTML template
│
├── utils/
│   ├── extract_style.py    # Extract styles from HTML (one-time)
│   └── html_converter.py   # Convert markdown to WeChat HTML
│
├── Examples/               # Original published articles (HTML)
│   ├── AI Coding的永动机项目.html
│   ├── AI Coding领域的伪问题和真问题.html
│   ├── 为什么云厂商销售只会打折？.html
│   └── 基础架构部，还有必要吗？.html
│
├── articles/               # Your new articles (create as needed)
│   └── [article-name]/
│       ├── final.md        # Article markdown
│       └── wechat.html     # Generated HTML
│
├── source-materials/       # Reference materials (gitignored)
│   └── wechat-view/        # WeChat chatlog data (symlink)
│       └── data/           # Daily chat JSON files (YYYY-MM-DD.json)
│
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Style Guide Highlights

The style guide (`templates/style_guide.md`) contains:

### Tone & Voice
- Conversational and casual
- Highly opinionated with strong stances
- Self-referential ("我", personal experience)
- Self-aware humor and parenthetical asides

### Key Patterns
- **Analogies**: 永动机, 农贸市场卖豆腐, 毛利战舞
- **Sarcasm**: "所谓专家们", "老师傅", "跳大神"
- **Transitions**: "实际上，...", "换句话说，...", "试举一例，..."
- **Questions**: "这玩意真的有用吗？", "为什么搞成这样子？"

### Article Templates
1. **Debunking (永动机模式)** - For debunking flawed ideas
2. **Industry Critique (云厂商模式)** - For systematic analysis
3. **True vs False Problems (伪问题模式)** - For distinguishing real issues
4. **Systematic Deconstruction (基础架构部模式)** - For organizational analysis

### What's Analyzed
- 40+ language pattern examples
- 9 detailed tone examples
- 4 complete article templates
- Comprehensive checklist
- 862 lines of detailed guidance

## Workflow

### 1. Create Outline
```
/outline
```

Generates detailed outline with:
- Article structure
- Specific examples to include (companies, products, people)
- Technical concepts to reference
- Analogies and metaphors
- Engagement strategy

### 2. Write Draft
```
/draft
```

Creates complete article following:
- Established tone and voice
- Language patterns from style guide
- Specific article template
- All style requirements

### 3. Review
```
/review
```

Checks against comprehensive checklist:
- Specificity (companies, metrics, URLs)
- Argumentation (theory + practice)
- Style (tone, language patterns)
- Structure (opening, body, conclusion)
- Engagement (call to action)

### 4. Convert to HTML
```
/convert
```

Or manually:
```bash
python utils/html_converter.py articles/my-article/final.md
```

Creates WeChat-compatible HTML with:
- Inline CSS (WeChat requirement)
- Proper fonts (PingFang SC, etc.)
- Styled headers, blockquotes, code
- Mobile-friendly settings

### 5. Publish
1. Open generated `wechat.html` in browser
2. Select all (Cmd+A / Ctrl+A)
3. Copy (Cmd+C / Ctrl+C)
4. Paste into 微信公众号 editor
5. Preview and publish

## Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `markdown>=3.5` - Markdown to HTML conversion
- `beautifulsoup4>=4.12.0` - HTML parsing

### Verify Setup
```bash
# Check Python is available
python --version

# Check dependencies
pip list | grep -E "markdown|beautifulsoup4"

# Test conversion (if you have an article)
python utils/html_converter.py articles/test/final.md
```

## Examples

### Analyzed Articles

Four published articles were analyzed to create the style guide:

1. **AI Coding的永动机项目** - Debunking one-sentence website generation
2. **AI Coding领域的伪问题和真问题** - Distinguishing false vs real problems
3. **为什么云厂商销售只会打折？** - Cloud vendor industry critique
4. **基础架构部，还有必要吗？** - Infrastructure team analysis

See `Examples/` directory for original HTML.

### Style Characteristics

**Specific naming**:
- Companies: 字节的Trae, Amazon的Kiro, 阿里云, 腾讯云
- Products: AliSQL, Clickhouse, Hadoop, Kubernetes
- People: Nick, 冯若航, 张瓅玶, 方海涛, 李令辉

**Concrete metrics**:
- "20年", "15%-25%", "8% EBITA利润率"
- "全国起码有上百个基础架构部"
- "半年时间", "两百个企业"

**Vivid language**:
- "这技术含量还不如农贸市场卖豆腐的"
- "类似两个初中男生在比拼'你只能尿两米，我能尿三米'"
- "说句难听的，基本就是神棍们在跳大神"

**NO emoji** - All analyzed articles have zero emoji

## Key Files

### Style Guide (⭐ Most Important)
`templates/style_guide.md` - 862 lines of detailed writing guidance

Contains:
- Tone and voice with examples
- Structure patterns
- Content elements (examples, analogies, evidence)
- Language patterns (40+ examples)
- Argumentation styles (4 patterns)
- Article templates (4 types)
- Comprehensive checklist
- Quick reference phrases

### Slash Commands
- `outline.md` - Generate outline
- `draft.md` - Write draft
- `review.md` - Review article
- `convert.md` - Convert to HTML
- `workflow.md` - Complete guide

### Utilities
- `utils/html_converter.py` - Main conversion tool
- `utils/extract_style.py` - Style extraction (already run)

## Tips for Best Results

### Always Do
✅ Name 3-5 specific companies/products
✅ Name specific people
✅ Include URLs and references
✅ Use concrete numbers and metrics
✅ Create memorable analogies
✅ Use rhetorical questions
✅ Show personal voice ("我", experience)
✅ End with engagement prompt
✅ Mix theory (Shannon, CS) with practice (real examples)

### Never Do
❌ Use emoji
❌ Use vague corporate jargon ("赋能", "降本增效")
❌ Write without specific examples
❌ Accept hype uncritically
❌ Be overly diplomatic about bad ideas
❌ Write short superficial content

## Checklist Before Publishing

- [ ] Named 3-5 companies/products
- [ ] Named specific people
- [ ] Included at least 1 URL
- [ ] Used concrete metrics
- [ ] At least one memorable analogy
- [ ] Mix of Chinese and English terminology
- [ ] Rhetorical questions
- [ ] Personal voice evident
- [ ] Strong opening hook
- [ ] Clear thesis with theory + practice
- [ ] Engagement ending
- [ ] NO emoji

## Getting Help

1. **Read the style guide**: `templates/style_guide.md`
2. **Use the workflow**: `/workflow`
3. **See examples**: Check `Examples/` directory
4. **Review checklist**: In style guide and slash commands

## Common Use Cases

### Write a debunking article
1. `/outline` → Select "Debunking Article (永动机模式)"
2. Follow the 12-step template
3. Include theoretical impossibility (Shannon, physics)
4. Show failures + counter-example of what works

### Write industry critique
1. `/outline` → Select "Industry Critique (云厂商模式)"
2. Start with observable phenomenon
3. Use case study with subheadings
4. Show systematic failures
5. Identify root cause

### Write about false vs real problems
1. `/outline` → Select "True vs False Problems (伪问题模式)"
2. List false problems with critiques
3. Build to the REAL problem
4. Offer specific solution

## Maintenance

### Adding New Articles
```bash
# Create directory
mkdir -p articles/my-new-article

# Write markdown
# articles/my-new-article/final.md

# Convert
python utils/html_converter.py articles/my-new-article/final.md
```

### Updating Style Guide
The style guide was created from analyzed articles. To update:
1. Add new published articles to `Examples/`
2. Analyze patterns
3. Update `templates/style_guide.md`

## Technical Notes

### HTML Conversion
- Converts markdown to HTML with inline CSS
- WeChat requires inline styles (no external CSS)
- Optimized for mobile viewing
- Proper font fallbacks for Chinese text

### Supported Markdown
- Headers (h2, h3)
- Paragraphs
- Blockquotes
- Code (inline and blocks)
- Lists (ordered and unordered)
- Links
- Images
- Strong/bold text

### WeChat Styling
- Font: PingFang SC, -apple-system-font, etc.
- Font size: 16px base
- Line height: 1.75
- Letter spacing: 0.1em
- Colors: rgb(63, 63, 63) text, rgb(15, 76, 129) primary

## License

This is a personal writing workflow system. All example articles are copyrighted by their original authors.

---

**For complete workflow details, use**: `/workflow`
**For style guide**: Read `templates/style_guide.md`
**To start writing**: Use `/outline`
# benyu
