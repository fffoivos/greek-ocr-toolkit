"""R8-02-i2 offline native part correspondence; never imported by runtime.

One focused repair of the isolated-CC unit observation. Existing native unit
spacing nominates windows; the unchanged chain shape test nominates a grouped
unit. Native stroke correspondence then explains actual pixels, never fills
predicted pixels. Residuals, edge contacts and below-threshold ink stay unknown.
"""
import json
from pathlib import Path
from time import perf_counter
import cv2
import numpy as np
from .r8_ink_support import frame_support, support
from ..shared.timing import dump
from ..shared.geometry import height_proxy

ROOT = Path('.astra/fast_lines/out/round8/R8-02-i2')
BASE = Path('.astra/fast_lines/out/round8/R8-02-i1/runtime')
MANIFEST = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack/.astra/fast_lines/out/round8/R8-01b/inputs-208.json')


def shape(mask):
    """The existing chain's 24-square proposal operator and distance witness."""
    tile = cv2.resize(mask.astype(np.float32), (24, 24), interpolation=cv2.INTER_AREA)
    bm = (tile > .5).astype(np.uint8)
    dt = cv2.distanceTransform(np.pad(bm, 1), cv2.DIST_L2, 3)[1:-1, 1:-1]
    ridge = (dt > 0) & (dt >= cv2.dilate(dt, np.ones((3, 3), np.uint8)))
    width = float(np.median(dt[ridge])) if ridge.any() else 0.
    v = tile.ravel() - tile.mean()
    v /= max(np.linalg.norm(v), 1e-6)
    return v, bm, cv2.distanceTransform(1-bm, cv2.DIST_L2, 3), width


def correspond(actual, exemplar):
    """Native finite support, with radius inherited from measured exemplar ink.

    Bbox-to-bbox transform is explicit and deliberately tested, not assumed to
    establish a unit. Output includes only observed pixels near exemplar ink;
    remote unmatched marks remain residual. Near-template touching ink is still
    an unresolved source ambiguity; this observation is not a source certificate.
    """
    ref = (cv2.resize(exemplar.astype(np.float32), actual.shape[::-1],
                      interpolation=cv2.INTER_AREA) > .5).astype(np.uint8)
    dt = cv2.distanceTransform(np.pad(ref, 1), cv2.DIST_L2, 3)[1:-1, 1:-1]
    ridge = (dt > 0) & (dt >= cv2.dilate(dt, np.ones((3, 3), np.uint8)))
    radius = float(np.median(dt[ridge])) if ridge.any() else 0.
    distance = cv2.distanceTransform(1-ref, cv2.DIST_L2, 3)
    explained = (actual > 0) & (distance <= radius/2)
    return explained, distance, radius


