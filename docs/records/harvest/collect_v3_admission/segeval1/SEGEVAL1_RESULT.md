# SEGEVAL-1 result after SEGEVAL-2

Finalised 19 October 2026 from the two existing blind reads (05:03–05:10 UTC). Both contexts are **VALID under canonical v4.5.5**, with zero violations and manifest checks enabled. No new reads, model launches, network access, or pixel adjudication were performed in SEGEVAL-2. Recorded reader turn contexts confirm `gpt-6.1-sol`, `medium`, and `network_access=false` for both reads.

**False positives: 29/50 rejects (58%). False negatives: 5/100 accepts (5%).** All ten controls pass (5/5 in each context). These counts reproduce the v4.4 results; the canonical rescan changes custody, not answers or scoring semantics. No numerical proceed threshold was supplied; owner acceptance remains undecided.

A false positive is a pipeline REJECT whose four owner rubric answers are all `no`. A false negative is an ACCEPT with any `yes`. An uncertain-only answer is unresolved and remains in the sampled denominator; it is not counted as a confirmed error or success. The rubric assesses neighbour whole words, multiple complete lines, orientation, and final-letter horizontal clipping. Transcription errors and `crop_ok` do not replace that rubric.

## False positives on rejects

| Verbatim rejection reason | FP / sampled | Rate |
|---|---:|---:|
| A second complete printed line is visible. | 1/1 | 100.00% |
| Too little OCR output for the text box after height normalisation. | 12/19 | 63.16% |
| Too much OCR output for the text box after height normalisation. | 15/24 | 62.50% |
| Top and bottom padding together exceed 1.5 target-line heights. | 1/6 | 16.67% |

The two OCR-length rules together contribute **27/43 (62.79%)**. These are the exported policy reasons, not newly recomputed length tests. The remaining two confirmed FP are 1/1 second-line and 1/6 padding. Overall reject outcomes: 29 fine, 19 flagged, 2 unresolved. These are sample estimates from an unstratified random draw, not exact population error rates; reason cells, especially n=1, are small.

## False negatives on accepts

| Owner rubric | Flagged accepts / 100 |
|---|---:|
| Whole neighbour word | 1/100 |
| Two complete lines | 0/100 |
| Rotated or vertical | 0/100 |
| Horizontal final-letter clipping | 4/100 |

Rubric counts may overlap; the unique false-negative count is 5. Accept outcomes: 94 fine, 5 flagged, 1 unresolved. Exact flagged rows and saved reader explanations:

| Row ID | Saved reader explanation |
|---|---|
| `30fff481-p000044-l0054` | Final iota of Οι is cut at the right edge. |
| `gazette_modern--3f76a65cf28046c3--s000-l0040` | Following line has readable words and digit bodies, but is vertically incomplete. |
| `gazette_modern--7f13295b2aeb94d7--s000-l0115` | Right boundary cuts the final rho of Νομαρ. |
| `7bd6c40b-p000040-l0023` | Right boundary cuts the final iota/punctuation of Όχι. |
| `8961f6bdd6daf004b4a84dfa-p000092-l0011` | Final η clipped at right edge. |

## Unresolved

Two rejects and one accept remain unresolved. If all uncertain cases were eventually counted as errors, FP would be 31/50 and FN 6/100; these are sensitivity bounds, not adjudicated scores.

| Row ID | Pipeline decision | Saved reader explanation |
|---|---|---|
| `gazette_modern--70dafa4f769a0d6a--s000-l0074` | ACCEPT | Only fragmented lower portions of the target glyphs are visible; final-letter boundary is indeterminate. |
| `gazette_modern--5158b7bf9def2bab--s000-l0012` | REJECT | Isolated vertical stroke; orientation cannot be established. |
| `gazette_modern--13a9303cfc83a9d4--s000-l0045` | REJECT | Tiny irregular glyph; no reliable orientation cue. |

