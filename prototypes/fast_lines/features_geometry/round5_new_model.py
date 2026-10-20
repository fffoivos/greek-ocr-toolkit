import cv2,numpy as np
from time import perf_counter
from greekocr.pages import process_page,PageOptions
from prototypes.fast_lines.features_geometry.round5_data import rows,DEST
from prototypes.fast_lines.shared.timing import dump
from prototypes.fast_lines.features_geometry.reference import COLORS,line,save
from prototypes.fast_lines.shared.geometry import robust_fit
out=DEST/'new-model-guides';out.mkdir(exist_ok=True)
cv2.setNumThreads(1)
for row in rows():
 if row['group']!='new_curved':continue
 p=row['page'];dst=out/(p+'.json')
 if dst.exists():raise RuntimeError(dst)
 t=perf_counter();r=process_page(row['path'],options=PageOptions(discounted='drop'));seconds=perf_counter()-t;dump(dst,dict(lines=r.lines,seconds=seconds,source='greekocr.pages process_page; active only, not truth'))
 g=cv2.imread(row['path'],0)
 for feature in ['curvature','skew','separation']:
  im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
  for i,q in enumerate(r.lines):
   if q.get('discounted'):continue
   x=np.arange(q['x0'],q['x1']);y=(np.array(q['baseline'])+np.array(q['meanline']))/2
   if feature=='curvature':
    for k,c in COLORS.items():line(im,np.c_[x,np.array(q[k])][::max(1,int(q['xheight']/4))],c,1)
   elif feature=='skew':
    a,b=robust_fit(x,y);line(im,np.c_[x,a+b*x],(180,0,180),2);line(im,np.c_[x,y],(0,150,0),1)
   else:
    for end in [0,-1]:line(im,[[x[end],q['accent_top'][end]],[x[end],q['accent_bottom'][end]]],(0,150,0),2)
  save(out/(p+'.'+feature+'.jpg'),im,p+' | model '+feature)
 print(p,len(r.lines),seconds,flush=True)
