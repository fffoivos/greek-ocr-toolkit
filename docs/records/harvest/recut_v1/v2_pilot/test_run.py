"""Read-only checks for pilot matching diagnostics and stop/containment gates.

No detector jobs, crops, fixtures, receipts or cache files are written.
  nice -n 15 .venv/bin/python -B docs/harvest/recut_v1/v2_pilot/test_run.py
"""
import sys
sys.dont_write_bytecode = True

import signal
import os
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import run


class MatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        from greekocr.glyphs.recut import LineFit
        cls.match, cls.fit = map(staticmethod, run.matcher())
        cls.np = np
        cls.LineFit = LineFit

    def line(self, centre, x0=0, x1=100):
        return self.LineFit(x0, x1, self.np.full(x1-x0, centre), 10, 10, 10, 0, (x0, 0, x1, 1))

    def test_diagnostic_ranking_matches_exact_original(self):
        box = (0, 40, 100, 60)
        fits = [self.line(70), self.line(53), self.line(48), self.line(50, 0, 49)]
        candidates = run.candidate_diagnostics(box, fits)
        self.assertEqual([r["index"] for r in candidates], [2, 1])
        self.assertEqual(self.match(box, fits), candidates[0]["index"])
        self.assertIn("ambiguous", run.line_failures(2, candidates, "a", "a", "a", True))

    def test_original_eligibility_boundaries_are_inclusive(self):
        box = (0, 40, 100, 60)
        fits = [self.line(65, 0, 50), self.line(65.001), self.line(50, 0, 49)]
        self.assertEqual(self.match(box, fits), 0)
        self.assertEqual([r["index"] for r in run.candidate_diagnostics(box, fits)], [0])

    def test_tie_preserves_original_winner_but_stops(self):
        fits = [self.line(50), self.line(50)]
        candidates = run.candidate_diagnostics((0, 40, 100, 60), fits)
        self.assertEqual(self.match((0, 40, 100, 60), fits), 0)
        self.assertEqual(run.line_failures(0, candidates, "a", "a", "a", True), ["ambiguous"])

    def test_unmatched_and_custody_failures_are_retained_together(self):
        self.assertEqual(run.line_failures(None, [], "b", "c", "a", False),
                         ["unmatched", "recut_sha_mismatch", "stored_crop_mismatch"])

    def test_unique_custody_checked_match_has_no_failure(self):
        self.assertEqual(run.line_failures(0, [dict(index=0)], "a", "a", "a", True), [])


class StopTests(unittest.TestCase):
    def result(self, **kw):
        return dict(wave="parliament", page_id="p", match_failures=0,
                    page_seconds=60, worker_wall_seconds=60) | kw

    def test_sixty_seconds_is_allowed(self):
        self.assertIsNone(run.page_stop_reason(self.result()))

    def test_parliament_page_or_full_worker_time_stops(self):
        for field in ("page_seconds", "worker_wall_seconds"):
            self.assertIn("over_60", run.page_stop_reason(self.result(**{field: 60.001})))

    def test_vouli_has_no_time_stop(self):
        self.assertIsNone(run.page_stop_reason(self.result(wave="vouli", page_seconds=90, worker_wall_seconds=95)))

    def test_any_matching_failure_stops_either_wave(self):
        for wave in run.WAVES:
            self.assertIn("matching_failure", run.page_stop_reason(self.result(wave=wave, match_failures=1)))

    def test_simultaneous_stop_rules_are_both_recorded(self):
        reason = run.page_stop_reason(self.result(match_failures=1, page_seconds=61))
        self.assertIn("matching_failure", reason)
        self.assertIn("over_60", reason)

    def test_priority_failure_precedes_any_io_guard_or_worker(self):
        with patch.object(sys, "argv", ["run.py", "--worker", "0"]), \
                patch.object(run.os, "getpriority", return_value=0), \
                patch.object(run, "install_io_guard") as guard, patch.object(run, "worker") as worker:
            with self.assertRaisesRegex(RuntimeError, "no processing started"):
                run.main()
            guard.assert_not_called()
            worker.assert_not_called()


class WatchdogTests(unittest.TestCase):
    def test_disk_floor_uses_available_bytes_and_strict_less_than(self):
        with patch.object(run.shutil, "disk_usage", return_value=SimpleNamespace(free=run.DISK_FLOOR)):
            watchdog = run.Watchdog()
            self.assertIsNone(watchdog.check())
        with patch.object(run.shutil, "disk_usage", return_value=SimpleNamespace(free=run.DISK_FLOOR-1)):
            self.assertIn("disk_below", watchdog.check())

    def test_watchdog_terminates_only_owned_worker_group(self):
        watchdog = run.Watchdog()
        worker = Mock(pid=123)
        worker.poll.return_value = None
        watchdog.process = worker
        with patch.object(watchdog, "check", return_value="disk_below"), patch.object(run.os, "killpg") as kill:
            watchdog.watch()
        kill.assert_called_once_with(123, signal.SIGTERM)
        worker.wait.assert_called_once_with(timeout=2)

    def test_stuck_worker_is_killed_after_term(self):
        watchdog = run.Watchdog()
        worker = Mock(pid=123)
        worker.poll.return_value = None
        worker.wait.side_effect = [subprocess.TimeoutExpired("worker", 2), 0]
        watchdog.process = worker
        with patch.object(watchdog, "check", return_value="disk_below"), patch.object(run.os, "killpg") as kill:
            watchdog.watch()
        self.assertEqual([call.args for call in kill.call_args_list], [(123, signal.SIGTERM), (123, signal.SIGKILL)])


class ContainmentTests(unittest.TestCase):
    def audit_hook(self):
        with patch.object(run.sys, "addaudithook") as register:
            run.install_io_guard()
        return register.call_args.args[0]

    def test_write_guard_accepts_only_pilot_and_exact_report_copy(self):
        hook = self.audit_hook()
        for path in (run.OUTPUT / "crops/example.png", run.HERE / "PILOT.md"):
            hook("open", (str(path), "w", os.O_WRONLY | os.O_CREAT))
        for path in (run.OUTPUT.parent / "outside.json", run.OUTPUT.parent.parent / "run/state.json",
                     run.HERE / "not-the-report.json", run.INPUT / "unwanted.json"):
            with self.assertRaises(PermissionError):
                hook("open", (str(path), "w", os.O_WRONLY | os.O_CREAT))

    def test_network_is_denied_but_input_reads_are_allowed(self):
        hook = self.audit_hook()
        hook("open", (str(run.PARAMS), "r", os.O_RDONLY))
        for event in ("socket.connect", "socket.getaddrinfo", "socket.bind"):
            with self.assertRaisesRegex(PermissionError, "network OFF"):
                hook(event, ())


if __name__ == "__main__":
    run.low_priority()
    sys.path.insert(0, str(run.ROOT))
    unittest.main()