The sampled population excludes pipeline UNCERTAIN/HOLD. The separate post-exclusion population has 151,645 such rows (`unresolved_population.json`); these three reader-uncertain study answers do not estimate errors in that population. See `HANDOFF.md` for original draw, exclusions, controls, and policy identity. Its preparation-only statements are historical and are superseded by these read/scan results.

## Scan custody

The canonical source is `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py`. SHA256 `e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1` matches its `HANDOVER.md`. The file was executed directly, without a local fork or skipped manifest check. `scan/v4.5.5/*/r1.custody.json` records executable, command, timestamp, scanner dependency hashes, handover hash, manifest hash, original closure hash, and unchanged answer/rollout hashes. Scanner success audits recorded inputs/outputs and provenance; it is not independent OS isolation proof.

| Context | Saved v4.4 | Canonical v4.5.5 | Violations | Matched returned images |
|---|---|---|---:|---:|
| segeval1_a | VALID | VALID | 0 | 85 |
| segeval1_b | VALID | VALID | 0 | 91 |

Original v4.4 scans/custody remain at `scan/segeval1_{a,b}/`; previous scoring outputs are preserved in `scored/v4.4/`. `scan/verdicts.json` records the side-by-side verdicts and hashes. No intermediate v4.5.x SEGEVAL-1 receipt was supplied; no intermediate verdict is inferred. No context is VOID, so no fresh-ID repack is required or prepared.

### segeval1_a

Rollout: `/Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/19/rollout-2026-10-19T05-03-31-01a151e6-51ce-7c13-9c62-48cdf4274e12.jsonl`

- Rollout SHA256: `c692e9f3a803c21d8decd8b77940d1c86756462e8649ab3c0d2085bbf3dcac22`
- Answer SHA256: `3fd2110ef2de2f220ff6ccc3cc6a4a8f2587d196a4cb18a4d9cd2cc2a9e19d55`
- v4.5.5 scan SHA256: `49731283dc0be2456cf2f2ee4d09e4bb290a6c1909169fc8b3b87a3a0abdbd2c`
- Manifest SHA256: `c9926e44c6f26bc18db28501687c0e30b79d00cd32a5b716542316dd0f52bdb9`

### segeval1_b

Rollout: `/Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/19/rollout-2026-10-19T05-06-48-01a151e9-52de-7693-96d1-990d345f3b06.jsonl`

- Rollout SHA256: `6d1226507825a82d1fa3706941480007d2bc186d47c12b7af1e0eb7fcbd0df81`
- Answer SHA256: `a9a9105780477bbcf70e7adbf0bbc5d22db8633b7643d810814b42609482f418`
- v4.5.5 scan SHA256: `39ab1c7724bb0fe9f62467e918c6d78116e029828b714126133cbdb170cc3364`
- Manifest SHA256: `76ce4d9d57dc9d16501251388142054157f67dbb6e2aa570a870d28c233bda82`

## Reproduction and validation

Run `tools/segeval2_rescan.py` with the existing collector virtualenv Python (Pillow available), then run `segeval1_score.py` with `--answers-a answers/segeval1_a/r1.jsonl --answers-b answers/segeval1_b/r1.jsonl --scan-a scan/v4.5.5/segeval1_a/r1.scan.json --scan-b scan/v4.5.5/segeval1_b/r1.scan.json --out scored` from this directory. This uses existing rollout files and public pack paths; it never invokes the reader launcher.

The scorer now requires canonical v4.5.5, zero violations, enabled manifest checks, and bound scanner/rollout/manifest/answer/scan custody before loading answers for scoring. `summary.json` carries context scan verdicts and custody; every `owner_rows.jsonl` record carries its context verdict and custody. Eight scoring tests pass, including rejection of VOID, v4.4, or skipped-manifest scans. `segeval2_verification.json` verifies counts, controls, original seals/hashes, row coverage, and unchanged historical scores. No crop or answer was changed.
