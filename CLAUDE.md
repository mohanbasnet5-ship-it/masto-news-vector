# CLAUDE.md — NepalPulse

Authoritative guide for Claude Code. The file at `nepalpulse/CLAUDE.md` is stale — ignore it.

**Before touching the daemon or Graph API, read [SOP.md](SOP.md).**

---

## Repository Layout

```
MASTO NEWS VECTOR/
├── nepalpulse/              ← ALL active code lives here — edit only this directory
│   ├── main.py              ← daemon entry point (PID lock, event loop, scheduler)
│   ├── config/
│   │   ├── settings.py      ← ALL tuneable constants — edit here first
│   │   ├── sources.py       ← RSS feed list with tier/routing/language flags
│   │   ├── keywords.py      ← Nepal keyword lists, Devanagari terms, category maps
│   │   └── politicians.py   ← politician name→FB page map (auto-tagging)
│   ├── scanner/
│   │   ├── scanner.py       ← RSS fetcher, three-path routing filter
│   │   └── social_scanner.py← FB page scraper (DISABLED — needs App Review)
│   ├── validator/
│   │   └── validator.py     ← tier-based corroboration logic
│   ├── formatter/
│   │   └── formatter.py     ← Claude Haiku rewriter, 3 post templates, hashtag pool
│   ├── illustrator/
│   │   ├── illustrator.py   ← wrapper → delegates to meridian_card
│   │   └── meridian_card.py ← PIL 1080×1080 story card (navy/bone/crimson brand)
│   ├── summarizer/
│   │   └── summarizer.py    ← 3 daily digest cards (Gemini text + PIL image)
│   ├── poster/
│   │   └── poster.py        ← Facebook Graph API, circuit breaker, diversity gates
│   ├── cartoonist/
│   │   └── cartoonist.py    ← daily editorial cartoon (DISABLED)
│   ├── weekly/
│   │   └── weekly.py        ← Sunday weekly wrap (Claude narrative)
│   ├── database/
│   │   └── db.py            ← SQLite WAL, all DB helpers
│   ├── web/
│   │   └── app.py           ← Flask reader + URL shortener (localhost:5050)
│   ├── tests/               ← pytest suite (db, scanner, validator, formatter, poster)
│   ├── fonts/               ← IBMPlexSerif, Gloock (Latin headings)
│   ├── docs/                ← static HTML for Facebook App Review (not the web reader)
│   ├── assets/              ← ridge_annapurna.json — ridge silhouette used by meridian_card
│   ├── samples/             ← reference PNG renders of story cards + digest cards
│   ├── requirements.txt     ← pip install -r requirements.txt installs all deps
│   ├── PRODUCTION_READINESS.md ← P0/P1/P2 fix log — timezone, migration, dup-risk
│   ├── README.md            ← short setup/run/checks doc
│   └── logs/                ← rotating daily log files
├── nepalpulse_dev/          ← STALE sandbox copy — do not edit; production is nepalpulse/
└── files/                   ← planning docs (not deployed)
```

---

## Commands

```bash
# Check daemon (only ONE instance allowed)
ps -A | grep "main.py" | grep -v grep

# Safe restart
pkill -f "python3 main.py" && sleep 3 && cd nepalpulse && nohup python3 main.py > logs/nepalpulse_run.log 2>&1 &

# Tail live log
tail -f nepalpulse/logs/nepalpulse_$(date +%Y%m%d).log

# Install dependencies
pip3 install -r nepalpulse/requirements.txt

# Run tests
cd nepalpulse && python3 -m pytest                     # all tests
cd nepalpulse && python3 -m pytest tests/test_poster.py # single file

# Syntax check all files
cd nepalpulse && python3 -m py_compile main.py config/settings.py database/db.py \
  poster/poster.py formatter/formatter.py summarizer/summarizer.py \
  cartoonist/cartoonist.py scanner/scanner.py validator/validator.py \
  weekly/weekly.py illustrator/illustrator.py illustrator/meridian_card.py web/app.py

# DB health
sqlite3 nepalpulse/nepalpulse.db "
  SELECT COUNT(*) total, SUM(is_verified) verified, SUM(is_posted_fb) posted FROM articles;
  SELECT COUNT(*) fresh_queue FROM articles
    WHERE is_verified=1 AND is_posted_fb=0 AND is_posting_blocked=0
    AND is_breaking=0 AND source_region!='statement'
    AND (published_at IS NULL OR published_at >= datetime('now','-12 hours'));
  SELECT MAX(posted_fb_at) last_post FROM articles WHERE is_posted_fb=1;
  SELECT tripped_at, error_code, cooldown_sec/3600.0 hours FROM fb_circuit_log ORDER BY id DESC LIMIT 3;
"

# Inspect recent posts
sqlite3 nepalpulse/nepalpulse.db "SELECT posted_fb_at, title FROM articles WHERE is_posted_fb=1 ORDER BY posted_fb_at DESC LIMIT 10;"

# Start web reader (separate from daemon)
python3 nepalpulse/web/app.py

# Manual post generator — interactive clipboard tool (recommended)
# Each post auto-copies to clipboard; you paste into Facebook, then confirm
./post_manually.sh 5                                       # Post 5 articles manually
./post_manually.sh                                         # Default: 5 articles

# Alternative: batch text export (no interaction)
python3 nepalpulse/manual_post_generator.py 3 text        # 3 posts as plain text
python3 nepalpulse/manual_post_generator.py 5 markdown    # 5 posts as markdown (for docs)
python3 nepalpulse/manual_post_generator.py 1 json        # 1 post as JSON (for Graph API)
# See MANUAL_POST_GUIDE.md for details
```

