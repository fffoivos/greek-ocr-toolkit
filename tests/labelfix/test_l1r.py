"""SF4 shard identity, durable reuse, and fail-closed receipt integration."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from tests.labelfix.test_l1e import runtime
from scripts.labelfix.clariden.l1_common import rows, sha256, write_json
from scripts.labelfix.clariden.r1_common import write_rows
from scripts.labelfix.clariden import l1r_recompose_ext as l1r


def fixture(root):
    base, peer, bind = root/'historical', root/'inference', root/'binding'
    for p in (base/'detector', base/'combined', peer, bind):
        p.mkdir(parents=True)
    source = root/'source.jsonl'
    # Selection order deliberately differs from detector/alignment shard order.
    selected = [dict(id=i,label='α',script_class='greek_poly',wave='wave1c',source='test') for i in ('y','x')]
    write_rows(source, selected)
    selection = bind/'selection.jsonl'
    write_rows(selection, selected)
    write_json(bind/'binding.json', dict(detector='s6',detector_commit='frozen',code_commit='historical',
                                       r1_sha256='Ahash',policy_sha256='old',source_sha256=sha256(source)))
    cp = dict(A='Ahash', B='Bhash', E='Ehash')
    steps, detectors, peers = {}, [], []
    for n, i in enumerate(('x','y')):
        prefix = f'shard-{n:05d}'
        r = runtime(); r['id'] = i
        old = {k:v for k,v in r.items() if not k.startswith('peer_')}
        det = base/'detector'/f'{prefix}-detector.jsonl.gz'
        write_rows(det, [old])
        dr = dict(shard=n,lines=1,windows=1,complete=True,sha256={det.name:sha256(det)})
        drp = base/'detector'/f'{prefix}-receipt.json'
        write_json(drp, dr); detectors.append(dr)
        steps[str(drp.relative_to(base))] = sha256(drp)
        ap = base/'combined'/f'{prefix}-combined.jsonl.gz'
        write_rows(ap, [old])
        arp = base/'combined'/f'{prefix}-receipt.json'
        write_json(arp, dict(shard=n,lines=1,samples=1,complete=True,output=ap.name,output_sha256=sha256(ap)))
        steps[str(arp.relative_to(base))] = sha256(arp)
        pp = peer/ap.name; write_rows(pp, [r])
        prp = peer/f'{prefix}-receipt.json'
        write_json(prp, dict(shard=n,lines=1,samples=1,complete=True,output=pp.name,output_sha256=sha256(pp),
                   inputs=dict(historical_combined_sha256=sha256(ap),window_receipt_sha256=sha256(drp),
                               checkpoint_sha256=cp,code_sha256={'historical':'code'})))
        peers.append(dict(receipt=prp.name,receipt_sha256=sha256(prp),lines=1,samples=1))
    dp = base/'detector/detector_receipt.json'
    write_json(dp, dict(complete=True,lines=2,shards=detectors,selection_sha256=sha256(selection)))
    steps[str(dp.relative_to(base))] = sha256(dp)
    ip = base/'input_receipt.json'
    write_json(ip,dict(source_sha256=sha256(source),exclusions={'locked':{'line_count':0}},out_of_scope={},
                      r0_policy='locked',input_documents_sha256='documents'))
    steps[ip.name] = sha256(ip)
    write_json(base/'run_receipt.json',dict(complete=True,lines=2,binding_sha256=sha256(bind/'binding.json'),step_receipts=steps))
    write_json(peer/'r1e_receipt.json',dict(complete=True,lines=2,samples=2,shards=peers,
               historical_run_receipt_sha256=sha256(base/'run_receipt.json'),selection_sha256=sha256(selection),
               checkpoint_sha256=cp,code_sha256={'historical':'code'}))
    return dict(input_run=base,selection=selection,binding_dir=bind,source=source,ensemble_run=peer)


def test_two_shards_use_line_ids_and_reuse_after_aggregation_timeout(tmp_path, monkeypatch):
    args = fixture(tmp_path)
    out = tmp_path/'out'
    merge = l1r.merge_shards
    def timeout(*a, **kw):
        raise TimeoutError('simulated after durable shards')
    monkeypatch.setattr(l1r, 'merge_shards', timeout)
    with pytest.raises(TimeoutError):
        l1r.recompose(**args,out=out,workers=2)
    receipts = list((out/'shards').glob('*/receipt.json'))
    assert len(receipts)==2 and not (out/'receipt.json').exists()
    before = {str(p):p.read_bytes() for p in receipts}
    monkeypatch.setattr(l1r, 'merge_shards', merge)
    result = l1r.recompose(**args,out=out,workers=2)
    assert result['complete'] and before=={str(p):p.read_bytes() for p in receipts}
    assert result['counts']['ensemble_ab']['corrected']==2
    assert {r['line_id'] for r in rows(out/'release/overlay_full.jsonl.gz')}=={'x','y'}
    assert l1r.recompose(**args,out=out,workers=1)==result
    # A crash after aggregate rename but before final seal is recoverable too.
    (out/'receipt.json').unlink()
    assert l1r.recompose(**args,out=out,workers=1)['complete']


@pytest.mark.parametrize('case',['missing_shard','incomplete','payload_changed','checkpoint_changed'])
def test_input_corruption_stops_before_output(tmp_path,case):
    args=fixture(tmp_path); peer=args['ensemble_run']; top=peer/'r1e_receipt.json'
    if case=='missing_shard':
        r=l1r.load(top); r['shards'].pop();write_json(top,r)
    elif case=='incomplete':
        r=l1r.load(top);r['complete']=False;write_json(top,r)
    elif case=='checkpoint_changed':
        r=l1r.load(top);r['checkpoint_sha256']['A']='wrong';write_json(top,r)
    else:
        p=peer/'shard-00000-combined.jsonl.gz';p.write_bytes(p.read_bytes()+b'changed')
    out=tmp_path/'out'
    with pytest.raises(ValueError):l1r.recompose(**args,out=out)
    assert not out.exists()


def test_missing_peer_fields_stop_without_completion(tmp_path):
    args=fixture(tmp_path); peer=args['ensemble_run'];p=peer/'shard-00000-combined.jsonl.gz'
    r=list(rows(p));r[0]['peer_predictions'].pop('E');write_rows(p,r)
    rp=peer/'shard-00000-receipt.json';sr=l1r.load(rp);sr['output_sha256']=sha256(p);write_json(rp,sr)
    top=peer/'r1e_receipt.json';r=l1r.load(top);r['shards'][0]['receipt_sha256']=sha256(rp);write_json(top,r)
    out=tmp_path/'out'
    with pytest.raises(ValueError,match='B/E inference incomplete'):l1r.recompose(**args,out=out)
    assert not (out/'receipt.json').exists() and not (out/'release').exists()


def test_output_can_never_contain_or_modify_historical_inputs(tmp_path):
    args=fixture(tmp_path)
    for out in (args['input_run'],args['input_run']/'new',tmp_path,args['ensemble_run']/'new'):
        with pytest.raises(ValueError,match='separate'):l1r.recompose(**args,out=out)
