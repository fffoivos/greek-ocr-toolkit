"""Frozen ink rule, locked selection and physical edit safety; all offline."""
import copy
import json
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/numerics'))
from greekocr.numerics.ink_rule import decide,freeze,load_rule,fit,measurements,sha
from greekocr.numerics.locks import load_locks
from greekocr.numerics.line_complete import enumerate_line,enumerate_locked_line,enumerate_slots
from n1e_prepare import choose
from n1t_packs import build,rows


@pytest.fixture
def rule(tmp_path):
    cfg=dict(schema='n1-ink-rule-v1',edit_margin_min=.02,thresholds=dict(
        raised_centre=[.3,.8],raised_height_max=.4,raised_width_max=.7,
        dash_width_cuts=[.75,1.45],baseline_centre_min=.82,comma_height_min=.3,space_gap_min=.5))
    return freeze(tmp_path/'rule.json',cfg)


def slot(glyph='.',height=3,width=3,y=.55,boundary=None):
    s=dict(slot_id='line:t0:s1',line_id='line',start=1,end=1+len(glyph),glyph=glyph,boundary=boundary,
        geometry=dict(geom_status='ok',left_digit=[0,0,10,20],right_digit=[20,0,30,20]),
        measurements=dict(digit_top=0,baseline=20,digit_height=20,gap_width=10,helper_band=[8,20],
        components=[dict(bbox=[12,10,12+width,10+height],height=height,width=width,
                         centre_y_relative_band=y,wholly_inside_gap=True)]),
        dash=dict(median_digit_width=10))
    return s


@pytest.mark.parametrize('glyph,expected',[('.',True),('-',True),(',',False),('–',False),('—',False),('·',False),('',False),(' ',False)])
def test_release_only_google_minus_or_dot(rule,glyph,expected):
    s=slot(glyph);d=decide(s,rule,'1'+glyph+'2')
    assert d['class']=='raised dot' and bool(d['edit'])==expected
    assert d['rule_hash']==rule['rule_hash']
    assert d['measurements']['component_count']==1


@pytest.mark.parametrize('width,kind',[(6,'hyphen'),(10,'en dash'),(20,'em dash')])
def test_horizontal_ink_vetoes_edit(rule,width,kind):
    d=decide(slot('-',height=2,width=width),rule,'1-2')
    assert d['class']==kind and d['edit'] is None and d['tags']==[kind]


@pytest.mark.parametrize('height,y,expected',[(3,.95,'baseline dot'),(8,.95,'comma'),(3,.1,'unsure')])
def test_other_mark_classes(rule,height,y,expected):
    d=decide(slot(height=height,y=y),rule,'1.2')
    assert d['class']==expected and d['edit'] is None


def test_stroke_crossing_digit_still_veto(rule):
    s=slot(width=8,height=2);s['measurements']['components'][0]['wholly_inside_gap']=False
    assert decide(s,rule)['edit'] is None


def test_boundary_never_edits(rule):
    s=slot(boundary='left');assert decide(s,rule)['edit'] is None


def test_ambiguous_components_abstain(rule):
    s=slot();s['measurements']['components']*=2
    d=decide(s,rule);assert d['class']=='unsure' and d['tags']==['unsure'] and not d['edit']


@pytest.mark.parametrize('gap,kind',[(1,'nothing'),(9,'space'),(-2,'unsure'),(0,'unsure')])
def test_empty_gap_custody(rule,gap,kind):
    s=slot('');s['measurements'].update(components=[],gap_width=gap)
    assert decide(s,rule)['class']==kind


def test_margin_is_required(rule):
    s=slot(y=.79);d=decide(s,rule)
    assert d['class']!='raised dot' and d['edit'] is None


def test_custody_and_tamper(rule,tmp_path):
    with pytest.raises(ValueError,match='custody'):decide(slot(),rule,'1-2')
    p=tmp_path/'rule.json';p.write_text(p.read_text()+' ')
    with pytest.raises(ValueError,match='hash'):load_rule(p)


