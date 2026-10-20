"""Small orchestration/adapter contract tests; no page detector or bulk masking."""
import io
import contextlib
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import run


class Contracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.out = self.root / 'out'
        self.source.mkdir()
        self.out.mkdir()
        (self.out / 'pages').mkdir()
        self.line = dict(id='doc-p000001-l0001', split='train', crop='docs/harvest/parliament/crops/doc/p000001-l0001.png')
        original = self.source / self.line['crop']
        original.parent.mkdir(parents=True)
        original.write_bytes(b'original PNG bytes, including encoding details')
        self.line['crop_sha256'] = run.sha(original)
        self.page = dict(wave='parliament', doc='doc', page=1, page_id='doc-p000001', megapixels=21, lines=[self.line])

    def tearDown(self):
        self.temp.cleanup()

    def records(self, status='parliament_skipped'):
        records = run.originals(self.page, self.source, self.out, status, 'test page error' if status == 'failed_page' else None)
        run.write_rows(self.out / 'pages' / (run.page_name(self.page) + '.records.jsonl'), records)
        return records

    def test_population_counts_and_splits(self):
        data, _ = run.population()
        self.assertEqual(run.Counter(r['split'] for r in data), dict(train=214436, test=44029))
        parliament = [r for r in data if r['wave'] == 'parliament']
        self.assertEqual(len(parliament), 76463)
        self.assertNotIn('dev', {r['split'] for r in data})
        inventory = run.load('t6h_test_inventory', run.PHASE / 'phase0_inventory.py')
        self.assertEqual(len({inventory.key(r) for r in data}), 5585)
        self.assertEqual(len({inventory.key(r) for r in parliament}), 645)

    def test_memory_caps(self):
        self.assertTrue(run.can_launch([1, 2, 3], 20))
        self.assertFalse(run.can_launch([1, 2, 3, 4], 1))
        self.assertFalse(run.can_launch([1, 2, 3], 20.01))
        self.assertFalse(run.can_launch([21, 2, 3], 1))
        self.assertTrue(run.can_launch([21, 2], 1))
        self.assertFalse(run.can_launch([1, 2], 1, workers=2))

    def test_parliament_skip_copies_exact_bytes_and_provenance(self):
        record, = self.records()
        self.assertEqual(record['output_sha256'], self.line['crop_sha256'])
        self.assertEqual(record['skipped_wave'], 'parliament')
        self.assertEqual(record['guard_status'], 'parliament_skipped')
        self.assertTrue(record['host'])
        self.assertEqual(record['tree_sha'], run.TREE)
        self.assertEqual((self.out / record['output_path']).read_bytes(), (self.source / self.line['crop']).read_bytes())
        run.validate_records(self.page, [record], self.out, self.source)

    def test_parliament_page_worker_never_loads_adapter(self):
        (self.out / 'inputs').mkdir()
        (self.out / 'work').mkdir()
        run.write_json(self.out / 'inputs/00000.json', self.page)
        run.write_json(self.out / 'binding.json', dict(source=str(self.source)))
        with patch.object(run, 'priority', return_value=15), patch.object(run, 'load') as adapter:
            run.page_worker(self.out, 0)
            adapter.assert_not_called()
        attempt = self.out / 'work' / run.page_name(self.page)
        record, = run.rows(attempt / 'records.jsonl')
        run.validate_records(self.page, [record], attempt, self.source)
        self.assertEqual(record['guard_status'], 'parliament_skipped')

    def test_page_failure_is_explicit_and_keeps_original(self):
        record, = self.records('failed_page')
        self.assertEqual(record['guard_status'], 'failed_page')
        self.assertEqual(record['page_error'], 'test page error')
        self.assertEqual(record['output_sha256'], record['original_sha256'])
        self.assertIsNotNone(run.completed(self.page, self.out, self.source))

    def test_missing_original_is_recorded_not_silent(self):
        (self.source / self.line['crop']).unlink()
        record, = self.records('failed_page')
        self.assertIsNone(record['output_sha256'])
        self.assertIn('FileNotFoundError', record['page_error'])
        self.assertIsNone(run.completed(self.page, self.out, self.source))

    def test_resume_complete_page(self):
        records = self.records()
        self.assertEqual(run.completed(self.page, self.out, self.source), records)

    def test_prepare_writes_page_inputs_and_checks_resume_bindings(self):
        with patch.object(run, 'make_selection', return_value=([self.page], {})), patch.object(run, 'code_snapshot', return_value={}):
            self.assertEqual(run.prepare(self.out, self.source, False), [self.page])
            self.assertEqual(json.loads((self.out / 'inputs/00000.json').read_text()), self.page)
            self.assertEqual(run.prepare(self.out, self.source, False), [self.page])
            run.write_json(self.out / 'inputs/00000.json', dict(self.page, page=999))
            with self.assertRaisesRegex(RuntimeError, 'page input drift'):
                run.prepare(self.out, self.source, False)

    def test_resume_rejects_missing_or_duplicate_records(self):
        records = self.records()
        path = self.out / 'pages' / (run.page_name(self.page) + '.records.jsonl')
        for bad in ([], records + records):
            run.write_rows(path, bad)
            self.assertIsNone(run.completed(self.page, self.out, self.source))

    def test_resume_rehashes_output(self):
        record, = self.records()
        (self.out / record['output_path']).write_bytes(b'tampered')
        self.assertIsNone(run.completed(self.page, self.out, self.source))

    def test_resume_rehashes_original(self):
        self.records()
        (self.source / self.line['crop']).write_bytes(b'tampered')
        self.assertIsNone(run.completed(self.page, self.out, self.source))

    def test_parliament_cannot_be_reported_as_masked(self):
        record, = self.records()
        record['guard_status'] = 'masked'
        with self.assertRaisesRegex(ValueError, 'parliament was masked'):
            run.validate_records(self.page, [record], self.out, self.source)

    def test_count_summary(self):
        record, = self.records()
        counts = {}
        run.add_counts(counts, [record])
        self.assertEqual(counts['parliament']['train'], dict(total=1, changed=0, guarded=0,
                         unmatched=0, failed=0, parliament_skipped=1, masked=0))

    def test_resume_rebuilds_truncated_aggregate_without_worker(self):
        records = self.records()
        (self.out / 'records.jsonl').write_text('{truncated')
        with run.DiskWatchdog(self.out) as watchdog:
            with patch.object(run.subprocess, 'Popen') as process:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(run.schedule(self.out, self.source, [self.page], 4, watchdog), 0)
                process.assert_not_called()
        self.assertEqual(list(run.rows(self.out / 'records.jsonl')), records)
        summary = json.loads((self.out / 'summary.json').read_text())
        self.assertEqual(summary['pages_resumed'], 1)
        self.assertEqual(summary['state'], 'completed')

    def test_page_failure_records_then_continues(self):
        (self.out / 'logs').mkdir()
        (self.out / 'work').mkdir()
        line2 = dict(self.line, id='doc-p000002-l0001', crop=self.line['crop'].replace('p000001', 'p000002'))
        (self.source / line2['crop']).write_bytes((self.source / self.line['crop']).read_bytes())
        page2 = dict(self.page, page=2, page_id='doc-p000002', lines=[line2])
        attempt = self.out / 'work' / run.page_name(page2)
        attempt.mkdir()
        records = run.originals(page2, self.source, attempt, 'parliament_skipped')
        run.write_rows(attempt / 'records.jsonl', records)
        failed = types.SimpleNamespace(poll=lambda: 1, wait=lambda timeout: None)
        good = types.SimpleNamespace(poll=lambda: 0, wait=lambda timeout: None)
        with run.DiskWatchdog(self.out) as watchdog, patch.object(run.subprocess, 'Popen', side_effect=[failed, good]) as process:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run.schedule(self.out, self.source, [self.page, page2], 4, watchdog), 1)
            self.assertEqual(process.call_count, 2)
        records = list(run.rows(self.out / 'records.jsonl'))
        self.assertEqual([r['guard_status'] for r in records], ['failed_page', 'parliament_skipped'])
        self.assertIn('worker exit 1', records[0]['page_error'])
        self.assertEqual(json.loads((self.out / 'summary.json').read_text())['state'], 'completed_with_failures')

    def test_verifier_rehashes_original_output_and_rejects_extra_files(self):
        records = self.records()
        run.write_rows(self.out / 'records.jsonl', records)
        pages = [self.page]
        digest = hashlib.sha256(json.dumps(pages, sort_keys=True).encode()).hexdigest()
        run.write_json(self.out / 'selection.json', pages)
        run.write_json(self.out / 'binding.json', dict(source=str(self.source), mode='full', inputs={},
                       selection_sha256=digest, code={}, adapter_sha256=run.sha(run.PHASE / 'phase0_mask.py'),
                       runner_sha256=run.sha(run.__file__)))
        counts = {}
        run.add_counts(counts, records)
        run.write_json(self.out / 'summary.json', dict(pages_complete=1, per_wave_split=counts, state='completed'))
        verifier = run.load('t6h_test_verify', run.HERE / 'verify.py')
        with patch.object(run, 'make_selection', return_value=(pages, {})):
            result = verifier.verify(self.out)
            self.assertTrue(result['ok'])
            self.assertEqual(result['originals_hashed'], 1)
            extra = self.out / 'crops/extra.png'
            extra.write_bytes(b'extra')
            with self.assertRaisesRegex(ValueError, 'output file population'):
                verifier.verify(self.out)
            extra.unlink()
            output = self.out / records[0]['output_path']
            output.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'output bytes changed'):
                verifier.verify(self.out)
            output.write_bytes((self.source / self.line['crop']).read_bytes())
            (self.source / self.line['crop']).write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'original bytes changed'):
                verifier.verify(self.out)

    def test_disk_watchdog_stops_below_ten_gb(self):
        with patch.object(run.shutil, 'disk_usage', return_value=types.SimpleNamespace(free=run.FLOOR - 1)):
            watchdog = run.DiskWatchdog(self.out)
            with self.assertRaisesRegex(RuntimeError, 'disk_below_10_GB'):
                watchdog.ensure()

    def test_disk_floor_equality_is_allowed(self):
        with patch.object(run.shutil, 'disk_usage', return_value=types.SimpleNamespace(free=run.FLOOR)):
            self.assertFalse(run.DiskWatchdog(self.out).check())

    def test_snapshot_is_frozen_tree_and_detects_tampering(self):
        code = run.code_snapshot(self.out)
        self.assertEqual(code['greekocr/glyphs/foreign_ink.py'],
                         'f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5')
        (self.out / 'code/greekocr/glyphs/foreign_ink.py').write_text('tampered')
        with self.assertRaisesRegex(RuntimeError, 'snapshot drift'):
            run.code_snapshot(self.out)

    def test_priority_fails_closed(self):
        with patch.object(run.os, 'getpriority', return_value=5):
            with self.assertRaisesRegex(RuntimeError, 'launch blocked'):
                run.priority()
        with patch.object(run.os, 'getpriority', return_value=15):
            self.assertEqual(run.priority(), 15)

    def test_full_run_rejects_failed_mock(self):
        binding = dict(tree_sha=run.TREE, params_sha256=run.PARAM, source=str(self.source),
                       code={}, adapter_sha256='adapter', runner_sha256='runner')
        run.write_json(self.out / 'binding.json', binding)
        run.write_json(self.out / 'mock-comparison.json', dict(ok=False, identical=19))
        with self.assertRaisesRegex(RuntimeError, '50/50 Mac mock'):
            run.gate(self.out, binding)

    def test_path_cannot_escape_output(self):
        with self.assertRaises(ValueError):
            run.contained(self.out, '../other.png')

    def test_full_selection_admitted_binding(self):
        pages, _ = run.make_selection()
        self.assertEqual(sum(len(p['lines']) for p in pages), 258465)
        self.assertEqual(len(pages), 5585)
        for page in pages:
            self.assertTrue(all(r['crop_sha256'] and len(r['crop_bbox']) == 4 for r in page['lines']))
        # Collection v2 imports define splits; an older admitted split can differ.
        line, = [r for p in pages for r in p['lines'] if r['id'] == '4c207e1e-p000147-l0001']
        self.assertEqual((line['split'], line['admitted_split']), ('train', 'test'))

    def test_mock_selection_is_exact_original_50(self):
        pages, _ = run.make_selection(mock=True)
        expected = {r['id']: r for r in run.rows(run.RECEIPTS / 'mock_50.jsonl')}
        actual = {r['id']: r for p in pages for r in p['lines']}
        self.assertEqual(len(pages), 50)
        self.assertEqual(set(actual), set(expected))
        for key in actual:
            self.assertEqual(actual[key]['crop_sha256'], expected[key]['crop_sha256'])
            self.assertEqual(actual[key]['crop_bbox'], expected[key]['crop_bbox'])


