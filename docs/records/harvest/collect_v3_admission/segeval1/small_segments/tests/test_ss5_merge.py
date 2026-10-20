"""SS5 merge integrity, frozen expectations, selection and rendered artifacts."""
import copy, importlib.util, math, random, sys, unittest
from pathlib import Path
SS=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ss5_merge',SS/'tools/ss5_merge.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SS5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample=m.rows(m.Q/'sample.jsonl');cls.key=m.read(m.Q/'keys/type2.json');cls.opus=m.rows(m.Q/'key_opus.jsonl')
        cls.report=m.read(m.Q/'AGREEMENT.json');cls.unavailable=cls.report['unavailable_contexts']
        cls.mapped={c:m.rows(m.Q/f'answers/{c}.mapped.jsonl') for c in cls.key['contexts'] if c not in cls.unavailable}
        cls.typed=m.rows(m.Q/'typing.jsonl')
    def merge(self,sample=None,mapped=None):return m.merge(self.sample if sample is None else sample,self.key,self.mapped if mapped is None else mapped,self.opus,self.unavailable)
    def test_missing_and_duplicate_sample_line_ids_refused(self):
        for sample in [self.sample[:-1],self.sample+[self.sample[0]], [dict(self.sample[0],line_id=None)]+self.sample[1:]]:
            with self.assertRaises(ValueError):self.merge(sample=sample)
    def test_missing_duplicate_and_wrong_answer_line_ids_refused(self):
        ctx=next(iter(self.mapped))
        for mode in ('missing','duplicate','wrong'):
            mm=copy.deepcopy(self.mapped)
            if mode=='missing':mm[ctx].pop()
            elif mode=='duplicate':mm[ctx][1]['line_id']=mm[ctx][0]['line_id']
            else:mm[ctx][0]['line_id']='unknown'
            with self.assertRaises(ValueError):self.merge(mapped=mm)
    def test_controls_excluded_and_sample_fields_preserved(self):
        controls={i['line_id'] for i in self.key['items'].values() if i['control']}
        self.assertEqual(len(self.typed),417);self.assertFalse(controls & {r['line_id'] for r in self.typed})
        sample={r['line_id']:r for r in self.sample}
        for r in self.typed:
            for k,v in sample[r['line_id']].items():self.assertEqual(r['sample_rotated'] if k=='rotated' else r[k],v)
        self.assertEqual(self.typed,self.merge())
    def test_opus_mapping_complete_or_explicitly_listed(self):
        present={r['type'] for r in self.opus}; self.assertEqual(present-set(m.MAP),set(self.report['unmapped_opus_types']))
        for r in self.typed:
            if 'opus_type' in r:self.assertEqual(r['opus_type'],m.MAP.get(r['opus_type_original'],r['opus_type_original']))
        expected=[r for r in self.typed if r['stratum']=='opus' and r['type'] is not None]
        self.assertEqual(self.report['compared_rows'],len(expected))
        self.assertEqual(sum(sum(v.values()) for v in self.report['confusion_matrix'].values()),len(expected))
    def test_groups_disjoint_complete_A_B_and_seeded_C(self):
        gs=m.groups(self.typed);self.assertEqual(gs,m.groups(self.typed))
        sets={g:{r['line_id'] for r in rs} for g,rs in gs.items()}
        self.assertFalse(sets['A']&sets['B'] or sets['A']&sets['C'] or sets['B']&sets['C'])
        self.assertEqual(sets['A'],{r['line_id'] for r in self.typed if r['type'] in m.A_TYPES or r['text'] in ('unreadable','not_text')})
        self.assertEqual(sets['B'],{r['line_id'] for r in self.typed if r['line_id'] not in sets['A'] and r.get('opus_type') is not None and r['type'] is not None and r['type']!=r['opus_type']})
        rest=sorted((r for r in self.typed if r['line_id'] not in sets['A']|sets['B']),key=lambda r:r['line_id'])
        self.assertEqual(gs['C'],random.Random(20261019).sample(rest,math.ceil(len(rest)/10)))
        self.assertEqual(gs['C'],m.groups(list(reversed(self.typed)))['C'])
    def test_controls_rescored_with_v1_key_and_amendments(self):
        for version,path in [('v1','LEAD_CONTROLS.v1.json'),('amended','LEAD_CONTROLS.json')]:
            expectations=m.read(m.Q/path)['controls']
            for ctx,rr in self.mapped.items():
                self.assertEqual(self.report['controls'][ctx][version],m.score(rr,expectations))
                for r in rr:
                    if r['control'] and version=='v1':self.assertEqual(self.key['items'][r['card_id']]['expected'],expectations[r['line_id']])
        self.assertEqual(self.report['flagged_contexts'],[ctx for ctx,v in self.report['controls'].items() if v['amended']['error_count']>1])
    def test_eye_index_geometry_and_nearest_pixels(self):
        gs=m.groups(self.typed);index=m.rows(m.Q/'eye_index.jsonl');geometry=m.rows(m.Q/'eye_geometry.jsonl')
        expected=[(g,r['line_id']) for g,rr in gs.items() for r in rr]
        self.assertEqual([(r['group'],r['line_id']) for r in index],expected)
        self.assertEqual(len({r['line_id'] for r in index}),len(index))
        typed={r['line_id']:r for r in self.typed}; bysheet={}
        for i,r in enumerate(index):
            self.assertEqual(r['sheet'],f'eye_{i//8+1:03}.png'); self.assertEqual(r['index'],i%8+1)
            bysheet.setdefault(r['sheet'],[]).append(geometry[i])
        for sheet,gg in bysheet.items():
            with m.Image.open(m.Q/'eye_sheets'/sheet) as im:
                y=0
                for r in gg:
                    w,h=r['rendered_size'];self.assertLessEqual(w,900);self.assertLessEqual(h,200);self.assertLessEqual(r['scale'],4)
                    self.assertEqual(im.getpixel((20,y+10)),(255,0,0))
                    with m.Image.open(typed[r['line_id']]['crop_path']) as source:
                        expected=source.convert('RGB').resize((w,h),m.Image.Resampling.NEAREST)
                        self.assertEqual(im.crop((21,y+11,21+w,y+11+h)).tobytes(),expected.tobytes())
                    y+=228+26*r['label_lines']+18
                self.assertEqual(im.size,(940,y))
if __name__=='__main__':unittest.main(verbosity=2)
