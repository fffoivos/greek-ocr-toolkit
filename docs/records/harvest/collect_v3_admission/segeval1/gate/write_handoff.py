"""Render exhaustive flip tables and the required SEG-GATE-1 hand-off."""
from collections import Counter
import json
from pathlib import Path
import sys

D=Path(__file__).resolve().parent


def read(name):return json.loads((D/name).read_text())


def rows(name):return [json.loads(s) for s in (D/name).read_text().splitlines()]


def cell(value):
    return str(value).replace('|','\\|').replace('\n','<br>')


def cut_text(c):
    cross='; '.join(f"{x['line']} {x['edge']} x={x['x']:.3f}: {x['meaning']}" for x in c['crossings']) or 'none'
    spans='; '.join(f"{s['edge']} [{s['x0']},{s['x1']}): min_visible={s['min_visible']}" for s in c['cut_spans']) or 'none'
    letters=c['cut_letters'];counts=Counter(x['edge'] for x in letters)
    return (f"crossings: {cross}; spans: {spans}; cut letters={len(letters)} {dict(counts)}, touches={sum(x['touches'] for x in letters)}, "
            f"max body_cut={max((x['body_cut'] for x in letters),default=0)}; "
            f"row/upright height={c['row_frame_height']}/{c['upright_box_height']}; "
            f"flags exit/span/taller={c['baseline_exit']}/{c['low_visibility_span']}/{c['row_frame_taller']}")


def flip_table(cohort):
    flips=rows(f'flips_{cohort}.jsonl')
    text=f'# {cohort}: all {len(flips)} verdict flips, 0.6 → 0.7\n\n'
    text+=('Exact full-precision main-cut records, every cut-letter body_cut/touches value and complete reader answers are in '
           f'[flips_{cohort}.jsonl](flips_{cohort}.jsonl). Full unchanged and flipped rows are in [replay_{cohort}.jsonl](replay_{cohort}.jsonl). '
           'The main-cut cell below displays all crossings/spans and summarizes cut letters. PASS rows can fail Stage B.\n\n')
    text+='| Line ID | 0.6 → 0.7 | Gate reason | Whole / cut-off | Main cut evidence | Reader state / owner rating | Reader detail |\n| --- | --- | --- | --- | --- | --- | --- |\n'
    for f in flips:
        answer=f.get('reader_answer') or {}
        detail='; '.join(f"{k}: {answer[k]}" for k in ['detail','segmentation_detail','errors','multi_line','neighbour_whole_word','rotated','horizontally_missegmented'] if answer.get(k))
        state=f"saved reader={f['reader_state']}; owner standard={f['owner_standard_state']}" if cohort=='segeval1' else (json.dumps(f['owner_rating'],ensure_ascii=False) if f['owner_rating'] else 'unrated')
        if cohort=='calibration': detail=f"0.6: {f['reason_06']}; 0.7: {f['reason_07']}"
        data=[f['line_id'],f"{f['verdict_06']} → {f['verdict_07']}",f['gate_reason'],f"{f['whole_words']} / {f['cutoff_words']}",cut_text(f['main_cut']),state,detail]
        text+='| '+' | '.join(cell(x) for x in data)+' |\n'
    (D/f'flips_{cohort}.md').write_text(text)


def confusion_table(s):
    t='| Decision | 0.5 fine | faulty | unresolved | 0.6 fine | faulty | unresolved | 0.7 fine | faulty | unresolved |\n'
    t+='| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n'
    for verdict,label in [('DROP','REJECT'),('KEEP','ACCEPT'),('UNCERTAIN','UNCERTAIN')]:
        values=[s['confusion'][v][verdict][state] for v in ['05','06','07'] for state in ['fine','faulty','unresolved']]
        t+='| '+label+' | '+' | '.join(map(str,values))+' |\n'
    return t


def transitions(s):
    t='| 0.6 → 0.7 | Rows |\n| --- | ---: |\n'
    for k,v in sorted(s['transitions'].items()):t+=f'| {k} | {v} |\n'
    return t


