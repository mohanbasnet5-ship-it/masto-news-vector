# NepalPulse — Master Roadmap & Project Management
# Last updated: 2026-05-08

---

## HOW TO USE THIS FILE
Paste this file at the start of any new Claude Code session.
It contains everything needed to continue work without prior context.
Each phase has a `[ ]` checkbox — mark `[x]` when done.
The line **"▶ NEXT STEP"** always points to what to build next.

---

## LIVE SYSTEM STATUS — READ BEFORE ANYTHING ELSE

```
Daemon:    RUNNING  (PID lock at nepalpulse/nepalpulse.pid)
Posting:   ACTIVE   (Facebook 24/7, ~10-12 min gap between posts)
DB:        nepalpulse/nepalpulse.db  (WAL mode, do not delete)
Logs:      nepalpulse/logs/nepalpulse_YYYYMMDD.log
```

### IRON RULES — NEVER VIOLATE
1. **Never start a second daemon** — two instances = FB spam block (code 368).
   Always check: `ps -A | grep "main.py" | grep -v grep` before starting anything.
2. **Never edit live files while daemon runs** unless the change is non-critical config.
   For code changes: stop daemon → edit → restart.
3. **Never post to Facebook from dev/test code** — the `.env` has the real page token.
   Dev system must have `DRY_RUN=True` and no `FACEBOOK_ACCESS_TOKEN`.
4. **Never delete or reset `nepalpulse.db`** — it holds posting history that prevents duplicates.
5. **News posting must never stop** — all development is parallel, not in-place.

---

## FACEBOOK COMMUNITY GUIDELINES CHECKLIST
Every new content type must pass all of these before going live:

- [ ] **No copied text** — all text is Claude-rewritten in its own voice (GOLDEN RULE)
- [ ] **No politician face images** — strip names from image prompts; use symbolic/abstract imagery
- [ ] **No violence/disaster photo-realistic images** — use illustrated/abstract style
- [ ] **No religious imagery in story images** — safe categories only
- [ ] **No fabricated quotes** — fact-check gate already in formatter; new content types need same
- [ ] **Source attribution** — every post includes "Full story: {url}" or clear origin
- [ ] **No spam cadence** — post-fatigue guard must be active before removing daily post cap
- [ ] **Transparency** — Page About section should say "automated news aggregator"
- [ ] **Sensitive category check** — crime/disaster posts: no graphic descriptions, no victim names

---

## TOKEN BURN MINIMIZATION — HARDCORE RULES

These rules apply to ALL new features and must never be relaxed:

### Claude API (most expensive — minimize every call)
1. **One call, two outputs** — every Claude call must return BOTH English AND Nepali. Never split.
2. **Pre-generate in bulk** — "On This Day" facts: one Claude call → 365 entries saved to JSON.
   Cost: ~1 call ever. Never call Claude per-post for this content type.
3. **Quote cards = zero Claude cost** — pull text from already-formatted articles in DB.
   No Claude rewrite needed. The text is already good.
4. **Fact cards** — one Claude call generates 100 cards, saved to `content/fact_cards.json`.
   Serve from file forever after.
5. **Skip breaking-significance check for Tier 1** — BBC/Reuters/AP are auto-breaking.
   Only call Claude's breaking-check for Tier 2/3 sources.
6. **Skip fact-check for Tier 1** — already trusted. Saves 1 call per Tier 1 article.
7. **Cartoon topic**: 1 call/day unavoidable — acceptable.
8. **Weekly wrap**: 1 call/week — acceptable.
9. **Max Claude calls per article**: 1 (rewrite only). Fact-check is optional/tier-gated.

### Gemini API (free but rate-limited)
10. **Digest text (3×/day)** — keep using primary key only. Already minimal.
11. **Image generation** — Pollinations.ai is free and unlimited. Use Gemini only as fallback.

### Pollinations.ai (free, no quota)
12. Primary image provider. Keep as-is. No optimization needed.

### PIL / local computation (free)
13. All digest images, quote cards, fact cards → PIL only. Zero API cost.
    Pre-render images during quiet hours if possible.

---

## ARCHITECTURE — CURRENT STATE (do not change)

