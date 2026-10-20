"""Write CAPS3 handoff after the offline build and qualification."""
import json
import shutil
from collections import Counter
import build as b


def launch_lines():
    py='/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B'
    lines=[f'{py} {b.HERE}/tools/scan_packs.py {b.BED}/{c} && bash {b.PACK_ROOT}/launchers/run_bed.sh caps3 {c}' for c in ('c1','c2')]
    (b.HERE/'launch_lines.txt').write_text('\n'.join(lines)+'\n')
    return lines


def main():
    s=json.loads((b.HERE/'screen_receipt.json').read_text())
    summary=json.loads((b.OUT/'summary.json').read_text())
    receipt=json.loads((b.HERE/'build_receipt.json').read_text())
    import xml.etree.ElementTree as ET
    test=ET.parse(b.HERE/'tests.xml').getroot().attrib
    assert test['tests']=='12' and all(test[k]=='0' for k in ('failures','errors','skipped'))
    totals={k:sum(r[k] for r in summary.values()) for k in ('total','masked','guarded','unmatched','changed')}
    per=', '.join(f'{k} {v}' for k,v in s['removed_per_source'].items())
    last=f"CAPS3: done | clip screen removed: {s['removed']} ({per}) [CAPS2 clipped flagged {s['clipped_flagged']}/6, fp {s['fp']}/89] | masked: {totals['masked']}/{totals['guarded']}/{totals['unmatched']} | cards: 100 | controls: 10 reused | launch lines: 2 | tests: 12 passed"
    for context in ('c1','c2'):
        shutil.copyfile(b.BED/f'MANIFEST.{context}.json',b.HERE/'pack_inventory'/f'MANIFEST.{context}.json')
    lines=launch_lines()
    table='\n'.join('| '+source+' | '+str(s['removed_per_source'][source])+' | '+' | '.join(str(v[k]) for k in ('total','masked','guarded','unmatched','changed'))+' |' for source,v in summary.items())
    text=f'''# CAPS3: screened and masked headings/capitals packs

Prepared offline. No reader or limit probe started; network OFF. Live weekly usage is unmeasured. CAPS2 remains letters 99/100 and crop_ok 89/100, a fail by one under the coordinator's ruling. CAPS3 is a fresh diagnostic sample, with no admission or scoring result yet.

## Existing clip screen

Input is the exact frozen CAPS1 pool: W1 `primary_class == headings_caps`, `candidate_usable is True`, starting release exclusions subtracted (458 rotated crops; no other starting class intersects). All 2,211 rows were screened, including held and usable rows, across all eight sources. No added merged-line, source, length, or usable-final filter was applied.

Functions: `greekocr.verify.images.image_checks` (through `readability_profile` and its native edge measurements), followed by `greekocr.verify.calibration._predict` using the existing `RULES['cut_left']` and `RULES['cut_right']`. Both rules are `edge_ink_fraction > 0.0`: the existing horizontal tolerance is zero. No new threshold, ink binarizer or edge heuristic was introduced. The 0.06 threshold elsewhere in the profile concerns smoothed **vertical** clipping and was not repurposed for horizontal edges. `screen_receipt.json` binds both helper files and their native-ink dependency `greekocr.real.geometry._ink`; `screen.jsonl` records fractions and sides for every row.

Removed **{s['removed']}** rows, leaving **{totals['total']}**. On the existing 100 CAPS2 verdicts, flagged **{s['clipped_flagged']}/6 crop_clipped** and **{s['fp']}/89 crop_ok=y**. This is a descriptive validation, not a gate; edge contact alone does not prove lost terminal text. Per-card validation is in `screen_receipt.json`.

## Concurrent exclusion registration

During qualification, the collector committed `ebc72b71369e`, adding `n1_locked_eval`. The exact starting manifest (`aaa579dce633…`, source commit `0a2f04527a3c`) is retained as `keys/release_exclusions_at_start.json`. Its existing classes are unchanged in the observed new manifest. The new class intersects **3** frozen pool rows and **1** drawn card; IDs and the opaque card mapping are private in `exclusion_drift.json`. The explicit requested CAPS1 2,211-row diagnostic population and seeded draw are preserved. No row is admitted to training. A future release must apply its current exclusion registry. The failed live-input binding check is retained in `attempts/tests_attempt2.log`; subsequent checks bind the exact starting snapshot rather than a moving external manifest.

## Frozen masking

`pipeline.py mask` calls the unmodified `docs/harvest/recut_v1/w1_masked/run.py::worker` directly. Only the population selection and output root change. The heading/caps row filter is bypassed by selecting the screened CAPS1 rows explicitly; no masking, matching, guard, detector or audit code is edited. Frozen validation runs before work. Params are `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`, foreign-ink library `f203504a…`. The nearest-curve `match` / `runtime_fit` functions come unchanged from `masking/probe.py`, the T6a2 matcher also used by T6c2 (overlap >=0.5; nearest median baseline within 1.5 x-height).

The exact T6b `guard_measure` input is original page-prepared dark ink sliced to the original crop, intersected with proposed changed pixels. Strictly >0.30 restores the byte-exact original and records `wrong_line_risk`. Guarded originals remain eligible; unmatched originals are excluded from this draw. No original W1 crop is modified. Byte hashes are checked against W1 before masking.

Run inline with at most two masking workers and numerical library threads capped at one. The initial direct-call orchestration completed 126 pages, then was stopped because per-worker I/O audit hooks accumulated in the shared process. All 126 completed page receipts, row coverage, frozen bindings and crop SHA256s were validated before reuse. The remaining 204 pages used T6b's fresh subprocess per page pattern at nice 15, two processes maximum. Masking/matching/guard code was unchanged throughout. Attempt source, binding and log are retained in `attempts/`; final binding lists resumed page IDs. All output is under `../caps_masked/`; each source has crops/pages/curves, and the aggregate is `../caps_masked/records.jsonl`, in T6b's record schema. PNGs, curves, page intermediates and selection files are git-ignored. `binding.json`, `summary.json` and `artifact_receipt.json` bind the run. Frozen T6b's legacy `usable_final=false` / `screen_merged=false` fields are preserved verbatim in its records; original W1 flags, including usable rows and any merged flags, remain in `keys/pool.jsonl` and were not used as extra filters.

| Source | Screen removed | Processed | Masked | Guarded | Unmatched | Changed |
|---|---:|---:|---:|---:|---:|---:|
{table}
| **Total** | **{s['removed']}** | **{totals['total']}** | **{totals['masked']}** | **{totals['guarded']}** | **{totals['unmatched']}** | **{totals['changed']}** |

Masked includes matched rows whose mask changes no pixels. Changed counts applied crop changes only; guarded and unmatched rows are identities.

## Draw, controls and closure

Uniform draw: `random.Random("{b.SEED}").sample(id_ordered_eligible_pool, 100)`. Eligible pool: **{receipt['pool']}** matched masked/guarded rows after excluding all CAPS1 sample IDs ({receipt['excluded_caps1']} matched rows excluded at this step). No source quota or length sorting. `keys/eligible.jsonl` and `keys/draw.jsonl` preserve input and order. Draw per source: `{json.dumps(receipt['draw_per_source'],sort_keys=True)}`.

Two disjoint contexts, 50 bed + 5 controls each. The ten lead-approved controls are reused byte-for-byte with their approved letters/crop truth: c057, c009, c013, c026, c046, c041, c029, c072, c035, c066. Their CAPS1 context assignment is preserved, context order is newly seeded with `{b.SEED}:order:c1` / `:c2`, and all 110 IDs are fresh opaque `k` + 10 hex. No new sheet was produced. `keys/control_truth.json` is identical to CAPS1's approved truth file; keys and truth stay outside PACK_ROOT.

Public contexts: `{b.BED}/c1` and `/c2`, each containing only `cards.jsonl` and `crops/`. Crops are copied, content-hash named, metadata-free PNGs in original L mode, with no hard links or symlinks. Masked bed hashes bind the frozen output; control hashes bind the originals.

Closure is clean under the explicitly requested CAPS1 adapter: unchanged grayscale allowance and disjoint 50+5 coverage checks, with only bed/output vocabulary renamed caps3. `reference_adapter.py` is byte-identical to CAPS1 after the literal caps1/CAPS1 -> caps3/CAPS3 rename. Source-bound Sol-reading checks remain read-only. Evidence: `scan/closure.json`, public `MANIFEST.c1.json` / `MANIFEST.c2.json`, and `pack_inventory/`. The source HANDOVER is `{b.REFERENCE}/HANDOVER.md`.

`prompts/caps3.md` is verbatim `prompts/bsb.md`, SHA256 `{b.sha(b.HERE/'prompts/caps3.md')}`. Sol letters/crop_ok are final for a future check; marks stay pending Opus. Every flag/unreadable needs eye review. More than one control error flags its context.

## Launch lines

Use these two lines in order, reviewing c1 scan, controls and budget before c2. Both perform adapted closure preflight. The existing public `launchers/run_bed.sh` dispatches bed caps3 to the private CAPS3 driver; its earlier behavior for other beds is preserved. The public run_read/limit_probe files are unchanged. Private scripts preserve reference flow and flags. No Codex invocation occurred during preparation.

```bash
{lines[0]}
{lines[1]}
```

Reader settings: gpt-6.1-sol, medium, network OFF, web/apps/plugins/multi-agent disabled, project docs disabled, workspace-write cwd in assigned context, approval never. Probe before/after; driver refuses at primary >=78%; inspect the actual 10080-minute weekly bucket and stop at >=80%, owner's dashboard wins. Do not spend credits. Outputs go to private `answers/caps3`, `scan/caps3`, launcher logs and `usage_ledger.json`; mandatory v4 rollout scanning remains active. A launcher's DONE string alone is not proof of scan/control success.

## Verification and guarded commit

**12 tests passed**, no errors/failures/skips. Tests replay all 2,211 screens from native crops, preserve the horizontal tolerance and CAPS2 report, check exact screen-to-mask coverage, actually re-mask three previously changed T6b rows (one per original source) byte-identically, verify frozen sources/guard/hash custody, seeded draw/exclusion, all control truths and placements, context order, closure, prompt/settings/launcher syntax, public copies and source bindings. Evidence: `tests.log`, `tests.xml`, `remask_receipt.json`.

Reproduce using the local `.venv/bin/python -B` (the frozen W1 Pillow/encoder environment):

```bash
.venv/bin/python -B docs/harvest/recut_v1/w1_masked/caps3/pipeline.py screen
.venv/bin/python -B docs/harvest/recut_v1/w1_masked/caps3/pipeline.py mask
.venv/bin/python -B docs/harvest/recut_v1/w1_masked/caps3/build.py
.venv/bin/python -B docs/harvest/recut_v1/w1_masked/caps3/prepare_launchers.py
.venv/bin/python -B docs/harvest/recut_v1/w1_masked/caps3/test_caps3.py
```

`COMMIT_FILES.txt` and `commit-inputs.json` are a guarded text-only list, bound to current HEAD, branch and file SHA256. `guarded_commit.py --check-only` verifies hashes, empty index, all tests, live closure and source bindings. The list includes aggregate masked records and receipts, excludes crops and page/curve intermediates, and leaves unrelated pre-existing untracked files alone. No staging or commit was attempted. The public launcher change is recorded separately in `public_launcher.diff` and is outside Git.

{last}
'''
    (b.HERE/'README.md').write_text(text)
    print(last)

if __name__=='__main__':main()
