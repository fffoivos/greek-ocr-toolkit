"""Render the completed fixed experiment; never selects settings or predictions."""
from pathlib import Path
import sys,json,hashlib,platform
from datetime import datetime,timezone
from importlib.metadata import version
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sys.path.insert(0,str(OUT));import run as current
prior=current.prior


def f(v):
    return 'n/a' if v is None else f'{v:.6f}'


def ci(v):
    return 'n/a' if v is None else f'[{v[0]:.6f}, {v[1]:.6f}]'


def table_stats(results,subset):
    lines=['| Source | Lines | Original CER | Masked CER | Difference | Paired line 95% CI | Paired page 95% CI |',
           '|---|---:|---:|---:|---:|---|---|']
    for source in (*prior.SOURCES,'overall'):
        r=results[source][subset]
        lines.append(f"| {source} | {r['lines']} | {f(r['original_cer'])} | {f(r['masked_cer'])} | {f(r['difference'])} | {ci(r['paired_bootstrap_95ci'])} | {ci(r['page_bootstrap_95ci'])} |")
    return '\n'.join(lines)


def main():
    frozen=prior.read_json(OUT/'params.json');harm=prior.read_json(OUT/'harm/summary.json');results=harm['results']
    dev=prior.read_json(OUT/'dev/summary.json');visual=prior.read_json(OUT/'dev/visual_summary.json');components=prior.read_json(OUT/'dev/component_summary.json')
    binding=prior.read_json(OUT/'harm/binding.json');validation=prior.read_json(OUT/'validation.json')
    commit_status=prior.read_json(OUT/'COMMIT_STATUS.json') if (OUT/'COMMIT_STATUS.json').exists() else None
    commit_text=("The guarded commit attempt was blocked: Git could not create the managed worktree index.lock (Operation not permitted). **No worker commit was created.** No retry or alternate index was used. The exact source-bound manifest and validated local handoff.patch.gz are the coordinator fallback; HANDOFF.json records applying it in a fresh temporary directory and verifying every file hash. See COMMIT_STATUS.json for the actual failure."
                 if commit_status and commit_status['status']=='commit_blocked' else
                 "Commit custody is recorded by the source-bound guarded_commit.py helper and its COMMIT_STATUS.json. An index permission failure is terminal: no staging retry or alternate index. If blocked, the exact manifest and validated handoff.patch.gz provide the coordinator handoff; HANDOFF.json records application in a fresh temporary directory and every file hash.")
    all_summary=prior.read_json(OUT/'f2/summary.json');step0=prior.read_json(OUT/'step0/agreement.json')
    records=prior.rows(OUT/'f2/records.jsonl');own=dev['overall'];vis=visual['results']['overall']
    loss=100*own['own_y_lost']/own['own_y_pixels'];removed=vis['readable_neighbour_fragment_removed_percent']
    a=results['overall']['all'];c=results['overall']['changed']
    signature=f"T6a2: done | inference-applicable: yes | dev neighbour-ink removed: {removed:.2f}% own-ink loss: {loss:.4f}% | harm CER orig/masked overall: {f(a['original_cer'])}/{f(a['masked_cer'])} changed: {f(c['original_cer'])}/{f(c['masked_cer'])} | params: {frozen['params_sha256'][:12]}"
    lines=['# T6a2: native foreign-ink masking — completed negative safety qualification','',
        '**Inference-applicable: yes. Own-ink safety gate: FAIL. Nothing admitted or enabled by default.** '+
        ('The overall CER non-worsening gate passes.' if harm['overall_nonworsening_pass'] else 'The overall CER non-worsening gate also FAILS.'),
        '',f"The fixed existing ownership rule removes substantial readable neighbour fragments on {vis['readable_neighbour_fragment_removed_cards']}/{vis['overrun_cards']} overrun cards ({removed:.2f}%), but erases {own['own_y_lost']:,}/{own['own_y_pixels']:,} cached own pixels on crop-ok-y cards ({loss:.4f}%). Native inspection confirms real target damage, including a gamma descender, an E serif and an f serif. Strong foreign-pixel removal is not zero own-ink loss or complete background cleanup.",
        '',"T6a at `6ed722f8` remains its recorded negative, unshipped result. Its code, parameters and evidence are unchanged. This work starts at brief HEAD `9ac8b3572ec2ed0c6cbafcb4f0b1eb6da5041453` on `sol/recut-v1`. Network OFF. F2 only; W1 and admission state were not accessed or changed.",
        '', '## Step 0: identical inference application', '',
        "The current page detector is `greekocr/pages/lines.py:segment_page`, used by `pages.api.process_page`. The actual deployment crop consumer is `greekocr/deploy/docling_plugin/model.py:GlossapiOcrModel._detect`, in its for-piece loop immediately before `extract_line_image(image, piece.line)`. `tables.line_piece` supplies the unchanged original native rectangle. The older `glyphs.lines_api.separate_lines` straightens crop-local fits; `glyphs.page_lines.page_lines` requires supplied boxes and is not the present deployment crop consumer.",
        '',"The opt-in call at that boundary is `mask_detected_line(mask_page, piece.line, runtime_neighbours, piece.box)`, where `mask_page=prepare_mask_page(image)` and `runtime_neighbours` is the non-discounted subset of `analysis.segmentation.lines`. The result is pasted into a private native-page copy before the unchanged extraction call. Centre=(baseline+meanline)/2; the runtime's detected guides supply every own and neighbouring curve. No Google geometry or cached component truth is required. Training proposals use exactly the same function and detector neighbour set inside the saved original training rectangle. Deployment defaults are unchanged; the exact insertion recipe is in [REUSE.md](REUSE.md).",
        '',"The gate was written and tested before the public library was added. Four fresh F2 runtime pages were used, one per source. Exact equivalent-input masks matched **187/187 training rectangles and 187/187 detector rectangles**. The later public-function check also matches all filled raster bytes and records, and executes the unchanged `extract_line_image` after each insertion: **187/187 actual extraction results identical**. [Initial gate](step0/agreement.json), [public-function identity](step0/public_function_identity.json).",
        '', '| Source | F2 target lines matched | Runtime / Google complete masks equal | Ink-pixel agreement | Masked-set IoU |',
        '|---|---:|---:|---:|---:|']
    for p in step0['pages']:
        r=p['counts'];lines.append(f"| {p['source']} | {r['matched']}/{r['lines']} | {r['google_equal']}/{r['matched']} | {100*r['ink_agreement']:.4f}% | {100*r['masked_iou']:.4f}% |")
    lines += ['',"Aggregate runtime-vs-Google comparison: 165/187 exact complete masks, 99.9428% agreement on 1,128,287 ink pixels (645 disagreements), masked-set IoU 102,825/103,470 = 99.3766%. Google-box-derived curves use the existing `fit_box(..., splits=False)` and are a diagnostic comparison only. They are not training-mask inputs. Equivalent-input equality is distinct from detector/Google agreement and from physical glyph ownership.",
        '',"Existing `pages`/`glyphs` runtime files match `046bd52`; additions are the pre-existing T6a `vertical_recut.py` and this opt-in `foreign_ink.py`. Neither is enabled in deployment. Fresh full-precision runtime curve observations for all 87 F2 pages are bound to source rasters and code in [runtime_manifest.json](runtime_manifest.json). The fixed training-target binding and its driver hashes are frozen in [binding_freeze.json](binding_freeze.json). Eleven unmatched target rectangles remain literal originals (10 Lekythos, 1 IA); no curve or row is invented.",
        '', '## Reused ownership and local fill', '',
        "[foreign_ink.py](../../../../greekocr/glyphs/foreign_ink.py) is opt-in. It directly calls unchanged `recut._voronoi_keep`, reuses `_neighbour` and `LineFit.base_at`, and adapts the existing straightened working grid by reversible integer column translations. Output pixels are never resampled: only the foreign foreground mask inside the original rectangle is filled. No output box expands, shifts or changes dimensions; no line is split, joined or added. The same page observation preparation is used by raw-page and prepared-page calls.",
        '',"For each selected native component, fill is the per-channel median of its native-page Chebyshev ring between one and three pixels from the component, excluding all binarised foreground. Ring spread is p90 minus p10. Empty rings abstain; there is no constant-white fallback. A measured median of 255 on saturated Gazette paper is a local statistic, not a hard-coded fill. Crop-level median/spread are unweighted medians across component statistics; every per-component ring size, median, spread and fill is retained in the row record.",
        '',"`_voronoi_keep` exposes **no ownership tolerance parameters**. No tuning grid, new semantic attachment rule or label-derived protection guard was introduced. Its unchanged nearest-centroid rule has a high detached-mark counterexample; its body-band touching test can also cut an own descender or serif. The wrapper is not claimed to cure those limitations.",
        '', '## F2 development: all 160 pinned v2 cards', '',
        "The same v2 keys, cards, verdict bytes and features were reverified against the existing T6a binding and pinned revision `2f34ed52`. There are 58 crop-ok-n and 102 crop-ok-y cards; 57 n cards have `crop_overrun`, while Lekythos c037 is a horizontal clip. The visual metric below means **at least one previously readable neighbour fragment substantially removed**, including partial improvements. It does **not** mean all neighbouring ink is gone.",
        '', '| Source | n / y | Changed y inspected | Visual fragment removal / overruns | Cached foreign pixels, n before → after | Cached own pixels lost / total, y | Own component appearances touched |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for source in (*prior.SOURCES,'overall'):
        r=dev[source];v=visual['results'][source];co=components[source]
        lines.append(f"| {source} | {r['crop_n']} / {r['crop_y']} | {r['changed_y']} | {v['readable_neighbour_fragment_removed_cards']}/{v['overrun_cards']} | {r['n_foreign_before']:,} → {r['n_foreign_after']:,} | {r['own_y_lost']:,}/{r['own_y_pixels']:,} | {co['own_y_components_touched']}/{co['own_y_components']} |")
    lines += ['',"All 160 paired cards and **every one of the 94 changed y cards** were inspected in 32 contact sheets. All 14 cached own-component loss witnesses and five larger native contexts were also inspected. This is an unblinded agent inspection, not a new owner blind verdict. [Visual observations](dev/visual_review.jsonl), [summary](dev/visual_summary.json), [hashed review artifacts](dev/review_artifacts.json).",
        '',"Decisive native y witnesses: IA c023 cuts the initial gamma's lower descender (94 cached pixels in that component); IA c040 removes the capital E's upper-left serif (91); IA c019 shortens the target Latin f's upper serif (12). Other small removed dots or boundary fragments have unresolved semantic attachment. IA c001's larger context confirms its own iota subscript remains. Therefore 387 is the independent **cached ownership pixel** loss, not a claim that every removed dot is semantically own text. The confirmed target damage alone falsifies zero loss. Capturing the original _voronoi_keep arguments for the three confirmed failures shows each component nearer its own centre but also touching a neighbour body band: its unchanged midline-cut branch removes the target extremity. The frozen masks reproduce exactly in this trace ([mechanisms](dev/confirmed_loss_mechanisms.json)). [Component audit](dev/component_audit.jsonl), [native loss list](dev/loss_witnesses.jsonl).",
        '',"Visual counterexamples to the foreign-pixel metric: Gazette c015 still contains the readable E.S.Y.E. neighbour while its cached foreign count was zero before masking. Gazette c005 loses upper neighbour fragments but retains a readable lower fragment. Lekythos and Kosmopolis cards can retain faint outlines/antialias halos around removed foreground. Lekythos c024 also cuts its own drop-cap H, which the cached own-pixel metric does not cover. No complete cleanup or universally correct ownership is claimed.",
        '',f"Across all 58 n cards, cached foreign pixels fall 52,515 → 263 ({100*(1-263/52515):.4f}% removed); cached neighbouring body pixels fall 36,080 → 9. Of 2,460 cached foreign component appearances in n crops, 2,435 are fully removed from the crop and 2,443 are touched. These are detector-label measurements, not independent text truth. On y cards, 14/4,268 own component appearances lose pixels across 11/102 cards; all y cards have a measurable cached owner. [Development metrics](dev/summary.json), [component metrics](dev/component_summary.json).",
        '', '## Fill statistics and frozen identity', '',
        '| Source | Dev masked pixels / component applications | Dev median ring value / spread | F2 masked pixels / component applications | F2 median ring value / spread |',
        '|---|---:|---:|---:|---:|']
    for source in (*prior.SOURCES,'overall'):
        d=dev[source];r=all_summary[source]
        lines.append(f"| {source} | {d['masked_pixels']:,} / {d['masked_components']:,} | {d['ring_median_median']:.2f} / {d['ring_spread_median']:.2f} | {r['masked_pixels']:,} / {r['masked_components']:,} | {r['ring_median_median']:.2f} / {r['ring_spread_median']:.2f} |")
    lines += ['',"Counts sum component applications per crop, rather than claiming distinct physical components across the page population. There are zero empty-ring abstentions. Full-corpus selected fill pixels total 2,173,625; 2,173,617 native pixels actually change. Eight selected pixels in two non-dev crops already equal their component ring median. Those two masks were reexecuted and hash-verified; the other masks were reconstructed from native differences. No crops or settings were changed in response to this verification distinction.",
        '',f"Parameters were frozen at `{frozen['frozen_utc']}`, before harm inference at `{binding['started_utc']}`. Canonical parameter SHA256: `{frozen['params_sha256']}`. Library SHA256: `{frozen['source_hashes']['greekocr/glyphs/foreign_ink.py']}`. The freeze already records the failed empirical own-ink safety gate. Neither settings nor crops were revised after seeing predictions. [params.json](params.json), [validation](validation.json).",
        '', '## Paired E4 ctrl_s0 harm test', '',
        f"Same 5,770 F2 lines; 11,540 paired arm observations; Mac CPU, four threads, batch 16, seed 20261017. Checkpoint SHA256 `{binding['model_sha256']}`; local safetensors were verified tensor-for-tensor against the SHA-verified best.pt. The unchanged `train/eval_cer.py:evaluate`, `bench/o4b_models.py:strip` and `data.collate_strips` implement strict NFD codepoint corpus CER against the same fixed Google labels in both arms. The CUDA-runtime custody wrapper `evaluate_run` is not used; this is its unchanged evaluator core with the documented CPU adapter. [Binding](harm/binding.json), [original receipt](harm/original.receipt.json), [masked receipt](harm/masked.receipt.json).",
        '',"CER values below are fractions. Difference is masked minus original; a negative value favours masking. CIs use 5,000 seeded paired bootstrap replicates, with both line resampling and page-cluster resampling. The original and masked corpus numerator/denominator are retained in the JSON. These CIs describe this F2 population, not W1 or production qualification.",
        '', '### Overall and per source', '',
        'The fresh original readout exactly reproduces all 5,770 recorded T6a original predictions, references, edit counts and source assignments; the entire prediction-file SHA256 is identical. [Reproduction receipt](harm/original_reproduction.json).', '',table_stats(results,'all'),
        '', '### Changed crops', '',table_stats(results,'changed'),
        '', '### Unchanged crops', '',table_stats(results,'unchanged'),
        '',f"All **{harm['unchanged_lines']} unchanged crops have exactly identical prediction strings and edit counts** in both arms, checked by ID. Crop dimensions keep both arms in the same width ordering. The remaining 5,399 crops changed. [Paired rows](harm/paired.jsonl).",
        '', '### Crop-ok-n development subset', '',table_stats(results,'crop_ok_n'),
        '', '### Crop-ok-y development subset', '',table_stats(results,'crop_ok_y'),
        '', '### Geometry-clean subset', '',table_stats(results,'geometry_clean'),
        '',"The geometry-clean subset is exactly the T6a detector-defined filter: `geometry_positive is False` and no screen rejection, within the fixed usable/text-exclusion-free F2 pool. It is not an independently certified zero-geometry-error population.",
        '', '## Contracts, outputs and disposition', '',
        "The 21 contract/characterization tests pass (11 new cases, including parameterized rectangle checks, plus 10 unchanged T6a tests). They cover ordinary own accents/breathings, connected descenders, apostrophe/coronis, iota subscripts, end punctuation, two-body touching, colour/ring statistics, native pixel preservation, exact adapters, invalid boxes, and an explicit detached-own-mark safety counterexample. A passing characterization test demonstrates that counterexample; it is not a passing universal safety property. [Tests](tests/test_foreign_ink.py), [test log](tests.log).",
        '',"Native output/hash/label/rectangle verification covers all 5,770 pairs. Original crops are under `f2/<source>/original/`; masked proposals are beside them under `f2/<source>/masked/`. Original source pages and the F2 input trees are unchanged. Raster witnesses and full-precision runtime curve payloads are local ignored artifacts, bound by the tracked receipts. Per-source receipts are [Gazette](gazette_modern/receipt.json), [Lekythos](lekythos_poly1900/receipt.json), [Kosmopolis](kosmopolis_poly1900/receipt.json), [IA](ia_greek_latin/receipt.json).",
        '',"**Disposition: reject as a safety-qualified crop replacement.** Inference applicability passes; empirical own-ink zero-loss fails, independently confirmed by native target glyph damage. "+
        ('Overall CER non-worsening passes, which does not overrule the own-ink gate.' if harm['overall_nonworsening_pass'] else 'Overall CER non-worsening also fails.')+
        " No defaults changed, no rows admitted, and no production path enabled.",
        '',commit_text,
        '',signature]
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    (OUT/'FINAL_LINE.txt').write_text(signature+'\n')
    runtime=dict(python=sys.version,platform=platform.platform(),packages={p:version(p) for p in ('numpy','Pillow','scipy','torch','safetensors')},
        task_start_upper_bound_utc='2026-10-16T22:50:00+00:00',completed_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_upper_bound_seconds=(datetime.now(timezone.utc)-datetime(2026,10,16,22,50,tzinfo=timezone.utc)).total_seconds(),
        network='OFF; process socket connections forbidden; no web, provider, SSH, or download calls',w1_accessed=False,
        params_sha256=frozen['params_sha256'],source_hashes=current.source_hashes(),
        script_hashes={p.name:prior.file_sha256(p) for p in OUT.glob('*.py')},
        note='Conservative wall-time bound starts before this task first tool call; pipeline timings separately recorded.')
    runtime['within_120_minutes']=runtime['elapsed_upper_bound_seconds']<=7200
    prior.write_json(OUT/'runtime.json',runtime)
    print(signature)

if __name__=='__main__':main()