```
nepalpulse/
├── main.py            ← daemon entry point — DO NOT TOUCH while running
├── config/
│   ├── settings.py    ← all constants
│   ├── sources.py     ← RSS feeds + tier assignments
│   ├── keywords.py    ← Nepal keyword lists + Devanagari keywords
│   └── politicians.py ← politician name list (auto-tagging)
├── scanner/
│   ├── scanner.py     ← RSS fetcher, 3-path routing
│   └── social_scanner.py ← FB page scraper (DISABLED — needs App Review)
├── validator/         ← cross-source story verification
├── formatter/         ← Claude Haiku rewriter → bilingual posts
├── illustrator/       ← Gemini → Pollinations.ai story images
├── summarizer/        ← 3 daily digest PIL images (07:00/13:40/20:00 NPT)
├── poster/            ← Facebook Graph API poster
├── cartoonist/        ← daily editorial cartoon (07:00 NPT)
├── weekly/            ← Sunday 18:00 NPT weekly wrap
├── database/db.py     ← SQLite WAL
└── web/app.py         ← Flask reader (localhost:5050, run separately)
```

**Event loop timing:**
- Every 50–110s (randomized): post 1 article (breaking → statement → verified)
- Every 45 min: RSS scan + validate
- 07:00 NPT: morning digest + editorial cartoon
- 13:40 NPT: midday digest
- 20:00 NPT: evening digest
- Sunday 18:00 NPT: weekly wrap

---

## PARALLEL DEVELOPMENT SETUP

All new work happens in `nepalpulse_dev/` — a separate directory.
The live `nepalpulse/` is NEVER touched during development.

### One-time setup (do this ONCE, then it persists):
```bash
# Copy live system to dev sandbox
cp -r "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse" \
      "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse_dev"

# Create dev .env — same API keys, but FB token removed
cp "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse/.env" \
   "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse_dev/.env"
# Then edit nepalpulse_dev/.env:
#   FACEBOOK_ACCESS_TOKEN=DRYRUN_NO_POSTING
#   Add: DRY_RUN=true

# Dev uses its own DB — never shares with live
# DB_PATH in dev settings.py will point to nepalpulse_dev.db
```

### Running dev (never interferes with live):
```bash
cd "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse_dev"
python3 test_runner.py   # lightweight harness, not main.py
```

### `test_runner.py` — what it does:
- Exercises only the module being developed
- Prints what WOULD be posted (no FB API calls)
- Writes to `nepalpulse_dev.db`
- Logs to `nepalpulse_dev/logs/`

---

## PHASE 1 — SAFETY HARDENING (do first, touches live only via settings)
**Goal:** protect the live system from FB flags during heavy news days.
**Risk to live system:** minimal — only `settings.py` changes + additive code in `poster.py`.

### Step 1.1 — Post-fatigue guard
- [ ] Add `POST_FATIGUE_THRESHOLD = 6` to `config/settings.py`
  (if 6+ posts in last 12h, minimum gap becomes 15 min instead of 10 min)
- [ ] Add `_fatigue_gap_minutes()` function to `poster/poster.py`
  reads count of `is_posted_fb=1` articles in last 12h from DB
  returns 15 if count >= threshold, else MIN_POST_GAP_MINUTES
- [ ] Replace hardcoded `MIN_POST_GAP_MINUTES` reference in poster's gap check
  with `_fatigue_gap_minutes()`
- [ ] Test in dev: simulate 8 posts in DB, confirm gap extends to 15 min
- [ ] Apply to live: stop daemon → edit poster.py + settings.py → restart

**Token cost:** zero (pure Python logic)
**FB guideline benefit:** prevents "spam-like volume" flag on high-news days

---

### Step 1.2 — Image safety layer (strip names from prompts)
- [ ] Add `UNSAFE_IMAGE_CATEGORIES = ["politics", "crime", "disaster", "religion"]`
  to `config/settings.py`
- [ ] Add `_sanitize_image_prompt(prompt, category)` to `illustrator/illustrator.py`:
  - If category in UNSAFE_IMAGE_CATEGORIES: strip all proper nouns/person names
  - Replace with abstract equivalents ("a Nepali government building", "symbolic scales of justice")
  - Use regex: remove capitalized word sequences (crude but effective)
- [ ] Test in dev: run illustrator on a political article, confirm no names in prompt
- [ ] Apply to live after dev test passes

**Token cost:** zero (local string processing)
**FB guideline benefit:** dramatically reduces AI-generated face/person flags

---

## PHASE 2 — CONTENT CALENDAR (fills dead air, zero ongoing Claude cost)
**Goal:** page feels active even at 02:00 NPT when no news breaks.
**Development:** entirely in `nepalpulse_dev/` first.

