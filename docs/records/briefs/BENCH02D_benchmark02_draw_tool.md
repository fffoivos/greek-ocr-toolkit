# BENCH02D: benchmark 0.2 draw tool, with a dry run (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Context (night plan step P5):** benchmark 0.2 is drawn from collect-v3 W1/W2 **admitted** rows of census_05.
- **Test** comes only from SPLIT1 **TEST** editions; **dev** only from SPLIT1 **DEV** editions. So training loses nothing beyond the split.
- census_05 has not run yet. Build the tool now, test it, and dry-run it on census_02 data so that it runs the moment census_05 lands.
- The design is the programme doc §3 (`~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/POST_CLEANUP_PROGRAMME_20261019.md`, read §3.1–3.3 in full) and the night plan P5 (`~/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/NIGHT_PLAN.md`). Where this brief and §3 differ, §3 wins; report the difference.

**Rules:**
- A tool is exactly the stated rules. Any extra filter or guard goes into the report as a diagnostic, never into the draw.
- Deterministic and seeded. Athens time from `date`. No pushes. No ssh.
- Read-only: everything outside `docs/harvest/collect_v3_admission/bench02/`.

## Inputs
1. **Census decisions** (`line-filter-decision-v1`, one row per line).
   - Fields: `binding.{id,parent_id,split,crop_sha256}`, `admitted`, `disposition`, `reasons`, `expectations.{classes,orthography,scripts,languages}`, `final_inventory` (letter counts, scripts, mixed_words, latin_words…), `final_text`, `routes.*`, `stages[]`, and `evaluation_diagnostics.jsonl` (per-row evidence, same keys).
   - The full files are about 8–9 GB on Clariden, so the tool has **two stages**:
     - **`extract`** streams decisions + diagnostics and writes a slim per-row tag file (`tags.jsonl.gz`) for W1/W2 rows only. It runs on Clariden as a CPU job the coordinator submits; write `extract.sbatch` (account a0140, a CPU partition, no GPU) but do not submit it.
     - **`draw`** runs anywhere from `tags.jsonl.gz` + the split + the snapshots.
   - **Dry-run sample:** `~/Projects/collect-v3-data/census02_sample/{decisions,evaluation_diagnostics}_{W1,W2}_2000.jsonl.gz` (census_02, 2,000 rows per tranche each; shas in `SHA256SUMS.txt`). Note the two files were grepped separately: join by (parent_id, row_id) and report the join rate.
2. **Split:** `docs/harvest/collect_v3_admission/split2/row_split.jsonl.gz` (SPLIT2; if not there yet, use `split1/row_split_proposal.jsonl.gz` with `proposed_split` as the split — the owner adopted it unchanged) + `split2/edition_map.jsonl` / `split1/editions.jsonl` for edition, gazette issue and series.
3. **Row features:** `~/Projects/collect-v3-data/snapshots/{W1,W2}_features_20261018_0524.jsonl` (sha in `SHA256_20261018_0524.txt`). These give source, class, bbox/crop size, Google confidence and text, for tags the decisions lack.
4. **Exclusions:** the v2 train/dev/test documents (`~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_{train,dev,test}.jsonl`) and the locked eval sets (sol-collect `docs/harvest/collect_v3/release_exclusions/release_exclusions.json`). SPLIT1 already forced these editions to test. §3.3 still excludes any edition that appears in v2 or a locked set: apply it and report how many forced-test editions it removes from the pool.

## Classes and tags (§3.2)
Assign each row its tags and **one primary class**, by a fixed, documented precedence. The 16 quota classes and their test quotas (dev = ¼) are:

| Class | Test quota |
|---|---:|
| Monotonic ordinary | 240 |
| Polytonic ordinary | 360 |
| Polytonic dictionary/journal (bsb/ia poly1850) | 160 |
| Latin | 160 |
| Legitimate Greek–Latin | 160 |
| Historical Russian | 120 |
| Modern Cyrillic (ru/sr/bg/uk, 40 each) | 160 |
| Numeric/table cells | 200 |
| Short (≤12 letters, non-cell) | 120 |
| Long (≥60 chars) | 160 |
| Vertical/turned | 100 |
| Caps/letter-spaced headings | 120 |
| Leaders/dashes/punctuation-heavy | 100 |
| Small/large fonts (50/50) | 100 |
| Degraded | 100 |
| Curved/skewed | 100 |

- Use the tag sources named in §3.2's third column.
- Where the census evidence for a tag is not in the data (e.g. x-height, turn flag, curvature), say exactly which field is missing, mark the tag `unavailable`, and leave the class unfilled in the dry run. Never substitute a guess.
- Secondary facets are tagged and reported, not counted.

## Draw rule (§3.3, exactly)
- Within each class: group by source, then by edition; round-robin across sources, then across editions.
- Caps: at most **4 lines per edition**, at most **12 per book series** (gazette issue = edition; series per editions.jsonl).
- Seeded by `bench02:<split>:<class>`.
- **20% overdraw:** draw 1.2 × quota as ordered candidates (rank 1..n), so that P6 replacements come from the same class + source in order.
- Report deficits; never fill a deficit with lines from another class.
- Test from TEST editions, dev from DEV editions.
- Admitted rows only. In the census_02 dry run no W1/W2 row is admitted (all HOLD, `split_or_edition_identity_unresolved`). The **dry-run pool** is therefore the W1/W2 rows whose **only** reason is that split reason. Label it clearly as the pre-filter supply.

## Outputs (`docs/harvest/collect_v3_admission/bench02/`)
- `bench02_draw.py` (`extract` and `draw` subcommands), `extract.sbatch`, `test_bench02_draw.py`.
- Per draw run (`dryrun_census02/` now, `census05/` later):
  - `candidates.jsonl`: split, class, rank, parent_id, row_id, edition_id, source, series, tags, crop_sha256, final_text;
  - `draw_plan.json`: seed, order, caps, quotas, input shas, precedence table, code sha;
  - `counts.json` + `COUNTS.md`: class × source × edition counts, deficits, the edition and series cap hits, and the supply per class.
- `BENCH02D.md`:
  - the exact census_05 commands (extract on Clariden, then draw);
  - the tag availability table (field → present / missing in census_02);
  - the dry-run result;
  - the open questions.

## Tests
- Determinism (same seed → identical candidates).
- Caps never exceeded.
- Test candidates only from TEST editions and dev only from DEV.
- No v2 or locked edition drawn.
- Overdraw = ceil(1.2 × quota) where supply allows.
- Primary class unique per row.
- `extract` on the sample gives the same tags as the in-memory path.
- No writes outside bench02/.

Write a guarded commit list (bench02/ code, tests, docs, the dry-run outputs if ≤ 5 MB, this brief). The last line must be exactly:
`BENCH02D: done | dry run census_02 sample: pool <n> rows, classes filled <k>/16 (test) <j>/16 (dev) | tags unavailable <list> | extract.sbatch ready | tests: <n> passed`
