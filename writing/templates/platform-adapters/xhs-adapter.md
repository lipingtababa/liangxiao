# Xiaohongshu (小红书) Adapter

## Platform characteristics

- Audience: young urban Chinese (18-35), lifestyle + knowledge content
- Format: note = title + body text + images (3-9 images optimal)
- Body limit: 1000 chars max; sweet spot 300-600 chars
- Title limit: 20 chars max
- Hashtags: 5-8 tags, appended at end, critical for discovery
- No hyperlinks allowed anywhere
- Tone: personal, first-person, slightly casual — more "分享" energy than essay

## Condensation rules

1. **Title**: Extract the sharpest, most curiosity-triggering phrase from the article. ≤20 chars. No punctuation at end. Must work as standalone hook.

2. **Body**: Condense entire article to 3-5 punchy paragraphs:
   - Open with the core tension or surprising finding (1-2 sentences)
   - State the main argument or insight (2-3 sentences)
   - Give 1 concrete example or data point (keep it real, no fabrication)
   - End with a question or provocation that invites comments

3. **Tone shift**: XHS readers scroll fast. Cut all academic framing. Make it feel like a smart friend sharing a hot take, not a columnist writing a think piece.

4. **Remove**: all markdown links, reference lists, section headings, footnotes

## Hashtag generation rules

Generate 5-8 hashtags:
- 2-3 topic hashtags: broad topic (e.g. #AI编程 #人工智能 #科技)
- 2-3 niche hashtags: specific angle (e.g. #Cursor #AIcoding #程序员)
- 1-2 emotion/behaviour hashtags: (e.g. #程序员必看 #深度思考 #反直觉)

Format: append at end of body, each prefixed with `#`, space-separated.

## Output format

```
[Title — ≤20 chars]

[Body — 300-600 chars, no links, no headings]

#tag1 #tag2 #tag3 #tag4 #tag5
```

## Images

- Cover image: cover-xhs.jpg (3:4 portrait, already generated)
- Section images: section-1.jpg, section-2.jpg, section-3.jpg (1:1 square)
- XHS shows images as a swipeable gallery — order matters
- Recommended order: cover-xhs → section-1 → section-2 → section-3
