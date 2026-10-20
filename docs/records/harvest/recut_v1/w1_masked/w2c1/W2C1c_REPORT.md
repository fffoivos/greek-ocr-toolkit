# W2C1c: VOID diagnosis, replacement packs and partial scoring

Four contexts repacked; no reading run, limit probe or network call executed.
[W2C1_RESULTS.md](W2C1_RESULTS.md) and [JSON](W2C1_RESULTS.json) are a **partial preview from the 12 clean contexts**. The four VOID originals are permanently excluded from scoring. Their replacement contexts are pending.

## VOID diagnosis

The original rollout files were read as records, without viewing crop images or adjudicating labels. Record numbers below are **zero based**, matching the canonical scanner. [void_diagnosis.json](void_diagnosis.json) binds the receipt, scan and rollout hashes and retains the relevant tool inputs and reproduction evidence.

| VOID context | What the reader did | Why the canonical scanner rejected it | Preventable tool behaviour |
|---|---|---|---|
| `w2c1_nlg_poly1900/c1` | Record 22 called `pwd` inside a path template in an image-view loop. Record 44 assigned `p` from command output and used `store("p",p)`. Records 60, 77, 92, 107, 122, 136, 150, 165, 180 and 191 interpolated `load('p')` into paths. | One outside-path literal fragment `/zoom/$`, and ten unresolvable load expressions. The computed store is not a preceding literal store under the canonical resolution rules. | Yes: explicit literal relative paths in each view call; no loop-built view paths, nested pwd expressions or store/load path construction. |
| `w2c1_nlg_poly1900/c2` | Record 22 used the same nested-pwd path construction in a five-image loop. Later record 38 switched to a literal base. | Record 22 still contributes `/zoom/$`; the later base does not cure that earlier violation. | Yes: use literal relative view paths from the first call. |
| `w2c1_nlg_greek_poly/c1` | Record 71 made and viewed `zoom/17end.png` at 720×300. Record 84 overwrote the same filename with another crop, now 550×198. | The earlier returned image in record 80 no longer matches the retained file. Replay verified the manifest but copied **zero originals**: canonical replay seeds only `items.jsonl` and `img/`, while this pack uses `cards.jsonl` and `crops/`. Its first generation command failed to find `cards.jsonl`; the mixed image-generation/answer-writing command at record 71 was also skipped. Result: reproduced view missing. | Yes: preserve every viewed image with a fresh filename. Separate image-generation commands from answer writes. This avoids needing overwrite replay; it does not repair or extend the scanner. |
| `w2c1_gazette_modern_modern_scanned/c2` | Record 22 used the same nested-pwd path expression in an eight-image loop; record 44 later stored a literal base. | `/zoom/$` at record 22, despite the later literal base. | Yes: literal relative view paths from the first call. |

The `/zoom/$` findings are the scanner's static fragments from tool inputs. They do not establish that the reader actually opened a file outside its directory. All four remain VOID under the unchanged rules.

Evidence receipts: [poly1900 c1](receipts/w2c1_nlg_poly1900/c1.json), [poly1900 c2](receipts/w2c1_nlg_poly1900/c2.json), [Greek-poly c1](receipts/w2c1_nlg_greek_poly/c1.json), [Gazette c2](receipts/w2c1_gazette_modern_modern_scanned/c2.json). Each names its actual rollout under `.codex/sessions/2026/10/18/`.

## Protocol and addendum

Addendum: **yes**. HANDOVER §3 distinguishes the verbatim protocol body from its tool-use wrapper, and prohibits editing a protocol body without another comparison. I interpret that wrapper allowance as permitting this operational addition: [prompts/path_addendum.md](prompts/path_addendum.md) is appended **verbatim, after** [prompts/bsb.md](prompts/bsb.md), only for the replacement beds. The BSB file is byte-identical to the HANDOVER source; no label definitions, decisions, or output fields changed.

