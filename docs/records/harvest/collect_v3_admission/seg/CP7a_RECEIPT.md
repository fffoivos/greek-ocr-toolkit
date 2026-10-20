# SEG-CP7a receipt — draw, packs and gate geometry complete

Current stage: CP7a3. The CP7a3 section below supersedes the historical CP7a2
geometry measurements; the population run remains prepared and not run.

18 October 2026. SEG-CP7a2 resumes step 3 after steps 1–2 committed in
`44601f08`. Part A is complete. Network OFF; no crop reading, reader runs,
limit probes, publication, Git staging/commits, or live-root writes. The original
03:52:46–04:52:46 snapshot wait remains recorded in `cp7/snapshot_poll.log`;
the missing-snapshot blocker was resolved by the lead's 05:24 exports.

## Freeze and carried fixes

Freeze SHA-256: `9212fe491a37e3992d245aec0d8a47a7e9437e8e6ef3a7aa6a1025ac825fa22e`. Before the draw, all 239 bound code/input/geometry
files matched; the collector-interpreter `freeze.py verify` also matched the
full geometry implementation binding. No frozen file, threshold, ownership
parameter, truth, or witness was changed. The same verification passes after
building and testing. Steps 1–2's composed witness gate remains bound to this
unchanged freeze: KEEP 22/22, D 9/9, C1 6/6, gallery 6/6, rotated 4/4
(`CP7_frozen_verification.json`). This continuation verified its bindings;
it did not rerun or retune that witness gate.

M1 uses shared `non_segmentation_eligibility`, including confidence, lookalikes,
and `tall_box` (> 1.7 times the pre-drop page median). Height is a metadata
heuristic, not evidence of multiple lines. M2 requires a resolved, passing
composed union, zero KEEP losses and required separator coverage. Their
regressions pass in this continuation's suite.

The frozen gate's limits remain: 17 verified KEEP and five orientation-unknown
policy admits; D includes eight measured detections and one NLG unavailable-
geometry policy drop. The four rotated witnesses have unavailable structural
geometry. No unknown or unavailable measurement is promoted to verified KEEP
or measured detection.

## Snapshot inputs and population

Only these feature snapshots were read; no live-root feature file was read:

| Snapshot | SHA-256, checked against `SHA256_20261018_0524.txt` |
|---|---|
| `W1_features_20261018_0524.jsonl` | `c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c` |
| `W2_features_20261018_0524.jsonl` | `4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4` |

Manifest SHA-256: `1d8006e3dc3bf64aa78e1a64b5b964cf08a122b4cf7cc1013d362fb4b3334974`.
The builder checked hashes before loading and again after construction; the final
artifact verifier independently rechecked them. All input/exclusion bindings are
in `cp7/build_receipt.json`.

Population is `candidate_usable == true` in ADM4's included release strata,
including measured-1986–1990 Gazette, before every text, crop and SEG screen.
Both retained and rejected candidates remain eligible. Only the registered
locked/evaluation classes and calibration fresh IDs are excluded; crop-rejection
classes `mirrored_showthrough`, `rotated_crop`, and `separator_ambiguous` are not
exclusions. The 48 calibration fresh IDs are registered independently of release
eligibility. The eligible pre-screen count before exclusions is W1 33,301 + W2
75,244; the exclusion union removes 311 W1 rows and zero W2 rows, leaving
**W1 32,990 + W2 75,244 = 108,234**. W1/W2 IDs are disjoint.

| Source | Class | W1 before exclusions | W1 draw population | W2 before exclusions and draw population |
|---|---|---:|---:|---:|
| bsb_poly1850 | headings_caps | 46 | 46 | 0 |
| bsb_poly1850 | poly1850 | 3,951 | 3,820 | 6,775 |
| elstat | headings_caps | 1 | 1 | 0 |
| elstat | numerics_tables | 2,659 | 2,609 | 7,250 |
| gazette_modern | headings_caps | 2,248 | 2,245 | 0 |
| gazette_modern | modern_scanned | 8,073 | 8,071 | 40,804 |
| ia_greek_latin | headings_caps | 6 | 6 | 0 |
| ia_poly1850 | headings_caps | 61 | 61 | 0 |
| ia_poly1850 | poly1850 | 2,076 | 1,966 | 9,321 |
| kosmopolis | headings_caps | 63 | 63 | 0 |
| kosmopolis | poly1850 | 473 | 472 | 0 |
| kosmopolis | poly1900 | 2,692 | 2,686 | 0 |
| lekythos | headings_caps | 209 | 209 | 0 |
| lekythos | poly1900 | 8,072 | 8,070 | 0 |
| nlg | greek_poly | 196 | 195 | 702 |
| nlg | headings_caps | 35 | 35 | 0 |
| nlg | poly1850 | 783 | 780 | 3,230 |
| nlg | poly1900 | 430 | 428 | 2,108 |
| serbia | cyrillic | 1,227 | 1,227 | 5,054 |
| **Total** | | **33,301** | **32,990** | **75,244** |

