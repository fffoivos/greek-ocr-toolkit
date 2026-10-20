"""Build the report from completed per-stratum evidence; no detector/network."""
from collections import Counter
import csv
import gzip
import hashlib
import json
from math import sqrt
from pathlib import Path

HERE=Path(__file__).resolve().parent
CLIP={'detector_clipped_top','detector_clipped_bottom'}
MODES=('ENSEMBLE_AB','PRESENCE')
METRICS=('localisation_unknown','segmentation_uncertain','clipped_top','clipped_bottom','unnamed')
VARIANTS=('original','masked')


def load(path):return list(map(json.loads,gzip.open(path,'rt')))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(map(str,headers))+' |','| '+' | '.join('---' for _ in headers)+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows])
def pair(a,b):return f'{a}→{b}'
def aggregate(rs):
    return {v:{k:sum(r['counts'][v][k] for r in rs) for k in METRICS+('slots','component_assignments','unnamed_blobs')} for v in VARIANTS}
def reasonclass(reasons,category):
    s=set(reasons)
    return bool(s) and s<=CLIP if category=='clipping_only' else bool(s&CLIP) and 'detector_localisation_unknown' in s
def wilson(x,n):
    if not n:return None
    z=1.96;p=x/n;d=1+z*z/n;mid=(p+z*z/(2*n))/d;rad=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return max(0,mid-rad),min(1,mid+rad)
def csvwrite(name,headers,rows):
    with (HERE/name).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)


