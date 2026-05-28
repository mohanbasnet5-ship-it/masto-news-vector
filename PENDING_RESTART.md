# Pending Restart — NepalPulse v2 "Nagarik"

Changes coded and syntax-checked but **not yet live**.
Daemon is **STOPPED** (crashed — last post 2026-05-28 00:55 NPT). Safe to restart.

**Run `python3 restart.py`** to safely restart (3 safety checks + promotes `[p]→[x]` in PROJECTS.md).

---

## ✅ LIVE — Items 1–16 (loaded in daemon run started 2026-05-26)

| # | Change | Files |
|---|---|---|
| 1 | Gold card: gold-api.com source, new 5-zone layout, tax premium strip | `gov_scanner.py`, `civic_cards.py` |
| 2 | Kalimati card removed from scheduler (DNS dead) | `main.py`, `gov_scanner.py` |
| 3 | DB migration: `image_url` column guard in `_ensure_columns()` | `db.py` |
| 4 | Civic cards 2× supersampling → LANCZOS 1080px output | `civic_cards.py` |
| 5 | Civic cards: zero decorative lines/rules — spacing only | `civic_cards.py` |
| 6 | ~~Image overlay language switch~~ **superseded by item 23** | — |
| 7 | Five new Google News RSS feeds (tech, climate, economy, migrant, Gulf) | `sources.py` |
| 8 | Topic cluster cap: blocks ≥3 posts sharing ≥2 keywords in 48h | `poster.py` |
| 9 | Global/diaspora priority +5 in queue scoring | `db.py` |
| 10 | Nepali word correction learner: DB table + `word_stats.py` CLI | `db.py`, `formatter.py` |
| 11 | NEPSE scraper: switched to `sharesansar.com/market`, column-position parser | `gov_scanner.py` |
| 12 | Monsoon situation card (13th civic card, manual trigger) | `civic_cards.py`, `gov_scanner.py` |
| 13 | Bandh auto-detection from RSS (Claude Haiku extracts 7 fields) | `gov_scanner.py`, `main.py` |
| 14 | Loksewa auto-detection from RSS + PSC website scrape | `gov_scanner.py`, `main.py` |
| 15 | Post-publication Hindi learning: DB logging + pass 4 auto-apply | `formatter.py`, `db.py`, `poster.py` |
| 16 | Hindi leakage guard: 16 new patterns + Haiku readability rules | `formatter.py` |

---

## 🔴 PENDING — Items 17–23 (activate on next restart)

### 17. Stories — Breaking & Civic Only
**File:** `poster/poster.py`

- Stories now only fire when `is_breaking=True` OR `source_region` in `(civic, nrb, fuel, aqi, earthquake, gold, nepse)`
- Previously: every article triggered a story → followers saw same news twice
- Result: stories signal urgency only; routine feed posts stay feed-only

### 18. Category Palette — PIL Card Visual Variety
**File:** `illustrator/meridian_card.py`

- `_CATEGORY_PALETTE`: 9 categories get unique `(top_band_rgb, accent_rgb)`
- politics=crimson · economy=forest green/gold · disaster=charcoal/amber · india_nepal=deep blue/saffron · china_nepal=slate/jade · society=umber/terracotta · geography=teal/mountain blue · international=purple/lavender · diaspora=deep teal/copper
- Roundel background matches top band; accent drives category label color

### 19. NEPSE Card — Correct Close Time + Validation
**Files:** `main.py`, `scanner/gov_scanner.py`

- Post time: **15:30 → 15:45 NPT** (45 min after close for final figures)
- Retry on failure: `last_nepse_card_date` only set on success (was set unconditionally)
- Cross-validation: index-table turnover vs summary-table must agree within 2%
- Sanity bounds: index 800–6000, change <10%, volume >100,000, transactions >1,000

### 20. Haiku Prompt — Explicit Hindi Blacklist
**File:** `formatter/formatter.py`

- "प्रतिबन्धित हिन्दी शब्दहरू" section added to Nepali prompt
- Top 19 leakers listed with hit counts: पूरा→पूरै (83×), साथ→सँगै (30×), केवल→मात्र (21×) etc.
- Makes Claude avoid them at generation time; word guard remains as safety net

### 21. Wikimedia Commons Photo Search
**File:** `illustrator/wikimedia.py` (new)

- CC-licensed real photo fetched when RSS has no image
- Three recency tiers:
  - Politician names + gov building keywords → **2025+ uploads only**
  - General politics, economy, infrastructure → **2020+ uploads only**
  - Disaster, geography, nature → **any year**
- Politician detection from title (KP Oli, Prachanda, Deuba, Rabi, Balen, Modi, Trump…) → face photo search first
- `gsrsort=create_timestamp_desc` — newest uploads surface first
- Falls back without year filter if strict search yields nothing

### 22. Pollinations AI Image Generation (Second Fallback)
**File:** `illustrator/pollinations.py` (new)

- Generates 1080×1080 photorealistic image when RSS + Wikimedia both return nothing
- Free, no API key — `flux-realism` model via `image.pollinations.ai`
- Prompt: `scene` field + category context + "photorealistic, editorial news photography, no text"
- Random seed per call; 20s timeout; None on failure → PIL card takes over

### 23. Photo Card — Devanagari Primary + English Subhead (supersedes item 6)
**Files:** `illustrator/meridian_card.py`, `illustrator/illustrator.py`

- All photo cards (RSS, Wikimedia, Pollinations) show **Devanagari as the big headline** whenever it exists — regardless of source language
- English rendered as smaller 22px subhead (70% opacity) below Devanagari
- `render_photo_card_from_bytes()` added for Pollinations raw-bytes path
- Full image hierarchy: RSS photo → Wikimedia → Pollinations AI → PIL text card

---

## Monsoon card — manual trigger (no restart needed)

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

---

## Safety checks before restart

| Check | Command | Pass condition |
|---|---|---|
| Gap since last post | `python3 restart.py --check` | ≥ 90 min |
| Time of day | — | 23:00–06:00 NPT |
| Circuit breaker | — | No active FB block |

Run `python3 restart.py --check` to see current state without restarting.
