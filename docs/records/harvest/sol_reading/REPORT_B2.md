# SR-B2 receipt

Implemented offline in the sol-reading worktree. No network, git, codex, reader launches, or changes to the external efficiency scorer. Production writes are under this directory; r3 packs/manifests are written under PACK_ROOT. Synthetic fixtures stay under `validation/` and are never loaded by production scoring.

## Scanner v2

`tools/scan_rollout.py` checks every returned `input_image` in recorded tool outputs against PNG bytes in reader `img/`, `crops/` and `zoom/`. A downscale must have a 2048-pixel long side, aspect ratio within one pixel, and RGB mean absolute error strictly below 2.0 on the 0–255 scale after Pillow resizing. It tries Pillow LANCZOS, BICUBIC, BILINEAR, NEAREST, BOX and HAMMING. The result records the matched file, filter and measured error. The historical probe's explicit absent-manifest mode admits its root PNGs as well.

Literal strings/template text and shell commands are checked for forbidden paths and names. Computed image paths and `.keys()` are permitted. Every original manifest file must remain intact; only `answers.jsonl` and `zoom/**` may be added. The scan lists all zoom files with hashes and sizes, including the pilot's generated Python and bytecode files. This remains a recorded-rollout audit, not OS isolation.

The pilot `rollout-2026-10-17T12-46-05-01a14941-1aa1-7462-9527-abe489c72a54.jsonl` passes with 62 image matches. Updated scan: `answers/owner39/r1.scan.json`; preserved original: `r1.scan.v1.json`. `PROBE_SCAN_B2.json` still rejects the historical canary read at record 12.

## Stage commands

Run from the worktree root. Define this interpreter helper and paths once:

```sh
py() { /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B "$@"; }
D=docs/records/harvest/sol_reading
P=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs
BED=owner39
```

After r1 and r2 are scanned and mapped for a bed:

```sh
py "$D/tools/build_tiebreak.py" "$BED"
```

If initial mappings/scans are not yet available, first run these for each reader, replacing `ROLLOUT` with its actual session path:

```sh
READER=r1
py "$D/tools/scan_rollout.py" "$ROLLOUT" "$P/$BED/$READER" > "$D/answers/$BED/$READER.scan.json"
py "$D/tools/map_answers.py" "$BED" "$READER" "$D/answers/$BED/$READER.jsonl"
```

A missing/VOID primary is reported and creates no pack. Zero disagreements creates no pack. A successful build writes `keys/<bed>_r3.json`, a fresh opaque ordered pack, seeded controls and owner option permutations, `MANIFEST.r3.json`, and `validation/<bed>_r3.pack_scan.json`. Existing r3 folders are retained; the builder refuses to rebuild a potentially active reader. `scan_packs.py` supports r3 and retains its original closure checks. Do not rerun the old full `build_packs.py` after reading begins.

After r3, audit its rollout and map its raw answers, then resolve and score:

```sh
py "$D/tools/scan_rollout.py" "$ROLLOUT" "$P/$BED/r3" > "$D/answers/$BED/r3.scan.json"
py "$D/tools/map_answers.py" "$BED" r3 "$D/answers/$BED/r3.jsonl"
py "$D/tools/resolve.py" "$BED"
py "$D/tools/score_all.py"
```

The mapping command uses the r3 key and restores yer's original slot numbers. The resolver uses bsb fields, yer slots, and complete owner anchor tuples; the owner's full majority answer object is retained. No matching third vote yields `u` or an unreadable owner answer with unknown heads and an entry in `S2.unresolved.json`. If no disagreements exist, skip r3 and run resolve/score directly. If r3 is absent on a disputed bed, resolution retains those units as unresolved and reports incomplete S2 cost. Missing primaries produce a status receipt on stdout without inventing S2 answers.

Measured usage continues to be recorded with `tools/ledger.py` using the launcher and actual before/after snapshots, as documented in README_B1. Scoring never estimates missing usage.

## Scoring scope and outputs

`score_all.py` imports the unchanged external `collect_v3/c1/efficiency/score.py`, hashes it in results, and calls its per-reader scorer. Owner scoring is dispatched through that scorer to its original owner module. Accuracy uses each reader's answered items only; r3 yer truth is restricted to its disputed slots. All denominators and bed coverage are explicit. The owner breathing exclusion comes directly from the original truth's `scored_heads`.

`results/results.json` retains original scorer output, raw mapped answers, per-field accuracy, agreement, variance, S1→S2 changes and item IDs, undecided counts, controls, scans, disagreement details and costs. `results/TABLES.md` contains plain tables without prose conclusions. BSB disagreement rows include both readers' detail strings and the Google text. Full matrix comparisons use a single common cohort among available matrix readers; pairwise owner overlaps are also shown because the four cached owner readers are partial. Missing runs are status rows, not fabricated results. VOID runs are excluded from accuracy, agreement, variance, change, undecided, control and cost tables and remain identified in status/leak audit rows. An S2 dependency on a VOID run is also VOID. Flagged controls are shown explicitly and are not silently treated as leak failures.

Sol per-run costs retain planted controls in their item denominator. S2 sums the used runs; its tokens per item and weekly points per 100 use unique bed items. Wall and weekly deltas are summed run measurements, not concurrent makespan or the difference between endpoint snapshots across unrelated intervening runs. Ratios use each S1 run's measured totals. A zero denominator or absent measurement is unavailable. Credits and weekly endpoint snapshots are retained separately. Opus run and arm-total rows report their own tokens, tool uses and summed duration, with partial owner runs marked partial. No conversion between meters is made.

## Real inputs at execution

Only owner39 r1 was present: 39 mapped bed cards, 4 controls, scan v2 OK, no control errors, not flagged. Its joint anchor agreement is 33/39; breathing is scored on 38 cards. Cached Opus E0a/E0b/E1 are scored for bsb and yer; owner partial readers have 5, 13, 8 and 7 answered cards. All other Sol runs are reported missing. No real r3 pack or S2 answer was fabricated. `validation/STAGE_STATUS_B2.json` records build/resolve responses for all beds; `results/SCORE_OUTPUT_B2.json` records the real scoring command output.

## Tests

```sh
py "$D/validation/run_tests_b2.py"
```

`TEST_RESULTS_B2.txt` records the complete SR-B1/B1b regressions plus synthetic SR-B2 suite. The previous computed-path rejection assertion was updated to v2 behavior; pre-reading-only assertions now allow manifest-authorized runtime additions. Synthetic cases cover provenance/downscale/outside images, literal paths, harmless code idioms, disputes, controls, fresh ids, all three pack formats, owner option inversion, yer submask inversion, majority/unresolved resolution, S1→S2 accounting, original scorer partial-slot dispatch, and VOID exclusion including S2 dependencies.

SR-B2 READY: tests=50/50
