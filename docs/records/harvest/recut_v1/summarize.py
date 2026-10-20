"""Pair exact frozen-arm predictions and publish T6a evidence (never W1)."""
from __future__ import annotations
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
import platform
import sys
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(OUT))
from run_f2 import SOURCES, BLIND, OCR, FEATURES, stratum, rows, read_json, write_json, write_rows, file_sha256


def paired_stats(rr, key):
    if not rr:
        return dict(lines=0,original_cer=None,recut_cer=None,difference=None,
                    paired_bootstrap_95ci=None,page_bootstrap_95ci=None)
    refs=np.array([r['ref_len'] for r in rr],np.int64)
    old=np.array([r['original_edits'] for r in rr],np.int64)
    new=np.array([r['recut_edits'] for r in rr],np.int64)
    delta=new-old
    rng=np.random.default_rng(int(hashlib.sha256(key.encode()).hexdigest()[:16],16))
    differences=[]
    for _ in range(50):
        indices=rng.integers(0,len(rr),size=(100,len(rr)))
        differences.extend((delta[indices].sum(axis=1)/refs[indices].sum(axis=1)).tolist())
    pages=defaultdict(lambda:np.zeros(2,np.int64))
    for r,d,n in zip(rr,delta,refs):
        pages[(r['stratum'],r['page_id'])]+=np.array([d,n])
    groups=np.array(list(pages.values()))
    page_differences=[]
    for _ in range(50):
        indices=rng.integers(0,len(groups),size=(100,len(groups)))
        sums=groups[indices].sum(axis=1)
        page_differences.extend((sums[:,0]/sums[:,1]).tolist())
    return dict(lines=len(rr),pages=len(pages),ref_len=int(refs.sum()),
        original_edits=int(old.sum()),recut_edits=int(new.sum()),
        original_cer=float(old.sum()/refs.sum()),recut_cer=float(new.sum()/refs.sum()),
        difference=float(delta.sum()/refs.sum()),
        paired_bootstrap_95ci=np.quantile(differences,[.025,.975]).tolist(),
        page_bootstrap_95ci=np.quantile(page_differences,[.025,.975]).tolist(),
        improved_lines=int((delta<0).sum()),worsened_lines=int((delta>0).sum()),
        equal_lines=int((delta==0).sum()))


def visual_review(records):
    """Persist the actual unblinded inspection, separate from blind verdicts."""
    out=[]
    for r in records:
        if not r['dev']:
            continue
        source,card=r['stratum'],r['dev']['card_id']
        overrun='crop_overrun' in r['dev']['errors']
        removed=source=='gazette_modern' and card in ('c015','c038')
        out.append(dict(id=r['id'],source=source,card_id=card,original_crop_ok=r['dev']['crop_ok'],
            inspection='unblinded agent: all 32 paired contact sheets plus three native 3x change witnesses',
            sheet=f'dev/review/{source}/sheet{(int(card[1:])-1)//5+1:02d}.png',
            original_overrun=overrun,
            readable_neighbour_removed=removed if overrun else None,
            new_own_ink_cutoff_seen=False if r['dev']['crop_ok']=='y' else None,
            own_component_pixels_lost=r['own_pixels_lost'],
            note=('Horizontal clip after Ἐ persists; vertical tightening cannot repair it.'
                  if source=='lekythos_poly1900' and card=='c037' else
                  'Readable neighbour fragments removed; not a new blind verdict.' if removed else
                  'Original rectangle retained; original overrun persists.' if overrun else
                  'No newly cut own body/accent/descender seen; component guard is not independent physical truth.')))
    return out


