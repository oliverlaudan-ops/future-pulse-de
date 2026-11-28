#!/usr/bin/env python3
"""Fail-closed, persistent admission gate for NEO editorial cron runs.

This gate does not grant publishing permissions or perform GitHub operations.
A slot is claimed once, permanently; ambiguous crashes require human reconciliation.
"""
import argparse
import datetime as dt
import json
import os
import sqlite3
import sys
import uuid
from pathlib import Path
from zoneinfo import ZoneInfo

ZONE = ZoneInfo("Europe/Berlin")
WARNING_AFTER = dt.timedelta(minutes=90)
SCHEMA = """
CREATE TABLE IF NOT EXISTS editorial_runs (
 slot TEXT PRIMARY KEY,
 run_id TEXT NOT NULL UNIQUE,
 state TEXT NOT NULL CHECK(state IN ('claimed','pr_open','merged','deployed','blocked')),
 claimed_at TEXT NOT NULL,
 updated_at TEXT NOT NULL,
 pr_number INTEGER,
 commit_sha TEXT,
 note TEXT
);
"""
ALLOWED = {"claimed": {"pr_open", "blocked"}, "pr_open": {"merged", "blocked"},
           "merged": {"deployed", "blocked"}, "blocked": set(), "deployed": set()}


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def slot_for(moment):
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("timezone-aware admission timestamp required")
    local = moment.astimezone(ZONE)
    if local.weekday() not in (1, 4) or local.hour != 9:
        raise ValueError("outside authorized Tuesday/Friday [09:00:00,10:00:00) Europe/Berlin admission window")
    return local.date().isoformat()


def connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15, isolation_level=None)
    conn.execute("PRAGMA busy_timeout=15000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    conn.executescript(SCHEMA)
    return conn


def claim(conn, moment):
    slot = slot_for(moment)
    run_id = str(uuid.uuid4())
    timestamp = moment.isoformat()
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute("INSERT INTO editorial_runs(slot,run_id,state,claimed_at,updated_at) VALUES(?,?,?,?,?)",
                     (slot, run_id, "claimed", timestamp, timestamp))
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    return {"slot": slot, "run_id": run_id, "state": "claimed"}


def transition(conn, run_id, target, pr_number=None, commit_sha=None, note=None):
    if target not in ("pr_open", "merged", "deployed", "blocked"):
        raise ValueError("invalid state")
    conn.execute("BEGIN IMMEDIATE")
    try:
        row = conn.execute("SELECT state,slot FROM editorial_runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None or target not in ALLOWED[row[0]]:
            raise ValueError("unknown run or forbidden transition")
        if target in ("pr_open", "merged") and not (pr_number and commit_sha):
            raise ValueError("PR number and exact commit SHA required")
        if target == "deployed" and row[0] != "merged":
            raise ValueError("must be merged before deployment confirmation")
        conn.execute("""UPDATE editorial_runs SET state=?,updated_at=?,pr_number=COALESCE(?,pr_number),
                     commit_sha=COALESCE(?,commit_sha),note=? WHERE run_id=?""",
                     (target, now_utc().isoformat(), pr_number, commit_sha, note, run_id))
        conn.execute("COMMIT")
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    return {"run_id": run_id, "state": target}


def runtime_warnings(conn, run_id, moment):
    """Read-only advisory; never expires a claim or grants continuation authority."""
    row = conn.execute(
        "SELECT state,claimed_at FROM editorial_runs WHERE run_id=?", (run_id,)
    ).fetchone()
    if row is None:
        raise ValueError("run not found")
    elapsed = moment - dt.datetime.fromisoformat(row[1])
    if row[0] not in ("deployed", "blocked") and elapsed >= WARNING_AFTER:
        return [{"code": "editorial_runtime_90m", "blocking": False,
                 "elapsed_seconds": elapsed.total_seconds(),
                 "message": "Editorial run has reached 90 minutes; observe progress, "
                            "do not abort or release its reservation solely due to elapsed time."}]
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=os.environ.get("FUTURE_PULSE_RUN_DB", "/root/.openclaw/state/future-pulse-runs.sqlite"))
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("claim")
    status = sub.add_parser("status")
    status.add_argument("--run-id", required=True)
    step = sub.add_parser("transition")
    step.add_argument("--run-id", required=True)
    step.add_argument("--to", required=True, choices=["pr_open", "merged", "deployed", "blocked"])
    step.add_argument("--pr-number", type=int)
    step.add_argument("--commit-sha")
    step.add_argument("--note")
    args = parser.parse_args()
    try:
        with connect(args.db) as conn:
            if args.action == "claim":
                result = claim(conn, now_utc())
            elif args.action == "status":
                row = conn.execute("SELECT slot,run_id,state,claimed_at,updated_at,pr_number,commit_sha,note FROM editorial_runs WHERE run_id=?", (args.run_id,)).fetchone()
                if not row:
                    raise ValueError("run not found")
                result = dict(zip(("slot", "run_id", "state", "claimed_at", "updated_at", "pr_number", "commit_sha", "note"), row))
            else:
                result = transition(conn, args.run_id, args.to, args.pr_number, args.commit_sha, args.note)
            warnings = runtime_warnings(conn, result["run_id"], now_utc())
            result["warnings"] = warnings
            for warning in warnings:
                print(json.dumps(warning), file=sys.stderr)
        print(json.dumps(result))
    except (ValueError, sqlite3.Error) as exc:
        print(json.dumps({"allowed": False, "reason": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