---

## Current System State (snapshot 2026-05-13)

### Posting model: continuous + diversity gates

The continuous publishing system is **live**. There is no daily cap — articles are drained from a priority queue as fast as the safety gates allow. Each scheduler tick (`poster._regular_post_allowed()` in [poster.py:156](nepalpulse/poster/poster.py)) checks, in order:

1. **Startup grace** — hold posting if daemon restarted within `POST_STARTUP_GRACE_MINUTES = 90` of last post
2. **Velocity brake** — refuse if ≥ `MAX_VELOCITY_POSTS_PER_4H = 8` in last 4h
3. **Hourly soft limit** — refuse if ≥ `MAX_POSTS_PER_HOUR = 5` this hour
4. **Adaptive jittered gap** — `_adaptive_min_gap()` returns 10–18 min (peak) or 25–35 min (off-peak 23:00–06:00 NPT)
5. **Diversity gates** — `_diversity_ok()` refuses same source or same `source_region` as last post

Live constants in [config/settings.py](nepalpulse/config/settings.py):
- `SCAN_INTERVAL_MINUTES = 15`
- `MIN_POST_GAP_MINUTES = 10` (peak floor)
- `MIN_POST_GAP_OFFPEAK_MIN = 25`, `MAX_POST_GAP_OFFPEAK_MIN = 35`
- `OFFPEAK_HOURS_NPT = (23, 6)`
- `MAX_POSTS_PER_HOUR = 5`
- `MAX_VELOCITY_POSTS_PER_4H = 8`
- `MIN_BREAKING_GAP_MINUTES = 15`
- `POST_STARTUP_GRACE_MINUTES = 90`
- `MAX_DAILY_ARTICLE_POSTS` — **removed** (replaced by hourly soft limit)

Supporting DB helpers in [database/db.py](nepalpulse/database/db.py): `get_fresh_queue_depth`, `get_posts_last_n_hours`, `get_posts_last_hour`, `get_last_posted_source`, `get_last_posted_category`, `get_recently_posted_titles`. `get_unposted_verified()` orders by priority score `(recency_band × 10) + tier_quality + corroboration`.

### Formatter anti-spam state

- All spam markers removed: `━━━━━━━━━`, `automated digest` footer, `✅ Verified`, `📌 Source:`, `🔗 Full story:`
- 3 rotating post templates (selected by `article_id % 3`)
- Hashtag pool of 5 — rotates so no two consecutive posts share base tags
- Engagement hook every 3rd post (`तपाईंको विचार के छ? 💬` etc.)

### Current post format (3 rotating templates)

Template 0 — English-lead (default + all breaking):
```
{headline}

{body}

{nepali}

{url}

{category_tag} {base_tags} 🇳🇵
```

Template 1 — Nepali-lead (only when Nepali content exists):
```
{devanagari_headline}

{nepali}

—

{headline}

{body}

{url}

{category_tag} {base_tags} 🇳🇵
```

Template 2 — Engagement hook:
```
{headline}

{body}

{nepali}

{engagement_hook}

{url}

{category_tag} {base_tags} 🇳🇵
```

### Feature flags in `.env`
- `ENABLE_STORY_IMAGES=0` — PIL cards disabled for regular posts
- `ENABLE_DIGESTS=0` — 3× daily digest cards disabled
- `ENABLE_CARTOON=0` — daily cartoon disabled
All three were disabled during FB account recovery. Re-enable once posting has been stable for at least one week with no fresh circuit trips.

---

