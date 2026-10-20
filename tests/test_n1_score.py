"""Offline N1-S contracts, including independent context gates and slot edits."""
import importlib.util
import json
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('n1_score',ROOT/'scripts/numerics/n1_score.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def fixture(meanings):
    key={'readers':{'r1':list(meanings)},'items':{}}
    answers=[]
    for iid,meaning in meanings.items():
        key['items'][iid]=dict(slot_id=iid,control_truth='comma' if iid!='bed' else None,
                              option_map={'A':meaning})
        answers.append(dict(item_id=iid,answer='A',confidence='high'))
    return key,answers


@pytest.mark.parametrize('meanings,wrong,abstain,status',[
    ({'c1':'comma','c2':'comma','bed':'raised dot'},0,0,'VALID'),
    ({'c1':'baseline dot','c2':'unreadable','bed':'raised dot'},1,1,'VALID'),
    ({'c1':'unreadable','c2':'unreadable','bed':'raised dot'},0,2,'VALID'),
    ({'c1':'baseline dot','c2':'raised dot','bed':'raised dot'},2,0,'VOID')])
def test_gate(meanings,wrong,abstain,status):
    gate,decoded=m.decode_and_gate(*fixture(meanings))
    assert (gate['wrong'],gate['abstentions'],gate['status'])==(wrong,abstain,status)
    assert gate['bed']==1 and len(decoded)==3


@pytest.mark.parametrize('defect',['missing','duplicate','invalid'])
def test_gate_malformed_fails_closed(defect):
    key,answers=fixture({'c1':'comma','bed':'raised dot'})
    if defect=='missing': answers.pop()
    elif defect=='duplicate': answers.append(answers[0])
    else: answers[0]['answer']='Z'
    with pytest.raises(ValueError): m.decode_and_gate(key,answers)


def test_table_exact_gaps_and_reader_columns():
    rows=[dict(glyph=g,meaning=s) for g,s in [('-','raised dot'),('-','raised dot'),
        (' -','hyphen or dash'),('','comma'),('.','unreadable'),(',','baseline dot')]]
    t=m.table(rows)
    assert t['-']['raised dot']==2 and t[' -']['hyphen or dash']==1
    assert t['']['comma']==1 and t['.']['unreadable']==1 and t[',']['baseline dot']==1
    assert t['-']['baseline dot']==0
    assert sum(sum(v.values()) for v in t.values())==6


@pytest.mark.parametrize('offset,glyph',[(1,'-'),(5,'-'),(1,'.')])
def test_proposed_single_gap_middle_dot_offsets_preserved(offset,glyph):
    text='4-547-331; 2-000'.replace('-',glyph) if glyph=='.' else '4-547-331; 2-000'
    r=dict(glyph=glyph,meaning='raised dot',grammar_candidates=['thousands'],start=offset,end=offset+1)
    p=m.proposed(text,r)
    assert len(p)==len(text)
    assert [i for i,(a,b) in enumerate(zip(text,p)) if a!=b]==[offset]
    assert ord(p[offset])==0x00B7
    assert p[:offset]==text[:offset] and p[offset+1:]==text[offset+1:]


@pytest.mark.parametrize('glyph,meaning,grammar',[
    (',','raised dot',['thousands']),('-','hyphen or dash',['thousands']),
    ('.','raised dot',['decimal']),(' -','raised dot',['thousands'])])
def test_proposed_eligibility(glyph,meaning,grammar):
    assert m.proposed('4'+glyph+'547',dict(glyph=glyph,meaning=meaning,grammar_candidates=grammar,start=1,end=1+len(glyph))) is None


def test_proposed_rejects_stale_offsets():
    with pytest.raises(ValueError):
        m.proposed('4.547',dict(glyph='-',meaning='raised dot',grammar_candidates=['thousands'],start=1,end=2))


def test_weighting_unsupported_cells_and_wilson():
    def row(s,g='-',meaning='raised dot'): return dict(source_era=s,position='thousands',glyph=g,meaning=meaning)
    frame=[row('a')]*4+[row('b')]*2+[row('missing')]*2
    valid=[row('a'),row('a',meaning='hyphen or dash'),row('b')]
    r=m.rates(frame,valid)
    assert r['supported_frame']==6 and r['unsupported_frame']==2
    assert r['rate']==pytest.approx(2/3)
    assert r['full_frame_point_identification_bounds']==pytest.approx([.5,.75])
    assert m.wilson(0,10)[1]>0 and m.wilson(10,10)[0]<1


def test_uncertain_group_precedence():
    r=dict(glyph='-',meaning='raised dot',confidence='low')
    assert m.group_for(r)=='Unreadable or low confidence'
    r['confidence']='high';assert m.group_for(r)=='Hyphen printed as raised dot'
    assert m.agrees(' - ','hyphen or dash') and not m.agrees('.-','hyphen or dash')


def test_real_outputs_exclude_void_and_bind_cards():
    require_file('artifacts/n1/n1t2/phase1_owner_sheet.html')
    result=json.loads((_data_input(m.OUT/'N1S_SCORE.json')).read_text())
    valid=json.loads((_data_input(m.OUT/'N1S_VALID_SLOTS.json')).read_text())
    assert len(valid)==319
    assert {r['context'] for r in valid}=={'ctx01','ctx02','ctx03','ctx06'}
    assert all(result['gates'][r['context']]['status']=='VALID' for r in valid)
    assert sum(sum(c.values()) for c in result['table'].values())==len(valid)
    # N1-TS2 replaces the live sheet; score the SHA-verified phase-1 cards.
    cards=json.loads((_data_input(m.OUT/'n1t2/phase1_owner_cards.json')).read_text())
    from hashlib import sha256
    phase1=json.loads((_data_input(m.OUT/'N1TS_PHASE1.json')).read_text())
    assert sha256((_data_input(m.OUT/'n1t2/phase1_owner_cards.json')).read_bytes()).hexdigest()==phase1['owner_products']['cards.json']
    assert len({c['doc_id'] for c in cards})==len(cards)
    assert sum(c['group']=='Agreement sample' for c in cards)==12
    for c in cards:
        assert c['doc_id'].endswith(':s'+str(c['slot'])) and c['printed']==''
        assert c['rows'][0]['name']=='Google' and c['rows'][0]['text']
        if len(c['rows'])==3:
            a,b=c['rows'][0]['text'],c['rows'][1]['text']
            changed=[i for i in range(len(a)) if a[i]!=b[i]]
            assert len(a)==len(b) and len(changed)==1
            assert a[changed[0]] in '-.' and b[changed[0]]=='\u00b7'
    html=(_data_input(m.OUT/'n1t2/phase1_owner_sheet.html')).read_text()
    assert sha256((_data_input(m.OUT/'n1t2/phase1_owner_sheet.html')).read_bytes()).hexdigest()==phase1['owner_sheet_sha256']
    assert html.count('class="card"')==len(cards)
    assert html.count('class="printed"')==len(cards)
    assert (_data_input(m.OUT/'n1t2/phase1_owner_sheet.html')).stat().st_size<15_000_000


def test_unsupported_nonhyphen_is_structural_target_zero():
    base=dict(source_era='a',position='thousands',glyph='-',meaning='raised dot')
    other=dict(base,source_era='b',glyph='.')
    r=m.rates([base,other],[base])
    assert r['unsupported_frame']==1 and r['unsupported_target_capable_slots']==0
    assert r['full_frame_point_identification_bounds']==[.5,.5]
