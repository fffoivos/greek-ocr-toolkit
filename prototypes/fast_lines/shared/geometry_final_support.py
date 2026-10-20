"""Same-call native measurements and finite row paths for final export.
No component class or every-anchor fit veto precedes construction.
"""
import hashlib
import cv2
import numpy as np
from .geometry import roi,robust_fit
from .contracts import bbox
from .geometry_bands import crop_mask

def identity(item):
    data=np.asarray(item['polygon'],float).tobytes()+str(item.get('raster_edges','')).encode()+item.get('final_support_hash','').encode()+repr(tuple(item.get('source_ids',[]))).encode()
    receipt=item.get('_selected_pixel_support')
    if receipt:
        data+=np.asarray(receipt['points'],int).tobytes()+receipt['namespace'].encode()
    return hashlib.sha256(data).hexdigest()



def observe(gray,items,prepared,*,diagnostics=False):
    ink=prepared["ink"];h=prepared["height"];pv=np.polynomial.polynomial.polyval
    n,lab,st,ce=cv2.connectedComponentsWithStats(ink.astype(np.uint8),8)
    it=items;H,Wd=gray.shape;g=gray
    # baseline masks
    base=np.zeros((H,Wd),np.uint16);bm=[];hits=[]
    for q in it:
        a,b,c,d=roi(np.array(bbox(q))+[-1,-1,2,2],gray.shape)
        m=crop_mask((d-b,c-a),q,[a,b])>0;bm.append((a,b,c,d,m));base[b:d,a:c]+=m
        hits.append(np.bincount(lab[b:d,a:c][m],minlength=n))
    hits=np.array(hits)  # items x comps
    big=(st[:,2]>12*h)|(st[:,3]>3.5*h);big[0]=True
    # (a) centre path per item from its own mask ink
    P=[];L=[];X=[]
    for i,(a,b,c,d,m) in enumerate(bm):
        cols=np.flatnonzero(m.any(0))
        if len(cols)==0:P.append(None);L.append(np.nan);X.append((0,-1));continue
        yy=np.arange(m.shape[0])[:,None];top=np.where(m,yy,10**6).min(0)[cols];bot=np.where(m,yy,-1).max(0)[cols]
        Li=float(np.median(bot-top+1));mid=(top+bot)/2
        sel=m&ink[b:d,a:c]&~big[lab[b:d,a:c]];py,px=np.nonzero(sel)
        midx=np.full(m.shape[1],np.nan);midx[cols]=mid
        keep=np.abs(py-midx[px])<=.6*Li;py,px=py[keep],px[keep]
        w=max(4,int(h));bins=px//w;bx=[];by=[]
        for k in np.unique(bins):
            s=bins==k
            if s.sum()>=3:bx.append(px[s].mean());by.append(np.median(py[s]))
        if len(bx)>=2:
            deg=2 if (cols[-1]-cols[0])>15*h and len(bx)>=6 else 1
            coef=robust_fit(np.array(bx)+a,np.array(by)+b,deg)
        else: coef=np.array([b+np.median(mid),0.])
        P.append(coef);L.append(Li);X.append((a+cols[0],a+cols[-1]))
    L=np.array(L);Lg=np.nanmedian(L);L=np.clip(np.nan_to_num(L,nan=Lg),.6*Lg,1.6*Lg)
    def path(i,x):
        x=np.clip(x,X[i][0],X[i][1]);return pv(x,P[i])
    # ownership: claimants plus nearby paths; nearest centre path wins
    owner=np.full(n,-1);cx,cy=ce[:,0],ce[:,1]
    best=np.full(n,np.inf);second=np.full(n,np.inf)
    stable=sorted(range(len(it)),key=lambda i:(tuple(np.asarray(it[i]["polygon"]).ravel()),tuple(it[i].get("source_ids",[]))))
    for i in stable:
        if P[i] is None:continue
        dist=np.abs(cy-path(i,cx));inx=(cx>=X[i][0]-.3*L[i])&(cx<=X[i][1]+.3*L[i])
        cand=(hits[i]>0)|(inx&(dist<=.75*L[i]))
        eligible=cand&~big;better=eligible&(dist<best)
        second=np.where(better,best,np.where(eligible,np.minimum(second,dist),second))
        owner[better]=i;best[better]=dist[better]
    # Only nearly equal paths need an old-owner tie receipt, never a row veto.
    margin=np.full(n,np.inf);np.subtract(second,best,out=margin,where=np.isfinite(best));tied=(margin<1)&(owner>=0);full=hits==st[:,4][None,:];full[:,0]=False
    unique=full.sum(0)==1;old_owner=np.argmax(full,axis=0);owner[tied&unique]=old_owner[tied&unique]
    # Original selected-pixel witnesses establish component correspondence;
    # they are never IDs borrowed from another observation namespace.
    receipt_owner=np.full(n,-1);contested=np.zeros(n,bool)
    for i,q in enumerate(items):
        packet=q.get('_selected_pixel_support')
        if not packet:continue
        if packet['image'] is not gray or tuple(packet['shape'])!=gray.shape:raise ValueError('selected original support image/transform mismatch')
        points=np.asarray(packet['points'],int);ks=lab[points[:,1],points[:,0]];lo=np.full((n,2),np.inf);hi=np.full((n,2),-np.inf)
        np.minimum.at(lo,ks,points);np.maximum.at(hi,ks,points);pad=.15*packet['height']
        qualified=np.all(st[:,:2]>=lo-pad,axis=1)&np.all(st[:,:2]+st[:,2:4]-1<=hi+pad,axis=1);qualified[0]=False
        contested|=qualified&(receipt_owner>=0)&(receipt_owner!=i);receipt_owner[qualified]=i
    selected=(receipt_owner>=0)&~contested;owner[selected]=receipt_owner[selected]
    return dict(selected_receipt_owner=receipt_owner,selected_receipt_contested=contested,margins=margin,tied_unknown=np.flatnonzero(tied&~unique),labels=lab,stats=st,centres=ce,hits=hits,masks=bm,base=base,paths=P,line_heights=L,extents=X,owners=owner,big=big,distances=best)