def grouped(gray, polygons, h):
    start = perf_counter()
    field, isolated, observed, sampled, records = frame_support(gray, polygons, h)
    owned = isolated.copy()
    band = np.zeros(gray.shape, np.uint8)
    for poly in field.bands:
        cv2.fillPoly(band, [np.rint(poly).astype(np.int32)], 1)
    accepted = {tuple(b) for b in field.units.tolist()}
    reports = []
    for chain_id, rec in enumerate(records):
        units = np.asarray([b for b in rec['units'] if tuple(b) in accepted])
        if not len(units):
            continue
        a, b, c, d = rec['bounds']
        axis = int(d-b > c-a)
        pad = int(np.ceil(h))
        x0, y0, x1, y1 = max(0,a-pad), max(0,b-pad), min(gray.shape[1],c+pad), min(gray.shape[0],d+pad)
        # Same source pixels and threshold. Added halo observes connected
        # continuation; it does not recalibrate the original native operator.
        mask = (gray[y0:y1,x0:x1] < rec['threshold']).astype(np.uint8)
        _, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        observed[y0:y1,x0:x1] |= mask > 0
        sampled[y0:y1,x0:x1] = True
        corridor = band[y0:y1,x0:x1] > 0
        ids = np.unique(labels[corridor]); ids = ids[ids > 0]
        eligible = np.isin(labels, ids)
        edge_ids = np.unique(np.r_[labels[0],labels[-1],labels[:,0],labels[:,-1]])
        exemplars = []
        for u in units:
            xx, yy, zz, ww = np.asarray(u, int)
            original_ids = np.unique(rec['labels'][yy-b:ww-b,xx-a:zz-a])
            matching = [k for k in original_ids if k and tuple(np.r_[rec['stats'][k,:2]+[a,b],rec['stats'][k,:2]+rec['stats'][k,2:4]+[a,b]]) == tuple(u)]
            if len(matching) != 1:
                continue
            m = (rec['labels'][yy-b:ww-b,xx-a:zz-a] == matching[0]).astype(np.uint8)
            exemplars.append((u, m, shape(m)))
        centers = ((units[:,:2]+units[:,2:])/2)[:,axis]
        centers = np.unique(np.sort(centers))
        if len(centers) < 2:
            continue
        period = float(np.median(np.diff(centers)))
        yy, xx = np.where(corridor)
        if not len(xx) or period <= 0:
            continue
        lo, hi = (xx.min()+x0,xx.max()+x0) if axis == 0 else (yy.min()+y0,yy.max()+y0)
        # Measured centers remain anchors; interpolate missing repeat positions,
        # and continue only to the independently traced finite cross-side ends.
        positions = []
        for l,r in zip(centers[:-1],centers[1:]):
            count = max(1,round((r-l)/period))
            positions.extend(np.linspace(l,r,count+1)[:-1])
        positions.append(centers[-1])
        positions = list(np.arange(centers[0]-period,lo-period,-period)[::-1])+positions+list(np.arange(centers[-1]+period,hi+period,period))
        positions = np.array([v for v in positions if lo-period/2 <= v <= hi+period/2])
        major_origin = x0 if axis == 0 else y0
        for slot, center in enumerate(positions):
            left = (positions[slot-1]+center)/2 if slot else center-period/2
            right = (positions[slot+1]+center)/2 if slot+1 < len(positions) else center+period/2
            l,r = max(0,int(np.floor(left-major_origin))),min(mask.shape[1-axis],int(np.ceil(right-major_origin)))
            if r <= l:
                continue
            sub = eligible[:,l:r] if axis == 0 else eligible[l:r,:]
            ys,xs = np.where(sub)
            if not len(xs):
                continue
            sx,sy,ex,ey = xs.min(),ys.min(),xs.max()+1,ys.max()+1
            if axis == 0:sx+=l;ex+=l
            else:sy+=l;ey+=l
            actual = eligible[sy:ey,sx:ex].astype(np.uint8)
            v,bm,dm,width = shape(actual)
            best = None
            for u,em,eshape in exemplars:
                if max(abs(np.array(actual.shape[::-1])-(u[2:]-u[:2]))) >= h/2:
                    continue
                ev,eb,ed,ew = eshape
                sim = float(v@ev)
                distance = max(float(dm[eb>0].mean()),float(ed[bm>0].mean())) if eb.any() and bm.any() else float('inf')
                if sim <= .75 and distance > min(width,ew)/2:
                    continue
                explained, native_distance, radius = correspond(actual, em)
                if best is None or explained.sum() > best[0].sum():
                    best = explained,u,sim,distance,radius,native_distance
            box = [int(x0+sx),int(y0+sy),int(x0+ex),int(y0+ey)]
            present = np.unique(labels[sy:ey,sx:ex][actual>0])
            edge = [int(i) for i in present if i in edge_ids]
            detail = dict(chain=chain_id,slot=slot,axis=axis,bbox=box,origin=[x0,y0],chain_bounds=rec['bounds'],observed_bounds=[x0,y0,x1,y1],threshold_DN=rec['threshold'],period=period,labels=present.tolist(),roi_edge_labels=edge,actual_pixels=int(actual.sum()),matched=best is not None)
            if best is not None:
                explained,u,sim,distance,radius,nd = best
                # An unfinished halo component cannot be certified from its
                # visible piece; retain it even if the resized tile matches.
                explained &= ~np.isin(labels[sy:ey,sx:ex],edge)
                owned[box[1]:box[3],box[0]:box[2]] |= explained
                detail.update(exemplar=u.tolist(),similarity=sim,chamfer_24=distance,native_radius=radius,explained_pixels=int(explained.sum()),residual_pixels=int(actual.sum()-explained.sum()),transform='native exemplar bbox -> actual grouped bbox; area interpolation; no template ink inserted')
            reports.append(detail)
    return field,owned,observed,sampled,reports,perf_counter()-start


