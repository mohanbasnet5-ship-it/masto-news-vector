#!/usr/bin/env python3
"""
NepalPulse daemon restart manager.

Runs 3 safety checks, shows all pending changes, restarts the daemon,
then promotes [p] → [x] in PROJECTS.md and archives PENDING_RESTART.md.

Usage:
    python3 restart.py           # interactive (checks + prompts)
    python3 restart.py --force   # skip time-of-day check (daemon crashed)
    python3 restart.py --check   # safety check only, no restart
"""

import subprocess, sqlite3, sys, re, os
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT    = Path(__file__).parent
DB      = ROOT / "nepalpulse" / "nepalpulse.db"
PROJ    = ROOT / "PROJECTS.md"
PEND    = ROOT / "PENDING_RESTART.md"
LOG_DIR = ROOT / "nepalpulse" / "logs"

NPT = timezone(timedelta(hours=5, minutes=45))
OFFPEAK_START = 23
OFFPEAK_END   = 6

RESTART_CMD = (
    "pkill -f 'python3 main.py' ; sleep 3 ; "
    "cd /Users/mohanbasnet/MASTO\\ NEWS\\ VECTOR/nepalpulse && "
    "nohup python3 main.py > logs/nepalpulse_run.log 2>&1 &"
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def hr(char="─", width=64):
    print(char * width)


def db_query(sql):
    if not DB.exists():
        return None
    try:
        con = sqlite3.connect(str(DB))
        row = con.execute(sql).fetchone()
        con.close()
        return row
    except Exception:
        return None


# ── Safety checks ─────────────────────────────────────────────────────────────

def check_gap():
    """Check minutes since last Facebook post. Must be ≥ 90."""
    row = db_query(
        "SELECT ROUND((julianday('now')-julianday(MAX(posted_fb_at)))*1440,1) "
        "FROM articles WHERE is_posted_fb=1;"
    )
    mins = row[0] if row and row[0] else None
    if mins is None:
        return True, "No posts found — safe to restart"
    ok = mins >= 90
    status = f"{mins:.0f} min since last post"
    note   = "✓ safe" if ok else f"✗ need ≥90 min (wait {90 - mins:.0f} more min)"
    return ok, f"{status}  {note}"


def check_time(force=False):
    """Check NPT time is off-peak (23:00–06:00). Skip if --force."""
    now_npt = datetime.now(NPT)
    h = now_npt.hour
    is_offpeak = h >= OFFPEAK_START or h < OFFPEAK_END
    time_str = now_npt.strftime("%H:%M NPT")
    if force:
        return True, f"{time_str}  (--force: peak-hour check bypassed)"
    ok = is_offpeak
    note = "✓ off-peak" if ok else f"✗ peak hours — use --force only if daemon is crashed"
    return ok, f"{time_str}  {note}"


def check_circuit():
    """Check no active Facebook circuit breaker block."""
    row = db_query(
        "SELECT tripped_at, cooldown_sec, resume_at_utc "
        "FROM fb_circuit_log ORDER BY id DESC LIMIT 1;"
    )
    if not row:
        return True, "No circuit trips on record  ✓"
    tripped_at, cooldown_sec, resume_at = row
    if resume_at:
        try:
            resume = datetime.fromisoformat(resume_at.replace("Z", "+00:00"))
            now_utc = datetime.now(timezone.utc)
            if resume > now_utc:
                mins_left = int((resume - now_utc).total_seconds() / 60)
                return False, f"✗ Circuit active — resumes in {mins_left} min ({resume_at})"
        except Exception:
            pass
    cooldown_h = (cooldown_sec or 0) // 3600
    return True, f"Last trip: {tripped_at}  cooldown {cooldown_h}h  (no active block)  ✓"


# ── Pending restart items ─────────────────────────────────────────────────────

def get_pending_items():
    """Return list of (number, title) for all pending items in PENDING_RESTART.md."""
    if not PEND.exists():
        return []
    items = []
    for line in PEND.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Safety checks"):
            break
        m = re.match(r"^## (\d+)\. (.+)$", line)
        if m:
            items.append((m.group(1), m.group(2)))
    return items


# ── Promote [p] → [x] in PROJECTS.md ─────────────────────────────────────────

def promote_pending():
    text = PROJ.read_text(encoding="utf-8")
    updated = text.replace("- [p] ", "- [x] ")
    PROJ.write_text(updated, encoding="utf-8")
    count = text.count("- [p] ")
    print(f"  PROJECTS.md: {count} items promoted [p] → [x]")


# ── Archive PENDING_RESTART.md ────────────────────────────────────────────────

def archive_pending():
    if not PEND.exists():
        return
    ts   = datetime.now(NPT).strftime("%Y-%m-%d %H:%M NPT")
    text = PEND.read_text(encoding="utf-8")

    # Extract the pending sections (between --- and the Archive section)
    archive_section = ""
    m = re.search(r"^---\n(.*?)\n---\n## Safety checks", text, re.DOTALL | re.MULTILINE)
    if m:
        archive_section = m.group(1).strip()

    new_text = (
        "# Pending Restart\n\n"
        "No changes pending restart. System is fully up to date.\n\n"
        "---\n\n"
        "## Archive\n\n"
        f"### Restarted {ts}\n\n"
        f"{archive_section}\n"
    )
    PEND.write_text(new_text, encoding="utf-8")
    print(f"  PENDING_RESTART.md: archived and cleared")


# ── Daemon PID ────────────────────────────────────────────────────────────────

def running_pid():
    try:
        r = subprocess.run(["ps", "-A"], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if "main.py" in line and "grep" not in line:
                return line.strip().split()[0]
    except Exception:
        pass
    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    force    = "--force" in sys.argv
    check_only = "--check" in sys.argv

    print()
    hr("═")
    print("  NepalPulse — Restart Manager")
    hr("═")
    print()

    # ── Show pending changes ──────────────────────────────────────────────────
    pending = get_pending_items()
    if pending:
        print(f"  ⏳  {len(pending)} changes pending restart:\n")
        for num, title in pending:
            print(f"     {num:>2}.  {title[:72]}")
        print()
        if PEND.exists():
            print(f"  Full details: PENDING_RESTART.md")
            print()
    else:
        print("  ✓  No pending changes — system is up to date.\n")
        if check_only:
            return

    # ── Safety checks ─────────────────────────────────────────────────────────
    hr()
    print("  Safety checks\n")

    g_ok,  g_msg  = check_gap()
    t_ok,  t_msg  = check_time(force)
    c_ok,  c_msg  = check_circuit()

    pid = running_pid()
    print(f"  Daemon:   {'Running  PID ' + pid if pid else '⚠️  NOT RUNNING'}")
    print(f"  Gap:      {g_msg}")
    print(f"  Time:     {t_msg}")
    print(f"  Circuit:  {c_msg}")
    print()

    all_ok = g_ok and t_ok and c_ok

    if check_only:
        hr()
        print(f"  {'✓  All checks passed — safe to restart.' if all_ok else '✗  Not safe to restart yet.'}")
        print()
        return

    if not all_ok:
        hr()
        print("  ✗  Restart blocked — fix the failing checks above.")
        if not t_ok and not force:
            print("     If the daemon has crashed and must restart now, use: python3 restart.py --force")
        print()
        sys.exit(1)

    # ── Confirm ───────────────────────────────────────────────────────────────
    hr()
    print("  All checks passed.\n")
    if pending:
        print(f"  After restart, {len(pending)} pending items will be marked live in PROJECTS.md.")
    print()
    try:
        ans = input("  Restart daemon now? [y/N]  ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n  Cancelled.")
        return

    if ans != "y":
        print("  Cancelled.")
        return

    # ── Restart ───────────────────────────────────────────────────────────────
    print()
    hr()
    print("  Restarting…\n")

    result = subprocess.run(RESTART_CMD, shell=True, capture_output=True, text=True)

    if result.returncode != 0 and result.stderr:
        print(f"  stderr: {result.stderr.strip()}")

    import time
    time.sleep(4)

    new_pid = running_pid()
    if new_pid:
        print(f"  ✓  Daemon running  PID {new_pid}")
    else:
        print("  ⚠️  Daemon not detected after restart — check logs:")
        print(f"      tail -f nepalpulse/logs/nepalpulse_run.log")
        print()
        sys.exit(1)

    # ── Post-restart updates ──────────────────────────────────────────────────
    print()
    hr()
    print("  Post-restart cleanup\n")
    promote_pending()
    archive_pending()

    print()
    print("  ✓  Done. All pending changes are now live.")
    print(f"  Tail log:  tail -f nepalpulse/logs/nepalpulse_run.log")
    print()
    hr("═")
    print()


if __name__ == "__main__":
    main()
