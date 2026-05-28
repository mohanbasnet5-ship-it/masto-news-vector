# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Authoritative guide for Claude Code. The file at `nepalpulse/CLAUDE.md` is stale — ignore it.

**Before touching the daemon or Graph API, read [SOP.md](SOP.md).**

## Hard constraints (never do without discussion)

- Never restart the daemon without first checking `fb_circuit_log` for an active block
- Never change `FB_SPAM_COOLDOWN_ESCALATION_HOURS` or `POST_STARTUP_GRACE_MINUTES`
- Never add back spam markers: `━━━`, `automated`, `✅ Verified`, `🔗 Full story:`
- Never remove `restore_circuit_state()` from `main.py` startup
- Never set `MIN_POST_GAP_MINUTES` below 10
- Never deploy (restart daemon) during peak hours (06:00–23:00 NPT) unless daemon is crashed

**Project management:** All active initiatives live in [PROJECTS.md](PROJECTS.md). Run `python3 pm.py` (or double-click `pm.command`) for a status dashboard. Read PROJECTS.md at the start of any session to know current priorities before suggesting work. Tracks: A (System), B (Content), C (Community), D (Owned Audience), E (Citizen Services & Government Data), F (Card System & Visual Formats).

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
│   │   ├── politicians.py   ← politician name→FB page map (legacy — superseded by tag_rules.py)
│   │   └── tag_rules.py     ← org tag system: 35 entities, LOCATION_MAP (77 districts), LOCAL_POLICE + LOCAL_GOVERNMENT resolvers; `resolve_tags(category, title, body)` → max 2 FB @page tags per post; never tags individual politicians
│   ├── scanner/
│   │   ├── scanner.py       ← RSS fetcher, three-path routing filter
│   │   ├── social_scanner.py← FB page scraper (DISABLED — needs App Review)
│   │   └── gov_scanner.py   ← govt/civic data: NRB rates, OpenAQ AQI, USGS earthquakes, NOC fuel prices + manual triggers
│   ├── validator/
│   │   └── validator.py     ← tier-based corroboration logic
│   ├── formatter/
│   │   └── formatter.py     ← Claude Haiku rewriter, 3 post templates, hashtag pool
│   ├── illustrator/
│   │   ├── illustrator.py   ← wrapper → delegates to meridian_card for article story cards
│   │   ├── meridian_card.py ← PIL 1080×1080 story card (navy/bone/crimson brand)
│   │   └── civic_cards.py   ← PIL 1080×1080 civic cards — 13 types (NRB, AQI, fuel, gold, NEPSE, earthquake, bandh, Loksewa, scholarship, Everest, cricket, Kalimati, monsoon); "Civic Bold" Masterframe; 2× supersampled → LANCZOS downsample
│   ├── summarizer/
│   │   └── summarizer.py    ← 3 daily digest cards (Gemini text + PIL image)
│   ├── poster/
│   │   └── poster.py        ← Facebook Graph API, circuit breaker, diversity gates
│   ├── cartoonist/
│   │   └── cartoonist.py    ← daily editorial cartoon (DISABLED)
│   ├── weekly/
│   │   └── weekly.py        ← Sunday weekly wrap (Claude narrative)
│   ├── alerter/
│   │   └── alerter.py       ← Ntfy.sh push notifications (circuit trips, empty queue, daily status)
│   ├── database/
│   │   └── db.py            ← SQLite WAL, all DB helpers
│   ├── web/
│   │   └── app.py           ← Flask reader + URL shortener (localhost:5050)
│   ├── scripts/
│   │   ├── com.nepalpulse.daemon.plist ← launchd service definition (auto-restart on crash)
│   │   ├── preflight.sh     ← blocks launchd restart if FB circuit active or post <5 min ago
│   │   └── start_daemon.sh  ← launchd wrapper: runs preflight then exec python3 main.py
│   ├── draft_writer.py      ← called each daemon tick; writes READY_TO_POST.txt (top 8 queue items pre-formatted)
│   ├── posts_folder.py      ← generates posts/ folder files for manual copy-paste posting
│   ├── mark_posted.py       ← marks an article as posted by article_id (used after manual posting)
│   ├── manual_post_generator.py ← batch text export (text/markdown/json); use posts_folder.py instead
│   ├── copy_post_to_clipboard.py ← interactive: copies formatted post to macOS clipboard, prompts confirm/skip/mark
│   ├── reels/
│   │   ├── reel_maker.py    ← PIL 1080×1920 Reels: 3-scene progressive reveal (S2 headline 3s, S3 story 8s, S5 CTA 2s) → ffmpeg H.264 MP4
│   │   └── reel_poster.py   ← posts Reels MP4 via Facebook Graph API video endpoint
│   ├── gov_scanner_state.json ← DO NOT DELETE — persists last fuel prices, NEPSE index, quake IDs across restarts
│   ├── setup.sh             ← one-time Mac setup: installs deps, creates .env template, inits DB
│   ├── backups/             ← SQLite backup files written by db.backup_database() at 02:00 NPT daily
│   ├── tests/               ← pytest suite: test_db, test_scanner, test_validator, test_formatter, test_poster, test_dry_run (full pipeline with DRY_RUN=1)
│   ├── fonts/               ← IBMPlexSerif, Gloock (Latin headings)
│   ├── docs/                ← static HTML for Facebook App Review (not the web reader)
│   ├── assets/              ← ridge_annapurna.json — ridge silhouette used by meridian_card
│   ├── samples/             ← reference PNG renders of story cards + digest cards
│   ├── requirements.txt     ← pip install -r requirements.txt installs all deps
│   ├── PRODUCTION_READINESS.md ← P0/P1/P2 fix log — timezone, migration, dup-risk
│   ├── README.md            ← short setup/run/checks doc
│   └── logs/                ← rotating daily log files (nepalpulse_YYYYMMDD.log, status_YYYYMMDD.txt)
├── posts/                   ← pre-formatted .txt files for manual copy-paste; named {id}_{source}_{slug}.txt
├── READY_TO_POST.txt        ← auto-generated by draft_writer.py on each daemon tick; top 8 pre-formatted posts for manual use
├── post_manually.sh         ← interactive clipboard poster: copies each post to clipboard, waits for confirm
├── "Card Samples"/          ← 10 reference PNG designs for Track F card types (NRB rate, AQI, fuel, earthquake, bandh, Loksewa, scholarship, Everest, gold/silver, vegetables)
├── reel_test/               ← 1080×1920 Reels scene PNGs: s2_headline.png, s3_story.png, s5_cta.png (S1 hook deleted; ffmpeg + poster.py wiring pending)
├── ROADMAP.md               ← detailed 4-phase technical checklist (legacy — PROJECTS.md is now authoritative)
├── PROJECTS.md              ← master project tracker: 4 tracks (Technical, Content, Community, Audience), priority-ordered
├── MANUAL_POST_GUIDE.md     ← step-by-step guide for manual posting when daemon/circuit is down
├── pm.py                    ← project status dashboard (daemon status, pending restart count, P0/P1 queue)
├── pm.command               ← double-click in Finder to show project dashboard
├── restart.py               ← safety-checked daemon restart (3 checks → confirm → restart → promotes [p]→[x] in PROJECTS.md)
├── PENDING_RESTART.md       ← human-readable list of all changes pending restart (7 areas, 20 items)
└── refresh_posts.command    ← double-click in Finder to regenerate posts/ folder (runs posts_folder.py)
```

---

## Commands

```bash
# Project + daemon status dashboard (shows pending restart items, queue depth, circuit state)
python3 pm.py

