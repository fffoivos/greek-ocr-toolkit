**ASTRA-CENSUS05b — scoped certification after the H1 fix, 20 October 2026**

Package `997b7d2ab5a8775b` is certified for submission within the existing smoke-before-full gates. H1 and the requested L1 invariant are fixed. I found no BLOCKER or HIGH in the C/D changes. This certifies the preparation package; it does not certify an executed census, release-v3 admission population, benchmark supply, or final release quality.

I reviewed checkout HEAD `55b19a44ea0ae3c8482c9942a4fb6fd5aa3e0eb9`, the C change `66f0774fa95a68cf0ae6614566ce2255d0407022`, D receipts, and the live deployment at `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_05_20261020/code/997b7d2ab5a8775b`. The scope follows [the supplied brief](OWNER_BRIEF.txt) and the repository's `REVIEW_INPUTS.md`. The unchanged conclusions of ASTRA-CENSUS05 stand. Repository files were read-only; all new evidence is in this scratch directory. Remote operations were `sha256sum`, `cat`, `ls`, and `sbatch --test-only`; no job was submitted or detached.

**H1 is fixed, with the original witness and an isolated control.** The deployed reader was fetched using `ssh clariden cat`, then hash-checked against the manifest and local reader: SHA256 `f6af78899571c46ef8fe4b92d49f5e4bc072f1de25a4a51bdd3bb1e15ca4b944`. I executed those exact bytes locally, rather than executing Python remotely. Lines 144–156 insert configured protected crops and observed non-train/non-unassigned crops into the same set, while retaining configured and observed protected-edition checks. This matches the packaged deduplicator's crop union; protected editions remain a separate protection set.

The original [ASTRA-CENSUS05 witness](readout_witnesses.py) was reused with only locations and the CLI reader path changed; its original fixture was frozen from the pre-C Git blob. [Adaptation diff](witness_adaptation.diff), [raw outcomes](readout_witnesses.json).

| Witness against fetched deployed reader | Observations | Leak count | Equality failures | Exit |
|---|---:|---:|---:|---:|
| Original configured-crop leak | 1 | **1** | 1 | **1** |
| Original empty train export | 3 | 0 | **3 missing** | **1** |
| Isolated configured-crop control | 1 | **1** | 0 | **1** |
| Same control without configured protection | 1 | **0** | 0 | **0** |
| Isolated empty export | 3 | 0 | **3 missing** | **1** |
| Duplicate export row | 1 | 0 | **1 duplicate** | **1** |
| Changed export text | 1 | 0 | **1 row mismatch** | **1** |

The original leak fixture also fails the new exact-content check because it predates that export contract: its exported row lacks the new fixture's final_text field and retains the original embedded decision version. The isolated control removes that confound: **only heldout_leaks fails**, with `crop:true`, `edition:false`; disabling configuration produces **15/15 PASS**. [Control program](supplemental_checks.py), [control outcomes](supplemental_witnesses.json).

Firsthand recount over all **592,466** canonicalized input observations and finalized split assignments gives:

| Protection quantity | Count |
|---|---:|
| Distinct configured protected crop hashes | **9,119** |
| Distinct observed dev/test crop hashes | **124,425** |
| Configured hashes also observed in dev/test | **2,215** |
| Config-only protected hashes | **6,904** |
| Union of configured and observed protected hashes | **131,329** |
| Train input observations with config-only protected crops | **1,828** |
| Of those, collection-v2-train / W1 | **1,545 / 283** |

These 1,828 are input observations, not asserted admissions. The recount script retains its historical field name `configured_missing_from_readout` for the set difference; after this fix those hashes are included in the reader. [Recount](protection_recount.json), [program](protection_audit.py).

**L1 is fixed at the invariant and CLI boundary.** The expected export uses the inventory's train split, ADMIT decisions, and the canonical hash of `dict(observation, final_text=decision.final_text, decision=decision)`. That is the packaged export construction. The reader checks unique identities, exact row contents, and missing eligible identities; the former subset check remains. All five isolated controls above have exactly the expected failing invariant, and the three-row empty export fails with count **3** and exit **1**.

