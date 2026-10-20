# CAPS1: headings and capitals — Sol reader packs

Prepared; closure clean under the explicitly approved CAPS1 configuration.

No reader, limit probe, OCR, masking, admission, or network request was run. Weekly used percentage is **unmeasured**: this is an offline build. No credit balance or live budget claim is made. Before a future run, use the live probes; the owner's dashboard wins.

The read-only reference is `greek-ocr-toolkit-sol-reading`, commit `ad1889bd92e9165cd73f4f7b1ac5395aee9642f7`, `docs/records/harvest/sol_reading/HANDOVER.md`. The build, launcher and tool receipts bind the source files by SHA256.

## Population and draw

Source: `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/features.jsonl`.

Pool predicate: `primary_class == "headings_caps"` and `candidate_usable is True`, across all sources. All line-ID classes in `release_exclusions.json` are subtracted, with file counts and SHA256 checked. The input has 2669 candidate headings/caps rows; 458 are excluded as rotated crops (456 gazette, 2 NLG). No other line-exclusion class intersects this stratum. The unchecked-strata admission gate is not a diagnostic sampling gate; nothing here admits rows.

The resulting pool has **2211** rows: 141 `usable_final` plus 2,070 held by `crop_tight_page`. No length ranking or source quota is used.

| Source | Pool | Uniform draw |
|---|---:|---:|
| bsb_poly1850 | 46 | 2 |
| elstat | 1 | 0 |
| gazette_modern | 1792 | 80 |
| ia_greek_latin | 6 | 0 |
| ia_poly1850 | 61 | 7 |
| kosmopolis | 63 | 2 |
| lekythos | 209 | 8 |
| nlg | 33 | 1 |
| **Total** | **2211** | **100** |

Exact draw: `random.Random("caps1:headings_caps").sample(id_ordered_pool, 100)`. The draw includes 10 `usable_final` and 90 held rows. `keys/pool.jsonl` and `keys/draw.jsonl` preserve the population and draw order. Split the sampled order into two disjoint groups of 50, then add five controls to each. The c1 order remains `caps1:headings_caps:order:c1`; only c2 is re-seeded with `caps1:headings_caps:order:c2:caps1b`. Every c1 file is verified byte-for-byte against the pre-swap inventory in `control_swap.json`.

## Original crops and controls

Every one of the **110 public PNGs has SHA256 equal to its W1 `crop_sha256`**, with matching content-hash filenames. They are copied regular files with one hard link, original grayscale mode `L`, and no PNG metadata. No crop is rotated, masked or re-encoded. `keys/crop_custody.json` binds each public file to its original source and hash.

Materialization used 29 existing collector originals and 81 calls through the read-only collector `ensure_crop`, changing only its destination `crop` field to this task's private cache. No byte-exact T6b original was available for these selected rows. The source raster, source hash, crop box, and expected crop hash were preserved. Python writes were audited to stay inside CAPS1 outputs; sockets were denied.

The collector's local venv is required for byte-exact regeneration: Pillow 12.3.0, arm64, zlib 1.3.1.zlib-ng. The handover's x86 Python 3.11 has Pillow 10.4.0 and zlib 1.3.1; it failed a regeneration hash check. It remains the interpreter for the reference scanner, as prescribed. The mismatch was not bypassed.

Controls come from C1 `bsb_poly1850__poly1850`, never `headings_caps`. The choice is seeded with `caps1:headings_caps:controls`, from seven letters=y/crop_ok=y examples and three clear negatives with nonempty reference detail. There are five per context. Labels and reference verdicts are unchanged. `marks` is excluded from control scoring and decisions.

Control sheet, **outside PACK_ROOT**: [caps1_controls_sheet.png](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/caps1_controls_sheet.png). It contains each crop, google_text, full reference verdict fields, errors and detail. The lead approved c057, c009, c013, c026, c046, c041, c029, c072 and c035. **Only replacement c066 awaits the second lead look before readers start**. Control truth is private in `keys/control_truth.json`.

CAPS1b replaces c058 in its c2 control slot with **c066**, letters=y, crop_ok=y, empty reference detail. Selection continues the original `caps1:headings_caps:controls` RNG immediately after its seven-positive draw, rejecting already-selected positives and nonempty details; c066 is the first candidate. The original negative draw/shuffle and all nine approved controls are preserved. The retired c058 public crop is removed from c2; source originals remain intact. The full sheet is re-rendered at its original path with c066 marked. The one-control lead-review image is [caps1_control_swap.png](/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/caps1_control_swap.png); it carries the same replacement marker. `control_swap.json` records the lead ruling and pre-swap c1 hashes.

