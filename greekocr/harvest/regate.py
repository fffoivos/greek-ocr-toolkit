"""Read-only offline replay of stored geometry; separate, unlabelled sidecars.

No stack inference, acquisition, sampling, reader construction or reader calls.
The original fused crop is rejected rather than inheriting labels on its splits.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image

from .core import bbox, body_font_gate, crop_gate, page_gate, split_columns
from .pipeline import crop_features, digest, inspect_straight_crop, polygon_crop
from .readers import atomic, read_jsonl


def resolve_artifact(stored, bulk_root):
    """Explicit portable mapping: old docs/harvest/<suffix> → bulk_root/<suffix>."""
    root=Path(bulk_root).resolve()
    parts=Path(stored).parts
    starts=[i+2 for i in range(len(parts)-1) if parts[i:i+2]==('docs','harvest')]
    suffix=Path(*parts[starts[-1]:]) if starts else Path(stored)
    if suffix.is_absolute():
        try: suffix=suffix.relative_to(root)
        except ValueError: raise ValueError('artifact has no bulk-root mapping') from None
    path=(root/suffix).resolve()
    if not path.is_relative_to(root): raise ValueError('artifact escapes bulk root')
    if not path.is_file(): raise FileNotFoundError(path)
    return path


def run(records_path, page_receipts, bulk_root, out, *, progress=print):
    records_path=Path(records_path).resolve();page_receipts=Path(page_receipts).resolve()
    bulk_root=Path(bulk_root).resolve();out=Path(out).resolve()
    protected=Path(__file__).resolve().parents[2]/'docs/harvest/pilot_v1'
    if out.is_relative_to(bulk_root) or out.is_relative_to(protected) or out==records_path.parent:
        raise ValueError('replay output must be separate from protected bulk/pilot inputs')
    records_sha=digest(records_path);pages_sha=digest(page_receipts)
    code_sha={p.name:digest(p) for p in sorted(Path(__file__).parent.glob('*.py'))}
    original=read_jsonl(records_path)
    if len({r['id'] for r in original})!=len(original): raise ValueError('duplicate record IDs')
    receipts={p['id']:p for p in json.loads(page_receipts.read_text())}
    grouped=defaultdict(list)
    for r in original: grouped[r['page_id']].append(r)
    if set(grouped)!=set(receipts): raise ValueError('records and page receipts differ')
    out.mkdir(parents=True,exist_ok=True)
    sidecar=out/'post_fix1_gate.jsonl';temp=sidecar.with_suffix('.jsonl.tmp')
    page_results=[];before_flags=Counter();after_flags=Counter();sample_tiers=Counter()
    added=released=sample_rejected=after_rejected=straightened=base_rejected=0
    started=time.perf_counter()
    with temp.open('w') as stream:
        for index,(pid,rows) in enumerate(sorted(grouped.items()),1):
            page_path=resolve_artifact(rows[0]['provenance']['page_image'],bulk_root)
            page_sha=digest(page_path)
            if any(resolve_artifact(r['provenance']['page_image'],bulk_root)!=page_path for r in rows):
                raise ValueError('one page ID maps to multiple images')
            items=[dict(polygon=r['polygon']) for r in rows]
            with Image.open(page_path) as source:
                image=source.convert('L')
            bend=any(f['side']!=0 for f in receipts[pid]['bend_scout'])
            pg=page_gate(np.asarray(image),items,bend_fired=bend)
            split=split_columns(items,pg['column_bands'],np.asarray(image));boxes=[bbox(q['polygon']) for q in split]
            pieces=defaultdict(list)
            for q in split: pieces[q['harvest_parent_index']].append(q)
            replay=[]
            for i,r in enumerate(rows):
                gate=crop_gate(r['bbox'],boxes,pg,image.size,long_complete=True)
                gate['column_bands']=pg['column_bands']
                features=copy.deepcopy(r['features'])
                if gate['accepted']: features.update(crop_features(polygon_crop(image,r['polygon'])))
                replay.append(dict(gates=gate,features=features,tier='unread',label=None))
            body_font_gate(replay,pg)
            for i,(r,new) in enumerate(zip(rows,replay)):
                gate=new['gates'];geometry_accepted=gate['accepted']
                base_rejected+=not geometry_accepted
                inspected=None
                if geometry_accepted:
                    inspected=inspect_straight_crop(polygon_crop(image,r['polygon']))
                    gate['flags'].extend(inspected['flags'])
                    gate['neighbour_sliver']=inspected['neighbour_sliver']
                    straightened+=1
                gate['accepted']=not gate['flags']
                before=bool(r['gates']['accepted']);after=bool(gate['accepted'])
                added+=before and not after;released+=not before and after;after_rejected+=not after
                sampled=bool(r.get('sampled'))
                if sampled and not after: sample_rejected+=1;sample_tiers[r['tier']]+=1
                before_flags.update(r['gates']['flags']);after_flags.update(gate['flags'])
                planned=[]
                if len(pieces[i])>1:
                    for piece in pieces[i]:
                        box=bbox(piece['polygon'])
                        planned.append(dict(polygon=piece['polygon'],bbox=box,
                            gate=crop_gate(box,boxes,pg,image.size,piece,long_complete=True),label=None))
                obj=dict(id=r['id'],page_id=pid,sampled=sampled,
                    before_gate=copy.deepcopy(r['gates']),post_fix1_gate=gate,
                    geometry_accepted=geometry_accepted,
                    straighten=inspected['straighten'] if inspected else None,
                    split_candidates=planned)
                stream.write(json.dumps(obj,ensure_ascii=False,allow_nan=False)+'\n')
            page_results.append(dict(id=pid,page_image_sha256=page_sha,page_gate=pg,
                before_page_gate=receipts[pid]['page_gate'],records=len(rows)))
            if digest(page_path)!=page_sha: raise ValueError('page input changed during replay')
            if progress and (index%10==0 or index==len(grouped)):
                progress(f'OFFLINE_REGATE pages={index}/{len(grouped)} added={added} sampled_now_rejected={sample_rejected} elapsed_s={time.perf_counter()-started:.1f}',flush=True)
    if digest(records_path)!=records_sha or digest(page_receipts)!=pages_sha:
        raise ValueError('input records/receipts changed during replay')
    if code_sha!={p.name:digest(p) for p in sorted(Path(__file__).parent.glob('*.py'))}:
        raise ValueError('gate code changed during replay')
    temp.replace(sidecar)
    sampled_rows=[r for r in original if r.get('sampled')]
    summary=dict(schema='harvest-fix1-offline-regate-1',records=len(original),pages=len(grouped),
        sampled=len(sampled_rows),before_rejected=sum(not r['gates']['accepted'] for r in original),
        after_rejected=after_rejected,regated_rejects_added=added,released_rejects=released,
        sampled_now_rejected=sample_rejected,sampled_now_rejected_by_original_tier=dict(sample_tiers),
        before_flags=dict(sorted(before_flags.items())),after_flags=dict(sorted(after_flags.items())),
        geometry_rejected=base_rejected,straightened_candidates=straightened,
        scope='page and crop gates on all stored originals; body-font and straightener/ink gates on every geometry survivor; split candidates have no inherited labels',
        source_records_sha256=records_sha,source_page_receipts_sha256=pages_sha,
        source_page_receipts=str(page_receipts),bulk_root=str(bulk_root),source_records=str(records_path),
        original_sampled_tiers=dict(Counter(r['tier'] for r in sampled_rows)),
        source_code_sha256=code_sha,
        no_detector_run=True,google_calls=0,originals_unchanged=True,
        elapsed_s=time.perf_counter()-started,sidecar_sha256=digest(sidecar))
    atomic(out/'page_gates.json',page_results);atomic(out/'summary.json',summary)
    atomic(out/'sampled_post_fix1_gate.json',
        [json.loads(s) for s in sidecar.read_text().splitlines() if json.loads(s)['sampled']])
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--records',type=Path,required=True)
    p.add_argument('--page-gates',type=Path,required=True)
    p.add_argument('--bulk-root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(run(a.records,a.page_gates,a.bulk_root,a.out),ensure_ascii=False,indent=2))


if __name__=='__main__': main()
