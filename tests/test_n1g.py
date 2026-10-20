"""N1-G control, provenance coverage and deferred finalization tests; offline."""
import copy
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts/numerics'),str(ROOT)]
import n1g
from test_n1r import rule,slot
from test_n1r_gate_apply import decision,votes,train_fixture
from greekocr.numerics.combine_v2 import decode_and_gate
from greekocr.numerics.ink_rule import sha


def data(rule):
    ds=[decision(rule),decision(rule,'h','hyphen'),decision(rule,'u','unsure')]
    ss=[dict(slot_id=d['slot_id'],google_glyph='.',render_scope='localized') for d in ds]
    rr={'p':votes('raised dot'),'h':votes('hyphen'),'u':votes('baseline dot')}
    rr['u'][0]['confidence']='low'
    return dict(rule=rule,decisions=ds,slots=ss,reads=rr,contexts={},evidence={},prepared_receipt_sha256='fixture')


def test_provisional_never_authorizes(rule):
    g,c=n1g.assemble(data(rule));assert g['phase']=='PROVISIONAL' and not g['passed']
    assert g['raised_precision']==1 and g['raised_recall']==1 and len(c)==3


def test_void_single_read_and_disagreement_require_lead(rule):
    for change in ('VOID','low','disagree','unviewed'):
        d=data(rule)
        if change=='VOID':d['reads']['p'][1]['context_status']='VOID'
        elif change=='low':d['reads']['p'][1]['confidence']='low'
        elif change=='unviewed':d['reads']['p'][1]['read_status']='unviewed'
        else:d['reads']['p'][1]['meaning']='baseline dot'
        g,c=n1g.assemble(d)
        assert next(x for x in c if x['slot_id']=='p')['status']=='lead_review'
        assert g['raised_predicted']==0
        lead=[dict(slot_id='p',truth='raised dot'),dict(slot_id='u',truth='baseline dot')]
        assert n1g.final_gate(d,lead,lead)['passed']


def test_unlocalized_never_reenters_even_with_lead(rule):
    d=data(rule);d['slots'][0]['render_scope']='whole_line_unlocalized'
    lead=[dict(slot_id='p',truth='raised dot'),dict(slot_id='u',truth='baseline dot')]
    g=n1g.final_gate(d,lead,lead)
    assert g['excluded_unlocalized']==['p'] and g['raised_predicted']==0 and not g['passed']


def test_lead_overrides_agreement_and_failure_ids(rule):
    d=data(rule);lead=[dict(slot_id='p',truth='hyphen'),dict(slot_id='u',truth='baseline dot')]
    g=n1g.final_gate(d,lead,lead)
    assert not g['passed'] and g['false_range_edit_ids']==['p'] and g['failing_slots']==['p']
    lead[0]['truth']='baseline dot';g=n1g.final_gate(d,lead,lead)
    assert not g['passed'] and g['false_range_edits']==0 and g['false_positive_ids']==['p']


def test_noncritical_unresolved_reported_and_required_hold_blocks(rule):
    d=data(rule);d['slots'][2]['google_glyph']=','
    lead=[dict(slot_id='p',truth='raised dot')]
    g=n1g.final_gate(d,lead,lead)
    assert g['passed'] and g['unadjudicated_noncritical_ids']==['u'] and not g['unresolved']
    lead[0]['truth']='hold';g=n1g.final_gate(d,lead,lead)
    assert not g['passed'] and g['unresolved']==['p']


@pytest.mark.parametrize('bad',[[],[dict(slot_id='p',truth=None)],[dict(slot_id='outside',truth='raised dot')],
                                 [dict(slot_id='p',truth='raised dot')]*2])
def test_complete_lead_template_required(bad):
    with pytest.raises(ValueError):n1g.validate_lead([dict(slot_id='p')],bad)


