# Secondary Google label corrections: plan (17 Oct 2026, 15:17 Athens)

Lead: the "Correct secondary Google OCR errors" session (Opus). Branch `opus/secondary-corrections`, forked from `opus/spellcheck`
5ab84e501 (contains the N1 step-0 commit acb77d817). Coordinator: the Fable coordinator session. Peers: the spell-check lead
(polytonic marks only) and the sourcing lead (collection, admission, masking, quotas, stratum re-checks).

**Scope (owner, 17 Oct).** Every Google label fault except polytonic accents, breathings and subscripts, in the owner's priority
order: N1 numeric separators; RU1 Cyrillic hard sign; capitals; punctuation; superscripts and rare glyphs; mixed-script lookalikes;
silent misprint correction.

**Standing rules.**
- Labels are the ink. Misprints stay. No correction may override the image.
- Every repair is one-directional: a stated Google glyph → the printed glyph, only when the ink says so. Anything uncertain becomes
  HOLD, never a guess.
- Repairs go into a new label version keyed by row id, with provenance (original text, edit spans, reader answer id, run id, rule
  hash). Google's text is never overwritten.
- All code, censuses, pack builders, reading runs, scoring and receipts are Sol briefs (`codex exec`, medium for mechanical work)
  with tests and receipts. The lead plans, briefs, verifies controls, reviews, rules and records. The lead commits, because the Codex
  sandbox cannot write `.git` locks. Nothing is pushed or deleted.
- Reading: no Opus reader runs until the Claude reset. Sol one-reader under the sol-reading HANDOVER (opus/sol-reading ad1889bd9,
  `docs/records/harvest/sol_reading/HANDOVER.md`): isolated packs outside every repo, ≤100 items per context, ~10% lead-verified controls,
  scanner v4 leak scan on every rollout, limit probe before and after each run. Every "unreadable" and every flag goes to a lead or
  owner eye.
- Owner pages go only through `greekocr.adjudicate.owner_sheet` (worktree greek-ocr-toolkit-cleanup). The coordinator publishes them,
  republishing to existing URLs so the owner's notes persist.
- Each class follows the accents path: measurement → owner sheet → one-directional rule or reader → blind audit on a locked
  stratum → gate.

## 1. Summary table

Rates are from the C1 uniform cards (14 strata × 100, `sol/collect-v3` `docs/records/harvest/collect_v3/c1/c1_results.json`), the N1
step-0 census (`docs/records/labelfix/N1_STEP0_REPORT.md`), E3 (`greek-page-ocr docs/ocr_program_2026-10-06/E3_RESULTS.md`) and T10
(`DOCAI_FAILED_LINES_v1.md`). "Cards" means cards with at least one such fault.