## Blinding and closure

Public contexts:

- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/caps1/c1` — 50 bed + 5 controls.
- `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/caps1/c2` — 50 bed + 5 controls.

Each contains only `cards.jsonl` and `crops/`. IDs are fresh `k` + 10 hex. The four fields are `card_id`, `crop`, `google_text`, `word_scripts`, identically rendered for bed cards and controls. CAPS1 keys, truth, reports, prompt, contact sheet and runtime outputs are outside PACK_ROOT. The explicitly requested `PACK_ROOT/launchers/` holds only the three copied scripts. Existing entries `kosmo_poly1850/`, `logs/`, `run_read.sh`, `srk1_validation/`, and `srk2_validation/` predate CAPS1 and were not modified. Closure claims concern the two CAPS1 contexts, not those existing root entries.

The reference scanner is not parameterized for this request: it only registers bsb/yer/owner39, insists on RGB PNGs, and requires r2 to duplicate r1 in reverse. Strict scanning with CAPS1 path/schema registration was run and **failed loudly**: 55 `image not RGB PNG` hits plus `reverse reader missing` per context. Evidence: `scan/strict_reference_closure.json`. There were no other hits. Converting the PNGs to RGB would break the required W1 byte hashes; duplicating the contexts would break the requested disjoint 100-card draw.

`reference_adapter.py` prepares a source-bound, in-memory configuration. **Approval status: approved.** It allows original mode L and replaces the reverse-reader condition with explicit disjoint 50+5 coverage, exact hash and control checks. It does not edit any Sol-reading file. All remaining reference closure checks execute from that source. Compatibility output is labelled CAPS1-adapted; strict scanner failures remain recorded. Approval comes from the user's CAPS1b lead ruling 2 and is recorded in `adapter_approval.json`.

Only the RGB-only test and reversed-duplicate-reader condition are relaxed. The exact closure adapter diff against the source-bound reference is:

```diff
--- /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_packs.py
+++ CAPS1 in-memory configuration
@@ -52,7 +52,7 @@
             try:
                 with Image.open(p) as im:
                     im.load()
-                    if im.format!='PNG' or im.mode!='RGB':fail('image not RGB PNG: '+rel)
+                    if im.format!='PNG' or (im.mode!='RGB' and not (bed=='caps1' and im.mode=='L')):fail('image not RGB PNG: '+rel)
                     if im.info:fail('image contains metadata: '+rel)
             except Exception as exc:fail('PNG decode: '+rel+': '+str(exc))
         else:
@@ -63,7 +63,7 @@
             if any(i and i in text for i in forbidden_ids):fail('source id in '+rel)
     for p in expected-set(files):fail('missing file: '+p)
     other=directory.parent/('r2' if directory.name=='r1' else 'r1')/itemfile(bed)
-    if directory.name!='r3':
+    if bed!='caps1' and directory.name!='r3':
         if not other.is_file():fail('reverse reader missing')
         elif data!=list(reversed(rows(other))):fail('r2 is not exact reverse')
     result={'ok':not violations,'directory':str(directory),'bed':bed,'items':len(data),'violations':violations,'files':files}
