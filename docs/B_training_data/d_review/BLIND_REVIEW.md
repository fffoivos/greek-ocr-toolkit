# Blind pixel adjudication

`greekocr/adjudicate` is an additive offline package. It unifies new deck construction and resolution without silently redirecting old builders or upgrading historical reader results. Blind decks establish printed observations; owner sheets expose tool outputs and owner decisions. The latter deliberately show Google/tool texts and therefore are not blind decks.

## Build a public deck and a private key

`deck.build_deck(spec)` takes `blind_dir`, optional sibling `private_dir`, `items`, `controls`, `seed`, `profile`, and `control_fraction` (default **0.08**). Every new shared-package deck requires **two independent readers plus an independent tiebreak for disagreements**. Controls require `pixel_verified:true` and literal `known_answer`; optional `expected_fields` validate structured observations. A control is not verified merely because its proposed answer is in a key.

Each item supplies a native local `image`, optional `line_image`, `bbox` or exact `crop_box`, literal `options` and private provenance. `free_text:true` permits no options. New public cards use opaque positional `item00000`-style IDs, shuffled item/control positions and shuffled option meanings. This differs from the Sol-reading pack convention of fresh `k`+10-hex IDs; neither identity convention authorizes sharing source IDs.

| Profile | Pixels supplied |
|---|---|
| `letter`, `word`, `mark` | Full native line height; horizontal padding 0.6× native height around target bbox; ≤3× LANCZOS with 900 px width cap |
| `line`, `page` | Native-size view by default |
| Explicit `crop_box` | Sealed bounds, no automatic padding; geometry must remain inside the native image |

There is a code-level exception to the simple ≤3× profile summary: when a `mark` record supplies `word_box` and `letter_box`, `build_deck` calls `mark_views` and emits a 3× word plus an **8× nearest-neighbour letter view** as `mark_img`. `tests/adjudicate/test_sr1.py` checks that view's native pixels. The package README's generic ≤3× description is incomplete for this optional path; the code wins. Do not confuse this pre-rendered letter view with permission for a reader to fabricate new crop geometry.

Images are encoded without metadata, named `img/<sha256(encoded_png)>.png`. Profile crops convert to RGB; line-image emission handles palette images explicitly. These are native-derived pixels, not a promise of original PNG byte equality. Geometry, source bindings and image maps stay private. A text/path/PNG-metadata leak scan checks public files; caller-supplied `forbidden` strings extend it. Native printed text can itself identify a source, so this is not semantic anonymization or an OS access-control boundary.

Output includes `items_blind.json`, `reader_2.json`, images, viewer, instructions and answer schema; the sibling private tree holds the key and receipt. Existing blind destinations and existing private keys are refused. The key is exclusive/write-once. `protocol:historical` plus `preserve_order:true` explicitly labels replay of old position/options/control order; it is not the new-deck default. R0 replay regenerates target pixels from native full-line rasters and sealed crop geometry.

## Independent reading and resolution

`protocol.INSTRUCTIONS` tells each reader to open only assigned items/images, read literal case/script/punctuation/marks, and return `{id,answer,printed,confidence,note}`. Confidence is `high|medium|low`. An option is never presumed true; `literal` carries a full transcription, `unreadable` preserves unknowns, and ∅ denotes no printed text/sign. Reader 2 follows the code-emitted exact reverse order; the viewer can select reader 2 with `?reader=2`.

`adapt_answer` validates canonical/R0/S8/R2C aliases. It rejects conflicting aliases or a literal transcription contradicting an offered-option choice. S8's legacy boolean uncertain maps to low/high only when confidence is absent; numeric confidence is not silently reinterpreted. R2C retains explicit readability, ownership and breathing/accent/diaeresis/subscript heads. Unknown heads remain unknown, never negative examples.

`resolve(deck,keys,r1,r2,...)` checks exact identity, full assigned coverage and order, then gates controls **before** truth resolution. Default `max_errors` is **0**, `no_shared_misses` is **true**; explicit `min_correct`, `expected_controls` and historical sample/rate settings are supported. Do not substitute a track's “at most one wrong” policy for this default.

