#!/usr/bin/env python3
"""NepalPulse project status dashboard. Run: python3 pm.py"""
from pathlib import Path
import re, sys, subprocess, sqlite3

ROOT   = Path(__file__).parent
PROJ   = ROOT / "PROJECTS.md"
PEND   = ROOT / "PENDING_RESTART.md"
DB     = ROOT / "nepalpulse" / "nepalpulse.db"

# ── Parse PROJECTS.md ────────────────────────────────────────────────────────

def parse():
    text = PROJ.read_text(encoding="utf-8")
    tracks = {}
    current_track = None
    for line in text.splitlines():
        m = re.match(r"^## (Track [A-Z].+)$", line)
        if m:
            current_track = m.group(1)
            tracks[current_track] = {"live": [], "pending": [], "active": [], "todo": []}
            continue
        if line.startswith("## "):
            current_track = None
            continue
        if not current_track:
            continue
        if line.startswith("- [x]"):
            tracks[current_track]["live"].append(line[6:].strip())
        elif line.startswith("- [p]"):
            tracks[current_track]["pending"].append(line[6:].strip())
        elif line.startswith("- [~]"):
            tracks[current_track]["active"].append(line[6:].strip())
        elif line.startswith("- [ ]"):
            tracks[current_track]["todo"].append(line[6:].strip())
    return tracks


def priority_key(item):
    if "**P0**" in item: return 0
    if "**P1**" in item: return 1
    if "**P2**" in item: return 2
    return 3


def strip_priority(item):
    return re.sub(r"\*\*P\d\*\*\s*", "", item)


# ── Live system checks ────────────────────────────────────────────────────────

def daemon_status():
    try:
        r = subprocess.run(["ps", "-A"], capture_output=True, text=True)
        pids = [l for l in r.stdout.splitlines() if "main.py" in l and "grep" not in l]
        return pids[0].strip().split()[0] if pids else None
    except Exception:
        return None


def minutes_since_last_post():
    if not DB.exists():
        return None
    try:
        con = sqlite3.connect(str(DB))
        row = con.execute(
            "SELECT ROUND((julianday('now')-julianday(MAX(posted_fb_at)))*1440,1) "
            "FROM articles WHERE is_posted_fb=1;"
        ).fetchone()
        con.close()
        return row[0] if row else None
    except Exception:
        return None


def circuit_status():
    if not DB.exists():
        return None
    try:
        con = sqlite3.connect(str(DB))
        row = con.execute(
            "SELECT tripped_at, cooldown_sec FROM fb_circuit_log ORDER BY id DESC LIMIT 1;"
        ).fetchone()
        con.close()
        return row
    except Exception:
        return None


def queue_depth():
    if not DB.exists():
        return None
    try:
        con = sqlite3.connect(str(DB))
        row = con.execute(
            "SELECT COUNT(*) FROM articles "
            "WHERE is_verified=1 AND is_posted_fb=0 AND is_posting_blocked=0 "
            "AND is_breaking=0 AND source_region!='statement' "
            "AND (published_at IS NULL OR published_at >= datetime('now','-6 hours'));"
        ).fetchone()
        con.close()
        return row[0] if row else 0
    except Exception:
        return None


# ── Pending restart summary ───────────────────────────────────────────────────

def pending_restart_summary(tracks):
    items = []
    for track, data in tracks.items():
        for item in data["pending"]:
            items.append((track, item))
    return items


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not PROJ.exists():
        print("PROJECTS.md not found — run from MASTO NEWS VECTOR root.")
        sys.exit(1)

    tracks = parse()

    total_live    = sum(len(t["live"])    for t in tracks.values())
    total_pending = sum(len(t["pending"]) for t in tracks.values())
    total_active  = sum(len(t["active"])  for t in tracks.values())
    total_todo    = sum(len(t["todo"])    for t in tracks.values())
    total         = total_live + total_pending + total_active + total_todo

    pct     = int(100 * total_live / total) if total else 0
    bar_len = 36
    filled  = int(bar_len * total_live / total) if total else 0
    bar     = "█" * filled + "░" * (bar_len - filled)

    W = 64
    print()
    print("=" * W)
    print("  NepalPulse — Project Status")
    print("=" * W)
    print(f"  [{bar}] {pct}%  live")
    print(f"  {total_live} live · {total_pending} pending restart · {total_active} in progress · {total_todo} todo\n")

    # ── Live system checks ────────────────────────────────────────────────────
    pid      = daemon_status()
    mins     = minutes_since_last_post()
    circuit  = circuit_status()
    q        = queue_depth()

    print("🖥️   DAEMON")
    if pid:
        print(f"     Running  PID {pid}")
    else:
        print("     ⚠️  NOT RUNNING")
    if mins is not None:
        flag = "  ✓" if mins >= 90 else f"  ⚠️  (need ≥90 min for safe restart)"
        print(f"     Last post: {mins:.0f} min ago{flag}")
    if q is not None:
        print(f"     Queue: {q} articles ready to post")
    if circuit:
        print(f"     Circuit: last trip {circuit[0]}  cooldown {circuit[1]//3600}h")
    print()

    # ── Pending restart ───────────────────────────────────────────────────────
    pending_items = pending_restart_summary(tracks)
    if pending_items:
        print(f"⏳  PENDING RESTART  ({len(pending_items)} items — run: python3 restart.py)")
        for track, item in pending_items:
            label = track.split("—")[-1].strip() if "—" in track else track
            print(f"     [{label}]  {strip_priority(item)[:70]}")
        print()

    # ── In progress ───────────────────────────────────────────────────────────
    all_active = [(tr, it) for tr, data in tracks.items() for it in data["active"]]
    if all_active:
        print("🔄  IN PROGRESS")
        for track, item in all_active:
            print(f"     {strip_priority(item)}")
        print()

    # ── Next up ───────────────────────────────────────────────────────────────
    all_todo = [(priority_key(it), tr, it) for tr, data in tracks.items() for it in data["todo"]]
    all_todo.sort(key=lambda x: x[0])

    p0 = [(tr, it) for p, tr, it in all_todo if p == 0]
    p1 = [(tr, it) for p, tr, it in all_todo if p == 1]

    if p0:
        print("🔴  DO TODAY (P0)")
        for track, item in p0:
            print(f"     {strip_priority(item)}")
        print()

    if p1:
        print("🟡  THIS WEEK (P1)")
        for track, item in p1[:5]:
            print(f"     {strip_priority(item)}")
        if len(p1) > 5:
            print(f"     … and {len(p1)-5} more P1 items")
        print()

    # ── Track breakdown ───────────────────────────────────────────────────────
    print("📊  BY TRACK")
    for track, data in tracks.items():
        lv = len(data["live"])
        pn = len(data["pending"])
        ac = len(data["active"])
        total_t = lv + pn + ac + len(data["todo"])
        label = track.split("—")[-1].strip() if "—" in track else track
        parts = [f"{lv} live"]
        if pn: parts.append(f"{pn} pending")
        if ac: parts.append(f"{ac} active")
        print(f"     {label}: {' · '.join(parts)} / {total_t} total")

    print()
    print(f"  Edit PROJECTS.md to update.  Run python3 restart.py to restart safely.")
    print("=" * W)
    print()


if __name__ == "__main__":
    main()
