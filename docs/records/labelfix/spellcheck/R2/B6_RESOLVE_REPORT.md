# B6: T2/T4 two-reader resolution and isolated tiebreak decks

Completed offline on 17 October 2026 in this worktree. No readers were launched and no `.git` writes were made. Resolver code and tests are unchanged. The requested reader configuration, for subsequent execution, is `gpt-6.1-sol`, medium reasoning, network OFF.

| Tranche / role | Agreed resolved | Agreed UNKNOWN | Pending tiebreak data | Controls excluded | Total |
|---|---:|---:|---:|---:|---:|
| T2 / supervision | 721 | 1 | 78 | 80 | 880 |
| T4 / witness | 696 | 2 | 102 | 80 | 880 |

The 880-card denominator includes 80 planted control-flagged cards; usable truth has an 800-data-card denominator. Controls never become supervision or witnesses. The agreement UNKNOWN cards receive no third reading under the owner rule. UNKNOWN values within otherwise resolved words also remain unchanged.

## Inputs, gate and resolution semantics

Protocol read from [`READER_PROTOCOL_R2.md`](../../../../../../greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_evidence/READER_PROTOCOL_R2.md), at `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_evidence/READER_PROTOCOL_R2.md`. It was absent at the same path under `greek-ocr-toolkit`; the available spellcheck worktree supplied it. Inputs were the T2/T4 decks in this worktree and all 32 original batch manifests/answers under:

```text
/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/
  r2read_{T2,T4}_{r1,r2}/b00..b07/{cards.jsonl,answers.jsonl}
```

Every batch was validated by the unchanged resolver CLI with `--dry-run`, its own assigned `--manifest`, and its original `answers.jsonl`. All 110 cards per batch were present in assigned order. Each full reader was then joined by card ID and written in the resolver-required forward/reverse deck order; no positional joining. Per-batch gates were checked before full-tranche resolution; every batch passed, so none was dropped. Each gate permits at most one control error. Existing `lead_verified: true` flags and lead notes were used without changing control inputs.

**T2 control-key coverage issue:** `aeead432bc9a619c69e081b1` (mining text `ἁλάτων`) is control-flagged in the private key but absent from `controls_proposed.json`. It is excluded from truth and not scored or planted in r3. Thus T2 has 79 scored controls, not 80. The emitted `control_readings`/`controls_excluded` fields count 79; the actual truth exclusion is all 80 flagged controls. This was not silently treated as a passed control. T4 has all 80 scored.

| Tranche | Reader | Batch | Cards | Scored controls | Control errors | Invalid votes | Gate |
|---|---|---|---:|---:|---:|---:|---|
| T2 | r1 | b00 | 110 | 14 | 0 | 0 | PASS |
| T2 | r1 | b01 | 110 | 5 | 0 | 2 | PASS |
| T2 | r1 | b02 | 110 | 7 | 0 | 1 | PASS |
| T2 | r1 | b03 | 110 | 14 | 0 | 0 | PASS |
| T2 | r1 | b04 | 110 | 11 | 0 | 0 | PASS |
| T2 | r1 | b05 | 110 | 10 | 0 | 1 | PASS |
| T2 | r1 | b06 | 110 | 13 | 0 | 0 | PASS |
| T2 | r1 | b07 | 110 | 5 | 0 | 1 | PASS |
| T2 | r2 | b00 | 110 | 5 | 0 | 1 | PASS |
| T2 | r2 | b01 | 110 | 13 | 0 | 1 | PASS |
| T2 | r2 | b02 | 110 | 10 | 0 | 0 | PASS |
| T2 | r2 | b03 | 110 | 11 | 1 | 6 | PASS |
| T2 | r2 | b04 | 110 | 14 | 0 | 1 | PASS |
| T2 | r2 | b05 | 110 | 7 | 0 | 3 | PASS |
| T2 | r2 | b06 | 110 | 5 | 0 | 0 | PASS |
| T2 | r2 | b07 | 110 | 14 | 0 | 0 | PASS |
| T4 | r1 | b00 | 110 | 11 | 1 | 4 | PASS |
| T4 | r1 | b01 | 110 | 9 | 0 | 0 | PASS |
| T4 | r1 | b02 | 110 | 6 | 0 | 1 | PASS |
| T4 | r1 | b03 | 110 | 14 | 0 | 0 | PASS |
| T4 | r1 | b04 | 110 | 6 | 0 | 0 | PASS |
| T4 | r1 | b05 | 110 | 16 | 0 | 0 | PASS |
| T4 | r1 | b06 | 110 | 10 | 0 | 0 | PASS |
| T4 | r1 | b07 | 110 | 8 | 0 | 0 | PASS |
| T4 | r2 | b00 | 110 | 8 | 0 | 1 | PASS |
| T4 | r2 | b01 | 110 | 10 | 0 | 0 | PASS |
| T4 | r2 | b02 | 110 | 16 | 0 | 1 | PASS |
| T4 | r2 | b03 | 110 | 6 | 0 | 0 | PASS |
| T4 | r2 | b04 | 110 | 14 | 0 | 0 | PASS |
| T4 | r2 | b05 | 110 | 6 | 0 | 0 | PASS |
| T4 | r2 | b06 | 110 | 9 | 0 | 0 | PASS |
| T4 | r2 | b07 | 110 | 11 | 0 | 1 | PASS |

