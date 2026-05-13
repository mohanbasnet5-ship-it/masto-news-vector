# 🇳🇵 NepalPulse
## "Heartbeat of the Nation"

Nepal's first globally verified, independent news platform.
**Donations only. No ads. No sponsors. No bias.**

---

## Mission
- Scan global + local sources for Nepal/Nepali news
- Validate: 2+ sources = ✅ Verified | 1 source = ❌ Skip
- Auto-post to Facebook + X every 2-3 hours
- Amplify world coverage of Nepal back to Nepal
- Tag concerned govt departments when action is needed

---

## Project Structure

```
nepalpulse/
├── config/
│   ├── sources.py        # All RSS feed sources by tier
│   ├── keywords.py       # Nepal/Nepali keywords to scan
│   └── settings.py       # API keys, posting schedule, etc.
│
├── scanner/
│   └── scanner.py        # Pulls RSS feeds, filters Nepal news
│
├── validator/
│   └── validator.py      # Cross-references sources, assigns verified status
│
├── formatter/
│   └── formatter.py      # Rewrites news in catchy format per platform
│
├── poster/
│   └── poster.py         # Posts to Facebook + X (Twitter)
│
├── database/
│   └── db.py             # SQLite database handler
│
├── logs/                 # Auto-generated logs
├── main.py               # Master runner — runs everything in sequence
└── setup.sh              # One-time Mac setup script
```

---

## Source Tiers

| Tier | Sources | Validation |
|------|---------|------------|
| **Tier 1** | BBC, Reuters, AP, Al Jazeera, UN | ✅ Auto-verified |
| **Tier 2** | The Hindu, Guardian, Times of India | Needs 1 more source |
| **Tier 3** | Onlinekhabar, Kantipur, Setopati, Ratopati | Needs 2+ sources |
| **Tier 4** | Social media, blogs | ❌ Never publish |

---

## Platforms

| Platform | Format | Posting Time (Nepal Time) |
|----------|--------|--------------------------|
| **Facebook** | Full story, 3 paragraphs + question | 7am, 12pm, 8pm |
| **X (Twitter)** | Punchy thread, tag relevant orgs | 8am, 1pm, 9pm |
| **Instagram** | Carousel format (future) | 6pm-9pm |
| **TikTok** | 45-60 sec script (future) | 7pm-10pm |

---

## Content Categories

| Tag | Focus |
|-----|-------|
| #NepalGlobal | Everest, tourism, culture reaching world |
| #NepalBreaking | Protests, politics, disasters |
| #WorldOnNepal | BBC, CNN, Al Jazeera Nepal stories |
| #NepalEconomy | Remittance, trade, investment |
| #GovtWatch | Policy, corruption, accountability |
| #NepalNature | Mountains, climate, rivers |
| #GlobalNepali | Nepalis excelling worldwide |

---

## Post Format

```
🔴 NEPAL PULSE

[Catchy 1-line headline]

[2-3 sentences — clear, factual, global tone]

✅ VERIFIED — Reported by [Source 1] + [Source 2]

🇳🇵 #NepalPulse #Nepal #Breaking
```

---

## Setup Instructions

### Step 1 — Run Setup Script (Mac)
```bash
bash setup.sh
```

### Step 2 — Add API Keys
Edit `config/settings.py` and add:
- Facebook Page Token
- X (Twitter) API Keys
- Anthropic API Key (for content formatting)

### Step 3 — Run NepalPulse
```bash
python3 main.py
```

### Step 4 — Schedule (runs every 2-3 hours automatically)
```bash
bash schedule.sh
```

---

## Roadmap

| Phase | Task | Status |
|-------|------|--------|
| ✅ 1 | Brand + planning | Done |
| 🔄 2 | Scanner + validator | Building |
| ⏳ 3 | Auto-poster | Upcoming |
| ⏳ 4 | Website + whitepaper | Month 2 |
| ⏳ 5 | Donation page | Month 2 |
| ⏳ 6 | Move to dedicated device | Month 3 |

---

*NepalPulse — Built for truth. Powered by people.*
