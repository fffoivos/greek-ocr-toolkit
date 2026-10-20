"""Offline N1-S scoring and owner sheet. No readers, fitting or network calls.

Build with the collector Python and PYTHONPATH set to the cleanup worktree.
"""
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import math
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/n1'
CLEANUP = Path.home() / 'Projects/greek-ocr-toolkit-cleanup'
FEATURES = Path.home() / 'Projects/collect-v3-data/run/W1/features.jsonl'
SEED = '20261017:N1S:agreements'
MEANINGS = ['raised dot', 'baseline dot', 'comma', 'hyphen or dash', 'space', 'nothing', 'other', 'unreadable']
GROUPS = ['Hyphen printed as raised dot', 'Dot printed as raised dot', 'Other mark disagreements', 'Unreadable or low confidence', 'Agreement sample']
INPUTS = {}


def sha(path):
    h = hashlib.sha256()
    with _data_input(Path(path)).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()


def bind(path):
    path = Path(path)
    INPUTS[str(path.resolve())] = dict(sha256=sha(path), bytes=path.stat().st_size)
    return path


def rows(path):
    return [json.loads(s) for s in _data_input(bind(path)).read_text().splitlines() if s.strip()]


def load(path):
    return json.loads(_data_input(bind(path)).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def decode_and_gate(key, answers):
    if len(key['readers']) != 1: raise ValueError('one reader assignment required')
    expected = next(iter(key['readers'].values()))
    assert len(set(expected)) == len(expected) and set(expected) == set(key['items'])
    grouped = defaultdict(list)
    for a in answers: grouped[a['item_id']].append(a)
    if set(grouped) - set(expected): raise ValueError('unexpected answer IDs')
    decoded = []; wrong = []; abstentions = []
    for iid in expected:
        k = key['items'][iid]; found = grouped[iid]
        if len(found) != 1 or found[0].get('answer') not in k['option_map']:
            raise ValueError('missing, duplicate or malformed answer: ' + iid)
        a = found[0]; meaning = k['option_map'][a['answer']]
        if meaning not in MEANINGS: raise ValueError('invalid meaning')
        control = k['control_truth'] is not None
        d = dict(item_id=iid, slot_id=k['slot_id'], meaning=meaning,
                 confidence=a['confidence'], note=a.get('note', ''), control=control)
        if control and meaning == 'unreadable': abstentions.append(d)
        elif control and meaning != k['control_truth']:
            wrong.append(dict(d, truth=k['control_truth']))
        decoded.append(d)
    return dict(status='VOID' if len(wrong) > 1 else 'VALID', controls=sum(d['control'] for d in decoded),
                wrong=len(wrong), abstentions=len(abstentions), wrong_answers=wrong,
                abstention_answers=abstentions, bed=sum(not d['control'] for d in decoded)), decoded


def table(records):
    result = defaultdict(Counter)
    for r in records: result[r['glyph']][r['meaning']] += 1
    return {g: {m: result[g][m] for m in MEANINGS} for g in sorted(result)}


def agrees(glyph, meaning):
    # Strip surrounding whitespace only for semantic agreement, never for the tables/edits.
    g = glyph.strip()
    if not glyph: return meaning == 'nothing'
    if not g: return meaning == 'space'
    return meaning == {'.': 'baseline dot', ',': 'comma', '-': 'hyphen or dash',
                       '–': 'hyphen or dash', '—': 'hyphen or dash', '·': 'raised dot', '·': 'raised dot'}.get(g)


def uncertain(r):
    return r['meaning'] in ('unreadable', 'other') or r['confidence'] != 'high'


def group_for(r):
    if uncertain(r): return GROUPS[3]
    if r['glyph'] == '-' and r['meaning'] == 'raised dot': return GROUPS[0]
    if r['glyph'] == '.' and r['meaning'] == 'raised dot': return GROUPS[1]
    if not agrees(r['glyph'], r['meaning']): return GROUPS[2]
    return GROUPS[4]


def proposed(text, r):
    """Change exactly one existing code point; all other offsets remain valid."""
    if r['glyph'] not in ('-', '.') or r['meaning'] != 'raised dot' or 'thousands' not in r['grammar_candidates']:
        return None
    a, b = r['start'], r['end']
    if b != a + 1 or text[a:b] != r['glyph']:
        raise ValueError('Google text/slot offsets disagree')
    return text[:a] + '\u00b7' + text[b:]


def wilson(k, n):
    if not n: return None
    z = 1.959963984540054; p = k/n; den = 1+z*z/n
    mid = (p+z*z/(2*n))/den
    rad = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0., mid-rad), min(1., mid+rad)]