Agreement supplies two literal votes. Disagreements receive `tiebreak_deck`: fresh positions, changed multi-option order, controls and a private map to original IDs. A third answer is decoded with its own options/map, never the old option letters. It must cover exactly disagreements plus controls and pass its gate with the initial readers. A failed initial reader cannot be discarded and rescued by counting the third as a new two-reader consensus. Unknown or unresolved observations remain UNKNOWN. Structured R2C truth also requires appropriate ownership/readability/head agreement; matching strings do not license known heads when those observations are unknown.

`controls_gate(...,readers=1)` describes historical C1 gates, including `allow_no_controls`, exact/minimum sample sizes and minimum rates. It does **not** authorize a one-reader new shared-package deck; `resolve` rejects that reduction. The qualified one-reader Sol tasks described in its separate HANDOVER remain historical/task-specific evidence, not a blanket relaxation.

## Custody, exports and scoring

`deal_batches` copies public assignments/images into isolated new reader folders, splits into matching batches then reverses reader 2 within each batch. Its receipt binds source manifest, IDs/order, every file hash and leak scan. It does not revoke the reader process's other filesystem access.

`batch_check` validates a dealt immutable assignment against its hash receipt, exact answers and private key coverage, using a dry-run resolver interface. It mirrors a single answer batch only for validation and explicitly returns `independent_readers:1`, `truth_written:false`. This is not independent agreement. Answer output must be outside that immutable tree; Sol-reading packs have a different convention allowing `answers.jsonl` within a manifest-audited reader tree.

`artifact_custody.copy_artifacts(source,destination,paths)` copies an explicit relative selection, refuses symlinks/overwrite, rechecks source hashes after copying, verifies exact destination file set/bytes, and atomically publishes the new **local tree** with `custody_manifest.json`. This operation is not claude.ai publication. `verify` repeats the exact file-set/hash comparison.

`protocol.write_truth` requires a passing initial control gate and writes JSONL or deterministic gzip (`mtime=0`) exclusively, retaining UNKNOWN, all reader observations, verdict/status and `control:false`. Controls do not enter data truth. `owner_notes_export` separately joins a supplied artifact dump to sheet/card identity with explicit note-status conventions; it does not generate print truth from notes.

`score.py` owns the statistics re-exported by `protocol.score`: weighted event ratio, fixed inclusion weights, document/line-cluster bootstrap (**4000** replicates by default), and Wilson-Kish fallback for degenerate document intervals. It reports raw/weighted numerators and denominators, cluster counts and both bootstrap intervals. Wilson uses **z=1.959963984540054**; `clopper_pearson_lb95` is the exact **one-sided 95%** lower bound. The boundary Wilson fallback ignores clustering and is diagnostic. These functions estimate outcomes after truth/custody decisions; they do not adjudicate pixels or prove a release gate passed.

## Sol scanner v4.5.5 and Opus/owner residual

The Sol canonical source on this branch is `docs/records/harvest/sol_reading/tools/scan_rollout.py`, reporting **4.5.5**. Its file SHA256 was read in this documentation pass:

```text
e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1
```

That matches `HANDOVER.md` and `out/scan2f/HANDOFF.md`. `tools/SCANNER_CANONICAL.json` still names v4.4 with `dd2fc59d…`; `SCANNER_V45_NOTES.md` records the earlier v4.5. These are historical/stale distribution records, not the current code identity. Copy by the verified canonical hash; do not fork a scanner to pass a run. See [AGENT_READERS.md](AGENT_READERS.md) for the actual input/provenance/VOID contract.

Common pitfalls are unresolved path templates or loop-generated image paths; looking at sibling keys/reader answers; incomplete image coverage; treating a final zoom file as evidence of what an earlier overwritten view contained; and accepting restored helper bytes without chronological source authority. V4.5.5 invalidates cached scripts on every execution-unit write barrier, including rejected/unknown writes. Its recorded P1 answer-argv, P2 proven-downscale and P3 finite-template rules are narrow proofs, not general exemptions. `docs/records/contexts/CONTEXT_20261019_spellcheck.md` records a remaining JS literal-array loop issue/follow-up v4.5.6; this branch's inspected canonical source remains 4.5.5.

