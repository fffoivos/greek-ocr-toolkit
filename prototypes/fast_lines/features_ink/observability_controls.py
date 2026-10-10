"""Controlled amplitude, stroke removal/filling and noise with fixed glyph cells."""
import cv2,numpy as np
from PIL import Image,ImageDraw
from ..shared.ink_observability import measure
from ..shared.timing import dump
from .study import DEST


def run(version=3):
    dest=DEST/'round4'/f'observability-controls-v{version}';dest.mkdir(parents=True,exist_ok=True)
    h=60;shape=np.zeros((110,100),np.uint8)
    cv2.rectangle(shape,(25,25),(34,85),1,-1)
    for y in (25,51,76):cv2.rectangle(shape,(25,y),(65,y+9),1,-1)
    other=shape.copy();other[76:86,35:66]=0
    noise=np.random.default_rng(40).normal(0,2.,shape.shape)
    records=[];panels=[]
    variants=[('original',shape,1.),('faint .15',shape,.15),('faint .03',shape,.03),('faint .01',shape,.01),('thinner',cv2.erode(shape,np.ones((3,3),np.uint8)),1.),('thicker',cv2.dilate(shape,np.ones((7,7),np.uint8)),1.),('lost bottom arm',other,1.)]
    blur=cv2.GaussianBlur(shape.astype(float),(0,0),2.);variants.append(('blur',blur,1.))
    for name,mask,amplitude in variants:
        image=np.uint8(np.clip(235-180*amplitude*mask+noise,0,255));rows={};tile=Image.new('RGB',(1400,220),'white');dr=ImageDraw.Draw(tile);dr.text((5,5),name+' | fixed cell, added noise unchanged; known E/F geometry only',fill='black')
        for j,route in enumerate(('slow','explicit','heuristic')):
            v=measure(image,[20,20,72,92],h,route=route,version=version,detail=True);rows[route]={k:x for k,x in v.items() if k not in ('raw','masks','certain','possible')}
            x=j*460;dr.text((x+5,30),f'{route} SNR{v["core_snr"]:.1f}; topology-stable {v["topology_stable"]}',fill='black')
            im=Image.fromarray(v['raw']).convert('RGB');im.thumbnail((110,140));tile.paste(im.resize((im.width*2,im.height*2)),(x+5,60))
            for k,b in enumerate(v['masks']):
                im=Image.fromarray(255-b*255).convert('RGB');im.thumbnail((70,140));tile.paste(im,(x+125+k*100,60))
            dr.text((x+5,200),v['faintness']+'; readability unknown',fill='black')
        # Two physically different letters become exactly identical after loss
        # of the distinguishing lower arm. No darkness threshold recovers it.
        rows['known_distinguishing_arm_present']=bool(np.sum(mask[76:86,35:66])>200)
        records.append(dict(name=name,measurements=rows));panels.append(tile)
    out=Image.new('RGB',(1400,220*len(panels)),'white')
    for i,p in enumerate(panels):out.paste(p,(0,i*220))
    out.save(dest/'controls.jpg',quality=95);dump(dest/'records.json',records)


if __name__=='__main__':run()
