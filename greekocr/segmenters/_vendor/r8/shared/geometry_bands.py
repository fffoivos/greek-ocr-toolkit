"""Finite smooth exports from already selected whole native components.

Pixel centres are integer page coordinates. Bands are x-monotone; shared
mathematical edges use top/left inclusive and bottom/right exclusive centres.
No membership selection or independent path fit occurs here.
"""
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d, minimum_filter1d, maximum_filter1d

EDGE_CONVENTION='pixel-centre-half-open-v1'
PADDING_H=.15
OUTER_RADIUS_H=.75
OUTER_SIGMA_H=.35
SEAM_RADIUS_H=.35
SEAM_SIGMA_H=.15
MAX_SLOPE=.5


def _slope_majorant(y):
    """Least sampled slope-limited upper bound; its negative is a lower bound."""
    axis=np.arange(len(y))*MAX_SLOPE
    return np.maximum(np.maximum.accumulate(y+axis)-axis,
                      np.maximum.accumulate((y-axis)[::-1])[::-1]+axis)


def extent(support):
    xs=np.flatnonzero(support.any(0))
    if not len(xs):return None
    yy=np.arange(support.shape[0])[:,None]
    return xs,np.where(support[:,xs],yy,support.shape[0]).min(0),np.where(support[:,xs],yy,-1).max(0)


def smooth_band(support, origin, corridor, h, *, path, fixed_top=None, fixed_bottom=None):
    """Widen selected ink around an existing finite density centre path.

    Bounds and origin use pixel centres in the support's own coordinate space.
    The corridor is that caller's already certified domain, never a detector.
    Fixed edges retain an unresolved external neighbour's exact legacy edge.
    """
    e=extent(support)
    if e is None:return None,'empty selected support'
    xx,top,bottom=e;pad=max(1,int(np.ceil(PADDING_H*h)))
    a=max(0,int(xx[0])-pad);c=min(support.shape[1],int(xx[-1])+pad+1)
    x=np.arange(a,c);p=np.asarray(path,float)
    if len(p)<2 or not np.isfinite(p).all() or np.any(np.diff(p[:,0])<=0):return None,'no finite existing centre path'
    centre=gaussian_filter1d(np.interp(x,p[:,0]-origin[0],p[:,1]-origin[1]),max(1,OUTER_SIGMA_H*h))
    anchor=np.interp(xx,x,centre)
    rise=np.interp(x,xx,top-anchor);drop=np.interp(x,xx,bottom-anchor)
    radius=max(1,round(OUTER_RADIUS_H*h));sigma=max(1,OUTER_SIGMA_H*h)
    lo=centre+gaussian_filter1d(minimum_filter1d(rise,2*radius+1),sigma)-PADDING_H*h-.5
    hi=centre+gaussian_filter1d(maximum_filter1d(drop,2*radius+1),sigma)+PADDING_H*h+.5
    # Smoothing must never pull an edge through a selected pixel. Shift the
    # smooth envelope as a whole rather than add per-letter corrective notches.
    lo-=max(0,float(np.max(lo[xx-a]-(top-.5))))
    hi+=max(0,float(np.max((bottom+.5)-hi[xx-a])))
    lo=-_slope_majorant(-lo);hi=_slope_majorant(hi)
    if fixed_top is not None:lo=np.interp(x,*fixed_top)
    if fixed_bottom is not None:hi=np.interp(x,*fixed_bottom)
    band=dict(x=x+origin[0],top=lo+origin[1],bottom=hi+origin[1],fixed_top=fixed_top is not None,fixed_bottom=fixed_bottom is not None,origin=list(origin))
    if corridor is not None:
        # Bound padding by the already supplied finite corridor. No clipped
        # selected mask is used as a certificate: the caller audits full labels.
        m=polygon_mask(support.shape,np.asarray(corridor)-origin)
        e=extent(m)
        if e is None:return None,'empty existing corridor'
        cx,ct,cb=e
        if xx[0]<cx[0] or xx[-1]>cx[-1]:return None,'selected support outside finite corridor'
        band['top']=np.maximum(band['top'],np.interp(x,cx,ct-.5)+origin[1])
        band['bottom']=np.minimum(band['bottom'],np.interp(x,cx,cb+.5)+origin[1])
    return band,None