Task assignment is evidence based. `HANDOVER.md` qualified Sol for letters/crop line checks and a separate final-accent word question; it did not qualify whole-line Sol marks (missed 3/3 printed-grave/label-acute errors) or four-head R2 word marks (assigned to Opus). New two-reader decks retain independent contexts and controls regardless of reader brand. Opus is not automatically truth: disagreement, unreadable calls and control/custody failures still route to independent tiebreak/lead pixel review and ultimately owner review or HOLD.

The SF7 context pack records **70/70** eligible accent lines from a valid Sol context, but a capital context VOID three times and **30 lines** needing Opus two-reader cards (23 pending heads + 7 unresolved capitals). That is a recorded pending audit, not completed Opus evidence or release authorization. Its manifest remains `candidate_pre_audit`. The owner review is the residual decision surface; prior judgments should be carried visibly rather than requested again.

## Receipts and limits

| Receipt / tests | What it establishes |
|---|---|
| `docs/records/cleanup_20261017/CLEANUP_STEP4_REPORT.md` | Historical additive CU4: zero content differences for 39-card held-out sheet, 100-card audit and 336-card R0-ib; 24 focused tests passed; broader 4718 passed with 5 failures/6 errors/19 skipped retained |
| `tests/adjudicate/test_deck_protocol.py` | Profile/pixel/metadata checks, sibling exclusive key, shuffled controls/options, reverse order, controls-before-truth, fresh tiebreak mapping, UNKNOWN, adapters and structured heads |
| `tests/adjudicate/{test_score.py,test_sr1.py}` | Statistical parity and custody/batch/export coverage (not independent pixel truth) |
| `out/scan2f/{HANDOFF.md,verification.json,SOURCE.json,tests_final.log}` | Recorded v4.5.5 qualification: 107 tests, zero skips, six historical witnesses; overwrite probes stay VOID |
| `out/scan2/rescan_v455.json` | Recorded 15/15 CQ4 rescans VALID; preserved prior ledgers/receipts, no answer scoring or reader rerun in SCAN2F |
| `docs/records/harvest/collect_v3_admission/segeval1/{SEGEVAL2_HANDOFF.md,SEGEVAL1_RESULT.md,segeval2_verification.json}` | Two existing contexts VALID under pinned v4.5.5, controls 10/10, original four-question FP 29/50 and FN 5/100; original v4.4 scoring retained |
| `docs/records/labelfix/spellcheck/R2/R2C_REPORT.md` | R2 deck preparation and later resolver/dry-run evidence; an initial proposed control is not lead-verified truth |

The two SEGEVAL contexts divide the study, rather than being two independent readings of every card; the report calls them two existing blind reads. Keep that historical task distinct from the shared package's new two-reader-per-item contract. The later gate2/S4 confusion matrices add saved error categories and use a different definition; do not splice their scores into the original four-question result.

No tests, rescans, exports, model calls or pixel adjudication ran for this documentation task. Test/scoring receipts demonstrate their stated boundaries, not OS isolation, unseen-data generalization, current live DB state or visual correctness of every crop.

## Sources read

- `greekocr/adjudicate/{README.md,deck.py,protocol.py,deal_batches.py,batch_check.py,artifact_custody.py,owner_notes_export.py,score.py}`
- `greekocr/adjudicate/mark_profile.py`
- `docs/records/briefs/CU4_adjudicate.md`
- `docs/records/cleanup_20261017/CLEANUP_STEP4_REPORT.md`
- `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_blinding.md`
- `tests/adjudicate/{test_deck_protocol.py,test_score.py,test_sr1.py}`
- `docs/records/harvest/sol_reading/{HANDOVER.md,SCANNER_V45_NOTES.md,tools/SCANNER_CANONICAL.json,tools/scan_rollout.py}`
- `out/scan2f/HANDOFF.md`
- `out/scan2f/{verification.json,SOURCE.json,tests_final.log}`
- `docs/records/harvest/collect_v3_admission/segeval1/{SEGEVAL2_HANDOFF.md,SEGEVAL1_RESULT.md,prompts/owner_rubric.md}`
- `docs/records/harvest/collect_v3_admission/segeval1/{segeval1_score.py,segeval2_verification.json}`
- `docs/records/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md`
- `docs/records/contexts/CONTEXT_20261019_spellcheck.md`
- `docs/records/labelfix/spellcheck/R2/R2C_REPORT.md`
- `docs/harvest/line_pipeline/tool_versions.json`
