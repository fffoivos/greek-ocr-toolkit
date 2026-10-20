"""Offline CROPS3 checks. No test generates crops beyond the 2,000-row pilot."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import stage_crops as st
from stage_crops import W2_PARENT

BASE = Path(__file__).resolve().parent


class AdmissionAdapter(unittest.TestCase):
    def row(self, **kw):
        return dict(id='same-id', parent_id=W2_PARENT, source='source', **kw)

    def test_canonical_id_and_parent_selection(self):
        rows, fmt = st.adapt_admission([self.row(), dict(id='same-id', parent_id='collect-v3-W1-other')])
        self.assertEqual(fmt, 'census')
        self.assertEqual([(r['parent_id'], r['row_id']) for r in rows], [(W2_PARENT, 'same-id')])

    def test_census_final_decision_overrides_raw_collector_flag(self):
        rows, _ = st.adapt_admission([self.row(admitted=False, decision={'disposition': 'ADMIT'})])
        self.assertEqual(len(rows), 1)

    def test_requested_output_sibling_of_readonly_roots(self):
        st.guard_output(Path.home() / 'Projects/collect-v3-data/w2_originals_v3',
                        Path.home() / 'Projects/collect-v3-data/snapshots/W2_features.jsonl')

    def test_row_id_alias(self):
        rows, _ = st.adapt_admission([dict(row_id='r1', parent_id=W2_PARENT)])
        self.assertEqual(rows[0]['row_id'], 'r1')

    def test_legacy_preserved(self):
        old = dict(row_id='r1', source='source', application_manifest_sha256='abc')
        self.assertEqual(st.adapt_admission([old]), ([old], 'legacy'))

    def test_zero_w2_refused(self):
        with self.assertRaisesRegex(ValueError, 'zero W2'):
            st.adapt_admission([dict(id='r1', parent_id='collect-v3-W1-other')])

    def test_empty_refused(self):
        with self.assertRaises(ValueError):
            st.adapt_admission([])

    def test_mixed_format_refused(self):
        with self.assertRaisesRegex(ValueError, 'mixed'):
            st.adapt_admission([self.row(), dict(row_id='legacy')])

    def test_conflicting_ids_refused(self):
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            st.adapt_admission([self.row(row_id='other')])

    def test_non_admit_refused(self):
        with self.assertRaisesRegex(ValueError, 'non-ADMIT'):
            st.adapt_admission([self.row(decision={'disposition': 'REJECT'})])

    def test_non_train_refused(self):
        with self.assertRaises(ValueError):
            st.adapt_admission([self.row(split='test')])

    def test_false_pass_refused(self):
        with self.assertRaises(ValueError):
            st.adapt_admission([dict(row_id='r', **{'pass': False})])

    def test_readonly_roots_and_metadata_guard(self):
        for protected in st.READ_ONLY:
            with self.assertRaisesRegex(ValueError, 'read-only'):
                st.guard_output(protected / 'crops', Path('/private/tmp/inputs/features.jsonl'))
        with self.assertRaises(ValueError):
            st.guard_output(Path('/private/tmp/input/crops'), Path('/private/tmp/input/features.jsonl'))

    def test_disk_floor_without_regeneration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inputs = root / 'input'
            inputs.mkdir()
            row = dict(id='r1', source='test', crop_bbox=[0, 0, 10, 10], crop_sha256='0'*64,
                       tranche='W2', crop_source_image='/must-not-read', crop_source_sha256='0'*64)
            features = inputs / 'W2_features.jsonl'
            features.write_text(json.dumps(row)+'\n')
            admitted = root / 'admitted.jsonl'
            admitted.write_text(json.dumps(dict(row, parent_id=W2_PARENT))+'\n')
            with contextlib.redirect_stdout(io.StringIO()):
                receipt = st.stage(admitted, features, root / 'output/crops', minimum_free_gb=10**9)
            self.assertEqual(receipt['disk_deferred'], 1)
            self.assertEqual(receipt['new_count'], 0)
            self.assertEqual(list((root / 'output').rglob('*.png')), [])

    def test_duplicate_admission_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'input').mkdir()
            a = root / 'admitted.jsonl'
            a.write_text((json.dumps(self.row())+'\n')*2)
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                st.stage(a, root / 'input/features.jsonl', root / 'out/crops')

    def existing_fixture(self, waves, *, corrupt=False):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        inputs = root / 'inputs'
        inputs.mkdir()
        source = inputs / 'page.dat'
        source.write_bytes(b'retained source fixture, no crop generation')
        out = root / 'output/crops'
        rows = []
        for index, wave in enumerate(waves):
            key = 'r' + str(index)
            path = out / 'test' / (key + '.png')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'existing opaque crop fixture')
            rows.append(dict(id=key, source='test', crop_bbox=[0, 0, 10, 10], crop_sha256=st.sha(path),
                             tranche=wave, crop_source_image=str(source), crop_source_sha256=st.sha(source)))
        if corrupt:
            path.write_bytes(b'corrupt')
        features = inputs / ('W2_features.jsonl' if 'W2' in waves else 'W1_features.jsonl')
        features.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        admitted = root / 'admitted.jsonl'
        admitted.write_text(''.join(json.dumps(dict(r, row_id=r['id']))+'\n' for r in rows))
        return root, admitted, features, out

    def test_legacy_w1_still_works(self):
        root, a, f, out = self.existing_fixture(['W1'])
        with contextlib.redirect_stdout(io.StringIO()):
            r = st.stage(a, f, out)
        self.assertEqual(r['count'], 1)
        self.assertEqual(r['new_count'], 0)

    def test_legacy_mixed_selects_w2(self):
        root, a, f, out = self.existing_fixture(['W1', 'W2'])
        with contextlib.redirect_stdout(io.StringIO()):
            r = st.stage(a, f, out)
        rows = [json.loads(s) for s in (out.parent/'crops_manifest.jsonl').read_text().splitlines()]
        self.assertEqual(r['admitted_count'], 1)
        self.assertEqual([(r['parent_id'], r['row_id']) for r in rows], [(W2_PARENT, 'r1')])

    def test_zero_w2_legacy_refused(self):
        root, a, f, out = self.existing_fixture(['W1'])
        renamed = f.with_name('W2_features.jsonl')
        f.rename(renamed)
        with self.assertRaisesRegex(ValueError, 'zero W2'):
            st.stage(a, renamed, out)

    def test_mismatch_records_failure_without_manifest_publication(self):
        root, a, f, out = self.existing_fixture(['W2'], corrupt=True)
        with contextlib.redirect_stdout(io.StringIO()):
            r = st.stage(a, f, out)
        self.assertEqual(r['failures'], 1)
        self.assertFalse((out.parent/'crops_manifest.jsonl').exists())
        self.assertIn('hash mismatch', (out.parent/'crops_failures.jsonl').read_text())


class UploadMock(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tree = self.root / 'crops'
        p = self.tree / 'source/r1.png'
        p.parent.mkdir(parents=True)
        p.write_bytes(b'opaque test bytes; not a regenerated crop')
        self.row = dict(row_id='r1', parent_id=W2_PARENT, source='source', admitted=True,
                        path='crops/source/r1.png', sha256=st.sha(p), bytes=p.stat().st_size)
        self.manifest = self.root / 'crops_manifest.jsonl'
        self.manifest.write_text(json.dumps(self.row)+'\n')

    def invoke(self, corrupt=False):
        env = dict(os.environ, CROPS3_MOCK_REMOTE=str(self.root / 'remote'))
        env.pop('CROPS3_MOCK_CORRUPT', None)
        if corrupt:
            env['CROPS3_MOCK_CORRUPT'] = 'source/r1.png'
        result = subprocess.run([str(BASE / 'upload_crops.sh'), str(self.tree), str(self.manifest)],
                                env=env, capture_output=True, text=True)
        receipt = json.loads((self.root / 'upload_receipt.json').read_text())
        return result, receipt

    def test_good_tree(self):
        result, r = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr+result.stdout)
        self.assertEqual(r['mismatches'], 0)
        self.assertEqual(r['status'], 'verified')
        self.assertEqual(r['file_count'], 1)
        self.assertEqual(r['bytes'], self.row['bytes'])
        self.assertEqual((self.root/'remote/source/r1.png').read_bytes(), (self.tree/'source/r1.png').read_bytes())

    def test_corrupt_remote_fails(self):
        result, r = self.invoke(corrupt=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertGreater(r['mismatches'], 0)
        self.assertEqual(r['status'], 'failed')

    def test_corrupt_local_refused_before_copy(self):
        (self.tree / 'source/r1.png').write_bytes(b'corrupt')
        result, r = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertGreater(r['mismatches'], 0)
        self.assertFalse((self.root/'remote').exists())

    def test_failure_row_refused_before_copy(self):
        self.manifest.write_text(json.dumps(dict(self.row, failure=True))+'\n')
        result, r = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'remote').exists())

    def test_failure_sidecar_refused(self):
        (self.root/'crops_failures.jsonl').write_text('{"row_id":"bad"}\n')
        result, r = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'remote').exists())

    def test_disk_deferred_receipt_refused(self):
        (self.root/'crops_receipt.json').write_text(json.dumps(dict(output_root=str(self.tree), disk_deferred=1)))
        result, r = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'remote').exists())

    def test_path_escape_refused(self):
        self.manifest.write_text(json.dumps(dict(self.row, path='../outside.png'))+'\n')
        result, _ = self.invoke()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root/'remote').exists())


class Measurement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.estimate = json.loads((BASE/'CROPS3_ESTIMATE.json').read_text())
        cls.out = Path(cls.estimate['output_root'])

    def test_2000_byte_exact(self):
        rows = [json.loads(s) for s in (self.out.parent/'crops_manifest.jsonl').read_text().splitlines()]
        selected = {r['row_id']: r for r in map(json.loads, (self.out.parent/'estimate_selection.jsonl').read_text().splitlines())}
        self.assertEqual(len(rows), 2000)
        for row in rows:
            self.assertEqual(st.sha(self.out.parent/row['path']), selected[row['row_id']]['crop_sha256'])

    def test_idempotent_rerun_receipt(self):
        self.assertTrue(self.estimate['idempotent_rerun'])
        receipt = json.loads((self.out.parent/'crops_receipt.json').read_text())
        self.assertEqual(receipt['new_count'], 0)

    def test_live_run_unchanged(self):
        self.assertTrue(self.estimate['live_run_unchanged'])
        self.assertGreater(self.estimate['live_run_inventory_entries'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
