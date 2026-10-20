# SCALE1: the scaling wave 3 part 1 data package (NIGHT_PLAN S1; programme §5 Stream S) (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

**Goal:** a deployable package that produces the unique-row subsets for the scaling ladder. It has two Clariden jobs, both submitted by the coordinator: (1) a tagging pass, then (2) the subset build, which takes job 1's output file + sha as input. Every rule below was ruled by the coordinator on 20 Oct (option B). Implement it as written and add no filters. **If anything below is ambiguous in the data, stop and report.**

## The ruled design
- **Universe** = release v3 ∪ the census_05-admitted v_c rows = **364,871**:
  - **release v3:** `$W/release_v3/rel3_c05_full_01/release_v3_admission.jsonl`, 168,637 W1/W2 rows. Take its sha from `RELEASE_V3_RECEIPT.json`; the coordinator quotes `92770112…`, so read the full value and bind it;
  - **v_c rows:** census_05 `admitted_train` rows of parent `collection-v2-train`, 196,234 rows (by_stratum ADMIT × train).

  `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`; census attempt `$W/census_05_20261020/attempts/full-split-001` (export g1-6283e1bc…, admitted_train sha `fe955d00…c4f3`, summary sha `096b18a8…`).
- **Sizes:** U ∈ {208,000, 364,871}. 420k exceeds the universe, so the top point is the actual maximum and is labelled **"actual maximum; targeted = reference at full universe"**.
- **Reference arm (natural frequency):** one seeded uniform permutation of the universe, keyed `(parent_id,row_id)` and sorted before shuffling. The subsets are its prefixes: ref_208k ⊂ ref_364871 (= the whole universe), nested by construction.
- **Targeted arm (208k only):** class-balanced toward the benchmark 0.2 class mix.
  - Target share per class = that class's **test quota / 2,460**, from `bench02/census05/counts.json` (16 classes; do not re-type them). Target count = share × 208,000.
  - Classes are assigned by the **bench02 precedence classifier, unchanged** (one primary class per row).
  - Selection within a class: seeded, with a source round-robin, the same mechanics as the bench02 draw (source → edition rotation; no per-edition cap unless the bench02 code applies one by default; say which).
  - A class whose supply is short of its target contributes all its rows. The surplus is redistributed proportionally over the classes that still have supply, iterating until filled.
  - If every class is exhausted before 208,000, fill the remainder from unclassified rows by the reference permutation's order, and report the count.
  - Record the exact algorithm, seeds and order in `subsets_plan.json`.
- **README statements, required verbatim in substance:**
  1. DATA_PLAN §4.1's strict reading (reference = v_c only, since every W1/W2 source was collected for a §3 target) collapses the ladder to 196k. So the programme §5 line "sized from release v3" governs, and the reference arm is natural frequency over the union.
  2. The E3-frame draw-contract elements stay with the trainer and are not applied in unique-row selection: the parliament 25% draw cap, synthetic 50%, equal optimizer draws, repeats/effective-support disclosure.
- **v_c crop custody:** checked by the lead, read-only. For 2,003 v_c admitted rows (every 98th, 28 sources), census `crop_path` exists and sha256 == `crop_sha256` in 2,003/2,003 cases. The job still re-hashes every selected crop.

## Job 1: tagging pass
- **Code:** the bench02 `census05_evidence` + tag classifier from `docs/harvest/collect_v3_admission/bench02/bench02_draw.py` at HEAD, imported unchanged. Bind its sha.
  - The BENCH02K relative-degraded rule (bottom 5% confidence within source, per split) is defined over admitted rows per split × source. Apply the same rule to the train population, per source over admitted train rows, and state it.
  - **Do not modify bench02 files.** If a wrapper is needed, put it in the new package.
- **Input:** census_05 `admitted_train.jsonl`, streamed, both parents. Each row carries its `decision`. For v_c rows, census fields such as `crop_bbox` may be null (the lead saw `crop_bbox: None` on a v2 row). Absent evidence becomes `unavailable`, exactly as the classifier already does; invent no proxies.
- **Output:** `$W/scaling_w3/tags/<attempt>/train_tags.jsonl.gz`, slim: key, parent, source, edition/doc, primary class, the tag booleans, crop_sha256, crop path. Write a receipt with the sha and bytes of the output file, the input shas, the code sha, per-parent × class counts and **per-field availability per parent**.
- Size the sbatch from local synthetic throughput plus the 7.87 GB input. Use 1 CPU on the normal partition, `$W/venv_l1/bin/python`, and an absolute `--output`.

## Job 2: subset build
**Inputs** (bound by sha): job 1's tags file + receipt; release_v3_admission.jsonl + RELEASE_V3_RECEIPT.json; census admitted_train (for the v_c rows' label/crop fields); SPLIT2 row_split + edition_map; benchmark candidates_v3 + candidates_readout.

**Outputs** to `$W/scaling_w3/subsets/<attempt>/`:
- `ref_208k.jsonl`, `ref_364871.jsonl`, `tgt_208k.jsonl`. Rows: key, parent, source, primary class, label (release v3 label for W1/W2; census `final_text` for v_c, byte for byte), crop path + crop_sha256.
- `SUBSETS_RECEIPT.json`.

