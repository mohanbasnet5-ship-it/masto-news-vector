# Manual News Post Generator

When the daemon is down or Facebook's circuit breaker is active, use this tool to generate formatted posts for manual copy-paste into Facebook.

## Quick Start

```bash
cd nepalpulse
python3 manual_post_generator.py [count] [format]
```

## Usage

### Generate 3 posts as plain text (default)
```bash
python3 manual_post_generator.py 3 text
```

### Generate 5 posts as markdown
```bash
python3 manual_post_generator.py 5 markdown
```

### Generate 1 post as JSON (for testing Graph API)
```bash
python3 manual_post_generator.py 1 json
```

## Output Formats

### Text Format
- Clean, easy-to-read blocks
- Each post separated by `====` dividers
- Ready to copy-paste directly into Facebook
- **Best for:** Manual Facebook posting

```
======================================================================
POST #1
======================================================================

{headline}

{body}

{nepali}

{url}

======================================================================
```

### Markdown Format
- Formatted for GitHub/documentation
- Includes source name and article ID
- Useful for documentation/archiving
- **Best for:** Keeping records, sharing in chat

```
## Post #1: {source}

**{headline}**

{body}

*{nepali}*

[Read full story]({url})

---
```

### JSON Format
- Structured data for programmatic use
- Includes metadata (article_id, source, region, timestamp)
- **Best for:** Graph API testing, integrations

```json
[
  {
    "article_id": 806,
    "source": "BBC South Asia",
    "region": "global",
    "message": "...",
    "link": "...",
    "generated_at": "2026-05-13T19:08:21+05:45"
  }
]
```

## Workflow During Circuit Breaker

1. **Daemon is down, circuit is active:**
   ```bash
   python3 manual_post_generator.py 5 text
   ```

2. **Copy first post from output**

3. **Go to Facebook, paste into status**

4. **Repeat for next posts (wait ~2–3 min between posts to avoid looking like spam)**

5. **Mark articles as posted** (optional — system will skip them on daemon restart)

## Marking Posts as Manually Posted

After you manually post an article, you can mark it in the DB so the daemon doesn't try to re-post it:

```bash
sqlite3 nepalpulse.db "UPDATE articles SET is_posted_fb=1, posted_fb_at=datetime('now') WHERE id=806;"
```

Or mark multiple:
```bash
sqlite3 nepalpulse.db "UPDATE articles SET is_posted_fb=1, posted_fb_at=datetime('now') WHERE id IN (806, 786, 785);"
```

## Notes

- Posts are auto-formatted by Claude Haiku (same as daemon)
- Each post includes headline (English), body, Nepali translation, and URL
- Diversity gates are NOT applied — you're responsible for not posting the same source twice
- Posts older than 12 hours are skipped (stale news)

## Troubleshooting

**"No fresh articles in queue"**
- The 41 articles in the DB are all unverified or marked as posted
- Enable the scanner: set `SCAN_INTERVAL_MINUTES = 15` in `config/settings.py` and restart daemon

**Formatting fails on an article**
- Likely missing Claude API key or formatter error
- Check `.env` has `ANTHROPIC_API_KEY` set
- See `nepalpulse_$(date +%Y%m%d).log` for details

**Need to get the raw article data instead?**
```bash
sqlite3 -header nepalpulse.db "SELECT id, source_name, title FROM articles WHERE is_verified=1 AND is_posted_fb=0 LIMIT 5;"
```
