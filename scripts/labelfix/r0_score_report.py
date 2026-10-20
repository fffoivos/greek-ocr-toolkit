"""Render R0c report from scored receipts; no measurement or source mutation."""
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter, defaultdict
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/records/labelfix/spellcheck'
EV=OUT/'R0_evidence/scoring'
d=json.loads((OUT/'R0_metrics.json').read_text())
fs=[json.loads(s) for s in (_data_input(OUT/'R0_failures.jsonl')).read_text().splitlines()]
labels=d['stratum_labels']; strata=list(labels)[:3]
short={'continuity_666':'666 continuity instrument','newsource':'(ii) mark-enriched, not a population estimate',
       'wikisource_ia':'(i-a) selection-exposed (v2 val)',
       'owner_DEV_supplement':'owner DEV supplement; excluded'}
def p(v):return 'UNKNOWN' if v is None else f'{v:.2f}%'
def table(head,rows):
    def cell(x):return str(x).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join(['---']*len(head))+' |']+
                     ['| '+' | '.join(map(cell,row))+' |' for row in rows])
def example(r):return r['line_id']
def type_examples(rr):
    seen={}
    for r in rr:seen.setdefault((r['stratum'],r['line_id']),r)
    selected=[]
    # Prefer three different physical lines, not the same line repeated for slots.
    for r in seen.values():
        if r['line_id'] not in [x['line_id'] for x in selected]:selected.append(r)
        if len(selected)==3:break
    return '; '.join(f"{short[r['stratum']]}: `{r['line_id']}`" for r in selected)+(f' (only {len(selected)} observed lines)' if len(selected)<3 else '')

snapshot=EV/'R0a_REPORT_snapshot.md'
if not snapshot.exists():snapshot.write_text((OUT/'R0_REPORT.md').read_text())
cov=d['truth_first']['coverage'];ls=d['letters']['by_stratum']; cs=d['case'];ps=d['punctuation']['by_stratum']
report=['# R0 recogniser audit — final R0c scoring, 17 October 2026','',
 '**Letter truth first: 2,376 adjudicated word-letter slots on 361 distinct lines across the three separately reported strata; 0 complete lines / 0 full-line slots certified.** The inventory total adds coverage only, never error rates. There are also 160 case-only cards, physical punctuation probes, ten native-cache variant word cards and one separate DEV witness. These are different evidence scopes.',
 '',
 'R0b supplies literal print forms, with combining diacritics ignored. The main deck has 932 AGREED, 14 MAJORITY_OF_3, 2 UNRESOLVED and 83 CONTROL; (i-a) has 24 AGREED and 3 CONTROL. Each reader passes 83/83 main controls and 3/3 IA controls. Controls are excluded from accuracy. No reader supplied `full_line_letters`. Shared errors outside the adjudicated words therefore remain possible; **whole-line/population letter error is UNKNOWN for every stratum**. The rates below describe the selected word cards, whose selection deliberately enriches disagreements.',
 '',table(['Stratum','Cohort lines','Non-control cards (resolved)','Lines touched by any card','Word cards / known letter slots / lines','Case-only cards','Full lines certified'],
 [[short[c['stratum']],c['cohort_lines'],f"{c['noncontrol_cards']} ({c['resolved_cards']})",c['card_touched_lines'],
   f"{c['word_identity_cards']} / {c['word_identity_truth_slots']} / {c['word_identity_truth_lines']}",c['case_only_cards'],0] for c in cov]),'',
 'Word identity is scored only on complete word-card scopes (`model_words`), including punctuation-disagreement words whose accepted printed form contains letters. Case probes certify case only; punctuation anchors certify their requested sign only. Neither silently adds letter-identity truth. Word windows are disjoint within each prediction stream. Exact line IDs, NFD windows and accepted text are in [line_truth_inventory.jsonl](R0_evidence/scoring/line_truth_inventory.jsonl); per-word counts are in [letter_units.jsonl](R0_evidence/scoring/letter_units.jsonl). Lines with no such scopes have no certified letter denominator.',
 '',
 '**UNKNOWN stays UNKNOWN.** `item00171` (`177b717d-p000045-l0004`) and `item00564` (`51fe7386-p000024-l0022`) are wholly excluded at their unresolved scopes. An overlapping punctuation card cannot resolve item00564: its boundary is masked. `item00174` (`384c3f89-p000050-l0034`) is MAJORITY_OF_3 but reads `επιστα?υεσκον`: its one `?` glyph is excluded, while its 11 known letters are retained. Its card pixels show the clipped lower part that readers identified. No alternative letter or punctuation shape was guessed.',
 '',
 '## Letter errors on adjudicated word-card slots','',
 'NFD combining marks, spaces, digits and punctuation are excluded. Case is kept for the first rate; the second uses Unicode casefold (including final-sigma folding). Unit-cost Levenshtein edits are divided by the number of known printed letters. Insertions add errors, not denominator slots. Case and Greek/Latin script substitutions are disjoint subtypes of substitution; the “substitution” column below contains the remaining substitutions. Google is used to diagnose label evidence, never as accuracy truth.',
 '',table(['Stratum','Known slots / lines','Errors','Letter error','Case-folded','Substitution','Insertion','Deletion','Case','Script mix-up'],
 [[short[r['stratum']],f"{r['truth_slots']} / {r['lines']}",r['errors'],p(r['letter_error_pct']),p(r['letter_error_case_folded_pct'])]+
   [r['by_type'].get(t,0) for t in ['substitution','insertion','deletion','case','script_mixup']] for r in ls if r['stratum'] in strata]),'',
 'These are **not CERs on all 666 / 200 / 133 lines**. In particular, 6.50% on the 666 card scopes cannot be compared directly with the old 1.37% v2_test CER against Google labels.',
 '',
 '**Prediction streams:** the primary 666 result uses the stored instrument prediction, not substituted native-cache output. Ten native variant cards cover 79 printed letters on eight lines, with 17 edits (12 substitutions, 5 deletions), 21.52% with either case convention **on those variant cards only**. They are not added to the 106 stored-stream errors or its denominator. Ten lines have cached text drift, eight at base-letter level; see [drift receipt](R0_evidence/cached_prediction_drift_10.jsonl). The DEV `02a3a2a6-p000318-l0017` witness has one Greek α → Latin a error in four letters (`ξανα` → `ξaνα`); it is excluded from every stratum.',
 '',
 '### By book and source, same selected-word denominator','']
