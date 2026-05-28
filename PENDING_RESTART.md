# Pending Restart — NepalPulse v2 "Nagarik"

Changes coded and syntax-checked but **not yet live**.
Daemon is **RUNNING** (started 2026-05-26 08:16 NPT). Items below activate on next restart.

**Items 17–23 are truly pending** — items 1–16 are already live (daemon started before those changes).

**Run `python3 restart.py`** to safely restart (3 safety checks + promotes `[p]→[x]` in PROJECTS.md).

---

## 1. Gold Card — New Source & Layout

**Files:** `scanner/gov_scanner.py`, `illustrator/civic_cards.py`

- Source changed from **FENEGOSIDA** (DNS dead) to **gold-api.com** — free JSON API, no key required
- Math: `spot_usd/oz → NPR/tola via NRB live rate → ×1.112 (10% customs + 2% agri dev fee)`
- New card layout: 5 zones (international spot / Nepal market / tax premium strip / silver / footer)
- Tax premium strip: `NPR {n} extra per tola (+11.2%)` — explains why gold costs more in Nepal
- Silver spot also fetched from gold-api.com (`/price/XAG`)

## 2. Kalimati Vegetable Card Removed

**Files:** `main.py`, `scanner/gov_scanner.py`

- `check_and_post_kalimati_card` removed from imports and 07:20 NPT scheduling block
- Reason: `kalimatimarket.com.np` DNS dead (hostname unresolvable)
- Function still in `gov_scanner.py` for future re-enable if DNS recovers
- 07:20 NPT slot now free

## 3. DB Migration — `image_url` Column Guard

**File:** `database/db.py`

- `"image_url": "TEXT"` added to `_ensure_columns()` dict
- Ensures fresh-DB installs include the column without a manual ALTER TABLE
- Live DB already has the column (patched manually 2026-05-21)

## 4. Civic Cards — 2× Supersampling

**File:** `illustrator/civic_cards.py`

- `_S = 2`: all cards render at 2160×2160, downsample to 1080×1080 via `Image.LANCZOS`
- `_ScaledDraw` wrapper scales all coordinates transparently — layout values unchanged
- Result: sharp antialiased text and edges at 1080px output

## 5. Civic Cards — Zero Decorative Lines / Rules

**File:** `illustrator/civic_cards.py`

- All `draw.line()` calls removed (NRB row separators, AQI city separators, etc.)
- Thin accent rectangles removed (NEPSE underlines, Gold tax strip accent)
- `_divider()` helper removed — was defined but never called
- Policy: sections separated by typography + spacing + background color only

## 6. Image Overlay Language Switch

**File:** `illustrator/illustrator.py`

- Photo cards for Nepali-source articles (`source_region="nepal"` or `source_language="ne"`) now show Devanagari headline as the big overlay text
- International/global articles (Reuters, AP, Al Jazeera) keep English headline overlay
- Renderer already handled Devanagari — this was a routing fix only
- Creates immediate visual differentiation: Nepali news = Nepali text on image

## 7. Five New Google News Topic RSS Feeds

**File:** `config/sources.py`

Added as Tier 2 (auto-verified, Nepal keyword baked into query):
- `Nepal Tech & Fintech (Google News)` — `region: global`
- `Nepal Climate & Environment (Google News)` — `region: global`
- `Nepal Economy & Remittance (Google News)` — `region: global`
- `Nepali Migrant Workers (Google News)` — `region: diaspora`
- `Nepal Gulf & Southeast Asia (Google News)` — `region: diaspora`

BBC Technology feed commented out — produced zero posts (global tech never mentions Nepal in headlines) but burned scan cycles every 7 min.

## 8. Topic Cluster Cap

**File:** `poster/poster.py`

- New `_topic_cluster_ok()` gate: blocks article if ≥ 3 posts sharing ≥ 2 title keywords were posted in last 48h
- Constants: `_TOPIC_CLUSTER_MAX_POSTS=3`, `_TOPIC_CLUSTER_MIN_KEYWORDS=2`, `_TOPIC_CLUSTER_HOURS=48`
- Prevents Everest-week–style saturation (9 distinct-headline posts on same event cluster)
- Called after diversity + duplicate gates; logs skip reason to DB