## Production Readiness Fixes (from `PRODUCTION_READINESS.md`)

The following P0/P1 fixes are baked into the current code and must not regress:

- **Gap enforcement**: SQLite UTC timestamps are normalized to tz-aware UTC before comparison. Naive comparison previously returned `9999` and silently bypassed the gap check. Test: `tests/test_db.py::test_minutes_since_last_post_handles_sqlite_utc_timestamp`.
- **Schema migration on startup**: `init_db()` migrates the `articles` table before creating dependent indexes (adds `nepali_text`, `source_language`, etc. on older DBs). Test: `tests/test_db.py::test_init_db_migrates_existing_articles_table`.
- **Duplicate-post guard**: `_publish_article()` re-reads the article's `is_posted_*` flag immediately before building the AI rewrite, preventing quota waste when another path posted it first. Test: `tests/test_poster.py::test_publish_skips_already_posted_before_building_post`.
- **FB spam-limit response**: Error code `368` / subcode `1390008` pauses posting via the circuit breaker (escalating 2h → 6h → 24h) rather than retrying every 30 min. State persists in `fb_circuit_log`.
- **Timezone discipline**: Daily/weekly windows (digests, cartoon, weekly wrap, daily counts, image quota) evaluate in NPT; stored timestamps stay UTC.
- **`settings.is_configured()`**: distinguishes placeholder credentials from real ones — gates Twitter, Claude, Gemini, and digest paths.
- **AI JSON parsing**: formatter extracts JSON objects from fenced/prefixed model responses before parsing.

---

## Architecture

**Event loop (`main.py`):**
- Every **15 min** (target) → RSS scan → validate
- Every **50–110s** (random sleep) → continuous posting tick
- 07:00 NPT daily → morning digest (DISABLED: `ENABLE_DIGESTS=0`)
- 13:40 NPT daily → midday digest (DISABLED)
- 20:00 NPT daily → evening digest (DISABLED)
- Sunday 18:00 NPT → weekly wrap (ACTIVE)
- 07:00 NPT daily → editorial cartoon (DISABLED: `ENABLE_CARTOON=0`)

**Pipeline:**
```
scanner → DB → validator → formatter (Claude Haiku) → poster (Facebook Graph API)
                                        ↓
                            illustrator/meridian_card (PIL, DISABLED for posts)
```

**Validation tiers (`config/sources.py`):**
- Tier 1 (BBC, Reuters, AP, Al Jazeera, UN): auto-verified
- Tier 2 (KPost, Guardian, The Hindu, ToI, Economic Times, The Wire, Gorkhapatra, Rising Nepal, MyRepublica, Himalayan Times, Nepali Times, Record Nepal, Himal): auto-verified
- Tier 3 (Onlinekhabar, Setopati, Kantipur, Nagarik, Ratopati, Pahilopost, Khabarhub, Nepal News, diaspora portals): needs 1 corroborating source
- Tier 4 (social, blogs): never published

**Source filtering — three routing paths in `scanner.py`:**
1. `language: "ne"` (Gorkhapatra): URL must contain `/news/` AND title must have `NEPAL_DEVANAGARI_KEYWORDS` term
2. `domestic_only: True` (all Nepal-based English): Nepal keyword in **title** only
3. International (BBC, Reuters, AP, India, diaspora): Nepal keyword anywhere in title+summary

---

## AI Models

| Model | Used for | Cost note |
|---|---|---|
| `claude-haiku-4-5-20251001` | Article rewrite (5 fields), breaking check (8 tokens), weekly wrap | ~600 tokens/article |
| `gemini-2.0-flash` | Digest text — story selection + bilingual headlines | 3× daily (DISABLED) |
| PIL (local) | Digest cards + story cards | Zero API cost |
| Gemini image | Cartoon images only (DISABLED) | 0 calls/day currently |

**Claude formatter output** — 5 fields in one call:
`{"headline", "body", "devanagari_headline", "nepali", "scene"}`

**GOLDEN RULE:** Claude rewrites in its own voice — never copies source text verbatim.

---

## Formatter Rules

- `_strip_byline()` — removes "By Name, Location, Date:" from RSS summaries before Claude
- `_entity_guard()` — checks key countries/actors from title appear in rewrite; discards if missing
- `_detect_category()` — maps keywords to one of 9 categories (india_nepal, china_nepal, economy, disaster, politics, society, geography, international, diaspora)
- Falls back to title-only text post if Claude fails — never blocks posting
- Nepali grammar enforced in prompt: `छ/भयो/मा/ले/को` — never `है/हुआ/में/ने/का`

---

