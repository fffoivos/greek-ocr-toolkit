"""Run with python3 -B -m unittest discover -s <bench02> -v (stdlib only)."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from collections import Counter
import bench02_draw as b

SAMPLE=Path.home()/'Projects/collect-v3-data/census02_sample'


def decision(i='r', parent='collect-v3-W1-20261018-0524'):
    return dict(binding=dict(id=i,parent_id=parent,crop_sha256='a'*64),admitted=True,
        disposition='ADMIT',reasons=[],final_text='Αβγ',expectations=dict(orthography='polytonic',scripts=['greek'],languages=['Greek']),
        final_inventory=dict(greek_letters=3,latin_letters=0,cyrillic_letters=0,letter_count=3,characters=3,mixed_words=[]))


def population(n=400, cls='latin', side='test'):
    return [dict(parent_id='p',row_id=f'r{i:05}',source=f's{i%4}',edition_id=f'{side}-e{i//2}',
        series=f'{side}-series{i//20}',primary_class=cls,split=side,tags={cls:True},
        crop_sha256='a'*64,final_text='abc',language=('ru','sr','bg','uk')[i%4],font_size=('small','large')[i%2]) for i in range(n)]


class DrawTests(unittest.TestCase):
    def test_determinism_and_input_permutation(self):
        p=population()
        a=b.round_robin(p,'test','latin',192,Counter(),Counter())
        z=b.round_robin(list(reversed(p)),'test','latin',192,Counter(),Counter())
        self.assertEqual(a,z)
        self.assertEqual(192,len(a))

    def test_overdraw_for_every_class_both_splits(self):
        for side in ('test','dev'):
            for cl,q in b.QUOTAS.items():
                quota=q if side=='test' else q//4
                subs=b.subgroup_quotas(side,cl)
                target=sum(__import__('math').ceil(1.2*v) for v in subs.values()) if subs else __import__('math').ceil(1.2*quota)
                group='language' if cl=='modern_cyrillic' else 'font_size' if cl=='font_extremes' else None
                chosen=b.round_robin(population(2000,cl,side),side,cl,target,Counter(),Counter(),group)
                self.assertEqual(target,len(chosen),(side,cl))

    def test_caps_per_class_across_classes(self):
        ec,sc=Counter(),Counter()
        p=population(1000)
        a=b.round_robin(p,'test','latin',192,ec,sc)
        z=b.round_robin(p,'test','polytonic',192,ec,sc)
        self.assertTrue(a and z)
        self.assertLessEqual(max(ec.values()),b.DEFAULT_EDITION_CAP)
        self.assertLessEqual(max(sc.values()),3*b.DEFAULT_EDITION_CAP)

    def test_source_then_edition_round_robin(self):
        p=population(80)
        for r in p:r['series']=None
        a=b.round_robin(p,'test','latin',12,Counter(),Counter())
        self.assertEqual(4,len({r['source'] for r in a[:4]}))
        for s in {r['source'] for r in a}:
            es=[r['edition_id'] for r in a if r['source']==s]
            self.assertEqual(len(es),len(set(es)))

    def test_caps_with_single_edition(self):
        p=population(40)
        for r in p:r['edition_id']='one';r['series']='one'
        self.assertEqual(min(40,b.DEFAULT_EDITION_CAP),len(b.round_robin(p,'test','latin',40,Counter(),Counter())))

    def test_subquota_no_language_substitution(self):
        p=population(800)
        for r in p:r['language']='ru'
        a=b.round_robin(p,'test','modern_cyrillic',192,Counter(),Counter(),'language')
        self.assertEqual(48,len(a))

    def test_fonts_equal(self):
        a=b.round_robin(population(800),'test','font_extremes',120,Counter(),Counter(),'font_size')
        self.assertEqual(Counter(small=60,large=60),Counter(r['font_size'] for r in a))

    def test_primary_unique_and_precedence(self):
        r=b.slim(decision(),dict(source='bsb_poly1850',primary_class='poly1850',xheight_px=8))
        t=b.tag(r)
        self.assertTrue(t['tags']['poly_dictionary_journal'])
        self.assertEqual('font_extremes',t['primary_class'])
        self.assertIsInstance(t['primary_class'],str)

    def test_numeric_and_noncell_need_evidence(self):
        d=decision();d['final_text']='12';d['final_inventory'].update(greek_letters=0,letter_count=0,characters=2)
        r=b.slim(d)
        self.assertEqual('unavailable',b.tag(r)['tags']['numeric_cells'])
        self.assertEqual('unavailable',b.tag(r)['tags']['short'])
        r['evidence'].update(cell_flag=True,A=2)
        self.assertEqual('numeric_cells',b.tag(r)['primary_class'])
        r['evidence']['cell_flag']=False
        self.assertTrue(b.tag(r)['tags']['short'])

    def test_no_proxy_for_missing_physical_evidence(self):
        r=b.slim(decision(),dict(xheight=8,tall_box=True,density_ratio=.01,confidence=.1))
        t=b.tag(r)['tags']
        for k in ('font_extremes','curved_skewed','vertical_turned'):
            self.assertEqual('unavailable',t[k])
        self.assertTrue(t['degraded'])  # BENCH02F: confidence .1 is direct evidence.

    def test_missing_inventory_is_unavailable(self):
        d=decision();d['final_inventory']={}
        t=b.tag(b.slim(d))['tags']
        for k in ('monotonic','polytonic','latin','greek_latin','historical_russian','modern_cyrillic'):
            self.assertEqual('unavailable',t[k])

    def test_quota_table_total(self):
        self.assertEqual(16,len(b.QUOTAS))
        self.assertEqual(2460,sum(b.QUOTAS.values()))
        self.assertEqual(615,sum(v//4 for v in b.QUOTAS.values()))

    def test_curves_physical_measurements(self):
        d=decision();d['stages']=[dict(stage='segmentation',result=dict(evidence=dict(detected_rows=[dict(side='main',curves=dict(base=[[0,20],[100,25]],mean=[[0,12],[100,17]]))]),frame=dict(normalization_cw=0,source_width=110,source_height=30)))]
        r=b.slim(d);t=b.tag(r)
        self.assertEqual(8,r['evidence']['xheight_px'])
        self.assertTrue(t['tags']['curved_skewed'])
        self.assertFalse(t['tags']['vertical_turned'])

    def test_greek_latin_requires_expected_scripts(self):
        d=decision();d['final_inventory']['latin_letters']=3
        self.assertFalse(b.tag(b.slim(d))['tags']['greek_latin'])
        d['expectations']['scripts'].append('latin')
        self.assertTrue(b.tag(b.slim(d))['tags']['greek_latin'])
        d['final_inventory']['mixed_words']=['abcΑβ']
        self.assertFalse(b.tag(b.slim(d))['tags']['greek_latin'])

    def test_write_guard_and_symlink(self):
        with self.assertRaises(ValueError):b.output(b.HERE.parent/'forbidden')
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            p=Path(td)/'escape';p.symlink_to(b.HERE.parent,target_is_directory=True)
            with self.assertRaises(ValueError):b.dump(p/'forbidden',{})

    def test_extract_sample_matches_in_memory(self):
        decisions=[SAMPLE/f'decisions_{w}_2000.jsonl.gz' for w in ('W1','W2')]
        diagnostics=[SAMPLE/f'evaluation_diagnostics_{w}_2000.jsonl.gz' for w in ('W1','W2')]
        if not all(p.exists() for p in decisions+diagnostics):self.skipTest('local sample absent')
        f={b.key(r['decision']):r['row'] for p in diagnostics for r in b.rows(p)}
        expected=[]
        for p in decisions:
            for d in b.rows(p):
                r=b.slim(d,f[b.key(d)]);expected.append(r)
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            out=Path(td)/'tags.jsonl.gz';receipt=b.extract(decisions,diagnostics,out)
            self.assertEqual(4000,receipt['joined'])
            self.assertEqual(1,receipt['decision_join_rate'])
            self.assertEqual(expected,list(b.rows(out)))
            first=out.read_bytes();b.extract(decisions,diagnostics,out)
            self.assertEqual(first,out.read_bytes())

    def test_extract_unordered_partial_join_and_non_w12(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td);ds=[decision('a'),decision('b'),decision('c',parent='v2')]
            (td/'d.jsonl').write_text(''.join(b.canonical(d)+'\n' for d in ds))
            (td/'e.jsonl').write_text(b.canonical(dict(decision=ds[1],row=dict(source='x')))+'\n')
            rec=b.extract([td/'d.jsonl'],[td/'e.jsonl'],td/'tags.gz')
            self.assertEqual(2,rec['decisions']);self.assertEqual(.5,rec['decision_join_rate'])
            self.assertEqual(['unavailable','x'],[b.tag(r)['source'] for r in b.rows(td/'tags.gz')])

    def test_end_to_end_split_exclusions_and_admission(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td)
            def write(name,rr):
                p=td/name;p.write_text(''.join(b.canonical(r)+'\n' for r in rr));return p
            tags=[];split=[];editions=[]
            for i,side in enumerate(('test','dev','train','test','test','test')):
                d=decision(str(i));d['expectations']['orthography']='monotonic'
                if i==5:d.update(admitted=False,reasons=[dict(reason=b.REASON)])
                r=b.slim(d,dict(source='s'));r.update(b.tag(r));tags.append(r)
                split.append(dict(parent_id=r['parent_id'],row_id=str(i),edition_id=f'e{i}',split=side))
                editions.append(dict(edition_id=f'e{i}',split=side,member_documents=[f'doc{i}'],leakage_matches=[dict(v2_doc='legacy')] if i==3 else []))
            t=write('tags.jsonl',tags);sp=write('split.jsonl',split);ed=write('ed.jsonl',editions)
            v=[write(f'v{i}.jsonl',[dict(id='legacy',doc='legacy')]) for i in range(3)]
            lock=td/'lock.txt';lock.write_text('4\n')
            manifest=td/'locks.json';manifest.write_text(b.canonical(dict(classes=dict(locked_eval=dict(file='lock.txt',sha256=b.sha(lock))))))
            fs=[write('W1.jsonl',[]),write('W2.jsonl',[])]
            out=td/'out';c=b.draw(t,sp,[ed],fs,v,manifest,out)
            drawn=list(b.rows(out/'candidates.jsonl'))
            self.assertEqual({'0','1'},{r['row_id'] for r in drawn})
            for r in drawn:self.assertEqual(split[int(r['row_id'])]['split'],r['split'])
            self.assertEqual({'e3','e4'},set(c['excluded_editions']))
            first=(out/'candidates.jsonl').read_bytes();b.draw(t,sp,[ed],fs,v,manifest,out)
            self.assertEqual(first,(out/'candidates.jsonl').read_bytes())
            dry=b.draw(t,sp,[ed],fs,v,manifest,td/'dry',True)
            self.assertEqual(1,dry['diagnostics']['pre_filter_supply'])
            self.assertEqual(['5'],[r['row_id'] for r in b.rows(td/'dry/candidates.jsonl')])

    def test_unavailable_series_is_diagnostic(self):
        self.assertIsNone(b.edition_series(dict(edition_id='abc')))
        self.assertIsNone(b.edition_series(dict(metadata=[dict(records=[dict(metadata=dict(journal='Journal'))])])))
        self.assertIsNone(b.edition_series(dict(gazette=True,series='Annual')))

    def test_sbatch_cpu_only(self):
        text=(b.HERE/'extract.sbatch').read_text()
        self.assertIn('#SBATCH --account=a0140',text)
        self.assertIn('#SBATCH --partition=normal',text)
        self.assertNotIn('#SBATCH --gpus',text)
        self.assertNotIn('#SBATCH --gres',text)

if __name__=='__main__':unittest.main()
