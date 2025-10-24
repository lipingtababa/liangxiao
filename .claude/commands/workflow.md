---
description: Guide for the complete article writing workflow
---

# 微信公众号 Article Writing Workflow

This guide explains the complete workflow for creating articles in the established style.

## Overview

You have a complete workflow for writing, reviewing, and publishing 微信公众号 articles that match your established voice and style.

## The Components

### 1. Style Guide
**Location**: `templates/style_guide.md`

This is your comprehensive writing reference based on 4 analyzed published articles. It contains:
- Tone and voice patterns
- Language patterns and favorite phrases
- Argumentation structures
- Article templates
- Extensive examples and quotes
- Complete checklist

### 2. Slash Commands

- `/outline` - Generate article outline based on style guide
- `/draft` - Write full article draft following style patterns
- `/review` - Review article against style checklist
- `/convert` - Convert markdown to WeChat HTML
- `/workflow` - This guide

### 3. Conversion Tools

- `utils/html_converter.py` - Converts markdown to WeChat-compatible HTML
- `templates/wechat_styles.css` - WeChat styling patterns
- `templates/wechat_template.html` - HTML template

## Recommended Workflow

### Step 1: Create Outline
```
Use: /outline
```

This will:
1. Ask about your topic
2. **Choose the right article template first:**
   - Debunking Article (永动机模式)
   - Industry Critique (云厂商模式)
   - True vs False Problems (伪问题模式)
   - Systematic Deconstruction (基础架构部模式)
   - Explorative AI Use Case (探索性AI应用案例)
3. **Define the structure based on the chosen template**
4. Generate a detailed outline with:
   - Section-by-section structure from the template
   - Specific examples to include in each section
   - Analogies to use
   - Technical concepts to reference
   - All following the template's proven pattern

### Step 2: Write Draft (Section by Section)
```
Work with Claude to write the article section by section
```

**IMPORTANT: Write one section at a time, not all at once.**

**Human-in-the-Loop Approach:**
1. Start with the outline structure
2. Claude writes the **Opening Hook (引入)** first
3. **Human reviews and provides feedback**
4. Claude refines based on feedback
5. Move to next section: **The Central Insight (核心洞察)**
6. **Human reviews and provides feedback**
7. Claude refines based on feedback
8. Continue section by section through the outline

Each section follows the style guide:
- Conversational, opinionated tone
- Specific company/product names
- Memorable analogies
- Proper language patterns
- No emoji

**Why section by section with human feedback?**
- Human provides direction and feedback at each step
- Allows for course correction early
- Easier to refine tone and content
- Prevents large rewrites
- Better quality control
- Ensures the article matches your vision

### Step 3: Human Reviews Each Section
After Claude writes each section, you:
- Read the section
- Provide feedback on:
  - Tone and voice
  - Specific examples or data
  - Analogies and language
  - Anything that doesn't feel right
- Claude adjusts based on your feedback
- Move to next section only when satisfied

### Step 4: Final Review
```
Use: /review
```

When the complete article is assembled:
1. Check overall flow and coherence
2. Verify all style guide requirements
3. Confirm engagement ending
4. Provide detailed feedback and suggestions

### Step 5: Final Revise
- Implement feedback from final review
- Ensure consistency across sections
- Polish transitions
- Run `/review` again if needed

### Step 6: Save Markdown
```
Save to: articles/[article-name]/final.md
```

Create a directory structure:
```
articles/
  └── my-article-name/
      └── final.md
```

### Step 7: Convert to HTML
```
Use: /convert
```

Or run directly:
```bash
python utils/html_converter.py articles/my-article-name/final.md
```

This creates: `articles/my-article-name/wechat.html`

### Step 8: Publish
1. Open `wechat.html` in browser
2. Select all (Cmd+A / Ctrl+A)
3. Copy (Cmd+C / Ctrl+C)
4. Paste into 微信公众号 editor
5. Preview and publish

## Tips

### For Best Results

**Always reference the style guide** - It contains extensive examples from your published articles

**Be specific** - Name companies, products, people, include URLs

**Use the templates** - Each article type has a proven structure:
- Debunking (永动机模式)
- Industry Critique (云厂商模式)
- True vs False Problems (伪问题模式)
- Systematic Deconstruction (基础架构部模式)
- Explorative AI Use Case (探索性AI应用案例)

**Use language patterns** - The guide has 40+ example phrases to use:
- "实际上，..."
- "换句话说，..."
- "试举一例，..."
- "所谓专家们"
- "说句难听的，..."

**Mix theory and practice** - Reference Shannon, physics, CS principles + real company examples

**No emoji** - Analyzed articles have ZERO emoji

### Quick Checks

Before publishing, verify:
- [ ] Named 3-5 companies/products
- [ ] Named specific people
- [ ] Included URLs
- [ ] Used concrete metrics
- [ ] At least one analogy
- [ ] Rhetorical questions
- [ ] Personal voice ("我", experience)
- [ ] Engagement ending
- [ ] NO emoji

## Files Reference

### Read These
- `templates/style_guide.md` - Complete style reference
- `Examples/` - Original HTML articles for reference

### Modify These
- `articles/[name]/final.md` - Your article markdown

### Run These
- `python utils/html_converter.py <markdown-file>` - Convert to HTML

### Don't Modify
- `templates/wechat_styles.css` - Auto-extracted styles
- `templates/wechat_template.html` - Auto-generated template
- `utils/extract_style.py` - One-time extraction tool
- `utils/html_converter.py` - Conversion tool

## What's Next?

**To start writing**: Use `/outline` with your topic

**To learn the style**: Read `templates/style_guide.md`

**To see examples**: Look at files in `Examples/`

**For help**: All commands have detailed instructions
