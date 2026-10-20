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
    from n1t_combine import load_reads
    from n1_pack_closure import scan
    from greekocr.numerics.combine_v2 import MEANINGS
    out=Path(out);rule=load_rule(rulepath)
    if rule['config']['implementation_sha256']!=sha(ROOT/'greekocr/numerics/ink_rule.py'):
        raise ValueError('frozen implementation changed')
    receiptpath=Path(receiptpath or out.parent/'N1R_RECEIPT.json')
    receipt=json.loads(receiptpath.read_text())
    for p,digest in receipt['outputs'].items():
        if sha(p)!=digest:raise ValueError('N1R sealed preparation changed: '+p)
    build=json.loads((out/'build.json').read_text())
    if build['rule_hash']!=rule['rule_hash']:raise ValueError('locked build rule mismatch')
    for p,digest in build['inputs'].items():
        if sha(p)!=digest:raise ValueError('locked source changed')
    slots=rows(out/'slots.jsonl');lines={r['line_id']:r['text'] for r in rows(out/'lines.jsonl')}
    decisions=rows(out/'rule_decisions.jsonl')
    if decisions != [decide(s,rule,lines[s['line_id']]) for s in slots]:raise ValueError('frozen decision replay differs')
    pack=Path(build['pack_root']);evidence={}
    for c in build['dry_runs']:
        ctx,reader=c['context'],c['reader'];rd=pack/ctx/reader
        closure=scan(rd,out,completed=True,meanings=MEANINGS)
        if not closure['ok']:raise ValueError('pack custody: '+str(closure['violations']))
        stem=out.parent/'answers'/out.name/(ctx+'.'+reader)
        for suffix in ('.jsonl','.scan.json','.run.json'):
            p=Path(str(stem)+suffix);evidence[str(p)]=sha(p)
        scanrecord=json.loads(Path(str(stem)+'.scan.json').read_text())
        if scanrecord.get('scanner_version')!='v4.4-canonical':raise ValueError('canonical scan required')
        if rows(Path(str(stem)+'.jsonl'))!=rows(rd/'answers.jsonl'):raise ValueError('answers custody differs')
    reads,gates=load_reads(out)
    if any(g['status']!='VALID' for g in gates.values()):raise ValueError('locked context not VALID')
    lead=rows(leadpath) if leadpath else []
    if leadpath:evidence[str(Path(leadpath).resolve())]=sha(leadpath)
    read_set=rows(out/'read_set.jsonl')
    result=score(decisions,[s['slot_id'] for s in read_set],reads,lead,
                 [s['slot_id'] for s in read_set if s.get('render_scope')=='whole_line_unlocalized'])
    result.update(evidence=evidence,prepared_receipt_sha256=sha(receiptpath),gate_scope='n1_locked_eval_alt',
                  locked_line_ids_sha256=sha(out.parent/'n1_locked_eval_line_ids_alt.txt'),contexts=gates)
    return result


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'artifacts/n1/n1e');p.add_argument('--rule',type=Path,default=ROOT/'artifacts/n1/n1r/rule.json')
    p.add_argument('--lead',type=Path);p.add_argument('--output',type=Path,default=ROOT/'artifacts/n1/n1e/gate.json')
    a=p.parse_args();result=score_locked(a.out,a.rule,a.lead)
    with a.output.open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps(result,ensure_ascii=False));return 0 if result['passed'] else 2
if __name__=='__main__':sys.exit(main())
