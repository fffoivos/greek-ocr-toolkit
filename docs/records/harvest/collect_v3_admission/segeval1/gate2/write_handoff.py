"""Render the four-version comparison, exhaustive flips and SEG-GATE-2 hand-off."""
from collections import Counter
import json
from pathlib import Path
import re
import sys

D=Path(__file__).resolve().parent
VERSIONS=('05','06','07','08')


def read(name):return json.loads((D/name).read_text())
def rows(name):return [json.loads(s) for s in (D/name).read_text().splitlines()]
def cell(value):return str(value).replace('|','\\|').replace('\n','<br>')


def cut_text(c,old):
    cross='; '.join(f"{x['line']} {x['edge']} x={x['x']:.3f}: {x['meaning']}" for x in c['crossings']) or 'none'
    spans='; '.join(f"{s['edge']} [{s['x0']},{s['x1']}): min_visible={s['min_visible']}" for s in c['cut_spans']) or 'none'
    letters=c['cut_letters'];counts=Counter(x['edge'] for x in letters)
    return (f"crossings: {cross}; spans: {spans}; cut letters={len(letters)} {dict(counts)}, touches={sum(x['touches'] for x in letters)}, "
            f"max body_cut={max((x['body_cut'] for x in letters),default=0)}; row/upright height={c['row_frame_height']}/{c['upright_box_height']}; "
            f"0.7 flags exit/span/taller={old['baseline_exit']}/{old['low_visibility_span']}/{old['row_frame_taller']} (diagnostics only in 0.8; taller flag removed)")


def flip_table(cohort):
    flips=rows(f'flips_{cohort}.jsonl')
    text=f'# {cohort}: all {len(flips)} verdict flips, 0.7 → 0.8\n\n'
    text+=f'Full cut records (both versions), length ratios, complete reader answers and rating metadata are in [flips_{cohort}.jsonl](flips_{cohort}.jsonl). Every unchanged and flipped row is in [replay_{cohort}.jsonl](replay_{cohort}.jsonl). Cut evidence is diagnostic only in 0.8.\n\n'
    text+='| Line ID | 0.7 → 0.8 | 0.8 gate reason | Whole / cut-off | 0.8 length ratio | Skew diagnostics and former 0.7 flags | Reader state / owner rating | Reasons and reader detail |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n'
    for f in flips:
        answer=f.get('reader_answer') or {}
        detail='; '.join(f"{k}: {answer[k]}" for k in ['detail','segmentation_detail','errors','multi_line','neighbour_whole_word','rotated','horizontally_missegmented'] if answer.get(k))
        state=f"saved reader={f['reader_state']}; owner standard={f['owner_standard_state']}" if cohort=='segeval1' else (json.dumps(f['owner_rating'],ensure_ascii=False) if f['owner_rating'] else 'unrated')
        detail=f"0.7: {f['reason_07']}; 0.8: {f['reason_08']}; {detail}"
        data=[f['line_id'],f"{f['verdict_07']} → {f['verdict_08']}",f['gate_reason'],f"{f['whole_words']} / {f['cutoff_words']}",repr(f['length_ratio']),cut_text(f['main_cut'],f['main_cut_07']),state,detail]
        text+='| '+' | '.join(cell(x) for x in data)+' |\n'
    (D/f'flips_{cohort}.md').write_text(text)


def confusion_table(s,key,states):
    t='| Decision | '+' | '.join(f'0.{v[-1]} {label}' for v in VERSIONS for label in states)+' |\n'
    t+='| --- | '+' | '.join(['---:']*(len(states)*4))+' |\n'
    for verdict,label in [('DROP','REJECT'),('KEEP','ACCEPT'),('UNCERTAIN','UNCERTAIN')]:
        values=[s[key][v][verdict][state] for v in VERSIONS for state in states]
        t+='| '+label+' | '+' | '.join(map(str,values))+' |\n'
    return t


def transitions(s):
    t='| 0.7 → 0.8 | Rows |\n| --- | ---: |\n'
    for k,v in sorted(s['transitions'].items()):t+=f'| {k} | {v} |\n'
    return t


