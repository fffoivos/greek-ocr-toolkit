"""Write the diagnostic hand-off from measured results and physical review."""
from pathlib import Path
import json
from collections import Counter
from run_diag import install_guard, BASE, ROOT, PILOT, MASKING, sha, write


def main():
    install_guard()
    pages=json.loads((BASE/'pages.json').read_text())
    f2=json.loads((BASE/'f2_check.json').read_text())
    reviews=json.loads((BASE/'classifications.json').read_text())
    sheets=json.loads((BASE/'sheets_manifest.json').read_text())
    execution=json.loads((BASE/'execution.json').read_text())
    def triplet(c):
        return f"{c['matched']} / {c['ambiguous']} / {c['unmatched']}"
    text=[
        '# T6c1b: line–curve matching diagnostic', '',
        '**The requested ≥50% crop-width horizontal overlap test already exists in T6a2.** '
        'Enabling it as an additional opt-in restriction produces no change: parliament remains '
        '**39 matched / 36 ambiguous / 12 unmatched**; the first vouli sample page gives '
        '**33 / 0 / 1**. The two-column layout is real, but the original matcher already rejects '
        'the disjoint opposite-column curves. The contact sheets show same-column neighbouring rows '
        'and malformed detector curves among the eligible alternatives.', '',
        '## Before → after', '',
        'Matched means exactly one eligible curve; ambiguous means more than one; unmatched means none. '
        'T6a2 itself returns the minimum-distance winner even in ambiguous cases. These exclusive '
        'diagnostic counts use the pilot’s conservative ambiguity definition.', '',
        '| Wave / page | Native raster | Lines / detector curves | Before M / A / U | After M / A / U | Winner / candidate-set differences |',
        '|---|---|---:|---|---|---:|'
    ]
    for p in pages:
        w,h=p['size']
        text.append(f"| {p['wave']} `{p['page_id']}` | {w}×{h}, {w*h/1e6:.3f} MP | {p['lines']} / {p['curves']} | {triplet(p['before'])} | {triplet(p['after'])} | {p['matching_index_differences']} / {p['candidate_set_differences']} |")
    text += [
        '', 'Vouli is the **first `wave == "vouli"` entry in the existing `sample.json`**, '
        '`0d2e3015ff99-p000009`. Parliament reuses the saved 89 full-precision curves; '
        'all 87 saved winners, complete candidate lists (including floating-point scores), and statuses '
        'reproduce exactly. Its 40 MP raster is used for the physical witnesses. Vouli alone was run '
        f"through the unchanged detector here ({pages[1]['detector_seconds']:.3f} s); the resulting 38 curves are archived locally. "
        'No masking, re-cutting, admission or collection processing is performed.', '',
        '## Restriction and unchanged scoring', '',
        'The existing source is [`masking/probe.py`, `match`](../../masking/probe.py), lines 60–70: '
        '`overlap = max(0, min(crop_x1, curve_x1) - max(crop_x0, curve_x0)) / crop_width`, '
        'followed by `if overlap < .5: continue`. T6c1’s extracted matcher and its candidate diagnostics '
        'both already apply this condition. Therefore the premise that the current matcher is vertical-only '
        'is not supported by this checkout or the saved pilot records.', '',
        '[`matcher.py`](matcher.py) adds `match(box, fits, *, min_horizontal_overlap=None)`. '
        'The default delegates directly to the exact original function, loaded without executing the '
        'probe’s unrelated entrypoint. Opting in with `min_horizontal_overlap=0.5` filters only by '
        '**intersection width ≥50% of crop width**, retaining original curve order and remapping the '
        'winner to its original detector index. The original matcher then executes unchanged. '
        'Its vertical gate remains **distance ≤1.5 x-height**, where distance is '
        '`abs(median(body_centre_at_all_crop_x) - crop_y_centre) / max(1, xheight)`. '
        'Sampling, extrapolation, distance score and index tie-break are unchanged. There is no added '
        'score, vertical threshold change, or threshold search. The diagnostic candidate list executes '
        'the original eligibility/scoring statements and replaces only its final reduction with '
        '`sorted(candidates)`.', '',
        'The opt-in 50% gate is deliberately reported as **redundant**, not as a repair. A greater '
        'horizontal threshold is an explicit API option but was not selected or applied to these results. '
        'The default matcher and all production/T6a2 files remain byte-for-byte unchanged.', '',
        '## Contact sheets and native evidence', '',
        '[Browse the evidence index](index.html). Each failure card has the exact `crop_bbox`, '
        'before/after failure kind, **every eligible curve** with its full x extent and score, an '
        'unaltered full-page-width raster strip, the same strip with curve meanline/baseline/centre '
        'and endpoints, and the unaltered target crop. Red is the crop; candidate colours follow ranked '
        'order; grey curves are nearby rejected output; purple highlights rejected evidence for the '
        'merge and partial-extent cases. The full page width preserves both columns. Curves can leave '
        'the vertical strip; the printed x intervals still give their complete horizontal extent. '
        'Each unmatched line also has a lossless, native-size PNG with raw context above the overlay. '
        'All 48 parliament failure cards and the vouli failure card were visually reviewed.', '',
        '| Sheet | Failure cards | Line IDs (page prefix omitted) |', '|---|---:|---|'
    ]
    for s in sheets:
        if s['kind']!='contact_sheet':
            continue
        text.append(f"| [{Path(s['path']).name}]({s['path']}) | {len(s['ids'])} | {', '.join(i.rsplit('-',1)[-1] for i in s['ids'])} |")
    text += [
        '', '[Parliament full raster overview](sheets/parliament--37e22f57-p000005--page.jpg); '
        '[vouli overview](sheets/vouli--0d2e3015ff99-p000009--page.jpg). '
        '[`sheets_manifest.json`](sheets_manifest.json) binds each sheet/witness to its IDs and SHA-256.', '',
        '## Unmatched classification', '',
        '**Parliament: merge 1, miss 11, crop 0, other 0 (12 total).** '
        '**Vouli: merge 0, miss 0, crop 0, other 1 (1 total).** '
        'The final hand-off line aggregates both pages: **13 distinct unmatched lines**. '
        'The original and post-restriction sets are identical, so no line is counted twice.', '',
        'These are physical classifications against the native rasters and the retained detector '
        'curves. “Miss” means that the retained output has no curve following the target’s printed '
        'body; it does not identify which internal detector stage discarded or failed to produce it. '
        '“Merge” means one retained curve traces ink from different printed rows. The vouli partial '
        'extent is “other” because an accurate curve is present over part of the row. All 13 boxes '
        'are on their intended printed row; no off-line crop_bbox problem was found.', '',
        '| Line / native witness | Crop bbox | Cause | Physical evidence |', '|---|---|---|---|'
    ]
    all_records={r['id']:r for p in pages for r in json.loads((BASE/(p['wave']+'--'+p['page_id']+'.matches.json')).read_text())}
    for r in reviews:
        text.append(f"| [{r['id']}](witnesses/{r['id']}.png) | `{all_records[r['id']]['crop_bbox']}` | {r['cause']} | {r['sheet_note']} |")
    text += [
        '', 'For the **merge**, c80 has x extent `[2356,5204)`. At x=2600 its meanline/baseline '
        'are y=6336.7/6426.7, over an earlier printed row; at x=4000 they are '
        'y=6529.4/6619.3, over l0116. Its median-centre distance for l0116 is 1.6506 x-height, '
        'so it fails the unchanged 1.5 gate despite 99.658% horizontal overlap. c82 and c83 also '
        'make large row jumps nearby; they are shown as context, not additional unmatched-line counts. '
        'This is a merge across printed rows within the right column, not evidence of a curve joining '
        'the two columns.', '',
        'For **vouli l0033**, the crop is `[349,2244,1809,2318]`; c30 is `[1169,1806)` in x. '
        'Its overlap is `637/1460 = 43.6301%`, and its vertical distance is only 0.043944 x-height. '
        'The native witness shows the crop contains the complete printed row while c30 covers only '
        'the right-hand words. The original horizontal gate already rejects this partial curve. '
        'Adding the same gate cannot restore its missing left-hand extent.', '',
        '## T6a2 unchanged check', '',
        '**Yes: identical matches with the restriction enabled.** We replayed matching against '
        'the existing full-precision, raster-bound T6a2 runtime caches. Every cache’s source hashes '
        'match the frozen T6a2 source manifest and the current source files. Cached curves were read '
        'only, not regenerated. Both saved-index reproduction and the opt-in comparison are exact, '
        'including null/unmatched values, ambiguous winners and complete ranked candidate lists.', '',
        '| Scope | Pages / lines | Before M / A / U | After M / A / U | Saved-index differences | Opt-in winner / candidate-set differences |',
        '|---|---:|---|---|---:|---:|'
    ]
    for key,label in [('dev_cards','160 F2 dev cards'),('all_lines_on_dev_pages','Every F2 line on a dev page'),('all_f2','All F2 (additional check)')]:
        r=f2['subsets'][key]
        text.append(f"| {label} | {r['pages']} / {r['lines']} | {triplet(r['before'])} | {triplet(r['after'])} | {r['saved_index_differences']} | {r['index_differences']} / {r['candidate_set_differences']} |")
    text += [
        '', 'The dev cards therefore retain 159 non-null winners and one unmatched; all lines on '
        'dev pages retain 4,569 non-null winners and 11 unmatched. Ambiguity is an observation added '
        'by the pilot, not a change to T6a2’s saved winner semantics. '
        '[`f2_check.json`](f2_check.json) contains all 5,770 per-line comparisons and all 87 cache hashes.', '',
        '## Execution, validation and commit', '',
        f"Executed locally with **actual nice {execution['nice']}**, one process/worker and one numerical thread; "
        'no sub-agents or network calls. An audit hook denies network operations and all writes outside '
        '`docs/harvest/recut_v1/v2_pilot/diag/`. Pilot files, page rasters and T6a2 caches are read-only. '
        f"Main diagnostic peak RSS was {execution['peak_rss_bytes']/2**20:.1f} MiB. "
        'This is a matching diagnostic, not a new 40 MP detector timing or speed qualification.', '',
        'Eight focused matcher/containment tests pass: actual legacy 50% eligibility, inclusive '
        'horizontal/vertical boundaries, unchanged ranking and global indices after filtering, '
        'tie order, default parity, inability to weaken the original gate, invalid thresholds, '
        'and denied external writes/network. See [`tests.log`](tests.log). '
        '[`validation.json`](validation.json) records sheet coverage, native raster pixel equality, '
        'source custody and F2 checks. [`input_bindings.json`](input_bindings.json) pins read-only '
        'inputs; [`execution.json`](execution.json) records execution limits.', '',
        'Reproduce sequentially from this worktree with an inherited actual nice ≥15 '
        '(the scripts refuse lower priority):', '',
        '```sh',
        '.venv/bin/python -B docs/harvest/recut_v1/v2_pilot/diag/run_diag.py',
        '.venv/bin/python -B docs/harvest/recut_v1/v2_pilot/diag/make_sheets.py',
        '.venv/bin/python -B docs/harvest/recut_v1/v2_pilot/diag/test_matcher.py',
        '.venv/bin/python -B docs/harvest/recut_v1/v2_pilot/diag/write_report.py',
        '.venv/bin/python -B docs/harvest/recut_v1/v2_pilot/diag/verify_artifacts.py',
        '```', '',
        'The scoped [`guarded_commit.py`](guarded_commit.py), adapted from the existing masking '
        'helper, uses `--prepare`, `--check-only`, then no flag for the one commit attempt. It '
        'excludes ignored files, accepts only diag/**, verifies exact starting HEAD/branch and '
        'file hashes, requires an empty index, and never retries or uses an alternate index. '
        'Earlier untracked T6c1 files outside diag are excluded. The actual commit outcome is '
        'written to `COMMIT_STATUS.json` (excluded from its own commit manifest).', '',
        'The pilot stop remains unresolved: the requested horizontal condition is already in force, '
        'and all original matching failures remain. Resolving detector misses/merged curves or '
        'changing the ambiguity policy needs a separately scoped follow-up.', '',
        'T6c1b: done | parliament before/after ambiguous: 36/36 unmatched: 12/12 | vouli before/after: 1/1 | unmatched causes: merge 1, miss 11, crop 0, other 1 | T6a2 unchanged: yes | overlap threshold: >=50% of crop width'
    ]
    (BASE/'DIAG.md').write_text('\n'.join(text)+'\n')
    paths=[PILOT/'sample.json',PILOT/'pilot_receipt.json',PILOT/'input_bindings.json',MASKING/'probe.py',MASKING/'params.json',MASKING/'dev/records.jsonl',MASKING/'f2/records.jsonl']
    paths += [Path(p['raster']) for p in pages]+[Path(p['curves_origin']) for p in pages]
    paths += [PILOT/'lines/parliament--37e22f57-p000005.jsonl']
    write(BASE/'input_bindings.json',dict(files=[dict(path=str(p),sha256=sha(p)) for p in paths],
                                         pilot_read_only=True,source_root=str(ROOT),
                                         full_f2_runtime_cache_hashes='f2_check.json:curve_bindings'))
    write(BASE/'physical_review.json',dict(method='Visual inspection of all 13 native unmatched witnesses and all 49 failure cards',
                                          parliament_cards=48,vouli_cards=1,unmatched_native_witnesses=13,
                                          classifications=reviews,scope='retained detector output; no internal stage attribution',
                                          cause_totals=dict(Counter(r['cause'] for r in reviews))))


if __name__=='__main__':
    main()
