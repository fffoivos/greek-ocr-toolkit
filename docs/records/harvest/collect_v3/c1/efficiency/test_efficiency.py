#!/usr/bin/env python3
"""Pack-integrity and independent arithmetic/error-path tests; no readers."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location('efficiency_'+name,ROOT/(name+'.py'))
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj


scorer = module('score')
validator = module('validate')
builder = module('build')


def fixture():
    arms = {a:a for a in ('E0a','E0b','E1','E2','E3','E4')}
    truth = {'bsb':{'c001':{'card_id':'c001','letters':'y','marks':'n','crop_ok':'y'},
                    'c002':{'card_id':'c002','letters':'n','marks':'na','crop_ok':'n'}},
             'yer':{'a001':{'item_id':'a001','slots':{'1':'ъ','2':'ь'}},
                    'a002':{'item_id':'a002','slots':{}}}}
    packs=[]; submissions=[]
    for bed in truth:
        for arm in arms:
            ids = list(truth[bed]); groups = [ids] if arm in ('E1','E4') else [[ids[0]],[ids[1]]]
            for n,group in enumerate(groups,1):
                reader=f'r{n}'
                packs.append({'bed':bed,'arm':arm,'reader':reader,'item_ids':group,'items_per_reader':len(group)})
                submissions.append((bed,arm,reader,[copy.deepcopy(truth[bed][i]) for i in group]))
    return {'packs':packs,'arms':arms},truth,submissions


class PackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/'MANIFEST.json').read_text())

    def test_01_isolation_hashes_ids_and_raster_sizes(self):
        result=validator.validate()
        self.assertEqual(result['isolation'],'ok')
        self.assertEqual(sum(p['bed'] in ('bsb','yer') for p in self.manifest['packs']),20)
        self.assertEqual(result['packs'],len(self.manifest['packs']))

    def test_02_controls_and_e1_protocol_byte_identity(self):
        for bed,source in [('bsb',ROOT.parent/'LABEL_CHECK_v2.md'),('yer',ROOT.parent/'yer_adjudication/INK.md')]:
            for arm in ('E0a','E0b','E1'):
                for p in (ROOT/f'packs/{bed}/{arm}').glob('*/PROTOCOL.md'):
                    self.assertEqual(p.read_bytes(),source.read_bytes())

    def test_03_e2_only_input_sentence_changed(self):
        for bed in ('bsb','yer'):
            control=builder.protocol(bed,'E0a'); changed=builder.protocol(bed,'E2')
            # Everything after the first input sentence is exactly unchanged.
            suffix = ' Your job is' if bed=='bsb' else ' Each hidden letter is'
            self.assertEqual(control.split(suffix,1)[1],changed.split(suffix,1)[1])
            self.assertEqual((ROOT/f'packs/{bed}/E2/r1/PROTOCOL.md').read_text(),changed)
            self.assertIn('you no longer get the full-line crop',changed)

    def test_04_e0_orders_differ_same_ids(self):
        for bed in ('bsb','yer'):
            a=json.loads((ROOT/f'keys/{bed}/E0a.json').read_text())['order']
            b=json.loads((ROOT/f'keys/{bed}/E0b.json').read_text())['order']
            self.assertNotEqual(a,b);self.assertEqual(set(a),set(b))

    def test_05_original_text_and_scripts_preserved(self):
        for bed in ('bsb','yer'):
            filename='cards.jsonl' if bed=='bsb' else 'items.jsonl';field='card_id' if bed=='bsb' else 'item_id'
            base={r[field]:r for p in (ROOT/f'packs/{bed}/E0a').glob('*/'+filename) for r in validator.read_rows(p)}
            for arm in self.manifest['arms']:
                for p in (ROOT/f'packs/{bed}/{arm}').glob('*/'+filename):
                    for row in validator.read_rows(p):
                        self.assertEqual({k:v for k,v in row.items() if k!='crop'},{k:v for k,v in base[row[field]].items() if k!='crop'})

    def test_06_approximation_receipt(self):
        for bed in ('bsb','yer'):
            mapping=json.loads((ROOT/f'keys/{bed}/E2.json').read_text())['e2_mapping']
            summary=self.manifest['e2_approximation'][bed]
            self.assertEqual(summary['approx_items'],sum(m['approx_box'] for m in mapping.values()))
            self.assertAlmostEqual(summary['approx_share_percent'],100*summary['approx_items']/len(mapping))

    def test_07_compact_prompts_shorter_and_shared(self):
        for bed in ('bsb','yer'):
            compact=(ROOT/f'packs/{bed}/E3/r1/PROTOCOL.md').read_text()
            self.assertEqual(compact,(ROOT/f'packs/{bed}/E4/r1/PROTOCOL.md').read_text())
            self.assertLess(len(compact),(len((ROOT/f'packs/{bed}/E0a/r1/PROTOCOL.md').read_text())))
            self.assertIn('Do not use sips or Pillow',compact)

    def test_08_pack_references_close_when_relocated(self):
        # Resolve as if the folder were elsewhere; no absolute path or .. escape.
        for p in self.manifest['packs']:
            base=Path('/hypothetical/isolated-reader')
            for row in validator.read_rows(ROOT/p['path']/p['items_file']):
                for rel in validator.image_paths(row):
                    self.assertTrue((base/rel).is_relative_to(base))

    def test_09_live_source_code_untouched(self):
        state=json.loads((ROOT/'keys/prebuild_state.json').read_text())
        repo=ROOT.parents[4]
        for rel,record in state['collect_v3'].items():
            path=repo/rel
            self.assertEqual(validator.sha(path),record['sha256'])
            self.assertEqual(path.stat().st_mtime_ns,record['mtime_ns'])


class ScorerTests(unittest.TestCase):
    def setUp(self):
        self.manifest,self.truth,self.submissions=fixture()

    def result(self, usage=None):
        return scorer.score(self.manifest,self.truth,self.submissions,usage)

    def arm(self,result,bed='bsb',arm='E1'):
        return result['beds'][bed]['arms'][arm]

    def test_10_perfect_reference_scores(self):
        result=self.result()
        self.assertEqual(self.arm(result)['agreement_with_truth']['fields']['marks']['rate'],1)
        self.assertEqual(self.arm(result,'yer')['agreement_with_truth']['slots']['agree'],2)

    def test_11_zero_slot_items_do_not_inflate_slot_accuracy(self):
        a=self.arm(self.result(),'yer')['agreement_with_truth']
        self.assertEqual(a['slots']['expected'],2)
        self.assertEqual(a['all_slots_per_item']['zero_slot_items'],1)

    def test_12_wrong_fields_are_separate(self):
        row=next(s[3][0] for s in self.submissions if s[:3]==('bsb','E1','r1'))
        row['letters']='u';row['marks']='y'
        a=self.arm(self.result())
        self.assertEqual(a['agreement_with_truth']['fields']['letters']['rate'],.5)
        self.assertEqual(a['agreement_with_truth']['fields']['crop_ok']['rate'],1)
        self.assertEqual(a['unresolved']['letters'],1)
        self.assertEqual(a['paired_quality_vs_E0a']['letters']['worse'],1)

    def test_13_reader_variance_is_actual_e0_difference(self):
        row=next(s[3][0] for s in self.submissions if s[:3]==('bsb','E0b','r2'))
        row['crop_ok']='y'
        result=self.result()
        self.assertEqual(result['beds']['bsb']['E0a_E0b_agreement']['fields']['crop_ok']['rate'],.5)
        self.assertEqual(self.arm(result)['agreement_with_E0a']['fields']['crop_ok']['rate'],1)

    def test_14_yer_other_u_and_confidence(self):
        row=next(s[3][0] for s in self.submissions if s[:3]==('yer','E2','r1'))
        row['slots']={'1':'other','2':'u'};row['confidence']={'1':'low','2':'high'}
        a=self.arm(self.result(),'yer','E2')
        self.assertEqual(a['unresolved'],{'u':1,'other':1,'items_with_u_or_other':1})
        self.assertEqual(a['confidence'],{'high':1,'low':1})
        self.assertEqual(a['agreement_with_truth']['slots']['rate'],0)

    def test_15_missing_usage_is_null_never_estimated(self):
        a=self.arm(self.result())['efficiency']
        self.assertIsNone(a['tokens_per_card']);self.assertIsNone(a['reader_wall_ms_per_card'])

    def test_16_measured_usage_arithmetic(self):
        u=scorer.parse_usage({'bsb/E1/r1':{'total_tokens':120,'tool_uses':6,'duration_ms':2000}})
        a=self.arm(self.result(u))['efficiency']
        self.assertEqual(a['tokens_per_card'],60);self.assertEqual(a['reader_wall_ms_per_card'],1000)
        self.assertEqual(a['tool_uses_per_card'],3)

    def test_17_two_readers_usage_summed(self):
        u=scorer.parse_usage({'bsb/E0a/r1':{'total_tokens':100,'tool_uses':2,'duration_ms':1000},
                              'bsb/E0a/r2':{'total_tokens':40,'tool_uses':4,'duration_ms':3000}})
        a=self.arm(self.result(u),arm='E0a')['efficiency']
        self.assertEqual(a['tokens_per_card'],70);self.assertEqual(a['reader_wall_ms_per_card'],2000)

    def test_18_partial_usage_is_not_extrapolated(self):
        u=scorer.parse_usage({'bsb/E0a/r1':{'total_tokens':100,'tool_uses':2,'duration_ms':1000}})
        a=self.arm(self.result(u),arm='E0a')['efficiency']
        self.assertFalse(a['usage_complete']);self.assertIsNone(a['tokens_per_card'])
        self.assertEqual(a['readers'][0]['tokens_per_card'],100)

    def test_19_missing_items_remain_visible(self):
        self.submissions=[s for s in self.submissions if s[:3]!=('bsb','E2','r2')]
        a=self.arm(self.result(),arm='E2')
        self.assertFalse(a['complete']);self.assertEqual(a['missing_items'],['c002'])
        self.assertEqual(a['agreement_with_truth']['fields']['letters']['expected'],2)
        self.assertEqual(a['agreement_with_truth']['fields']['letters']['compared'],1)

    def test_20_wrong_reader_id_rejected(self):
        self.submissions[0][3][0]['card_id']='c002'
        with self.assertRaisesRegex(ValueError,'different reader'):
            self.result()

    def test_21_duplicate_item_rejected(self):
        self.submissions[0][3].append(copy.deepcopy(self.submissions[0][3][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate card_id'):
            self.result()

    def test_22_duplicate_reader_rejected(self):
        self.submissions.append(self.submissions[0])
        with self.assertRaisesRegex(ValueError,'duplicate reader'):
            self.result()

    def test_23_missing_slot_rejected(self):
        row=next(s[3][0] for s in self.submissions if s[:3]==('yer','E1','r1'))
        del row['slots']['2']
        with self.assertRaisesRegex(ValueError,'Incorrect slot'):
            self.result()

    def test_24_invalid_call_rejected(self):
        self.submissions[0][3][0]['letters']='yes'
        with self.assertRaisesRegex(ValueError,'Invalid BSB'):
            self.result()

    def test_25_bad_usage_rejected(self):
        for value in (-1,float('nan'),True,1.5):
            with self.subTest(value=value),self.assertRaises(ValueError):
                scorer.parse_usage({'bsb/E1/r1':{'total_tokens':value,'tool_uses':1,'duration_ms':1}})

    def test_26_unknown_usage_reader_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unknown usage'):
            self.result({('bsb','E1','r99'):dict(total_tokens=1,tool_uses=1,duration_ms=1)})

    def test_27_no_outputs_no_fake_agreement(self):
        self.submissions=[];a=self.arm(self.result(),'yer')
        self.assertIsNone(a['agreement_with_truth']['slots']['rate'])
        self.assertEqual(a['missing_slots'],2)

    def test_28_usage_list_format(self):
        records={'readers':[{'bed':'yer','arm':'E4','reader':'r1','total_tokens':0,'tool_uses':0,'duration_ms':0}]}
        self.assertEqual(scorer.parse_usage(records)[('yer','E4','r1')]['total_tokens'],0)

    def test_29_cli_real_assignment_partial_file(self):
        with tempfile.TemporaryDirectory(prefix='.test-',dir=ROOT) as tmp:
            tmp=Path(tmp);manifest=json.loads((ROOT/'MANIFEST.json').read_text());truth=json.loads((ROOT/'keys/truth.json').read_text())
            p=next(p for p in manifest['packs'] if p['bed']=='bsb' and p['arm']=='E1');iid=p['item_ids'][0]
            verdict=tmp/'reader.jsonl';verdict.write_text(json.dumps(truth['bsb'][iid])+'\n')
            output=tmp/'score.json'
            proc=subprocess.run([sys.executable,'-B',str(ROOT/'score.py'),'--verdict','bsb','E1','r1',str(verdict),'--output',str(output)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            result=json.loads(output.read_text());self.assertEqual(self.arm(result)['agreement_with_truth']['compared_items'],1)
            self.assertEqual(len(self.arm(result)['missing_items']),99)

    def test_30_invalid_confidence_slot_rejected(self):
        row=next(s[3][0] for s in self.submissions if s[:3]==('yer','E1','r1'));row['confidence']={'3':'high'}
        with self.assertRaisesRegex(ValueError,'Confidence keys'):
            self.result()


class GeometryTests(unittest.TestCase):
    def test_31_response_transform_inverted(self):
        import base64,struct
        transform={'type':5,'rows':3,'cols':3,'data':base64.b64encode(struct.pack('<9f',2,0,10,0,2,20,0,0,1)).decode()}
        page={'dimension':{'width':200,'height':200},'transforms':[transform]}
        inv,size=builder.frame(page,(100,100))
        node={'layout':{'boundingPoly':{'vertices':[{'x':30,'y':60},{'x':70,'y':100}]}}}
        self.assertEqual(builder.box(node,inv,size),[10,20,30,40])

    def test_32_crop_translation_scaling_and_clamp(self):
        self.assertEqual(builder.local_box([100,200,110,210],[100,200,120,220],(40,40),padding=0),[0,0,20,20])

    def test_33_response_frame_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'Unmapped'):
            builder.frame({'dimension':{'width':20,'height':10}},(10,10))


if __name__=='__main__':
    unittest.main(verbosity=2)