class FrozenGuard(unittest.TestCase):
    """Execute the existing adapter closure with a stub mask and no detector."""
    def exercise(self, changed_count, unmatched=False):
        import numpy as np
        from PIL import Image
        adapter = run.load('t6h_guard_adapter', run.PHASE / 'phase0_mask.py')
        t6b = run.load('t6h_real_guard', run.HERE.parent / 'w1_masked/run.py')
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            (out / 'page-lines').mkdir()
            original = Image.fromarray(np.array([[127] * 10 + [128] * 10], dtype=np.uint8))
            original_path = out / 'original.png'
            original.save(original_path, compress_level=9)
            original_hash = run.sha(original_path)
            selection = dict(wave='testwave', doc='doc', page_id='doc-p000001', lines=[dict(id='line', split='test')])
            (out / 'selection.json').write_text(json.dumps([selection]))
            foreign = types.ModuleType('greekocr.glyphs.foreign_ink')

            def stub_mask(page, line, neighbours, box):
                arr = np.array(original)
                arr[0, :changed_count] = 255
                return types.SimpleNamespace(image=Image.fromarray(arr), mask=np.ones(arr.shape, dtype=bool),
                       record=dict(masked_pixel_count=changed_count, masked_component_count=1,
                                   changed=True, native_changed_pixels=changed_count))

            foreign.mask_foreign_ink = stub_mask
            captured = []

            def fake_worker(output, index):
                dest = output / 'crops/testwave/doc/original.png'
                dest.parent.mkdir(parents=True)
                if unmatched:
                    details = dict(masked_pixel_count=0, masked_component_count=0)
                    output_hash = original_hash
                else:
                    result = foreign.mask_foreign_ink(types.SimpleNamespace(image=original), None, [], (0, 0, 20, 1))
                    details = result.record
                    if result.record['changed']:
                        result.image.save(dest, compress_level=3)
                    else:
                        dest.write_bytes(original_path.read_bytes())
                    output_hash = run.sha(dest)
                captured.append(dict(details, id='line', original_path=str(original_path),
                                     masked_path='crops/testwave/doc/original.png',
                                     stored_crop_sha256=original_hash, masked_sha256=output_hash,
                                     match_status='unmatched' if unmatched else 'matched'))

            fake = types.SimpleNamespace(io_guard=lambda out: None, worker=fake_worker,
                       rows=lambda path: iter(captured), sha=run.sha,
                       write_rows=lambda path, values: run.write_rows(path, values))
            real_load = adapter.load
            adapter.load = lambda name, path: fake if name == 't6f_frozen_t6c2' else t6b
            # These modules only let the unchanged adapter import the stub mask.
            greekocr = types.ModuleType('greekocr')
            glyphs = types.ModuleType('greekocr.glyphs')
            greekocr.glyphs = glyphs
            glyphs.foreign_ink = foreign
            modules = {'greekocr': greekocr, 'greekocr.glyphs': glyphs, 'greekocr.glyphs.foreign_ink': foreign}
            old_path = list(sys.path)
            try:
                with patch.dict(sys.modules, modules), patch.object(sys, 'argv',
                     ['phase0_mask.py', '--code', str(run.ROOT), '--harvest', str(out), '--out', str(out), '--worker', '0']):
                    adapter.main()
            finally:
                sys.path[:] = old_path
                adapter.load = real_load
            record, = run.rows(out / 'page-lines/testwave--doc-p000001.guarded.jsonl')
            return record, original_hash, (out / record['masked_path']).read_bytes(), original_path.read_bytes()

    def test_exactly_thirty_percent_is_not_guarded(self):
        record, _, _, _ = self.exercise(3)
        self.assertEqual(record['original_dark_ink_pixels'], 10)  # 128 is excluded.
        self.assertEqual(record['own_ink_masked_fraction'], .30)
        self.assertFalse(record['wrong_line_risk'])
        self.assertEqual(record['guard_status'], 'masked')

    def test_strictly_above_thirty_restores_original_bytes(self):
        record, digest, output, original = self.exercise(4)
        self.assertTrue(record['wrong_line_risk'])
        self.assertEqual(record['own_ink_masked_fraction'], .40)
        self.assertEqual(record['guard_status'], 'guarded_original')
        self.assertEqual(record['output_sha256'], digest)
        self.assertEqual(output, original)
        self.assertEqual(record['masked_pixel_count'], 0)
        self.assertEqual(record['masked_component_count'], 0)

    def test_unmatched_restores_original_bytes(self):
        record, digest, output, original = self.exercise(0, unmatched=True)
        self.assertEqual(record['guard_status'], 'unmatched_original')
        self.assertEqual(record['output_sha256'], digest)
        self.assertEqual(output, original)


if __name__ == '__main__':
    unittest.main()
