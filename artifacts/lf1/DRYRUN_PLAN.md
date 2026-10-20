# LF1 dry run — lead-operated, build only

Built 2026-10-20 00:02:45 EEST. No reader contexts or probes ran. Two contexts contain 50 bed + 6 controls each (56 + 56 cards, 12 control presentations). The 100 bed lines are distinct and all carry explicit owner ratings: 58 KEEP, 42 DROP. Controls are not scored as bed lines.

## Before the reader contexts: required lead pixel review

The frozen pool is `keys/control_pool.json` (SHA256 `c8027c47dbdb1284f00c9ed89ea801b2ceeba9d87344a5b9f8954447039dfc18`). These are **constructed controls**, made from one saved SEGEVAL1 clean line; no new reading was performed. Its source ID is outside the entire 888 calibration cohort. Expected results derive from the stated constructions, pending the lead's pixel check. They are not newly asserted owner truth. If a construction does not demonstrate its listed fault, do not approve it; rebuild the pool and packs with a new receipt before running.

| Pool ID | Native control crop for the lead | Expected | Construction |
|---|---|---|---|
| `lf1-control-ok` | `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs/control_pool/img/0c9299b271d20effe58efedcf0e1ebd033ba5026c2623c35999ef3ae2eab3a18.png` | OK  | unchanged saved clean line |
| `lf1-control-multiline` | `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs/control_pool/img/f82cd0d82ffba461223734fff2169822b9a3ae9e79aa715e7c1c3e1823bdbc7e.png` | CROP_VIOLATES one_central_line, other_complete_line, gt2_whole_neighbour_words | two full copies appended vertically |
| `lf1-control-omitted_span` | `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs/control_pool/img/0c9299b271d20effe58efedcf0e1ebd033ba5026c2623c35999ef3ae2eab3a18.png` | CROP_VIOLATES text_ne_visible_line | label omits final stored word; pixels unchanged |
| `lf1-control-turned` | `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs/control_pool/img/c042ad5d403b95f07691a258346b707b372d9e289ea9044b45ccf6c71b8f5dc3.png` | CROP_VIOLATES turned_or_clipped | native line turned 90 degrees |
| `lf1-control-clipped` | `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs/control_pool/img/540f41d4623d773f7e10355cbd6fed71f7ecc2bfc12f81669cff01fa12b63914.png` | CROP_VIOLATES turned_or_clipped | upper half removed through target glyphs |
| `lf1-control-textdiff` | `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs/control_pool/img/0c9299b271d20effe58efedcf0e1ebd033ba5026c2623c35999ef3ae2eab3a18.png` | TEXT_DIFFERS  | first label base letter replaced with X; pixels unchanged |

The lead records the pixel review outside the packs, at `artifacts/lf1/keys/control_pixel_review.json`, with this schema after actually checking all six crops:

```json
{"pool_sha256":"c8027c47dbdb1284f00c9ed89ea801b2ceeba9d87344a5b9f8954447039dfc18","approved_pool_ids":["lf1-control-ok", "lf1-control-multiline", "lf1-control-omitted_span", "lf1-control-turned", "lf1-control-clipped", "lf1-control-textdiff"],"reviewer":"<lead>","reviewed_at":"<timestamp>","notes":"<pixel evidence>"}
```

This review file was deliberately not created by the builder. The runner enforces HANDOVER §4's pre-run lead pixel check; it does not ask a reader to find its own controls. Control images are stored under `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs/control_pool/img/`; only public card fields and byte copies enter the reader contexts.

## Commands for the lead

From this worktree, after the pixel review:

```sh
bash artifacts/lf1/RUN_ALL.sh --jobs 1
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/lf1/tools/score_dryrun.py
```

Use `--jobs 1` for the dry run so weekly meter intervals do not overlap. Production supports `--jobs 1` through `--jobs 24`; other values are refused. The prompt is supplied on stdin; nothing is added to a reader folder except reader-produced `answers.jsonl` and `zoom/**`. Every zoom must have a new name and every view path must be an explicit literal relative path. No rotation or font paths are permitted in reader zooms. No path loops or computed view paths.

The driver probes the Codex 10080-minute bucket before and after each started context. A pre-probe ≥90% refuses the context. An unavailable probe cannot authorize a start. This 90% night-plan rule supersedes the historical handover launchers' 78%/80% numbers. The owner's live dashboard wins over a probe (HANDOVER §7); the lead must stop the fleet if the dashboard reaches 90%. The builder did not probe or infer current usage. The reader uses gpt-6.1-sol, medium, workspace-write, network false, web disabled, approval never, project docs 0, multi-agent/apps/remote plugins false.

Every located reader rollout is scanned by the unmodified canonical v4.5.5 scanner (SHA `e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1`), including failed CLI contexts. VOID gets exactly one fresh directory/context with the original items/images and the same key. A second VOID is recorded and left. Receipts and both attempts remain under `artifacts/lf1/runs/`. Rerunning the fleet reads existing attempt receipts and does not grant additional retries. If a process dies before its receipt is complete, the existing attempt directory blocks an accidental restart; inspect it explicitly.

