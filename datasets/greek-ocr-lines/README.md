# Greek OCR lines: the dataset and its code

[`fffoivos/greek-ocr-lines`](https://huggingface.co/datasets/fffoivos/greek-ocr-lines) is the public line dataset of the [Greek OCR models](https://huggingface.co/fffoivos/greek-ocr). Each row is one printed text line: its image and its transcription. Tag **`v0.5`** (commit `996c88c6b1f83338e02991aee8d451247568f1df`) holds exactly the lines OCR v0.10 trained and was evaluated on. The dataset card on HF describes every split and column; this page covers using it, the code behind it and how to update it.

## Contents

| Path | What it is |
|---|---|
| `data/real/<split>/*.parquet` | 878,202 real lines (splits `train`, `validation`, `harvest_dev`, `seal04_dev`, `harvest_test`, `seal04_test`); config `real` |
| `data/synthetic/train/*.parquet` | 190,486 synthetic lines; config `synthetic` |
| `metadata/real_lines.parquet` | one row per real line: book (`book_id`, provider, source, item, title, year, volume), `page`, `bbox` on the page, catalogue/source URL, and the reason for every null; config `line_metadata` |
| `synthetic/RECIPE.json`, `synthetic/DISTRIBUTION.json`, `synthetic/factory_*.json` | the generator's configured distribution, the realised counts and the factory's own reports |
| `COUNTS.json`, `SOURCES_BY_SPLIT.json` | line counts per split, pool and source collection |
| `CORRECTIONS.jsonl` | appears with the first correction: one record per corrected line (see [Updating](#updating)) |

Each shard holds 4,096 lines in row groups of 500, zstd-compressed, written by pyarrow 26.0.0. Columns: `image` (PNG, exactly what the trainer read), `gt_nfc`, `gt_nfd`, `label_ids` (codec v2.1 ids of `gt_nfd`), `codec_version`, `width`, `script_class`, `pool`, `split`, `line_id`, `source_dataset`, `source_doc_id`, `applied_ops` and the synthetic generation fields (`severity`, `font`, `polarity`, `bg_type`, `accent_survival`, `reuse_index`).

## Using it

```python
from datasets import load_dataset

# Exactly what the models trained on: pin the tag.
train = load_dataset("fffoivos/greek-ocr-lines", "real", split="train", revision="v0.5")
synth = load_dataset("fffoivos/greek-ocr-lines", "synthetic", split="train", revision="v0.5")

# The latest labels (v0.5 plus any corrections): no revision.
test = load_dataset("fffoivos/greek-ocr-lines", "real", split="harvest_test")

# Book and page position of each real line: join on line_id.
meta = load_dataset("fffoivos/greek-ocr-lines", "line_metadata", split="all").to_pandas()
df = test.to_pandas().merge(meta, on="line_id", how="left", suffixes=("", "_meta"))
```

`harvest_test` and `seal04_test` were never used to select anything; report on them. `seal04_dev` chose each released checkpoint, and `harvest_dev` with `seal04_dev` chose the Stage B hyperparameters.

To turn `label_ids` back into text, or text into `label_ids`, use [`greekocr/train/codec/v2.1.json`](../../greekocr/train/codec/v2.1.json): normalise to NFD, collapse whitespace runs to one space, then map one id per code point (`encode` in [`update_lines.py`](update_lines.py) does this; it reproduces the stored `gt_nfd` and `label_ids` exactly).

## The code

| Step | Code |
|---|---|
| Real and synthetic shards: the Stage C trainer inputs (`prepared005`) exported as they were read, licence column dropped | not yet in this repository: the 29 Oct 2026 export scripts are still on Clariden (`release_v0/hf/2026-10-29/`) and are being recovered |
| Synthetic lines: the Rust line factory and recipe | [`greekocr/synth/`](../../greekocr/synth/), [`greekocr/_vendor/factory/`](../../greekocr/_vendor/factory/) |
| `metadata/real_lines.parquet`: per-line book and position, from the release build's row table ([`scripts/release_v0_dataset/build_dataset.py`](../../scripts/release_v0_dataset/build_dataset.py)) | [`build_line_meta.py`](build_line_meta.py) |
| v0.5 commit (metadata + card) with read-back and tag | [`publish_meta.py`](publish_meta.py) |
| Text corrections without re-uploading images | [`update_lines.py`](update_lines.py) |
| Codec | [`greekocr/train/codec/v2.1.json`](../../greekocr/train/codec/v2.1.json) |
| Trainer that read these files | [`greekocr/train/`](../../greekocr/train/) |

## Updating

The repository has one branch, `main`. Every update is one commit whose parent is the commit it was prepared from (`parent_commit`), so a concurrent change makes it fail instead of being overwritten. A tag marks each release; `v0.5` is never moved, so the trained-on data always stays loadable.

**Correcting line text (the expected update).** Text and image of a line share a shard, but the images do not have to be re-sent. [`update_lines.py`](update_lines.py) rewrites only the shards that contain a corrected line, and in them only `gt_nfc`, `gt_nfd` and `label_ids`:

1. Write the corrections as JSONL, one line each: `{"line_id": "...", "old": "<current gt_nfc>", "new": "<corrected text>", "reason": "..."}`. `old` guards against editing a line that changed meanwhile.
2. Prepare and verify, with no upload: `python datasets/greek-ocr-lines/update_lines.py corrections.jsonl --work DIR`. It finds each line's shard from `metadata/real_lines.parquet` and the shards' `line_id` column, downloads only those shards, and refuses to continue unless each one re-encodes to its original bytes. It then encodes the new text with codec v2.1, refusing characters outside the codec. It checks that every other column, images included, is unchanged and that the text changed only on the corrected rows.
3. Upload: `HF_TOKEN=... python datasets/greek-ocr-lines/update_lines.py corrections.jsonl --work DIR --commit --tag v0.6`. One commit adds the rewritten shards and the appended `CORRECTIONS.jsonl`. It is then read back: the uploaded shards' hashes match, and no other path changed. `--tag` is optional (tag when a batch of corrections makes a release).

What it costs: the images and every unedited row are byte-identical in the rewritten shard. Correcting two lines in a 113.8 MB `harvest_test` shard changed 196 KB of it: the text columns of the two affected row groups (141 KB) plus the parquet footer (55 KB). The Hub stores files with Xet, which splits files into content-defined chunks (about 64 KB) and uploads only chunks it does not already have. So that correction should upload roughly 0.5 MB instead of 114 MB. This is an estimate from the measured byte changes; the first real correction commit gives the actual figure.

Only real lines are corrected this way. A synthetic image is rendered from its text, so a wrong synthetic label means fixing the generator and regenerating the affected lines.

**Other updates.**

- New lines: add new shard files (for example `data/real/train/<pool>-part-<next>.parquet`); never rewrite existing ones. Update `COUNTS.json`, `SOURCES_BY_SPLIT.json`, the card's counts, and `metadata/real_lines.parquet` with rows for the new lines.
- New or corrected book metadata: rewrite only `metadata/real_lines.parquet` (about 10 MB); the line shards are untouched. `build_line_meta.py` and `publish_meta.py` show the build and the read-back.
- Card text: a commit of `README.md` alone.
