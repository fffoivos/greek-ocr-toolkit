"""Map R1 samples to frozen reading.recogniser_slots; reuse S4 PRINT slot scoring.

Local, cached-text evaluation only. Does not open crops, run CTC, or fit anything.
S5 artifacts can be supplied by the track lead once available in this worktree.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import itertools
import hashlib
import json
from pathlib import Path
from collections import Counter
from scripts.labelfix.clariden.r1_common import (ARMS,HEADS,LETTERS,MARKS,clusters,compose,nfd,rows,sha256,verify_receipt,write_json,write_rows)
from scripts.labelfix.clariden.r1_owner import evaluate as owner_evaluate
from greekocr.labelfix.linemetric import mark_set,score_slots,pooled
from greekocr.labelfix.reading import LineReading, apply_constraints


def metric(slots):return score_slots([dict(s,unknown_kinds=[]) for s in slots])
def frozen_metric(lines):return pooled([metric(l['slots']) for l in lines])
def pct(x):return f'{x:.2%}' if x is not None else '—'
def prf(m):return ' / '.join(pct(m.get(k)) for k in ('precision','recall','f1'))


def prediction_map(path,meta,*,extraction=None,checkpoint=None):
    receipt=json.loads(path.with_suffix('.receipt.json').read_text())
    if receipt['prediction_sha256']!=sha256(path):raise ValueError('prediction hash mismatch')
    if extraction is None or checkpoint is None:
        raise ValueError('explicit extraction and checkpoint bindings required')
    ex=Path(extraction);checkpoint=Path(checkpoint)
    er=json.loads((ex/'extraction_receipt.json').read_text())
    for name,actual in [('extraction_receipt_sha256',sha256(ex/'extraction_receipt.json')),
                        ('input_index_sha256',sha256(ex/'index.npy')),
                        ('checkpoint_sha256',sha256(checkpoint))]:
        if receipt.get(name)!=actual:raise ValueError('prediction '+name+' binding mismatch')
    if er['sha256'].get('index.npy')!=receipt['input_index_sha256']:raise ValueError('index differs from extraction receipt')
    pred={}
    for r in rows(path):
        key=(r['line_id'],r['start'])
        if key in pred:raise ValueError('duplicate prediction '+str(key))
        if r['cls']!=compose(r['factors']):raise ValueError('composed class differs from factors')
        if r['base']!=meta[key[0]]['coverage_by_start'][key[1]]['base']:raise ValueError('prediction base changed')
        pred[key]=r
    expected={(lid,c['start']) for lid,l in meta.items() for c in l['coverage'] if c['scored']}
    if set(pred)!=expected:raise ValueError(f'predictions do not cover extraction: {len(set(pred)^expected)}')
    if receipt['samples']!=len(pred):raise ValueError('prediction receipt count mismatch')
    return pred


def metadata(directory):
    verify_receipt(directory)
    return {l['id']:dict(l,coverage_by_start={c['start']:c for c in l['coverage']}) for l in rows(directory/'lines.jsonl.gz')}


def map_lines(frozen,meta,pred,*,filtered=True):
    """Filter reader parts before scoring/reporting; raw replay is selectable."""
    out=deepcopy(frozen);mapping=Counter()
    for l in out:
        lid=l['line_id'];md=meta.get(lid);l['prediction_line_present']=md is not None
        if md and md['recogniser_text']!=l['recogniser_text']:raise ValueError('frozen recogniser text differs '+lid)
        cov=md['coverage_by_start'] if md else {};owners={};fused_components=set()
        byslot={s['slot']:s for s in l['slots']}
        for r in l['recogniser_slots']:
            start=r['start'];p=pred.get((lid,start));c=cov.get(start,{})
            r.update(mark_support_source='reader',reader_evidence=p.get('evidence',{}) if p else {},
                     detector_evidence=r.get('evidence',{}),evidence=p.get('evidence',{}) if p else {},
                     parts=p['cls'].split('+') if p and p['cls']!='none' else [],naming={},
                     mark_probabilities=p.get('mark_probabilities',{}) if p else {},reader_scored=p is not None,
                     reader_fused=c.get('fused',False))
            slot=r.get('component_slot')
            # Preserve the frozen reading->component mapping. For unlocated
            # fused letters, diagnostic overlap marks the affected truth slots;
            # it never invents a per-letter truth or awards an arbitrary owner.
            if slot is not None:owners.setdefault(slot,[]).append((r,p,c))
            elif r['base'] in LETTERS:
                mapping['unmapped_reader_slots']+=int(p is not None)
            if c.get('fused'):
                span=r['locator_span'];hits=[s for s in l['slots'] if min(span[1],s['bbox'][2])>max(span[0],s['bbox'][0])]
                if hits:
                    best=max(max(0,min(span[1],s['bbox'][2])-max(span[0],s['bbox'][0])) for s in hits)
                    fused_components.update(s['slot'] for s in hits if max(0,min(span[1],s['bbox'][2])-max(span[0],s['bbox'][0]))==best)
        bystart={r['start']:r for r in l['recogniser_slots']}
        raw_text=''.join(c.base+''.join(MARKS[p] for p in bystart.get(c.start,{}).get('parts',[]) if p in MARKS) for c in clusters(nfd(l['recogniser_text'])))
        reading=LineReading(raw_text,l['recogniser_slots'],[])
        reading,_=apply_constraints(reading,output='normalised' if filtered else 'print')
        l.update(reading=reading.text,recogniser_slots=reading.slots,
                 removed_by_constraint=reading.removed_by_constraint,constraint_flags=reading.constraint_flags)
        mapping['removed_by_constraint']+=len(reading.removed_by_constraint)
        mapping['constraint_evidence_ties']+=sum(f.get('reason')=='evidence_tie' for f in reading.constraint_flags)
        bystart={r['start']:r for r in reading.slots}
        owners={slot:[(bystart[r['start']],p,c) for r,p,c in entries] for slot,entries in owners.items()}
        for s in l['slots']:
            matches=owners.get(s['slot'],[]);s.update(detected=[],cls='none',reader_scored=False,
                                                     reader_fused=s['slot'] in fused_components,unnamed=[],unknown_kinds=[])
            if len(matches)==1:
                r,p,c=matches[0]
                if p:
                    s.update(detected=sorted(mark_set('+'.join(r['parts']))),cls='+'.join(r['parts']) or 'none',reader_scored=True,
                             recogniser_start=r['start'],reader_fused=c.get('fused',False),
                             hold=r.get('hold',False),label_status=r.get('label_status','UNADJUDICATED'),constraint_flags=r.get('constraint_flags',[]))
                    mapping['mapped_scored_slots']+=1
                    mapping['mapped_scored_known_truth']+=int(s['truth'] is not None)
            elif len(matches)>1:mapping['competing_frozen_component_owners']+=1
    return out,dict(mapping)


def detection(slots):
    known=[s for s in slots if s['truth'] is not None]
    t=[bool([m for m in s['truth'] if m[0]!='apostrophe']) for s in known]
    d=[bool([m for m in s['detected'] if m[0]!='apostrophe']) for s in known]
    tp=sum(a and b for a,b in zip(t,d));fp=sum(not a and b for a,b in zip(t,d));fn=sum(a and not b for a,b in zip(t,d))
    return dict(n=len(known),tp=tp,fp=fp,fn=fn,precision=tp/(tp+fp) if tp+fp else None,
                recall=tp/(tp+fn) if tp+fn else None)


def summaries(lines):
    slots=[s for l in lines for s in l['slots']];scored=[s for s in slots if s.get('reader_scored')]
    fused=[s for s in slots if s.get('reader_fused')]
    caps=[s for s in slots if s['base'].isupper()]
    marked_caps=[s for s in caps if s['truth'] and any(k!='apostrophe' for k,v in s['truth'])]
    classes=sorted({compose(v) for v in itertools.product(*(range(len(c)) for c in HEADS.values()))})
    known=[s for s in slots if s['truth'] is not None];perclass={}
    for cls in classes:
        target=mark_set(cls);support=sum(set(map(tuple,s['truth']))==target for s in known)
        predicted=sum(set(map(tuple,s['detected']))==target for s in known)
        tp=sum(set(map(tuple,s['truth']))==target==set(map(tuple,s['detected'])) for s in known)
        perclass[cls]=dict(support=support,predicted=predicted,tp=tp,precision=tp/predicted if predicted else None,recall=tp/support if support else None)
    asc=[s for s in slots if s['truth']==[] and (s['base'] in 'δβλθφξζ' or s['base'].isupper())]
    return dict(all_unscored_none=metric(slots),scored=metric(scored),fused_all_unscored_none=metric(fused),
                fused_scored=metric([s for s in fused if s.get('reader_scored')]),
                capital_detection=detection(caps),capital_naming=metric(marked_caps),capital_marked_slots=len(marked_caps),
                ascender_false_marks=dict(n=len(asc),false=sum(bool(s['detected']) for s in asc)),per_class=perclass,
                per_book={doc:metric([s for l in lines if l['doc']==doc for s in l['slots']]) for doc in sorted({l['doc'] for l in lines})})


def google_disagreements(lines,sources):
    from greekocr.labelfix.text import tokenize
    from scripts.labelfix.clariden.r1_common import factors
    total=confirmed=unknown=0
    for l in lines:
        ts=tokenize(sources[l['line_id']]['google'])
        for s in l['slots']:
            wi=s.get('word');ci=s.get('char')
            if wi is None or ci is None or wi>=len(ts):continue
            cs=clusters(ts[wi].core)
            if ci>=len(cs):continue
            fs=factors(cs[ci].marks)
            if fs is None:continue
            g=mark_set(compose(fs));d={tuple(m) for m in s['detected'] if m[0]!='apostrophe'}
            if g!=d:
                total+=1
                if s['truth'] is None:unknown+=1
                else:confirmed+=d=={tuple(m) for m in s['truth'] if m[0]!='apostrophe'}
    return dict(disagreements=total,known=total-unknown,print_confirms=confirmed,unknown=unknown,
                print_confirmation_fraction=confirmed/(total-unknown) if total>unknown else None)


def identity_hash(lines):
    data=[dict(line_id=l['line_id'],slots=[{k:s.get(k) for k in ('slot','bbox','truth')} for s in l['slots']],
        recogniser_slots=[{k:r.get(k) for k in ('start','component_slot','component_slots','bbox','locator_span')} for r in l['recogniser_slots']]) for l in sorted(lines,key=lambda l:l['line_id'])]
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()


def load_baselines(specs,manifest):
    if not specs:raise ValueError('at least one explicitly named --baseline is required')
    result={};bindings={}
    for spec in specs:
        name,path=spec.split('=',1);path=Path(path)
        if name in result or name not in manifest:raise ValueError('unknown or duplicate baseline '+name)
        bound=manifest[name]
        if sha256(path)!=bound['sha256']:raise ValueError(name+' baseline hash mismatch')
        ls=list(rows(path));held=[l for l in ls if not l['dev']]
        total=frozen_metric(held)['total']
        if any(total.get(k,0)!=v for k,v in bound['expected_totals'].items()):raise ValueError(name+' expected totals mismatch')
        if identity_hash(ls)!=bound['identity_sha256']:raise ValueError(name+' slot/box identity mismatch')
        result[name]=ls;bindings[name]=dict(path=str(path),**bound)
    truth={l['line_id']:[s['truth'] for s in l['slots']] for l in next(iter(result.values()))}
    for name,ls in result.items():
        if {l['line_id']:[s['truth'] for s in l['slots']] for l in ls}!=truth:raise ValueError(name+' scope/truth differs')
    return result,bindings


def filter_baseline(lines):
    from scripts.labelfix.s6_validate import detected
    out=deepcopy(lines)
    for l in out:
        rd,_=apply_constraints(LineReading(l['reading'],l['recogniser_slots'],l.get('reading_flags',[])),output='normalised')
        l.update(reading=rd.text,recogniser_slots=rd.slots,removed_by_constraint=rd.removed_by_constraint,constraint_flags=rd.constraint_flags)
        for s in l['slots']:
            rs=[r for r in rd.slots if r.get('component_slot')==s['slot']]
            s['detected']=sorted({tuple(x) for r in rs for x in detected(r)})
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runs',type=Path,required=True);ap.add_argument('--heldout',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--mock',action='store_true')
    ap.add_argument('--baseline',action='append',required=True,help='named frozen baseline, e.g. S4=path')
    ap.add_argument('--baseline-manifest',type=Path,default=Path('docs/records/labelfix/spellcheck/SF1_baselines.json'))
    a=ap.parse_args()
    baselines,bindings=load_baselines(a.baseline,json.loads(a.baseline_manifest.read_text()))
    if 'S4' not in baselines:raise ValueError('explicit S4 mapping baseline required')
    frozen=baselines['S4'];root=Path(bindings['S4']['path']).parent
    held=[l for l in frozen if not l['dev']]
    assert len(held)==666 and len({l['doc'] for l in held})==14
    meta=metadata(a.heldout);assert set(meta)=={l['line_id'] for l in held}
    from greekocr.labelfix.validate import load_three_way
    sources={l['line_id']:l for l in load_three_way(0)}
    result=dict(schema='sf1-r1-score-v1',mock=a.mock,quality_claim='frozen-slot candidate; not physical or untouched-test certification',
        heldout_lines=len(held),policies={},ctc_forward_passes=0,baseline_bindings=bindings,
        scoring_contract='frozen physical slots; UNKNOWN preserved; raw and explicitly normalised comparisons are symmetric',
        source_sha256={str(a.baseline_manifest):sha256(a.baseline_manifest)},coverage=json.loads((a.heldout/'extraction_receipt.json').read_text()))
    predictions={};armmeta=dict(meta)
    extra=a.runs/'owner_extra'
    em=metadata(extra) if extra.exists() else {}
    armmeta.update(em)
    for arm in ARMS:
        p=prediction_map(a.runs/arm/'heldout_predictions.jsonl',meta,extraction=a.heldout,checkpoint=a.runs/arm/'best.pt')
        if em:p.update(prediction_map(a.runs/arm/'owner_predictions.jsonl',em,extraction=extra,checkpoint=a.runs/arm/'best.pt'))
        predictions[arm]=p
    a.out.mkdir(parents=True,exist_ok=False)
    baseby={l['line_id']:l for l in frozen}
    for policy_name,filtered in [('raw',False),('filtered',True)]:
        policy_result=dict(reference={},arms={})
        mappings={}
        for arm in ARMS:
            mapped,mapping=map_lines(frozen,armmeta,predictions[arm],filtered=filtered)
            mh=[l for l in mapped if not l['dev']]
            # Split-specific mapping denominators; pooled owner counts are separate.
            _,heldmapping=map_lines(held,meta,{k:v for k,v in predictions[arm].items() if k[0] in meta},filtered=filtered)
            stats=summaries(mh);stats['mapping']=heldmapping;stats['mapping_including_owner_extra']=mapping
            stats['google_disagreements']=google_disagreements(mh,sources)
            own=owner_evaluate({l['line_id']:l for l in mapped},baseby,root)
            stats['owner_counts']=own['counts'];policy_result['arms'][arm]=stats
            write_rows(a.out/f'{arm}_{policy_name}_owner_checks.jsonl',[dict(group=g,**r) for g,rs in own.items() if g!='counts' for r in rs])
            write_rows(a.out/f'{arm}_{policy_name}_readings.jsonl.gz',[dict(line_id=l['line_id'],reading=l['reading'],removed_by_constraint=l['removed_by_constraint'],constraint_flags=l['constraint_flags']) for l in mapped])
            if arm=='A':mappings={(l['line_id'],s['slot']):s for l in mh for s in l['slots']}
        for name,ls in baselines.items():
            refs=filter_baseline(ls) if filtered else deepcopy(ls)
            refs=[l for l in refs if not l['dev']]
            for l in refs:
                for s in l['slots']:
                    f=mappings[(l['line_id'],s['slot'])];s.update(reader_scored=f['reader_scored'],reader_fused=f['reader_fused'])
            policy_result['reference'][name]=summaries(refs)
            policy_result['reference'][name]['google_disagreements']=google_disagreements(refs,sources)
        result['policies'][policy_name]=policy_result
    # Compatibility aliases explicitly identify raw policy.
    result.update(reference=result['policies']['raw']['reference'],arms=result['policies']['raw']['arms'],default_table_policy='raw')
    write_json(a.out/'metrics.json',result)
    report=['# R1 print-truth result (SF1 rescoring)','',result['quality_claim'],
        'S4, S5 and S6 are hash-bound by name and expected totals. Raw and filtered tables use the same policy on every column.',
        'UNKNOWN, unscored and unmapped denominators remain explicit. Fused scores do not establish per-letter physical accuracy. No model inference was run.','']
    columns=[*baselines,*ARMS]
    for pn,stats in result['policies'].items():
        allstats={**stats['reference'],**stats['arms']}
        for key in ('all_unscored_none','scored','fused_all_unscored_none','fused_scored'):
            report += [f'## {pn}: {key} (P / R / F1)','','| kind | '+' | '.join(columns)+' |','|---|'+'---|'*len(columns)]
            for kind in ('total','accent','breathing','compound','subscript','dialytika','apostrophe'):
                vals=[prf(allstats[col][key]['total'] if kind=='total' else allstats[col][key]['by_kind'][kind]) for col in columns]
                report.append('| '+kind+' | '+' | '.join(vals)+' |')
            report.append('')
        report += [f'## {pn}: owner notes','','| set | '+' | '.join(ARMS)+' |','|---|'+'---|'*len(ARMS)]
        for group in ('old_59','review_33','examples_56','review_v16_49','examples_v10_57'):
            report.append('| '+group+' | '+' | '.join(f"{stats['arms'][a]['owner_counts'][group]['fixed']}/{stats['arms'][a]['owner_counts'][group]['n']}" for a in ARMS)+' |')
        report.append('')
        report += [f'### {pn}: clause dimensions (fixed / n)','','| note set | dimension | '+' | '.join(ARMS)+' |','|---|---|'+'---|'*len(ARMS)]
        for group in ('old_59','review_33','examples_56','review_v16_49','examples_v10_57'):
            for dimension in ('physical','naming','segmentation','complete_note'):
                vals=[]
                for arm in ARMS:
                    d=stats['arms'][arm]['owner_counts'][group]['dimensions'][dimension]
                    vals.append(f"{d['fixed']}/{d['n']}")
                report.append('| '+group+' | '+dimension+' | '+' | '.join(vals)+' |')
        report.append('')
    report += ['Filtered means explicitly normalised output; default print transcription only flags. C1-after-consonant and C3 remain held back.',
        'Reader support is its exported evidence/probabilities only. The saved predictions contain no confidence; no S4 detector blob ranks an R1 proposal.',
        'D changes both sampling and loss weighting; E prevalence belongs to the selected source pool.']
    (a.out/'RESULT.md').write_text('\n'.join(report)+'\n')
    from scripts.labelfix.owner_reading import policy
    source_paths=['scripts/labelfix/clariden/r1_score.py','scripts/labelfix/clariden/r1_owner.py','scripts/labelfix/clariden/r1_common.py','scripts/labelfix/s6_notes.py','scripts/labelfix/s5_notes.py','scripts/labelfix/s4_report.py','greekocr/labelfix/linemetric.py','greekocr/labelfix/reading.py','scripts/labelfix/owner_reading.py']
    receipt=dict(schema='sf1-r1-score-receipt-v1',mock=a.mock,heldout_lines=len(held),baselines=bindings,
        baseline_manifest_sha256=sha256(a.baseline_manifest),metrics_sha256=sha256(a.out/'metrics.json'),result_sha256=sha256(a.out/'RESULT.md'),
        scorer_sha256={p:sha256(Path(p)) for p in source_paths},constraint_policy={pn:policy('normalised' if pn=='filtered' else 'print') for pn in result['policies']},
        extraction={str(ex):dict(receipt_sha256=sha256(ex/'extraction_receipt.json'),index_sha256=sha256(ex/'index.npy'),metadata_sha256=sha256(ex/'lines.jsonl.gz')) for ex in [a.heldout]+([extra] if em else [])},
        checkpoints={arm:sha256(a.runs/arm/'best.pt') for arm in ARMS},
        note_sets={p:sha256(root/p) for p in ['owner_slot_expectations.jsonl','owner_examples_expectations.jsonl','S5_review_expectations.jsonl','owner_notes_db_20261016.jsonl','owner_notes_examples_20261016.jsonl','owner_notes_review_v16_20261016.jsonl','owner_notes_examples_v10_20261016.jsonl']},
        reader_support_sha256={arm:hashlib.sha256(json.dumps([dict(line_id=k[0],start=k[1],evidence=v.get('evidence'),probabilities=v.get('mark_probabilities')) for k,v in sorted(pred.items())],sort_keys=True).encode()).hexdigest() for arm,pred in predictions.items()},
        predictions={arm:{name:dict(sha256=sha256(a.runs/arm/(name+'_predictions.jsonl')),receipt_sha256=sha256(a.runs/arm/(name+'_predictions.receipt.json'))) for name in ['heldout']+(['owner'] if em else [])} for arm in ARMS},
        reader_support='saved reader probabilities/evidence only; absent support remains unknown',ctc_forward_passes=0)
    write_json(a.out/'score_receipt.json',receipt)
    print('R1_SCORE_OK '+json.dumps(dict(lines=len(held),arms=list(ARMS),baselines=list(baselines),policies=list(result['policies']))),flush=True)


if __name__=='__main__':main()
