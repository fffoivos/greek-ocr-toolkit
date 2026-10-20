"""Step-0 offline applicability probe. No pixels are painted by this probe."""
from __future__ import annotations
import sys, json, hashlib, socket, time
from dataclasses import asdict
from pathlib import Path
from collections import defaultdict
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(OUT.parent))
import run_f2 as prior
from greekocr.glyphs.recut import LineFit, _neighbour, _voronoi_keep, fit_box
from greekocr.glyphs.lines_api import straighten
from greekocr.glyphs.components import binarise, to_gray
from greekocr.pages import process_page
from greekocr.pages.tables import line_piece


def runtime_fit(line):
    """The existing LineFit sampler, with its base carrying the body centre."""
    if isinstance(line,dict):
        x0,x1,xh=line['x0'],line['x1'],line['xheight']
        base,mean=np.asarray(line['baseline']),np.asarray(line['meanline'])
    else:
        x0,x1,xh=line.x0,line.x1,line.xheight
        base,mean=line.baseline,line.meanline
    rise=float(np.median(base-mean))
    return LineFit(x0,x1,(base+mean)/2,xh,rise,rise,0,(x0,0,x1,1))


def google_fit(fit):
    return LineFit(fit.x0,fit.x1,fit.base-fit.rise/2,fit.xh,fit.rise,fit.up,fit.down,fit.box)


def ownership_mask(ink,line,neighbours,crop_box):
    """Lossless integer grid adapter around existing neighbour and ownership code."""
    x0,y0,x1,y1=map(int,crop_box)
    a,b=max(0,min(x0,line.x0)),min(ink.shape[1],max(x1,line.x1))
    xs=np.arange(a,b,dtype=float)
    centre=line.base_at(xs)
    rounded=np.rint(centre)
    # Existing 4.2-xh recut context, enlarged only for ownership observation of
    # the complete ORIGINAL rectangle. No output rectangle changes.
    radius=max(1,int(np.ceil(4.2*line.xh)),int(np.ceil(np.max(rounded-y0))),int(np.ceil(np.max(y1-rounded))))
    straight,miss,br=straighten(ink[:,a:b].astype(float),rounded,1,paper=0,above=radius,below=radius+1)
    curves=[]
    for side in (-1,1):
        nb=_neighbour(neighbours,xs,centre,line.xh,side)
        curves.append(np.full(len(xs),side*np.inf) if nb is None else br+centre+nb[1]-rounded)
    keep=_voronoi_keep(straight.astype(bool)&~miss,miss,float(br),curves[0],curves[1],line.rise)
    cols=np.arange(x0,x1)-a
    rows=np.arange(y0,y1)[:,None]-rounded[cols].astype(int)[None,:]+br
    # radius construction covers every original crop pixel exactly.
    foreign=ink[y0:y1,x0:x1]&~keep[rows,cols[None,:]]
    return foreign


def match(box,fits):
    x0,y0,x1,y1=box
    xs=np.arange(x0,x1,dtype=float)
    candidates=[]
    for i,f in enumerate(fits):
        overlap=max(0,min(x1,f.x1)-max(x0,f.x0))/(x1-x0)
        if overlap<.5:continue
        distance=abs(float(np.median(f.base_at(xs)))-(y0+y1)/2)/max(1,f.xh)
        if distance<=1.5:candidates.append((distance,i))
    return min(candidates)[1] if candidates else None


def main():
    rr,_=prior.bind()
    chosen=[]
    for source in prior.SOURCES:
        chosen.append(next(r for r in rr if r['stratum']==source and r['dev']))
    results=[]
    for r in chosen:
        group=[t for t in rr if t['page_id']==r['page_id']]
        native,_,original,_,_,prov=prior.page_bundle(group)
        start=time.monotonic()
        runtime=process_page(native)
        lines=[l for l in runtime.segmentation.lines if l.discounted is None]
        fits=[runtime_fit(l) for l in lines]
        # Store exact arrays, not rounded to_record(), so equivalent means exact.
        payload=[dict(x0=l.x0,x1=l.x1,xheight=l.xheight,baseline=l.baseline.tolist(),meanline=l.meanline.tolist()) for l in lines]
        restored=[runtime_fit(l) for l in json.loads(json.dumps(payload))]
        gray=to_gray(native);ink=binarise(gray)
        google=[]
        for old in original.values():
            google.extend(google_fit(f) for f in fit_box(gray,tuple(old['crop_bbox']),splits=False))
        counts=dict(lines=len(group),runtime_lines=len(fits),google_fits=len(google),matched=0,equivalent_equal=0,runtime_piece_equal=0,google_equal=0,ink_pixels=0,disagreed_ink_pixels=0,mask_intersection=0,mask_union=0)
        comparisons=[]
        for t in group:
            box=t['crop_bbox'];i=match(box,fits);j=match(box,google)
            if i is None or j is None:continue
            actual=ownership_mask(ink,fits[i],[f for k,f in enumerate(fits) if k!=i],box)
            equivalent=ownership_mask(ink,restored[i],[f for k,f in enumerate(restored) if k!=i],box)
            assert np.array_equal(actual,equivalent)
            pc=line_piece(lines[i],i,native.size).box
            runtime_mask=ownership_mask(ink,fits[i],[f for k,f in enumerate(fits) if k!=i],pc)
            restored_mask=ownership_mask(ink,restored[i],[f for k,f in enumerate(restored) if k!=i],pc)
            assert np.array_equal(runtime_mask,restored_mask)
            gmask=ownership_mask(ink,google[j],[f for k,f in enumerate(google) if k!=j],box)
            x0,y0,x1,y1=box
            counts['matched']+=1;counts['equivalent_equal']+=1;counts['runtime_piece_equal']+=1
            counts['google_equal']+=int(np.array_equal(actual,gmask))
            counts['ink_pixels']+=int(ink[y0:y1,x0:x1].sum())
            counts['disagreed_ink_pixels']+=int((actual^gmask).sum())
            counts['mask_intersection']+=int((actual&gmask).sum());counts['mask_union']+=int((actual|gmask).sum())
            comparisons.append(dict(id=t['id'],box=box,runtime_mask_sha256=hashlib.sha256(actual.tobytes()).hexdigest(),google_mask_sha256=hashlib.sha256(gmask.tobytes()).hexdigest(),runtime_mask_pixels=int(actual.sum()),google_mask_pixels=int(gmask.sum())))
        assert counts['matched']>0
        counts['ink_agreement']=1-counts['disagreed_ink_pixels']/max(1,counts['ink_pixels'])
        counts['masked_iou']=counts['mask_intersection']/max(1,counts['mask_union'])
        results.append(dict(source=r['stratum'],page_id=r['page_id'],counts=counts,comparisons=comparisons,provenance=prov,seconds=time.monotonic()-start))
        prior.write_json(OUT/'step0'/f"{r['stratum']}.json",results[-1])
        print(r['stratum'],counts,'seconds',round(time.monotonic()-start,1),flush=True)
    prior.write_json(OUT/'step0/agreement.json',dict(inference_applicable=True,equivalent_inputs_exact=True,training_geometry='runtime-detected curves; Google fits comparison only',pages=results,source_head='9ac8b357',probe_sha256=prior.file_sha256(__file__)))

if __name__=='__main__':main()
