"""Locked gate scorer. Prepare/test now; invoke only after independent readings."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from greekocr.numerics.ink_rule import DASHES,CLASSES,metrics,load_rule,sha,decide
from n1t_packs import rows


def truth_from_reads(slot_ids, reads, lead):
    if len(lead)!=len({r['slot_id'] for r in lead}):raise ValueError('duplicate lead ruling')
    if any(r['slot_id'] not in slot_ids for r in lead):raise ValueError('lead outside locked read set')
    rulings={r['slot_id']:r['truth'] for r in lead};truth={};unresolved=[]
    for sid in slot_ids:
        votes=reads.get(sid,[])
        if len(votes)!=2 or {r['reader'] for r in votes}!={'r1','r2'}:
            raise ValueError('two complete independent reads required: '+sid)
        if sid in rulings:
            t=rulings[sid]
            if t not in (*CLASSES,'any dash','hold'):raise ValueError('invalid lead truth')
            if t not in ('hold','unsure'):truth[sid]=t;continue
        else:
            usable=[r['meaning'] for r in votes if r['context_status']=='VALID' and r['read_status']=='ok' and r['confidence']=='high']
            if len(usable)==2 and usable[0]==usable[1] and usable[0] in CLASSES[:-1]:
                truth[sid]=usable[0];continue
        unresolved.append(sid)
    return truth,unresolved


def score(decisions, read_ids, reads, lead=(), unlocalized_ids=()):
    byid={d['slot_id']:d for d in decisions}
    if len(byid)!=len(decisions) or not read_ids or len(read_ids)!=len(set(read_ids)) or not set(read_ids)<=set(byid):
        raise ValueError('invalid decision/read population')
    if set(reads)!=set(read_ids):raise ValueError('read population differs')
    if len({d['rule_hash'] for d in decisions})!=1:raise ValueError('mixed rule hashes')
    truth,unresolved=truth_from_reads(read_ids,reads,list(lead))
    ruled={r['slot_id'] for r in lead if r['truth'] not in ('hold','unsure')}
    for sid in set(unlocalized_ids)-ruled:
        truth.pop(sid,None)
        if sid not in unresolved:unresolved.append(sid)
    unresolved.sort()
    # Precision includes every raised prediction as a possible error, not just
    # baseline/hyphen examples. Any-dash truth is a true range too.
    chosen=[byid[s] for s in truth]
    result=metrics(list(truth.values()),chosen)
    range_edits=[s for s,t in truth.items() if t in (*DASHES,'any dash') and byid[s]['edit'] is not None]
    result.update(schema='n1-locked-gate-v1',rule_hash=next(iter(byid.values()))['rule_hash'],
                  read_slots=len(read_ids),unresolved=unresolved,false_range_edits=len(range_edits),false_range_edit_ids=range_edits,
                  all_slots=len(decisions),all_slot_unsure_rate=sum(d['class']=='unsure' for d in decisions)/len(decisions),
                  recall_population='adjudicated locked read set; sampled remainder is not population recall')
    result['passed']=bool(not unresolved and result['raised_predicted']>0 and result['raised_truth']>0 and
                          result['raised_precision']>=.99 and not range_edits)
    return result


def score_locked(out,rulepath,leadpath=None,receiptpath=None):
    """Revalidate immutable preparation, public packs, scans and answer custody."""
    from n1g import audit, assemble, final_gate, DEST
    data = audit(Path(out), Path(rulepath))
    if leadpath is None:
        return assemble(data)[0]
    indexpath = DEST/'sheets_index.json'
    receipt = json.loads((ROOT/'artifacts/n1/N1G_RECEIPT.json').read_text())
    for p, digest in receipt.get('implementation_hashes', {}).items():
        if sha(p) != digest:
            raise ValueError('gate implementation changed: '+p)
    if sha(indexpath) != receipt['sheets_index_sha256']:
        raise ValueError('sealed gate sheet index changed')
    index = json.loads(indexpath.read_text())
    for sheet in index['sheets']:
        if sha(DEST/sheet['file']) != sheet['sha256']:
            raise ValueError('sealed gate sheet changed')
    if data['evidence'] != receipt['evidence']:
        raise ValueError('Phase 1 evidence changed')
    template = [cell for sheet in index['sheets'] for cell in sheet['cells']]
    return final_gate(data, template, rows(leadpath))


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'artifacts/n1/n1e');p.add_argument('--rule',type=Path,default=ROOT/'artifacts/n1/n1r/rule.json')
    p.add_argument('--lead',type=Path);p.add_argument('--output',type=Path,default=ROOT/'artifacts/n1/n1e/gate.json')
    a=p.parse_args();result=score_locked(a.out,a.rule,a.lead)
    with a.output.open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps(result,ensure_ascii=False));return 0 if result['passed'] else 2
if __name__=='__main__':sys.exit(main())
