#!/usr/bin/env python3
"""One-off T7 inventory, measurements and explicitly enabled, resumable Luna runs.

Without --online it never invokes Codex. Never writes .git. Shared ledger limits
ALL judge invocations (including failures) to 500, with at most 200 text calls.
"""
from __future__ import annotations
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from greekocr.verify import readability_profile, render_overlay, text_checks
from greekocr.verify.images import feature_vector
from greekocr.verify.calibration import calibrate, fit_distribution
from greekocr.verify.cli import crop_records, reading_records, write_jsonl
from greekocr.verify.judges import CallBudget, vlm_annotate, judge_texts, _load_cache, _cache_key, READABILITY_SCHEMA, TEXT_SCHEMA


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--online', action='store_true', help='explicitly invoke gpt-6-luna')
    parser.add_argument('--budget', type=int, default=500)
    args = parser.parse_args()
    out=ROOT/'docs/verify'
    out.mkdir(parents=True,exist_ok=True)
    crops=[]
    manifest=[]
    for name in ('o4d_lines','o4d_sample400'):
        directory=ROOT/'tests/fixtures'/name
        index=directory/'index.json'
        manifest.append({'sample_set':name,'index_sha256':hashlib.sha256(index.read_bytes()).hexdigest()})
        for row in crop_records(directory):
            row['crop']=str(Path(row['crop']).relative_to(ROOT))
            crops.append(row | {'sample_set':name})
    readings=reading_records(ROOT/'tests/fixtures/o4d_sample400/index.json')
    elapsed=[]
    wall_elapsed=[]
    checks=[]
    # Exclude decode/I/O from the CPU measurement, but record end-to-end separately.
    from PIL import Image
    total_started=time.perf_counter()
    for row in crops:
        with Image.open(ROOT/row['crop']) as im:
            im.load()
            started=time.process_time()
            wall_started=time.perf_counter()
            profile=readability_profile(im)
            elapsed.append((time.process_time()-started)*1000)
            wall_elapsed.append((time.perf_counter()-wall_started)*1000)
        checks.append(row | {'crop_sha256':hashlib.sha256((ROOT/row['crop']).read_bytes()).hexdigest(),
                             'measurement_cpu_ms':elapsed[-1], 'measurement_wall_ms':wall_elapsed[-1],
                             'checks':profile.summaries.to_dict()})
    distribution=fit_distribution(checks,ROOT/'greekocr/verify/sample_distribution.json')
    import numpy as np
    # Publish functions and summaries against the newly fitted identical reference.
    # This final pass also measures the shipped calculation rather than the bootstrap.
    elapsed.clear()
    wall_elapsed.clear()
    # Stream large maps/bins rather than retaining thousands of nested lists. That
    # also avoids whole-batch garbage collection inside the per-crop CPU timer.
    with (out/'image_checks_sample.jsonl').open('w',encoding='utf-8') as stream:
        for row in checks:
            with Image.open(ROOT/row['crop']) as im:
                im.load()
                started=time.process_time()
                wall_started=time.perf_counter()
                profile=readability_profile(im)
                elapsed.append((time.process_time()-started)*1000)
                wall_elapsed.append((time.perf_counter()-wall_started)*1000)
            row.update(checks=profile.summaries.to_dict(),
                       measurement_cpu_ms=elapsed[-1],measurement_wall_ms=wall_elapsed[-1],
                       distribution_digest=distribution['sample_digest'])
            published=row | {'profile_bins':{k:v.tolist() for k,v in profile.bins.items()},
                             'quality_map':profile.quality_map.tolist(),'segments':list(profile.segments)}
            stream.write(json.dumps(published,ensure_ascii=False,allow_nan=False)+'\n')
    end_to_end=time.perf_counter()-total_started
    text_rows=[r | {'checks':text_checks(r['text']).to_dict()} for r in readings]
    write_jsonl(out/'text_checks_sample.jsonl',text_rows)
    regression=ROOT/'tests/fixtures/o4d_lines/regressions/s2-60f24a3d8a2d714767f2-p00003-l00024_old.png'
    profile=readability_profile(regression)
    (out/'regression_overlay.png').write_bytes(render_overlay(regression,profile))
    (out/'regression_profile.json').write_text(json.dumps(profile.to_dict(),ensure_ascii=False)+'\n')
    failures=[]
    budget=CallBudget(out/'calls.jsonl',args.budget)
    if args.online:
        for kind in ('image','text'):
            try:
                if kind=='image':
                    vlm_annotate([ROOT/r['crop'] for r in crops],cache=out/'image_cache.jsonl',budget=budget,receipts_dir=out/'receipts')
                else:
                    judge_texts([r['text'] for r in readings],cache=out/'text_cache.jsonl',budget=budget,receipts_dir=out/'receipts')
            except (RuntimeError,ValueError,OSError) as error:
                failures.append({'kind':kind,'error':str(error)})
                print(f'{kind} judge blocked: {error}',file=sys.stderr)
    image_cache=_load_cache(out/'image_cache.jsonl')
    text_cache=_load_cache(out/'text_cache.jsonl')
    vlm=[]
    for row in checks:
        key=_cache_key('image',(ROOT/row['crop']).read_bytes(),'gpt-6-luna',READABILITY_SCHEMA)
        found=image_cache.get(key)
        vlm.append({k:row[k] for k in ('crop','crop_sha256','line_id','sample_set')} |
                   ({'judgement':found['judgement'],'receipt':found['receipt'],'status':'ok'} if found else
                    {'judgement':None,'receipt':None,'status':'unavailable',
                     'reason':'Codex initialization blocked; see RUN_STATUS.json and receipts' if budget.count else 'online judge not invoked'}))
    judged_text=[]
    for row in readings:
        key=_cache_key('text',row['text'].encode(),'gpt-6-luna',TEXT_SCHEMA)
        found=text_cache.get(key)
        judged_text.append(row | ({'judgement':found['judgement'],'receipt':found['receipt'],'status':'ok'} if found else
                                {'judgement':None,'receipt':None,'status':'unavailable',
                                 'reason':'Codex initialization blocked; see RUN_STATUS.json and receipts' if budget.count else 'online judge not invoked'}))
    write_jsonl(out/'vlm_readability_sample.jsonl',vlm)
    write_jsonl(out/'llm_text_judgements.jsonl',judged_text)
    owner=json.loads((ROOT/'tests/fixtures/o4d_lines/index.json').read_text()).get('owner_notes',{})
    calibration=calibrate(checks,vlm,owner_notes=owner,output=out/'CALIBRATION.md')
    reservations=[json.loads(line) for line in (out/'calls.jsonl').read_text().splitlines()] if budget.count else []
    archived_failures=[]
    for reservation in reservations:
        receipt_path=out/'receipts'/(reservation['call_id']+'.receipt.json')
        if receipt_path.exists():
            receipt=json.loads(receipt_path.read_text())
            if receipt.get('status')=='failed':
                archived_failures.append({'call_id':reservation['call_id'],'kind':reservation['kind'],
                                          'error':receipt.get('error'),'receipt':str(receipt_path.relative_to(ROOT))})
    status={'schema':'greekocr.verify.run.v1','status':'complete' if all(r['status']=='ok' for r in vlm+judged_text) else 'judges_blocked' if budget.count else 'offline_pending',
            'manifest':manifest,'images':len(crops),'readings':len(readings),'owner_notes':len(owner),
            'successful_image_labels':sum(r['status']=='ok' for r in vlm),
            'successful_text_labels':sum(r['status']=='ok' for r in judged_text),
            'total_judge_invocations':budget.count,'image_invocations':sum(r['kind']=='image' for r in reservations),
            'text_invocations':sum(r['kind']=='text' for r in reservations), 'call_limit':args.budget,
            'failures':failures,'archived_failures':archived_failures,
            'cpu_ms':{'mean':float(np.mean(elapsed)),'p50':float(np.median(elapsed)),
                      'p95':float(np.percentile(elapsed,95)),'max':float(max(elapsed)),
                      'over_20ms':sum(v>=20 for v in elapsed),'end_to_end_s':end_to_end,
                      'definition':'time.process_time: loaded Pillow crop -> full profile and scalar summaries; sample run includes warm-up'},
            'wall_ms':{'mean':float(np.mean(wall_elapsed)),'p95':float(np.percentile(wall_elapsed,95)),
                       'max':float(max(wall_elapsed))},
            'empirical_calibration_available':calibration['labelled_images']>0,
            'network':'only codex exec judges; no PDF text layer transmitted'}
    (out/'RUN_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status,indent=2))
    return 0 if status['status']=='complete' else 2


if __name__=='__main__':
    raise SystemExit(main())
