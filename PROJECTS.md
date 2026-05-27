# NepalPulse — Project Management

Master tracker for all active initiatives across four tracks.

**Status markers:** `[ ]` not started · `[~]` in progress · `[p]` pending restart · `[x]` live
**Priority:** **P0** do today · **P1** this week · **P2** this month · **P3** backlog

Run `./pm.command` in Finder for a status dashboard.
Run `python3 pm.py` in Terminal for the same.
Run `python3 restart.py` to safely restart the daemon (runs 3 checks, promotes `[p]→[x]` on success).

---

## Track A — System & Technical

### A1 Breaking News
- [x] **P1** Fast-track breaking — validator.py Pass 2: 2+ Tier 1/2 sources on same story within 20 min → `is_breaking=1` automatically. (2026-05-17)
- [ ] **P1** Earthquake direct feed — poll NSC Nepal (`seismonepal.gov.np`) every 5 min; auto-post any magnitude 4.5+ within 2 minutes
- [x] **P1** Same-story cross-source block — validator.py Pass 3: lower-tier duplicate blocked at verification time; same-tier: later arrival blocked. Threshold 0.60. (2026-05-17)

### A4 Tagging System
- [x] **P1** Organisation tag system — `config/tag_rules.py`: 35 entities, category→(local, national) rules, LOCATION_MAP (77 districts), LOCAL_POLICE + LOCAL_GOVERNMENT resolvers. Never tags individual politicians — only org/ministry pages. (2026-05-21)
- [x] **P1** Formatter wired — `formatter.py` replaces `_detect_politician_tags()` with `resolve_tags(category, title, body)` → max 2 org tags per post. (2026-05-21)
- [ ] **P2** Fill local police station FB slugs — 14 districts in LOCAL_POLICE all have `slug=None`; visit each district police FB page to fill in
- [ ] **P2** Fill local government slugs — Lalitpur, Birgunj, Butwal, Dharan, Dhangadhi, Nepalgunj, Hetauda, Janakpur missing
- [ ] **P2** Fill Ministry of Finance slug — no vanity FB slug found; check mof.gov.np footer for official page link
- [ ] **P2** Fill destination embassy slugs — Malaysia, Qatar, Saudi, UAE, Korea, Japan for diaspora stories

### A2 Reliability
- [x] **P1** Posting block audit trail — `db.log_skip_reason()` writes diversity/duplicate skip reason to `posting_block_reason` on every rejected article. (2026-05-17)
- [ ] **P2** Feed error alert — if 3+ Tier 1/2 feeds fail in one scan cycle, send Ntfy push notification
- [ ] **P2** Daemon death alert — Ntfy alert if daemon exits without launchd restart within 5 min
- [ ] **P2** Test launchd auto-restart — restart Mac cold, confirm daemon starts without any manual step

### A3 Infrastructure
- [x] Recovery mode flag (`RECOVERY_MODE`) — auto-lifts after 3 days
- [x] FB circuit breaker — escalating 2h → 6h → 24h, persisted across restarts
- [x] Startup grace — 90 min (3h after recent circuit trips) holds posting after restart
- [x] Velocity brake — max 8 posts/4h (4 in recovery mode)
- [x] Duplicate post guard — 24h lookback, 50% title overlap threshold, punctuation-stripped tokens
- [x] Hindi leakage guard — 28 word pairs, two-layer (prompt + code gate)
- [x] Northeast India source filter — `nepal_explicit` flag requires "nepal/nepali/gorkha" in title

---

## Track B — Content & Voice

### B1 Immediate Wins
- [x] **P0** Re-enable Meridian story cards — set `ENABLE_STORY_IMAGES=1` in `nepalpulse/.env`. Cards are built, tested, and 3–5× reach of text posts on Facebook
- [x] **P0** Pin mission statement to Facebook page — LIVE 2026-05-17. Bilingual "Nepal is far. Keep the news close." + location comment hook. PP and cover also updated.