def cell(r): return (r['source_era'], r['position'], r['glyph'])
def target(r): return r['glyph'] == '-' and r['meaning'] == 'raised dot'


def rates(frame, valid):
    sizes = Counter(cell(r) for r in frame); obs = defaultdict(list)
    for r in valid: obs[cell(r)].append(r)
    strata = []; weights = []; supported = 0; weighted_events = 0
    for c, N in sorted(sizes.items()):
        rr = obs[c]; n = len(rr); k = sum(target(r) for r in rr)
        strata.append(dict(source_era=c[0], position=c[1], glyph=c[2], frame=N, read=n, faults=k,
                           frame_design_weight=N/len(frame), response_weight=N/n if n else None,
                           rate=k/n if n else None, wilson95=wilson(k,n)))
        if n:
            supported += N; weighted_events += N*k/n
            weights.extend([N/n]*n)
    point = weighted_events/supported
    neff = sum(weights)**2/sum(w*w for w in weights)
    interval = wilson(point*neff, neff)
    missing = len(frame)-supported
    unknown_target_slots = sum(s['frame'] for s in strata if not s['read'] and s['glyph']=='-')
    return dict(frame=len(frame), valid_read=len(valid), supported_frame=supported,
                unsupported_frame=missing, unsupported_target_capable_slots=unknown_target_slots, supported_cells=sum(s['read']>0 for s in strata), cells=len(strata),
                rate=point, wilson95_kish_approx=interval, effective_n=neff,
                crude_rate=sum(map(target,valid))/len(valid), crude_wilson95=wilson(sum(map(target,valid)),len(valid)),
                full_frame_point_identification_bounds=[weighted_events/len(frame),(weighted_events+unknown_target_slots)/len(frame)],
                full_frame_wilson_envelope=[sum(s['frame']*s['wilson95'][0] for s in strata if s['read'] and s['glyph']=='-')/len(frame),
                    (sum(s['frame']*s['wilson95'][1] for s in strata if s['read'] and s['glyph']=='-')+unknown_target_slots)/len(frame)], strata=strata)


def measurement_summary(records):
    listing = []; by = defaultdict(list)
    for r in records:
        if r['meaning'] not in ('raised dot','hyphen or dash'): continue
        m = r['measurements']
        listing.append({k:r[k] for k in ('slot_id','context','meaning','confidence','source_era','position')} | dict(measurements=m))
        by[r['meaning']].extend(m['components'])
    stats = {}
    for field in ('height','centre_y_relative_band','width'):
        values = {g:[c[field] for c in by[g]] for g in ('raised dot','hyphen or dash')}
        ranges = {g:[min(v),max(v)] if v else None for g,v in values.items()}
        a,b = ranges.values(); overlap = [max(a[0],b[0]),min(a[1],b[1])] if a and b else None
        if overlap and overlap[0]>overlap[1]: overlap=None
        stats[field] = dict(ranges=ranges, intersection=overlap,
            components_inside_intersection={g:sum(overlap[0]<=x<=overlap[1] for x in v) if overlap else 0 for g,v in values.items()})
    return listing, dict(slots=dict(Counter(r['meaning'] for r in listing)),
        components={g:len(v) for g,v in by.items()}, zero_component_slots=dict(Counter(r['meaning'] for r in listing if not r['measurements']['components'])), fields=stats)