## 9. Tier 1 / Global Priority Boost

**File:** `database/db.py`

- `get_unposted_verified()` priority score gains `+5` for `source_region IN ('global', 'diaspora')`
- Fixes: Reuters/AP were buried under Gorkhapatra volume even when equally fresh
- Before: domestic Nepal 81% of posts, global 8%. Boost surfaces international stories

## 10. Nepali Word Correction Learner

**Files:** `database/db.py`, `formatter/formatter.py`, `nepalpulse/word_stats.py` (new)

- New DB table `nepali_corrections (id, article_id, token, replacement, pass_type, created_at)`
- `_nepali_word_guard()` now accepts `article_id` and logs every correction (all 3 passes: anusvara, leakage, domain)
- Both call sites in `formatter.py` pass `article_id` through
- `word_stats.py` CLI: `python3 word_stats.py` — shows top Hindi leakage patterns by frequency, surfaces candidates for expanding the guard lists

## 11. NEPSE Scraper Fix

**File:** `scanner/gov_scanner.py`

- **Root cause**: scraper was hitting `sharesansar.com/` homepage — picked up year "2019" as false index, leaked same value into volume + transactions fields. `nepalstock.com.np` and `merolagani.com` are JS SPAs (BeautifulSoup gets loading skeleton).
- **Fix**: switched to `sharesansar.com/market` — server-rendered page with clean HTML index table
- Parser finds "Index Open High Low Close Point Change % Change Turnover" table header, locates NEPSE Index row by label, extracts each column by position
- Second pass reads summary table for Traded Shares and Total Transactions
- **Verified live**: 2,758.49 (+16.38, +0.59%), turnover NPR 449.85 Cr, 54,497 transactions

## 12. Monsoon Situation Card

**Files:** `illustrator/civic_cards.py`, `scanner/gov_scanner.py`

- New `make_monsoon_card()` — 13th civic card type, "Civic Bold" Masterframe design
- Shows cumulative season totals: deaths (big crimson), missing + injured (side by side), displaced, economic loss (gold), infrastructure damage (crimson), districts affected footer
- Bilingual: Devanagari labels, English sub-labels, safety CTA in Devanagari
- New `post_monsoon_update()` in `gov_scanner.py` — manual trigger with NDRRMA data
- One post per day max (use `force=True` for significant data updates mid-day)
- State tracked in `gov_scanner_state.json` key `last_monsoon_post_date`

**To post** (get data from ndrrma.gov.np/situation-reports):
```python
cd nepalpulse
python3 -c "
from scanner.gov_scanner import post_monsoon_update
post_monsoon_update(
    deaths=87, missing=34, injured=142, displaced=4280,
    economic_loss_cr=1240.5, infrastructure_damage_cr=820.0,
    districts_affected=42,
    date_range='June 13 – July 14, 2026',
    top_district='Sindhupalchok',
)
"
```

## 13. Bandh Auto-Detection from RSS

**Files:** `scanner/gov_scanner.py`, `main.py`

- New `check_bandh_from_articles()` — runs each scan cycle
- Scans last 12h of verified articles from: Gorkhapatra, Rising Nepal, Onlinekhabar, Setopati, Kantipur, Nagarik News, Ratopati, Pahilopost
- Keywords: `बन्द`, `हड़ताल`, `चक्काजाम`, `bandh`, `hartal`, `strike`, `shutdown`
- Claude Haiku extracts 7 required fields: location, organizer, start_time, end_time, date_str, affected, exempt
- Auto-posts bandh card only when **all 7 fields are non-null** — skips silently if any field ambiguous
- Max 1 auto-bandh card per day (state key: `last_bandh_auto_date`)
- Processed article IDs tracked to avoid re-checking (state key: `processed_bandh_ids`, capped at 200)

## 14. Loksewa Auto-Detection from RSS + PSC Website

**Files:** `scanner/gov_scanner.py`, `main.py`

