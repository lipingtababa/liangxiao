---
description: Publish article to all platforms (WeChat, XHS, Zhihu, magong.se)
---

You are publishing a converted article to one or more platforms.

**Prerequisite**: `/convert` must have been run first. The article directory should contain:
`weixin.html`, `xhs.md`, `zhihu.md`, `english.md`, `images/`

# Instructions

## Step 1 — Locate the article

Find the article directory (same as /convert — detect from current working directory or ask).
Verify all required files exist. If any are missing, tell the user to run `/convert` first.

## Step 2 — Ask which platforms

Ask: "Publish to which platforms?"
Options: **All** / WeChat / Xiaohongshu / Zhihu / magong.se (multi-select allowed)

If the user says "all" or doesn't specify, use all four.

## Step 3 — Publish to each platform (one by one)

**CRITICAL**: Publish platforms sequentially (one at a time), not in parallel.

For each selected platform:
1. Complete the full publishing workflow for that platform
2. Get user confirmation or completion signal before moving to the next
3. Report success or failure clearly before proceeding

**Sequential order** (if all selected):
1. magong.se (automated, quickest)
2. WeChat (manual paste + publish)
3. Xiaohongshu (manual upload + publish)
4. Zhihu (manual paste + publish)

This allows the user to work through each platform methodically and pause if needed.

---

### magong.se (English blog)

1. Copy `english.md` → `magong/posts/[slug].md`
   - Slug: kebab-case version of the English title from frontmatter
   - e.g. `english.md` → `magong/posts/why-ai-coding-fails-without-constraints.md`

2. Copy generated images to `magong/public/images/posts/[slug]/`:
   ```bash
   mkdir -p magong/public/images/posts/[slug]
   cp <article_dir>/images/cover-weixin.jpg magong/public/images/posts/[slug]/cover.jpg
   ```
   Update any image references in the post if needed.

3. Run pre-publish checks (from `.claude/commands/publish.md` original):
   - frontmatter: title, date, author=MaGong, category, description, tags
   - No WeChat links, no emoji, no placeholders
   - No "Translation Notes" section left in
   - At least 3 `##` subheadings

4. Enhance SEO metadata (run from `magong/`):
   ```bash
   cd magong && npm run seo:enhance
   ```

5. Build verification (run from `magong/`):
   ```bash
   cd magong && npm run build
   ```
   Fix any errors before proceeding.

6. Commit and push:
   ```bash
   git add magong/posts/[slug].md magong/public/images/posts/[slug]/
   git commit -m "feat: publish [article title in English]

   Generated with [Claude Code](https://claude.ai/code)
   via [Happy](https://happy.engineering)

   Co-Authored-By: Claude <noreply@anthropic.com>
   Co-Authored-By: Happy <yesreply@happy.engineering>"
   git push
   ```

7. Report: `✓ magong.se — live at https://magong.se/posts/[slug] (Vercel deploying, ~2 min)`

---

### WeChat (微信公众号)

Open the WeChat MP new article editor in Edge:

```bash
open -a "Microsoft Edge" "https://mp.weixin.qq.com/cgi-bin/appmsgEdit?action=edit&isNew=1&type=10"
```

Then tell the user:
"WeChat editor is open in Edge. The article content is in `weixin.html` — open it in a browser, select all, copy, and paste into the editor. Cover image: `images/cover-weixin.jpg`. Click 发布 when done."

Report: `✓ WeChat — editor opened, ready for manual paste and publish`

---

### Xiaohongshu (小红书)

Open the XHS publish page in Edge:

```bash
open -a "Microsoft Edge" "https://www.xiaohongshu.com/publish/publish"
```

Read `xhs.md` and display the full content to the user clearly — title on one line, body below.

Also tell the user which images to upload (in order):
1. `images/cover-xhs.jpg` (cover)
2. `images/section-1.jpg`
3. `images/section-2.jpg`
4. `images/section-3.jpg` (if exists)

Tell the user: "XHS publish page is open in Edge. Copy the title and body above, upload the images in order, paste content, add hashtags, and publish."

Report: `✓ Xiaohongshu — editor opened, ready for manual publish`

---

### Zhihu (知乎)

Open Zhihu write page in the default browser:
```bash
open "https://zhuanlan.zhihu.com/write"
```

Read `zhihu.md` content. Display it to the user and say:
"Zhihu editor is open. The article content is shown above — please paste it (Cmd+V after clicking into the editor) and click 发布."

Then wait for user confirmation.

Report: `✓ Zhihu — ready for manual publish`

---

## Step 4 — Final report

After each platform, confirm before moving to the next. After all selected platforms are complete:

```
✓ Publishing complete: [article title]

Platform results:
  magong.se      ✓  https://magong.se/posts/[slug]
  WeChat         ✓  Draft published
  Xiaohongshu    ✓  Published
  Zhihu          ✓  Manually published

```

If the user opted for selective publishing (not all platforms), report only the platforms that were published.

# Important

- **Sequential publishing**: Complete one platform fully before moving to the next
- **User confirmation**: After each platform, confirm success before proceeding to the next
- **Selective publishing**: It's OK to publish to only some platforms (e.g., just magong.se, or WeChat + Zhihu)
- Always run magong.se build check before git push — never push a broken build
- WeChat: do NOT auto-click publish — always leave final publish action to the user
- Zhihu: browser automation is too risky (account ban) — always manual paste
- If XHS login fails, tell the user to run `xhs-mcp login` and try again
- If any platform fails, report it clearly and ask whether to continue with the remaining platforms
