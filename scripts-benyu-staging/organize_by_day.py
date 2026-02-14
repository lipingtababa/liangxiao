#!/usr/bin/env python3
"""
Organize filtered messages by day for analysis
"""

import json
from pathlib import Path
from collections import defaultdict

# Configuration
INPUT_FILE = Path("/Users/Shared/code/benyu/my_wechat_messages.json")
OUTPUT_DIR = Path("/Users/Shared/code/benyu/daily_messages")

def organize_by_day():
    """Organize messages by day and save each day separately"""

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load all messages
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    messages = data['messages']

    # Group messages by date
    messages_by_day = defaultdict(list)
    for msg in messages:
        date = msg.get('date')
        messages_by_day[date].append(msg)

    # Save each day's messages
    print(f"Organizing {len(messages)} messages into {len(messages_by_day)} days")
    print(f"Output directory: {OUTPUT_DIR}\n")

    for date in sorted(messages_by_day.keys()):
        day_messages = messages_by_day[date]

        # Extract text content only
        text_messages = []
        for msg in day_messages:
            content = msg.get('content', '')
            if content:  # Only include messages with actual content
                text_messages.append({
                    'time': msg.get('time'),
                    'content': content,
                    'type': msg.get('type'),
                    'talker': msg.get('talker')
                })

        # Save day's data
        day_data = {
            'date': date,
            'total_messages': len(day_messages),
            'text_messages': len(text_messages),
            'messages': text_messages
        }

        output_file = OUTPUT_DIR / f"{date}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(day_data, f, ensure_ascii=False, indent=2)

        print(f"{date}: {len(day_messages)} total, {len(text_messages)} with text")

    print(f"\n{'='*60}")
    print(f"Organization complete!")
    print(f"Files saved to: {OUTPUT_DIR}")
    print(f"{'='*60}")

if __name__ == "__main__":
    organize_by_day()
