# R1 — Purpose-built mark reader: scripts, mock, deployment check (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-r1`, branch `opus/spellcheck-r1`). No `.git` writes; leave files in the
working tree; the track lead commits. Do not touch other worktrees (another Sol run, S5, is editing `~/Projects/greek-ocr-toolkit-spellcheck`).
Local Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` with `PYTHONPATH=$PWD`. The MacBook is not a bulk
worker: local runs = the 192-crop mock plus the held-out extraction of the 666 held-out lines only.

**DO NOT SUBMIT A JOB.** You prepare, mock, deploy, sha-check and run `sbatch --test-only`. The coordinator sha-compares and submits.

## The design (approved; read it first)
`docs/records/labelfix/spellcheck/clariden/R1_mark_reader_outline.md`: per-letter reader, crop = the full-height line window from 1.5 line-heights
left to 0.75 right of our recogniser's CTC span of each vowel/ρ, resized 64×128 grey + a span-mask channel, plus the recogniser base letter
(marks stripped, case kept) as a 64-d embedding. Four factorised heads (breathing none/psili/dasia; accent none/acute/grave/circumflex;
dialytika 0/1; subscript 0/1). Small ResNet (32/64/128/192, 2 blocks per stage) ≈ 1.6 M params, bf16. Labels = agreement words (Google
NFD core == recogniser NFD core, case + marks) in the C1 lines only. No ink.py, no x-height fit, no Google letters at inference.

Inputs: C1 selection `.cache/labelfix/clariden/C1_selection.jsonl` (91,469 lines, 316 docs), alignments
`.cache/labelfix/clariden/C1_alignments.jsonl.gz`, crop inventory `.cache/labelfix/clariden/C1_crop_inventory.jsonl.gz`, C1 scripts
`scripts/labelfix/clariden/c1_*.py` + `c1_job.sbatch` (reuse their style, Clariden paths, runtime.sh, E3 venv `torch 2.11.0+cu128`, scratch
`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`, staged crops `.../collection_v2/crops`), `docs/records/labelfix/spellcheck/clariden/C1_REPORT.md`.
Local crops for the mock: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/` (read-only). Labels/tokenising:
`greekocr/labelfix/candidates.pair_tokens`, `markshape.mark_class`, `text.clusters/nfd`.

## RESTART NOTE (22:05) — owner rule overrides the outline's column filter
A first attempt was stopped at 22:03; its partial files are in the working tree (`scripts/labelfix/clariden/r1_*.py`, `artifacts/`,
`R1_heldout_extraction.log`). Reuse what is sound, but CHANGE the slot filter:

The owner (16 Oct, after reviewing the S4 pages): "if you are detecting letters with no gap heuristic you need to reconsider because this
causes problems — you need to consider font size." His notes show touching letters fused into one blob ("fused letters at 33", "3 letters
fused at 15 and missed accent there", "τυ merged", "15 is 2 letters") and accents whose ink merges with the letter ("care is required to not
detect within the height of letters since the ink of accents and chars are merged"). Therefore:
- NO gap / column-profile / connected-component test decides whether a letter is usable. Remove `letter_columns` /
  `column_competing_owners` as a filter. Fused letters are exactly the cases we must cover.
- A slot is usable when its CTC span is plausible for the line's FONT SIZE: estimate the line's letter size from the pixels (x-height or
  stroke-height of the line, robust to capitals/ascenders) and from the median CTC span width of the line; drop a span only if its width is
  outside a stated range of that size (e.g. < 0.2× or > 2× the median letter width), plus line confidence ≥ 0.5. State the rule and the
  numbers in the receipt.
- The crop window is scaled by that font size (not by the crop height alone, which varies with line spacing); keep the outline's margins
  in font-size units (≈ 1.5 letter heights left, 0.75 right, full mark zone above and below).
- Coverage (condition 2) = fraction of held-out vowel/ρ slots passing THIS rule; also report how many held-out slots are fused (more than
  one recogniser character over one connected component) and the reader's scores on them separately.

## Coordinator's seven conditions (binding)
1. **Disjointness verified, not assumed.** The extraction receipt lists the C1 document ids ∩ {14 held-out Wikisource books, 3 DEV books,
   document ids of v2_test, wikisource_human and e1_real_test} and the line-id intersections too, printed as counts; all must be 0. Test-set
   files: `docs/records/harvest/collection/v2/import_real_v2_test.jsonl`, `~/Projects/greek-page-ocr/out/e3b/predictions/full_s0_v2_test.jsonl`,
   `full_s0_wikisource_human.jsonl`, `full_s0_e1_real_test.jsonl`; book lists in `C1_selection.summary.json`.
