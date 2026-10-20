"""Readback fail-closed checks and teacher probability integrity accounting."""
from copy import deepcopy
import json
from pathlib import Path
from tests._paths import require_file
import pytest
from scripts.labelfix.r2_readback_verify import sha, verify
from scripts.labelfix.r2_job1_digest import head_check, add_row, bucket, finish, physical_ledger
from scripts.labelfix.clariden.r1_common import HEADS


def readback(tmp_path):
    root=tmp_path/'readback';(root/'B').mkdir(parents=True)
    payload=root/'B'/'chunk-000000-train.jsonl.gz';payload.write_bytes(b'payload')
    chunk=root/'B'/'chunk-000000.receipt.json'
    chunk.write_text(json.dumps(dict(complete=True,sha256={payload.name:sha(payload)})))
    stage=root/'stage_B.json';stage.write_text(json.dumps(dict(complete=True,sha256={'B/'+payload.name:sha(payload),'B/'+chunk.name:sha(chunk)})))
    manifest=tmp_path/'remote.txt';manifest.write_text(f'{sha(stage)}  output_3681404/stage_B.json\n')
    return root,manifest,payload


def test_readback_payload_and_envelope_are_distinct(tmp_path):
    root,manifest,payload=readback(tmp_path)
    r=verify(root,manifest,'2026-10-17T08:00:00Z')
    assert r['sha256_verified']==3 and r['receipt_matched']==2 and r['total_bytes']>7
    assert not r['failures']
    entries=json.loads((root/'READBACK_RECEIPT.json').read_text())['files']
    assert next(e for e in entries if e['path']=='stage_B.json')['receipt_match']=='no'


@pytest.mark.parametrize('failure',['tamper','missing','unbound'])
def test_readback_stops_on_invalid_or_missing_payload(tmp_path,failure):
    root,manifest,payload=readback(tmp_path)
    if failure=='tamper':payload.write_bytes(b'tampered')
    elif failure=='missing':payload.unlink()
    else:(root/'unbound.log').write_text('unbound')
    with pytest.raises(ValueError,match='VERIFICATION FAILED'):verify(root,manifest,'start')
    assert json.loads((root/'READBACK_RECEIPT.json').read_text())['failures']


def head():return dict(probabilities={'none':.995,'dialytika':.005},top='none',top_probability=.995,margin=.990)


def test_full_probability_validation_includes_consistency():
    assert head_check(head(),HEADS['dialytika'])['invalid']==[]
    for k in ('top_probability','margin','probabilities','top'):
        bad=head();del bad[k];assert k in head_check(bad,HEADS['dialytika'])['missing']
    for probabilities in ({'none':1.1,'dialytika':-.1},{'none':float('nan'),'dialytika':0.},{'none':.9,'dialytika':.05},{'none':1.}):
        bad=head();bad['probabilities']=probabilities;assert head_check(bad,HEADS['dialytika'])['invalid']
    for field,value in [('top','dialytika'),('top_probability',.8),('margin',.2)]:
        bad=head();bad[field]=value;assert head_check(bad,HEADS['dialytika'])['invalid']


def test_inventory_keeps_missing_heads_in_denominator_and_unknown():
    b=bucket();r=dict(line_id='l',teacher_seen_document=True,heads={'dialytika':head()},factors=[0]*4,
        crop_validity=dict(clipped_top=True,span_plausible=False),coverage=dict(uncertainty=['ambiguous']))
    add_row(b,r);add_row(b,dict(r,heads={}))
    z=finish(b);assert z['lines']==1 and z['slots']==2 and z['teacher_seen_document']=={'True':2}
    assert z['heads']['dialytika']['both_share']==.5 and z['heads']['dialytika']['missing_rows']==1
    assert z['heads']['accent']['missing_rows']==2 and z['validity']['localisation_unknown']==2


def test_physical_ledger_preserves_exact_wrong_names_and_unknown():
    old=[dict(line_id='l',doc='d',slots=[dict(slot=1,base='α',truth=[['accent','acute']],detected=[['accent','acute']]),dict(slot=2,base='η',truth=None,detected=[])])]
    new=deepcopy(old);new[0]['slots'][0]['detected']=[['accent','grave']];new[0]['slots'][1]['detected']=[['accent','acute']]
    z=physical_ledger(old,new)
    assert z['counts']=={'old_right_new_wrong':1} and z['ledger'][0]['slot']==1


def test_dev_pending_uses_full_census_and_retains_truth_scope(tmp_path,monkeypatch):
    from scripts.labelfix import r2_job1_digest as d
    truth=tmp_path/'truth.jsonl';out=tmp_path/'out';out.mkdir()
    truth.write_text(json.dumps(dict(type='item',line_id='line000',wave='test',control=False))+'\n')
    sources={f'line{i:03d}':dict(doc='d',crop=f'crop{i}.png',label='α',wave='test') for i in range(600)}
    (tmp_path/'sources.json').write_text(json.dumps(sources))
    (tmp_path/'baseline_per_line.jsonl').write_text(''.join(json.dumps(dict(id=k))+'\n' for k in sources))
    monkeypatch.setattr(d,'DEV',truth);monkeypatch.setattr(d,'EVID',out)
    assert d.dev_pending()==600
    result=json.loads((out/'DEV_pending.json').read_text())
    assert result['truth_card_lines']==1 and result['noncontrol_truth_card_lines']==1
    assert len((out/'DEV_selection.jsonl').read_text().splitlines())==600
    assert not result['proposed_job']['submitted']


def test_population_line_counts_include_lines_without_slots(tmp_path,monkeypatch):
    require_file('artifacts/labelfix_r2/population/population.jsonl')
    from scripts.labelfix import r2_job1_digest as d
    (tmp_path/'B').mkdir();(tmp_path/'B/teacher_receipt.json').write_text(json.dumps(dict(binding=dict(line_list_sha256='bound'))))
    monkeypatch.setattr(d,'ROOT',tmp_path)
    monkeypatch.setattr(d,'sha256',lambda p:'bound')
    monkeypatch.setattr(d,'rows',lambda p:iter([dict(role='train',source='s',teacher_seen_document=True),dict(role='train',source='s',teacher_seen_document=False)]))
    inv=d.bind_population(dict(roles={'train':finish(bucket())},role_source={}))
    assert inv['roles']['train']['lines']==2 and inv['roles']['train']['zero_slot_lines']==2
    assert inv['role_source']['train / s']['teacher_seen_document_lines']=={'True':1,'False':1}


def test_real_frozen_compound_truth_and_owner_overlays_are_preserved():
    require_file('docs/records/labelfix/spellcheck/S4_lines.jsonl.gz')
    from scripts.labelfix.r2_score import truth_lines, apply_overlay
    lines=truth_lines('docs/records/labelfix/spellcheck/S4_lines.jsonl.gz')
    def target(ll):return next(s for l in ll for s in l['print_slots'] if s['id']=='384c3f89-p000059-l0013:s33')
    assert target(lines)['targets']==[1,1,0,0]
    for version,expected,unknown in [('v0',[1,1,0,0],[]),('v1',[None,3,0,0],['breathing']),('v1_1',[1,3,0,0],[])]:
        overlay=json.loads(Path(f'docs/records/labelfix/spellcheck/R2/truth_overlay_{version}.json').read_text())
        revised,receipt=apply_overlay(lines,overlay)
        assert target(revised)['targets']==expected and target(revised)['unknown']==unknown
    assert target(lines)['targets']==[1,1,0,0]