def shared_separator(upper, lower, up_support, down_support, origin, h, domain):
    """One midpoint constrained by both rows' entire selected native support."""
    a,c=map(int,domain);xs=np.arange(a,c)
    if len(xs)<2:return None,'empty finite shared domain'
    ue=extent(up_support);de=extent(down_support)
    if ue is None or de is None:return None,'missing neighbour support'
    ux,_,ub=ue;dx,dt,_=de
    # Whole pixel edges; never certify just a clipped component mask.
    low=np.interp(xs-origin[0],ux,ub+.5)+origin[1]
    high=np.interp(xs-origin[0],dx,dt-.5)+origin[1]
    radius=max(1,round(SEAM_RADIUS_H*h))
    low=maximum_filter1d(low,2*radius+1);high=minimum_filter1d(high,2*radius+1)
    # Slope-constrained extremal closure: spread a protruding whole pixel's
    # clearance smoothly instead of re-clamping to a vertical letter notch.
    # This enforces the frozen slope; it does not relax it or fit a new curve.
    low=_slope_majorant(low);high=-_slope_majorant(-high)
    if np.any(low>high):return None,'no whole-component paper separator'
    seam=gaussian_filter1d((low+high)/2,max(1,SEAM_SIGMA_H*h))
    seam=np.maximum(low,np.minimum(high,seam))
    if np.max(abs(np.diff(seam)))>MAX_SLOPE:return None,'whole-component separator exceeds slope contract'
    simplified=cv2.approxPolyDP(np.c_[xs,seam].astype(np.float32),.25,False).reshape(-1,2).astype(float)
    trial=np.interp(xs,simplified[:,0],simplified[:,1])
    if np.all(trial>=low) and np.all(trial<=high) and np.max(abs(np.diff(trial)))<=MAX_SLOPE:
        seam=trial
    # Both sides consume exactly these vertices. No independent simplification
    # or rint phase can move one copy of the shared edge.
    for band,key in [(upper,'bottom'),(lower,'top')]:
        # Continue the same edge to this row's finite short-line end. The
        # common domain alone is tessellation evidence; no neighbour ownership
        # is invented beyond it. Constant end continuation avoids a vertical
        # spike where the shorter line disappears, as in _boundaries.
        band[key]=np.interp(band['x'],xs,seam)
    return np.c_[xs,seam],None


def band_polygon(band):
    x=band['x'];top=band['top'];bottom=band['bottom']
    if np.any(top>=bottom):return None,'empty/inverted band'
    for key in ['top','bottom']:
        if not band['fixed_'+key] and np.max(abs(np.diff(band[key])))>MAX_SLOPE:return None,'smooth boundary exceeds slope contract'
    # Dense vertices preserve a shared seam and its phase. Compress only exact
    # collinear runs; approximate simplification cannot silently cut a member.
    def compress(y):
        keep=np.r_[True,abs(np.diff(y,2))>1e-10,True]
        return np.c_[x[keep],y[keep]]
    t=compress(top);b=compress(bottom)
    polygon=np.vstack([[x[0]-.5,top[0]],t,[x[-1]+.5,top[-1]],[x[-1]+.5,bottom[-1]],b[::-1],[x[0]-.5,bottom[0]]])
    return polygon,None


