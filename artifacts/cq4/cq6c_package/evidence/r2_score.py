"""R2 union-slot, exact-head scoring and symmetric versioned truth overlays.

Input: JSONL lines with print_slots (base, targets[4], id, unknown), and
prediction JSONL (line_id, start, base, factors). All alphabetic base slots,
including unmarked consonants, participate in case-preserving alignment.
Physical-slot scoring remains a separately invoked, unchanged R1 instrument.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import argparse
import json
from pathlib import Path
import numpy as np
from scripts.labelfix.clariden.r1_common import HEADS, MARKS, clusters, compose, factors, nfd, rows, sha256, write_json, write_rows, text_functions
from scripts.labelfix.clariden import r1_score
from greekocr.labelfix.release_gate import policy_binding, bind_runtime


def truth_lines(path):
    """Canonical union input or frozen physical lines; never infer truth from Google."""
    result=list(rows(path))
    for line in result:
        if 'print_slots' in line: continue
        line['print_slots']=[]
        for s in line['slots']:
            # Physical truth stores breathing+accent as one compound atom.
            # Expand it before factorisation so named compounds cannot become none.
            marks=None if s['truth'] is None else [MARKS[part] for k,v in s['truth']
                for part in (v.split('+') if k=='compound' else [v]) if part in MARKS]
            target=None if marks is None else factors(marks)
            line['print_slots'].append(dict(id=f"{line['line_id']}:s{s['slot']}",base=s['base'],
                targets=target,unknown=list(HEADS) if target is None else [],physical_slot=s['slot']))
    return result


def apply_overlay(lines,overlay):
    out=deepcopy(lines);entries={e['id']:e for e in overlay['entries']};seen=set()
    if len(entries)!=len(overlay['entries']): raise ValueError('duplicate overlay id')
    for l in out:
        for s in l['print_slots']:
            e=entries.get(s['id'])
            if e:
                if s['targets']!=e['previous_tuple']: raise ValueError('overlay previous tuple mismatch')
                s['targets']=e['new_tuple'];s['unknown']=e.get('unknown',[]);seen.add(s['id'])
                # The physical continuity adapter sees the same known overlay heads.
                if 'slots' in l:
                    for physical in l['slots']:
                        if physical['slot']==s.get('physical_slot'):
                            physical['truth']=None if e.get('unknown') else sorted(r1_score.mark_set(compose(e['new_tuple'])))
    return out,dict(version=overlay['version'],applied=sorted(seen),out_of_scope=sorted(set(entries)-seen))


def union_records(lines,predictions):
    byline=defaultdict(list);seen=set()
    for p in predictions:
        p=deepcopy(p);cov=p.get('coverage',{});validity=p.get('crop_validity',{})
        p.setdefault('fused',cov.get('fused',validity.get('fused',False)))
        p.setdefault('clipped',bool(validity.get('clipped_top') or validity.get('clipped_bottom')))
        p.setdefault('localisation_unknown',cov.get('evidence_state')=='UNKNOWN' or bool(cov.get('uncertainty')))
        if cov: p.setdefault('unscored',not cov.get('scored',True))
        key=p['line_id'],p['start']
        if key in seen: raise ValueError('duplicate prediction slot')
        seen.add(key);byline[p['line_id']].append(p)
    if set(byline)-{l['line_id'] for l in lines}: raise ValueError('prediction lines outside truth cohort')
    result=[]
    align=text_functions()['align_chars']
    for l in lines:
        truth=[s for s in l['print_slots'] if s['base'].isalpha()]
        pred=sorted(byline[l['line_id']],key=lambda p:p['start'])
        # Prediction exporters can supply full recogniser context. Preserve
        # missing reader slots as none, rather than aligning a vowel-only string.
        if l.get('recogniser_text'):
            loc={p['start']:p for p in pred}
            context=[c for c in clusters(nfd(l['recogniser_text'])) if c.base.isalpha()]
            if any(p['start'] not in {c.start for c in context} for p in pred): raise ValueError('prediction start outside recogniser')
            pred=[dict(loc.get(c.start,dict(start=c.start,base=c.base,factors=[0]*4,unscored=True)),line_id=l['line_id']) for c in context]
        a=''.join(s['base'] for s in truth);b=''.join(s['base'] for s in pred)
        for ti,pi in align(a,b):
            # A base substitution has no shared slot: one omitted, one inserted.
            pairs=[(ti,None),(None,pi)] if ti is not None and pi is not None and a[ti]!=b[pi] else [(ti,pi)]
            for t,p in pairs:
                ts=truth[t] if t is not None else None; ps=pred[p] if p is not None else None
                # An inserted recogniser letter has no frozen physical truth.
                # Treat it like print-truth None, never as a known unmarked slot.
                y=ts['targets'] if ts else None; unknown=ts.get('unknown',[]) if ts else []
                if y is None: unknown=list(HEADS);y=[None]*4
                result.append(dict(line_id=l['line_id'],doc=l['doc'],source=l.get('source',l['doc'].split(':')[0]),
                    id=ts['id'] if ts else f"{l['line_id']}:insert:{p}:{ps['base']}",
                    base=(ts or ps)['base'],
                    truth=y,prediction=ps['factors'] if ps else [0]*4,unknown=unknown,
                    coverage=p is not None and not ps.get('unscored',False),
                    unmatched_print=p is None,inserted_prediction=t is None,
                    localisation=(ts or {}).get('localisation_unknown',False) or (ps or {}).get('localisation_unknown',False),
                    fused=(ps or {}).get('fused',False),clipped=(ps or {}).get('clipped',False),
                    inclusion_weight=float(l.get('inclusion_weight',1.))))
    return result


def ratio(a,b): return a/b if b else None


def summarize(records):
    heads={}; exact={}; atomic=Counter();states=Counter();tuples=Counter({k:0 for k in ('all_denominator','all_correct','marked_denominator','marked_correct')});compound=Counter()
    inserted=[r for r in records if r['inserted_prediction']]
    def marked_counts(slots):
        return dict(total=sum(any(r['prediction']) for r in slots),
            by_head={name:sum(bool(r['prediction'][h]) for r in slots) for h,name in enumerate(HEADS)})
    # Raw slot counts, separate from weighted scoring; a multi-mark letter
    # counts once in total and once on each marked head.
    inserted_marked=marked_counts(inserted)
    inserted_marked['by_letter']={base:marked_counts([r for r in inserted if r['base']==base])
        for base in sorted({r['base'] for r in inserted})}
    for r in records:
        states['union_slots']+=1
        for k in ('coverage','localisation','fused','clipped','unmatched_print','inserted_prediction'): states[k]+=int(r[k])
        states['UNKNOWN']+=bool(r['unknown']);w=r['inclusion_weight']
        if w<=0 or not np.isfinite(w): raise ValueError('invalid inclusion weight')
        if not r['unknown']:
            right=r['truth']==r['prediction'];marked=any(r['truth'])
            tuples['all_denominator']+=w;tuples['all_correct']+=w*right
            tuples['marked_denominator']+=w*marked;tuples['marked_correct']+=w*(marked and right)
        # Dialytika-only and dialytika+acute are distinct exact compound values.
        if not set(r['unknown']) & {'dialytika','accent'}:
            def dc(y): return 'none' if not y[2] else 'dialytika-only' if y[1]==0 else 'dialytika+'+HEADS['accent'][y[1]]
            compound[(dc(r['truth']),dc(r['prediction']))]+=w
    for h,(name,values) in enumerate(HEADS.items()):
        matrix={v:{q:0. for q in values} for v in values};unknown=0
        for r in records:
            if name in r['unknown']: unknown+=1;continue
            matrix[values[r['truth'][h]]][values[r['prediction'][h]]]+=r['inclusion_weight']
        cells={}
        for v in values[1:]:
            tp=matrix[v][v];fn=sum(matrix[v].values())-tp;fp=sum(row[v] for row in matrix.values())-tp
            total=sum(sum(row.values()) for row in matrix.values());tn=total-tp-fp-fn
            cell=dict(tp=tp,fp=fp,fn=fn,tn=tn,positive_opportunities=tp+fn,negative_opportunities=fp+tn,
                precision=ratio(tp,tp+fp),recall=ratio(tp,tp+fn),false_additions_per_1000_negative=1000*fp/(fp+tn) if fp+tn else None)
            cells[v]=cell
            for k in ('tp','fp','fn','tn'): atomic[k]+=cell[k]
        heads[name]=dict(confusion=matrix,values=cells,unknown=unknown)
    atomic.update(positive_opportunities=atomic['tp']+atomic['fn'],negative_opportunities=atomic['fp']+atomic['tn'])
    atomic=dict(atomic)
    atomic.update(precision=ratio(atomic['tp'],atomic['tp']+atomic['fp']),recall=ratio(atomic['tp'],atomic['tp']+atomic['fn']),
        false_additions_per_1000_negative=ratio(1000*atomic['fp'],atomic['fp']+atomic['tn']))
    return dict(heads=heads,atomic=dict(atomic),states=dict(states),inserted_slots=len(inserted),
        inserted_slots_marked=inserted_marked,composed_tuple=dict(tuples,
        accuracy_all=ratio(tuples['all_correct'],tuples['all_denominator']),accuracy_marked=ratio(tuples['marked_correct'],tuples['marked_denominator'])),
        dialytika_compound_confusion={a:{b:compound[a,b] for b in ('none','dialytika-only','dialytika+acute','dialytika+grave','dialytika+circumflex')} for a in ('none','dialytika-only','dialytika+acute','dialytika+grave','dialytika+circumflex')})


def score(lines,predictions):
    records=union_records(lines,predictions);groups={}
    for key in ('source','doc'):
        gs={v:summarize([r for r in records if r[key]==v]) for v in sorted({r[key] for r in records})}
        macro={metric:dict(mean=float(np.mean([g['atomic'][metric] for g in gs.values() if g['atomic'][metric] is not None])) if any(g['atomic'][metric] is not None for g in gs.values()) else None,
            defined=sum(g['atomic'][metric] is not None for g in gs.values()),total=len(gs)) for metric in ('precision','recall')}
        groups[key]=dict(groups=gs,macro=macro,micro=summarize(records))
    return dict(micro=summarize(records),groups=groups),records


def paired(old,new,replicates=2000,seed=20261017,per_head=True):
    aa={r['id']:r for r in old};bb={r['id']:r for r in new};ledger=[];bydoc=defaultdict(lambda:np.zeros(2))
    for key in sorted(set(aa)|set(bb)):
        a=aa.get(key);b=bb.get(key);r=a or b
        if (a and a['unknown']) or (b and b['unknown']): continue
        ar=a['truth']==a['prediction'] if a else True;br=b['truth']==b['prediction'] if b else True
        if ar!=br: ledger.append(dict(id=key,doc=r['doc'],inclusion_weight=r['inclusion_weight'],direction='old_right_new_wrong' if ar else 'old_wrong_new_right'))
        bydoc[r['doc']]+=np.array([int(br)-int(ar),1])*r['inclusion_weight']
    rng=np.random.default_rng(seed);docs=sorted(bydoc);values=np.asarray([bydoc[d] for d in docs]);est=[]
    for _ in range(replicates):
        total=values[rng.integers(len(docs),size=len(docs))].sum(0) if docs else [0,0]
        if total[1]: est.append(total[0]/total[1])
    total=values.sum(0) if docs else [0,0]
    result=dict(ledger=ledger,counts=dict(Counter(r['direction'] for r in ledger)),documents=len(docs),
        weighted_accuracy_delta=ratio(total[0],total[1]),document_cluster_95_interval=np.quantile(est,[.025,.975]).tolist() if est else None,
        bootstrap_replicates=replicates,seed=seed,inclusion_weights='original line weights retained within resampled documents')
    if per_head:
        result['by_head']={}
        for h,name in enumerate(HEADS):
            def project(records):
                return [dict(r,truth=[r['truth'][h]],prediction=[r['prediction'][h]],unknown=[name] if name in r['unknown'] else []) for r in records]
            result['by_head'][name]=paired(project(old),project(new),replicates,seed,False)
    return result


def continuity(frozen,meta,predictions):
    mapped,mapping=r1_score.map_lines(frozen,meta,{(p['line_id'],p['start']):p for p in predictions},filtered=False)
    return dict(instrument='unchanged R1 physical slots, raw',summary=r1_score.summaries(mapped),mapping=mapping,
        historical_apostrophe_fn=206,four_head_excludes_apostrophes=True)


def pipeline(lines,predictions,runtimes,mode='FULL'):
    """Run the exact frozen whole-line release policy for both checkpoints."""
    from scripts.labelfix.clariden.l1_common import overlay
    byline=defaultdict(list)
    for p in predictions: byline[p['line_id']].append(p)
    output=[]; counts=Counter();subscript=Counter()
    for line in lines:
        rt=deepcopy(runtimes[line['line_id']]);rt.pop('evidence_sha256',None);rt['r1_predictions']=byline[line['line_id']]
        rt=bind_runtime(rt)
        binding=dict(detector='frozen-runtime',r1_sha256='prediction input hash bound by scorer receipt',policy_sha256=policy_binding()['sha256'])
        release=overlay(dict(id=line['line_id'],label=line['google'],script_class='greek_poly'),rt,mode.lower(),binding)
        output.append(release);counts['lines']+=1;counts['abstained_lines']+=release['status']=='hold'
        selected=release.get('label',line['google']);g=clusters(nfd(line['google']));o=clusters(nfd(selected));truth=line['print_slots']
        # Frozen policy guarantees base preservation; align original against print
        # separately so Google insertions cannot inherit an unrelated print label.
        pmap={j:i for i,j in text_functions()['align_chars'](''.join(s['base'] for s in truth),''.join(c.base for c in g)) if j is not None}
        if [c.base for c in g]!=[c.base for c in o]: raise ValueError('pipeline changed bases')
        for j,(gc,oc) in enumerate(zip(g,o)):
            gy=factors(gc.marks);oy=factors(oc.marks)
            if gy is None or oy is None or gy==oy: continue
            ti=pmap.get(j);ts=truth[ti] if ti is not None else None
            counts['changed_slots']+=1
            for h,name in enumerate(HEADS):
                if gy[h]==oy[h]: continue
                counts['accepted_edits']+=1
                if ts is None or name in ts.get('unknown',[]) or ts['targets'] is None:
                    counts['unknown_edits']+=1;continue
                y=ts['targets'];right=oy[h]==y[h]
                action='addition' if gy[h]==0 else 'deletion' if oy[h]==0 else 'substitution'
                counts[action+'_correct' if right else action+'_incorrect']+=1
                counts['recovered_google_errors']+=right and gy[h]!=y[h]
                counts['regressions_google_right']+=not right and gy[h]==y[h]
                if h==3 and oy[h] and not gy[h]: subscript['correct' if right else 'incorrect']+=1
    known=counts['accepted_edits']-counts['unknown_edits']
    return dict(policy=policy_binding(),mode=mode,counts=dict(counts),edit_unit='changed head on an accepted whole line',precision=ratio(counts['addition_correct']+counts['substitution_correct']+counts['deletion_correct'],known),
        yield_per_line=ratio(counts['recovered_google_errors'],counts['lines']),abstention=ratio(counts['abstained_lines'],counts['lines']),
        subscript_addition=dict(subscript,precision=ratio(subscript['correct'],sum(subscript.values()))),overlays=output)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('truth','baseline','candidate','out'): ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--overlay',type=Path,action='append',required=True)
    ap.add_argument('--sources',type=Path,help='JSONL line_id/google for frozen correction-pipeline view')
    ap.add_argument('--physical-metadata',type=Path);ap.add_argument('--runtime',type=Path)
    ap.add_argument('--policy-mode',choices=['FULL','PRESENCE','ENSEMBLE_AB','ENSEMBLE_AE'],default='FULL')
    a=ap.parse_args();lines=truth_lines(a.truth);old=list(rows(a.baseline));new=list(rows(a.candidate));out={}
    runtime={r['id']:r for r in rows(a.runtime)} if a.runtime else None
    if a.sources:
        sources={r['line_id']:r['google'] for r in rows(a.sources)}
        for l in lines: l['google']=sources[l['line_id']]
    if a.physical_metadata:
        md=r1_score.metadata(a.physical_metadata)
        for p in old+new:
            c=md.get(p['line_id'],{}).get('coverage_by_start',{}).get(p['start'])
            if c: p.setdefault('coverage',c)
    for path in a.overlay:
        ov=json.loads(path.read_text());ll,version=apply_overlay(lines,ov)
        bs,br=score(ll,old);cs,cr=score(ll,new)
        result=dict(overlay=dict(version,sha256=sha256(path)),baseline=bs,candidate=cs,paired=paired(br,cr))
        if a.physical_metadata:
            meta=r1_score.metadata(a.physical_metadata)
            result['continuity']={k:continuity(ll,meta,p) for k,p in [('baseline',old),('candidate',new)]}
        else: result['continuity']=dict(status='requires --physical-metadata and frozen physical lines',historical_apostrophe_fn=206)
        if runtime: result['pipeline']={k:pipeline(ll,p,runtime,a.policy_mode) for k,p in [('baseline',old),('candidate',new)]}
        else: result['pipeline']=dict(status='requires --runtime; no policy result inferred from raw slots')
        out[ov['version']]=result
    a.out.mkdir(parents=True,exist_ok=True)
    write_json(a.out/'raw_and_continuity.json',{k:{q:v for q,v in r.items() if q!='pipeline'} for k,r in out.items()})
    write_json(a.out/'fixed_pipeline.json',{k:r['pipeline'] for k,r in out.items()})
    write_json(a.out/'score_receipt.json',dict(inputs={str(p):sha256(p) for p in [a.truth,a.baseline,a.candidate,*a.overlay]+([a.runtime] if a.runtime else [])+([a.sources] if a.sources else [])},
        policy=policy_binding(),code_sha256=sha256(__file__),outputs={p.name:sha256(p) for p in a.out.glob('*.json') if p.name!='score_receipt.json'}))

if __name__=='__main__': main()
