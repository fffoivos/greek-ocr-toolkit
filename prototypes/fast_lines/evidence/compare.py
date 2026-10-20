"""Version comparison: exact polygons and raw/before/after crops for every change."""
import argparse,json
from pathlib import Path
import cv2,numpy as np
from ..round2 import manifest,ROOT
from ..shared.contracts import bbox
from ..shared.geometry import roi
from ..shared.review import save_image
from ..shared.timing import dump
from .__main__ import label,cohort


def compare(previous,directory):
    records=[];boards=[]
    for row in cohort(directory.name):
        if not (previous/(row['page']+'.json')).exists():continue
        page=row['page'];old=json.loads((previous/(page+'.json')).read_text())['items'];new=json.loads((directory/(page+'.json')).read_text())['items']
        key=lambda q:json.dumps(q['polygon'])
        aa={key(q) for q in old};bb={key(q) for q in new}
        before=[q for q in old if key(q) not in bb];after=[q for q in new if key(q) not in aa]
        rec=dict(page=page,items_exact=old==new,polygons_changed=bool(before or after),before=before,after=after,crops=[])
        if before or after:
            gray=cv2.imread(str(ROOT/row['path']))
            # New envelopes cover joined old boxes. Lost old lines also get a crop.
            targets=after+[q for q in before if not any(set(q.get('source_ids',[]))&set(z.get('source_ids',[])) for z in after)]
            seen=set()
            for j,q in enumerate(targets):
                b=bbox(q);h=(b[3]-b[1])/2;x,y,z,w=roi([b[0]-h,b[1]-h,b[2]+h,b[3]+h],gray.shape)
                if (x,y,z,w) in seen:continue
                seen.add((x,y,z,w));raw=gray[y:w,x:z];panels=[raw]
                for items,color in ((old,(180,120,25)),(new,(30,160,30))):
                    im=raw.copy()
                    for item in items:
                        c=bbox(item)
                        if not item.get('discounted') and c[0]<z and c[2]>x and c[1]<w and c[3]>y:
                            cv2.polylines(im,[np.rint(np.asarray(item['polygon'])-[x,y]).astype(np.int32)],True,color,2)
                    panels.append(im)
                im=np.vstack(panels);scale=min(1.,1500/im.shape[1]);im=cv2.resize(im,None,fx=scale,fy=scale)
                name=f'{page}.change-{j}.jpg';save_image(directory/name,label(im,page+' | raw / previous / '+directory.name));rec['crops'].append(name)
            aa=cv2.imread(str(previous/(page+'.jpg')));bb=cv2.imread(str(directory/(page+'.jpg')))
            height=max(aa.shape[0],bb.shape[0]);aa=cv2.resize(aa,(round(aa.shape[1]*height/aa.shape[0]),height));bb=cv2.resize(bb,(round(bb.shape[1]*height/bb.shape[0]),height));pagepair=np.hstack([aa,bb])
            save_image(directory/(page+'.comparison.jpg'),pagepair)
        records.append(rec)
    dump(directory/'changes.json',records)
    print(json.dumps([dict(page=r['page'],before=len(r['before']),after=len(r['after']),crops=len(r['crops'])) for r in records if r['polygons_changed']],indent=2))
    return records

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--previous',default='final');ap.add_argument('--version',default='r4b');a=ap.parse_args()
    compare(ROOT/'.astra/fast_lines/out/stack'/a.previous,ROOT/'.astra/fast_lines/out/stack'/a.version)
