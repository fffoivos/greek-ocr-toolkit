"""BENCH02K relative confidence populations and production draw regressions."""
import json
from pathlib import Path
import tempfile
import unittest
import bench02_draw as b
from test_bench02_draw import decision


class Bench02KTests(unittest.TestCase):
    def test_ceil_ties_split_source_missing_and_determinism(self):
        rr=[]; splits={}
        for side,source,n in (('test','a',21),('test','b',20),('dev','a',1)):
            for i in range(n):
                r=b.slim(decision(f'{side}-{source}-{i:02}'),dict(source=source,confidence=.95))
                rr.append(r);splits[b.key(r)]=dict(split=side)
        missing=b.slim(decision('missing'),dict(source='a',confidence=None))
        rr.append(missing);splits[b.key(missing)]=dict(split='dev')
        for rid,side,admitted,parent in (('train','train',True,'collect-v3-W1-x'),
                ('rejected','test',False,'collect-v3-W2-x'),('other','test',True,'v2')):
            r=b.slim(decision(rid,parent),dict(source='a',confidence=0))
            r['admitted']=admitted;rr.append(r);splits[b.key(r)]=dict(split=side)
        flagged,plan=b.relative_degraded(rr,splits)
        self.assertEqual({'test-a-00','test-a-01','test-b-00','dev-a-00'},{k[1] for k in flagged})
        self.assertEqual((flagged,plan),b.relative_degraded(list(reversed(rr)),splits))
        self.assertEqual(1,plan['missing_confidence_count'])
        self.assertEqual((set(),{}),(b.relative_degraded([],{} )[0],b.relative_degraded([],{} )[1]['populations']))
        self.assertEqual(21,plan['populations']['test|a']['population'])
        self.assertEqual(2,plan['populations']['test|a']['flagged'])
        tagged=b.tag(rr[0],relative_flag=True)
        self.assertEqual(b.DEGRADED_LABEL,tagged['tags']['degraded_label'])
        self.assertEqual('degraded',tagged['primary_class'])
        # Relative production ignores both absolute branches.
        r=b.slim(decision(),dict(confidence=.1,ink_density=0))
        self.assertFalse(b.tag(r,density_p25=1,relative_flag=False)['tags']['degraded'])

    def test_excluded_rows_ranked_never_drawn_and_labels(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as tmp:
            td=Path(tmp)
            def write(name,rr):
                p=td/name;p.write_text(''.join(b.canonical(r)+'\n' for r in rr));return p
            rr=[b.slim(decision(f'r{i:02}'),dict(source='s',confidence=.90+i*.001)) for i in range(41)]
            # Lowest two: one directly locked, one v2-blocked edition. Third is drawable.
            split=[dict(parent_id=r['parent_id'],row_id=r['row_id'],edition_id=f'e{i}',split='test') for i,r in enumerate(rr)]
            ed=[dict(edition_id=f'e{i}',leakage_matches=[{}] if i==1 else []) for i in range(41)]
            lock=td/'lock';lock.write_text('r00\n')
            manifest=td/'manifest';manifest.write_text(b.canonical(dict(classes=dict(locked_eval=dict(file='lock',sha256=b.sha(lock))))))
            args=dict(tags_path=write('tags',rr),split_path=write('split',split),edition_paths=[write('ed',ed)],
                features=[write('w1',[]),write('w2',[])],v2_paths=[write(f'v{i}',[]) for i in range(3)],manifest=manifest)
            counts=b.draw(**args,dest=td/'out')
            candidates=list(b.rows(td/'out/candidates.jsonl'))
            self.assertEqual({'r02'},{r['row_id'] for r in candidates if r['class']=='degraded'})
            self.assertFalse({'r00','r01'} & {r['row_id'] for r in candidates})
            self.assertEqual(b.DEGRADED_LABEL,counts['classes']['test:degraded']['label'])
            self.assertIn(b.DEGRADED_LABEL,(td/'out/COUNTS.md').read_text())
            self.assertEqual(3,json.loads((td/'out/draw_plan.json').read_text())['degraded']['populations']['test|s']['flagged'])
            b.draw(**args,dest=td/'again')
            for name in ('candidates.jsonl','counts.json','COUNTS.md','draw_plan.json'):
                self.assertEqual((td/'out'/name).read_bytes(),(td/'again'/name).read_bytes())
