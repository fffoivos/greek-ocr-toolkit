# Data contracts (FROZEN v1 — 2026-07-06)

These interfaces are frozen before any implementation. The Rust factory (`factory/`), the training
stack (`train/`), and evaluation all build against this file. Changing anything here bumps the
codec/schema version — never edit in place after data exists.

## 1. Codec v1 (`codec/v1.json`, emitted by `linefactory codec-emit`)

- **Normalization:** ground truth is stored and encoded in **NFD** (Unicode canonical decomposition,
  canonical ordering). Rendering uses NFC (fonts carry precomposed glyphs); labels never do.
- **Atoms:** one class per NFD codepoint. Kinds: `base` (letters incl. ς, ϝ, ϙ, ϡ), `mark`
  (combining: U+0300 grave/varia, U+0301 acute/oxia, U+0342 perispomeni, U+0313 psili, U+0314 dasia,
  U+0308 dialytika, U+0345 ypogegrammeni, U+0304 macron, U+0306 breve, U+0302 circumflex, U+0303
  tilde, U+0327 cedilla, U+030A ring, U+030C caron), `digit`, `punct` (incl. Greek ano teleia U+0387,
  guillemets, dashes incl. U+2014, apostrophes incl. U+1FBD/U+02BC as normalized), `space` (U+0020
  only; all other whitespace folds to it), `sym` (minimal: % § † ‡ * / = + °).
- **Scripts covered:** Greek (mono+polytonic bases identical after NFD), Latin (en/fr/de/it/es
  coverage via marks), Cyrillic (ru/uk).
- **Encoding:** `encode(text) = map(normalize_gt(text))`, `normalize_gt` = NFD + whitespace-collapse +
  the enumerated G0-3 folds below; any unmapped codepoint ⇒ the LINE is rejected at corpus ingest
  (accounted per source, never silently). **No case folding, and no *general* confusable folding** —
  cross-script homoglyph contamination stays a quality gate at ingest, NOT a codec fold.
- **G0-3 canonicalization (owner decision 2026-07-07; part of codec v1, `factory/src/codec.rs::normalize_gt`,
  rev H F10 reconciliation).** A *narrow, enumerated* set of Greek-internal typographic-variant folds is
  applied in-codec (this is deliberately NOT the "general confusable folding" the line above forbids):
  U+02BC modifier-apostrophe / U+1FBD koronis / U+1FBF psili → U+0027 `'`; U+03F2 lunate sigma → U+03C3 σ;
  U+1FFE spacing-dasia and U+0384 spacing-tonos → dropped (spacing-accent artifacts). G0-3 also added
  € £ as `sym` atoms (real modern-text currency). These are frozen in **v1** (247 atoms + blank = 248
  classes); any change requires a **v2 version bump**, guarded by the codec-lint test (no new decomposable
  atom may be emitted, `codec.rs` tests). Known residue: U+0407 is a dead atom (S15b) — retire at the v2 bump.
- **Mark order rule (D-4a):** NFD canonical ordering is the ONLY order; equal-ccc sequences
  (breathing+accent, both ccc=230) keep NFD-normalized source order. Scorer default = strict;
  lenient mark-set diagnostic is reported separately.
- **IDs:** `0` = CTC blank, `1` = space, then atoms sorted by (kind, codepoint), contiguous. The
  JSON is the artifact of record: `{"version":"v1","blank_id":0,"atoms":[{"id":..,"cp":"U+03B1",
  "ch":"α","kind":"base","script":"grek"},...]}`.

## 2. Strip contract

- Grayscale, 8-bit, **height = 48 px** exactly; ink nominally dark-on-light (polarity is a recipe
  distribution, recorded per strip).
