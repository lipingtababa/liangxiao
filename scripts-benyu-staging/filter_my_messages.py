#!/usr/bin/env python3
"""
Filter WeChat messages by a specific sender ID (wxid_xsrpijjy5ljx22)
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Configuration
WECHAT_DATA_DIR = Path("/Users/Shared/code/wechat-view/data")
MY_WXID = "wxid_xsrpijjy5ljx22"
OUTPUT_FILE = Path("/Users/Shared/code/benyu/my_wechat_messages.json")

def filter_my_messages():
    """Filter all messages sent by my WeChat ID"""
    all_my_messages = []
    total_files = 0
    total_my_messages = 0

    # Get all JSON files sorted by date
    json_files = sorted(WECHAT_DATA_DIR.glob("*.json"))

    print(f"Found {len(json_files)} data files")
    print(f"Filtering messages from: {MY_WXID}\n")

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Filter messages where sender matches my wxid
            my_messages = [
                msg for msg in data.get('messages', [])
                if msg.get('sender') == MY_WXID
            ]

            if my_messages:
                total_files += 1
                total_my_messages += len(my_messages)
                print(f"{json_file.name}: {len(my_messages)} messages")

                # Add each message with date context
                for msg in my_messages:
                    msg['date'] = data['date']
                    all_my_messages.append(msg)

        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")

    # Save filtered messages
    output_data = {
        "wxid": MY_WXID,
        "total_messages": total_my_messages,
        "date_range": {
            "first": json_files[0].stem if json_files else None,
            "last": json_files[-1].stem if json_files else None
        },
        "extracted_at": datetime.now().isoformat(),
        "messages": all_my_messages
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Extraction complete!")
    print(f"Total files processed: {len(json_files)}")
    print(f"Files with my messages: {total_files}")
    print(f"Total messages from {MY_WXID}: {total_my_messages}")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"{'='*60}")

    return total_my_messages

if __name__ == "__main__":
    filter_my_messages()
