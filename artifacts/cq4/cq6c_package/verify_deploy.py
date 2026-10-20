"""Read-only CQ6C byte closure and assembly checks; training is a distinct gate."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rows(p):
    return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]

def key(r):
    return tuple(r['slot_id'])

def verify(root):
    root=root.resolve()
    expected=[]
    for line in (root/'DEPLOY_SHA256.txt').read_text().splitlines():
        digest,rel=line.split('  ',1)
        p=Path(rel)
        if p.is_absolute() or '..' in p.parts or not (root/p).resolve().is_relative_to(root):
            raise ValueError('unsafe deploy path')
        if (root/p).is_symlink() or sha(root/p)!=digest:
            raise ValueError('hash/symlink mismatch: '+rel)
        expected.append(rel)
    if len(expected)!=len(set(expected)) or expected!=(root/'DEPLOY_FILES.txt').read_text().splitlines():
        raise ValueError('deploy lists disagree or duplicate paths')
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()
            and p.name not in ('DEPLOY_FILES.txt','DEPLOY_SHA256.txt') and '__pycache__' not in p.parts}
    if actual!=set(expected):
        raise ValueError('unlisted/missing package files')
    data=json.loads((root/'DATA_MANIFEST.json').read_text())
    for f in data['files']:
        if sha(root/f['path'])!=f['sha256'] or (root/f['path']).stat().st_size!=f['bytes']:
            raise ValueError('data manifest mismatch')
    if {f['path'] for f in data['files']}!={str(p.relative_to(root)) for p in (root/'data').iterdir() if p.is_file()}:
        raise ValueError('data manifest incomplete')
    rr=json.loads((root/'assembly_receipt.json').read_text())
    if sha(root/'R2A2_PREREGISTRATION.md')!=rr['preregistration_sha256']:
        raise ValueError('preregistration mismatch')
    src=json.loads((root/'evidence/source_inputs.json').read_text())
    frozen=src['frozen_cq6_hashes']
    if sha(root/'data/r2a_slots_v2.jsonl')!=frozen['cq6_package/data/r2a_slots_v2.jsonl']:
        raise ValueError('v2 bytes changed')
    v2=rows(root/'data/r2a_slots_v2.jsonl')
    topup=rows(root/'data/topup_assembled.jsonl')
    truth=rows(root/'data/topup_all_resolved.jsonl')
    order=rows(root/'data/topup_frozen_order.jsonl')
    witness=rows(root/'data/wcap_truth.jsonl')
    if rows(root/'data/overlay_assembled.jsonl')!=v2+topup:
        raise ValueError('combined overlay mismatch')
    tt={key(r):r for r in truth}
    if len(tt)!=len(truth):
        raise ValueError('duplicate truth')
    wanted={'negative':586,'positive':373};counts=Counter();chosen=[]
    for rank,r in enumerate(order):
        t=tt.get(key(r))
        if t is None:
            continue
        pol='negative' if (t['breathing'],t['accent'])==('none','none') else 'positive'
        if counts[pol]<wanted[pol]:
            chosen.append((key(r),rank,pol)); counts[pol]+=1
    if [(key(r),r['frozen_selection_rank'],r['polarity']) for r in topup]!=chosen:
        raise ValueError('frozen order/quota selection differs')
    for r in topup:
        t=tt[key(r)]
        target=[('none','smooth','rough').index(t['breathing']),('none','acute','grave','circumflex').index(t['accent']),None,None]
        if r['targets']!=target or r['unknown']!=['diaeresis','subscript'] or r['truth_tier']!=t['truth_tier']:
            raise ValueError('top-up truth or UNKNOWN policy changed')
    counts.update(r['polarity'] for r in v2 if r['slice']=='capitals')
    if dict(counts)!=rr['capital_slice'] or rr['capital_slice']!={'negative':800,'positive':500}:
        raise ValueError('capital slice differs')
    assembled=v2+topup
    if len({key(r) for r in assembled})!=len(assembled):
        raise ValueError('duplicate overlay')
    if {r['doc'] for r in topup}&{r['doc'] for r in witness}:
        raise ValueError('witness/training overlap')
    if len(witness)!=281 or len({key(r) for r in witness})!=281:
        raise ValueError('witness size/identity mismatch')
    guard=rows(root/'data/lqb_in_sample_guard.jsonl')
    if len(guard)!=300 or any(r['trained_on'] or not r['exclude_from_fresh_final_capitals_readout'] for r in guard):
        raise ValueError('W-CAP exposure guard changed')
    if {key(r) for r in guard}!={key(r) for r in rows(root/'data/wcap_frozen_selection.jsonl')}:
        raise ValueError('exposure guard identities changed')
    unused=rows(root/'data/topup_unused_resolved.jsonl')
    if {key(r) for r in unused}!={key(r) for r in truth}-{key(r) for r in topup}:
        raise ValueError('unused pool differs')
    if rr['seeds']!=[20261016,20261017,20261018]:
        raise ValueError('seed mismatch')
    return len(expected),rr

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--require-ready',action='store_true',help='require assembly ready only')
    ap.add_argument('--require-training-ready',action='store_true',help='strict production admission, expected to refuse CQ6C')
    args=ap.parse_args()
    n,r=verify(args.root)
    print(f'HASH_CLOSURE_PASS {n} files; ASSEMBLY {r["status"]} {r["capital_slice"]}')
    if args.require_ready and r['status']!='ready':
        raise SystemExit('STOP: frozen assembly quota unmet')
    if args.require_training_ready and (not r['training_ready'] or not r['deployable']):
        raise SystemExit('NOT_ADMITTED: CQ4 diaeresis/subscript UNKNOWN; unchanged R2a rejects/quarantines whole tuple. No production runtime sealed.')
    print('Training admission: '+str(r['training_ready']))

if __name__=='__main__':
    main()
