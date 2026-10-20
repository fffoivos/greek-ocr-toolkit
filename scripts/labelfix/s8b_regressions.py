"""Offline 666-line and owner-snapshot regressions for the frozen S8b candidate."""
from scripts.labelfix import s8b_measure as b
from scripts.labelfix import s6_notes as notes
from scripts.labelfix import s5_notes
from scripts.labelfix import box_regression as boxes
from scripts.labelfix import s6_validate as s6
from scripts.labelfix.clariden import r1_score
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.reading import LineReading
from greekocr.labelfix.linemetric import mark_set
from copy import deepcopy
import collections as C
import gzip
import json
from pathlib import Path
import time
from PIL import Image
import ast
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.text import nfd, clusters, strip_marks

# Execute the unchanged text-only instrument functions without importing its
# GPU CLI (l1e_run imports torch). No model module is imported or instantiated.
_instrument = Path(__file__).with_name('clariden')/'l1e_measure.py'
_nodes = ast.parse(_instrument.read_text()).body
_selected = [n for n in _nodes if isinstance(n, ast.FunctionDef) and n.name in
             ('atomic','google_marks','saved_runtime','score_line')]
_marks = b.p.reading.MARKS
_namespace = dict(Counter=C.Counter,defaultdict=C.defaultdict,deepcopy=deepcopy,
    LineReading=LineReading,MARKS=_marks,KINDS={k:('breathing' if k in ('psili','dasia') else
        'accent' if k in ('acute','grave','circumflex') else k) for k in _marks},
    MODES=b.p.gate.MODES,serialize=b.p.gate.serialize,compose_runtime=b.p.gate.compose_runtime,
    edit_guard=b.p.gate.edit_guard,pair_tokens=pair_tokens,nfd=nfd,clusters=clusters,strip_marks=strip_marks,mark_set=mark_set)
exec(compile(ast.Module(body=_selected,type_ignores=[]),str(_instrument),'exec'),_namespace)
score_line, saved_runtime, atomic = (_namespace[k] for k in ('score_line','saved_runtime','atomic'))

p, OUT = b.p, b.OUT
O = p.OUT.parent
R1 = p.ROOT.parent/'greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1'
NOTESETS = ('owner_notes_review_v16_20261016.jsonl','owner_notes_examples_v10_20261016.jsonl')


def serial(line):
    return p.gate.serialize(LineReading(line['reading'],deepcopy(line['recogniser_slots']),[],
        opening_quotes=deepcopy(line.get('opening_quotes',[])),constraint_flags=deepcopy(line.get('reading_flags',[]))))


def side(record):
    bb, zones = [], []
    for s in record['slots']:
        ev = s['evidence'];slot=s['display_slot'];bbox=s['bbox'];xh=ev['xh']
        zones.append(dict(display_slot=slot,mark_zone=[ev['window'][0],ev['meanline']-1.3*xh,ev['window'][1],ev['baseline']+.9*xh]))
        for field,kind in (('above','above'),('below','below'),('apostrophes','above')):
            bb += [dict(z,kind=kind,display_slot=slot,start=s['start'],status='raw-detection') for z in ev.get(field,[])]
    bb += [dict(z,kind='quote',status='raw-detection') for z in record.get('opening_quotes',[])]
    return dict(reading=record['text'],boxes=bb,letters=[s['bbox'] for s in record['slots']],letter_zones=zones,line_reading=record)


def tally(truth, pred, counts):
    counts['TP'] += len(truth & pred)
    counts['FP'] += len(pred-truth)
    counts['FN'] += len(truth-pred)


def rates(c):
    return dict(c,precision=c['TP']/(c['TP']+c['FP']) if c['TP']+c['FP'] else None,
        recall=c['TP']/(c['TP']+c['FN']) if c['TP']+c['FN'] else None)