**Code and deployment identity pass.** Independently hashed filesystem bytes and Git blobs establish:

| Check | Result |
|---|---:|
| CODE_SHA `3b4090bf9b15d2d2cac53ee55161e936157ec0e5` source files | **154/154 byte-identical** |
| Additive deploy files | **13** |
| Manifest files / live package regular files | **167 / 167** |
| Live manifest payload hashes | **167/167 match** |
| Additional live input hashes: five N1, split2, five Cyrillic | **11/11 match** |
| Combined live readback | **178/178 match; 0 mismatches** |
| Changed payload paths versus pre-C manifest | **1: readout/census_readout.py** |
| Added / removed payload paths | **0 / 0** |
| PROJECTS_SHA256 and DEPLOY_PATHS.txt versus pre-C bytes | **Both identical** |

The requested “178 files” is the combined readback, not the deploy manifest's cardinality. The manifest binds 167 package files; the other 11 are external inputs. Manifest SHA256 is `997b7d2ab5a8775b2968800ba9b5161266b945574e31acf7b1dfc8bca15de9bb`; PROJECTS_SHA256 is `4864a067da0a597ea410d5bcb8346ec6736fb6f689beddff7f8d92da53c333e6`. [Local audit](identity_local.json), [live audit](identity_remote.json), [raw remote hashes](remote_sha256sum.txt), [remote inventory](remote_tree.txt).

All four **D verifier receipts are VERIFY_OK**, with empty reasons, no allowed-untracked exemptions, no dirty tracked files, and `job_submitted:false`. I checked **8/8 receipt/log checksums**, each receipt's **167/167 local and remote checks**, its manifest binding, and independently rehashed **167/167 payload Git blobs at the receipts' commit `76a6510d4eb2ad4d67b09f881bd81c2630e4ad77`**. These are revalidated existing verifier receipts, not four new invocations of the verifier. Fresh independent remote hashes and scheduler tests supplement them. [Receipt audit](records_audit.json).

**Changed tests pass, with fixture availability stated explicitly.** Pytest ran from the supplied repository root with `PYTHONDONTWRITEBYTECODE=1`, `-B`, `-p no:cacheprovider`, and scratch-only outputs using the existing sol-recut virtualenv.

| Execution | Pass | Fail | Skip | Time |
|---|---:|---:|---:|---:|
| Direct current readout suite | **19** | **0** | **9** | **31.01 s** |
| Only those nine historical cases, unchanged test/reader bytes in documented scratch layout | **9** | **0** | **0** | **1.15 s** |
| Distinct readout cases covered | **28** | **0** | **0 unresolved** | — |

The first run skips five census_04 mock cases, one census_03 evidence case, and three census_05 mock cases because their expected paths are absent from this checkout. The second run supplies the existing producer fixtures through scratch symlinks. [Direct log](readout-tests.log), [direct JUnit](readout-tests.xml), [historical-case log](readout-view-tests.log), [historical JUnit](readout-view-tests.xml), [scratch links](readout_view_setup.json). The read-only historical mock tests also assert that their source-file hashes do not change.

The inherited **600,000-row** test passes all invariants: readout **19.2718601227 s**, peak **188.09375 MiB**. This is a synthetic streaming check, not a full-population runtime forecast. [Metrics](pytest-tmp/test_streaming_600k0/streaming_receipt.json). The first recount invocation hit the system Python's pre-existing NumPy architecture mismatch; rerunning in the established virtualenv succeeded. No repository dependency was changed.

Separate reads of the three existing census_05 mocks using the fetched deployed reader also pass:

| Mock | Rows | ADMIT | HOLD | DROP | admitted_train | Invariants |
|---|---:|---:|---:|---:|---:|---|
| smoke-mode-i | 200 | 43 | 128 | 29 | 43 | **15/15 PASS** |
| smoke-mode-ii | 200 | 119 | 39 | 42 | 103 | **15/15 PASS** |
| full-mode-ii | 200 | 119 | 39 | 42 | 103 | **15/15 PASS** |

