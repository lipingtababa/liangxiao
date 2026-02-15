---
description: Publish an English article to magong.se
---

You are publishing an English article to magong.se. This is the final step after `/english` has produced a translated post in `posts/`.

# Instructions

1. **Identify the post to publish**: Ask the user which post in `posts/` to publish, or accept a file path. Read the post fully.

2. **Pre-publish checklist** — verify each item, fix issues inline:

### Front Matter Validation
- [ ] `title` exists and is concise (under 80 chars)
- [ ] `date` exists and is valid YYYY-MM-DD format
- [ ] `author` is "MaGong"
- [ ] `category` exists and matches existing categories (check other posts in `posts/`)
- [ ] `description` exists and is a compelling one-sentence summary (100-160 chars for SEO)
- [ ] `tags` array exists (can be empty)

### Content Quality
- [ ] No WeChat links (`mp.weixin.qq.com`) — these are inaccessible outside China
- [ ] No broken markdown (unclosed links, malformed headers)
- [ ] No emoji
- [ ] No placeholder text (`[需要`, `TODO`, `TBD`)
- [ ] Ends with `---` followed by `*Originally written in Chinese. Translated by the author.*`
- [ ] No "Translation Notes" section left in (that's for author review only)
- [ ] Article has at least 3 `##` subheadings
- [ ] No duplicate `#` title (front matter `title` is enough, remove `# Title` if duplicated)

### File Naming
- [ ] Filename is kebab-case: `my-article-title.md`
- [ ] No Chinese characters in filename
- [ ] No spaces in filename

3. **Fix any issues found** — edit the file directly. Report what you fixed.

4. **Enhance SEO metadata** — run:
```bash
node scripts/website/enhance-seo-metadata.js
```

5. **Build verification** — run:
```bash
npm run build
```
If build fails, diagnose and fix. Common issues:
- Front matter parsing errors
- Image references to missing files
- Markdown syntax errors

6. **Local preview** (optional, if user wants):
```bash
npm run dev
```
Then tell the user to check `http://localhost:3000` and the specific post URL.

7. **Commit and push** — when the user confirms:
```bash
git add posts/[filename].md
git commit -m "feat: publish [article title]"
git push
```
Vercel auto-deploys from the GitHub push. No manual deployment needed.

8. **Post-publish verification**:
- Tell the user the expected URL: `https://magong.se/posts/[slug]`
- Remind them to check the live site after Vercel deploys (usually 1-2 minutes)

# Important

- This skill assumes `/english` has already been run and a post exists in `posts/`
- Do NOT modify the article's content/argument — only fix formatting, metadata, and technical issues
- If you find content problems (fabricated data, missing sources), flag them but don't silently fix
- The post filename (without `.md`) becomes the URL slug: `posts/my-article.md` → `magong.se/posts/my-article`
- Always verify the build passes before committing
