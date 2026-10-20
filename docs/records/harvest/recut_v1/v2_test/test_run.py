"""Offline population, scheduling, matching and paired-analysis contract tests."""
import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import run
import harm


class PopulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records, cls.templates, cls.summary = run.population()

    def test_exact_1991_e3_exclusions(self):
        bad = {r["line_id"] for r in run.rows(list(run.PINS)[1]) if r["instrument"] == "v2_test"}
        self.assertEqual(len(bad), 1991)
        self.assertFalse(bad & {r["id"] for r in self.records})
        self.assertEqual(self.summary["raw_lines"], 44029)

    def test_before_parliament_counts(self):
        self.assertEqual(self.summary["before_parliament"], dict(lines=42038, pages=995))

    def test_parliament_excluded(self):
        self.assertEqual({r["wave"] for r in self.records}, set(run.WAVES))
        self.assertEqual(self.summary["excluded_parliament"], dict(lines=11936, pages=99))

    def test_final_counts_and_unique_pages(self):
        self.assertEqual(len(self.records), 30102)
        self.assertEqual(len({run.page_key(r) for r in self.records}), 896)
        self.assertEqual(len({r["id"] for r in self.records}), len(self.records))

    def test_wave_counts(self):
        self.assertEqual(self.summary["per_wave"], {w: dict(lines=n[0], pages=n[1]) for w, n in run.EXPECTED_WAVES.items()})

    def test_e3_projection_and_codec_are_bound(self):
        self.assertEqual(run.sha(run.OCR / "codec/v1.json"), run.PINS[run.OCR / "codec/v1.json"])
        self.assertTrue(all(self.templates[r["id"]]["split"] == "reserved" for r in self.records))

    def test_test_selection_is_two_pages_each_wave(self):
        pages, bindings = run.select_pages(self.records, 2)
        self.assertEqual(len(pages), 14)
        self.assertEqual({w: sum(p["wave"] == w for p in pages) for w in run.WAVES}, dict.fromkeys(run.WAVES, 2))
        self.assertIn(str(run.PAGE_INDEX), bindings)


class SchedulerTests(unittest.TestCase):
    def test_small_pages_cap_six(self):
        self.assertTrue(run.can_launch([20]*5, 20))
        self.assertFalse(run.can_launch([20]*6, 20))

    def test_large_pages_cap_three(self):
        self.assertTrue(run.can_launch([21, 21], 21))
        self.assertFalse(run.can_launch([21]*3, 21))

    def test_large_page_waits_for_small_workers(self):
        self.assertFalse(run.can_launch([1, 1, 1], 20.0001))
        self.assertTrue(run.can_launch([1, 1], 20.0001))

    def test_small_page_cannot_bypass_active_large_cap(self):
        self.assertFalse(run.can_launch([21, 1, 1], 1))

    def test_disk_floor_watchdog(self):
        with patch.object(run.shutil, "disk_usage", return_value=type("Disk", (), {"free": run.DISK_FLOOR-1})()):
            watchdog = run.Watchdog(run.HERE, 5)
            self.assertIn("disk_below_10_GB", watchdog.check())