- Width: proportional to text, clamped to **[64, 2560] px** (`MIN_W`/`MAX_W`). WIDTH POLICY (rev H
  F10 — one policy, matching the implementation `factory/src/render.rs`, `composer.rs` and
  `pipeline/strips.py`): an over-wide line is **letterboxed** — the ink is shrunk (aspect preserved,
  never squeezed, never clipped) until it fits `MAX_W`, down to a **14 px ink readability floor**.
  Only a *pathological* line that cannot reach `MAX_W` even at that floor is **dropped and accounted**
  (never silently). During page composition, over-wide lines have trailing words trimmed to fit. So:
  over-wide ⇒ letterbox; sub-floor pathological ⇒ accounted drop. (The earlier "longer renders are
  rejected" wording is superseded — the pipeline letterboxes to match inference-time band resizing.)
- Model stride contract: **timesteps T = ceil(width / 4)**. Training pads right with the strip's
  own background level to the batch bucket width; `input_length` = pre-pad T.
- Batch padding (WP-A F1, deterministic own-bucket): a batch canvas = (batch-max width + 128 px),
  and EVERY strip (incl. the batch-widest) is right-padded with ITS OWN background to fill it
  (`DET_PAD_MARGIN`=128 >= recognizer conv RF ~110px). This makes a strip's reading deterministic
  regardless of batch composition. `pipeline/recognize.py` + `train/data.collate_strips` both do this.

## 3. Shard schema (Parquet, written by the factory, read by train/)

One row per strip. Columns (exact names/types):

| column | type | note |
|---|---|---|
| `image_png` | binary | PNG-encoded grayscale 48×W |
| `width` | int32 | pre-pad pixel width |
| `gt_nfd` | utf8 | label of record (NFD) |
| `gt_nfc` | utf8 | display/render form |
| `label_ids` | list<int32> | codec v1 ids — training reads THIS, never re-encodes |
| `codec_version` | utf8 | "v1" |
| `script_class` | utf8 | `greek_mono` \| `greek_poly` \| `greek_latin_cs` \| `latin` \| `cyrillic` \| `furniture` |
| `split` | utf8 | `train` \| `val` \| `reserved` (never-trainable band) |
| `severity` | int32 | 0–3 |
| `applied_ops` | list<utf8> | distortion op names actually applied |
| `font` | utf8 | font file stem |
| `polarity` | utf8 | `dark_on_light` \| `light_on_dark` |
| `bg_type` | utf8 | `flat` \| `gradient` \| `textured` |
| `accent_survival` | float32 | mark-ink survival ∈ [0,1]; 1.0 for markless strips |
| `reuse_index` | int32 | nth render of this line (0-based) |
| `line_id` | utf8 | xxh3_64 hex of NFD gt (salted) |
| `source_dataset` | utf8 | provenance ledger key |
| `source_doc_id` | utf8 | document within source |
| `license` | utf8 | SPDX-ish tag from the ledger |

Shards: `out/{train,val,reserved}/shard-NNNNN.parquet`, ≤4096 rows each; `out/build_info.json` +
`out/audit_report.json` + `out/select_report.json` are part of the dataset, not optional.

## 4. Split rule (deterministic, content-independent)

`h = xxh3_64(gt_nfd bytes, seed = xxh3_64("greek-page-ocr/v1"))`, `b = h mod 1000`:
- `b ≥ 985` → **reserved** (never-trainable band, 1.5%) — the standing leak-proofing pattern;
- `940 ≤ b < 985` → val (4.5%);
- else train.
Same text ⇒ same split, across builds, forever (per codec version). Eval sets are additionally
excluded by explicit exclusion manifests at select time (fail-closed if a manifest is missing).

**Rider — detector-crop automatic label repair (`crop.enabled`; repair is intrinsic to cropping, always
on when cropping runs; whole crop path default OFF).** The crop DEPTH is set by the recipe alone (never
bounded by accent legibility; letters are protected geometrically). When a crop destroys a diacritic, the
emitted `gt_nfd`/`label_ids`/`gt_nfc`/`gt_len` are re-derived from the *repaired* label, but the row keeps
its ORIGINAL provenance: `line_id` and `split` are the source line's (NOT recomputed from the repaired text),
and `script_class` is unchanged (a poly→mono repair is not reclassified — a small marginal-accounting
caveat). So for a repaired row `line_id != xxh3(emitted gt_nfd)` and `split != split_of(emitted gt_nfd)` —
the identities describe the *source* line, not the emitted label. `accent_survival` for a cropped row is the
pre-crop Photo survival × the geometric top-band retention (markless-after-repair ⇒ 1.0), so audits measure
the emitted image.

**NOT contamination (owner ruling).** A repaired training label that happens to equal a held-out eval line's
text is **not** a leak and gets **no guard**: the two are *different images* (the training image has a unique
crop that destroyed the accent; the eval image is clean), and it is a rare corner case (repairs fire ~never
at survivable maxima). The standard select-time text-exclusion for NORMAL, unrepaired rows is untouched and
remains the real anti-leak mechanism. (There is deliberately no `exclusion_belt` / split-band guard.)

**Eval splits are crop-free (schema invariant of `split`).** The crop augmentation is gated to `split=="train"`
rows in `build.rs`, so `val`, `reserved`, and `transfer_dev` (which renders `split=="reserved"`) rows render
**byte-identical to a crop-less build** even when `crop.enabled` — no crop, no repair, no RNG perturbation.
This keeps the retrain-vs-baseline eval a consistent clean instrument; a crop-robustness eval, if ever wanted,
must be a separate deliberately-augmented slice.

**Rider — lunate-sigma GT rewrite (`ink_transfer.lunate_sigma_fraction`; default OFF).** The lunate knob (I9-B
fix, `docs/reviews/ink_transfer_v2_design.md §10`) rewrites `σ → ς` in the row's GT so the rendered pixels AND the
emitted `gt_nfd`/`label_ids`/`gt_nfc` all use ς (**image == label** — a faithful old-orthography variant, never a
render/label mismatch). **INDEPENDENT distribution** (owner redesign 2026-07-14): `Job.lunate` is minted by a
*separate* rng draw from the degradation cohort (`Job.letterpress`) in `select.rs`, on a fraction of GREEK rows — so
**lunate ⊥ degradation** (a lunate row is degraded only at `cohort_fraction`, ~20%, not 100%; it is NOT a sub-fraction
of the cohort). A lunate row routes to a historical cut (shared with the cohort's routing) for the right ς glyph.
Three invariants: **(a) TRAIN-ONLY** — the rewrite is gated to `split=="train"` in `build.rs`, so eval splits (`val`,
`reserved`, `transfer_dev`) keep modern σ and stay a consistent clean instrument (Fable cert F1: an un-gated rewrite
silently edited 888 frozen-eval labels — fixed; verified 0 eval label edits by source-join). **(b) NOT contamination**
— the select-time text-exclusion runs on the ORIGINAL source text (catching original-text leaks before any rewrite),
but it is **σ-form-blind**: the rewrite can manufacture a `ς`-form train label that collides with a natural-`ς` eval
line the σ-form exclusion never matched. This is the SAME posture as crop-repair — a rewritten train label equal to an
eval line's text is not a leak (different *images*: a lunate-degraded historical render vs a clean eval render; and
the rows are different source lines). Empirically zero such collisions with the real-crop manifest today. The rewrite
does NOT change provenance.
**(c) OFF = byte-identical** — the mint's `> 0.0` short-circuit draws no rng when the fraction is 0, leaving the
degradation-cohort stream unchanged. Unlike crop-repair, the rewrite is deterministic per row (no accent destruction),
and provenance (`line_id`, `split`, `script_class`) is unchanged.

## 5. Standing rules baked in from the sibling program's failures (2026-07-05/06)

1. **No OCR-judge drop gate.** Legibility is guarded geometrically (ink-contrast floor +
   `accent_survival ≥ 0.5` with REPAIR = re-render milder, never silent drop). Any drop of any kind
   is accounted per (reason × severity × script_class × length-bucket) in the audit report.
2. **Reuse is hard-capped** (`reuse.max_per_line`, default 2) with NO bypass path. Class floors are
   met by SUPPLY or the build fails loudly listing deficits — never by extra reuse.
3. **Appearance band is measured, not declared.** `linefactory measure` computes the band from real
   page crops; the audit gates realized appearance against that band file (config-independent), not
   against the recipe.
4. **Pre-IPF diversity**: per-source / per-doc caps apply to the candidate pool BEFORE the marginal
   draw (so they cannot fight content marginals), and realized concentration is reported.
5. Naming: datasets/evals say what images ARE (`rendered`, `scan`, `photo`) — "real" alone is banned.

## Recipes of record

| version | recipe file SHA-256 (committed bytes) | dataset | custody |
|---|---|---|---|
| v1-final | `03c132afd4bd8198161b206884f7d601b764ac5de045bd51ab6671643a03214e` | strips_v4a | `factory/recipe.v1.json` |
| v5 | `2f228950e9a508b5e130e82ce5b89de2b911be4a23872c3acc7f53e83c59dce7` | distribution for subsequent builds | `73733d6` (C0 custody, installed in main ancestry) |
| v7 (eval-only) | `4fbf257172cab1255fd068e37b1a6cac11b5f2fb84ecce83da0136a9150fb87f` | E1 clean synthetic held-out (held-out fonts; polytonic ≥300, Cyrillic ≥300) | this commit |

v6 → v7 (eval-only, 7 Oct 2026): identical to v6 except content_marginals {greek_mono .30, greek_poly .34, greek_latin_cs .11, latin .10, cyrillic .15}: the reserved text band supplies only 270 greek_latin_cs lines (v6 asked 360); the shift goes to polytonic. v6 stays committed and unused.

v7 → v8 (eval-only, 8 Oct 2026, CP-E2code H03 fix): identical rendering, with
`factory/exclusions/e2_v7_transfer_shared.txt` adding the 137 NFD GT texts shared
by E1 v7 and the legacy transfer instrument. **Explicit quota change:**
`greek_latin_cs .11 → .10` (264 → 240 lines), `greek_poly .34 → .35`
(816 → 840 lines); the other marginals and total 2,400 are unchanged.
The documented 270 mixed-script candidates lose 14 shared texts, leaving at
most 256; 264 is therefore infeasible even before other exclusions. The original
pool bytes are absent locally, so this ceiling is documentary, not a measured
census. E2 computes the actual reserved census from the staged pool, filters all
exclusions, and binds source/filtered pool, recipe and exclusion hashes in
`v8_exclusions.json` alongside exact quotas, remaining supply and shortfalls.
Every quota must be met by independent supply; any further shortfall refuses
before rendering. No exclusion is relaxed and no missing line is duplicated.
E2 additionally filters its bound
eval pool against bake-off gold/control texts and all Vouli train/val/test texts,
then rebuilds through the factory; it never relabels existing v7 shards as v8.
The pool, exclusion bytes and realized class counts are receipted. The original
v8 recipe/exclusion were already committed in E2; these quota edits remain for
the coordinator to commit outside this no-Git-writes fix. v8 must pass
the unchanged committed-recipe gate on the node; this offline implementation
does not write Git. v5 training remains unchanged and disclosed as in E1.

v1 → v5 retains the script, severity, background, polarity, length, reuse and
held-out-font distributions and adds training-only detector-crop augmentation with
automatic destroyed-mark label repair, a 20% Greek letterpress ink-transfer cohort,
historical-font routing, and an independent 7% lunate-sigma label-and-image rewrite.
Validation and reserved renders stay crop/rewrite-free. This records the v5 recipe's
custody; promotion as the production recipe of record still requires its own full
audit run. C0's fixture smoke audit does not certify the 200,000-row v5 distribution.

## Provenance

Binding P1–P5, verbatim from the 7 October plan copy:

P1 **No ad-hoc shard writers.** `o5_prepare.py`-style scripts stop writing training shards directly. Real crops enter through the
   factory's ingest path so they get the same schema, `script_class` and word tags, and appear in the same audit.
P2 **Every mix is a manifest.** A training/eval set is defined by `mix.json`: components = {factory build dir with `build_info.json`
   (synthetic) | real shard set with sha256 and source-partition id}, fraction per component, seed, codec version, recipe_sha256 per
   synthetic component. Training reads `mix.json` only; `--train-dir` on a loose directory is removed.
P3 **The trainer refuses unprovenanced data.** `train.py` (and the detector trainer) fail closed unless every synthetic component's
   `recipe_sha256` equals the sha256 of a recipe file that is **git-tracked at a committed revision** and `audit_ok` is true; the
   realised marginals of the assembled mix are recomputed from the rows and written next to the checkpoint (`data_provenance.json`).
P4 **Recipes are versioned, never edited in place.** A new distribution = `recipe.vN+1.json` + a one-paragraph change note in
   `docs/data_contracts.md`; the disclose-recipe-changes rule applies to every training launch (table recipe vs previous run).
P5 **Reviews check it.** Every checkpoint brief that gates training (CP-C1, CP-C4) lists P1–P4 as acceptance criteria; a run whose
   checkpoint lacks `data_provenance.json` is not reportable.

### Checkpoint integrity

The full-state trainer writer stores `state_hash_version: 2` and `state_sha256`
in every resume checkpoint, and the same digest in
`data_provenance.json.epochs[epoch].state_sha256` and the checkpoint's embedded
receipt epoch record. The digest covers the **complete checkpoint payload**:
model state and state-dict metadata, optimizer/scheduler state, global step,
epoch, seed/architecture/head/codec-byte/mix identities, original epoch and
optimizer-step horizons, RNG states (Torch, NumPy, Python, CUDA), arguments,
best/patience state and provenance snapshot. Future fields are covered as well.

Canonical serialization v2 uses typed, length-framed values, sorted dictionary
keys, distinct list/tuple tags, and tensor/array dtype, shape and all logical
bytes in contiguous little-endian order. Tensors additionally bind strides,
storage offsets, internal-overlap status, storage byte sizes and storage-sharing
and overlapping-allocation relationships. Storage IDs are first-encounter ordinals
in canonical traversal, never pointer addresses. It is independent of dictionary
insertion order, storage addresses and the PyTorch ZIP/pickle encoding. Only
the top-level `state_sha256` and the donor epoch's embedded receipt
`state_sha256` are excluded to break self-reference; older epoch hashes remain
covered. Unsupported value types fail closed.

`validate_resume` first recomputes this digest, then requires the existing and
embedded receipt epoch hashes to match it, before semantic checks or restoration.
Changed/truncated checkpoints, missing hashes or receipt disagreements produce
exit 3 before any run-output write. Legacy checkpoints without `state_sha256`,
or using the old value-only hash version 1, have
**no migration: retrain**; a digest cannot certify an unverified old artifact.

The independent completeness checks require the optimizer state key set to equal
all parameter IDs in its groups whose live parameters require gradients, with no
missing or extra records. Every parameter's scalar step must equal `global_step`,
both moments must match its parameter's shape/dtype, and scheduler `last_epoch`
must equal `global_step`. This trainer has no freezes or per-parameter schedules;
adding either requires a deliberate contract change. These invariants also apply
at step zero; the gate never accepts partial/lazy optimizer state.

Before restoration, optimizer and scheduler tensor occurrences must have separate
storage allocations: the gate checks storage identity and full byte ranges from
`untyped_storage().data_ptr()` and `nbytes()`, including disjoint views of one
allocation and distinct allocations whose ranges overlap. Internal tensor overlap
is forbidden; layouts whose sorted strides cannot prove non-overlap fail closed.
Every optimizer counter must be its own zero-dimensional scalar tensor. Aliasing
in the loaded FILE is a refusal, never silently repaired, even with matching hashes.
Only after the file checks pass, every optimizer/scheduler tensor is restored via
`t.detach().clone().contiguous()` into fresh independent storage. Independence,
contiguity and zero offsets are asserted before load and again on live state after
`load_state_dict`; live counters must remain scalar. The clone prevents restored
mutable state from retaining references into the deserialized checkpoint.

### Checkpoint integrity — threat model

The gate certifies **receipt-relative integrity of trainer-produced state** against
corruption, truncation, mix-ups and accidental or naive edits. It does **not and
cannot** defend against an actor with write access to both checkpoint and receipt
who replaces them together. That requires signatures or external custody, which
are out of scope for this experiment track. In the reviewer's own sentence:
“As already documented by the implementer, matching hashes are not signatures
against coordinated replacement of checkpoint and receipt.”

This is not authentication or safe deserialization of arbitrary executable pickle
content. “No writes on refusal” means no **run-output writes**: no output directory,
temporary receipt, receipt replacement, CSV or checkpoint creation/modification.
Existing output bytes and mtimes remain unchanged. Torch/runtime initialization
before validation may touch system temporary/cache paths; the gate does not promise
literal all-filesystem silence.

### Resume preflight and receipt publication

`train/train.py::validate_resume(ck, plan, receipt)` is the single full-state resume
gate. The plan is reconstructed from the validated training/transfer mixes,
deterministic epoch assemblies and actual width-bucket loader batch counts. The
optimizer horizon is `sum(ceil(epoch_batches / accum))`; resumption retains the
original total epochs and cannot extend or replace that schedule.

Before any output directory, temporary receipt, receipt replacement, CSV or
checkpoint write, the gate checks model keys/shapes by strict restoration; AdamW
state/group/parameter keys, configuration, moment shapes and update counters; and
an exact scheduler key set matching the newly constructed OneCycleLR. Every fixed
scheduler field must match, including `total_steps`, all phase endpoints,
annealing, momentum and base rates. `last_epoch == global_step` must lie in
`[0,total_steps]`, `_step_count == global_step + 1`, and learning rates/momentum
must equal the planned schedule at that progress. Updates cannot exceed the
completed epochs' accumulated-step budget; skipped nonfinite batches may reduce
that count. Optimizer progress must also agree with global updates.

The same gate verifies seed, architecture, head, codec version/classes and codec
file SHA-256, command settings, exact mix/shard/build-receipt identities, historical
epoch summaries and any interrupted next epoch. The checkpoint writer records
`checkpoint_updates[epoch] = global_step` in the existing receipt and its embedded
snapshot; these counts must agree exactly at the donor epoch and throughout the
shared completed history. A receipt with a newer completed checkpoint is refused.
RNG, best metric/epoch and patience state must validate and restore as well.

Only after this function succeeds may the existing receipt be copied and a session
appended, preserving historic HEAD, metadata and epoch summaries. Any mismatch
returns a clear nonzero refusal (exit 3), preserving all existing output bytes and
mtimes and creating no output files. Legacy checkpoints/receipts without exact
update counts or codec-byte identity fail closed; do not invent historic values.
New resume fields and compatibility decisions belong in this one gate, before
publication, rather than relying on permissive `load_state_dict` calls.

### mix.json (schema version 1)

`train/mix.py` implements the builder and validator; `train/mix.schema.json` is the
structural schema. Paths resolve relative to the manifest. Components point at a
factory dataset ROOT containing `build_info.json` and `{train,val,reserved}/`.

```json
{
  "schema_version": 1,
  "components": [
    {"kind": "synthetic", "build_dir": "../factory-build",
     "recipe_sha256": "<sha256>", "fraction": 0.5},
    {"kind": "real", "shard_dir": "../imported-crops",
     "shard_sha256": {"train/shard-00000.parquet": "<sha256>",
                      "val/shard-00000.parquet": "<sha256>"},
     "partition_id": "document-family-partition-v1",
     "source": "verified text-layer line crops at plugin scale", "fraction": 0.5}
  ],
  "seed": 20261007, "codec_version": "v1",
  "created_by": "owner or generating command", "notes": "source/admission evidence"
}
```

All displayed fields are required except `schema_version` (defaults to 1). Notes may
be empty; unknown fields fail. Fractions must be finite, nonnegative, ≤1, and sum
to 1 within 1e-6. Zero-fraction components still undergo custody validation.
Synthetic `build_info.json` must carry the same codec and recipe hash, `audit_ok:
true`, and an exact `shard_sha256` inventory. The recipe hash is SHA-256 of RAW
bytes from `HEAD:<path>` for a recipe in `git ls-files factory/*.json`; staged-only
recipes and working-copy edits cannot establish commitment. The historical
serialized-recipe identity survives as `recipe_effective_sha256`, a diagnostic
rather than a substitute for the file hash. Builds refuse in-memory recipe
overrides and nonempty outputs. Old builds without shard custody need fresh builds;
the grandfathered O5 synthetic arm remains historical.

Real hashes must match the exact on-disk inventory (missing, extra and changed
shards fail), and the factory receipt must have `kind: real`, the same partition,
codec and shard hashes. This stronger receipt requirement enforces P1. Real audit
failures are report-only and do not discard supervision.

The component specification for the builder is a JSON array; synthetic recipe
hashes and real shard hashes are filled from receipts/files. Validation occurs
before the requested manifest is published:

```sh
python -m train.mix build --components components.json --out mix.json \
  --seed 20261007 --codec-version v1 --created-by owner --notes 'source evidence'
python -m train.mix validate mix.json
```

Validation returns 0 on success, 3 with a clear reason on failure.

### Importing real crops

```sh
linefactory import-real --records records.jsonl --crops crops/ \
  --out imported/ --partition document-family-partition-v1
```

`ingest` remains the corpus-TEXT entry point. Real records contain `crop_path`,
`text`, `doc`, and `id`; aliases are `crop`, `label`/`label_text`/`gt_nfc`,
`doc_id`/`source_doc_id`, and `line_id`. Optional fields are `script_class`, `split`,
`source_dataset`, `license`, `admitted`, and `word_tags`. Relative crop paths resolve
under `--crops`; absolute paths must also stay within it. Supplied splits must be
valid, and each document has one split; omitted splits default to train. The caller
supplies the source-document partition. Import does not certify C3 partitioning or
C3b admission evidence.

Crops resize to 48 pixels with aspect preserved, own-background padding, [64,2560]
width and the 14-pixel readability floor. Labels use the same Rust codec and the
exact §3 Parquet schema. Supplied script classes retain their provenance; missing
classes use the factory classifier (its additional Cyrillic code-switch categories
map to `cyrillic` for this frozen real-import contract). Word tags and origin live
in `word_tags.jsonl`, keeping Parquet columns frozen. Severity=0, font=`real`, reuse=0;
polarity uses the crop median. `bg_type=flat` is an explicit importer default and
`accent_survival=1` an unmeasured placeholder, not certified appearance measurements.

Appearance/length reports reuse the generator's audit functions and cover every
crop, including reserved rows. Length/contrast warnings retain rows. Unencodable
or empty labels, invalid script classes, inadmissible records, unreadable crops and
sub-floor pathological widths have per-record reasons in `drop_ledger`. Malformed
records, duplicate IDs, path escapes and document split conflicts fail the import.
Receipts contain the JSONL hash, individual record and consumed-crop hashes,
partition, document splits, class counts and exact shard hashes. Outputs must be
new or empty. `o5_prepare.prepare()` and `write_shards()` refuse writes;
`select_manifests()` retains seeded selection and text exclusions in memory.

O4b (2026-10-07) adds optional source-quality metadata to real input records:
`label_tier`, `source_url`, `licence_evidence`, `attribution`. Admitted tiers are
`gold`, `silver`, `silver_ocr_layer`, `silver_agreed`, `gold_aligned`; flagged rows
must set `admitted=false`. Tiered records require a nonempty `license`. Metadata
survives in `word_tags.jsonl` alongside `licence`, `source_dataset`, and
`source_doc_id`; its SHA-256 and tier counts are recorded in `build_info.json`.
The frozen Parquet schema remains unchanged (`license` is its spelling).
O4b source JSONL carries both `licence` and `license` with identical values.
Gold is human/source ground truth, silver is machine text, and agreement/alignment
are machine evidence rather than a human seal. O4b admission additionally requires
a reviewed document-family map excluding O5/E1 test and C1 documents.

### Consumer sampling and checkpoint receipt

The line trainer accepts `--mix mix.json` only. Loose `--train-dir`, `--val-dir`,
and `--transfer-dev` flags fail with migration guidance. Optional held-out evaluation
uses `--transfer-mix` and reads reserved rows only. Invalid custody returns 3 before
Torch imports, device detection, output creation or an optimizer step.

Per-epoch weighted concatenation uses N=sum of active component pool sizes (capped
at 2000 in smoke mode). Largest-remainder rounding assigns N×fraction rows to each
component. Each pool shuffles deterministically by `seed:epoch:component`; quotas
above pool size cycle through fresh permutations. Train membership redraws each
epoch; validation stays at epoch 0. `--greek-only` filters source pools before
quotas. Sampling uses the manifest seed, independent of model `--seed`. Width-bucket
loaders rebuild each epoch; OneCycle uses the sum of actual per-epoch optimizer-step
horizons. Reserved rows never enter train or val.

Before the first step, `data_provenance.json` records validated original/resolved
mixes, repository HEAD, recipe file hashes, component counts (including zero quotas),
per-component shard SHA-256 and build-receipt SHA-256,
and realised counts/fractions for script_class, severity, bg_type, polarity, font
stems and 128-pixel width buckets, recomputed from assembled rows. Each epoch adds
its own marginals atomically before stepping. No image payloads enter this receipt.
Full checkpoints embed its snapshot and training/transfer manifest byte hashes.
Resume requires that existing receipt and a compatible checkpoint, checks all bound
bytes and saved epoch summaries, and restores full state before any output write.
It appends a continuation session and epoch summaries while preserving historical
epochs, HEAD and metadata. Legacy receipts lacking these bindings fail closed.
No training is launched by C0. The untracked July detector/page trainers are outside
this line-shard implementation; their page-manifest bridge and checkpoint receipt
must be implemented before they satisfy P3 or authorize detector training.

### E1 v6 evaluation distribution (2026-10-07)

`factory/recipe.v6.json` is an evaluation-only companion to unchanged v5, not a
training replacement. It declares 2,400 reserved lines: modern Greek 30%,
polytonic 30%, Greek/Latin 15%, Latin 10%, Cyrillic 15%; polytonic and Cyrillic
each have a hard emitted-row minimum of 300. Its `eval_only` object names the
three v5 held-out fonts and an explicit 0.85 maximum per-font share (the training
audit's 0.25 cap cannot apply to a three-font instrument). Crop augmentation and
ink transfer are disabled, atom_floor=0 because no training atoms are selected;
other v5 appearance/distortion settings and exclusions remain. Factory selection
uses exact class quotas without replacement from the reserved text band, fails
on supply deficits, and audits all emitted reserved rows, fonts and minima.
All synthetic bytes still come from `linefactory build`; receipts set
`eval_only=true`. The mix loader refuses this component for train/val. Missing
sources/fonts/strata fail rather than changing the recipe. The recipe must be
committed before gate validation; no in-memory distribution overrides are used.

E1 keeps v5's committed 200,000 target intact. The optional trainer
`--epoch-rows` caps TRAIN assembly at the real TRAIN size, using the same C0
largest-remainder quotas, per-epoch pool permutations and receipt marginals.
`--pack-bucket-tails` combines width-bucket remainders to yield ceil(N/bs) batches
without changing pixels, labels or row counts; default loaders are unchanged.
`--selection-metric val_cer --transfer-final-only` binds the `--transfer-mix`
receipt while keeping held-out data out of epoch evaluation/selection. Final
best checkpoints alone feed E1 readout. Resume retains prior committed-epoch
provenance. Readout may distinguish Cyrillic/Latin lines inside the frozen real
importer's `cyrillic` class; this diagnostic does not edit Parquet labels.
