"""Offline complete-cohort inventory, comparison index and conservation audit."""
import argparse,html,json
from collections import Counter
import cv2
import numpy as np
from ..round2 import manifest,get_baseline,contacts
from ..shared.manifest import ROOT,digest
from ..shared.timing import dump
from ..shared.geometry_feature_correct import retention
from ..shared.geometry import height_proxy
from ..layout_barriers.fast import run as q8
from .reference import DEST,FEATURES
from .study import comparisons


def inventory(rows):
    result=[]
    for r in rows:
        p=r['page'];e=json.loads((DEST/'corrections-v6'/(p+'.evidence.json')).read_text())
        routes=json.loads((DEST/'routes-v4'/(p+'.json')).read_text())
        ref=json.loads((DEST/'explicit-v2'/(p+'.json')).read_text())
        routes['lines']=comparisons(get_baseline(r),ref,routes['route1'],routes['route2'])
        dump(DEST/'routes-v4'/(p+'.json'),routes)
        result.append(dict(page=p,group=r['group'],parked=r['parked'],baseline=len(get_baseline(r)),
            explicit_lines=len(ref['lines']),comparison_lines=len(routes['lines']),
            changed=e['summary']['changed'],geometry=e['summary']['geometry'],
            q8_cuts=len(e.get('separator_changes',[])),curved_cuts=len((e.get('curved') or {}).get('applied',[])),
            geometry_scout=e.get('witness',{}).get('trigger',False),
            decisions=e.get('geometry_decisions',[]),crops=e['crops']))
    dump(DEST/'inventory.json',result)
    dump(DEST/'source-receipt.json',dict(source={str(p.relative_to(ROOT)):digest(p) for p in
        sorted((ROOT/'prototypes/fast_lines/features_geometry').glob('*.py'))+sorted((ROOT/'prototypes/fast_lines/shared').glob('geometry_feature_*.py'))},
        images={r['page']:r['sha256'] for r in rows},note='Final v6 correction and v4 route source; earlier iterations remain historical diagnostics.'))
    return result


def validate(rows):
    failures=[];checks=Counter();geometry_audits=[]
    for r in rows:
        p=r['page'];items=get_baseline(r);W,H=r['image_size']
        paths=[DEST/'explicit-v2'/(p+'.'+f+'.jpg') for f in FEATURES]
        paths += [DEST/'routes-v4'/(p+'.'+f+'.'+route+'.jpg') for f in FEATURES for route in ('r1','r2')]
        paths += [DEST/'explicit-curved-rules'/(p+'.jpg'),DEST/'corrections-v6'/(p+'.jpg')]
        for fp in paths:
            checks['render_files']+=1
            if not fp.exists():failures.append(str(fp))
        e=json.loads((DEST/'corrections-v6'/(p+'.evidence.json')).read_text())
        final=json.loads((DEST/'corrections-v6'/(p+'.json')).read_text())
        record=json.loads((DEST/'routes-v4'/(p+'.json')).read_text())
        checks['line_accounting']+=1
        if [q['line'] for q in record['lines']]!=list(range(len(items))):failures.append(p+' line accounting')
        checks['schema']+=1
        assert final['page']==p and final['image_size']==[W,H] and final['unit']=='line'
        for q in final['items']:
            a=np.asarray(q['polygon']);assert a.shape[1]==2 and len(a)>=3 and np.isfinite(a).all()
            assert (a>=[0,0]).all() and (a<=[W,H]).all() and q['baseline'] is None and 0<=q['score']<=1
        owned={i for q in final['items'] for i in q.get('source_ids',[])}
        checks['source_accounting']+=1
        if not r['parked'] and owned!=set(range(len(items))):failures.append(p+' source accounting')
        gray=cv2.imread(str(ROOT/r['path']),0);h=height_proxy(items,(W,H));current=list(items)
        for change in e.get('geometry_changes',[]):
            i=change['line'];audit=retention(gray,current,i,change['new'][0],h)
            geometry_audits.append(dict(page=p,line=i,**audit));checks['geometry_conservation']+=1
            if audit['lost_ink']:failures.append(p+f' geometry lost ink {i}')
            current[i]=dict(current[i],polygon=change['new'][0])
        if not r['parked']:
            old=q8(gray,items);expected=old['changes'];actual=e['separator_changes'];checks['q8_retained']+=1
            if expected!=actual:failures.append(p+' Q8 changed')
        else:
            checks['parked_unchanged']+=1
            if [q['polygon'] for q in final['items']]!=[q['polygon'] for q in items]:failures.append(p+' parked changed')
    out=dict(checks=dict(checks),passed=sum(checks.values())-len(failures),total=sum(checks.values()),failures=failures,geometry_audits=geometry_audits)
    dump(DEST/'validation.json',out);print(json.dumps({k:v for k,v in out.items() if k!='geometry_audits'},indent=2))
    assert not failures


