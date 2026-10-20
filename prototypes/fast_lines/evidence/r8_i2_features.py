"""Iteration-2 offline attribution and contrast falsification, never runtime.

Existing saved rows are conditional evidence. Crop fitting uses its own starting
scale; agreement with font.evidence after that fit is not independent proof.
"""
import argparse,json
from pathlib import Path
from types import SimpleNamespace
from time import perf_counter
import cv2,numpy as np
from greekocr.glyphs.components import _line_geometry
from greekocr.pages.pixels import prepare_pixels
from greekocr.pages.font import evidence,fit_guides
from ..shared.geometry import height_proxy
from ..shared.image_evidence import ImageEvidence
from ..layout_barriers.fast import scout,verify_rule
from ..layout_barriers.run import detect
from ..shared import observations as obs
from .r8_measurements import digest,dump


def attribution(inputs,old,out):
    inputs,old,out=map(Path,(inputs,old,out));out.mkdir(parents=True,exist_ok=True);receipt=[]
    for row in json.loads(inputs.read_text())['pages']:
        name=row['page'];g=cv2.imread(row['path'],0);assert digest(row['path'])==row['sha256']
        selected=json.loads((old/'local-scale'/f'{name}.json').read_text())['selected']
        # The unchanged four dense-profile controls cover pages with no chains.
        probes=selected or [dict(source=p['source'],crop=p['bbox']) for p in json.loads((old/'pilot'/f'{name}.json').read_text())['probes']]
        original=json.loads(Path(row['original_paddle']).read_text())['original']
        saved=json.loads((inputs.parent/'slow'/name/'reference.json').read_text())
        t0=perf_counter();pixels=prepare_pixels(g);prep_s=perf_counter()-t0;lookup={int(c[5]):c for c in pixels.components};records=[];tiles=[]
        for qi,q in enumerate(probes):
            a,t,b,d=map(int,q['crop']);crop=g[t:d,a:b];raw=cv2.cvtColor(crop,cv2.COLOR_GRAY2BGR);view=raw.copy();path=np.asarray(q.get('path',[]))
            if len(path):
                extent=q['scale']['value_px'];focus=(float(np.median(path[:,1])-t-extent/2),float(np.median(path[:,1])-t+extent/2));rid=q['reference_row']
            else:
                poly=np.array(original[q['source']]['polygon']);focus=(float(poly[:,1].min()-t),float(poly[:,1].max()-t));rid=None
            fitted=_line_geometry(crop,xh_prior=None,focus=focus)
            letters=[c for c in fitted.components if c.role=='letter'];components=np.array([[c.x0,c.y0,c.x1,c.y1,c.area,c.index,0] for c in letters]).reshape(-1,7)
            p=SimpleNamespace(components=components,labels=fitted.labels,xheight=pixels.xheight)
            line=SimpleNamespace(xheight=fitted.band.xh,baseline=fitted.band.bottom.copy(),component_ids=np.array([c.index for c in letters]),x0=0,x1=crop.shape[1],discounted=None,support=len(letters))
            fit_guides(p,[line])
            for c in fitted.components:cv2.rectangle(view,(c.x0,c.y0),(c.x1,c.y1),(0,150,0) if c.role=='letter' else (200,120,0),1)
            for key,color in [('baseline',(255,0,0)),('meanline',(0,0,255))]:cv2.polylines(view,[np.c_[np.arange(crop.shape[1]),getattr(line,key)].astype(np.int32)],False,color,1)
            ref=next((z for z in saved['rows'] if z['id']==rid),None);conditional=None;full=[]
            if ref is not None:
                lr=SimpleNamespace(**ref);lr.baseline=np.array(ref['baseline']);lr.component_ids=np.array(ref['component_ids']);counts,points=evidence(pixels,lr,_lookup=lookup)
                for label in ref['component_ids']:
                    c=lookup[label];x0,y0,x1,y1=map(float,c[:4])
                    if x0<b and x1>a and y0<d and y1>t:full.append(dict(id=int(label),bbox=[x0,y0,x1,y1],area=float(c[4])))
                conditional=dict(row_id=rid,starting_xheight=ref['xheight'],after_capital_xheight=lr.xheight,borrowed=ref['borrowed'],component_ids=ref['component_ids'],classes=counts,contacts=points,baseline=ref['baseline'],x0=ref['x0'],x1=ref['x1'])
            title=f"{qi} field {q.get('field')} chain {q.get('row')} initial {fitted.band.xh:.1f} fitted {line.xheight:.1f} CONDITIONAL"
            band=np.full((25,2*raw.shape[1],3),255,np.uint8);cv2.putText(band,title,(3,17),0,.4,(0,0,0),1)
            tiles.append(np.vstack([band,np.hstack([raw,view])]))
            record=dict(probe=qi,identity=q,crop=[a,t,b,d],starting_focus=focus,page_scale_prior=pixels.xheight,starting_scale=fitted.band.xh,starting_scale_source=fitted.band.xh_source,starting_baseline=fitted.band.bottom.tolist(),body_height_candidate=line.xheight,borrowed=line.borrowed,classes=line.ink_classes,contacts=line.guide_samples,components=[dict(id=int(c.index),bbox=[c.x0+a,c.y0+t,c.x1+a,c.y1+t],area=c.area,role=c.role,touches=c.touches) for c in fitted.components],conditional_reference=conditional,complete_reference_components=full,status='unvalidated candidate; raw adjudication required')
            records.append(record)
        # All tiles have equal native widths in the inherited probes.
        width=max(z.shape[1] for z in tiles);padded=[]
        for z in tiles:
            pad=np.full((z.shape[0],width,3),255,np.uint8);pad[:,:z.shape[1]]=z;padded.append(pad)
        cv2.imwrite(str(out/f'{name}.jpg'),np.vstack(padded));dump(out/f'{name}.json',dict(page=name,input_sha256=row['sha256'],reference_sha256=digest(inputs.parent/'slow'/name/'reference.json'),prepare_s=prep_s,probes=records))
        receipt.append(dict(page=name,probes=len(records),prepare_s=prep_s));print(name,len(records),flush=True)
    dump(out/'receipt.json',dict(pages=receipt,scope='existing crop fit and font attribution; no runtime promotion; saved row identities conditional',inputs_sha256=digest(inputs)))


