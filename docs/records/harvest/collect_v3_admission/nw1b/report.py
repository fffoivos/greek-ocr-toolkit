"""Render the owner gate, every measured witness, and W1 source/class counts."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent
report=json.loads((BASE/'calibration.json').read_text())
cards=[json.loads(line) for line in (BASE/'measurements.jsonl').read_text().splitlines()]
params=report['selected']['params']
import sys
sys.path.insert(0,str(BASE.parents[3]))
from greekocr.harvest.neighbour_words import runs

def triple(r):
    return f"{r['components']} / {r['width_xh']:.6f} / {r['median_height_xh']:.6f}"

def metrics(entry):
    c=entry['confusion']
    return f"P={entry['precision']:.6f}, R={entry['recall']:.6f}; TP={c['tp']}, FP={c['fp']}, FN={c['fn']}, TN={c['tn']}"

text=['# NW1b owner calibration and application', '',
    'No OCR reading, recognizer, network call, payment, masking, PNG deletion, or write/lock in the live run root. Native geometry and the existing foreign-ink ownership measure only. Interpreter: `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`.', '',
    '## Truth and scope', '',
    'The 22 KEEP labels come verbatim from the NW1b brief. Seven owner issue IDs are explicitly named. The manifest at collect commit `83aaab5d` contains six `merged_multi_line` witnesses; their union with those seven IDs and the other gallery `screen_merged` cards (excluding explicit owner KEEP overrides) contains **ten distinct DROP cards**, including all three-line witnesses. The manifest does not uniquely identify an eighth owner issue: sg1-05 (Gazette l0128) and sg1-06 (Gazette l0146) are both additional merged witnesses; both are included, with neither invented as an owner-labelled eighth.', '',
    'The gallery also has `screen_merged: true` on half-line examples, including an explicit owner KEEP. Owner labels take precedence. All six full-line merged witnesses and every gallery `screen_merged` witness are measured. The additional flagged half-line witness (sg1-07) is DROP under the explicit request to include every gallery screen_merged card; this uses its screen flag, not checker wording. BORDERLINE is not gating.', '',
    'The retained matcher uses native body-centre LineFits; foreign ink comes directly from `_foreign_mask` with frozen ownership parameters `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`. The NW1 horizontal graph uses positive vertical overlap and the existing recut `GAP_STOP` (3 x-heights). Half-only components at crop boundaries are excluded. NW1b evaluates the **median height of the whole run**, without pre-filtering individual heights. Measurements include every candidate run before admission thresholds.', '',
    '## Gate', '',
    f"Defaults (4 components, 3 xh width, .6 median height): standalone {metrics(report['default']['standalone'])}; union {metrics(report['default']['combined'])}.", '',
    f"Selected {params}: standalone **{metrics(report['selected']['standalone'])}**. Standalone gate passes: 0/22 KEEP false drops and 10/10 DROP detections.", '',
    f"Combined with the existing screen_merged flags: {metrics(report['selected']['combined'])}. Its four KEEP false drops are already caused by screen_merged. The combined full confusion gate fails; the task is qualified through the passing standalone screen. No claim is made that screen_merged has zero owner false drops.", '',
    'Every one of the 27 nearby settings fails. Search then expanded on the same positive lattice: 1 component, .5 width xh, .1 height xh. Distance is L1 in those units, with ties resolved by fewer changed thresholds then numeric order. After 228 settings, (10, 3, .6) is the nearest passing lattice setting (distance 6). All lattice settings at smaller distance are covered; settings outside the enumerated positive bounds have distance greater than 6. This is a lattice result, not a claim of a nearest real-valued threshold.', '',
    'Existing screen_merged KEEP false drops: '+', '.join('`'+c['row_id']+'`' for c in cards if c['truth']=='keep' and c['screen_merged'])+'.', '',
    '## Every measured card', '',
    'Run notation is **components / width in x-heights / median height in x-heights**. The table reports every connected candidate run; `none` means none after half-only exclusion. Raw components, half-only flags, crop boxes, x-height, all runs and gallery IDs are in `measurements.jsonl`. Width and median are displayed rounded only; decisions use full precision. All 33 cards matched native lines.', '',
    '| Row ID | Truth | Measured runs (n / width / median) | NW selected | screen_merged | Union |',
    '|---|---|---|---|---|---|']
for c in cards:
    nw=bool(runs(c['measurement'],**params));sm=c['screen_merged']
    text.append(f"| `{c['row_id']}` | {c['truth']} | "+'; '.join(triple(r) for r in c['candidate_runs'])+('none' if not c['candidate_runs'] else '')+f" | {'drop' if nw else 'keep'} | {sm} | {'drop' if nw or sm else 'keep'} |")
merged=[c for c in cards if c['merged_full_lines']]
text+=['',f"Full-line merged subset: neighbour_words {sum(bool(runs(c['measurement'],**params)) for c in merged)}/{len(merged)}; existing screen_merged {sum(c['screen_merged'] for c in merged)}/{len(merged)}; union {sum(bool(runs(c['measurement'],**params)) or c['screen_merged'] for c in merged)}/{len(merged)}. The gallery flags do not support the assertion that screen_merged already drops every merged card.", '',
    'BORDERLINE is **keep** at the selected setting. Its largest run is 6 components / 10.092805 xh width / .604877 xh median height; another run is 5 / 3.698391 / .933239. Defaults would drop it. It does not affect threshold selection.', '',
    '## Nearby grid', '',
    '| Components | Width xh | Median xh | NW FP/22 | NW TP/10 | NW P | NW R | Union FP/22 | Union TP/10 | Union P | Union R |',
    '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for g in report['grid']:
    p=g['params'];a=g['standalone'];b=g['combined']
    text.append(f"| {p['min_components']} | {p['min_width_xh']} | {p['min_height_xh']} | {a['confusion']['fp']} | {a['confusion']['tp']} | {a['precision']:.6f} | {a['recall']:.6f} | {b['confusion']['fp']} | {b['confusion']['tp']} | {b['precision']:.6f} | {b['recall']:.6f} |")
summary=BASE/'w1_summary.json'
text+=['','## W1 application','']
if summary.exists():
    w=json.loads(summary.read_text())
    text += [f"Admission reissued from the identical input SHA-256 `{w['input_sha256']}`: **{w['before']} → {w['after']}**; {w['all_neighbour_drops']} total neighbour_words failures, {w['withdrawn']} newly withdrawn rows; {w['unmatched']} native-line unmatched rows conservatively remain n/a. Counts overlap prior admission rules; withdrawals are incremental. The row schema is unchanged. Tool version is NW1b-20261018.1; receipts record the selected thresholds and frozen ownership SHA. Later admissions use the same CLI and calibrated defaults.", '',
        '| Source × class | All neighbour_words failures | Newly withdrawn |','|---|---:|---:|']
    for k in sorted(w['neighbour_drops_per_source_class'].keys()|w['withdrawals_per_source_class'].keys()):
        text.append(f"| {k.replace('|',' × ')} | {w['neighbour_drops_per_source_class'].get(k,0)} | {w['withdrawals_per_source_class'].get(k,0)} |")
    text+=['','The withdrawn IDs are in `../w1_neighbour_words_withdrawn.txt`. `crops_manifest.jsonl` retains all previous PNG entries and marks withdrawn rows `admitted: false`; admitted rows are `true`. PNG custody is checked by the staging tests and verification receipt. No PNG was deleted.']
else:
    text+=['Application pending; published admission and crop manifests remain unchanged.']
text+=['','## Review of NW1 and ADM5b dependencies','',
    'Kept the frozen ownership adapter, page image hash checks, page-grouped cache, matcher, pure admission decision wiring, receipt provenance, ID-row CLI support, source verification and non-deleting crop retention. Corrected individual-height filtering to whole-run median, corrected component-native-label selection to use the current connected label, replaced the checker-derived C1 calibration with owner truth, and recalibrated CLI defaults. Old NW1 calibration/reissue entry points now refuse to run because their truth is superseded. Their old files and partial cache remain historical and excluded from the new commit list, except the two disabled entry points.', '',
    '`tests/test_adm5b_schema.py` and `greekocr/_vendor/codec/v2.json` are included in the guarded commit list. ADM5b needs the vendored v2 inventory because `load_codec()` defaults to it; its exact SHA-256 is tested. Neither requested file is ignored (`git check-ignore --no-index` returns 1). No ignore exception was needed. NW1/NW1b derived caches are ignored, and staged PNGs remain ignored by the existing crop directory rule. The schema test now recognizes the NW1b receipt version and its four existing neighbour provenance fields. The untracked ADM5c variant tests are retained in the list as relevant regression coverage; unrelated census outputs and other worktree changes are excluded.', '',
    'The guarded list binds reviewed paths, SHA-256, branch, HEAD and an empty index. Its guard is read-only. No staging or commit was attempted.']
(BASE/'REPORT.md').write_text('\n'.join(text)+'\n')
