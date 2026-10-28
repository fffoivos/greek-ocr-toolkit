"""Identity boundaries and fail-closed split tests; no external service calls."""
import gzip
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_book_registry import Registry, aliases, decide, prefix, sha, rows, REFERENCE_NAMESPACES


class BookRegistryTests(unittest.TestCase):
    def test_train_test_never_resolves_by_priority(self):
        for labels in [('train', 'test'), ('dev', 'test'), ('train', 'seal04_dev')]:
            self.assertEqual(decide([{'split': s} for s in labels]), ('unassigned', 'conflict', False))

    def test_line_instruments_are_not_book_splits(self):
        for kind in ('lqb', 'release_exclusion'):
            self.assertEqual(decide([{'split':'train'}, {'split':kind, 'scope':'row'}]), ('train','assigned',True))
            self.assertEqual(decide([{'split':kind, 'scope':'row'}]), ('unassigned','no_recorded_split',False))

    def test_train_holdout_remains_pending_owner_ruling(self):
        self.assertEqual(decide([{'split':'train'}, {'split':'hold_out'}]), ('conflict_hold_out','conflict',False))

    def test_explicit_ruling_is_scoped_and_preserves_history(self):
        import hashlib
        from build_book_registry import canonical
        ruling = json.loads((Path(__file__).resolve().parent/'SPLIT_RULING.json').read_text())
        aa = {('ia_identifier', 'b28038630')}
        ruling['book_id'] = 'book-' + hashlib.sha256(canonical(next(iter(aa))).encode()).hexdigest()[:24]
        r = Registry()
        for label in ('train','hold_out'):
            r.add(aa, {'file':label}, {'split':label,'provenance':[{'file':label,'sha256':'1'*64}]})
        r.add({('ia_identifier','another')}, {'file':'other'}, {'split':'train'})
        r.add({('ia_identifier','another')}, {'file':'other2'}, {'split':'hold_out'})
        records = r.materialize(ruling, [{'file':'SPLIT_RULING.json','sha256':'2'*64}])
        target = next(x for x in records if x['book_id']==ruling['book_id'])
        self.assertEqual((target['split'],target['exportable'],target['harvest_protection']), ('train',True,True))
        self.assertEqual(target['split_labels'], ['hold_out','train'])
        old = next(a for a in target['assignments'] if a['split']=='hold_out')
        self.assertEqual(old['superseded_by'],ruling['ruling_id'])
        self.assertEqual(old['provenance'][0]['file'],'hold_out')
        other = next(x for x in records if x['book_id']!=ruling['book_id'])
        self.assertEqual(other['split'],'conflict_hold_out')
        ruling['book_id']='wrong'
        with self.assertRaisesRegex(ValueError,'identity'):
            r.materialize(ruling, [])

    def test_real_ruling_publishability_and_policy_provenance(self):
        import pyarrow.parquet as pq
        root=Path(__file__).resolve().parent
        report=json.loads((root/'BUILD_RECEIPT.json').read_text())
        self.assertTrue(report['publishable'])
        self.assertEqual(report['conflicts'],[])
        records=pq.read_table(root/'book_registry.parquet').to_pylist()
        target=next(x for x in records if any(a['namespace']=='ia_identifier' and a['value']=='b28038630' for a in x['aliases']))
        self.assertEqual((target['split'],target['harvest_protection'],target['exportable']),('train',True,True))
        assignment=next(a for a in target['assignments'] if a.get('ruling_id'))
        self.assertEqual({Path(p['file']).name for p in assignment['provenance']}, {'SPLIT_RULING.json','apply_clean.py','split_moves_v2.json'})
        for p in assignment['provenance']:
            self.assertEqual(sha(p['file']),p['sha256'])

    def test_compatible_suite_annotation_and_recorded_val(self):
        self.assertEqual(decide([{'split': 'dev'}, {'split': 'seal04_dev'}]), ('seal04_dev', 'assigned', True))
        self.assertEqual(decide([{'split': 'hold_out'}, {'split': 'lqb'}]), ('hold_out', 'assigned', True))
        self.assertEqual(decide([]), ('unassigned', 'no_recorded_split', False))

    def test_provider_scoping_and_url_normalization(self):
        a = aliases({'item': '1234'}, 'nlg')
        b = aliases({'item': '1234'}, 'mytilene')
        self.assertFalse(a & b)
        a = aliases({'source_url': 'http://archive.org/details/example/'})
        b = aliases({'identifier': 'example'}, 'ia')
        self.assertIn(('ia_identifier', 'example'), a & b)
        a = aliases({'book': '/metadata/a/b/c/one.tkl'}, 'anemi')
        b = aliases({'source_url': 'https://anemi.lib.uoc.gr/metadata/a/b/c/one.tkl'})
        self.assertTrue(a & b)

    def test_local_namespaces_and_line_prefixes(self):
        self.assertEqual(prefix('source--abc--s012-l0004'), 'source--abc')
        self.assertEqual(prefix('W3--nlg--abc--p000123-l002'), 'W3--nlg--abc')
        a = aliases({'doc': 'round1:abc', 'id': 'abc-p000001-l001'}, 'anemi')
        self.assertIn(('v2_book_id', 'round1:abc'), a)
        self.assertIn(('line_id_prefix', 'abc'), a)

    def test_transitive_observed_alias_join_conflict_retains_provenance(self):
        r = Registry()
        r.add({('local', 'a'), ('provider', 'x')}, {'file': 'one', 'sha256': '1'}, {'split': 'train'})
        r.add({('local', 'b'), ('provider', 'x')}, {'file': 'two', 'sha256': '2'}, {'split': 'test'})
        result = r.materialize()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['conflict'])
        self.assertFalse(result[0]['exportable'])
        self.assertEqual(result[0]['split'], 'unassigned')
        self.assertEqual(len(result[0]['assignments']), 2)
        self.assertEqual(len(result[0]['identity_provenance']), 2)

    def test_shared_catalogue_landing_page_does_not_merge_issues(self):
        r = Registry()
        for item in ('issue56', 'issue65'):
            aa = aliases({'id': item, 'catalogue_url': 'https://example.test/catalogue/14041'}, 'lekythos')
            r.add(aa, {'file': item})
        self.assertEqual(len(r.materialize()), 2)

    def test_real_artifact_roundtrip_and_assignment_hashes(self):
        import pyarrow.parquet as pq
        root = Path(__file__).resolve().parent
        if not (root / 'book_registry.parquet').exists():
            self.skipTest('build real artifact first')
        rr = [json.loads(s) for s in gzip.decompress((root / 'book_registry.jsonl.gz').read_bytes()).splitlines()]
        self.assertEqual(rr, pq.read_table(root / 'book_registry.parquet').to_pylist())
        self.assertEqual(len(rr), len({r['book_id'] for r in rr}))
        seen = set()
        for r in rr:
            if r['conflict']:
                self.assertFalse(r['exportable'])
                self.assertIn(r['split'], ('unassigned', 'conflict_hold_out'))
                self.assertTrue(r['harvest_protection'])
            self.assertNotIn(r['split'], ('lqb', 'release_exclusion'))
            if r['assignment_status']=='no_recorded_split':
                self.assertTrue(r['split'].startswith('unassigned_'))
                self.assertTrue(r['unassigned_reason'])
            if r['row_instrument_roles']:
                self.assertTrue(r['harvest_protection'])
            for a in r['aliases']:
                if a['namespace'] in REFERENCE_NAMESPACES:
                    continue
                key = (a['namespace'], a['value'])
                self.assertNotIn(key, seen)
                seen.add(key)
            for a in r['assignments']:
                self.assertTrue(a['provenance'])
                for p in a['provenance']:
                    self.assertEqual(len(p['sha256']), 64)
        report = json.loads((root / 'BUILD_RECEIPT.json').read_text())
        self.assertEqual(report['books'], len(rr))
        self.assertEqual(sum(report['counts_per_split'].values()), len(rr))
        self.assertTrue({'W1', 'W2', 'W3', 'W4'} <= {c['wave'] for c in report['coverage']})
        self.assertTrue({'round1', 'round2', 'mixed', 'cyrillic', 'openarchives', 'parliament', 'vouli', 'wikisource'} <= {c['wave'] for c in report['coverage']})

    def test_every_wave_manifest_page_and_legacy_raster_joins(self):
        import csv
        import pyarrow.parquet as pq
        root = Path(__file__).resolve().parent
        if not (root / 'BUILD_RECEIPT.json').exists():
            self.skipTest('build real artifact first')
        report = json.loads((root / 'BUILD_RECEIPT.json').read_text())
        index = {a['value']:r['book_id'] for r in pq.read_table(root / 'book_registry.parquet').to_pylist() for a in r['aliases'] if a['namespace']=='line_id_prefix'}
        for c in report['coverage']:
            if c['wave'] in ('W1','W2','W3','W4'):
                n = 0
                for r in rows(c['file']):
                    self.assertIn(prefix(r['id']), index)
                    n += 1
                self.assertEqual(n, c['records'])
            if c['wave'] == 'all_retained_legacy_images':
                import re
                with Path(c['file']).open() as f:
                    for r in csv.DictReader(f, delimiter='\t'):
                        key = prefix(re.sub(r'-\d{6}$', '', Path(r['relative_path']).stem))
                        self.assertIn(key, index)

    def test_exact_line_instrument_memberships_and_original_309_origins(self):
        import pyarrow.parquet as pq
        root = Path(__file__).resolve().parent
        report = json.loads((root/'BUILD_RECEIPT.json').read_text())
        memberships = pq.read_table(root/'row_instruments.parquet').to_pylist()
        for source in report['inputs']:
            if 'row_instrument_list' not in source['kinds']:
                continue
            expected = set(Path(source['path']).read_text().splitlines())
            actual = [r for r in memberships if r['list_name']==Path(source['path']).name]
            self.assertEqual({r['row_id'] for r in actual}, expected)
            self.assertEqual(len(actual),len(expected))
            self.assertTrue(all(r['list_sha256']==source['sha256'] for r in actual))
        self.assertEqual({r['kind'] for r in memberships if r['list_name']=='w1_elstat_separator_ambiguous_ids.txt'}, {'release_exclusion'})
        records=pq.read_table(root/'book_registry.parquet').to_pylist()
        original_no_split=[r for r in records if r['assignment_status']=='no_recorded_split' and not r['row_instrument_roles']]
        self.assertEqual(len(original_no_split),309)
        self.assertTrue(all(r['unassigned_reason'] and r['identity_provenance'] for r in original_no_split))


if __name__ == '__main__':
    unittest.main()