```

The reason is byte-exact grayscale originals and disjoint 50-card contexts. Schema/path registration only binds CAPS1 to the reference's existing cards schema. Private-field, source/line-ID, keys/truth, symlink/hardlink, hash-filename, metadata and unexpected-file checks remain active. Manifest integrity in scanner v4 still requires originals intact and permits only `answers.jsonl` and `zoom/**` additions.

For rollout scanner v4, only path vocabulary is adapted: c1/c2 sibling names, sol_packs, cards.jsonl, crops/, and the local replay entrypoint. Its byte/downscale/exact-pixel matching, literal-command allowlist, path scan, and manifest integrity algorithms remain intact. The replay helper receives the same cards/crops path changes. Synthetic tests reject outside/sibling paths and foreign images and reproduce an overwritten zoom exactly. This preserves fail-closed behavior for unsupported commands; no unmatched image is accepted.

On successful approved closure, manifests live at `caps1/MANIFEST.c1.json` and `caps1/MANIFEST.c2.json`, beside their context folders, with text snapshots in `pack_inventory/`. Actual closure status: **clean (CAPS1-adapted)**.

## Prompt and execution paths

`prompts/caps1.md` is a byte-identical copy of Sol-reading `prompts/bsb.md`.

SHA256: `1b27b5d2fac6491ffa5c84f3d12f762883bbaa0af01de2d91a17576760741f57`.

The launcher placeholder replacement is a byte no-op for this prompt because the placeholder is absent. Sol's letters and crop_ok are final for this check; marks remain pending Opus. Every flag and unreadable item must be routed for eye review per the handover. More than one control error flags a context. No decisions have been produced yet.

The requested scripts are copied to `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers` and identically mirrored in this track's `launchers/`. Their `S` points to the track's private launcher directory, keeping logs, probes and rendered prompts outside PACK_ROOT. `W` and `D` point to this track; `RD` points to the requested public context. Scan output paths point to this track's `scan/`. These are path substitutions only; model flags, reader protocol, command flow and budget threshold logic are unchanged. Local entrypoints call source-bound Sol-reading scanner, mapper and ledger functions read-only.

Outputs after a future run:

- `answers/caps1/c1.*` and `c2.*`: prompt, raw answers, mapped bed answers and control checks.
- `scan/caps1/c1.scan.json` and `c2.scan.json`: mandatory v4 rollout scans.
- `usage_ledger.json`: original ledger function, rooted here.
- `launchers/logs/`, `launchers/probe.*/`, `launchers/limit_probe.log`: launcher runtime evidence.

Use `gpt-6.1-sol`, medium effort, network OFF, web disabled, apps/plugins/multi-agent disabled, project docs disabled, workspace-write cwd in the assigned context, approval=never. Probe before and after; the inherited driver refuses at primary >=78%. The handover account uses its 10080-minute weekly bucket as primary; inspect the probe's actual 10080-minute bucket, stop at weekly >=80%, and follow the owner's dashboard if it differs. Never spend credits. No probe was run during preparation.

After the lead's second pixel look at c066, run these **two exact lines in order**, c1 fully finished and its scan/control/budget results reviewed before c2. Each line runs the approved adapter closure preflight before any Codex call. The second preflight scans c2 only, so c1's permitted `answers.jsonl` / `zoom/` additions cannot invalidate a fresh-context closure check. Do not interpret the inherited driver's DONE string alone as model, mapper, control, scan or ledger success; inspect those artifacts.

```bash
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/caps1/tools/scan_packs.py /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/caps1/c1 && bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers/run_bed.sh caps1 c1
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/caps1/tools/scan_packs.py /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/caps1/c2 && bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers/run_bed.sh caps1 c2
```

## Launcher diff

```diff
--- Sol-reading/launchers/run_bed.sh
+++ CAPS1/launchers/run_bed.sh
@@ -2,8 +2,8 @@
 # run_bed.sh <bed> <reader> : one blind Sol reading run with limit probes, rollout leak scan, mapping and ledger entry.
 # Stops (exit 8) before the run if weekly used >= 78%. Exit 2 = leak (run void).
 set -u; BED=$1; RDR=$2
-S=$(cd "$(dirname "$0")" && pwd); W=~/Projects/greek-ocr-toolkit-sol-reading; D=$W/docs/harvest/sol_reading
-RD=$S/sol_reading_packs/$BED/$RDR; P=$S/prompts_rendered/${BED}_${RDR}.md; LABEL=SR-$BED-$RDR
+S=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/caps1/launchers; W=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut; D=$W/docs/harvest/recut_v1/w1_masked/caps1
+RD=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/$BED/$RDR; P=$S/prompts_rendered/${BED}_${RDR}.md; LABEL=SR-$BED-$RDR
 case $RDR in r1) CL="";; *) CL=" (The README mentions cards_reverse.jsonl for reader 2: your cards.jsonl is already in your assigned order; use it as given.)";;esac
 python3 - "$D/prompts/$BED.md" "$P" "$CL" <<'PY'
 import sys; t=open(sys.argv[1]).read().replace('{{READER2_CLAUSE}}',sys.argv[3]); open(sys.argv[2],'w').write(t)
@@ -16,8 +16,8 @@
 RUN=$("$S/run_read.sh" "$LABEL" "$RD" "$P" medium | tail -1); echo "$RUN"
 ROLL=$(echo "$RUN" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['rollout'])")
 mkdir -p "$D/answers/$BED"; cp "$P" "$D/answers/$BED/$RDR.prompt.md"
