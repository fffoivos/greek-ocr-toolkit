"""Coordinator rulings, census_05 producer paths and absent-evidence regressions."""
from collections import Counter
import json
from pathlib import Path
import tempfile
import unittest
import bench02_draw as b
from test_bench02_draw import decision, population


class Bench02FTests(unittest.TestCase):
    def test_confidence_boundary(self):
        for confidence,expected in ((.88,True),(.89,False)):
            r=b.slim(decision(),dict(confidence=confidence))
            self.assertIs(expected,b.tag(r)['tags']['degraded'])
        self.assertEqual('unavailable',b.tag(b.slim(decision(),dict(degraded=True,density_ratio=.01)))['tags']['degraded'])

    def test_density_p25_per_source_and_strict_boundary(self):
        rr=[]
        for source,values in (('a',[0,4,8,12,16]),('b',[100,104,108,112,116])):
            for i,value in enumerate(values):
                d=decision(f'{source}{i}');d['admitted']=False
                rr.append(b.slim(d,dict(source=source,ink_density=value)))
        ps=b.density_percentiles(rr,{})
        self.assertEqual({'a':dict(p25=4,rows=5),'b':dict(p25=104,rows=5)},ps)
        for source,threshold in (('a',4),('b',104)):
            for density,expected in ((threshold-.01,True),(threshold,False)):
                r=b.slim(decision(),dict(source=source,ink_density=density,confidence=.89))
                self.assertIs(expected,b.tag(r,density_p25=ps[source]['p25'])['tags']['degraded'])
        self.assertEqual({},b.density_percentiles([b.slim(decision())],{}))

    def test_punctuation_threshold_and_leader_dash_paths(self):
        for text,expected in (('a b !',True),('abc!',False),('ab$',True),('   ',False)):
            d=decision();d['final_text']=text
            self.assertIs(expected,b.tag(b.slim(d))['tags']['punctuation_heavy'])
        for feature in (dict(leader_runs=['...']),dict(emdash_label_count=1)):
            self.assertTrue(b.tag(b.slim(decision(),feature))['tags']['punctuation_heavy'])
        d=decision();d['routes']=dict(dashes=dict(status='tag_only',evidence=dict(dashes=[dict(offset=1,character='—')])))
        r=b.slim(d)
        self.assertIs(True,r['evidence']['dash_tag'])
        self.assertTrue(b.tag(r)['tags']['punctuation_heavy'])
        self.assertTrue(b.tag(r)['tags']['leaders_dashes'])

    def test_dev_fonts_and_overdraw_no_substitution(self):
        self.assertEqual(dict(small=13,large=12),b.subgroup_quotas('dev','font_extremes'))
        chosen=b.round_robin(population(800),'dev','font_extremes',31,Counter(),Counter(),'font_size')
        self.assertEqual(Counter(small=16,large=15),Counter(r['font_size'] for r in chosen))
        p=population(800)
        for r in p:r['font_size']='large'
        chosen=b.round_robin(p,'dev','font_extremes',31,Counter(),Counter(),'font_size')
        self.assertEqual(15,len(chosen))

    def test_serbian_exact_document_ids_only(self):
        self.assertEqual({'cyrillic:7235f8d0','cyrillic:975289f3'},set(b.SERBIAN_DOCUMENTS))
        d=decision();d['final_inventory'].update(greek_letters=0,cyrillic_letters=3)
        d['expectations']=dict(scripts=['cyrillic'],orthography='modern',languages=[])
        for field in ('doc','book_id'):
            for doc in (*sorted(b.SERBIAN_DOCUMENTS),'cyrillic:unknown','cyrillic:7235f8d0-extra'):
                r=b.slim(d,{field:doc})
                expected='sr' if doc in b.SERBIAN_DOCUMENTS else None
                self.assertEqual(expected,b.tag(r)['language'])
        d['binding']['book_id']='cyrillic:975289f3'
        self.assertEqual('sr',b.tag(b.slim(d))['language'])

    def test_gate03_bbox_and_inventory_paths(self):
        d=decision();d['final_text']='12';d.pop('final_inventory')
        d['raw_inventory']=dict(greek_letters=0,latin_letters=0,cyrillic_letters=0,letter_count=0,characters=2,mixed_words=[],scripts={})
        for bbox,a,cell in (([0,0,60,10],6,True),([0,0,10,60],6,True),([0,0,61,10],6.1,False)):
            r=b.slim(d,dict(crop_bbox=bbox))
            self.assertEqual(a,r['evidence']['A']);self.assertIs(cell,r['evidence']['cell_flag'])
            self.assertIs(cell,b.tag(r)['tags']['numeric_cells'])
            self.assertIn('greek_letters',r['text_facets'])
            self.assertEqual({},r['text_facets']['observed_scripts'])
        r=b.slim(d,dict(crop_bbox=None))
        self.assertNotIn('A',r['evidence'])
        self.assertEqual('unavailable',b.tag(r)['tags']['numeric_cells'])

    def test_slim_numeric_fields_and_confidence_alias(self):
        r=b.slim(decision(),dict(docai_confidence=.88))
        self.assertEqual(.88,r['evidence']['confidence'])
        self.assertIsNone(r['evidence']['ink_density'])
        self.assertIsInstance(r['text_facets']['punctuation_share'],float)

    def test_missing_evidence_deficit_and_recorded_plan(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td)
            def write(name,rr):
                p=td/name;p.write_text(''.join(b.canonical(r)+'\n' for r in rr));return p
            d=decision();d['final_text']='12';d.pop('final_inventory')
            r=b.slim(d,dict(source='a'))
            tags=write('tags.jsonl',[r]);split=write('split.jsonl',[dict(parent_id=r['parent_id'],row_id=r['row_id'],edition_id='e',split='test')])
            ed=write('ed.jsonl',[dict(edition_id='e')]);fs=[write(f'f{i}.jsonl',[]) for i in range(2)]
            vs=[write(f'v{i}.jsonl',[]) for i in range(3)]
            m=td/'manifest.json';m.write_text('{"classes":{}}')
            counts=b.draw(tags,split,[ed],fs,vs,m,td/'out')
            self.assertEqual([],list(b.rows(td/'out/candidates.jsonl')))
            for cl in b.QUOTAS:self.assertEqual(b.QUOTAS[cl],counts['classes']['test:'+cl]['deficit'])
            plan=json.loads((td/'out/draw_plan.json').read_text())
            self.assertEqual(1,plan['degraded']['missing_confidence_count'])
            self.assertEqual(0,plan['degraded']['populations']['test|a']['flagged'])
            self.assertEqual(dict(small=13,large=12),plan['subquotas']['dev']['font_extremes'])
            self.assertEqual(31,counts['classes']['dev:font_extremes']['overdraw_target'])

            r['evidence'].update(ink_density=.2,confidence=.89)
            write('tags.jsonl',[r])
            b.draw(tags,split,[ed],fs,vs,m,td/'density')
            plan=json.loads((td/'density/draw_plan.json').read_text())
            self.assertEqual({'a':dict(p25=.2,rows=1)},b.density_percentiles([r],{}))
            self.assertEqual(1,plan['degraded']['populations']['test|a']['flagged'])
            self.assertNotIn('density_p25_by_source',plan['degraded'])
