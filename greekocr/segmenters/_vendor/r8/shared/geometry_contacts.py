"""Original-ink contacts and anchored paths beyond detector ends.

Slow diagnostic first. A component is ink, not necessarily a glyph or foreground.
The path is a body-support centre, not a baseline. Ambiguous neighboring paths
remain visible; this module does not change detector items.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.signal import find_peaks
from .geometry import height_proxy, line_axis, quantize, roi
from .contracts import bbox
from .geometry_fragments import candidates,hermite
from . import observations as obs


def prepare(gray, height, target_height=None, fast_filter=False, *, with_labels=False, with_density=True, density_regions=None):
    scale = min(1., target_height/height) if target_height else 1.
    H,W = gray.shape
    small = obs.resize(gray,(quantize(W*scale),quantize(H*scale))) if scale<1 else gray
    sx,sy = small.shape[1]/W,small.shape[0]/H
    h = height*sy
    # Inherited 8-bit texture floor: 8% of the representable grey range.
    # This is not illumination invariant and is NOT evidence of front ink.
    # Keep its measured behavior until a paper-relative replacement is audited.
    ink = obs.ink(small, quantize(4*h)|1, method="mean", threshold=255*.08, arithmetic="dn")
    n,labels,stats,centres = obs.components(ink)
    valid = ((stats[:,3]>.3*h)&(stats[:,3]<2.3*h)&(stats[:,2]<5*h)&(stats[:,4]>.035*h*h))
    valid[0]=False
    records=[]
    for i in np.flatnonzero(valid):
        x,y,w,hh,area=stats[i]
        records.append(dict(id=int(i),bbox=[float(x/sx),float(y/sy),float((x+w)/sx),float((y+hh)/sy)],
            centre=(centres[i]/[sx,sy]).tolist(),area=float(area/(sx*sy)),height_h=float(hh/h)))
    local=with_density and fast_filter and density_regions is not None
    body=valid[labels].astype(np.float32) if with_density and not local else None
    if not with_density:density=None
    elif fast_filter:
        ky=cv2.getGaussianKernel(2*int(4*.20*h+.5)+1,.20*h)
        kx=cv2.getGaussianKernel(2*int(4*.75*h+.5)+1,.75*h)
        if density_regions is None:
            density=cv2.sepFilter2D(body,cv2.CV_32F,kx,ky,borderType=cv2.BORDER_REFLECT)
        else:
            # Components are still measured on the whole native page. Only the
            # finite-support convolution is local. Each requested remap domain
            # gets the complete Gaussian halo; page edges keep REFLECT padding.
            density=np.zeros(labels.shape,np.float32);rx=len(kx)//2;ry=len(ky)//2
            for x0,y0,x1,y1 in density_regions:
                a=max(0,x0-rx);b=max(0,y0-ry);z=min(labels.shape[1],x1+rx);w=min(labels.shape[0],y1+ry)
                filtered=cv2.sepFilter2D(valid[labels[b:w,a:z]].astype(np.float32),cv2.CV_32F,kx,ky,borderType=cv2.BORDER_REFLECT)
                density[y0:y1,x0:x1]=filtered[y0-b:y1-b,x0-a:x1-a]
    else:density=gaussian_filter(body,(.20*h,.75*h))
    return dict(density=density,components=records,scale=[sx,sy],height=height,
                _centres=np.asarray([q['centre'] for q in records]).reshape(-1,2),
                _boxes=np.asarray([q['bbox'] for q in records]).reshape(-1,4),
                **({'labels': labels} if with_labels else {}))


def walk(signal, seed, step):
    """Anchored maximum-support path with a bounded physical slope."""
    ny,nx=signal.shape
    value=np.full(ny,-1e6,np.float32);value[seed]=0
    back=np.zeros((nx,ny),np.int16)
    shift=np.arange(-step,step+1)
    yy=np.arange(ny)
    for col in range(1,nx):
        previous=yy[None,:]-shift[:,None]
        legal=(previous>=0)&(previous<ny)
        candidates=np.where(legal,value[np.clip(previous,0,ny-1)]-.015*shift[:,None]**2,-1e6)
        which=np.argmax(candidates,axis=0)
        value=candidates[which,yy]+signal[:,col]
        back[col]=np.clip(previous[which,yy],0,ny-1)
    path=np.empty(nx,int);path[-1]=int(np.argmax(value))
    for col in range(nx-1,0,-1):path[col-1]=back[col,path[col]]
    return path


def follow_contacts(sample, xs, ys, offsets, anchor, seed, h, *, fast_fit=False,peak_cache=None):
    """Local ridge continuation with no reward for a different, distant row.

    Word gaps retain the last direction briefly. Long gaps stop observation;
    they do not become a bridge to another line or a new line proposal.
    """
    indices=np.full(len(xs),seed,int);observed=np.zeros(len(xs),bool)
    observed[anchor]=sample[seed,anchor]>.035
    for direction in (-1,1):
        history=[(xs[anchor],ys[anchor]+offsets[seed])]
        blank=0.
        for col in range(anchor+direction,len(xs) if direction==1 else -1,direction):
            previous=col-direction;dx=xs[col]-xs[previous]
            if len(history)>=4:
                hx,hy=np.asarray(history[-12:]).T
                centered=hx-hx.mean()
                slope=(float(np.dot(centered,hy-hy.mean())/np.dot(centered,centered))
                       if fast_fit else np.polyfit(centered,hy,1)[0])
                slope=float(np.clip(slope,-.65,.65))
            else:slope=0.
            expected=ys[previous]+offsets[indices[previous]]+slope*dx
            candidates=(find_peaks(sample[:,col])[0] if peak_cache is None else peak_cache[col])
            cy=ys[col]+offsets[candidates]
            possible=(abs(cy-expected)<.65*h)&(sample[candidates,col]>.035)
            candidates=candidates[possible]
            if len(candidates):
                errors=abs(ys[col]+offsets[candidates]-expected)/h
                # Closest body ridge wins; strength cannot buy a row switch.
                chosen=int(candidates[np.argmin(errors)])
                indices[col]=chosen;observed[col]=True;blank=0.
                history.append((xs[col],ys[col]+offsets[chosen]))
            else:
                indices[col]=int(np.argmin(abs(ys[col]+offsets-expected)))
                blank+=abs(dx)
                if blank>3*h:
                    remaining=np.arange(col,len(xs) if direction==1 else -1,direction)
                    indices[remaining]=indices[col]
                    break
    return indices,observed


def sample_grid(item,h,size):
    """One definition of the complete remap domain for tracing and its filter."""
    b=bbox(item);axis=line_axis(item);W,H=size
    extension=min(8*h,.25*(b[2]-b[0]))
    left=max(0,b[0]-extension);right=min(W-1,b[2]+extension)
    xs=np.linspace(left,right,max(3,quantize((right-left)/(.25*h))))
    offsets=np.linspace(-3.5*h,3.5*h,113)
    ys=axis[0]+axis[1]*xs
    return xs,ys,offsets


def trace(prepared,item,version=1,end_seeds=(),*,fast_fit=False):
    h=prepared['height'];sx,sy=prepared['scale'];density=prepared['density']
    b=bbox(item);axis=line_axis(item);W=density.shape[1]/sx;H=density.shape[0]/sy
    xs,ys,offsets=sample_grid(item,h,(W,H));left=xs[0];right=xs[-1]
    mx=np.broadcast_to(xs[None,:]*sx,(len(offsets),len(xs))).astype(np.float32)
    my=((ys[None,:]+offsets[:,None])*sy).astype(np.float32)
    sample=cv2.remap(density,mx,my,cv2.INTER_LINEAR)
    anchor=int(np.argmin(abs(xs-(b[0]+b[2])/2)))
    middle=abs(offsets)<.75*h
    if version>=5:
        central=(xs>b[0]+.3*(b[2]-b[0]))&(xs<b[0]+.7*(b[2]-b[0]))
        mass=sample[middle].max(0)
        anchor=int(np.argmax(np.where(central,mass,-1)))
    seed=int(np.argmax(np.where(middle,sample[:,anchor],-1)))
    objective=sample.copy()
    if version>=2:
        # A single anchor can switch rows at any word gap. The returned box
        # localizes an entire central body interval, while its ends may curl.
        fraction=(xs-b[0])/max(b[2]-b[0],1)
        core=np.clip(np.minimum(fraction,1-fraction)/.3,0,1)
        objective-=.18*(offsets[:,None]/h)**2*core[None,:]**3
        objective[(abs(offsets[:,None])>.75*h)&(core[None,:]>=.999)]=-1e6
    peak_cache=[find_peaks(sample[:,col])[0] for col in range(sample.shape[1])] if version>=4 else None
    observed=None
    if version>=3:
        indices,observed=follow_contacts(sample,xs,ys,offsets,anchor,seed,h,fast_fit=fast_fit,peak_cache=peak_cache)
    else:
        forward=walk(objective[:,anchor:],seed,4)
        backward=walk(objective[:,:anchor+1][:,::-1],seed,4)[::-1]
        indices=np.r_[backward[:-1],forward]
    alternatives=[]
    if version>=4:
        for end in end_seeds:
            ex,ey=end['point'];acol=int(np.argmin(abs(xs-ex)))
            eseed=int(np.argmin(abs(ys[acol]+offsets-ey)))
            if version>=5:
                near=abs(ys[acol]+offsets-ey)<.75*h
                eseed=int(np.argmax(np.where(near,sample[:,acol],-1)))
            other,seen=follow_contacts(sample,xs,ys,offsets,acol,eseed,h,fast_fit=fast_fit,peak_cache=peak_cache)
            common=observed&seen
            error=abs(offsets[indices]-offsets[other])/h
            # Need an extended shared ink interval, not one fortuitous crossing.
            overlap=float(common.sum()*(xs[1]-xs[0])/h)
            agreement=bool(overlap>=4 and np.quantile(error[common],.9)<.35)
            alternatives.append(dict(fragment=end['fragment'],path=np.c_[xs,ys+offsets[other]].tolist(),
                observed=seen.tolist(),overlap_h=overlap,agrees=agreement,
                error_p90_h=float(np.quantile(error[common],.9)) if common.any() else None))
            if agreement:
                use=seen&~observed;indices[use]=other[use];observed|=seen
    py=ys+offsets[indices]
    strength=sample[indices,np.arange(len(xs))]
    contacts=[]
    boxes=prepared.get('_boxes')
    if boxes is None:boxes=np.asarray([c['bbox'] for c in prepared['components']]).reshape(-1,4)
    centres=prepared.get('_centres')
    if centres is None:centres=np.asarray([c['centre'] for c in prepared['components']]).reshape(-1,2)
    ids=np.flatnonzero((boxes[:,2]>=left)&(boxes[:,0]<=right))
    distances=centres[ids,1]-np.interp(centres[ids,0],xs,py)
    for k in np.flatnonzero(abs(distances)<.8*h):
        contacts.append(dict(prepared['components'][int(ids[k])],distance_h=float(distances[k]/h)))
    support=strength>.035 if observed is None else observed
    return dict(path=np.c_[xs,py].tolist(),support=strength.tolist(),contacts=contacts,
        height=h,axis=axis.tolist(),bbox=b,source_kind='original component body support',
        observed=support.tolist(),supported_fraction=float(support.mean()),version=version,
        alternatives=alternatives,
        warning='Ink contacts may be accents, neighbors or verso; path is not a semantic baseline.')


def render_contacts(gray,items,route='slow',version=1,selected=None,*,fast_fit=True,field_cache=None,local_filter=False):
    t=perf_counter();h=height_proxy(items,(gray.shape[1],gray.shape[0]))
    regions=None
    if local_filter and route=='explicit_fast' and version>=6:
        regions=[]
        for i,q in enumerate(items):
            if selected is not None and i not in selected:continue
            if bbox(q)[2]-bbox(q)[0]<16*h:continue
            xs,ys,offsets=sample_grid(q,h,(gray.shape[1],gray.shape[0]))
            # float32 remap coordinates + bilinear neighbors need one extra cell.
            regions.append(roi([xs[0]-1,ys.min()+offsets[0]-1,xs[-1]+2,ys.max()+offsets[-1]+2],gray.shape))
    cached=(field_cache or {}).get('prepared')
    reuse=bool(cached is not None and field_cache.get('native_full') and field_cache['height']==h and field_cache['shape']==gray.shape and route=='explicit_fast' and version>=6)
    prepared=cached if reuse else prepare(gray,h,10 if route=='explicit_fast' and version<6 else None,
                     fast_filter=route=='explicit_fast' and version>=6,
                     with_labels=field_cache is not None,density_regions=regions)
    if field_cache is not None:field_cache.update(height=h,shape=gray.shape,prepared=prepared,native_full=reuse or regions is None)
    pairs=candidates(items,(gray.shape[1],gray.shape[0]))
    lines=[]
    for i,q in enumerate(items):
        if selected is not None and i not in selected:continue
        b=bbox(q)
        if b[2]-b[0]<16*h:continue
        endpoints=[]
        for pair in pairs['pairs']:
            if pair['line']!=i or (version<7 and pair['owners']!=1):continue
            f=bbox(items[pair['fragment']]);a,s=line_axis(items[pair['fragment']]);x=(f[0]+f[2])/2
            endpoints.append(dict(fragment=pair['fragment'],point=[x,float(a+s*x)]))
        lines.append(dict(trace(prepared,q,version,endpoints,fast_fit=fast_fit and route=='explicit_fast'),line=i))
    return dict(height=h,components=prepared['components'],lines=lines,
        seconds=perf_counter()-t,route=route,version=version,
        fragment_witness=dict(pairs,paths=[dict(q,path=hermite(items,q,h)) for q in pairs['pairs']]))