def polygon_mask(shape, polygon, origin=(0,0), *, half_open=False):
    """Actual crop/audit raster; legacy inclusive fill or centre half-open band."""
    p=np.asarray(polygon,float)-origin;m=np.zeros(shape,np.uint8)
    if not half_open:
        cv2.fillPoly(m,[np.rint(p).astype(np.int32)],1);return m
    a=max(0,int(np.ceil(p[:,0].min())));c=min(shape[1],int(np.ceil(p[:,0].max())))
    if c<=a:return m
    # Evaluate in exported coordinates: translating each crop's vertices
    # before interpolation can flip an exact boundary centre through rounding.
    p=np.asarray(polygon,float);offset=np.asarray(origin,float)
    xs=np.arange(a,c)+offset[0];lo=np.full(len(xs),np.inf);hi=np.full(len(xs),-np.inf)
    # The exported band has two monotone chains. Interpolate these once rather
    # than test every edge against every column. Clipped legacy fragments can
    # use the generic scanline fallback below.
    p=np.roll(p,-int(np.argmin(p[:,0])),axis=0);right=int(np.argmax(p[:,0]))
    one=p[:right+1];two=np.vstack([p[right:],p[0]])[::-1]
    if np.all(np.diff(one[:,0])>=0) and np.all(np.diff(two[:,0])>=0):
        y1=np.interp(xs,one[:,0],one[:,1]);y2=np.interp(xs,two[:,0],two[:,1])
        lo=np.minimum(y1,y2);hi=np.maximum(y1,y2)
        ys=(np.arange(shape[0])+offset[1])[:,None];m[:,a:c]=((ys>=lo)&(ys<hi)).astype(np.uint8)
        return m
    # Even/odd scanline intervals preserve concavities in non-monotone
    # duplicate residues. Min/max intersections would silently fill the holes.
    for x in xs:
        cuts=[]
        for one,two in zip(p,np.roll(p,-1,axis=0)):
            left,right=sorted([one[0],two[0]])
            if left<=x<right:
                cuts.append(one[1]+(x-one[0])*(two[1]-one[1])/(two[0]-one[0]))
        cuts.sort()
        for low,high in zip(cuts[::2],cuts[1::2]):
            top=max(0,int(np.ceil(low-offset[1])));bottom=min(shape[0],int(np.ceil(high-offset[1])))
            m[top:bottom,int(x-offset[0])]=1
    return m


def crop_mask(shape,item,origin=(0,0)):
    if 'export_regions' in item:
        mask=np.zeros(shape,np.uint8)
        for region in item['export_regions']:mask|=crop_mask(shape,region,origin)
        if item.get('legacy_intervals'):
            legacy=crop_mask(shape,item['legacy_export'],origin)
            for a,c in item['legacy_intervals']:
                a=max(0,a-int(origin[0]));c=min(shape[1],c-int(origin[0]))
                if c>a:mask[:,a:c]=legacy[:,a:c]
        return mask
    return polygon_mask(shape,item['polygon'],origin,half_open=item.get('raster_edges')==EDGE_CONVENTION)


def _clearance(band,support,obstacles,origin,h):
    """One-sided obstacle bounds, preserving any already shared inner edge."""
    own=extent(support)
    if own is None:return 'empty whole support'
    x=band['x'];centre=(band['top']+band['bottom'])/2
    yy,xx=np.nonzero(obstacles)
    for side in ['top','bottom']:
        if band.get('shared_'+side):continue
        bound=np.full(len(x),-np.inf if side=='top' else np.inf)
        at=(xx+origin[0]>=x[0])&(xx+origin[0]<=x[-1])
        cx=xx[at]+origin[0];cy=yy[at]+origin[1];j=(cx-x[0]).astype(int)
        above=cy<np.interp(cx,x,centre)
        if side=='top':np.maximum.at(bound,j[above],cy[above]+.5)
        else:np.minimum.at(bound,j[~above],cy[~above]-.5)
        if side=='top':
            edge=np.maximum(band[side],bound);band[side]=_slope_majorant(edge)
        else:
            edge=np.minimum(band[side],bound);band[side]=-_slope_majorant(-edge)
    return None


def local_patch(item,original,ranges):
    """Override only these original-page x intervals, retaining true concavity."""
    merged=[]
    for a,c in sorted(ranges):
        if merged and a<=merged[-1][1]:merged[-1][1]=max(c,merged[-1][1])
        else:merged.append([a,c])
    item['legacy_intervals']=merged
    item['legacy_export']={k:original[k] for k in ['polygon','raster_edges','export_regions','legacy_intervals','legacy_export'] if k in original}
    item['polygon']=cv2.convexHull(np.vstack([item['polygon'],original['polygon']]).astype(np.float32)).reshape(-1,2).astype(float).tolist()