### Step 2.1 — Pre-generate content library (ONE-TIME Claude cost)
- [ ] Create `content/` directory in nepalpulse
- [ ] Write `content/generate_library.py` — run ONCE manually, never by daemon:
  - One Claude call → 365 "On This Day in Nepal" entries (one per calendar date)
    Format: `{"date": "MM-DD", "en": "...", "ne": "...", "category": "history"}`
    Saved to `content/onthisday.json`
  - One Claude call → 100 Nepal fact cards
    Format: `{"en": "...", "ne": "...", "category": "geography|culture|economy"}`
    Saved to `content/factcards.json`
  - Total cost: 2 Claude Sonnet calls (use Haiku to keep cheap), never repeated
- [ ] Run `generate_library.py` once in dev, review output quality
- [ ] Copy JSON files to live `nepalpulse/content/`

**Token cost:** ~2 Haiku calls EVER (one-time generation, then free forever)

---

### Step 2.2 — "On This Day" module
- [ ] Create `content/onthisday.py`:
  - `get_today_entry()`: reads `onthisday.json`, returns entry for today's MM-DD
  - `build_post()`: generates PIL image (dark card, same style as digests)
    + formats FB text: "📅 On This Day in Nepal\n\n{en}\n\n{ne}\n\n#NepalHistory 🇳🇵"
  - Returns `{"text": ..., "image_path": ...}` — same interface as formatter