| # | Class | Measured | Rule / reader | Signal | Locked eval stratum | Gate |
|---|---|---|---|---|---|---|
| N1 | Numeric separators | ELSTAT 3/100 cards with true separator faults (`4·547·331` → `4-547-331`, `555,6` → `555.6`). 1,078 inner hyphens in 4+-digit tokens in W1. Training labels: 1 raised dot vs 1,074 such hyphens. | Grammar proposes, ink decides. Google `-`/`.` → `·` only when ink says raised dot AND grammar admits a thousands slot. Never touch a hyphen-length stroke. | Sol glyph pass (dev frame); ink rule from `glyphs.components` + x-height/baseline estimates, with a per-slot decision record | 300 slots: ELSTAT, Gazette 82–85, Gazette 86–90 × 100; 62 reserved documents disjoint from the dev frame (`artifacts/n1/locked_eval_docs.json`) | ≥99% precision raised-vs-hyphen on the held-out half and on the locked stratum; 0 edits on true ranges; HOLD rate reported |
| RU1 | Cyrillic word-final ъ → ь | ia_russian letters 74/100 (c1_fail). Ink adjudication: Google ь wrong at 26/49 positions; Google ъ never wrong (0/26). W1 ia_russian labels have ≈1,084 word-final ь and 4,197 word-final ъ (all 2,963 rows; ≈420 ь expected in the 1,146 usable rows). | Only word-final ь that Google wrote is a candidate. ь → ъ only on a Sol "ъ" answer. Google ъ and non-final ь are never touched. | Sol glyph question per position: "ъ, ь or unreadable". The orthographic prior (≈96% right on decided positions) is a cross-check, not a decider. | The 65 adjudicated positions are the controls (coordinator ruling). The 100-card re-check by the sourcing lead on the repaired labels is the audit. | Controls ≤1 error per context; every Sol-vs-prior disagreement pixel-checked by the lead; re-check letters ≥90 and crop_ok ≥90 |
| 3 | Capitals case | Not measured for Google labels. E3 recogniser CER on all-caps lines 4.12%, the worst line type. C1 has no case tally. | To be measured. Expected shape: inside an all-caps token, a lowercase letter whose capital has the same shape (ο κ π χ ψ ω υ; Latin c o s v w x z) → capital, when ink height reaches the cap line. | Ink height of the component vs the cap and x-height bands (`glyphs` helpers); Sol letter question on a sample | 200 all-caps tokens from disjoint documents, drawn after the census | ≥99% precision; 0 edits on true lowercase (mixed-case controls) |
| 4 | Punctuation | C1 "punctuation" tags on 48/1,400 cards. E3 punctuation-heavy CER 3.25%, dotted leaders 2.97%. Dashes: 21/1,400 cards. | Ano teleia `.`/`;` vs printed `·`: the same raised-dot ink rule as N1, applied in prose. Ellipsis: codec fold only. Line-end hyphen dropped: add `-` only when ink shows a dash component right of the last letter box. **Em dashes: tag only** (owner). | N1 dot-height rule reused; right-edge component check; Sol letter question on a sample | 200 slots per sub-class from disjoint documents | ≥99% precision per sub-class; dash tag has no gate (it is not a repair) |
| 5 | Superscripts and rare glyphs | Superscripts: 7/1,400 cards, 4/100 in ia_poly1850 poly1850 (dropped, or read as `8`/`2`/`**`). Codec v2 has no superscript atoms. Rare glyphs (T10, 396 crops): Google never emits ϗ ȣ ϛ ϲ ϝ ϙ ϡ and substitutes (`χείριϛον` → `χείριςον`). Codec v2 has ϛ ϝ ϙ ϡ but not ϗ ȣ ϲ Ϲ. Lunate ϲ: 3/1,400 cards. | Superscripts: a detector class (small component above the x-height band, next to a word or number) that tags or masks; no text repair until the owner rules on atoms. ϛ: medial `ς` inside a word is a text signal → Sol glyph question "ϛ, ς or σ" → ϛ. ϗ ȣ: owner codec decision first; synthetic coverage via linefactory. Lunate ϲ: keep the C1 codec convention; no repair. | Text signal (medial ς; `κὶ`) + Sol glyph question; component geometry for superscripts | Superscripts: all detected candidates in 2 disjoint books (≈100). ϛ: 100 candidates from disjoint Anemi/IA books. | Detector precision ≥95% for tagging; ϛ repair ≥99% precision |
| 6 | Mixed-script lookalikes | `lookalike_script_letter` on 5/100 cards in ia_poly1850 mixed_greek_latin (`T.` Latin siglum → Greek `Τ.`). That stratum is c1_pending at 90 letters. | The ink cannot decide (the glyphs are identical), so the rule is context-only. Extend the existing `collect_v3/vendor/lookalike_rule` to that stratum: a token whose letters are all shared Greek/Latin shapes, inside a Latin-majority span or a known siglum pattern → Latin code points. Owner ruling needed (Q4). | Script context of neighbouring tokens; no reader needed except a Sol letter-check audit sample | 100 lookalike tokens from disjoint documents | ≥99% precision on the audit; c1_pending re-draw passes (sourcing lead) |
| 7 | Silent misprint correction | Not measured. Google normalises printed misprints to dictionary words; C1 does not separate this from wrong_letter. | Candidates: our recogniser (E3 checkpoint) reads a non-word at edit distance 1 from Google's lexicon word. Sol letter question "which letters are printed" decides. Google word → printed form only on a Sol read that matches the recogniser. | Recogniser disagreement + lexicon + Sol letter question (qualified 99/100 on letters) | 200 candidates from disjoint documents, plus 100 agreement controls | ≥99% precision; a rate estimate before any repair |

## 2. N1 numeric separators (priority 1, taken over at step 0 complete)

**State.** Step 0 is DONE (Sol, committed acb77d817): census, a 600-slot dev frame and a 300-slot locked frame in
`artifacts/n1/`, the tokenizer in `greekocr/numerics/`, 17 tests passing.

**Convention ruling (lead, 17 Oct): a printed raised dot is U+00B7 MIDDLE DOT.** Codec v1 and v2 both have the U+00B7 atom, have no
U+0387 atom, and fold U+0387 → U+00B7 under NFD. The raw input code point is kept in audit metadata.

