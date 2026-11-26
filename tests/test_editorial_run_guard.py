import datetime as dt
import importlib.util
import sqlite3
import tempfile
import threading
import unittest
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
        for stamp in ("2026-11-26T08:00:00+00:00", "2026-11-27T08:06:00+00:00", "2027-03-30T08:00:00+00:00"):
            with self.assertRaises(ValueError):
                guard.slot_for(dt.datetime.fromisoformat(stamp))

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
