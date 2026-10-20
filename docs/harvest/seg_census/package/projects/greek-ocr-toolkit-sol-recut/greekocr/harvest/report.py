"""Complete-sample gallery and auditable yield, noise, characters and cost tables."""
from pathlib import Path
from collections import Counter, defaultdict
import csv, html, json, math, shutil, statistics, unicodedata, xml.etree.ElementTree as ET
from .core import RARE, STACK_COMMIT, normalise
from .pipeline import collect, polygon_crop
from .readers import atomic


def table(headers, rows):
    return ['| '+' | '.join(map(str,headers))+' |', '| '+' | '.join('---' for _ in headers)+' |'] + ['| '+' | '.join(map(str,r))+' |' for r in rows]


def wilson(k,n):
    if not n: return None
    z=1.96;p=k/n;den=1+z*z/n;centre=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,centre-half),min(1,centre+half)]


def review(records, root, summary):
    chosen=sorted((r for r in records if r.get('sampled')),key=lambda r:(r['source'],r['decade'],r['book'],r['page'],r['id']))
    images=root/'pilot_review_images';images.mkdir(exist_ok=True)
    esc=lambda s:html.escape(str(s));cards=[];previous=None
    for r in chosen:
        refs={}
        for kind in ('raw','straight'):
            name=r['id']+'.'+kind+'.png'
            shutil.copyfile(r[kind+'_crop'],images/name);refs[kind]='pilot_review_images/'+name
        group=(r['source'],r['decade'])
        if group!=previous:
            cards.append(f'<h2 class="group" data-decade="{r["decade"]}">{esc(r["source"])} · {r["decade"]}s</h2>');previous=group
        readers=r['readers'];flags=r['gates']['flags']+r.get('tags',[])
        flags += [f for v in readers.values() for f in v.get('flags',[])]
        reading=[]
        for e,title in (('vision','Vision · el + grc'),('docai','Document AI')):
            v=readers.get(e,{})
            confidence=v.get('mean_confidence');conf='—' if confidence is None else f'{confidence:.3f}'
            reading.append(f'<div class="reading"><b>{title}<small>confidence {conf}</small></b><p lang="el">{esc(v.get("text") or v.get("raw_text") or "— (empty / unavailable)")}</p></div>')
        cards.append(f'''<article id="{esc(r['id'])}" data-source="{esc(r['source'])}" data-decade="{r['decade']}" data-tier="{r['tier']}">
<header><strong>{esc(r['provenance']['catalogue']['title'])}</strong><span>{r['year']} · page {r['page']} · <b class="tier {r['tier']}">{r['tier']}</b></span></header>
<img loading="lazy" src="{refs['straight']}" alt="Straightened line {esc(r['id'])}">
<details><summary>Raw polygon crop</summary><img loading="lazy" src="{refs['raw']}" alt="Raw polygon line {esc(r['id'])}"></details>
{''.join(reading)}
<div class="reading weak"><b>Text layer</b><p>None — Anemi scan; two Google readers only.</p></div>
<p class="flags">{esc(', '.join(sorted(set(flags))) or 'All gates passed')}</p>
{('<p class="flags">Visual review: '+esc(' '.join(v['note'] for v in r.get('visual_review_notes',[])))+'</p>') if r.get('visual_review_notes') else ''}
<p class="muted">{esc(r['id'])} · {r['features']['width']} × {r['features']['height']} px · band width {100*r['features']['width_band_ratio']:.1f}% · paragraph {esc(r['gates']['paragraph_position'])} · contrast {r['features']['faintness_proxy']:.1f} · x-height {r['features']['x_height_estimate']:.1f} px · stack {STACK_COMMIT[:7]}</p>
<p class="muted"><a href="{esc(r['provenance']['catalogue']['volumes'][0]['viewer_url'])}">Catalogue viewer</a> · <a href="{esc(r['provenance']['source_url'])}">Source page</a></p>
</article>''')
    options=lambda field:'<option value="">All '+field+'s</option>'+''.join(f'<option>{esc(v)}</option>' for v in sorted({str(r[field]) for r in chosen}))
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>T13c · Anemi sample review</title><style>
:root{--bg:#f3f5f6;--surface:#fff;--fg:#1a1f25;--muted:#5a6470;--rule:#d6dce1;--accent:#0d6e72}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif}.wrap{max-width:1640px;margin:auto;padding:28px 20px 64px}h1{font:32px Georgia,serif;margin:0 0 12px}h2{font:24px Georgia,serif;padding-top:28px;border-top:2px solid var(--accent)}p{margin:8px 0}a{color:var(--accent)}nav{display:flex;gap:12px;flex-wrap:wrap;position:sticky;top:0;background:var(--bg);padding:12px 0;z-index:1;border-bottom:1px solid var(--rule)}select{max-width:100%;padding:8px;font:inherit;border:1px solid var(--rule);background:var(--surface);border-radius:4px}article{background:var(--surface);padding:18px;margin:22px 0;border:1px solid var(--rule);border-radius:5px;min-width:0}header{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;overflow-wrap:anywhere;margin-bottom:12px}header strong{max-width:100%;font-weight:500}header span{flex-shrink:0;max-width:100%}img{display:block;max-width:100%;height:auto;background:white;border:1px solid var(--rule);margin:8px 0}.reading{display:grid;grid-template-columns:160px minmax(0,1fr);gap:16px;border-top:1px solid var(--rule);padding:10px 0}.reading p{font:20px/1.6 Georgia,serif;white-space:pre-wrap;overflow-wrap:anywhere;margin:0}.reading small{display:block;font:12px/1.5 ui-monospace,Menlo,monospace;color:var(--muted)}.weak{color:var(--muted)}.weak p{font:14px/1.5 -apple-system,sans-serif}.muted,.flags{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted);overflow-wrap:anywhere}details summary{cursor:pointer;color:var(--accent)}.tier{font-weight:600}.tier1{color:#23764a}.tier2{color:#936200}.tier3,.rejected{color:#b42318}[hidden]{display:none!important}@media(max-width:600px){.wrap{padding:16px 10px}h1{font-size:26px}article{padding:12px}.reading{grid-template-columns:1fr;gap:4px}.reading p{font-size:18px}nav{gap:6px}select{font-size:13px}}@media print{nav{position:static}article{break-inside:avoid}details{display:none}}
</style></head><body><main class="wrap"><h1>T13c · Anemi sample review</h1>'''
    page+=f'<p>All <b>{len(chosen)} sampled long lines</b>, grouped by source and decade. {summary["represented_books"]} of 150 books supplied passing lines from 300 middle pages. Internal review · CC BY-NC-ND.</p>'
    page+=f'<p>{summary["tier1"]} tier 1 · {summary["tier2"]} tier 2 · {summary["tier3"]} tier 3 · {summary["sample_rejected"]} reader rejects. Google list-price reservations USD {summary["cost_usd"]:.3f}. <a href="PILOT_v1.md">Report</a> · <a href="pilot_v1/summary.json">Summary</a></p>'
    page+='<p>Agreement supplies provisional labels; two readers from one vendor can share errors. Tier 3 keeps both readings without a label. Zero-yield books and gate failures remain in the report.</p>'
    page+='<nav>'+''.join(f'<label>{field.title()} <select id="{field}">{options(field)}</select></label>' for field in ('source','decade','tier'))+'<span id="count" aria-live="polite"></span></nav>'+''.join(cards)
    page+='''</main><script>const fields=['source','decade','tier'];function filter(){let n=0;document.querySelectorAll('article').forEach(a=>{a.hidden=fields.some(k=>document.getElementById(k).value&&a.dataset[k]!==document.getElementById(k).value);if(!a.hidden)n++});document.querySelectorAll('.group').forEach(h=>h.hidden=!Array.from(document.querySelectorAll('article')).some(a=>!a.hidden&&a.dataset.decade===h.dataset.decade));document.getElementById('count').textContent=n+' lines'}fields.forEach(k=>document.getElementById(k).addEventListener('change',filter));filter();</script></body></html>'''
    (root/'pilot_review.html').write_text(page)
    atomic(root/'pilot_v1/review_selection.json',dict(rule='ALL sampled lines; no subsampling',ids=[r['id'] for r in chosen],cards=len(chosen)))
    return chosen


def failure_examples(records,out):
    from PIL import Image
    examples={};directory=out/'failure_images';directory.mkdir(exist_ok=True)
    for r in records:
        flags=r['gates']['flags']+r.get('tags',[])+[f for v in r['readers'].values() for f in v.get('flags',[]) if v.get('rejected')]
        if r.get('sampled') and r['tier']=='tier3': flags=flags+['reader_disagreement']
        for flag in flags:
            if flag in examples:continue
            raw=r.get('raw_crop')
            if raw is None:
                with Image.open(r['provenance']['page_image']) as page: im=polygon_crop(page,r['polygon'])
                crop_root=Path(r['provenance']['page_image']).parent.parent/'crops'/r['page_id']
                crop_root.mkdir(parents=True,exist_ok=True)
                p=crop_root/(r['id']+'.raw.png');im.save(p);raw=str(p.resolve());r['raw_crop']=raw
            dest=directory/(r['id']+'.raw.png')
            if Path(raw).resolve()!=dest.resolve(): shutil.copyfile(raw,dest)
            examples[flag]=dict(id=r['id'],book=r['book'],page=r['page'],crop='pilot_v1/failure_images/'+dest.name,
                page_image=r['provenance']['page_image'],sampled=r.get('sampled',False))
    atomic(out/'failure_examples.json',examples)
    return examples


def report(out):
    out=Path(out);root=out.parent;pages,records=collect(out)
    sampling=json.loads((out/'sampling.json').read_text());sampled=[r for r in records if r.get('sampled')]
    observations_path=out/'visual_observations.json'
    observations=json.loads(observations_path.read_text()) if observations_path.exists() else {}
    for r in records:
        if r['id'] in observations.get('by_id',{}): r['visual_review_notes']=observations['by_id'][r['id']]
    cost=json.loads((out/'cost_receipt.json').read_text()) if (out/'cost_receipt.json').exists() else {'cost_usd':0.,'calls_reserved':0}
    counts=Counter(r['tier'] for r in sampled);groups=defaultdict(list);pgroups=defaultdict(list)
    for r in records:groups[('Anemi',str(r['decade']))].append(r)
    for p in pages:pgroups[('Anemi',str(p['decade']))].append(p)
    yields=[];noise=[]
    for key in sorted(pgroups):
        rows=groups[key];sample_rows=[r for r in rows if r.get('sampled')];c=Counter(r['tier'] for r in sample_rows)
        measured=[r for r in sample_rows if all(r['readers'].get(e,{}).get('status')=='ok' for e in ('vision','docai'))]
        usable=[r for r in measured if all(not r['readers'][e]['rejected'] for e in ('vision','docai'))]
        disagree=sum(normalise(r['readers']['vision']['text'])!=normalise(r['readers']['docai']['text']) for r in usable)
        yields.append(dict(source=key[0],decade=key[1],books=len({p['book'] for p in pgroups[key]}),pages=len(pgroups[key]),
            lines_found=len(rows),survived_gates=sum(r['gates']['accepted'] for r in rows),sampled=len(sample_rows),
            **{k:c[k] for k in ('tier1','tier2','tier3')},rejected=c['rejected'],unread=c['unread'],
            gate_rejected=sum(not r['gates']['accepted'] for r in rows)))
        noise.append(dict(source=key[0],decade=key[1],sampled=len(sample_rows),paired=len(measured),usable_pairs=len(usable),
            exact_disagreements=disagree,disagreement_rate=disagree/len(usable) if usable else None,wilson95=wilson(disagree,len(usable)),
            disagreement_after_substitutions=sum(r['tier']!='tier1' for r in usable)/len(usable) if usable else None))
    characters=defaultdict(Counter)
    for r in sampled:
        for e,v in r['readers'].items():characters[('Anemi',e)].update(v.get('raw_text',''))
    char_rows=[dict(source=s,engine=e,character=ch,codepoint=f'U+{ord(ch):04X}',name=unicodedata.name(ch,'UNNAMED'),count=n)
        for (s,e),c in sorted(characters.items()) for ch,n in sorted(c.items(),key=lambda x:ord(x[0]))]
    with (out/'characters.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=['source','engine','character','codepoint','name','count']);w.writeheader();w.writerows(char_rows)
    reasons=Counter(f for r in records for f in r['gates']['flags'])
    reader_reasons=Counter(f for r in sampled for v in r['readers'].values() if v.get('rejected') for f in v.get('flags',[]))
    timings=defaultdict(list)
    for p in pages:
        for stage,v in p['timing'].items():
            if isinstance(v,(int,float)):timings[stage].append(v)
    service=defaultdict(lambda:defaultdict(float))
    for r in sampled:
        for e,v in r['readers'].items():service[r['page_id']][e]+=v.get('elapsed_s',0.)
    for e in ('vision','docai'):timings[e+'_elapsed_s']=[service[p['id']][e] for p in pages]
    timing_summary={k:dict(mean=statistics.mean(v),median=statistics.median(v),p95=sorted(v)[math.ceil(.95*len(v))-1],sum=sum(v)) for k,v in timings.items() if v}
    with (out/'timings_per_page.csv').open('w') as f:
        fields=['page_id','book','decade']+list(timings)
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for p in pages:w.writerow(dict(page_id=p['id'],book=p['book'],decade=p['decade'],**{k:(service[p['id']][k[:-10]] if k.endswith('_elapsed_s') else p['timing'][k]) for k in timings}))
    limitations=['Agreement is provisional; both readers share a vendor and can share errors.',
        'Noise is strict NFD reader disagreement, not CER against ground truth. Wilson intervals ignore book clustering.',
        'Selection is purposive: long complete rows from middle pages, with three per eligible book and at most four. It estimates sample behaviour, not the full Anemi population.',
        'Some books supply zero passing lines on the two requested pages; no gate was relaxed to manufacture coverage.',
        'No independent third reader or rare-glyph gold/exposure denominator; zero emissions do not establish incapability.',
        'Page/column, table, clipping and neighbour gates are heuristic. Undetected clipping, stamps and faint ink can remain.',
        'Unsampled geometry survivors were not straightened or read. Cheap features unmeasured on early rejects are null; chars/100px requires a reader.',
        'External script and destination writes were denied by the filesystem sandbox; the tested local amended fetcher and repository harvest_big are used.']
    validation_path=out/'artifact_validation.json'
    validation=json.loads(validation_path.read_text()) if validation_path.exists() else {}
    if validation.get('browser_render',{}).get('ok') is False:
        limitations.append('Browser pixel QA is unavailable: headless Chrome launch failed (TargetClosedError); automatic approval review denied Firefox access, so visible handoff is unverified.')
    test_count=None
    if (out/'tests.xml').exists():
        tree=ET.parse(out/'tests.xml').getroot();suites=[tree] if tree.tag=='testsuite' else list(tree)
        test_count=sum(int(t.attrib.get('tests',0))-sum(int(t.attrib.get(k,0)) for k in ('failures','errors','skipped')) for t in suites)
    summary=dict(schema='harvest-pilot-summary-2',task='T13c',stack_commit=STACK_COMMIT,target_books=150,
        represented_books=sampling['represented_books'],zero_books=sampling['zero_books'],pages=len(pages),lines_found=len(records),
        survived_gates=sum(r['gates']['accepted'] for r in records),sampled=len(sampled),
        **{k:counts[k] for k in ('tier1','tier2','tier3')},sample_rejected=counts['rejected'],sample_unread=counts['unread'],
        rejected=counts['rejected']+sum(not r['gates']['accepted'] for r in records),
        unread=sum(r['tier']=='unread' for r in records),
        gate_rejected=sum(not r['gates']['accepted'] for r in records),unsampled=sum(not r.get('sampled') for r in records),
        cost_usd=cost['cost_usd'],cost=cost,yield_by_source_decade=yields,noise_by_source_decade=noise,
        exact_disagreement_rate=sum(n['exact_disagreements'] for n in noise)/max(1,sum(n['usable_pairs'] for n in noise)),
        gate_reasons=dict(reasons),reader_rejection_reasons=dict(reader_reasons),timings_per_page=timing_summary,
        rare_characters={f'{s}|{e}':{ch:c[ch] for ch in RARE} for (s,e),c in characters.items()},
        rare_substitution_lines=sum('rare_glyph_substitution' in r.get('tags',[]) for r in sampled),limitations=limitations,
        visual_review_scope=observations.get('inspection_scope'),
        tests_passed=test_count,artifact_validation=validation,
        complete=len(pages)==300 and len(sampled)<=500 and not counts['unread'],montage=False)
    atomic(out/'summary.json',summary);review(records,root,summary);examples=failure_examples(records,out)
    # Persist newly materialized failure crops without changing decisions.
    from .pipeline import persist
    persist(out,pages,records)
    lines=['# T13c — H1 Anemi pilot sample','',
        f'**{len(pages)} pages from all 150 target books; {len(sampled)} sampled long lines from {summary["represented_books"]} books.** Tier 1: **{counts["tier1"]}**; tier 2: **{counts["tier2"]}**; tier 3: **{counts["tier3"]}**; reader rejected: **{counts["rejected"]}**. Google list-price reservations: **USD {cost["cost_usd"]:.3f}**.',
        '', 'Only Anemi; two contiguous middle pages per proposal book, across volumes. No Vouli and no text-layer third vote. Owner 12 October 01:20/01:35 instructions supersede the initial broad pilot. No training set was produced.',
        '',f'Frozen stack `{STACK_COMMIT}`: all 256 exported files match canonical Git blobs ([receipt](pilot_v1/stack_verification.json)). Every line carries source catalogue, public page URL, page-PDF receipt/hash, stack commit and model/source hashes. Images are files under `harvest_big`, never embedded in JSONL.',
        '', '## Yield by source and decade','']
    cols=['source','decade','books','pages','lines_found','survived_gates','sampled','tier1','tier2','tier3','rejected','unread']
    lines+=table(['Source','Decade','Books','Pages','Found','Crop gates','Sampled','Tier 1','Tier 2','Tier 3','Reader reject','Unread'],[[y[k] for k in cols] for y in yields])
    totals={k:sum(y[k] for y in yields) for k in cols[2:]}
    lines+=['| Anemi | ALL | '+' | '.join(str(totals[k]) for k in cols[2:])+' |','',
        f'Geometry rejects: {summary["gate_rejected"]}; unsampled lines: {summary["unsampled"]}. Found means final `Stack().items`; suppressed candidates are separate in page receipts. Crop-gate survivors include unselected candidates; only ranked sampling candidates receive the straightener/clipping check. Reader-tier columns apply only to the sample.',
        '', '## Sampling and book coverage','',
        'Minimum width = 80% of the observed column text band. Short paragraph starts/ends, page/gutter-edge touches, tall rows, bend-trigger pages and table pages are excluded. Full-width paragraph interiors rank first; candidate order alternates the two pages. Three rounds cover each eligible book before fourth lines; rich books (≥12 pre-straightener candidates) receive at most one extra, round-robin by decade. Rejected straightener candidates are replaced before the sample is frozen. Selection never uses OCR agreement.',
        '',f'{len(summary["zero_books"])} books yield zero; [every book and its selected count](pilot_v1/sampling.json). Empty books remain in the denominator. [Exact proposal and path receipt](pilot_v1/run_manifest.json).','']
    if summary['zero_books']:
        catalog={p['book']:p['catalogue'] for p in pages}
        lines+=table(['Zero-yield book','Year','Page gate flags'],[[f'[{catalog[b]["title"]}]({catalog[b]["volumes"][0]["viewer_url"]})',catalog[b]['year'],', '.join(sorted({f for p in pages if p['book']==b for f in p['page_gate']['flags']})) or 'no long complete crop survives'] for b in summary['zero_books']])
    lines+=['','## Reader disagreement — sample noise proxy','']
    fmt=lambda v:'—' if v is None else f'{100*v:.1f}%'
    lines+=table(['Source','Decade','Sampled','Paired OK','Usable pairs','Strict disagreement','After substitutions','95% Wilson'],[[n['source'],n['decade'],n['sampled'],n['paired'],n['usable_pairs'],fmt(n['disagreement_rate']),fmt(n['disagreement_after_substitutions']),'—' if n['wilson95'] is None else '–'.join(fmt(x) for x in n['wilson95'])] for n in noise])
    lines+=['',f'Overall strict disagreement: **{fmt(summary["exact_disagreement_rate"])}** over {sum(n["usable_pairs"] for n in noise)} usable pairs. Denominator excludes service errors and geometric list-return rejects. It does not measure accuracy or population noise.',
        '', 'Side-by-side pieces in one vertical band are joined in x order. Stacked bands are rejected. Foreign-script/punctuation garbage outside the main row is dropped; garbage inside the row obstructs the crop and rejects it. Raw texts, all boxes, dropped pieces and confidences remain recorded.',
        '', 'Tier 1 = exact NFD/whitespace agreement, including tagged documented substitutions; tier 2 = ≤2 NFD edits; tier 3 = both usable readings disagree, with no label. Empty/obstructed/garbage pairs are rejected. No third-vote tier applies.',
        '', '## Character emissions by source','', '[Full raw character table](pilot_v1/characters.csv). Counts include raw output before list cleanup, including rejected reads.','']
    lines+=table(['Source','Reader','Characters','Distinct','NFD combining marks','Greek letters'],[[s,e,sum(c.values()),len(c),sum(unicodedata.combining(x)!=0 for ch,n in c.items() for x in unicodedata.normalize('NFD',ch) for _ in range(n)),sum(n for ch,n in c.items() if ch.isalpha() and 'GREEK' in unicodedata.name(ch,''))] for (s,e),c in sorted(characters.items())])
    lines+=['','Rare-glyph rows; zero means absent in this sample output.','']+table(['Source','Reader']+list(RARE),[[s,e]+[c[ch] for ch in RARE] for (s,e),c in sorted(characters.items())])
    lines+=['',f'Rare substitution tags: **{summary["rare_substitution_lines"]} lines**. Whole-word DocAI κὶ/κὰ/κὴ → Vision καὶ and χείριςον → χείρισον/χείρισὸν only, as documented in [the engine comparison](VISION_VS_DOCAI_v1.md). Other differences must still match exactly for tier 1. These are expected glyph substitutions, not confirmed rare-ink labels; no broad sigma or accent folding.',
        '', '## Google cost receipt','',f'{cost["calls_reserved"]} single-crop request reservations, by reader `{cost.get("calls_by_engine",{})}`. USD 0.0015 per request; no monthly free allowance deducted. Persisted cross-process reservations enforce both ≤1000 calls and USD 3. No montage and no implicit retry. Interrupted reserved attempts fail closed.',
        '', 'Rates checked 12 October 2026: [Vision pricing](https://cloud.google.com/vision/pricing), [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). This conservative receipt counts failures/ambiguous attempts; it is not a billing-console invoice. [Cost receipt](pilot_v1/cost_receipt.json). The archived earlier pilot reserved two calls (USD 0.003), separately retained in the run manifest.',
        '', '## Timings per stage per page','', '[All page timings](pilot_v1/timings_per_page.csv) · [Native stack substage receipts](pilot_v1/page_gates.json).','']
    lines+=table(['Stage','Mean s/page','Median','p95','Total s'],[[k]+[f'{v[x]:.3f}' for x in ('mean','median','p95','sum')] for k,v in timing_summary.items()])
    lines+=['','Service times sum call elapsed times within each page; both readers and four crop pairs run concurrently, so these sums are not wall time. Straightener timings include replacement attempts. Rendering uses 200 dpi grayscale; `separate_lines(tight=True, margin=0.2)` preserves the raw polygon crop.',
        '', '## Ten most common gate reasons','']+table(['Reason','Line flags'],reasons.most_common(10))
    lines+=['','Page flags propagate to each excluded line; overlapping flags do not sum to rejects. Stack catalogue suppressions (frames/ornaments/seal rims/faintness) are counted separately per page. Reader rejection flags: `'+str(dict(reader_reasons))+'`.',
        '', '## Failure modes and crop links','']
    for flag,ex in sorted(examples.items()):
        link=f'[sample card](pilot_review.html#{ex["id"]})' if ex['sampled'] else 'unsampled gate example'
        lines.append(f'- `{flag}`: [raw crop]({ex["crop"]}), {link}, page {ex["page"]}; `{ex["id"]}`.')
    observations=out/'visual_observations.json'
    if observations.exists():lines+=['','Visual observations:','']+['- '+v for v in json.loads(observations.read_text()).get('observations',[])]
    lines+=['','Limitations:','']+['- '+v for v in limitations]
    lines+=['','## Acquisition, outputs and verification','',
        'The source fetch script and requested external destination denied writes under the session sandbox. [Minimal upstream patch](pilot/o4b_anemi_pages.patch) · [executed amended copy](pilot/_fetch/o4b_anemi_pages.py). Actual source pages: `docs/harvest/harvest_big/anemi_wave3_sample_t13c/`; page/crop images: `docs/harvest/harvest_big/t13c/`. Plan/fetch/verify preserve hash-bound resumability and the ≥2-second transport rate. Credentials remain in memory/environment, never printed or written.',
        '', '[All sampled cards](pilot_review.html) · [All found line records](pilot_v1/records.jsonl) · [Summary](pilot_v1/summary.json) · [Fetch verification](pilot_v1/anemi_verification.json) · [Tests](pilot_v1/tests.log) · [API](../API.md) · [Inventory](../INVENTORY.md).','']
    lines += [f'Offline validation: **{test_count} tests passed** (harvest, Google-reader contracts and CLI/API/provenance tests). Artifact audit checks all {len(records):,} records, {len(sampled)} gallery IDs, {2*len(sampled):,} crop image references, all reader image hashes and source-secret absence. [Artifact receipt](pilot_v1/artifact_validation.json).', '']
    if (out/'run_manifest.json').exists():
        run=json.loads((out/'run_manifest.json').read_text());acq=Path(run['actual_destination'])/'last_wave.json'
        if acq.exists():
            wave=json.loads(acq.read_text());saved_bytes=sum(Path(p['pdf']).stat().st_size for p in pages)
            lines += [f'Acquisition verification: {len({p["book"] for p in pages})}/150 records, {len(pages)}/300 pages, {saved_bytes:,} saved PDF bytes; {run["seeded_receipted_pages"]} pages reused from verified receipts and {wave["pages"]} newly fetched. New HTTP bodies total {wave["bytes"]:,} bytes including descriptors/login/robots overhead.', '']
    (root/'PILOT_v1.md').write_text('\n'.join(lines))
    return summary
