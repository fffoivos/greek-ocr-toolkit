"""Page-relative component photometry. Experimental R6 task A renderer.

Components are observed ink, not transcribed characters. Faintness and stroke
width remain separate axes. Normal print is calibrated within the page. A broad
normal distribution abstains; optical-density proximity to paper bounds the
faint class. No font, text content, page identity or provenance is inferred.
"""
from time import perf_counter
import cv2
import numpy as np
from .contracts import bbox
from .geometry import roi, height_proxy
from .ink_photometry import percentiles8


def components(gray, item, height, *, route='slow'):
    box=bbox(item); x,y,z,w=roi(box,gray.shape); pad=max(2,round(height))
    a,b,c,d=max(0,x-pad),max(0,y-pad),min(gray.shape[1],z+pad),min(gray.shape[0],w+pad)
    raw=gray[b:d,a:c]; scale=min(1.,24/height) if route=='explicit' else 1.
    if scale<1:raw=cv2.resize(raw,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    h=height*scale; k=max(3,round(2*h)|1)
    # One exact uint8 histogram replaces two independent order-statistic scans.
    p50,p90=percentiles8(raw,[50,90])
    paper=(cv2.medianBlur(raw,k).astype(np.float32) if route!='localized' else np.full(raw.shape,float(p50),np.float32))
    contrast=np.maximum(0,paper-raw)/np.maximum(paper,1)
    core_paper=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8)).astype(np.float32)
    # A large solid component can occupy the local median window. Never call
    # its black interior faint merely because the estimated paper became black.
    core_paper=np.maximum(core_paper,float(p90))
    core_contrast=np.maximum(0,core_paper-raw)/np.maximum(core_paper,1)
    mask=np.zeros(raw.shape,np.uint8)
    cv2.fillPoly(mask,[np.rint((np.asarray(item['polygon'])-[a,b])*scale).astype(np.int32)],1)
    # Bright-background neighbour differences estimate noise, separately from ink.
    bright=contrast<=np.median(contrast)
    diff=np.abs(np.diff(raw.astype(np.float32),axis=1)); pairs=bright[:,1:]&bright[:,:-1]
    noise=max(1.,float(np.median(diff[pairs]))/.954) if pairs.any() else 1.
    floor=3*noise/np.maximum(paper,1)
    # One fortieth of a letter body: suppress sampling-scale specks without
    # merging adjacent strokes. The old .6 pixel blur was this scale at h=24.
    sigma=max(.25,h/40)
    radius=max(1,int(np.ceil(2*sigma)))
    smooth=cv2.GaussianBlur(core_contrast,(2*radius+1,)*2,sigma)
    selected=np.rint(smooth[mask>0]*255).astype(np.uint8)
    threshold=cv2.threshold(selected,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[0]/255 if selected.size else 1.
    ink=((smooth>np.maximum(floor,threshold))&(mask>0)).astype(np.uint8)
    n,lab,stats,_=cv2.connectedComponentsWithStats(ink,8)
    edge=(mask>cv2.erode(mask,np.ones((3,3),np.uint8))).astype(np.uint8)
    records=[]
    for j in range(1,n):
        xx,yy,ww,hh,area=map(int,stats[j])
        if area<max(3,.006*h*h):continue
        m=(lab[yy:yy+hh,xx:xx+ww]==j).astype(np.uint8); vals=core_contrast[yy:yy+hh,xx:xx+ww]
        depth=float(np.percentile(vals[m>0],90)); core=(m>0)&(vals>=depth/2)
        dt=cv2.distanceTransform(np.pad(core.astype(np.uint8),1),cv2.DIST_L2,5)[1:-1,1:-1]
        ridge=(dt>0)&(dt>=cv2.dilate(dt,np.ones((3,3),np.uint8)))
        tone=float(np.median(vals[ridge])) if ridge.any() else depth
        width=float(2*np.median(dt[ridge])/scale) if ridge.any() else 0.
        body=hh>=.25*h and hh<=2*h and ww>=.07*h and ww<=3*h
        records.append(dict(bbox=[a+xx/scale,b+yy/scale,a+(xx+ww)/scale,b+(yy+hh)/scale],
            core=tone,peak=depth,noise=3*noise/max(float(np.median(paper[yy:yy+hh,xx:xx+ww])),1),
            stroke=width,stroke_h=width/height,area=area/scale**2,body=bool(body),
            clipped=bool(np.any((m>0)&(edge[yy:yy+hh,xx:xx+ww]>0)))))
    return records


def reference(regions):
    bodies=[g for r in regions for g in r['components'] if g['body']]
    if not bodies:return dict(core=0.,stroke=0.,spread=0.,boundary=0.,body_height=0.,support=0)
    mid=float(np.median([g['core'] for g in bodies])); upper=[g for g in bodies if g['core']>=mid]
    ref=float(np.median([g['core'] for g in upper])); width=float(np.median([g['stroke'] for g in upper]))
    spread=1.4826*float(np.median(np.abs(np.array([g['core'] for g in bodies])-ref)))
    # Nearest paper/print prototype in optical density, with a one-DN
    # saturation interval. This prevents a zero-MAD black mode from declaring
    # slightly grey front ink faint. The empirical lower envelope may only
    # make the decision more conservative.
    optical_midpoint=1-np.sqrt(max(1-ref,1/255))
    boundary=max(0.,min(ref-3*spread,optical_midpoint))
    return dict(core=ref,stroke=width,boundary=boundary,optical_midpoint=float(optical_midpoint),spread=spread,body_height=float(np.median([g['bbox'][3]-g['bbox'][1] for g in upper])),support=len(upper))


def normal_run(components, strong, bh):
    """Two independently repeated adjacency links establish a run (3 bodies).

    A single body gives no adjacency evidence; a pair gives just one link and
    can be a broken glyph. The third body corroborates the shared row and
    spacing. Body centres of ALL ink establish the segment's own row, so a
    neighbouring black letter cannot protect an otherwise faint row.
    """
    bodies=[g for g in components if g['body'] and not g.get('clipped',False)]
    if not bodies or bh<=0:return []
    # The observed median is robust to isolated neighbouring components.
    yc=float(np.median([(g['bbox'][1]+g['bbox'][3])/2 for g in bodies]))
    candidates=sorted([g for g in strong if g['body'] and not g.get('clipped',False)
        and g['bbox'][3]-g['bbox'][1]>=bh/2
        and abs((g['bbox'][1]+g['bbox'][3])/2-yc)<bh/2],key=lambda g:g['bbox'][0])
    runs=[];run=[]
    for g in candidates:
        if run:
            a=run[-1]['bbox'];b=g['bbox']
            if b[0]-a[2]>bh or abs((a[1]+a[3]-b[1]-b[3])/2)>=bh/2:
                runs.append(run);run=[]
        run.append(g)
    runs.append(run)
    return [g['bbox'] for r in runs if len(r)>=3 for g in r]


def classify(regions, ref):
    for r in regions:
        for g in r['components']:
            g['relative_core']=g['core']/max(ref['core'],1e-6)
            g['relative_stroke']=g['stroke']/max(ref['stroke'],1e-6)
            g['faint']=bool(max(g['core'],g['peak'])+g['noise']<ref['boundary'])
            g['edge_fragment']=bool(g['clipped'] and g['bbox'][3]-g['bbox'][1]<ref.get('body_height',0)/2)
        bodies=[g for g in r['components'] if g['body']]; normal=[g for g in bodies if not g['faint'] and not g['edge_fragment']]
        strong=[g for g in r['components'] if not g['faint'] and not g['edge_fragment']]
        bh=ref.get('body_height',0)
        witness=normal_run(r['components'],strong,bh)
        supported=bool(witness)
        faint_bodies=[g for g in bodies if g['faint']]
        dark_area=sum(g['area'] for g in r['components'] if not g['faint'] and not g['edge_fragment'] and not g['clipped'])
        faint_area=sum(g['area'] for g in faint_bodies)
        owned=[g for g in bodies if not g['clipped']]
        yc=float(np.median([(g['bbox'][1]+g['bbox'][3])/2 for g in owned])) if owned else 0.
        row=[g for g in owned if g['bbox'][3]-g['bbox'][1]>=bh/2 and abs((g['bbox'][1]+g['bbox'][3])/2-yc)<bh/2]
        short_ambiguous=bool(len(row)<3 and any(not g['faint'] for g in row))
        # "Essentially all" excludes a substantial normal word even when its
        # letters touch and form one component. Permit at most one median faint
        # body of normal ink as isolated contamination, and never a dark majority.
        isolated=bool(faint_bodies and dark_area<=np.median([g['area'] for g in faint_bodies]) and dark_area<faint_area)
        r.update(normal_run=supported,normal_witnesses=witness,bodies=len(bodies),normal=len(normal),normal_share=len(normal)/len(bodies) if bodies else None,
                 normal_area=dark_area,faint_area=faint_area,isolated_normal_ink=isolated,short_ambiguous=short_ambiguous,
                 drop=bool(faint_bodies and isolated and not supported and not short_ambiguous and ref['support']>=12),reason='faint bodies throughout; no repeated normal adjacency; at most one body of isolated normal ink')
    return regions


def render(gray,items,*,height=None,route='slow'):
    if route not in ('slow','explicit'):raise ValueError(route)
    start=perf_counter();h=height_proxy(items,(gray.shape[1],gray.shape[0])) if height is None else height
    regions=[dict(line=i,bbox=bbox(q),components=components(gray,q,h,route=route)) for i,q in enumerate(items)]
    ref=reference(regions);classify(regions,ref)
    return dict(version=9,route=route,height=h,reference=ref,regions=regions,
                suppress_indices=[r['line'] for r in regions if r['drop']],seconds=perf_counter()-start)


def analyze(gray,items,*,height=None,detail=False,ownership_evidence=None,selected_indices=None,require_reference=False):
    """Sparse longitudinal scout, sampled page calibration, native ROI witnesses.

    Only accepted original polygons can become exclusions. No front/back cause
    is inferred. The page identity and old-model line list are never inputs.
    """
    from .ink_faint_scout import render as scout_render
    start=perf_counter();h=height_proxy(items,(gray.shape[1],gray.shape[0])) if height is None else height
    if ownership_evidence is not None:
        if ownership_evidence.get('image_size')!=[gray.shape[1],gray.shape[0]]:raise ValueError('Page ownership image size mismatch')
        # A prior box census cannot certify newly recovered or reshaped rows.
        # Nominate the current polygons on every call.
    scout=scout_render(gray,items,h);candidates=scout['candidate_indices']
    if selected_indices is not None:candidates=[i for i in candidates if i in selected_indices]
    if not candidates and not require_reference:
        return dict(version=9,height=h,scout=scout,reference=None,regions=[],suppress_indices=[],scout_s=scout['seconds'],seconds=perf_counter()-start)
    if not items:
        return dict(version=10,height=h,scout=scout,reference=reference([]),regions=[],suppress_indices=[],scout_s=scout['seconds'],seconds=perf_counter()-start)
    # Sample the observed distribution across weak and strong rows, not only
    # the darkest heading. Bound the calibration search by physical line length.
    ordered=sorted(range(len(items)),key=lambda i:scout['regions'][i]['core'])
    ids=sorted({ordered[i] for i in np.linspace(0,len(ordered)-1,min(8,len(ordered))).astype(int)})
    calibration=[];samples=[]
    for i in ids:
        q=items[i];x,y,z,w=bbox(q);mid=(x+z)/2
        a=max(x,mid-8*h);b=min(z,mid+8*h)
        # Intersect the real polygon with a central calibration strip. Retain
        # sloping edges: a rectangle would sample a neighbouring row on a curl.
        from shapely.geometry import Polygon,box as rect
        geom=Polygon(np.asarray(q['polygon'],float)).intersection(rect(a,y,b,w))
        if geom.geom_type!='Polygon' or geom.is_empty:continue
        sample=dict(polygon=list(geom.exterior.coords)[:-1])
        samples.append((i,sample))
    regions=[dict(line=i,bbox=bbox(items[i]),components=components(gray,items[i],h,route='localized')) for i in candidates]
    # No isolated-body shortcut: it would defeat the repeated-adjacency test.
    calibration=[dict(line=i,bbox=bbox(q),components=components(gray,q,h,route='localized')) for i,q in samples]
    ref=reference(calibration);classify(regions,ref)
    return dict(version=9,height=h,scout=scout,reference=ref,calibration=calibration if detail else [dict(line=r['line'],bbox=r['bbox']) for r in calibration],
                regions=regions,suppress_indices=[r['line'] for r in regions if r['drop']],scout_s=scout['seconds'],seconds=perf_counter()-start)