# Safe restart — runs 3 safety checks, restarts, promotes [p]→[x] in PROJECTS.md automatically
python3 restart.py
python3 restart.py --check   # check-only, no restart
python3 restart.py --force   # bypass time-of-day check (daemon crashed)

# Check daemon manually (only ONE instance allowed)
ps -A | grep "main.py" | grep -v grep

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
  weekly/weekly.py illustrator/illustrator.py illustrator/meridian_card.py \
  illustrator/civic_cards.py reels/reel_maker.py web/app.py

# DB health
sqlite3 nepalpulse/nepalpulse.db "
  SELECT COUNT(*) total, SUM(is_verified) verified, SUM(is_posted_fb) posted FROM articles;
  SELECT COUNT(*) fresh_queue FROM articles
    WHERE is_verified=1 AND is_posted_fb=0 AND is_posting_blocked=0
    AND is_breaking=0 AND source_region!='statement'
    AND (published_at IS NULL OR published_at >= datetime('now','-6 hours'));
  SELECT MAX(posted_fb_at) last_post FROM articles WHERE is_posted_fb=1;
  SELECT tripped_at, error_code, cooldown_sec/3600.0 hours FROM fb_circuit_log ORDER BY id DESC LIMIT 3;
"

# Inspect recent posts
sqlite3 nepalpulse/nepalpulse.db "SELECT posted_fb_at, title FROM articles WHERE is_posted_fb=1 ORDER BY posted_fb_at DESC LIMIT 10;"

