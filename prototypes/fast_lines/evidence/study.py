"""R5b finite-support equivalence and all-supported-row shaping experiments."""
import argparse,json
from time import perf_counter
import cv2,numpy as np
from .__main__ import cohort,DEST
from ..shared.manifest import ROOT
from ..shared.timing import dump
from ..shared.geometry_fragments import candidates
from ..shared.geometry_contacts import render_contacts
from ..shared.geometry_envelopes import correct
from ..round2 import OLD,COMMON


def run(action):
    out=DEST/'r5-study';out.mkdir(exist_ok=True)
    report=[];cv2.setNumThreads(1)
    for row in cohort('r5'):
        p=row['page'];g=cv2.imread(str(ROOT/row['path']),0)
        e=json.load(open(DEST/'r5-merged'/(p+'.evidence.json')))
        if row['parked']:continue
        if action=='fields':
            pairs=candidates(e['original'],row['image_size']);selected={q['line'] for q in pairs['pairs']}
            if not selected:continue
            a=render_contacts(g,e['original'],'explicit_fast',7,selected)
            b=render_contacts(g,e['original'],'explicit_fast',7,selected,local_filter=True)
            # All path, support, contacts and alternative-owner records, not
            # just the accepted joins. Numeric drift is recorded separately.
            assert len(a['lines'])==len(b['lines'])
            maxerr=0
            for x,y in zip(a['lines'],b['lines']):
                for k in ('line','path','observed','contacts','alternatives'):
                    assert x[k]==y[k],(p,k)
                maxerr=max(maxerr,float(np.max(abs(np.array(x['support'])-y['support']))))
            report.append(dict(page=p,lines=len(a['lines']),max_support_error=maxerr,full_s=a['seconds'],local_s=b['seconds']))
        else:
            items=json.load(open(DEST/'r5-merged'/(p+'.json')))['items']
            for c in e['shapes']['changes']:items[c['line']]=dict(items[c['line']],polygon=c['old'])
            pmfile=next((q for q in [OLD/(p+'.npy'),COMMON/'baseline'/(p+'.npy')] if q.exists()),None)
            if pmfile is None:
                from ..shared.detector import Detector
                pm,_=Detector().infer(g)
            else:pm=np.load(pmfile)
            r=correct(g,pm,items,e['original'],scout=e['geometry']['witness'],map_bands=e['geometry'].get('map_bands'),column_evidence=e['geometry'].get('columns'),forbidden_regions=e['removed'],universal=True)
            dump(out/(p+'.all-bands.json'),r)
            report.append(dict(page=p,group=row['group'],seconds=r['seconds'],changes=len(r['changes']),decisions=len(r['decisions']),merged_shape_s=e['stages']['shape_s'],projected_correction_s=e['timing']['correction_s']-e['stages']['shape_s']+r['seconds']))
        print(action,p,report[-1],flush=True)
    dump(out/(action+'.json'),report)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['fields','all_bands']);run(ap.parse_args().action)