Full wave × source × class counts, before and after exclusions, are also in
`cp7/build_receipt.json`; sorted eligible IDs are in `cp7/keys/population_ids.jsonl`.

## Draw, sealed measurements and crops

Uniform 100 without replacement, seed `seg-cp7:fresh100`:
`random.Random(seed).sample(sorted(unique population by id), 100)`.
Selection is unchanged when the population input order is reversed. All 100 IDs
exclude locked/evaluation and calibration IDs. `cp7/keys/draw.jsonl` has SHA-256
`8f02a40036e9b8fd94c04328ede6062a34d74dc9e5544d3885c63ac742242c7d`. No redraw or selection by any screen result occurred.

All 100 crops were regenerated with the collector interpreter's `ensure_crop`
logic into `cp7/crops/` outside the run root. Every crop matches `crop_sha256`;
the 110 copied pack crops (including controls) also match. The collector `.venv`
resolves to the shared toolkit environment; its prefix assertion passed. No new
detector, OCR, OSD, or fallback row fitting ran. Existing geometry caches were
consulted read-only; separator preparation used only existing structure and pixels.

`cp7/keys/sealed_decisions.jsonl.gz` contains all 100 composed per-row decisions,
including merged, neighbour_words, orientation, geometry_unavailable,
orientation_unknown and text rules. Mode is 0600. SHA-256: `70492405bc2e380d99013da6c93e9c7a3c074c389ba59a2c0f7cd1de82c28ab8`.
These decisions and their keys are outside both public reader folders.

**Measurement limitation:** all 100 have unavailable geometry and therefore
all 100 receive the frozen fail-closed screen DROP policy. There are 21
orientation-unknown observations and zero unresolved composed decisions.
The 100 policy drops are not 100 measured defect detections, and no fresh
semantic accuracy, FP/FN or generalization claim is made. These fixed outcomes
remain sealed from readers; no geometry was refitted to change them.

## Packs and launch handoff

PACK_ROOT is
`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs`.
`segcp7_a/r1` and `segcp7_b/r1` each contain 50 draw cards plus five controls.
The ten lead-approved controls are c057, c009, c013, c026, c046, c041, c029,
c072, c035 and c066; source bytes match their CAPS1 bindings. Fresh opaque IDs,
seeded order, hash-named metadata-free PNG copies, and exact public-only fields
are verified. There are no links, truth, source IDs, flags or screen outputs
in either reader folder. Each folder closes exactly over cards and crops.
Manifests sit beside the reader folders; all keys stay under `cp7/keys/`.

100/100 bed answer mappings are prepared and validated through synthetic answers
in memory, with 10/10 controls mapped separately. There are **zero actual reader
answers**, zero reader runs and zero leak-scan rollout results; pack closure is
not a completed reading scan. Evidence: `cp7/pack_closure.json`,
`cp7/keys/answer_mapping.json`, `cp7/keys/crop_custody.jsonl`, and
`cp7/verification_cp7a2.json`.

Canonical scanner SHA-256, rechecked against the required hash:
`dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`.
The frozen canonical copy is unchanged. `prompts/bsb.md` matches the Sol-reading
source byte-for-byte; the appended `prompts/segcp7_crop_rubric.md` retains both
owner sentences verbatim and the four yes/no fields, each with a one-line reason.
The launcher concatenates these exact files and contains no screen decisions.

`cp7/launch_cp7.sh` is ready and **not run**. It runs the two contexts sequentially
through `launchers/run_bed.sh`, stops at weekly usage ≥78%, uses network OFF,
`gpt-6.1-sol`, medium, and logs to `cp7/run.log`. Shell syntax checks pass for
all four launch scripts. No `cp7/run.log`, reader answers, or CP7 probe logs
were created. The canonical scanner and complete mapping run after each future
read. Part B scoring, flag/unreadable adjudication and staged replay remain later work.

## Tests and preservation

**661 passed in 10.89s**, including all 28 CP7 contracts and M1/M2 regressions
(`cp7/pytest_cp7a2.log`). This is the same scoped offline qualification suite,
rerun in this continuation:

