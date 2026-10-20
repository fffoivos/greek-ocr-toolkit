"""SF5 offline release replay. Saved evidence only; no inference or network.

The 56 witnesses use the saved AB runtime fields. The 666 instrument retains
its complete saved SF4 slot decisions (full extraction coverage is unavailable)
and replays only the release text rules. M2 is filtered to the DEV allowlist
before decoding cached records. No locked (ii) record is evaluated.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import sys

from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.text import (clusters, nfd, nfc, is_letter, punctuation_sites,
                                   elision_alias_key, ELISION, spacing_breathing)
from scripts.labelfix.clariden import l1_common as common
from scripts.labelfix.clariden.r1_common import rows, sha256, write_json, write_rows

DOC = Path('docs/records/labelfix/spellcheck')
SIX = {
    '399d224c580127635c47cd8d-p000019-l0010': 'mu_elision',
    '32aae9fec147d3b483deb96e-p000052-l0026': 'kappa_elision',
    'a963b33d02c23d4127f5ec26-p000012-l0029': 'capital_breathing',
    '32aae9fec147d3b483deb96e-p000060-l0057': 'capital_breathing',
    '00c322b3ee04b419d1979f22-p000115-l0022': 'known_reader_breathing',
    '827d2345ad77e5cdec320e80-p000028-l0019': 'known_reader_subscript',
}
BINDING = dict(detector='s6', r1_sha256='saved-A', policy_sha256='source-bound-SF5')


def baseline(root=Path('artifacts/labelfix_sf5/before')):
    """Load all three frozen c6064650 sources without changing package imports."""
    names = ('greekocr.labelfix.text', 'greekocr.labelfix.release_gate',
             'scripts.labelfix.clariden.l1_common')
    paths = ('greekocr/labelfix/text.py', 'greekocr/labelfix/release_gate.py',
             'scripts/labelfix/clariden/l1_common.py')
    previous = {n: sys.modules.get(n) for n in names}
    loaded = []
    try:
        for name, path in zip(names, paths):
            spec = importlib.util.spec_from_file_location(name, root/path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            loaded.append(module)
    finally:
        for name, module in previous.items():
            if module is None: sys.modules.pop(name, None)
            else: sys.modules[name] = module
    return loaded[1], loaded[2]


def runtime_from_overlay(overlay, raw=None, mode=None):
    """Recover only fields actually retained by the saved accepted AB overlay.

    Six L1M witnesses retain the entire raw detector. The 50 overlays retain
    every release gate input used by their accepted decisions, with geometry
    in per-slot evidence. No peer E record was saved here; it remains absent.
    Frozen-SF4 recomposition must reproduce all 56 labels before use.
    """
    ev = overlay['changes'][0]['evidence']
    details = {s['start']: s for s in ev['slots']}
    slots = (mode or {}).get('slots', overlay['gate_decisions'])
    if raw is None:
        rawslots = []
        for s in slots:
            d = details[s['start']]
            z = deepcopy(s)
            z.update(parts=s['detector_parts'], locator_span=d['locator_span'])
            # These are saved observation labels, not newly inferred geometry.
            z['case_class'] = s['evidence'].get('case_class')
            rawslots.append(z)
        raw = dict(text=ev['detector_text'], slots=rawslots, unnamed=[],
                   opening_quotes=overlay['opening_quotes'], constraint_flags=[])
    predictions, coverage, peers, pcov = [], [], [], []
    for s in slots:
        if s.get('r1_coverage') is not None:
            predictions.append(dict(start=s['start'], base=s['base'], parts=s['r1_parts'],
                                    mark_probabilities=details[s['start']].get('mark_probabilities')))
            coverage.append(s['r1_coverage'])
        if s.get('peer_prediction') is not None: peers.append(s['peer_prediction'])
        if s.get('peer_coverage') is not None: pcov.append(s['peer_coverage'])
    return dict(id=overlay['line_id'], recogniser_text=ev['recogniser_text'],
                detector=deepcopy(raw), r1_predictions=predictions, coverage=coverage,
                peer_predictions={'B': peers}, peer_coverage={'B': pcov})


def prepare_witnesses(out):
    ids = (DOC/'SF5_witness/witness_50_ids.txt').read_text().splitlines()
    overlays = {r['line_id']: r for r in rows(DOC/'SF5_witness/sf5_witness_50_ab_records.jsonl.gz')}
    assert set(ids) == set(overlays) and len(ids) == 50
    wanted = set(ids) | SIX.keys()
    source = Path('docs/records/harvest/collection/v2/import_real_v2_train.jsonl')
    records = {}
    for r in rows(source):
        lid = r.get('id', r.get('line_id'))
        if lid in wanted: records[lid] = dict(r, id=lid, script_class='greek_poly')
    assert set(records) == wanted
    result = []
    for lid in ids:
        o = overlays[lid]
        result.append(dict(id=lid, kind='seeded_elision', record=records[lid],
                           runtime=runtime_from_overlay(o), before=o['label'], before_status=o['status']))
    l1m = Path.home()/'Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_evidence/200/details.jsonl.gz'
    for r in rows(l1m):
        if r['id'] not in SIX: continue
        o = r['overlays']['masked']['ENSEMBLE_AB']
        assert common.label_sha(records[r['id']]['label'])==o['original_label_sha256']
        result.append(dict(id=r['id'], kind=SIX[r['id']], record=records[r['id']],
            runtime=runtime_from_overlay(o, r['detector']['masked'], r['modes']['masked']['ENSEMBLE_AB']),
            before=o['label'], before_status=o['status']))
    assert len(result) == 56
    oldgate, oldcommon = baseline()
    for r in result:
        assert common.label_sha(r['record']['label']) == (
            overlays[r['id']]['original_label_sha256'] if r['id'] in overlays else common.label_sha(r['record']['label']))
        o = oldcommon.overlay(r['record'], r['runtime'], 'ensemble_ab', BINDING)
        assert (o['status'], o.get('label')) == (r['before_status'], r['before']), (r['id'], o['status'], o.get('label'))
        r['sf4_decisions'] = oldgate.compose_runtime(r['runtime'], 'ENSEMBLE_AB')
    write_rows(out/'witness_inputs.jsonl.gz', result)
    write_json(out/'witness_inputs_receipt.json', dict(lines=56, frozen_sf4_labels_reproduced=56,
        diagnostic_E_saved=False, detector_runs=0, r1_runs=0, ctc_runs=0,
        inputs={str(p):sha256(p) for p in (source,l1m,DOC/'SF5_witness/sf5_witness_50_ab_records.jsonl.gz',DOC/'SF5_witness/witness_50_ids.txt')},
        runtime_sha256=sha256(out/'witness_inputs.jsonl.gz')))
    return result


def witnesses(out):
    inputs = list(rows(out/'witness_inputs.jsonl.gz'))
    result = []
    for r in inputs:
        o = common.overlay(r['record'], r['runtime'], 'ensemble_ab', BINDING)
        before = r['before']; after = o.get('label', r['record']['label'])
        g = punctuation_sites(r['record']['label']); rec = punctuation_sites(r['runtime']['recogniser_text'])
        both = g.keys() & rec.keys(); final = punctuation_sites(after)
        # Only the two text rules and spelling accounting may change. The
        # accepted per-letter decisions and all raw evidence remain identical.
        now = gate.compose_runtime(r['runtime'], 'ENSEMBLE_AB')
        assert now['slots'] == r['sf4_decisions']['slots'], r['id']
        result.append(dict(id=r['id'],kind=r['kind'],google=r['record']['label'],
            recogniser=r['runtime']['recogniser_text'],before=before,after=after,
            before_status=r['before_status'],after_status=o['status'],alias_only=o['alias_only'],
            consensus=len(both),consensus_kept=len(both & final.keys()),
            consensus_deleted=len(both-final.keys()),elision_census=o['elision_census'],
            combining_marks_changed=nfd(''.join(c.base+c.marks for c in clusters(nfd(before)) if is_letter(c.base))) !=
                                    nfd(''.join(c.base+c.marks for c in clusters(nfd(after)) if is_letter(c.base))),
            changes=o['changes']))
    write_rows(out/'witness_results.jsonl.gz',result)
    return result


def mapped_elisions(text, model):
    """R0 punctuation scopes include printed initial elisions ('ς, 'φελα).

    Count their emitted sign too. Only the SF5 preservation rule is restricted
    to word-final elisions; a present initial sign must not score as deleted.
    Spacing breathings are excluded in either position.
    """
    from scripts.labelfix.r0_score import align
    a=''.join(c.base for c in clusters(nfd(model)) if is_letter(c.base))
    b=''.join(c.base for c in clusters(nfd(text)) if is_letter(c.base))
    mapping={j:i for i,j in align(a,b,True) if i is not None and j is not None}
    signs=punctuation_sites(text,lambda cs,i:cs[i].base in ELISION and not cs[i].marks
                            and not spacing_breathing(cs,i))
    return {mapping[k-1]+1 if k-1 in mapping else mapping[k] if k in mapping
            else 0 if k==0 else len(a) for k in signs}


def elision_truth(ids):
    """Read continuity scopes only; human reference is used only if adjudicated.

    The R0 site records certify punctuation scopes, never whole lines. A human
    Wikisource emission agreeing with a resolved site supplies its text; an
    absent/disagreeing human emission falls back to the literal R0 judgment.
    """
    path=DOC/'R0_evidence/scoring/punctuation_sites.jsonl'
    result=[]
    with path.open() as f:
        for line in f:
            # Do not decode any new-source locked truth while using this file.
            if '"stratum": "continuity_666"' not in line:continue
            r=json.loads(line)
            if r['line_id'] not in ids:continue
            r['truth_source']=('human_Wikisource_pixel_adjudicated_by_R0'
                if r['status']=='KNOWN' and
                   ((r['printed_role']=='apostrophe_elision' and r['emitted']['human'] in set("'’ʼ᾽᾿`´"))
                    or (r['printed_role']=='absent' and r['emitted']['human']==''))
                else 'R0_adjudication')
            result.append(r)
    return result


def score_elisions(sites,texts,models):
    counts=Counter(kept=0,deleted=0,added=0,positive_sites=0,negative_sites=0,unknown_sites=0)
    events=[];mapped={lid:mapped_elisions(text,models[lid]) for lid,text in texts.items()}
    for r in sites:
        if r['status']!='KNOWN':counts['unknown_sites']+=1;continue
        if r['printed_role']=='quote':
            # R0 explicitly calls two curly/ASCII terminal signs closing
            # quotes. Their presence is not an added elision apostrophe.
            counts['excluded_quote_sites']+=1
            continue
        present=r['letter_boundary'] in mapped[r['line_id']]
        positive=r['printed_role']=='apostrophe_elision'
        counts['positive_sites' if positive else 'negative_sites']+=1
        outcome=('kept' if present else 'deleted') if positive else ('added' if present else 'absent')
        counts[outcome]+=1
        events.append(dict(id=r['line_id'],boundary=r['letter_boundary'],outcome=outcome,
            printed_role=r['printed_role'],truth_source=r['truth_source'],card_ids=r['card_ids']))
    return dict(counts),events


def effective_label(policy,original,recogniser,decision,*,sf5):
    proposal=decision['text'];census={};alias_only=False
    if sf5:
        proposal,census=gate.release_text(original,recogniser,proposal)
        alias_only=(nfd(original)!=nfd(decision['text']) and
                    elision_alias_key(original)==elision_alias_key(decision['text']))
    census=source_census(original,recogniser,proposal)
    holds=[*decision['hold_slots'],*policy.edit_guard(original,recogniser),*policy.edit_guard(original,proposal)]
    status='hold' if holds else 'unchanged' if nfd(original)==nfd(proposal) else 'corrected'
    return dict(status=status,label=original if status=='hold' else proposal,
                proposal=proposal,alias_only=alias_only and status=='unchanged',elision_census=census)


def source_census(original,recogniser,proposal):
    """Same source domain in both phases; presence is read from that phase."""
    _,c=gate.release_text(original,recogniser,proposal)
    if not c['aligned']:return dict(c,unaligned_lines=1,aligned_lines=0)
    g=punctuation_sites(original).keys();r=punctuation_sites(recogniser).keys()
    p=punctuation_sites(proposal).keys()
    for name,sites in [('both',g&r),('google_only',g-r),('recogniser_only',r-g)]:
        c[name+'_kept']=len(sites&p);c[name+'_deleted']=len(sites-p)
    c['added']=len(p-g)
    return dict(c,unaligned_lines=0,aligned_lines=1)


def heldout(out):
    """Retain frozen slot decisions; rerender and apply SF5 release text only."""
    from scripts.labelfix.clariden.l1e_measure import score_line
    oldgate,_=baseline()
    paths=[DOC/'SF4_evidence/heldout/decisions.jsonl.gz',DOC/'S6_lines.jsonl.gz',
           DOC/'S4_lines.jsonl.gz',DOC/'R0_evidence/continuity_666.jsonl',
           DOC/'R0_evidence/scoring/punctuation_sites.jsonl',
           Path('artifacts/labelfix_r1/output_3678928/A/heldout_predictions.jsonl'),
           DOC/'SF4_evidence/heldout/comparison.json',DOC/'SF4_evidence/heldout/receipt.json']
    sf4_receipt=json.loads(paths[7].read_text())
    assert sha256(paths[0])==sf4_receipt['outputs'][paths[0].name]
    assert sha256(paths[6])==sf4_receipt['outputs'][paths[6].name]
    for path in paths:
        if str(path) in sf4_receipt['inputs']:assert sha256(path)==sf4_receipt['inputs'][str(path)]
    before=list(rows(paths[0]));detector={r['line_id']:r for r in rows(paths[1]) if not r['dev']}
    truth={r['line_id']:r for r in rows(paths[2]) if not r['dev']}
    sources={r['line_id']:r for r in rows(paths[3])}
    ids={r['id'] for r in before}
    assert len(before)==666 and ids==set(detector)==set(truth)==set(sources)
    sites=elision_truth(ids)
    predictions={}
    for r in rows(paths[5]):
        predictions.setdefault(r['line_id'],[]).append(r)
    totals={p:{m:Counter() for m in gate.MODES} for p in ('before','after')}
    release={p:{m:{} for m in gate.MODES} for p in totals}
    events={p:[] for p in totals};proof=[];mode_records=[]
    for b in before:
        lid=b['id'];raw=detector[lid];recogniser=raw['recogniser_text'];a=deepcopy(b)
        for mode in gate.MODES:
            old=b['decisions'][mode];new=a['decisions'][mode]
            by={s['start']:s for s in new['slots']}
            render_slots=[dict(s,parts=by[s['start']]['parts']) for s in raw['recogniser_slots']]
            prior=oldgate._render_reading(recogniser,render_slots).lstrip(oldgate.LEADING_QUOTES+' ')
            rendered=gate._render_reading(recogniser,render_slots).lstrip(gate.LEADING_QUOTES+' ')
            if raw.get('opening_quotes'):prior='“'+prior;rendered='“'+rendered
            assert prior==old['text'],lid
            assert oldgate.edit_guard(recogniser,prior)==gate.edit_guard(recogniser,rendered),lid
            new['text']=rendered
            for s,t in zip(old['slots'],new['slots']):
                assert s==t
                proof.append(dict(id=lid,mode=mode,start=s['start'],base=s['base'],
                    parts=s['parts'],hold_reasons=s['hold_reasons'],slot_identical=True))
            for phase,policy,d in [('before',oldgate,old),('after',gate,new)]:
                release[phase][mode][lid]=effective_label(policy,sources[lid]['google'],recogniser,d,sf5=phase=='after')
        rt=dict(recogniser_text=recogniser,r1_predictions=predictions.get(lid,[]))
        for phase,r in [('before',b),('after',a)]:
            stats,ev=score_line(truth[lid],sources[lid]['google'],rt,decisions=r['decisions'])
            for mode in gate.MODES:totals[phase][mode].update(stats[mode])
            events[phase].append(dict(id=lid,counts=stats,events=ev))
        mode_records.append(a)
    frozen=json.loads(paths[6].read_text())['modes']['after']
    assert {m:dict(v) for m,v in totals['before'].items()}==frozen
    assert totals['before']==totals['after']
    assert events['before']==events['after']
    models={lid:r['model'] for lid,r in sources.items()}
    elision={p:{} for p in totals};elision_events=[];release_counts={};census={}
    for phase in totals:
        release_counts[phase]={};census[phase]={}
        for mode in gate.MODES:
            vv=release[phase][mode]
            elision[phase][mode]={}
            for kind,key in [('candidate','proposal'),('effective_release','label')]:
                counts,ee=score_elisions(sites,{lid:r[key] for lid,r in vv.items()},models)
                elision[phase][mode][kind]=counts
                elision_events.extend(dict(phase=phase,mode=mode,scope=kind,**e) for e in ee)
            release_counts[phase][mode]=dict(Counter(r['status'] for r in vv.values()),
                alias_only=sum(r['alias_only'] for r in vv.values()))
            c=Counter()
            for r in vv.values():
                c.update({k:v for k,v in r['elision_census'].items() if k!='aligned'})
            census[phase][mode]=dict(c)
    result=dict(mark_rows={p:{m:dict(c) for m,c in q.items()} for p,q in totals.items()},
        elision=elision,release_counts=release_counts,elision_census=census,
        truth=dict(positive_sites=sum(s['status']=='KNOWN' and s['printed_role']=='apostrophe_elision' for s in sites),
            known_negative_sites=sum(s['status']=='KNOWN' and s['printed_role']=='absent' for s in sites),
            excluded_quote_sites=sum(s['status']=='KNOWN' and s['printed_role']=='quote' for s in sites),
            unknown_sites=sum(s['status']!='KNOWN' for s in sites),
            lines=len({s['line_id'] for s in sites if s['status']=='KNOWN' and s['printed_role']!='quote'}),
            full_lines_certified=0,sources=dict(Counter(s['truth_source'] for s in sites if s['status']=='KNOWN' and s['printed_role']!='quote')),
            positive_sources=dict(Counter(s['truth_source'] for s in sites if s['status']=='KNOWN' and s['printed_role']=='apostrophe_elision'))),
        mark_events_identical=True,slot_mode_records_identical=len(proof),
        method=__doc__,full_runtime_recomposition=False)
    dest=out/'heldout';dest.mkdir(exist_ok=True)
    write_json(dest/'metrics.json',result);write_rows(dest/'elision_events.jsonl',elision_events)
    write_rows(dest/'per_slot_proof.jsonl.gz',proof);write_rows(dest/'decisions.jsonl.gz',mode_records)
    write_rows(dest/'release_labels.jsonl.gz',[dict(phase=p,mode=m,id=lid,**r) for p,q in release.items() for m,v in q.items() for lid,r in v.items()])
    write_json(dest/'receipt.json',dict(policy=gate.policy_binding(),lines=666,complete=True,
        inputs={str(p):sha256(p) for p in paths},detector_runs=0,r1_runs=0,ctc_runs=0,network=False,
        extraction_coverage_synthesized=False,locked_ii_records_evaluated=0,
        script_sha256=sha256(Path(__file__)),outputs={p.name:sha256(p) for p in dest.iterdir() if p.name!='receipt.json'}))
    return result


def m2_dev(out):
    from scripts.labelfix.sf3_measure import dev_inventory,dev_runtime
    from scripts.labelfix import m2_score as score
    oldgate,_=baseline();score.MODES=gate.MODES
    manifest=DOC/'SF3_evidence/m2_dev_manifest.jsonl'
    inv=dev_inventory(manifest);allowed={r['id'] for r in inv}
    assert len(inv)==273
    assert all(r['human'] is None for r in rows(manifest))
    line_ids={r['line_id'] for r in inv};certified_dev=[]
    punct=DOC/'R0_evidence/scoring/punctuation_sites.jsonl'
    with punct.open() as f:
        for line in f:
            match=re.search(r'"line_id":\s*("(?:[^"\\]|\\.)*")',line)
            if match and json.loads(match[1]) in line_ids:certified_dev.append(json.loads(line))
    assert not certified_dev, 'New DEV punctuation truth exists; use it instead of UNKNOWN'
    cache=Path('.cache/labelfix/m2/runtime.jsonl')
    runs=dev_runtime(cache,allowed);by={r['id']:r for r in inv}
    ledger=score.pair_ledger(inv);result={};proof=[];outputs=[]
    for phase,policy in [('before',oldgate),('after',gate)]:
        runtime={}
        for r in runs:
            r=deepcopy(r);r['modes']={m:policy.compose_runtime(r,m) for m in gate.MODES};runtime[r['id']]=r
            outputs.append(dict(phase=phase,id=r['id'],modes=r['modes']))
        pairs=[score.score_case(c,by[c['id']],runtime[c['id']]) for c in ledger if c['included']]
        lines=[];census={m:Counter() for m in gate.MODES};release_counts={m:Counter() for m in gate.MODES}
        for line in inv:
            r=runtime[line['id']];changes,cov=score.changes_for(line,r)
            lines.append(dict(**line,**{k:v for k,v in r.items() if k!='id'},changes=changes,
                reference_change_alignment_coverage=cov))
            for mode in gate.MODES:
                label=effective_label(policy,line['google_label'],r['recogniser_text'],r['modes'][mode],sf5=phase=='after')
                release_counts[mode][label['status']]+=1
                release_counts[mode]['alias_only']+=label['alias_only']
                census[mode].update({k:v for k,v in label['elision_census'].items() if k!='aligned'})
        metrics=score.summarize(inv,runtime,pairs,lines)
        result[phase]=dict(marks=metrics['POOLED'],release_counts={m:dict(c) for m,c in release_counts.items()},
            elision_census={m:dict(c) for m,c in census.items()},
            elision={m:dict(kept=None,deleted=None,added=None,positive_sites=0,negative_sites=0,
                truth_source='UNKNOWN: DEV manifest human=null; R0b punctuation adjudications cover locked (ii), not DEV') for m in gate.MODES})
        if phase=='before':prior=runtime;prior_pairs=pairs
        else:
            assert pairs==prior_pairs
            for lid,r in runtime.items():
                for mode in gate.MODES:
                    a=prior[lid]['modes'][mode];b=r['modes'][mode]
                    assert a['slots']==b['slots'] and a['hold_slots']==b['hold_slots'],lid
                    proof.extend(dict(id=lid,mode=mode,start=s['start'],slot_identical=True) for s in b['slots'])
    assert result['before']['marks']==result['after']['marks']
    dest=out/'m2_dev';dest.mkdir(exist_ok=True)
    write_json(dest/'metrics.json',result);write_rows(dest/'decisions.jsonl.gz',outputs)
    write_rows(dest/'per_slot_proof.jsonl.gz',proof)
    write_json(dest/'receipt.json',dict(policy=gate.policy_binding(),complete=True,dev_lines=273,
        allowed_card_ids=sorted(allowed),locked_ii_records_decoded_or_composed=0,
        truth_positive_sites=0,truth_negative_sites=0,elision_truth_unknown=True,
        slot_mode_records_identical=len(proof),mark_rows_and_pair_events_identical=True,
        inputs={str(manifest):sha256(manifest),str(cache):sha256(cache),str(punct):sha256(punct)},
        detector_runs=0,r1_runs=0,ctc_runs=0,network=False,script_sha256=sha256(Path(__file__)),
        outputs={p.name:sha256(p) for p in dest.iterdir() if p.name!='receipt.json'}))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('instrument',choices=['prepare','witnesses','heldout','m2'])
    p.add_argument('--out',type=Path,default=DOC/'SF5_evidence')
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    result={'prepare':prepare_witnesses,'witnesses':witnesses,'heldout':heldout,'m2':m2_dev}[a.instrument](a.out)
    print('complete:',a.instrument,len(result))


if __name__=='__main__':main()