def main(commit):
    for cohort in ('segeval1','calibration'):flip_table(cohort)
    a,b=read('summary_segeval1.json'),read('summary_calibration.json')
    scope,validation,witness=read('scope_guard.json'),read('replay_validation.json'),read('witnesses.json')
    tests=int(re.search(r'(\d+) passed', (D/'all_tests.log').read_text())[1])
    assert a['rows']==150 and b['rows']==888 and validation['rows']==1038 and scope['no_rule_beyond_the_three']
    error_rows='\n'.join(f"| 0.{v[-1]} | {a['errors'][v]['FP']} | {a['errors'][v]['FN']} | {a['errors'][v]['UNC']} |" for v in VERSIONS)
    rating_rows='\n'.join(f"| 0.{v[-1]} | {b['rating_agreement'][v]['agree']} | {b['rating_agreement'][v]['FP']} | {b['rating_agreement'][v]['FN']} | {b['rating_agreement'][v]['UNC']} |" for v in VERSIONS)
    witness_rows='\n'.join(f"| `{rid}` | {w['ratio']!r} | {w['verdict']} | {w['padding']!r} | {w['whole_words']} / {w['cutoff_words']} |" for rid,w in witness.items())
    f08,f07=a['errors']['08'],a['errors']['07']
    status=f"SEGGATE2: done | 150 owner-standard 0.8: FP {f08['FP']} FN {f08['FN']} UNC {f08['UNC']} | 0.7: FP {f07['FP']} FN {f07['FN']} UNC {f07['UNC']} | 888 rated agree {b['rating_agreement']['08']['agree']}/135 | 888 flips 0.7->0.8 {b['flip_count']} | tests {tests} passed | commit {commit}"
    document=f'''# SEG-GATE-2 hand-off — segmentation 0.8

## Complete policy: exactly the owner's three rules

Owner, 19 October, verbatim:

> The rules are
> 1. detection of other lines, at least two words cutoff doesn't count
> 2. Comparison of de skewed lines' long sides normalized for height (the deskewed line's) with google output
> 3. And also height of deskewed line box x 1.5 + bounding box's height

> stop adding rules I didn't tell you to

The policy's complete rule list, in execution order:

1. **Other lines.** Run the unchanged 0.7 crop-only line inventory first. DROP for an additional complete line, preserving the frozen 0.5 `detectedRowsJudgement` additional-complete-line rule and feeding it from the crop-only inventory. DROP when whole words from other rows total **>2**. Exactly two whole words pass; cut-off words do not count. The existing absent/unsupported main row and unresolved orientation conditions remain the only gate UNCERTAIN cases. Context is optional diagnostics and never required.
2. **Length.** Measure the main row's text components with the unchanged **0.6 de-skewed row-frame box**, normalise its long side by its own height through the unchanged predictor, then call byte-identical `boxLengthJudgement` with **0.5–1.5**. The saved Google output character count is unchanged. The unchanged comparison ratio is `(characters+1)/(predicted_characters+1)`.
3. **Padding.** Call byte-identical `paddingJudgement` with **1.5** and input `(segment_height − upright_box_height) / row_frame_height`. Thus crop height may be at most upright box height + 1.5 × de-skewed line height.

**No rule beyond these three exists in the policy.** The row-frame-taller-than-upright guard and `gate: target line cut` veto are removed entirely. No baseline crossing, low-visibility span or cut letter affects a verdict. `skew_line` crossings, cut spans and cut letters remain in `evidence.gate.main_cut` for owner-sheet diagnostics, together with the unchanged raw heights; the `row_frame_taller` field is removed and the remaining `cut` summary is diagnostic only. No rule, threshold, epsilon, cap or detector was added or tuned. The 0.6 flat-angle identity handling and all 0.7 inventory definitions remain unchanged.

The retained inventory has all existing detected rows, visible fractions, body counts/IDs, supported x-ranges, coverage, component IDs, whole/cut-off word groups and optional context counts. The existing complete-row proxy is votes ≥6, bodies ≥6, visibility ≥.9, coverage ≥.6. Existing word groups use the .35-x-height gap; a whole group needs ≥2 ≥60%-visible bodies and neither horizontal crop edge. These are unchanged inventory definitions from 0.7, not new decision tests. Order is **inventory → other-lines gate → length → padding**. Non-passing gates skip length/padding. The frozen numerical functions retain their existing missing/invalid-measurement handling.

## Witnesses and tests

| Witness | Computed length ratio | Verdict | Padding in row-frame heights | Whole / cut-off other words |
| --- | ---: | --- | ---: | ---: |
{witness_rows}

`847e1ec1-p000015-l0035` now passes the gate and **KEEP** follows from ratio **0.5077247645452321**, inside the unchanged interval. It still records the baseline exit at x=1817.4010238826568, span [1990,2044) with min_visible=.869, and 10 cut letters. Those observations do not veto it. Its 0.6 full verdict was UNCERTAIN under the old neighbour logic; only its frozen numerical evidence is reused for identity checking. No verdict was forced to fit the old DROP witness designation.

`b8b6779da9a68fbed0ccdb5b-p000011-l0018` remains **KEEP**, with 0 whole / 4 cut-off words. The clean θ=0 witness `51db636c-p000048-l0024` has box, prediction and padding evidence equal to 0.6 to the digit.

**{tests} passed**, using `.venv/`, in [all_tests.log](all_tests.log). Coverage includes the two real witnesses, exactly two versus three whole words, second complete line, horizontal-edge fragments, one-body groups, the exact 60% boundary, the two gate uncertainty cases, seven diagnostic counterexamples that cannot change gate/final decisions, optional context failures, and θ=0 numerical identity. Existing pipeline and geometry regressions pass.

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_line_pipeline.py tests/test_seg_deskew.py tests/test_seg_gate.py -q
```

## 150: owner-standard confusion, all versions side by side

Fresh native replay: **150/150**, zero failures, {a['elapsed_seconds']:.2f} seconds. [Full evidence](replay_segeval1.jsonl), [summary](summary_segeval1.json), [replay log](replay_150.log). Version 0.5 is the sealed census decision; 0.6 and 0.7 are the saved native replays on the same byte-bound crops; 0.8 is this fresh native replay. REJECT = DROP; ACCEPT = KEEP.

The unchanged owner standard is recomputed from complete saved answers: a yes in multi_line / neighbour_whole_word / rotated / horizontally_missegmented, or an extra_text / missing_word_or_span / crop_clipped / merged_two_lines error, is faulty. A positive fault takes precedence over unknown flags; otherwise any missing/unknown segmentation flag is unresolved. `crop_overrun` alone is fine; other character/mark/punctuation errors alone are outside this segmentation scoring. Labels: **118 fine / 30 faulty / 2 unresolved**. Saved reader_state and full answers remain alongside these labels in every row.

{confusion_table(a,'confusion',('fine','faulty','unresolved'))}
FP = REJECT/fine; FN = ACCEPT/faulty; UNC = all UNCERTAIN verdicts, across **all 150**:

| Version | FP | FN | UNC |
| --- | ---: | ---: | ---: |
{error_rows}

The last line uses full-population counts, including **0.7 FP 59**. The older 0.7 hand-off's 19/50 fixed-reject-stratum number is not substituted for this count.

## 0.7 → 0.8 flips

All **{a['flip_count']}** flips on the 150 are DROP→KEEP: 41 owner-fine and 6 owner-faulty. All other decisions retain their verdict. [Exhaustive table](flips_segeval1.md), [full flip records](flips_segeval1.jsonl).

{transitions(a)}

All **{b['flip_count']}** flips on the 888 are DROP→KEEP; **{b['rated_flips']}** are owner-rated. [Exhaustive table](flips_calibration.md), [full flip records](flips_calibration.jsonl). Both tables include prior/current reasons, whole/cut-off counts, exact ratios, cut diagnostics, former 0.7 flags and saved labels/ratings. Only removing the two additions causes these changes; some formerly target-cut rows still DROP under one of the three retained rules.

{transitions(b)}

## 888: owner-rating confusion, all versions side by side

Fresh native replay: **888/888**, zero failures, {b['elapsed_seconds']:.2f} seconds. [Full evidence](replay_calibration.jsonl), [summary](summary_calibration.json), [replay log](replay_888.log). Fresh crop orientation/refocus/component/line/box detection uses the same local inputs and script workflow as SEG-GATE-1. Frozen raw source-context observations are reconciled again; no page detector or reader is rerun. Text is bound through the same local detail chunks and hashes. Version 0.5 is the historical `judgements.current` saved in the 0.6 replay (`verdict_before`), not a new 0.5 native replay. Versions 0.6/0.7 are saved native replays.

**135 rated** (78 owner KEEP, 57 owner DROP), **753 unrated**. Labels below come strictly from `owner_rating.decision`. Unrated rows have no accuracy label.

{confusion_table(b,'rating_confusion',('KEEP','DROP','unrated'))}
| Version | Agreement / 135 | FP: owner KEEP rejected | FN: owner DROP accepted | UNC rated |
| --- | ---: | ---: | ---: | ---: |
{rating_rows}

0.8 improves rated agreement over 0.7 (**65→94/135**), but remains below 0.5/0.6 (**98/97**). On the 150, false rejects fall **59→18** and false accepts rise **8→14**; uncertainty stays **11**. These are measured outcomes, with no tuning or new rules to force agreement. Existing inventory word/completeness proxies and sparse owner ratings limit accuracy claims; the 753 unrated crops have no agreement claim.

## Readback and scope guard

[validate.py](validate.py) passes [readback validation](replay_validation.json): all **{validation['rows']}** gate/final decisions replay exactly, every crop-only inventory and `skew_line` record matches 0.7 except the explicitly removed flag/summary dependency, and both removing and replacing all cut diagnostics plus removing context leave every final verdict unchanged. All **{validation['stage_b_exact']}** gate-passing box/padding records equal 0.6 exactly, with **{validation['predictions_exact']}** predictor outputs independently re-run exactly. All **{validation['gate_blocks_stage_b']}** blocked rows have no Stage-B measurement. Every historical decision and label/rating is read back from the frozen sources; all confusion/error/agreement totals and flip membership are independently checked. The only excluded equality field is fresh orientation elapsed `seconds`; both original timing records remain stored.

[scope_guard.json](scope_guard.json) and [source_changes.patch](source_changes.patch) restrict production changes to the policy script, the `line_inventory` segmentation stage removal, versions builder and generated versions. `NativeSegmenter` is byte-identical to 0.7, so the census fingerprint is unchanged. Only the segmentation tool fingerprint/version changes. All **{scope['immutable_source_files_verified']}** other source files, the predictor source/config/lock/executable/coefficient bytes, and the five pre-existing edited files match the initial hashes. `boxLengthJudgement` and `paddingJudgement` match frozen 0.5 and 0.7 byte for byte. Shared tracked diff/stat remains unchanged. [Initial receipt](initial_state.json), [design](DESIGN.md).

Policy SHA256: `{scope['policy_sha256']}`. Segmentation digest: `{scope['segmentation_digest']}`.

## Branch and delivery

Implementation commit: **`{commit}`**, exact parent **`67e670bac293b55afed32c1da823173344e33a38`** (requested 0.7 implementation). `sol/seg-gate` currently has a documentation-only child `f9d83ec4bb2f7722f5518eb82600700eb76af75e`; this branch deliberately starts at the explicitly requested implementation commit.

The shared Git directory is outside the sandbox's writable roots. The authorised fallback creates **`sol/seg-gate2`** in an isolated writable Git directory and packages it in [SEGGATE2.bundle](SEGGATE2.bundle). A separate hand-off commit follows the implementation. [bundle_receipt.json](bundle_receipt.json) records exact ancestry, bundle verification, independent local import and committed-byte readback. The shared checkout stays on `sol/recut-v1`, with shared refs/index untouched. The bundle is scoped to this worktree and retains the prior bundle's dependence on existing untracked runtime assets. **Never pushed.**

Network remained OFF through test fixtures and replay/readback audit hooks. Only the authorised local 150+888 replay ran, using `.venv/`; no Clariden, Slurm, OCR reader or new reader call was used.

{status}
'''
    (D/'HANDOFF.md').write_text(document)
    print(D/'HANDOFF.md')


if __name__=='__main__':main(sys.argv[1])