```sh
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
../greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider \
--basetemp=/private/tmp/seg-cp7a2-tests \
tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py \
tests/test_neighbour_words.py tests/test_round1_admission_outputs.py \
tests/test_seg_cp1.py tests/test_seg_cp2.py tests/test_seg_cp3.py tests/test_seg_cp4.py \
tests/test_seg_cp4c.py tests/test_seg_cp5.py tests/test_seg_cp6.py tests/test_seg_cp7.py \
tests/labelfix --ignore=tests/labelfix/test_capture.py
```

The real artifact verifier also passed under the offline audit guard: deterministic
100, fresh 100, crop SHAs 110, mapping 100, controls 10, closure 2, public-only 2,
zero pack leaks, no reader answers. This adds actual-artifact checks to the unit
contracts without inventing real reader results. Build and verification commands
are the frozen `build.py` and `verify_artifacts.py`, with `PYTHONPATH=.` and
`PYTHONDONTWRITEBYTECODE=1` under the collector interpreter.

The earlier optional external canonical-scanner suite result remains historical:
51 passed and two RU1 historical-pack witness failures (`cp7/scanner_tests.log`).
It was not rerun, repaired, waived, or counted in the 661. Scanner hash and actual
CP7 pack closure checks pass; no 53/53 external-scanner-suite claim is made.

All nine protected artifacts match SHA, size and mtime, and all 28,798 retained
PNGs match the unchanged manifest (`cp7/preservation_cp7a2.json`). No original
PNG was deleted or rewritten. RankWarning diagnostics from existing component
polyfits are retained in `cp7/build.log`; no tuning was performed.

`CP7_COMMIT_LIST.json` binds the completed artifacts and external packs by hash.
Snapshot files remain read-only external inputs. Unrelated worktree changes and
old CP3/CP4 geometry remain outside the CP7 payload. No staging, commit or publish
action was performed. `cp7/status.json` records completion of Part A only.

SEG-CP7a: done | M1/M2 fixed | freeze: 9212fe491a37e3992d245aec0d8a47a7e9437e8e6ef3a7aa6a1025ac825fa22e | frozen gate 22/22, D 9/9, C1 6/6, gallery 6/6 | population: 32990 + 75244 | drawn 100 (screen-drop 100 sealed) | packs 2x55 | scanner sha ok | launch_cp7.sh ready | tests: 661 passed

## CP7a3 — gate geometry prepared; population run held

This section supersedes CP7a2's geometry-unavailable measurements above. It does
not supersede its unchanged draw, packs, snapshots, controls, or freeze.
No reader, OCR, OSD, network, publication, or population preparation run occurred.

The freeze remains `9212fe491a37e3992d245aec0d8a47a7e9437e8e6ef3a7aa6a1025ac825fa22e`. Full file and implementation verification
passed before preparation, before/after replay, and at final validation. Every
frozen code/input/geometry file remains unchanged. New entry points adapt cache
lookup only; the composed decision functions and parameters are unchanged.

The unchanged draw covers **96 distinct source-bound pages**. The complete
page-ID/source-path/source-SHA/frame list is [cp7/gate_geometry_pages.jsonl](cp7/gate_geometry_pages.jsonl).
Aliases are grouped by resolved source path, SHA and frame, and retain all page IDs.
The list was derived from the existing draw; no sampling or redraw was performed.

Exactly **96** existing-detector fallback calls completed, with
**0 failures**. CP3/CP4's collector `geometry.io.cache_page` mechanism
ran once per source-bound page, with row joins, row granularity, tables/statistics/
orientation off, exclusive attempt claims, and complete source/frame/options/code/
dependency/payload binding. The source rasters were read only; no live metadata or
feature file was needed. A write audit confined worker mutations to `CP7_geometry/`,
which is git-ignored. The detector resolved to the collector checkout, as in CP3/CP4;
replay used the frozen recut code. No changes were made to the live run root.

Measured serial preparation: **532.89 seconds summed over pages,
5.55 s/page** with one worker; total cache footprint including claims,
receipts and progress is **144.78 MB, 1.51 MB/page**
(decimal units). Hash-valid caches need not be structurally usable: the frozen
observer still enforces native planes, row identity, curves and row dependencies.

Recomputed sealed screen results: **6/100 drops**;
**2/100 geometry unavailable**. Reasons:
`{"invalid_source_frame_or_labels": 2}`. Both are on distinct
source pages where `labels > 0` differs from the detector ink mask (153,603 and
21,132 pixels respectively). Dimensions, schema, and label types passed; these
are inconsistent native planes, not inverted-row failures. No repair or refit was
applied. Evidence: `cp7/geometry_unavailable_diagnostics.json`.
Exclusive attribution, with unavailable → merged → neighbour_words → crossing →
orientation priority, is `geometry_unavailable=2, merged=4`. Independent positive rule counts, which
can overlap, are `geometry_unavailable=2, merged=4, neighbour_words=4, orientation=4`. Orientation unknown: 21.
These are screen observations/policy losses, not reader truth or accuracy results.

