"""Frozen, development-only orientation evaluation; never fits decision margins.

Report accepted/correct/error/coverage separately. Oracle crops and blind
regions are deliberately separate. All timings exclude disk IO and rendering.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter

import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from greekocr.glyphs.orientation import measure_orientation, discover_directions, QuarterTurn
from greekocr.glyphs.orientation_regions import page_regions

OUT=ROOT/'.astra/out/orientation_eval'


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n')


def decision_row(decision,truth):
    accepted=decision.orientation_cw is not None
    return dict(truth_cw=truth,scored=truth is not None,accepted=accepted,correct=accepted and decision.orientation_cw==truth,
                error=truth is not None and accepted and decision.orientation_cw!=truth,
                axis_correct=truth is not None and decision.axis==('vertical' if truth%180 else 'horizontal'),**decision.to_record())


def counts(rows):
    rows=[r for r in rows if r.get('scored',True)]
    n=len(rows);accepted=sum(r['accepted'] for r in rows);correct=sum(r['correct'] for r in rows)
    return dict(total=n,accepted=accepted,correct=correct,errors=accepted-correct,
                accuracy=correct/accepted if accepted else None,coverage=accepted/n if n else None,
                axis_correct=sum(r.get('axis_correct',False) for r in rows))


def time_summary(values):
    return dict(mean=float(np.mean(values)),median=float(np.median(values)),p95=float(np.percentile(values,95)),
                maximum=max(values),total=sum(values)) if values else {}


def overlap(a,b):
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    return inter/max(1,(a[2]-a[0])*(a[3]-a[1]))


def draw(image,regions,path,roi=None):
    view=image.convert('RGB');view.thumbnail((1100,1300));sx=view.width/image.width;sy=view.height/image.height
    d=ImageDraw.Draw(view);colors={0:'green',90:'blue',180:'purple',270:'orange',None:'gray'}
    for r in regions:
        box=r['box'];o=r['decision'];b=[box[0]*sx,box[1]*sy,box[2]*sx,box[3]*sy]
        d.rectangle(b,outline=colors[o.orientation_cw],width=2)
        d.text((b[0]+2,b[1]+2),f"{r['id']} {o.orientation_cw if o.orientation_cw is not None else '?'}",fill=colors[o.orientation_cw])
    if roi:d.rectangle([roi[0]*sx,roi[1]*sy,roi[2]*sx,roi[3]*sy],outline='red',width=2)
    view.save(path,quality=90)


def evaluate(out, *, use_osd=False, include_research=True):
    manifest=json.loads((out/'manifest.json').read_text());cases=manifest['cases'].copy()
    if include_research:
        research=ROOT/'.astra/orientation_research'
        for c in json.loads((research/'testset/manifest.json').read_text())['cases']:
            row={**c,'id':'research__'+c['id'],'path':str((research/c['path']).relative_to(ROOT)),'research':True}
            cases.append(row)
    results=[]
    save(out/'run-source-hashes.json', {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
        [ROOT/'greekocr/glyphs/orientation.py', ROOT/'greekocr/glyphs/orientation_guides.py', ROOT/'greekocr/glyphs/orientation_regions.py', Path(__file__)]})
    for i,c in enumerate(cases):
        path=ROOT/c['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==c['sha256']
        image=Image.open(path).convert('L')
        start=perf_counter();unit=c.get('unit','page')
        whole=measure_orientation(image,unit=unit,use_osd=use_osd)
        measure_s=perf_counter()-start
        truth=c['truth_cw'];whole_row=decision_row(whole,truth)
        row=dict(id=c['id'],kind=c['kind'],research=c.get('research',False),applied_cw=c.get('applied_cw',truth),
                 source=c.get('source'),mixed=c.get('mixed',False),whole=whole_row,measure_seconds=measure_s)
        # Standalone word crops remain unknown by policy; no forbidden word vote.
        if c['kind'] in ('whole','composite','skew'):
            start=perf_counter()
            dominant,regions,proposals=page_regions(image,dominant=whole,use_osd=use_osd)
            row['region_seconds']=measure_s+perf_counter()-start
            scored=[]
            for r in regions:
                rt=truth
                if c.get('roi') and r['id']!='page' and overlap(r['box'],c['roi'])>.5:
                    rt=c['roi_truth_cw']
                if c.get('source')=='s2-6419488b7f8e69fd20da-p00001' and r['id']!='page':
                    # Only independently labelled ROIs have local polarity truth.
                    # Do not label an actual 180-degree header as dominant 270.
                    rt=None
                    frame=QuarterTurn(*image.size,c.get('applied_cw',0))
                    box_points=frame.rectangle(r['box'],inverse=False)
                    source_box=[*box_points.min(0),*box_points.max(0)]
                    for box,angle in [([180,487,320,1907],270),([1270,3922,1530,4037],180),
                                      ([1610,187,1810,297],0),([1710,390,2390,1180],270)]:
                        if overlap(source_box,box)>.5:rt=(angle+c.get('applied_cw',0))%360
                scored.append(dict(id=r['id'],box=r['box'],components=r.get('components',0),**decision_row(r['decision'],rt)))
            row['regions']=scored
            if c.get('roi'):
                roi=c['roi'];correct_axis='vertical' if c['roi_truth_cw']%180 else 'horizontal'
                cover=np.zeros((image.height,image.width),bool)
                hits=[]
                all_hits=[r for r in regions[1:] if overlap(r['box'],roi)>0]
                for r in regions[1:]:
                    if r['axis']!=correct_axis or overlap(r['box'],roi)<=0:continue
                    hits.append(r)
                    for a,t,b,bot in r.get('chain_boxes',[r['box']]):
                        cover[max(0,int(t)):min(image.height,int(np.ceil(bot))),max(0,int(a)):min(image.width,int(np.ceil(b)))]=True
                target=np.zeros_like(cover);l,t,r,b=map(int,roi);target[t:b,l:r]=True
                union=(cover|target).sum();intersection=(cover&target).sum()
                roi_decision=measure_orientation(image.crop(roi),unit='block',use_osd=use_osd)
                row['minority']=dict(unit=c['roi_unit'],truth_cw=c['roi_truth_cw'],numbers_only=c.get('numbers_only',False),
                    found_axis=bool(hits),union_iou=float(intersection/max(1,union)),
                    found=sum(overlap(p['box'],roi)>0 and p['axis']==correct_axis for p in proposals),
                    decisions=[r['decision'].orientation_cw for r in all_hits],
                    errors=sum(r['decision'].orientation_cw not in (None,c['roi_truth_cw']) for r in all_hits),
                    accepted=sum(r['decision'].orientation_cw is not None for r in all_hits),
                    oracle=decision_row(roi_decision,c['roi_truth_cw']))
            if c['kind']=='composite' or c.get('source')=='s2-6419488b7f8e69fd20da-p00001' or i<4:
                draw(image,regions,out/(c['id']+'.regions.jpg'),c.get('roi'))
        results.append(row)
        save(out/'decisions'/f"{c['id']}.json",row)
        print(i+1,len(cases),c['id'],whole.orientation_cw,'truth',truth,'seconds',round(measure_s,3),flush=True)
    summary={}
    for scope in ('development','research'):
        subset=[r for r in results if r['research']==(scope=='research')]
        whole=[r for r in subset if r['kind']=='whole']
        summary[scope]=dict(whole={str(a):counts([r['whole'] for r in whole if r['applied_cw']==a]) for a in (0,90,180,270)},
            main_regions={str(a):counts([r['regions'][0] for r in whole if r['applied_cw']==a]) for a in (0,90,180,270)},
            all_regions={str(a):counts([g for r in whole if r['applied_cw']==a for g in r['regions']]) for a in (0,90,180,270)},
            measure_time=time_summary([r['measure_seconds'] for r in whole]),
            regions_time=time_summary([r['region_seconds'] for r in whole]))
        summary[scope]['composites']=[dict(id=r['id'],main=r['regions'][0]['orientation_cw'],**r['minority']) for r in subset if r['kind']=='composite']
        summary[scope]['skew']=counts([r['whole'] for r in subset if r['kind']=='skew'])
        summary[scope]['words']={str(a):counts([r['whole'] for r in subset if r['kind']=='crop' and r['whole']['evidence'].get('polarity_source')=='word-requires-region' and r['whole']['truth_cw']==a]) for a in (0,90,180,270)}
    summary['use_osd']=use_osd
    summary['errors']=[dict(id=r['id'],scope='whole',decision=r['whole']['orientation_cw'],truth=r['whole']['truth_cw']) for r in results if r['whole']['error']]
    summary['region_errors']=[dict(id=r['id'],region=g['id'],decision=g['orientation_cw'],truth=g['truth_cw']) for r in results for g in r.get('regions',[]) if g['error']]
    real=Image.open(ROOT/'.astra/pages/s2-6419488b7f8e69fd20da-p00001.png').convert('L')
    real_rows=[]
    for name,box,truth in [('title',[180,487,320,1907],270),('Kapnou',[1270,3922,1530,4037],180),
                           ('folio',[1610,187,1810,297],0),('numbers',[1710,390,2390,1180],270)]:
        decision=measure_orientation(real.crop(box),unit='line' if name=='title' else 'block',use_osd=use_osd)
        real_rows.append(dict(name=name,box=box,**decision_row(decision,truth)))
    save(out/'real-crops.json',real_rows)
    save(out/'summary.json',summary)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=OUT)
    p.add_argument('--osd',action='store_true');p.add_argument('--no-research',action='store_true')
    args=p.parse_args();evaluate(args.out,use_osd=args.osd,include_research=not args.no_research)
