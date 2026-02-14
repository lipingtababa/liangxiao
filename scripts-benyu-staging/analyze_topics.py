#!/usr/bin/env python3
"""
Analyze extracted insights and group by topics/themes for article writing
"""

import json
from pathlib import Path
from collections import defaultdict
import re

# Configuration
INSIGHTS_FILE = Path("/Users/Shared/code/benyu/article_insights.md")
OUTPUT_FILE = Path("/Users/Shared/code/benyu/topic_analysis.md")

# Define topic patterns (keywords that indicate specific topics)
TOPIC_PATTERNS = {
    'AI编程与工具': [
        'AI', 'LLM', 'GPT', 'Claude', 'ChatGPT', 'Cursor',
        'AI辅助', 'prompt', '编程', '代码', 'IDE',
        'agent', '智能体', 'token'
    ],
    '软件工程方法论': [
        '敏捷', '瀑布', '设计', '架构', '测试', '流程',
        '方法', '迭代', '开发', '工程', '需求',
        '故事', 'story', 'bmad'
    ],
    '产品与商业': [
        '产品', '商业', '市场', '客户', '用户', '销售',
        '公司', '创业', '竞争', '模式', '价值'
    ],
    '技术架构与基础设施': [
        'kubernetes', 'Docker', 'pipeline', 'CD', 'CI',
        '容器', '部署', '环境', '数据库', '架构',
        'frontend', 'backend', 'API'
    ],
    '行业观察与评论': [
        'Palantir', 'OpenAI', 'FDE', '硅谷', '美国', '中国',
        '国防', '军工', '政府', '腐败'
    ],
    '学习与教育': [
        '学习', '教育', '家教', '培训', '知识', 'L&D'
    ],
    '云计算与DevOps': [
        '云计算', '云', 'AWS', '阿里云', 'DevOps', '运维',
        '自动化', '监控'
    ]
}

def extract_insights_from_md():
    """Extract insights from markdown file"""
    with open(INSIGHTS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    insights = []
    current_date = None
    current_insight = None

    for line in content.split('\n'):
        # Match date headers
        if line.startswith('## 2025-'):
            current_date = line.split()[1]

        # Match insight headers
        elif line.startswith('### Insight'):
            if current_insight and current_insight['content']:
                insights.append(current_insight)
            score_match = re.search(r'Score: (\d+)', line)
            current_insight = {
                'date': current_date,
                'score': int(score_match.group(1)) if score_match else 0,
                'content': ''
            }

        # Match time
        elif line.startswith('**Time:**') and current_insight:
            current_insight['time'] = line.replace('**Time:**', '').strip()

        # Collect content
        elif current_insight and line and not line.startswith('#') and not line.startswith('---'):
            current_insight['content'] += line + '\n'

    # Add last insight
    if current_insight and current_insight['content']:
        insights.append(current_insight)

    return insights

def categorize_insight(content):
    """Determine which topics an insight belongs to"""
    topics = []

    for topic, keywords in TOPIC_PATTERNS.items():
        for keyword in keywords:
            if keyword.lower() in content.lower():
                topics.append(topic)
                break  # One match per topic is enough

    return topics if topics else ['其他']

def analyze_topics():
    """Analyze insights and group by topics"""

    insights = extract_insights_from_md()

    print(f"Analyzing {len(insights)} insights for topic patterns\n")

    # Group insights by topic
    topic_insights = defaultdict(list)

    for insight in insights:
        topics = categorize_insight(insight['content'])

        for topic in topics:
            topic_insights[topic].append(insight)

    # Generate topic analysis report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Topic Analysis for Article Writing\n\n")
        f.write(f"**Based on {len(insights)} insights from WeChat messages**\n\n")
        f.write("---\n\n")

        # Summary table
        f.write("## Topic Overview\n\n")
        f.write("| Topic | Insights Count |\n")
        f.write("|-------|----------------|\n")

        for topic in sorted(topic_insights.keys(), key=lambda t: len(topic_insights[t]), reverse=True):
            f.write(f"| {topic} | {len(topic_insights[topic])} |\n")

        f.write("\n---\n\n")

        # Detailed insights per topic
        for topic in sorted(topic_insights.keys(), key=lambda t: len(topic_insights[t]), reverse=True):
            insights_list = topic_insights[topic]
            f.write(f"## {topic} ({len(insights_list)} insights)\n\n")

            # Sort by score
            insights_list.sort(key=lambda x: x['score'], reverse=True)

            for idx, insight in enumerate(insights_list[:20], 1):  # Top 20 per topic
                f.write(f"### {idx}. {insight['date']} (Score: {insight['score']})\n\n")
                f.write(f"{insight['content'].strip()}\n\n")
                f.write("---\n\n")

    print(f"\n{'='*60}")
    print(f"Topic analysis complete!")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"\nTopic breakdown:")
    for topic in sorted(topic_insights.keys(), key=lambda t: len(topic_insights[t]), reverse=True):
        print(f"  {topic}: {len(topic_insights[topic])} insights")
    print(f"{'='*60}")

if __name__ == "__main__":
    analyze_topics()
