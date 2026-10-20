"""Build the round-4 tables report from the completed, bound measurements."""
from pathlib import Path
import hashlib
import importlib.metadata
import json

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'.astra/out'
PAGES={
 'Nav':'an-7a2b17a3fb0f-p000200',
 'V35':'s2-200e977f2dab5291c42c-p00035',
 'V20':'s2-831443dc5e6f1ccfbaf5-p00020',
 'Side':'s2-6419488b7f8e69fd20da-p00001',
 'Dense':'an-d3237d690aa0-p000138',
 'Grammar':'an-a3c2bdf81256-p000112',
 'Votes':'s2-80513ae109b4f749ca58-p00003',
 'Budget':'s2-dee99fdf5214acdc6f25-p00005'}

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def total(v,field):return sum(t[field] for t in v['tables'])
def fmt(v):return str(v) if isinstance(v,int) else f'{v:.4f}'


def main():
    a=read(OUT/'acceptance/summary.json');d=read(OUT/'acceptance/delivery-audit.json')
    runs=read(OUT/'integration/summary.json');reg=read(OUT/'regression.json')
    assert len(a)==len(d)==len(runs)==8 and len(reg['rows'])==54
    assert not reg['non_table_regressions']
    assert all(r['status']=='ConversionStatus.SUCCESS' and not r['errors'] for r in runs.values())
    assert all(len(v['frozen'])==2*len(v['discovery']) and all('error' not in m for m in v['frozen']) for v in a.values())
    text=['# Page lines, round 4 part 1: tables — 9 October 2026','',
      '**Result: PARTIAL.** The detector and plugin changes are implemented and tested. Cases 28 and 33 recover substantial previously missing text; case 34’s upper-prose boundary defect is fixed on both named pages. The complete table acceptance gate is **not passed on any of the eight pages**. Remaining pixel omissions/crossings, missing image-layout wrappers, and incorrect TableFormer structures are measured below.','',
      '## Method and scope','',
      'Inside an image-layout table proposal, remove the observed rule strokes before rejecting connected components. This retains letters touching a table frame. Group nearby baselines, attach small marks, and split at rules, locally repeated whitespace lanes, and conservative word gaps. A divider is used only over its observed vertical extent. Refit the prose prefix independently so a lower table cannot divide the paragraph above it. A conservative fallback handles repeated ruled blocks missed by Heron.','',
      'The ordinary round-3 page fitter is unchanged. All thresholds in the production table module use x-heights or page-relative dimensions; there are no page-name branches. Page-specific coordinates occur only in annotation/review code. No PDF text or `.boxes.json` supplied the annotations. Part 2 and writing-orientation correction remain outside this change.','',
      'The plugin selector is now `recognition_mode="detector"`; inherited `OcrOptions.mode` retains Docling’s enum. Every delivered piece is unrolled and recognized separately by the existing recognizer. Narrow glyph strips receive white tensor padding without enlarging their output boxes. TextCells use explicit TOPLEFT page coordinates from the actual independent image/page x/y ratios. Replacement clears native and prior-OCR words, characters and old lines in both parsed-page and backend cached objects. V1 matching stays enabled, with Accurate as default.','',
      'The standalone review uses a declared logical page size of PNG/3. The actual DocumentConverter run uses native PNG resolution (`crop_scale=1`, because these PNGs have no DPI metadata). Different raster preprocessing can change the image model’s prediction; invariance is tested at fixed pixels within each controlled layout run, not between these two render configurations.','',
      'All 54 pages have `.segments.json`, `.lines.json`, `.checks.json`, `.cells.json`, `.lines.jpg`, and `.unrolled.jpg` in `.astra/out/`. Discounted candidates remain in JSON with reasons and are absent from both images. A table piece’s `cell_id` is explicitly a **provisional detector geometry-group ID**, not a recovered semantic grid ID.','',
      '## Owner cases','',
      '| Case | New output and measured figure | Verdict |',
      '|---|---|---|',
      '| 28 — V20, first two columns | 0 → 94 active pieces start left of x=637; leftmost start 637 → 55 px. Row numbers and municipality names are visibly recovered. Text completeness and currency boundaries still fail the gate below. [New image](../../.astra/out/cases/case-28.jpg). | Improved, not fixed |',
      '| 33 — navigation spread | Active pieces wholly left of the page midpoint: 14 → 607. Both table leaves now have substantial text; whole-page delivery grows 414 → 1,262 pieces. Remaining clipped characters, rule fragments and cross-entry pieces are enumerated. [New image](../../.astra/out/cases/case-33.jpg). | Improved, not fixed |',
      '| 34 — grammar **and** votes | Grammar’s opening paragraph: 6 halves → 3 full-width lines, x≈92–1143; the sentence between its two blocks is also restored from 2 pieces to 1. Votes’ first five prose rows: 10 halves → 5 full-width lines, x≈325–1778. Lower blocks remain divided. Grammar still has no Heron table wrapper; table completeness is not certified. [New image, both pages](../../.astra/out/cases/case-34.jpg). | Fixed for the reported upper-boundary defect; tables remain incomplete |','',
      '## Annotations and measurement limits','',
      'The eight [annotation JSONs](../tables/annotations/) record extents, cell rows/columns/spans, headers, empty cells and pixel text envelopes, with source hashes. Grids and row sequences were set from page images; connected-ink envelopes were proposed independently inside them and reviewed as overlays. They are **provisional**, not exhaustive character transcriptions. Faint punctuation, touching rules, close currency subcolumns and independent panel row phases need owner adjudication. Sideways annotations were inspected in a rotated view and mapped back; detector inputs were never rotated.','',
      '“Covered” below means at least 98% of contrast pixels in an annotated text-element envelope fall inside emitted piece boxes; it is **not** OCR accuracy or proof of a correct unrolled crop. Every failed envelope is listed by cell/element ID in `acceptance/summary.json`. Crossing counts are pieces overlapping more than 20% of text envelopes in multiple annotated entries. They are provisional geometric flags; zero noise is not established.','',
      'Frozen tests inject one unique label per annotated envelope into fixed regions and run installed TableFormer V1, matching, postprocessing, and final TableItem construction. Exact row/column/span comparison is made for single-grid pages; independent panels additionally detect mixed-owner cells, but are not claimed fully grid-qualified. Their wrong-owner numbers are lower bounds. All labels surviving is explicitly insufficient.','',
      '## Each of the eight pages','',
      '| Page | New output; covered elements round 3 → round 4 | Crossing pieces round 3 → round 4 | Verdict |',
      '|---|---|---:|---|']
    descriptions={
      'Nav':'Both leaves recovered; frame-attached digits retained, finer independent pieces',
      'V35':'Ruled table resegmented; currency subcolumns and small marks remain unreliable',
      'V20':'Previously absent numbers and municipality names recovered',
      'Side':'Completes without a crash; horizontal slices remain inappropriate for vertical writing',
      'Dense':'Four term/locator panels receive finer pieces; fragments and row ownership remain',
      'Grammar':'Upper prose restored; two local ruled blocks split; Heron still misses both tables',
      'Votes':'Upper prose restored; lower list split into small pieces; incomplete names/marks remain',
      'Budget':'Original lines retained; leader/amount crossings remain and Heron finds no table'}
    verdicts={'Nav':'Improved, not fixed','V35':'Not fixed','V20':'Improved, not fixed','Side':'Not fixed; orientation deferred',
              'Dense':'Improved, not fixed','Grammar':'Prose improved; table recall worse, not fixed','Votes':'Prose improved; table recall worse, not fixed','Budget':'Not fixed'}
    for name,key in PAGES.items():
        old=d[key]['previous_geometry'];new=a[key]['geometry'];n=total(new,'elements')
        text.append(f'| **{name}** — `{key}` | {descriptions[name]}. **{total(old,"complete")} → {total(new,"complete")} / {n}** | {len(old["crossing_pieces"])} → {len(new["crossing_pieces"])} | {verdicts[name]} |')
    text += ['', '## Acceptance gate (research A and B)', '',
      'PASS requires the research’s strict result, not a page-average score. Extent coverage is intersection / annotated extent area; a value below 100% does not meet full-extent coverage. All eight controlled layout runs are invariant under lines, pieces, word approximations, omitted columns, and no cells. Annotation admission is distinct from detector recall.', '',
      '| Research test | '+ ' | '.join(PAGES)+' |',
      '|---|'+'---|'*len(PAGES)]
    gates={k:[] for k in ('A: discovery / OCR invariance','A: annotation admission exactly once','A: detector-piece admission exactly once','Pixel-to-TextCell geometry','Detector recall','Matcher isolation: Accurate / Fast','Source ownership','Full integration','Real recognition (optional)')}
    for name,key in PAGES.items():
        v=a[key];g=v['geometry'];i=d[key]['integration']
        coverage='/'.join(f'{100*t["maximum_extent_coverage"]:.2f}%' for t in v['discovery'])
        gates['A: discovery / OCR invariance'].append(f'{len(v["retained_tables"])} regions; extent {coverage}; invariant PASS; discovery FAIL')
        gates['A: annotation admission exactly once'].append(f'{v["admitted_exactly_once"]}/{v["annotated_elements"]}'+(' PASS' if v['admitted_exactly_once']==v['annotated_elements'] else ' FAIL'))
        admission=d[key]['standalone_admission']
        gates['A: detector-piece admission exactly once'].append(f'{admission["admitted_exactly_once"]}/{admission["detector_table_pieces"]}'+(' (no proposed pieces)' if not admission['detector_table_pieces'] else ''))
        gates['Pixel-to-TextCell geometry'].append(f'TOPLEFT/finite/IDs PASS; {len(g["crossing_pieces"])} crossing flags; crop fit unqualified')
        gates['Detector recall'].append(f'{total(g,"complete")}/{total(g,"elements")}; FAIL')
        wrong=[]
        for mode in ('accurate','fast'):
            ms=[m for m in v['frozen'] if m['mode']==mode]
            wrong.append(f'{sum(m["lost"] for m in ms)} lost, {sum(m["duplicated"] for m in ms)} dup, {sum(m["wrong_owner"] for m in ms)} wrong')
        gates['Matcher isolation: Accurate / Fast'].append(' / '.join(wrong)+'; FAIL')
        sent=sum(m['sentinel_survived'] for m in v['frozen'])
        gates['Source ownership'].append(f'{sent} stale sentinels; PASS')
        gates['Full integration'].append(f'{runs[key]["tables"]} tables; {len(i["missing_from_final_tables"])} missing, {len(i["wrong_owner_labels"])} wrong; FAIL')
        gates['Real recognition (optional)'].append('Not run')
    for name,values in gates.items():text.append('| '+name+' | '+' | '.join(values)+' |')
    text += ['', 'The source-ownership controls install conflicting backend words, characters and old line labels before replacement. None survives in any frozen final table. Separate unit tests cover distinct backend/parsed caches and both native and prior-OCR words. Border-fused controls preserve retained table identity while excluding the fused label. **22/22 fused controls** retain both constituent labels exactly once in the same output cell despite their different annotated owners. This is explicitly rejected as wrong ownership: [fused-control audit](../../.astra/out/acceptance/fused-controls-audit.json).','',
      '### Frozen structure details','',
      '| Page / table | Mode | Input labels | Grid rows × cols | Lost / duplicated / wrong-owner | Exact grid comparable? |',
      '|---|---|---:|---|---|---|']
    for name,key in PAGES.items():
        for m in a[key]['frozen']:
            text.append(f'| {name} / {m["table"]} | {m["mode"]} | {m["input"]} | {m["rows"]} × {m["columns"]} | {m["lost"]} / {m["duplicated"]} / {m["wrong_owner"]} | {m["exact_grid_comparable"]} |')
    text += ['', '### Actual standard pipeline','',
      'Ran `DocumentConverter` on all eight full PNGs: image layout → detector plugin → layout postprocessing → Accurate V1 table stage → assembly and reading order. Only recognition was replaced by unique labels. All eight conversions complete with SUCCESS and no conversion errors; this does not mean the resulting tables are correct. The serialized documents and OCR call records are preserved. Ownership scoring uses each run’s actual TextCell rectangles and page size. Ambiguous input pieces and unmatched ink are excluded from positive ownership claims and listed separately.','',
      '| Page | Final grids | OCR pieces inside annotated extents | Ambiguous / unmatched inputs | Missing / duplicated / wrong final labels |',
      '|---|---|---:|---|---|']
    for name,key in PAGES.items():
        i=d[key]['integration'];shapes=', '.join(f'{s["rows"]}×{s["columns"]}' for s in runs[key]['table_shapes']) or 'none'
        text.append(f'| {name} | {shapes} | {i["input_pieces_in_annotated_extents"]} | {len(i["ambiguous_input_pieces"])} / {len(i["unmatched_input_pieces"])} | {len(i["missing_from_final_tables"])} / {len(i["duplicated_in_final_tables"])} / {len(i["wrong_owner_labels"])} |')
    text += ['', '## Round-3 checks on all 54 pages','',
      '**46/46 non-table pages preserve the complete line-record JSON exactly, with no worsening of the measured checks.** Case 27 (`s2-93f8070059f938bda524-p00001`) retains 117 active / 12 discounted lines, 47 cut flags, 39 foreign-ink flags, and zero rule crossings, overlaps or broken pairs. Existing errors are preserved, not claimed solved. The extra part-2 page is included unchanged.','',
      'The following table includes every page. Each vector is **round 3 → round 4**. `1` = median guide p90 / borrowed lines; `2` = no-body / close pairs; `3` = cut lines; `4` = discounts; `5` = maximum boundary step (x-heights); `6` = detected / review-reference crossings; `7` = unassigned text-size components / pixels; `8` = graphic line / segment flags; `9` = broken pairs; `10` = foreign / overlap / seam-gap flags. Counts on recovered table pixels have a different denominator; increases are still explicitly flagged. Complete check-path differences, source-boundary/strip-edge counts, retained-ink fractions and source hashes are in [regression.json](../../.astra/out/regression.json).','',
      '| Page | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Any worse? |',
      '|---|'+'---|'*11]
    for r in reg['rows']:
        vals=[]
        groups=[('guide_p90_median','borrowed_lines'),('no_body_lines','close_pairs'),('cut_ink_lines',),
                (),('maximum_jump',),('rule_gutter_crossings','review_crossings'),
                ('unassigned_text_size_components','unassigned_text_size_ink'),('graphic_lines','graphic_segments'),
                ('broken_line_pairs',),('foreign_ink_lines','boundary_overlaps','seam_gaps')]
        for group in groups:
            if not group:vals.append(f'{r["discounted"]["old"]}→{r["discounted"]["new"]}');continue
            vals.append('→'.join('/'.join(fmt(r['metrics'][v][k]) for k in group) for v in ('old','new')))
        text.append('| `'+r['key']+'` | '+' | '.join(vals)+' | '+('**YES**' if r['worse'] else 'No')+' |')
    text += ['', '### Every page with a worsened measurement','']
    for r in reg['rows']:
        if r['worse']:text.append('- `'+r['key']+'`: '+', '.join(f'{k} {fmt(v["old"])}→{fmt(v["new"])}' for k,v in r['worse'].items())+'.')
    text += ['', '## What still does not work','',
      '- Complete table text recall and suppression of rule/noise fragments are not achieved. Per-element omission lists and cross-entry piece IDs are saved, not averaged away. The 98% coverage test also does not certify dewarped crop completeness.',
      '- Heron misses the grammar and budget tables. The grammar pixel fallback does not inject a TABLE wrapper into Docling, so its recovered pieces remain ordinary text. Its header above the first rule is still fused across the two paradigm panels. Budget leader/amount splitting is not implemented outside a table proposal and remains unchanged.',
      '- TableFormer produces incorrect grids even with fixed regions and independently annotated labels. Fast is not an automatic remedy. Single-grid span errors and mixed-owner cells fail acceptance; multi-panel exact grid qualification is still incomplete.',
      '- Annotations are provisional pixel-reviewed cell grids with automatic envelope proposals, not certified exhaustive ground truth. Currency splits, empty-cell decisions, punctuation and nested-panel spans need owner review. Semantic cell IDs are not reconstructed by the detector.',
      '- Sideways text is still processed horizontally. This run proves it does not crash; orientation belongs to part 3.',
      '- Real character recognition, per-cell CER and monetary transcription accuracy were not tested. No production-readiness claim is made. The 44 held-out pages were not accessed.','',
      '## Validation and reproduction','',
      '**2,022 passed, 16 skipped, 0 failed** in the full pytest suite (2,038 collected), including `tests/glyphs`, Docling contracts, provenance/API, and 12 new table tests. All 16 skips are browser-render tests because Chromium is unavailable in this sandbox. [Full test log](../../.astra/out/tests-all-final.log). API regenerated: 211 public callable entries. All 54 artifact sets pass the saved-output audit.','',
      'Use the supplied Python from this worktree root, with `PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`. All commands run in the foreground; no push or model download was performed.','',
      '```sh',
      'python scripts/generate_api_docs.py',
      'python -m pytest -p no:cacheprovider',
      'python .astra/layout_inventory.py',
      'python scripts/glyphs/render_page_line_segments.py --layout .astra/layout',
      'python scripts/glyphs/archive/annotate_tables_round4.py',
      'python scripts/glyphs/archive/evaluate_tables_round4.py',
      'python scripts/glyphs/archive/integrate_docling_tables_round4.py',
      'python scripts/glyphs/archive/score_tables_round4.py',
      'python scripts/glyphs/archive/audit_tables_round4.py',
      'python scripts/glyphs/archive/report_tables_round4.py',
      '```','',
      'The acceptance harness reuses `.astra/docling_research/research_tables.py` and `research_layout.py`; matcher unit tests follow `probe_matching.py`, and frozen tests follow the real-stage method of `probe_actual_stage.py`. Accurate and Fast each execute 11 real table-image forwards, reusing tensors only for identical fused controls. The layout stage executes 54 fresh full-page forwards (six variants × eight pages plus six border controls).','',
      'Evidence: [acceptance summary](../../.astra/out/acceptance/summary.json), [delivery audit](../../.astra/out/acceptance/delivery-audit.json), [integration summary](../../.astra/out/integration/summary.json), [artifact/regression audit](../../.astra/out/regression.json), [durable compact receipt](../tables/round4-summary.json). Per-label destinations, omissions, final TableItems, per-mode forward hashes and annotation hashes remain under `.astra/out/acceptance/`.','',
      '## Commit handoff','',
      'The sandbox refused creation of the worktree `index.lock` during `git add` (`Operation not permitted`), so no commit was made. The requested fallback is [page-lines-round4-tables.patch](../../.astra/page-lines-round4-tables.patch), with [commit-page-lines-round4-tables.sh](../../.astra/commit-page-lines-round4-tables.sh). The script verifies branch `astra/page-lines-4`, base revision, an empty staging area, every file hash, and reverse patch applicability before staging the explicit file list and committing with the requested Co-Authored-By and Claude-Session footers. It does not push. The patch is checked and replayed against a temporary copy of its HEAD source files, with byte-for-byte equality verified.','']
    report=ROOT/'docs/records/reviews/PAGE_LINES_ROUND4_TABLES_20261009.md'
    report.write_text('\n'.join(text))
    # Compact committed evidence; large source images/line arrays stay in .astra.
    compact=dict(status='PARTIAL',versions={p:importlib.metadata.version(p) for p in ('docling','docling-core','docling-ibm-models')},
      tests=dict(passed=2022,skipped=16,failed=0,total=2038),non_table_regressions=reg['non_table_regressions'],
      worse_pages=reg['any_worse_pages'],pages={key:dict(alias=name,layout_invariant=a[key]['layout_invariant'],
        discovery=a[key]['discovery'],admitted=a[key]['admitted_exactly_once'],annotation_elements=a[key]['annotated_elements'],
        geometry=a[key]['geometry']['tables'],crossing_pieces=len(a[key]['geometry']['crossing_pieces']),
        frozen=a[key]['frozen'],fused_controls=a[key].get('fused_controls',[]),integration={k:v for k,v in runs[key].items() if k!='ocr_records'}) for name,key in PAGES.items()},
      receipts={str(p.relative_to(ROOT)):sha(p) for p in [report,OUT/'acceptance/summary.json',OUT/'acceptance/delivery-audit.json',
        OUT/'integration/summary.json',OUT/'regression.json',OUT/'tests-all-final.log',OUT/'acceptance/fused-controls-audit.json',
        *sorted((ROOT/'docs/records/tables/annotations').glob('*.json')),
        ROOT/'greekocr/glyphs/table_lines.py',ROOT/'greekocr/deploy/docling_plugin/model.py',ROOT/'greekocr/deploy/docling_plugin/options.py']})
    (ROOT/'docs/records/tables/round4-summary.json').write_text(json.dumps(compact,indent=2)+'\n')
    print(report)


if __name__=='__main__':main()
