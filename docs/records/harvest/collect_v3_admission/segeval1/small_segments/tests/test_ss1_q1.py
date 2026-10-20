"""Synthetic SS1 contract checks; no real inputs, image reads or network."""
import importlib.util
from pathlib import Path
import math
import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/ss1_q1.py'
spec = importlib.util.spec_from_file_location('ss1_q1', SCRIPT)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


@pytest.fixture
def rows():
    # Twenty rows, with deliberate equality boundaries, Unicode and missing x-height.
    dimensions = [(10,20),(20,20),(20,10),(15,10),(20,10),(30,10),(40,10),
                  (50,10),(60,10),(80,10),(100,10),(150,10),(200,10),(300,10),(500,10),
                  (10,25),(40,200),(200,40),(201,40),(50,50)]
    texts = [('12',True),('Α2',False),('AB2',False),('ABC2',False),('  ',False),
             ('Ⅻ',True),('١β',False),('hello',False),('123IV',False),('12€',True)]*2
    result=[]
    for i,((w,h),(text,numeric)) in enumerate(zip(dimensions,texts)):
        r=dict(row_id=f'r{i}',crop_sha256=f'hash{i}',width_px=w,height_px=h,characters=i,
               text_characters=len(text.strip()),raw_text=text,xheight_px=None if i==1 else 0 if i==0 else 10)
        r.update(s.rotation(w,h));r.update(s.xheight(r['xheight_px'],r['L'],r['S']))
        r['chars']=s.chars(r);r['output_type']=s.output_type(text,numeric)
        result.append(r)
    return pd.DataFrame(result)


def test_rotation(rows):
    assert rows.rotated[:3].tolist()==[True,False,False]
    assert rows.L[:3].tolist()==[20,20,20]
    assert rows.S[:3].tolist()==[10,20,10]
    assert rows.A[:3].tolist()==[2,1,2]
    assert rows.unrotated_w_over_h[:3].tolist()==[.5,1,2]
    assert rows.chars.tolist()==list(range(20))
    assert rows.iloc[0].text_characters==2  # does not replace saved chars=0


@pytest.mark.parametrize('edge',s.A_EDGES[:-1])
def test_aspect_edges(edge):
    label=s.bucket(edge,s.A_EDGES)
    i=s.A_EDGES.index(edge)
    assert label==(f'≤{edge:g}' if i==0 else f'({s.A_EDGES[i-1]:g}, {edge:g}]')
    assert s.bucket(edge+1e-7,s.A_EDGES)!=label


def test_reason_categories():
    cases=[('KEEP','anything','KEEP'),
           ('DROP','Too little OCR output for the text box after height normalisation.','DROP_too_little'),
           ('DROP','Too much OCR output for the text box after height normalisation.','DROP_too_much'),
           ('UNCERTAIN','The detector returned no row with observed support.','UNC_no_row'),
           ('UNCERTAIN','No supported row.','UNC_no_row'),
           ('UNCERTAIN','No detected row.','UNC_no_row'),
           ('DROP','A second complete printed line is visible.','DROP_second_line'),
           ('DROP','More than 2 complete neighbouring words are visible.','DROP_neighbour_words'),
           ('DROP','Top and bottom padding together exceed 1.5 target-line heights.','DROP_padding'),
           ('UNCERTAIN','No usable text box was measured.','UNC_no_usable_text_box'),
           ('UNCERTAIN','The complete neighbouring-word count or line extent is unresolved.','UNC_neighbour_extent_unresolved'),
           ('UNCERTAIN','The reading direction remains unresolved.','UNC_reading_direction_unresolved')]
    for verdict,reason,category in cases:
        assert s.reason_category(verdict,reason)==category
        assert s.box_fail(category)==(category in {'DROP_too_little','DROP_too_much','UNC_no_row'})
    unknown=s.reason_category('UNCERTAIN','An unexpected reason!')
    assert unknown.startswith('UNC_an_unexpected_reason_')
    assert unknown!=s.reason_category('UNCERTAIN','An unexpected reason?')
    assert not s.box_fail(unknown)


def test_types_and_xh(rows):
    assert rows.output_type[:10].tolist()==['numeric','mixed','mixed','nonnumeric','nonnumeric',
                                           'numeric','mixed','nonnumeric','mixed','numeric']
    assert rows.xh_usable[:3].tolist()==[False,False,True]
    assert pd.isna(rows.L_xh[0]) and pd.isna(rows.L_xh[1])
    assert rows.L_xh[2]==2 and rows.S_xh[2]==1
    assert s.wave_group('W1')==s.wave_group('W2')=='collect_v3'
    assert s.wave_group('w1')==s.wave_group(None)=='v2'


def test_candidates(rows):
    defs={d[0]:d for d in s.candidate_definitions()}
    assert len(defs)==45
    c1=s.candidate_membership(rows,defs['C1_chars_le_3'])
    c2=s.candidate_membership(rows,defs['C2_A_le_2'])
    c6=s.candidate_membership(rows,defs['C6_chars_le_3_A_le_2'])
    c7=s.candidate_membership(rows,defs['C7_chars_le_3_A_le_3'])
    assert c1.tolist()==[i<=3 for i in range(20)]
    assert c2.tolist()==[max(w,h)/min(w,h)<=2 for w,h in zip(rows.width_px,rows.height_px)]
    assert c6.equals(c1|c2)
    assert c7.tolist()==[i<=3 and a<=3 for i,a in zip(rows.chars,rows.A)]
    c4=s.candidate_membership(rows,defs['C4_L_xh_le_3'])
    assert not c4[0] and not c4[1] and c4[2]
    # Rotated C5 accepts both orientations; chars boundary is inclusive.
    fixture=rows.iloc[[16,17]].copy();fixture['chars']=10
    assert s.candidate_membership(fixture,defs['C5_S_le_40_L_le_200_chars_le_10']).all()


def test_owner_join(rows):
    records=[dict(set='O_marks',line_id='r0'),dict(set='O_ratings',line_id='r0'),
             dict(set='O_marks',line_id='missing'),dict(set='O_ratings',line_id='alias',crop_sha256='hash1')]
    joined,stats=s.join_records(rows,records)
    assert [r['census_index'] for r in joined]==[0,0,None,1]
    assert stats['O_marks']['matched']==1 and stats['O_marks']['unmatched_ids']==['missing']
    assert stats['O_ratings']['by_line_id']==1 and stats['O_ratings']['by_crop_sha256']==1
    assert joined[-1]['join_method']=='crop_sha256'
    assert len({r['census_index'] for r in joined if r['census_index'] is not None})==2
    assert s.owner_class('KEEP')==s.owner_class('ACCEPTED')==s.owner_class('GOOD-like')=='good'
    assert s.owner_class('DROP')==s.owner_class('REJECTED')==s.owner_class('BAD-like')=='bad'
    assert s.owner_class('unknown')==s.owner_class('good bad')=='other'
    assert s.owner_bad_box('Wrong BOX') and not s.owner_bad_box('padding')


def test_empty_breaks():
    result=s.breaks(pd.DataFrame({'category':[],'box_fail':[]}))
    assert result['n']==0 and result['n_lt_30'] and result['pct_box_fail'] is None


def test_char_buckets():
    upper=[1,2,3,4,5,9,15]
    assert [s.char_bucket(x,upper) for x in [0,1,5,6,9,10,15,16]]==['≤0','1','5','6–9','6–9','10–15','10–15','16+']