def test_control_threshold_and_any_dash():
    key=dict(readers={'r1':['a','b','c']},items={x:dict(slot_id=x,control_truth='any dash' if x=='a' else 'baseline dot',
        option_map={'A':'hyphen','B':'en dash','C':'em dash','D':'baseline dot'}) for x in 'abc'})
    for dash in 'ABC':
        answers=[dict(item_id=x,answer=dash if x=='a' else 'D',confidence='high') for x in 'abc']
        assert decode_and_gate(key,answers)[0]['status']=='VALID'
        answers[1]['answer']='A';assert decode_and_gate(key,answers)[0]['status']=='VALID'
        answers[2]['answer']='A';assert decode_and_gate(key,answers)[0]['status']=='VOID'


def test_direct_derived_unviewed_coverage(tmp_path):
    items=[dict(item_id=x,line=f'img/{x}line.png',zoom=f'img/{x}zoom.png',options={}) for x in 'abc']
    command="magick img/bzoom.png -resize 200% zoom/montage.png"
    records=[dict(payload=dict(type='custom_tool_call',name='exec',input='await tools.exec_command({cmd:'+json.dumps(command)+'})')),
             dict(payload=dict(type='custom_tool_call_output'))]
    rollout=tmp_path/'rollout.jsonl';rollout.write_text(''.join(json.dumps(x)+'\n' for x in records))
    scan=dict(image_matches=[dict(record=1,path='img/aline.png'),dict(record=1,path='zoom/montage.png')],
              images_viewed=['img/aline.png','zoom/montage.png'])
    cov=n1g.item_coverage(scan,rollout,tmp_path,items)
    assert cov['counts']==dict(direct=1,derived=1,unviewed=1)
    assert cov['items']==dict(a='direct',b='derived',c='unviewed')


def test_phase2_requires_go_before_any_access(tmp_path,monkeypatch):
    monkeypatch.setattr(n1g,'audit',lambda:pytest.fail('must not audit'))
    with pytest.raises(ValueError,match='go'):n1g.phase2(tmp_path/'absent',False)


def setup_phase2(tmp_path,monkeypatch,d,lead):
    base=tmp_path/'artifacts/n1';base.mkdir(parents=True);out=base/'n1e';out.mkdir()
    dest=tmp_path/'review';dest.mkdir();report=tmp_path/'docs/records/labelfix/secondary/N1R_REPORT.md';report.parent.mkdir(parents=True);report.write_text('fixture\n')
    lp=dest/'lead.jsonl';n1g.jsonl(lp,lead)
    index=dest/'sheets_index.json';n1g.write(index,dict(sheets=[dict(cells=lead,file='sheet.png',sha256=sha(lp))]))
    (dest/'sheet.png').write_bytes(lp.read_bytes())
    n1g.write(base/'N1G_RECEIPT.json',dict(evidence={},sheets_index_sha256=sha(index),phase2_executed=False,
                                           training_written=False,lqb_registered=False))
    monkeypatch.setattr(n1g,'ROOT',tmp_path);monkeypatch.setattr(n1g,'BASE',base);monkeypatch.setattr(n1g,'OUT',out);monkeypatch.setattr(n1g,'DEST',dest)
    monkeypatch.setattr(n1g,'audit',lambda:d)
    return base,lp


def test_phase2_failure_stops_before_apply_and_registration(rule,tmp_path,monkeypatch):
    d=data(rule);lead=[dict(slot_id='p',truth='hyphen'),dict(slot_id='u',truth='baseline dot')]
    base,lp=setup_phase2(tmp_path,monkeypatch,d,lead)
    monkeypatch.setattr(n1g.subprocess,'run',lambda *a,**k:pytest.fail('must not apply'))
    g=n1g.phase2(lp,True)
    assert not g['passed'] and g['failing_slots']==['p']
    assert not (base/'n1_v1_train.jsonl').exists()
    receipt=json.loads((base/'N1G_RECEIPT.json').read_text());assert receipt['phase']=='FINAL FAIL' and not receipt['lqb_registered']


