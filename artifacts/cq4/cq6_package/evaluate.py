"""CQ6 W-CAP instrument. No inference; consumes complete paired prediction ledgers."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np

SEEDS = (20261016, 20261017, 20261018)
ARMS = ('BASE', 'R2a', 'R2a-2')

def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def key(row):
    return tuple(row['slot_id'])

def marks(row):
    b, a = row['breathing'], row['accent']
    if b not in ('none', 'smooth', 'rough') or a not in ('none','acute','grave','circumflex'):
        raise ValueError('unknown/invalid capital tuple; cannot silently score as bare')
    return b, a

def primary(truth, predictions, review, truth_hash, prediction_hash, reps=50000):
    tt = {key(r):r for r in truth}
    if len(tt)!=len(truth):
        raise ValueError('duplicate truth identity')
    pp = {}
    for r in predictions:
        k = (r['seed'],r['arm'],key(r))
        if k in pp or r['seed'] not in SEEDS or r['arm'] not in ARMS or key(r) not in tt:
            raise ValueError('unexpected/duplicate prediction identity')
        pp[k]=marks(r)
    expected={(s,a,k) for s in SEEDS for a in ARMS for k in tt}
    if set(pp)!=expected:
        raise ValueError('missing paired predictions; no complete-case denominator')
    disagreements = {(s,k) for s in SEEDS for k in tt if len({pp[s,a,k] for a in ARMS})>1}
    reviewed = {(r['seed'],tuple(r['slot_id'])) for r in review.get('items',[])
                if r.get('pixel_checked') is True and r.get('blind_to_arm') is True and r.get('evidence')}
    if (review.get('truth_sha256')!=truth_hash or review.get('predictions_sha256')!=prediction_hash
            or reviewed!=disagreements):
        raise ValueError('every disagreement requires blind lead pixel review bound to these bytes')
    positive=[k for k,r in tt.items() if marks(r)!=('none','none')]
    bare=[k for k,r in tt.items() if marks(r)==('none','none')]
    if not positive or not bare:
        raise ValueError('empty endpoint support')
    def comparison(parent):
        byseed=[]
        for s in SEEDS:
            count=lambda arm:sum(pp[s,arm,k]==marks(tt[k]) for k in positive)
            invented=lambda arm:sum(pp[s,arm,k]!=('none','none') for k in bare)
            byseed.append(dict(seed=s,parent_correct=count(parent),new_correct=count('R2a-2'),
                support=len(positive),gain_pp=100*(count('R2a-2')-count(parent))/len(positive),
                parent_invented=invented(parent),new_invented=invented('R2a-2')))
        docs=sorted({r['doc'] for r in truth})
        numer=[];denom=[]
        for doc in docs:
            ks=[k for k in positive if tt[k]['doc']==doc]
            numer.append(sum(int(pp[s,'R2a-2',k]==marks(tt[k]))-int(pp[s,parent,k]==marks(tt[k])) for k in ks for s in SEEDS))
            denom.append(len(ks)*len(SEEDS))
        numer=np.asarray(numer);denom=np.asarray(denom)
        rng=np.random.default_rng(20261017)
        # Resample documents, preserving all slots, seeds, and paired arms together.
        draws=rng.integers(0,len(docs),(reps,len(docs)))
        sample_den=denom[draws].sum(1)
        valid=sample_den>0
        if not valid.any():
            raise ValueError('bootstrap has no defined recall replicates')
        gains=100*numer[draws].sum(1)[valid]/sample_den[valid]
        ci=np.quantile(gains,[.025,.975]).tolist()
        gain=100*float(numer.sum())/float(denom.sum())
        invented_delta=sum(r['new_invented']-r['parent_invented'] for r in byseed)
        gates=dict(gain_at_least_10pp=gain>=10,ci_lower_above_zero=ci[0]>0,
                   at_least_two_seeds=sum(r['gain_pp']>0 for r in byseed)>=2,
                   positive_mean=gain>0,invented_marks_delta_at_most_two=invented_delta<=2)
        return dict(parent=parent,by_seed=byseed,pooled_gain_pp=gain,document_cluster_ci95_pp=ci,
                    bootstrap_replicates=reps,bootstrap_seed=20261017,
                    undefined_bootstrap_replicates=int((~valid).sum()),
                    marked_slots=len(positive),bare_slots=len(bare),
                    pooled_false_additions_delta=invented_delta,gates=gates,primary_pass=all(gates.values()))
    secondary=comparison('R2a')
    secondary.pop('gates')
    secondary.pop('primary_pass')
    return dict(primary=comparison('BASE'),secondary_vs_R2a=secondary,
                secondary_has_no_pass_criterion=True,
                adoption='NOT_ESTABLISHED: protection families must be scored separately',
                pixel_review_disagreements=len(disagreements))

def lqb(records, guard):
    exposed={key(r) for r in guard}
    # Inputs are canonical four-head ledgers, not released edits alone.
    groups={};seen=set()
    for r in records:
        identity=(r['arm'],key(r))
        if identity in seen:
            raise ValueError('duplicate LQB arm/slot')
        seen.add(identity)
        if r['truth_tier'] not in ('A','B'):
            continue
        bucket='exposed_descriptive_only' if key(r) in exposed else 'independent'
        c=groups.setdefault((r['arm'],bucket),Counter())
        t,p=r['truth'],r['prediction']
        if len(t)!=4 or len(p)!=4:
            raise ValueError('four heads required')
        for truth,pred in zip(t,p):
            if truth is None:
                c['unknown_truth']+=1
                continue
            if pred is None:
                c['missing_prediction']+=1
                continue
            c['predicted_marks']+=int(pred!=0)
            c['correct_named_marks']+=int(pred!=0 and pred==truth)
            c['false_additions']+=int(truth==0 and pred!=0)
            c['wrong_named_marks']+=int(truth!=0 and pred!=0 and pred!=truth)
    return [dict(arm=a,cohort=b,**c,marks_precision=(c['correct_named_marks']/c['predicted_marks'] if c['predicted_marks'] else None))
            for (a,b),c in sorted(groups.items())]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--truth',type=Path,required=True)
    ap.add_argument('--predictions',type=Path,required=True)
    ap.add_argument('--lead-review',type=Path,required=True)
    ap.add_argument('--lqb',type=Path,required=True)
    ap.add_argument('--guard',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    frozen_path=Path(__file__).resolve().parent/'data/wcap_truth.jsonl'
    frozen={key(r):r for r in rows(frozen_path)}
    reviewed_truth=rows(args.truth)
    current={key(r):r for r in reviewed_truth}
    if len(frozen)!=281 or set(current)!=set(frozen) or len(current)!=len(reviewed_truth):
        raise ValueError('frozen 281-slot witness identity set changed')
    if any(current[k]['doc']!=frozen[k]['doc'] for k in frozen):
        raise ValueError('frozen witness document mapping changed')
    review=json.loads(args.lead_review.read_text())
    changes={k for k in frozen if marks(current[k])!=marks(frozen[k])}
    corrections=review.get('truth_corrections',[])
    if changes:
        if review.get('original_truth_sha256')!=sha(frozen_path):
            raise ValueError('truth correction must bind original truth bytes')
        if {tuple(r['slot_id']) for r in corrections}!=changes:
            raise ValueError('truth correction ledger incomplete')
        for r in corrections:
            k=tuple(r['slot_id'])
            if tuple(r['old_tuple'])!=marks(frozen[k]) or tuple(r['new_tuple'])!=marks(current[k]) or not r.get('evidence'):
                raise ValueError('truth correction evidence mismatch')
    result=primary(reviewed_truth,rows(args.predictions),review,sha(args.truth),sha(args.predictions))
    result['lqb_marks_precision']=lqb(rows(args.lqb),rows(args.guard))
    result['input_sha256']={str(p):sha(p) for p in (args.truth,args.predictions,args.lead_review,args.lqb,args.guard)}
    args.out.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
    main()
