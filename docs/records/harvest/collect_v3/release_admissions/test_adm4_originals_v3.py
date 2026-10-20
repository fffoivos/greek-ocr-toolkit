"""Independent full-population ADM4 contract checks; no crop reading or network."""
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path
import subprocess
import unittest

BASE = Path(__file__).resolve().parent.parent
OUT = BASE/'release_admissions'
RUN = Path.home()/'Projects/collect-v3-data/run/W1/features.jsonl'

def load(p): return json.loads(p.read_text())
def rows(p): return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

class ADM4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.features = {r['id']:r for r in rows(RUN)}
        cls.output = rows(OUT/'w1_originals_v3.jsonl')
        cls.summary = load(OUT/'w1_originals_v3_summary.json')
        cls.registry = load(BASE/'release_exclusions/release_exclusions.json')['classes']
        cls.sets = {k:set((BASE/'release_exclusions'/v['file']).read_text().split()) for k,v in cls.registry.items()}
        cls.removals = set().union(*cls.sets.values())
        cls.expected = set()
        cls.pool = []
        for r in cls.features.values():
            s,c = r['source'],r['primary_class']
            qualified = (c=='headings_caps' or
                         (s,c) in {('bsb_poly1850','poly1850'),('ia_poly1850','poly1850'),
                                   ('nlg','poly1850'),('nlg','poly1900'),('nlg','greek_poly'),
                                   ('serbia','cyrillic'),('elstat','numerics_tables'),
                                   ('kosmopolis','poly1850'),('kosmopolis','poly1900'),('lekythos','poly1900')} or
                         (s,c,r.get('gazette_stratum'))==('gazette_modern','modern_scanned','measured_1986_1990'))
            if r.get('candidate_usable') is True and qualified:
                cls.pool.append(r)
                if not r.get('screen_merged') and r['id'] not in cls.removals: cls.expected.add(r['id'])

    def test_exact_eligible_population(self):
        self.assertEqual({r['row_id'] for r in self.output},self.expected)
        self.assertEqual(len(self.output),len(self.expected))
        self.assertTrue(all(self.features[r['row_id']]['candidate_usable'] is True for r in self.output))

    def test_no_removal_sets(self):
        self.assertFalse(self.expected & self.removals)
        self.assertTrue(all(not self.features[r['row_id']]['screen_merged'] for r in self.output))

    def test_original_fields_and_marks(self):
        for r in self.output:
            f = self.features[r['row_id']]
            for k in ['source','primary_class','page_id','label','crop_bbox','crop_sha256']:
                self.assertEqual(r[k],f[k],(r['row_id'],k))
            self.assertEqual(r['gazette_stratum'],f.get('gazette_stratum'))
            self.assertEqual(r['line_index'],int(f['id'].rsplit('-l',1)[1]))
            self.assertEqual((r['arm'],r['crop']),('release-v3','original'))
            pending = r['primary_class']=='headings_caps' or (r['source'],r['primary_class'])==('kosmopolis','poly1850')
            self.assertEqual(r['marks_status'],'pending_opus' if pending else 'recorded')
            self.assertTrue(r['provenance']['evidence_commit'])

    def test_counts_and_disjoint_removals(self):
        s = self.summary
        self.assertEqual(s['pool'],len(self.pool))
        self.assertEqual(s['pool']-sum(s['removals'].values()),len(self.output))
        actual_removed = set()
        for reason, ids in s['removed_row_ids'].items():
            self.assertFalse(actual_removed & set(ids))
            self.assertEqual(len(ids),s['removals'][reason])
            actual_removed.update(ids)
        self.assertEqual(actual_removed,{r['id'] for r in self.pool}-self.expected)
        for key, cnt in s['counts_per_source_class'].items():
            source,category = key.split('|')
            group = [r for r in self.pool if (r['source'],r['primary_class'])==(source,category)]
            self.assertEqual(cnt['pool'],len(group))
            self.assertEqual(cnt['pool']-sum(cnt.get('removed_'+k,0) for k in s['removals']),cnt.get('rows',0))
        expected_counts=Counter('|'.join([r['source'],r['primary_class'],r.get('gazette_stratum') or '-']) for r in self.output)
        self.assertEqual(s['counts_per_stratum'],dict(expected_counts))
        self.assertEqual(s['screen_hits']['rotated_crop'],sum(r['id'] in self.sets['rotated_crop'] for r in self.pool))
        for p,h in s['input_sha256'].items(): self.assertEqual(digest(Path(p)),h)
        self.assertEqual(digest(OUT/s['file']),s['sha256'])

    def test_lqb_in_sample_is_not_excluded(self):
        ids=set((BASE/'release_exclusions/lqb_truth_v1_wave1d_in_sample_ids.txt').read_text().split())
        self.assertEqual(len(ids),11)
        self.assertTrue(ids <= self.expected)
        self.assertNotIn('lqb_truth_v1_wave1d_in_sample_ids',self.registry)

    def test_masked_bytes_unchanged_and_summary_superseded(self):
        p=OUT/'w1_masked_1d.jsonl'
        self.assertEqual(digest(p),'d9343b74c4eeb61b592257f25f63f9b624e7a83d3ddcb3971d8951998253d064')
        tracked=subprocess.check_output(['git','show','HEAD:docs/harvest/collect_v3/release_admissions/w1_masked_1d.jsonl'],cwd=BASE)
        self.assertEqual(p.read_bytes(),tracked)
        summary=load(OUT/'w1_masked_1d_summary.json')
        self.assertEqual(summary['superseded_for_admission_by'],'w1_originals_v3.jsonl')
        self.assertEqual(summary['owner_rule'],self.summary['owner_rule'])
        old=json.loads(subprocess.check_output(['git','show','HEAD:docs/harvest/collect_v3/release_admissions/w1_masked_1d_summary.json'],cwd=BASE))
        self.assertEqual({k:v for k,v in summary.items() if k not in ['owner_rule','superseded_for_admission_by']},old)

    def test_ledger_current_and_history(self):
        ledger=load(BASE/'weak_ledger/ledger.json')
        old_md=subprocess.check_output(['git','show','HEAD:docs/harvest/collect_v3/WEAK_CATEGORY_LEDGER.md'],cwd=BASE).decode()
        tree=ast.parse((BASE/'weak_ledger/build_ledger.py').read_text())
        ns={}
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='render')
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<render>','exec'),ns)
        for r,history in zip(ledger['rows'],ledger['adm4_history']['rows']):
            selected=[a for a in self.output if a['primary_class'] in r['primary_classes']]
            self.assertEqual(r['collected_release_v3_original_rows']['value'],len(selected))
            current={x['source_name']:x['counts']['admitted']['value'] for x in r['collected_by_source_status'] if x['tranche']=='W1 release-v3 original'}
            self.assertEqual(current,dict(Counter(a['source'] for a in selected)))
            old_line=next(line for line in old_md.splitlines() if line.startswith('| '+r['category']+'<br>'))
            self.assertEqual(ns['render'](history['collected_by_source_status']),old_line.split(' | ')[3])
            self.assertIn(ns['render'](history['qualified_w1_union_rows']),old_line)
            self.assertIn('53–82%',r['crop_ok_notes'])
        md=(BASE/'WEAK_CATEGORY_LEDGER.md').read_text()
        self.assertIn('not admission blockers',md)
        self.assertIn('adm4_history',md)

if __name__=='__main__': unittest.main()