def validate_native(records):
    current_path,current=None,None
    expected={r['id']:r for r in rows(FEATURES) if stratum(r)}
    assert set(expected)=={r['id'] for r in records}
    checked=0
    for r in records:
        old,new=r['old_box'],r['new_box']
        feature=expected[r['id']]
        assert old==feature['crop_bbox'] and r['google_text']==feature['label_after_conventions']
        assert r['original_page']==feature['crop_page_path'] and r['stratum']==stratum(feature)
        assert old[0]==new[0] and old[2]==new[2] and old[1]<=new[1]<new[3]<=old[3]
        assert r['params_sha256']==read_json(OUT/'params.json')['params_sha256']
        assert r['own_pixels_lost']==0
        path=OUT/r['recut_path'];assert file_sha256(path)==r['recut_sha256']
        if current_path!=r['original_page']:
            with Image.open(r['original_page']) as image:current=image.copy()
            current_path=r['original_page']
        assert 0<=old[0]<old[2]<=current.width and 0<=old[1]<old[3]<=current.height
        assert 0<=new[0]<new[2]<=current.width and 0<=new[1]<new[3]<=current.height
        with Image.open(path) as image:
            assert image.mode==current.mode
            assert np.array_equal(np.asarray(image),np.asarray(current.crop(tuple(new))))
        if not r['changed']:
            assert r['recut_sha256']==r['original_crop_sha256']
        if r['dev']:
            with Image.open(BLIND/r['stratum']/'crops'/f"{r['dev']['card_id']}.png") as card:
                assert np.array_equal(np.asarray(card),np.asarray(current.crop(tuple(old))))
        checked+=1
    freeze=read_json(OUT/'params.json')
    for path,digest in freeze['inputs'].items():assert file_sha256(path)==digest
    for p in rows(OUT/'f2/provenance.jsonl'):
        cache=Path(p['cache']);receipt=read_json(cache/'receipt.json')
        assert file_sha256(p['source'])==p['source_sha256']
        assert file_sha256(p['raw_response'])==p['raw_sha256']
        assert file_sha256(cache/'receipt.json')==p['cache_receipt_sha256']
        for filename,key in [('detector.json.gz','geometry_sha256'),('ink.png','mask_sha256'),('labels.npz','labels_sha256')]:
            assert file_sha256(cache/filename)==receipt[key]
    return dict(native_crops_checked=checked,literal_native_subarray=True,
        unchanged_png_hash_identity=True,no_vertical_expansion=True,horizontal_extent_unchanged=True,
        accepted_own_component_pixels_lost=0,all_frozen_inputs_reverified=True,
        source_pages_and_response_cache_bytes_reverified=True,development_crops_match_pinned_v2=True,all_labels_boxes_and_source_scope_match_pinned_features=True,w1_accessed=False)


