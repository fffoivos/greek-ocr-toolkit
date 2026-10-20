"""Render the CAPS1 handoff from measured receipts, without starting a reader."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from build import HERE, REPO, REFERENCE, PACK_ROOT, BED, SHEET, SWAP_SHEET, dump
from reference_adapter import APPROVAL, load_reference, CLOSURE_SUBSTITUTIONS, ROLLOUT_SUBSTITUTIONS, REPLAY_SUBSTITUTIONS


def write():
    r = json.loads((HERE / 'build_receipt.json').read_text())
    tests = ET.parse(HERE / 'tests.xml').getroot().attrib
    passed = int(tests['tests']) - int(tests['failures']) - int(tests['errors']) - int(tests['skipped'])
    closure_path = HERE / 'scan/closure.json'
    closure = json.loads(closure_path.read_text()) if closure_path.is_file() else []
    approved = APPROVAL.is_file() and json.loads(APPROVAL.read_text()).get('approved') is True
    clean = bool(len(closure) == 2 and all(c['ok'] for c in closure) and approved)
    complete = clean and passed == int(tests['tests'])
    if clean:
        for context in ('c1', 'c2'):
            shutil.copyfile(BED / ('MANIFEST.' + context + '.json'), HERE / 'pack_inventory' / ('MANIFEST.' + context + '.json'))
    status = 'Prepared; closure clean under the explicitly approved CAPS1 configuration.' if complete else 'Prepared; strict scanner incompatibility remains unresolved. Do not start readers.'
    source_table = '\n'.join('| ' + source + ' | ' + str(n) + ' | ' + str(r['draw_per_source'].get(source, 0)) + ' |' for source, n in r['pool_per_source'].items())
    lines = []
    for context in ('c1', 'c2'):
        lines.append('/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B ' +
                     str(HERE / 'tools/scan_packs.py') + ' ' + str(BED / context) + ' && bash ' +
                     str(PACK_ROOT / 'launchers/run_bed.sh') + ' caps1 ' + context)
    (HERE / 'launch_lines.txt').write_text('\n'.join(lines) + '\n')
    tool_diffs = []
    for name, substitutions in (('scan_packs', CLOSURE_SUBSTITUTIONS), ('scan_rollout', ROLLOUT_SUBSTITUTIONS), ('replay_literal', REPLAY_SUBSTITUTIONS)):
        tool_diffs.append(load_reference(name, substitutions).__adaptation__['diff'])
    (HERE / 'tool_configuration.diff').write_text('\n'.join(tool_diffs))
    pool_mix = ', '.join(f'{s}={n}' for s, n in r['pool_per_source'].items())
    draw_mix = ', '.join(f'{s}={n}' for s, n in r['draw_per_source'].items())
    last = (f'CAPS1b: done | swapped c058 -> c066 | closure: clean (adapter) | tests: {passed}/{tests["tests"]} | launch lines ready'
            if complete else f'CAPS1b: incomplete | closure clean: {clean} | tests: {passed}/{tests["tests"]}')
    text = f'''# CAPS1: headings and capitals — Sol reader packs

{status}

No reader, limit probe, OCR, masking, admission, or network request was run. Weekly used percentage is **unmeasured**: this is an offline build. No credit balance or live budget claim is made. Before a future run, use the live probes; the owner's dashboard wins.

The read-only reference is `greek-ocr-toolkit-sol-reading`, commit `ad1889bd92e9165cd73f4f7b1ac5395aee9642f7`, `docs/harvest/sol_reading/HANDOVER.md`. The build, launcher and tool receipts bind the source files by SHA256.

## Population and draw

Source: `{r['inputs'] and next(p for p in r['inputs'] if p.endswith('/W1/features.jsonl'))}`.

Pool predicate: `primary_class == "headings_caps"` and `candidate_usable is True`, across all sources. All line-ID classes in `release_exclusions.json` are subtracted, with file counts and SHA256 checked. The input has {r['candidates_before_exclusions']} candidate headings/caps rows; {sum(r['excluded_by_class'].values())} are excluded as rotated crops (456 gazette, 2 NLG). No other line-exclusion class intersects this stratum. The unchecked-strata admission gate is not a diagnostic sampling gate; nothing here admits rows.

The resulting pool has **{r['pool']}** rows: 141 `usable_final` plus 2,070 held by `crop_tight_page`. No length ranking or source quota is used.

| Source | Pool | Uniform draw |
|---|---:|---:|
{source_table}
| **Total** | **2211** | **100** |

Exact draw: `random.Random("caps1:headings_caps").sample(id_ordered_pool, 100)`. The draw includes 10 `usable_final` and 90 held rows. `keys/pool.jsonl` and `keys/draw.jsonl` preserve the population and draw order. Split the sampled order into two disjoint groups of 50, then add five controls to each. The c1 order remains `caps1:headings_caps:order:c1`; only c2 is re-seeded with `caps1:headings_caps:order:c2:caps1b`. Every c1 file is verified byte-for-byte against the pre-swap inventory in `control_swap.json`.

## Original crops and controls

Every one of the **110 public PNGs has SHA256 equal to its W1 `crop_sha256`**, with matching content-hash filenames. They are copied regular files with one hard link, original grayscale mode `L`, and no PNG metadata. No crop is rotated, masked or re-encoded. `keys/crop_custody.json` binds each public file to its original source and hash.

Materialization used {r['crop_methods'].get('existing collector original', 0)} existing collector originals and {r['crop_methods'].get('collector ensure_crop (redirected output only)', 0)} calls through the read-only collector `ensure_crop`, changing only its destination `crop` field to this task's private cache. No byte-exact T6b original was available for these selected rows. The source raster, source hash, crop box, and expected crop hash were preserved. Python writes were audited to stay inside CAPS1 outputs; sockets were denied.

The collector's local venv is required for byte-exact regeneration: Pillow {r['materializer_environment']['pillow']}, {r['materializer_environment']['architecture']}, zlib {r['materializer_environment']['zlib']}. The handover's x86 Python 3.11 has Pillow 10.4.0 and zlib 1.3.1; it failed a regeneration hash check. It remains the interpreter for the reference scanner, as prescribed. The mismatch was not bypassed.

Controls come from C1 `bsb_poly1850__poly1850`, never `headings_caps`. The choice is seeded with `caps1:headings_caps:controls`, from seven letters=y/crop_ok=y examples and three clear negatives with nonempty reference detail. There are five per context. Labels and reference verdicts are unchanged. `marks` is excluded from control scoring and decisions.

Control sheet, **outside PACK_ROOT**: [{SHEET.name}]({SHEET}). It contains each crop, google_text, full reference verdict fields, errors and detail. The lead approved c057, c009, c013, c026, c046, c041, c029, c072 and c035. **Only replacement c066 awaits the second lead look before readers start**. Control truth is private in `keys/control_truth.json`.

CAPS1b replaces c058 in its c2 control slot with **c066**, letters=y, crop_ok=y, empty reference detail. Selection continues the original `caps1:headings_caps:controls` RNG immediately after its seven-positive draw, rejecting already-selected positives and nonempty details; c066 is the first candidate. The original negative draw/shuffle and all nine approved controls are preserved. The retired c058 public crop is removed from c2; source originals remain intact. The full sheet is re-rendered at its original path with c066 marked. The one-control lead-review image is [{SWAP_SHEET.name}]({SWAP_SHEET}); it carries the same replacement marker. `control_swap.json` records the lead ruling and pre-swap c1 hashes.

## Blinding and closure

Public contexts:

- `{BED / 'c1'}` — 50 bed + 5 controls.
- `{BED / 'c2'}` — 50 bed + 5 controls.

Each contains only `cards.jsonl` and `crops/`. IDs are fresh `k` + 10 hex. The four fields are `card_id`, `crop`, `google_text`, `word_scripts`, identically rendered for bed cards and controls. CAPS1 keys, truth, reports, prompt, contact sheet and runtime outputs are outside PACK_ROOT. The explicitly requested `PACK_ROOT/launchers/` holds only the three copied scripts. Existing entries `kosmo_poly1850/`, `logs/`, `run_read.sh`, `srk1_validation/`, and `srk2_validation/` predate CAPS1 and were not modified. Closure claims concern the two CAPS1 contexts, not those existing root entries.

The reference scanner is not parameterized for this request: it only registers bsb/yer/owner39, insists on RGB PNGs, and requires r2 to duplicate r1 in reverse. Strict scanning with CAPS1 path/schema registration was run and **failed loudly**: 55 `image not RGB PNG` hits plus `reverse reader missing` per context. Evidence: `scan/strict_reference_closure.json`. There were no other hits. Converting the PNGs to RGB would break the required W1 byte hashes; duplicating the contexts would break the requested disjoint 100-card draw.

`reference_adapter.py` prepares a source-bound, in-memory configuration. **Approval status: {'approved' if approved else 'pending; no compatible closure certification has been performed'}.** It allows original mode L and replaces the reverse-reader condition with explicit disjoint 50+5 coverage, exact hash and control checks. It does not edit any Sol-reading file. All remaining reference closure checks execute from that source. Compatibility output is labelled CAPS1-adapted; strict scanner failures remain recorded. Approval comes from the user's CAPS1b lead ruling 2 and is recorded in `adapter_approval.json`.

Only the RGB-only test and reversed-duplicate-reader condition are relaxed. The exact closure adapter diff against the source-bound reference is:

```diff
{tool_diffs[0].rstrip()}
```

The reason is byte-exact grayscale originals and disjoint 50-card contexts. Schema/path registration only binds CAPS1 to the reference's existing cards schema. Private-field, source/line-ID, keys/truth, symlink/hardlink, hash-filename, metadata and unexpected-file checks remain active. Manifest integrity in scanner v4 still requires originals intact and permits only `answers.jsonl` and `zoom/**` additions.

For rollout scanner v4, only path vocabulary is adapted: c1/c2 sibling names, sol_packs, cards.jsonl, crops/, and the local replay entrypoint. Its byte/downscale/exact-pixel matching, literal-command allowlist, path scan, and manifest integrity algorithms remain intact. The replay helper receives the same cards/crops path changes. Synthetic tests reject outside/sibling paths and foreign images and reproduce an overwritten zoom exactly. This preserves fail-closed behavior for unsupported commands; no unmatched image is accepted.

On successful approved closure, manifests live at `caps1/MANIFEST.c1.json` and `caps1/MANIFEST.c2.json`, beside their context folders, with text snapshots in `pack_inventory/`. Actual closure status: **{'clean (CAPS1-adapted)' if clean else 'strict failed; compatible scan pending'}**.

## Prompt and execution paths

`prompts/caps1.md` is a byte-identical copy of Sol-reading `prompts/bsb.md`.

SHA256: `{r['prompt_sha256']}`.

The launcher placeholder replacement is a byte no-op for this prompt because the placeholder is absent. Sol's letters and crop_ok are final for this check; marks remain pending Opus. Every flag and unreadable item must be routed for eye review per the handover. More than one control error flags a context. No decisions have been produced yet.

The requested scripts are copied to `{PACK_ROOT / 'launchers'}` and identically mirrored in this track's `launchers/`. Their `S` points to the track's private launcher directory, keeping logs, probes and rendered prompts outside PACK_ROOT. `W` and `D` point to this track; `RD` points to the requested public context. Scan output paths point to this track's `scan/`. These are path substitutions only; model flags, reader protocol, command flow and budget threshold logic are unchanged. Local entrypoints call source-bound Sol-reading scanner, mapper and ledger functions read-only.

Outputs after a future run:

- `answers/caps1/c1.*` and `c2.*`: prompt, raw answers, mapped bed answers and control checks.
- `scan/caps1/c1.scan.json` and `c2.scan.json`: mandatory v4 rollout scans.
- `usage_ledger.json`: original ledger function, rooted here.
- `launchers/logs/`, `launchers/probe.*/`, `launchers/limit_probe.log`: launcher runtime evidence.

Use `gpt-6.1-sol`, medium effort, network OFF, web disabled, apps/plugins/multi-agent disabled, project docs disabled, workspace-write cwd in the assigned context, approval=never. Probe before and after; the inherited driver refuses at primary >=78%. The handover account uses its 10080-minute weekly bucket as primary; inspect the probe's actual 10080-minute bucket, stop at weekly >=80%, and follow the owner's dashboard if it differs. Never spend credits. No probe was run during preparation.

After the lead's second pixel look at c066, run these **two exact lines in order**, c1 fully finished and its scan/control/budget results reviewed before c2. Each line runs the approved adapter closure preflight before any Codex call. The second preflight scans c2 only, so c1's permitted `answers.jsonl` / `zoom/` additions cannot invalidate a fresh-context closure check. Do not interpret the inherited driver's DONE string alone as model, mapper, control, scan or ledger success; inspect those artifacts.

```bash
{lines[0]}
{lines[1]}
```

## Launcher diff

```diff
{(HERE / 'launchers.diff').read_text().rstrip()}
```

Exact in-memory reference configuration changes are recorded in `tool_configuration.diff`. Source hashes are in `runtime_bindings.json`; no source-worktree mutation is needed.

## Verification and guarded commit list

Current tests: **{passed}/{tests['tests']} passed**, {tests['errors']} errors, {tests['failures']} failures. Evidence is `tests.log` and `tests.xml`. The suite checks the real W1 filter and all exclusion classes, held rows, crop byte hashes/copy properties, seed and context order, controls and reference truth, closure, prompt identity, launcher paths/settings/syntax, immutable inputs, mapping/control behavior, foreign-image rejection, and v4 overwritten-zoom replay. Synthetic answers occur only in tests and are never saved as reader outputs.

Reproduce offline:

```bash
cd {REPO}
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B docs/harvest/recut_v1/w1_masked/caps1/build.py --build
.venv/bin/python -B docs/harvest/recut_v1/w1_masked/caps1/prepare_launchers.py
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B docs/harvest/recut_v1/w1_masked/caps1/reference_adapter.py closure
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B docs/harvest/recut_v1/w1_masked/caps1/test_caps1.py
```

`COMMIT_FILES.txt` and `commit-inputs.json` are an explicit, SHA256-guarded text-only list. `guarded_commit.py --check-only` rejects changed HEAD/branch/files, a nonempty index, PNGs, failed tests, or missing/failed compatible closure. It performs no staging or commit. The cache and all PNGs remain local. Existing unrelated untracked files are outside the list. No Git index writes were attempted.

{last}
'''
    (HERE / 'README.md').write_text(text)
    print(status)


if __name__ == '__main__':
    write()