def build():
    records=[];details=[];flags=[];blobs=[];receipts={}
    for sample in ('200','vouli'):
        root=HERE/sample
        if not (root/'receipt.json').exists():continue
        receipt=json.loads((root/'receipt.json').read_text());assert receipt['complete']
        receipts[sample]=receipt
        for filename,dest in [('lines.jsonl.gz',records),('details.jsonl.gz',details),('border_flags.jsonl.gz',flags),('border_blobs.jsonl.gz',blobs)]:
            assert sha(root/filename)==receipt['outputs'][filename]
            dest.extend(load(root/filename))
    assert '200' in receipts
    base=[r for r in records if r['sample']=='200']; byid={r['id']:r for r in records}
    groups=[(w,[r for r in records if r['wave']==w]) for w in ('round1','round2','mixed','vouli')]
    groups=[(w,rs) for w,rs in groups if rs]+[('ALL evaluated',records)]
    totals=aggregate(records);btotal=aggregate(base)
    status=lambda rs,v,m,s:sum(r['status'][v][m]==s for r in rs)
    sumstage=lambda key:sum(r['source'].get(key) or 0 for r in records)
    measured=[r for r in records if r['source'].get('own_pixels_lost') is not None]
    ownloss=[r for r in records if (r['source'].get('own_pixels_lost') or 0)>0]
    unknown=[r for r in records if r['source'].get('own_pixels_lost') is None]
    flips=[r for r in records if r['status']['original']['ENSEMBLE_AB']=='hold' and r['status']['masked']['ENSEMBLE_AB']!='hold']
    regressed=[r for r in records if r['status']['original']['ENSEMBLE_AB']!='hold' and r['status']['masked']['ENSEMBLE_AB']=='hold']
    localisation_new=sum(len(r['new_localisation_starts']) for r in records)
    localisation_cleared=sum(sum(bool(s.get('localisation_unknown')) and not {q['start']:q for q in d['detector']['masked']['slots']}.get(s['start'],{}).get('localisation_unknown',False) for s in d['detector']['original']['slots']) for d in details)
    text=['# L1M — Masking foreign ink under frozen SF4','',
        f"**Verdict: partial.** On the 200 held round1/round2/mixed lines, masking releases **{sum(r['sample']=='200' for r in flips)}/200 ENSEMBLE_AB lines** ({status(base,'masked','ENSEMBLE_AB','corrected')} kept with a changed label) and **{200-status(base,'masked','PRESENCE','hold')}/200 PRESENCE lines** ({status(base,'masked','PRESENCE','corrected')} changed labels). Raw clipping flags fall {pair(btotal['original']['clipped_top']+btotal['original']['clipped_bottom'],btotal['masked']['clipped_top']+btotal['masked']['clipped_bottom'])}; localisation_unknown is {pair(btotal['original']['localisation_unknown'],btotal['masked']['localisation_unknown'])} and segmentation_uncertain {pair(btotal['original']['segmentation_uncertain'],btotal['masked']['segmentation_uncertain'])}. Masking helps the clipping driver; it does not remove most complete-gate holds or improve the localisation driver in this sample.",
        '', '**Coverage: '+('260 evaluated, with vouli reported separately.' if 'vouli' in receipts else '200 of 260 evaluated; vouli pending. The vouli sourcing directory/receipt was absent at the staging check.')+'** Parliament is not sampled (two-column neighbour matching unsettled); **no projection to parliament**. Openarchives is also unsampled.',
        '', '**Border attribution limitation:** The supplied r3 `lines.jsonl` carries row ownership summaries, fill component IDs, counts and a mask hash; it does **not** carry pixel ownership masks, mask paths or the centre curves needed for `_voronoi_keep`. The staged tree has crops, JSON and logs only. Every original clipping flag is mapped to its exact border pixels and native connected blob(s), but all blob ownership is **undecidable**. Removed does not prove neighbour-owned, and retained does not prove own-line. Consequently the requested 6-neighbour/6-own visual attribution check cannot be completed from this handoff; the twelve inspected panels instead cover six verdict flips and six persistent border flags. The paired detector/gate result is complete for the 200; semantic border attribution remains open.',
        '', '## Frozen method and verification','',
        '- Detector: `reading.read_ink(ink.analyse(crop), alignment.prediction, alignment, S4_model, filtered=False)`; S5 case model; default qualified geometry is empty, as in the original S6 job. Both variants use the same original text and saved alignment.',
        '- Gate: unmodified `release_gate.compose_runtime`, `sf4-release-v1`, and the frozen `l1_common.overlay` wrapper, including original-label edit guards and line HOLD semantics. Kept-and-corrected means a changed NFD label accepted by the gate, **not independently verified print truth**.',
        '- Imports and assets are read-only from c6064650fa5451cbc3bd13197d7a31c0d3bbf33d. Every imported frozen Python source and both model assets were compared byte-for-byte with its committed blob; hashes and Python/library versions are in each receipt. No detector, gate, release, original crop or `.git` file was written.',
        f"- Original-crop gate decisions match frozen recomposition of saved detector evidence on **{sum(all(r['saved_original_gate_parity'].values()) for r in records)}/{len(records)} lines in both modes**. A/B/E predictions, A/B/E coverage, recogniser text and any saved K1 inputs have one identical content digest within each original/masked pair. No recogniser or reader inference ran.",
        '- Counts below distinguish raw detector clipping predicates on all letter slots from SF4 clipping vetoes after zone relevance. Counts are slot incidences, not independent physical defects. Unnamed counts are slots with unnamed marks; separate blob counts and component IDs are saved per letter.',
        '- Foreign-removal strata: none=0 audited foreign pixels removed, small=1–100, large=>100; unknown audit measurements remain separate. These descriptive thresholds were fixed before reading outcomes. Matching failures remain in all totals with unchanged crops.',
        '', '## Staging and own-ink audit','']
    stage_rows=[]
    for w,rs in groups:
        ml=[r for r in rs if r['source'].get('own_pixels_lost') is not None]
        stage_rows.append([w,len(rs),sum(r['source']['mask_applied'] for r in rs),sum(r['changed_pixels']>0 for r in rs),sum(r['source']['match_status']!='ok' for r in rs),sum(r['source'].get('own_pixels_lost') is None for r in rs),sum((r['source'].get('own_pixels_lost') or 0)==0 for r in ml),len(ml),sum(r['source'].get('own_pixels_lost') or 0 for r in rs),sum(r['source'].get('foreign_pixels_removed') or 0 for r in rs)])
    text += [table(['Wave','N','Mask applied','Crop changed','Match failed','Audit unmeasured','Own loss=0','Own measured','Own lost px','Foreign removed px'],stage_rows),'',f"All {len(measured)} measured audits are retained: {len(measured)-len(ownloss)} have zero own-pixel loss, {len(ownloss)} have nonzero loss; {len(records)-len(measured)} are unknown/unmeasured. The source audit statuses are {dict(Counter(r['source']['audit_status'] for r in records))}; unmeasured means null own/foreign measurements, including cross-row and invalid-page-geometry cases. Total own loss is {sumstage('own_pixels_lost')} pixels, foreign removal {sumstage('foreign_pixels_removed')} audited pixels. `mask_applied` includes successfully processed unchanged crops; it is not the crop-changed count.",'']
    raw_rows=[]
    for w,rs in groups:
        c=aggregate(rs);raw_rows.append([w,len(rs),c['original']['slots']]+[pair(c['original'][k],c['masked'][k]) for k in METRICS]+[pair(c['original']['component_assignments'],c['masked']['component_assignments'])])
    text += ['## Paired raw detector counts','',table(['Wave','N','Letters',*METRICS,'Component assignments'],raw_rows),'',f"Localisation newly fails at {localisation_new} starts and clears at {localisation_cleared} starts. Net counts alone conceal these exchanges. Full per-line counts, per-letter component IDs/bboxes, histograms, native labels and flags are preserved in [evidence](L1M_evidence/200/).",'']
    hist_rows=[]
    for variant in VARIANTS:
        hist=Counter()
        for r in records:hist.update({int(k):v for k,v in r['counts'][variant]['components_per_letter_histogram'].items()})
        hist_rows.extend([[variant,n,count] for n,count in sorted(hist.items())])
    text += [table(['Crop','Native component IDs per letter','Letter slots'],hist_rows),'','Component assignments may count one fused native component for several letter partitions; zero means no native letter component was assigned, not no printed character.','', '## Complete frozen-gate outcomes','']
    status_rows=[]
    for mode in MODES:
        for w,rs in groups:
            status_rows.append([mode,w,len(rs)]+[pair(status(rs,'original',mode,s),status(rs,'masked',mode,s)) for s in ('hold','corrected','unchanged')])
    text += [table(['Mode','Wave','N','Held','Kept changed','Kept unchanged'],status_rows),'',f"AB releases {len(flips)} lines and introduces {len(regressed)} new line holds. Of the 42 newly kept base-sample lines, 40 have measured zero own-pixel loss, one has 1 own pixel lost (and is accepted as corrected), and one has an unmeasured audit. A/B agreement is a stability signal from readers sharing training data; the new accepted labels have not been scored against independent print truth.",'']
    reason_rows=[]; guard_rows=[]
    for mode in MODES:
        for w,rs in groups:
            keys={r['id'] for r in rs};c={v:Counter() for v in VARIANTS};g={v:Counter() for v in VARIANTS}
            for d in details:
                if d['id'] not in keys:continue
                for v in VARIANTS:
                    c[v].update(z for s in d['modes'][v][mode]['hold_slots'] for z in s['reasons'])
                    g[v].update(h['detail'] for h in d['overlays'][v][mode]['hold_slots'] if h['letter']=='')
            reason_rows.extend([mode,w,k,c['original'][k],c['masked'][k]] for k in sorted(c['original'].keys()|c['masked'].keys()))
            guard_rows.extend([mode,w,k,g['original'][k],g['masked'][k]] for k in sorted(g['original'].keys()|g['masked'].keys()))
    csvwrite('slot_hold_reasons.csv',['mode','wave','exact_reason','original','masked'],reason_rows)
    csvwrite('line_guards.csv',['mode','wave','exact_guard','original','masked'],guard_rows)
    text += ['### Exact slot HOLD reasons (all evaluated lines)','',table(['Mode','Exact reason','Before','After'],[[m,k,a,b] for m,w,k,a,b in reason_rows if w=='ALL evaluated']),'','For the base 200, SF4-relevant clipping veto incidences are **1,073→283**, compared with raw clipping predicates **2,269→650**. Zone relevance explains the difference. [Per-wave exact slot counts](L1M_evidence/slot_hold_reasons.csv); [additional original-label line guards](L1M_evidence/line_guards.csv). Line guards are counted separately and still participate in held-line outcomes.','', '## Source-record strata','']
    strat_rows=[]
    for w,rs in groups:
        for group in ('none','small','large','unknown','matching_failed'):
            ss=[r for r in rs if r['foreign_group']==group]
            if not ss:continue
            c=aggregate(ss);strat_rows.append([w,group,len(ss),pair(c['original']['localisation_unknown'],c['masked']['localisation_unknown']),pair(c['original']['segmentation_uncertain'],c['masked']['segmentation_uncertain']),pair(c['original']['clipped_top']+c['original']['clipped_bottom'],c['masked']['clipped_top']+c['masked']['clipped_bottom']),pair(status(ss,'original','ENSEMBLE_AB','hold'),status(ss,'masked','ENSEMBLE_AB','hold'))])
    text += [table(['Wave','Foreign removal','N','Localisation','Segmentation','Clipping','AB held'],strat_rows),'']
    auditrows=[]
    for label,rs in [('audit unknown',unknown),('own loss >0',ownloss),('own measured zero',[r for r in measured if r not in ownloss])]:
        c=aggregate(rs);auditrows.append([label,len(rs),pair(c['original']['localisation_unknown'],c['masked']['localisation_unknown']),sum(len(r['new_localisation_starts']) for r in rs),pair(status(rs,'original','ENSEMBLE_AB','hold'),status(rs,'masked','ENSEMBLE_AB','hold'))])
    text += [table(['Audit stratum','N','Localisation','New failed starts','AB held'],auditrows),'',table(['Own-loss line','Wave','Own px lost','New localisation starts','AB'],[[r['id'],r['wave'],r['source']['own_pixels_lost'],str(r['new_localisation_starts']),pair(r['status']['original']['ENSEMBLE_AB'],r['status']['masked']['ENSEMBLE_AB'])] for r in ownloss]),'','For the base 200, none of the six own-loss lines gains a new localisation failure. All four new failed starts are on measured-zero-loss lines. The mask can change thresholding, component roles and geometry even when this aggregate audit reports zero own-pixel loss; the saved counts do not establish the mechanism of each new failure.','', '## Border blobs: exhaustive mapping, ownership unresolved','']
    border_rows=[]
    for w,rs in groups:
        keys={r['id'] for r in rs};fs=[f for f in flags if f['id'] in keys];bs=[b for b in blobs if b['id'] in keys]
        for edge in ('top','bottom'):
            ff=[f for f in fs if f['edge']==edge];bb=[b for b in bs if b['edge']==edge]
            new=sum(sum(f['edge']==edge for f in r['new_clipping_flags']) for r in rs)
            border_rows.append([w,edge,len(ff),sum(f['persists'] for f in ff)+new,new,'0→0','0→0',pair(len(ff),sum(f['persists'] for f in ff)+new),len(bb),sum(b['edge_pixels_no_longer_ink']==len(b['edge_x']) for b in bb)])
    text += [table(['Wave','Edge','Flags before','After','New flags','Neighbour flags','Own flags','Undecidable flags','Unique edge blobs','Blobs edge fully cleared'],border_rows),'',f"Blob attribution denominator: **{len(blobs)} unique (line, crop-edge, native-label) blobs**, each counted once even if it triggers several letter flags. Confirmed neighbour 0 (0%), confirmed own 0 (0%), undecidable {len(blobs)} (100%). These zeros mean **no confirmed attribution**, not absence of neighbour/own ink. Flag and blob denominators are different; exact pixel lists and slot-to-blob joins are in `border_flags.jsonl.gz` and `border_blobs.jsonl.gz`.",'',
        '**Interpretation required by the ownership contract:** Neighbour-owned border blobs would make their flag removal a legitimate consequence of masking. Own-line accents/breathings touching a tight top, or descenders touching the bottom, require crop padding at cut time; masking cannot restore missing own-line pixels. Both ownership counts are currently unmeasured (0 confirmed in either class). The measured own-pixel-loss audit is not a border-ownership map and cannot substitute for those numbers.','',
        '## Twelve-panel visual check','',
        '**Verdict flips, 12 panels:** [1–3](L1M_evidence/flip_panels/sheet_1.png), [4–6](L1M_evidence/flip_panels/sheet_2.png), [7–9](L1M_evidence/flip_panels/sheet_3.png), [10–12](L1M_evidence/flip_panels/sheet_4.png); [selection](L1M_evidence/flip_visual_selection.json). All twelve lines flip AB from hold to kept.',
        '', '**Border check, 12 panels:** [1–3](L1M_evidence/panels/sheet_1.png), [4–6](L1M_evidence/panels/sheet_2.png), [7–9](L1M_evidence/panels/sheet_3.png), [10–12](L1M_evidence/panels/sheet_4.png); [selection](L1M_evidence/visual_selection.json). These cover six cleared and six persistent SF4-relevant border flags; ownership remains undecidable, so this is not the requested confirmed neighbour/own split.',
        '', 'Each composite shows the complete original/masked crop, a native-pixel zoom, and actual detector component pixels tinted inside their letter partitions. Boxes show the letter bounds; blue is other letters, magenta the target, red its clipping predicate window. Every selected flag is an active SF4 AB veto before masking; persistent examples remain active after masking.','']
    reviewpath=HERE/'visual_review.md'
    text += [reviewpath.read_text() if reviewpath.exists() else '**Visual inspection pending.** Panels have not yet been inspected; no visual correctness claim is made.','', '## Reading against the SF4 population census','']
    census=HERE.parent/'L1C_census_3679781/CENSUS.json'
    population=json.loads(census.read_text())['modes']['ENSEMBLE_AB']['per_wave']
    summary=HERE.parent/'L1C_census_3679781/AB_SF4_SUMMARY.md'
    text += [f"Census input: [AB_SF4_SUMMARY.md](L1C_census_3679781/AB_SF4_SUMMARY.md), SHA-256 `{sha(summary)}`; [CENSUS.json](L1C_census_3679781/CENSUS.json), SHA-256 `{sha(census)}`. The summary below is included verbatim to preserve the population context.",'','<details>','<summary>Full supplied census summary</summary>','',summary.read_text().strip(),'','</details>','',
        'The census counts detailed SF4 line reasons: 89,886 lines carry clipped_top; at least 30,280 are clipping-only. The older 1,024-row pilot counted broad pre-SF4 reason entries, which folded clipping into localisation_unknown. It cannot establish localisation as the SF4 population driver. This paired sample independently shows clipping falls sharply while localisation persists.','',
        '### Conditional projections (scenarios, not release authorisation)','',
        'For each wave and category, estimate = census known-category lower bound × observed sample fraction fully released by AB. Clipping-only means a nonempty exact reason set contained in {top,bottom}; clipping+localisation means at least one clipping reason and localisation_unknown, allowing other holds. Census category sizes below sum qualifying top-ten exact reason sets only, so they are lower bounds. Wilson 95% binomial intervals illustrate sampling uncertainty; they do not correct sample selection, clustered pages, missing ownership or census truncation. No extrapolation uses the overall 21% release rate.','']
    projections=[]
    for wave in ('round1','round2','mixed','vouli','parliament','openarchives'):
        rs=[r for r in records if r['wave']==wave]
        for category in ('clipping_only','clipping_plus_localisation'):
            n_pop=sum(s['lines'] for s in population[wave]['top10_exact_reason_sets'] if reasonclass(s['reasons'],category))
            ss=[r for r in rs if reasonclass(r['reason_sets']['original']['ENSEMBLE_AB'],category)]
            released=sum(r['status']['masked']['ENSEMBLE_AB']!='hold' for r in ss)
            if ss:
                lo,hi=wilson(released,len(ss));estimate=round(n_pop*released/len(ss));interval=f'{round(n_pop*lo):,}–{round(n_pop*hi):,}'
            else:estimate='no projection';interval='unsampled' if not rs else 'no sample in category'
            projections.append([wave,category,n_pop,len(ss),released,estimate,interval])
    text += [table(['Wave','SF4 category','Known population ≥','Sample N','Released','Conditional lines released','95% scenario range'],projections),'',
        'Across the three evaluated waves, the clipping-only scenario sums to approximately **12,608** released lines out of the known 22,261 clipping-only lines, based on **39/72** sample releases. Clipping+localisation has **0/33** sample releases; its zero point estimates have wide uncertainty, not a proven zero population effect.', '',
        'Assumptions: these pre-SF4-held sampled lines represent the same wave and exact SF4 reason category in the census; the sourcing matcher/mask quality, own-loss rate, reader coverage and other gate inputs transfer to that category; masking is applied without new ownership errors; and the frozen readers remain fixed as here. The sample was stratified by wave, not by SF4 reason set or foreign-ink amount, and excludes already-kept lines. These scenarios therefore do not measure population precision, final kept-label correctness, or the release effect of retraining/rerunning the readers. No estimate is made for parliament; vouli is pending until evaluated.','',
        '## Reproduce / append vouli','',
        'From the workspace root, with networking permitted only for the bounded selected Clariden extraction:','',
        '```sh',
        'PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python docs/labelfix/spellcheck/L1M_evidence/run_pair.py --sample vouli',
        '```','',
        'This requires a completed vouli receipt with all 60 selected records. It reuses the saved C1 alignments where available, fetches only missing selected evidence, saves vouli separately and rebuilds this report including both strata. It never reruns the 200 detector pairs unless explicitly requested with `--sample 200 --refresh`. If vouli staging is absent/incomplete, it reports pending and preserves the report.','',
        '## Evidence and limits','',
        '- [200-line run receipt](L1M_evidence/200/receipt.json), [per-line results](L1M_evidence/200/lines.jsonl.gz), [all per-letter records](L1M_evidence/200/slots.jsonl.gz), [detector, gate and overlays](L1M_evidence/200/details.jsonl.gz), native pixel arrays under `200/pixels/`.',
        '- [Every original border flag](L1M_evidence/200/border_flags.jsonl.gz), [deduplicated border blobs with native pixel coordinates](L1M_evidence/200/border_blobs.jsonl.gz). These identify which blob caused which flag; ownership remains undecidable.',
        '- [Validation receipt](L1M_evidence/validation.json), [staging inventory and record schema](L1M_evidence/staging_inventory.json), and [visual review](L1M_evidence/visual_review.md). Validation checks every original flag-to-blob join, every saved native blob pixel, all mode-to-overlay reason joins, both original-crop gate projections and the absent-vouli command.',
        '- [Read-only Clariden extractor](L1M_evidence/fetch_selected.py), [fetch log](L1M_evidence/fetch_200_log.json), [selected evidence](L1M_evidence/remote_200.json.gz), [paired driver](L1M_evidence/run_pair.py), [report builder](L1M_evidence/build_report.py). The first extraction had a crop-key join error (full document IDs vs shortened crop directory IDs); it stopped after 41 seconds without output. The corrected extraction took 31 seconds. No auth/cert error occurred, no cert refresh, submission or remote write occurred. Full source-shard hashes were not recomputed; shard receipts were read and selected A fields compared exactly.',
        '- All 200 lines were held under the original L1E gate and are also held under the recomputed SF4 baseline. One failed match and all unknown audits are included. No independent accuracy/precision claim follows from reader agreement or gate acceptance.',
        '- Ownership percentages and the neighbour/own visual split require the missing saved pixel ownership masks/curves. That evidentiary limit cannot be repaired by relabelling removed pixels as foreign or retained pixels as own.',
        '']
    masked=sum(r['source']['mask_applied'] for r in records);failed=sum(r['source']['match_status']!='ok' for r in records)
    linecount='260 lines' if 'vouli' in receipts else '200/260 lines (vouli pending)'
    result=(f"L1M RESULT: {linecount} (masked {masked}, matching-failed {failed}); localisation_unknown slots {pair(totals['original']['localisation_unknown'],totals['masked']['localisation_unknown'])}; segmentation_uncertain {pair(totals['original']['segmentation_uncertain'],totals['masked']['segmentation_uncertain'])}; clipping {pair(totals['original']['clipped_top']+totals['original']['clipped_bottom'],totals['masked']['clipped_top']+totals['masked']['clipped_bottom'])} (border blobs neighbour 0% / own 0% / undecidable 100%); AB lines held {status(base,'original','ENSEMBLE_AB','hold')}/200→{status(base,'masked','ENSEMBLE_AB','hold')}/200, corrected {status(base,'original','ENSEMBLE_AB','corrected')}→{status(base,'masked','ENSEMBLE_AB','corrected')}; PRESENCE {status(base,'original','PRESENCE','hold')}→{status(base,'masked','PRESENCE','hold')}; verdict: partial")
    text.append(result)
    (HERE.parent/'L1M_REPORT.md').write_text('\n'.join(text)+'\n')
    csvwrite('per_line.csv',['id','wave','foreign_group','audit_status','own_pixels_lost','AB_before','AB_after','PRESENCE_before','PRESENCE_after','new_localisation_starts'],[[r['id'],r['wave'],r['foreign_group'],r['source']['audit_status'],r['source'].get('own_pixels_lost'),r['status']['original']['ENSEMBLE_AB'],r['status']['masked']['ENSEMBLE_AB'],r['status']['original']['PRESENCE'],r['status']['masked']['PRESENCE'],str(r['new_localisation_starts'])] for r in records])
    csvwrite('projections.csv',['wave','category','population_lower_bound','sample_n','released','conditional_estimate','wilson95_scaled'],projections)
    (HERE/'summary.json').write_text(json.dumps(dict(evaluated=len(records),vouli_pending='vouli' not in receipts,raw_counts=totals,AB_released=len(flips),AB_regressed=len(regressed),border_blobs=len(blobs),border_flags=len(flags),new_localisation_slots=localisation_new,cleared_localisation_slots=localisation_cleared,result=result),indent=2)+'\n')
    print(result)


if __name__=='__main__':
    from make_panels import render
    render();render('flips');build()
