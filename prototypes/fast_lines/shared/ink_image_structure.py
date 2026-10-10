"""Extended original-ink edges and orientation texture, never a picture eraser."""
import cv2,numpy as np


def render(gray,height,*,route='slow',version=4):
    scale=1. if route=='slow' else min(1.,16/height) if route=='explicit' else min(1.,8/height)
    raw=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA) if scale<1 else gray
    h=height*scale;mask=np.zeros(raw.shape,np.uint8);segments=[];tiles=[]
    if route!='heuristic':
        detected=cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD).detect(raw)[0]
        if detected is not None:
            for x0,y0,x1,y1 in detected.reshape(-1,4):
                length=np.hypot(x1-x0,y1-y0)
                if length<2*h:continue
                # V2 keeps continuous native contrast support, eliminating fitted
                # lines across white gaps. Still not a text/image ownership test.
                n=max(3,round(length));xs=np.linspace(x0,x1,n);ys=np.linspace(y0,y1,n)
                nx=-(y1-y0)/length;ny=(x1-x0)/length;step=max(1,.08*h)
                samples=[]
                for off in (-step,0,step):samples.append(cv2.remap(raw,(xs+nx*off).astype('float32')[None],(ys+ny*off).astype('float32')[None],cv2.INTER_LINEAR)[0].astype(float))
                contrast=np.maximum(samples[0],samples[2])-samples[1]
                supported=float((contrast>3).mean())
                if version>=2 and supported<.6:continue
                p0=(int(x0),int(y0));p1=(int(x1),int(y1));cv2.line(mask,p0,p1,1,max(1,round(.1*h)))
                segments.append(dict(points=[[float(x0/scale),float(y0/scale)],[float(x1/scale),float(y1/scale)]],length_h=float(length/h),support=supported))
    else:
        gx=cv2.Sobel(raw,cv2.CV_32F,1,0);gy=cv2.Sobel(raw,cv2.CV_32F,0,1);mag=np.hypot(gx,gy);angle=np.mod(np.arctan2(gy,gx),np.pi)
        step=max(2,round(3*h))
        for y in range(0,raw.shape[0],step):
            for x in range(0,raw.shape[1],step):
                m=mag[y:y+step,x:x+step];a=angle[y:y+step,x:x+step];keep=m>max(12,float(np.percentile(m,75)))
                bins=np.histogram(a[keep],bins=np.linspace(0,np.pi,7),weights=m[keep])[0]
                mixed=sum(bins>.12*max(bins.sum(),1))>=3
                if mixed and keep.mean()>.15:mask[y:y+step,x:x+step][keep]=1;tiles.append([x/scale,y/scale,(x+step)/scale,(y+step)/scale])
    return dict(raw=raw,mask=mask,scale=scale,segments=segments,tiles=tiles,
                interpretation='extended edges or mixed orientations, including print and images',safe_exclusions=[])