## Comparison truth and outputs

- `keys/owner_rating_truth.jsonl`: original explicit rating object and frozen `line_id`; KEEP → expected `OK`, DROP → expected `not OK`. Never use historical `reference_verdict` or a segmenter decision as owner truth.
- `keys/selected.jsonl`: all 100 immutable stored labels, source crop hashes and available quota facets. Labels came from the frozen calibration metadata or its bound population detail chunk, as S1's replay does.
- `contexts.json` and `keys/ctx01.json`, `keys/ctx02.json`: sealed opaque ID → line ID / control pool ID. Keys remain outside the packs.
- `runs/<context>.attemptN/receipt.json`: run status, rollout SHA, tokens, model/effort and pre/post probe readings; `scan.json`: canonical scan result; `mapping_receipt.json`, `verdicts.jsonl`, `unresolved.jsonl`: mapped answer custody.
- `ledger.json`: all context attempts, including VOID/refused attempts; `verdicts.jsonl`: only terminal VALID attempts. It includes controls, distinguished only by keys, not by reader-visible data.
- `dryrun_score.json`: flag rate per available quota class, overall and crop-only owner agreement, confusion table (OK / not OK / unresolved), tokens and observed weekly pp per 100 actual card reads, including retry cards. Probe tokens are present in probe receipts separately. No execution means costs remain null, not zero.

Marks and historical bsb crop_ok never decide an LF1 verdict. An optional reader transcription is stored only as evidence. Positive crop faults take precedence over text differences; there is exactly one mapped verdict per resolved card. Unknown/incomplete answers go to `unresolved.jsonl` for lead/human routing under HANDOVER §8; they do not receive an invented fourth verdict, OK, or an automatic replacement. Their context may remain scanner VALID; this does not mean all its cards are resolved. More than one control error is explicitly flagged under HANDOVER §4; the tool adds no new acceptance threshold. Review control flags before using the score or sealing anything.

The 16-class benchmark scheme is defined in main-next `docs/cleanup_20261019/POST_CLEANUP_PROGRAMME.md` §3.2, so source × script fallback was not used. Classes overlap and that document supplies no primary-class precedence. The dry-run stratification is a seeded proportional sample by the **signature of available quota facets**, not an invented primary precedence. Four selected lines have no safely bound facet and are explicitly UNASSIGNED. The score reports overlapping facets and UNASSIGNED separately. Missing language, legitimate mixed-word, font/baseline and degraded-scan evidence is not invented. This calibration exercise is not a class-complete benchmark draw. The production builder consumes P5's primary `class` verbatim.

## Production draw adapter and replacement hook

After P5 provides its draw, JSONL rows must contain `line_id`, `source`, `class`, `label` (the corrected reference), `source_crop`, `source_sha256`. The adapter makes no selection or label edits:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/lf1/tools/build_candidates.py /path/to/draw.jsonl
bash artifacts/lf1/RUN_ALL.sh --contexts artifacts/lf1/candidate_contexts.json --jobs 24
```

The candidate adapter uses 50 bed cards and six frozen controls per full context. A short final chunk still contains all six controls. Candidate folders are under the pack root's `candidates/`, separate from `dryrun/`. Supply a control pool outside the benchmark stratum as HANDOVER §4 requires; the adapter rejects exact control-line overlap. Broader stratum disjointness is the draw lead's responsibility, not inferred by LF1.

Use the replacement hook only on the lead's flagged IDs. `flagged.jsonl` has `line_id` in replacement order; drawn/overdraw JSONL have `line_id`, `class`, `source`. The overdraw file is the draw's already ordered list. Pass previously consumed replacement IDs with `--used` on subsequent invocations:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/lf1/tools/replace_flagged.py --flagged flagged.jsonl --selected draw.jsonl --overdraw overdraw.jsonl --output replacements.jsonl
```

It selects the first unused exact class+source match, records its zero-based overdraw index, or records UNFILLED. No source substitution, ranking, quota relaxation, label replacement, or extra crop rule occurs. Each replacement still requires its own LF1 card check before seal. There is no automatic benchmark sealing or remote submission in this package.

## Offline verification

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -m unittest discover -s artifacts/lf1/tools -p test_lf1.py -v
```

37 tests passed. The tests use synthetic model histories, not live readers. They cover the complete 32-row crop truth table, text mapping/mark exclusion, replacement order and exhaustion, 90% refusal without a reader call, single VOID retry, physical layout, native-pixel equality and replay, plus the SS4c heredoc montage/overwrite rejection. `receipts/ctx01.synthetic_scan.json` and `ctx02.synthetic_scan.json` are mechanical scans of fabricated direct-image returns from the sealed pack bytes, not real reader run receipts. `dryrun_score.json` currently says NOT_RUN.
