"""Render captured explicit/dense native exemplar references, without new inference."""
import json
from pathlib import Path
import cv2,numpy as np
from .r8_ink02 import OUT,load,dump,sha

def main():
    inputs={r['page']:r for r in load()['pages']};records=[]
    for path in sorted((OUT/'calls').glob('*.json')):
        page=path.stem;calls=json.loads(path.read_text())['C'];gray=None
        for call_index,call in enumerate(calls):
            if 'dense' not in call:continue
            chosen=[];labels=set()
            for region,(explicit,dense) in enumerate(zip(call['result']['regions'],call['dense']['regions'])):
                ew=explicit.get('witnesses',[]);dw={tuple(w['bbox']):w for w in dense.get('witnesses',[])}
                pairs=[(w,dw[tuple(w['bbox'])]) for w in ew if tuple(w['bbox']) in dw]
                differing=[pair for pair in pairs if pair[0]['exemplar']!=pair[1]['exemplar']]
                label=explicit['ownership']
                if differing:chosen.append((region,label,*differing[0],'different native exemplars'))
                elif label not in labels and pairs:chosen.append((region,label,*pairs[0],'same native exemplar'));labels.add(label)
            for region,label,e,d,meaning in chosen:
                row=inputs[page];assert sha(row['path'])==row['sha256']
                if gray is None:gray=cv2.imread(row['path'],0)
                boxes=[e['bbox'],e['exemplar'],d['exemplar']];crops=[]
                for box in boxes:
                    a,b,c,z=map(int,box);crops.append(gray[b:z,a:c])
                height=max(p.shape[0] for p in crops)+8;width=max(p.shape[1] for p in crops)+8
                tiles=[]
                for p in crops:
                    tile=np.full((height,width),255,np.uint8);tile[4:4+p.shape[0],4:4+p.shape[1]]=p;tiles.append(tile)
                native=np.hstack(tiles);zoom=cv2.resize(native,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST)
                dest=OUT/'native_comparisons'/f'{page}.call{call_index}.r{region}.{label}.png';dest.parent.mkdir(exist_ok=True);cv2.imwrite(str(dest),zoom)
                records.append(dict(page=page,call=call_index,region=region,classification=label,meaning=meaning,query_bbox=e['bbox'],explicit=e,dense=d,file=str(dest.relative_to(OUT)),layout='4x nearest-neighbour: native query left, explicit exemplar centre, dense exemplar right; no intensity adjustment',source_identity='unvalidated; darkness and matching alone do not certify source'))
    dump(OUT/'NATIVE_WITNESS_COMPARISONS.json',records)
    print('native comparisons',len(records),'different exemplars',sum(r['meaning'].startswith('different') for r in records))
if __name__=='__main__':main()