rows=[]
for r in d['letters']['by_book_source']:
    if r['stratum']=='owner_DEV_supplement':continue
    if r['stratum']=='newsource' and r['grouping']!='source':continue
    rows.append([short[r['stratum']],r['source'],r['truth_slots'],r['errors'],p(r['letter_error_pct']),p(r['letter_error_case_folded_pct']),
        '/'.join(str(r['by_type'].get(t,0)) for t in ['substitution','insertion','deletion','case','script_mixup'])])
report += [table(['Stratum','Book/source','Known slots','Errors','Case kept','Case folded','Sub/ins/del/case/script'],rows),'',
 'Zero-denominator books are shown as UNKNOWN, not 0% error. The machine metrics additionally retain every (ii) document beneath its source group; see `letters.by_book_source` in [R0_metrics.json](R0_metrics.json).',
 '',
 '## Case: recogniser versus the S5 pixel-case decision','',
 '**Recogniser right 160/160; S5 pixel-case right 0/160; UNKNOWN 0.** The book-stratified estimator `sum_h N_h × recogniser_right_h/n_h` gives **753.0 / 753 = 100.00% recogniser right** as a point estimate. This does not certify all 753 individually. All-success strata yield a zero plug-in standard error; that is not a useful confidence interval and none is asserted.',
 '',table(['Stratum','Book','Population N','Adjudicated n','Recogniser right','S5 pixel right','Extrapolated recogniser right'],
 [[short[r['stratum']],r['doc'],r['population'],r['sampled'],r['recogniser_right'],r['S5_pixel_right'],f"{r['extrapolated_right']:.1f}"] for r in cs['by_book']]),'',
 'These are failures of the **S5 pixel-case decision**, not recogniser case errors. The word cards independently find three recogniser case errors: one Φ → φ on `6b47791c-p000005-l0005` (666 continuity instrument), and two Ι → ι on `anemi--_metadata_6_2_f_metadata-352-0000000.tkl-23eeee17--000052-l0033` ((ii), mark-enriched, not a population estimate). The case cohort has a locator caveat: item00818 offers Ο/ο at frozen S5 slot 7, while its saved NFD start 6 points to Τ. It is scored as uppercase-versus-lowercase only; no body identity or span is transferred from it.',
 '',
 '## Apostrophes, elision and quotation','',
 'The denominator is **deduplicated print-positive sites in adjudicated candidate scopes**, not punctuation prevalence in a source population. Straight apostrophe, curly apostrophe, modifier apostrophe, spacing koronis and grave-like elision ticks count as functional apostrophe emissions; exact printed shape is reported separately. Opening and closing quote shapes are also recorded separately. One logical site is counted once even when a word card and an S4/M2 probe both cover it. Thirty-five rejected S4 opening-quote probes are physical components (often breathings), not 35 absent signs at text offset zero; their pixels/boxes are retained separately.',
 '',table(['Stratum','Printed kind','Printed sites','Recogniser emitted/printed','Google emitted/printed','Human emitted/printed'],
 [[short[r['stratum']],r['kind'],r['printed']]+[
  f"{r['systems'][s]['emitted_same_function']}/{r['systems'][s]['printed_with_reference']} ({p(r['systems'][s]['emitted_pct'])})"
  for s in ['model','google','human']] for r in ps]),'',
 table(['Stratum','Printed kind','Recogniser exact shape/available','Google exact shape/available','Human exact shape/available'],
 [[short[r['stratum']],r['kind']]+[f"{r['systems'][s]['exact_printed_shape']}/{r['systems'][s]['printed_with_reference']}" for s in ['model','google','human']] for r in ps]),'',
 'No human full-line reference exists for (ii); 0/0 means unavailable. For the 666 apostrophes, recogniser and Google each emit 212/213, and human 212/213; most recogniser/Google emissions are straight ASCII apostrophes. Their exact-shape count is only 1/213, versus human 207/213. The one recogniser omission is `384c3f89-p000050-l0037`, where Google and human contain the printed elision. The 666 quote omissions are six sites, five also absent from Google and one with a correct Google quote. Presence and shape are different questions: **the data do not support “the recogniser never emits apostrophes.”**',
 '',
 'The one unresolved typography site is excluded even though an overlapping S4 card proposes an apostrophe. There are no remaining contradictory resolved site joins. [Punctuation site evidence](R0_evidence/scoring/punctuation_sites.jsonl) contains every source emission, card ID and letter boundary; [rejected physical quote probes](R0_evidence/scoring/rejected_opening_quote_probes.jsonl) retain their component boxes.',
 '',
 '## Span placement and historical mapping — R0a evidence retained','',
 'The historical R0a headline **998/25,437 = 3.9234% outside blob** is a diagnostic total over 666+(ii), retained only for continuity with the requested 3.92% line. Separate strata are below; it is not a pooled accuracy estimate. A clean slot owns one native connected component, no other character owns it, and its CTC centre is tested against the half-open native bbox. Blob assignment itself uses the runtime overlap rule, so this is not independent print truth for glyph identity.',
 '',table(['Stratum','All alphabetic slots','Clean','Outside','Outside %','Fused','Split','No letter blob'],
 [[short[r['stratum']],r['all_slots'],r['clean'],r['outside'],p(r['outside_pct']),
   r['statuses'].get('fused_multi_character_blob',0),r['statuses'].get('split_character_multi_blob',0),r['statuses'].get('no_letter_blob',0)]
  for r in d['spans']['by_stratum'] if r['dimension']=='all']),'',
 table(['Stratum','Dimension','Bucket','All slots','Clean','Outside','Outside %'],
 [[short[r['stratum']],r['dimension'],r['bucket'],r['all_slots'],r['clean'],r['outside'],p(r['outside_pct'])]
  for r in d['spans']['by_stratum'] if r['dimension']!='all']),'',
 'Geometry uses native cached predictions only. Greek/modern classification follows the saved line script; Latin is per character. Size uses the saved runtime x-height: <20, 20–34, ≥35 px. Fused, split and absent-blob cases are **diagnostic states, not automatically bad letters or bad physical print**. The full native slot ledgers and script × size/book tables remain [R0a span evidence](R0_evidence/span_summary.json) and [(i-a) span evidence](R0_evidence/ia/span_summary.json).',
 '',
 'For the **666 continuity instrument**, the original R1 mapper still omits 715/11,329 scored frozen samples: 698 share a primary blob and 17 have no overlapping primary letter blob. Every one is `localisation_unknown=True` and lacks `component_slot`; the historical mapper refuses non-unique ownership. The separate R1 extractor supports 261 with one component owner, 448 with shared owners and six with no owners under its own windows. These are evaluation/mapping omissions, not 715 missing letters. Every original reason is preserved in [R1_unmapped_715.jsonl](R0_evidence/R1_unmapped_715.jsonl) and the final failure ledger.',
 '',
 '## DATA / MODEL verdicts and training-track evidence','',
 'Each final ledger row has `DATA_MODEL`, a line ID, a slot with an explicit coordinate convention, prediction stream and evidence. Text errors use adjudicated print. **DATA** means the paired Google target is also wrong/missing at that error; **MODEL** means the paired Google target is correct, or the failure is runtime position/case mapping. These are evidence-backed routes for the training track, **not causal identification of which training example E3 consumed**. An observed held-out Google error is not proof that the same error was present in a consumed training row. Geometry cannot be attributed to text-label frequencies alone.',
 '',
 'The exact `import_real_v2_train.jsonl` was read once as a stream: 214,436 rows, SHA-256 `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`. Frequency evidence for every target letter and punctuation symbol is in [training_frequencies.json](R0_evidence/scoring/training_frequencies.json); per-error rows carry the relevant target frequency.',
 '',table(['Evidence scope / stratum','Symbol','Training occurrences','greek_poly occurrences','Implication'],[
 ['all training label scripts (not an audit accuracy stratum)',"ASCII ' / U+0027",5571,2908,'functional apostrophes present'],
 ['all training label scripts (not an audit accuracy stratum)','᾽ / U+1FBD',4027,3736,'spacing-koronis convention well represented'],
 ['all training label scripts (not an audit accuracy stratum)','’ / U+2019',2,0,'curly printed form has essentially no polytonic target coverage'],
 ['all training label scripts (not an audit accuracy stratum)','‘ / U+2018',21,8,'opening-single-quote target is rare'],
 ['all training label scripts (not an audit accuracy stratum)','“ / U+201C',130,45,'curly double quote exists but is uncommon'],
 ['all training label scripts (not an audit accuracy stratum)','Α / α', '29,471 / 882,246','13,664 / 571,413','case and Greek alpha targets exist'],
 ['all training label scripts (not an audit accuracy stratum)','Latin a',39675,2,'mixed-script routing remains a reading problem where Google is correct'],
 ['all training label scripts (not an audit accuracy stratum)','ſ',1,0,'historical Latin long-s coverage is scarce; do not infer broad competence']]),'',
 'DATA training arm: correct demonstrably bad letter targets and missing/misencoded quotes; choose and consistently normalize the desired apostrophe representation before changing capacity. The existing apostrophe detector may propose corrections, but its rejected breathing probes show why pixel validation is needed. MODEL arm: evaluate letter identity, mixed-script reading and deletion recovery with correct targets, and address pixel-case/component/CTC localisation separately. More width might help reading; this audit supplies no measured width gain and does not establish model capacity as the cause. Leave locked strata out of all selection/tuning.',
 '',
 '### Every observed type, with separate stratum counts and example IDs','',
 'Counts below are error/diagnostic slots, not unique lines. No stratum is pooled into an accuracy estimate. “Stored” includes the stored 666 instrument and the unchanged locked recognitions. Native variant errors and the DEV witness are in separate rows. Sparse subtypes have fewer than three observed lines; all actual IDs are shown. **The requested ≥3 distinct examples is not attainable for those sparse cells/types without inventing observations.** Their evidence is retained rather than suppressing or exaggerating them.',
 '']
