"""Read-only comparison/export of the pinned 208 R8-02 candidate artifacts."""
import collections, hashlib, html, json
from pathlib import Path
import cv2
import numpy as np
from .r8_ink_support import BASE, OUT


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def strip_times(value):
    if isinstance(value, dict):
        return {k:strip_times(v) for k,v in value.items()
                if not k.endswith('_s') and k not in ('seconds','elapsed')}
    if isinstance(value, list):return [strip_times(v) for v in value]
    return value


def key(q):
    return json.dumps({k:v for k,v in q.items() if k!='removal'},sort_keys=True)


def main():
    rows=json.loads((BASE.parent/'R8-01b/inputs-208.json').read_text())['pages']
    pilots=json.loads(Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model/.astra/fast_lines/out/round8/R8-01/inputs.json').read_text())
    pilots={r['page'] for r in pilots['pages']}
    results=[];reasons=[]
    for row in rows:
        p=row['page'];a=json.loads((BASE/'runtime'/f'{p}.json').read_text());b=json.loads((OUT/'runtime'/f'{p}.json').read_text())
        x=json.loads((BASE/'runtime'/f'{p}.evidence.json').read_text());y=json.loads((OUT/'runtime'/f'{p}.evidence.json').read_text())
        def ex(r):return collections.Counter(key(q) for q in r.get('removed',[]))
        counts={k:[x['counts'].get(k),y['counts'].get(k)] for k in x.get('counts',{}) if x['counts'].get(k)!=y['counts'].get(k)}
        changed=[k for k in ('q8','geometry','type','added','frame','shapes','rows','page_field','row_ownership','ink_footprints') if strip_times(x.get(k))!=strip_times(y.get(k))]
        old={key(q):q for q in x.get('removed',[])}
        for q in y.get('removed',[]):
            k=key(q)
            if k in old and old[k]['removal']!=q['removal']:
                reasons.append(dict(page=p,source_ids=q.get('source_ids'),polygon=q['polygon'],before=old[k]['removal'],after=q['removal']))
        results.append(dict(page=p,items_equal=a['items']==b['items'],exclusions_equal=ex(x)==ex(y),count_changes=counts,structural_stage_changes=changed,pilot=p in pilots,items=len(b['items'])))
    assert all(r['items_equal'] and r['exclusions_equal'] for r in results)
    dump(OUT/'acceptance.json',dict(pages=results,final_items=sum(r['items'] for r in results),pilot_count=len(pilots),reason_changes=reasons,
         native_loss='Zero candidate-vs-cb4d6b4 final crop loss/reassignment by exact polygon and item equality on all 208. This does not certify historical missing glyphs or source understanding.'))
    # Preserve every prior field and verbatim record; append this iteration only.
    for filename,expected in [('COMMENTS.json',104),('ROWS.json',256)]:
        records=json.loads((BASE/filename).read_text());assert len(records)==expected
        for r in records:r['r8_02_i1']=dict(exported_items_equal=True,verdict='Inherited R7/latest disposition unchanged; no new physical fix claimed',output='runtime/'+r['page']+'.json',prior_source=str(BASE/filename))
        dump(OUT/filename,records)
    # Native context and final-only review overviews. Discounted polygons never
    # enter these review outputs. Separate raw diagnostic sheets show exclusions.
    selected=set(json.loads((OUT/'paired-controls.json').read_text()))
    selected.update(r['page'] for r in json.loads((OUT/'support-v1/results.json').read_text()))
    selected.update(r['page'] for r in json.loads((BASE/'COMMENTS.json').read_text()) if r['id'] in {f'O{i:02}' for i in range(8,25)})
    gallery=OUT/'gallery';gallery.mkdir(exist_ok=True)
    cards=[]
    for row in rows:
        if row['page'] not in selected:continue
        p=row['page'];g=cv2.imread(row['path'],0);data=json.loads((OUT/'runtime'/f'{p}.evidence.json').read_text());final=json.loads((OUT/'runtime'/f'{p}.json').read_text())['items']
        panels=[]
        for name,items in [('Paddle',data['original']),('cb4d6b4 = candidate',final)]:
            v=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
            for q in items:cv2.polylines(v,[np.rint(q['polygon']).astype(np.int32)],True,(0,140,0),2)
            factor=min(1,1500/v.shape[0]);v=cv2.resize(v,None,fx=factor,fy=factor,interpolation=cv2.INTER_AREA)
            cv2.putText(v,name,(8,22),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,255),1);panels.append(v)
        cv2.imwrite(str(gallery/(p+'.jpg')),np.hstack(panels))
        if p.startswith('an-7792') or any(s in p for s in ['c99f','1ba3','00f143','fd4fa','922e','1be6','e745']):
            # Six horizontal native strips retain page context without shrinking
            # the feature into a whole-page thumbnail.
            for j,part in enumerate(np.array_split(g,6,axis=0)):
                cv2.imwrite(str(gallery/f'{p}.raw-{j}.jpg'),part)
        cards.append(f'<figure><figcaption>{html.escape(p)}</figcaption><a href="gallery/{p}.jpg"><img loading="lazy" src="gallery/{p}.jpg"></a></figure>')
    links=[]
    for sub in ('propagation','support-v1','frame-native','source-audit','retention-ablation','controls'):
        for p in sorted((OUT/sub).glob('*.jpg')):
            rel=str(p.relative_to(OUT));links.append(f'<li><a href="{rel}">{rel}</a></li>')
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>R8-02 i1 ink evidence</title><style>body{font:16px system-ui;max-width:1400px;margin:2em auto}img{max-width:100%}figure{margin:2em 0}li{margin:.3em}</style><h1>R8-02 i1 — partial</h1><p>Final output is exact on all 208 pages. Fifteen exclusions change from propagated source attribution to the existing native faintness decision. Frame replacement is rejected. In the review panels: Paddle left, final cb4d6b4 = candidate right; only final kept polygons are shown. Separate diagnostics show raw exclusions and unresolved support.</p><p>Frame diagnostics: raw left, native selected-unit pixels blue, unresolved observed support red, current polygon green. Faintness diagnostics: raw left, component photometry right; green means normal relative to this population, not front-source proof. DN ablation: red lost pixels, green added pixels; not all thresholded pixels are text.</p><h2>Native diagnostic sheets</h2><ul>'+''.join(links)+'</ul><h2>Final-only review controls</h2>'+''.join(cards))


if __name__=='__main__':main()