def main(commit):
    for cohort in ['segeval1','calibration']:flip_table(cohort)
    a,b=read('summary_segeval1.json'),read('summary_calibration.json')
    scope,validation=read('scope_guard.json'),read('replay_validation.json')
    tests=152
    assert f'{tests} passed' in (D/'all_tests.log').read_text()
    assert a['rows']==150 and b['rows']==888 and validation['rows']==1038
    document=f'''# SEG-GATE-1 hand-off — segmentation 0.7

## Design

[DESIGN.md](DESIGN.md) was written before implementation (496 words; source timestamps and hash in [scope_guard.json](scope_guard.json)). The owner design is implemented as **crop-only Stage A → gate → Stage B**. The existing detector, refocus and component roles are reused. `text_lines` retains up to three rows per side. Each inventory record contains side, votes, visibility, inclusive supported x-range, coverage, ≥60%-visible body count and IDs, completeness, component IDs, whole/cut-off word counts and groups, and optional reconciled context counts. Row component assignment uses the closest existing body centre at the component's centre x; it fits no new bands.

A complete row needs **votes ≥6, bodies ≥6, visible ≥.9, coverage ≥.6**. Word gaps use the existing `neighbour_words.row_word_evidence`/`WORD_PROXY.word_gap_xh=.35` scale within each band, rather than `runs`' archival 3-x-height line grouping. Whole words require ≥2 ≥60%-visible bodies and neither horizontal crop edge; all other groups count as cut-off. `skew_line` contributes every crossing, cut span and cut letter. The target-cut guard is an exiting baseline crossing, a cut span with min_visible <.6, or exact row-frame height > upright height. Then complete neighbours and >2 whole words veto. Missing/unsupported main rows or unresolved orientation alone give gate UNCERTAIN.

Gate failures skip Stage B entirely and explicitly leave box/padding unavailable. The gate records all cut evidence and height measurements. Stage B retains the 0.6 row-frame pixel-cell measurement, predictor, byte-identical `boxLengthJudgement`/`paddingJudgement`, 0.5–1.5 length thresholds and padding input `(segment_height-upright_box_height)/row_frame_height`. Reasons name their stage. Optional context is reconciled unchanged; expected missing/unusable page errors are recorded as diagnostics and cannot veto a verified crop.

The DROP witness `847e1ec1-p000015-l0035` exits bottom at x=1817.401; span [1990,2044) has min_visible=.869 and there are 10 cut letters (3 top, 7 bottom). It now drops as **gate: target line cut**, before any predictor call. The KEEP witness `b8b6779da9a68fbed0ccdb5b-p000011-l0018` has no crossings/spans; its one touched top letter has body_cut=0. It has **0 whole / 4 cut-off groups**, passes the gate and keeps through length. The independent `second_line` diagnostic reports 1 body with visibility .274 and coverage .102; the `text_lines` above band has visibility .192 and 0 qualifying bodies. Those existing functions use different fitted band positions; no refit was introduced to equate them.

Policy SHA256: `{scope['policy_sha256']}`. Segmentation component digest: `{scope['segmentation_digest']}`. [source_changes.patch](source_changes.patch) and [scope_guard.json](scope_guard.json) show production changes limited to `NativeSegmenter.__call__`, the additive crop-tools inventory feature, policy, versions builder and generated versions. The census digest changes only because it fingerprints the native adapter. Both measurement helper functions are unchanged. Predictor source, lock/config, executable and coefficients are byte-identical. All five protected edits retain their original hashes and the tracked diff stat is unchanged.

Git creation of `sol/seg-gate` failed with `cannot lock ref ... sol/seg-gate.lock: Operation not permitted`, because the shared Git directory is outside the writable sandbox. [SEGGATE1.bundle](SEGGATE1.bundle) contains the branch and commits in an isolated writable Git directory. Its parent is the local `sol/seg-deskew` tip `cb042ae4ff74bb99c546e8af4de4b3e944aa2339`, a documentation-only child of the requested **58978481c669a21068a5192c9c3022dcd31320af** implementation. Implementation commit: `{commit}`. The bundle includes a separate hand-off commit. The shared worktree remains on `sol/recut-v1`; shared refs/index are unchanged. No push. Like 0.6, this is a scoped bundle for this worktree and depends on its existing untracked runtime assets, rather than packaging every pre-existing untracked file. [bundle_receipt.json](bundle_receipt.json) records ancestry, contents, hashes and verification.

## Tests

`.venv/` was used throughout. Network is disabled by test fixtures and replay audit hooks; no Clariden, Slurm or OCR reader was used. The new gate suite covers the two real witnesses, complete second line, three versus two whole words, horizontal-edge fragments and one-body groups, the exact 60% threshold, absent main/orientation uncertainty, cut/word precedence, context invariance, and missing/invalid optional page context. The DROP witness forbids both Stage-B features and predictor calls. A clean θ=0 crop matches every 0.6 box/predictor/padding value to the digit.

Final command:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_line_pipeline.py tests/test_seg_deskew.py tests/test_seg_gate.py -q
```

**{tests} passed**: 16 new gate tests, 6 geometry regressions and 130 pipeline regressions ([all_tests.log](all_tests.log)). Historical geometry tests now measure the unchanged arithmetic independently when 0.7 intentionally stops before length; their old synthetic glyph stub also supplies the band data now consumed by `skew_line`. The initial four old-test failures (additive evidence, intentional skipped boxes, incomplete stub) remain in [regression_tests.log](regression_tests.log).

[validate.py](validate.py) independently replays all **1,038** stored gate and final policy decisions, removes context and checks invariant verdicts, recomputes all cut flags and inventory counts, reruns all **{validation['predictions_exact']}** passing predictor outputs exactly, and verifies unchanged Stage-B evidence on **{validation['stage_b_exact']}** passing rows. All **{validation['gate_blocks_stage_b']}** blocked rows have no Stage-B result. Version rebuild and source/protected hashes pass. See [replay_validation.json](replay_validation.json).

## 150 confusion tables

Full evidence: [replay_segeval1.jsonl](replay_segeval1.jsonl); score receipt: [summary_segeval1.json](summary_segeval1.json). Fresh local native crop replay: {a['elapsed_seconds']:.2f} s, 150/150, zero failures. 0.5 is the sealed census decision; 0.6 is the previous native replay on the same byte-bound crops; 0.7 is this fresh replay. DROP maps to REJECT and KEEP to ACCEPT.

The **owner standard**, recomputed from full answers, is faulty for any yes in multi_line / neighbour_whole_word / rotated / horizontally_missegmented, or any extra_text / missing_word_or_span / crop_clipped / merged_two_lines error. A positive fault takes precedence over unknown flags; otherwise any unknown/missing segmentation flag is unresolved. `crop_overrun` alone is fine. Other character/mark/punctuation errors alone are outside the requested segmentation scoring rule. This gives **118 fine / 30 faulty / 2 unresolved**, rather than the older saved reader_state counts (123 fine / 24 flagged / 3 unresolved). Both labels and full answers remain in every row.

{confusion_table(a)}
FP = REJECT/fine; FN = ACCEPT/faulty; UNC = every UNCERTAIN verdict. Across **all 150**:

| Version | FP | FN | UNC |
| --- | ---: | ---: | ---: |
| 0.5 | {a['errors']['05']['FP']} | {a['errors']['05']['FN']} | {a['errors']['05']['UNC']} |
| 0.6 | {a['errors']['06']['FP']} | {a['errors']['06']['FN']} | {a['errors']['06']['UNC']} |
| 0.7 | {a['errors']['07']['FP']} | {a['errors']['07']['FN']} | {a['errors']['07']['UNC']} |

The requested last-line `/50-rejects` denominator denotes the **fixed original 0.5 reject stratum**: 0.7 has **19** false rejects there versus 0.6's **21** (0.5: 26). It is not the full-population FP count: **40 additional reader-fine crops from the original accepted stratum now reject**, giving **59** total. FN and UNC in the last line use the full 150. This distinction prevents the fixed-stratum number from masking the overall regression.

## Flip tables

The full 150 flip table, including gate reason, whole/cut-off counts, crossings/spans, cut-letter summaries, heights, saved reader state, owner-standard state and full reader detail, is [flips_segeval1.md](flips_segeval1.md). Exact cut-letter records and full answers are in [flips_segeval1.jsonl](flips_segeval1.jsonl). **{a['flip_count']}** verdict flips:

{transitions(a)}

Of 45 KEEP→DROP flips, 44 are target-line-cut and 1 is too many whole neighbour words. Among newly rejecting fine rows, **37** have only the row-frame-taller flag; one has only a low-visibility span, one only a baseline exit, one all three cut flags, and one the word-count veto. Three prior neighbour-uncertain rows now KEEP, including the required KEEP witness. Eleven prior DROP rows become UNCERTAIN because Stage A runs before length (5 unsupported main rows, 6 unresolved orientations).

## 888

Full evidence: [replay_calibration.jsonl](replay_calibration.jsonl); receipt: [summary_calibration.json](summary_calibration.json). Fresh native orientation/refocus/glyph/row/cut/box passes on **888/888** local calibration crops, zero failures, {b['elapsed_seconds']:.2f} s. The 0.6 comparison is its saved native replay, not the historical pre-0.6 judgements. Original text is hash-bound through the same local detail chunks used in SEG-DESKEW-1. Source-page observations are the same frozen raw context, reconciled again; no source-page detector rerun.

**{b['flip_count']}** flips, **{b['rated_flips']}** owner-rated. The exhaustive table is [flips_calibration.md](flips_calibration.md), with exact evidence and rating metadata in [flips_calibration.jsonl](flips_calibration.jsonl).

{transitions(b)}

**135 rated** (78 owner KEEP, 57 owner DROP); **753 unrated**. Against these existing owner ratings:

| Version | Agreement / 135 | FP (owner KEEP rejected) | FN (owner DROP accepted) | UNC |
| --- | ---: | ---: | ---: | ---: |
| 0.6 | {b['rating_agreement']['06']['agree']} | {b['rating_agreement']['06']['FP']} | {b['rating_agreement']['06']['FN']} | {b['rating_agreement']['06']['UNC']} |
| 0.7 | {b['rating_agreement']['07']['agree']} | {b['rating_agreement']['07']['FP']} | {b['rating_agreement']['07']['FN']} | {b['rating_agreement']['07']['UNC']} |

Gate reasons: {json.dumps(b['gate_reasons'],ensure_ascii=False)}. Every one of the {b['stage_b_exact']} gate-pass rows has box/predictor/padding evidence identical to its 0.6 result.

## Open issues

**This implements the requested policy; it does not improve overall owner agreement.** The height guard is strongly over-rejecting against existing labels: across all 150, FP rises 21→59 while FN falls 11→8 and UNC rises 5→11; rated calibration agreement falls 97→65. Exact row-frame height greater than upright height is not, by itself, reliable proof of clipped ink in these replays. The guard remains literal and unchanged from this brief; no epsilon, ratio, angle cutoff, detector change or threshold tuning was added to force a better score.

Crop-only words and completeness are disclosed geometric proxies. `text_lines` can only inventory its existing supported bands (up to three per side); full line detection or exact word truth is not certified by these results. The ≥2-body rule intentionally cannot count single-letter words as whole. A cut-letter edge touch without the required crossing/span/height evidence does not veto; isolated accents, ascenders or edge fragments can therefore still pass. Complete-line coverage ≥.6 can miss short full printed lines. Unknown orientation and unsupported main rows remain held. Calibration ratings cover only 135/888 and are historical local ratings; the unrated remainder has no accuracy claim. No tuning was performed on either replay.

## Context-vs-crop-only agreement

Context never enters the gate. [context_pairs_segeval1.jsonl](context_pairs_segeval1.jsonl) and [context_pairs_calibration.jsonl](context_pairs_calibration.jsonl) list every pair, including all disagreements; per-band context counts are also in `evidence.lines`.

| Cohort | Numeric context pairs | Resolved pairs | Whole-count exact (all pairs) | Whole-count exact (resolved) | Cut-off exact (all pairs) | Complete-row-count exact (all pairs) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 150 | {a['context_pairs']} | {a['context_resolved_pairs']} | {a['context_whole_agree']}/{a['context_pairs']} | {a['context_resolved_whole_agree']}/{a['context_resolved_pairs']} | {a['context_cutoff_agree']}/{a['context_pairs']} | {a['context_complete_agree']}/{a['context_pairs']} |
| 888 | {b['context_pairs']} | {b['context_resolved_pairs']} | {b['context_whole_agree']}/{b['context_pairs']} | {b['context_resolved_whole_agree']}/{b['context_resolved_pairs']} | {b['context_cutoff_agree']}/{b['context_pairs']} | {b['context_complete_agree']}/{b['context_pairs']} |

Unavailable context on detected-neighbour crops: 7/150 and 121/888. Crops without a detected neighbour need no context call and are excluded from pair denominators. The two methods deliberately differ: crop-only uses ≥2 visible bodies and a .35-xh component gap; existing context uses original source-row geometry, its prior whole-group predicate and extent reconciliation. Cut-off counts differ especially because crop-only tips can split into multiple groups. Exact count agreement does not imply lexical correctness. All 1,038 final decisions remain identical after removing context in readback validation.

SEGGATE1: done | 150 owner-standard 0.7: FP 19/50-rejects FN 8 UNC 11 | vs 0.6: FP 21 FN 11 UNC 5 | 888 flips 0.6->0.7 {b['flip_count']} | tests {tests} passed | commit {commit}
'''
    (D/'HANDOFF.md').write_text(document)
    print(D/'HANDOFF.md')


if __name__=='__main__':main(sys.argv[1])
