#!/usr/bin/env python3
"""
Generate a file with daily messages prepared for Claude analysis
Outputs weeks in batches for systematic analysis
"""

import json
from pathlib import Path
from datetime import datetime

# Configuration
DAILY_DIR = Path("/Users/Shared/code/benyu/daily_messages")
OUTPUT_DIR = Path("/Users/Shared/code/benyu/weekly_batches")

def get_week_number(date_str):
    """Get ISO week number from date string"""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.isocalendar()[1]  # Returns week number

def create_weekly_batches():
    """Organize days into weekly batches for analysis"""

    OUTPUT_DIR.mkdir(exist_ok=True)

    json_files = sorted(DAILY_DIR.glob("*.json"))
    weekly_batches = {}

    print(f"Organizing {len(json_files)} days into weekly batches\n")

    for json_file in json_files:
        date = json_file.stem
        week_num = get_week_number(date)
        year = date[:4]
        week_key = f"{year}-W{week_num:02d}"

        if week_key not in weekly_batches:
            weekly_batches[week_key] = []

        with open(json_file, 'r', encoding='utf-8') as f:
            day_data = json.load(f)

        if day_data['text_messages'] > 0:
            weekly_batches[week_key].append({
                'date': date,
                'message_count': day_data['text_messages'],
                'messages': day_data['messages']
            })

    # Save each week to a separate file
    for week_key in sorted(weekly_batches.keys()):
        week_data = weekly_batches[week_key]
        output_file = OUTPUT_DIR / f"{week_key}.json"

        week_summary = {
            'week': week_key,
            'days': len(week_data),
            'total_messages': sum(d['message_count'] for d in week_data),
            'daily_data': week_data
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(week_summary, f, ensure_ascii=False, indent=2)

        print(f"{week_key}: {len(week_data)} days, {week_summary['total_messages']} messages")

    print(f"\n{'='*60}")
    print(f"Weekly batches created!")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Total weeks: {len(weekly_batches)}")
    print(f"{'='*60}")

    return weekly_batches

if __name__ == "__main__":
    create_weekly_batches()
