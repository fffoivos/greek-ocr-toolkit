"""Export audit, per-page ledgers, timings and links. Does not rerun inference."""
import argparse,json,html
from pathlib import Path
from collections import Counter
import cv2,numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from .round5_data import DEST,rows,load,ROOT
from ..shared.timing import dump
from ..stack.validate import retained_pixel_loss


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='final');a=ap.parse_args();out=DEST/a.version
    checks=0;ledger=[];links=[];repeats=[];totals=Counter();changed=0;cut_audit=[]
    for row in rows():
        p=row['page'];d=json.load(open(out/(p+'.json')));e=json.load(open(out/(p+'.evidence.json')));order=json.load(open(out/(p+'.order.json')))
        g,old,_=load(row);checks+=1;assert e['original']==old['original']
        checks+=1;assert d['page']==p and d['image_size']==row['image_size'] and d['unit']=='line'
        checks+=1;assert sorted(q['item_index'] for q in order)==list(range(len(d['items'])))
        counts=e['counts']
        if row['parked']:
            checks+=1;assert d['items']==e['original']
        else:
            checks+=1;assert len(d['items'])==len(e['original'])+counts['q8']+counts['curved']+counts['columns']-counts['back']-counts['ornaments']+counts['added']-counts['joined_reduction']
            present={i for q in d['items'] for i in q.get('source_ids',[])}
            removed={i for q in e.get('removed',[]) for i in q.get('source_ids',[])}
            checks+=1;assert present|removed==set(range(len(e['original'])))
        for q in d['items']:
            poly=np.array(q['polygon']);checks+=1
            assert len(poly)>=3 and np.isfinite(poly).all() and not q.get('discounted')
            checks+=1;assert (poly>=0).all() and (poly<=np.array(row['image_size'])).all()
            checks+=1;assert all(0<=i<len(e['original']) for i in q.get('source_ids',[]))
            checks+=1;assert q.get('baseline') is None or np.isfinite(q['baseline']).all()
            checks+=1;assert np.isfinite(q['score'])
        for c in e.get('geometry',{}).get('columns',{}).get('changes',[]):
            checks+=1
            # Floating half-plane pieces conserve vector area. Independently
            # rounded OpenCV edges need not rasterize identically: audit both
            # representations and never call vector conservation pixel identity.
            b=np.array(c['old']);lo=np.floor(b.min(0)).astype(int)-2;hi=np.ceil(b.max(0)).astype(int)+2
            lo=np.maximum(0,lo);hi=np.minimum([g.shape[1],g.shape[0]],hi);W,H=hi-lo
            oldmask=np.zeros((H,W),np.uint8);newmask=oldmask.copy();cv2.fillPoly(oldmask,[np.rint(b-lo).astype(np.int32)],1)
            for pp in c['new']:cv2.fillPoly(newmask,[np.rint(np.array(pp)-lo).astype(np.int32)],1)
            lost=(oldmask>0)&(newmask==0)
            raw=g[lo[1]:hi[1],lo[0]:hi[0]]
            vector=Polygon(c['old']);union=unary_union([Polygon(pp) for pp in c['new']])
            error=float(vector.symmetric_difference(union).area)
            assert error<1e-7,(p,'column vector loss')
            # One raster cell is a representation bound, not a feature gate.
            # Any deeper loss is an export bug, even if the area audit passes.
            assert not np.any(lost & (cv2.dilate(newmask,np.ones((3,3),np.uint8))==0)),(p,'deep raster loss')
            cut_audit.append(dict(page=p,line=c['line'],vector_symdiff=error,
                raster_lost=int(lost.sum()),raster_dark_lost=int((lost&(raw<200)).sum())))
        for decision in e.get('shapes',{}).get('decisions',[]):
            if decision['accepted']:
                checks+=1;assert decision['retention']['lost_ink']==0
        baseline=[q['polygon'] for q in old['items']];current=[q['polygon'] for q in d['items']]
        changed+=current!=baseline;totals.update(e.get('counts',{}))
        equalpilot=None;pilot=DEST/'composed-v1'/(p+'.json')
        if pilot.exists():equalpilot=json.load(open(pilot))['items']==d['items']
        ledger.append(dict(page=p,group=row['group'],counts=e.get('counts',{}),equal_reviewed_pilot=equalpilot,changed_from_R4b=current!=baseline,
            review='Native page overview; accepted shape/pair raw crops and changed column sheets reviewed. See report for limits.'))
        for repeat in [1,2]:
            fp=out/f'{p}.r{repeat}.json'
            if fp.exists():repeats.append(dict(json.load(open(fp)),repeat=repeat))
        refs=[(f'{a.version}/{p}.jpg','Numbered final'),(f'{a.version}/{p}.json','Detector JSON'),(f'{a.version}/{p}.evidence.json','Evidence'),
              (f'shapes-v5-slow/{p}.jpg','Native contacts'),(f'routes-v5/{p}.r1.jpg','Fast explicit'),(f'routes-v5/{p}.r2.jpg','Reduced heuristic'),(f'columns-v4/{p}.jpg','Column witnesses'),(f'routes-v5/{p}.columns.jpg','Column routes')]
        model='new-model-guides' if row['group']=='new_curved' else '../../features_geometry/explicit-v2'
        refs.extend((f'{model}/{p}.{feature}.jpg','Model '+feature) for feature in ('curvature','skew','separation'))
        for rel,label in refs:checks+=1;assert (DEST/rel).is_file(),rel
        links.append('<article><h3>'+html.escape(p)+'</h3><a href="'+refs[0][0]+'"><img loading="lazy" src="'+refs[0][0]+'"></a><p>'+' · '.join('<a href="'+rel+'">'+label+'</a>' for rel,label in refs)+'</p></article>')
    summary={}
    for repeat in sorted({r['repeat'] for r in repeats}):
        for group,pred in [('agreement',lambda r:r['group']=='agreement'),('discrepancy',lambda r:r['group'].startswith('discrepancy')),('new_curved',lambda r:r['group']=='new_curved'),('all',lambda r:True)]:
            rr=[r for r in repeats if r['repeat']==repeat and pred(r)]
            if not rr:continue
            fields={}
            for key in ['correction_s','total_s','column_s','shape_s','geometry_all_s','fragment_s','type_s']:
                vals=np.array([r.get(key,r['stages'].get(key,0)) for r in rr])*1000
                fields[key]=dict(median=float(np.median(vals)),p95=float(np.percentile(vals,95)),max=float(vals.max()),max_page=rr[int(vals.argmax())]['page'])
            vals=np.array([r['stages'].get('column_s',0)+r['stages'].get('shape_s',0) for r in rr])*1000
            fields['r5_geometry_new_s']=dict(median=float(np.median(vals)),p95=float(np.percentile(vals,95)),max=float(vals.max()),max_page=rr[int(vals.argmax())]['page'])
            summary[f'{group}_r{repeat}']=dict(n=len(rr),milliseconds=fields)
    dump(out/'summary.json',summary);dump(out/'review.json',ledger)
    dump(out/'column-conservation.json',cut_audit)
    dump(out/'validation.json',dict(checks=checks,pages=len(ledger),fresh_runs=len(repeats),counts=dict(totals),changed_R4b_pages=changed,equal_pilot_pages=sum(q['equal_reviewed_pilot'] is True for q in ledger),
        column_vector_max_error=max((r['vector_symdiff'] for r in cut_audit),default=0),
        column_raster_lost=sum(r['raster_lost'] for r in cut_audit),column_raster_gray_under_200_lost=sum(r['raster_dark_lost'] for r in cut_audit),column_raster_loss_max_chebyshev_pixels=1))
    (DEST/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>R5 geometry evidence</title><style>body{font:16px system-ui;background:#f5f3ed;margin:24px}main{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}article{background:white;padding:12px}h3{overflow-wrap:anywhere}img{width:100%}@media(max-width:900px){main{grid-template-columns:1fr}}</style><h1>Round 5 geometry</h1><p>Blue unchanged; green additions; purple reshaped or separated; old grey; removed red. Geometric reading-order numbers map to item indices in each order.json. Only active lines are drawn.</p><p>R5 A with merged R4 B/C. Severe curl, unruled physical leaves and universal smooth bands remain partial. Native contact renderings are hypotheses, never foreground truth.</p><p><a href="COMMENTS.md">Owner comments</a> · <a href="README.md">Legends and study versions</a> · <a href="'+a.version+'/summary.json">Repeated timings</a> · <a href="'+a.version+'/validation.json">Export audit</a></p><main>'+''.join(links)+'</main>')
    print(json.dumps(dict(checks=checks,pages=len(ledger),counts=dict(totals),changed=changed,pilot_equal=sum(q['equal_reviewed_pilot'] is True for q in ledger)),indent=2))
if __name__=='__main__':main()
