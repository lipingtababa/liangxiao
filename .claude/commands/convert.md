---
description: Convert markdown article to WeChat-compatible HTML
---

You are helping convert a markdown article to WeChat-compatible HTML format.

# Instructions

1. **Ask for the markdown file**: Request the path to the markdown file (or the article can be in `articles/[name]/final.md`)

2. **Verify the file exists**: Check that the markdown file is readable

3. **Run the conversion**:
   ```bash
   python utils/html_converter.py <path/to/article.md>
   ```

4. **Explain the output**:
   - The HTML file will be created in the same directory as the markdown file
   - Default name: `wechat.html`
   - The HTML includes:
     - Inline CSS styles (WeChat doesn't support external CSS)
     - Proper font families (PingFang SC, etc.)
     - Styled headers, blockquotes, code, lists
     - Mobile-friendly viewport settings

5. **Next steps for the user**:
   ```
   1. Open the generated wechat.html file in a web browser
   2. Select all content (Cmd+A or Ctrl+A)
   3. Copy (Cmd+C or Ctrl+C)
   4. Paste into 微信公众号 editor
   5. Preview and publish
   ```

6. **Troubleshooting**: If conversion fails:
   - Check if markdown file exists
   - Verify dependencies are installed: `pip install -r requirements.txt`
   - Check if templates/wechat_styles.css exists
   - Look for markdown syntax errors

# Example Usage

For an article at `articles/my-article/final.md`:

```bash
python utils/html_converter.py articles/my-article/final.md
```

This creates: `articles/my-article/wechat.html`

# Optional: Custom Output Path

You can specify a custom output path:

```bash
python utils/html_converter.py articles/my-article/final.md articles/my-article/custom.html
```

# Important

- Ensure the markdown is finalized before conversion
- The conversion applies WeChat-specific styling automatically
- Images in markdown will be included (but verify paths)
- The HTML is optimized for copying into WeChat editor, not for direct web hosting
