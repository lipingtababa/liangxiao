#!/usr/bin/env python3
"""
Analyze daily WeChat messages to extract topics and insights
This script prepares batches of messages for analysis
"""

import json
from pathlib import Path
from collections import Counter
import re

# Configuration
DAILY_DIR = Path("/Users/Shared/code/benyu/daily_messages")
OUTPUT_FILE = Path("/Users/Shared/code/benyu/daily_analysis_batches.txt")

def extract_keywords(text):
    """Extract potential keywords from Chinese text"""
    # Remove common patterns and extract meaningful words
    # This is a simple approach - for better results, use jieba or similar
    keywords = []

    # Common technical terms and topics (case insensitive English)
    tech_patterns = [
        r'AI', r'LLM', r'GPT', r'Claude', r'ChatGPT', r'API',
        r'token', r'FDE', r'Palantir', r'OpenAI',
        r'kubernetes', r'Docker', r'CD', r'pipeline',
        r'frontend', r'backend', r'database', r'db',
    ]

    for pattern in tech_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            keywords.append(pattern.lower())

    return keywords

def analyze_day(date, messages_file):
    """Analyze a single day's messages"""
    with open(messages_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    messages = data.get('messages', [])

    if not messages:
        return None

    # Combine all content
    all_content = '\n'.join([msg.get('content', '') for msg in messages])

    # Extract keywords
    keywords = extract_keywords(all_content)
    keyword_counts = Counter(keywords)

    # Prepare batch entry
    batch_entry = {
        'date': date,
        'message_count': len(messages),
        'total_chars': len(all_content),
        'keywords': dict(keyword_counts.most_common(10)),
        'sample_messages': messages[:5] if len(messages) > 5 else messages,  # First 5 messages as sample
        'all_content': all_content[:2000]  # First 2000 chars for context
    }

    return batch_entry

def create_analysis_batches():
    """Create batches of days for analysis"""

    json_files = sorted(DAILY_DIR.glob("*.json"))

    print(f"Analyzing {len(json_files)} days of messages\n")

    batch_data = []

    for json_file in json_files:
        date = json_file.stem  # e.g., "2025-09-15"
        entry = analyze_day(date, json_file)

        if entry:
            batch_data.append(entry)
            print(f"{date}: {entry['message_count']} messages, Keywords: {list(entry['keywords'].keys())[:5]}")

    # Save batches for manual analysis
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DAILY MESSAGE ANALYSIS - BATCHES FOR REVIEW\n")
        f.write("=" * 80 + "\n\n")

        for entry in batch_data:
            f.write(f"\n{'='*80}\n")
            f.write(f"Date: {entry['date']}\n")
            f.write(f"Messages: {entry['message_count']}\n")
            f.write(f"Keywords: {entry['keywords']}\n")
            f.write(f"{'-'*80}\n")
            f.write(f"Content Preview:\n{entry['all_content']}\n")
            f.write(f"{'='*80}\n\n")

    print(f"\n{'='*60}")
    print(f"Batch analysis prepared!")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"Total days analyzed: {len(batch_data)}")
    print(f"{'='*60}")

    return batch_data

if __name__ == "__main__":
    create_analysis_batches()