def contrasts(inputs,old,out):
    inputs,old,out=map(Path,(inputs,old,out));out.mkdir(parents=True,exist_ok=True);receipt=[];original_ink=obs.ink
    for row in json.loads(inputs.read_text())['pages']:
        name=row['page']
        if (out/f'{name}.json').exists():
            r=json.loads((out/f'{name}.json').read_text());assert r['input_sha256']==row['sha256'];receipt.append(dict(page=name,scout_candidates=[len(s['candidates']) for s in r['scouts']],dense_rules=len(r['dense_native_rules']),native_threshold_band_pixels=r['threshold_band_pixels']));continue
        g=cv2.imread(row['path'],0);assert digest(row['path'])==row['sha256'];items=json.loads(Path(row['original_paddle']).read_text())['original'];h=height_proxy(items,g.shape[::-1]);profiles=json.loads((old/'pilot'/f'{name}.json').read_text())
        p=obs.paper(g,max(1,round(4*h))|1,method='mean');delta=p-g;low=delta>255*.06;high=delta>255*.08;tiles=[];probes=[]
        for probe in profiles['probes']:
            a,t,b,d=probe['bbox'];raw=cv2.cvtColor(g[t:d,a:b],cv2.COLOR_GRAY2BGR);v=raw.copy();changed=low[t:d,a:b]&~high[t:d,a:b];v[changed]=(0,0,255)
            band=np.full((24,2*raw.shape[1],3),255,np.uint8);cv2.putText(band,f"source {probe['source']}: red = .06 DN support absent at .08; not ownership",(4,16),0,.4,(0,0,0),1);tiles.append(np.vstack([band,np.hstack([raw,v])]))
            probes.append(dict(**probe,paper_range=[float(p[t:d,a:b].min()),float(p[t:d,a:b].max())],threshold_band_pixels=int(changed.sum()),raw_pixels=int(changed.size)))
        scouts=[]
        for threshold in (.06,.08):
            def alternative(*a,**kw):
                if kw.get('method')=='mean' and kw.get('arithmetic')=='dn':kw['threshold']=255*threshold
                return original_ink(*a,**kw)
            obs.ink=alternative
            try:s,_=scout(g,items)
            finally:obs.ink=original_ink
            scouts.append(dict(threshold=threshold,**s,native_verification=[verify_rule(g,c,h) for c in s['candidates']]))
        # Explicit native preparation and rule nomination run even when scout is
        # quiet. These old witnesses themselves remain hypotheses, not labels.
        ev=ImageEvidence(g,h,long_side=max(g.shape));ctx=SimpleNamespace(gray=g,ev=ev,height=h,items=items,size=g.shape[::-1]);barriers,rules,table=detect(ctx)
        width=max(z.shape[1] for z in tiles);tiles=[cv2.copyMakeBorder(z,0,0,0,width-z.shape[1],cv2.BORDER_CONSTANT,value=(255,255,255)) for z in tiles]
        cv2.imwrite(str(out/f'{name}.jpg'),np.vstack(tiles));record=dict(page=name,input_sha256=row['sha256'],height_engineering=h,native_window=round(4*h)|1,threshold_band_pixels=int((low&~high).sum()),probes=probes,scouts=scouts,dense_native_rules=rules,dense_barriers=barriers,table=table,scope='Finite rules and component support distinct; DN floor calibration not established')
        dump(out/f'{name}.json',record);receipt.append(dict(page=name,scout_candidates=[len(s['candidates']) for s in scouts],dense_rules=len(rules),native_threshold_band_pixels=record['threshold_band_pixels']));print(name,receipt[-1],flush=True)
    dump(out/'receipt.json',dict(pages=receipt,inputs_sha256=digest(inputs),arithmetic_domain=dict(paper_values=256,pixel_values=256,pairs=65536,division_product_disagreements=0),scope='23 positive/quiet pilot pages; native preparation bypasses scouts; not glyph identity or rule truth'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['body','masks']);p.add_argument('inputs');p.add_argument('old');p.add_argument('out');a=p.parse_args();(attribution if a.mode=='body' else contrasts)(a.inputs,a.old,a.out)
