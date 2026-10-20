# W2C1b: W2 snapshot stratum packs

Prepared and validated; no readers started and no admission verdicts produced.

Input: `verified W2_features_20261018_0524.jsonl snapshot; no replay`, at
`~/Projects/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl`.
The complete 219,381-row snapshot is SHA-256 verified before sampling:
`4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4`.
No replay is used. Live run features files are never read; preparation rejects
those reads and network sockets. No live locks or writes are taken.

| Source | Class | W2 rows before filters | Eligible pool | Draw |
|---|---|---:|---:|---:|
| bsb_poly1850 | poly1850 | 8929 | 6761 | 100 |
| ia_poly1850 | poly1850 | 13641 | 9296 | 100 |
| nlg | poly1850 | 3926 | 3037 | 100 |
| nlg | poly1900 | 2869 | 2077 | 100 |
| nlg | greek_poly | 833 | 686 | 100 |
| serbia | cyrillic | 6159 | 5011 | 100 |
| elstat | numerics_tables | 10083 | 7206 | 100 |
| gazette_modern | modern_scanned | 60712 | 37584 | 100 |

BSB W2 is partial: 298 pages at snapshot time. All eight pools have at least
100 rows; each uniform draw contains exactly 100. Gazette additionally requires
`gazette_stratum == "measured_1986_1990"`; counts before filters include all
Gazette modern_scanned rows, and the eligible pool applies this field gate.

Pools require W2, the specified source/class, candidate_usable true,
screen_merged false, and absence from every registered release exclusion class.
Rotated crops are excluded when height > width with at least four non-space
label characters. SEG screens are being qualified separately under CP7; these
letters and crop_ok checks do not wait for SEG. No new SEG filters are added.

Original crops are copied. Missing crops are regenerated from retained source
rasters only through `collect_v3.storage.ensure_crop`, using exclusively
`~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, into this task's
`cache/`, outside the live run. Every source and copied crop matches the
snapshot crop SHA-256; custody is recorded in `keys/crop_custody.json`.

Seed: `w2c1:<source>:<class>`, uniform sampling over rows sorted by id; context
order adds `:order:c1` or `:order:c2`. Eight beds, two disjoint contexts each,
50 bed cards + five approved CAPS1/CAPS1b controls per context. All 10 lead
controls are reused per bed. Fresh opaque ids and public closure are verified.
Keys, truth, pool/draw inventories and custody stay here, outside PACK_ROOT.
PACK_ROOT: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs`.

`prompts/bsb.md` is copied verbatim from Sol-reading; only its reader-2 template
placeholder is rendered empty for independent one-reader contexts.
Canonical scanner: `tools/scan_rollout.py`, SHA-256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`, invoked directly
without scanner wrappers. Every prepared and executed run receipt records this
hash. Canonical replay helper is unchanged; closure uses the CAPS1 grayscale
and disjoint-context adapter. Manifests live beside the reader directories.

The lead can run `bash /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/w2c1/launch_all.sh` after reviewing READY.json.
It runs all 16 contexts sequentially and logs to `run.log`. Before every
context, `launchers/limit_probe.sh` must yield exactly one weekly 10080-minute
bucket. Use >=78%, missing or ambiguous readings stop with exit 8; the bed
launcher probes before and after as well. `launch_lines.txt` has the 16 public
launch lines. Preparation and tests never call the real probe or reader.

Reader settings: gpt-6.1-sol, medium, network OFF, web disabled,
apps/plugins/multi-agent OFF. Receipts retain rollout, usage, limit readings,
scanner hash and audit/map return codes. More than one control error flags a
context. Letters and crop_ok are the final Sol dimensions; marks remain pending
Opus for grave-heavy strata. No check scores or admission outcomes are claimed.

Validation: 64 tests passed, zero skipped. Coverage includes exact pool
filters, eight seeds/order, crop SHA equality, all 16 context closures, scanner
hash/direct invocation, prompt/settings, snapshot SHA/count verification and
rejection of corrupt bindings, and shell stop-rule execution with fake probes
and readers. See `tests.log`, `tests.xml`, `closure.json`, `build_receipt.json`,
`runtime_bindings.json`, and `READY.json`. The real launcher has not been run.

W2C1b: done | strata: 8 | pools: bsb_poly1850_poly1850=6761, ia_poly1850_poly1850=9296, nlg_poly1850=3037, nlg_poly1900=2077, nlg_greek_poly=686, serbia_cyrillic=5011, elstat_numerics_tables=7206, gazette_modern_modern_scanned=37584 | contexts: 16 | READY.json written | canonical scanner sha ok | launch_all ready | tests: 64 passed