def tessellate(gray,items,*,prepared=None,columns=None,excluded=(),refresh=None,diagnostics=False):
    """Construct final rows first from their finite ink paths and shared seams."""
    from time import perf_counter
    import hashlib
    from .stack_ownership import prepare
    from .geometry_final_support import observe
    start=perf_counter();build=not prepared
    if build:prepared=prepare(gray,items)
    if prepared['image'] is not gray or prepared['shape']!=gray.shape or prepared['scale']!=1. or prepared['threshold']!=.08:raise ValueError('final export native observation contract mismatch')
    D=observe(gray,items,prepared,diagnostics=diagnostics);observed=perf_counter()
    lab,st,ce,owner=D['labels'],D['stats'],D['centres'],D['owners'];P,X,L=D['paths'],D['extents'],D['line_heights'];it=items;H,Wd=gray.shape;h=prepared['height'];PAD_H=.3;TIGHT=1.8
    pv=np.polynomial.polynomial.polyval
    def path(i,x):return pv(np.clip(x,X[i][0],X[i][1]),P[i])
    protected=set()
    from .geometry import roi
    from .contracts import bbox
    for q in excluded:
        a,b,c,d=roi(np.array(bbox(q))+[-1,-1,2,2],gray.shape);m=crop_mask((d-b,c-a),q,[a,b])>0;protected.update(map(int,np.unique(lab[b:d,a:c][m])))
    for r in (columns or {}).get('rules',[]):
        rule=r.get('rule',r);p=np.array(rule.get('path',[]),float)
        if p.ndim!=2 or len(p)<2:continue
        yy=np.arange(max(0,int(p[:,1].min())),min(H,int(p[:,1].max())+1));xx=np.rint(np.interp(yy,p[:,1],p[:,0])).astype(int);good=(xx>=0)&(xx<Wd);protected.update(map(int,lab[yy[good],xx[good]]))
    protected.discard(0)
    if protected:owner[list(protected)]=-1
    # own pixel profiles
    ys,xs=np.nonzero(lab);ow=owner[lab[ys,xs]];ok=ow>=0
    otop=np.full((len(it),Wd),np.inf);obot=np.full((len(it),Wd),-np.inf)
    np.minimum.at(otop,(ow[ok],xs[ok]),ys[ok]);np.maximum.at(obot,(ow[ok],xs[ok]),ys[ok])
    E={}
    for i in range(len(it)):
        c=np.flatnonzero(np.isfinite(otop[i]))
        if len(c):E[i]=[c[0]-int(.3*L[i]),c[-1]+int(.3*L[i]),c[0],c[-1]]
    # same-row trimming / duplicate conflicts
    dup_conf=[]
    keys=sorted(E)
    for i in keys:
        for j in keys:
            if j<=i:continue
            lo=max(E[i][0],E[j][0]);hi=min(E[i][1],E[j][1])
            if hi<lo:continue
            xm=(lo+hi)/2
            if abs(path(i,xm)-path(j,xm))<.5*max(L[i],L[j]):
                if E[i][3]<E[j][2]:bx=(E[i][3]+E[j][2])/2;E[i][1]=min(E[i][1],int(np.floor(bx)));E[j][0]=max(E[j][0],int(np.floor(bx))+1)
                elif E[j][3]<E[i][2]:bx=(E[j][3]+E[i][2])/2;E[j][1]=min(E[j][1],int(np.floor(bx)));E[i][0]=max(E[i][0],int(np.floor(bx))+1)
                else:dup_conf.append((i,j))
    # bands
    top={i:np.full(E[i][1]-E[i][0]+1,np.nan) for i in E};bot={i:np.full(E[i][1]-E[i][0]+1,np.nan) for i in E}
    pairs={};loose={}
    act=[[] for _ in range(Wd)]
    for i,(l,r,_,_) in E.items():
        for x in range(max(0,l),min(Wd-1,r)+1):act[x].append(i)
    samerow=0
    for x in range(Wd):
        A=act[x]
        if len(A)<2:continue
        ps=sorted(((path(i,x),i) for i in A),key=lambda v:(v[0],tuple(np.asarray(it[v[1]]["polygon"]).ravel()),tuple(it[v[1]].get("source_ids",[]))))
        for (pu,u),(pl,l) in zip(ps,ps[1:]):
            dmax=max(L[u],L[l])
            if pl-pu<.5*dmax:samerow+=1;continue
            (pairs if pl-pu<=TIGHT*dmax else loose).setdefault((u,l),[]).append(x)
    R=max(1,round(.35*h));interlock=0;exceptions=[]
    for (u,l),xs_ in pairs.items():
        xs_=np.array(xs_)
        for run in np.split(xs_,np.flatnonzero(np.diff(xs_)>1)+1):
            pu=path(u,run);pl=path(l,run);mid=(pu+pl)/2
            low=np.where(np.isfinite(obot[u,run]),obot[u,run]+.5,pu);high=np.where(np.isfinite(otop[l,run]),otop[l,run]-.5,pl)
            low=np.maximum(low,pu);high=np.minimum(high,pl)
            low=maximum_filter1d(low,2*R+1);high=minimum_filter1d(high,2*R+1)
            low=_slope_majorant(low);high=-_slope_majorant(-high)
            bad=low>high;interlock+=int(bad.sum())
            # No averaging crossing constraints into a glyph. Keep the nominal
            # midpoint provisionally and restore only the infeasible columns.
            if bad.any():exceptions.append(dict(kind='infeasible whole-component seam',rows=[u,l],interval=[int(run[bad][0]),int(run[bad][-1])+1]))
            low=np.where(bad,-np.inf,low);high=np.where(bad,np.inf,high)
            seam=gaussian_filter1d(np.clip(mid,low,high),max(1,.35*h));seam=np.clip(seam,low,high)
            top[l][run-E[l][0]]=seam;bot[u][run-E[u][0]]=seam
    caps_top={i:np.full(len(top[i]),-np.inf) for i in E};caps_bot={i:np.full(len(bot[i]),np.inf) for i in E}
    for (u,l),xs_ in loose.items():
        xs_=np.array(xs_);mid=(path(u,xs_)+path(l,xs_))/2
        caps_bot[u][xs_-E[u][0]]=np.minimum(caps_bot[u][xs_-E[u][0]],mid);caps_top[l][xs_-E[l][0]]=np.maximum(caps_top[l][xs_-E[l][0]],mid)
    Rr=max(1,round(.75*h));pad=PAD_H*h
    for i in E:
        x=np.arange(E[i][0],E[i][1]+1);xc=np.clip(x,0,Wd-1);pc=path(i,x)
        tt=otop[i,xc];bb=obot[i,xc];f=np.isfinite(tt)
        if f.sum()==0:continue
        tt=np.where(f,tt,np.interp(x,x[f],tt[f]));bb=np.where(f,bb,np.interp(x,x[f],bb[f]))
        ot_=gaussian_filter1d(minimum_filter1d(tt,2*Rr+1),max(1,.35*h))-pad-.5;ob_=gaussian_filter1d(maximum_filter1d(bb,2*Rr+1),max(1,.35*h))+pad+.5
        ot_-=max(0,float(np.max((ot_-(tt-.5))[f])));ob_+=max(0,float(np.max(((bb+.5)-ob_)[f])))
        ot_=-_slope_majorant(-ot_);ob_=_slope_majorant(ob_)
        ot_=np.maximum(ot_,caps_top[i]);ob_=np.minimum(ob_,caps_bot[i])
        # Whole-profile outer clearance, never move an already shared edge.
        other_top=np.full(len(x),-np.inf);other_bottom=np.full(len(x),np.inf)
        ya=max(0,int(np.floor(np.min(ot_))));yb=min(H,int(np.ceil(np.max(ob_)))+1)
        nearby=lab[ya:yb,np.clip(x,0,Wd-1)]
        oy,ox=np.nonzero((nearby>0)&(owner[nearby]!=i));oy=oy+ya
        above=oy<pc[ox];np.maximum.at(other_top,ox[above],oy[above]+.5);np.minimum.at(other_bottom,ox[~above],oy[~above]-.5)
        free_top=_slope_majorant(np.maximum(ot_,other_top));free_bottom=-_slope_majorant(-np.minimum(ob_,other_bottom))
        infeasible=f&((free_top>tt-.5)|(free_bottom<bb+.5))
        if infeasible.any():
            for run in np.split(np.flatnonzero(infeasible),np.flatnonzero(np.diff(np.flatnonzero(infeasible))>1)+1):
                exceptions.append(dict(kind='outer clearance/whole support conflict',rows=[i],interval=[int(x[run[0]]),int(x[run[-1]])+1]))
        # Keep the smooth nomination; incompatible columns use the local legacy
        # operation below instead of per-letter corrective notches.
        ot_=np.where(infeasible,ot_,free_top);ob_=np.where(infeasible,ob_,free_bottom)
        top[i]=np.where(np.isnan(top[i]),ot_,top[i]);bot[i]=np.where(np.isnan(bot[i]),ob_,bot[i])
    out=list(items);seams=[]
    for (u,l),xs_ in pairs.items():
        for run in np.split(np.array(xs_),np.flatnonzero(np.diff(xs_)>1)+1):
            seams.append(dict(rows=[u,l],domain_x=[int(run[0]),int(run[-1])+1],path=np.c_[run,bot[u][run-E[u][0]]].tolist()))
    for i in range(len(items)):
        regions=[]
        if i in E:
            x=np.arange(E[i][0],E[i][1]+1);valid=np.isfinite(top[i])&np.isfinite(bot[i])&(top[i]<bot[i]);at=np.flatnonzero(valid)
            if len(at):
                for run in np.split(at,np.flatnonzero(np.diff(at)>1)+1):
                    if len(run)==1:
                        p=np.array([[x[run[0]]-.5,top[i][run[0]]],[x[run[0]]+.5,top[i][run[0]]],[x[run[0]]+.5,bot[i][run[0]]],[x[run[0]]-.5,bot[i][run[0]]]])
                    else:p,_=band_polygon(dict(x=x[run],top=top[i][run],bottom=bot[i][run],fixed_top=True,fixed_bottom=True))
                    regions.append(dict(polygon=p.tolist(),raster_edges=EDGE_CONVENTION))
        if i not in E:
            regions=[{k:items[i][k] for k in ['polygon','raster_edges','export_regions','legacy_intervals','legacy_export'] if k in items[i]}]
            exceptions.append(dict(kind='no owned native support; finite legacy item',rows=[i],interval=[int(np.floor(np.asarray(items[i]['polygon'])[:,0].min())),int(np.ceil(np.asarray(items[i]['polygon'])[:,0].max()))+1]))
        q=dict(items[i],export_regions=regions,raster_edges=EDGE_CONVENTION,final_band=i in E)
        if regions:q['polygon']=cv2.convexHull(np.vstack([r['polygon'] for r in regions]).astype(np.float32)).reshape(-1,2).astype(float).tolist()
        q['final_support_hash']=hashlib.sha256(np.flatnonzero(owner==i).astype(np.int32).tobytes()).hexdigest()
        out[i]=q
    # Local legacy operations are x-intervals, not connected row transactions.
    from .contracts import bbox
    from .geometry import roi
    def legacy(rows,a,c,kind,component=None):
        a=max(0,int(a)-2);c=min(Wd,int(c)+2)
        if c<=a:return
        exceptions.append(dict(kind=kind,rows=sorted(set(map(int,rows))),interval=[a,c],component=None if component is None else int(component)))
    # Oversized/unassigned and near-equal support stays visible, including rules.
    for k in np.flatnonzero(((owner<0)&(D['hits'].sum(0)>0))|np.isin(np.arange(len(st)),D['tied_unknown'])):
        if not k:continue
        x,y,w,v,_=st[k];legacy(np.flatnonzero(D['hits'][:,k]),x,x+w,'unassigned/near-equal legacy component',k)
    # Reconcile already dealt with exact duplicates. Remaining mixed/same-row
    # hypotheses are not treated as vertical neighbours; retain conflicts only.
    for i,j in dup_conf:
        common=(D['hits'][i]>0)&(D['hits'][j]>0);ks=np.flatnonzero(common);ks=ks[ks>0]
        for k in ks:
            x,y,w,v,_=st[k];legacy([i,j],x,x+w,'same-row or mixed support',k)
    # Actual exported masks, grouped whole-component counts. A component that
    # was whole before may not become a newly cut interlock or endpoint.
    native_count=np.zeros(gray.shape,np.uint16);native_hits=np.zeros_like(D['hits']);mask_cache={}
    def measure(qs):
        for i,q in enumerate(qs):
            bounds=roi(np.array(bbox(q))+[-1,-1,2,2],gray.shape);key=(bounds,tuple(map(tuple,q.get('legacy_intervals',[]))))
            previous=mask_cache.get(i)
            if previous is not None and previous[0]==key:continue
            if previous is not None:
                a,b,c,d=previous[1];native_count[b:d,a:c]-=previous[2]
            a,b,c,d=bounds;m=crop_mask((d-b,c-a),q,[a,b])>0
            native_count[b:d,a:c]+=m;native_hits[i]=np.bincount(lab[b:d,a:c][m],minlength=len(st));mask_cache[i]=(key,bounds,m)
        return native_count,native_hits
    raw_count,raw_hits=measure(out)
    old_whole=(D['hits']==st[:,4][None,:]).any(0);new_whole=(raw_hits==st[:,4][None,:]).any(0)
    for k in np.flatnonzero(old_whole&~new_whole):
        if not k:continue
        x,y,w,v,_=st[k];legacy(np.flatnonzero((D['hits'][:,k]>0)|(raw_hits[:,k]>0)),x,x+w,'newly cut whole component',k)
    for k in np.flatnonzero((D['hits'].sum(0)==0)&(raw_hits.sum(0)>0)&(D['selected_receipt_owner']<0)):
        if not k:continue
        x,y,w,v,_=st[k];legacy(np.flatnonzero(raw_hits[:,k]),x,x+w,'outside accepted content lacks source receipt',k)
    lost=(D['base']>0)&(raw_count==0)&prepared['ink']
    for k in np.unique(lab[lost]):
        if not k:continue
        x,y,w,v,_=st[k];legacy(np.flatnonzero((D['hits'][:,k]>0)|(raw_hits[:,k]>0)),x,x+w,'accepted native union loss',k)
    # Explicit R/B original-pixel witnesses remain separate from relative IDs.
    for i,q in enumerate(items):
        receipt=q.get('_selected_pixel_support')
        if not receipt:continue
        pts=np.asarray(receipt['points'],int);a,b,c,d=roi(np.array(bbox(out[i]))+[-1,-1,2,2],gray.shape);m=crop_mask((d-b,c-a),out[i],[a,b]);inside=(pts[:,0]>=a)&(pts[:,0]<c)&(pts[:,1]>=b)&(pts[:,1]<d);kept=np.zeros(len(pts),bool);kept[inside]=m[pts[inside,1]-b,pts[inside,0]-a]>0
        if not kept.all():
            for x in np.unique(pts[~kept,0]):legacy([i],x,x+1,'original R/B selected pixel',None)
    intervals={i:[] for i in range(len(items))}
    def apply():
        for event in exceptions:
            for i in event['rows']:intervals[i].append(event['interval'])
        for i,ranges in intervals.items():
            if not ranges:continue
            local_patch(out[i],items[i],ranges)
    apply()
    # Changes are measured on content, not the new envelope/background ROI.
    final_count,final_hits=measure(out);changed=np.flatnonzero(np.any(final_hits[:,1:]!=D['hits'][:,1:],axis=1)).tolist();refresh_records=[]
    if changed and refresh is not None:
        content=[]
        for i,q in enumerate(out):
            ks=np.flatnonzero(final_hits[i]>0);ks=ks[ks>0]
            if len(ks):
                boxes=st[ks];a,b=boxes[:,:2].min(0);c,d=(boxes[:,:2]+boxes[:,2:4]).max(0);polygon=[[int(a),int(b)],[int(c),int(b)],[int(c),int(d)],[int(a),int(d)]]
            else:polygon=items[i]['polygon']
            new_ids=ks[(D['hits'][:,ks].sum(0)==0)]
            content.append(dict(items[i],polygon=polygon,final_support_hash=hashlib.sha256(final_hits[i,1:].astype(np.int32).tobytes()).hexdigest(),_content_change=dict(new_observed_components=new_ids.tolist(),content_ids=ks.tolist())))
        receipt=refresh(content,changed);refresh_records.append(receipt)
        from .geometry_final_support import identity
        if receipt.get('input_identities')!={str(i):identity(content[i]) for i in changed}:raise ValueError('stale final decision refresh input')
        for i in receipt.get('refused_indices',[]):
            ks=np.flatnonzero((final_hits[i]>0)!=(D['hits'][i]>0));ks=ks[ks>0]
            for k in ks:
                x,y,w,v,_=st[k];legacy(np.flatnonzero((D['hits'][:,k]>0)|(final_hits[:,k]>0)),x,x+w,'changed content decision unresolved',k)
        apply()
    # Close patch joins on native component support, never rerun classifiers.
    repair_pass=0
    while True:
        count,hits=measure(out);whole=(hits==st[:,4][None,:]).any(0)
        unseen=D['hits'].sum(0)==0
        bad=(old_whole|((hits.sum(0)>0)&unseen))&~whole;bad[0]=False
        missing=(D['base']>0)&(count==0)&prepared['ink'];bad[np.unique(lab[missing])]=True;bad[0]=False
        ks=np.flatnonzero(bad)
        if not len(ks):break
        for k in ks:
            x,y,w,v,_=st[k];rows=np.flatnonzero((D['hits'][:,k]>0)|(hits[:,k]>0));legacy(rows,x,x+w,'patch-join whole/native closure',k)
        before_intervals=tuple(tuple(map(tuple,q.get('legacy_intervals',[]))) for q in out)
        apply();repair_pass+=1
        after_intervals=tuple(tuple(map(tuple,q.get('legacy_intervals',[]))) for q in out)
        if before_intervals==after_intervals:break
    final_count,final_hits=measure(out)
    native_lost=int(((D['base']>0)&(final_count==0)&prepared['ink']).sum())
    native_new_cut=np.flatnonzero((old_whole|((D['hits'].sum(0)==0)&(final_hits.sum(0)>0)))&~(final_hits==st[:,4][None,:]).any(0));native_new_cut=native_new_cut[native_new_cut>0]
    for i,q in enumerate(out):
        q['final_support_hash']=hashlib.sha256(final_hits[i,1:].astype(np.int32).tobytes()).hexdigest()
        q['final_export_hash']=hashlib.sha256(repr((q['export_regions'],q.get('legacy_intervals',[]),q.get('legacy_export'))).encode()).hexdigest()
    post_decision_changed=[]
    if refresh_records:
        for i in changed:
            if content[i]['final_support_hash']!=out[i]['final_support_hash']:post_decision_changed.append(i)
        # Proposal calibration is not misrepresented as a refreshed final pool.
        # Affected intervals carry incoming evidence; the unresolved dependency
        # stays explicit rather than triggering another batch or classifier loop.
    elapsed=perf_counter()-start
    return dict(items=out,considered=len(items),migrated=list(range(len(items))),pairs=seams,paths=[p.tolist() if p is not None else None for p in P],path_extents=X,line_heights=L.tolist(),same_row=dup_conf,interlock_columns=interlock,exceptions=exceptions,content_refresh=refresh_records,refresh=refresh_records,local_closure_passes=repair_pass,post_decision_content_changed=post_decision_changed,final_calibration_qualified=not bool(post_decision_changed),changed_content=changed,native_lost=native_lost,newly_cut_components=native_new_cut.tolist(),preparation=dict(reused=not build,builds=int(build),labels_builds=1,height=h,scale=1,threshold=.08,kernel=prepared['paper_kernel']),stages=dict(observe_s=observed-start,construction_s=elapsed-(observed-start)),seconds=elapsed)
