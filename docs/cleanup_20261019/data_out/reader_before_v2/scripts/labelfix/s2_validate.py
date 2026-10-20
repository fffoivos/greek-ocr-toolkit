"""S2 CPU/offline reproduction: cached alignments only, no recogniser construction.

Run from this worktree: python scripts/labelfix/s2_validate.py
"""
import os
for key in ('VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[key]='1'
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import gzip,json,subprocess,time,types,random,hashlib
from collections import Counter,defaultdict
import numpy as np
from PIL import Image
from greekocr.labelfix import ink as I, markshape as M
from greekocr.labelfix.validate import load_three_way,DEV_BOOKS,lb95
from greekocr.labelfix.sheet import load_alignments,crop_key
from greekocr.labelfix.ctc_align import transfer_alignment
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.spellink import locate
from greekocr.labelfix.text import tokenize,clusters,VOWELS,nfd,nfc
from greekocr.labelfix.linemetric import slot_mapping,score_slots,pooled,mark_set,printed_words,printed_line
from greekocr.labelfix.spellcheck_validate import score_print
BASELINE_REVISION='fb87c8f4e491669a149abca29ba3f2b8262bdf96'
OUT=ROOT/'docs/labelfix/spellcheck';OUT.mkdir(exist_ok=True)

def write(path, rows):
    with open(path,'w') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')

def baseline_module():
    code=subprocess.check_output(['git','show',BASELINE_REVISION+':greekocr/labelfix/ink.py'],cwd=ROOT,text=True)
    mod=types.ModuleType('greekocr.labelfix._s2_baseline');mod.__package__='greekocr.labelfix'
    sys.modules[mod.__name__]=mod;exec(compile(code,'HEAD:ink.py','exec'),mod.__dict__)
    return mod

def main():
    start=time.monotonic(); old=baseline_module()
    lines=load_three_way(0);als=load_alignments(ROOT/'.cache/labelfix/align_s0.jsonl')
    assert all(crop_key(l['crop']) in als for l in lines),'missing cached alignment; no forward allowed'
    truth=json.loads((OUT/'print_truth_s0.json').read_text())
    oldmodel=M.load_model(ROOT/'docs/labelfix/markshape_model.json')
    samples=[];cache=[]
    for idx,l in enumerate(lines):
        with Image.open(l['crop']) as im:ci=I.analyse(im)
        al=transfer_alignment(l['model'],als[crop_key(l['crop'])])
        gm={g.index:m for g,m in pair_tokens(l['google'],l['model'])}
        gh={g.index:h for g,h in pair_tokens(l['google'],l['human'])}
        for g in tokenize(l['google']):
            m,h=gm.get(g.index),gh.get(g.index)
            if not m or not h or not(g.core==m.core==h.core):continue
            for j,cl in enumerate(clusters(g.core)):
                if cl.base not in VOWELS:continue
                label=M.mark_class(cl.marks)
                loc=locate(g,m,al,j)
                if label is None or loc is None:continue
                _,x0,x1,b0,b1=loc
                ev=I.mark_evidence(ci,x0,x1,core_x0=b0,core_x1=b1,base_letter=cl.base)
                if ev.body_source!='letter' or ev.n_letters_in_span!=1:continue
                before=old.mark_evidence(ci,x0,x1,core_x0=b0,core_x1=b1)
                samples.append(dict(line_id=l['line_id'],doc=l['doc'],dev=l['doc'] in DEV_BOOKS,word=m.core,word_index=g.index,cluster=j,
                    base=cl.base,label=label,x=M.features(ev),old_x=M.features(before),composition=[len(ev.above),len(ev.below),[b.source for b in ev.above]],
                    old_composition=[len(before.above),len(before.below),[b.source for b in before.above]]))
        mapping=slot_mapping(l,al,ci,truth)
        apost=I.apostrophe_candidates(ci,[(s['component'],s['base'],s['word_final']) for s in mapping])
        apost_boxes={tuple((b.x0,b.y0,b.x1,b.y1)) for bs in apost.values() for b in bs}
        slots=[]
        for i,s in enumerate(mapping):
            c=s.pop('component'); ev=I.mark_evidence(ci,c.x0,c.x1,base_letter=s['base']);bv=old.mark_evidence(ci,c.x0,c.x1)
            # Elision owns its sign; it must not be credited as next word's breathing.
            ev.above=[b for b in ev.above if (b.x0,b.y0,b.x1,b.y1) not in apost_boxes]
            slots.append(dict(s,slot=i+1,bbox=[c.x0,c.y0,c.x1,c.y1],truth=sorted(s['truth']) if s['truth'] is not None else None,
                x=M.features(ev),before_x=M.features(bv),above=len(ev.above),below=len(ev.below),before_above=len(bv.above),before_below=len(bv.below),
                evidence=ev.to_record(),before_evidence=bv.to_record(),apostrophe=i in apost))
        cache.append(dict(line_id=l['line_id'],doc=l['doc'],dev=l['doc'] in DEV_BOOKS,crop=l['crop'],slots=slots))
        if idx%200==0:print('S2 extraction',idx,len(samples),round(time.monotonic()-start,1),flush=True)
    # Additional train crops: only cached locations and DEV books; no inference, no held books.
    train_seen=train_cached=0
    for raw in open(ROOT/'docs/harvest/collection/v2/import_real_v2_train.jsonl'):
        r=json.loads(raw)
        if r['doc'] not in DEV_BOOKS:continue
        train_seen+=1
        if crop_key(r['crop']) in als:train_cached+=1
    # Freeze architecture and tau on DEV line-separated calibration, never held books.
    dev=[s for s in samples if s['dev']];held=[s for s in samples if not s['dev']]
    dev_ids=sorted({s['line_id'] for s in dev});rng=random.Random(20261016);rng.shuffle(dev_ids)
    cal_ids=set(dev_ids[:max(1,len(dev_ids)//5)])
    fit=[s for s in dev if s['line_id'] not in cal_ids];cal=[s for s in dev if s['line_id'] in cal_ids]
    compounds=[b+'+'+a+z for b in ('psili','dasia') for a in ('acute','grave','circumflex') for z in ('','+subscript')]
    classes=sorted(set(s['label'] for s in fit)|set(compounds))
    model=M.fit_mlp([s['x'] for s in fit],[s['label'] for s in fit],classes,epochs=140,seed=20261016)
    calibration=M.calibrate(model,[s['x'] for s in cal],[s['label'] for s in cal])
    model.tau=calibration['threshold']['tau'] if calibration['threshold'] else 1.0
    counts=Counter(s['label'] for s in fit)
    model.meta=dict(iteration='S2',fit_books=list(DEV_BOOKS),fit_lines=sorted(set(dev_ids)-cal_ids),calibration_lines=sorted(cal_ids),
                    fit_counts=dict(counts),calibration=calibration,heldout_used_for_selection=False,epochs=140,seed=20261016)
    model.save(ROOT/'docs/labelfix/markshape_model_S2.json')
    with gzip.open(ROOT/'docs/labelfix/markshape_samples_S2.jsonl.gz','wt') as f:
        for s in samples:f.write(json.dumps(s,ensure_ascii=False)+'\n')
    P=model.probs([s['x'] for s in held]);pred=P.argmax(1);conf=P.max(1)
    per={}
    for i,c in enumerate(classes):
        tt=np.array([s['label']==c for s in held]);sel=(pred==i)&(conf>=model.tau)
        per[c]=dict(fit=counts[c],dev_calibration=sum(s['label']==c for s in cal),held=int(tt.sum()),
            recall=float((pred[tt]==i).mean()) if tt.any() else None,
            precision_at_tau=float(tt[sel].mean()) if sel.any() else None,coverage=float(sel.sum()/max(1,len(held))),n_at_tau=int(sel.sum()))
    for l in cache:
        for s in l['slots']:
            before=oldmodel.predict(s['before_x'])[0] if s['before_above'] or s['before_below'] else 'none'
            after=model.predict(s['x'])[0] if s['above'] or s['below'] else 'none'
            def physical(cls,a,b):
                parts=cls.split('+') if cls!='none' else []
                parts=[p for p in parts if (p=='subscript' and b) or (p!='subscript' and a)]
                # A nonempty unclassified blob is a false/missed mark, never silently none.
                ms=mark_set('+'.join(parts))
                if a and not any(k!='subscript' for k,v in ms):ms.add(('accent','unclassified'))
                if b and not any(k=='subscript' for k,v in ms):ms.add(('subscript','subscript'))
                return ms
            s['before']=sorted(physical(before,s['before_above'],s['before_below']))
            s['detected']=sorted(physical(after,s['above'],s['below']) | ({('apostrophe','apostrophe')} if s['apostrophe'] else set()))
            s['before_cls']=before;s['cls']=after
        l['before_metric']=score_slots([dict(s,detected=s['before']) for s in l['slots']]);l['metric']=score_slots(l['slots'])
    with gzip.open(OUT/'S2_lines.jsonl.gz','wt') as f:
        for l in cache:f.write(json.dumps(l,ensure_ascii=False)+'\n')
    heldlines=[l for l in cache if not l['dev']]
    before=pooled([l['before_metric'] for l in heldlines]);after=pooled([l['metric'] for l in heldlines])
    asc=defaultdict(lambda:Counter())
    byid={l['line_id']:l for l in lines}
    for l in cache:
        source=byid[l['line_id']]
        gs=tokenize(source['google']);gm={g.index:m for g,m in pair_tokens(source['google'],source['model'])};gh={g.index:h for g,h in pair_tokens(source['google'],source['human'])}
        for s in l['slots']:
            # Agreement-only zero-mark slots, excludes adjudicated disagreements.
            wi=s['word']
            if wi is None or not gm.get(wi) or not gh.get(wi) or not(gs[wi].core==gm[wi].core==gh[wi].core):continue
            if s['truth']!=[]:continue
            base=s['base'];key='capitals' if base.isupper() else base
            asc[key]['n']+=1;asc[key]['before']+=bool(s['before_above']);asc[key]['after']+=bool(s['above'])
    fixed=OUT/'heldout_sample60.txt'
    ids=sorted(l['line_id'] for l in heldlines)
    sample=random.Random(20261016).sample(ids,60)
    if fixed.exists():assert fixed.read_text().splitlines()==sample,'fixed sample drift'
    else:fixed.write_text('\n'.join(sample)+'\n')
    selected=sample+[l['line_id'] for l in heldlines if l['line_id'] not in sample and any(s['before']!=s['detected'] for s in l['slots'])]
    write(OUT/'S2_sheet_lines.jsonl',[dict(line_id=x) for x in selected[:140]])
    (OUT/'S2_sheet_overflow.txt').write_text('\n'.join(selected[140:])+'\n')
    # Old stored samples include labels/classes filtered by the old min-class policy.
    with gzip.open(ROOT/'docs/labelfix/markshape_samples.jsonl.gz','rt') as f:old_samples=[json.loads(x) for x in f]
    og=defaultdict(list);ng=defaultdict(list)
    for s in old_samples:og[(s['line_id'],s['word'],s['base'],s['label'])].append(s)
    for s in samples:ng[(s['line_id'],s['word'],s['base'],s['label'])].append(s)
    paired=changed=0
    for key,ss in og.items():
        for a,b in zip(ss,ng[key]):paired+=1;changed+=a['x']!=b['x']
    result=dict(before=before,after=after,per_class=per,ascender=dict(asc),samples=len(samples),old_samples=len(old_samples),paired=paired,changed_features=changed,
        changed_composition=sum(s['composition']!=s['old_composition'] for s in samples),labels_changed=0,train_dev_lines=train_seen,train_cached=train_cached,
        training_policy='DEV books only; fixed MLP 140 epochs; 20% DEV lines calibrate tau; held-out never selects model/threshold',
        tau=model.tau,elapsed_seconds=round(time.monotonic()-start,2),ctc_forward_passes=0,alignment_lines=len(lines),heldout_lines=len(heldlines),
        iteration=subprocess.check_output(['git','rev-parse','--short','HEAD'],text=True).strip()+'dirty')
    (OUT/'S2_metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('S2 extraction/classifier complete',result['elapsed_seconds'],flush=True)
if __name__=='__main__':main()
