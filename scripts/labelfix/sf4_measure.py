"""Offline SF3 -> SF4 saved-decision replay; no missing evidence is synthesized.

The local checkout has the complete SF3 decisions, S6 physical evidence, frozen
S4 truth and A/B/E predictions, but lacks the full extraction coverage records.
Replay ONLY the changed observation predicates, retaining every other saved
veto and output. Prove acceptance is a subset per slot; rescore both phases
with the identical frozen instrument. This is not a full runtime recomposition.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import importlib.util
import json
import sys
from pathlib import Path
import time

from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.reading import LineReading,MARKS
from greekocr.labelfix.text import clusters,nfd,is_letter
from scripts.labelfix.clariden.l1e_measure import score_line
from scripts.labelfix.clariden.r1_common import rows,sha256,write_json,write_rows
from scripts.labelfix.sf3_measure import reason_table


def observation_reasons(policy,slot,predictions,text,line_flags,mode):
    """Compare policy effects with reader coverage held missing in BOTH calls.

    Missing-coverage reasons are identical and cancel from the difference.
    They are never emitted as measured decisions or treated as observed pixels.
    All actual reader coverage vetoes remain in the saved SF3 decisions.
    """
    cs=clusters(nfd(text));s=deepcopy(slot);start=s['start']
    if any(c.start==start and i and c.base in 'ιΙ' and cs[i-1].base in 'ΑΗΩ' for i,c in enumerate(cs)):
        s['iota_adscript']=True
    signals=[p for c in cs if c.start==start for p,v in MARKS.items() if v in c.marks]
    for arm in ('B','E'):
        p=predictions[arm].get(start)
        if p:signals.extend(p.get('parts',p.get('cls','none').split('+')))
    parts=[*s.get('parts',()),*signals]
    for arm in ('A',mode[-1] if mode.startswith('ENSEMBLE_') else 'A'):
        p=predictions[arm].get(start)
        if p:parts.extend(p.get('parts',p.get('cls','none').split('+')))
    relevance=policy.zone_relevance(s,parts)
    active=[f for f in line_flags if policy._flag_targets(f,start) and policy._flag_relevant(f,relevance)]
    peer=predictions[mode[-1]].get(start) if mode.startswith('ENSEMBLE_') else None
    decision=policy.decide(s,predictions['A'].get(start),None,mode,
        flagged=bool(active),peer_prediction=peer,peer_coverage=None,signal_parts=signals)
    reasons=set(decision['reasons'])
    # K1 attaches start-targeted line flags after composition, as well as the
    # saved slot's own flags. Orthographic outputs/flags are otherwise frozen.
    post=[*s.get('constraint_flags',()),*[f for f in active if f.get('start')==start or
        any(a.get('start')==start for a in f.get('alternatives',()))]]
    reasons.update('K1:'+f.get('rule','observation')+':'+f.get('reason','unknown')
                   for f in post if policy._flag_relevant(f,relevance))
    return reasons


def measure(baseline, sf3_gate, google_path, out):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=False)
    ref=json.loads((baseline/'measurement_receipt.json').read_text());inputs={}
    def check(path,expected=None):
        actual=sha256(path)
        if expected is not None and actual!=expected:raise ValueError('saved evidence changed: '+str(path))
        inputs[str(path)]=actual
    for name,expected in ref['outputs'].items():
        if (baseline/name).exists():check(baseline/name,expected)
    check(baseline/'measurement_receipt.json')
    check(sf3_gate,ref['policy']['sources']['greekocr/labelfix/release_gate.py'])
    check(google_path,ref['inputs']['inputs/google_predictions.jsonl'])
    source=Path('docs/records/labelfix/spellcheck')
    for name in ('S4_lines.jsonl.gz','S6_lines.jsonl.gz'):check(source/name,ref['inputs']['inputs/'+name])
    spec=importlib.util.spec_from_file_location('greekocr.labelfix._sf3_saved_gate',sf3_gate)
    oldgate=importlib.util.module_from_spec(spec);spec.loader.exec_module(oldgate)
    reading_path=sf3_gate.with_name('reading.py')
    check(reading_path,ref['policy']['sources']['greekocr/labelfix/reading.py'])
    spec=importlib.util.spec_from_file_location('greekocr.labelfix._sf3_saved_reading',reading_path)
    oldreading=importlib.util.module_from_spec(spec);sys.modules[spec.name]=oldreading;spec.loader.exec_module(oldreading)
    before=list(rows(baseline/'decisions.jsonl.gz'));after=deepcopy(before)
    frozen={r['line_id']:r for r in rows(source/'S4_lines.jsonl.gz') if not r['dev']}
    detector={r['line_id']:r for r in rows(source/'S6_lines.jsonl.gz') if not r['dev']}
    google={r['line_id']:r['gt'] for r in rows(google_path)}
    predictions={arm:defaultdict(dict) for arm in ('A','B','E')}
    for arm in predictions:
        path=Path('artifacts/labelfix_r1/output_3678928')/arm/'heldout_predictions.jsonl'
        key=next(k for k in ref['inputs'] if k.endswith('/'+arm+'/heldout_predictions.jsonl'))
        check(path,ref['inputs'][key]);check(path.with_suffix('.receipt.json'),ref['inputs'][key.replace('.jsonl','.receipt.json')])
        receipt=json.loads(path.with_suffix('.receipt.json').read_text())
        checkpoint=path.with_name('best.pt');check(checkpoint,receipt['checkpoint_sha256'])
        if receipt['prediction_sha256']!=sha256(path):raise ValueError('prediction receipt mismatch')
        for p in rows(path):
            if p['start'] in predictions[arm][p['line_id']]:raise ValueError('duplicate prediction')
            predictions[arm][p['line_id']][p['start']]=p
    ids={r['id'] for r in before}
    if len(before)!=666 or ids!=set(frozen) or ids!=set(detector):raise ValueError('held-out identity changed')
    # All textual changes in SF4 concern declared elision aliases. Prove there
    # are no alias misclassified as letters in this held-out instrument.
    if any(c.base.isalpha()!=is_letter(c.base) for r in detector.values() for c in clusters(nfd(r['recogniser_text']))):
        raise ValueError('held-out has an alias slot; requires full runtime replay')
    totals={phase:{m:Counter() for m in gate.MODES} for phase in ('before','after')}
    events={phase:[] for phase in totals};proof=[];changes=[]
    for b,a in zip(before,after):
        lid=b['id'];raw=detector[lid];text=raw['recogniser_text']
        pred={arm:predictions[arm][lid] for arm in predictions}
        for mode in gate.MODES:
            expected=[c.start for c in clusters(nfd(text)) if is_letter(c.base)]
            slots=a['decisions'][mode]['slots']
            if [s['start'] for s in slots]!=expected:raise ValueError('slot correspondence changed')
            by={s['start']:s for s in slots}
            # Punctuation, unsupported-edit guards and orthographic K1 are
            # unchanged on this exact cohort, before adding observation vetoes.
            render_slots=[dict(s,parts=by[s['start']]['parts']) for s in raw['recogniser_slots']]
            for policy in (oldgate,gate):
                rendered=policy._render_reading(text,render_slots).lstrip(policy.LEADING_QUOTES+' ')
                if raw.get('opening_quotes'):rendered='“'+rendered
                assert rendered==b['decisions'][mode]['text']
            assert oldgate.edit_guard(text,rendered)==gate.edit_guard(text,rendered)
            for s in render_slots:
                if s['base'] in gate.R1_LETTERS:
                    p=pred['A'].get(s['start']) or {}
                    s.update(mark_support_source='reader',reader_evidence={},naming={},mark_probabilities=p.get('mark_probabilities',{}))
                s['constraint_flags']=[]
            rd=LineReading(rendered,render_slots,[])
            assert oldgate.serialize(oldreading.apply_constraints(rd)[0])==gate.serialize(gate.R.apply_constraints(rd)[0])
            for s in raw['recogniser_slots']:
                prior=observation_reasons(oldgate,s,pred,text,raw.get('reading_flags',[]),mode)
                now=observation_reasons(gate,s,pred,text,raw.get('reading_flags',[]),mode)
                if prior-now:raise ValueError('SF4 removed a veto')
                added=now-prior
                if any(not z.startswith(('detector_clipped_','K1:')) for z in added):
                    raise ValueError('non-observation policy delta')
                target=by[s['start']];old=deepcopy(target)
                target['hold_reasons']=list(dict.fromkeys([*target['hold_reasons'],*sorted(added)]))
                if target['hold_reasons']:target['label_status']='HOLD'
                entry=dict(id=lid,mode=mode,start=s['start'],base=s['base'],parts=old['parts'],
                    before_status=old['label_status'],after_status=target['label_status'],
                    before_reasons=old['hold_reasons'],after_reasons=target['hold_reasons'],
                    accepted_after_implies_accepted_before=bool(target['hold_reasons']) or not old['hold_reasons'],
                    output_mark_sets_identical=old['parts']==target['parts'])
                assert entry['accepted_after_implies_accepted_before'] and entry['output_mark_sets_identical']
                proof.append(entry)
                if target!=old:changes.append(dict(**entry,evidence=s.get('evidence',{}),height_band=s.get('height_band'),case_class=s.get('case_class')))
            oldholds={s['start']:s for s in b['decisions'][mode]['hold_slots']}
            a['decisions'][mode]['hold_slots']=[dict(oldholds.get(s['start'],dict(start=s['start'],base=s['base'],parts=s['parts'],
                detector_parts=next(x['parts'] for x in raw['recogniser_slots'] if x['start']==s['start']),
                r1_parts=s['parts'],locator_span=next(x.get('locator_span') for x in raw['recogniser_slots'] if x['start']==s['start']))),
                reasons=s['hold_reasons']) for s in slots if s['hold_reasons']]
            assert a['decisions'][mode]['text']==b['decisions'][mode]['text']
        runtime=dict(id=lid,recogniser_text=text,r1_predictions=list(pred['A'].values()))
        for phase,r in [('before',b),('after',a)]:
            stats,ev=score_line(frozen[lid],google[lid],runtime,decisions=r['decisions'])
            for mode in gate.MODES:totals[phase][mode].update(stats[mode])
            events[phase].append(dict(id=lid,counts=stats,events=ev))
    if {m:dict(c) for m,c in totals['before'].items()}!=ref['modes']:raise ValueError('SF3 table not reproduced')
    if json.loads(json.dumps(events['before']))!=list(rows(baseline/'events.jsonl')):raise ValueError('SF3 per-slot outcomes not reproduced')
    safety={}
    for mode in gate.MODES:
        def unsafe(phase):return {(r['id'],e['start'],e['slot'],e['outcome']):e for r in events[phase] for e in r['events'][mode] if e['outcome'] in ('wrong','new')}
        old,new=unsafe('before'),unsafe('after')
        if not new.keys()<=old.keys():raise ValueError('new unsafe slot')
        for k in new:
            for field in ('google','truth','reader','outcome'):assert old[k][field]==new[k][field]
        safety[mode]=dict(no_added_wrong_or_new=True,identical_unsafe_slots=old==new,
            before=[dict(id=k[0],**v) for k,v in old.items()],after=[dict(id=k[0],**v) for k,v in new.items()])
    write_rows(out/'decisions.jsonl.gz',after);write_rows(out/'events.jsonl',events['after'])
    write_rows(out/'per_slot_proof.jsonl.gz',proof);write_rows(out/'slot_changes.jsonl.gz',changes)
    write_json(out/'reasons.json',reason_table(after))
    write_json(out/'comparison.json',dict(modes={phase:{m:dict(c) for m,c in totals[phase].items()} for phase in totals},
        wrong_new=safety,slot_mode_records=len(proof),changed_slot_mode_records=len(changes)))
    for path,digest in inputs.items():assert sha256(path)==digest
    receipt=dict(schema='sf4-saved-decision-delta-v1',complete=True,lines=666,google_errors=80,
        method=__doc__,full_runtime_recomposition=False,missing_extraction_coverage_synthesized=False,
        baseline_all_table_cells_and_error_events_reproduced=True,per_slot_acceptance_subset=True,
        punctuation_output_edit_guards_and_orthographic_K1_verified_unchanged=True,
        policy=gate.policy_binding(),inputs=inputs,measurement_script_sha256=sha256(Path(__file__)),
        detector_runs=0,r1_runs=0,ctc_runs=0,network=False,elapsed_seconds=time.monotonic()-started,
        outputs={p.name:sha256(p) for p in out.iterdir()})
    write_json(out/'receipt.json',receipt)
    print(json.dumps({phase:{m:dict(c) for m,c in totals[phase].items()} for phase in totals},indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,default=Path('docs/records/labelfix/spellcheck/SF3_evidence/heldout_after'))
    p.add_argument('--sf3-gate',type=Path,default=Path('artifacts/labelfix_sf4/before/greekocr/labelfix/release_gate.py'))
    p.add_argument('--google',type=Path,default=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/e3b/predictions/full_s0_v2_test.jsonl'))
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();measure(a.baseline,a.sf3_gate,a.google,a.out)


if __name__=='__main__':main()
