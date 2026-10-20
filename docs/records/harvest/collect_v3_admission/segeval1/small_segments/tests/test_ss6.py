"""SS6 acceptance checks using saved evidence; no reading/model execution."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

SS=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ss6_build',SS/'tools/ss6_build.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

class SS6(unittest.TestCase):
    def test_class_mapping_every_type(self):
        expected={'word':'legit_text','caps_display':'legit_text','abbrev_label':'legit_text','marker':'legit_text','roman_lower':'legit_text','digits_letters':'legit_text','number':'legit_text','punctuation':'printed_nonletter','foreign_script':'out_of_scope_script','handwriting':'non_text','watermark':'non_text','figure_ornament':'non_text','show_through':'non_text','noise':'non_text','cut_fragment':'segmentation_fault','multi_line':'segmentation_fault','part_of_line':'segmentation_fault','other':'other'}
        for t,cl in expected.items():
            self.assertEqual(b.classify(t,'ok'),cl,t)
            if t in b.LEGIT|{'punctuation'}:
                for crop in ['clipped','extra']:self.assertEqual(b.classify(t,crop),'segmentation_fault')
    def test_lead_precedence_and_all_real_rows(self):
        sol={'type':'word','text':'wrong','crop':'clipped'}
        lead={'type':'noise','text':'not_text','crop':'na','note':'saved correction'}
        self.assertEqual(b.final(sol,lead),{k:lead[k] for k in sol})
        self.assertEqual(b.final(sol,None),sol)
        typed={r['line_id']:r for r in b.jsonl(SS/'q3/typing.jsonl')}
        eye=b.load(SS/'q3/LEAD_EYE.json')
        rows=b.jsonl(SS/'samples.jsonl')
        for r in rows:
            if r['control']:continue
            wanted=eye['corrections'].get(r['line_id'],typed[r['line_id']])
            for key in ['type','text','crop']:self.assertEqual(r['final_'+key],wanted[key])
            self.assertEqual(r['label_ok'],wanted['text'] in ['match','minor'])
            self.assertEqual(r['final_class'],b.classify(wanted['type'],wanted['crop']))
    def test_group_order(self):
        expected='word caps_display abbrev_label marker roman_lower digits_letters number punctuation foreign_script handwriting watermark figure_ornament show_through noise cut_fragment multi_line part_of_line other'.split()
        self.assertEqual(b.ORDER,expected)
        manifest=b.load(SS/'sheet/card_manifest.json')
        self.assertEqual(manifest,sorted(manifest,key=lambda r:(expected.index(r['group']),not r['inside'],r['source'],r['line_id'])))
    def test_ids_unique_stable(self):
        manifest=b.load(SS/'sheet/card_manifest.json')
        ids=[r['doc_id'] for r in manifest]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(all(r['doc_id']=='smallseg:'+r['line_id'] for r in manifest))
        self.assertEqual({r['line_id'] for r in manifest},{r['line_id'] for r in b.jsonl(SS/'q3/typing.jsonl')})
        html=(SS/'sheet/small_segments_sheet.html').read_text()
        for i in ids:self.assertEqual(html.count('id="n-'+i+'"'),1)
    def test_samples_complete_and_controls(self):
        sample=b.jsonl(SS/'q3/sample.jsonl');rows=b.jsonl(SS/'samples.jsonl')
        self.assertEqual(len(rows),437)
        self.assertEqual([r['line_id'] for r in rows],[r['line_id'] for r in sample])
        controls=set(b.load(SS/'q3/AGREEMENT.json')['excluded_control_line_ids'])
        self.assertEqual({r['line_id'] for r in rows if r['control']},controls)
        self.assertEqual(sum(not r['control'] for r in rows),417)
        for r in rows:
            self.assertEqual(r['text'],r['raw_text'])
            self.assertEqual(r['class'],r['primary_class'])
            if r['control']:self.assertTrue(r['control_observations'])
    def test_tables_weights_and_counts(self):
        q=b.load(SS/'q3/q3.json')
        for g in q['T7'].values():
            for key in ['class','final_type']:self.assertEqual(sum(r['n'] for r in g[key]),g['n'])
        for rs in q['T8'].values():
            self.assertEqual(sum(r['n'] for r in rs),150)
            self.assertAlmostEqual(sum(r['weighted_share'] for r in rs),1)
            for r in rs:self.assertTrue(r['wilson95_unweighted'][0]-1e-12<=r['unweighted_share']<=r['wilson95_unweighted'][1]+1e-12)
        self.assertEqual(q['T13']['checked'],209)
        self.assertEqual(q['T13']['changed'],19)
    def test_versions_latest_and_crop_hashes(self):
        from html.parser import HTMLParser
        class Parser(HTMLParser):
            def __init__(self):super().__init__();self.cards=[];self.notes=[];self.images=0
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if tag=='div' and a.get('class')=='card':self.cards.append(a['data-tool'])
                if tag=='img':self.images+=1;self.assert_image=a['src'].startswith('data:image/')
                if tag=='textarea':self.notes.append(a['id'][2:])
        p=Parser();p.feed((SS/'sheet/small_segments_sheet.html').read_text());p.close()
        manifest=b.load(SS/'sheet/card_manifest.json');owners={r['line_id']:r for r in b.jsonl(SS/'q1/owner_joined.jsonl')};sample={r['line_id']:r for r in b.jsonl(SS/'q3/sample.jsonl')}
        self.assertEqual(p.images,417);self.assertEqual(len(p.cards),417)
        for m,tool in zip(manifest,p.cards):
            s=sample[m['line_id']];o=owners.get(m['line_id'],{})
            self.assertEqual(tool,o.get('verdict_08') or s['verdict_05'])
            self.assertEqual(b.sha(Path(s['crop_path'])),s['crop_sha256'])
    def test_google_profiles(self):
        self.assertTrue(b.text_profile('Ἄλφα')['letters_only'])
        self.assertTrue(b.text_profile('3η.')['digits_letters'])
        self.assertTrue(b.text_profile('...')['punctuation_only'])
        self.assertTrue(b.text_profile('字')['other_script'])
        self.assertTrue(b.text_profile('  ')['empty'])

if __name__=='__main__':unittest.main(verbosity=2)