## Posting Safety Rules

| Rule | Value | Purpose |
|---|---|---|
| Min gap (peak) | 10–18 min jitter | Fast but not mechanical |
| Min gap (off-peak 23–06 NPT) | 25–35 min jitter | Quiet hours |
| Velocity brake | Max 8 posts / 4h | Catches burst from restart |
| Hourly soft limit | Max 5 / hour | Human page cadence |
| Startup grace | 90 min hold if last post was recent | Kills restart-churn blocks |
| Breaking gap | 15 min | Urgent news |
| Freshness | Articles must be <12h old | No stale news |
| Daily cap | Removed — replaced by hourly soft limit | n/a |
| Diversity: source | No two consecutive same source | Looks organic |
| Diversity: category | No two consecutive same `source_region` | Varied content |
| Per-article failures | 3 → durably blocked in DB | Stops stuck articles |
| FB circuit breaker | 368 spam → 2h → 6h → 24h escalation (persisted in `fb_circuit_log`) | Survives restarts |

**NEVER run two daemon instances.** Always `ps -A | grep "main.py"` before starting.

---

## Facebook Block History & Prevention

**What triggers Meta's spam filter (confirmed from 3 blocks):**
- Identical byte-for-byte content in consecutive posts (fixed: templates + hashtag rotation)
- Box-drawing Unicode `━━━━━━━` — spam marker (fixed: removed)
- Self-declaring `automated digest` in post (fixed: removed)
- Mechanical clock intervals (fixed: jitter)
- Restart churn — daemon on/off/on/off then posting (fixed: startup grace)
- Burst posting after backlog (fixed: velocity brake)

**Safe restart procedure:**
```bash
pkill -f "python3 main.py" && sleep 3 && nohup python3 main.py > logs/nepalpulse_run.log 2>&1 &
```
Startup grace in `poster.py` automatically holds posting if last post was recent.

---

## Credentials

All in `nepalpulse/.env`:
- `ANTHROPIC_API_KEY` — Claude Haiku
- `GOOGLE_API_KEY` / `GOOGLE_API_KEY_2` / `GOOGLE_API_KEY_3` — Gemini (digest text + images when enabled)
- `FACEBOOK_PAGE_ID=1044997868704601`
- `FACEBOOK_APP_ID=1630336044890621`
- `FACEBOOK_APP_SECRET`
- `FACEBOOK_ACCESS_TOKEN` — **permanent page token** (set 2026-05-07, `expires_at=0`). Regenerate: Graph API Explorer → Nepal Pulse News app → Nepal Pulse page → Generate Token → exchange for long-lived → get page token.
- `TWITTER_API_KEY/SECRET/ACCESS_TOKEN/SECRET` — optional, Twitter disabled without these
- `ENABLE_STORY_IMAGES=0`, `ENABLE_DIGESTS=0`, `ENABLE_CARTOON=0` — re-enable when FB is stable

---

## Database Schema (`nepalpulse.db`, WAL mode)

| Table | Purpose |
|---|---|
| `articles` | All scraped items. Key flags: `is_verified`, `is_breaking`, `is_posted_fb`, `is_posted_x`, `is_posting_blocked`, `posting_block_reason`, `posting_blocked_at`, `posted_fb_at`, `source_name`, `source_region`, `nepali_text` |
| `source_matches` | Cross-reference records for Tier 3 corroboration |
| `cartoons` | Daily cartoon metadata (scene, captions, post IDs) |
| `morning_digests` | One row per digest (`digest_type`: morning/day/evening) |
| `weekly_wraps` | One row per Sunday wrap |
| `image_generations` | Quota tracking for all image API calls |
| `short_links` | 6-char codes for web reader `/s/<code>` |
| `fb_circuit_log` | Every FB circuit trip — used for escalating spam backoff |

---

## Notes

- PID lock: `nepalpulse/nepalpulse.pid` — use `ps -A | grep "main.py"` not `pgrep` (Python path non-standard on macOS)
- Politician scanning disabled — needs FB App Review for `pages_read_engagement` on third-party pages. Statements still captured via RSS.
- `nepalpulse/docs/` — static HTML for Facebook App Review only, not part of web reader
- Devanagari fonts: `/System/Library/Fonts/Kohinoor.ttc` (system) + `nepalpulse/fonts/` (project IBMPlexSerif, Gloock)
- `NEPAL_DEVANAGARI_KEYWORDS` in `keywords.py` — Devanagari terms for Gorkhapatra domestic filtering
- Second `CLAUDE.md` inside `nepalpulse/` is stale — this root file is authoritative
