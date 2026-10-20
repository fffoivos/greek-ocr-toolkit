"""N1-TS gate provenance, complete lead scope and phase-2 publication fixtures."""
import copy
import json
from pathlib import Path
from tests._paths import require_file
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/numerics'))
import n1ts
from n1t_combine import load_reads
from greekocr.numerics.combine_v2 import decode_and_gate, decide
from test_n1t import SLOT, vote, key_fixture, owner_fixture


@pytest.mark.parametrize('meaning,wrong,abstain', [('unreadable',1,0),('other',1,0),('hyphen',0,0),('en dash',0,0),('em dash',0,0)])
def test_unsure_dash_rule(meaning,wrong,abstain):
    key,a=key_fixture(['hyphen']);key['items'][a[0]['item_id']]['control_truth']='any dash'
    item=key['items'][a[0]['item_id']];a[0]['answer']=next(k for k,v in item['option_map'].items() if v==meaning)
    g,_=decode_and_gate(key,a);assert (g['wrong'],g['abstentions'])==(wrong,abstain)


def test_ordinary_u_abstains_and_two_errors_void():
    key,a=key_fixture(['raised dot','comma','baseline dot'])
    a[0]['answer']='J';assert decode_and_gate(key,a)[0]==dict(status='VALID',wrong=0,abstentions=1)
    a[1]['answer']=a[2]['answer']='D';assert decode_and_gate(key,a)[0]['status']=='VOID'


@pytest.mark.parametrize('reads,reason', [
 ([vote(),vote('r2',gate='INVALID')],'invalid_context_provenance'),
 ([vote(),vote('r2',gate='VOID')],'void_context'),
 ([vote(),vote('r2',confidence='low')],'low_confidence'),
 ([vote(),vote('r2',meaning='unreadable')],'unreadable_or_other'),
 ([vote(),vote('r2',meaning='comma')],'reader_disagreement')])
def test_reason_split(reads,reason):assert decide(SLOT,reads)['reason']==reason


def fixture():
    s=dict(SLOT);d=decide(s,[vote(),vote('r2')]);return [s],[d],[dict(slot_id=s['slot_id'],truth='raised dot',note='pixels')]


def test_raised_coverage_includes_void_and_invalid():
    s,ds,_=fixture()
    ds.append(dict(ds[0],slot_id='extra',truth_candidate=None,status='lead_review',reads=[vote(gate='INVALID')]))
    raised,review=n1ts.selections(ds);assert {d['slot_id'] for d in raised}=={s[0]['slot_id'],'extra'}
    assert len(review)==1


def test_review_cap_selection_is_seeded():
    _,ds,_=fixture();many=[dict(ds[0],slot_id=str(i),status='lead_review') for i in range(135)]
    a=n1ts.selections(many)[1];b=n1ts.selections(list(reversed(many)))[1]
    assert [d['slot_id'] for d in a]==[d['slot_id'] for d in b] and len(a[:120])==120


@pytest.mark.parametrize('defect',['missing','duplicate','extra','pending','invalid','both_void'])
def test_phase2_rejects_incomplete_or_blocked_rulings(defect):
    s,d,r=fixture();blocked=[]
    if defect=='missing':r=[]
    elif defect=='duplicate':r+=r
    elif defect=='extra':r.append(dict(slot_id='extra',truth='comma'))
    elif defect=='pending':r[0]['truth']=None
    elif defect=='invalid':r[0]['truth']='guess'
    else:blocked=['ctx01']
    with pytest.raises(ValueError):n1ts.apply_lead(s,d,r,blocked)


@pytest.mark.parametrize('truth',['raised dot','em dash','nothing','keep Google','unreadable'])
def test_lead_overrides_proposal_without_label_edits(truth):
    s,d,r=fixture();r[0]['truth']=truth;before=copy.deepcopy(d)
    final=n1ts.apply_lead(s,d,r);assert d==before
    assert final[0]['edit'] is None and not final[0]['apply_edit']
    assert bool(final[0]['edit_candidate'])==(truth=='raised dot')
    assert final[0]['truth_candidate']==(truth if truth in n1ts.GLYPHS else None)


def test_phase2_refuses_without_go_before_reading_any_files(monkeypatch):
    monkeypatch.setattr(n1ts,'BASE',Path('/no/such/place'))
    with pytest.raises(ValueError,match='lead go'):n1ts.phase2()