-cd "$W"; /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$D/tools/scan_rollout.py" "$ROLL" "$RD" > "$D/answers/$BED/$RDR.scan.json"; SC=$?
-echo "scan rc=$SC $(head -c 300 "$D/answers/$BED/$RDR.scan.json")"
+cd "$W"; /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$D/tools/scan_rollout.py" "$ROLL" "$RD" > "$D/scan/$BED/$RDR.scan.json"; SC=$?
+echo "scan rc=$SC $(head -c 300 "$D/scan/$BED/$RDR.scan.json")"
 [ -f "$RD/answers.jsonl" ] && cp "$RD/answers.jsonl" "$D/answers/$BED/$RDR.jsonl"
 python3 -B "$D/tools/map_answers.py" "$BED" "$RDR" "$D/answers/$BED/$RDR.jsonl"; MC=$?; echo "map rc=$MC"
 AFTER=$("$S/limit_probe.sh" "after:$BED/$RDR" | tail -1); echo "$AFTER"

--- Sol-reading/launchers/run_read.sh
+++ CAPS1/launchers/run_read.sh
@@ -4,7 +4,7 @@
 # Asserts the model from the rollout and prints token usage + wall time; prints <label>_DONE / _FAILED.
 set -u; LABEL=$1; RD=$2; PROMPT=$3; EFFORT=${4:-medium}; shift 4 2>/dev/null || shift $#
 IMGS=(); [ "${1:-}" = "--" ] && { shift; for f in "$@"; do IMGS+=(-i "$f"); done; }
-S=$(cd "$(dirname "$0")" && pwd); LOG="$S/logs/$LABEL.codexlog"; OUT="$S/logs/${LABEL}_final.md"; MODEL=gpt-6.1-sol
+S=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/caps1/launchers; LOG="$S/logs/$LABEL.codexlog"; OUT="$S/logs/${LABEL}_final.md"; MODEL=gpt-6.1-sol
 B=$(date +%s); echo "[$(date '+%H:%M:%S')] $LABEL START effort=$EFFORT dir=$RD images=${#IMGS[@]}"
 codex exec -m "$MODEL" -c "model_reasoning_effort=$EFFORT" -c approval_policy=never -c project_doc_max_bytes=0 -c features.multi_agent=false \
   -c features.remote_plugin=false -c features.apps=false -c sandbox_workspace_write.network_access=false -c 'web_search="disabled"' \

--- Sol-reading/launchers/limit_probe.sh
+++ CAPS1/launchers/limit_probe.sh
@@ -1,6 +1,6 @@
 #!/usr/bin/env bash
 # limit_probe.sh <tag>: one-word non-ephemeral gpt-6.1-sol call; prints the rate-limit buckets from its rollout; appends to limit_probe.log
-S=$(cd "$(dirname "$0")" && pwd); TAG=${1:-probe}; D=$(mktemp -d "$S/probe.XXXX")
+S=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/caps1/launchers; TAG=${1:-probe}; D=$(mktemp -d "$S/probe.XXXX")
 for i in 1 2 3; do
   LOG="$D/p$i.log"
   codex exec -m gpt-6.1-sol -c model_reasoning_effort=low -c project_doc_max_bytes=0 -c features.remote_plugin=false -c features.apps=false \
```

Exact in-memory reference configuration changes are recorded in `tool_configuration.diff`. Source hashes are in `runtime_bindings.json`; no source-worktree mutation is needed.

## Verification and guarded commit list

Current tests: **14/14 passed**, 0 errors, 0 failures. Evidence is `tests.log` and `tests.xml`. The suite checks the real W1 filter and all exclusion classes, held rows, crop byte hashes/copy properties, seed and context order, controls and reference truth, closure, prompt identity, launcher paths/settings/syntax, immutable inputs, mapping/control behavior, foreign-image rejection, and v4 overwritten-zoom replay. Synthetic answers occur only in tests and are never saved as reader outputs.

Reproduce offline:

```bash
cd /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B docs/records/harvest/recut_v1/w1_masked/caps1/build.py --build
.venv/bin/python -B docs/records/harvest/recut_v1/w1_masked/caps1/prepare_launchers.py
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B docs/records/harvest/recut_v1/w1_masked/caps1/reference_adapter.py closure
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B docs/records/harvest/recut_v1/w1_masked/caps1/test_caps1.py
```

`COMMIT_FILES.txt` and `commit-inputs.json` are an explicit, SHA256-guarded text-only list. `guarded_commit.py --check-only` rejects changed HEAD/branch/files, a nonempty index, PNGs, failed tests, or missing/failed compatible closure. It performs no staging or commit. The cache and all PNGs remain local. Existing unrelated untracked files are outside the list. No Git index writes were attempted.

CAPS1b: done | swapped c058 -> c066 | closure: clean (adapter) | tests: 14/14 | launch lines ready
