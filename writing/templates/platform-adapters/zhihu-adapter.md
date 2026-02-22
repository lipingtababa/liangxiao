# Zhihu (知乎) Adapter

## Platform characteristics

- Audience: educated Chinese (students, professionals, knowledge workers)
- Format: long-form article — full markdown supported, headings, bold, links
- Length: 1500-4000 chars optimal; longer than XHS, similar to WeChat
- Tone: analytical, credible — Zhihu readers are skeptical and well-read
- Links: allowed (but external links may reduce algorithm reach)
- Images: optional but helpful; inline images supported

## Adaptation rules

1. **Title**: Keep close to the original Chinese title. Zhihu titles reward precision and intellectual promise. Avoid clickbait but do not be bland. Can be slightly longer than WeChat.

2. **Content**: Near-identical to the original draft. Zhihu supports full markdown:
   - Keep all `##` headings
   - Keep bold text
   - Convert reference list to inline links where possible
   - Remove WeChat-specific formatting (e.g. coloured highlight boxes)

3. **Opening tweak**: Add a one-line framing sentence at the very top if the article starts mid-argument. Zhihu readers often arrive cold (not via follow), so context helps.

4. **No fabrication**: Zhihu community aggressively fact-checks. Only real data, real sources.

5. **Ending**: Add a genuine discussion question at the end — Zhihu rewards comment engagement.

## Output format

Full markdown article, clean and ready to paste into Zhihu editor.

No special character limits. Maintain original structure.

Add at the very end:
```
---
*欢迎在评论区分享你的看法。*
```
