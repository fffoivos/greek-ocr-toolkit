"""Offline K1 constraint qualification; no model fitting, CTC, or network.

Regenerate S6 from cached alignments to preserve classifier support. Runtime
never receives truth. The audit joins removals to explicit character PRINT
truth, and separately retains the frozen S2--S6 component scoring instrument.
"""
import os
for key in ('VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict
import gzip
import hashlib
import json
from pathlib import Path
import socket
import sys
import time
from PIL import Image
from greekocr.labelfix import ink as I
from greekocr.labelfix.markshape import load_model
from greekocr.labelfix.reading import LineReading, read_ink, apply_constraints, CONSTRAINT_RULES
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.ctc_align import Recognizer, transfer_alignment
from greekocr.labelfix.linemetric import mark_set, score_slots, pooled, summary
from greekocr.labelfix.text import clusters,nfd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/records/labelfix/spellcheck'
sys.path.insert(0,str(ROOT/'scripts/labelfix'))
from greekocr.ops.data_root import input_path as _data_input
from s6_validate import detected
from s6_notes import clause, current_review_specs
from s5_notes import specs


def read(path):
    with (gzip.open if str(path).endswith('.gz') else open)(_data_input(path),'rt') as f:
        return [json.loads(x) for x in f]


def write(path,rows):
    with (gzip.open if str(path).endswith('.gz') else open)(path,'wt') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def atomic(ms):
    if ms is None:return None
    return {p for kind,value in ms for p in (value.split('+') if kind=='compound' else [value])}


def reading_of(line):
    return LineReading(line['reading'],line['recogniser_slots'],line['reading_flags'],line.get('opening_quotes',[]))


def classify(line,receipt):
    truth=next(c['truth'] for c in line['character_checks'] if c['start']==receipt['start'])
    return 'unknown' if truth is None else 'printed' if receipt['part'] in atomic(truth) else 'false'


def filtered_line(line,reading):
    out=dict(line,reading=reading.text,recogniser_slots=reading.slots,
             removed_by_constraint=reading.removed_by_constraint,constraint_flags=reading.constraint_flags)
    out['slots']=[]
    for s in line['slots']:
        rs=[r for r in reading.slots if r.get('component_slot')==s['slot']]
        out['slots'].append(dict(s,detected=sorted({tuple(x) for r in rs for x in detected(r)})))
    return out


def score(lines):
    metric=pooled([score_slots(l['slots']) for l in lines])
    atomic_legacy=pooled([score_slots([dict(s,truth=sorted((('accent' if p in ('acute','grave','circumflex') else 'breathing'),p) if k=='compound' else (k,p) for k,v in s['truth'] for p in (v.split('+') if k=='compound' else [v])) if s['truth'] is not None else None,
              detected=sorted((('accent' if p in ('acute','grave','circumflex') else 'breathing'),p) if k=='compound' else (k,p) for k,v in s['detected'] for p in (v.split('+') if k=='compound' else [v]))) for s in l['slots']]) for l in lines])
    count=Counter()
    for l in lines:
        by={r['start']:r for r in l['recogniser_slots']}
        for c in l['character_checks']:
            t=atomic(c['truth'])
            if t is None:count['unknown_slots']+=1;continue
            d=set(by[c['start']]['parts'])
            if by[c['start']].get('apostrophe'):d.add('apostrophe')
            if by[c['start']].get('unnamed'):d.add('unclassified')
            count['known_slots']+=1;count['tp']+=len(t&d);count['fp']+=len(d-t);count['fn']+=len(t-d)
    return dict(frozen_semantic=metric['total'],frozen_atomic=atomic_legacy['total'],character_atomic=summary(count))


def audit(lines,enabled):
    records=[];outputs=[]
    for line in lines:
        r,removed=apply_constraints(reading_of(line),enabled_rules=enabled,output="normalised")
        outputs.append(filtered_line(line,r))
        for event in removed:
            records.append(dict(event,line_id=line['line_id'],dev=line['dev'],print_status=classify(line,event)))
    return outputs,records


def rule_counts(records):
    return {rule:dict(Counter(r['print_status'] for r in records if r['rule']==rule),total=sum(r['rule']==rule for r in records)) for rule in sorted(CONSTRAINT_RULES)}


def owners(before,after,s4):
    results={};details=[]
    lookup=specs();lookup['8b6b0de9-p000021-l0012']=[('no_top',1,None)]
    for name,path,sp in [('review','owner_notes_review_v16_20261016.jsonl',current_review_specs()),('examples','owner_notes_examples_v10_20261016.jsonl',lookup)]:
        checks=[]
        for note in read(OUT/path):
            lid=note['line_id'];cs=sp.get(lid) if note['note'] else [('no_regression',None,None)]
            row=dict(note,checks=[])
            for kind,target,value in cs:
                a=clause(before[lid],s4[lid],kind,target,value)
                b=clause(after[lid],s4[lid],kind,target,value)
                row['checks'].append(dict(kind=kind,target=target,value=value,before=dict(fixed=a[0],evidence=a[1]),after=dict(fixed=b[0],evidence=b[1])))
            row['before']=all(c['before']['fixed'] for c in row['checks']);row['after']=all(c['after']['fixed'] for c in row['checks']);checks.append(row)
        details+=checks
        results[name]=dict(n=len(checks),before=sum(r['before'] for r in checks),after=sum(r['after'] for r in checks),clauses=sum(len(r['checks']) for r in checks),clauses_before=sum(c['before']['fixed'] for r in checks for c in r['checks']),clauses_after=sum(c['after']['fixed'] for r in checks for c in r['checks']))
    return results,details


def implicit(before,after):
    # Exact slot_of_letters contract from owner_implicit_changes.py: the page
    # script uses maximum CTC overlap with native components, rather than S6's
    # certified character ownership. These are distinct slot namespaces.
    als=load_alignments(ROOT/'.cache/labelfix/align_s0.jsonl')
    slot_maps={}
    for lid in {r['line'] for r in read_implicit()}:
        line=before[lid]
        with Image.open(line['crop']) as image:ci=I.analyse(image)
        comps=sorted((c for c in ci.components if c.role=='letter'),key=lambda c:c.x0)
        al=als[crop_key(line['crop'])];text=nfd(line['recogniser_text'])
        if nfd(al.prediction)!=text:al=transfer_alignment(text,al)
        mapped=[]
        for c in clusters(text):
            if not c.base.isalpha():continue
            x0,x1=al.window(c.start,c.start+1)
            overlaps=[max(0,min(k.x1,x1)-max(k.x0,x0)) for k in comps]
            j=max(range(len(comps)),key=lambda i:overlaps[i]) if comps else None
            mapped.append(j+1 if j is not None and overlaps[j]>0 else None)
        slot_maps[lid]=mapped
    out=[]
    for r in read_implicit():
        row=dict(r)
        if 'slot' not in r:out.append(row);continue
        candidates=[(i,s) for i,s in enumerate(before[r['line']]['recogniser_slots']) if slot_maps[r['line']][i]==r['slot'] and s['base']==r['letter']]
        if len(candidates)!=1:
            row['unresolved']='component/letter mapping is not unique';out.append(row);continue
        i,s=candidates[0];a=after[r['line']]['recogniser_slots'][i]
        old=atomic(mark_set('+'.join(s['parts'])))
        # Reproduce only the exact approved S4 -> S6 changed-letter witnesses.
        from greekocr.labelfix.markshape import mark_class
        baseline=atomic(mark_set(mark_class(clusters(nfd(r['s4']))[0].marks)))
        frozen=atomic(mark_set(mark_class(clusters(nfd(r['s6']))[0].marks)))
        assert old==frozen,(r,s)
        row.update(start=s['start'],slot_source='owner_implicit_changes.slot_of_letters',after_parts=a['parts'],implicit_false_before=sorted(old-baseline),implicit_false_after=sorted(set(a['parts'])-baseline),lost_approved_before=sorted(baseline-old),lost_approved_after=sorted(baseline-set(a['parts'])))
        out.append(row)
    selected=[r for r in out if r['kind'].startswith('REGRESSION')]
    return dict(changed_rows=len(out),implicit_rows=len(selected),unresolved=sum('unresolved' in r or 'slot' not in r for r in selected),
        false_marks_before=sum(len(r.get('implicit_false_before',[])) for r in selected),false_marks_after=sum(len(r.get('implicit_false_after',[])) for r in selected),
        false_slots_before=sum(bool(r.get('implicit_false_before')) for r in selected),false_slots_after=sum(bool(r.get('implicit_false_after')) for r in selected),
        lost_approved_before=sum(len(r.get('lost_approved_before',[])) for r in selected),lost_approved_after=sum(len(r.get('lost_approved_after',[])) for r in selected)),out


def read_implicit():return json.loads((OUT/'owner_implicit_changes_S4_to_S6.json').read_text())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reuse-support','--reuse-raw',dest='reuse_raw',action='store_true');args=parser.parse_args()
    start=time.monotonic()
    def forbidden(*a,**kw):raise RuntimeError('K1 offline cached-alignment-only')
    Recognizer.__init__=forbidden;Recognizer.align_batch=forbidden;socket.socket.connect=forbidden
    frozen=read(OUT/'S6_lines.jsonl.gz');raw=[]
    source_paths=[OUT/'S6_lines.jsonl.gz',ROOT/'docs/records/labelfix/markshape_model_S4.json',
                  ROOT/'docs/records/labelfix/case_model_S5.json',ROOT/'.cache/labelfix/align_s0.jsonl']
    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    if args.reuse_raw:
        receipt=json.loads((OUT/'K1_support_receipt.json').read_text())
        assert receipt['source_sha256']==source_hashes,'stale classifier support cache'
        support={r['line_id']:r['naming'] for r in read(OUT/'K1_support.jsonl.gz')}
        for line in frozen:
            names=support[line['line_id']]
            assert len(names)==len(line['recogniser_slots'])
            raw.append(dict(line,recogniser_slots=[dict(slot,naming=name) for slot,name in zip(line['recogniser_slots'],names)]))
    else:
        als=load_alignments(ROOT/'.cache/labelfix/align_s0.jsonl');model=load_model(ROOT/'docs/records/labelfix/markshape_model_S4.json')
        for n,line in enumerate(frozen):
            with Image.open(line['crop']) as im:ci=I.analyse(im)
            r=read_ink(ci,line['recogniser_text'],als[crop_key(line['crop'])],model,filtered=False)
            assert r.text==line['reading'],line['line_id']
            slots=[]
            for new,old in zip(r.slots,line['recogniser_slots']):
                assert list(new['parts'])==old['parts'] and new['evidence'].to_record()==old['evidence'],line['line_id']
                slots.append(dict(old,naming=asdict(new['naming']) if 'naming' in new else {}))
            raw.append(dict(line,recogniser_slots=slots))
            if n%200==0:print('regenerated',n,round(time.monotonic()-start,1),flush=True)
        write(OUT/'K1_support.jsonl.gz',[dict(line_id=l['line_id'],naming=[r['naming'] for r in l['recogniser_slots']]) for l in raw])
        save(OUT/'K1_support_receipt.json',dict(source_sha256=source_hashes,lines=len(raw)))
    _,proposals=audit(raw,CONSTRAINT_RULES)
    enabled=set(CONSTRAINT_RULES);iterations=[]
    while True:
        outputs,applied=audit(raw,enabled)
        bad={r['rule'] for r in applied if r['print_status']=='printed'}
        iterations.append(dict(enabled=sorted(enabled),printed_conflict_rules=sorted(bad)))
        if not bad:break
        enabled-=bad
    from greekocr.labelfix.reading import APPLIED_CONSTRAINT_RULES
    results=dict(heldout_lines=sum(not l['dev'] for l in raw),dev_lines=sum(l['dev'] for l in raw),candidate_rules=rule_counts(proposals),applied_rules=sorted(enabled),held_back=sorted(CONSTRAINT_RULES-enabled),gate_iterations=iterations,
                 runtime_allowlist_matches=enabled==APPLIED_CONSTRAINT_RULES)
    assert results['runtime_allowlist_matches'],'update the reviewed runtime allowlist to match qualification'
    for name,dev in [('heldout',False),('dev',True)]:
        result=dict(before=score([l for l in raw if l['dev']==dev]),after=score([l for l in outputs if l['dev']==dev]),
            proposed=rule_counts([r for r in proposals if r['dev']==dev]),applied=rule_counts([r for r in applied if r['dev']==dev]))
        results[name]=result
    before={l['line_id']:l for l in raw};after={l['line_id']:l for l in outputs};s4={l['line_id']:l for l in read(OUT/'S4_lines.jsonl.gz')}
    results['owner_notes'],checks=owners(before,after,s4)
    results['owner_implicit'],implicit_rows=implicit(before,after)
    results.update(elapsed_seconds=round(time.monotonic()-start,2),network=False,ctc_forward_passes=0,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'S6_lines.jsonl.gz',OUT/'print_truth_s0.json',ROOT/'docs/records/labelfix/markshape_model_S4.json',ROOT/'docs/records/labelfix/case_model_S5.json',ROOT/'greekocr/labelfix/reading.py',ROOT/'scripts/labelfix/clariden/r1_score.py',OUT/'owner_implicit_changes_S4_to_S6.json',OUT/'owner_notes_review_v16_20261016.jsonl',OUT/'owner_notes_examples_v10_20261016.jsonl']})
    write(OUT/'K1_proposals.jsonl',proposals);write(OUT/'K1_removals.jsonl',applied)
    write(OUT/'K1_printed_conflicts.jsonl',[r for r in proposals if r['print_status']=='printed'])
    write(OUT/'K1_owner_checks.jsonl',checks);save(OUT/'K1_implicit_changes.json',implicit_rows)
    # Compact receipt: source text/evidence remain in frozen S6 + raw support.
    write(OUT/'K1_readings.jsonl.gz',[dict(line_id=l['line_id'],reading=l['reading'],removed_by_constraint=l['removed_by_constraint'],constraint_flags=l['constraint_flags']) for l in outputs])
    save(OUT/'K1_metrics.json',results)
    print(json.dumps({k:results[k] for k in ('heldout_lines','dev_lines','candidate_rules','applied_rules','held_back','owner_notes','owner_implicit','elapsed_seconds')},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
