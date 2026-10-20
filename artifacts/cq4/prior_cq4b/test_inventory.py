"""CQ4b mandatory-stop, amendment-scope and canonical-scanner regression checks."""
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'artifacts/cq4'
SCANNER_SHA = 'dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
PREREG_SHA = 'dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc'


def load(p):
    return json.loads(p.read_text())


def alias(d):
    return d.removesuffix(':human').split(':')[-1]


class InventoryGateTests(unittest.TestCase):
    def setUp(self):
        self.inventory=load(OUT/'inventory.json')
        self.excluded=load(OUT/'excluded_docs.json')

    def test_separate_exclusion_unions(self):
        e=self.excluded
        union=set().union(*(set(ds) for ds in e['by_reason'].values()))
        self.assertEqual(sorted(union),e['documents'])
        self.assertEqual(len(union),e['count'])
        self.assertEqual(e['topup']['documents'],e['documents'])
        wunion=set().union(*(set(ds) for k,ds in e['by_reason'].items() if k!='validation'))
        self.assertEqual(sorted(wunion),e['wcap']['documents'])
        self.assertEqual(union-wunion,set(e['by_reason']['validation']))
        self.assertLessEqual(set(e['by_reason']['calibration']),wunion)

    def test_amended_wcap_population_exact(self):
        roles=load(ROOT/'docs/labelfix/spellcheck/R2/doc_roles.json')['documents']
        validation={alias(d) for d,m in roles.items() if m['role']=='validation'}
        unused={alias(d) for d in load(OUT/'prior_cq4/inventory.json')['wcap_candidate_documents']}
        self.assertEqual(len(validation),17)
        self.assertEqual(len(unused),3)
        chosen=set(self.inventory['wcap_candidate_documents'])
        self.assertEqual(chosen,validation|unused)
        self.assertTrue(chosen.isdisjoint(self.excluded['wcap']['documents']))
        self.assertEqual(chosen,set(self.excluded['wcap']['eligible_documents']))
        self.assertGreaterEqual(len(chosen)*30,210)

    def test_topup_excludes_validation_and_other_custody(self):
        ds=set(self.inventory['topup_candidate_documents'])
        self.assertTrue(ds.isdisjoint(self.excluded['topup']['documents']))
        self.assertEqual(ds,{'1909952','euripidesexrecen03euri','IA41545826_0032'})
        # All three are available to EITHER set, never assigned to both.
        self.assertLessEqual(ds,set(self.inventory['wcap_candidate_documents']))
        self.assertEqual({r['pool'] for r in self.inventory['topup_candidate_documents'].values()},{'W1'})

    def test_stop_bound_even_before_wcap_reservation(self):
        x=self.inventory
        self.assertEqual(x['topup_target'],735+470)
        self.assertEqual(x['topup_document_cap'],math.floor(.1*x['topup_target']))
        self.assertEqual(x['topup_minimum'],math.ceil(.7*x['topup_target']))
        self.assertEqual(x['topup_upper_bound'],len(x['topup_candidate_documents'])*x['topup_document_cap'])
        self.assertLess(x['topup_upper_bound'],x['topup_minimum'])
        self.assertLess(x['topup_upper_bound'],math.ceil(.7*((800-214)+(500-127))))
        self.assertEqual(x['status'],'STOP_TOPUP_INVENTORY_SHORTFALL')
        self.assertIsNone(x['slot_counts'])
        for k in ('pack_contexts_built','controls_built','reader_runs','training_runs','manifest_builds'):
            self.assertEqual(x[k],0)
        self.assertFalse((OUT/'RUN_ALL.sh').exists())
        self.assertFalse((OUT/'control_review/controls.png').exists())

    def test_per_document_line_counts(self):
        counts={d:0 for d in self.inventory['wcap_candidate_documents']}
        with (ROOT/'docs/labelfix/spellcheck/R2/eligible_lines.jsonl').open() as f:
            for s in f:
                r=json.loads(s);d=alias(r['document'])
                if d in counts:counts[d]+=1
        self.assertEqual(counts,{d:m['lines'] for d,m in self.inventory['wcap_candidate_documents'].items()})
        for d,m in self.inventory['topup_candidate_documents'].items():
            self.assertEqual(m['lines'],counts[d])

    def test_heldout_custody(self):
        groups=self.excluded['by_reason']
        self.assertEqual(len(groups['old_pool_316']),316)
        self.assertEqual(len(groups['old_pool_heldout16']),16)
        self.assertLessEqual(set(groups['old_pool_heldout16']),set(groups['old_pool_316']))

    def test_canonical_scanner_and_preregistration(self):
        self.assertEqual(hashlib.sha256((OUT/'tools/scan_rollout.py').read_bytes()).hexdigest(),SCANNER_SHA)
        self.assertEqual(self.inventory['scanner_sha256'],SCANNER_SHA)
        self.assertEqual(self.inventory['preregistration_sha256'],PREREG_SHA)
        self.assertEqual(self.inventory['scanner_version'],'v4.4-canonical')
        self.assertTrue(self.inventory['scanner_copy_before_and_after_verified'])
        for name in ('r1','r1b'):
            scan=load(OUT/'regression'/f'cq1_{name}.scan_v44.json')
            self.assertEqual(scan['scanner_sha256'],SCANNER_SHA)
            self.assertFalse(scan['manifest_check_skipped'])
            self.assertEqual(scan['ok'],name=='r1b')
            self.assertTrue(scan['image_matches'])
            if name=='r1':
                self.assertEqual(scan['violations'],[dict(record=24,reason='absolute path outside reader_dir',path='/zoom/batch1.png')])
            else:self.assertEqual(scan['violations'],[])

    def test_input_hashes(self):
        receipt=load(OUT/'build_receipt.json')
        for name,sha in receipt['inputs_sha256'].items():
            with self.subTest(path=name):
                h=hashlib.sha256()
                with Path(name).open('rb') as f:
                    for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
                self.assertEqual(h.hexdigest(),sha)

if __name__=='__main__':unittest.main()
