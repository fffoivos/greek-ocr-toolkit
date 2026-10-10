"""Page/line records against rendered physical witnesses; no detector truth score."""
import json
from pathlib import Path
import cv2,numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT
from ..shared.timing import dump
from ..shared.review import save_image
from ..shared.geometry import roi
from ..shared.contracts import bbox
from .reference import DEST,label
from .rows4 import draw


def pointer(name):return ROOT/json.loads((DEST/name).read_text())['directory']


def run():
    dest=DEST/'round4-audit';dest.mkdir(exist_ok=True);rows=[];summaries=[];outliers=[]
    for f in pointer('active-rows4.json').glob('*.json'):
        data=json.loads(f.read_text());p=data['page'];records=[]
        for i,s in enumerate(data['slow']):
            for r in ['explicit','heuristic']:
                q=data[r][i];a=sum(b['supported'] and b['within_box'] for b in s['bands']);b=sum(b['supported'] and b['within_box'] for b in q['bands']);err=None
                if s['body_height'] is not None and q['body_height'] is not None:err=abs(s['body_height']-q['body_height'])/s['prior']
                rec=dict(page=p,line=i,route=r,slow_rows=a,fast_rows=b,slow_joined=s['joined'],fast_joined=q['joined'],height_error_prior=err,slow_height=s['body_height'],fast_height=q['body_height'])
                records.append(rec)
                if err is not None:outliers.append((err,p,i))
        rows+=records
        summaries.append(dict(page=p,n=len(data['slow']),slow_ambiguous=sum(s['ambiguous'] for s in data['slow']),routes={r:dict(row_count_disagreements=sum(z['slow_rows']!=z['fast_rows'] for z in records if z['route']==r),height_pairs=sum(z['height_error_prior'] is not None for z in records if z['route']==r),max_height_error_prior=max((z['height_error_prior'] for z in records if z['route']==r and z['height_error_prior'] is not None),default=None)) for r in ['explicit','heuristic']}))
    dump(dest/'rows-per-line.json',rows);dump(dest/'rows-summary.json',summaries)
    tiles=[];seen=set();selected=[];manifest_rows={r['page']:r for r in manifest()['pages']}
    for err,p,i in sorted(outliers,reverse=True):
        if (p,i) in seen:continue
        seen.add((p,i));data=json.loads((pointer('active-rows4.json')/(p+'.json')).read_text());row=manifest_rows[p];g=cv2.imread(str(ROOT/row['path']),0);q=get_baseline(row)[i];bb=bbox(q);h=(bb[3]-bb[1])/2;a,t,b,d=roi([bb[0],bb[1]-h,bb[2],bb[3]+h],g.shape)
        crop=np.vstack([cv2.cvtColor(g[t:d,a:b],cv2.COLOR_GRAY2BGR)]+[draw(g,data[r][i])[t:d,a:b] for r in ['slow','explicit','heuristic']]);sc=min(1,1050/crop.shape[1]);tiles.append(label(cv2.resize(crop,None,fx=sc,fy=sc),p+f' line{i} maxHeightError={err:.2f}prior raw/S/R1/R2'));selected.append(dict(page=p,line=i,error=err,board=(len(tiles)-1)//3))
        if len(tiles)>=12:break
    for i in range(0,len(tiles),3):save_image(dest/f'rows-outliers-{i//3:02d}.jpg',np.vstack(tiles[i:i+3]))
    dump(dest/'rows-outliers.json',selected)
    table=[]
    for f in pointer('active-extents4.json').glob('*.json'):
        d=json.loads(f.read_text());p=d['page'];n=len(get_baseline(manifest_rows[p]))
        table.extend(dict(page=p,line=i,**{r:i in d[r]['protected_indices'] for r in ['slow','explicit','heuristic']}) for i in range(n))
    dump(dest/'tables-per-line.json',table)
    identity=[]
    for f in pointer('active-identity4.json').glob('*.json'):
        d=json.loads(f.read_text());maps={r:{m['query']:m for m in d[r]['pairs']} for r in ['slow','explicit','heuristic']}
        for i in range(len(d['glyphs'][0])):
            m=maps['slow'].get(i);slow=[] if m is None else [a['atlas'] for a in m['alternatives']]
            for r in ['explicit','heuristic']:
                q=maps[r].get(i);best=None if q is None else q['alternatives'][0]['atlas']
                identity.append(dict(query=d['query'],atlas=d['atlas'],glyph=i,line=d['glyphs'][0][i]['line'],route=r,slow_alternatives=slow,fast_best=best,within_slow_top3=best in slow if best is not None and slow else None))
    dump(dest/'identity-per-glyph.json',identity)
    edge=[]
    for f in pointer('active-edges4.json').glob('*.json'):
        d=json.loads(f.read_text())
        if not isinstance(d,dict) or 'slow' not in d or 'explicit' not in d:continue
        for i,s in enumerate(d['slow']['slots']):
            edge.append(dict(page=d['page'],slot=i,**{r:dict(supported=d[r]['slots'][i]['supported'],owned_fraction=d[r]['slots'][i]['owned_fraction'],bodies=d[r]['slots'][i]['bodies']) for r in ['slow','explicit','heuristic']}))
    dump(dest/'grid-per-slot.json',edge)
    print(json.dumps(dict(row_records=len(rows),table_lines=len(table),glyph_records=len(identity),grid_slots=len(edge))))

if __name__=='__main__':cv2.setNumThreads(1);run()