- New `check_loksewa_from_articles()` — runs each scan cycle
- **Two sources:**
  1. `psc.gov.np/notices` — direct HTML scrape; fingerprinted to detect new notices (earlier than RSS)
  2. Last 24h verified articles from: Gorkhapatra, Rising Nepal, Onlinekhabar, Setopati, Kantipur, Nagarik News
- Keywords: `लोकसेवा`, `लोक सेवा`, `PSC`, `खरिदार`, `नायब सुब्बा`, `vacancy`, `lok sewa`, etc.
- Claude Haiku extracts: position, ministry, vacancies, eligibility, deadline, days_left, adv_no, vacancy_type
- Posts only when position + ministry + eligibility + deadline are all present — skips if ambiguous
- Max 2 auto-Loksewa cards per day (state key: `loksewa_auto_count`)
- Helper functions: `_claude_extract_json()`, `_scrape_psc_notices()`, `_extract_loksewa_fields()`

## 15. Post-Publication Hindi Learning System

**Files:** `formatter/formatter.py`, `database/db.py`, `poster/poster.py`, `word_stats.py`

- `scan_postpub_hindi(article_id, nepali_text)` — runs after every successful Facebook post (called from `poster.py` after `db.mark_posted()`)
- Checks published Nepali text against two sets:
  - `_POSTPUB_EXTRA` (17 Hindi patterns not in the main guard) → logged as `pass_type='postpub_new'`
  - All `_HINDI_LEAKAGE` and `_ANUSVARA_NORM` patterns → logged as `pass_type='postpub_slip'`
- `get_learned_replacements(min_hits=2)` in `db.py` — fetches high-frequency `postpub_new` patterns
- Pass 4 in `_nepali_word_guard()` — auto-applies learned patterns (refreshed every 50 guard calls)
- `word_stats.py` updated — shows `POST-PUBLICATION LEAKAGE` and `GUARD FAILURES` sections
- CLI: `cd nepalpulse && python3 word_stats.py --postpub`

## 16. Nepali Word Quality — Hindi Leakage Guard + Readability

**File:** `formatter/formatter.py`

- **16 new patterns added to `_HINDI_LEAKAGE`** (were only in `_POSTPUB_EXTRA` detection, never blocking):
  - Multi-word postpositions: `के लिए→का लागि`, `के साथ→सँग`, `के बारे में→बारेमा`, `के रूप में→रूपमा`
  - Time phrases: `के बाद→पछि`, `से पहले→अघि`
  - Other multi-word: `के मुताबिक→अनुसार`, `बताते हुए→जानकारी दिँदै`, `कम से कम→कम्तीमा`, `सब कुछ→सबै केही`
  - Single words: `हालांकि→यद्यपि` (anusvara form — chandrabindu form was guarded but not this), `फिलहाल→हालसम्म`, `खासकर→विशेषगरी`, `ज्यादा→धेरै`, `ज्यादातर→अधिकांश`, `बेहद→अत्यन्त`
- **Nepali prompt — 2 readability rules added:**
  - एउटा वाक्यमा एउटा मात्र विचार (one idea per sentence, no compound chains)
  - १५–२५ शब्द प्रति वाक्य target (mobile reading length)
- **Prompt vocabulary section expanded** — all new mappings shown as explicit examples so Claude Haiku sees them before writing

## 17. Stories — Breaking & Civic Only

**File:** `poster/poster.py`

- Stories now only fire when `article.get("is_breaking")` is True OR `source_region` is in `("civic", "nrb", "fuel", "aqi", "earthquake", "gold", "nepse")`
- Previously: every article triggered a story card → followers saw same news twice (feed + story)
- Result: stories become a signal for urgency; routine articles post to feed only

## 18. Category Palette — Card Visual Variety

**File:** `illustrator/meridian_card.py`

- Added `_CATEGORY_PALETTE` dict: 9 categories each get a unique `(top_band_rgb, accent_rgb)`
- Top band color changes per category; bone body and navy footer unchanged (brand preserved)
- Roundel background now matches top band (was always `GROUND` navy — looked mismatched on tinted bands)
- Category label text (Devanagari + English) uses accent color instead of hardcoded `SIGNAL` crimson
- Palettes: politics=crimson, economy=forest green/gold, disaster=charcoal/amber, india_nepal=deep blue/saffron, china_nepal=slate/jade, society=umber/terracotta, geography=teal/mountain blue, international=purple/lavender, diaspora=deep teal/copper

