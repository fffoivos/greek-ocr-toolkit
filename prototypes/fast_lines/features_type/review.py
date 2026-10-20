"""Render review-only crop/contact boards from saved evidence; no inference."""
import json
import cv2,numpy as np
from ..shared.manifest import ROOT
from ..round2 import manifest
from ..shared.review import save_image
from .reference import DEST,label
from .lattice import draw

def lattice_boards():
    dest=ROOT/json.loads((DEST/'active-lattice.json').read_text())['directory'];rows={r['page']:r for r in manifest()['pages']};tiles=[];ledger=[]
    for f in sorted(dest.glob('*.json')):
        data=json.loads(f.read_text())
        if not isinstance(data,dict) or 'page' not in data:continue
        p=data['page'];g=cv2.imread(str(ROOT/rows[p]['path']),0);overlay=draw(g,data['slow'])
        for i,s in enumerate(data['slow']['slots']):
            h=s['height'];y=s['y'];a=max(0,int(s['x0']-h));b=min(g.shape[1],int(s['x1']+h));t=max(0,int(y-2*h));d=min(g.shape[0],int(y+2*h))
            im=np.vstack([cv2.cvtColor(g[t:d,a:b],cv2.COLOR_GRAY2BGR),overlay[t:d,a:b]]);sc=min(1.,1050/max(im.shape[1],1));im=cv2.resize(im,None,fx=sc,fy=sc)
            tile=label(im,p+f" slot {i} bodies {s['bodies']} contacts {s.get('contact_support')} supported {s['supported']}");tiles.append(tile);ledger.append(dict(page=p,slot=i,board=(len(tiles)-1)//6))
    for i in range(0,len(tiles),6):save_image(dest/f'slots-{i//6:02d}.jpg',np.vstack(tiles[i:i+6]))
    (dest/'slot-review-index.json').write_text(json.dumps(ledger))
    print(dest,len(tiles))

if __name__=='__main__':lattice_boards()
