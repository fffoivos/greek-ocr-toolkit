"""Raw/after crops for every added line; no model reference or discounted line."""
import argparse,json
from pathlib import Path
import cv2,numpy as np
from ..round2 import manifest,ROOT
from ..shared.contracts import bbox
from ..shared.geometry import roi
from ..shared.review import save_image
from ..shared.timing import dump
from .__main__ import label


def run(directory):
    cells=[];ledger=[]
    for row in manifest()['pages']:
        e=json.loads((directory/(row['page']+'.evidence.json')).read_text())
        if not e.get('added'):continue
        gray=cv2.imread(str(ROOT/row['path']))
        for j,q in enumerate(e['added']):
            b=bbox(q);h=(b[3]-b[1])/2;x,y,z,w=roi([b[0]-h,b[1]-h,b[2]+h,b[3]+h],gray.shape)
            raw=gray[y:w,x:z];out=raw.copy()
            cv2.polylines(out,[np.rint(np.asarray(q['polygon'])-[x,y]).astype(np.int32)],True,(30,165,30),2)
            im=np.vstack([raw,out]);s=min(1.,1400/im.shape[1]);im=cv2.resize(im,None,fx=s,fy=s)
            canvas=np.full((im.shape[0],1400,3),255,np.uint8);canvas[:,:im.shape[1]]=im
            cells.append(label(canvas,row['page']+f' addition {j}: raw / after'))
            ledger.append(dict(page=row['page'],addition=j,board=(len(cells)-1)//3))
    for i in range(0,len(cells),3):save_image(directory/f'additions-{i//3:02d}.jpg',np.vstack(cells[i:i+3]))
    dump(directory/'addition-crops.json',ledger)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='final');a=ap.parse_args();run(ROOT/'.astra/fast_lines/out/stack'/a.version)