## 19. NEPSE Card — Correct Close Time + Data Validation

**Files:** `main.py`, `scanner/gov_scanner.py`

- **Post time moved 15:30 → 15:45 NPT** — sharesansar publishes intraday values during trading; 15:45 gives 45 min after market close (15:00) for final figures to settle. Root cause: today printed 2786.35 (mid-session) instead of correct close 2777.10.
- **Retry on failure** — `last_nepse_card_date` now only set when `check_and_post_nepse_card()` returns `True`; previously set unconditionally so failed/stale fetches were never retried
- **Cross-validation** — turnover from index table vs summary table must agree within 2%; aborts if mismatch
- **Sanity bounds** — index must be 800–6000; daily change must be <10% of index; volume >100,000; transactions >1,000; any breach aborts and logs a warning

## 20. Haiku Prompt — Explicit Hindi Blacklist

**File:** `formatter/formatter.py` (`_generate_nepali_fields`)

- Added "प्रतिबन्धित हिन्दी शब्दहरू" section to Claude Haiku Nepali prompt
- Lists top 19 high-frequency leakers with correct replacements and hit counts visible to model
- Top offenders shown explicitly: पूरा→पूरै (83×), साथ→सँगै (30×), केवल→मात्र (21×), पुलिस→प्रहरी (9×), शुरू→सुरु (9×) etc.
- Word guard (`_HINDI_LEAKAGE`) already covers all these as a safety net — this makes Claude not generate them in the first place
- Confirmed: all `_POSTPUB_EXTRA` words already in `_HINDI_LEAKAGE` — guard is complete

## 21. Wikimedia Commons Photo Search

**File:** `illustrator/wikimedia.py` (new)

- Fetches a CC-licensed real photo from Wikimedia Commons when the RSS article has no image
- Three recency tiers to keep photos current:
  - Politician names + government building keywords (parliament, Singha Durbar, ministry…) → **2025+ uploads only**
  - General politics, economy, infrastructure → **2020+ uploads only**
  - Disaster, geography, nature → **any year** (timeless subjects)
- Politician detection: scans article title for known names (KP Oli, Prachanda, Deuba, Rabi, Balen Shah, Modi, Trump, etc.) — triggers face photo search first
- Sorts results by `create_timestamp_desc` (newest upload first)
- If strict year filter yields nothing, retries once without year filter before giving up
- Zero API keys required

## 22. Pollinations AI Image Generation (Fallback)

**File:** `illustrator/pollinations.py` (new)

- Generates a 1080×1080 photorealistic image via Pollinations.ai when both RSS and Wikimedia return nothing
- Free, no API key, uses `flux-realism` model
- Prompt built from formatter's `scene` field + category context hint + editorial style suffix ("photorealistic, news photography, no text, no watermark")
- Random seed per call — no two retries produce the same image
- 20s timeout; returns None on failure (graceful — PIL card takes over)
- Zero new dependencies (urllib only)

## 23. Photo Card — Devanagari Primary Headline + English Subhead

**Files:** `illustrator/meridian_card.py`, `illustrator/illustrator.py`

- All photo cards (RSS, Wikimedia, Pollinations) now show **Devanagari as the big headline** when it exists, regardless of article source
- English headline rendered as smaller subhead (70% opacity, 22px) below the Devanagari block
- Previously: only Nepal-source articles showed Devanagari; international articles showed English only
- `render_photo_card_from_bytes()` added to `meridian_card.py` — same chyron overlay as `render_photo_card()` but accepts raw image bytes instead of a URL (used by Pollinations path)
- Image hierarchy in `illustrator.py`: RSS → Wikimedia → Pollinations AI → PIL text card

---

## Safety checks before restart

| Check | Command | Pass condition |
|---|---|---|
| Gap since last post | `python3 restart.py --check` | ≥ 90 min |
| Time of day | — | 23:00–06:00 NPT |
| Circuit breaker | — | No active FB block |

Run `python3 restart.py --check` to see current state without restarting.
