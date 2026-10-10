"""Batched R3 geometry witness: same samples, continuity and nomination thresholds.

This speeds arithmetic, not the feature definition. Per-line rendering and
dispatch equivalence are checked by features_geometry.scout_audit.
"""
from time import perf_counter
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from ..shared.geometry import height_proxy,line_axis
from ..shared.contracts import bbox
from ..shared.geometry_feature_paths import describe


def affine_batch(x,y,mask):
    """The four IRLS affine fits of robust_fit, batched over independent rows."""
    centre=(np.min(np.where(mask,x,np.inf),axis=1)+np.max(np.where(mask,x,-np.inf),axis=1))/2
    xx=x-centre[:,None];weights=mask.astype(float)
    for _ in range(4):
        w=weights**2;sw=w.sum(1);sx=(w*xx).sum(1);sy=(w*y).sum(1)
        sxx=(w*xx*xx).sum(1);sxy=(w*xx*y).sum(1)
        slope=(sxy-sx*sy/sw)/np.maximum(sxx-sx*sx/sw,1e-20)
        intercept=(sy-slope*sx)/sw
        residual=y-(intercept[:,None]+slope[:,None]*xx)
        median=np.nanmedian(np.where(mask,residual,np.nan),axis=1)
        scale=np.maximum(1e-6,1.4826*np.nanmedian(np.where(mask,abs(residual-median[:,None]),np.nan),axis=1))
        weights=np.where(mask,np.minimum(1,1.5*scale[:,None]/np.maximum(abs(residual),1e-6)),0)
    return intercept-slope*centre,slope