def test_phase2_pass_invokes_applier_then_scores(rule,tmp_path,monkeypatch):
    d=data(rule);lead=[dict(slot_id='p',truth='raised dot'),dict(slot_id='u',truth='baseline dot')]
    base,lp=setup_phase2(tmp_path,monkeypatch,d,lead)
    from greekocr.labelfix import lqb
    calls=[]
    def fake_apply(args,check):
        calls.append(args)
        assert '--lead-go' in args and check
        (base/'n1_v1_train.jsonl').write_text('{}\n')
        reg=tmp_path/'docs/records/labelfix/lqb/versions.json';reg.parent.mkdir(parents=True);n1g.write(reg,dict(versions={}))
    def fake_score(truth,registry,names):
        assert (base/'n1_v1_train.jsonl').exists() and names[-1]=='n1_v1_train'
        return dict(fixture=True)
    monkeypatch.setattr(n1g.subprocess,'run',fake_apply);monkeypatch.setattr(lqb,'run',fake_score)
    assert n1g.phase2(lp,True)['passed'] and len(calls)==1
    assert (base/'n1_v1_train.jsonl.sha256').read_text().split()[0]==sha(base/'n1_v1_train.jsonl')
    receipt=json.loads((base/'N1G_RECEIPT.json').read_text());assert receipt['lqb_registered'] and receipt['training_written']


def test_real_phase1_selection_and_sheets_are_complete():
    cs=[json.loads(x) for x in (n1g.OUT/'gate_candidates.jsonl').read_text().splitlines()]
    template=rows(n1g.DEST/'gate_lead_template.jsonl')
    assert {r['slot_id'] for r in template}==n1g.review_ids(cs)
    assert len({r['slot_id'] for r in template})==len(template)
    assert all(r['truth'] is None for r in template)
    index=json.loads((n1g.DEST/'sheets_index.json').read_text())
    from PIL import Image
    for sh in index['sheets']:
        assert sh['total_cells']<=12 and len({r['document'] for r in sh['references']})==1
        assert {r['truth'] for r in sh['references']}=={'raised dot','baseline dot'}
        assert sha(n1g.DEST/sh['file'])==sh['sha256']
        with Image.open(n1g.DEST/sh['file']) as im:
            for c in sh['cells']:assert 0<=c['bbox'][0]<c['bbox'][2]<=im.width and 0<=c['bbox'][1]<c['bbox'][3]<=im.height
    excluded=rows(n1g.OUT/'gate_unlocalized.jsonl');assert len(excluded)==36
    g=json.loads((n1g.OUT/'gate_provisional.json').read_text())
    assert g['phase']=='PROVISIONAL' and not g['passed'] and g['rows']==384

from n1t_packs import rows


def test_missing_review_union_cannot_pass(rule):
    d=data(rule)
    with pytest.raises(ValueError,match='union'):n1g.final_gate(d,[],[])


def test_forged_provisional_pass_cannot_authorize(rule):
    from n1_apply_train import authorize_gate
    g,_=n1g.assemble(data(rule));g['passed']=True;g['unresolved']=[]
    with pytest.raises(ValueError,match='gate'):authorize_gate(g,rule)


def test_sealed_predecessors_and_frozen_rule_are_unchanged():
    sealed=json.loads((n1g.BASE/'N1R_RECEIPT.json').read_text())
    for name in ('n1_gate.py','n1_apply_train.py'):
        # Receipt keys retain their producing checkout's absolute paths.
        recorded = next(value for path, value in sealed['outputs'].items()
                        if Path(path).parts[-3:] == ('scripts', 'numerics', name))
        assert sha(n1g.BASE/'n1g/predecessor'/name) == recorded
    assert sha(n1g.RULE)==json.loads((n1g.OUT/'build.json').read_text())['rule_hash']


def test_applier_cli_uses_final_locked_gate_without_dev_requalification(rule,tmp_path,monkeypatch):
    import n1_apply_train
    import n1_gate
    from test_n1r_gate_apply import gate
    g=gate(rule);g['phase']='FINAL'
    monkeypatch.setattr(sys,'argv',['n1_apply_train.py','--lead-go','--lead',str(tmp_path/'lead.jsonl')])
    monkeypatch.setattr(n1_gate,'score_locked',lambda *a,**k:g)
    monkeypatch.setattr(n1_apply_train,'load_rule',lambda p:rule)
    called=[]
    monkeypatch.setattr(n1_apply_train,'run',lambda *a,**k:called.append(a) or {'fixture':True})
    n1_apply_train.main()
    assert len(called)==1 and called[0][4]['phase']=='FINAL'