[Fresh mock results](mock_readouts_recomputed.json). These remain synthetic generations. The unchanged packaged regression suite's prior 360-pass/9-skip result stands under the specified scope; it was not rerun or counted among the 28 changed-reader tests.

**Scheduler checks pass and the full census has no debug leftovers.** Fresh live `sbatch --test-only` checks return **8/8 exit 0**:

| Kind | Smoke partition / time | Full partition / time | Smoke exit | Full exit |
|---|---|---|---:|---:|
| regression | debug / 00:30:00 | normal / 00:05:00 | 0 | 0 |
| parity | debug / 00:30:00 | normal / 00:05:00 | 0 | 0 |
| census | debug / 00:30:00 | normal / **04:00:00** | 0 | 0 |
| readout | debug / 00:30:00 | normal / 00:30:00 | 0 | 0 |

The full command sets `E4_SMOKE=0`, `CENSUS05_EXPECT_ROWS=592466`, the real split2 path/hash, and `full-split-001`; it passes no debug or short-time override. The hash-verified census sbatch declares normal/04:00:00, one task and 256 CPUs. Its `--smoke` preparation flag is conditional on `E4_SMOKE=1`. [Exact commands/responses](test_only_live.json), [static inspection](scheduler_static.json), [live census-script read](ssh_read_probe.json).

The first smoke-regression dry-check invocation timed out after 45 seconds without a scheduler result. A read-only SSH probe then succeeded; retrying the documented C commands passed all eight in 2.27–3.81 seconds each. Cause of the initial timeout is not established. [Timeout record](scheduler_initial_timeout.json), [retry log](scheduler-retry.log). Scheduler predictions are not submitted jobs or successful census execution.

**Release-v3 and benchmark consequences.** Only the reader changes in the deployed payload. The 154 production-source bytes, job scripts, configuration, split input, and correction input hashes are unchanged, so this delta introduces no changed segmentation/admission rule or release-scope policy. The reader now detects the demonstrated config-only leakage and omitted/duplicated/altered train-export rows. The mock exports remain readable under the stricter check. I found no C/D change making the run's outputs unusable for release v3 or the benchmark. Actual admissions, benchmark quotas, production runtime, and final release suitability still require the already-planned real smoke and completed-results checkpoints.

**Logged MEDIUM/LOW items; none require blocking this scoped submission certification.**

- **M1, carried forward:** the prior 02:18 sizing estimate remains a heuristic, not a qualification against the actual census_03 segmentation baseline or population timing tails. This delta does not resolve or worsen it.
- **M2, reproducibility qualification:** repository-write failures and the root-discovery error are fixed. A bare current-checkout run is **19 passed / 9 skipped**, not 28 passed. All nine missing-fixture cases pass with the documented scratch layout; retain that fixture setup with any 28-pass claim.
- **M3, closed:** the custody statement now identifies gitignored data-root archives rather than claiming committed chunks. I rehashed **35/35 archives** at that location and matched both the original archive receipt and checksum list. The prior decompression/reconstruction conclusions stand; no redundant reconstruction was needed. [Audit](records_audit.json).
- **LOW, residual L1 wording:** `complete` still describes inventory/decision completion. Both deliberate failing witnesses print `complete yes`, while their invariants fail and the CLI correctly exits 1. Consumers must use CLI success plus all invariants; `complete` alone remains insufficient for release readiness. This is retained behavior, not an exit-status regression.
- **LOW, stale handoff copy:** `FOLLOW_UP.md:189` still reports C's pre-commit **0/4 VERIFY_OK**, whereas the current `REVIEW_INPUTS.md`, `HANDOFF_CENSUS05.md`, and D receipts correctly establish **4/4**. Label that FOLLOW_UP result historical or update its pointer. The verified payload and current command block are unaffected.

No fixes were implemented during certification. [Final repository status](repo_status_final.txt) has no tracked changes; its single untracked review-session log was already present at the start.

VERDICT: CERTIFIED for submission; prior smoke-before-full gates retained | BLOCKERS: 0 | HIGH: 0
