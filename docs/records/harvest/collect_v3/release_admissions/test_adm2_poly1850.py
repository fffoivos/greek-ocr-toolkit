"""Offline ADM2 checks, including the pre-existing literal arm mismatch."""
from collections import Counter
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import append_adm2_poly1850 as adm


class ADM2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base, cls.old = adm.baseline()
        cls.data = adm.ADMISSIONS.read_bytes()
        cls.lines = cls.data.splitlines(keepends=True)
        cls.rows = [json.loads(line) for line in cls.lines]
        cls.new = [r for r in cls.rows if r['arm'] == adm.ARM]
        cls.summary = json.loads(adm.SUMMARY.read_text())
        cls.expected, cls.counts, cls.dropped, cls.inputs = adm.candidates()
        cls.w1 = {}
        with (adm.RUN / 'W1/crop_tight_page.jsonl').open() as stream:
            for line in stream:
                r = json.loads(line)
                if (r['source'], r['primary_class']) == ('kosmopolis', 'poly1850'):
                    cls.w1[r['id']] = r
        cls.records = {r['id']: r for line in (adm.W / 'kosmopolis/records.jsonl').read_text().splitlines()
                       if (r := json.loads(line))}

    def test_01_wave_subset_is_byte_identical_before_and_after(self):
        subset = b''.join(line for line, r in zip(self.lines, self.rows) if r['arm'] == adm.WAVE_ARM)
        self.assertEqual(subset, self.base)
        self.assertEqual(adm.digest(subset), adm.BASE_SHA)
        self.assertEqual(self.data[:len(self.base)], self.base)
        self.assertEqual(len(self.old), 16562)

    def test_02_arm_filters_and_literal_mismatch_are_explicit(self):
        counts = Counter(r['arm'] for r in self.rows)
        self.assertEqual(counts, {adm.WAVE_ARM: 16562, adm.ARM: 462})
        self.assertEqual(counts['wave-1d'], 0)
        self.assertEqual(self.summary['arm_filter_counts'],
                         {'wave-1d': 0, adm.WAVE_ARM: 16562, adm.ARM: 462})
        self.assertIn('matches zero rows', self.summary['arm_contract_note'])

    def test_03_candidate_is_exact_t6g_pool_without_duplicates(self):
        key = json.loads((adm.W / 'cards_kosmo_poly1850_key.json').read_text())
        self.assertEqual([r['row_id'] for r in self.new], key['_pool_line_ids'])
        self.assertEqual(len({r['row_id'] for r in self.rows}), 17024)
        self.assertEqual(self.new, self.expected)
        self.assertEqual(self.data[len(self.base):], adm.encode(self.expected))

    def test_04_candidate_fields_and_reading_provenance(self):
        for r in self.new:
            with self.subTest(row_id=r['row_id']):
                self.assertEqual(set(r), set(self.old[0]) | {'marks_status'})
                self.assertEqual((r['source'], r['primary_class'], r['tranche']),
                                 ('kosmopolis', 'poly1850', 'W1'))
                self.assertEqual(r['marks_status'], 'pending_opus')
                self.assertEqual(r['provenance']['sol_reading'], 'sol/recut-v1 87db4392')
                self.assertEqual(set(r['provenance']), set(self.old[0]['provenance']) | {'sol_reading'})

    def test_05_every_new_row_has_builder_hash_and_collector_metadata(self):
        for r in self.new:
            with self.subTest(row_id=r['row_id']):
                w1, rec = self.w1[r['row_id']], self.records[r['row_id']]
                want = rec['masked_crop_sha256'] if r['guard_status'] == 'masked' else rec['original_crop_sha256']
                self.assertEqual(adm.sha(r['crop']), want)
                self.assertEqual(r['crop_sha256'], want)
                self.assertEqual(r['original_crop_sha256'], w1['crop_sha256'])
                self.assertEqual(r['label'], w1['label'])
                self.assertEqual(r['page_id'], w1['page_id'])
                self.assertEqual(r['line_index'], int(r['row_id'].rsplit('-l', 1)[1]))

    def test_06_guarded_original_branch_and_hash_rejections(self):
        r = self.w1[self.new[0]['row_id']]
        x = dict(self.records[r['id']], output_kind='guarded_original')
        with patch.object(adm, 'sha', return_value=x['original_crop_sha256']):
            guarded = adm.make_row(r, x)
            self.assertEqual(guarded['guard_status'], 'guarded_original')
            self.assertIsNone(guarded['crop_masked_tag'])
        with patch.object(adm, 'sha', return_value='0' * 64):
            with self.assertRaisesRegex(ValueError, 'T6b crop hash mismatch'):
                adm.make_row(r, x)
        with patch.object(adm, 'sha', return_value=x['original_crop_sha256']):
            with self.assertRaisesRegex(ValueError, 'collector crop hash mismatch'):
                adm.make_row(dict(r, crop_sha256='0' * 64), x)

    def test_07_exclusions_and_unmatched_are_absent(self):
        excluded = set()
        for name, spec in self.inputs.items():
            if name.startswith('exclusion_ids:') or name == 'rotated_ids':
                excluded.update(Path(spec['path']).read_text().split())
        old_key = json.loads((adm.W / 'cards/kosmopolis_key.json').read_text())
        previous = {v['line_id'] for v in old_key.values() if isinstance(v, dict) and 'line_id' in v}
        for r in self.new:
            rid = r['row_id']
            self.assertNotIn(rid, excluded | previous)
            self.assertFalse(self.w1[rid].get('screen_merged'))
            self.assertFalse(self.records[rid].get('screen_merged'))
            self.assertIn(self.records[rid]['output_kind'], ('masked', 'guarded_original'))

    def test_08_pool_difference_is_explained_with_exact_ids(self):
        self.assertEqual(self.counts['class_rows'], 473)
        self.assertEqual(self.counts['builder_eligible'], 473)
        self.assertEqual(self.counts['admitted'], 462)
        reason = 'previous_t6b_card (outside recorded T6g pool)'
        self.assertEqual(self.counts[reason], 11)
        self.assertEqual(set(self.w1) - {r['row_id'] for r in self.new}, set(self.dropped[reason]))
        self.assertEqual(self.summary['adm2']['difference_from_t6g_pool'], 0)

    def test_09_summary_counts_file_sha_and_bound_inputs(self):
        self.assertEqual(self.summary['sha256'], adm.digest(self.data))
        self.assertEqual(self.summary['wave1d_subset_sha256'], adm.BASE_SHA)
        self.assertEqual(self.summary['wave1d_subset_before_sha256'], adm.BASE_SHA)
        expected_counts = Counter((r['arm'], r['source'], r['primary_class']) for r in self.rows)
        actual_counts = {(r['arm'], r['source'], r['primary_class']): r['rows']
                         for r in self.summary['counts_per_arm_source_class']}
        self.assertEqual(expected_counts, actual_counts)
        self.assertEqual(self.summary['bound_inputs'], adm.bindings())
        self.assertEqual(self.summary['srk2_results_sha256'],
                         adm.sha(adm.W / 'checks/kosmo_poly1850_sol/results.json'))
        self.assertEqual(self.summary['adm2']['marks']['status'], 'pending_opus')

    def test_10_full_readonly_verification_and_original_builder_unchanged(self):
        result = adm.verify()
        self.assertEqual((result['wave1d_rows'], result['candidate_rows']), (16562, 462))
        p = adm.HERE / 'build_w1_masked_1d.py'
        self.assertEqual(p.read_bytes(), adm.git_bytes(adm.BASE_HEAD, str(p.relative_to(adm.ROOT))))


if __name__ == '__main__':
    unittest.main(verbosity=2)
