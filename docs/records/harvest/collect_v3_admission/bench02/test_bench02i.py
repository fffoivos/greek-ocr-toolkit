"""Ruled fair caps, receipt integrity, deterministic emission and cap selection."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import tempfile
import unittest
import bench02_draw as b
from test_bench02_draw import population, decision
from run_ruled_draw import below


class Bench02ITests(unittest.TestCase):
    def test_fair_allocation_three_classes_and_caps(self):
        ec,sc=Counter(),Counter();selected=[];classes=b.PRECEDENCE[:3]
        for cl in classes:
            p=population(30,cl)
            for r in p:
                r.update(edition_id='one',series='one',row_id=cl+r['row_id'])
            chosen=b.round_robin(p,'test',cl,30,ec,sc,edition_cap=12,series_cap=36)
            self.assertEqual(12,len(chosen))
            selected.extend(dict(r,**{'class':cl}) for r in chosen)
        fair=list(b.fair_order(selected))
        self.assertEqual(list(classes)*12,[r['class'] for r in fair])
        self.assertEqual([12]*3,sorted(ec.values()))
        self.assertEqual(fair,list(b.fair_order(selected)))

    def test_fair_multiple_editions_and_short_supply(self):
        selected=[]
        for cl,n in zip(b.PRECEDENCE[:3],(1,3,4)):
            for eid in ('b','a'):
                selected += [dict(edition_id=eid,**{'class':cl},row_id=f'{eid}-{cl}-{i}') for i in range(n)]
        fair=list(b.fair_order(selected));byedition=defaultdict(list)
        for r in fair:byedition[r['edition_id']].append(r['class'])
        expected=list(b.PRECEDENCE[:3])+list(b.PRECEDENCE[1:3])*2+[b.PRECEDENCE[2]]
        for rr in byedition.values():self.assertEqual(expected,rr)
        self.assertEqual(len(selected),len(fair))

    def test_receipt_sha_match_mismatch_and_argument(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            tags=Path(td)/'tags.jsonl.gz';tags.write_bytes(b'abc')
            receipt=tags.with_suffix('.receipt.json');actual=b.sha(tags)
            receipt.write_text(json.dumps(dict(tags_sha256=actual,tags_bytes=3)))
            self.assertEqual('receipt',b.verify_tags(tags,require_receipt_sha=True)['verified_against'])
            with self.assertRaisesRegex(ValueError,'mismatch'):b.verify_tags(tags,'0'*64)
            tags.write_bytes(b'abd')
            with self.assertRaisesRegex(ValueError,'mismatch'):b.verify_tags(tags)
            receipt.write_text('{}')
            with self.assertRaisesRegex(ValueError,'required'):b.verify_tags(tags,require_receipt_sha=True)
            self.assertEqual('argument',b.verify_tags(tags,b.sha(tags))['verified_against'])
            with self.assertRaisesRegex(ValueError,'mismatch'):b.verify_tags(tags,actual)

    def test_extract_receipt_tags_sha_and_bytes(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td);d=td/'d.jsonl';d.write_text(b.canonical(decision())+'\n')
            tags=td/'tags.jsonl.gz';rec=b.extract([d],[],tags)
            self.assertEqual(b.sha(tags),rec['tags_sha256'])
            self.assertEqual(tags.stat().st_size,rec['tags_bytes'])
            self.assertEqual('receipt',b.verify_tags(tags,require_receipt_sha=True)['verified_against'])

    def test_cap_choice_and_no_supply_rule(self):
        self.assertEqual(['dev:low'],below(dict(classes={'test:empty':dict(supply=0,credited=0,quota=100),
            'test:edge':dict(supply=1,credited=90,quota=100),'dev:low':dict(supply=1,credited=89,quota=100)})))
        payload=json.loads((b.HERE/'sweep/cap_choice.json').read_text())
        expected=next((r['cap'] for r in payload['evaluations'] if not r['below90']),50)
        self.assertEqual(expected,b.DEFAULT_EDITION_CAP)
        self.assertEqual([12,25,50],[r['cap'] for r in payload['evaluations']])
        self.assertEqual(99,payload['pool']['included_forced_editions'])
        for result in (payload['dry'],payload['upper_bound']):
            for v in result['classes'].values():
                self.assertEqual(min(v['quota'],v['drawn']),v['credited'])
                self.assertGreaterEqual(v['top_edition_share'],0)
                self.assertLessEqual(v['top_edition_share'],1)
                self.assertEqual(v['editions']>=10 and v['sources']>=3,v['diversity_pass'])

    def test_draw_fair_default_and_receipt_failure_before_output(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td)
            def write(name,rr):
                path=td/name;path.write_text(''.join(b.canonical(r)+'\n' for r in rr));return path
            rr=[]
            for cl,feature in (('vertical_turned',dict(turn_cw=90,source_width=100,source_height=20)),
                ('font_extremes',dict(xheight_px=8)),('degraded',dict(confidence=.1))):
                for i in range(60):rr.append(b.slim(decision(f'{cl}-{i}'),dict(source='s',**feature)))
            tags=write('tags.jsonl',rr)
            split=write('split.jsonl',[dict(parent_id=r['parent_id'],row_id=r['row_id'],edition_id='one',split='test') for r in rr])
            ed=write('ed.jsonl',[dict(edition_id='one')]);fs=[write(f'f{i}.jsonl',[]) for i in range(2)]
            vs=[write(f'v{i}.jsonl',[]) for i in range(3)]
            manifest=td/'manifest.json';manifest.write_text('{"classes":{}}')
            args=dict(tags_path=tags,split_path=split,edition_paths=[ed],features=fs,v2_paths=vs,manifest=manifest)
            counts=b.draw(**args,dest=td/'out')
            drawn=list(b.rows(td/'out/candidates.jsonl'))
            # 180 admitted rows, 120 missing confidence: ceil(.05 * 180) = 9 relative.
            self.assertEqual([50,50,9],[sum(r['class']==cl for r in drawn) for cl in b.PRECEDENCE[:3]])
            # Remaining former absolute-degraded rows now fall through to polytonic.
            self.assertEqual(50,counts['classes']['test:polytonic']['drawn'])
            self.assertEqual([9,50,50,50],sorted(counts['edition_counts'].values()))
            self.assertEqual(list(b.fair_order(drawn)),drawn)
            receipt=tags.with_suffix('.receipt.json');receipt.write_text('{"tags_sha256":"invalid"}')
            with self.assertRaisesRegex(ValueError,'mismatch'):b.draw(**args,dest=td/'bad')
            self.assertFalse((td/'bad').exists())

    def test_production_wrapper_requires_receipt_sha(self):
        text=(b.HERE/'run_census05_draw.sh').read_text()
        self.assertIn('--require-receipt-sha',text)
        self.assertNotIn('--edition-cap',text)
        self.assertNotIn('--pool-include-forced',text)


if __name__=='__main__':unittest.main()
