"""SF6 saved-evidence release replay. No network, pixels or inference.

Held-out uses the hash-bound SF5 frozen slot decisions, without inventing the
missing extraction coverage. M2 is filtered to DEV before JSON decoding.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import gzip
import json
from pathlib import Path
import random

from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.text import nfd
from scripts.labelfix.clariden import l1_common as common
from scripts.labelfix.clariden.r1_common import rows, write_rows, write_json, sha256
from scripts.labelfix import sf5_measure as sf5

DOC=sf5.DOC
EV=DOC/'SF6_evidence'
FROZEN=Path('artifacts/labelfix_sf6/frozen_sf5_05f2dafb')
CLASSES=('mark','apostrophe','quote','keraia','other')
KERAIA='a300f5e1c3f6a38d97201791-p000442-l0085'
PROBE=Path('docs/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v2_evidence/out_of_scope_quote_probe.json')
BINDING=dict(sf5.BINDING,policy_sha256='source-bound-SF6')


def baseline():
    return sf5.baseline(FROZEN)


def checked(path,receipt=None):
    digest=sha256(path)
    if receipt:
        assert digest==json.loads(receipt.read_text())['outputs'][path.name],path
    return digest


def prepare():
    """Copy fresh SF5 witnesses, plus all 48 L1A lines from saved evidence."""
    dest=EV/'witness_inputs.jsonl.gz'
    inputs=list(rows(DOC/'SF5_evidence/witness_inputs.jsonl.gz'))
    for r in inputs:r['cohort']='sf5'
    s8=Path.home()/'Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck'
    l1=Path.home()/'Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_evidence'
    audit=s8/'S8_DEV/private/audit/items_key.json'
    wanted={r['line_id'] for r in json.loads(audit.read_text()) if not r['control']}
    assert len(wanted)==48
    records={r['id']:r for r in rows('docs/harvest/collection/v2/import_real_v2_train.jsonl') if r['id'] in wanted}
    oldgate,oldcommon=baseline()
    for pool in ('200','vouli'):
        with gzip.open(l1/f'remote_{pool}.json.gz','rt') as f:remote=json.load(f)['runtime']
        for r in rows(l1/pool/'details.jsonl.gz'):
            lid=r['id']
            if lid not in wanted:continue
            saved=r['modes']['masked']['ENSEMBLE_AB'];rt=deepcopy(remote[lid])
            rt['detector']=r['detector']['masked']
            # L1M holds the reader fixed but remaps observation to the masked crop.
            rt['coverage']=[s['r1_coverage'] for s in saved['slots'] if s.get('r1_coverage') is not None]
            rt['peer_coverage']={'B':[s['peer_coverage'] for s in saved['slots'] if s.get('peer_coverage') is not None]}
            rt['peer_predictions']={'B':[s['peer_prediction'] for s in saved['slots'] if s.get('peer_prediction') is not None]}
            rt.pop('evidence_sha256',None)
            # The SF5 composer must reproduce all saved per-slot decisions exactly.
            actual=oldgate.compose_runtime(rt,'ENSEMBLE_AB')
            assert actual['slots']==saved['slots'],lid
            record=dict(records[lid],id=lid,script_class='greek_poly')
            inputs.append(dict(id=lid,cohort='l1a',kind='l1a_audit',record=record,runtime=rt))
    assert sum(r['cohort']=='l1a' for r in inputs)==48
    # Probe runtimes are fixtures of the reviewer's synthetic saved-text cases,
    # never claims of newly observed detector evidence.
    from tests.labelfix.test_sf5 import synthetic
    for i,case in enumerate(json.loads(PROBE.read_text())['cases']):
        record=dict(id=f'quote-probe-{i:02}',label=case['original'],script_class='greek_poly')
        rt=synthetic(case['recogniser'])
        rt['id']=record['id']
        prior=oldcommon.overlay(record,rt,case['mode'],BINDING)
        assert prior['label']==case['after'],(i,prior)
        inputs.append(dict(id=record['id'],cohort='quote_probe',kind='leading_quote',
                           mode=case['mode'],record=record,runtime=rt))
    write_rows(dest,inputs)
    paths=[DOC/'SF5_evidence/witness_inputs.jsonl.gz',audit,l1/'remote_200.json.gz',
           l1/'200/details.jsonl.gz',l1/'remote_vouli.json.gz',l1/'vouli/details.jsonl.gz',Path('docs/harvest/collection/v2/import_real_v2_train.jsonl'),PROBE]
    write_json(EV/'witness_inputs_receipt.json',dict(inputs={str(p):sha256(p) for p in paths},
        output_sha256=sha256(dest),cohorts=dict(Counter(r['cohort'] for r in inputs)),
        l1a_full_slot_parity=48,detector_runs=0,r1_runs=0,ctc_runs=0,network=False))


def effective(original,recogniser,decision,policy,runtime=None):
    label=sf5.effective_label(policy,original,recogniser,decision,sf5=True)
    checks=gate.deletion_guard(original,label['proposal'],runtime,decision) if runtime else []
    if any(not c['allowed'] for c in checks):label.update(status='hold',label=original,alias_only=False)
    label['deletion_checks']=checks
    return label


def census_summary(records):
    result={m:dict(before=Counter(),after=Counter(),held=Counter(),punctuation_held=Counter(),
                   all_held=Counter(),punctuation_all_held=Counter(),
                   single_source_before=0,single_source_after=0,uncertified_before=0,uncertified_after=0)
            for m in gate.MODES}
    for r in records:
        d=result[r['mode']];before=r['before'];after=r['after'];events=r['checks']
        if after['status']=='hold':
            cats={c['category'] for c in events if not c['allowed']}
            d['all_held'].update(cats)
            punct=cats&{'apostrophe','quote','keraia'}
            d['punctuation_all_held'].update(punct)
            d['punctuation_all_held']['union']+=bool(punct)
        for phase,label in [('before',before),('after',after)]:
            if label['status']=='hold':continue
            for event in events:
                d[phase][event['category']]+=1
                if not event['allowed']:d['uncertified_'+phase]+=1
                if sum(event['signals'].values())==1 and not event['allowed']:d['single_source_'+phase]+=1
        if before['status']!='hold' and after['status']=='hold':
            cats={c['category'] for c in events if not c['allowed']}
            d['held'].update(cats)
            # Counts by class can overlap; this is the distinct union.
            punct=cats&{'apostrophe','quote','keraia'}
            d['punctuation_held'].update(punct)
            d['punctuation_held']['union']+=bool(punct)
    return {m:{k:dict(v) if isinstance(v,Counter) else v for k,v in d.items()} for m,d in result.items()}


def witnesses():
    oldgate,oldcommon=baseline();result=[]
    inputs=list(rows(EV/'witness_inputs.jsonl.gz'))
    if (EV/'census_inputs.jsonl.gz').exists():inputs+=list(rows(EV/'census_inputs.jsonl.gz'))
    for w in inputs:
        mode=w.get('mode','ENSEMBLE_AB')
        before=oldcommon.overlay(w['record'],w['runtime'],mode,BINDING)
        after=common.overlay(w['record'],w['runtime'],mode,BINDING)
        assert oldgate.compose_runtime(w['runtime'],mode)['slots']==gate.compose_runtime(w['runtime'],mode)['slots']
        assert (before['status'],before.get('label'))==(after['status'],after.get('label')) or (
            before['status']!='hold' and after['status']=='hold'),w['id']
        checks=after['deletion_checks']
        result.append(dict(id=w['id'],cohort=w['cohort'],kind=w['kind'],mode=mode,
            google=w['record']['label'],recogniser=w['runtime']['recogniser_text'],
            before=dict(status=before['status'],label=before.get('label',w['record']['label'])),
            after=dict(status=after['status'],label=after.get('label',w['record']['label'])),checks=checks))
    write_rows(EV/'witness_results.jsonl.gz',result)
    summaries={c:census_summary([r for r in result if r['cohort']==c]) for c in {r['cohort'] for r in result}}
    write_json(EV/'witness_metrics.json',dict(cohorts=summaries,
        keraia_hold=next(r['after']['status']=='hold' for r in result if r['id']==KERAIA),
        quote_held=sum(r['after']['status']=='hold' for r in result if r['cohort']=='quote_probe'),
        quote_total=sum(r['cohort']=='quote_probe' for r in result)))


def heldout():
    from scripts.labelfix.clariden.l1e_measure import score_line
    decisions=DOC/'SF5_evidence/heldout/decisions.jsonl.gz'
    checked(decisions,DOC/'SF5_evidence/heldout/receipt.json')
    frozen=list(rows(decisions));det={r['line_id']:r for r in rows(DOC/'S6_lines.jsonl.gz') if not r['dev']}
    sources={r['line_id']:r for r in rows(DOC/'R0_evidence/continuity_666.jsonl')}
    truth={r['line_id']:r for r in rows(DOC/'S4_lines.jsonl.gz') if not r['dev']}
    assert len(frozen)==666 and {r['id'] for r in frozen}==set(det)==set(sources)==set(truth)
    oldgate,_=baseline();result=[];totals={p:{m:Counter() for m in gate.MODES} for p in ('before','after')}
    predictions={}
    for r in rows('artifacts/labelfix_r1/output_3678928/A/heldout_predictions.jsonl'):
        predictions.setdefault(r['line_id'],[]).append(r)
    slot_changes=[];proof=[]
    for line in frozen:
        lid=line['id'];s6=det[lid];rec=s6['recogniser_text'];google=sources[lid]['google']
        rt=dict(recogniser_text=rec,r1_predictions=predictions.get(lid,[]),coverage=[],
            detector=dict(text=s6['reading'],slots=s6['recogniser_slots'],
                opening_quotes=s6.get('opening_quotes',[]),constraint_flags=s6.get('reading_flags',[])))
        after_decisions=deepcopy(line['decisions'])
        for mode in gate.MODES:
            d=dict(line['decisions'][mode],mode=mode)
            before=effective(google,rec,d,oldgate)
            after=effective(google,rec,d,gate,rt)
            checks=after['deletion_checks']
            result.append(dict(id=lid,mode=mode,google=google,recogniser=rec,
                before=before,after=after,checks=checks))
            assert before['proposal']==after['proposal']
            # Keep the original slot instrument, then apply ONLY SF6's added
            # whole-line veto. Existing SF5 slot and line vetoes are unchanged.
            if any(not c['allowed'] for c in checks):
                d2=after_decisions[mode]
                for s in d2['slots']:s['hold_reasons']=[*s['hold_reasons'],'sf6:line_deletion_hold']
                d2['hold_slots']=[*d2['hold_slots'],dict(start=0,reasons=['sf6:line_deletion_hold'])]
            proof.extend(dict(id=lid,mode=mode,start=s['start'],slot_identical=True) for s in d['slots'])
        before_counts,before_events=score_line(truth[lid],google,rt,decisions=line['decisions'])
        after_counts,after_events=score_line(truth[lid],google,rt,decisions=after_decisions)
        for mode in gate.MODES:
            totals['before'][mode].update(before_counts[mode]);totals['after'][mode].update(after_counts[mode])
            for a,b in zip(before_events[mode],after_events[mode]):
                if a!=b:slot_changes.append(dict(id=lid,mode=mode,before=a,after=b))
    ref=json.loads((DOC/'SF5_evidence/heldout/metrics.json').read_text())
    assert {m:dict(c) for m,c in totals['before'].items()}==ref['mark_rows']['after']
    # Exact parity of SF5 effective labels/statuses, not just aggregate counts.
    ref_labels={(r['id'],r['mode']):r for r in rows(DOC/'SF5_evidence/heldout/release_labels.jsonl.gz') if r['phase']=='after'}
    for r in result:
        prior=ref_labels[r['id'],r['mode']]
        assert all(r['before'][k]==prior[k] for k in ('status','label','proposal')),r['id']
    models={lid:r['model'] for lid,r in sources.items()};sites=sf5.elision_truth(set(sources));elision={}
    for phase in totals:
        elision[phase]={m:sf5.score_elisions(sites,{r['id']:r[phase]['label'] for r in result if r['mode']==m},models)[0] for m in gate.MODES}
    dest=EV/'heldout';dest.mkdir(exist_ok=True)
    write_rows(dest/'release_labels.jsonl.gz',result);write_rows(dest/'per_slot_changes.jsonl',slot_changes)
    write_rows(dest/'per_slot_proof.jsonl.gz',proof)
    write_json(dest/'metrics.json',dict(marks={p:{m:dict(c) for m,c in q.items()} for p,q in totals.items()},
        elision=elision,deletions=census_summary(result),release_counts=release_counts(result),
        legacy_slot_rows_unchanged=True,full_runtime_recomposition=False,coverage_synthesized=False,
        truth=ref['truth']))
    receipt(dest,[decisions,DOC/'SF5_evidence/heldout/release_labels.jsonl.gz',DOC/'SF5_evidence/heldout/metrics.json',
        DOC/'S6_lines.jsonl.gz',DOC/'S4_lines.jsonl.gz',DOC/'R0_evidence/continuity_666.jsonl',
        DOC/'R0_evidence/scoring/punctuation_sites.jsonl',Path('artifacts/labelfix_r1/output_3678928/A/heldout_predictions.jsonl')])


def release_counts(result):
    return {p:{m:dict(Counter(r[p]['status'] for r in result if r['mode']==m)) for m in gate.MODES}
            for p in ('before','after')}


def m2():
    from scripts.labelfix.sf3_measure import dev_inventory,dev_runtime
    from scripts.labelfix import m2_score as score
    score.MODES=gate.MODES
    manifest=DOC/'SF3_evidence/m2_dev_manifest.jsonl';cache=Path('.cache/labelfix/m2/runtime.jsonl')
    inv=dev_inventory(manifest);runs=dev_runtime(cache,{r['id'] for r in inv});by={r['id']:r for r in inv}
    oldgate,_=baseline();result=[];before_rt={};after_rt={};proof=[]
    for rt in runs:
        lid=rt['id'];google=by[lid]['google_label'];decisions={m:oldgate.compose_runtime(rt,m) for m in gate.MODES}
        before_rt[lid]=dict(rt,modes=decisions);after_rt[lid]=deepcopy(before_rt[lid])
        for mode,d in decisions.items():
            assert d['slots']==gate.compose_runtime(rt,mode)['slots']
            proof.extend(dict(id=lid,mode=mode,start=s['start'],slot_identical=True) for s in d['slots'])
            before=effective(google,rt['recogniser_text'],d,oldgate)
            after=effective(google,rt['recogniser_text'],d,gate,rt)
            result.append(dict(id=lid,mode=mode,google=google,recogniser=rt['recogniser_text'],
                before=before,after=after,checks=after['deletion_checks']))
            if any(not c['allowed'] for c in after['deletion_checks']):
                for s in after_rt[lid]['modes'][mode]['slots']:
                    s['hold_reasons']=[*s['hold_reasons'],'sf6:line_deletion_hold'];s['hold']=True
                after_rt[lid]['modes'][mode]['hold_slots'].append(dict(start=0,reasons=['sf6:line_deletion_hold']))
    ledger=score.pair_ledger(inv);metrics={};pair_results={}
    for phase,runtime in [('before',before_rt),('after',after_rt)]:
        pairs=[score.score_case(c,by[c['id']],runtime[c['id']]) for c in ledger if c['included']]
        lines=[]
        for line in inv:
            r=runtime[line['id']];changes,cov=score.changes_for(line,r)
            lines.append(dict(**line,**{k:v for k,v in r.items() if k!='id'},changes=changes,
                              reference_change_alignment_coverage=cov))
        metrics[phase]=score.summarize(inv,runtime,pairs,lines)['POOLED'];pair_results[phase]=pairs
    assert metrics['before']==json.loads((DOC/'SF5_evidence/m2_dev/metrics.json').read_text())['after']['marks']
    changes=[dict(before=a,after=b) for a,b in zip(pair_results['before'],pair_results['after']) if a!=b]
    control_changes=[]
    for line in inv:
        lid=line['id'];a,_=score.changes_for(line,before_rt[lid]);b,_=score.changes_for(line,after_rt[lid])
        for mode in gate.MODES:
            prior={s['google_nfd_start']:s for s in a[mode]}
            for s in b[mode]:
                old=prior.get(s['google_nfd_start'])
                if old and old['status']!=s['status']:
                    control_changes.append(dict(id=lid,mode=mode,before=old,after=s))
    dest=EV/'m2_dev';dest.mkdir(exist_ok=True)
    write_rows(dest/'release_labels.jsonl.gz',result);write_rows(dest/'per_slot_proof.jsonl.gz',proof)
    write_rows(dest/'per_slot_changes.jsonl',changes)
    write_rows(dest/'control_slot_changes.jsonl',control_changes)
    write_json(dest/'metrics.json',dict(marks=metrics,deletions=census_summary(result),release_counts=release_counts(result),
        elision_truth='UNKNOWN: no certified DEV punctuation truth',dev_lines=len(inv),locked_ii_records_decoded=0))
    receipt(dest,[manifest,cache,DOC/'SF5_evidence/m2_dev/metrics.json'])


def receipt(dest,inputs):
    write_json(dest/'receipt.json',dict(policy=gate.policy_binding(),network=False,detector_runs=0,r1_runs=0,ctc_runs=0,
        inputs={str(p):sha256(p) for p in inputs},script_sha256=sha256(Path(__file__)),
        outputs={p.name:sha256(p) for p in dest.iterdir() if p.name!='receipt.json'}))


def add_census(path):
    """Accept a pulled JSON/JSONL(.gz) census with saved runtime or overlays.

    Each deletion row needs record+runtime, or a full SF5 overlay (including
    edit evidence) plus google/original_label. Nothing missing is synthesized.
    """
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt') as f:data=f.read()
    try:
        decoded=json.loads(data)
        values=(decoded if isinstance(decoded,list) else
                next((decoded[k] for k in ('records','cases','lines') if k in decoded),[decoded]))
    except json.JSONDecodeError:values=[json.loads(line) for line in data.splitlines() if line.strip()]
    material_paths=[]
    if isinstance(values,list) and len(values)==1 and 'modes' in values[0]:
        # L1R2's pulled CHANGES.json is an aggregate with up to 20 examples per
        # class/wave, not a runtime export. Never turn those IDs into evidence.
        aggregate=values[0];ids=set()
        def collect(node):
            if not isinstance(node,dict):return
            for key,value in node.items():
                if key=='deletions_by_class':
                    for bucket in value.values():ids.update(bucket.get('example_ids',()))
                else:collect(value)
        collect(aggregate.get('modes',{}).get('ENSEMBLE_AB',{}))
        if len(ids)<30:raise ValueError(f'census witnesses pending: only {len(ids)} AB deletion example IDs; need 30')
        candidates_paths=[]
        for parent in [path.parent,*list(path.parents)[1:3]]:
            candidates_paths.extend(parent/name for name in ('witness_inputs.jsonl.gz','deletion_witness_inputs.jsonl.gz',
                'overlay_ensemble_ab.jsonl.gz','release/overlay_ensemble_ab.jsonl.gz'))
        if aggregate.get('witness_inputs_file'):
            candidates_paths.insert(0,path.parent/aggregate['witness_inputs_file'])
        candidates_paths.append(EV/'witness_inputs.jsonl.gz')
        supplied={};overlays={}
        for candidate in dict.fromkeys(candidates_paths):
            if not candidate.is_file():continue
            material_paths.append(candidate)
            for r in rows(candidate):
                lid=r.get('id',r.get('line_id'))
                if lid not in ids:continue
                if 'runtime' in r and 'record' in r:supplied[lid]=r
                elif r.get('status')=='corrected' and r.get('changes'):overlays[lid]=r
        needed=set(overlays)-supplied.keys()
        originals=({r['id']:r['label'] for r in rows('docs/harvest/collection/v2/import_real_v2_train.jsonl') if r['id'] in needed}
                   if needed else {})
        supplied.update({lid:dict(line_id=lid,original_label=originals[lid],overlay=o)
                         for lid,o in overlays.items() if lid in originals and lid not in supplied})
        if len(supplied)<30:
            write_json(EV/'census_pending.json',dict(census=str(path),sha256=sha256(path),seed=6,
                candidate_ids=sorted(ids),available_saved_inputs=sorted(supplied),
                missing_saved_inputs=sorted(ids-supplied.keys()),
                required='Place deletion_witness_inputs.jsonl.gz (record+runtime), or overlay_ensemble_ab.jsonl.gz, beside CHANGES.json; then rerun --add-census'))
            raise ValueError(f'census witnesses pending: {len(supplied)}/{len(ids)} AB example IDs have saved runtime/overlays; see census_pending.json')
        values=list(supplied.values())
    candidates={}
    oldgate,oldcommon=baseline()
    for r in values:
        lid=r.get('id',r.get('line_id'))
        if 'runtime' in r and 'record' in r:w=dict(r,id=lid)
        else:
            o=r.get('overlay',r.get('sf5_overlay'))
            if o is None and 'changes' in r:o=r
            original=r.get('google',r.get('original_label'))
            if o is None or original is None:
                raise ValueError('census needs saved runtime or full overlay and original_label: '+str(lid))
            assert common.label_sha(original)==o['original_label_sha256'],lid
            w=dict(id=lid,record=dict(id=lid,label=original,script_class='greek_poly'),runtime=sf5.runtime_from_overlay(o))
        prior=oldcommon.overlay(w['record'],w['runtime'],'ENSEMBLE_AB',BINDING)
        if 'runtime' not in r:
            assert (prior['status'],prior.get('label'))==(o['status'],o.get('label')),lid
        if prior['status']=='hold' or not gate.google_deletions(w['record']['label'],prior['label']):continue
        assert lid not in candidates,'duplicate census line: '+lid
        candidates[lid]=dict(w,cohort='census',kind='seeded_census',mode='ENSEMBLE_AB')
    if len(candidates)<30:raise ValueError(f'need 30 distinct released deletion lines; got {len(candidates)}')
    ids=random.Random(6).sample(sorted(candidates),30)
    write_rows(EV/'census_inputs.jsonl.gz',[candidates[lid] for lid in ids])
    write_json(EV/'census_receipt.json',dict(path=str(path),sha256=sha256(path),seed=6,
        eligible_lines=len(candidates),selected_ids=ids,output_sha256=sha256(EV/'census_inputs.jsonl.gz'),
        saved_materials={str(p):sha256(p) for p in material_paths}))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('instrument',choices=['prepare','witnesses','heldout','m2','all'],nargs='?',default='all')
    p.add_argument('--add-census',type=Path)
    a=p.parse_args();EV.mkdir(exist_ok=True)
    if a.add_census:add_census(a.add_census)
    for name,fn in [('prepare',prepare),('witnesses',witnesses),('heldout',heldout),('m2',m2)]:
        if a.instrument in (name,'all'):fn();print('complete:',name,flush=True)
    if a.add_census:
        # The one-command addition updates the regression tests and report too.
        import os,subprocess,sys
        with (EV/'tests_after.log').open('w') as f:
            completed=subprocess.run([sys.executable,'-m','pytest','tests/labelfix','-q','-p','no:cacheprovider'],
                stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONPATH=str(Path.cwd())))
        from scripts.labelfix.sf6_report import main as report
        report()
        from scripts.labelfix.sf6_verify import main as verify
        verify()
        if completed.returncode:raise SystemExit(completed.returncode)


if __name__=='__main__':main()
