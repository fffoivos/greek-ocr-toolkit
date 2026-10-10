"""Publish measured records and auditable per-line route comparisons."""
import argparse,hashlib,json,shutil,platform
from pathlib import Path
import cv2,numpy as np
from ..round2 import manifest,get_baseline,ROOT
from ..shared.timing import dump,summary
from .study import DEST,source_key
from .final import gallery


def comparisons():
    records=[]
    for version in ('reference-v2','reference-v3','reference-v4-controls'):
        for path in sorted((DEST/version).glob('*.json')):
            d=json.loads(path.read_text())
            if 'ownership' not in d or 'lines' not in d:continue
            p=d['page'];lines=[]
            for r in d['lines']:
                a=r['slow']['thresholds'][1];b=r['route1']['thresholds'][1];c=r['route2']
                lines.append(dict(line=r['line'],bbox=r['bbox'],slow_width_h=a['width_h'],
                    route1_width_h=b['width_h'],route2_width_h=c['width_h'],
                    route1_error_h=b['width_h']-a['width_h'],route2_error_h=c['width_h']-a['width_h'],
                    slow_fragments_per_h=a['fragments_per_h'],route1_fragments_per_h=b['fragments_per_h'],route2_fragments_per_h=c['fragments_per_h'],
                    slow_holes_per_h=a['holes_per_h'],route1_holes_per_h=b['holes_per_h'],route2_holes_per_h=c['holes_per_h'],ownership=r['ownership']))
            dense=d['ownership']['dense']['regions'];ownership={}
            for route in ('explicit','sampled'):
                rs=d['ownership'][route]['regions']
                ownership[route]=dict(disagreements=[i for i,(a,b) in enumerate(zip(dense,rs)) if a['ownership']!=b['ownership']],
                    back=[i for i,r in enumerate(rs) if r['ownership']=='back'])
            masks={n:cv2.imread(str(path.parent/(p+'.images-'+n+'.png')),0)>0 for n in ('dense','route1','route2')}
            a=masks['dense'];image={}
            for route in ('route1','route2'):
                b=cv2.resize(masks[route].astype(np.uint8),(a.shape[1],a.shape[0]),interpolation=cv2.INTER_NEAREST)>0
                image[route]=dict(intersection=int((a&b).sum()),union=int((a|b).sum()),slow_pixels=int(a.sum()),route_pixels=int(b.sum()))
            records.append(dict(page=p,version=version,lines=lines,ownership=ownership,area_ink_support=image,
                width_error={k:summary([abs(r[k+'_error_h']) for r in lines]) for k in ('route1','route2')}))
    dump(DEST/'route-comparisons.json',records)
    return records


def snapshot():
    dest=DEST/'source-final';dest.mkdir(exist_ok=True);hashes={}
    # Include pre-existing detector/geometry/Q8 dependencies, not just new files.
    for base in ('shared','layout_barriers','features_ink'):
        for p in sorted((ROOT/'prototypes/fast_lines'/base).glob('*.py')):
            rel=p.relative_to(ROOT);q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(p,q);hashes[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
    for name in ('round2.py',):
        p=ROOT/'prototypes/fast_lines'/name;rel=p.relative_to(ROOT);q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);hashes[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
    dump(dest/'receipt.json',dict(files=hashes,source_key=source_key(),model_sha256=manifest()['model_sha256'],environment=platform.platform(),numpy=np.__version__,opencv=cv2.__version__))


def timing(version):
    dest=DEST/version;records=[]
    for f in sorted(dest.glob('benchmark-[012]-*.json')):records.extend(json.loads(f.read_text())['rows'])
    seen=set()
    for r in records:
        key=(r['page'],r['repeat']);assert key not in seen,key;seen.add(key)
    pages=manifest()['pages'];assert len(records)==430,len(records)
    bypage={p['page']:[r for r in records if r['page']==p['page']] for p in pages}
    for p,rs in bypage.items():
        assert {r['repeat'] for r in rs}==({0,1,2} if rs[0]['group']=='agreement' else {0,1})
        out=json.loads((dest/(p+'.json')).read_text());out.update(seconds=float(np.median([r['total_s'] for r in rs])),
            timing_status='measured warm-session median; detector + postprocess + Q8 + B; decode/startup separate',timing_samples=rs)
        assert out['page']==p and out['unit']=='line' and out['seconds']>0
        for item in out['items']:
            assert item['baseline'] is None
            assert len(item['polygon'])>=3 and np.isfinite(item['polygon']).all()
            assert 0<=item['score']<=1
        dump(dest/(p+'.json'),out)
    fields=['baseline_s','r2_s','ink_s','ink_scout_s','ink_refinement_s','added_s','correction_s','total_s','wall_s']
    groups={g:[r for r in records if r['group']==g] for g in sorted({r['group'] for r in records})}
    groups['all_discrepancy']=[r for r in records if r['group'] not in ('agreement','development')]
    changed={p['page'] for p in pages if json.loads((dest/(p['page']+'.evidence.json')).read_text())['removed']}
    groups['B_changed']=[r for r in records if r['page'] in changed]
    stats={g:{k:summary([r[k]*1000 for r in rs]) for k in fields} for g,rs in groups.items()}
    dump(dest/'timing-summary.json',dict(units='milliseconds',samples=len(records),groups=stats,
        by_repeat={str(i):{g:{k:summary([r[k]*1000 for r in rs if r['repeat']==i]) for k in fields} for g,rs in groups.items()} for i in (0,1,2)},
        slowest=sorted(records,key=lambda r:-r['added_s'])[:15],
        over_one_second_added=[r for r in records if r['added_s']>1],
        notes='Fresh decode/inference/postprocessing/Q8/B; no cached primitive. Warmup and per-batch startup separately recorded. Shared Mac contention not controlled.'))
    return stats


def publish(version):
    comparisons();stats=timing(version);gallery(version);snapshot()
    links=[]
    for folder in ['model','reference-v1','reference-v2','reference-v3','reference-v4-controls','density','density-v2','stroke-comparisons','edge-profiles','edge-profiles-v2','cooperation','perturbations','motif-gate-v2','motif-gate-v3',version]:
        dest=DEST/folder
        if folder!=version:
            files=sorted(dest.glob('*.jpg'))
            (dest/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>'+folder+'</title><style>body{font:16px system-ui}img{max-width:100%;height:auto}article{margin:2em 0}</style><h1>'+folder+'</h1>'+''.join('<article><a href="'+p.name+'">'+p.name+'</a><br><img loading="lazy" src="'+p.name+'"></article>' for p in files))
        links.append('<li><a href="'+folder+'/index.html">'+folder+'</a></li>')
    (DEST/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Track B feature evidence</title><style>body{font:18px system-ui;max-width:1000px;margin:40px auto;line-height:1.6}</style><h1>Faintness, inkiness, images</h1><p>Explicit features, both fast routes, retained failures and conditional corrections. See README.md for legends and limitations. The final stack preserves unknown ownership; area masks and stamp rings do not erase text.</p><ul>'+''.join(links)+'</ul><p><a href="route-comparisons.json">Every measured line comparison</a> · <a href="'+version+'/timing-summary.json">Fresh repeated timings</a></p>')
    print(json.dumps(stats,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='study-v2');ap.add_argument('--compare-only',action='store_true');args=ap.parse_args()
    if args.compare_only:comparisons()
    else:publish(args.version)