The only control errors were T2 r2/b03 `11f560b94eb71916e13ab133` and T4 r1/b00 `3253788b76d18803699f7d57`; both batches passed at one error. All failure IDs and invalid-vote reasons are retained in the per-batch receipts and `gate.json`.

T2 has 15 data cards with invalid vote(s), plus 63 valid-vote disagreements; T4 has 7 plus 95. Both-invalid data cards are retained for tiebreak as required by the resolver. Resolution uses the resolver signature: normalized literal form, readability, applicable ownership and explicit head tuples; confidence/note wording alone does not create a disagreement.

**Agreement-only publication:** the unchanged resolver emits `truth.jsonl` with provisional two-vote head/form majorities even on signature-disagreement cards. Its raw `resolved` counts are 760 (T2) and 777 (T4). Those include 39 and 81 pending-disagreement cards, respectively. B6 `resolved.jsonl` contains only non-disagreement cards that the resolver marks resolved: 721 and 696. Raw outputs remain intact; disagreement cards are listed in `pending_tiebreak.jsonl`. Agreed unresolved rows are retained in `unknown_agreements.jsonl`: T2 `99564febd9970ecc11507949` (unreadable); T4 `1b41188cc203904404d0ef63` and `a6bf85b46577fa73d09f7969` (undecided heads). No runtime resolver change was needed.

## Third-reader deal

Only the resolver-selected disagreements/invalid-vote data cards plus its planted controls were dealt. No agreed data card was added. Options come directly from the resolver’s newly randomized tiebreak manifest. Its private maps remain in `artifacts/r2_resolve/{T2,T4}/tiebreak/private/`, outside all blind/reader folders.

| Tranche | Folder suffix | Total cards | Pending data | Planted controls | Leak scan |
|---|---|---:|---:|---:|---|
| T2 | `r2read_T2_r3/b00/` | 79 | 37 | 42 | PASS |
| T2 | `r2read_T2_r3/b01/` | 78 | 41 | 37 | PASS |
| T4 | `r2read_T4_r3/b00/` | 91 | 50 | 41 | PASS |
| T4 | `r2read_T4_r3/b01/` | 91 | 52 | 39 | PASS |

Folders are beneath the scratchpad root above. Each contains `cards.jsonl`, `img/`, `README.md`, `answer_schema.json`, and empty `answers.jsonl`. Each context must open only its own folder and only the listed files/images. The maximum is 91 cards, including controls, below the 100-card cap. The hash-ordered full resolver manifest is dealt round-robin into two folders per tranche. To consume future answers, join all r3 files by card ID and restore the full resolver manifest order; never concatenate folder answers positionally.

Each folder was scanned recursively: exact file allowlist, no symlinks, image references restricted to local basenames, image byte hashes equal filenames, PNG metadata empty, and no private source IDs/paths, Google text fields, truth/control key fields, or copied reader answers. All answer files are empty. Per-file SHA-256 hashes and card ID membership are in `r3_deal_receipt.json` outside the reader folders. This proves folder-content isolation and absence of escaping references; the ordinary filesystem does not enforce denial of parent/sibling reads. The reader instruction must enforce the file allowlist. Native printed image text is intentionally retained.

## Usable-slot inventory