def test_owner_rulings_typed_dash_and_complete_boxes_render_to_fixture(tmp_path):
    line,slots,ds=owner_fixture(tmp_path)
    raised,review=n1ts.selections(ds)
    rulings=[dict(slot_id=d['slot_id'],truth='en dash',note='lead pixels') for d in raised+review]
    final=n1ts.apply_lead(slots,ds,rulings)
    from greekocr.numerics.owner_v2 import build
    from n1t_owner_sheet import publish
    cards,spec=build([line],slots,final)
    assert cards[0]['printed']=='1–234 5–678'
    assert all(s['evidence'] for s in cards[0]['slots'])
    summary=publish(cards,spec,tmp_path/'sheet.html')
    html=(tmp_path/'n1_sheet.html').read_text()
    assert 'data-printed-source="ours-proposal"' in html and 'value="1–234 5–678"' in html
    assert summary['cards']==1 and summary['printed_prefilled']==1


def test_actual_phase1_accounting_and_coverage():
    require_file('artifacts/n1/n1t2/slots.jsonl')
    slots,ds,gates,blocked=n1ts.combine()
    assert len(slots)==2129 and len(ds)==2129 and not blocked
    assert gates['ctx01.r1']['control_status']=='VALID' and gates['ctx01.r1']['status']=='INVALID'
    assert sum(g['status']=='VALID' for k,g in gates.items() if k.endswith('.r1'))==11
    raised,review=n1ts.selections(ds)
    index=json.loads((n1ts.DEST/'sheets_index.json').read_text())
    assert all(s['total_cells']<=12 for s in index['sheets'])
    assert {c['slot_id'] for s in index['sheets'] if s['set']=='raised' for c in s['cells']}=={d['slot_id'] for d in raised}
    shown={c['slot_id'] for s in index['sheets'] if s['set']=='review' for c in s['cells']}
    assert shown=={d['slot_id'] for d in review[:120]}
    assert {r['slot_id'] for r in index['deferred_slots']}=={d['slot_id'] for d in review[120:]}
    assert {r['slot_id'] for r in n1ts.rows(n1ts.BASE/'lead_t_template.jsonl')}=={d['slot_id'] for d in raised+review}
    for s in index['sheets']:
        if s['set']=='raised':assert [r['truth'] for r in s['references']]==['raised dot']*2+['baseline dot']*2
    receipt=json.loads((n1ts.BASE/'N1TS_PHASE1.json').read_text())
    if not (n1ts.BASE/'N1TS_PHASE2.json').exists():
        assert n1ts.sha(n1ts.BASE/'owner_sheet/n1_sheet.html')==receipt['owner_sheet_sha256']
    else:
        phase2=json.loads((n1ts.BASE/'N1TS_PHASE2.json').read_text())
        ts3=n1ts.BASE/'N1TS3_RECEIPT.json'
        current=json.loads(ts3.read_text())['owner'] if ts3.exists() else phase2
        assert n1ts.sha(n1ts.BASE/'owner_sheet/n1_sheet.html')==current['hashes']['n1_sheet.html']
    assert len(receipt['geometry_audit'])==30
    assert sum(x['count'] for x in receipt['google_ours'])==receipt['decided']


def test_phase2_complete_entrypoint_in_temporary_fixture(tmp_path,monkeypatch):
    line,slots,ds=owner_fixture(tmp_path)
    base=tmp_path/'artifacts';out=base/'n1t2';out.mkdir(parents=True)
    monkeypatch.setattr(n1ts,'BASE',base);monkeypatch.setattr(n1ts,'OUT',out)
    n1ts.dump(out/'decisions.json',dict(decisions=ds,gates={}))
    (out/'lines.jsonl').write_text(json.dumps(line)+'\n')
    n1ts.dump(base/'N1TS_PHASE1.json',dict(source_hashes={},gates={}))
    raised,review=n1ts.selections(ds)
    (base/'lead_t_template.jsonl').write_text(''.join(json.dumps(dict(slot_id=d['slot_id'],truth='raised dot'))+'\n' for d in raised+review))
    monkeypatch.setattr(n1ts,'combine',lambda:(slots,ds,{},[]))
    from greekocr.numerics.locks import Locks
    monkeypatch.setattr(n1ts,'load_locks',lambda p:Locks(frozenset(),frozenset(),frozenset()))
    summary=n1ts.phase2(True)
    assert (base/'owner_sheet/n1_sheet.html').exists()
    assert json.loads((base/'N1TS_PHASE2.json').read_text())==summary
    assert summary['label_edits_applied']==0 and summary['lead_rulings']==2
    assert summary['cards']==1 and (out/'lead_decisions.json').exists()


def test_phase2_stale_source_refusal_before_publishing(tmp_path,monkeypatch):
    monkeypatch.setattr(n1ts,'BASE',tmp_path)
    n1ts.dump(tmp_path/'N1TS_PHASE1.json',dict(source_hashes={'README.md':'bad'}))
    with pytest.raises(ValueError,match='source changed'):n1ts.phase2(True)
    assert not (tmp_path/'owner_sheet').exists()
