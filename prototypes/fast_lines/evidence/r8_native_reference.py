"""Missing native-mask/font-contact comparison, using the existing slow tools.

Saved row identity/curves are explicit inputs to this offline comparison. This
is not row discovery and cannot validate those identities. No runtime imports
this module; no failed physical_page code is imported.
"""
import argparse,json,hashlib
from pathlib import Path
from types import SimpleNamespace
from time import perf_counter
import cv2,numpy as np
from greekocr.pages.pixels import prepare_pixels
from greekocr.pages.font import evidence
from .r8_measurements import digest,dump


def run(inputs,pilot,out):
    inputs=Path(inputs);pilot=Path(pilot);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    pages=json.loads(inputs.read_text())['pages'];receipt=[]
    for page in pages:
        name=page['page'];g=cv2.imread(page['path'],0);assert digest(page['path'])==page['sha256']
        start=perf_counter();p=prepare_pixels(g);seconds=perf_counter()-start
        saved=json.loads((inputs.parent/'slow'/name/'reference.json').read_text());probes=json.loads((pilot/(name+'.json')).read_text())['probes'];lookup={int(q[5]):q for q in p.components}
        records=[];tiles=[]
        for probe in probes:
            a,b,c,d=probe['bbox'];raw=cv2.cvtColor(g[b:d,a:c],cv2.COLOR_GRAY2BGR);view=raw.copy()
            # Render only raw component support, not discounted output lines.
            for component in p.components:
                x,t,z,bot=component[:4]
                if a<(x+z)/2<c and b<(t+bot)/2<d:cv2.rectangle(view,(round(x-a),round(t-b)),(round(z-a),round(bot-b)),(0,150,0),1)
            match=probe['match'];record=dict(source=probe['source'],bbox=probe['bbox'],conditional_row=None)
            if match:
                row=next(q for q in saved['rows'] if q['id']==match['slow_row']);missing=[i for i in row['component_ids'] if i not in lookup]
                record.update(conditional_row=row['id'],missing_component_ids=missing,saved_xheight=row['xheight'],borrowed=row['borrowed'])
                if not missing:
                    line=SimpleNamespace(**row);line.baseline=np.array(row['baseline']);line.component_ids=np.array(row['component_ids'])
                    counts,points=evidence(p,line,_lookup=lookup)
                    record.update(classes=counts,points=points,after_capital_handling_xheight=line.xheight)
                    for key,color in [('baseline',(255,150,0)),('meanline',(0,0,255)),('font_top',(255,0,255)),('font_bottom',(0,170,230))]:
                        for x,y in points[key]:
                            if a<=x<c and b<=y<d:cv2.circle(view,(round(x-a),round(y-b)),2,color,-1)
            band=np.full((30,raw.shape[1]*2,3),255,np.uint8);cv2.putText(band,f"source {probe['source']} slow native pixels; class contacts conditional on saved row {record['conditional_row']}",(4,20),0,.4,(0,0,0),1)
            tile=np.vstack([band,np.hstack([raw,view])]);pad=np.full((250,920,3),255,np.uint8);pad[:tile.shape[0],:tile.shape[1]]=tile;tiles.append(pad);records.append(record)
        cv2.imwrite(str(out/(name+'.jpg')),np.vstack(tiles))
        dump(out/(name+'.json'),dict(page=name,input_sha256=page['sha256'],prepare_s=seconds,components=len(p.components),slow_page_xheight=p.xheight,probes=records,scope='offline preparation + class evidence only; saved row identities/curves are conditional inputs'))
        receipt.append(dict(page=name,prepare_s=seconds,probes=len(records),missing=sum(len(r.get('missing_component_ids',[])) for r in records)));print(name,round(seconds,3),receipt[-1]['missing'],flush=True)
    dump(out/'receipt.json',dict(pages=receipt,reference_source={str(p):digest(p) for p in sorted(Path('greekocr/pages').glob('*.py'))},inputs_sha256=digest(inputs)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('pilot');p.add_argument('out');a=p.parse_args();run(a.inputs,a.pilot,a.out)
