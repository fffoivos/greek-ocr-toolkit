"""S5 case, body-band and independent owner-crop regression checks."""
import json
from pathlib import Path
import pytest
from greekocr.labelfix import case
from greekocr.labelfix.reading import read_line_details
from greekocr.labelfix.markshape import load_model
from greekocr.labelfix.ctc_align import Alignment
from tests.labelfix.test_s4 import ink_components
R=Path(__file__).parents[2];F=R/'tests/data/labelfix_s4'

@pytest.mark.parametrize('lid,capitals,counts',[
 ('177b717d-p000013-l0009',['Η'],[2]),
 ('51fe7386-p000024-l0015',['Ο','Ο','Ο'],[1,2,2]),
])
def test_owner_capitals_have_pixel_case_and_side_marks(lid,capitals,counts):
 r=next(r for r in json.loads((F/'cases.json').read_text()) if r['line_id']==lid)
 out=read_line_details(F/(lid+'.png'),r['recogniser_text'],Alignment.from_record(r['alignment']),load_model(R/'docs/records/labelfix/markshape_model_S4.json'))
 ss=[s for s in out.slots if s['base'] in capitals]
 assert [s['base'] for s in ss]==capitals
 assert [len(s['evidence'].above) for s in ss]==counts
 assert all(s['case_class']=='capital' and s['evidence'].band_source=='capital_height' for s in ss)
 assert all('case_disagreement' in s for s in ss)
 # The owner-requested Ἦ/Ὅ naming is measured independently; these tests
 # establish physical detection without converting recogniser marks to truth.


def test_delta_lambda_cannot_gain_side_marks_or_set_word_body_band():
 ci=ink_components([((10,8,24,40),'letter'),((40,8,54,40),'letter'),((65,20,79,40),'letter'),((82,20,96,40),'letter'),((1,10,8,18),'mark')])
 ss=[dict(base=b,start=i,end=i+1,component=c,component_ids=[c.index],word_index=0) for i,(b,c) in enumerate(zip('δλαο',ci.components))]
 case.prepare(ci,ss)
 assert all(s['case_class']!='capital' for s in ss[:2])
 from greekocr.labelfix.ink import mark_evidence
 assert not mark_evidence(ci,10,24,base_letter='δ',certified_body=(10,24)).above
 assert all(s['height_band']['source']=='word_lowercase_bodies' for s in ss)


def test_theta_owner_line_has_own_cap_height_and_next_vowel_grave():
 f=R/'tests/data/labelfix_s5/theta.json';r=json.loads(f.read_text())
 out=read_line_details(f.with_suffix('.png'),r['recogniser_text'],Alignment.from_record(r['alignment']),load_model(R/'docs/records/labelfix/markshape_model_S4.json'))
 assert out.text.startswith('Θὰ')
 assert out.slots[0]['case_class']=='capital'
 assert not out.slots[0]['evidence'].above
 assert 'grave' in out.slots[1]['parts']
 assert out.slots[1]['height_band']['source']!='capital_run'
