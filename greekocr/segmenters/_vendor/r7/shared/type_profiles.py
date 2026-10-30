"""Observable body geometry; image pixels + boxes only, no text/page identities.

Dense original-pixel components are the offline renderer. Route 1 resamples the
same strip to 12 samples/provisional body. Route 2 uses sparse projection steps.
Connected ink pieces are NOT Unicode characters or named fonts.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from .geometry import line_axis, height_proxy
from .contracts import bbox


def strip(gray,item,samples=None):
    b=bbox(item); axis=line_axis(item)
    h=max(1.,min(cv2.minAreaRect(np.asarray(item['polygon'],np.float32))[1])*.5)
    step=1. if samples is None else max(1.,h/samples)
    x=np.arange(max(0,b[0]),min(gray.shape[1],b[2]),step,dtype=np.float32)
    dy=np.arange(-1.6*h,1.6*h+step,step,dtype=np.float32)
    if not len(x): x=np.array([0.],np.float32)
    mx=np.broadcast_to(x,(len(dy),len(x))).copy()
    my=(axis[0]+axis[1]*x[None,:]+dy[:,None]).astype(np.float32)
    patch=cv2.remap(gray,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255)
    return patch,x,dy,axis,h,step


def mode(values, h, weights=None):
    if len(values)==0: return None,0
    values=np.asarray(values); lo=float(values.min()); bw=max(.08*h,.5)
    hist=np.bincount(np.rint((values-lo)/bw).astype(int),weights=weights)
    smooth=gaussian_filter1d(hist.astype(float),.8)
    centre=lo+float(np.argmax(smooth))*bw
    near=abs(values-centre)<=.16*h
    return float(np.median(values[near])),int(near.sum())


def measure_line(gray,item,detail=False,samples=12,version=2):
    patch,x,dy,axis,prior,step=strip(gray,item,samples)
    h=prior/step
    # Local white reference is deliberately simple and shown by threshold masks.
    k=max(1,int(round(3*h)))|1
    paper=cv2.morphologyEx(patch,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8))
    contrast=(paper.astype(np.float32)-patch)/np.maximum(paper,1)
    ink=(contrast>.18).astype(np.uint8)
    n,labels,allstats,centres=cv2.connectedComponentsWithStats(ink,8)
    s=allstats[1:]; c=centres[1:]; n-=1
    valid=(s[:,3]>.4*h)&(s[:,3]<2.5*h)&(s[:,2]>.1*h)&(s[:,2]<4*h)&(s[:,4]>.055*h*h)
    # v1 included neighbouring ink. v2 isolates bottom-contact population first.
    centre_y=(dy[0]/step+c[:,1])
    eligible=valid & (abs(centre_y)<.85*h)
    if version>=2:
        density=gaussian_filter1d(ink.mean(1).astype(float),max(.5,.08*h))
        peaks,_=find_peaks(density,prominence=max(.03,float(density.max())*.18),distance=max(1,int(.65*h)))
        peaks=[int(k) for k in peaks if abs(dy[k]/step)<.9*h]
        peak=min(peaks,key=lambda k:abs(dy[k])) if peaks else int(np.argmax(density))
        centre=dy[peak]/step
        eligible &= abs(centre_y-centre)<.6*h
    else:
        peaks=[];centre=0.
    ii=np.flatnonzero(eligible)
    heights=s[ii,3].astype(float)
    body,body_support=mode(heights,h)
    if body is None: body=h
    bottom=s[:,1]+s[:,3]+dy[0]/step
    baseline,base_support=mode(bottom[ii],body)
    if baseline is None: baseline=.3*h
    if version>=2:
        ii=ii[abs(bottom[ii]-baseline)<.24*body]
    top,top_support=mode(s[ii,1]+dy[0]/step,body)
    if top is None: top=baseline-body
    measured=baseline-top
    if measured<.35*h: measured=body;top=baseline-body
    bodies=np.flatnonzero(valid & (s[:,1]+dy[0]/step<baseline-.3*measured)&
                         (bottom>baseline-.22*measured)&(bottom<baseline+.7*measured))
    assigned=[];marks=[];gaps=[]
    ordered=bodies[np.argsort(s[bodies,0])]
    for a,b in zip(ordered[:-1],ordered[1:]):
        gap=s[b,0]-(s[a,0]+s[a,2])
        if gap>=0: gaps.append(float(gap/measured))
    for i in np.flatnonzero((s[:,3]<.6*measured)&(s[:,4]>.01*measured*measured)):
        dx=np.maximum(np.maximum(s[i,0]-s[bodies,0]-s[bodies,2],s[bodies,0]-s[i,0]-s[i,2]),0)
        vy=(s[i,1]+s[i,3]+dy[0]/step)
        if len(bodies) and vy<top+.15*measured and vy>top-.9*measured and dx.min()<.45*measured:
            marks.append(int(i))
    guide={'body_top':top*step,'body_bottom':baseline*step}
    supports={'body_top':top_support,'body_bottom':base_support}
    above=bodies[(s[bodies,1]+dy[0]/step)<top-.24*measured]
    below=bodies[bottom[bodies]>baseline+.22*measured]
    if len(above)>=3: guide['tall_top']=float(np.median(s[above,1]+dy[0]/step)*step);supports['tall_top']=len(above)
    if len(below)>=3: guide['descender_bottom']=float(np.median(bottom[below])*step);supports['descender_bottom']=len(below)
    if len(marks)>=3:
        guide['mark_top']=float(np.median(s[marks,1]+dy[0]/step)*step)
        guide['mark_bottom']=float(np.median(s[marks,1]+s[marks,3]+dy[0]/step)*step)
        supports['mark_top']=supports['mark_bottom']=len(marks)
    # Stroke thickness is descriptive; it does not identify damage or typeface.
    dist=cv2.distanceTransform(ink,cv2.DIST_L2,3)
    ridge=(dist>0)&(dist>=cv2.dilate(dist,np.ones((3,3),np.uint8)))
    widths=2*dist[ridge]/measured
    record=dict(xheight=float(measured*step),prior=prior,axis=axis.tolist(),xrange=[float(x[0]),float(x[-1])],
        guides=guide,supports={k:int(v) for k,v in supports.items()},body_count=len(bodies),mark_count=len(marks),
        component_width_xh=float(np.median(s[bodies,2])/measured) if len(bodies) else None,
        gap_xh=np.quantile(gaps,[.25,.5,.75]).tolist() if gaps else None,
        stroke_xh=float(np.median(widths)) if len(widths) else None,
        guide_count=len(guide),baseline=None,semantics='body-contact hypotheses; no script identification',
        uncertain=base_support<5 or top_support<5,
        alternate_density_rows=[float(dy[k]) for k in peaks])
    if version>=3:
        record['joined_ink']=bool(len(bodies) and np.mean(s[bodies,2]>1.5*measured)>.25)
        record['uncertain'] |= record['joined_ink']
        record['gap_segments']=[[[float(x[0]+(s[a,0]+s[a,2])*step),float(axis[0]+axis[1]*(x[0]+(s[a,0]+s[a,2])*step)+(baseline+.5*measured)*step)],
                                [float(x[0]+s[b,0]*step),float(axis[0]+axis[1]*(x[0]+s[b,0]*step)+(baseline+.5*measured)*step)]]
                               for a,b in zip(ordered[:-1],ordered[1:]) if 0<=s[b,0]-s[a,0]-s[a,2]<1.5*measured]
    if version>=2 and record['uncertain']:
        record['unsupported_guides']=record['guides'];record['guides']={}
        record['guide_count']=0
    if detail:
        for i in range(n):
            sx,sy,w,hh,area=map(int,s[i]);gx=float(x[0]+sx*step)
            yoff=float(dy[0]+sy*step);xx=[gx,gx+w*step]
            p=[[xx[0],axis[0]+axis[1]*xx[0]+yoff],[xx[1],axis[0]+axis[1]*xx[1]+yoff],
               [xx[1],axis[0]+axis[1]*xx[1]+yoff+hh*step],[xx[0],axis[0]+axis[1]*xx[0]+yoff+hh*step]]
            assigned.append(dict(polygon=p,role='body' if i in bodies else 'mark' if i in marks else 'other',
                                 area=area*step*step))
        record['components']=assigned
    return record


def projection_line(gray,item,version=2):
    patch,x,dy,axis,h,step=strip(gray,item,12)
    # Route 2 pays for only 64 column samples; these are a sampling budget.
    patch=patch[:,np.linspace(0,patch.shape[1]-1,min(64,patch.shape[1])).astype(int)]
    paper=np.percentile(patch,90,axis=0)
    p=np.maximum(0,paper[None,:]-patch).mean(1)
    p=gaussian_filter1d(p,.6)
    peaks,_=find_peaks(p,prominence=max(p.max()*.15,1e-6),distance=max(1,int(.5*h/step)))
    if len(peaks): peak=min(peaks,key=lambda k:abs(dy[k])) if version>=2 else int(np.argmax(p))
    else: peak=int(np.argmax(p))
    active=p>p[peak]*.45
    lo=hi=peak
    while lo>0 and active[lo-1]:lo-=1
    while hi+1<len(p) and active[hi+1]:hi+=1
    return dict(xheight=float(max(step,dy[hi]-dy[lo]+step)),axis=axis.tolist(),xrange=[float(x[0]),float(x[-1])],
                guides={'body_top':float(dy[lo]),'body_bottom':float(dy[hi]+step)},
                peak_count=len(peaks),baseline=None,semantics='sparse density envelope, not semantic guides')


def size_groups(lines):
    groups=[]
    for i in sorted(range(len(lines)),key=lambda i:lines[i]['xheight']):
        h=lines[i]['xheight']
        if lines[i].get('uncertain'):
            lines[i]['size_group']=-1;continue
        if not groups or h>groups[-1]['minimum']*1.25:
            groups.append(dict(id=len(groups),minimum=h,members=[]))
        groups[-1]['members'].append(i);lines[i]['size_group']=groups[-1]['id']
    for g in groups:
        g['height']=float(np.median([lines[i]['xheight'] for i in g['members']]))
    return groups


def analyze(gray,items,*,route='explicit',detail=False,version=2):
    start=perf_counter()
    records=[]
    for i,item in enumerate(items):
        if item.get('discounted'):continue
        r=projection_line(gray,item,version) if route=='heuristic' else measure_line(gray,item,detail,
                        samples=None if route=='slow' else (24 if version>=3 else 12),version=version)
        records.append(dict(r,line=i))
    groups=size_groups(records)
    return dict(lines=records,size_groups=groups,route=route,seconds=perf_counter()-start,
                font_identity='unidentified; size classes are not fonts')
