"""Source-bound i2 artifact accounting. No detector or runtime imports."""
import collections
import hashlib
import html
import json
from pathlib import Path
import cv2
import numpy as np
from .r8_ink_acceptance import strip_times
from .r8_frame_parts import ROOT, BASE, MANIFEST
from ..shared.timing import dump


def run():
    rows=json.loads(MANIFEST.read_text())['pages'];oldroot=BASE.parent
    pilots=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/inputs.json')
    pilot_ids={r['page'] for r in json.loads(pilots.read_text())['pages']}
    acceptance=[]
    for row in rows:
        p=row['page'];a=json.loads((BASE/f'{p}.json').read_text());b=json.loads((ROOT/'runtime'/f'{p}.json').read_text())
        aa=json.loads((BASE/f'{p}.evidence.json').read_text());bb=json.loads((ROOT/'runtime'/f'{p}.evidence.json').read_text())
        # Timings are the only ignored fields. Include source votes, actual
        # calibration, frame/column cuts, accepted recoveries and exclusions.
        diff=[k for k in set(aa)|set(bb) if k not in ('timing','stages') and strip_times(aa.get(k))!=strip_times(bb.get(k)) and not k.endswith('_s') and k!='seconds']
        acceptance.append(dict(page=p,items_equal=a['items']==b['items'],items=len(b['items']),exclusions_equal=aa.get('removed')==bb.get('removed'),structural_differences=diff,pilot=p in pilot_ids))
    assert len(acceptance)==208 and all(r['items_equal'] and r['exclusions_equal'] and not r['structural_differences'] for r in acceptance)
    dump(ROOT/'acceptance.json',dict(pages=acceptance,items=sum(r['items'] for r in acceptance),pilots=23,native_loss='Zero added/lost/reassigned native crop pixels relative to 3b09d57 by exact final polygon/item equality. No newly changed exclusion. Historical missed words remain open; equality does not validate inherited ownership.'))
    for name,count in [('COMMENTS.json',104),('ROWS.json',256)]:
        records=json.loads((oldroot/name).read_text());assert len(records)==count
        for r in records:r['r8_02_i2']=dict(prior=str((oldroot/name).resolve()),items_equal=True,stage_evidence_equal=True,verdict='Inherited prior disposition; no new physical fix claimed',output='runtime/'+r['page']+'.json')
        dump(ROOT/name,records)
    timing=[]
    for repeat in (1,2):
        a=json.loads((ROOT/f'paired-base-{repeat}/receipt.json').read_text());b=json.loads((ROOT/f'paired-candidate-{repeat}/receipt.json').read_text())
        aa={z['page']:z for z in a['records']};pairs=[]
        for z in b['records']:
            old=aa[z['page']]
            pairs.append(dict(page=z['page'],before=old,after=z,delta_ms={k:1000*(z[k]-old[k]) for k in ('correction_s','decode_s','detector_s','total_s')},stage_delta_ms={k:1000*(z['stages'].get(k,0)-old['stages'].get(k,0)) for k in set(z['stages'])|set(old['stages'])}))
        timing.append(dict(repeat=repeat,order='base then candidate, forward' if repeat==1 else 'candidate then base, reverse',pairs=pairs,summary={k:dict(median_ms=float(np.median([z['delta_ms'][k] for z in pairs])),sum_ms=float(sum(z['delta_ms'][k] for z in pairs))) for k in ('correction_s','decode_s','detector_s','total_s')}))
    full=json.loads((ROOT/'runtime/receipt.json').read_text())
    dump(ROOT/'TIMING.json',dict(full=full,paired=timing,older_debt=dict(baseline='cb4d6b4',accepted_i1='3b09d57',page='s2-0ce9d1025b3f23c7119e-p00001',correction_increase_ms=[216.293,194.639],late_M35_increase_ms=[123.399,124.517],status='not erased by comparison to the slower accepted baseline')))
    ops=[]
    for p in sorted((ROOT/'operations').glob('*.timing.json')):
        a=json.loads((oldroot/'operations'/p.name).read_text());b=json.loads(p.read_text())
        ops.append(dict(page=b['page'],before=a['operations'],after=b['operations'],delta={k:{v:b['operations'][k][v]-a['operations'][k][v] for v in a['operations'][k]} for k in a['operations']}))
    dump(ROOT/'OPERATION_DELTA.json',ops)
    selected={r['page'] for r in json.loads((ROOT/'COMMENTS.json').read_text()) if r['id'] in {f'O{i:02}' for i in range(8,25)}}|pilot_ids
    selected|={r['page'] for r in json.loads((ROOT/'frame-parts/results.json').read_text())}
    selected|={r['page'] for r in json.loads((ROOT/'frame-controls/results.json').read_text())}
    gallery=ROOT/'gallery';gallery.mkdir(exist_ok=True);cards=[]
    for row in rows:
        p=row['page']
        if p not in selected:continue
        gray=cv2.imread(row['path'],0);ev=json.loads((ROOT/'runtime'/f'{p}.evidence.json').read_text());final=json.loads((ROOT/'runtime'/f'{p}.json').read_text())['items'];prior=json.loads((BASE/f'{p}.json').read_text())['items']
        panels=[]
        for name,items in [('Paddle',ev['original']),('accepted 3b09d57',prior),('i2 candidate',final)]:
            v=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
            for q in items:cv2.polylines(v,[np.rint(q['polygon']).astype(np.int32)],True,(0,140,0),2)
            scale=min(1,1500/v.shape[0]);v=cv2.resize(v,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA);cv2.putText(v,name,(8,22),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,0,255),1);panels.append(v)
        cv2.imwrite(str(gallery/f'{p}.jpg'),np.hstack(panels));cards.append(f'<figure><figcaption>{p}</figcaption><a href="gallery/{p}.jpg"><img loading="lazy" src="gallery/{p}.jpg"></a></figure>')
    links=[]
    for folder in ('frame-review','frame-parts','population','controls'):
        for p in sorted((ROOT/folder).glob('*.jpg')):
            rel=str(p.relative_to(ROOT));links.append(f'<li><a href="{rel}">{html.escape(rel)}</a></li>')
    (ROOT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>R8-02 i2 ink evidence</title><style>body{font:16px system-ui;max-width:1500px;margin:2em auto}img{max-width:100%}figure{margin:2em 0}li{margin:.3em}</style><h1>R8-02 i2 — partial</h1><p>Native anchor label preparation is shared; source and calibration decisions remain fresh. All208 final exports and stage decisions equal accepted3b09d57. M55 centre authority remains: the focused parts/whole-support trial explains14of57 thresholded crops and would revive43 approved removals. Trial outputs are rejected.</p><p>Review panels: Paddle, accepted3b09d57, candidate. Only kept polygons are drawn in final panels. Separate diagnostics show excluded ink. Frame raw left; proposed correspondence blue, unexplained observed support red, current polygon green. No blankness is inferred below the thresholds. Population raw left; upper-half admitted components green, lower-half purple, rejected body filter orange. These colors do not certify source or character identity.</p><p><a href="FRAME_PRESERVATION.json">57-removal ledger</a> · <a href="SUPPORT_HANDOFF.json">03 support contract</a> · <a href="TIMING.json">timing</a> · <a href="ITERATION_HANDOFF.json">handoff</a></p><h2>Native evidence</h2><ul>'+''.join(links)+'</ul><h2>Final crops / geometry pilot controls</h2>'+''.join(cards))
    print('208 exact;57 frame ledger;104 comments;256 marks;',len(selected),'gallery pages')


if __name__=='__main__':run()
