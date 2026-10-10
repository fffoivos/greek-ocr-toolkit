"""S9/X02: deterministic physical counterexamples, never accuracy labels."""
import cv2,numpy as np

def variants(gray,height,seed=20261010):
    h,w=gray.shape
    xs,ys=np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32))
    shift=.6*height*((xs/max(w-1,1))-.5)**2
    gap=np.zeros_like(gray,bool); gap[:,int(w*.49):int(w*.51)+1]=True
    faded=np.uint8(255-(255-gray)*.35); broken=gray.copy(); broken[gap]=255
    kernel=np.ones((max(1,round(.12*height)),)*2,np.uint8)
    blurred=cv2.GaussianBlur(gray,(0,0),max(.1,height*.08))
    thickened=cv2.erode(gray,kernel)
    delta=lambda changed: abs(changed.astype(np.int16)-gray.astype(np.int16))
    return dict(control=(gray.copy(),np.zeros_like(gray)),fade=(faded,abs(faded.astype(float)-gray)),
        blur=(blurred,delta(blurred)),
        break_strokes=(broken,gap.astype(np.uint8)*255),thicken=(thickened,delta(thickened)),
        curl=(cv2.remap(gray,xs,ys+shift,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=255),shift),
        shift=(cv2.warpAffine(gray,np.float32([[1,0,.5*height],[0,1,0]]),(w,h),borderValue=255),np.full_like(gray,.5*height,dtype=float)))
