# Source Materials

This directory contains external reference materials used for article writing. These materials are **NOT** committed to git.

## Contents

### wechat-view/ (symlink)

- **Location**: Symlinked to `../wechat-view`
- **Type**: WeChat chatlog daily reporter
- **Content**: 88+ JSON files containing daily chat logs (2025-09-15 onwards)
- **Purpose**: Real conversation data for finding authentic examples, quotes, and scenarios

## Usage

### Finding Real Examples

Instead of fabricating examples, search the chat logs for real conversations:

```bash
# Search for specific topics
grep -r "关键词" source-materials/wechat-view/data/

# View a specific day's chat
cat source-materials/wechat-view/data/2025-11-27.json | jq
```

### Important Reminders

Following the article writing rules in `CLAUDE.md`:

✅ **DO**: Use real quotes/examples from these chat logs
✅ **DO**: Cite actual conversations with dates
✅ **DO**: Extract genuine user feedback and scenarios

❌ **NEVER**: Fabricate examples when real data exists
❌ **NEVER**: Modify quotes without noting the change
❌ **NEVER**: Present estimated data as facts

## Adding More Source Materials

To add additional reference materials:

```bash
cd /Users/Shared/code/benyu/source-materials
ln -s /path/to/your/reference reference-name
```

All contents in this directory are gitignored.
