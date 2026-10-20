# DATA_NEEDS: what data the wave 3 novelty families need (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` only; no building, no jobs, no writes on Clariden, no spend)

**Question from the coordinator.** For each novelty family in programme §5b, which data artefacts does it need **beyond** these three?
- release v3: `$W/release_v3/rel3_c05_full_01/`, 168,637 W1/W2 rows;
- the SCALE1 subsets: `$W/scaling_w3/subsets/scale1-c05-003/`. Job 3705111 is running, so treat the subsets as pending;
- benchmark 0.2: `$W/benchmark_0.2/seal04/`, suite `9447f09c…`.

For each such artefact: does it already exist on Clariden, with custody (a sha/receipt)? And what would a package to produce it take?

Families, from `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/POST_CLEANUP_PROGRAMME_20261019.md` §5b:
- **C2** training-only semantic guidance;
- **P1** in-domain masked pretraining on unlabelled train-only crops, with a compute-matched control;
- **S3** calibrated confidence weighting of the CTC loss;
- **G** generator v6 ablations;
- **M1/M2** (born-digital replay 10%; synthetic fraction 40/50/60 + curriculum);
- also M3/M4 (class reweighting, source temperature).

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`. **Read the specs, do not guess them.** For each family, read its entry in `TRAINING_DIRECTIONS_20261016.md` (same directory) and the referenced literature-review sections.

## For each family, determine
1. **The data artefacts its spec requires**, with the spec sentence quoted or cited. Examples:
   - P1: an unlabelled train-only crop pool. Which crops qualify (W1/W2 admitted train, HOLD/DROP train rows, v_c, other unlabelled page lines?), and what keeps it from touching benchmark/dev/test editions?
   - S3: per-row calibrated confidence. Report availability by parent: the lead knows DocAI `evidence.confidence` is present for W1/W2 and **absent for v_c rows** in census_05. Check the tags receipt `$W/scaling_w3/tags/scale1-c05-002/TAGS_RECEIPT.json` (per-field availability) and any older v2 confidence source;
   - C2: semantic or word-level targets: what the auxiliary head is trained on, whether it needs a lexicon or tokenised text, and whether labels suffice;
   - G: generator inputs (fonts, real-statistics measurements, degraded twins) and where the v5/v6 generator lives;
   - M1: the born-digital pool (E1 train partition, 19,657 rows; find it); M2: synthetic shards per fraction;
   - M3/M4: per-row class/source tags. These are probably covered by the SCALE1 tags; say so if true.
2. **Whether each exists on Clariden now**, read-only: path, row count, and sha/receipt if one exists. Say "custody: none" when no receipt binds it. Look in the repos' records and receipts first (greek-page-ocr `docs/`, toolkit worktrees' `docs/records`, `docs/harvest/**`). Then confirm on Clariden with `ls`/`stat`/`head` and small file hashes only; no multi-GB hashing.
3. **The exposure constraint** for each artefact: 0 dev/test editions, 0 benchmark 0.2 keys or crop shas. Say whether it can be met with existing receipts or needs a new audit.
4. **What a package would take:**
   - the inputs;
   - a job or none;
   - a rough size and time, as arithmetic from known sizes;
   - the dependencies (e.g. "after C1", "after S2 validated");
   - any owner/coordinator decision the spec leaves open. List these as open questions; do not decide them.

## Output
Write `docs/harvest/collect_v3_admission/scaling_w3/DATA_NEEDS.md`, short:
- one section per family;
- a summary table at the top: family | artefact | exists? | custody | exposure audit | package effort | blocking decision.

Numbers and citations only, no recommendations beyond "what it would take". Do not touch any other file. Write a guarded commit list (this file + this brief). Do not run `git add` or `git commit`.

The last line must be exactly:
`DATA_NEEDS: done | families <n> | artefacts <k> (exist <a>, with custody <b>) | open decisions <m> | no builds, no jobs`