def adapt(line, record):
    """Carry the OLD owner-slot namespace by frozen recognizer start only."""
    out=deepcopy(line);old={s['start']:s for s in line['recogniser_slots']}
    rr=deepcopy(record['slots'])
    for r in rr:
        prior=old[r['start']]
        r['component_slot']=prior.get('component_slot')
        r['component_slots']=prior.get('component_slots',[])
    for slot in out['slots']:
        children=[r for r in rr if r.get('component_slot')==slot['slot']]
        slot['detected']=sorted({tuple(m) for r in children for m in s6.detected(r)})
        ev=deepcopy(slot['evidence'])
        for field in ('above','below','diagnostics','apostrophes'):
            ev[field]=[z for r in children for z in r['evidence'].get(field,[])]
        slot['evidence']=ev
    out.update(recogniser_slots=rr,reading=record['text'],opening_quotes=record.get('opening_quotes',[]))
    return out


def main():
    started=time.monotonic();binding=b.freeze()
    old={r['line_id']:r for r in p.rows(O/'S6_lines.jsonl.gz')}
    frozen={r['line_id']:r for r in p.rows(O/'S4_lines.jsonl.gz')}
    sets={name:p.rows(O/name) for name in NOTESETS}
    ownerids={r['line_id'] for rr in sets.values() for r in rr}
    heldids={lid for lid,r in old.items() if not r['dev']}
    assert len(heldids)==666 and len(ownerids)==92
    aligns=load_alignments(p.ROOT/'.cache/labelfix/align_s0.jsonl')
    model=p.markshape.load_model(p.ROOT/'docs/records/labelfix/markshape_model_S4.json')
    after={};before={};custody=[]
    for i,lid in enumerate(sorted(heldids|ownerids),1):
        line=old[lid];crop=Path(line['crop']);al=aligns[crop_key(str(crop))]
        cache=OUT/'regression_detector'/(lid+'.json.gz');sha=p.sha(crop)
        before[lid]=serial(line)
        if cache.exists():
            record=b.read_record(cache)
            assert record['candidate_binding']==binding and record['crop_sha256']==sha
        else:
            rd,font=b.detect(crop,line['recogniser_text'],al,model)
            record=dict(id=lid,candidate_binding=binding,crop=str(crop),crop_sha256=sha,detector=rd,font_fit=font)
            cache.parent.mkdir(exist_ok=True)
            cache.write_bytes(gzip.compress(json.dumps(record,ensure_ascii=False,allow_nan=False).encode(),mtime=0))
        after[lid]=record['detector']
        custody.append(dict(id=lid,crop=str(crop),crop_sha256=sha,after_sha256=p.sha(cache)))
        if i%100==0:print(f'S8b regression detector {i}/{len(heldids|ownerids)}; {time.monotonic()-started:.1f}s',flush=True)
    b.write('regression_input_custody.jsonl',custody)
    # Frozen character truth, all 3 physical zones; exact-name atomic marks.
    counts={v:{k:C.Counter(TP=0,FP=0,FN=0) for k in ('presence','above','below','apostrophe','marks','accent','breathing','subscript','dialytika')}
        for v in ('before','after')}
    line_scores=[];changed=[];known=unknown=0
    for lid in sorted(heldids):
        rr=dict(line_id=lid,weight=1.,presence={v:dict(counts={k:C.Counter(TP=0,FP=0,FN=0) for k in counts[v]}) for v in counts})
        by={v:{s['start']:s for s in rd['slots']} for v,rd in (('before',before[lid]),('after',after[lid]))}
        for tr in old[lid]['character_checks']:
            if tr['truth_zones'] is None:unknown+=1;continue
            known+=1;start=tr['start'];truth=set(tr['truth_zones']);tm=atomic(tr['truth'])
            for v in counts:
                s=by[v][start];ph=set(s6.physical(s));nm=atomic(mark_set('+'.join(s['parts']) or 'none'))
                for key in counts[v]:
                    a,c=(truth,ph) if key=='presence' else (truth & {key},ph & {key}) if key in ('above','below','apostrophe') else (tm,nm) if key=='marks' else ({x for x in tm if x[0]==key},{x for x in nm if x[0]==key})
                    tally(a,c,counts[v][key]);tally(a,c,rr['presence'][v]['counts'][key])
            a,c=by['before'][start],by['after'][start]
            if set(s6.physical(a))!=set(s6.physical(c)) or a['parts']!=c['parts']:
                changed.append(dict(id=lid,start=start,truth=tr['truth'],truth_zones=tr['truth_zones'],
                    before_parts=a['parts'],after_parts=c['parts'],before_presence=s6.physical(a),after_presence=s6.physical(c)))
        line_scores.append(rr)
    held_summary=dict(lines=666,known_characters=known,unknown_characters=unknown,
        scores={k:{v:rates(counts[v][k]) for v in counts}|
            dict(paired_change={m:b.paired_delta(line_scores,k,m,20261017) for m in ('precision','recall')}) for k in counts['before']},
        changed_known_characters=len(changed))
    b.dump('heldout_detector_summary.json',held_summary);b.write('heldout_detector_changes.jsonl',changed)
    b.write('heldout_line_counts.jsonl',line_scores)
    # Exact saved A/B/E metadata is available read-only in the R1 worktree.
    ex=R1/'heldout_font';meta=r1_score.metadata(ex);pred={}
    for arm in ('A','B','E'):
        pred[arm]=C.defaultdict(list)
        for (lid,_),r in r1_score.prediction_map(R1/'output_3678928'/arm/'heldout_predictions.jsonl',meta,
                extraction=ex,checkpoint=R1/'output_3678928'/arm/'best.pt').items():
            pred[arm][lid].append(r)
    recovery=p.load(O/'SF3_evidence/heldout_after/observation_recovery.json')
    assert set(meta)==heldids
    for lid,row in meta.items():
        if all('evidence_state' in c and 'uncertainty' in c for c in row['coverage']):
            continue
        rec=recovery[lid]
        assert p.sha(old[lid]['crop'])==rec['crop_sha256']
        assert row['font_size']['pixel_measurements']==rec['pixel_measurements']
        for c in row['coverage']:
            uncertainty=[]
            if rec['pixel_measurements']==0:uncertainty.append('no_pixel_evidence')
            if c['span'][0]<0 or c['span'][1]>rec['width']:uncertainty.append('out_of_image_span')
            c.setdefault('uncertainty',uncertainty)
            c.setdefault('evidence_state','UNKNOWN' if uncertainty else 'unadjudicated')
    saveddec={r['id']:r for r in p.rows(O/'SF4_evidence/heldout/decisions.jsonl.gz')}
    google={r['line_id']:r['gt'] for r in p.rows(Path.home()/'Projects/greek-page-ocr/out/e3b/predictions/full_s0_v2_test.jsonl')}
    totals={v:{m:C.Counter() for m in p.gate.MODES} for v in ('saved_sf4','before','after')}
    decisions=[];events=[]
    for lid in sorted(heldids):
        rt=saved_runtime(old[lid],meta[lid],{a:pred[a][lid] for a in pred})
        decisions_by={}
        for v in totals:
            if v=='saved_sf4':
                dd=saveddec[lid]['decisions']
            else:
                run=deepcopy(rt);run['detector']=before[lid] if v=='before' else after[lid]
                dd={m:p.gate.compose_runtime(run,m) for m in p.gate.MODES}
            stats,ev=score_line(frozen[lid],google[lid],rt,decisions=dd)
            for m in p.gate.MODES:totals[v][m].update(stats[m])
            decisions_by[v]=dd
            events.append(dict(id=lid,variant=v,events=ev))
        decisions.append(dict(id=lid,decisions={v:decisions_by[v] for v in ('before','after')}))
    tables={v:{m:dict(c) for m,c in tt.items()} for v,tt in totals.items()}
    gate_summary=dict(lines=666,tables=tables,baseline_table_reproduced=tables['saved_sf4']==tables['before'],
        full_runtime_recomposition=True,coverage='exact saved metadata plus hash-bound SF3 observation recovery',
        prediction_inputs={str(R1/'output_3678928'/a/'heldout_predictions.jsonl'):p.sha(R1/'output_3678928'/a/'heldout_predictions.jsonl') for a in pred})
    b.dump('heldout_gate_summary.json',gate_summary);b.write('heldout_gate_events.jsonl',events);b.write('heldout_gate_decisions.jsonl.gz',decisions)
    # Box changes use the standard one-to-one IoU instrument, including every line.
    oldside={l:side(before[l]) for l in ownerids};newside={l:side(after[l]) for l in ownerids}
    b.dump('owner_before_boxes.json',dict(lines=oldside));b.dump('owner_after_boxes.json',dict(lines=newside))
    diff=boxes.compare_pages(oldside,newside,.3)
    b.dump('owner_box_regression.json',dict(summary={k:sum(len(r[k]) for r in diff.values()) for k in
        ('lost','added','moved','owner_changed','pixels_changed','status_changed','pixels_unknown','owner_unknown','status_unknown')},lines=diff))
    # Notes refer to the original S4 state, not a newly generated page.
    adapted={l:adapt(old[l],after[l]) for l in ownerids}
    lookup=s5_notes.specs();lookup['8b6b0de9-p000021-l0012']=[('no_top',1,None)]
    ownerchecks=[];implicit=[];approved_removals=[]
    for name,rr in sets.items():
        spec=notes.current_review_specs() if name==NOTESETS[0] else lookup
        for note in rr:
            lid=note['line_id'];named=boxes.mentioned_slots(note.get('note') or '')
            clauses=spec.get(lid) if note.get('note') else [('no_regression',None,None)]
            for kind,target,value in clauses or [('uncertain',None,None)]:
                entry=dict(note_set=name,line_id=lid,kind=kind,target=target,value=value,versions={})
                for v,line in (('before',old[lid]),('after',adapted[lid])):
                    ok,ev=notes.clause(line,frozen[lid],kind,target,value)
                    entry['versions'][v]=dict(fixed=bool(ok),evidence=ev)
                ownerchecks.append(entry)
            oldby={r['start']:r for r in old[lid]['recogniser_slots']}
            newby={r['start']:r for r in adapted[lid]['recogniser_slots']}
            # State fixed by S4, evaluated through its unchanged start mapping.
            for slot in frozen[lid]['slots']:
                n=slot['slot']
                if n in named:continue
                ss=[r for r in frozen[lid]['recogniser_slots'] if r.get('component_slot')==n]
                if not ss:continue
                state=set(z for s in ss for z in s6.physical(s))
                values={v:set(z for s in ss for z in s6.physical(by.get(s['start']))) for v,by in (('before',oldby),('after',newby))}
                implicit.append(dict(note_set=name,line_id=lid,approved_S4_slot=n,approved_presence=sorted(state),
                    before=dict(missed=sorted(state-values['before']),false=sorted(values['before']-state)),
                    after=dict(missed=sorted(state-values['after']),false=sorted(values['after']-state))))
            for loss in diff[lid]['lost']:
                # Namespace is resolved against OLD S4 component ownership,
                # not the new display slot or an ambiguous overlapping zone.
                start=loss.get('start');slot=next((s.get('component_slot') for s in frozen[lid]['recogniser_slots'] if s['start']==start),None)
                approved_removals.append(dict(note_set=name,line_id=lid,old_S4_slot=slot,
                    scope='unresolved' if slot is None else 'named' if slot in named else 'implicitly approved',box=loss))
    b.write('owner_note_checks.jsonl',ownerchecks);b.write('owner_implicit_checks.jsonl',implicit)
    b.write('owner_box_removals.jsonl',approved_removals)
    owner_summary={name:dict(clauses=len([x for x in ownerchecks if x['note_set']==name]),
        clauses_fixed={v:sum(x['versions'][v]['fixed'] for x in ownerchecks if x['note_set']==name) for v in ('before','after')},
        implicit={v:{k:sum(len(x[v][k]) for x in implicit if x['note_set']==name) for k in ('missed','false')} for v in ('before','after')},
        implicit_slots=sum(x['note_set']==name for x in implicit)) for name in NOTESETS}
    b.dump('owner_summary.json',owner_summary)
    b.dump('regression_receipt.json',dict(candidate_binding=binding,heldout_lines=666,owner_lines=92,
        detector_lines=len(after),ctc_runs=0,r1_runs=0,network=False,elapsed_seconds=time.monotonic()-started,
        owner_snapshot='S4_lines.jsonl.gz plus exact v16/v10 notes; original reviewed HTML unavailable',
        input_hashes={str(x):p.sha(x) for x in [O/'S4_lines.jsonl.gz',O/'S6_lines.jsonl.gz',*[(O/n) for n in NOTESETS],
            ex/'extraction_receipt.json',ex/'lines.jsonl.gz',p.ROOT/'.cache/labelfix/align_s0.jsonl']}))
    assert b.freeze()==binding
    print('Regression measurement complete.',flush=True)


if __name__=='__main__':
    main()
