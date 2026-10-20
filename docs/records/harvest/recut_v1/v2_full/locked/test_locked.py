"""Contract tests and artifact verification for locked orchestration."""
import importlib.util
import os
from pathlib import Path
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('locked_test_runner', HERE / 'run_locked.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class LockedTests(unittest.TestCase):
    def test_priority_is_job_local(self):
        with patch.object(r.os, 'getpriority', return_value=5):
            self.assertEqual(r.priority(), 5)
            with self.assertRaises(RuntimeError):
                r.h.priority()  # Original T6h floor remains 15.
        with patch.object(r.os, 'getpriority', return_value=4):
            with self.assertRaises(RuntimeError):
                r.priority()
        self.assertEqual(r.WORKERS, 2)

    def test_custody_refuses_source_and_mirror_drift(self):
        with tempfile.TemporaryDirectory() as folder:
            source, target = Path(folder) / 'source', Path(folder) / 'copy'
            source.write_bytes(b'original')
            digest = r.h.sha(source)
            r.copy_bound(source, target, digest)
            target.write_bytes(b'drift')
            with self.assertRaises(AssertionError):
                r.copy_bound(source, target, digest)
            source.write_bytes(b'drift')
            with self.assertRaises(AssertionError):
                r.copy_bound(source, target, digest)

    def test_execute_never_exceeds_two_fresh_processes(self):
        active, peak, launched = 0, 0, 0
        mutex = threading.Lock()
        class Process:
            def __init__(self, *args, **kwargs):
                nonlocal active, peak, launched
                with mutex:
                    active += 1
                    launched += 1
                    peak = max(peak, active)
            def wait(self):
                nonlocal active
                time.sleep(.02)
                with mutex:
                    active -= 1
                return 0
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            (out / 'logs').mkdir()
            jobs = [(out, i, dict(wave='locked', page_id=str(i))) for i in range(8)]
            with patch.object(r.subprocess, 'Popen', Process), \
                 patch.object(r.h, 'completed', return_value=None), \
                 patch.object(r.h, 'rows', return_value=iter(())), \
                 patch.object(r.h, 'validate_records'), \
                 patch.object(r.h, 'write_rows'), \
                 patch.object(r, 'read', return_value=dict(source=folder, nice=5, worker_pid=123)):
                r.execute(jobs, SimpleNamespace(ensure=lambda: None, processes={}))
        self.assertEqual(launched, 8)
        self.assertEqual(peak, 2)
        self.assertEqual(active, 0)

    def test_population_equals_both_exclusion_files(self):
        self.assertEqual(len(r.population()), 600)

    def test_mock_five_byte_identity_and_fresh_pids(self):
        self.assertTrue(r.compare_mock()['ok'])
        out = HERE / 'mock-5'
        results = [r.read(out / 'work' / r.h.page_name(p) / 'result.json')
                   for p in r.read(out / 'selection.json')]
        self.assertEqual(len({v['worker_pid'] for v in results}), 5)
        self.assertTrue(all(v['nice'] >= 5 and not v['failed'] for v in results))

    def test_final_population_and_rehash(self):
        if not (HERE / 'summary.json').exists():
            self.skipTest('run not yet complete')
        summary = r.read(HERE / 'summary.json')
        records = list(r.h.rows(HERE / 'records.jsonl'))
        population = r.population()
        self.assertEqual({(v['stratum'], v['id']) for v in records},
                         {(v['stratum'], v['id']) for v in population})
        self.assertEqual(len(records), 600)
        for stratum, counts in summary['per_stratum'].items():
            selected = [v for v in records if v['stratum'] == stratum]
            for key, status in [('masked', 'masked'), ('guarded', 'guarded_original'),
                                ('unmatched', 'unmatched_original'), ('unresolved', 'unresolved')]:
                self.assertEqual(counts[key], sum(v['guard_status'] == status for v in selected))
        self.assertEqual(r.h.sha(HERE / 'records.jsonl'), summary['records_sha256'])
        for v in records:
            self.assertGreaterEqual(v['nice'], 5)
            self.assertFalse(v['training_release_allowed'])
            self.assertFalse(v['train_pool_eligible'])
            self.assertEqual(r.h.sha(v['original_path']), v['original_sha256'])
            if v.get('output_sha256'):
                self.assertEqual(v['output_path'], f"crops/{v['stratum']}/{v['id']}.png")
                self.assertEqual(r.h.sha(HERE / v['output_path']), v['output_sha256'])
            if v.get('worker_binding'):
                self.assertEqual(r.h.sha(v['worker_binding']), v['worker_binding_sha256'])
                binding = r.read(v['worker_binding'])
                harvest = Path(binding['source']) / 'docs/harvest'
                self.assertTrue(Path(v['worker_original_path']).resolve().is_relative_to(harvest))
                self.assertTrue(v['recut_pixels_equal'])
                custody = next(c for c in binding['custody'] if c['id'] == v['id'])
                self.assertEqual(custody['original_path'], v['original_path'])
                self.assertEqual(custody['original_sha256'], v['original_sha256'])
                self.assertEqual(custody['raster'], v['source_raster'])
                self.assertTrue(Path(custody['mirror_raster']).resolve().is_relative_to(harvest))

if __name__ == '__main__':
    unittest.main()
