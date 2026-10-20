# T6e: per-line ownership label maps for the L1E masking sample (gpt-6.1-sol, xhigh, network OFF, nice, ≤ 45 min)

**Build and test only.** I execute the run; your sandbox cannot write `~/Projects/collect-v3-data`. This runs in this worktree (`sol/l1e-mask`), on top of the T6d runner (latest commit), whose `WAVES` now includes vouli.

**Request (spell-check lead).** Their L1M attribution needs, per line, the per-pixel ownership produced by the masking, so they can tell whose ink sits at the crop border. Today the records hold only counts.

## Add an opt-in `--export-ownership` to `docs/records/harvest/recut_v1/l1e_sample/run.py`

Masking itself (`foreign_ink.py`) is **unchanged**: params `801d517e`, library `f203504a` (the hash checks stay). Reproduce its internal sets to build the export:
- the `_foreign_mask` keep and ink sets;
- the ring abstentions.

The cleanest way is to call the same internal functions on the same inputs. Do not modify `foreign_ink.py`.

Per line, write `ownership/<wave>/<doc>/<crop-stem>.png`: an 8-bit label map aligned exactly to the crop rectangle, with these values:

| Value | Meaning |
|---|---|
| 0 | background (not ink) |
| 1 | own ink: ink kept by `_voronoi_keep` for this line |
| 2 | masked; the component belongs to the detector row **above** this line |
| 3 | masked; the component belongs to the detector row **below** this line |
| 4 | masked; the component belongs to **no** detector row (unassigned specks or blobs) |
| 5 | foreign by Voronoi but **left unmasked** (empty background ring) |

How to assign:
- Use the existing audit ownership: the detector component rows prepared by `prepare_audit_rows`.
- A component owned by any other row that is neither the immediately-above nor the immediately-below row gets value 2 or 3 by its vertical side, and the record says which row.

Per line, add to `lines.jsonl` a `components` list: component id, class value, pixel count, owner row id or null, side.

Checks:
- **The union of values 2, 3 and 4 must equal the applied mask exactly** (mask_sha256 matches), and value 5 must equal the abstained set.
- **The masked crops must be byte-identical** to the corresponding T6d r3 / vouli outputs. Pass the earlier output dir as `--compare <dir>`; mismatches fail loudly.

## Test
Test on 5 of the 200 ids: compare against `~/Projects/collect-v3-data/v2_masked/l1e_sample_r3` (read-only), writing to a git-ignored test-out. Add unit tests for the class-union invariant and the PNG alignment.

## Hand-off
README lines with the two exact commands I run:
1. the 200 ids, written to `~/Projects/collect-v3-data/v2_masked/l1e_sample_r4`, with `--compare …/l1e_sample_r3`;
2. the vouli 60 (`~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_masking_sample_ids_vouli.txt`), written to `…/l1e_sample_vouli_r2`, with `--compare …/l1e_sample_vouli`.

Commit with a helper that excludes ignored paths. The last line must be exactly:
`T6e: done | export ready | test 5 lines: union==mask <ok> crops identical <ok> | tests: <n> passed`