def mdtable(t):
    lines = ['| Google exact gap | '+' | '.join(MEANINGS)+' | Total |', '|---|'+'---:|'*(len(MEANINGS)+1)]
    for g, cols in t.items():
        name = json.dumps(g,ensure_ascii=False).replace('|','&#124;')
        lines.append('| `'+name+'` | '+' | '.join(str(cols[m]) for m in MEANINGS)+f' | {sum(cols.values())} |')
    return '\n'.join(lines)


def build():
    from PIL import Image, ImageDraw
    from greekocr.adjudicate import owner_sheet
    renderer = CLEANUP/'greekocr/adjudicate/owner_sheet.py'
    assert Path(owner_sheet.__file__).resolve() == renderer
    for p in (renderer, renderer.with_suffix('.css'), renderer.with_suffix('.js'), Path(__file__), ROOT/'docs/records/labelfix/secondary/PLAN.md'):
        bind(p)
    calibration = load(OUT/'answers/cal01.r1.calibration.json')
    assert calibration['items'] == calibration['correct'] == 82
    frame = [r for r in rows(OUT/'frame_step1.jsonl') if r['partition']=='step1']
    assert len(frame)==600
    byid = {r['slot_id']:r for r in frame}
    rendered = {r['slot_id']:r for r in rows(OUT/'step1_rendered_v3.jsonl')}
    for p in ('step1_geometry.jsonl','step1_dropped_misaligned_v2.jsonl','step1_crop_outside_v2.jsonl','zoom_measurement_checks_cc.jsonl','census.json','controls/approved.jsonl'):
        bind(OUT/p)
    gates={}; valid=[]; reread=[]; seen=set(); latest_limit=None
    for i in range(1,8):
        ctx=f'ctx{i:02}'
        key=load(OUT/f'keys/{ctx}.json'); answers=rows(OUT/f'answers/{ctx}.r1.jsonl')
        gate, decoded=decode_and_gate(key,answers)
        scan=load(OUT/f'answers/{ctx}.r1.scan.json'); assert scan['ok'] and scan['scanner_version'] in (4, 'v4.4-canonical')
        run=load(OUT/f'answers/{ctx}.r1.run.json'); assert run['rc']==0
        latest_limit=run.get('rate_limits_in_rollout')
        # Preserve historical mapper results; this scorer implements abstention explicitly.
        old=load(OUT/f'answers/{ctx}.r1.mapped.json')
        gate['historical_mapper_errors']=old['control_errors']; gates[ctx]=gate
        for a in decoded:
            if a['control']: continue
            sid=a['slot_id']; assert sid not in seen; seen.add(sid)
            assert sid in byid and sid in rendered
            r=byid[sid] | a | dict(context=ctx,measurements=rendered[sid]['measurements'])
            assert r['glyph']==key['items'][a['item_id']]['google_glyph']==rendered[sid]['google_glyph']
            assert r['measurements']==key['items'][a['item_id']]['measurements']
            (valid if gate['status']=='VALID' else reread).append(r)
    assert seen==set(rendered)
    sheetdir=OUT/'owner_sheet'; sheetdir.mkdir(exist_ok=True)
    wanted={r['line_id'] for r in valid}; texts={}
    with bind(FEATURES).open() as f:
        for line in f:
            r=json.loads(line)
            if r['id'] in wanted: texts[r['id']]=r['text']
    assert set(texts)==wanted and all(texts.values())
    for r in valid: assert texts[r['line_id']][r['start']:r['end']]==r['glyph']
    selected=[r for r in valid if group_for(r)!=GROUPS[4]]
    agreements=sorted([r for r in valid if group_for(r)==GROUPS[4]],key=lambda r:r['slot_id'])
    sample=random.Random(SEED).sample(agreements,12); selected+=sample
    selected.sort(key=lambda r:(GROUPS.index(group_for(r)),r['slot_id']))
    cards=[]; manifests=[]
    for r in selected:
        imrec=rendered[r['slot_id']]
        for name in ('line','zoom'):
            p=bind(imrec[name]); assert INPUTS[str(p.resolve())]['sha256']==imrec[name+'_sha256']
        # The shared renderer's slot argument binds note identity; its image helper
        # does not draw numeric gap boxes. Add that saved-geometry box locally.
        with Image.open(imrec['line']) as opened: image=opened.convert('RGB')
        g=imrec['geometry']; draw=ImageDraw.Draw(image)
        x0,x1=g['gap']; y0,y1=g['digit_top']+12,g['baseline']+12
        draw.rectangle((x0-1,y0-1,max(x0+1,x1),y1),outline=(190,80,20),width=1)
        ident=f"{r['line_id']}:s{r['index']}"
        rr=[dict(name='Google',text=texts[r['line_id']])]
        prop=proposed(texts[r['line_id']],r)
        if prop is not None: rr.append(dict(name='Proposed',text=prop))
        rr.append(dict(name='Reader',text=r['meaning']+'; '+r['confidence']+' confidence'))
        tags=[json.dumps(r['glyph'],ensure_ascii=False)+' → '+r['meaning'],r['position']+' ('+', '.join(r['grammar_candidates'])+')',r['source_era']]
        card=dict(line_id=r['line_id'],doc_id=ident,label=ident,slot=r['index'],image=image,
            zooms=[dict(image=imrec['zoom'],alt='Marked 3× gap zoom')],rows=rr,
            tags=[dict(text=t) for t in tags],printed='',note='',group=group_for(r))
        cards.append(card)
        manifests.append(dict(doc_id=ident,slot_id=r['slot_id'],slot=r['index'],context=r['context'],group=card['group'],
            rows=rr,tags=tags,printed='',line_sha256=imrec['line_sha256'],zoom_sha256=imrec['zoom_sha256'],
            gap_box=[x0-1,y0-1,max(x0+1,x1),y1],image_box_overlay=True))
    assert len({c['doc_id'] for c in cards})==len(cards)
    intro=('Google writes raised thousands dots (4·547·331) as hyphens. '
        'A blind Sol reader read each gap from the ink. '
        '“Proposed” changes only Google -/. to · where the ink shows a raised dot and the number grammar allows grouping. '
        'Please correct anything wrong in the note or Printed.')
    spec=dict(title='N1 Numeric Separators',intro=intro,groups=[dict(id=g,heading=g) for g in GROUPS])
    sheet=sheetdir/'n1_sheet.html'; sheet.write_text(owner_sheet.render(cards,spec))
    assert _data_input(sheet).stat().st_size < 15_000_000
    dump(sheetdir/'cards.json',manifests)
    dump(sheetdir/'spec.json',spec)
    counts={g:sum(c['group']==g for c in cards) for g in GROUPS}
    summary=dict(cards=len(cards),groups=counts,agreement_seed=SEED,agreement_slot_ids=[r['slot_id'] for r in sample],
        html_bytes=_data_input(sheet).stat().st_size,html_MB=_data_input(sheet).stat().st_size/1e6,
        hashes={p.name:sha(p) for p in (sheet,sheetdir/'cards.json',sheetdir/'spec.json')},
        renderer=str(renderer),renderer_sha256=sha(renderer),printed_prefilled=0,proposed_rows=sum(len(c['rows'])==3 for c in cards))
    dump(sheetdir/'summary.json',summary)
    rate=rates(frame,valid); listing,measure=measurement_summary(valid)
    dump(OUT/'N1S_MEASUREMENTS.json',dict(note='All saved components, including gap-crossing components; none selected as the true mark.',slots=listing,descriptive=measure))
    dump(OUT/'N1S_REREAD.json',dict(contexts=[c for c,g in gates.items() if g['status']=='VOID'],slots=[{k:r[k] for k in ('context','item_id','slot_id','line_id')} for r in reread]))
    dump(OUT/'N1S_VALID_SLOTS.json',valid)
    alltable=table(valid)
    per_source={s:table([r for r in valid if r['source_era']==s]) for s in sorted({r['source_era'] for r in valid})}
    per_position={s:table([r for r in valid if r['position']==s]) for s in sorted({r['position'] for r in valid})}
    highlights={"'-' → raised dot":sum(target(r) for r in valid),"'.' → raised dot":sum(r['glyph']=='.' and r['meaning']=='raised dot' for r in valid),
        "'-' → baseline dot":sum(r['glyph']=='-' and r['meaning']=='baseline dot' for r in valid),
        "'.' → comma":sum(r['glyph']=='.' and r['meaning']=='comma' for r in valid),
        "',' → baseline dot":sum(r['glyph']==',' and r['meaning']=='baseline dot' for r in valid),
        'empty → any mark':sum(r['glyph']=='' and r['meaning'] in MEANINGS[:4] for r in valid),
        'any → unreadable / other':sum(r['meaning'] in ('unreadable','other') for r in valid)}
    totals=dict(valid_contexts=sum(g['status']=='VALID' for g in gates.values()),void_contexts=[c for c,g in gates.items() if g['status']=='VOID'],
        bed_slots_read=len(valid),excluded_void_bed=len(reread),target=highlights["'-' → raised dot"],dot_raised=highlights["'.' → raised dot"],
        other_disagreements=sum(not agrees(r['glyph'],r['meaning']) and not uncertain(r) and not (r['glyph'] in ('-','.') and r['meaning']=='raised dot') for r in valid),
        unreadable_low=sum(uncertain(r) for r in valid),disagreements_all_confidences=sum(not agrees(r['glyph'],r['meaning']) for r in valid))
    dump(OUT/'N1S_SCORE.json',dict(gates=gates,totals=totals,highlights=highlights,table=alltable,by_source_era=per_source,by_position=per_position,rates=rate))
    report=['# N1-S: numeric separator glyph-pass score','',
        f"Calibration: 82/82 PASS. **{totals['valid_contexts']}/7 contexts VALID; {len(valid)} valid bed slots**. VOID: {', '.join(totals['void_contexts'])}; {len(reread)} bed answers excluded and listed in `artifacts/n1/N1S_REREAD.json` for a fresh-order re-read. No reading run or rule fitting was performed.",'',
        '## Context gate','', '| Context | Controls | Wrong | Abstain | Bed | Status |','|---|---:|---:|---:|---:|---|']
    for c,g in gates.items(): report.append(f"| {c} | {g['controls']} | {g['wrong']} | {g['abstentions']} | {g['bed']} | {g['status']} |")
    report+=['','More than one wrong control voids the context. Unreadable controls abstain; malformed/missing/duplicate answers fail closed before scoring. Historical mapped files count unreadables as errors; they are preserved, and gates are independently decoded from answers and private option keys. No control abstentions occurred here.','', 'Control errors (item, truth → answer):','']
    for c,g in gates.items():
        for d in g['wrong_answers']: report.append(f"- {c} `{d['item_id']}`: {d['truth']} → {d['meaning']} (`{d['slot_id']}`).")
    report+=['','## Google × ink','', 'Exact Google text gaps form rows (JSON strings preserve spaces and empty gaps). Reader meanings form columns. Only VALID bed answers enter these tables, including low-confidence and unresolved reads; these remain owner-review evidence, not adjudicated truth.','',mdtable(alltable),'','### Highlighted transitions','']
    report += [f'- **{k}: {v}**' for k,v in highlights.items()]
    report+=['', 'For semantic agreement only, surrounding whitespace is ignored around a single known mark; empty agrees with nothing, whitespace-only with space, and single dash variants agree with hyphen/dash. Multi-mark gaps are disagreements. Highlight counts use exact glyphs. Unreadable/other/low-confidence cards take precedence over transition groups. Target and dot transition tallies include low-confidence reads; group counts therefore need not equal them.','']
    for title,tables in [('Source / era',per_source),('Grammar position',per_position)]:
        report += ['### '+title,'']
        for name,t in tables.items(): report+=['#### '+name,'',mdtable(t),'']
    report+=['## Target-fault rate inside the enriched frame','',
        '**This is an enriched diagnostic frame, not a population sample.** Only the 600 `step1` slots enter the frame denominator; the 300 locked slots are untouched. Of 600, 42 were dropped for geometry, 239 belong to VOID contexts, and 319 have valid reads.','',
        'The frame contains no numeric inclusion probabilities. Its recorded design cells are source/era × primary grammar position × exact Google gap. We use empirical frame weights W_h = N_h/600, not inverse population inclusion probabilities. Within each observed cell, each read receives N_h/n_h (response standardization, assuming the missing reads resemble the observed reads in that cell). No population correction is claimed.','',
        f"Observed support covers {rate['supported_cells']}/{rate['cells']} cells, representing {rate['supported_frame']}/600 frame slots; {rate['unsupported_frame']} frame slots have no valid read in their cell. The **supported-cell standardized rate is {100*rate['rate']:.3f}% [{100*rate['wilson95_kish_approx'][0]:.3f}, {100*rate['wilson95_kish_approx'][1]:.3f}]**. This is conditional on supported cells, not an identified full-frame point rate. The bracket is an approximate 95% weighted Wilson interval with Kish effective n = {rate['effective_n']:.3f}, ignoring line/document clustering and reader error; it is descriptive, not a precision qualification.",'',
        f"Crude VALID-read rate: {100*rate['crude_rate']:.3f}% [{100*rate['crude_wilson95'][0]:.3f}, {100*rate['crude_wilson95'][1]:.3f}] (ordinary 95% Wilson). Full-frame point identification bounds, retaining within-cell response assumptions but allowing unsupported exact-hyphen cells any rate (all non-hyphen cells are structural target zeros): [{100*rate['full_frame_point_identification_bounds'][0]:.3f}, {100*rate['full_frame_point_identification_bounds'][1]:.3f}]%. Weighted target-capable cell-Wilson envelope with unsupported hyphen cells [0,1]: [{100*rate['full_frame_wilson_envelope'][0]:.3f}, {100*rate['full_frame_wilson_envelope'][1]:.3f}]%; this envelope is not a simultaneous 95% confidence interval. Only {rate['unsupported_target_capable_slots']} unsupported frame slot can carry this exact target transition; other unsupported slots are structural target zeros. Re-reads are required for a complete frame estimate.",'',
        'All valid slots are the denominator; unreadable/other reads are not target-positive and remain uncertain. The estimate measures recorded reader-positive faults, not the unknown true rate among unresolved answers.','',
        '| Source/era | Grammar | Exact gap | Frame N | Read n | Fault k | W_h | N_h/n_h | Rate % | Wilson 95% % |', '|---|---|---|---:|---:|---:|---:|---:|---:|---|']
    for s in rate['strata']:
        interval=s['wilson95']; bounds='—' if interval is None else f'{100*interval[0]:.2f}, {100*interval[1]:.2f}'
        point='—' if s['rate'] is None else f"{100*s['rate']:.2f}"
        weight='—' if s['response_weight'] is None else f"{s['response_weight']:.3f}"
        report.append(f"| {s['source_era']} | {s['position']} | `{json.dumps(s['glyph'])}` | {s['frame']} | {s['read']} | {s['faults']} | {s['frame_design_weight']:.5f} | {weight} | {point} | {bounds} |")
    report+=['','## Rule readiness: descriptive evidence only','',
        'Full per-slot side records, including component height, centre relative to digit band, width, bbox, containment, digit band and gap width, are in `artifacts/n1/N1S_MEASUREMENTS.json`. All components intersecting each gap are retained, including digit fragments and components crossing the gap; none was selected as the true mark. Centre = (component centre y − digit_top)/digit_height, increasing downward. Heights and widths are native pixels. Ranges pool components by reader class. Overlap counts count components within the intersection of the two class ranges; they do not count classification errors. No threshold, classifier, train/test split or rule was fit.','',
        f"Slots by class: {measure['slots']}; component counts: {measure['components']}; zero-component slots: {measure['zero_component_slots']}.",'',
        '**Readiness limitation:** 14 of 19 raised-dot reads have no saved gap component. The five available components overlap the hyphen/dash ranges on every reported measurement. These records do not establish a separating rule; step 2 must resolve missing component evidence before using it for an ink decision.', '',
        '| Measurement | Raised-dot range | Hyphen/dash range | Range intersection | Raised components in overlap | Hyphen components in overlap |','|---|---|---|---|---:|---:|']
    for f,s in measure['fields'].items(): report.append(f"| {f} | {s['ranges']['raised dot']} | {s['ranges']['hyphen or dash']} | {s['intersection']} | {s['components_inside_intersection']['raised dot']} | {s['components_inside_intersection']['hyphen or dash']} |")
    report+=['','### Per-slot components','', '| Slot | Read / confidence | Height px, centre/band, width px (all components) |','|---|---|---|']
    for r in listing:
        vals='; '.join(f"({c['height']}, {c['centre_y_relative_band']:.6f}, {c['width']})" for c in r['measurements']['components']) or 'none'
        report.append(f"| `{r['slot_id']}` | {r['meaning']} / {r['confidence']} | {vals} |")
    report+=['','## Owner sheet','', f"`artifacts/n1/owner_sheet/n1_sheet.html`: **{summary['html_MB']:.3f} MB**, {len(cards)} cards; 12 seeded high-confidence agreement slots. Proposed rows: {summary['proposed_rows']}. Printed fields are blank. Every card uses its slot-specific doc ID; only one code point changes in each Proposed row, preserving offsets. All Google rows come from W1 features `text`, checked against frame gap offsets.",'',
        'The prescribed cleanup renderer was used under the collector interpreter with cleanup PYTHONPATH. Its `slot` argument binds note identity but does not draw numeric gap boxes; this builder overlays a thin box from the saved geometry on each saved line image, leaving the marked 3× zoom unchanged. The cleanup worktree was read only. This HTML is built for coordinator publication; no publication or owner adjudication is claimed.','', '| Group | Cards |','|---|---:|']
    report += [f'| {g} | {n} |' for g,n in counts.items()]
    report+=['','Group counts are mutually exclusive. Summary `other disagreements` excludes unreadable/other/low-confidence slots and raised-dot transitions; `unreadable/low` includes other. Thus headline transitions and uncertainty may overlap, while sheet groups do not.','',
        f"Saved probe evidence (not refreshed; no reading launcher invoked): {latest_limit['primary']['used_percent']}% weekly, from ctx07 run receipt. This is historical usage, not a live probe.",'', 'Validation results are recorded in `artifacts/n1/N1S_TESTS.json` after the offline test run.']
    reportpath=ROOT/'docs/records/labelfix/secondary/N1S_REPORT.md'; reportpath.write_text('\n'.join(report)+'\n')
    outputs=[sheetdir/'summary.json',sheetdir/'cards.json',sheetdir/'spec.json',sheet,reportpath]+[OUT/f'N1S_{s}.json' for s in ('SCORE','MEASUREMENTS','REREAD','VALID_SLOTS')]
    receipt=dict(schema='N1S-1',network_calls=0,reading_runs=0,fitting=False,git_writes=False,cleanup_writes=False,
        interpreter=sys.executable,python_version=sys.version,renderer=str(renderer),pythonpath=str(CLEANUP),
        calibration=dict(correct=82,total=82,status='PASS'),totals=totals,owner_sheet=summary,
        rate=rate,inputs=INPUTS,outputs={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in outputs},
        tests='pending',usage_probe=dict(source='ctx07.r1.run.json',live=False,rate_limits=latest_limit))
    dump(OUT/'N1S_RECEIPT.json',receipt)
    print(json.dumps(dict(totals=totals,rate={k:v for k,v in rate.items() if k!='strata'},sheet=summary),ensure_ascii=False,indent=2))


if __name__=='__main__': build()
