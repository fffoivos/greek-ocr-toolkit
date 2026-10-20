"""BENCH02H safety, cap, production-parity and full-sweep regression checks."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import bench02_draw as b
from test_bench02_draw import decision, population
import run_sweep as sweep


class Bench02HTests(unittest.TestCase):
    def test_default_cli_reproduces_ruled_v2_bytes(self):
        args=sweep.inputs()
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            cmd=[sys.executable,'-B',str(b.HERE/'bench02_draw.py'),'draw','--tags',str(args['tags_path']),
                '--split',str(args['split_path']),'--editions',*map(str,args['edition_paths']),
                '--features',*map(str,args['features']),'--v2',*map(str,args['v2_paths']),
                '--exclusions',str(args['manifest']),'--tags-sha256',__import__('run_ruled_draw').TAGS_SHA,'--dry-run','--output',td]
            # No new flags; the subprocess must remain offline as the module has no network calls.
            subprocess.run(cmd,check=True,capture_output=True)
            self.assertEqual((b.HERE/'census03/dryrun_v2/candidates.jsonl').read_bytes(),(Path(td)/'candidates.jsonl').read_bytes())
            self.assertEqual({'edition':b.DEFAULT_EDITION_CAP,'series':3*b.DEFAULT_EDITION_CAP,'scope':'per class x edition, including overdraw; series per class'},json.loads((Path(td)/'draw_plan.json').read_text())['caps'])

    def test_per_class_caps_every_sweep_value(self):
        p=population(4000)
        # Reuse editions in different strata, with enough rows to hit all finite limits.
        for i,r in enumerate(p):
            r['edition_id']=f'e{i%8}';r['series']=f'series{i%2}'
        for cap in sweep.CAPS:
            with self.subTest(cap=cap):
                ec,sc=Counter(),Counter();series=None if cap is None else 3*cap
                chosen=[]
                for cl in ('latin','polytonic'):
                    chosen+=b.round_robin(p,'test',cl,2000,ec,sc,edition_cap=cap,series_cap=series)
                self.assertEqual(4000 if cap is None else 12*cap,len(chosen))
                if cap is not None:
                    self.assertLessEqual(max(ec.values()),cap)
                    self.assertEqual(series,max(sc.values()))

    def test_locked_rows_and_pool_membership_all_modes(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td)
            def write(name,rr):
                p=td/name;p.write_text(''.join(b.canonical(r)+'\n' for r in rr));return p
            manifests={};tags=[];split=[];editions=[]
            for g in ('n1','lqb','lqb_extra','other','dev'):
                name={'n1':'n1_locked_eval','lqb':'lqb_truth_v1','lqb_extra':'lqb_truth_v1_1','other':'locked_eval','dev':'dev_locked_eval'}[g]
                lock=td/f'{g}.txt';lock.write_text(g+'_locked\n')
                manifests[name]=dict(file=lock.name,sha256=b.sha(lock),rule='never admitted to training')
                editions.append(dict(edition_id=g,forced=True,split='dev' if g=='dev' else 'test',leakage_matches=[{'locked':True}]))
                for suffix in ('locked','free'):
                    r=b.slim(decision(g+'_'+suffix),dict(source='s'))
                    r.update(admitted=False,reasons=[b.REASON]);tags.append(r)
                    split.append(dict(parent_id=r['parent_id'],row_id=r['row_id'],edition_id=g,split='dev' if g=='dev' else 'test'))
            manifest=td/'manifest.json';manifest.write_text(b.canonical(dict(classes=manifests)))
            args=dict(tags_path=write('tags.jsonl',tags),split_path=write('split.jsonl',split),
                edition_paths=[write('editions.jsonl',editions)],features=[write('w1.jsonl',[]),write('w2.jsonl',[])],
                v2_paths=[write(f'v{i}.jsonl',[]) for i in range(3)],manifest=manifest)
            cache={}
            for pool,expected in [('none',set()),('n1',{'n1_free'}),('lqb',{'lqb_free','lqb_extra_free'}),('both',{'n1_free','lqb_free','lqb_extra_free'})]:
                for upper in (False,True):
                    with self.subTest(pool=pool,upper=upper):
                        out=td/f'{pool}-{upper}'
                        b.draw(**args,dest=out,dry_run=not upper,upper_bound=upper,edition_cap=None,pool_include_forced=pool,_cache=cache)
                        fresh=td/f'fresh-{pool}-{upper}'
                        b.draw(**args,dest=fresh,dry_run=not upper,upper_bound=upper,edition_cap=None,pool_include_forced=pool)
                        self.assertEqual((fresh/'candidates.jsonl').read_bytes(),(out/'candidates.jsonl').read_bytes())
                        drawn=list(b.rows(out/'candidates.jsonl'))
                        self.assertEqual(expected,{r['row_id'] for r in drawn})
                        self.assertTrue(all(r['split']=='test' for r in drawn))

    def test_full_sweep_checks_and_accounting(self):
        payload=json.loads((b.HERE/'sweep/sweep.json').read_text())
        self.assertEqual(48,len(payload['runs']))
        self.assertEqual(48,len({(r['rule'],r['cap'],r['pool']) for r in payload['runs']}))
        self.assertTrue(payload['default_candidates_byte_identical'])
        self.assertEqual(0,payload['checks']['locked_row_intersections'])
        self.assertEqual(0,payload['checks']['cap_violations'])
        for r in payload['runs']:
            for s in ('test','dev'):
                cc=[v for k,v in r['classes'].items() if k.startswith(s+':')]
                self.assertEqual(r['splits'][s]['quota'],r['splits'][s]['credited']+sum(v['deficit'] for v in cc))
                self.assertEqual(16,len(cc))
                if r['cap'] is not None:self.assertLessEqual(r['splits'][s]['max_edition_lines'],r['cap'])
            # Forced pool changes cannot change dev selection (edition sets are disjoint).
            base=next(x for x in payload['runs'] if x['rule']==r['rule'] and x['cap']==r['cap'] and x['pool']=='none')
            self.assertEqual(base['splits']['dev'],r['splits']['dev'])

    def test_cap_parser(self):
        self.assertEqual(4,b.edition_cap_arg('4'))
        self.assertIsNone(b.edition_cap_arg('unlimited'))
        for v in ('0','-1','nan','1.5'):
            with self.assertRaises(__import__('argparse').ArgumentTypeError):b.edition_cap_arg(v)

    def test_subgroup_credit_remains_distinct(self):
        p=population(800)
        for r in p:r['language']='sr';r['series']=None
        chosen=b.round_robin(p,'test','modern_cyrillic',192,Counter(),Counter(),'language',None,None)
        self.assertEqual(48,len(chosen))


if __name__=='__main__':unittest.main()
