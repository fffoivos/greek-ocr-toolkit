"""Read-only experiment audit and shared, non-inference review materialisation.

Numerical path coverage is a diagnostic, never a correctness label. No new
algorithm/threshold sweep or inference is run here.
"""
import json,html
from pathlib import Path
import cv2,numpy as np
from scipy.spatial import cKDTree
from .shared.manifest import ROOT,OUT,load
from .shared.contracts import bbox
from .shared.geometry import roi
from .shared.timing import dump,append,summary
from .shared.review import overlay,save_image,atlas,detector_record
from .workflow import NAMES

def main():
    cv2.setNumThreads(1)
    rows=load(OUT/'shared/manifest.json')['pages']; checks=[]; totals={}; all_failures=[]
    for name in NAMES:
        d=OUT/name; page_metrics=[]; line_records=[]; missing=[]
        for row in rows:
            page=row['page']; path=d/f'{page}.json'; ep=d/f'{page}.evidence.json'
            if not path.exists() or not ep.exists(): missing.append(page); continue
            result=json.loads(path.read_text()); e=json.loads(ep.read_text()); ref=json.loads((OUT/'shared/references'/f'{page}.json').read_text())
            # Materialise comparator/variant JSON from existing receipts only.
            for variant,vitems in e.get('variants',{}).items():
                vp=d/'variants'/variant/f'{page}.json'
                if vp.exists():
                    v=json.loads(vp.read_text())
                    if v.get('seconds') is None:
                        v['seconds']=sum(c['seconds'] for c in e.get('calls',[]) if c['variant']==variant)
                        dump(vp,v)
            for field,timer in (('full_page','full_page_seconds'),('full_page_diagnostic','full_page_seconds')):
                if field in e:
                    dump(d/'variants'/field/f'{page}.json',detector_record(row,e[field],e[timer]))
            base=json.loads((OUT/'shared/cache'/f'{page}.json').read_text())['items']; items=result['items']; w,h=row['image_size']
            for i,q in enumerate(items):
                p=np.asarray(q['polygon']); assert p.ndim==2 and p.shape[1]==2 and np.isfinite(p).all()
                assert not q.get('discounted') and 'baseline' in q and 'score' in q
                assert p[:,0].min()>=0 and p[:,0].max()<=w and p[:,1].min()>=0 and p[:,1].max()<=h
            if row['parked']: assert items==base, (name,page,'orientation changed')
            if name=='layout_barriers' and e.get('table'): assert items==base,(name,page,'table changed')
            bbs=np.asarray([bbox(q) for q in items]); centres=(bbs[:,:2]+bbs[:,2:])/2 if len(bbs) else np.empty((0,2)); tree=cKDTree(centres) if len(centres) else None
            bad=[]
            for line in ref['lines']:
                path=np.asarray(line['path']); support=np.asarray(line['support'])>.06; b=line['bbox']; centre=np.array([(b[0]+b[2])/2,(b[1]+b[3])/2]); cov=0.; match=None
                if tree is not None:
                    _,ids=tree.query(centre,k=min(3,len(items)))
                    for idx in np.atleast_1d(ids):
                        poly=np.asarray(items[int(idx)]['polygon'],np.float32)
                        frac=float(np.mean([cv2.pointPolygonTest(poly,tuple(map(float,p)),False)>=0 for p in path[support]])) if support.any() else None
                        if frac is not None and (match is None or frac>cov): cov=frac; match=int(idx)
                record=dict(page=page,line=line['id'],candidate=match,raw_support_inside_fraction=cov if support.any() else None,supported_samples=int(support.sum()),
                            verdict='not checked',meaning='independent raw-support containment; not accuracy')
                line_records.append(record)
                if support.any() and cov<.5: bad.append(line['id'])
            failures=[]
            if e.get('unprocessed_requests'): failures.append('crop budget left requests unscheduled')
            if bad: failures.append('some independent raw supports outside candidate envelopes; unadjudicated')
            if name=='local_ribbons' and any(q.get('abstain') for q in e.get('witnesses',[])): failures.append('ambiguous multi-ridge/barrier requests abstained')
            if name=='foreground_profiles': failures.append('front-verso ownership unknown; no false-positive deletion')
            if name=='font_guides': failures.append('baseline/accent semantics unidentified')
            if name=='ink_condition': failures.append('readability and actual broken/filled attribution unknown')
            if name in ('map_graph','classical_residual'): failures.append('new candidates need ownership/geometry adjudication')
            if name=='sheet_lattice' and any(q['status']!='shared candidate' for q in e.get('fields',[])): failures.append('some fields underconstrained or tables protected')
            if name=='image_motifs': failures.append('stamp/initial ownership unresolved; existing lines retained')
            if name=='residual_ledger' and e.get('requests'): failures.append('requests are nominations, not recovered lines')
            geometry_changed=len(items)!=len(base) or any(q['polygon']!=b['polygon'] for q,b in zip(items,base))
            rec=dict(page=page,group=row['group'],parked=row['parked'],baseline=len(base),items=len(items),geometry_changed=geometry_changed,raw_support_flags=bad,limitations=failures)
            page_metrics.append(rec)
            if failures: all_failures.append(dict(approach=name,**rec))
            # Rendering reuses saved products, no new inference or decisions.
            if name=='native_contours':
                gray=cv2.imread(str(ROOT/row['path']),0)
                accepted=[dict(points=q['contour'],discounted=q.get('discounted')) for q in e.get('genealogy',{}).get('poly',[])]
                save_image(d/f'{page}_4_evidence.jpg',overlay(gray,paths=accepted,title=page+' | accepted unexpanded contours (cyan); discounted absent'))
                pm=np.load(OUT/'shared/cache'/f'{page}.npy'); heat=cv2.applyColorMap(np.uint8(np.clip(pm,0,1)*255),cv2.COLORMAP_TURBO)
                save_image(d/f'{page}_2_map.jpg',heat)
            if name=='image_motifs' and e.get('motif_pairs'):
                gray=cv2.imread(str(ROOT/row['path']),0); cells=[]
                for i,pair in enumerate(e['motif_pairs']):
                    x0,y0,x1,y1=roi(pair['bbox'],gray.shape); shift=round(pair['shift_page']); patch=gray[y0:y1,x0:x1]
                    if patch.shape[1]>shift>0:
                        cells.extend([(f'motif {i} left',patch[:,:-shift]),(f'motif {i} shifted',patch[:,shift:])])
                if cells: atlas(cells,d/f'{page}_5_motifs.jpg',columns=2,cell_width=500)
        assert not missing,(name,missing)
        dump(d/'per_line_comparison.json',line_records); dump(d/'page_failures.json',page_metrics)
        totals[name]=dict(pages=len(page_metrics),lines_checked_numerically=len(line_records),pages_with_raw_support_flags=sum(bool(r['raw_support_flags']) for r in page_metrics))
        print(name,totals[name],flush=True)
    dump(OUT/'shared/validation.json',dict(status='passed',prototypes=totals,scope=len(rows),checks=['174 outputs per approach','finite full-page polygons','discounted absent','score/baseline keys including null','orientation unchanged','A02 tables unchanged','per-line raw-support diagnostic emitted']))
    dump(OUT/'shared/failures_and_unknowns.json',all_failures)
    # One labelled sheet per approach and cohort batch. The UI can open any original.
    for name in NAMES:
        for batch in range(0,len(rows),24):
            cells=[(r['page'],cv2.imread(str(OUT/name/f"{r['page']}_6_result.jpg"))) for r in rows[batch:batch+24]]
            atlas(cells,OUT/name/f'contact-{batch//24:02d}.jpg',columns=6,cell_width=280)

if __name__=='__main__': main()