def main():
    frozen=read_json(OUT/'params.json');binding=read_json(OUT/'harm/binding.json')
    for name,key in [('train/eval_cer.py','evaluator_sha256'),('train/data.py','collator_sha256'),('bench/o4b_models.py','preprocessing_sha256')]:
        assert file_sha256(OCR/name)==binding[key], 'evaluator source changed during readout'
    for name,key in [('out/e4/wave1a/job01/runs/ctrl_s0/best.pt','model_sha256'),('out/e4/wave1a/job01/runs/ctrl_s0/best.safetensors','weights_sha256'),('codec/v1.json','codec_sha256')]:
        assert file_sha256(OCR/name)==binding[key], 'model or codec changed during readout'
    records=rows(OUT/'f2/records.jsonl');old={r['id']:r for r in rows(OUT/'harm/original.jsonl')};new={r['id']:r for r in rows(OUT/'harm/recut.jsonl')}
    assert len(old)==len(new)==len(records)==5770
    assert set(old)==set(new)=={r['id'] for r in records}
    for arm in ('original','recut'):
        receipt=read_json(OUT/f'harm/{arm}.receipt.json')
        assert file_sha256(OUT/f'harm/{arm}.jsonl')==receipt['predictions_sha256']
        assert receipt['binding']==binding
    for r in records:
        a,b=old[r['id']],new[r['id']]
        assert a['ref']==b['ref'] and a['ref_len']==b['ref_len']
        r.update(ref_len=a['ref_len'],original_edits=a['edits'],recut_edits=b['edits'])
        if not r['changed']:
            assert a['prediction']==b['prediction'] and a['edits']==b['edits']
    stats={}
    subsets=dict(all=lambda r:True,changed=lambda r:r['changed'],unchanged=lambda r:not r['changed'],
                 dev_crop_n=lambda r:r['dev'] is not None and r['dev']['crop_ok']=='n',
                 dev_crop_y=lambda r:r['dev'] is not None and r['dev']['crop_ok']=='y',
                 geometry_clean=lambda r:r['geometry_clean'],
                 screen_merged_flag=lambda r:r['screen_merged'])
    for source in (*SOURCES,'overall'):
        source_rows=[r for r in records if source=='overall' or r['stratum']==source]
        stats[source]={name:paired_stats([r for r in source_rows if select(r)],source+':'+name) for name,select in subsets.items()}
    write_json(OUT/'harm/summary.json',dict(metric='corpus strict NFD CER',difference='recut minus original',
        bootstrap='5000 paired line resamples and 5000 paired whole-page cluster resamples; percentile 95%; deterministic per-cell SHA256 seed',
        bootstrap_unit_disclosure='Primary line intervals assume exchangeable lines; page intervals resample whole source/page clusters. Overall page bootstrap allows source mix to vary.',
        results=stats))
    joined=[dict(id=r['id'],stratum=r['stratum'],page_id=r['page_id'],changed=r['changed'],
                 geometry_clean=r['geometry_clean'],dev_crop_ok=r['dev']['crop_ok'] if r['dev'] else None,
                 original_edits=r['original_edits'],recut_edits=r['recut_edits'],ref_len=r['ref_len']) for r in records]
    write_rows(OUT/'harm/paired.jsonl',joined)
    review=visual_review(records);write_rows(OUT/'dev/visual_review.jsonl',review)
    integrity=validate_native(records);write_json(OUT/'validation.json',integrity)
    grid=read_json(OUT/'dev/grid.json')['0.3/0.3']
    # Use the exact original protocol, not a revised local definition.
    protocol=ROOT.parent/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/v2/LABEL_CHECK_v2.md'
    for source in SOURCES:
        rr=[r for r in records if r['stratum']==source];v=[r for r in review if r['source']==source]
        receipt=dict(schema='t6a-recut-source-1',source=source,parameters=frozen['params'],params_sha256=frozen['params_sha256'],
            cutter_sha256=frozen['cutter_sha256'],params_receipt_sha256=file_sha256(OUT/'params.json'),
            f2_provenance_sha256=file_sha256(OUT/'f2/provenance.jsonl'),model_sha256=binding['model_sha256'],weights_sha256=binding['weights_sha256'],
            frozen_utc=frozen['frozen_utc'],dev=grid[source],
            dev_visual=dict(overrun_cards=sum(x['original_overrun'] for x in v),
                readable_neighbour_removed=sum(x['readable_neighbour_removed'] is True for x in v),
                new_own_cutoff_seen_on_crop_y=sum(x['new_own_ink_cutoff_seen'] is True for x in v),
                review_path='dev/visual_review.jsonl'),
            harm=stats[source],harm_overall=stats['overall']['all'],
            harm_rule_pass_overall=stats['overall']['all']['difference']<=0,
            harm_source_nonworsening_point=stats[source]['all']['difference']<=0,
            model_path=str(OCR/'out/e4/wave1a/job01/runs/ctrl_s0/best.pt'),
            native_lines=len(rr),changed_lines=sum(r['changed'] for r in rr),
            native_crop_height_xh=dict(before_median=float(np.median([r['before_height_xh'] for r in rr if r['before_height_xh'] is not None])),
                after_median=float(np.median([r['after_height_xh'] for r in rr if r['after_height_xh'] is not None]))),
            statuses=dict(Counter(r['status'] for r in rr)),
            row_records=f'f2/{source}/records.jsonl',row_records_sha256=file_sha256(OUT/f'f2/{source}/records.jsonl'),
            qualification=dict(status='not_run; separate T6b',cards=None,key=None,w1_accessed=False,
                v2_letters_y=sum(r['dev']['letters']=='y' for r in rr if r['dev']),v2_cards=40,v2_crop_ok_y=grid[source]['crop_y'],
                protocol=str(protocol),protocol_sha256=file_sha256(protocol),
                gate='crop_ok >=90%; letters-y >= same-source v2; no crop_clipped own ink cut-off',
                row_admission='none; pending owner blind gate'),
            validation=integrity)
        write_json(OUT/source/'receipt.json',receipt)
    counts=dict(reused_direct_repository_functions=14,added_library_functions_and_methods=
                sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) for n in ast.walk(ast.parse((ROOT/'greekocr/glyphs/vertical_recut.py').read_text()))),
                added_all_named_functions_and_methods=sum(sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) for n in ast.walk(ast.parse(p.read_text()))) for p in [ROOT/'greekocr/glyphs/vertical_recut.py',OUT/'run_f2.py',OUT/'summarize.py',OUT/'guarded_commit.py',ROOT/'tests/glyphs/test_vertical_recut.py']),
                counting='direct repo calls exclude third-party and inspected-only functions; all additions count named functions and methods across library, experiment scripts, helper and tests, including nested functions and fixtures')
    counts['added_definitions_by_file']={str(p.relative_to(ROOT)): [n.name for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))] for p in [ROOT/'greekocr/glyphs/vertical_recut.py',OUT/'run_f2.py',OUT/'summarize.py',OUT/'guarded_commit.py',ROOT/'tests/glyphs/test_vertical_recut.py']}
    write_json(OUT/'function_counts.json',counts)
    completed=datetime.now(timezone.utc)
    task_start=datetime.fromisoformat('2026-10-16T22:24:47+00:00')
    elapsed=(completed-task_start).total_seconds()
    assert elapsed<=7200, 'T6a 120-minute wall budget exceeded'
    write_json(OUT/'runtime.json',dict(python=sys.version,platform=platform.platform(),
        task_started_utc=task_start.isoformat(),task_elapsed_seconds=elapsed,within_120_minutes=True,
        numpy=np.__version__,packages={p:version(p) for p in ('torch','Pillow','scipy','safetensors')},completed_utc=completed.isoformat(),
        script_hashes={p.name:file_sha256(p) for p in (OUT/'run_f2.py',OUT/'summarize.py')},
        network='OFF; process connection entrypoints forbidden; no provider/SSH calls',
        w1='Not read, written, locked or qualified'))
    lines=['# T6a: frozen vertical tightening on F2', '',
        'T6a completes steps 0, 1 and 3 only. Step 2 is deferred to T6b; W1 was not accessed. No rows are admitted by this run. Original source trees and crops remain unchanged.', '',
        '## Development results', '',
        'The exact 2f34ed52 v2 keys, cards and saved verdict bytes were verified using `git show` before development; the complete features file also matches that revision byte-for-byte ([input identity](INPUTS.json)). The eligible F2 pool uses `fixed_usable` and no `text_exclusions`; it deliberately includes screen-rejected crops to expose merged-line effects. No new Google calls, page segmentation, label changes, horizontal edits or outward expansion occurred.', '',
        '| Source | v2 n/y | Median crop height xh before → after | Changed | Readable neighbour removed among overrun n | Own component pixels lost on y |',
        '|---|---:|---:|---:|---:|---:|']
    for source in SOURCES:
        d=grid[source];v=[x for x in review if x['source']==source]
        lines.append(f"| {source} | {d['crop_n']}/{d['crop_y']} | {d['before_median_xh']:.3f} → {d['after_median_xh']:.3f} | {d['changed']}/40 ({100*d['changed']/40:.1f}%) | {sum(x['readable_neighbour_removed'] is True for x in v)}/{sum(x['original_overrun'] for x in v)} | 0/{d['crop_y_own_pixels']:,} |")
    lines += ['',
        'Unblinded inspection covered all 160 pairs in [32 contact sheets](dev/review/) and three native 3× change witnesses. Gazette c015 and c038 lose the readable neighbouring fragments; 55/57 overrun cards retain their original overrun. Lekythos c037 is the remaining crop-ok n: its right-edge clipping after Ἐ persists because X is immutable. No newly cut own body/accent/descender was seen on the 102 original crop-ok y cards, including the 29 changed y cards. These observations do not replace a fresh blind check.', '',
        'The separate detector-defined body-band metric finds neighbour body pixels in 52/58 n crops and complete body removal in **0/52**; body pixels remain 36,080 → 36,080. Readable partial glyphs outside the body band explain why the two visual improvements are not counted by that narrower measure. Visual readable-neighbour removal is 2/57 overrun cards (3.51%), or 2/58 all n cards (3.45%). Assigned foreign-component pixels on n cards fall 52,515 → 52,084. The cached component assignment is a measurement witness, not independent glyph truth.', '',
        f"The own-component guard refuses {grid['overall']['own_guard_refusals']}/160 proposals; the raw proposals would lose {grid['overall']['proposal_own_pixels_lost']:,} assigned own pixels. Accepted loss is 0/510,558 pixels on y cards and zero on all 5,770 F2 lines, by construction. This is why zero accepted loss is not claimed as proof of guide correctness. [Full grid](dev/grid.json), [dev row records](dev/records.jsonl), [unblinded observations](dev/visual_review.jsonl).", '',
        'The result is a conservative negative efficacy finding under the requested token-edge constraint. Within the tested margin grid, many token boundaries conflict with the own-line band or would discard owned pixels. The cutter abstains in those cases.', '',
        '## Frozen parameters', '',
        'All nine top/bottom combinations from {0.1, 0.2, 0.3} xh were evaluated on the 160 v2 development cards only. Selection maximises n-card complete neighbour body removal, then minimises residual neighbour body pixels, then prefers the larger total/top margin. All combinations tie on neighbour body removal; the conservative 0.3/0.3 tie-break wins. No harm-test predictions were used to choose or revise parameters.', '',
        '```json',json.dumps(frozen['params'],indent=2),'```', '',
        f"Parameter SHA256: `{frozen['params_sha256']}`. Frozen at `{frozen['frozen_utc']}`, before inference began at `{binding['started_utc']}`. [Freeze receipt](params.json).", '',
        'For each uniquely owned F2 row, use the receipt-verified saved six-guide font band: top=min(font_top, accent_top), bottom=font_bottom, evaluated on the crop X overlap, with 0.3 xh margins. Clip against the closest overlapping-X foreign Google token edges above/below the own body centre; same-row centres within 0.5 xh do not clip. Font guides round outward, token edges inward. Intersect with the original rectangle. Conflicting geometry or any lost supplied own-component pixel returns the original. Horizontal bounds and native sampling remain literal.', '',
        'The general `tighten_page` callable accepts arbitrary native Google line/token geometry, plus optional existing bands/ownership. Without supplied bands it calls existing `fit_box(splits=False)` on a stable `guide_box`. Source IDs and F2 paths are unnecessary. Supply immutable guides/guide boxes on repeated calls for idempotence. Without supplied component coordinates, the pixel guard is unavailable: generic output still requires the same owner qualification gate. F2 always supplies its cached assigned-component evidence.', '',
        'The old four-guide fit and the current six-guide page font runtime were inspected; F2 uses its saved detector identity, recorded per page in [provenance](f2/provenance.jsonl), not a claim to have rerun 046bd52. `fix_page`, `separate_lines`, and the expansion path are not invoked. `_voronoi_keep` was considered, but final loss measurement uses the stronger pre-existing assigned-component cache instead.', '',
        '## Qualification card sets — T6b only', '',
        'Not generated or qualified here. W1 status, `collector.exit`, locks and PID files were not accessed. Each source receipt records null card/key paths and the unchanged original `LABEL_CHECK_v2.md` hash for the later run. No 100-card sets are represented as ready. IA remains included in the T6b handoff; the saved 2f34ed52 IA verdict is 37/40 crop-ok y, whereas the brief separately cites 35/40. T6a does not resolve that discrepancy by editing verdicts.', '',
        '## Paired CPU harm test', '',
        f"E4 wave1a `ctrl_s0`: full checkpoint SHA256 `{binding['model_sha256']}`; safetensors SHA256 `{binding['weights_sha256']}`. The full-checkpoint hash matches the existing local Clariden comparison receipt; safe CPU loading verified every safetensors model tensor equal to that checkpoint. Clariden was not contacted. Codec SHA256 `{binding['codec_sha256']}`.", '',
        'All 5,770 distinct eligible F2 crops on 87 pages were included: Gazette 525, Lekythos 4,023, Kosmopolis 562, IA 660. This is below the 10k input-crop cap; evaluating both versions gives 11,540 paired-arm observations. The raw Google labels are the post-fix `label_after_conventions`, encoded to the model codec in NFD once. CER is strict NFD codepoint edit distance, weighted by reference character count. These are silver-reference harm results, not human transcription accuracy.', '',
        'The unchanged `train/eval_cer.py:evaluate` core is used with `load_checkpoint`, the existing `bench/o4b_models.py:strip` 48-pixel crop adapter, and `data.collate_strips` own-background halo; CPU float32, four threads, batch size 16, sorted by width. The factory `evaluate_run` custody wrapper itself requires the CUDA training runtime and cannot certify this CPU readout. The explicit adapter boundary and hashes are recorded in [harm binding](harm/binding.json). Both arms use the same preprocessing and scorer. No unchanged prediction may differ: this is checked exactly.', '',
        'Difference is recut − original CER, in percentage points below. CIs use 5,000 paired line resamples per cell; [machine-readable results](harm/summary.json) also contain 5,000 whole-page cluster bootstrap intervals, preserving within-page dependence. A zero point difference is allowed by the stated non-worsening rule; an interval crossing zero does not prove non-inferiority.', '',
        '| Source | Subset | N | Orig CER % | Recut CER % | Δ pp [paired 95% CI] |',
        '|---|---|---:|---:|---:|---:|']
    for source in (*SOURCES,'overall'):
        for subset,s in stats[source].items():
            if not s['lines']:
                lines.append(f'| {source} | {subset} | 0 | — | — | not estimable |');continue
            ci=s['paired_bootstrap_95ci']
            lines.append(f"| {source} | {subset} | {s['lines']:,} | {100*s['original_cer']:.4f} | {100*s['recut_cer']:.4f} | {100*s['difference']:+.4f} [{100*ci[0]:+.4f}, {100*ci[1]:+.4f}] |")
    allstats=stats['overall']['all'];changed=stats['overall']['changed']
    lines += ['',f"Overall non-worsening point-estimate rule: **{'PASS' if allstats['difference']<=0 else 'FAIL'}**. {allstats['improved_lines']} lines improve, {allstats['worsened_lines']} worsen, {allstats['equal_lines']} have equal edits. The {stats['overall']['unchanged']['lines']:,} unchanged crops have exactly identical predictions. Per-source outcomes remain visible regardless of the overall result. No post-readout parameter changes were made.", '',
        f"The overall paired 95% interval is {100*allstats['paired_bootstrap_95ci'][0]:+.4f} to {100*allstats['paired_bootstrap_95ci'][1]:+.4f} pp; the whole-page interval is {100*allstats['page_bootstrap_95ci'][0]:+.4f} to {100*allstats['page_bootstrap_95ci'][1]:+.4f} pp. Both cross zero. Kosmopolis worsens from {100*stats['kosmopolis_poly1900']['all']['original_cer']:.4f}% to {100*stats['kosmopolis_poly1900']['all']['recut_cer']:.4f}%, with changed-line CER {100*stats['kosmopolis_poly1900']['changed']['original_cer']:.4f}% to {100*stats['kosmopolis_poly1900']['changed']['recut_cer']:.4f}%. Its source-specific harm is not hidden by the overall gain. Lekythos and IA development y subsets also worsen despite zero measured component loss: preserving assigned ink does not guarantee identical recognition after height normalisation.", '',
        'The geometry-clean subset means exactly F2 `geometry_positive is False` (G1b-negative) and no `screen_reject` flag (the v2 key names this `screen_merged`). All eligible lines already have G1b-negative status; the screen flag supplies the additional split. It is an audit-defined subset, not a physical-correctness guarantee. Development-card n/y cells are repeated-development diagnostics, not held-out evidence.', '',
        '## Artifacts, validation and handoff', '',
        f"The native validation checks {integrity['native_crops_checked']:,} literal pixel subarrays, source hashes, raw-response/cache hashes, X invariance, no expansion, and unchanged PNG identity. [Validation receipt](validation.json). Cutter tests: 10 passed (26 total including 16 existing structure regressions), covering inclusion, neighbour clipping/rounding, conflicts, idempotence, owned accent/descender refusal, exact native pixels, arbitrary-page use without cache, accent guides, missing/invalid fits and canonical hashes. [Tests log](tests.log).", '',
        'Recut PNGs remain in `f2/<source>/recut/` beside references to immutable original page/crop geometry; every row records old/new/proposed boxes, parameter hash and PNG hash. They are experimental outputs and not collection admission. Bulk PNGs and review sheets are git-ignored, present locally, and bound by the tracked records. Per-source receipts:']
    lines += ['']+[f'- [{s}]({s}/receipt.json)' for s in SOURCES]
    lines += ['',f"Reuse count convention: {counts['reused_direct_repository_functions']} directly called existing repository functions; {counts['added_all_named_functions_and_methods']} added named functions/methods in total, of which {counts['added_library_functions_and_methods']} are in the cutter library; the rest are experimental binding/evaluation/reporting/commit helpers and tests. The last line uses the total addition count. [Inventory](REUSE.md), [counts](function_counts.json), [runtime](runtime.json).", '',
        'The guarded commit attempt was blocked: Git could not create the worktree `index.lock` under the read-only main checkout (`Operation not permitted`). **No worker commit was created.** No retry or alternate index was used. The source-bound helper remains ready; `--prepare` and `--check-only` validate exact HEAD, branch, file hashes, an empty staging area and exclusion of git-ignored payloads. The local `handoff.patch.gz` packages the reviewed source files and manifest; its application/hash validation is recorded in `HANDOFF.json`. The original failure is recorded in `COMMIT_STATUS.json`.', '',
        f"T6a: done | reused: {counts['reused_direct_repository_functions']} functions added: {counts['added_all_named_functions_and_methods']} | dev neighbour-ink removed: {100*2/58:.2f}% own-ink loss: 0.00% | harm CER orig/recut overall: {100*allstats['original_cer']:.4f}%/{100*allstats['recut_cer']:.4f}% changed-lines: {100*changed['original_cer']:.4f}%/{100*changed['recut_cer']:.4f}% | params: {frozen['params_sha256'][:12]} | model: {binding['model_sha256'][:12]}"]
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(lines[-1])


if __name__=='__main__':main()