### B2 Post Quality
- [x] **P1** Story-specific engagement hooks — `_topic_hook()` in formatter.py maps category + keywords to a specific Nepali question (Everest, disaster, economy, etc.). (2026-05-17)
- [x] **P1** "This matters because…" editorial line — injected into Claude user_msg for politics/economy/disaster/india_nepal/china_nepal; Claude ends body with concrete real-world impact sentence. (2026-05-17)
- [x] **P1** Achievement/pride tone — `_is_nepal_pride()` detects records/medals/rankings; TONE OVERRIDE injected into Claude user_msg for celebratory voice. (2026-05-17)

### B3 Recurring Series (builds return habit)
- [ ] **P1** "यस हप्ता नेपाल इतिहासमा" (This week in Nepal history) — every Thursday, one event from Nepal's past on this week's date. Short format, manually drafted weekly batch, no API needed
- [ ] **P1** "परदेशी नेपाली" (Nepali Abroad) — weekly spotlight on migrant worker issues: labor agreements, rights violations, repatriation, country-specific updates (Gulf, Malaysia, Korea, Japan). Enormous underserved diaspora audience
- [ ] **P1** "Everest Season Live" — April–May only. Daily summit counter card: summits / deaths / rescues / active expeditions. Update on every change. Engages global Everest audience beyond Nepali diaspora
- [ ] **P2** "आजको नेपाल" (Today's Nepal) — daily morning digest card: top 3 stories + exchange rate + AQI. One card, everything. For people who want to stay informed in 10 seconds. Post at 07:30 NPT
- [ ] **P2** "एक तथ्य, एक संख्या" (One fact, one number) — weekly PIL data card: remittance $9B, 26% of GDP; tourism arrivals; Everest permits issued, etc. Zero API cost
- [ ] **P2** Explainer format — for complex stories (budget, BRI, election), a 3-bullet "What you need to know" block added by formatter when category = economy or politics
- [ ] **P2** Scholarship deadline countdown series — post at D-30, D-14, D-7, D-3, D-1 for major scholarships (China, India, Fulbright, Turkey). Each angle slightly different. D-1 goes viral as people panic-share to everyone they know

---

## Track C — Community & Interaction

### C1 Engagement Mechanics
- [ ] **P1** Native Facebook polls — 3× per week on major stories. One-tap polls get 40× more algorithmic reach than text posts. Example: "के नेपाल BRICS मा सामेल हुनुपर्छ? / Should Nepal join BRICS?" (manual, takes 2 min per poll). Always post after fuel hike, bandh, or major political announcement
- [ ] **P1** "On this day in Nepal" posts — short weekly batch of 7 historical facts, one auto-posted per day. Curate once, runs for a week
- [ ] **P1** "Tag a family member" CTA on practical content — exchange rate: "Tag your family member working abroad." Bandh alert: "Tag someone who needs to know before they leave home." Drives comments → algorithm boost
- [ ] **P2** "Before WhatsApp gets it wrong" framing — on major breaking stories add: "यो जानकारी तपाईंको WhatsApp मा आउन सक्छ — तर गलत हुन सक्छ। Verified version share गर्नुहोस्।" Positions NepalPulse as the correction source
- [ ] **P2** Comment section as information layer — post = core update, first comment = source link, second comment = full detail/PDF. Rewards deep readers, keeps post clean and shareable
- [ ] **P2** Consistent series emoji as visual bookmarks — 💰 आजको दर · 🌫️ आजको वायु · ⚡ बिजुली · 🚨 Alert · 📋 सरकारी जागिर · 🏔️ एभरेस्ट · ✈️ परदेशी नेपाली. Same emoji every post = people scroll until they see it and stop

### C2 Community Building
- [ ] **P2** Facebook Group — "NepalPulse Community | नेपाल छलफल" alongside the page. Page reaches people; group builds relationships. Readers discuss stories here
- [ ] **P2** Reader submissions prompt — monthly post asking for photos, stories, or tips from any district. Turns passive readers into contributors
- [ ] **P3** Community spotlight — monthly recognition of the most engaged reader or sharer by name. One person feeling seen brings in ten more

---

## Track D — Owned Audience (Survival Insurance)

If Facebook bans the page again, this is what survives. Build this in parallel with everything else.

### D0 Organic Growth — Do Before Any Paid Ads
- [~] **P0** Personal outreach — founding message drafted (2026-05-21). Send 1:1 to friends and family. Text in project_branding memory. Never broadcast — personal only.
- [ ] **P0** Replace pinned post — current one (2026-05-17) answers WHY not WHAT. New text drafted (2026-05-21): lists all 6 content types with emoji anchors. Saved in growth_goals memory. Pin first, boost second.
- [ ] **P0** Always-on awareness ad — NPR 100–150/day, no end date. Objective: Page Likes. Target: UAE, Qatar, Saudi, Bahrain, Kuwait, Malaysia. Language: Nepali. Age 22–45. Facebook Feed only. Image: NRB rate card or gold card. Creative: short "Nepal news. Both languages. Every day." text. Check weekly — stop if cost per like exceeds NPR 200.
- [ ] **P0** Reply to every comment within 1 hour — trains FB algorithm that page is alive
- [ ] **P1** Post one Facebook poll per week — 40× more algorithmic reach than text posts
- [ ] **P1** Add "Full story in first comment" to every card caption — gives people reason to engage

### D1 Email Newsletter (highest priority)
- [ ] **P1** Create Mailchimp free account — up to 500 contacts, free forever (manual, ~15 min)
- [ ] **P1** Weekly digest email — top 5 Nepal stories of the week, sent Sunday 8pm NPT. Repurposes the weekly wrap Claude already writes
- [ ] **P1** Add newsletter signup link to Facebook page About section and web reader footer
- [ ] **P2** Automate weekly wrap email via Mailchimp API — Sunday wrap (already generated) sent to subscribers automatically

### D2 Platform Expansion
- [ ] **P2** Telegram channel — "NepalPulse | नेपाल समाचार". Create via @BotFather, get token, add as admin. Fill `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHANNEL_ID` in `.env` to activate auto-posting
- [ ] **P2** Instagram — link Nepal Pulse Facebook Page in Meta Business Suite (manual). Meridian 1080×1080 cards are already perfectly sized
- [ ] **P3** Public web reader — deploy `web/app.py` on Render free tier (~1 hour setup). Gives the page a URL that survives any platform ban

---

---

## Track E — Citizen Services & Government Data

The anti-WhatsApp strategy: every piece of information below reaches Nepalis through unverified WhatsApp forwards. NepalPulse becomes the verified source people cite to stop the misinformation chain.

### E1 Daily Survival Data (highest citizen frustration)
- [~] **P0** Bandh/strike alert system — `trigger_bandh_card()` built in gov_scanner.py; card design locked. Still needed: Ntfy operator alert when RSS detects bandh keywords
- [x] **P0** Fuel price change monitor — `check_and_alert_fuel_prices()` in gov_scanner.py scrapes NOC hourly; Ntfy urgent alert sent on price change with ready-to-paste trigger_fuel_card() call. (2026-05-17)
- [x] **P1** Nepal Rastra Bank exchange rate daily card — live in gov_scanner.py; posts 07:00 NPT daily. 💰 आजको दर series (2026-05-17)
- [ ] **P1** NEA load shedding tracker — trigger function ready; needs NEA scraper
- [x] **P1** OpenAQ air quality card — live in gov_scanner.py; posts 08:00 NPT daily. 🌫️ आजको वायु series (2026-05-17)
- [ ] **P2** KUKL water supply schedule — Kathmandu ward-by-ward schedule; scrape or partner with KUKL. Diaspora asks "did mum get water today?" — nobody covers this
- [ ] **P2** DHM weather + flood/landslide alerts — Department of Hydrology and Meteorology RSS; automated post for any red/orange warning during monsoon (June–September). Diaspora with family in hill districts are terrified; this makes you essential

### E2 Government Services (everyone's nightmare)
- [ ] **P1** Lok Sewa Aayog (PSC) tracker — monitor PSC website for exam schedules, results, vacancy notices. Card: position, vacancies, deadline (days remaining countdown), eligibility. Government jobs are the dream for millions; competing pages post this late or wrong
- [ ] **P1** SEE / NEB exam results alert — monitor NEB results publication; post immediately when results drop with grade distribution stats. Every family with teenagers is watching
- [ ] **P2** Scholarship alert system — monitor embassy websites (China CSC, Indian ICCR, US Fulbright, Turkey Türkiye Burslari, Korean KGSP). Card: scholarship name, fields, deadline countdown, eligibility. Post at D-30, D-14, D-7, D-3, D-1. Life-changing for qualifying readers
- [ ] **P2** Passport/visa processing delay tracker — monitor DoP announcements + community reports. "Current wait time: ~X weeks." People applying don't know this — shared by everyone waiting
- [x] **P2** USGS earthquake feed — live in gov_scanner.py; checks every scan cycle, posts M≥4.5 within ~7 min. Card design locked. 🚨 series (2026-05-17)
- [ ] **P3** DOFe / migrant worker advisories — Department of Foreign Employment notices: banned destination countries, new labor agreements, worker rights alerts. High impact for Gulf/Malaysia/Korea-bound workers

### E3 Markets & Economy (diaspora money anxiety)
- [ ] **P2** NRB monetary policy plain-language translation — when NRB changes interest rates or policy, post plain Nepali/English explanation. "Your savings account rate is now X%. Fixed deposit Y%." Dense policy → actionable for ordinary readers
- [ ] **P2** Remittance corridor alerts — "Malaysia restricts Nepali workers from X sector." "Qatar new visa rules effective [date]." Life-altering information that currently arrives via WhatsApp weeks late
- [ ] **P3** Nepal Stock Exchange (NEPSE) weekly summary — index movement, top gainers/losers. One card, end of week. Growing retail investor class in Nepal
- [ ] **P3** Real estate / land price trend — quarterly NRB data on property prices by district. Diaspora buying land back home; nobody translates the stats

---

## Track F — Card System & Visual Formats

One Meridian card design is not enough. A family of cards — same brand DNA, different visual language per type — so people recognize the content category before reading a word.

### F1 Alert Cards (urgent, high-share)
- [x] **P0** Bandh alert card — red background, bold affected areas + duration + exemptions (ambulance, press). `make_bandh_card()` + `trigger_bandh_card()` in gov_scanner.py. (2026-05-21)
- [x] **P0** Fuel price card — split "पहिले/Before" · "अहिले/Now" design, big numbers, red/green. `make_fuel_card()` + `check_and_post_fuel_card()`, wired in main.py per scan cycle. (2026-05-21)
- [x] **P1** Earthquake alert card — dark navy, magnitude large, location/depth/NPT time. `make_earthquake_card()`, wired in main.py per scan cycle, posts M≥4.5 within ~7 min. (2026-05-21)
- [ ] **P1** Flood/landslide warning card — DHM-sourced, orange/red palette, affected districts listed, DHM alert level (watch/warning/danger)

### F2 Daily Habit Cards (7–8 AM NPT, screenshot-and-forward)
- [x] **P1** Exchange rate card — 6 currencies, NRB rate, daily change, date prominent. `make_rate_card()`, wired 07:00 NPT daily. Currency order: USD·EUR·INR·SAR·MYR·QAR·GBP (Gulf/worker priority). (2026-05-21)
- [x] **P1** AQI card — color-coded circles per city, health advisory, "mask recommended" when red. `make_aqi_card()`, wired 08:00 NPT daily. (2026-05-21)
- [ ] **P2** "आजको नेपाल" digest card — top 3 headlines + exchange rate snapshot + AQI dot. One card = full morning briefing. 07:30 NPT daily
- [ ] **P2** Load shedding card — today's affected groups by time slot. Clean grid. People save it to phone

### F3 Achievement & Pride Cards (diaspora shares to non-Nepali friends)
- [x] **P1** Everest season counter card — summits / deaths / rescues / weather window. `make_everest_card()` + `trigger_everest_card()` in gov_scanner.py. (2026-05-21)
- [x] **P2** Nepal cricket score card — Nepal vs [team], score, run rate, result. `make_cricket_card()` + `trigger_cricket_card()` in gov_scanner.py. (2026-05-21)
- [ ] **P2** "Nepal on the world stage" card — triggered by formatter's existing `_is_nepal_pride()` flag. Distinct gold/crimson design so these stand out from news cards
- [ ] **P3** Nepal film / music milestone card — new Nepali film release, song crossing 10M views, Nepali artist charting internationally. Diaspora uses to stay culturally connected

### F4 Government & Services Cards (official-looking, trustworthy)
- [x] **P1** Lok Sewa vacancy card — position, vacancies, deadline countdown, eligibility. `make_loksewa_card()` + `trigger_loksewa_card()` in gov_scanner.py. Blue/white institutional style. (2026-05-21)
- [x] **P2** Scholarship card — gold/prestige palette, name/funder/fields/deadline countdown. `make_scholarship_card()` + `trigger_scholarship_card()` in gov_scanner.py. (2026-05-21)
- [ ] **P2** NRB rate policy card — when NRB announces rate changes. Plain-language design with before/after comparison
- [x] **P2** NEPSE daily close card — index / change% / turnover / volume / transactions. `make_nepse_card()`, wired 15:30 NPT Mon–Fri. Full redesign (clean spacing, navy hero, 3-chip stats, 2× supersampled). (2026-05-21)
- [p] **P2** Gold & Silver rate card — redesigned: London/NY spot via gold-api.com → NPR via NRB rate × 1.112 duty factor. Editorial "tax premium" strip. `make_gold_card()`, wired 07:15 NPT daily. (2026-05-21)
- [-] **P2** ~~Kalimati vegetables price card~~ — REMOVED. `kalimatimarket.com.np` DNS dead. Function kept in gov_scanner.py but not scheduled. (2026-05-21)

### F5 Publishing Schedule (time-based architecture)
- [x] **P1** 07:00 NPT — 💰 NRB exchange rate card (`check_and_post_rate_card`), wired in main.py. (2026-05-21)
- [p] **P1** 07:15 NPT — 💛 Gold & Silver rate card (`check_and_post_gold_card`), wired in main.py. New source: gold-api.com. (2026-05-21)
- [-] ~~07:20 NPT — 🥦 Kalimati vegetable prices~~ — slot removed. DNS dead. (2026-05-21)
- [x] **P1** 08:00 NPT — 🌫️ AQI air quality card (`check_and_post_aqi_card`), wired in main.py. (2026-05-21)
- [x] **P1** 15:30 NPT Mon–Fri — 📈 NEPSE closing index card (`check_and_post_nepse_card`), wired in main.py. (2026-05-21)
- [x] **P1** Per-scan-cycle — 🔴 Earthquake M≥4.5 (`check_and_post_earthquake`), ⛽ Fuel price change (`check_and_post_fuel_card`), wired in main.py. (2026-05-21)
- [ ] **P2** 07:30 NPT "आजको नेपाल" digest card (after rate + AQI are posted)
- [ ] **P2** 12:00 NPT government/policy slot — Lok Sewa, passport, ministry announcements
- [ ] **P2** 18:00 NPT evening engagement slot — poll OR pride story OR culture/sports
- [ ] **P2** 21:00 NPT lighter content slot — film, music, history, Everest update
- [x] **P3** Breaking alerts interrupt schedule at any time with priority override (`is_breaking` flag, already live)

---

## Completed (Archive)

- [x] Continuous posting with diversity gates (source, region, velocity, gap)
- [x] 3 rotating post templates + hashtag pool of 5
- [x] Claude Haiku rewriter — 5-field bilingual output
- [x] Anti-spam formatter (removed all box-drawing unicode, footers, verified labels)
- [x] Startup grace + circuit breaker + velocity brake
- [x] Ntfy.sh push alerts for circuit trips and empty queue
- [x] Feed auto-disable after 5 consecutive failures
- [x] Per-source daily cap (max 8 posts/source/day)
- [x] Regional balance gate (nepal region capped at 70% of last 50 posts)
- [x] Recovery mode with auto-lift after 3 days
- [x] Duplicate story guard (24h, 50% title overlap)
- [x] Hindi leakage fix — prompt table + 28-pair code gate
- [x] Northeast India filter — nepal_explicit flag on Sentinel Assam + Morung Express
- [x] Manual posting via posts/ folder + mark_posted.py
- [x] DRY_RUN mode for testing without touching Facebook