def run(pages, directory='frame-parts'):
    out = ROOT/directory;out.mkdir(parents=True,exist_ok=False)
    results=[]
    for row in json.loads(MANIFEST.read_text())['pages']:
        p=row['page']
        if p not in pages:continue
        gray=cv2.imread(row['path'],0);e=json.loads((BASE/f'{p}.evidence.json').read_text())
        final=json.loads((BASE/f'{p}.json').read_text())['items']
        old=[q for q in e.get('removed',[]) if q['removal']=='recurrent frame']
        h=e.get('ink',{}).get('ownership',{}).get('height',height_proxy(e['original'],gray.shape[::-1]));items=final+old
        field,owned,observed,sampled,groups,seconds=grouped(gray,[q['polygon'] for q in e['original']],h)
        np.savez_compressed(out/f'{p}.npz',owned=owned,observed=observed,sampled=sampled)
        entries=[]
        for i,q in enumerate(items):
            cs,l=support(gray,q,h);a,b,c,d=l['a'],l['b'],l['c'],l['d'];pm=l['mask']>0
            if i<len(final) and not (owned[b:d,a:c]&pm).any():continue
            ink=(l['ink']>0)|(observed[b:d,a:c]&pm);residual=ink&~owned[b:d,a:c];unobserved=pm&~sampled[b:d,a:c]
            drop=bool(ink.any() and not residual.any() and not unobserved.any())
            n,labels,stats,_=cv2.connectedComponentsWithStats(residual.astype(np.uint8),8)
            entries.append(dict(line=i,source_ids=q.get('source_ids'),polygon=q['polygon'],approved_frame=i>=len(final),support=int(ink.sum()),unresolved=int(residual.sum()),unobserved_domain=int(unobserved.sum()),drop=drop,residual=[dict(bbox=[a+int(x),b+int(y),a+int(x+w),b+int(y+t)],area=int(ar)) for x,y,w,t,ar in stats[1:]]))
            raw=cv2.cvtColor(gray[b:d,a:c],cv2.COLOR_GRAY2BGR);vis=raw.copy();vis[ink&owned[b:d,a:c]]=(255,140,0);vis[residual]=(0,0,255)
            cv2.polylines(vis,[np.rint(np.array(q['polygon'])-[a,b]).astype(np.int32)],True,(0,180,0),1)
            cv2.imwrite(str(out/f'{p}.{i}.jpg'),np.hstack([raw,vis]))
        dump(out/f'{p}.json',dict(page=p,input=row,height=h,groups=groups,items=entries,seconds=seconds,complete_physical_support=False,weak_below_threshold='not certified blank'))
        result=dict(page=p,old=len(old),proposed=sum(x['drop'] for x in entries if x['approved_frame']),new_drops=[x['line'] for x in entries if x['drop'] and not x['approved_frame']],seconds=seconds)
        results.append(result);print(result,flush=True)
    dump(out/'results.json',results)


def attempt():
    """Replace the actual compose consumer ONLY in this rejected experiment."""
    from ..stack import pipeline as sp
    from ..shared import detector
    from .r8_frame_attempt import exclude
    out=ROOT/'frame-caller-attempt';out.mkdir(parents=True,exist_ok=False)
    detector.MODEL=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx')
    previous_render,previous_exclude=sp.frame_render,sp.frame_exclude
    observation=[];trace=[];results=[]
    def rendering(gray,polygons,height):
        field,owned,observed,sampled,groups,seconds=grouped(gray,polygons,height)
        observation[:]=[gray,field,height,owned,observed,sampled]
        trace.append(dict(stage='original polygon arrays -> grouped observation',polygons=polygons,height=height,groups=groups,seconds=seconds))
        return field
    def excluding(gray,items,field,height):
        r=exclude(gray,items,field,height,observation)
        trace.append(dict(stage='actual current item dictionaries -> complete observed support',items=items,height=height,decisions=r['decisions']))
        return r
    stack=sp.Stack();sp.frame_render,sp.frame_exclude=rendering,excluding
    try:
        for row in json.loads(MANIFEST.read_text())['pages']:
            if not row['page'].startswith('an-7792a3301892-'):continue
            trace.clear();r=stack(row['path']);p=row['page']
            old=json.loads((BASE/f'{p}.evidence.json').read_text())
            dump(out/f'{p}.json',r);dump(out/f'{p}.calls.json',trace)
            results.append(dict(page=p,frames_before=old['counts']['frames'],frames_after=r['counts']['frames'],items_after=len(r['items'])))
    finally:sp.frame_render,sp.frame_exclude=previous_render,previous_exclude
    dump(out/'results.json',results);print(results)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('pages',nargs='*');parser.add_argument('--directory',default='frame-parts');parser.add_argument('--attempt',action='store_true');args=parser.parse_args()
    attempt() if args.attempt else run(args.pages,args.directory)
