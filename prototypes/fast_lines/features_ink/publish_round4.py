"""Bind final round4 exports to exact reviewed decisions and fresh timings."""
import hashlib,html,json,math
from pathlib import Path
import numpy as np
from ..round2 import manifest
from ..shared.timing import dump
from .study import DEST


def run():
    dest=DEST/'round4';study=dest/'study-v3';rows=manifest()['pages'];all_t=[]
    for f in study.glob('benchmark-*.json'):all_t.extend(json.loads(f.read_text())['rows'])
    assert len(all_t)==390
    receipt=json.loads((dest/'runtime-handoff.json').read_text())
    for f,h in receipt['hashes'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,f
    for row in rows:
        p=row['page'];before=json.loads((DEST/'study-v2'/(p+'.evidence.json')).read_text());after=json.loads((study/(p+'.evidence.json')).read_text())
        assert before['items']==after['items'],p
        ts=[r for r in all_t if r['page']==p];assert len(ts)==2 and {r['repeat'] for r in ts}=={1,2}
        export=json.loads((study/(p+'.json')).read_text());export['seconds']=float(np.median([r['total_s'] for r in ts]));export['timing_status']='median of two fresh warm detector + Q8+B runs; decode/startup separate'
        assert export['image_size']==row['image_size'] and math.isfinite(export['seconds'])
        for q in export['items']:
            assert q['baseline'] is None and all(math.isfinite(v) for xy in q['polygon'] for v in xy)
        dump(study/(p+'.json'),export)
    summary={}
    for group in ('agreement','new_discrepancy','development'):
        summary[group]={}
        for repeat in (1,2):
            selected=[r for r in all_t if r['repeat']==repeat and (r['group'].startswith('discrepancy') if group=='new_discrepancy' else r['group']==group)]
            summary[group][repeat]=dict(pages=len(selected),ms={})
            for k in ('ink_s','added_s','total_s','ink_scout_s','ink_refinement_s'):
                v=[r[k]*1000 for r in selected];summary[group][repeat]['ms'][k]=dict(zip(('median','p95','max'),map(float,np.percentile(v,[50,95,100]))))
    dump(dest/'timing-summary.json',summary)
    routes={}
    for name in ('dense','explicit','heuristic'):
        routes[name]={(r['page'],r['line']):r for r in json.loads((dest/f'recurrence-v4-{name}'/'records.json').read_text())}
    comparisons=[]
    for key,r in routes['explicit'].items():
        q=routes['heuristic'][key];slow=routes['dense'].get(key)
        comparisons.append(dict(page=key[0],line=key[1],old_accepted=r['old_accepted'],slow=slow['best'] if slow else None,route1=r['best'],route2=q['best'],route1_nominate=r['nominate'],route2_nominate=q['nominate']))
    dump(dest/'recurrence-comparisons.json',comparisons)
    groups=[('Corrections and detector JSON','study-v3'),('Native repeated ink','recurrence-v4-dense'),('Fast explicit repeated ink','recurrence-v4-explicit'),('Recurrence heuristic','recurrence-v4-heuristic'),('Faintness and stroke observability','observability-v4'),('Route disagreements','observability-review'),('Known physical perturbations','observability-controls-v4'),('Image/stamp intersections','image-structure-v4'),('Borrowed table conflict evidence','cooperation')]
    body=['<h1>Feature B — round4</h1><p>All195 final line lists equal the reviewed round3 outputs. No new generic image/stamp or unreadability suppression. Runtime recurrence is an early nomination only.</p><p><a href="README.md">Legend and limitations</a> · <a href="timing-summary.json">two fresh timing repeats</a> · <a href="recurrence-comparisons.json">per-line recurrence comparison</a></p>']
    for label,folder in groups:
        links=[]
        for p in sorted((dest/folder).glob('*')):
            if p.suffix not in ('.jpg','.json','.html'):continue
            if folder=='study-v3' and p.name!='index.html':continue
            if folder.startswith('recurrence') and p.stem.isdigit():continue
            link=p.relative_to(dest).as_posix();links.append('<li><a href="'+html.escape(link)+'">'+html.escape(p.name)+'</a></li>')
        body.append('<h2>'+label+'</h2><ul>'+''.join(links)+'</ul>')
    (dest/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Ink features round4</title><style>body{font:16px system-ui;margin:2em auto;padding:0 1em;max-width:1100px}li{margin:.3em 0;overflow-wrap:anywhere}</style>'+''.join(body))
    dump(dest/'validation.json',dict(fresh_executions=390,exact_old_decisions=195,detector_exports=195,runtime_hashes=receipt['hashes'],recurrence_comparisons=len(comparisons),positive_motifs=sum(r['old_accepted'] for r in comparisons)))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':run()