**Next steps, in order:**
1. **N1-L: lock the evaluation stratum** (Sol, medium). Write `artifacts/n1/n1_locked_eval_line_ids.txt` (every line carrying a
   locked slot) and the reserved-document list, with hashes and a receipt. I send the path and hash to the sourcing lead, who
   registers it in `collect_v3/release_exclusions/release_exclusions.json`. That worktree is theirs. **Step 1 does not start until
   they confirm.**
2. **N1-C: controls** (Sol builds, lead verifies). Crops are transient, so the builder regenerates them byte-exactly with
   `collect_v3/storage.ensure_crop(row)` and checks `crop_sha256`. Slot localisation uses Google's symbol boxes for the two flanking
   digits. Sol builds 4 contact sheets of 80 candidate control slots: clear decimal commas, clear range hyphens, clear thousands dots,
   plus the 3 C1 separator cards. All are drawn from documents outside both frames. I pixel-verify and keep about 60.
3. **N1-1: glyph pass** (Sol one-reader). The 600 dev slots plus controls in 7 contexts of ≤100 items (≈86 bed + 9 controls each).
   - Item: a 3× zoom from the left digit to the right digit, plus the whole line with the gap marked. No Google text is shown.
   - Options: raised dot · baseline dot · comma · hyphen/dash · space · nothing (digits touch) · other · unreadable.
   - Prompt `sep.md`: the yer protocol body with the question and options replaced and the GPT-6 wrapper unchanged. A 20-item
     dry run is compared against my reading before the full pass.
   - Gate: ≤1 control error per context, otherwise that context is void and re-read in a fresh order.
4. **N1-2: ink rule** (Sol). Built from `glyphs.components` plus the x-height/baseline estimates, with a decision record per slot:
   component height, vertical position relative to the x-height band, width, gap width. Thresholds are fit on half of the glyph-pass
   slots and scored on the other half. The rule hash is frozen.
5. **N1-E: locked read** (Sol, 3 contexts). Runs only after the rule hash is frozen. I pixel-check every Sol-vs-rule disagreement.
6. **Owner sheet.** Decision records for the edits and HOLDs go to the coordinator to publish. Then the composer: label version
   `n1_v1` with provenance, applied to W1 ELSTAT and Gazette, plus collection-v2 train rows where ink is available.
7. **Step 3** (the CNN reader) only on the coordinator's go after the step-2 numbers.

**Codex cost:** ≈1,000 reads, ≤2 weekly points.

## 3. RU1 Cyrillic hard sign (priority 2, taken over from sourcing, nothing started)

**Inputs (read only).**
- Rows: `~/Projects/collect-v3-data/run/W1/features.jsonl`, ia_russian. That is the live W2 root, so it is read only and `run.lock`
  is never taken.
- Current label: the `label` field.
- Crops: regenerated with `storage.ensure_crop` and checked against `crop_sha256`.
- Controls: the yer table at `sol/collect-v3` `docs/records/harvest/collect_v3/c1/yer_adjudication/` (65 positions, ink truth from two
  blind Opus readers).

**Steps.**
1. **RU1-0: census and pack build** (Sol, medium).
   - Enumerate word-final ь that Google wrote, in the 1,146 usable rows. The 65 control positions are excluded from the bed.
   - Per book, record the count of Google word-final ъ. Books with no final ъ (post-1918 orthography, e.g. the 1930 Sobranie
     zakonov) are not read in full: 20 of their positions are read as a spot check instead.
   - Items: a word crop at 3× and a letter zoom at 8× on the final sign, from Google's symbol boxes. No Google text is shown.
   - Packs follow HANDOVER §4. The census also records the orthographic prior per position.
2. **RU1-1: reading.** Sol one-reader on "ъ, ь or unreadable", ≤100 per context with ≈10% controls from the 65 positions. A context
   with more than 1 control error is void.
3. **Review** (lead). Pixel check of every Sol-vs-prior disagreement (expected ≈4%, ≈20 positions) and every "unreadable". If
   unreadables exceed 20, they go to an owner sheet instead.
4. **RU1-2: label version** (Sol). `ru1_v1.jsonl` keyed by row id with provenance; ь → ъ only on a confirmed ъ; a row with an
   unresolved position is marked HOLD. The path and sha256 go to the sourcing lead, who runs the 100-card re-check (Sol line letters,
   one reader). ia_russian stays out of release until that passes at letters ≥90 and crop_ok ≥90.

