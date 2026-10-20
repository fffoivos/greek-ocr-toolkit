"""Lightweight local CQ6 manifest/receipt assembly; no training or network calls."""
import collections
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
CQ = ROOT / 'artifacts/cq4'
OUT = CQ / 'cq6_package'
PREP = ROOT.parent / 'greek-ocr-toolkit-spellcheck-r2prep'
OLD_SHA = 'dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(p):
    return json.loads(Path(p).read_text())

def rows(p):
    return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]

def dump(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def write_rows(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in obj))

def sid(r):
    return tuple(r['slot_id'])

def main():
    (OUT/'data').mkdir(parents=True, exist_ok=True)
    before = OUT/'evidence/cq4_before_amendment1a'
    before.mkdir(parents=True, exist_ok=True)
    prereg = CQ/'R2A2_PREREGISTRATION.md'
    if not (before/prereg.name).exists():
        assert sha(prereg) == OLD_SHA
        shutil.copyfile(prereg, before/prereg.name)
    original = (before/prereg.name).read_text()
    assert sha(before/prereg.name) == OLD_SHA
    amendment = '''
## Amendment 1a (19 Oct 2026, CQ6 coordinator consequence note)

The validation documents are now exposed to capitals witness selection, so they
cannot serve as a fresh final capitals readout. The locked (ii)/(i-b) strata are
the only untouched final cohorts. The LQB in-sample guard lists the W-CAP items
against R2a-2. This is an exposure guard, not a claim that W-CAP was trained on:
W-CAP remains an independent evaluation witness and is never training data.

This consequence note is recorded after the existing CQ4 reads, as directed in
HANDOFF_20261018_spellcheck.md §2 and CQ6. It does not claim to predate those reads.
No endpoint, quota, seed, recipe or truth label changes. Historical CQ4 receipts
retain their original freeze hash and acquire a separate current binding.
'''
    prereg.write_text(original + amendment)
    new_sha = sha(prereg)
    shutil.copyfile(prereg, OUT/prereg.name)
    binding = dict(original_preregistration_sha256=OLD_SHA,
                   current_preregistration_sha256=new_sha, amendment='1a',
                   timing='after existing CQ4 reads; consequence note only',
                   authority='CQ6 coordinator instruction; HANDOFF_20261018_spellcheck.md §2')
    for name in ('build_receipt.json','reread_build_receipt.json',
                 'aggregate_receipt.json','rescan_evidence_receipt.json'):
        p = CQ/name
        if not (before/name).exists():
            shutil.copyfile(p, before/name)
        obj = load(before/name)
        obj['cq6_amendment1a_binding'] = binding
        dump(p, obj)
    dump(CQ/'cq6_preregistration_binding.json', binding)
    dump(OUT/'data/preregistration_binding.json', binding)

    src = PREP/'artifacts/r2a_manifest/r2a_slots_v2.jsonl'
    assert sha(src) == '20b24e0fa6831487568d3bf00bac928e0fcd94831db566c520535a8216a855e1'
    shutil.copyfile(src, OUT/'data/r2a_slots_v2.jsonl')
    v2 = rows(src)
    cap = [r for r in v2 if r['slice']=='capitals']
    counts = collections.Counter(r['polarity'] for r in cap)
    assert counts == {'negative':214, 'positive':127}
    truth = rows(CQ/'truth/topup.jsonl')
    wcap = rows(CQ/'truth/wcap.jsonl')
    assert len(truth)==1009 and len(wcap)==281
    assert len({sid(r) for r in truth})==1009
    assert not {sid(r) for r in truth} & {sid(r) for r in v2}
    assert not {r['doc'] for r in truth} & {r['doc'] for r in wcap}
    alias=lambda d:d.removesuffix(':human').split(':')[-1]
    wd={alias(r['doc']) for r in wcap}
    assert not wd & {alias(r['doc']) for r in v2}
    old_receipt=load(OUT/'evidence/old_extraction_receipt.json')
    assert not wd & {alias(d) for d in old_receipt['document_split']['train']}
    assert sha(OUT/'evidence/old_extraction_receipt.json')==load(OUT/'evidence/run_binding_20261016.json')['extraction_receipt_sha256']
    selected = {sid(r):r for r in rows(CQ/'keys/topup_selected.jsonl')}
    assert len(selected)==1205
    pools = {'negative':[], 'positive':[]}
    for r in truth:
        assert r['breathing'] in ('none','smooth','rough')
        assert r['accent'] in ('none','acute','grave','circumflex')
        pools['positive' if (r['breathing'],r['accent'])!=('none','none') else 'negative'].append(r)
    # Keep frozen selection order; do not select by model outcomes or refill quarantine.
    rank = {key:i for i,key in enumerate(selected)}
    for rr in pools.values():
        rr.sort(key=lambda r:rank[sid(r)])
    chosen = pools['negative'][:586] + pools['positive'][:373]
    chosen.sort(key=lambda r:rank[sid(r)])
    overlay = []
    for r in chosen:
        x = selected[sid(r)]
        assert x['role']=='train'
        overlay.append(dict(slot_id=r['slot_id'],line_id=r['line_id'],doc=r['doc'],
            source=r['source'],role='train',provenance='native_print',
            targets=[('none','smooth','rough').index(r['breathing']),
                     ('none','acute','grave','circumflex').index(r['accent']),None,None],
            unknown=['diaeresis','subscript'],loss_weight=1,teacher_seen_document=r['teacher_seen_document'],
            pool='native',slice='capitals',polarity='positive' if (r['breathing'],r['accent'])!=('none','none') else 'negative',
            truth_tier=r['truth_tier'],truth_scope='breathing/accent only; other heads not asserted by CQ4 truth',
            page=x['page'],overlay_action=r['overlay_action']))
    write_rows(OUT/'data/topup_partial.jsonl', overlay)
    write_rows(OUT/'data/overlay_partial.jsonl', v2+overlay)
    write_rows(OUT/'data/topup_unused_resolved.jsonl', [r for r in truth if sid(r) not in {sid(x) for x in chosen}])
    shutil.copyfile(CQ/'truth/wcap.jsonl',OUT/'data/wcap_truth.jsonl')
    shutil.copyfile(CQ/'truth/topup.jsonl',OUT/'data/topup_all_resolved.jsonl')
    # Include all 300 selected items, including quarantine, in the exposure guard.
    write_rows(OUT/'data/lqb_in_sample_guard.jsonl',[
        dict(arm='R2a-2',set='W-CAP',slot_id=r['slot_id'],line_id=r['line_id'],doc=r['doc'],
             reason='exposed_to_witness_selection',trained_on=False,
             exclude_from_fresh_final_capitals_readout=True,
             resolved=sid(r) in {sid(x) for x in wcap})
        for r in rows(CQ/'keys/wcap_selected.jsonl')])
    write_rows(OUT/'data/lqb_guard.jsonl', rows(OUT/'data/lqb_in_sample_guard.jsonl') + [
        dict(arm='R2a-2',set='planned_training_overlay',slot_id=r['slot_id'],line_id=r['line_id'],doc=r['doc'],
             reason='planned_training_identity',trained_on=False,planned_training=True,
             exclude_from_fresh_final_capitals_readout=True)
        for r in v2+overlay])
    shutil.copyfile(CQ/'keys/old_overlap.json',OUT/'evidence/old_overlap.json')
    dump(OUT/'data/old_pool_reference.json',dict(
        path=load(OUT/'evidence/config.json')['data'],
        binding_source='evidence/run_binding_20261016.json',
        extraction_receipt_sha256=load(OUT/'evidence/run_binding_20261016.json')['extraction_receipt_sha256'],
        shard_sha256=load(OUT/'evidence/run_binding_20261016.json')['shard_sha256'],
        old_rows=1935016,unique_keys=1935011,duplicate_groups=5,excess_rows=5,
        policy='preserve BASE row order and every duplicate; replace unique old identities in place; STOP on duplicated-key hit'))
    nc = 214+sum(r['polarity']=='negative' for r in overlay)
    pc = 127+sum(r['polarity']=='positive' for r in overlay)
    receipt = dict(status='stopped',reason='frozen 500-positive capital quota unmet; no reduced training quota authorized',
        seeds=[20261016,20261017,20261018],v2_slots=1572,
        v2_capitals=dict(negative=214,positive=127),
        resolved_topup=dict(negative=len(pools['negative']),positive=len(pools['positive'])),
        selected_topup=dict(negative=nc-214,positive=pc-127,total=len(overlay)),
        capital_slice=dict(negative=nc,positive=pc),shortfall=dict(negative=800-nc,positive=500-pc),
        wcap=dict(resolved=281,total=300,marked=133,bare=148,minimum=210,minimum_pass=True),
        minimum_note='The preregistration specifies W-CAP minimum 210 only. CQ4 build inventory minimum 844 passes (1009 resolved; 875 selected). No separate lower training quota is specified.',
        preregistration_binding=binding,training_ready=False,deployable=False,
        witness_disjoint_from_old_training_and_v2=True,
        deployed=False,submitted=False,smoke_executed=False,real_input_dry_run_executed=False)
    dump(OUT/'assembly_receipt.json',receipt)
    files = sorted((OUT/'data').glob('*'))
    dump(OUT/'DATA_MANIFEST.json',dict(files=[dict(path=str(p.relative_to(OUT)),sha256=sha(p),bytes=p.stat().st_size) for p in files]))
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':
    main()