def sparse_fast(pm,items,size,version=3):
    if version!=3:raise ValueError('Only the validated R3 witness is implemented')
    start=perf_counter();h=height_proxy(items,size);W,H=size
    bounds=np.asarray([bbox(q) for q in items]).reshape(-1,4)
    axes=np.asarray([line_axis(q) for q in items]).reshape(-1,2)
    ids=np.flatnonzero((bounds[:,2]-bounds[:,0]>=12*h)&(bounds[:,3]-bounds[:,1]<=6*h))
    rows=[]
    if len(ids):
        b=bounds[ids];ax=axes[ids]
        x=b[:,0,None]+(b[:,2]-b[:,0])[:,None]*np.linspace(0,1,19)[None]
        y=ax[:,0,None]+ax[:,1,None]*x;o=np.linspace(-1.5*h,1.5*h,31)
        mx=np.broadcast_to((x*pm.shape[1]/W)[:,None,:],(len(ids),31,19)).reshape(-1,19).astype(np.float32)
        my=((y[:,None,:]+o[None,:,None])*pm.shape[0]/H).reshape(-1,19).astype(np.float32)
        a=cv2.remap(pm.astype(np.float32,copy=False),mx,my,cv2.INTER_LINEAR).reshape(len(ids),31,19)
        a=gaussian_filter1d(a,1,axis=1)
        k=np.argmax(a-.15*(o[None,:,None]/h)**2,axis=1)
        offsets=np.arange(31)[None,:]
        for direction in (-1,1):
            for col in range(9+direction,19 if direction==1 else -1,direction):
                previous=k[:,col-direction];delta=offsets-previous[:,None]
                local=a[:,:,col]-.03*delta**2
                k[:,col]=np.argmax(np.where(abs(delta)<=4,local,-1.e9),axis=1)
        values=np.take_along_axis(a,k[:,None,:],axis=1)[:,0];good=values>.3
        keep=good[:,4:-4].sum(1)>=6
        ids=ids[keep];x=x[keep];y=y[keep];a=a[keep];k=k[keep];values=values[keep];good=good[keep];ax=ax[keep]
        if len(ids):
            z=y+o[k];index=np.arange(31)[None,:,None]
            below=np.where((a<=.2)&(index<k[:,None,:]),index,-1).max(1)
            above=np.where((a<=.2)&(index>k[:,None,:]),index,31).min(1)
            widths=(above-below-1)*(o[1]-o[0])
            local_height=np.maximum(np.nanmedian(np.where(good[:,4:15],widths[:,4:15],np.nan),axis=1),H/pm.shape[0])
            xmin=np.min(np.where(good,x,np.inf),axis=1);xmax=np.max(np.where(good,x,-np.inf),axis=1)
            central=good&(x>=xmin[:,None]+.25*(xmax-xmin)[:,None])&(x<=xmin[:,None]+.75*(xmax-xmin)[:,None])
            central=np.where((central.sum(1)<3)[:,None],good,central)
            intercept,slope=affine_batch(x,z,central)
            fit=intercept[:,None]+slope[:,None]*x;residual=z-fit
            bend=np.zeros(len(ids))
            for ix in (np.arange(1,4),np.arange(15,18)):
                v=residual[:,ix]/local_height[:,None]
                valid=good[:,ix].all(1)&(v*v[:,0,None]>0).all(1)
                bend=np.maximum(bend,np.where(valid,abs(np.median(v,axis=1)),0))
            angles=np.degrees(np.arctan(slope))
            skew=abs(np.tan(np.radians(angles))-ax[:,1])*np.ptp(x,axis=1)/local_height
            for j,i in enumerate(ids):
                take=good[j]
                record=dict(line=int(i),path=np.c_[x[j,take],z[j,take]].tolist(),
                    affine=np.c_[x[j,take],fit[j,take]].tolist(),residual_h=(residual[j,take]/local_height[j]).tolist(),
                    bend_h=float(bend[j]),angle_deg=float(angles[j]),skew_error_h=float(skew[j]),
                    support=values[j].tolist(),local_height=float(local_height[j]),scale_kind='DB band',
                    box_angle_deg=float(np.degrees(np.arctan(ax[j,1]))))
                # Endpoint sign has a strict zero boundary. Replay the original
                # solver only when roundoff at one sample could admit a nonzero
                # endpoint median. No feature threshold or dispatch is relaxed.
                fragile=bool(abs(bend[j]-.3)<1e-8 or abs(skew[j]-.6)<1e-8)
                for ix in (np.arange(1,4),np.arange(15,18)):
                    v=residual[j,ix]/local_height[j]
                    fragile |= bool(good[j,ix].all() and np.min(abs(v))<1e-8 and abs(np.median(v))>1e-8)
                if fragile:
                    exact=describe(x[j,take],z[j,take],local_height[j])
                    residual_old=z[j]-np.interp(x[j],np.asarray(exact['affine'])[:,0],np.asarray(exact['affine'])[:,1])
                    endpoints=[]
                    for ix in (np.arange(1,4),np.arange(15,18)):
                        v=residual_old[ix]/local_height[j]
                        if good[j,ix].all() and np.all(v*v[0]>0):endpoints.append(abs(float(np.median(v))))
                    exact['bend_h']=max(endpoints+[0.])
                    record.update(exact)
                    record['skew_error_h']=float(abs(np.tan(np.radians(exact['angle_deg']))-ax[j,1])*np.ptp(x[j])/local_height[j])
                rows.append(record)
    nominations=[q['line'] for q in rows if q['bend_h']>.3 or q['skew_error_h']>.6]
    fragments=[]
    for i,b in enumerate(bounds):
        width=b[2]-b[0]
        if not 2*h<width<12*h or abs(axes[i,1])<.08:continue
        gap=np.maximum(bounds[:,0]-b[2],b[0]-bounds[:,2])
        near=abs((bounds[:,1]+bounds[:,3]-b[1]-b[3])/2)<2*h
        if np.any(near&(gap<2*h)&(gap>-.5*h)&((bounds[:,2]-bounds[:,0])>12*h)):fragments.append(i)
    return dict(height=h,lines=rows,nominated=nominations,fragments=fragments,
        trigger=bool(nominations or len(fragments)>=3),seconds=perf_counter()-start)