A slot is `(crop_sha256, crop_letter_offset + letter_index)`, deduplicated within each reported group; repeated views do not add slots. “Complete slots” require all four heads known and the resolver’s ownership eligibility. Resolved words may retain unknown heads on some letters. “Pending” counts unique anchor opportunities only: their transcription length and usable full-word slots are not yet known, so these counts are potential, not accepted truth. No estimated future usable-slot total is reported. Controls are excluded throughout. Full JSON is `b6_usable_slot_inventory.json`; the original resolver inventory remains `usable_slot_inventory.json`.

| Tranche / role | Resolved cards | Complete slots now | Pending cards / unique anchors |
|---|---:|---:|---:|
| T2 supervision | 721 | 3644 | 78 / 78 |
| T4 witness | 696 | 3817 | 102 / 102 |

Known individual heads on the accepted resolved words (less restrictive than a complete four-head tuple):

| Head | T2 known slots now | T4 known slots now |
|---|---:|---:|
| breathing | 3644 | 3817 |
| accent | 3646 | 3818 |
| dialytika | 3646 | 3818 |
| subscript | 3646 | 3818 |

By prespecified target head, showing all complete word-letter slots supplied by cards assigned to that head (not only anchors):

| Tranche | Target head | Resolved cards | Complete slots now | Pending cards / anchors |
|---|---|---:|---:|---:|
| T2 | breathing | 372 | 1806 | 38 / 38 |
| T2 | accent | 156 | 754 | 17 / 17 |
| T2 | dialytika | 30 | 283 | 6 / 6 |
| T2 | subscript | 163 | 801 | 17 / 17 |
| T4 | breathing | 431 | 2474 | 60 / 60 |
| T4 | accent | 165 | 834 | 30 / 30 |
| T4 | dialytika | 11 | 100 | 1 / 1 |
| T4 | subscript | 89 | 409 | 11 / 11 |

Available slice/subtype tags were used as acquisition tags, never as printed truth. The `capitals` tag pools capital/ALL-CAPS/numeral cases; `omicron_monotonic` is broader than literal ο/οι. These pools cannot be split reliably from the provided tags.

| Tagged hallucination pool | T2 resolved cards / complete slots | T2 pending anchors | T4 resolved cards / complete slots | T4 pending anchors |
|---|---:|---:|---:|---:|
| capital/ALL-CAPS/numeral (pooled tag) | 224 / 827 | 36 | 87 / 396 | 13 |
| ο/οι monotonic (pooled tag) | 147 / 803 | 13 | 80 / 444 | 19 |
| crasis | 27 / 175 | 1 | 8 / 44 | 2 |
| untagged | 323 / 1839 | 28 | 521 / 2933 | 68 |

**Missing fine tags:** `-η subscript`, exact `ΐ`, and `clipped top` are **untagged**, not measured zeros. No card supplies those exact slice tags. The broader available `subscript`, `dialytika` and `specks` pools are shown below for traceability; they must not be relabelled as those finer slices. All 800 data cards per tranche lack each of those three exact tags. The residual untagged row above is a mutually exclusive pool after the available capital/omicron/crasis tags; it is not a count of all cards lacking every fine tag.

| Raw tag | T2 resolved cards / slots | T2 pending anchors | T4 resolved cards / slots | T4 pending anchors |
|---|---:|---:|---:|---:|
| slice:capitals | 224 / 827 | 36 | 87 / 396 | 13 |
| slice:omicron_monotonic | 147 / 803 | 13 | 80 / 444 | 19 |
| slice:subscript | 163 / 801 | 17 | 88 / 403 | 11 |
| slice:specks | 115 / 690 | 4 | 171 / 1010 | 29 |
| slice:exact_names | 72 / 523 | 8 | 86 / 492 | 14 |
| slice:random | 0 / 0 | 0 | 184 / 1072 | 16 |
| subtype:dialytika | 30 / 283 | 6 | 11 / 100 | 1 |
| subtype:crasis | 27 / 175 | 1 | 8 / 44 | 2 |

Agreed UNKNOWN inventory is kept separately: T2 one unknown anchor and zero complete slots; T4 two unknown anchors and zero complete slots. On those T4 UNKNOWN words, one accent and two dialytika/subscript individual head slots remain known. They are not promoted into `resolved.jsonl`.

