"""Observed text columns for field computation and the opt-in bend route.

These regions restrict observations and detector reruns, never cut final text.
Printed-boundary and final native ownership operators still decide every edit.
"""
import cv2
import numpy as np

def columns(pm, boxes, size, h, rules=(), gray=None):
    """Repeated box x-clusters must have a measured white channel.

    A verified M13 rule is independently sufficient. The reduced pixel route
    avoids treating an overfilled detector box as evidence against whitespace.
    No horizontal cuts are introduced.
    """
    W,H=size
    if not len(boxes):return np.empty((0,4))
    b=np.asarray(boxes);wide=b[(b[:,2]-b[:,0]>6*h)&(b[:,3]-b[:,1]<4*h)]
    edges=[]
    channel=pm>.3;channel_sx=pm.shape[1]/W;channel_sy=pm.shape[0]/H
    if gray is not None:
        scale=min(1.,1200/max(W,H));raw=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
        paper=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((max(3,round(2*h*scale)|1),)*2,np.uint8))
        channel=cv2.threshold(cv2.subtract(paper,raw),0,1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        channel=cv2.morphologyEx(channel,cv2.MORPH_CLOSE,np.ones((max(1,round(h*scale/2)),)*2,np.uint8))
        channel_sx=raw.shape[1]/W;channel_sy=raw.shape[0]/H
    for r in rules:
        if r.get('accepted'):
            p=np.asarray(r['rule']['path']);edges.append(float(np.median(p[:,0])))
    if len(wide):
        left,right=wide[:,None,:],wide[None,:,:]
        ii,jj=np.nonzero((right[:,:,0]>=left[:,:,2])&(right[:,:,0]-left[:,:,2]<=6*h)&(right[:,:,1]<left[:,:,3])&(right[:,:,3]>left[:,:,1]))
        mid=(wide[ii,2]+wide[jj,0])/2
        for x in mid:
            near=abs(mid-x)<h
            if near.sum()<3:continue
            y0=np.min(np.maximum(wide[ii[near],1],wide[jj[near],1]));y1=np.max(np.minimum(wide[ii[near],3],wide[jj[near],3]))
            if y1-y0<12*h:continue
            sx0,sy0=channel_sx,channel_sy
            strip=channel[max(0,int(y0*sy0)):int(y1*sy0)+1,max(0,int((x-h)*sx0)):int((x+h)*sx0)+1]
            if strip.size:
                white=(strip==0).astype(np.uint8);_,lab=cv2.connectedComponents(white,8)
                if (set(lab[0])&set(lab[-1]))-{0}:edges.append(float(np.median(mid[near])))
    keep=[]
    for x in sorted(edges):
        if h<x<W-h and (not keep or x-keep[-1]>2*h):keep.append(x)
    return np.array([[a,0,b,H] for a,b in zip([0]+keep,keep+[W])],float)


