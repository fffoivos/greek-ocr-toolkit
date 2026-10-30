"""Cheap column-continuity nomination plus contextual whole-band repetition."""
import cv2,numpy as np
from scipy.signal import find_peaks
from .ink_motifs import strip
from .geometry import quantize,line_axis,roi
from .contracts import bbox
from .image_evidence import components
from .ink_photometry import percentiles8
from .ink_recurrence import render as recurrence


def coarse_scout(gray,item,height):
    """Axis-aligned, eight samples per body; only nominates deskewed inspection."""
    x0,y0,x1,y1=roi(bbox(item),gray.shape)
    step=max(1,int(height/8))
    raw=gray[y0:y1:step,x0:x1:step]
    if not raw.size or x1-x0<5*height:return False
    paper,core=percentiles8(raw,[90,10]);ink=(raw<paper-.5*(paper-core)).astype(np.uint8)
    if ink.any(0).mean()<.8:return False
    _,stats,_=components(ink)
    large=sum(q[4] for q in stats if q[2]>1.5*height/step)
    return bool(large>.25*ink.sum())


def scout(gray,item,height,*,samples=16):
    raw,s=strip(gray,item,height,samples=samples)
    paper,core=percentiles8(raw,[90,10]);ink=raw<paper-.5*(paper-core)
    occupied=ink.any(0)
    _,stats,_=components(ink.astype(np.uint8))
    large=sum(q[4] for q in stats if q[2]>2*height*s)
    return dict(occupancy=float(occupied.mean()),width_h=raw.shape[1]/(height*s),large_ink=float(large/max(ink.sum(),1))),raw,s