## Card quality

Counts use both reader files joined by card ID. Full examples and verbatim notes are in each tranche’s `card_quality.json`; private option/readback evidence also appears in `base_letter_candidates.json`. The combined [word-image review sheet](../../../../../artifacts/r2_resolve/base_letter_review.png) was visually inspected. These quality notes do not change votes or keys.

| Finding | T2 | T4 |
|---|---:|---:|
| Option base differs from at least one literal reader transcription | 9 | 5 |
| Both readers supply the same alternative letter base | 6 | 4 |
| Scored controls from `greek_mono` sources | 72/79 (91.1%) | 76/80 (95.0%) |
| Scored control forms compatible with monotonic heads | 74/79 | 76/80 |
| Both readers unreadable OR low confidence | 9 | 6 |
| Both low confidence | 9 | 6 |
| Both unreadable | 1 | 0 |

Base-mismatch counts are reader-supported candidates, not 14 newly adjudicated ground-truth errors. They compare literal letter sequences, including case, against every offered option; missing non-anchor accents alone do not count. T2 has three reader-disputed base cases; T4 has one unreadable-versus-numeral case. The rendered sheet supports the option-quality concern but ambiguous glyphs remain unresolved where readers disagree. Examples:

- T2 `d06cfd3b0badd2bb3c1b248a`: all options are οι variants, both readers give printed υι (with an overbar noted). T2 `f96e01361d4b4615eb892dd3`: ο options versus both readers’ ἁ. T2 `be79fc3da430227a8fd65a71`: duplicated final alpha in option bases (`μοχθηριαα`) versus both readers’ eight-letter `μοχθηρίᾳ`; its anchor index lies outside the literal reading and both votes are invalid, so it remains pending.
- T4 `57d4ae4187933b7593d6b8dd`: τους-based options versus both readers’ `τοὶς`. T4 `3e770c86cb23b92ae852acf9`: ο options versus printed/read c. T4 `c6c7764b87c13762fa0d367e`: ο options over a numeral 5; one reader says unreadable, the other writes 5 with an invalid anchor index.
- T2 `24ad48ef611d09c519fe23f8` and `e54a376fa9d7413ad3414b49` remain disputes over α/κ and ι/r; the quality flag does not settle them. T2 also includes case/script mismatches (`2Ο` versus `2ο`, Greek ι versus Latin i, Greek ΖΝ versus mathematical ℤN, Π versus Roman II).

Monotonic-source control examples: T2 `4e7ec9525dbb95adc01ce912` πλάνα, `6f0f214cc4ba6ef85f6fdd56` με, `0c7184503e21cecb28313a3e` τους; T4 `806af78332e57303cbe24483` από, `fe5caee01ce11baa9b476765` λιγότερο, `8532641fdf9469c193ee351d` που. “Monotonic-compatible” means no breathing/subscript and accents only none/acute, not a claim about historical orthography. Passing these controls gives limited coverage of difficult polytonic distinctions.

Both-low examples: T2 `e53b51448df2c78c1f02369c` (ἅπας, partial/low twice), `80655f477a39286e71ce8b0e` (τῇ, low twice), and `99564febd9970ecc11507949` (unreadable/low twice). T4 `1f0c36459eb2167e13ee3f18` (Ὁ versus Ὃ, partial/low), `fd2c69c9a0529ed493e24589` (ἥμερον versus ἤμερον, low), and `a6bf85b46577fa73d09f7969` (agreed undecided breathing, partial/low). These counts include flagged controls if any; in fact all listed low/unreadable cases are data cards.

## Opus usage: emitted fields, token totals not recorded

The protocol required per-answer `usage` zeros. Therefore the emitted zeros below are placeholders, not measured token totals. **Input tokens, output tokens and total tokens: not recorded for both tranches. No estimates.** Tiebreak deck preparation consumes no additional Opus reading; reader 3 has not run.

| Tranche | reader | cards | readings | tiebreaks | control_readings | accepted | invalid_answers | valid_answers | input_tokens emitted | output_tokens emitted |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| T2 | reader1 | 880 | 880 | 0 | 79 | true | 5 | 875 | 0 | 0 |
| T2 | reader2 | 880 | 880 | 0 | 79 | true | 12 | 868 | 0 | 0 |
| T4 | reader1 | 880 | 880 | 0 | 80 | true | 5 | 875 | 0 | 0 |
| T4 | reader2 | 880 | 880 | 0 | 80 | true | 3 | 877 | 0 | 0 |