class PolicyTests(unittest.TestCase):
    def test_default_output_outside_checkout(self):
        self.assertFalse(run.OUTPUT.is_relative_to(run.ROOT))
        self.assertEqual(run.OUTPUT, Path.home() / "Projects/collect-v3-data/v2_masked/v2_test")

    def test_checkout_requires_explicit_ignored_test_output(self):
        with self.assertRaises(ValueError):
            run.validate_output(run.HERE / "outputs", True)
        with self.assertRaises(ValueError):
            run.validate_output(run.TEST_OUTPUT, False)
        self.assertEqual(run.validate_output(run.TEST_OUTPUT / "unit", True), run.TEST_OUTPUT / "unit")

    def test_evaluation_inputs_cannot_be_outputs(self):
        for path in (run.HARVEST / "new", run.OCR / "out/new"):
            with self.assertRaises(ValueError):
                run.validate_output(path)

    def test_ambiguity_masks_nearest_and_unmatched_abstains(self):
        import numpy as np
        from greekocr.glyphs.recut import LineFit
        fit = lambda y: LineFit(0, 100, np.full(100, y), 10, 10, 10, 0, (0, 0, 100, 1))
        match, _ = run.pilot.matcher()
        box, fits = (0, 40, 100, 60), [fit(51), fit(49), fit(70)]
        candidates = run.pilot.candidate_diagnostics(box, fits)
        self.assertEqual(match(box, fits), 0)
        self.assertEqual(run.match_status(0, candidates), "ambiguous")
        self.assertEqual(len(candidates), 2)
        self.assertEqual(run.match_status(None, []), "unmatched")
        self.assertEqual(run.match_status(0, candidates[:1]), "matched")
        self.assertIn("zero-ambiguity rule retired", run.POLICY)

    def test_incomplete_receipt_refused(self):
        with patch.object(Path, "read_text", return_value=json.dumps(dict(schema="t6c2-mask-1", status="incomplete"))):
            with self.assertRaisesRegex(RuntimeError, "complete masking receipt"):
                harm.verify_mask_output(run.TEST_OUTPUT)

    def test_network_and_outside_writes_denied(self):
        with tempfile.TemporaryDirectory(dir=run.TEST_OUTPUT) as directory:
            code = """
import sys, socket
from pathlib import Path
import run
output = Path(sys.argv[1])
run.io_guard(output)
for action in (lambda: socket.getaddrinfo('localhost', 80),
               lambda: (output.parent / 'must-not-exist').open('w')):
    try:
        action()
    except PermissionError:
        pass
    else:
        raise RuntimeError('guard did not refuse forbidden action')
with (output / 'allowed').open('x') as stream:
    stream.write('ok')
"""
            result = subprocess.run([sys.executable, "-B", "-c", code, directory], cwd=run.HERE, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertEqual((Path(directory) / "allowed").read_text(), "ok")

    def test_generated_data_are_git_ignored(self):
        result = subprocess.run(["git", "check-ignore", str(run.TEST_OUTPUT / "final/lines.jsonl")],
                                cwd=run.ROOT, capture_output=True)
        self.assertEqual(result.returncode, 0)


class PairedTests(unittest.TestCase):
    def records(self):
        return [dict(id=str(i), wave=w, page=str(i//2), script_class="greek_poly", original_edits=2,
                     masked_edits=1, ref_len=10) for i, w in enumerate(["a"]*8 + ["b"]*4)]

    def test_stratified_exact_proportional_reproducible(self):
        a, quotas = harm.stratified_subset(self.records(), 6, 7)
        self.assertEqual(quotas, dict(a=4, b=2))
        self.assertEqual(len({r["id"] for r in a}), 6)
        self.assertEqual(a, harm.stratified_subset(list(reversed(self.records())), 6, 7)[0])

    def test_small_test_uses_all_lines(self):
        selected, _ = harm.stratified_subset(self.records(), 10000, 7)
        self.assertEqual(len(selected), 12)

    def test_sample_must_represent_all_waves(self):
        with self.assertRaises(ValueError):
            harm.stratified_subset(self.records(), 1, 7)

    def test_paired_delta_and_cluster_units(self):
        m = harm.metrics(self.records(), 100, 7)
        self.assertAlmostEqual(m["original_cer"], .2)
        self.assertAlmostEqual(m["masked_cer"], .1)
        self.assertAlmostEqual(m["delta_masked_minus_original"], -.1)
        self.assertEqual(m["line_bootstrap_95_ci"]["units"], 12)
        self.assertEqual(m["page_cluster_bootstrap_95_ci"]["units"], 6)
        for ci in ("line_bootstrap_95_ci", "page_cluster_bootstrap_95_ci"):
            for bound in m[ci]["delta_masked_minus_original"]:
                self.assertAlmostEqual(bound, -.1)

    def test_identical_arms_have_zero_paired_interval(self):
        records = [dict(r, masked_edits=r["original_edits"]) for r in self.records()]
        m = harm.metrics(records, 100, 7)
        self.assertEqual(m["line_bootstrap_95_ci"]["delta_masked_minus_original"], [0, 0])
        self.assertEqual(m["page_cluster_bootstrap_95_ci"]["delta_masked_minus_original"], [0, 0])

    def test_page_units_include_wave(self):
        a = self.records()[0]
        b = dict(a, id="other", wave="b")
        self.assertEqual(harm.bootstrap([a, b], "page", 100, 7)["units"], 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    run.low_priority()
    sys.path.insert(0, str(run.ROOT))
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    if args.receipt:
        path = run.validate_output(args.receipt, test=True)
        run.write_json(path, dict(passed=result.wasSuccessful(), tests=result.testsRun,
                       sources={name: run.sha(run.HERE / name) for name in ("run.py", "harm.py", "test_run.py")}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
