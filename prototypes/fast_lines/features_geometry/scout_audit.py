"""Every-page/line arithmetic and dispatch audit; no accuracy inference."""
import argparse,json
import cv2
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.geometry_feature_paths import sparse
from ..shared.geometry_scout import sparse_fast
from ..shared.manifest import digest,ROOT
from ..shared.timing import dump
from .reference import DEST
from .study import probability


def run(repeat,groups):
    cv2.setNumThreads(1);rows=manifest()['pages']
    if groups:rows=[r for r in rows if r['group'] in groups]
    records=[]
    for j,r in enumerate(rows):
        pm=probability(r);items=get_baseline(r)
        if j%2:a=sparse(pm,items,r['image_size'],3);b=sparse_fast(pm,items,r['image_size'])
        else:b=sparse_fast(pm,items,r['image_size']);a=sparse(pm,items,r['image_size'],3)
        assert all(a[k]==b[k] for k in ('nominated','fragments','trigger','height')),(r['page'],'dispatch')
        assert [q['line'] for q in a['lines']]==[q['line'] for q in b['lines']]
        errors=[]
        for old,new in zip(a['lines'],b['lines']):
            err={k:float(np.max(abs(np.asarray(old[k])-np.asarray(new[k])))) for k in ('path','affine','bend_h','angle_deg','skew_error_h','support','local_height')}
            assert max(err.values())<1e-7,(r['page'],old['line'],err)
            errors.append(dict(line=old['line'],errors=err))
        records.append(dict(page=r['page'],group=r['group'],lines=errors,dispatch_exact=True,
            old_s=a['seconds'],new_s=b['seconds'],trigger=a['trigger']))
    out=DEST/'round4/scout';out.mkdir(parents=True,exist_ok=True)
    dump(out/f'repeat-{repeat}.json',dict(records=records,source_sha256=digest(ROOT/'prototypes/fast_lines/shared/geometry_scout.py')))
    for group in sorted({r['group'] for r in records}):
        subset=[r for r in records if r['group']==group]
        print(group,len(subset),{k:[round(float(v),4) for v in np.percentile([q[k]*1000 for q in subset],[50,95,100])] for k in ('old_s','new_s')})
    print('all page dispatch and line values match',len(records),sum(len(r['lines']) for r in records),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repeat',type=int,required=True);p.add_argument('--groups',nargs='*');a=p.parse_args();run(a.repeat,a.groups)