# Start web reader (separate from daemon)
python3 nepalpulse/web/app.py

# Manual posting via posts/ folder (use when daemon is down or FB circuit is tripped)
# posts/ contains pre-formatted .txt files — open, copy text, paste into Facebook
python3 nepalpulse/posts_folder.py                        # Regenerate posts/ folder on demand
# OR double-click refresh_posts.command in Finder (same thing, no terminal needed)
python3 nepalpulse/mark_posted.py <article_id>            # Mark article as posted after manual post
# article_id is the number at the start of each filename in posts/

# Interactive clipboard posting (copies each post to clipboard, you paste into Facebook, confirm here)
./post_manually.sh 5                                      # Prepare 5 posts for clipboard pasting
cd nepalpulse && python3 copy_post_to_clipboard.py 3      # Same thing, called directly

# Batch text export (alternative, no interaction)
python3 nepalpulse/manual_post_generator.py 3 text        # 3 posts as plain text
python3 nepalpulse/manual_post_generator.py 1 json        # 1 post as JSON (for Graph API)

# Dev runner — test any module without touching the running daemon
cd nepalpulse && python3 dev.py queue                    # show current post queue
cd nepalpulse && python3 dev.py format <article_id>      # format article, print post text
cd nepalpulse && python3 dev.py card <article_id>        # render story card PNG, open in Preview
cd nepalpulse && python3 dev.py post <article_id>        # simulate full post (DRY_RUN, no FB call)
cd nepalpulse && python3 dev.py scan                     # run one scan cycle, print new articles
cd nepalpulse && python3 dev.py gov nrb                  # render NRB forex card
cd nepalpulse && python3 dev.py gov gold                 # render Gold/Silver card
cd nepalpulse && python3 dev.py gov aqi                  # render AQI card
cd nepalpulse && python3 dev.py gov nepse                # render NEPSE card
cd nepalpulse && python3 dev.py gov fuel                 # render Fuel card
cd nepalpulse && python3 dev.py gov earthquake           # render Earthquake card (sample)
cd nepalpulse && python3 dev.py gov kalimati             # render Kalimati vegetable price card
# Monsoon card: manually triggered (not scheduled); call post_monsoon_update() directly from scanner.gov_scanner

# Nepali word guard — diagnose Hindi leakage from Claude Haiku
cd nepalpulse && python3 word_stats.py                   # last 30 days, top 30 leaking patterns
cd nepalpulse && python3 word_stats.py --days 7 --limit 50 --pass leakage

# A/B test Claude Haiku vs Gemini 2.0 Flash on formatter prompts (read-only, no DB writes)
cd nepalpulse && python3 ab_test_gemini.py               # 5 articles (default)
cd nepalpulse && python3 ab_test_gemini.py 10            # outputs ab_test_results_<UTC>.md
# Render sample Meridian story card
cd nepalpulse && python3 -m illustrator.meridian_card --sample

