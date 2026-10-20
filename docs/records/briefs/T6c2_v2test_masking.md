# T6c2: v2_test masking (all waves except parliament) + per-wave paired harm test (gpt-6.1-sol, xhigh, network OFF, nice ≥ 15, ≤ 90 min)

**Build and test only.** I execute the full run myself, because your sandbox cannot write `~/Projects/collect-v3-data/`. This runs in this worktree, `sol/recut-v1`, on top of 414ab0b7.

## Coordinator ruling
- Mask v2_test for **every wave except parliament**.
- Use **T6a2 semantics exactly as frozen**: params `801d517e…`, library `f203504a…`.
  - Nearest-curve match, which is T6a2's own matcher.
  - **Unmatched lines are left unmasked and flagged per line.**
  - Ambiguous lines are recorded per line, with the candidate count, but still masked with the nearest curve, as T6a2 does.
- **The pilot's zero-ambiguity rule is retired in favour of the harm test.** The receipt must say so.
- Parliament waits for a separate matching fix, which the coordinator takes to the owner.

## Build
`docs/records/harvest/recut_v1/v2_test/run.py`, adapted from `v2_pilot/run.py`. Same safety:
- frozen-hash checks;
- nice ≥ 15;
- a disk watchdog at 10 GB;
- no W1 locks;
- the originals untouched.

**Population.** All v2_test lines: `import_real_v2_test.jsonl` minus the 1,991 codec-rejected lines. Take that exclusion list from the E3 instrument definition; locate it and bind its hash. The resulting population is 42,038 lines on 995 pages. **Drop wave parliament.** Report the line and page counts per wave.

**Parallelism.** Page workers capped by memory:
- **≤3 concurrent when the page is above 20 MP;**
- ≤6 otherwise.

Use one fresh process per page. A page-level failure records and continues; it is never silent.

**Output root.** Default `~/Projects/collect-v3-data/v2_masked/v2_test/`. Masked crops go under `crops/<wave>/<doc>/<file>.png`, beside nothing else; the originals stay in place. Also write a `lines.jsonl` per line with:
- id, wave, page;
- original / stored / masked sha, and the re-cut pixel equality;
- match status: matched / ambiguous (n candidates) / unmatched;
- whether the mask was applied;
- masked pixel and component counts;
- fill statistics;
- changed.

**Import.** Build the import `real_v2_test_masked` in the same format as the existing v2_test import used by E3/E4. Apply the same 1,991 exclusions and the same codec. Masked crop paths replace the crop paths; unmatched lines point to their original crops. Bind hashes. Never overwrite existing eval crops or receipts.

**Harm test (the gate).** `harm.py` runs on a **10k seeded subset**, stratified by wave, with E4 ctrl_s0 `~/Projects/greek-page-ocr/out/e4/wave1a/job01/runs/ctrl_s0/best.pt` on CPU. Use the same evaluator path and adapter as T6a2's harm test. Report:
- paired CER, original vs masked, **per wave**;
- the same per script class;
- line and page-cluster bootstrap 95% CIs;
- a check that unchanged crops give identical predictions;
- the ambiguous / unmatched counts per wave.

The gate rule: CER must not get worse overall, with per-wave results reported either way.

## Test
Run the full pipeline on **2 pages per wave**: round1, round2, mixed, vouli, openarchives, cyrillic, wikisource. Write to a git-ignored test-out inside this worktree. Run `harm.py` on those lines (a small n is fine for the test). Add unit tests for the population (parliament excluded, 1,991 excluded, counts), the memory cap and the default out-path being outside the checkout.

## Hand-off
Write `docs/records/harvest/recut_v1/v2_test/README.md` with the exact two commands I run: the masking run, then the harm test. Include the expected wall time from your test timings, extrapolated to roughly 680 non-parliament pages.

Commit with a guarded helper that excludes ignored paths. Run it under nice, and allow retry if a sandbox Git failure occurred. The last line must be exactly:
`T6c2: done | runner+harm ready | population: <lines>/<pages> excl. parliament | test: 14 pages ok | est wall: <h> h | tests: <n> passed`
