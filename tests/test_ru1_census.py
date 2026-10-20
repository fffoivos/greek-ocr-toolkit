import sys
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
from ru1_census import positions,mask,prior,usable

def test_boundary_and_hyphen():
    p=positions('ъ ь aь въ домь, соль- соль-на пьеса')
    assert [(x['word'],x['kind']) for x in p]==[('въ','final'),('домь','final'),('соль','pre_hyphen'),('соль','pre_hyphen')]

def test_mask_both_signs_and_offsets():
    text='Онъ могъ взять соль-'
    masked,p=mask(text)
    assert masked=='Он⟦1⟧ мог⟦2⟧ взят⟦3⟧ сол⟦4⟧-'
    assert all(text[s['offset']]==s['google'] for s in p)

def test_historic_cyrillic():
    assert len(positions('ѣь іъ ѳь ѵъ'))==4
    assert [p['google'] for p in positions('ьъ ъь')]==['ъ','ь']
    assert positions('aъ')==[]

def test_prior_leave_occurrence_out():
    p=dict(stem='сол',google='ь');v={'сол':Counter({'ь':1,'ъ':2})}
    assert prior(p,v)=='ъ_only'
    assert prior(p,{'сол':{'ь':1}})=='unknown'
    assert prior(p,{'сол':{'ь':2}})=='ь_only'
    assert prior(p,{'сол':{'ь':2,'ъ':1}})=='both'

def test_usable_needs_recipe_and_exclusion():
    r=dict(id='a',candidate_usable=True,crop='gone.png',crop_sha256='h',crop_source_image='src',crop_source_sha256='s',crop_bbox=[0,0,1,1])
    assert usable(r,set())
    assert not usable(r,{'a'})
    assert not usable(dict(r,candidate_usable=False),set())