# One-time setup (new machine)
cd nepalpulse && bash setup.sh
```

---

## Current System State

### Posting model: continuous + diversity gates

The continuous publishing system is **live**. There is no daily cap — articles are drained from a priority queue as fast as the safety gates allow. Each scheduler tick (`poster._regular_post_allowed()` in [poster.py:156](nepalpulse/poster/poster.py)) checks, in order:

1. **Startup grace** — hold posting if daemon restarted within `POST_STARTUP_GRACE_MINUTES = 90` of last post
2. **Velocity brake** — refuse if ≥ `MAX_VELOCITY_POSTS_PER_4H = 8` in last 4h
3. **Hourly soft limit** — refuse if ≥ `MAX_POSTS_PER_HOUR = 5` this hour
4. **Adaptive jittered gap** — `_adaptive_min_gap()` returns 10–18 min (peak) or 25–35 min (off-peak 23:00–06:00 NPT)
5. **Diversity gates** — `_diversity_ok()` refuses same source or same `source_region` as last post

Live constants in [config/settings.py](nepalpulse/config/settings.py):
- `SCAN_INTERVAL_MINUTES = 7` (peak) / off-peak defaults to 20 min (set `SCAN_INTERVAL_OFFPEAK_MINUTES` in settings.py to override)
- `MIN_POST_GAP_MINUTES = 10` (peak floor)
- `MIN_POST_GAP_OFFPEAK_MIN = 25`, `MAX_POST_GAP_OFFPEAK_MIN = 35`
- `OFFPEAK_HOURS_NPT = (23, 6)`
- `MAX_POSTS_PER_HOUR = 5`
- `MAX_VELOCITY_POSTS_PER_4H = 8`
- `MIN_BREAKING_GAP_MINUTES = 15`
- `POST_STARTUP_GRACE_MINUTES = 90`
- `MAX_ARTICLE_AGE_HOURS_FOR_POSTING = 6` (articles older than 6h are not posted)
- `MAX_DAILY_ARTICLE_POSTS` — **removed** (replaced by hourly soft limit)

Supporting DB helpers in [database/db.py](nepalpulse/database/db.py): `get_fresh_queue_depth`, `get_posts_last_n_hours`, `get_posts_last_hour`, `get_last_posted_source`, `get_last_posted_category`, `get_recently_posted_titles`. `get_unposted_verified()` orders by priority score `(recency_band × 10) + tier_quality + corroboration`.

### Formatter anti-spam state

- All spam markers removed: `━━━━━━━━━`, `automated digest` footer, `✅ Verified`, `📌 Source:`, `🔗 Full story:`
- 3 rotating post templates (selected by `article_id % 3`)
- Hashtag pool of 5 — rotates so no two consecutive posts share base tags
- Engagement hook every 3rd post (`तपाईंको विचार के छ? 💬` etc.)

### Current post format (3 rotating templates)

**URL is NOT in the post body** (`URL_IN_COMMENT=1`). The daemon posts the URL as the first comment automatically after publishing, so Facebook's algorithm does not penalise the post for having an outbound link.

Template 0 — English-lead (default + all breaking):
```
{headline}

{body}

{nepali}

{category_tag} {base_tags} 🇳🇵

— first comment (auto) —
🔗 {url}
```

Template 1 — Nepali-lead (only when Nepali content exists):
```
{devanagari_headline}

{nepali}

—

{headline}

{body}

{category_tag} {base_tags} 🇳🇵

— first comment (auto) —
🔗 {url}
```

Template 2 — Engagement hook:
```
{headline}

{body}

{nepali}

{engagement_hook}

{category_tag} {base_tags} 🇳🇵