**Exposure audit**, asserted per subset; any failure fails the job:
- 0 rows from SPLIT2 dev/test editions;
- 0 benchmark keys;
- 0 rows whose crop_sha256 equals a benchmark candidate's crop_sha256;
- every crop exists and re-hashes to its crop_sha256.

Also check v_c rows against the original v2 dev/test (`collection-v2-dev`/`-test` docs): count rows whose `doc` appears in v2 dev/test. This should be 0 by construction; report it, and fail if it is not 0.

**Receipt:** input/output shas and bytes; per subset, the counts per parent, per source and per primary class, alongside the targeted target shares; the nesting assertion (ref_208k ⊂ ref_364871); the redistribution trace for the targeted arm.

## Package (sol-recut `docs/harvest/collect_v3_admission/scaling_w3/`)
- Code, two sbatch files, `submit_tags.sh` and `submit_subsets.sh`. Use absolute paths. The subset submit requires the tags receipt sha as an argument.
- `VERIFY.sh` with three modes, all light on the login node:
  - package;
  - inputs-tags;
  - inputs-subsets: small shas and big-file existence/size; the jobs hash the big files.
- Tests on synthetic data:
  - prefix nesting;
  - determinism;
  - targeted redistribution, including a short class;
  - unclassified fill;
  - each exposure assertion failing correctly;
  - v_c label taken byte for byte;
  - a missing or mismatched crop failing.
- `DEPLOY_PATHS.txt`, `DEPLOY_SHA256SUMS`, `README.md` (the statements above), and `SCALE1.md`:
  - the design as implemented;
  - the exact coordinator command block: VERIFY, submit tags, then after it completes VERIFY inputs-subsets + submit subsets;
  - sbatch sizing arithmetic;
  - expected counts where they are known before the jobs run.

Deploy to the new `$W/scaling_w3/data_pkg/<sha8>/` and read every sha back. Run VERIFY package and VERIFY inputs-tags there. Inputs-subsets will report the tags output as pending.

Write a guarded commit list. Do not run `git add` or `git commit`. Touch nothing outside `scaling_w3/` except this brief's receipt section.

The last line must be exactly:
`SCALE1: done | package <root> VERIFY package ok | inputs-tags <k>/<n> | subsets pending tags job | tests <n> passed | no jobs submitted`

## Receipt — 2026-10-20 SCALE1 package

Implemented the lead's cap-free ruling in `docs/harvest/collect_v3_admission/scaling_w3/`: two streamed tagging/subset jobs, absolute-path sbatch and submit launchers, three light VERIFY modes, frozen input bindings, unchanged HEAD classifier/counts copies, exact rational redistribution, uncapped source/edition rotation, per-parent field availability, all exposure assertions and selected-crop rehashing. No bench02 file was modified. The obsolete scratch cap probe was removed; the acceptance suite tests selection of all 160 rows in one edition/series.

20 synthetic tests passed, including a complete two-job tags-receipt handoff, nested deterministic reference prefixes, iterative short-class redistribution, unclassified fill, exact v_c labels and all required exposure/crop failures. Local synthetic throughput and sbatch arithmetic are in SCALE1.md and SYNTHETIC_THROUGHPUT.json. The full release SHA remains `92770112efe63669eb079384da0b2e4754901fff0b14fdcc97208207533e37b9`.

Deployed via rsync to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/data_pkg/d14521ee/`. All 17 remote file SHAs, including both deploy manifests, were read back and matched. Remote VERIFY package: ok (15 payload hashes). VERIFY inputs-tags: 3/3. VERIFY inputs-subsets: 11/11 static inputs, tags output pending. Readback evidence is in `scaling_w3/DEPLOY_READBACK.json`; exact coordinator commands and guarded commit list are in the package. Production subsets, class counts, redistribution and full crop/exposure audits remain pending the coordinator's two jobs. No jobs submitted, allocations, spend, git add or git commit.

## Lead ruling on the stop above (20 Oct; resolves the cap ambiguity my brief introduced)
- **The targeted arm uses no edition cap and no series cap.** The per-edition/series caps are benchmark-diversity rules and do not apply to training-row selection. The coordinator's ruling names only "seeded within class with a source round-robin".
- **Mechanics:**
  - Within each class: sources in seeded order; within a source, editions in seeded order; within an edition, rows sorted by `(parent_id,row_id)` and then seeded-shuffled.
  - Take one row per source per round. Within a source, rotate editions with a persistent cursor.
  - Every row is selectable.
- **Supply and exhaustion** = the raw class population. "A class contributes all its rows" means all of them.
- **Reuse:** reuse bench02 code only where it is cap-free (the classifier and tags). Write the cap-free round-robin in the new package. **Do not modify bench02.**
- Continue the full brief from "Job 1" onward to the same final line. Keep `probe_caps.py` only if a test uses it; otherwise delete it, since it is your own scratch file.
