# MIX1 record: draw manifests and trainer export for the wave 3 M arms (20 Oct 2026)

**Package** `$W/scaling_w3/mix1_pkg/8d25940f` (MIX1D, commit 25dc74b06). It supersedes c6f7e628, e87b9e8d and f1384fdb.

**Submitted by the coordinator:**
- manifests job **3705332** (4 CPU / 32 GiB / 2 h), output `$W/scaling_w3/mix1_runs/MIX1D-8d25940f-manifests-001`;
- export job **3705333**, afterok on 3705332 (4 CPU / 128 GiB / 4 h), output `…/MIX1D-8d25940f-export-001`.

Pre-submit checks, re-run by the lead: VERIFY package ok (70/70 inputs), VERIFY inputs ok, `CROSSCHECK_A12_CONTRACT_OK`, `--account=a0140` in every sbatch.

**Both jobs COMPLETED:** manifests 3705332 in 18:16, export 3705333 in 29:29. The receipts are copied to `run_record/` and are sha-equal to Clariden:
- `MANIFESTS_RECEIPT.json` `a4bbb3f9…`;
- `EXPORT_RECEIPT.json` `965fae30…`, status ok;
- `ARM_STATUS.json`: M1–M4 ok.

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`; `P=$W/greek-page-ocr/out`.

## What each manifest is
Shared contract for every arm:
- D = 428,872 draws per epoch, 8 epochs, seed provenance 20261015;
- real pool = `ref_364871` (SCALE1 subsets receipt `467566a7…`, 364,871 rows: W1 50,736 / W2 117,901 / v_c 196,234);
- synthetic = A12, E1 = A10, both with the exposure drops below applied;
- output per arm: `indices.jsonl.gz` rows `[epoch, position, component, pool_index, line_id]` (the training lead's wave-1c form, byte-checked by their unchanged wave1c check), plus `draws.json` and `RECEIPT.json` binding the pool shas, D and the seed.

| Arm | Definition (coordinator rulings, 20 Oct) |
|---|---|
| M1 born-digital replay | 10 pp of the scanned real half (round(0.1·D) = 42,887 positions per epoch) are replaced by E1 train rows. Matching is collector `script_class` × `ceil(width/128)·128`, as in e4prep m1_mix, with largest-remainder allocation over supported strata. Unsupported strata stay scanned and are reported per stratum. Synthetic stays at 50%. |
| M2 synthetic 40 / 50 / 60 + curriculum | Largest remainder per epoch, with the 8-epoch totals exact: 1,372,390 / 1,715,488 / 2,058,586 synthetic draws. The curriculum is 70% × 4 epochs then 30% × 4, with per-image cumulative exposure equal to the 50% arm (±1). 0 new images. |
| M3 class reweighting (capped, uncapped) | Dominant script = the unique positive argmax of census `decision.final_inventory` greek/latin/cyrillic letters. A tie or no letters gives `none`. This is census evidence, not import `script_class`. The baseline Cyrillic share on ref_364871 is **7,693 / 364,871 = 2.108%** (Greek 305,984, Latin 37,000, none 14,194; 0 missing inventories). Cyrillic reaches 6% by repetition only. In the capped manifest, parliament is capped at 25% of draw mass first and the rest renormalised. |
| M4 source temperature (α = 1, 0.5) | `p_i ∝ n_i^α` over 9 waves (table below). The parliament 25% cap is applied after temperature. A ledger records the raw weights, pre-cap and post-cap probabilities. Independent of M3. |

## Wave table (M4)
Waves come from the v2 import `wave` field (import sha `5c5429a4…`), joined to v_c rows by id, plus W1 and W2.

| Wave | v2 import rows | In ref_364871 |
|---|---:|---:|
| W1 | — | 50,736 |
| W2 | — | 117,901 |
| parliament | 64,521 | 57,251 |
| round1 | 46,964 | 46,172 |
| mixed | 27,583 | 26,434 |
| vouli | 24,938 | 24,604 |
| openarchives | 19,625 | 18,429 |
| round2 | 18,782 | 18,421 |
| cyrillic | 12,023 | 4,923 |

## Exposure and text audit against benchmark 0.2 (seal04, suite `9447f09c…`)
- **Real pool:** inherits the SCALE1 subset audit: 0 benchmark keys, 0 benchmark crop shas, 0 dev/test editions, 0 v2 dev/test docs, all crops re-hashed.
- **E1 and A12:** a text-exposure audit against the 2,690 seal04 references, replacing the edition check (coordinator ruling). The two rules are an exact match after NFC + whitespace normalisation, and any shared normalised substring of ≥ 30 characters (exact 30-codepoint window index). Hits are dropped and counted; the key and crop-sha checks are kept.

| Family | Candidates kept | Dropped | By source |
|---|---:|---:|---|
| E1 (born-digital) | 19,655 | 2 | CJN_511 1 exact, ZRL_809 1 exact |
| A12 (synthetic v5) | 190,199 | 287 | synth_furniture 274 exact (short furniture strings); estianews 11 (1 exact, 10 ≥ 30 chars); o1d_real 1; wikisource_el 1 |

The A12 counts are identical whether computed on `old_v2` or on its v1 root, since the labels are equal across the chain.

## Custody chains
- **A12, synthetic v5:**
  - root `$P/e1_run4/synthetic` (v1, build_info `49545343…`);
  - then `$P/e4/wave1b/v2-codec/old_v2/synthetic` (v2 tag only, build_info `94e899a3…`), **the wave-2 control's source**;
  - then MIX1's own `clone_build` v2.1 derivative (the training lead's unchanged `bench/e4_codec_release.py`; only `codec_version` changes; codec `eae613e8…`).
  - Chain gt equality (line_id, gt_nfd, gt_nfc, label_ids) is sampled at 1,122 rows across 51 shards and checked in full in the export job before cloning.
  - **Cross-check with the control** (`inventory03/control_synthetic_7`): `CROSSCHECK_A12_CONTRACT_OK source 94e899a3… codec eae613e8…`, pre-export. The post-export shard-inventory or column equality goes in EXPORT_RECEIPT.
- **E1, born-digital:** root `$P/e1_run4/real` (build_info `dfd1ff0c…`), then MIX1's own `clone_build` v2.1 derivative. There is no v2 intermediate, which the training lead agreed. Train shards only; val 359 and reserved 3,600 are excluded (asserted).
- **Real:** ref_364871 is written once into shared v2.1 factory shards (unchanged wave-2 factory binary `bdd52e58…` + `encode_admissions`), referenced by all 9 plans. The 1,000-row real round trip (all three parents, full `validate()` + `load_rows`) passed: 0 drops, 0 NFD mismatches. Evidence is kept at `$W/scaling_w3/mix1_scratch/`.
- **Loader:** the final wave-2 package `$W/e4_wave2_rel3_20261020/code/27a49e51fa735e8f` (c5841ba), local = deployed.

## Dependency: the fixed-draw reader (S1 package)
The trainer's `assemble()` samples by fractions and cannot consume a given draw list. Coordinator decision: an **opt-in, separately tested entry point inside the S1 training package**, owned by the training lead ("Segmentation and secondary corrections"). It reads these `[epoch, position, component, pool_index, line_id]` manifests and checks the line_id at each pool index, D per epoch and the component map. The S1 arms stay on `assemble()`. **The M arms cannot train until that reader exists.**

## Owner decisions still open (not in MIX1)
- C2 target and codec;
- P1 pool eligibility;
- S3 needs a validated S2 calibration;
- G audits.

See `../scaling_w3/DATA_NEEDS.md`.

## Run results (jobs 3705332 → 3705333)
- **Manifests:** 9 plans, each with `indices.jsonl.gz` in the wave-1c form (schema `mix1-wave1c-index-v1`), `draws.json`, `RECEIPT.json` and per-epoch census key streams.
  - `POOLS.jsonl` `ba824f9b…`.
  - Bound sources: A12 = old_v2 `94e899a3…`; E1 = `dfd1ff0c…`.
  - D = 428,872 per epoch × 8 epochs = 3,430,976 draws per arm; seed 20261015.
- **The table is computed by the lead** from each arm's `RECEIPT.json`. Unique and repeats are per epoch, averaged over the 8 epochs. "Repeats" means draws beyond the first of the same row within an epoch.

| Arm | Real draws (8 ep) | Synthetic draws (8 ep) | E1 draws (8 ep) | Real unique / repeats per epoch (mean) | Synthetic unique / repeats per epoch | E1 unique / repeats per epoch | Cyrillic real draws / epoch | draws.json sha |
|---|---:|---:|---:|---|---|---|---:|---|
| M1 | 1,372,392 | 1,715,488 | 343,096 | 164,402 / 7,147 | 169,797 / 44,639 | 7,794 / 35,093 | 4,406 | `10bc6cb84aec…` |
| M2_syn40 | 2,058,586 | 1,372,390 | 0 | 237,573 / 19,750 | 144,702 / 26,847 | — | 5,424 | `654a4cd0fb2f…` |
| M2_syn50 | 1,715,488 | 1,715,488 | 0 | 203,397 / 11,039 | 169,797 / 44,639 | — | 4,523 | `f8a81e3cd763…` |
| M2_syn60 | 1,372,390 | 2,058,586 | 0 | 166,141 / 5,408 | 181,126 / 76,197 | — | 3,621 | `eee57617a76b…` |
| M2_curriculum | 1,715,488 | 1,715,488 | 0 | 201,554 / 12,882 | 155,263 / 59,173 | — | 4,523 | `6dcbc21ae641…` |
| M3_capped | 1,715,488 | 1,715,488 | 0 | 209,263 / 5,173 | 190,199 / 24,237 | — | 12,866 | `0b23ba2f388c…` |
| M3_uncapped | 1,715,488 | 1,715,488 | 0 | 209,263 / 5,173 | 190,199 / 24,237 | — | 12,866 | `0b23ba2f388c…` |
| M4_alpha1 | 1,715,488 | 1,715,488 | 0 | 214,436 / 0 | 190,199 / 24,237 | — | 4,523 | `ccccb967d535…` |
| M4_alpha0.5 | 1,715,488 | 1,715,488 | 0 | 210,424 / 4,012 | 190,199 / 24,237 | — | 9,782 | `5ba958b36d89…` |

**Facts these numbers establish, for the preregistrations:**
1. **M3 capped and M3 uncapped are byte-identical:** the same `draws.json` sha `0b23ba2f…` and the same per-epoch key shas. Parliament is about 15.5% of natural real draw mass (57,251 / 364,871 rows), below the 25% cap, so the cap never binds. Both ledgers record it: capped weights equal the uncapped rationals. **The pair cannot be a capped-versus-uncapped comparison on this pool.** Treat it as one M3 arm, or set a cap below about 15% if the comparison is wanted (an owner/coordinator decision).
2. **M4 α = 1** gives `after_cap` = `before_cap` = natural row shares. The cap does not bind here either. It draws each real row at most once per epoch (214,436 unique, 0 repeats). This makes it a natural-frequency arm, unlike M2_syn50, which draws with within-epoch repeats (11,039 per epoch). The two "natural 50%" arms differ only in sampling mechanics. α = 0.5 doubles Cyrillic real draws (4,523 → 9,782 per epoch).
3. **M3 reaches 6% Cyrillic** (12,866 draws per epoch, = 0.06 × 214,436) by repeating the 7,693 Cyrillic rows: 5,173 repeats per epoch.
4. **M1 replay is concentrated.** 42,887 E1 draws per epoch come from about 7,794 unique E1 rows (about 35,093 repeats per epoch), because matched script × width strata hold only part of the 19,655-row E1 train pool. The synthetic positions are identical to M2_syn50 (169,797 unique / 44,639 repeats per epoch).
5. M2 synthetic totals are exactly 1,372,390 / 1,715,488 / 2,058,586. The curriculum's synthetic total equals the 50% arm's, with per-image exposure asserted equal by the job.

## Export (3705333)
- **Shared real v2.1 shards:**
  - 364,871 rows (W1 50,736 / W2 117,901 / v_c 196,234) in 90 shards, from 9.43 GB of source crops;
  - drop ledger empty; full `validate()` ok; `load_rows` reader ok; round trip ok; full membership preserved; physical map `e62b2e94…`;
  - codec v2.1 `eae613e8…`, factory `bdd52e58…`, loader `bcce698f…` (root 27a49e51);
  - census `final_text` against factory label: 0 NFD differences. The 301,111 literal differences are NFC-versus-NFD form only; the factory stores NFD.
- **Derivatives (our own clone_build, v2.1 tag only; source columns equal, readback equal):**
  - A12: build_info `e81aa95b…`, source `94e899a3…`, rows 190,486 / 9,208 / 3,999;
  - E1: build_info `dd2a2bb0…`, source `dfd1ff0c…`, rows 19,657 / 359 / 3,600. Only train is drawable.
- **The A12 cross-check, post-export, is ok:**
  - our `prep/A12/build_info.json` sha `e81aa95b…` == the control's `inventory03/control_synthetic_7/build_info.json` sha;
  - **shard inventory sha equal `72e7c51d21de15382d06679e6dfc37a411d874d4968df0fbae7b2fdd8910a8e2`**, so the bytes are identical and column equality follows;
  - this line is sent to the training lead for the S1 REVIEW_INPUTS.
- Per arm: `export-001/<arm>/{INDEX.json, mix.json}` reference `shared/` (real) and `prep/{A12,E1}`. These are ready for the S1 fixed-draw reader.

## Coordinator rulings for the M preregistrations (20 Oct; no redraw)
1. **M3 is one arm:** Cyrillic at 6% by repetition. The parliament 25% cap is recorded as **non-binding at about 15.5% natural mass**, which is why M3_capped and M3_uncapped are byte-identical (`0b23ba2f…`). If the owner wants a cap contrast, it needs a cap below 15% and a separate draw later.
2. **The M-family control is M2_syn50:** natural frequency with within-epoch repeats, the same sampling mechanics as the wave-2 ctrl. The measured value here is 214,436 real draws per epoch over a mean of 203,397 unique rows (11,039 repeats); see the table above.
3. **M4's α contrast is internal to M4:** α = 1 against α = 0.5, reported against each other, **not against M2_syn50**. M4 α = 1 does **not** match the control in mechanics: 214,436 unique and 0 repeats per epoch.
   - Lead note on the measured mechanics: **M4 α = 0.5 is not strictly no-repeat.** It has a mean of 4,012 repeats per epoch, because upweighting small waves, e.g. Cyrillic (4,523 → 9,782 draws per epoch), exceeds those waves' unique rows. The α contrast therefore also carries a small repeat-mechanics difference: 0 against about 4.0k repeats per epoch. Report it alongside the result.