2. **Coverage is a reported number.** On the 666 held-out lines: the fraction of vowel/ρ slots the reader can score at all (span overlaps
   exactly one letter column, recogniser line confidence ≥ 0.5). Scoring (later, on the Mac, by the track lead's instrument) gives two
   tables: on scored slots, and on all slots with unscored counted as "none". Your job: extract the held-out samples locally (666 line crops,
   cached alignments `.cache/labelfix/align_s0.jsonl`; same extraction code), record coverage, ship them as a small shard with the deployment,
   and write `scripts/labelfix/clariden/r1_score.py` that maps the job's per-sample predictions back to `reading.recogniser_slots` slots and
   scores them against print truth exactly as `scripts/labelfix/s4_validate.py` does (same 666 lines, same per-slot truth), producing both
   tables plus the owner-note checks. Mock-test r1_score.py on the mock predictions.
3. **Job:** `--partition=normal`, `--time=03:00:00`, account a0140, one node, 4 GPUs (coordinator's explicit choice for this job). Every
   epoch: save the best checkpoint (by validation loss) and append `train_log.csv`; a per-arm `DONE` marker at the end, so a timeout still
   leaves a result. Extraction writes its own receipt (counts, class histogram per head and composed, coverage/filter losses, shard sha256)
   BEFORE training starts; training refuses to start without it.
4. **Receipts in the E3 driver's style** (`~/Projects/greek-page-ocr` E3 runs; look at their run_binding.json / data_provenance.json):
   `run_binding.json` (source commit placeholder filled by the track lead, file sha256s, shard hashes, recipe per arm),
   `data_provenance.json`, per-arm held-out predictions as jsonl + receipt, and a `RESULT.md` template that r1_score.py fills with the S4/S5
   table plus the five arms side by side. Nothing stays only in a log.
5. **Compute check in the mock:** measure forward+backward samples/s on the Mac CPU for arm A's model at the real input size, print it, and
   state the GPU assumption behind ~35 min/arm (15 epochs × ~2 M samples at ~15k samples/s/GPU). If the measured CPU rate implies the GPU
   assumption is off by > 3× (state your reasoning, e.g. a FLOPs estimate per sample vs GH200 bf16 throughput, and the data-loader rate),
   set epochs to 8 and say so.
6. **Five arms:** A = full (balanced per head, rare/compound ≥ 5% of batch, "none" downsampled to 40%); B = no letter embedding; C = narrower
   left window (0.75 line-height); D = natural class frequencies; **E = A but the "none" class at its natural frequency (~60%), balanced for
   the rest**. Four GPUs: A then E sequentially on GPU 0; B, C, D on GPUs 1–3. All within the 3 h limit.
7. **Data = the 91,469 C1 lines only.** No extra alignment job.

Also: document split 300 train / 16 validation by doc (seed 20261016); filters = span overlaps exactly one letter column (from the alignment
and a pixel column profile, no ink.py) and line confidence ≥ 0.5; extraction on the node with CPU multiprocessing from the staged crops
into uint8 shards (≈17 GB scratch).

## Before the coordinator submits (you do these)
- Mock: the EXACT job entry points on 192 C1 crops on the Mac CPU (extraction + 50 training steps per arm config, + r1_score.py on mock
  predictions). Log to `docs/records/labelfix/spellcheck/clariden/R1_mock.log`; print samples/s.
- Unit tests in `tests/labelfix/test_r1.py` (label derivation on agreeing/non-agreeing word pairs, compound composition, window geometry,
  disjointness check failing on a planted overlap). All labelfix tests green.
- Deploy to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/` (scripts, code, selection, held-out shard; NOT crops — they
  are staged already; verify they are all present against the C1 inventory). Write `R1_DEPLOY_SHA256.txt` (remote vs local, all match).
- `sbatch --test-only --parsable scripts/labelfix/clariden/r1_job.sbatch` on Clariden → `R1_sbatch_test_only.txt`.
- CSCS cert: `ssh-keygen -Lf ~/.ssh/cscs-key-cert.pub | grep Valid` (valid to 2026-10-17 19:18). If ssh fails, STOP and report; never
  refresh. Read `~/.claude/skills/optimize-apertus-cscs/SKILL.md` "Clariden operating rules" before touching the cluster.

## Deliverables
`scripts/labelfix/clariden/r1_*.py` + `r1_job.sbatch`, tests, `docs/records/labelfix/spellcheck/clariden/R1_REPORT.md` with: disjointness counts,
held-out coverage, mock result + CPU samples/s + GPU assumption + chosen epochs, deployed-file sha256 list, test-only output, the exact
submit command for the coordinator. Last line:
`R1 READY: mock ok (<n> crops, <samples/s> CPU); coverage <x>% of held-out vowel/ρ slots; disjointness all 0; deploy sha256 <k>/<k> match; test-only <output>; epochs <n>`.