— first comment (auto) —
🔗 {url}
```

### Gold-standard content format — civic impact

The highest-engagement post type for Nepal diaspora connects an international event to Nepal's specific situation with three layers:

1. **The Nepal angle** — who/what in Nepal is directly involved (e.g. peacekeepers in the epicentre, Nepali workers in the affected country)
2. **Practical local impact** — what does this mean right now for people in Kathmandu or the diaspora ("expect delays at health desks", "remittance corridors may be affected")
3. **Forward guidance** — what to watch for ("if suspected cases emerge, government will announce quarantine protocols")

The `"This matters because…"` editorial line (auto-injected for disaster/economy/politics/india_nepal/china_nepal categories) and the `_topic_hook()` engagement question implement this automatically. For international→Nepal stories, the civic reporter persona (template 2 rotation) is the best fit.

### Nepali writing — quality rules

Nepali is generated by Claude Haiku via `_generate_nepali_fields()` with an explicit grammar prompt. Google Translate is fallback only. Key rules baked into the prompt:

**Verb endings (enforced in prompt + word guard):**
- Present: `छ / छन्` — never `है / हैं`
- Past: `भयो / गर्‍यो / गरे` — never `हुआ / किया / गया`
- Continuous: `गर्दैछ / भइरहेको छ` — never `कर रहा है / हो रहा है`
- Future: `हुनेछ / गर्नेछ` — never `होगा / करेगा`

**Postpositions (enforced):**
`ले` (agent) · `लाई` (object) · `बाट` (source) · `मा` (location/time) · `सँग` (with) · `सम्म` (until)
Never: `ने, को, से, में, पर, तक`

**Vocabulary:**
- Peacekeepers: `शान्तिरक्षक` (not `समाधानकर्मी`)
- "Means": `यसको मतलब छ` (not `मतलब है`)
- Numbers: Nepali digits `१ २ ३` not `1 2 3`

Word guard runs as a post-processing safety net — 70+ Hindi→Nepali replacement pairs covering multi-word verb phrases, past tense forms, postpositions, and vocabulary. Leaking patterns are classified into `leakage` (`_HINDI_LEAKAGE` regex in `formatter.py`), `domain` (`_NEPALI_DOMAIN` corrections), and `postpub_*` (slipped through after publish). Use `word_stats.py` to find high-frequency leaks and add them to the appropriate list in `formatter.py`.

### Feature flags in `.env`
- `ENABLE_STORY_IMAGES=1` — Meridian PIL cards active for regular posts
- `URL_IN_COMMENT=1` — URL stripped from post body, threaded as first comment (algorithm boost)
- `ENABLE_DIGESTS=0` — 3× daily digest cards disabled
- `ENABLE_CARTOON=0` — daily cartoon disabled
- `DRY_RUN=0` — when set to `1`, full pipeline runs (scan, validate, format) but no posts are sent to Facebook; useful for testing without touching the page
- `RECOVERY_MODE=0` — when `1`, caps 4h velocity to `RECOVERY_VELOCITY_CAP = 4` (vs normal 8); set `RECOVERY_MODE_START=YYYY-MM-DD` and it auto-lifts after `RECOVERY_DAYS = 3` days.

Re-enable digests and cartoon once posting has been stable for at least one week with no fresh circuit trips.

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
- Every **7 min** (peak) / **20 min** (off-peak 23–06 NPT) → RSS scan → validate
- Every **50–110s** (random sleep) → continuous posting tick
- 02:00 NPT daily → SQLite DB backup (`db.backup_database()`)
- 06:00 NPT daily → daily status summary written to `logs/status_YYYYMMDD.txt` + Ntfy alert
- Sunday 18:00 NPT → weekly wrap (ACTIVE)
- 07:00 NPT daily → editorial cartoon (DISABLED: `ENABLE_CARTOON=0`)
- Monday 03:00 NPT weekly → stale article cleanup (removes articles >30 days old)
- 07:00 NPT daily → 💰 NRB exchange rate card (`gov_scanner.check_and_post_rate_card`)
- 07:15 NPT daily → 💛 Gold & Silver rate card (`gov_scanner.check_and_post_gold_card`) — source: gold-api.com London/NY spot → NPR via NRB rate × 1.112 duty factor; editorial tax-premium strip
- 08:00 NPT daily → 🌫️ OpenAQ AQI card (`gov_scanner.check_and_post_aqi_card`)
- Every scan cycle → 🔴 USGS earthquake check M≥4.5 (`gov_scanner.check_and_post_earthquake`)
- Every scan cycle → ⛽ NOC fuel price monitor, throttled to once/hour (`gov_scanner.check_and_post_fuel_card`)
- 15:45 NPT weekdays (Mon–Fri) → 📈 NEPSE closing index card (`gov_scanner.check_and_post_nepse_card`) — 15:45 not 15:30; gives sharesansar 45 min after close to settle; retries if data unavailable or fails validation

State for all gov_scanner checks (last rates, posted quake IDs, NEPSE index) persists in `nepalpulse/gov_scanner_state.json` — never delete this file.

**Pipeline:**
```
scanner → DB → validator → formatter (Claude Haiku) → poster (Facebook Graph API)
                                        ↓                        ↓
                            illustrator/meridian_card    alerter (Ntfy.sh — circuit trips,
                              (PIL story cards, ACTIVE)    empty queue, daily status)
