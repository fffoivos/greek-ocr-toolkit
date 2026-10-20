"""R8-01b offline pilot: source-bound observations, no runtime import."""
import argparse, hashlib, json
from pathlib import Path
import cv2
import numpy as np
from ..shared.type_profiles import measure_line
from ..shared.geometry import height_proxy
from ..shared.geometry_contacts import prepare
from ..shared.contracts import bbox


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,default=lambda v:v.tolist() if hasattr(v,'tolist') else float(v))+'\n')
def sig():return {str(p):digest(p) for p in sorted(Path('prototypes/fast_lines').rglob('*.py'))}


def pilot(inputs,out):
    manifest=json.loads(Path(inputs).read_text());base=Path(inputs).parent;out=Path(out);out.mkdir(parents=True,exist_ok=True)
    summary=[]
    for page in manifest['pages']:
        name=page['page'];gray=cv2.imread(page['path'],0);assert digest(page['path'])==page['sha256']
        old=json.loads(Path(page['original_paddle']).read_text());items=old['original']
        slow=json.loads((base/'slow'/name/'reference.json').read_text());assert slow['input_sha256']==page['sha256']
        original_native=[];used=set();matches=[]
        for i,q in enumerate(items):
            if q.get('discounted'):continue
            r=measure_line(gray,q,True,samples=None,version=3);original_native.append(dict(r,source=i))
            x=sum(r['xrange'])/2
            possible=[]
            for row in slow['rows']:
                if row.get('discounted') or row['id'] in used or not row['x0']<=x<row['x1']:continue
                xs=np.linspace(row['x0'],row['x1'],len(row['baseline']))
                y=float(np.interp(x,xs,(np.asarray(row['baseline'])+row['meanline'])/2))
                if cv2.pointPolygonTest(np.array(q['polygon'],np.float32),(x,y),False)>=0:possible.append(row)
            if len(possible)==1:
                row=possible[0];used.add(row['id']);matches.append(dict(source=i,slow_row=row['id'],native_contact_px=r['xheight'],slow_xheight_px=row['xheight'],difference_px=r['xheight']-row['xheight'],uncertain=r['uncertain'],borrowed=row['borrowed']))
        # Observations of full native components; not an assertion of body or front ink.
        h=height_proxy(items,gray.shape[::-1]);contact=prepare(gray,h,with_density=False)
        # Small and large localizations, plus evenly spread native probes. Source
        # selection is diagnostic only; identities are recorded and never runtime inputs.
        ordered=sorted(original_native,key=lambda r:r['prior'])
        chosen=[]
        for r in [ordered[0],ordered[-1],original_native[len(original_native)//3],original_native[2*len(original_native)//3]] if ordered else []:
            if r['source'] not in [q['source'] for q in chosen]:chosen.append(r)
        tiles=[];probes=[]
        for r in chosen:
            q=items[r['source']];bb=bbox(q);cx=(bb[0]+bb[2])/2;cy=(bb[1]+bb[3])/2
            a=max(0,round(cx-230));c=min(gray.shape[1],a+460);b=max(0,round(cy-110));d=min(gray.shape[0],b+220)
            raw=cv2.cvtColor(gray[b:d,a:c],cv2.COLOR_GRAY2BGR);view=raw.copy()
            for g in contact['components']:
                l,t,z,w=g['bbox']
                if a<g['centre'][0]<c and b<g['centre'][1]<d:cv2.rectangle(view,(round(l-a),round(t-b)),(round(z-a),round(w-b)),(0,150,0),1)
            xx=np.array([a,c-1]);axis=r['axis']
            for key,offset in r.get('guides',r.get('unsupported_guides',{})).items():
                if key not in ('body_top','body_bottom'):continue
                yy=axis[0]+axis[1]*xx+offset;cv2.line(view,(0,round(yy[0]-b)),(c-a-1,round(yy[1]-b)),(255,170,0),1)
            m=next((m for m in matches if m['source']==r['source']),None)
            if m:
                row=next(row for row in slow['rows'] if row['id']==m['slow_row']);xs=np.linspace(row['x0'],row['x1'],len(row['baseline']))
                for k in ('baseline','meanline'):
                    xy=np.c_[xs-a,np.array(row[k])-b];cv2.polylines(view,[np.rint(xy).astype(np.int32)],False,(0,0,255),1)
            label=f"source {r['source']} prior {r['prior']:.1f} contact {r['xheight']:.1f} uncertain {r['uncertain']} slow {m['slow_row'] if m else 'unmatched'}"
            band=np.full((30,raw.shape[1]*2,3),255,np.uint8);cv2.putText(band,label,(5,20),0,.43,(0,0,0),1)
            tile=np.vstack([band,np.hstack([raw,view])]);pad=np.full((250,920,3),255,np.uint8);pad[:tile.shape[0],:tile.shape[1]]=tile;tiles.append(pad)
            probes.append(dict(source=r['source'],bbox=[a,b,c,d],match=m))
        image=out/(name+'.jpg');cv2.imwrite(str(image),np.vstack(tiles))
        # These are unique containment associations of a localization and a
        # saved row centre, not an ordered row-discovery accuracy evaluation.
        record=dict(page=name,input_sha256=page['sha256'],reference_sha256=digest(base/'slow'/name/'reference.json'),original_sha256=page['original_paddle_sha256'],native_profiles=original_native,unique_containment_matches=matches,unmatched_sources=[r['source'] for r in original_native if not any(m['source']==r['source'] for m in matches)],unmatched_reference=[r['id'] for r in slow['rows'] if not r.get('discounted') and r['id'] not in used],probes=probes,engineering_height=h)
        dump(out/(name+'.json'),record);summary.append(dict(page=name,profiles=len(original_native),unique_matches=len(matches),uncertain=sum(r['uncertain'] for r in original_native),probes=probes));print(name,len(original_native),len(matches),flush=True)
    dump(out/'receipt.json',dict(inputs_sha256=digest(inputs),source_hashes=sig(),pages=summary,cv2_threads=cv2.getNumThreads(),scope='23 development pilot; cached slow evidence comparison, not ground truth'))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('inputs');parser.add_argument('out');args=parser.parse_args();pilot(args.inputs,args.out)
