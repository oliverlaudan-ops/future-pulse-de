import datetime as dt
import contextlib
import io
import json
import importlib.util
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path

spec = importlib.util.spec_from_file_location("editorial_run_guard", Path(__file__).resolve().parents[1] / "scripts/editorial_run_guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
UTC = dt.timezone.utc


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "runs.sqlite"

    def tearDown(self):
        self.temp.cleanup()

    def test_schedule_and_dst(self):
        for stamp in ("2026-11-27T08:00:00+00:00", "2027-03-30T07:00:00+00:00"):
            moment = dt.datetime.fromisoformat(stamp)
            self.assertTrue(guard.slot_for(moment))
        for stamp in ("2026-11-26T08:00:00+00:00", "2027-03-30T08:00:00+00:00"):
            with self.assertRaises(ValueError):
                guard.slot_for(dt.datetime.fromisoformat(stamp))

    def test_exact_admission_boundaries_winter_and_summer(self):
        for date, offset in (("2026-11-27", "+01:00"), ("2027-03-30", "+02:00")):
            for time in ("09:00:00", "09:05:00.000001", "09:59:59.999999"):
                with self.subTest(date=date, time=time):
                    self.assertEqual(guard.slot_for(dt.datetime.fromisoformat(
                        f"{date}T{time}{offset}")), date)
            for time in ("08:59:59.999999", "10:00:00", "10:00:00.000001", "15:00:00"):
                with self.subTest(date=date, time=time), self.assertRaises(ValueError):
                    guard.slot_for(dt.datetime.fromisoformat(f"{date}T{time}{offset}"))
        with self.assertRaises(ValueError):
            guard.slot_for(dt.datetime(2026, 11, 27, 9))

    def test_warning_boundaries_are_read_only_and_nonblocking(self):
        start = dt.datetime.fromisoformat("2026-11-27T08:00:00+00:00")
        with guard.connect(self.db) as conn:
            run_id = guard.claim(conn, start)["run_id"]
            before = conn.execute("SELECT * FROM editorial_runs").fetchall()
            self.assertEqual(guard.runtime_warnings(conn, run_id,
                             start + dt.timedelta(minutes=90, microseconds=-1)), [])
            for elapsed in (dt.timedelta(minutes=90), dt.timedelta(days=7)):
                warnings = guard.runtime_warnings(conn, run_id, start + elapsed)
                self.assertEqual(warnings[0]["code"], "editorial_runtime_90m")
                self.assertIs(warnings[0]["blocking"], False)
            self.assertEqual(conn.execute("SELECT * FROM editorial_runs").fetchall(), before)
            with self.assertRaises(sqlite3.IntegrityError):
                guard.claim(conn, start + dt.timedelta(minutes=59))
            # No re-admission/time-window check for the existing run, even days later.
            with patch.object(guard, "now_utc", return_value=start + dt.timedelta(days=7)):
                guard.transition(conn, run_id, "pr_open", 1, "abc")
                guard.transition(conn, run_id, "merged", 1, "abc")
                guard.transition(conn, run_id, "deployed")
            self.assertEqual(guard.runtime_warnings(conn, run_id,
                             start + dt.timedelta(days=7)), [])

    def test_cli_warning_is_emitted_with_success_exit(self):
        start = dt.datetime.fromisoformat("2026-11-27T08:00:00+00:00")
        with guard.connect(self.db) as conn:
            run_id = guard.claim(conn, start)["run_id"]
        for action in (["status"], ["transition", "--to", "pr_open",
                                     "--pr-number", "1", "--commit-sha", "abc"]):
            output, errors = io.StringIO(), io.StringIO()
            args = ["guard", "--db", str(self.db), *action, "--run-id", run_id]
            with patch("sys.argv", args), patch.object(guard, "now_utc",
                    return_value=start + dt.timedelta(minutes=90)), \
                    contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                self.assertEqual(guard.main(), 0)
            self.assertIs(json.loads(output.getvalue())["warnings"][0]["blocking"], False)
            self.assertEqual(json.loads(errors.getvalue())["code"], "editorial_runtime_90m")

    def test_no_claim_outside_window_even_after_previous_run(self):
        start = dt.datetime.fromisoformat("2026-11-27T08:59:59.999999+00:00")
        with guard.connect(self.db) as conn:
            run_id = guard.claim(conn, start)["run_id"]
            with self.assertRaises(ValueError):
                guard.claim(conn, start + dt.timedelta(microseconds=1))
            guard.transition(conn, run_id, "blocked", note="requires human reconciliation")
            with self.assertRaises(sqlite3.IntegrityError):
                guard.claim(conn, start)
            with self.assertRaises(ValueError):
                guard.transition(conn, run_id, "pr_open", 1, "abc")

    def test_duplicate_and_restart(self):
        moment = dt.datetime.fromisoformat("2026-11-27T08:00:00+00:00")
        with guard.connect(self.db) as conn:
            run = guard.claim(conn, moment)
        with guard.connect(self.db) as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                guard.claim(conn, moment)
            self.assertEqual(conn.execute("SELECT state FROM editorial_runs WHERE run_id=?", (run["run_id"],)).fetchone()[0], "claimed")

    def test_parallel_claim_only_one_wins(self):
        moment = dt.datetime.fromisoformat("2026-11-27T08:00:00+00:00")
        results = []
        barrier = threading.Barrier(6)
        def worker():
            with guard.connect(self.db) as conn:
                barrier.wait()
                try:
                    guard.claim(conn, moment)
                    results.append("ok")
                except sqlite3.IntegrityError:
                    results.append("duplicate")
        threads = [threading.Thread(target=worker) for _ in range(6)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(results.count("ok"), 1)
        self.assertEqual(results.count("duplicate"), 5)

    def test_no_double_merge_or_republish(self):
        moment = dt.datetime.fromisoformat("2026-11-27T08:00:00+00:00")
        with guard.connect(self.db) as conn:
            run_id = guard.claim(conn, moment)["run_id"]
            with self.assertRaises(ValueError):
                guard.transition(conn, run_id, "merged", 1, "abc")
            guard.transition(conn, run_id, "pr_open", 1, "abc")
            guard.transition(conn, run_id, "merged", 1, "abc")
            with self.assertRaises(ValueError):
                guard.transition(conn, run_id, "merged", 1, "abc")
            guard.transition(conn, run_id, "deployed")
            with self.assertRaises(ValueError):
                guard.transition(conn, run_id, "deployed")


if __name__ == "__main__":
    unittest.main()
