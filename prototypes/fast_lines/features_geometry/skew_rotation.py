"""Known small rotations of allowed-page pixels, not extra evaluation pages."""
import json
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.geometry_contacts import render_contacts
from ..shared.manifest import ROOT
from ..shared.timing import dump
from .reference import DEST,save,line
from .skew_contacts import fit


def run():
    out=DEST/'round4/skew-rotation';out.mkdir(parents=True,exist_ok=True);records=[]
    pages=['s2-77d1bd63d5babbe0df73-p00001','an-778126cc8c2b-p000007','an-ef481610a820-p000151']
    for r in [r for r in manifest()['pages'] if r['page'] in pages]:
        p=r['page'];g=cv2.imread(str(ROOT/r['path']),0);items=get_baseline(r)
        body=json.loads((DEST/'round4/body-slow-v7'/(p+'.json')).read_text());eligible=[]
        for q in body['lines']:
            a=fit(q,version=2)
            if a and a['provisional_straight']:eligible.append((np.ptp(np.array(q['path'])[:,0]),q,a))
        if not eligible:continue
        _,q,old=max(eligible,key=lambda x:x[0]);index=q['line']
        for rotation in [-2.,2.]:
            matrix=cv2.getRotationMatrix2D((g.shape[1]/2,g.shape[0]/2),rotation,1)
            transformed=cv2.warpAffine(g,matrix,(g.shape[1],g.shape[0]),borderValue=255)
            transformed_items=[dict(item,polygon=cv2.transform(np.array(item['polygon'],np.float32)[None],matrix)[0].tolist()) for item in items]
            overlay=cv2.cvtColor(transformed,cv2.COLOR_GRAY2BGR);measurements={}
            for route,color in [('slow',(30,170,20)),('explicit_fast',(190,30,180))]:
                result=render_contacts(transformed,transformed_items,route,7,selected={index});new=fit(result['lines'][0],version=2)
                expected=old['angle_deg']-rotation
                measurements[route]=dict(new,expected_angle_deg=expected,error_deg=new['angle_deg']-expected)
                line(overlay,result['lines'][0]['path'],color,2);line(overlay,new['path'],color,3)
            save(out/(p+f'.rotation{rotation:+.0f}.jpg'),overlay,p+f' | known rotation {rotation:+.0f} deg; native green / fast purple')
            records.append(dict(page=p,line=index,rotation=rotation,original=old,measurements=measurements))
    dump(out/'results.json',records)

if __name__=='__main__':
    cv2.setNumThreads(1);run()