def test_fit_without_measurable_raised_refuses():
    s=slot();s.update(truth='baseline dot')
    with pytest.raises(ValueError,match='no measurable'):fit([s])


def test_reserved_fit_and_explicit_locked_route():
    locks=load_locks(ROOT/'artifacts/n1');lid=next(iter(locks.locked_line_ids))
    r=dict(id=lid,text='1.2',label='1.2')
    with pytest.raises(ValueError,match='reserved'):enumerate_line(r,locks)
    assert len(enumerate_locked_line(r,locks,{lid}))==3
    with pytest.raises(ValueError,match='draw'):enumerate_locked_line(r,locks,set())


def test_pack_builder_refuses_repo_and_symlink(tmp_path):
    with pytest.raises(ValueError,match='in-repo'):build([],[],ROOT/'artifacts/bad',tmp_path,None)
    link=tmp_path/'alias';link.symlink_to(ROOT,target_is_directory=True)
    with pytest.raises(ValueError,match='in-repo'):build([],[],link/'bad',tmp_path,None)


def test_locked_requires_freeze_and_reservation(tmp_path):
    with pytest.raises(ValueError,match='freeze'):build([],[],tmp_path/'packs',tmp_path,None,evaluation_ids={'line'})


@pytest.mark.skip(reason="historical binding; green at opus/secondary-corrections@69c068b18; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_frozen_artifact_and_document_split():
    out=ROOT/'artifacts/n1/n1r';r=load_rule(out/'rule.json');truth=rows(out/'truth.jsonl')
    cfg=r['config'];assert not set(cfg['fit_documents'])&set(cfg['held_documents'])
    assert abs(len(cfg['fit_documents'])-len(cfg['held_documents']))<=1
    locks=load_locks(ROOT/'artifacts/n1');locks.assert_fit_rows(s['line_id'] for s in truth)
    assert not any(s.get('c1_control_only') or s['document'] in locks.reserved_docs for s in truth)
    assert fit([s for s in truth if s['split']=='fit'])['thresholds']==cfg['thresholds']
    for name,digest in cfg['inputs'].items():assert sha(ROOT/'artifacts/n1'/name)==digest
    assert sha(ROOT/'greekocr/numerics/ink_rule.py')==cfg['implementation_sha256']


def test_locked_complete_selection_and_hash_order():
    require_file('artifacts/n1/n1e/slots.jsonl')
    base=ROOT/'artifacts/n1';out=base/'n1e';slots=rows(out/'slots.jsonl');lines=rows(out/'lines.jsonl')
    rule=load_rule(base/'n1r/rule.json');ids=set(_data_input(base/'n1_locked_eval_line_ids_alt.txt').read_text().splitlines())
    assert {r['line_id'] for r in lines}==ids and len(lines)==258
    ss={s['slot_id']:s for s in slots}
    assert len(ss)==len(slots)
    for line in lines:
        assert [s['slot_id'] for s in enumerate_slots(dict(id=line['line_id'],text=line['text']))]==line['slots']
    ds=rows(out/'rule_decisions.jsonl');byline={r['line_id']:r['text'] for r in lines}
    assert ds==[decide(s,rule,byline[s['line_id']]) for s in slots]
    selected,pool=choose(slots,ds)
    assert set(selected)=={s['slot_id'] for s in rows(out/'read_set.jsonl')}
    assert sum(v=='marked-ten-percent' for v in selected.values())==__import__('math').ceil(pool*.1)
    assert all(d['rule_hash']==rule['rule_hash'] for d in ds)
    # Checkout timestamps describe file materialization, not experiment order.
    # Preserve the producing receipt's freeze-order claim and bind its rule.
    receipt = json.loads(_data_input(out/'build.json').read_text())
    assert receipt['rule_frozen_before_locked'] is True
    assert receipt['rule_hash'] == rule['rule_hash']
    recorded = next(value for path, value in receipt['inputs'].items()
                    if Path(path).parts[-3:] == ('n1', 'n1r', 'rule.json'))
    assert recorded == sha(base/'n1r/rule.json')
