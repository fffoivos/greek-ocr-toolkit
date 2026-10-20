# R2 preparation inputs

The production config binds the complete R2C population plus the Addendum A
teacher-seen slice. R2a remains off (`manifest: null`).
No eligible population, reserve assignment, admission decision or print label is
invented by this package.

Population JSONL (one line per eligible native crop, including reserve documents):

```json
{"line_id":"native-line-id","doc":"source:document","source":"source","role":"train","image":"/absolute/Clariden/path/to/crop.png","crop":"docs/records/harvest/harvest_big/wave/crops/doc/line.png","crop_sha256":"64 lowercase hex characters"}
```

`role` is `train`, `validation_reserve`, `witness`, or `calibration`. R2C
`supervision` maps to `train`; `validation` maps to `validation_reserve`.
Every role exports into physically separate `chunk-*-ROLE.jsonl.gz` files.
Only `train` may enter a manifest, including removals and unknown quarantines.
`teacher_seen_document` is a boolean carried through teacher exports and manifests;
Stage A refuses a manifest that drops a true bound flag. Legacy frozen-old rows
without a role retain their frozen training membership. All eligible lines must appear; `image` is
the exact staged native image, not a reconstructed crop. For native extraction,
`crop` is the R1 canonical crop key resolved against the supplied crop root/layout.

R2C role binding JSON:

```json
{"documents":{"source:document":{"eligible":true,"source":"source","role":"train"}},"eligible_line_ids":["native-line-id"],"excluded_documents":[],"excluded_lines":[]}
```

R2C owns eligibility, edition aliases and the frozen four-role assignment.
R2P2 preserves those roles and adds only the excluded-checked teacher-seen train slice. The binding must represent ALL eligible lines, with the
exclusions prescribed by the R2 plan. R1 exclusions are unioned with it. The
package checks membership, completeness, source, role consistency and hashes;
it does not certify the lead's source-admission or alias judgments.

Manifest JSONL is an overlay on the old training extraction. An old-pool-only
manifest may enumerate every old slot with unchanged targets, or be empty:

```json
{"slot_id":["crop sha256",0],"line_id":"line-id","doc":"source:document","source":"source","provenance":"native_print","targets":[1,3,0,0],"unknown":[],"loss_weight":1,"replaces":["crop sha256",0]}
```

Head order: breathing (`none`, `psili`, `dasia`), accent (`none`, `acute`,
`grave`, `circumflex`), dialytika (`none`, `dialytika`), subscript (`none`,
`subscript`). Targets are integer class indices. Unknown heads may have null
targets; ANY unknown head quarantines the WHOLE slot from training.
`provenance` is `old`, `native_print`, `pseudo`, or `override`. Weights are 1,
1, 0.5 and 1 respectively. The frozen-old-pool capped inverse-frequency class weights
multiply the provenance weights. Weighted CE keeps the original per-head
class-weight denominator, so pseudo weights actually reduce effective loss mass.

A removal has `slot_id` and `removes` (both identities). A correction uses
`replaces`; its target must exist. Same-identity corrections stay in place.
New identities need `pool`, referring to an existing hash-bound extraction, or
`"native"` for the Stage B native pool. No second modification or collision is
allowed. Each identity is `(native crop bytes sha256, recogniser NFD start)`.
The crop inventory JSONL maps `crop` to `sha256`. For new pools extend the
inventory; do not rehash modified/resized images. `source` defaults to the
source prefix of the extraction's document identity.

For a new native pool, add this config field and bind the line list in `sha256`:

```json
{"native":{"line_list":"config/native_train_lines.jsonl","crop_root":"/absolute/crop/root","layout":"e3"}}
```

The native line list uses the population schema and contains train documents
only. Stage B runs alignment → teacher export → `r2_native.native_pool`, using
unchanged R1 extraction. Stage D resolves `pool: "native"` to `B/native`. R2a's
manifest is independently hash-bound. No native pool is currently admitted.

Bind production inputs on Clariden after the lead stages them (preparation only):

```bash
PYTHONPATH=$PWD /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python -B \
  scripts/labelfix/clariden/r2_prepare.py \
  --line-list config/population.jsonl --roles config/r2c_roles.json \
  --external-hashes docs/records/labelfix/spellcheck/R2/evidence/external_hashes.json \
  --out config/r2_job.json
```

Add `--manifest config/r2a.jsonl --inventory config/combined_inventory.jsonl.gz`
when R2a cards are admitted. For extra extracted pools bind each extraction
receipt hash in `sha256`; its payload is verified by that receipt. Rebuild the
deployment checksum list after changing any bound input. Read the new
`forecast.requested_minutes` and pass that exact `--time` to both test-only and
real submission. The 120-minute script default is only the current planning
reference; the population-bound forecast supersedes it.

Scorer input: JSONL with `line_id`, `doc`, `source`, `inclusion_weight` (default
1), `print_slots` (id, base, targets, unknown) and optional `recogniser_text`.
For frozen physical lines the scorer accepts the existing `slots` format; this
is a continuity adapter, not new adjudicated per-letter localisation. Include
ALL printed alphabetic bases, including consonants, in genuinely new union
truth. Unknown printed/ownership states must remain unknown. Predictions are
JSONL `line_id`, recogniser NFD `start`, `base`, `factors`, `cls`, and optional
`fused`, `clipped`, `localisation_unknown` fields. The four-head teacher export
is directly compatible. A missing reader prediction becomes none with coverage
false. An unmatched printed positive is FN; an inserted positive is FP.
Case-changing base substitutions become omission plus insertion.

```bash
PYTHONPATH=$PWD python -B scripts/labelfix/r2_score.py \
  --truth PRINT_UNION.jsonl --baseline OLD.jsonl --candidate NEW.jsonl \
  --overlay docs/records/labelfix/spellcheck/R2/truth_overlay_v0.json \
  --overlay docs/records/labelfix/spellcheck/R2/truth_overlay_v1.json \
  --physical-metadata FROZEN_HELDOUT_EXTRACTION \
  --runtime FROZEN_RUNTIME.jsonl.gz --sources GOOGLE_SOURCES.jsonl \
  --policy-mode FULL --out SCORE_DIRECTORY
```

Sources rows have `line_id` and `google`; canonical truth can instead include
`google`. Runtime contains the complete saved detector, coverage, recogniser and
peer evidence. Both checkpoints use this same runtime and policy mode, with only
their own R1 predictions replaced. Historical pipeline and raw results are
separate outputs; missing runtime/physical metadata is explicitly reported as
unavailable. The pipeline's edit unit is a changed head on an accepted whole
line. No quality is inferred from a HOLD. The frozen policy itself is unchanged.
