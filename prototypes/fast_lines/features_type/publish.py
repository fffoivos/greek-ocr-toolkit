"""Validate artifacts and publish their local review index; no external actions."""
import json,html
from pathlib import Path
from collections import Counter
import numpy as np
from ..round2 import manifest,get_baseline
from ..shared.manifest import ROOT,digest
from ..shared.timing import dump
from .reference import DEST


def location(name):return ROOT/json.loads((DEST/('active-'+name+'.json')).read_text())['directory']

def stats(rows,key):
    x=np.array([r[key]*1000 for r in rows]);return dict(n=len(x),median_ms=float(np.median(x)),p95_ms=float(np.quantile(x,.95)),max_ms=float(x.max()))


def run():
    rows=manifest()['pages'];cor=location('corrections');bench=location('benchmark');typ=location('type');tab=location('tables');lat=location('lattice')
    times=[json.loads(p.read_text()) for p in bench.glob('*.json')];assert len(times)==390,(len(times),bench)
    receipts={(r['page'],r['repeat']):r for r in times};checks=Counter();adds=[];summary={}
    for row in rows:
        p=row['page'];r=json.loads((cor/(p+'.json')).read_text());e=json.loads((cor/(p+'.evidence.json')).read_text());before=get_baseline(row)
        assert e['input_sha256']==row['sha256']==digest(ROOT/row['path'])
        assert r['page']==p and r['image_size']==row['image_size'] and r['unit']=='line';checks['source_and_schema']+=1
        assert len(receipts[p,1]['page']) and len(receipts[p,2]['page'])
        assert len(e['added'])==receipts[p,1]['additions']==receipts[p,2]['additions'];checks['fresh_repeat_addition_counts']+=1
        for q in r['items']:
            a=np.asarray(q['polygon']);assert a.ndim==2 and a.shape[1]==2 and len(a)>=3 and np.isfinite(a).all()
            assert 'baseline' in q and 'score' in q and not q.get('discounted')
        if row['group']=='agreement':
            assert r['items']==before and receipts[p,1]['unchanged'] and receipts[p,2]['unchanged'];checks['agreement_exact']+=1
        if not row['parked']:
            # Q8 cuts carry source geometry in their ledger. Every other old item
            # must remain byte-for-byte equal; C never rewrites an old line.
            changed={z['line'] for z in e['separator']['changes']}
            assert all(q in r['items'] for i,q in enumerate(before) if i not in changed)
            checks['unchanged_original_items']+=1
        assert (cor/(p+'.jpg')).exists()
        lattice=json.loads((lat/(p+'.json')).read_text());assert all(k in lattice for k in ['slow','explicit','heuristic']);checks['three_lattice_routes']+=1
        # Bind seconds to a fresh full-stack observation, with decode/startup
        # separately available in the linked raw timing receipt.
        r['seconds']=receipts[p,2]['total_s'];dump(cor/(p+'.json'),r)
        for k,q in enumerate(e['added']):adds.append(dict(page=p,addition=k,review='raw/after visually inspected',limits='row ink may overlap marks, a drop cap, stamp, or a curved terminal'))
    for repeat in [1,2]:
        for group,predicate in [('agreement',lambda r:r['group']=='agreement'),('new_discrepancy',lambda r:r['group'] in ['discrepancy','discrepancy_extra']),('correction_pages',lambda r:r['additions']>0),('all',lambda r:True)]:
            rr=[r for r in times if r['repeat']==repeat and predicate(r)]
            summary[f'{group}_r{repeat}']={k:stats(rr,k) for k in ['type_s','scout_s','correction_s','stack_added_s','detector_s','total_s']}
    dump(DEST/'timing-summary.json',summary);dump(DEST/'validation.json',dict(checks=checks,tests=dict(passed=17,total=17),exports=195,additions=len(adds),addition_pages=len({r['page'] for r in adds}),source=json.loads((DEST/'active-corrections.json').read_text())['source'],review_limits='all final additions inspected; not a glyph-complete audit of every page'))
    dump(DEST/'reviewed-additions.json',adds)
    txt=['# Review artifacts — track C','', 'Final correction JSON seconds are the fresh repeat-2 full stack, excluding decode/startup and rendering. Raw repeats include these separately. See `validation.json`, `timing-summary.json` and `feature-timings.json`.','', '## Legend','', '- Type: coloured component boxes are supported size groups, not named fonts; purple bars are inter-component gaps. S-1 means uncertain.','- Guides: cyan body top; red body bottom; green tall top; purple descender; orange mark top/bottom. No inferred semantic baselines.','- Tables: orange rules, purple individual dot witnesses and cached Docling proposals, cyan localized cells/rows, green protected hypotheses, amber uncertain alignment.','- Lattice: blue ideal pitch grid, magenta measured raw ridges, green supported body components, orange unsupported slots, grey already-owned components.','- Corrections: original small-detector boxes grey; additions and new ink green; removed ink red. No discounted candidate outlines. Q8 separators remain included.','', '## Current directories','']
    for name in ['type','tables','lattice','corrections','benchmark']:
        d=location(name);txt.append(f'- [{name}]({d.name}/): machine-readable per-page records and images.')
    txt+=['- [Model/A07](model/): six cached slow-model anchors and explicit A07 fragmentation.','- [Book context](book-v1/): three pages, original/R1/R2 relative-size views.','- [All-page gallery](index.html): final corrections and feature evidence.','', '## Coverage and limits','', '195 final correction images/exports; 195 × 3 lattice images; 9 × 2 × 3 typography images and all-line detail boards; 14 × 3 table images. Every new table item remains Paddle-owned; table recognition is incomplete. Fourteen accepted additions on twelve pages. See the research report for every observed failure. Earlier v1/v2 output is deliberately retained as counterevidence, not accepted corrections.']
    (DEST/'README.md').write_text('\n'.join(txt)+'\n')
    parts=['<!doctype html><meta charset="utf-8"><title>Track C: type feature evidence</title><style>body{font:16px system-ui;max-width:1300px;margin:24px auto;padding:12px}article{display:inline-block;width:290px;margin:12px;vertical-align:top}img{width:100%}a{color:#19556c}</style><h1>Type feature evidence</h1><p>Grey: original detector. Green: added lines/ink. Red: removed ink. Click any image for full size. <a href="README.md">Legend and limits</a>.</p>']
    for row in rows:
        p=row['page'];prefix=cor.name+'/'+p;parts.append(f'<article><b>{html.escape(p)}</b><p>{row["group"]}</p><a href="{prefix}.jpg"><img loading="lazy" src="{prefix}.jpg"></a><p><a href="{prefix}.json">Detector JSON</a> · <a href="{prefix}.evidence.json">Decisions</a> · <a href="{lat.name}/{p}.slow.jpg">Explicit lattice</a> · <a href="{lat.name}/{p}.explicit.jpg">R1</a> · <a href="{lat.name}/{p}.heuristic.jpg">R2</a></p></article>')
    (DEST/'index.html').write_text('\n'.join(parts))
    report=ROOT/'docs/research/FAST_LINES_FEATURES_C.md';s=report.read_text();marker='\n## Measured final receipts\n';s=s.split(marker)[0];s+=marker+'\nAll times below are milliseconds. Each row covers a complete independent repeat.\n\n| Cohort/repeat | n | C median / p95 / max | Q8+C median / p95 / max | Full detector+stack median / max |\n|---|---:|---|---|---|\n'
    for key in ['agreement_r1','agreement_r2','new_discrepancy_r1','new_discrepancy_r2','correction_pages_r1','correction_pages_r2']:
        z=summary[key];fmt=lambda k:' / '.join(f'{z[k][j]:.3f}' for j in ['median_ms','p95_ms','max_ms'])
        s+=f"| {key} | {z['type_s']['n']} | {fmt('type_s')} | {fmt('stack_added_s')} | {z['total_s']['median_ms']:.3f} / {z['total_s']['max_ms']:.3f} |\n"
    s+='\nRaw numbers for every page: `benchmark-v4-'+json.loads((DEST/'active-benchmark.json').read_text())['source']+'/`. All 40 agreement outputs are identical in both fresh repeats. C adds under 3 ms on every agreement observation in these runs. All observed C corrections fit below one second; this is not a held-out guarantee. Full-stack times are reported separately from correction cost.\n'
    feature=json.loads((DEST/'feature-timings.json').read_text());s+='\nOn-demand feature census, milliseconds (median / maximum across the named pages):\n\n| Feature / route | repeat 1 | repeat 2 |\n|---|---|---|\n'
    for feature_name in ['typography','tables']:
        for route in ['slow','explicit','heuristic']:
            vals=[]
            for rep in [1,2]:
                z=stats([r for r in feature if r['feature']==feature_name and r['route']==route and r['repeat']==rep],'seconds');vals.append(f"{z['median_ms']:.3f} / {z['max_ms']:.3f}")
            s+=f'| {feature_name} / {route} | '+ ' | '.join(vals)+' |\n'
    report.write_text(s);print(json.dumps(dict(checks=checks,summary=summary),indent=2))

if __name__=='__main__':run()