HANDOVER source: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/HANDOVER.md`, §§2–5. Its image and file rules already require local images and allow `zoom/**`; the addendum makes a conservative tool-use pattern explicit. It does not promise scanner success before the reread has been scanned.

The addendum, verbatim:

```text

# Tool-use addendum
Use only relative paths inside your current reader folder. In every view_image call, write the complete relative path as a literal string, for example "zoom/card01-v1.png". Batch several explicit calls together. Do not build file paths in loops, template strings, concatenations, pwd expressions, or store/load expressions.

Create enlargements only inside ./zoom/. Give every new image a fresh filename. Never overwrite or delete an image after viewing it; preserve all zoom versions until the run is complete. Keep image-generation commands separate from commands that read or write answers.jsonl.

These instructions govern tool use only. Apply the label-check protocol above unchanged.
```

## Replacement packs and launch

| Original | Replacement |
|---|---|
| `w2c1_nlg_poly1900/c1` | `w2c1_nlg_poly1900_r2/c1` |
| `w2c1_nlg_poly1900/c2` | `w2c1_nlg_poly1900_r2/c2` |
| `w2c1_nlg_greek_poly/c1` | `w2c1_nlg_greek_poly_r2/c1` |
| `w2c1_gazette_modern_modern_scanned/c2` | `w2c1_gazette_modern_modern_scanned_r2/c2` |

Each context retains its exact original 50 bed cards and five approved controls: identical labels, scripts and crop bytes. No draw was repeated. All 220 opaque IDs are fresh, disjoint from the VOID packs and all other existing packs. Seeded shuffling moves each of the five controls away from its original position. The two poly1900 context row sets remain disjoint.

Packs remain outside repositories at the original PACK_ROOT recorded in [repack_receipt.json](repack_receipt.json). Private mappings and original draw slices are under `w2c1/keys/`, outside PACK_ROOT. Reader directories contain only `cards.jsonl` and copied, content-hash crops. Manifests are beside the reader directories. [repack_closure.json](repack_closure.json) records all four closures.

[launch_repack.sh](launch_repack.sh) runs the four sequentially and logs to `repack_run.log`; **it has not been run**. The launcher probes before each context; `run_bed.sh` also probes before/after each run. Exactly one weekly 10080-minute reading is required, and ≥78%, missing or ambiguous readings stop execution. A VOID or failed reader stops the sequence. The existing refuse-rerun guard remains intact. Empty sibling contexts are not prepared and cannot launch.

Settings remain `gpt-6.1-sol`, medium, network OFF, web/apps/plugins/multi-agent disabled. The canonical scanner is called directly by `run_bed.sh`; no scanner or replay source was changed or wrapped. SHA-256: `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`.

## Scoring and validation

Run `python3 -B docs/records/harvest/recut_v1/w1_masked/w2c1/score.py` after the reread. It writes `W2C1_RESULTS.md` and `W2C1_RESULTS.json`. It selects exactly the 12 good original contexts and four replacements, validates clean scanner receipts and rollout hashes, recomputes answer mappings and controls, compares stored results, checks the exact draw slices, and excludes controls from the label-quality denominators. It never substitutes VOID answers for a missing reread.

C1 bars are **letters ≥90% and crop_ok ≥90% on 100 cards**, from `greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/C1_REPORT.md`, first paragraph. A stratum awaiting either context is PENDING; its observed partial gate is displayed separately. A complete stratum passes only if both bars pass and neither context is control-flagged (>1 error). `letters=u` remains in the denominator. Whole-line Sol marks do not affect these gates: marks remain pending Opus, including the grave-heavy Greek strata (HANDOVER §§1, 3).

The current preview includes 600 bed cards and 60 controls, with one control error in BSB c2 (below the flag threshold). Last recorded weekly probes were 6–7%, then 7%; no live budget measurement was made in this task.

Tests run offline with fake launchers/probes and synthetic reread answers. They cover closure, exact cards/pixels, fresh IDs, shifted controls, original scanner/replay/prompt hashes, refusal to rerun, sequential launch stop rules, fixed replacement routing, partial denominators, all-eight-strata completion, exact 90% boundaries, marks exclusion, control flags, tamper rejection, and byte-identical scoring outputs. See [tests_w2c1c.log](tests_w2c1c.log) and [tests_w2c1c.xml](tests_w2c1c.xml).

Validation: **41 tests passed**, zero skipped. The real launcher and probes remain unexecuted.