All fields of each resolver-emitted `opus_usage.json` are represented above. Per-batch usage/gate receipts also remain available. Neither usage files nor source answer placeholders were rewritten.

## Artifacts and validation

Outputs are in [T2](../../../../../artifacts/r2_resolve/T2/) and [T4](../../../../../artifacts/r2_resolve/T4/): `resolved.jsonl`, `unknown_agreements.jsonl`, `pending_tiebreak.jsonl`, `gate.json`, `opus_usage.json`, raw resolver outputs/receipt, `batch_gates/`, `tiebreak/{blind,private}/`, slot inventory, quality notes and r3 deal receipt. Original readers/decks were read-only. Receipt hashes bind original answers/manifests/control files and the assembled ID-joined reader inputs. Preparation scripts are saved under `artifacts/r2_resolve/b6_{gate,resolve,assemble}.py`; the assembler deliberately refuses to overwrite existing r3 folders.

Validation command (requested Python):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \
  -m pytest -q -p no:cacheprovider \
  tests/test_r2_cards.py tests/test_docai.py tests/test_harvest_admission.py \
  --basetemp=.cache/b6-suite
```

**167 passed in 6.99s.** Log: `artifacts/r2_resolve/resolver_suite.txt`. The resolver-only suite also passed 45/45 with a worktree-local `--basetemp`. An initial run using pytest’s default external temp folder failed the resolver’s deliberate worktree-output guard; rerunning with local temp fixed the harness placement without changing code. The broader 167-test suite then passed. All operations were local, with no network calls. `artifacts/r2_resolve/b6_final_receipt.json` verifies input hashes unchanged, all four reader folders/empty answers and hashes intact, exact tiebreak coverage, and the data/control partitions.

B6 READY: T2 resolved 721/880 tiebreak 78 (2 folders); T4 resolved 696/880 tiebreak 102 (2 folders); gates ok; resolver changed no

## B6b: v2 deal with ten controls per folder

Completed offline on 17 October 2026. B6 outputs, including the original `tiebreak/` decks and `r3_deal_receipt.json`, remain hash-identical. The new decks are siblings at `artifacts/r2_resolve/{T2,T4}/tiebreak_v2/{blind,private}/`. All four destination `answers.jsonl` files were checked as zero bytes before rebuilding the existing folders in place, and remain empty. Reader READMEs are byte-identical to B6 and contain no model name. No reader was launched; no network calls or `.git` writes were made.

| Tranche | Folder | Pending data | Controls | Total | Leak scan | Resolver dry-run |
|---|---|---:|---:|---:|---|---|
| T2 | `r2read_T2_r3/b00/` | 37 | 10 | 47 | PASS | PASS |
| T2 | `r2read_T2_r3/b01/` | 41 | 10 | 51 | PASS | PASS |
| T4 | `r2read_T4_r3/b00/` | 50 | 10 | 60 | PASS | PASS |
| T4 | `r2read_T4_r3/b01/` | 52 | 10 | 62 | PASS | PASS |
| **Total** | **4 folders** | **180** | **40** | **220** | **PASS** | **PASS** |

The 78 T2 and 102 T4 pending data cards retain their original folder assignment, relative order, complete public card objects and resolver-randomized option letters. Only controls and their insertion positions change. Private option maps and selected control IDs remain outside blind/reader folders.

**Selection rule:** seed `20261017`, using independent `Random("20261017:<tranche>:selection")` instances over sorted scored IDs. Controls are selected without replacement within each tranche, excluding T2 `aeead432bc9a619c69e081b1`. Shuffle polytonic-source and other controls separately. Stably rank the polytonic-source pool by descending count of verified breathing, grave/circumflex, subscript and diaeresis marks, then distribute it round-robin across b00/b01. Reserve missing scored-anchor breathing, accent and subscript-or-diaeresis examples from the remaining pool when available, falling back to all-letter coverage when no anchor example exists; fill to ten using seeded pool order. Shuffle each folder's controls and sample their insertion positions with `Random("20261017:<tranche>:b<NN>:positions")`. The exact rule, selected IDs, positions and all-letter/scored-anchor coverage are recorded in each tranche's `r3_deal_receipt_v2.json`.

**Available head mix:** T2 has only seven polytonic-source scored controls, distributed 4/3; T4 has four, distributed 2/2. All are retained. There are no scored subscript or dialytika examples in either tranche. T2's sole breathing example (`11f560b94eb71916e13ab133`, `αὐτοὺς`) is in b00 and its breathing is on a non-anchor letter; no T2 control scores breathing at the anchor. T4 has three anchor-breathing examples, distributed 1/2. Each folder includes scored-anchor accent examples. These limits are reported rather than manufacturing new control truth or reusing controls between folders.

**Resolver validation and consumption:** the unchanged resolver's reader3 gate is `R.batch(answer_path, public_mapping, selected_controls, assigned_order)`. Each folder was exercised through that exact function with its v2 mapping and ten controls, and through `R.validate_batch` using a temporary deck adapter whose public manifest is exactly the v2 folder manifest and whose private controls are exactly that folder's ten scored controls. Synthetic zero-, one- and two-control-error cases verified zero invalid answers, ten evaluated controls, acceptance at zero/one errors and rejection at two errors for every folder. Temporary answers and deck adapters were removed; no synthetic truth was published. Case receipts remain in `tiebreak_v2/private/dry_run/b00.json` and `b01.json`.

For actual v2 consumption, gate each folder independently using those v2 inputs, then join accepted normalized third-reader votes to the B6 reader votes by card ID. The full resolver `run(..., reader3=...)` entry point regenerates the original B6 full-control manifest and cannot directly consume the reduced v2 answers; do not concatenate folders or use that entry point unchanged. The folder-level resolver path above is the verified integration, with the original at-most-one-control-error rule preserved per folder.

Preparation and validation script: `artifacts/r2_resolve/b6b_redeal.py`. Hash/leak receipts: `artifacts/r2_resolve/{T2,T4}/r3_deal_receipt_v2.json`; final unchanged-B6/output check: `artifacts/r2_resolve/b6b_final_receipt.json`. The leak scan covers recursive file/field allowlists, private text and paths, symlinks, exact image references, PNG hashes/metadata and README model names. An initial temporary-output placement was rejected by the resolver's worktree/output guard; the folders were restored against original B6 hashes before correcting the harness and rerunning successfully. Resolver source and tests remain unchanged.

B6b READY: folders 4; cards 220 (data 180, controls 40); leak scan pass; resolver dry-run pass

## B6c + R2M: final resolution and R2a supervision manifest

Completed offline with the requested Python. No network calls, inference, training, submissions, or `.git` writes. Original reader answers, deals and input worktrees were read-only.

| Tranche | Final resolved / 800 | Unresolved | r3 b00 controls / errors / invalid | r3 b01 controls / errors / invalid |
|---|---:|---:|---|---|
| T2 | 790 | 10 | 10 / 0 / 1 | 10 / 1 / 3 |
| T4 | 791 | 9 | 10 / 0 / 1 | 10 / 0 / 1 |

Every folder passes the original at-most-one-control-error gate. Receipt-bound manifests, private maps, immutable reader-folder files and PNG hashes match v2. Answers are valid JSONL with exact unique card membership and line counts (47, 51, 60, 62). Answers are joined by card ID before normalization; invalid individual votes remain excluded, with reasons in each final `gate.json`. The unchanged resolver computes 2-of-3 truth. UNKNOWN heads remain UNKNOWN, and cards without the required majority remain unresolved. Controls never enter the 800-card denominators.

Final artifacts: `artifacts/r2_resolve/{T2,T4}/final/{resolved.jsonl,unresolved.jsonl,gate.json,opus_usage.json}`. Reader-3 tokens supplied by the lead, including tool I/O: T2 b00 157,076; b01 160,476; total 317,552. T4 b00 169,280; b01 161,761; total 331,041. Combined: 648,593. Input/output token splits are unavailable; earlier readers emitted zero usage fields remain labelled placeholders.

### Slot identity and admission

Manifest: `artifacts/r2a_manifest/r2a_slots.jsonl`, using the R2 training overlay schema: integer four-head targets, native_print provenance, weight 1, train role, preserved teacher_seen_document, and pool native for new slots. Native extraction/staging is a separate R2 job operation; this task creates the supervision overlay.

Card crop_letter_offset is a provider alphabetic-letter ordinal, not a recogniser NFD start. The builder uses case-preserving, mark-blind alignment to saved R2 job 3681404 recogniser predictions. A base is mapped only when every optimal LCS alignment gives the same match and none skips it. Printed/mined word base mismatches, ambiguous/missing mapping and unknown tuples are quarantined; no zeros are invented. Teacher head predictions are never labels. Readback alignment and train-export file hashes are verified against READBACK_RECEIPT.json and recorded in receipt.json.

Each card anchor and each resolver-emitted letter entry is accounted for. Extra decided letters inherit the card slice and target head; capitals require an uppercase printed base, and the subscript slice requires printed α/η/ω. Letters outside the frozen R1 vowel/rho embedding are excluded with explicit reasons. Exact-name target-head negatives are excluded because that slice has no negative budget. Negative/positive refers to the card target head, not whether all four heads are absent. Duplicate keys with conflicting tuples STOP; identical duplicates count once.

Diversity selection uses seed 20261017 via SHA256 ordering. The page cap counts distinct target cards across slices, at most five per document/page. The document cap is at most 10% of the final retained slice, computed with a feasible retained denominator rather than the larger planned budget. Capped slots are recorded in excluded.jsonl.

| Slice | Negative / target | Negative deficit | Positive / target | Positive deficit | Documents |
|---|---:|---:|---:|---:|---:|
| capitals | 214 / 800 | 586 | 127 / 500 | 373 | 86 |
| omicron_monotonic | 444 / 400 | 0 | 73 / 400 | 327 | 96 |
| subscript | 178 / 400 | 222 | 85 / 500 | 415 | 73 |
| specks | 314 / 400 | 86 | 59 / 200 | 141 | 64 |
| exact_names | 0 / 0 | 0 | 79 / 400 | 321 | 37 |
| Total | 1150 / 2000 | 894 | 423 / 2000 | 1577 | 97 unique |

Deficits remain as measured; top-up reading is paused. Targets are shown per cell; a surplus in one cell does not cancel the deficit in another cell.

Admitted 1573 unique slots (1150 negative, 423 positive); identical duplicates 0. Quarantined 258: {"printed_base_sequence_differs_from_located_word": 9, "recogniser_base_alignment_not_unique_or_missing": 3, "unknown_head": 246}. Excluded 2264: {"base_outside_frozen_R1_embedding": 1581, "exact_names_has_no_negative_budget": 244, "printed_base_outside_tagged_slice": 439}. Per-document and per-page cap exclusions are zero if absent from that breakdown. Every exclusion/quarantine retains card provenance; exact per-slice document lists are in receipt.json.

Replacement check: 0 replaced, 1573 new. Frozen R2 data path from r2-prep config/r2_job.json: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/data`. The complete C1 crop inventory SHA256 `4dfb7e8e72675c7b0fa415d43a55d082d04b05cd7d6f79f95c6f7bcf51c3da88` matches the deployment external-hash binding. All T2 data crop hashes are disjoint from this inventory, proving zero existing old-pool identities without reading the remote index. Existing identities use replaces and never append; that branch is covered by a fixture.

Leakage: **0**. All T2 data documents and all admitted manifest documents have supervision role and are absent from the complete T4 document set, validation and calibration. Any hit or unknown role raises STOP before manifest publication.

Manifest SHA256: `3dda20644c17b44e1a1c9f69781a9f1dd18657f6dc8b8b7e9cd14d8dd30a7667`.

Validation: `tests/test_r2_finalize_manifest.py` plus `tests/test_r2_cards.py`; log `artifacts/r2_resolve/b6c_tests.txt`. Fixtures cover UNKNOWN quarantine, duplicate identity/conflict, final-denominator document cap, page cap, replacement rather than append, leakage STOP, case-preserving/ambiguous base alignment, printed-base slice membership, no-majority resolution and UNKNOWN preservation. Independent output readback checks manifest schema, hashes, all partitions, diversity and leakage.

B6c+R2M READY: T2 final 790/800 (unresolved 10), T4 final 791/800 (unresolved 9); gates ok; R2a slots 1573 (neg 1150/pos 423; replaced 0, new 1573; quarantined 258); leakage 0; manifest sha 3dda20644c17