def inspect(gray,item,height,diagnostic=False,*,scouted=None,samples=16,template_specs=None):
    if not diagnostic and not (coarse_scout(gray,item,height) if scouted is None else scouted):
        return dict(drop=False,reason='coarse connected-band scout negative',coverage=0.,matches=[]),None
    witness,raw,s=scout(gray,item,height,samples=samples)
    if not diagnostic and (witness['width_h']<5 or witness['occupancy']<.9 or witness['large_ink']<.45):
        return dict(witness,drop=False,reason='column continuity absent',coverage=0.,matches=[]),raw
    # A low-resolution spatial rendering nominates the expensive full witness.
    # Whole-strip autocorrelation cannot nominate short fragments whose repeats
    # lie in the surrounding frame. This test includes that context.
    reduced=None
    recurrent=None
    if not diagnostic and samples==16:
        recurrent=recurrence(gray,item,height,route='heuristic')
        if not recurrent['nominate']:
            return dict(witness,drop=False,reason='local four-copy recurrence absent',coverage=0.,matches=[],recurrence=recurrent),raw
        reduced,_=inspect(gray,item,height,diagnostic=True,samples=8)
        if reduced['coverage']<.125 or reduced['span']<.5:
            return dict(witness,drop=False,reason='reduced spatial repetition absent',coverage=0.,matches=[],
                        reduced=dict(coverage=reduced['coverage'],span=reduced['span']),recurrence=recurrent),raw
    b=bbox(item);axis=line_axis(item);left=max(0,b[0]-6*height);right=min(gray.shape[1]-1,b[2]+6*height)
    half=(b[3]-b[1])/2
    expanded=dict(polygon=[[left,axis[0]+axis[1]*left-half],[right,axis[0]+axis[1]*right-half],
                           [right,axis[0]+axis[1]*right+half],[left,axis[0]+axis[1]*left+half]])
    context,s=strip(gray,expanded,height,samples=samples)
    paper,core=map(float,percentiles8(context,[90,10]));ink=np.clip((paper-context.astype(np.float32))/max(paper-core,1),0,1)
    h=height*s
    target0=int(round((b[0]-left)*s));target1=min(ink.shape[1],target0+raw.shape[1])
    candidates=[];specs=[]
    for bh in (.5,1.,1.5):
      th=min(ink.shape[0],quantize(bh*h))
      for top in np.unique(np.linspace(0,ink.shape[0]-th,4).astype(int)):
       for bw in (1.,1.5,2.,3.,4.,6.):
        tw=quantize(bw*h)
        if ink.shape[1]<4*tw:continue
        for bx in np.unique(np.linspace(0,ink.shape[1]-tw,5).astype(int)):
            specs.append((bx,top,tw,th))
    if template_specs is not None:specs=template_specs
    for bx,top,tw,th in specs:
            template=ink[top:top+th,bx:bx+tw]
            if template.std()<.15:continue
            response=cv2.matchTemplate(ink,template,cv2.TM_CCOEFF_NORMED)
            prof=response.max(0);yy=response.argmax(0)
            peaks,_=find_peaks(prof,height=.75,distance=max(1,int(.85*tw)))
            peaks=np.r_[0,peaks,len(prof)-1];peaks=np.unique(peaks[prof[peaks]>=.75])
            if len(peaks)<4:continue
            gaps=np.diff(peaks);period=float(np.median(gaps))
            # Printed motif spacing can drift; random recurring letter fragments
            # do not maintain this sequence. Skipped copies are not bridged here.
            if np.std(gaps)/max(period,1)>.23:continue
            cover=np.zeros(ink.shape,np.uint8)
            template_support=cv2.dilate((template>.45).astype(np.uint8),np.ones((3,3),np.uint8))
            for x in peaks:cover[yy[x]:yy[x]+th,x:x+tw] |= template_support
            numerator=(ink*cover)[:,target0:target1].sum();denom=ink[:,target0:target1].sum()
            coverage=float(numerator/max(denom,1));span=float((peaks[-1]-peaks[0]+tw)/ink.shape[1])
            candidates.append(dict(coverage=coverage,span=span,cover=cover,period=period,
                         matches=[[int(x),int(yy[x]),float(prof[x])] for x in peaks],
                         template=[int(bx),int(top),tw,th],target=[target0,target1]))
    best=None
    for candidate in candidates:
        peers=[q for q in candidates if abs(q['period']/candidate['period']-1)<.18]
        peers=sorted(peers,key=lambda q:-q['coverage'])[:8]
        cover=np.maximum.reduce([q['cover'] for q in peers])
        coverage=float((ink*cover)[:,target0:target1].sum()/max(ink[:,target0:target1].sum(),1))
        if best is None or coverage>best['coverage']:
            best=dict(coverage=coverage,span=max(q['span'] for q in peers),matches=candidate['matches'],
                template=candidate['template'],target=candidate['target'],period_h=candidate['period']/h,
                supports=[{k:v for k,v in q.items() if k!='cover'} for q in peers],cover=cover)
    best=best or dict(coverage=0.,span=0.,matches=[])
    covered=best.pop('cover',np.zeros(ink.shape,np.uint8))
    original=(ink>.5).astype(np.uint8)[:,target0:target1]
    labels,stats,_=components(original)
    supported=covered[:,target0:target1]
    glyphs=[]
    for j,q in enumerate(stats):
        if not (.5*h<q[3]<1.8*h and .12*h<q[2]<1.6*h and q[4]>.055*h*h):continue
        x,y,w,ch,area=q
        if x==0 or y==0 or x+w>=original.shape[1] or y+ch>=original.shape[0]:continue
        component=labels[y:y+ch,x:x+w]==j+1
        fraction=float(supported[y:y+ch,x:x+w][component].mean())
        if fraction<.5:glyphs.append(q.tolist())
    best['remaining_glyphs']=len(glyphs)
    best['unexplained_original_components']=glyphs
    best.update(witness)
    large=[q for q in best.get('supports',[]) if q['template'][2]>=3*h and q['template'][3]>=h and len(q['matches'])>=5]
    best['large_motif']=bool(large)
    best['drop']=best['remaining_glyphs']<3 and best['span']>.65 and (best['coverage']>.68 or (best['coverage']>.45 and bool(large)))
    best['reason']='continuous repeated non-word band' if best['drop'] else 'repeat coverage insufficient'
    if reduced is not None:best['reduced']=dict(coverage=reduced['coverage'],span=reduced['span'])
    if recurrent is not None:best['recurrence']=recurrent
    return best,context
