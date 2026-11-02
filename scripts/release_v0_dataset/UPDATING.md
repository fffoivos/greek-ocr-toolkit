# Correction updates

> **Not the published dataset.** This page describes updates to the full relational release package (pages, tables, label history), which was built and sealed but not published. For the published `fffoivos/greek-ocr-lines`, see [datasets/greek-ocr-lines/README.md](../../datasets/greek-ocr-lines/README.md) and its `update_lines.py`.

Run credential-free on a separate copy of sealed candidate C. The base is read
only. The output is a metadata overlay; upload exactly its printed commit paths,
including deletes recorded in UPDATE_RECEIPT, together in one commit. It never
writes trainer data, memberships or images. Verify the merged view before upload.

## What an update rewrites

Updating is **metadata-only**: no image or frozen trainer file is rebuilt or
re-uploaded. It is **not** proportional to the number of corrected rows:

- appended: new label versions (`labels/versions/<producer>/<version>/`) and
  their features (`tables/row_features/updates/<producer>/<version>/`);
- rewritten whole: the two current projections, `labels/current` and
  `tables/current_features`. Even one correction rematerialises both (about
  34 MB in the 2% sample, an extrapolated 1–2 GB at full scale). Changed feature
  rows move to the end of `current_features`;
- regenerated: `manifests/{CONFIGS,COVERAGE,MANIFEST}.json`, `SHA256SUMS`,
  `UPDATES.jsonl` and `README.md`.

Xet may transmit much less than these local sizes; only the drill's measured
`transmitted_bytes` is transport evidence.

The card is retargeted as a whole: front matter, title, introduction and every
loader revision move to the new generation together (a stale reference fails),
and a line records which generation the correction supersedes.

## Inputs

JSONL or parquet columns: row_key, text, producer, producer_version, reason,
expected_label_version_id, expected_text_sha256. Producer/version is append-only;
stale predecessors, conflicting duplicates, no-op and unencodable edits fail.
The generation must follow the card's generation. The pinned codec supplies atom
IDs; factory NFD/G0-3/whitespace normalization is recorded alongside exact
submitted text and recomputed NFC/NFD/IDs. A repeat of the identical command
checks output hashes and returns the same paths.

Only real rows (`row_key`) can be corrected. A row keyed by synthetic occurrence
(`synthetic_key`, or factory_build_id/split/source_shard/source_ordinal) is
refused: there is no occurrence-keyed synthetic label layer yet.

```
python -B scripts/release_v0_dataset/update_labels.py COPY_OF_C corrections.parquet \
  --out CORRECTION_OVERLAY --generation v0.6
```

## Upload and drill

The coordinator allocates the substantive generation in VERSIONS.md, checks the
complete overlay, commits, verifies all paths and immutable oids, then tags the
verified commit. Uploads go through Xet only: `drill_update.py`,
`upload_staging.py` and `promote_candidate.py` refuse an unqualified
huggingface_hub (2.2.0 qualified), unavailable or disabled Xet, and any
non-path operation, so there is no silent HTTP fallback.

The drill uses ten real edits, branch `drill` on private staging and a disjoint
full copy of C (the copy is not proportional to the edit either); sealed C is
untouched. It records `transmitted_bytes` for the correction commit and
`rewrite_transmitted_bytes` for an identical feature-table rewrite (CDC/Xet
savings), from hf_xet's own transfer counters plus inline regular files. A
field stays null, with a reason, when the client reports nothing. Local file
bytes are not transmitted bytes. No token is read from disk, argv or implicit
credential state:

```
HF_TOKEN=... python -B scripts/release_v0_dataset/drill_update.py SEALED_C edits.jsonl \
  --scratch FRESH_DIR --parent-commit STAGING_MAIN_SHA --generation v0.6
```

The coordinator checks current joins, idempotent rerun and immutable trainer/image
identities after a full pinned download. For public promotion use
promote_candidate.py: one CAS commit. Only private staging may batch commits. A
correction does not retrain any model.
