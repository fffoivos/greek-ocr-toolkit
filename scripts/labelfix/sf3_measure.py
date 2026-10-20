"""SF3 saved-evidence replay. Held-out on Clariden; M2 DEV allowlist on CPU.

Run in separate processes with the baseline or candidate on PYTHONPATH.
Never invokes a detector, aligner, reader, model forward pass or mock builder.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import time
import unicodedata as ud

from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.text import clusters, nfd
from scripts.labelfix.clariden.r1_common import rows, sha256, write_json, write_rows


def char_record(text):
    return [dict(character=c,codepoint=f'U+{ord(c):04X}',name=ud.name(c,'UNNAMED')) for c in text]


def guard_audit(lid, original, decision):
    proposal=decision['text'];reasons=gate.edit_guard(original,proposal)
    if not reasons:return None
    raw_a=[c for c in clusters(original) if c.base.isalpha()]
    raw_b=[c for c in clusters(proposal) if c.base.isalpha()]
    a=[c for c in clusters(nfd(original)) if c.base.isalpha() or ud.combining(c.base)]
    b=[c for c in clusters(nfd(proposal)) if c.base.isalpha() or ud.combining(c.base)]
    defects=[]
    for reason in reasons:
        if reason.startswith(('edit_guard:unsupported_character:','edit_guard:unsupported_raw_character:')):
            aa,bb=(raw_a,raw_b) if ':unsupported_raw_' in reason else (a,b)
            i=int(reason.rsplit(':',1)[1]);x=aa[i].base+aa[i].marks;y=bb[i].base+bb[i].marks
            defects.append(dict(reason=reason,index=i,original=x,proposal=y,
                original_characters=char_record(x),proposal_characters=char_record(y)))
    pa,pb=gate._punctuation(original),gate._punctuation(proposal)
    diffs=[]
    if 'edit_guard:punctuation_mismatch' in reasons:
        for tag,i,j,k,l in SequenceMatcher(None,pa,pb,autojunk=False).get_opcodes():
            if tag!='equal':diffs.append(dict(operation=tag,original=pa[i:j],proposal=pb[k:l],
                original_characters=char_record(pa[i:j]),proposal_characters=char_record(pb[k:l])))
    return dict(id=lid,original=original,proposal=proposal,reasons=reasons,
                unsupported=defects,punctuation=[pa,pb],punctuation_differences=diffs)


def reason_table(decisions):
    out={}
    for mode in gate.MODES:
        counts=Counter();lines=Counter();alone=Counter();groups=Counter()
        for r in decisions:
            reasons=[z for s in r['decisions'][mode]['hold_slots'] for z in s['reasons']]
            counts.update(reasons);lines.update(set(reasons))
            def group(z):
                if z.startswith('K1:'):return 'K1'
                if z.startswith('edit_guard:'):return 'edit_guard:'+z.split(':')[1]
                return z
            families={group(z) for z in reasons}
            if len(families)==1:alone.update(families)
            for s in r['decisions'][mode]['hold_slots']:groups.update({group(z) for z in s['reasons']})
        out[mode]=dict(reason_incidences=dict(counts),lines_per_reason=dict(lines),
                       unique_slots_per_family=dict(groups),lines_held_only_for_family=dict(alone))
    return out


def heldout(a):
    from scripts.labelfix.clariden.l1e_measure import saved_runtime, score_line, recover_observation
    from scripts.labelfix.clariden.l1e_run import decision_record
    from scripts.labelfix.clariden.r1_score import metadata, prediction_map
    started=time.monotonic();out=a.out;out.mkdir(parents=True,exist_ok=False)
    reference=json.loads((a.deploy/'heldout_final/measurement_receipt.json').read_text())
    # Recheck the exact L1E evidence, extraction, predictions and checkpoints.
    for name,digest in reference['inputs'].items():
        path=Path(name) if Path(name).is_absolute() else a.deploy/name
        if sha256(path)!=digest:raise ValueError('L1E input changed: '+str(path))
    ex=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/artifacts/labelfix_r1/heldout_font')
    runs=ex.parents[2]/'output_3678928'
    meta=metadata(ex);pred={}
    for arm in ('A','B','E'):
        pred[arm]=defaultdict(list)
        for (lid,_),p in prediction_map(runs/arm/'heldout_predictions.jsonl',meta,
                extraction=ex,checkpoint=runs/arm/'best.pt').items():pred[arm][lid].append(p)
    recovered=recover_observation(meta,Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/collection_v2/crops'))
    write_json(out/'observation_recovery.json',recovered)
    google={r['line_id']:r['gt'] for r in rows(a.deploy/'inputs/google_predictions.jsonl') if r['line_id'] in meta}
    frozen={r['line_id']:r for r in rows(a.deploy/'inputs/S4_lines.jsonl.gz') if not r['dev']}
    totals={m:Counter() for m in gate.MODES};decisions=[];events=[];audit=[];observations=[]
    seen=set()
    for line in rows(a.deploy/'inputs/S6_lines.jsonl.gz'):
        if line['dev']:continue
        lid=line['line_id'];seen.add(lid)
        rt=saved_runtime(line,meta[lid],{arm:pred[arm][lid] for arm in pred})
        stats,ev=score_line(frozen[lid],google[lid],rt)
        for m in gate.MODES:totals[m].update(stats[m])
        d=decision_record(rt);decisions.append(dict(id=lid,decisions=d))
        events.append(dict(id=lid,counts=stats,events=ev))
        guards={m:guard_audit(lid,rt['recogniser_text'],d[m]) for m in gate.MODES}
        if any(guards.values()):audit.append(dict(id=lid,modes=guards))
        relevant=[]
        for s in rt['detector']['slots']:
            e=s.get('evidence',{})
            if any(e.get('clipped_'+z) for z in ('top','bottom')) or s.get('constraint_flags'):
                relevant.append(dict(start=s['start'],base=s['base'],parts=s['parts'],
                    bbox=s.get('bbox'),evidence=e,constraint_flags=s.get('constraint_flags',[]),
                    predictions={arm:[p for p in rt['r1_predictions'] if p['start']==s['start']]
                        if arm=='A' else [p for p in rt['peer_predictions'][arm] if p['start']==s['start']] for arm in ('A','B','E')}))
        observations.append(dict(id=lid,flags=rt['detector'].get('constraint_flags',[]),slots=relevant))
    if seen!=set(meta) or len(seen)!=666:raise ValueError('held-out identity changed')
    for m in gate.MODES:
        if totals[m]['google_errors']!=80:raise ValueError('80-error instrument changed')
    if a.phase=='before':
        old=list(rows(a.deploy/'heldout_final/decisions.jsonl.gz'))
        if decisions!=old:raise ValueError('baseline does not reproduce L1E decisions')
        if {m:dict(totals[m]) for m in gate.MODES}!=reference['modes']:raise ValueError('L1E table changed')
    write_rows(out/'decisions.jsonl.gz',decisions);write_rows(out/'events.jsonl',events)
    write_rows(out/'guard_audit.jsonl',audit);write_rows(out/'clipping_evidence.jsonl.gz',observations)
    write_json(out/'reasons.json',reason_table(decisions))
    receipt=dict(schema='sf3-heldout-v1',phase=a.phase,complete=True,lines=666,google_errors=80,
        measurement_script_sha256=sha256(Path(__file__)),
        modes={m:dict(c) for m,c in totals.items()},policy=gate.policy_binding(),
        inputs=reference['inputs'],baseline_measurement_sha256=sha256(a.deploy/'heldout_final/measurement_receipt.json'),
        instrument=reference['instrument'],detector_runs=0,r1_runs=0,ctc_runs=0,
        elapsed_seconds=time.monotonic()-started,outputs={p.name:sha256(p) for p in out.iterdir()})
    write_json(out/'measurement_receipt.json',receipt)
    print(json.dumps(receipt['modes'],indent=2))


def dev_inventory(manifest):
    """Allowlist only; never load locked truth, predictions or cached decisions."""
    inv=[];seen=set()
    for r in rows(manifest):
        if r.get('selection_role')!='development_only':raise ValueError('non-DEV manifest record')
        cid=r['card_id']
        if cid in seen:raise ValueError('duplicate DEV card')
        seen.add(cid)
        inv.append(dict(id=cid,source=r['source'],google_label=r['google'],
            verdict=r['existing_blind_verdict'],line_id=r['line_id']))
    return inv


def dev_runtime(cache, allowed):
    # Cache format starts with id. Filter before JSON decoding any record.
    runs=[]
    with open(cache) as f:
        for line in f:
            match=re.match(r'\{\s*"id"\s*:\s*("(?:[^"\\]|\\.)*")',line)
            if not match:raise ValueError('cache id is not the first field')
            if json.loads(match[1]) in allowed:runs.append(json.loads(line))
    if len(runs)!=len(allowed) or {r['id'] for r in runs}!=allowed:raise ValueError('DEV runtime identity mismatch')
    return runs


def m2(a):
    from scripts.labelfix import m2_score as score
    # Missing B/E is measured as missing evidence, never filled with A.
    score.MODES=gate.MODES
    started=time.monotonic();out=a.out;out.mkdir(parents=True,exist_ok=False)
    inv=dev_inventory(a.dev_manifest)
    if len(inv)!=273:raise ValueError('expected frozen 273-card DEV pool')
    allowed={r['id'] for r in inv};runs=dev_runtime(a.cache,allowed)
    for r in runs:
        if r['status']!='ok':raise ValueError('DEV line missing saved evidence')
        r['modes']={m:gate.compose_runtime(r,m) for m in score.MODES}
    runtime={r['id']:r for r in runs};by={r['id']:r for r in inv}
    ledger=score.pair_ledger(inv)
    pairs=[score.score_case(c,by[c['id']],runtime[c['id']]) for c in ledger if c['included']]
    lines=[]
    for r in inv:
        run=runtime[r['id']];changes,cov=score.changes_for(r,run)
        lines.append(dict(**r,**{k:v for k,v in run.items() if k!='id'},changes=changes,
            reference_change_alignment_coverage=cov))
    metrics=score.summarize(inv,runtime,pairs,lines)
    write_json(out/'metrics.json',metrics);write_rows(out/'pairs.jsonl',pairs)
    # No need to duplicate pixels or historical/modes in this audit.
    write_rows(out/'lines.jsonl.gz',[dict(id=l['id'],source=l['source'],changes=l['changes'],
        modes={m:dict(text=l['modes'][m]['text'],hold_slots=l['modes'][m]['hold_slots']) for m in score.MODES}) for l in lines])
    write_json(out/'receipt.json',dict(schema='sf3-m2-dev-v1',phase=a.phase,complete=True,lines=len(inv),
        measurement_script_sha256=sha256(Path(__file__)),
        allowed_card_ids=sorted(allowed),policy=gate.policy_binding(),locked_records_decoded_or_composed=0,
        inputs={str(p):sha256(p) for p in (a.dev_manifest,a.cache)},detector_runs=0,r1_runs=0,ctc_runs=0,
        elapsed_seconds=time.monotonic()-started,outputs={p.name:sha256(p) for p in out.iterdir()}))
    print(json.dumps(metrics['POOLED']['modes'],indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('instrument',choices=['heldout','m2']);p.add_argument('--phase',choices=['before','after'],required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--deploy',type=Path)
    p.add_argument('--dev-manifest',type=Path);p.add_argument('--cache',type=Path)
    a=p.parse_args()
    (heldout if a.instrument=='heldout' else m2)(a)


if __name__=='__main__':main()