**Codex cost:** ≈500–1,200 reads, ≤2.5 weekly points.

## 4. Classes 3–7: measurement first

**M1: one Sol brief, text-only census, no pixels**, over W1 and the collection-v2 train labels. Per source and era:
- **Case:** lowercase letters inside all-caps tokens, by letter; case-shape-ambiguous letters.
- **Punctuation:** `.` or `;` where Greek prose expects ano teleia; `...` vs `…`; lines whose next line starts lowercase but which
  end without a hyphen (the dropped line-end hyphen); spaced hyphens between words (the dash tag).
- **Superscripts:** footnote-marker patterns (`**`, digits glued to a word end, `"` after a word).
- **Rare glyphs:** medial `ς` inside a word; `κὶ` standing alone.
- **Lookalikes:** mixed-script tokens and all-shared-shape tokens inside Latin spans.
- **Misprints:** recogniser-vs-Google edit-distance-1 non-word candidates, if E3 predictions exist for the rows. Otherwise this part
  waits for a predictions pass.

**Then, per class:**
- a ≤200-item Sol reading sample;
- an owner sheet of the top cases, built through `owner_sheet` and published by the coordinator;
- the rule;
- a locked stratum drawn before tuning, with its ids sent to the sourcing lead for release_exclusions;
- a blind audit;
- the gate in the table.

**Order:** punctuation (it reuses the N1 dot rule) → capitals → ϛ and superscripts → lookalikes → misprints.

**Codex cost:** ≈1,000 reads plus builds, ≤3 weekly points.

## 5. Order of work and Codex budget

| When | Work | Codex (weekly points, upper bound) |
|---|---|---|
| Now | N1-L lock brief; RU1-0 census and pack brief (in parallel; both mechanical) | ≤0.5 |
| After the lock is confirmed and controls are verified | N1-1 glyph pass (7 contexts); RU1-1 reading | ≤3 |
| Next | RU1 review + label version → sourcing re-check; N1-2 ink rule; M1 census | ≤1 |
| Then | N1 locked read + gate + owner sheet; classes 3–7 samples and sheets | ≤4 |
| **Total through the first gates** | | **≤9 → about 44% from ≈35% today** |

