# E-build / E-build2 reader packs

Build only. No readers have been run and there are no experimental quality or efficiency results yet. All writes for these builds are under this directory. The live `collect_v3/` package is never imported or modified. Network access was not used. Both builds inherited nice priority +5. E-build image processing ran serially with ImageMagick limited to one thread; E-build2 uses serial Pillow rendering. E-build2 extends commit `b8658ae0`; existing BSB/yer packs and bed keys are byte-unchanged, and their scorer behavior is checked against that commit.

The original BSB and yer beds have 10 independent reader folders each (20 total). In each original bed, E0a, E0b, E2 and E3 have two readers; E1 and E4 have one. Every item appears exactly once in every original-bed arm. The BSB split is 50/50 and the yer split is 30/29. E0a and E0b contain identical item sets in different seeded orders. Keys record `eff:<bed>:<arm>`, the exact order, and assignments. Owner39 adds eight folders, for 28 total; its two readers both read every card, as detailed below.

| Arm | Input and protocol |
| --- | --- |
| E0a, E0b | Original full-line crops; byte-identical control protocol |
| E1 | All items in one context; byte-identical control protocol |
| E2 | Word crops at 3x; glyph close-ups at 8x; only the control's input-image sentence changes |
| E3 | Compact instructions once, with one minimal JSONL line per item; all rules retained |
| E4 | E1 and E3 combined |

For BSB, E2 includes every transcribed word and every nonspace glyph, including punctuation. This avoids selecting interesting glyphs using reference answers. For yer, E2 includes only the word holding each masked slot and its final alphabetic glyph, with following punctuation excluded from the close-up. The image paths are ordered word then glyph(s). No E2 folder contains a full-line image. The existing whole-line checks remain in the protocol, as required. In particular, yer's zero-slot items have no E2 images, so the retained unmarked-hard-sign and pre-1918 checks lack line-wide evidence in that arm. These are experimental limitations to measure, not grounds to change the rules or declare an arm adopted.

All crop paths are relative to the reader's items file, making each folder relocatable. The unchanged yer control protocol still calls its `crop` field an absolute path; relocation to a relative path is the sole shared packaging convention across all yer arms. Start the reader in its folder so the path resolves directly. BSB files are `cards.jsonl`; yer files are `items.jsonl`; both use `PROTOCOL.md`.

## Reader hand-off

Give each reader only its own `packs/<bed>/<arm>/<reader>/` folder, its protocol, and an OUT/zoom location outside the pack. Keep the pack immutable. Do not expose this README, `MANIFEST.json`, `keys/`, scorer files, QA files, other arms, reference outputs, or the worktree root to the reader. No keys, truth, reference verdicts, source paths, or links occur inside a reader folder or its immediate parent. This is a checked file-layout boundary; it is not an operating-system sandbox against arbitrary traversal of a shared filesystem.

Use a fresh reader context for each folder. E1 and E4 deliberately process their full bed in one context. Reader execution and the final adoption decision remain with the owner; this build supplies no evidence of no quality loss.

## E2 geometry and approximation

BSB source rows were matched by copied-crop SHA256, without opening the BSB key. Yer source IDs came from its adjudication mapping and its C1/earlier-v2 mapping, used only for construction. Earlier-v2 rows and saved responses were found locally. The private source index and source hashes are under `keys/`.

Response transforms are inverted into the native page frame before selecting tokens fully inside each row's `crop_bbox`. Dropped assembly tokens are excluded. Tokens are aligned to the unchanged machine text; symbol boxes supply glyph geometry. Each box is translated/scaled into the existing crop frame, padded by one native crop pixel for words or two for glyphs, and clamped to the crop. ImageMagick resizes these rectangles to exactly 3x/8x; it never synthesizes ink. The key records every resulting rectangle and scale.

E2 uses measured boxes for all 100 BSB items and 58/59 yer items. Yer `a020` has saved tokens, but the tokens fully inside its crop do not align with the supplied transcription; complete aligned token geometry is therefore unavailable. As required, this item uses character-count subdivisions of the whole line box and `approx_box=true`. Its final-letter boxes are approximate too. The receipt lists this reason separately from a wholly missing response.

