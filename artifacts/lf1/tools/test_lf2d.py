"""Offline synthetic LF2d CLI/schema/seal integration; sourcing files read-only."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator
from lf1 import dump, jsonl, rows, sha
import prod_finalize

SEAL = Path.home()/'Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seal02'
SCHEMA_SHA = 'ec430f1460fa9d35ccc581ee9408efdf6be03a69e73d14765563520d7ebf972f'
OUT = Path(__file__).resolve().parents[1]/'prod/lf2d_synthetic'


def candidate(rid, rank, selected=True, source='s', split='test'):
    return dict(parent_id='SYNTHETIC',row_id=rid,source=source,split=split,
        **{'class':'latin'},quota_scope=split+':latin',scope_rank=rank,
        in_quota=selected,overdraw_order=None if selected else rank)


class SealIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        OUT.mkdir(parents=True,exist_ok=True)
        cls.cs=[candidate('a',1),candidate('b',2),candidate('c',3,source='no-reserve'),
                candidate('ok',4),candidate('blocked',5,False),candidate('same',6,False),
                candidate('foreign',7,False,source='foreign'),candidate('dev',1,split='dev')]
        cls.vs=[dict(line_id=r['row_id'],verdict='OK' if r['row_id'] in
                    ('ok','same','foreign') else 'CROP_VIOLATES',
                    reasons=['synthetic flag'],where=[],state='RESOLVED',mock=False) for r in cls.cs]
        jsonl(OUT/'candidates.SYNTHETIC.jsonl',cls.cs)
        jsonl(OUT/'line_verdicts_merged.SYNTHETIC.jsonl',cls.vs)
        with patch('sys.argv',['prod_finalize.py','--candidates',str(OUT/'candidates.SYNTHETIC.jsonl'),
                '--verdicts',str(OUT/'line_verdicts_merged.SYNTHETIC.jsonl'),
                '--output',str(OUT/'final_list.SYNTHETIC.jsonl'),
                '--receipt',str(OUT/'final_receipt.SYNTHETIC.json')]):
            prod_finalize.main()
        cls.schema=json.loads((SEAL/'FINAL_LIST.schema.json').read_text())
        spec=importlib.util.spec_from_file_location('sourcing_seal02',SEAL/'build_suite02.py')
        cls.seal=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.seal)
        cls.binding=json.loads((OUT/'final_receipt.SYNTHETIC.json.bindings.json').read_text())
        cls.binding['candidates']=dict(path=str(OUT/'candidates.SYNTHETIC.jsonl'),
                                     sha256=sha(OUT/'candidates.SYNTHETIC.jsonl'))

    def test_schema_and_three_bindings(self):
        self.assertEqual(sha(SEAL/'FINAL_LIST.schema.json'),SCHEMA_SHA)
        Draft202012Validator.check_schema(self.schema)
        for r in rows(self.binding['final_list']['path']):
            Draft202012Validator(self.schema).validate(r)
            self.assertIs(r['mock'],False)
        receipt=json.loads(Path(self.binding['final_receipt']['path']).read_text())
        Draft202012Validator(self.schema['$defs']['receipt']).validate(receipt)
        self.assertEqual(receipt['counts'],dict(flagged=4,REPLACED=1,UNFILLED=3))
        for b in self.binding.values():self.assertEqual(sha(b['path']),b['sha256'])
        details=json.loads((OUT/'final_receipt.SYNTHETIC.json.details.json').read_text())
        self.assertEqual(details['replacements'][0]['flag_reason']['reasons'],['synthetic flag'])
        self.assertEqual([r['line_id'] for r in details['non_OK_reserve_used']],['blocked'])

    def test_sourcing_final_checked_accepts_cli_output(self):
        fi,rc,vd,unfilled=self.seal.final_checked(dict(inputs=self.binding),self.cs,False)
        self.assertEqual(len(fi),2);self.assertEqual(len(unfilled),3)

    def check_modified(self, final=None, cs=None):
        with tempfile.TemporaryDirectory(prefix='lf2d-') as tmp:
            b=copy.deepcopy(self.binding)
            if final is not None:
                p=Path(tmp)/'final.jsonl';jsonl(p,final);b['final_list']['path']=str(p)
            return self.seal.final_checked(dict(inputs=b),cs or self.cs,False)

    def test_sourcing_rejects_foreign_source_promotion(self):
        fs=rows(self.binding['final_list']['path'])
        fs[0].update(row_id='foreign',lf1_receipt_ref=dict(
            verdicts_sha256=self.binding['verdicts']['sha256'],line_id='foreign'))
        with self.assertRaisesRegex(ValueError,'selection/replacement'):
            self.check_modified(final=fs)

    def test_sourcing_rejects_non_ok_final(self):
        fs=rows(self.binding['final_list']['path']);fs[0]['lf1_verdict']='CROP_VIOLATES'
        with self.assertRaisesRegex(ValueError,'non-OK'):self.check_modified(final=fs)

    def test_sourcing_order_discrepancy_is_visible(self):
        # Both reserves OK, but ranks disagree with explicit overdraw order.
        cs=[candidate('a',1),candidate('later',2,False),candidate('first',3,False)]
        cs[1]['overdraw_order']=3;cs[2]['overdraw_order']=2
        vs=[dict(line_id=r['row_id'],verdict='BAD' if r['row_id']=='a' else 'OK') for r in cs]
        final,details=prod_finalize.finalize(cs,vs)
        self.assertEqual(final[0]['row_id'],'first')
        with tempfile.TemporaryDirectory(prefix='lf2d-order-') as tmp:
            root=Path(tmp);jsonl(root/'v',vs)
            jsonl(root/'f',prod_finalize.seal_rows(final,details,cs,sha(root/'v')))
            dump(root/'r',dict(status='FINALIZED',mock=False,final_list_sha256=sha(root/'f'),
                verdicts_sha256=sha(root/'v'),candidates_sha256='0'*64,
                counts=dict(flagged=1,REPLACED=1,UNFILLED=0)))
            b={role:dict(path=str(root/name),sha256=sha(root/name)) for role,name in
               [('verdicts','v'),('final_list','f'),('final_receipt','r')]}
            b['candidates']=dict(sha256='0'*64)
            with self.assertRaisesRegex(ValueError,'selection/replacement'):
                self.seal.final_checked(dict(inputs=b),cs,False)


if __name__=='__main__':unittest.main(verbosity=2)
