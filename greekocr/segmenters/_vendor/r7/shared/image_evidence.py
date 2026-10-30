"""S2: lazy native array primitives; lengths in a declared body-height proxy."""
from functools import cached_property
import cv2,numpy as np
from .geometry import quantize,roi

class ImageEvidence:
    def __init__(self,gray,height,long_side=1200):
        self.raw=gray; self.height=height; h,w=gray.shape
        scale=min(1.,long_side/max(h,w)); self.shape=(quantize(h*scale),quantize(w*scale))
        self.sx=self.shape[1]/w; self.sy=self.shape[0]/h
        self.body=height*self.sy
    @cached_property
    def gray(self): return cv2.resize(self.raw,(self.shape[1],self.shape[0]),interpolation=cv2.INTER_AREA)
    @cached_property
    def paper(self):
        k=quantize(3*self.body)|1
        return cv2.morphologyEx(self.gray,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k))).astype(np.float32)
    @cached_property
    def contrast(self): return np.maximum(0,(self.paper-self.gray)/np.maximum(self.paper,1))
    @cached_property
    def gradients(self):
        g=self.gray.astype(np.float32)/255
        return cv2.Sobel(g,cv2.CV_32F,1,0),cv2.Sobel(g,cv2.CV_32F,0,1)
    @cached_property
    def persistence(self):
        return sum((self.contrast>t).astype(np.uint8) for t in (.06,.12,.24))
    @cached_property
    def ink(self): return (self.persistence>0).astype(np.uint8)
    @cached_property
    def stroke(self): return stroke_features(self.ink)
    def crop(self,array,b):
        x0,y0,x1,y1=roi(np.asarray(b)*[self.sx,self.sy,self.sx,self.sy],array.shape)
        return array[y0:y1,x0:x1]

def components(binary):
    n,labels,stats,centres=cv2.connectedComponentsWithStats(binary.astype(np.uint8),8)
    return labels,stats[1:],centres[1:]

def runs(binary,length,vertical=False):
    k=(1,quantize(length)) if vertical else (quantize(length),1)
    return cv2.morphologyEx(binary.astype(np.uint8),cv2.MORPH_OPEN,np.ones((k[1],k[0]),np.uint8))

def stroke_features(binary):
    b=binary.astype(np.uint8); distance=cv2.distanceTransform(b,cv2.DIST_L2,5)
    # Morphological skeleton; bounded by actual maximum stroke depth, no per-pixel Python.
    sk=np.zeros_like(b); er=b.copy(); cross=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    while cv2.countNonZero(er):
        nex=cv2.erode(er,cross); opened=cv2.dilate(nex,cross); sk|=er-opened; er=nex
    neighbours=cv2.filter2D(sk,cv2.CV_16S,np.ones((3,3),np.int16))-sk
    endpoints=((sk>0)&(neighbours==1)).astype(np.uint8)
    cs,hierarchy=cv2.findContours(b,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    holes=sum(int(q[3]>=0) for q in hierarchy[0]) if hierarchy is not None else 0
    return dict(distance=distance,skeleton=sk,endpoints=endpoints,holes=holes)

def profile_features(contrast,gx,gy,persistence):
    ink=contrast>.06
    if not ink.any(): return dict(contrast=0.,edge=0.,persistence=0.,density=0.)
    c=float(np.median(contrast[ink])); edge=np.hypot(gx,gy)
    return dict(contrast=c,edge=float(np.mean(edge[ink])/max(c,1e-6)),
                persistence=float(np.mean(persistence[ink])/3),density=float(ink.mean()))