- BSB: 0/100 approximated (0%).
- Yer: 1/59 approximated (1.694915%).
- Combined: 1/159 approximated (0.628931%).

There are no additional approximated glyph-only items. `keys/e2_approximation.json` lists all affected IDs. The fallback is visible in the key only and is not disclosed as an answer cue to a reader.

`MANIFEST.json` binds all 6,558 pack files, including 6,486 PNGs, to their SHA256 and size. The original beds account for 5,920 files/5,880 PNGs; owner39 adds 638 files/606 PNGs (shared native lines are deduplicated within each reader folder). Each reader entry states item count, IDs, factor, and copied-crop hashes. Full-line copies in the original beds are bound to their original hashes; derived crops are bound to their source-crop hash and detailed geometry. PNGs are ignored by Git. Keep the built folders on disk or transfer them separately: a text-only checkout does not contain the images.

## Owner39: R2 practice extension

This is exposed evaluation material. Its private truth snapshot, source joins, owner note and scoring outputs stay under `keys/` or coordinator-only output locations. Readers receive only their own copied `packs/owner39/<arm>/<r1|r2>/` folder. Each contains `PROTOCOL.md` (the prompt to deliver), byte-identical R2 T2 `README.md` and `answer_schema.json`, `cards.jsonl`, and `img/`. The T4 prompt retains its literal `<BATCH_DIR>` placeholder and reader-2 clarification. Deliver that prompt with the assigned folder as the working directory; reader 2's `cards.jsonl` is already reversed, so no `cards_reverse.jsonl` is needed. Reader-created `answers.jsonl` and `zoom/` are permitted by the unchanged prompt during execution, after the build hand-off; the frozen pack validator intentionally rejects such additions to the build artifact.

Each of E0a, E0b, E2 and E3 has two independent readers, each assigned all 39 cards: 78 card-reads per arm, 312 in total. Reader 1 uses `random.Random("eff:owner39:<arm>").shuffle(sorted(opaque_card_ids))`; reader 2 uses its exact reverse. E1 and E4 do not apply because 39 cards are smaller than one practice batch. No controls, third-reader adjudications, or experimental outcomes have been invented for this fixed 39-card bed; the T4 prompt and README keep their practice rules verbatim.

| Arm | Owner39 input and prompt |
| --- | --- |
| E0a, E0b | R2 T4 reader prompt verbatim; uniform integer 1–3x LANCZOS word zoom and full native line |
| E2 | Only the word crop at 3x LANCZOS and the letter close-up at 8x NEAREST; only the native-line input-image sentence in T4 changes |
| E3 | Instructions once in a shorter prompt, every rule retained; minimal JSONL item lines and the same images as E0 |

`build_owner39.py` **ports** the R2 `render_deck` RGB/native and integer-scale word-rendering block and six pure Unicode/option helpers from `r2_cards_prepare.py`; it never imports or executes that source module. Supplied `word_bbox` x-ranges get ±6 native pixels of context and full line height. The scale is `max(1,min(3,floor(min(3,1200/width))))`. E2 ports the exact `build_r1a_errors.py` word/letter formulas: word x-range ±6, full height, 3x LANCZOS; letter x-range ±`max(6,(x1-x0)//2)`, full height, 8x NEAREST; both ranges are clamped to the line. These are native raster crops, with no ink synthesis or approximate boxes. PNG metadata is removed without changing RGB pixels; files use content-hash names and independent copies, with no symlinks or hardlinks. All spell-check worktrees remain read-only.

E2 loses the full native line, neighbouring words beyond the word-crop margin, and line-wide evidence for mark ownership, cuts and context. The R2 README and every other prompt instruction remain unchanged, including the ownership requirement; that loss of evidence is part of the experiment.

Public card fields match R2: opaque `card_id`, `word_image`, `line_image`, `anchor_index`, `anchor_base`, `options`, `extra_options`. E2 replaces `line_image` with `letter_image`. No source IDs/paths, truth forms or labels, section, owner note/status, Google/reader words or error framing are copied into cards. Options use only the source word's stripped base letters and punctuation, and the same fixed accent-head variation for every card; option selection never depends on owner marks. As in R2, an unlabelled generated option can naturally coincide with a printed form. `literal` remains available for the complete word. There are no repeated-view cards in this bed.

