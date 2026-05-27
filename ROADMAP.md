# NepalPulse — Project Roadmap

Living checklist. Work top-to-bottom within each phase. Mark items `[x]` when done.
Phase 1 must be complete before Phase 4. Phases 2 and 3 run in parallel.

---

## PHASE 1 — Fix Broken Things (Do First)

### 1.1 Feed Health
- [x] Replace dead AP News RSS URL → Google News RSS (`news.google.com/rss/search?q=Nepal+site:apnews.com`)
- [x] Replace dead Reuters World RSS URL → Google News RSS (`news.google.com/rss/search?q=Nepal+site:reuters.com`)
- [x] Nepali Times feed (404) — marked `disabled: True` in sources.py
- [x] The Himalayan Times feed (returns HTML) — marked `disabled: True` in sources.py
- [x] The Wire feed (returns HTML, bot-blocked) — marked `disabled: True` in sources.py
- [x] MyRepublica feed (read timeout) — marked `disabled: True` in sources.py
- [x] Migrant-Rights.org feed (returns HTML) — marked `disabled: True` in sources.py
- [x] Nepali UK feed (DNS failure, domain defunct) — marked `disabled: True` in sources.py
- [x] **Build auto-disable:** `db.record_feed_failure()` tracks consecutive failures; after 5 hits, `is_feed_disabled()` blocks scanning; auto-retried weekly (`feed_health` DB table)
- [x] **Add feed health log** — `feed_health` table stores `last_success_at`, `consec_failures`, `disabled_at` per feed

### 1.2 Source Balance
- [x] **Per-source daily cap:** max 8 posts from any single source per day — checked in `_diversity_ok()` via `db.get_posts_today_by_source()`
- [x] **Regional balance gate:** if `nepal` region > 70% of last 50 posts, skip nepal-region articles — checked in `_diversity_ok()` via `db.get_region_post_fraction()`
- [x] **Tier 1 keyword filter audit:** added Sherpa, Annapurna, Manaslu, Dhaulagiri, Lhotse, Cho Oyu, Lukla, Namche, Base Camp + city names to GEOGRAPHY in keywords.py; AP/Reuters now flow via Google News RSS so no longer blocked by feed errors

### 1.3 Post-Ban Recovery
- [x] **Recovery mode flag** (`RECOVERY_MODE=1` in `.env`) — caps `MAX_VELOCITY_POSTS_PER_4H` to 4; auto-lifts after `RECOVERY_DAYS=3` days from `RECOVERY_MODE_START`; implemented via `_in_recovery_mode()` in poster.py
- [x] **Weekly posting budget:** if yesterday had 30+ posts, today's 4h velocity cap drops by 2 — implemented via `db.get_posts_yesterday()` in `_regular_post_allowed()`
- [x] Set `RECOVERY_MODE=1` with `RECOVERY_MODE_START=2026-05-14` in `.env` (auto-lifts 2026-05-17)

### 1.4 Breaking News (Currently Posting 1 Story Ever)
- [ ] **Fast-track breaking:** if 2+ sources publish same story within 20 min → auto-flag breaking, bypass Claude significance check
- [x] **Keyword-triggered breaking:** "earthquake", "flood", "killed", "arrested", "resigned", "emergency" in Tier 1/2 headline → skip Claude check via `_keyword_confirms_breaking()` in poster.py
- [ ] **Earthquake direct feed:** poll National Seismological Centre Nepal (`seismonepal.gov.np`) every 5 min — auto-post any magnitude 4.5+ within 2 minutes
- [x] Audit: Claude breaking-check was too strict; `_keyword_confirms_breaking()` bypasses it for Tier 1/2 articles with obvious trigger words

### 1.5 Duplicate Story Guard
- [x] **Pre-post similarity check:** `_is_duplicate_of_recent_post()` in poster.py — checks 60% title word-overlap against last 20 posts in past 2h; integrated into `post_scheduled()` loop
- [ ] **Same-story cross-source block:** if article A and article B share 60%+ title word overlap and both are verified, only post the higher-tier one

### 1.6 Silent Failure Fixes
- [ ] **Posting block audit trail:** when an article is skipped (diversity gate, age, etc.) log the reason to `posting_block_reason` column — currently empty for all 0 blocked articles
- [x] **Nepali text length check:** if Claude returns `nepali` field under 30 words, trigger one retry before falling back — implemented in `_rewrite_for_social()` in formatter.py
- [x] **`DRY_RUN=1` mode:** set in settings.py + .env; `_post_facebook()`, `_post_facebook_photo()`, `_post_twitter()` all log and return `"dry-run"` without calling any API