def gallery(rows,counts):
    parts=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Geometry feature evidence</title>',
        '<style>body{font:16px system-ui;max-width:1300px;margin:24px auto;padding:0 18px;background:#faf9f5;color:#202020}a{color:#126079}article{border-top:1px solid #ccc;padding:20px 0}.views{display:flex;flex-wrap:wrap;gap:14px}.views a{flex:1;min-width:240px;max-width:410px}img{width:100%}small{display:block}</style>',
        '<h1>Curvature, skew and separation</h1><p>195 supplied pages. Reference guides are model hypotheses. Map centres are not baselines. Orientation remains parked. Click any view for full resolution.</p>',
        '<p><a href="README.md">Legends and limitations</a> · <a href="inventory.json">Page and line inventory</a> · <a href="validation.json">Validation</a> · <a href="benchmark-v6/summary.json">Fresh timing</a></p>',
        '<p>Corrections: old geometry grey, new outline green; newly covered ink green, uncovered ink red. Green contour does not claim a recovered missing line. Whitespace routes are diagnostic and never cut.</p>']
    lookup={q['page']:q for q in counts}
    for r in rows:
        p=r['page'];s=lookup[p]
        parts.append(f'<article id="{p}"><h2>{html.escape(p)}</h2><p>{r["group"]} · {s["geometry"]} geometry changes · {s["q8_cuts"]} Q8 cuts · {s["curved_cuts"]} extra curved cuts</p><div class="views">')
        for feature in FEATURES:
            f=f'explicit-v2/{p}.{feature}.jpg';parts.append(f'<a href="{f}"><img loading="lazy" src="{f}">{feature}: explicit</a>')
        parts.append('</div><p>')
        for feature in FEATURES:
            for route in ('r1','r2'):
                parts.append(f'<a href="routes-v4/{p}.{feature}.{route}.jpg">{feature} {route}</a> · ')
        parts.append(f'<a href="routes-v4/{p}.json">every-line comparison</a></p><p><a href="explicit-curved-rules/{p}.jpg">curved rule evidence</a> · <a href="corrections-v6/{p}.jpg">correction overlay</a> · <a href="detector/{p}.json">detector JSON</a> · <a href="corrections-v6/{p}.evidence.json">decisions</a></p>')
        parts.append('<p>'+' · '.join(f'<a href="corrections-v6/{f}">changed lines {j*8+1}–{(j+1)*8}</a>' for j,f in enumerate(s['crops']))+'</p></article>')
    (DEST/'index.html').write_text('\n'.join(parts))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--validate',action='store_true');p.add_argument('--sheets',action='store_true');a=p.parse_args();cv2.setNumThreads(1)
    rows=manifest()['pages'];counts=inventory(rows);gallery(rows,counts)
    if a.sheets:
        for feature in FEATURES:
            for route in ('r1','r2'):contacts(rows,DEST/'routes-v4',f'.{feature}.{route}.jpg',DEST/'routes-v4'/'sheets'/f'{feature}-{route}')
        contacts(rows,DEST/'corrections-v6','.jpg',DEST/'corrections-v6'/'sheets')
    if a.validate:validate(rows)