- Codex is ≈35% today (the coordinator's figure; my first run will probe it). The meter resets Thu 22 Oct 09:13. I stop at 80%, and
  the drivers refuse at 78%. Credits are never spent.
- Every deliverable report carries the live probe figure.

## 6. Owner questions (batched for the coordinator)

- **Q1.** Small caps: label them as capitals? Greek has no small-cap code points.
- **Q2.** Superscript markers: add codec atoms, or tag and mask the marker span? A text repair is impossible without one of the two.
- **Q3.** ϗ (kai sign) and ȣ: add codec atoms (v2.2 arm), or map them to their spelled forms? This is still open from T10.
- **Q4.** Identical-ink Greek/Latin lookalikes (`T.` siglum): accept a context rule that writes Latin code points inside Latin spans?
- **Q5.** RU1 positions that stay unreadable: hold the row out of release, or keep Google's ь? I default to HOLD.

**Owner notes already on the failure-modes sheet** (R3FELfNGyz4WVWohCboHy4, collection `notes`, 4 notes, all 11:41–11:43):
- **Three ia_poly1850 cards: "doesnt necessarily have to do with the latin? (but maybe?)".** The cards are
  `ia_poly1850--41e90f3ba967f920--s006-l0022`, `--a89bd2c9bdb1ca6d--s005-l0038` and `--a89bd2c9bdb1ca6d--s007-l0016`.
  - **Resolved 15:25.** The v1 sheet grouped them under "Latin siglum labelled with a Greek lookalike" because the checker coded them
    `lookalike_script_letter`.
  - Their actual faults are circumflex errors on Greek words in mixed lines: θλῖψις → θλίψις, Λαῖτοι → Λαϊτοι, ὧν → ὢν (OS2_REPORT,
    opus/cleanup-1 994456de0, re-tagged).
  - The owner is right: they are not Latin faults. They belong to the marks track, and class 6 uses only the true siglum cards (C1
    mixed_greek_latin c059, c085: Latin `T.` → Greek `Τ.`).

## 7. Agreements after the plan (17 Oct)

- **15:20, spell-check lead.** N1 and the punctuation repairs compose AFTER the marks release, because the frozen sf6
  `release_gate.edit_guard` compares punctuation against raw Google. Keraia signs (U+0374, U+0375, U+02B9, U+0384) stay in the marks
  gate. N1 edits only digit-flanked separator slots.
- **15:22, coordinator.** The plan is accepted. RU1 unreadables default to HOLD. Q1–Q5 were sent as one-line questions with defaults.
- **15:21.** Codex probe: 36.0% weekly. N1-L and RU1-0 were launched on Sol (medium, network off).
- **Sourcing lead.** The N1 lock is registered through their Sol brief after an overlap check against the wave-1d preregistered rows,
  the release-v3 candidates and W2 Gazette/ELSTAT. An overlap with 1d needs a coordinator ruling, so N1-L pre-computes an alternative
  lock that avoids 1d rows.
- **`nlg--1144074169f43992--s006-l0032`: "why is this in em dash dropped".** C1 recorded a dash stroke clipped at the crop's left
  edge, so the label had no dash. That is a crop fault, not a Google dash fault: it was misfiled and belongs to the crop tracks.
- **15:24, N1-L done (Sol).** The original lock had 14 wave-1d overlaps, so the lead ruled to register the **alternative lock**
  instead: `artifacts/n1/n1_locked_eval_line_ids_alt.txt`, 258 lines, 300 slots, sha256
  `3d6f0d29edf728514f0721ded09b9f3df65cbe352f70814e8bcbe49f51c430fe`. It has 0 wave-1d, 0 C1 and 0 step1 overlap.
  - 6 of its lines are already in `w1_rotated_crop_ids.txt`. Their slots are pre-declared as excluded from N1 locked scoring (they
    will be reported separately).
  - The fitting exclusion is the full reserved-document list (8,540 lines), which covers both draws. `greekocr.numerics.locks`
    enforces it.
- **15:27, N1 lock registered** by the sourcing lead as class `n1_locked_eval` (258 ids; wave-1d overlap 0, verified).
  - Location: sol/collect-v3 ebc72b71.
  - release_exclusions.json sha256 `d995e3ed05c2522f79460246a1475192411c3691b59e1e9aeceb3a877bf31da6`.
  - Coordinator condition 1 is met, so step 1 may run once the controls are verified.

## 8. Owner sheets (owner, 17 Oct: "when you are ready to show me first results do it")

Parameters are from the coordinator.

**Renderer.** `greekocr.adjudicate.owner_sheet.render(lines, spec)` (opus/cleanup-1 ≥ 994456de0). Run it under
`~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` with PYTHONPATH set to the cleanup worktree.

**Line dict.**
- `line_id`: the doc id (`line_id:s<slot>` when a slot is passed);
- `label`;
- `image`;
- optional `slots`, `clean_image` and `zooms` [{image, alt}];
- `rows`: [{name:'Google', text}, …]. The Google row is never empty; its text comes from W1 features `text`;
- `tags`;
- optional `printed`: prefill only from adjudicated truth, with the source recorded;
- `note`, `group`, `data`.

**Spec.** {title, intro, groups, sections}. Notes and Printed autosave to db collection `notes` (doc id = the card doc id).

**Publishing.**
- I publish myself, with the Artifact tool: capabilities {"db":{}, "user":{}}, icon "sheet".
- The title is two to four words; the description is one sentence.
- One artifact per track ("RU1 Hard Sign Decisions", "N1 Numeric Separators"). It is created once and always republished to the same
  URL, so the owner's notes persist.
- Each URL is sent to the coordinator once.

**Notes export.** Read with ArtifactData (collection `notes`) and export to jsonl, keeping every non-empty note or edited Printed.

**Building.** The HTML build is a Sol brief. The lead reviews it and publishes.

## 9. Owner feedback on the N1 sheet (17 Oct 16:47)

Notes: `elstat…l0648:s4` "missed first one", with Printed "7.504.643"; `bsb…l0039:s3` "arent the rest detected?". Chat:
1. **Raised dot.** "replacing with high dot instead of full stop is fine, it looks like that, although the intended use is full stop."
   - **Ruling:** the label keeps the printed raised dot U+00B7 (transcribe what is printed).
   - The owner's remark is recorded for downstream text normalisation: a thousands-separator · may be mapped to "." outside the OCR
     labels.
2. **Show all detections.** Every separator gap of every number in the line is drawn on the image, not one sampled gap.
   - **Change:** the N1 unit becomes the LINE. Every inner gap and boundary separator of every numeric token in it is enumerated,
     read and decided.
   - The step-1 frame's slot sampling stays only as the line-selection frame.
3. **"Ours".** The card carries our full proposed line text in the editable field, prefilled as a proposal with its source recorded.
   The owner overrides the "prefill only from adjudicated truth" convention for this sheet.
4. **Dash names.** Hyphen (-), en dash (–), em dash (—) and minus (−) are named and distinguished, so the owner can compare them with
   Google.
   - Dash type comes from ink geometry (dash length ÷ the token's digit width) cross-checked by the reader, which gets length options.
   - In labels, dashes stay tag-only until the owner rules on them.

## 10. RU1 re-check (17 Oct 17:02, sourcing lead; sol/recut-v1 50147b93 docs/records/harvest/recut_v1/w1_masked/ruc1/)

**Result.** 100 fresh ia_russian cards: letters 87, crop_ok 83. **The stratum still fails the gate.**
- **The RU1 repair holds:** 17/18 repaired cards are letter-correct. The 1 miss is a final ъ clipped at the crop edge, a crop fault.
- **Residual Google letter faults on unrepaired cards (12/82),** added as Russian classes in my scope:
  - **RU3:** the italic/variant т (printed in an m-like shape) labelled ш/п (ство→спво, стымъ→сшымъ, притворится→пришворится,
    то→по).
  - **Class 6 in Cyrillic:** Latin D/E written as Cyrillic Д/Е, and Cyrillic со- written as Latin Co-.
  - **Singles:** баталіи→баталіп, Россіи→Россія, 3→З, переселенные→нереселенные. Also Павловичъ→Павловить, where a ч→т error hides
    a word-final ъ.
- **Ownership.** crop_ok (15 clipped) is the sourcing lead's. ia_russian stays excluded.
- **Order.** RU3 and the Cyrillic lookalikes come after N1 and the punctuation classes, unless the owner wants Russian sooner.

## 11. Correction status table (coordinator, 17 Oct 17:37)

I own `docs/records/labelfix/CORRECTION_STATUS_20261017.md` for every non-accent class: per Google fault class, the measured rate, what
corrects it today, the signal needed and the next gated step.
- It is Sol-built from existing measurements only (C1, N1/RU1, E3, the owner sheets).
- The polytonic-marks rows come from the spell-check lead by reference.
- It feeds the correction column of the sourcing lead's WEAK_CATEGORY_LEDGER.md.
- The first version follows N1-T; the table is kept living after that.

## 12. Deferred (coordinator ruling, 17 Oct 22:26; low priority, not tonight)

**Cited renders may be deleted** once their receipt is amended to status "regenerable" with an exact recipe: the source crop id and
sha, the geometry, and the renderer version. A test must prove that re-rendering reproduces the cited sha byte for byte; the sha stays
the citation.
- Apply this to the N1 renders when convenient.
- Keep every file whose reproduction is not proven.

## 13. Programme re-cut (owner, via the coordinator, 17 Oct 22:31): binding order

1. **ru1_v2_train** on the v2 Cyrillic training rows: register it in the LQB, then hand it to the coordinator for wave 1c.
2. **The N1 rule at release scale.** The ink test from glyph geometry, with a per-slot decision record; the locked eval (the
   n1_locked_eval lines); the gate (≥99% raised-vs-hyphen precision, 0 false edits on ranges). Then **n1_v1_train** over all numeric
   tokens of the v2 training rows, the LQB delta, and the hand-off.

**PARKED** until both are in wave 1c: capitals, punctuation, superscripts and rare glyphs, lookalikes, misprints, RU3, RU2.

## 14. RU1 outcome and standing instructions (coordinator, 18 Oct 09:51)

**Wave 1c re-scored on ru1_v3_test_edits** (no retrain). Details: `greek-page-ocr-wave1c/out/e4/wave1c_rescore/E4_WAVE1C_RESCORE.md`.

| Measure | Control | With RU1 labels |
|---|---|---|
| CER on the 135 changed-label test rows | 1.68% | 1.25% (all lc seeds below the control minimum) |
| ъ emitted at the 144 corrected positions | 104/144 | 127/144 |
| Cyrillic class CER | 1.199 | 1.174 (−0.026 pp, inside the control range) |

H6 stays REFUTED by the preregistered class rule. The fault touches about 0.2% of Cyrillic characters.

**Reading.** RU1 is validated as a label tool (it fixes what it targets, with no harm elsewhere). It is not a lever on class CER.

**Standing instructions.**
- Produce ru1/n1 versions **edits-only** for new collections: ru1 over the W2 Serbian/Russian rows once W2 admission exists, and
  n1_v1_w2.
- Register train AND test counterparts by default.
- No further RU experiments.
