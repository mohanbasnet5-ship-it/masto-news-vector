# NepalPulse — Claude Code Project Handoff
# Paste this entire file as your FIRST message in Claude Code

---

## PROJECT NAME
NepalPulse — "Heartbeat of the Nation"

## MISSION
Nepal's first globally verified, independent, donation-only news platform.
Scans global + local sources, validates news, auto-posts to Facebook + X.

---

## WHAT WE ARE BUILDING

### The Pipeline
```
Every 2-3 hours:
RSS Feeds → Scan for "Nepal/Nepali" → Validate (2+ sources) → Format per platform → Auto-post
```

### Rules
- 2+ sources reporting same story = ✅ VERIFIED → Publish
- 1 source only = ❌ SKIP — never publish
- Posting frequency: every 2-3 hours
- Revenue: donations only — no ads, no sponsors

---

## SOURCE TIERS

| Tier | Sources | Rule |
|------|---------|------|
| Tier 1 | BBC, Reuters, AP, Al Jazeera, UN | Auto-verified, publish immediately |
| Tier 2 | The Hindu, Guardian, Times of India | Needs 1 more source |
| Tier 3 | Onlinekhabar, Kantipur, Setopati, Ratopati, Himalayan Times | Needs 2+ sources |
| Tier 4 | Social media, blogs | NEVER publish |

---

## PLATFORMS

| Platform | Format | Post Time (Nepal Time) |
|----------|--------|----------------------|
| Facebook | Full story + 3 paragraphs + question | 7am, 12pm, 8pm |
| X/Twitter | Punchy thread + tag relevant orgs | 8am, 1pm, 9pm |
| Instagram | Carousel (Phase 2) | 6-9pm |
| TikTok | 60sec script (Phase 2) | 7-10pm |

---

## POST FORMAT

```
🔴 NEPAL PULSE

[Catchy headline]

[2-3 sentences, clear, global tone]

✅ VERIFIED — Reported by [Source 1] + [Source 2]

🇳🇵 #NepalPulse #Nepal #Breaking
```

---

## CONTENT CATEGORIES + GOVT TAGS

| Category | Hashtag | Tag These Accounts |
|----------|---------|-------------------|
| Environment/Mountains | #NepalNature | @MinistryofFEN @NTBNepal |
| Tourism | #NepalGlobal | @NTBNepal @TourismMinNepal |
| Breaking news | #NepalBreaking | relevant dept |
| World covers Nepal | #WorldOnNepal | relevant dept |
| Economy | #NepalEconomy | @FinanceMinNepal |
| Govt accountability | #GovtWatch | @MoHANepal |
| Diaspora | #GlobalNepali | none |

---

## PROJECT FILE STRUCTURE TO BUILD

```
nepalpulse/
├── config/
│   ├── sources.py       # RSS feeds by tier
│   ├── keywords.py      # Nepal/Nepali keywords
│   └── settings.py      # API keys + schedule
├── scanner/
│   └── scanner.py       # Pulls + filters RSS feeds
├── validator/
│   └── validator.py     # Cross-references, assigns verified status
├── formatter/
│   └── formatter.py     # Rewrites news per platform using Claude AI
├── poster/
│   └── poster.py        # Posts to Facebook + X
├── database/
│   └── db.py            # SQLite — stores all articles + status
├── logs/                # Auto-generated run logs
├── main.py              # Master runner
└── setup.sh             # One-time Mac setup script
```

---

## TECH STACK

| Tool | Purpose |
|------|---------|
| Python 3 | Main language |
| feedparser | Parse RSS feeds |
| BeautifulSoup | Scrape where no RSS |
| SQLite | Local database |
| Claude AI API | Rewrite news in catchy format |
| Facebook Graph API | Auto-post to Facebook Page |
| X (Twitter) API v2 | Auto-post to X |
| launchd (Mac) | Schedule every 2-3 hours |

---

## DEVICE PLAN

- Phase 1: Build + test on Mac laptop
- Phase 2: Move to small dedicated device (like Raspberry Pi) — runs 24/7
- Phase 3: Same device hosts website

---

## WHAT TO BUILD FIRST IN CLAUDE CODE

1. setup.sh — one-time Mac installer
2. config/sources.py — all RSS feeds
3. config/keywords.py — Nepal keywords
4. config/settings.py — API keys template
5. database/db.py — SQLite setup
6. scanner/scanner.py — RSS scanner
7. validator/validator.py — cross-reference logic
8. formatter/formatter.py — Claude AI formatter
9. poster/poster.py — Facebook + X poster
10. main.py — master runner that chains everything

---

## FIRST INSTRUCTION FOR CLAUDE CODE

"Build the NepalPulse news automation system starting with 
setup.sh and the scanner. Mac OS. User is not a coder — 
every script must be fully working, no placeholders. 
Start with setup.sh that installs Python dependencies, 
then build scanner/scanner.py that pulls RSS feeds from 
all tier sources, filters for Nepal/Nepali keywords, 
and saves results to SQLite database."

---

## SOCIAL HANDLES TO REGISTER
- X: @NepalPulse
- Facebook: facebook.com/NepalPulse
- Instagram: @nepalpulse
- TikTok: @nepalpulse
- YouTube: @NepalPulse

---

*NepalPulse — Built for truth. Powered by people. 🇳🇵*