- [ ] Add PIL image renderer (reuse digest card design from summarizer.py)
- [ ] Test in dev: generate image for today's date, check PIL output
- [ ] Add to `content/scheduler.py`:
  `should_post_onthisday()` — returns True if:
    1. Not yet posted today (check new `content_posts` DB table)
    2. Current time is between 10:00–12:00 NPT (quiet slot, after cartoon)
    3. No regular news posted in last 20 min (don't crowd out real news)

**Token cost:** zero per post (reads from JSON, PIL image, no AI calls)

---

### Step 2.3 — Quote card module
- [ ] Create `content/quotecard.py`:
  - `get_quote_candidate()`: queries DB for articles with politician names
    that were posted in last 7 days; extracts a key sentence
    NO Claude call — pulls from already-formatted article body in DB
  - `build_post()`: PIL image — quote text in large font on dark background
    Nepal Pulse logo overlay, politician name attribution
  - Post 2–3×/week (Tue, Thu, Sat 11:00 NPT)
- [ ] Test in dev with real DB articles
- [ ] Add to `content/scheduler.py`

**Token cost:** zero (reuses already-formatted content from DB)

---

### Step 2.4 — Content scheduler integration
- [ ] Create `content/scheduler.py`:
  ```python
  def get_content_post_if_due(now_npt, db):
      """Returns a content post dict or None. Called from main.py event loop."""
      # Priority order: On This Day > Quote Card > Fact Card
      # Each checks its own schedule and "posted today/this week" guard
  ```
- [ ] Add `content_posts` table to `database/db.py`:
  `(id, type, posted_at, fb_post_id)` — tracks what was posted, prevents duplicates
- [ ] Wire into `main.py` event loop — add one check per tick:
  ```python
  content_post = content_scheduler.get_content_post_if_due(now, db)
  if content_post:
      poster.post(content_post)
  ```
  This fires ONLY when no news post is due (content fills gaps, doesn't compete)

**Integration risk:** low — it's additive, behind its own schedule guard

---

## PHASE 3 — SMART POSTING (improves story quality, reduces noise)
**Goal:** post the most significant story first, suppress near-duplicates.
**Development:** entirely in dev first, then careful live integration.

### Step 3.1 — Engagement re-ranking
- [ ] Add `score` column to `articles` table in `db.py` (migration: ALTER TABLE)
- [ ] Add `_score_article(article)` to `validator/validator.py`:
  ```
  score = (is_breaking × 3) + tier_weight + recency_score - duplicate_penalty
  tier_weight: Tier1=3, Tier2=2, Tier3=1
  recency_score: max(0, 1 - hours_since_verified/24)
  duplicate_penalty: -5 if very_similar_story_posted_in_6h else 0
  ```
- [ ] In `poster.py`, change article selection from "oldest verified" to "highest score"
- [ ] Test in dev with real DB data

**Token cost:** zero (pure Python math)

---

### Step 3.2 — Near-duplicate suppression (separate from corroboration)
- [ ] Add `_near_duplicate_posted_recently(article, db, hours=6)` to `poster.py`:
  Checks posted articles in last 6h for title overlap ≥ 0.4 (higher than corroboration threshold)
  Returns True if a nearly-identical story was already posted
- [ ] In posting gate: skip article if near-duplicate found
- [ ] This is different from the validator's corroboration check — corroboration CONFIRMS a story,
  this check PREVENTS re-posting the same story twice under slightly different headlines

**Token cost:** zero

---

### Step 3.3 — Tier-gated Claude calls (reduces Haiku burn on trusted sources)
- [ ] In `formatter/formatter.py`, add tier check before fact-check call:
  ```python
  if article.source_tier <= 2:
      skip_fact_check = True   # BBC/Reuters/AP/Guardian — trust them
  ```
- [ ] In `formatter/formatter.py`, add tier check before breaking-significance call:
  ```python
  if article.source_tier == 1:
      article.is_breaking = True   # Tier 1 breaking = auto-confirmed
      skip_breaking_check = True
  ```
- [ ] Estimated savings: ~30–40% reduction in Claude calls on busy news days

---

## PHASE 4 — WEEKLY DATA CARD (free, automated, high engagement)
**Goal:** rupee rate, fuel price, remittance data → weekly infographic. Zero AI cost.

### Step 4.1 — Data scraper
- [ ] Create `content/weeklydata.py`:
  - Scrape NRB (Nepal Rastra Bank) exchange rate page for USD/NPR, INR/NPR
  - Scrape NOC (Nepal Oil Corporation) for fuel prices
  - Both are public, no API key needed
  - Run every Sunday 17:00 NPT (before weekly wrap at 18:00)
- [ ] PIL image: 3-panel card (forex | fuel | remittance headline from weekly wrap)
- [ ] Post separately from weekly wrap (different format, different audience)

**Token cost:** zero (scraped data → PIL, no AI)

---

## INTEGRATION SEQUENCE (safe order)

```
Week 1:  Phase 1.1 (fatigue guard) + Phase 1.2 (image safety)
         → only settings.py + minor poster.py edits → low risk

Week 2:  Phase 2.1 (generate content library — ONE-TIME run)
         → run generate_library.py in dev, review output, copy JSONs

Week 3:  Phase 2.2 + 2.3 (On This Day + Quote Card modules)
         → build + test in dev, no live changes yet

Week 4:  Phase 2.4 (content scheduler) + wire into main.py
         → stop daemon → add content/ dir + content_posts table → restart

Week 5:  Phase 3.1 + 3.2 (re-ranking + near-duplicate suppression)
         → stop daemon → edit validator + poster → restart

Week 6:  Phase 3.3 (tier-gated Claude calls)
         → stop daemon → edit formatter → restart → watch logs for token reduction

Week 7+: Phase 4 (weekly data card) — isolated module, low risk
```

---

## ▶ NEXT STEP (update this line when you complete a step)

**Current:** Phase 1.1 — Post-fatigue guard
**File to create/edit:** `nepalpulse/poster/poster.py` + `nepalpulse/config/settings.py`
**What to do:**
1. Confirm dev directory exists: `ls "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse_dev"` — if not, create it
2. Build fatigue guard in dev first: copy poster.py to dev, add `_fatigue_gap_minutes()`
3. Test: insert 8 fake posts into dev DB dated last 12h, run poster logic, confirm 15 min gap
4. If test passes: stop live daemon, apply same edit to live poster.py, restart

**DO NOT skip the dev test step.**

---

## COST TRACKER (running total)

| Phase | Claude calls (one-time) | Claude calls (ongoing) | Other |
|-------|------------------------|----------------------|-------|
| Phase 1 (safety) | 0 | 0 saved per article on Tier1 (after 3.3) | — |
| Phase 2 (content) | 2 calls to generate JSONs | 0 per post | PIL only |
| Phase 3 (smart posting) | 0 | ~30–40% reduction | — |
| Phase 4 (data card) | 0 | 0 | Free scrape |
| **Total new cost** | **~2 Haiku calls** | **net reduction** | — |

---

## QUICK REFERENCE — SAFE COMMANDS

```bash
# Check if daemon is running
ps -A | grep "main.py" | grep -v grep

# Tail live logs
tail -f "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse/logs/nepalpulse_$(date +%Y%m%d).log"

# Check recent posts
sqlite3 "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse/nepalpulse.db" \
  "SELECT id,title,created_at FROM articles WHERE is_posted_fb=1 ORDER BY created_at DESC LIMIT 5;"

# Check post count last 12h (for fatigue guard)
sqlite3 "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse/nepalpulse.db" \
  "SELECT COUNT(*) FROM articles WHERE is_posted_fb=1 AND created_at > datetime('now','-12 hours');"

# Stop daemon safely
pkill -f "python3 main.py"

# Start daemon
cd "/Users/mohanbasnet/MASTO NEWS VECTOR/nepalpulse"
nohup python3 main.py > logs/nepalpulse_run.log 2>&1 &
```

---

*NepalPulse — Built for truth. Powered by people. 🇳🇵*
*Roadmap owner: mohan.basnet5@gmail.com*
