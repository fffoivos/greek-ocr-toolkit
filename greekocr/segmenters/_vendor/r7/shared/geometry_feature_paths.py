"""Map-band geometry (route 1) and sparse probes (route 2).

Inputs are map, page dimensions and detector items. No page identity, old-model
geometry, corpus labels or reference artifacts enter this module. A map centre
is deliberately not a baseline. Lengths use the provisional detector body height.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from .geometry import height_proxy, line_axis, robust_fit, roi, quantize
from .contracts import bbox
from .paddle_db import DBPostProcess


def describe(x,y,h):
    x=np.asarray(x,float);y=np.asarray(y,float)
    central=(x>=x[0]+.25*np.ptp(x))&(x<=x[0]+.75*np.ptp(x))
    if central.sum()<3:central=np.ones(len(x),bool)
    a,b=robust_fit(x[central],y[central]); residual=y-(a+b*x)
    k=max(1,len(x)//5)
    bend=max(abs(float(np.median(residual[:k]))),abs(float(np.median(residual[-k:]))))/h
    return dict(path=np.c_[x,y].tolist(),affine=np.c_[x,a+b*x].tolist(),
                bend_h=bend,angle_deg=float(np.degrees(np.arctan(b))),
                residual_h=(residual/h).tolist())


def sparse(pm,items,size,version=1):
    """Batched 19 x 31 probes; inferred cost is measured by the harness."""
    start=perf_counter();h=height_proxy(items,size);W,H=size
    bounds=np.asarray([bbox(q) for q in items]).reshape(-1,4)
    ids=np.flatnonzero((bounds[:,2]-bounds[:,0]>=12*h)&(bounds[:,3]-bounds[:,1]<=6*h))
    rows=[]
    if len(ids):
        axes=np.asarray([line_axis(items[i]) for i in ids]);b=bounds[ids]
        x=b[:,0,None]+(b[:,2]-b[:,0])[:,None]*np.linspace(0,1,19)[None]
        y=axes[:,0,None]+axes[:,1,None]*x;o=np.linspace(-1.5*h,1.5*h,31)
        mx=np.broadcast_to((x*pm.shape[1]/W)[:,None,:],(len(ids),31,19)).reshape(-1,19).astype(np.float32)
        my=((y[:,None,:]+o[None,:,None])*pm.shape[0]/H).reshape(-1,19).astype(np.float32)
        a=cv2.remap(pm.astype(np.float32,copy=False),mx,my,cv2.INTER_LINEAR).reshape(len(ids),31,19)
        a=gaussian_filter1d(a,1,axis=1)
        k=np.argmax(a-.15*(o[None,:,None]/h)**2,axis=1)
        if version>=2:
            # Walk outward from the central stripe. Independent maxima can
            # jump an entire neighbouring row when one word is missing.
            for direction in (-1,1):
                for col in range(9+direction,19 if direction==1 else -1,direction):
                    previous=k[:,col-direction]
                    legal=abs(np.arange(31)[None,:]-previous[:,None])<=4
                    local=a[:,:,col]-.03*(np.arange(31)[None,:]-previous[:,None])**2
                    k[:,col]=np.argmax(np.where(legal,local,-1.e9),axis=1)
        values=np.take_along_axis(a,k[:,None,:],axis=1)[:,0]
        z=y+o[k]
        for j,i in enumerate(ids):
            good=values[j]>.3
            if good[4:-4].sum()<6:continue
            local_height=h
            if version>=3:
                widths=[]
                for col in range(4,15):
                    if not good[col]:continue
                    lo=hi=int(k[j,col])
                    while lo>0 and a[j,lo-1,col]>.2:lo-=1
                    while hi<30 and a[j,hi+1,col]>.2:hi+=1
                    widths.append((hi-lo+1)*(o[1]-o[0]))
                if widths:local_height=max(float(np.median(widths)),H/pm.shape[0])
            d=describe(x[j,good],z[j,good],local_height)
            if version>=2:
                # End witness needs contiguous support and consistent sign. A
                # lone stray peak is not a shared sheet deformation.
                residual=z[j]-np.interp(x[j],np.asarray(d['affine'])[:,0],np.asarray(d['affine'])[:,1])
                endpoints=[]
                for ix in (np.arange(1,4),np.arange(15,18)):
                    v=residual[ix]/local_height
                    if good[ix].all() and np.all(v*v[0]>0):endpoints.append(abs(float(np.median(v))))
                d['bend_h']=max(endpoints+[0.])
            d.update(line=int(i),support=values[j].tolist(),local_height=local_height,scale_kind='DB band' if version>=3 else 'box proxy',box_angle_deg=float(np.degrees(np.arctan(axes[j,1]))))
            d['skew_error_h']=abs(np.tan(np.radians(d['angle_deg']))-axes[j,1])*np.ptp(x[j])/local_height
            rows.append(d)
    nominations=[r['line'] for r in rows if r['bend_h']>.3 or r['skew_error_h']>.6]
    # Curled short fragments are visible evidence beyond a truncated long box.
    # They nominate a page only; they are never joined automatically.
    fragments=[]
    for i,q in enumerate(items):
        b=bounds[i];width=b[2]-b[0]
        if not 2*h<width<12*h or abs(line_axis(q)[1])<.08:continue
        gap=np.maximum(bounds[:,0]-b[2],b[0]-bounds[:,2])
        near=abs((bounds[:,1]+bounds[:,3]-b[1]-b[3])/2)<2*h
        if np.any(near&(gap<2*h)&(gap>-.5*h)&((bounds[:,2]-bounds[:,0])>12*h)):fragments.append(i)
    return dict(height=h,lines=rows,nominated=nominations,fragments=fragments,
                trigger=bool(nominations or len(fragments)>=3),seconds=perf_counter()-start)


def contour_owners(pm,size):
    """Reproduce pinned DB quad genealogy, without changing DB itself."""
    W,H=size;mh,mw=pm.shape;db=DBPostProcess();owners={}
    contours,_=cv2.findContours((pm>.2).astype(np.uint8),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours[:3000]:
        p,short=db.get_mini_boxes(contour)
        p=np.asarray(p)
        if short<db.min_size or db.box_score_fast(pm,p)<.45:continue
        expanded=db.unclip(p,1.4).reshape(-1,1,2)
        quad,short=db.get_mini_boxes(expanded)
        if short<db.min_size+2:continue
        quad=np.clip(np.rint(np.asarray(quad)*[W/mw,H/mh]),[0,0],[W,H]).astype(int)
        owners[tuple(quad.ravel())]=contour.reshape(-1,2)
    return owners


def bands(pm,items,size,version=2):
    """Explicit connected DB bands, retaining disconnected or multirow warnings."""
    start=perf_counter();W,H=size;mh,mw=pm.shape;h=height_proxy(items,size)
    n,labels,stats,_=cv2.connectedComponentsWithStats((pm>.2).astype(np.uint8),8)
    db=DBPostProcess();records=[];cache={}
    owners=contour_owners(pm,size) if version>=2 else {}
    for i,q in enumerate(items):
        b=bbox(q);ax=line_axis(q)
        xs=np.linspace(b[0]+.3*(b[2]-b[0]),b[0]+.7*(b[2]-b[0]),7)
        yy=ax[0]+ax[1]*xs
        xx=np.clip(np.rint(xs*mw/W).astype(int),0,mw-1)
        cy=np.clip(np.rint(yy*mh/H).astype(int),0,mh-1)
        # Select support nearest the middle of the box; wide bands remain
        # explicitly ambiguous if more than one source box chooses them.
        rad=quantize(h*mh/H)
        off=np.arange(-rad,rad+1);sy=np.clip(cy[None,:]+off[:,None],0,mh-1)
        v=pm[sy,xx[None,:]]-.1*(off[:,None]/max(1,rad))**2
        best=np.argmax(v,axis=0);ids=labels[sy[best,np.arange(7)],xx]
        ids=ids[ids>0]
        if not len(ids) and version<4:records.append(dict(line=i,status='no map band'));continue
        k=int(np.bincount(ids).argmax()) if len(ids) else 0
        if version>=2:
            contour=owners.get(tuple(np.rint(q['polygon']).astype(int).ravel()))
            if contour is None:
                records.append(dict(line=i,status='no exact contour genealogy'));continue
            labels_on_contour=labels[contour[:,1],contour[:,0]]
            labels_on_contour=labels_on_contour[labels_on_contour>0]
            if not len(labels_on_contour):
                records.append(dict(line=i,status='contour has no foreground'));continue
            k=int(np.bincount(labels_on_contour).argmax())
        if k not in cache:
            x,y,w,hh,area=map(int,stats[k]);local=(labels[y:y+hh,x:x+w]==k)
            weights=local*pm[y:y+hh,x:x+w];mass=weights.sum(0);valid=mass>0
            bx=np.arange(x,x+w)[valid]*W/mw
            by=(y+(weights*np.arange(hh)[:,None]).sum(0)[valid]/mass[valid])*H/mh
            by=gaussian_filter1d(by,max(.5,.6*h*mw/W))
            if len(bx)<3:cache[k]=dict(status='too short')
            else:
                central=local[:,w//4:max(w//4+1,3*w//4)]
                local_height=max(float(np.median(central.sum(0)))*H/mh,H/mh) if version>=3 else h
                d=describe(bx,by,local_height)
                d.update(local_height=local_height,scale_kind='DB band' if version>=3 else 'box proxy')
                transitions=np.sum(np.diff(np.pad(local.astype(np.int8),((1,1),(0,0))),axis=0)==1,axis=0)
                d['multi_run_fraction']=float(np.mean(transitions>1))
                contours,_=cv2.findContours(local.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                contour=max(contours,key=cv2.contourArea).reshape(-1,2)+[x,y]
                p=cv2.approxPolyDP(contour.astype(np.float32),.002*cv2.arcLength(contour.astype(np.float32),True),True).reshape(-1,2)
                expanded=db.unclip(p,1.4) if len(p)>=4 else []
                polygon=None
                if len(expanded)==1:
                    poly=np.asarray(expanded[0],float)*[W/mw,H/mh]
                    poly=np.clip(poly,[0,0],[W,H]);polygon=poly.tolist()
                d.update(status='measured map centre',polygon=polygon,band=k,source_bbox=[x*W/mw,y*H/mh,(x+w)*W/mw,(y+hh)*H/mh])
                cache[k]=d
        records.append(dict(cache[k],line=i))
    counts={}
    for r in records:
        if 'band' in r:counts[r['band']]=counts.get(r['band'],0)+1
    for r in records:
        if 'band' in r:r['source_boxes']=counts[r['band']]
    return dict(height=h,lines=records,seconds=perf_counter()-start)
