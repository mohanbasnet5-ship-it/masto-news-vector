# NepalPulse — Standard Operating Procedure

---

## 1. Daily health check (2 minutes)

Run this once a day, any time:

```bash
# Is the daemon running?
ps -A | grep "main.py" | grep -v grep

# Last post time + queue depth
sqlite3 nepalpulse/nepalpulse.db "
  SELECT posted_fb_at, title FROM articles WHERE is_posted_fb=1 ORDER BY posted_fb_at DESC LIMIT 1;
  SELECT COUNT(*) AS queue FROM articles
    WHERE is_verified=1 AND is_posted_fb=0 AND is_posting_blocked=0
    AND is_breaking=0 AND source_region!='statement'
    AND (published_at IS NULL OR published_at >= datetime('now','-12 hours'));
"

# Any active Facebook block?
sqlite3 nepalpulse/nepalpulse.db "
  SELECT tripped_at, cooldown_sec/3600.0 AS hours FROM fb_circuit_log ORDER BY id DESC LIMIT 3;
"

# Live log (last 20 lines)
tail -20 nepalpulse/logs/nepalpulse_$(date +%Y%m%d).log
```

**Healthy signs:**
- One `main.py` process in `ps` output
- Last post within the last 2 hours (peak hours) or 3 hours (off-peak)
- No recent entry in `fb_circuit_log`, or last entry is expired
- Log shows `Scan complete`, `Publishing to facebook`, no repeated errors

---

## 2. Restart rules

### ✅ Safe to restart
- Daemon has crashed (not in `ps` output)
- Off-peak hours: **11:00 PM – 6:00 AM NPT**

### ❌ Never restart
- During an active FB cooldown (`fb_circuit_log` shows unexpired trip)
- Within 2 hours of the last post during peak hours
- More than once in the same hour

### How to restart (always the same command)
```bash
pkill -f "python3 main.py" && sleep 3 && cd /Users/mohanbasnet/MASTO\ NEWS\ VECTOR/nepalpulse && nohup python3 main.py > logs/nepalpulse_run.log 2>&1 &
```
The system handles startup grace and circuit recovery automatically. No extra waiting needed.

---

## 3. Facebook spam block — what to do

### How to tell you're blocked
Log shows: `🔴 Facebook circuit OPEN (code 368 ...)`

### What to do: **nothing**
- The daemon keeps scanning and queuing articles
- The circuit reopens automatically when the cooldown expires
- Do NOT restart the daemon
- Do NOT try to post manually

### Cooldown durations (escalating)
| Block count in 24h | Cooldown |
|---|---|
| 1st block | 2 hours |
| 2nd block | 6 hours |
| 3rd block | 24 hours |

Each extra restart during a cooldown escalates to the next level. **Leaving it alone is always the right move.**

### Check when posting resumes
```bash
sqlite3 nepalpulse/nepalpulse.db "
  SELECT tripped_at, cooldown_sec/3600.0 AS cooldown_hours,
    datetime(tripped_at, '+' || cooldown_sec || ' seconds') AS resumes_at_utc
  FROM fb_circuit_log ORDER BY id DESC LIMIT 1;
"
```
Add 5h 45min to `resumes_at_utc` to get NPT time.

---

## 4. Deploying code changes

### Rule: only deploy during off-peak hours (11 PM – 6 AM NPT)

Steps:
1. Make and test changes in `nepalpulse/`
2. Syntax check:
   ```bash
   cd nepalpulse && python3 -m py_compile main.py config/settings.py database/db.py poster/poster.py formatter/formatter.py
   ```
3. Confirm no active FB block (check `fb_circuit_log`)
4. Restart using the standard command above
5. Watch first 3 minutes of log to confirm clean startup

---

## 5. When the daemon is not running

```bash
# Check it's actually stopped
ps -A | grep "main.py" | grep -v grep

# Check for stale PID file
ls nepalpulse/nepalpulse.pid

# Start fresh
cd /Users/mohanbasnet/MASTO\ NEWS\ VECTOR/nepalpulse && nohup python3 main.py > logs/nepalpulse_run.log 2>&1 &
```

---

## 6. Feature flags (in `nepalpulse/.env`)

| Flag | Current | Re-enable when |
|---|---|---|
| `ENABLE_STORY_IMAGES=1` | OFF | Account stable for 1 week with no blocks |
| `ENABLE_DIGESTS=1` | OFF | Account stable for 1 week with no blocks |
| `ENABLE_CARTOON=1` | OFF | Account stable for 1 week with no blocks |

To enable: open `.env`, change `0` to `1`, restart daemon (off-peak only).

---

## 7. What Claude Code should never do to this system

- Never restart the daemon mid-conversation without checking `fb_circuit_log` first
- Never change `FB_SPAM_COOLDOWN_ESCALATION_HOURS` or `POST_STARTUP_GRACE_MINUTES` without discussing
- Never add back spam markers: `━━━`, `automated`, `✅ Verified`, `🔗 Full story:`
- Never remove `restore_circuit_state()` from `main.py` startup
- Never set `MIN_POST_GAP_MINUTES` below 10

---

## 8. Quick reference

| What | Command |
|---|---|
| Is daemon running? | `ps -A \| grep "main.py" \| grep -v grep` |
| Live log | `tail -f nepalpulse/logs/nepalpulse_$(date +%Y%m%d).log` |
| Last post | `sqlite3 nepalpulse/nepalpulse.db "SELECT MAX(posted_fb_at) FROM articles;"` |
| Queue depth | `sqlite3 nepalpulse/nepalpulse.db "SELECT COUNT(*) FROM articles WHERE is_verified=1 AND is_posted_fb=0 AND is_posting_blocked=0 AND is_breaking=0 AND (published_at >= datetime('now','-12 hours'));"` |
| Block history | `sqlite3 nepalpulse/nepalpulse.db "SELECT tripped_at, cooldown_sec/3600.0 FROM fb_circuit_log ORDER BY id DESC LIMIT 5;"` |
| Safe restart | `pkill -f "python3 main.py" && sleep 3 && cd nepalpulse && nohup python3 main.py > logs/nepalpulse_run.log 2>&1 &` |
