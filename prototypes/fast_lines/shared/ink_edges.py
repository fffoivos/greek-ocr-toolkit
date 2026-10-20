"""Cross-stroke transition profiles, measured independently of stroke width.

Normal rays may hit another stroke, so only locally monotone 20/80 transitions
are measured. This describes edge spread; it cannot establish front ownership.
"""
import cv2,numpy as np
from .geometry import roi,quantize


def profiles(gray,box,height,*,budget=128,samples=81,detail=False):
    x0,y0,x1,y1=roi(box,gray.shape);pad=quantize(.6*height)
    xa,ya,xb,yb=roi([x0-pad,y0-pad,x1+pad,y1+pad],gray.shape)
    raw=gray[ya:yb,xa:xb].astype(np.float32)
    if min(raw.shape)<3:return dict(edge_width_h=None,accepted=0,attempted=0)
    amplitude_floor=max(3.,.15*float(np.percentile(raw,90)-np.percentile(raw,10)))
    gx=cv2.Sobel(raw,cv2.CV_32F,1,0)/8;gy=cv2.Sobel(raw,cv2.CV_32F,0,1)/8;mag=cv2.magnitude(gx,gy)
    # Local maxima along either image axis nominate a physical transition.
    peaks=(mag>np.percentile(mag,90))&(mag>=cv2.dilate(mag,np.ones((3,3),np.uint8)))
    yy,xx=np.nonzero(peaks);valid=(xx>=x0-xa)&(xx<x1-xa)&(yy>=y0-ya)&(yy<y1-ya)
    xx,yy=xx[valid],yy[valid]
    if len(xx)>budget:
        ii=np.linspace(0,len(xx)-1,budget).astype(int);xx,yy=xx[ii],yy[ii]
    offsets=np.linspace(-.35*height,.35*height,samples,dtype=np.float32)
    rows=[];widths=[]
    for x,y in zip(xx,yy):
        norm=max(float(mag[y,x]),1e-6);ux,uy=float(gx[y,x]/norm),float(gy[y,x]/norm)
        sx=x+offsets*ux;sy=y+offsets*uy
        if sx.min()<0 or sy.min()<0 or sx.max()>=raw.shape[1]-1 or sy.max()>=raw.shape[0]-1:continue
        v=cv2.remap(raw,sx.astype(np.float32)[None],sy.astype(np.float32)[None],cv2.INTER_LINEAR)[0]
        mid=samples//2
        # The nearest local low/high straddling the maximum-gradient point.
        left=max(0,mid-samples//4)+int(np.argmin(v[max(0,mid-samples//4):mid+1]))
        right=mid+int(np.argmax(v[mid:min(samples,mid+samples//4+1)]))
        amplitude=float(v[right]-v[left])
        if amplitude<amplitude_floor or right-left<2:continue
        local=(v[left:right+1]-v[left])/amplitude
        if np.sum(np.maximum(0,-np.diff(local)))>.2:continue
        t20=np.flatnonzero(local>=.2);t80=np.flatnonzero(local>=.8)
        if not len(t20) or not len(t80):continue
        def crossing(level,index):
            if index==0:return float(offsets[left])
            fraction=(level-local[index-1])/max(float(local[index]-local[index-1]),1e-6)
            return float(offsets[left+index-1]+fraction*(offsets[1]-offsets[0]))
        width=(crossing(.8,t80[0])-crossing(.2,t20[0]))/height
        widths.append(width)
        if detail:rows.append(dict(point=[int(x+xa),int(y+ya)],normal=[ux,uy],offsets_h=(offsets/height).tolist(),gray=v.tolist(),edge_width_h=width,amplitude=amplitude))
    return dict(edge_width_h=float(np.median(widths)) if widths else None,
                edge_q90_h=float(np.percentile(widths,90)) if widths else None,
                accepted=len(widths),attempted=len(xx),profiles=rows,semantics='local edge spread, not ink width or source ownership')
