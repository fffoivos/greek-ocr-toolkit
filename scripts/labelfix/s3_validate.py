"""S3 offline CPU evaluation; fit/calibrate DEV first, then evaluate frozen held-out books.

No recognizer is imported or constructed. Original S2 artifacts are read-only.
"""
from greekocr.ops.data_root import input_path as _data_input
import os
for key in ('VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[key]='1'
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
import argparse, gzip, hashlib, json, random, subprocess, time
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from PIL import Image
from greekocr.labelfix import ink as I, markshape as M
from greekocr.labelfix.validate import load_three_way, DEV_BOOKS
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.ctc_align import transfer_alignment
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.spellink import locate
from greekocr.labelfix.text import tokenize, clusters, VOWELS
from greekocr.labelfix.linemetric import slot_mapping, score_slots, pooled, mark_set
from greekocr.labelfix.owner_slots import overlap_slots
ROOT=Path(__file__).resolve().parents[2]; O=ROOT/'docs/records/labelfix/spellcheck'


def read(p):
    with (gzip.open if str(p).endswith('.gz') else open)(_data_input(p),'rt') as f:
        return [json.loads(x) for x in f]


def write(p, rows):
    with (gzip.open if str(p).endswith('.gz') else open)(p,'wt') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')


def physical(cls,a,b):
    parts=cls.split('+') if cls!='none' else []
    parts=[p for p in parts if (p=='subscript' and b) or (p!='subscript' and a)]
    ms=mark_set('+'.join(parts))
    if a and not any(k!='subscript' for k,v in ms):ms.add(('accent','unclassified'))
    if b and not any(k=='subscript' for k,v in ms):ms.add(('subscript','subscript'))
    return sorted(ms)


def extract(l,al,truth,old,collect=False):
    with Image.open(l['crop']) as im:ci=I.analyse(im)
    mapping=slot_mapping(l,al,ci,truth)
    apost=I.apostrophe_candidates(ci,[(s['component'],s['base'],s['word_final']) for s in mapping])
    apost_boxes={(b.x0,b.y0,b.x1,b.y1) for bs in apost.values() for b in bs}
    slots=[]
    for i,s in enumerate(mapping):
        c=s['component'];kw={}
        if s.get('locator_span'):
            b0,b1=s['locator_span']
            u0,u1,_,n=I.snap_body(ci,b0,b1,vowel=s['base'] in VOWELS)
            # A second component with another character owner is not a split vowel.
            if u1-u0<=1.6*ci.xh and not any(j!=i and q['base'] and I._overlap(q['component'].x0,q['component'].x1,u0,u1)>0 for j,q in enumerate(mapping)):
                kw=dict(core_x0=b0,core_x1=b1)
        ev=I.mark_evidence(ci,c.x0,c.x1,base_letter=s['base'],**kw)
        ev.above=[b for b in ev.above if (b.x0,b.y0,b.x1,b.y1) not in apost_boxes]
        bs=old['slots'][i]
        assert bs['bbox']==[c.x0,c.y0,c.x1,c.y1], 'component topology changed; explicit remap required'
        slots.append(dict((k,v) for k,v in s.items() if k!='component') | dict(slot=i+1,bbox=bs['bbox'],truth=bs['truth'],
            before=bs['detected'],before_cls=bs['cls'],before_evidence=bs['evidence'],before_above=bs['above'],before_below=bs['below'],
            x=M.features(ev),above=len(ev.above),below=len(ev.below),evidence=ev.to_record(),apostrophe=i in apost,
            unknown_kinds=['subscript'] if ev.clipped_bottom else []))
    samples=[]
    if collect:
        al=transfer_alignment(l['model'],al)
        gm={g.index:m for g,m in pair_tokens(l['google'],l['model'])};gh={g.index:h for g,h in pair_tokens(l['google'],l['human'])}
        for g in tokenize(l['google']):
            m,h=gm.get(g.index),gh.get(g.index)
            if not m or not h or not(g.core==m.core==h.core):continue
            for j,cl in enumerate(clusters(g.core)):
                if cl.base not in VOWELS:continue
                label=M.mark_class(cl.marks);loc=locate(g,m,al,j)
                if label is None or loc is None:continue
                _,x0,x1,b0,b1=loc
                ev=I.mark_evidence(ci,x0,x1,core_x0=b0,core_x1=b1,base_letter=cl.base)
                if ev.body_source!='letter' or ev.n_letters_in_span!=1:continue
                samples.append(dict(line_id=l['line_id'],doc=l['doc'],dev=True,word=m.core,word_index=g.index,cluster=j,base=cl.base,label=label,x=M.features(ev)))
    return dict(line_id=l['line_id'],doc=l['doc'],dev=l['doc'] in DEV_BOOKS,crop=l['crop'],slots=slots),samples


def classify(lines,model):
    for l in lines:
        for s in l['slots']:
            s['cls']=model.predict(s['x'])[0] if s['above'] or s['below'] else 'none'
            s['detected']=physical(s['cls'],s['above'],s['below'])
            if s['apostrophe']:s['detected'].append(['apostrophe','apostrophe'])
            s['truth']=sorted(s['truth']) if s['truth'] is not None else None
        l['before_metric']=score_slots([dict(s,detected=s['before']) for s in l['slots']])
        l['metric']=score_slots(l['slots'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dev-only',action='store_true');args=parser.parse_args()
    start=time.monotonic();lines=load_three_way(0);als=load_alignments(ROOT/'.cache/labelfix/align_s0.jsonl')
    assert all(crop_key(l['crop']) in als for l in lines),'cached alignments required; no forward allowed'
    truth=json.loads((O/'print_truth_s0.json').read_text());old={l['line_id']:l for l in read(O/'S2_lines.jsonl.gz')}
    dev=[];samples=[]
    for l in lines:
        if l['doc'] not in DEV_BOOKS:continue
        row,ss=extract(l,als[crop_key(l['crop'])],truth,old[l['line_id']],True);dev.append(row);samples.extend(ss)
    # Same line-separated DEV partition, architecture and epoch count as S2.
    ids=sorted({s['line_id'] for s in samples});random.Random(20261016).shuffle(ids);cal_ids=set(ids[:max(1,len(ids)//5)])
    fit=[s for s in samples if s['line_id'] not in cal_ids];cal=[s for s in samples if s['line_id'] in cal_ids]
    compounds=[b+'+'+a+z for b in ('psili','dasia') for a in ('acute','grave','circumflex') for z in ('','+subscript')]
    classes=sorted(set(s['label'] for s in fit)|set(compounds))
    model=M.fit_mlp([s['x'] for s in fit],[s['label'] for s in fit],classes,epochs=140,seed=20261016)
    calibration=M.calibrate(model,[s['x'] for s in cal],[s['label'] for s in cal]);model.tau=calibration['threshold']['tau'] if calibration['threshold'] else 1.
    model.meta=dict(iteration='S3',fit_books=list(DEV_BOOKS),fit_lines=sorted(set(ids)-cal_ids),calibration_lines=sorted(cal_ids),fit_counts=dict(Counter(s['label'] for s in fit)),calibration=calibration,heldout_used_for_selection=False,epochs=140,seed=20261016)
    model.save(ROOT/'docs/records/labelfix/markshape_model_S3.json');write(ROOT/'docs/records/labelfix/markshape_samples_S3.jsonl.gz',samples)
    classify(dev,model)
    print('DEV frozen',json.dumps(dict(before=pooled([l['before_metric'] for l in dev])['total'],after=pooled([l['metric'] for l in dev])['total'])),flush=True)
    write(O/'S3_dev_lines.jsonl.gz',dev)
    if args.dev_only:return
    frozen_hash=hashlib.sha256((ROOT/'docs/records/labelfix/markshape_model_S3.json').read_bytes()).hexdigest()
    held=[]
    for l in lines:
        if l['doc'] in DEV_BOOKS:continue
        row,_=extract(l,als[crop_key(l['crop'])],truth,old[l['line_id']]);held.append(row)
    classify(held,model);allrows=dev+held;write(O/'S3_lines.jsonl.gz',allrows)
    per={}
    for cls in classes:
        hs=[s for l in held for s in l['slots'] if s['truth'] is not None and set(map(tuple,s['truth']))==mark_set(cls)]
        per[cls]=dict(fit=sum(s['label']==cls for s in fit),dev_calibration=sum(s['label']==cls for s in cal),held_slots=len(hs),held_exact=sum(set(map(tuple,s['detected']))==mark_set(cls) for s in hs))
    bybook={d:dict(before=pooled([l['before_metric'] for l in held if l['doc']==d]),after=pooled([l['metric'] for l in held if l['doc']==d])) for d in sorted({l['doc'] for l in held})}
    # Identical baseline speck exposure: known non-subscript slots with an S1
    # below blob. This is the S2 stratum, not a new favourable denominator.
    specks=[s for l in held for s,bs in zip(l['slots'],old[l['line_id']]['slots']) if s['truth'] is not None and not any(k=='subscript' for k,v in s['truth']) and bs['before_below'] and 'subscript' not in s['unknown_kinds']]
    speck=dict(n=len(specks),before_rejected=sum(not any(k=='subscript' for k,v in s['before']) for s in specks),after_rejected=sum(not any(k=='subscript' for k,v in s['detected']) for s in specks))
    asc={}
    for split,ls in [('held-out',held),('all',allrows)]:
        ss=[s for l in ls for s in l['slots'] if s['truth']==[] and (s['base'] in 'βδζθλξφψ' or s['base'].isupper())]
        asc[split]=dict(n=len(ss),before=sum(bool(s['before_above']) for s in ss),after=sum(bool(s['above']) for s in ss))
    result=dict(iteration='S3',before=pooled([l['before_metric'] for l in held]),after=pooled([l['metric'] for l in held]),dev_before=pooled([l['before_metric'] for l in dev]),dev_after=pooled([l['metric'] for l in dev]),per_book=bybook,per_class=per,speck=speck,ascender=asc,tau=model.tau,ctc_forward_passes=0,cpu_only=True,network=False,heldout_used_for_selection=False,heldout_lines=len(held),dev_lines=len(dev),elapsed_seconds=time.monotonic()-start,model_sha256=frozen_hash,head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
    (O/'S3_metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('S3 held-out',json.dumps(dict(before=result['before'],after=result['after'],speck=speck)),flush=True)


if __name__=='__main__':main()