gov_scanner → illustrator/civic_cards.py → poster (NRB/AQI/fuel/gold/NEPSE/earthquake cards)
reels/reel_maker.py (ffmpeg MP4) → reels/reel_poster.py (video endpoint, wiring pending)
```

**Alerter (`alerter/alerter.py`):**
Push notifications via [Ntfy.sh](https://ntfy.sh) (free, no account required). Set `NTFY_TOPIC=nepalpulse-yoursecretword` in `.env` and subscribe to that topic in the Ntfy phone app. Sends alerts for: FB circuit trips, 30-min empty queue during peak hours, daily 6am status. Silent no-op if `NTFY_TOPIC` is not configured.

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
| `claude-haiku-4-5-20251001` | Article rewrite (5 fields) + Nepali fields (headline+body), breaking check (8 tokens), weekly wrap | ~700 tokens/article |
| `gemini-2.0-flash` | (reserved for future use — digests removed) | 0 calls/day |
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
- `resolve_tags(category, title, body)` (from `config/tag_rules.py`) — replaces legacy `_detect_politician_tags()`; returns at most 2 org FB @page slugs per post; never individual politicians
- Falls back to title-only text post if Claude fails — never blocks posting
- Nepali grammar enforced in prompt: `छ/भयो/मा/ले/को` — never `है/हुआ/में/ने/का`

---

## Posting Safety Rules

| Rule | Value | Purpose |
|---|---|---|
| Min gap (peak) | 10–18 min jitter | Fast but not mechanical |
| Min gap (off-peak 23–06 NPT) | 25–35 min jitter | Quiet hours |
| Velocity brake | Max 8 posts / 4h (4 in recovery mode) | Catches burst from restart |
| Hourly soft limit | Max 5 / hour | Human page cadence |
| Startup grace | 90 min hold if last post was recent | Kills restart-churn blocks |
| Breaking gap | 15 min | Urgent news |
| Freshness | Articles must be <6h old | No stale news |
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
python3 restart.py   # preferred — runs 3 safety checks, then restarts
```
If the daemon has crashed and `restart.py` refuses (time-of-day check), use `python3 restart.py --force`. Startup grace in `poster.py` automatically holds posting if last post was recent.

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
- `NTFY_TOPIC` — optional, e.g. `nepalpulse-yoursecretword`; enables phone push alerts via Ntfy.sh
- `ENABLE_STORY_IMAGES=1` — Meridian cards active (re-enabled 2026-05-17)
- `URL_IN_COMMENT=1` — URL posted as first comment, not in post body (algorithm boost)
- `ENABLE_CARTOON=0` — re-enable once posting is stable for 1+ week
- `DRY_RUN=0` — set to `1` to run full pipeline without posting
- `RECOVERY_MODE=0`, `RECOVERY_MODE_START=YYYY-MM-DD` — set to `1` + ISO date after a FB ban; auto-lifts after 3 days