The isolation check covers folder closure, immediate-parent contents, copied-file/link status, exact public fields, paths, private source IDs and actual owner-note text, metadata-free PNGs, dimensions, hashes, and seeded/reverse orders. This is the same checked delivery boundary as the original build: hand over an isolated copy of the individual reader folder, never the worktree or this coordinator directory. It is not an OS sandbox against arbitrary access to a shared disk.

`verify_owner39_rasters.py` independently checks all 156 card/view rasters: E0 against the five read-only rendering statements extracted from the original R2 renderer's AST, and E2 against the owner-page formulas. Every RGB pixel matches. Three private construction panels, including the noted card, were visually inspected; receipts and image hashes are in `keys/owner39/raster_receipt.json`. This verifies construction, not reading quality.

## Scoring supplied outputs

Use Python 3.10 or later. The scorer, validators and unit tests use the standard library. The original builder additionally needs ImageMagick; the owner39 builder and raster verifier need Pillow. On this Mac, the installed Python 3.11 Pillow is x86_64, so owner39 rendering/QA ran with `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`. Both builders refuse to overwrite completed packs. Neither has a network or live-pipeline dependency.

Reader verdict files are arguments, never placed into the packs. The two C1 BSB reference partitions and the two ink partitions were normalized into `keys/truth.json`; table.json and ink slot calls were cross-checked at build time. Optional external truth arguments are checked against that fixed snapshot.

Example for one submitted reader (other arms/readers remain explicitly missing):

```sh
python3 -B docs/records/harvest/collect_v3/c1/efficiency/score.py \
  --verdict bsb E1 r1 /path/to/bsb_E1_r1.jsonl \
  --output docs/records/harvest/collect_v3/c1/efficiency/scores.json
```

`keys/verdicts.template.json` lists all 28 expected outputs. Replace its paths with your actual output paths, or put the files at the indicated locations, then run:

```sh
python3 -B docs/records/harvest/collect_v3/c1/efficiency/score.py \
  --verdicts docs/records/harvest/collect_v3/c1/efficiency/keys/verdicts.template.json \
  --usage docs/records/harvest/collect_v3/c1/efficiency/keys/usage.template.json \
  --output docs/records/harvest/collect_v3/c1/efficiency/scores.json
```

Fill every usage template value from measured reader usage first. Its initial nulls are intentionally rejected; they are not estimates. Alternatively supply a JSON mapping:

```json
{"bsb/E1/r1":{"total_tokens":12000,"tool_uses":100,"duration_ms":600000}}
```

Those numbers illustrate the schema only. A `{"readers":[{"bed":"bsb","arm":"E1","reader":"r1","total_tokens":12000,"tool_uses":100,"duration_ms":600000}]}` list is also accepted. Duplicate/unknown reader usage, negative/nonfinite values, and fractional token/tool counts fail validation. Omit `--usage` to leave all costs null. Arm totals stay null until every reader's usage is supplied; measured individual-reader values remain available.

Repeat `--bsb-truth PATH` for the two C1 reference files, and `--yer-truth PATH` for the two ink files, if scoring against the originals explicitly. `--yer-table PATH` optionally rechecks the table. All are local reads.

The JSON report contains each arm's BSB letters/crop_ok/marks equality and joint per-card equality, or yer slot equality and per-item equality. It also reports agreement with E0a, E0a–E0b agreement, paired better/worse truth outcomes versus E0a, u/other counts, confidence counts where reported, and missing items/slots. Zero-slot items count toward item completion but never inflate slot accuracy. Rates use explicitly stated compared denominators; expected and missing denominators are retained, so partial output cannot masquerade as complete.

Usage gives measured tokens, tool calls and reader wall milliseconds per assigned card. The arm wall metric sums reader durations; it cannot infer concurrent elapsed makespan from the supplied fields. The scorer does not estimate usage, apply a quality gate, or claim statistical equivalence. Duplicate IDs, wrong-reader IDs, unknown IDs, missing/extra slot calls, and invalid calls fail with exit status 2.

