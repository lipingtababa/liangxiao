#!/usr/bin/env python3
"""
Prepare chat data for LLM summarization.

Converts JSON chat data to a simple, token-efficient text format.

Usage:
    python3 prepare_chat.py <chatroom_dir> [date]
    python3 prepare_chat.py 87714869_AI_Coding 2026-01-17
    python3 prepare_chat.py 87714869_AI_Coding  # defaults to today

Output:
    /tmp/chat-{chatroom_dir}-{date}.txt

Format:
    [HH:MM] sender: content
    [HH:MM] ★self: content
    [HH:MM] sender: content [reply: snippet...]
"""

import json
import os
import sys
from datetime import date

# Chat data location
CHAT_BASE = '/Users/Shared/code/aichat/chats'

def load_messages(chatroom_dir: str, target_date: str) -> list:
    """Load messages from JSON file."""
    path = os.path.join(CHAT_BASE, chatroom_dir, f'{target_date}.json')
    if not os.path.exists(path):
        print(f"Error: No data for {target_date} in {chatroom_dir}", file=sys.stderr)
        sys.exit(1)

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_message(msg: dict) -> str:
    """Format a single message to simple text: author: content"""
    msg_type = msg.get('type')

    # Get sender
    if msg.get('isSelf'):
        sender = '★我'
    else:
        sender = msg.get('senderName', 'unknown')

    # Handle different message types
    if msg_type == 3:  # Image
        return f'{sender}: [图片]'
    elif msg_type == 43:  # Video
        return f'{sender}: [视频]'
    elif msg_type == 34:  # Voice
        return f'{sender}: [语音]'
    elif msg_type == 47:  # Sticker
        return None  # Skip stickers

    content = msg.get('content', '')
    if not content:
        return None

    # Clean content (remove newlines for single-line format)
    content = content.replace('\n', ' ').strip()

    # Skip very short or emoji-only messages
    if len(content) < 3:
        return None
    if content.startswith('[') and content.endswith(']') and len(content) < 20:
        return None
    if 'recalled a message' in content:
        return None

    return f'{sender}: {content}'

def prepare_chat(chatroom_dir: str, target_date: str) -> str:
    """Prepare chat data and return output path."""
    messages = load_messages(chatroom_dir, target_date)

    lines = []
    for msg in messages:
        line = format_message(msg)
        if line:
            lines.append(line)

    # Get chatroom name from first message if available
    chatroom_name = chatroom_dir
    if messages and messages[0].get('talkerName'):
        chatroom_name = messages[0]['talkerName']

    # Add header
    header = f"# {chatroom_name} - {target_date}\n# Messages: {len(lines)}\n\n"

    output = header + '\n'.join(lines)

    # Write to /tmp
    output_path = f'/tmp/chat-{chatroom_dir}-{target_date}.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

    return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: prepare_chat.py <chatroom_dir> [date]")
        print("Example: prepare_chat.py 87714869_AI_Coding 2026-01-17")
        print("\nAvailable chatrooms:")
        for d in sorted(os.listdir(CHAT_BASE)):
            if os.path.isdir(os.path.join(CHAT_BASE, d)):
                print(f"  {d}")
        sys.exit(1)

    chatroom_dir = sys.argv[1]
    target_date = sys.argv[2] if len(sys.argv) > 2 else date.today().isoformat()

    # Validate chatroom exists
    chatroom_path = os.path.join(CHAT_BASE, chatroom_dir)
    if not os.path.isdir(chatroom_path):
        print(f"Error: Chatroom not found: {chatroom_dir}", file=sys.stderr)
        sys.exit(1)

    output_path = prepare_chat(chatroom_dir, target_date)
    print(f"Prepared: {output_path}")

if __name__ == '__main__':
    main()