---

## Database Schema (`nepalpulse.db`, WAL mode)

| Table | Purpose |
|---|---|
| `articles` | All scraped items. Key flags: `is_verified`, `is_breaking`, `is_posted_fb`, `is_posted_x`, `is_posting_blocked`, `posting_block_reason`, `posting_blocked_at`, `posted_fb_at`, `source_name`, `source_region`, `nepali_text` |
| `source_matches` | Cross-reference records for Tier 3 corroboration |
| `cartoons` | Daily cartoon metadata (scene, captions, post IDs) |
| `morning_digests` | Legacy digest table — digest feature removed from event loop |
| `weekly_wraps` | One row per Sunday wrap |
| `image_generations` | Quota tracking for all image API calls |
| `short_links` | 6-char codes for web reader `/s/<code>` |
| `fb_circuit_log` | Every FB circuit trip — used for escalating spam backoff |

---

## Notes

- PID lock: `nepalpulse/nepalpulse.pid` — use `ps -A | grep "main.py"` not `pgrep` (Python path non-standard on macOS)
- `.fb_circuit.lock` (in `nepalpulse/`) — JSON file written by the circuit breaker with `resume_at_utc`; read by `preflight.sh` to block launchd restarts during an active ban. Do not delete manually.
- `scripts/` — launchd-based alternative to nohup. `preflight.sh` checks both the circuit lock and recent post time before allowing Python to start, preventing restart churn at the OS level.
- Politician scanning disabled — needs FB App Review for `pages_read_engagement` on third-party pages. Statements still captured via RSS.
- `nepalpulse/docs/` — static HTML for Facebook App Review only, not part of web reader
- Devanagari fonts: `/System/Library/Fonts/Kohinoor.ttc` (system) + `nepalpulse/fonts/` (project IBMPlexSerif, Gloock)
- `NEPAL_DEVANAGARI_KEYWORDS` in `keywords.py` — Devanagari terms for Gorkhapatra domestic filtering
- Second `CLAUDE.md` inside `nepalpulse/` is stale — this root file is authoritative
- `posts/` folder is the primary manual posting interface; each file is named `{article_id}_{source}_{slug}.txt` and auto-deleted once `mark_posted.py` is run. Auto-replenished by daemon ticks or `refresh_posts.command`.
- `ROADMAP.md` at repo root is a legacy 4-phase technical reference — `PROJECTS.md` is now authoritative for active work
- **Meridian card layout** (`meridian_card.py`): `TOP_BAND_H=180`, `BOTTOM_BAND_H=110`. Ridge is dynamic — floats up to sit 10px below the last content line (`_draw_ridge_motif(y_top=y+10, y_bottom=BODY_BAND_Y1)`). English body font 27px. Render test cards: `cd nepalpulse && python3 -m illustrator.meridian_card --sample`
- **Civic card system** (`illustrator/civic_cards.py`): 13 `make_*` functions — one per card type. Shared design language: Devanagari name as largest header text, chip-based data layout, navy/paper/accent tricolor per card, NEPALPULSE·BY MASTO gold footer. 2× supersampled (`_S=2`, all coords via `_ScaledDraw` wrapper, final `resize((1080,1080), LANCZOS)`). Zero decorative lines or boxes anywhere — sections separated by spacing and background color only.
- **Reels** (`nepalpulse/reels/`): `reel_maker.py` generates 325-frame PNG sequence → ffmpeg MP4 (25 fps, 13s). Scene 2 = dark navy headline, Scene 3 = warm paper story (Devanagari + English + body + Nepali), Scene 5 = navy CTA. ffmpeg + poster wiring not yet connected to daemon.
- **Restart safety check**: `sqlite3 nepalpulse/nepalpulse.db "SELECT ROUND((julianday('now')-julianday(MAX(posted_fb_at)))*1440,1) FROM articles WHERE is_posted_fb=1;"` — wait until result is ≥ 90 min before restarting