Owner39 accepts the unchanged R2 answer schema, resolving option choices or literal transcription into the anchor's base letter and four mark heads. Known heads must agree with the transcription. `unknown` is an unconfirmed head, never `none` and never credit for an inferred form; it remains in the compared denominator and is counted separately. Unknown/unknown is reported as literal call agreement but not confirmed agreement. `unreadable` supplies an unknown base and four unknown heads. Missing cards/readers are explicit and do not receive accuracy credit.

Owner accuracy covers the **one confirmed anchor slot per card**. The 38 `left_as_shown` cards use the accepted base/mark tuple; `384c3f89-p000059-l0013:s33` uses circumflex accent with breathing unknown and excluded. Thus each complete reader has 39 base/accent/diaeresis/subscript comparisons and 38 breathing comparisons. Other `letter_heads` are checked for valid indexes and consistency but not assigned new truth. Punctuation, ownership, readability and confidence have no owner truth and are not accuracy targets. Complete-word transcription is used to locate the anchor base; whole-word exact accuracy is not claimed.

The owner39 report retains r1 and r2 separately, with per-card and per-head owner agreement, matched-reader agreement with E0a, E0a–E0b agreement for each reader, and agreement between the two readers in each arm. No majority or resolver outcome is inferred. Confidence/readability distributions and unknown counts are separate from accuracy. Measured cost is given both per card-read (`tokens_per_card`, denominator 78 for a complete arm) and per unique card (`tokens_per_unique_card`, denominator 39, covering both reads), with analogous tool/wall metrics. Arm totals remain null until both readers supply measured usage. The R2 answer's required `usage={"input_tokens":0,"output_tokens":0}` values are placeholders and never used as measurements.

For a supplied owner reader, for example:

```sh
python3 -B docs/records/harvest/collect_v3/c1/efficiency/score.py \
  --verdict owner39 E0a r1 /path/to/answers.jsonl \
  --usage /path/to/measured_usage.json \
  --output docs/records/harvest/collect_v3/c1/efficiency/scores.json
```

## Validation and commit hand-off

```sh
python3 -B docs/records/harvest/collect_v3/c1/efficiency/validate.py
python3 -B -m unittest discover -s docs/records/harvest/collect_v3/c1/efficiency -p 'test_*.py' -v
python3 -B docs/records/harvest/collect_v3/c1/efficiency/guard_commit.py
```

Validation checks complete pack closure, no links or external image paths, immediate-parent isolation, every manifest hash, source-copy hashes, IDs/orders/assignments, and every derived raster's dimensions. The tests cover all original 33 checks plus owner39 prompt/schema identity, two-read assignment, privacy, the owner exception, unknown handling, measured costs, negative cases and exact original-scorer regression. `TEST_RESULTS.txt` records the combined suite. Original QA remains in `BUILD_RECEIPT.json`; `BUILD2_RECEIPT.json` records the extension and private owner39 QA. These are construction checks, not reader adjudication.

The sandbox cannot write `.git`, so nothing was staged or committed. `COMMIT_FILES.txt` is the exact changed/new non-PNG commit list relative to the bound HEAD; unchanged files from E-build are not staged again. `COMMIT_SHA256.json` binds the complete non-PNG tree as well as that delta list. The read-only guard checks HEAD/branch, the exact commit delta, outside-scope changes against the E-build2 prebuild snapshot, live source hashes/mtimes, frozen BSB/yer pack/key bytes, owner39 source hashes, candidate hashes, and all packs. The repository already had unrelated modifications, which are preserved and excluded. The original prebuild snapshot and build receipt are retained.

After a successful guard, an operator with Git-write access can run the following from the repository root:

```sh
git add --pathspec-from-file=docs/records/harvest/collect_v3/c1/efficiency/COMMIT_FILES.txt
python3 -B docs/records/harvest/collect_v3/c1/efficiency/guard_commit.py --staged
git commit -m "Extend adjudication efficiency experiment with owner39 R2 reader packs"
```

The staged guard requires exactly the listed paths and verifies each staged blob against disk. Do not commit if either guard fails. Later reader outputs or score files are outside this frozen commit list and require a fresh review.
