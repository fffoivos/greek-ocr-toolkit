"""Materialize the LF1 build report and lead's instructions from sealed receipts."""
import collections
import json
import subprocess
from pathlib import Path
from lf1 import BASE, PACK_ROOT, CROP_TABLE, SCANNER_SHA, rows, dump, sha

def main():
    receipt=json.loads((BASE/'receipts/build.json').read_text());contexts=receipt['contexts']
    selected=rows(BASE/'keys/selected.jsonl');pool=json.loads((BASE/'keys/control_pool.json').read_text())
    testlog=(BASE/'receipts/tests.log').read_text();import re
    count=int(re.search(r'Ran (\d+) tests',testlog)[1]);assert testlog.rstrip().endswith('OK')
    stamp=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip()
    controls='\n'.join(f"| `{c['pool_id']}` | `{c['crop']}` | {c['expected']['verdict']} {', '.join(c['expected'].get('reasons',[]))} | {c['construction']} |" for c in pool)
    py='/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B'
    plan=f'''# LF1 dry run — lead-operated, build only

Built {stamp}. No reader contexts or probes ran. Two contexts contain 50 bed + 6 controls each (56 + 56 cards, 12 control presentations). The 100 bed lines are distinct and all carry explicit owner ratings: 58 KEEP, 42 DROP. Controls are not scored as bed lines.

## Before the reader contexts: required lead pixel review

The frozen pool is `keys/control_pool.json` (SHA256 `{sha(BASE/'keys/control_pool.json')}`). These are **constructed controls**, made from one saved SEGEVAL1 clean line; no new reading was performed. Its source ID is outside the entire 888 calibration cohort. Expected results derive from the stated constructions, pending the lead's pixel check. They are not newly asserted owner truth. If a construction does not demonstrate its listed fault, do not approve it; rebuild the pool and packs with a new receipt before running.

| Pool ID | Native control crop for the lead | Expected | Construction |
|---|---|---|---|
{controls}

The lead records the pixel review outside the packs, at `artifacts/lf1/keys/control_pixel_review.json`, with this schema after actually checking all six crops:

```json
{{"pool_sha256":"{sha(BASE/'keys/control_pool.json')}","approved_pool_ids":{json.dumps([c['pool_id'] for c in pool])},"reviewer":"<lead>","reviewed_at":"<timestamp>","notes":"<pixel evidence>"}}
```

This review file was deliberately not created by the builder. The runner enforces HANDOVER §4's pre-run lead pixel check; it does not ask a reader to find its own controls. Control images are stored under `{PACK_ROOT}/control_pool/img/`; only public card fields and byte copies enter the reader contexts.

## Commands for the lead

From this worktree, after the pixel review:

```sh
bash artifacts/lf1/RUN_ALL.sh --jobs 1
{py} artifacts/lf1/tools/score_dryrun.py
```

Use `--jobs 1` for the dry run so weekly meter intervals do not overlap. Production supports `--jobs 1` through `--jobs 24`; other values are refused. The prompt is supplied on stdin; nothing is added to a reader folder except reader-produced `answers.jsonl` and `zoom/**`. Every zoom must have a new name and every view path must be an explicit literal relative path. No rotation or font paths are permitted in reader zooms. No path loops or computed view paths.

The driver probes the Codex 10080-minute bucket before and after each started context. A pre-probe ≥90% refuses the context. An unavailable probe cannot authorize a start. This 90% night-plan rule supersedes the historical handover launchers' 78%/80% numbers. The owner's live dashboard wins over a probe (HANDOVER §7); the lead must stop the fleet if the dashboard reaches 90%. The builder did not probe or infer current usage. The reader uses gpt-6.1-sol, medium, workspace-write, network false, web disabled, approval never, project docs 0, multi-agent/apps/remote plugins false.

Every located reader rollout is scanned by the unmodified canonical v4.5.5 scanner (SHA `{SCANNER_SHA}`), including failed CLI contexts. VOID gets exactly one fresh directory/context with the original items/images and the same key. A second VOID is recorded and left. Receipts and both attempts remain under `artifacts/lf1/runs/`. Rerunning the fleet reads existing attempt receipts and does not grant additional retries. If a process dies before its receipt is complete, the existing attempt directory blocks an accidental restart; inspect it explicitly.

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
{py} artifacts/lf1/tools/build_candidates.py /path/to/draw.jsonl
bash artifacts/lf1/RUN_ALL.sh --contexts artifacts/lf1/candidate_contexts.json --jobs 24
```

The candidate adapter uses 50 bed cards and six frozen controls per full context. A short final chunk still contains all six controls. Candidate folders are under the pack root's `candidates/`, separate from `dryrun/`. Supply a control pool outside the benchmark stratum as HANDOVER §4 requires; the adapter rejects exact control-line overlap. Broader stratum disjointness is the draw lead's responsibility, not inferred by LF1.

Use the replacement hook only on the lead's flagged IDs. `flagged.jsonl` has `line_id` in replacement order; drawn/overdraw JSONL have `line_id`, `class`, `source`. The overdraw file is the draw's already ordered list. Pass previously consumed replacement IDs with `--used` on subsequent invocations:

```sh
{py} artifacts/lf1/tools/replace_flagged.py --flagged flagged.jsonl --selected draw.jsonl --overdraw overdraw.jsonl --output replacements.jsonl
```

It selects the first unused exact class+source match, records its zero-based overdraw index, or records UNFILLED. No source substitution, ranking, quota relaxation, label replacement, or extra crop rule occurs. Each replacement still requires its own LF1 card check before seal. There is no automatic benchmark sealing or remote submission in this package.

## Offline verification

```sh
{py} -m unittest discover -s artifacts/lf1/tools -p test_lf1.py -v
```

{count} tests passed. The tests use synthetic model histories, not live readers. They cover the complete 32-row crop truth table, text mapping/mark exclusion, replacement order and exhaustion, 90% refusal without a reader call, single VOID retry, physical layout, native-pixel equality and replay, plus the SS4c heredoc montage/overwrite rejection. `receipts/ctx01.synthetic_scan.json` and `ctx02.synthetic_scan.json` are mechanical scans of fabricated direct-image returns from the sealed pack bytes, not real reader run receipts. `dryrun_score.json` currently says NOT_RUN.
'''
    (BASE/'DRYRUN_PLAN.md').write_text(plan)
    prompt_changes=json.loads((BASE/'receipts/prompt_lines_added.json').read_text())
    prompt_lines='\n'.join(f"| {x['line']} | {x['text'].replace('|','&#124;')} | {x['source']} |" for x in prompt_changes)
    allocation='\n'.join(f'| `{cls}` | {n} |' for cls,n in sorted(receipt['allocation'].items()))
    final=f'LF1 READY: tests {count} passed; packs 2 (cards 56+56, controls 12); dry-run lines 100 (owner-rated 100)'
    report=f'''# LF1 — benchmark last-filter builder and dry-run packs

Built {stamp}. **BUILD ONLY. No model reads, crop-pixel adjudication, probes, network calls, remote launches or .git writes were performed.** All other worktrees were read-only inputs. New writes are confined to this worktree and the requested external pack root. Synthetic tests decode/copy/transform pixels mechanically; no line was newly read or adjudicated.

## Deliverables and receipts

- [Lead run plan](../../../artifacts/lf1/DRYRUN_PLAN.md) (workspace path `artifacts/lf1/DRYRUN_PLAN.md`); entrypoint `artifacts/lf1/RUN_ALL.sh`.
- Packs: `{PACK_ROOT}/dryrun/ctx01/` and `ctx02/`, each containing only `items.jsonl` + `img/`; **50 bed + 6 controls = 56 cards each**. All 112 opaque IDs are unique, k + 10 lowercase hex. Crops are independent file copies, content-hash PNG names, with metadata removed; 100/100 native bed crops retain exactly the same mode, dimensions and pixels as the source PNG.
- `artifacts/lf1/receipts/build.json`: source paths/hashes, seed 20261019, allocation, sealed key and manifest hashes. `artifacts/lf1/keys/ctx*.json`: private ID → line ID/label/source/control bindings. No crop image was written in the repository.
- `artifacts/lf1/prompts/source_bsb.md`, `GUIDE_NOTES.md`, `lf1.md`; `receipts/prompt_receipt.json`: unchanged qualified protocol-body hash and source/prompt hashes; `receipts/prompt_lines_added.json`: every new nonblank line and provenance.
- `tools/lf1.py`: deterministic mapping table and literal replacement hook. `tools/run.py`: lead fleet, limit probes, scanner, one VOID retry, answer mapping, run receipts and ledger. `tools/build_candidates.py`: accepts a primary-class-bound corrected draw without selecting/relabeling it. `tools/score_dryrun.py`: scoring.
- `receipts/tests.log`: {count} passed. `receipts/synthetic_positive_replay.json`: confined literal heredoc ImageMagick replay passes. `receipts/synthetic_ss4c_void.json`: SS4c-shaped items-driven montage heredoc with overwritten final zoom cannot be replayed and remains VOID. The scanner was copied by hash and **not changed**. Its dependencies were copied verbatim and pinned in the build receipt.

Scanner v4.5.5 SHA256: `{SCANNER_SHA}`. Scanner tests and real-pack synthetic audits ran offline under the handover's x86_64 Python/Pillow interpreter. No canonical live-reader rollout was rescored; no reader contexts were spawned.

## Qualified prompt and owner standard

Read: Sol `HANDOVER.md` §§2–7 and its unresolved routing in §8; `prompts/bsb.md` with `GUIDE_NOTES.md`; main-next SEGEVAL1 `prompts/owner_rubric.md`; `SEGMENTATION_FILTER.md`; local `CONTEXT_20261019_spellcheck.md` rule 1; main-next `NIGHT_PLAN.md` P6 and `POST_CLEANUP_PROGRAMME.md` §§3.2–3.4.

The bsb body from “You are a blind label checker” through its final “Never open key files or anything else” is **verbatim**, including its marks/crop_ok fields and output example. Its GPT-6 non-interactive header and completion wrapper are retained/adapted only for the items/img paths and extra answer fields. The preserved cards.jsonl references are explicitly aliased to items.jsonl; no duplicate cards file is created.

The original crop_ok rejects readable neighbour characters/letter bodies, which conflicts with the current owner's allowance. SEGEVAL1 already separated independent owner questions from this stricter field, but its old single-neighbour-word question cannot implement the current >2 whole-word standard. All five current requirements are therefore explicit independent owner questions. No detector proxies (95% visibility, x-height, padding, length predictor or height guard) enter the LF1 crop verdict. The five quoted owner wordings come from this LF1 brief and are corroborated by the context rule/programme §3.4; the current brief's 100% visibility governs over SEGMENTATION_FILTER's historical detector tolerance.

Marks are recorded because the qualified body is preserved, but ignored exactly as requested. This is the qualified letters-and-crop check, not a new claim of whole-line accent qualification. Reading is evidence only; labels are never replaced. One stored label contains Hebrew letters: the input wrapper explicitly names this script-data extension beyond bsb's listed script examples, rather than mislabelling it as Greek/Latin/Cyrillic or changing the stored text. No reading qualification on Hebrew is claimed.

### Every added nonblank prompt line, with source

Line numbers refer to `artifacts/lf1/prompts/lf1.md`. Existing body lines were neither rewritten nor removed. Formatting-only blank lines are excluded from this table.

| Line | Added line | Source |
|---:|---|---|
{prompt_lines}

## Deterministic mapping (implemented and tested)

| Reader field / condition | Result |
|---|---|
| Any `owner_crop` field = yes | CROP_VIOLATES; collect every yes in table order: one_central_line, text_ne_visible_line, other_complete_line, gt2_whole_neighbour_words, turned_or_clipped |
| No positive crop fault, but uncertain crop answer or letters=u / incomplete answer | No invented verdict: unresolved receipt and lead/human routing (HANDOVER §8); never auto-OK |
| All owner crop answers no; letters=n, or errors contains wrong_letter / lookalike_script_letter / missing_word_or_span / extra_text / punctuation / hyphen / digits | TEXT_DIFFERS, with validated literal label-substring + printed span in where |
| All owner crop answers no; letters=y; no listed textual error | OK |
| marks, mark-only error types, historical crop_ok, optional reading | Evidence only; no independent verdict effect |

Crop faults take precedence over text differences. A crop extent mismatch (text beyond crop, omitted visible span, cut letters or merged lines) is the `text_ne_visible_line` question; a character substitution within the same extent is letters/errors/where. Positive crop faults take precedence over uncertainty, following gate2's saved scoring order; remaining uncertain cards require the lead. Schema/coverage checks are data-integrity checks, not extra segmentation rules.

The replacement hook consumes exactly the flagged IDs and the draw's ordered overdraw list. For each flag in supplied order it takes the next unused line of the same class and source; every outcome is recorded, including UNFILLED. Replacements are not automatically accepted or relabelled. No benchmark is sealed by LF1.

## Dry-run sample and controls

The 888 calibration crop hashes are bound to `main-next/docs/records/harvest/seg_steps/s1/crop_bindings.jsonl`. Labels and ratings are taken from the frozen review-site `box-length-experiment.json`, predicted-rows, and bound population detail chunks in the same way S1's replay loads them. All 135 explicit rating objects were found: 78 KEEP /57 DROP. The proportional seeded sample selects **100 rated lines**, 58 KEEP /42 DROP. The 753 unrated lines were not needed. The owner truth file preserves the complete rating object; KEEP → OK and DROP → not OK, independently of historical reference_verdict or segmenter output.

The benchmark-0.2 scheme **is defined** in `docs/cleanup_20261019/POST_CLEANUP_PROGRAMME.md` §3.2 (16 rows despite its older nearby “15” prose). It is used as available overlapping quota facets; source × script fallback is not used. Because primary precedence and several tag definitions are absent, sampling strata are quota-facet signatures; four selected lines are UNASSIGNED. We do not infer Cyrillic language from source or invent confidence/degradation thresholds. This is explicitly a calibration dry run, not a class-complete benchmark draw or a new primary allocation policy. The production adapter requires P5's primary class unchanged.

| Available quota-facet sampling stratum | Selected |
|---|---:|
{allocation}

Six frozen constructed controls are copied into both contexts. Together they cover OK, all five crop fault codes, and TEXT_DIFFERS. Pool keys and constructions are in `artifacts/lf1/keys/control_pool.json`; the complete native paths and expected outcomes for the lead's mandatory pixel check are listed in `DRYRUN_PLAN.md`. **Lead pixel review is pending by design.** The runner will not start until it is recorded. Existing saved SEGEVAL evidence justifies the base line; the transformations do not constitute a new owner rating or a live reader qualification.

## Lead execution and measurement

The run plan supplies the exact commands and review-file schema. The fleet accepts ≤24 concurrent reader contexts, probes before and after each start, refuses ≥90% weekly usage, runs the canonical scanner on every located reader rollout, and gives a VOID context one fresh-context retry only. A second VOID is left in the ledger. A control error count >1 is flagged as the handover requires; no additional control threshold was introduced. Prompt, key, manifest, scanner and dependency hashes are checked for custody. Network/web, plugins/apps and delegation are disabled for future readers.

Scoring reports per-class flag rate, owner binary agreement and confusion table, explicit unresolved count, plus a crop-only comparison because owner marks judge segmentation rather than label spelling. Tokens and weekly pp are normalized by all actually read cards (including controls and retries). Weekly deltas remain shared, coarse observations; concurrent intervals overlap. Use the serial dry-run command to avoid overlap, and do not interpret zero displayed movement as zero cost. No live budget/quality figures are claimed: `dryrun_score.json` is NOT_RUN and token/weekly measures are null.

{final}
'''
    root=BASE.parents[1]
    (root/'docs/labelfix/spellcheck/LF1_REPORT.md').write_text(report)
    dump(BASE/'receipts/tests.json',dict(passed=count,failed=0,log_sha256=sha(BASE/'receipts/tests.log'),
         reader_runs=0,network='OFF',synthetic_scans_only=True))
    print(final)

if __name__=='__main__':main()
