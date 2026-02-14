#!/usr/bin/env python3
"""
Extract article-worthy insights and opinions from daily messages
Focus on: technical insights, opinions, critiques, analysis
Ignore: daily life, casual chat, simple reactions
"""

import json
from pathlib import Path

# Configuration
DAILY_DIR = Path("/Users/Shared/code/benyu/daily_messages")
OUTPUT_FILE = Path("/Users/Shared/code/benyu/article_insights.md")

def is_article_worthy(message):
    """
    Determine if a message contains article-worthy content
    Returns score: higher = more likely to be article material
    """
    content = message.get('content', '')

    if not content or len(content) < 15:  # Too short
        return 0

    score = 0

    # Indicators of article-worthy content
    article_indicators = [
        ('我认为', 3), ('我觉得', 2), ('我的经验', 4), ('我发现', 3),
        ('问题在于', 3), ('关键是', 3), ('本质上', 4),
        ('这说明', 2), ('这意味着', 3), ('这反映', 3),
        ('应该', 2), ('不应该', 2), ('必须', 2),
        ('错误', 2), ('正确', 2), ('误区', 3),
        ('原因', 2), ('为什么', 2), ('怎么', 1),
        ('软件', 1), ('代码', 1), ('系统', 1), ('架构', 2),
        ('产品', 1), ('设计', 1), ('工程', 2),
        ('流程', 2), ('方法', 2), ('模式', 2),
    ]

    for indicator, weight in article_indicators:
        if indicator in content:
            score += weight

    # Technical terms boost
    tech_terms = ['AI', 'LLM', 'API', 'GPT', 'Claude', 'token', 'FDE', 'Palantir',
                   'kubernetes', 'Docker', 'pipeline', 'frontend', 'backend', 'database']

    for term in tech_terms:
        if term.lower() in content.lower():
            score += 1

    # Long messages tend to be more substantial
    if len(content) > 100:
        score += 2
    if len(content) > 200:
        score += 2

    # Negative indicators (casual chat)
    casual_patterns = [
        ('[', 1),  # Emoji patterns like [捂脸]
        ('哈哈', 2), ('😂', 2), ('👍', 2),
        ('不错', 1), ('好的', 1), ('谢谢', 1),
    ]

    for pattern, penalty in casual_patterns:
        if pattern in content:
            score -= penalty

    return max(0, score)

def extract_insights_by_day():
    """Extract article-worthy insights organized by day"""

    json_files = sorted(DAILY_DIR.glob("*.json"))

    print(f"Analyzing {len(json_files)} days for article-worthy content\n")

    all_insights = []

    for json_file in json_files:
        date = json_file.stem

        with open(json_file, 'r', encoding='utf-8') as f:
            day_data = json.load(f)

        messages = day_data.get('messages', [])

        # Score and filter messages
        scored_messages = []
        for msg in messages:
            score = is_article_worthy(msg)
            if score >= 5:  # Threshold for article-worthiness
                scored_messages.append({
                    'content': msg['content'],
                    'time': msg['time'],
                    'score': score
                })

        if scored_messages:
            # Sort by score (descending)
            scored_messages.sort(key=lambda x: x['score'], reverse=True)

            all_insights.append({
                'date': date,
                'count': len(scored_messages),
                'insights': scored_messages
            })

            print(f"{date}: {len(scored_messages)} insights found")

    # Generate markdown report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Article-Worthy Insights from WeChat Messages\n\n")
        f.write(f"**Extracted from messages by 马工 (wxid_xsrpijjy5ljx22)**\n\n")
        f.write(f"Total days with insights: {len(all_insights)}\n\n")
        f.write("---\n\n")

        for day in all_insights:
            f.write(f"## {day['date']} ({day['count']} insights)\n\n")

            for idx, insight in enumerate(day['insights'], 1):
                f.write(f"### Insight {idx} (Score: {insight['score']})\n")
                f.write(f"**Time:** {insight['time']}\n\n")
                f.write(f"{insight['content']}\n\n")
                f.write("---\n\n")

    print(f"\n{'='*60}")
    print(f"Insights extraction complete!")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"Total days with insights: {len(all_insights)}")
    print(f"Total insights: {sum(day['count'] for day in all_insights)}")
    print(f"{'='*60}")

    return all_insights

if __name__ == "__main__":
    extract_insights_by_day()