The current seal is `cp7/keys/sealed_decisions.jsonl.gz` (0600), SHA-256
`87014014a5098e67b033b9ac49003f2e793ad4701349be68171f5c3a39c16119`. The prior CP7a2 seal is preserved separately as
`cp7/keys/sealed_decisions_cp7a2.jsonl.gz` (0600), SHA-256
`70492405bc2e380d99013da6c93e9c7a3c074c389ba59a2c0f7cd1de82c28ab8`. Both remain outside reader packs. The historical
`build_receipt.json` remains intact; `build_receipt_cp7a3.json` binds the current
seal to the original inputs. No decisions were inserted into packs.
All **114 external pack files**, including manifests, are byte-unchanged;
closure, mapping, all 110 crop SHAs, zero answers, and no leaks passed the frozen
artifact verifier using the current seal receipt. Preservation also rechecked nine
protected artifacts by SHA/size/mtime and all 28,798 retained crop PNGs by manifest.

### Prepared full-population run — NOT RUN

Scope is the exact CP7a2 eligible pre-screen population after its registered
locked/evaluation/calibration exclusions: W1 32,990 + W2 75,244 = 108,234 rows,
**3057 distinct source-bound pages**. `cp7/population_geometry_pages.jsonl`
and `cp7/population_geometry_plan.json` bind the complete page manifest to the
original snapshot hashes; newer snapshots are never auto-discovered.

Output: `~/Projects/collect-v3-data/geometry_prep/`, outside any repository.
Per-page cache, exclusive attempt and preparation receipt live under `cache/PAGE/`.
The parent updates `progress.json` atomically after each completed page. Valid
source/code/options/frame/payload-bound pages are skipped on resume. Failed or
interrupted claimed pages are reported and never implicitly redetected; they need
explicit inspection before any new attempt. Alias IDs do not duplicate calls.

Exact launch command, prepared only:

```sh
bash "/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seg/cp7/launch_population_geometry.sh" 4
```

The launcher uses `nohup … &`, defaults to four workers, runs computation at
`nice 10`, records `population.pid` and `launcher.pid`, and serializes launchers
with `launcher.lock`. The watchdog refuses new submissions below **10,000,000,000
bytes** free, at startup and while running; at most N in-flight pages drain to
completion. A TERM signal similarly stops submission and drains current pages.
The actual preflight on this Mac stopped before any page because free disk was
already below the threshold (`cp7/watchdog_cp7a3.json`); this test used a temporary
output and did not launch the population run or create its output directory.

Estimated disk: **5.30 GB** including 15% headroom over the gate's measured
cache bytes/page. Keep a further 10 GB free for the watchdog. Idealized wall times
from measured serial s/page:

| Workers | Estimated hours |
|---:|---:|
| 1 | 4.71 |
| 2 | 2.36 |
| 4 | 1.18 |

These extrapolate the row-uniform gate's page mix; population page mix, CPU/disk
contention and parallel efficiency can change the result. No multiworker speed
claim is implied. No full-population geometry was prepared.

Monitor and stop after an explicitly authorized launch:

```sh
OUT="$HOME/Projects/collect-v3-data/geometry_prep"
cat "$OUT/progress.json"
tail -f "$OUT/population.log"
kill -TERM "$(cat "$OUT/population.pid")"
```

Wait for active pages and the launcher to finish before resuming with the same
launch command. A leftover launcher lock after an unclean exit requires inspection;
the launcher never removes an active or stale lock automatically.

### CP7a3 validation

**385 passed** in `cp7/pytest_geometry_cp7a3.log`: the 12 new preparation contracts
plus CP2/CP3/CP4/CP4c/CP5/CP6/CP7 regressions. New contracts include two-page
synthetic dry-run resumability, skip-valid without detector calls, watchdog zero
submissions and exact 10 GB boundary, payload/source/identity/missing corruption,
once-per-source aliases, dry/real separation, network/write confinement, and the
detached nice launcher contract. Dry-run payloads are explicitly synthetic and
cannot pass real-cache validation. Shell syntax passed; actual gate cache hashes
and the frozen public-pack artifact verifier passed separately.

SEG-CP7a3: done | gate pages prepared 96 (fail 0, 5.55 s/page, 1.51 MB/page) | still unavailable 2/100 | sealed drops 6 (geometry_unavailable=2, merged=4) | packs unchanged | population run: 3057 pages, ~5.30 GB, ~1.18 h @4 workers, command ready (not run) | tests: 385 passed
