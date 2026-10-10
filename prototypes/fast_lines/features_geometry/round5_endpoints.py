import json,cv2,numpy as np
from .round5_data import DEST,rows,load
from ..shared.geometry_envelopes import endpoint_pairs
from ..shared.timing import dump

def main():
 out=DEST/'endpoint-v1';out.mkdir(exist_ok=True)
 for row in rows():
  saved=DEST/'shape-corrections-v4'/(row['page']+'.json')
  if not saved.exists():continue
  d=json.load(open(saved));e=d.get('rendering')
  if not e:continue
  gray,o,pm=load(row);pairs=endpoint_pairs(o['items'],e);dump(out/(row['page']+'.json'),dict(pairs=pairs))
  if not pairs:continue
  im=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
  for pair in pairs:
   for k in ('line','fragment'):cv2.polylines(im,[np.rint(o['items'][pair[k]]['polygon']).astype(np.int32)],True,(180,0,180),2)
   for c in e['components']:
    if c['id'] in pair['components']:cv2.circle(im,tuple(np.rint(c['centre']).astype(int)),4,(0,180,0),-1)
  sc=min(1,1700/im.shape[1]);cv2.imwrite(str(out/(row['page']+'.jpg')),cv2.resize(im,None,fx=sc,fy=sc));print(row['page'],pairs,flush=True)
if __name__=='__main__':main()
