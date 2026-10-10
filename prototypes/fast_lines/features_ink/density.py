"""Full-page optical depth without detector ownership, including unboxed ink."""
import argparse,cv2,numpy as np
from PIL import Image,ImageDraw
from ..round2 import manifest,get_baseline,ROOT
from ..shared.geometry import height_proxy,quantize
from ..shared.ink_photometry import tones
from ..shared.timing import dump
from ..shared.contracts import bbox
from .study import DEST,ANCHORS,triptych


def local_depth(gray,height,scale=1.):
    raw=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA) if scale<1 else gray
    h=height*scale;k=quantize(3*h)|1
    smooth=cv2.GaussianBlur(raw,(0,0),max(.5,.06*h))
    paper=cv2.morphologyEx(smooth,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8)).astype(np.float32)
    return raw,np.maximum(0,paper-raw)/np.maximum(paper,1)


def panel(raw,depth,strong,title):
    rgb=np.repeat(raw[:,:,None],3,axis=2)
    bright=raw[raw>=np.percentile(raw,75)].astype(float)
    noise=1.4826*float(np.median(abs(bright-np.median(bright))))/255
    visible=depth>max(3/255,3*noise,.10*strong)
    weak=visible&(depth<.5*strong)
    rgb[weak]=(0,175,205);rgb[visible&~weak]=(20,130,60)
    im=Image.fromarray(rgb);im=im.resize((650,round(im.height*650/im.width)))
    out=Image.new('RGB',(650,im.height+40),'white');out.paste(im,(0,40));ImageDraw.Draw(out).text((5,5),title,fill='black');return out,weak


def run(version='density-v2'):
    cv2.setNumThreads(1);dest=DEST/version;dest.mkdir(exist_ok=True)
    wanted=set(ANCHORS)|{'an-ef481610a820-p000150','s2-31f40cef90235c91b023-p00001','s2-77d1bd63d5babbe0df73-p00001','s2-200e977f2dab5291c42c-p00035'}
    for row in manifest()['pages']:
        if row['page'] not in wanted:continue
        p=row['page'];gray=cv2.imread(str(ROOT/row['path']),0);items=get_baseline(row);h=height_proxy(items,row['image_size'])
        strong=float(np.percentile([tones(gray,bbox(q))[1] for q in items],80))
        raw,dense=local_depth(gray,h);a,weak=panel(raw,dense,strong,'slow original-pixel local depth')
        raw,reduced=local_depth(gray,h,min(1.,16/h,1600/max(gray.shape)))
        b,rweak=panel(raw,reduced,strong,'R1 reduced local depth')
        paper=float(np.percentile(raw,90));global_depth=np.maximum(0,paper-raw)/max(paper,1)
        c,hweak=panel(raw,global_depth,strong,'R2 global-paper depth heuristic')
        triptych([a,b,c],dest/(p+'.jpg'))
        comparisons={}
        for name,m in [('route1',rweak),('route2',hweak)]:
            small=cv2.resize(weak.astype(np.uint8),(m.shape[1],m.shape[0]),interpolation=cv2.INTER_NEAREST)>0
            comparisons[name]=dict(intersection=int((small&m).sum()),union=int((small|m).sum()))
        dump(dest/(p+'.json'),dict(page=p,height=h,print_depth=strong,weak_support=comparisons,
            semantics='cyan weak contrast; green stronger contrast; neither is source ownership or readability',source='original image, no box support clipping'))
        print('depth',p,flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='density-v2');args=ap.parse_args();run(args.version)