groups=defaultdict(list)
for r in fs:groups[(r['prediction_stream'],r['type'],r['DATA_MODEL'])].append(r)
rows=[]
for (stream,typ,verdict),rr in sorted(groups.items()):
    counts=Counter(r['stratum'] for r in rr)
    rows.append([stream,typ,verdict]+[counts[s] for s in strata]+[counts['owner_DEV_supplement'],type_examples(rr)])
report += [table(['Prediction stream / stratum scope','Type','Verdict','666 continuity instrument','(ii) mark-enriched, not a population estimate','(i-a) selection-exposed (v2 val)','DEV excluded','Example line IDs with stratum'],rows),'',
 'The stored-stream letter totals route **4 DATA / 102 MODEL** errors for the 666 continuity instrument, **6 DATA / 146 MODEL** for (ii), and **0 DATA / 2 MODEL** for (i-a). For example, the weak historical-Latin targets `auch`, `ſ`, and `b` are not grounds to claim all mixed-script errors need a wider model. Conversely, correct paired Google targets and abundant target-letter frequencies support the MODEL route for the bulk of measured letter failures.',
 '',
 '## Locked-set scope and exposure','',
 '(ii) remains 200 lines / 11 sources from the seeded 20261017 M2 split; 273 measured cards remain DEV. Its explicit polytonic-mark selection makes it **mark-enriched, not a population estimate**. M2 was previously used for S7 qualification; freezing cannot undo that exposure. (i-a) remains 133 lines / three books, with 122 from Ἀστέρια. Its 131/133 collection-v2-val overlap means **selection-exposed (v2 val)**. It is reported beside, never pooled with, the other strata. The coming clean (i-b) is not measured here.',
 '',
 'Frozen receipts retain zero line/document/normalized-stem overlap with 666, detector DEV and L1 input, and zero (i-a)/(ii) overlap; crop-hash checks are also retained. (ii), new-source DEV and the 666+DEV instrument have zero v2-val overlap. Locked strata are never used for training, threshold/policy/checkpoint selection or tuning. See [IA freeze receipt](R0_locked_set_receipt.json), [new-source split receipt](R0_newsource_split_receipt.json), [IA exclusion IDs](R0_locked_ia_ids.txt) and [(ii) exclusion IDs](R0_newsource_exclusion_ids.txt).',
 '',
 '## Review page, validation and reproduction','',
 '[R0_review_failures.html](R0_review_failures.html) contains exactly 60 distinct lines, all observed failure categories and all strata, plus the DEV witness. Each row has its line ID/stratum, full crop, thin native CTC letter-span boxes and letter labels, Google line, native recogniser line, stored line when different, card truth scopes and one note placeholder with local autosave/export. It is written locally; **the track lead publishes it**. Geometry badges identify diagnostics rather than certifying text errors.',
 '',
 'Machine checks verify source/truth/cache hashes unchanged, disjoint word windows, independent edit-count agreement, the 160-card case join, UNKNOWN exclusions, all 60 embedded PNGs and SVG span counts, single note fields, no external page resources and JavaScript syntax. Browser visual/interaction QA is **unverified**: the cached headless Firefox build aborts in this sandbox, and computer-use access to Firefox was not approved. No browser download or publication was attempted. Native card images were inspected for the clipped UNKNOWN and distinct opening-quote versus breathing probes; this is not browser layout proof.',
 '',
 f"Launch head `{d['head_at_launch']}` on `opus/spellcheck-r0`. Local Mac CPU, network off, zero new CTC forwards, no model/detector changes and no `.git` mutation commands. [Validation receipt](R0_evidence/scoring/validation.json), [machine metrics](R0_metrics.json), [per-failure ledger](R0_failures.jsonl), [original R0a/R0a2 report snapshot](R0_evidence/scoring/R0a_REPORT_snapshot.md).",
 '',
 'Reproduce with the specified venv Python and `PYTHONPATH=$PWD`, `PYTHONDONTWRITEBYTECODE=1`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `GIT_OPTIONAL_LOCKS=0`: run `scripts/labelfix/r0_score.py`, `scripts/labelfix/r0_score_validate.py`, then `scripts/labelfix/r0_score_report.py`. These scripts neither forward crops nor change runtime/model data.',
 '',
 'R0 RESULT: letter truth 2376 slots/361 lines (word-card scopes; 0 full lines certified); letter error 6.50% (case-folded 6.43%) on 666 continuity instrument, (ii) 24.56% (24.23%; mark-enriched, not a population estimate), (i-a) 1.60% (1.60%; selection-exposed (v2 val)), all on adjudicated word cards only; spans outside blob 3.92% (historical 666+(ii) diagnostic); case disagreements recogniser right 100.00% (160/160; stratified extrapolation 753/753); apostrophes emitted 99.53% of printed on 666 (212/213; (ii) 2/2, (i-a) 9/9); DATA types letter-label errors, apostrophe/quote representation and missing quote labels; MODEL types letter substitution/insertion/deletion/case/script, punctuation reading, S5 pixel case, CTC span/component localisation and frozen R1 mapping.'
]
(OUT/'R0_REPORT.md').write_text('\n'.join(report)+'\n')
print('R0_REPORT.md written')
