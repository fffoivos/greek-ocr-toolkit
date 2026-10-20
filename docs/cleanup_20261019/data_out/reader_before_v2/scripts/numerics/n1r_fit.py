"""Fit/freeze on development documents only. Never load locked measurements."""
import hashlib
import json
from pathlib import Path
import random
import sys
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from greekocr.numerics.ink_rule import fit,freeze,decide,metrics,sha
from greekocr.numerics.locks import load_locks
from n1t_packs import typed_controls,rows
BASE=ROOT/'artifacts/n1'
SEED='20261017:N1R:document-half'


def write(path,value):
    with Path(path).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')


def jsonl(path,records):
    with Path(path).open('x') as f:
        for r in records:f.write(json.dumps(r,ensure_ascii=False)+'\n')


def main():
    out=BASE/'n1r';out.mkdir(exist_ok=True)
    source=['n1t2/slots.jsonl','n1t3/combined_decisions.json','lead_t.jsonl','controls/approved.jsonl','controls/dash_types.jsonl',
            'n1_locked_eval_line_ids.txt','n1_reserved_doc_line_ids.txt','n1_reserved_docs.txt']
    receipt=json.loads((BASE/'N1TS3_RECEIPT.json').read_text())
    # Bind the current truth inputs to their prior receipt before fitting.
    sealed=receipt['input_hashes']
    for name in source:
        expected=sealed.get('artifacts/n1/'+name)
        if isinstance(expected,str) and sha(BASE/name)!=expected:raise ValueError('TS3 truth changed: '+name)
    slots={s['slot_id']:s for s in rows(BASE/'n1t2/slots.jsonl')}
    ds=json.loads((BASE/'n1t3/combined_decisions.json').read_text())['decisions']
    locks=load_locks(BASE)
    # Assert ALL dev rows before touching their measured features, even unresolved.
    locks.assert_fit_rows(s['line_id'] for s in slots.values())
    controls=typed_controls(rows(BASE/'controls/approved.jsonl'),rows(BASE/'controls/dash_types.jsonl'))
    # Recover exact offsets and token median digit widths for the approved controls.
    from greekocr.numerics.line_complete import enumerate_line
    from greekocr.numerics.tokens import tokenize
    from greekocr.numerics.dash import digit_widths
    wanted={c['line_id'] for c in controls};byline={}
    run=Path.home()/'Projects/collect-v3-data/run/W1'
    for row in rows(run/'features.jsonl'):
        if row['id'] in wanted:byline[row['id']]=row
    docs_cache={}
    for c in controls:
        row=byline[c['line_id']];slot=next(s for s in enumerate_line(row,locks) if s['slot_id']==c['slot_id'])
        c.update(slot)
        page=json.loads((run/'pages'/(row['page_id']+'.json')).read_text());response=Path(page['response'])
        if str(response) not in docs_cache:
            if sha(response)!=page['response_sha256']:raise ValueError('control response custody')
            docs_cache[str(response)]=json.loads(response.read_text())['document']
        c['dash']=digit_widths(row,tokenize(row['text'])[slot['token_index']],docs_cache[str(response)])

    locks.assert_fit_rows(c['line_id'] for c in controls)
    selected=[];excluded=Counter()
    for d in ds:
        truth=d.get('truth_candidate')
        valid=[r for r in d['reads'] if r['context_status']=='VALID' and r['read_status']=='ok' and r['confidence']=='high' and r['meaning']==truth]
        if truth and (d['status']=='lead_ruled' or len(valid)>=2):
            s=slots[d['slot_id']]
            selected.append(dict(s,truth=truth,truth_source=d['reason']))
        else:excluded[d['reason']]+=1
    for c in controls:
        # The four C1 raised references are explicitly control-only, never N1 fit.
        if c.get('c1_control_only'):
            excluded['c1_control_only']+=1;continue
        s=dict(c,glyph=c['google_glyph'],truth_source='approved_control')
        selected.append(s)
    if len({s['slot_id'] for s in selected})!=len(selected):raise ValueError('duplicate truth slot')
    if any(s['document'] in locks.reserved_docs for s in selected):raise ValueError('reserved fitting document')
    # Document identities are source:item, including controls. No slot-level split.
    docs=sorted({s['document'] for s in selected});random.Random(SEED).shuffle(docs)
    train_docs=set(docs[:len(docs)//2]);held_docs=set(docs)-train_docs
    train=[s for s in selected if s['document'] in train_docs];held=[s for s in selected if s['document'] in held_docs]
    locks.assert_fit_rows(s['line_id'] for s in train+held)
    cfg=fit(train)
    cfg.update(seed=SEED,split_unit='source:item document',fit_documents=sorted(train_docs),
               held_documents=sorted(held_docs),inputs={name:sha(BASE/name) for name in source},
               implementation_sha256=sha(ROOT/'greekocr/numerics/ink_rule.py'))
    rule=freeze(out/'rule.json',cfg)
    held_decisions=[decide(s,rule) for s in held]
    result=metrics([s['truth'] for s in held],held_decisions)
    result.update(rule_hash=rule['rule_hash'],seed=SEED,fit_rows=len(train),fit_documents=len(train_docs),
                  held_documents=len(held_docs),fit_truth=dict(Counter(s['truth'] for s in train)),
                  held_truth=dict(Counter(s['truth'] for s in held)),excluded=dict(excluded),
                  note='C1 control-only references excluded. Geometry-only nothing decisions are not human fitting truth.')
    jsonl(out/'truth.jsonl',[dict(s,split='fit' if s['document'] in train_docs else 'held') for s in selected])
    jsonl(out/'held_decisions.jsonl',held_decisions)
    write(out/'held_metrics.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='confusion_matrix'},indent=2))
if __name__=='__main__':main()