---

## PHASE 2 — Resilience (Run Parallel with Phase 3)

### 2.1 Alerting — Know Instantly When Things Break
- [x] **FB circuit trip alert:** Ntfy.sh push notification within seconds of circuit trip — `alerter/alerter.py`, called from `_trip_fb_circuit()`
- [x] **Queue depth alert:** if fresh queue drops to 0 for 30+ minutes during peak hours, Ntfy.sh alert — in `main.py` scan cycle
- [ ] **Daemon death alert:** LaunchAgent `KeepAlive=true` auto-restarts daemon on crash (2.2 done); email on exit not yet wired
- [ ] **Feed error alert:** if 3+ Tier 1/2 feeds fail in a single scan, alert — requires scanner to return per-feed failure counts (deferred)

### 2.2 Daemon Auto-Restart
- [x] **macOS LaunchAgent plist:** `~/Library/LaunchAgents/com.nepalpulse.daemon.plist` — `KeepAlive=true`, `RunAtLoad=true`
- [x] File location: `~/Library/LaunchAgents/com.nepalpulse.daemon.plist`
- [ ] Test: restart Mac, confirm daemon is running without manual start (manual step — do after loading plist)

### 2.3 Database
- [x] **Daily backup:** SQLite online backup API to `backups/nepalpulse_YYYYMMDD.db`, triggered at 2am NPT, keeps last 7 — `db.backup_database()`
- [x] **Weekly stale cleanup:** delete unposted articles older than 30 days, triggered Monday 3am NPT — `db.cleanup_stale_articles()`
- [x] **Health check endpoint:** `/health` on `web/app.py` returns JSON: daemon PID, queue depth, last post time, circuit status

### 2.4 Operations
- [x] **Daily 6am NPT status summary:** writes `logs/status_YYYYMMDD.txt` + Ntfy.sh push — `_write_daily_status()` in `main.py`
- [x] **Off-peak scan interval:** 20 min between 23:00–06:00 NPT (was 7 min all day) — `_current_scan_interval()` in `main.py`
- [x] **Meta maintenance window awareness:** FB error codes 1 or 2 between 17:45–19:45 NPT → 30 min pause, no circuit trip — in `_post_facebook()`

---

## PHASE 3 — Platform Expansion (Run Parallel with Phase 2)

