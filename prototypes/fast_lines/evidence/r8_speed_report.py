"""Aggregate completed R8-04-i1 receipts; this is offline evidence only."""
import json
from collections import Counter
from pathlib import Path
import numpy as np
from r8_speed_acceptance import OUT,BASE,dump,sha


def stats(values):
    a=np.asarray(values,float)
    return dict(n=len(a),median_ms=float(np.median(a)),p95_ms=float(np.percentile(a,95)),max_ms=float(a.max()),sum_ms=float(a.sum()))


def run():
    full=json.loads((OUT/'runtime/receipt.json').read_text())
    timing=[]
    for repeat in (1,2):
        pairs=[]
        for folder,only in [(OUT,None),(OUT/'extra-controls','s2-0ce9d1025b3f23c7119e-p00001')]:
            a=json.loads((folder/f'paired-base-{repeat}/receipt.json').read_text())
            b=json.loads((folder/f'paired-candidate-{repeat}/receipt.json').read_text())
            aa={r['page']:r for r in a['records']}
            for r in b['records']:
                if only and r['page']!=only:continue
                old=aa[r['page']]
                pairs.append(dict(page=r['page'],baseline=old,candidate=r,receipt_root=str(folder),
                    delta_ms={k:1000*(r[k]-old[k]) for k in ('correction_s','detector_s','decode_s','total_s')},
                    stage_delta_ms={k:1000*(r['stages'].get(k,0)-old['stages'].get(k,0)) for k in set(r['stages'])|set(old['stages'])}))
        assert len(pairs)==84 and len({r['page'] for r in pairs})==84
        assert set(full['over1s'])<={r['page'] for r in pairs}
        stage_keys=sorted({k for r in pairs for k in r['stage_delta_ms']})
        timing.append(dict(repeat=repeat,order='baseline then candidate, forward' if repeat==1 else 'candidate then baseline, reversed',pairs=pairs,
            summary={k:stats([r['delta_ms'][k] for r in pairs]) for k in ('correction_s','detector_s','decode_s','total_s')},
            stages={k:dict(all=stats([r['stage_delta_ms'].get(k,0) for r in pairs]),active=stats([r['stage_delta_ms'].get(k,0) for r in pairs if k in r['baseline']['stages'] or k in r['candidate']['stages']])) for k in stage_keys}))
    work=[]
    for stem in ('work','work-quiet'):
        for p in sorted((OUT/f'{stem}-base').glob('*.json')):
            if p.name=='receipt.json':continue
            a=json.loads(p.read_text());b=json.loads((OUT/f'{stem}-candidate'/p.name).read_text())
            assert a['inferences']==b['inferences']
            work.append(dict(page=a['page'],before=a['counts'],after=b['counts'],
                delta={k:b['counts'].get(k,0)-a['counts'].get(k,0) for k in set(a['counts'])|set(b['counts'])},
                inference_calls=len(a['inferences']),duplicate_inference_requests=a['duplicate_inference_requests'],inference_inputs_and_maps_exact=True,
                baseline_receipt=str(p),candidate_receipt=str(OUT/f'{stem}-candidate'/p.name)))
    before=Counter();after=Counter()
    for r in work:
        before.update({k:v for k,v in r['before'].items() if not k.startswith('ink.max_')})
        after.update({k:v for k,v in r['after'].items() if not k.startswith('ink.max_')})
    dump(OUT/'OPERATION_DELTA.json',dict(scope='Four supplied profiled pages plus f9ec p10 and 77d1 p1; not extrapolated to208. Instrumentation is outside all timing.',pages=work,
        totals_before=dict(before),totals_after=dict(after),totals_delta={k:after[k]-before[k] for k in set(before)|set(after)},
        memory='Owned tile/vector copies are charged. max_single_roi_retained_tile_bytes is a single-ROI bound, not process peak. Each normalization is3872 bytes; total constructed normalization bytes bound additional resident tiles within one page. No cross-page persistence.',
        initial_cli_correction='The first baseline work command included two unmatched shorthand quiet IDs and ran only the four exact IDs. work-quiet-* uses exact manifest IDs; the tool now rejects unmatched inputs.'))
    allwork=[];abefore=Counter();aafter=Counter()
    for p in sorted((OUT/'work208-base').glob('*.json')):
        if p.name=='receipt.json':continue
        a=json.loads(p.read_text());b=json.loads((OUT/'work208-candidate'/p.name).read_text())
        assert a['inferences']==b['inferences'] and a['export_exact'] and b['export_exact']
        abefore.update({k:v for k,v in a['counts'].items() if not k.startswith('ink.max_')})
        aafter.update({k:v for k,v in b['counts'].items() if not k.startswith('ink.max_')})
        allwork.append(dict(page=a['page'],before=a['counts'],after=b['counts'],
            delta={k:b['counts'].get(k,0)-a['counts'].get(k,0) for k in set(a['counts'])|set(b['counts'])},
            inference_calls=len(a['inferences']),duplicate_inference_requests=a['duplicate_inference_requests'],inference_inputs_and_maps_exact=True,
            baseline_receipt=str(p),candidate_receipt=str(OUT/'work208-candidate'/p.name)))
    assert len(allwork)==208
    dump(OUT/'OPERATION_DELTA_208.json',dict(scope='Full pinned 208, identical instrumentation in both source trees. Clocks are not performance; no saved outputs feed the detector.',pages=allwork,
        totals_before=dict(abefore),totals_after=dict(aafter),totals_delta={k:aafter[k]-abefore[k] for k in set(abefore)|set(aafter)}))
    stages={k:stats([r['stages'].get(k,0)*1000 for r in full['records']]) for k in sorted({k for r in full['records'] for k in r['stages']})}
    slow=[]
    for r in sorted(full['records'],key=lambda x:x['correction_s'],reverse=True):
        if r['correction_s']<=1:continue
        slow.append(dict(page=r['page'],correction_ms=r['correction_s']*1000,stages_ms={k:v*1000 for k,v in r['stages'].items()}))
    dump(OUT/'TIMING.json',dict(full_receipt='runtime/receipt.json',source_sha256=full['source_sha256'],input_sha256=full['input_sha256'],model_sha256=full['model_sha256'],
        summary=full['summary'],full_stage_distributions=stages,slow_pages=slow,paired=timing,
        methodology='84 unique controls: initial83 plus accidentally omitted0ce9 measured in a separate four-profile-page two-order repeat. Both raw sets retained. Differences pair the same page/source/settings; no detector-drift subtraction. All field/native/regional/copy preparation charged; export/offline instrumentation excluded. First-page execution retained, startup separate.',
        startup_ms={str(p.relative_to(OUT)):json.loads(p.read_text())['records'][0]['startup_s']*1000 for p in OUT.glob('**/paired-*/receipt.json')},
        full_startup_ms=full['records'][0]['startup_s']*1000,
        full_first_page=full['records'][0],
        full_after_first_page={k:stats([r[k]*1000 for r in full['records'][1:]]) for k in ('correction_s','detector_s','decode_s','total_s')},
        opencv_threads=full['opencv_threads'],onnx=full['onnx'],G4='PARTIAL: one fresh208 pass,22 pages over1s; no qualified clean cohort yet; no two-pass all-page gate claim'))
    lines=['# R8-04-i1 timing','', 'All clocks include decode, unchanged Paddle and every correction dependency. Correction is the extra cost against the same Paddle-only decode/inference setup. Offline work instrumentation and exports are excluded. OpenCV actually reports 10 threads; ONNX CPU is sequential, intra/inter 1. Startup is separate in TIMING.json. First-page effects remain in both sources; there is no prerecorded output reuse.','',
        '| Full 208, milliseconds | Median | p95 | Maximum |','|---|---:|---:|---:|']
    for key in ('correction_s','detector_s','decode_s','total_s'):
        q=full['summary']['all'][key];lines.append(f"| {key} | {q['median_ms']:.3f} | {q['p95_ms']:.3f} | {q['max_ms']:.3f} |")
    lines+=['','22 pages remain above 1000 ms. One full pass is supplied; G4 is not passed. The 40 agreement pages are not qualified clean pages. Their correction median/p95/max is %.3f/%.3f/%.3f ms.'%tuple(full['summary']['agreement']['correction_s'][k] for k in ('median_ms','p95_ms','max_ms')),'',
        '## Paired controls','', '83 controls were paired in forward then reversed order. 0ce9 was omitted from the union by mistake; it was then measured with the four profile controls in both source orders. The 84-page summary includes its separate pair. All 22 slow pages are represented; raw supplemental repeats are retained.','',
        '| Pair | Correction median / total delta ms | Field proposal total delta ms | Detector total delta ms | Decode total delta ms |','|---|---:|---:|---:|---:|']
    for r in timing:
        q=r['summary'];lines.append(f"| {r['repeat']} ({r['order']}) | {q['correction_s']['median_ms']:.3f} / {q['correction_s']['sum_ms']:.3f} | {r['stages']['field_proposal_s']['all']['sum_ms']:.3f} | {q['detector_s']['sum_ms']:.3f} | {q['decode_s']['sum_ms']:.3f} |")
    lines+=['','The consistent field-stage decrease accompanies removed work. Small all-page median shifts and mixed ink timings do not establish a general speedup. Detector/decode drift is reported, never subtracted. Stage clocks overlap: do not sum nested type/field clocks. 0ce9 remains about 200 ms slower than cb4d6b4 historically; this comparison does not erase that debt.','', '## All slow pages','', '| Page | Correction ms | Field proposal ms | Type ms | Row ownership ms | Ink ms |','|---|---:|---:|---:|---:|---:|']
    for r in slow:
        s=r['stages_ms'];lines.append(f"| {r['page']} | {r['correction_ms']:.3f} | {s.get('field_proposal_s',0):.3f} | {s.get('type_s',0):.3f} | {s.get('row_ownership_s',0):.3f} | {s.get('ink_s',0):.3f} |")
    (OUT/'TIMING.md').write_text('\n'.join(lines)+'\n')
    print('timing84controls;work',len(work),'pages;field deltas',[r['stages']['field_proposal_s']['all']['sum_ms'] for r in timing])


if __name__=='__main__':run()
