"""Synthetic file tests for BENCH02L identity, accounting and determinism."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import derive_candidates_v3 as v3


class CandidatesV3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        # Emission order deliberately differs from recorded rank order.
        self.rows = [dict(parent_id='p', row_id=f'r{rank}', split='test',
                          source='s', **{'class': 'latin'}, rank=rank,
                          tags={}, evidence={'number': 1.2500, 'text': 'Α'})
                     for rank in (3, 1, 2)]
        self.counts = {'classes': {'test:latin': dict(quota=2, credited=2, drawn=3, subgroup_quotas={})}}
        self.plan = dict(quotas={'latin': 2}, dev_quotas={}, subquotas={})
        self.write_inputs()

    def write_inputs(self):
        data = b''.join((json.dumps(r, ensure_ascii=False) + '\n').encode() for r in self.rows)
        # A number spelling that JSON reserialization would change.
        data = data.replace(b'1.25', b'1.2500')
        (self.directory / 'candidates.jsonl').write_bytes(data)
        for name, value in (('counts.json', self.counts), ('draw_plan.json', self.plan)):
            (self.directory / name).write_text(json.dumps(value))

    def generate(self):
        result, summary = v3.run(self.directory)
        return [json.loads(line) for line in result.splitlines()], summary

    def test_in_quota_equals_credited(self):
        rows, summary = self.generate()
        self.assertEqual(2, sum(r['in_quota'] for r in rows))
        self.assertEqual([False, True, True], [r['in_quota'] for r in rows])
        self.assertEqual(0, summary['classes']['test:latin']['subgroup_gap'])
        self.counts['classes']['test:latin']['credited'] = 1
        self.write_inputs()
        with self.assertRaisesRegex(AssertionError, 'in-quota count'):
            self.generate()

    def test_reserve_equals_drawn_minus_credited_and_rank_order(self):
        rows, _ = self.generate()
        self.assertEqual([1, None, None], [r['overdraw_order'] for r in rows])
        damaged = copy.deepcopy(rows)
        damaged[0]['overdraw_order'] = 2
        with self.assertRaisesRegex(AssertionError, 'reserve order'):
            v3.validate(self.rows, damaged, self.counts, self.plan)
        self.counts['classes']['test:latin']['drawn'] = 4
        self.write_inputs()
        with self.assertRaisesRegex(AssertionError, 'drawn count'):
            self.generate()

    def test_no_duplicate_row_keys(self):
        self.rows[0]['row_id'] = self.rows[1]['row_id']
        self.write_inputs()
        with self.assertRaisesRegex(AssertionError, 'duplicate row key'):
            self.generate()

    def test_row_order_set_values_and_member_bytes_unchanged(self):
        before = (self.directory / 'candidates.jsonl').read_bytes()
        rows, _ = self.generate()
        result = (self.directory / 'candidates_v3.jsonl').read_bytes()
        for old, new in zip(before.splitlines(), result.splitlines()):
            self.assertTrue(new.startswith(old[:-1] + b','))
        self.assertEqual(before, (self.directory / 'candidates.jsonl').read_bytes())
        self.assertEqual(self.rows, [{k: value for k, value in r.items() if k not in v3.NEW_FIELDS} for r in rows])
        with self.assertRaisesRegex(AssertionError, 'row order/set'):
            v3.validate(self.rows, list(reversed(rows)), self.counts, self.plan)
        rows[0]['source'] = 'changed'
        with self.assertRaisesRegex(AssertionError, 'row order/set'):
            v3.validate(self.rows, rows, self.counts, self.plan)

    def test_second_run_byte_identical(self):
        v3.run(self.directory)
        names = ('candidates_v3.jsonl', 'CANDIDATES_V3.md')
        first = [(self.directory / name).read_bytes() for name in names]
        v3.run(self.directory)
        self.assertEqual(first, [(self.directory / name).read_bytes() for name in names])

    def test_subgroup_ranks_restrict_draw_order_and_account_for_credit_gap(self):
        # Serbian-only supply: credited=min(3,4)=3, but Serbian quota=2.
        for r in self.rows:
            r['class'] = 'modern_cyrillic'
            r['tags'] = {'cyrillic_language': 'sr'}
        subs = {'sr': 2, 'ru': 2}
        self.counts = {'classes': {'test:modern_cyrillic': dict(quota=4, credited=3, drawn=3,
                        subgroup_quotas=subs, subgroups={'sr': 3})}}
        self.plan = dict(quotas={'modern_cyrillic': 4}, dev_quotas={},
                         subquotas={'test': {'modern_cyrillic': subs}})
        self.write_inputs()
        rows, summary = self.generate()
        self.assertEqual([3, 1, 2], [r['scope_rank'] for r in rows])
        self.assertEqual(['test:modern_cyrillic:sr'] * 3, [r['quota_scope'] for r in rows])
        self.assertEqual(dict(in_quota=2, reserve=1, credited=3, subgroup_gap=1),
                         summary['classes']['test:modern_cyrillic'])
        self.assertEqual(dict(quota=2, in_quota=0, reserve=0), summary['scopes']['test:modern_cyrillic:ru'])
        # Interleaved fonts: subgroup ranks must differ from original ranks.
        for r in self.rows:
            r['class'] = 'font_extremes'
            r['tags'] = {'font_size': 'small' if r['rank'] in (1, 3) else 'large'}
        subs = {'small': 1, 'large': 1}
        self.counts = {'classes': {'test:font_extremes': dict(quota=2, credited=2, drawn=3,
                        subgroup_quotas=subs, subgroups={'small': 2, 'large': 1})}}
        self.plan = dict(quotas={'font_extremes': 2}, dev_quotas={}, subquotas={'test': {'font_extremes': subs}})
        self.write_inputs()
        rows, _ = self.generate()
        self.assertEqual([2, 1, 1], [r['scope_rank'] for r in rows])
        self.assertEqual([1, None, None], [r['overdraw_order'] for r in rows])

    def test_duplicate_json_members_rejected(self):
        p = self.directory / 'candidates.jsonl'
        p.write_bytes(p.read_bytes().replace(b'"rank": 3', b'"rank": 3, "rank": 3'))
        with self.assertRaisesRegex(AssertionError, 'duplicate JSON member'):
            self.generate()

    def test_quota_disagreement_rejected(self):
        self.plan['quotas']['latin'] = 3
        self.write_inputs()
        with self.assertRaisesRegex(AssertionError, 'quota disagreement'):
            self.generate()


if __name__ == '__main__':
    unittest.main()