### 3.1 Telegram Channel (Highest Priority — Do First)
- [ ] Create Telegram channel: "NepalPulse | नेपाल समाचार" — **manual step**
- [ ] Create Telegram Bot via @BotFather, get bot token — **manual step**
- [ ] Add bot as channel admin — **manual step**
- [x] Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID` to `.env` (placeholders added)
- [x] Telegram posting wired in `poster.py` — mirrors every successful FB post automatically
- [ ] Fill in real bot token + channel ID in `.env` to activate

### 3.2 Instagram (Reuse Existing Cards)
- [ ] Link Instagram account to Nepal Pulse Facebook Page in Meta Business Suite — **manual step**
- [ ] Meridian cards (1080×1080) are already perfectly sized for Instagram
- [x] Instagram Graph API stub in `poster.py` — activates automatically once public website deployed (Phase 3.4)
- [x] Add `INSTAGRAM_ACCOUNT_ID` to `.env` (placeholder added)
- [ ] Fill in real Instagram account ID in `.env` after linking in Business Suite

### 3.3 Email Newsletter
- [ ] Create Substack or Mailchimp account (both free to start) — **manual step**
- [ ] Daily digest: 5 best stories of the day, sent 8pm NPT
- [ ] No new writing — paste the day's top posts
- [ ] Add newsletter signup link to Facebook page About section and web reader
- [ ] This is your owned audience — survives any platform ban

### 3.4 Public Website
- [ ] Deploy `web/app.py` publicly on Render or Railway (both free tier) — **manual step**
- [x] RSS feed endpoint `/rss` added to `web/app.py` — ready for Google News, Apple News, aggregators
- [ ] Add deployed URL to Facebook page About section URL field — legitimacy signal to Meta
- [ ] Add Nepal Press Council seal once registered (Phase 4)

---

## PHASE 4 — Brand Building

### 4.1 Content Formats (Expand Beyond Articles)

**Data posts (high shareability, zero Claude cost)**
- [ ] **NEPSE daily close:** scrape Nepal Stock Exchange closing index, post PIL card each market day at 3:30pm NPT
- [ ] **Remittance exchange rates:** scrape Nepal Rastra Bank rates every Thursday, post PIL card (USD/SAR/MYR/KRW to NPR) — most needed info for diaspora
- [ ] **Weekly weather alert:** monsoon season (June–Sept) — daily rainfall/landslide warnings from DHM Nepal
- [ ] **"Nepal in Numbers":** monthly PIL card — 5 stats about Nepal that month (tourists, earthquakes, NEPSE, inflation, remittances)

**Recurring content (build audience habit)**
- [ ] **"On this day in Nepal"** — daily historical fact from a static dataset; post during off-peak hours to fill quiet gaps
- [ ] **Weekly poll** — one Facebook native poll per week ("Do you support Nepal joining BRICS?" / "Which province needs most investment?"); high engagement, zero writing
- [ ] **Weekly explainer** — "What is the Kalapani dispute?", "Why does Nepal keep changing governments?" — Claude writes from a brief, posted Sunday evening
- [ ] **Province spotlight** — one post per week featuring news from a non-Kathmandu province; builds national credibility

**Live event coverage**
- [ ] **Nepal cricket/football** — pre-write 5–6 score update posts, release on timer during matches
- [ ] **Parliament sessions** — key votes, debates; Gorkhapatra and Rising Nepal cover these; create a "Parliament Watch" recurring format
- [ ] **Disaster live blog** — during earthquakes/floods, post updates every 30 min until situation stabilises

### 4.2 Diaspora Content
- [ ] **Gulf labour news:** deaths, visa changes, kafala reforms — add Gulf-specific sources (Arab News, Gulf News when Nepal angle)
- [ ] **Korea/Japan worker visa** news — dedicated source monitoring
- [ ] **UK Gurkha news** — add Gurkha Justice Campaign feed if available
- [ ] **Remittance rates** (see 4.1 above — double priority for diaspora)
- [ ] **Province-of-origin news** — Madhesh, Koshi, Lumbini province news for diaspora from those regions

### 4.3 Page Credibility (Meta's Hidden Checklist)
- [ ] **Fill page completely:** About section, business category (News/Media), contact email, website URL, founding year — incomplete pages get lower distribution
- [ ] **Apply for Facebook News Page Index:** `facebook.com/journalismproject` — puts you in "news" category, different spam rules
- [ ] **Comment engagement:** respond to at least 3 comments per day — Facebook tracks this; never-responding pages get flagged as bots
- [ ] **Pin best-performing post** every Sunday — signals active editorial curation
- [ ] **Profile/cover photo update** monthly — static pages look abandoned
- [ ] **Minimal ad spend:** even $1–2/week boosting one post signals a real business to Meta's systems

### 4.4 Credibility & Registration
- [ ] **Nepal Press Council registration:** free, ~2 weeks, need a registered editor name — gives legal status, legitimacy signal to Meta and sources
- [ ] **Wikipedia page:** stub page for NepalPulse with founding date, coverage area, registration — Meta uses Wikipedia as credibility signal
- [ ] **Editorial policy page:** publish on website — "How we verify stories", "Our sources", "Correction policy" — required for Facebook News Index
- [ ] **Byline consistency:** add "NepalPulse Desk" or "NepalPulse Bureau" footer to posts — signals editorial structure vs. bot

### 4.5 Engagement Feedback Loop
- [ ] **Log post performance:** after each FB post, fetch `/{post_id}/insights` 24h later — store reach, shares, reactions in `articles` table
- [ ] **Weight queue by category performance:** if disaster posts get 3× shares vs. politics, boost disaster category priority score
- [ ] **Weekly performance report:** which 5 posts performed best this week and why — informs next week's content priorities

---

## NEVER DO AGAIN (Ban Prevention Rules — Permanent)

- Never post the same source twice in 2 consecutive posts
- Never post >8 articles in any 4-hour window
- Never restart the daemon and post immediately — 90 min grace is mandatory
- Never use box-drawing characters (━━━) in post text
- Never include "automated", "digest", "bot" in any post
- Never run two daemon instances simultaneously
- Never use the FB access token from two different IPs on the same day
- Always wait 30 min before retrying after FB error code 1 or 2 (maintenance)
- Always ramp slowly after any ban — `RECOVERY_MODE=1` for minimum 3 days

---

## Progress Tracker

| Phase | Status | Started | Completed |
|---|---|---|---|
| Phase 1 — Fix Broken | 🟡 Mostly Done | 2026-05-14 | — |
| Phase 2 — Resilience | 🟡 Mostly Done | 2026-05-14 | — |
| Phase 3 — Platforms | 🟡 In Progress | 2026-05-14 | — |
| Phase 4 — Brand | ⬜ Not Started | — | — |
