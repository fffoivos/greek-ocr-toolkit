# Greek OCR toolkit

Tools for reading printed Greek with OCR, especially polytonic Greek in 19th- and 20th-century books.

The toolkit covers the whole process, from finding scanned books to running a recognizer inside a document pipeline.
Everything sits behind one typed Python package, `greekocr`, with a command-line tool of the same name and an offline
test suite.

> **Status: in active development.** APIs, file formats and results still change between commits. Experimental work
> lives on branches and in `prototypes/` before it reaches the package.

## Principles

- **A PDF text layer is another OCR, not ground truth.** It is never a reference, a judge input or a calibration target.
- **Machine agreement is not human gold.** Lines on which readers agree are kept as "silver" labels and marked as such.
- **Provenance is recorded.** Data, recipes, models and results carry the hashes and receipts needed to reproduce them.
- **Fast methods are checked against slow, explicit ones.** A heuristic stays only if it tracks a real feature of the
  page and agrees with the explicit method.
- **Offline by default.** Network calls (source discovery, cloud OCR services, pod operations) happen only when the
  matching function is called explicitly. The tests use recorded responses and mocks.

## The process

| # | Dimension | Question it answers | Code |
| --- | --- | --- | --- |
| 1 | [Sources](#1-sources) | Which scanned books and pages can we use, under what rights? | `greekocr.real.sources` |
| 2 | [Page analysis](#2-page-analysis) | Where are the text lines on a page, and in what order? | `greekocr.pages`, `greekocr.glyphs` |
| 3 | [Line geometry](#3-line-geometry) | Is each line crop tight, straight and complete? | `greekocr.real.geometry` |
| 4 | [Readability and line metadata](#4-readability-and-line-metadata) | Is a crop readable, and what kind of line is it? | `greekocr.verify`, `greekocr.annotate`, `greekocr.glyphs` |
| 5 | [Labels for real lines](#5-labels-for-real-lines) | What text does a real line contain, and how sure are we? | `greekocr.real`, `greekocr.harvest`, `greekocr.readers.services` |
| 6 | [Synthetic lines](#6-synthetic-lines) | How do we make unlimited correctly labelled training lines? | `greekocr.synth` |
| 7 | [Training-data custody](#7-training-data-custody) | Which lines may be trained on, and which must stay held out? | `greekocr.real`, `greekocr.synth` |
| 8 | [Recognition models](#8-recognition-models) | Which line readers exist, and how are they loaded and converted? | `greekocr.readers`, `greekocr.warmstart` |
| 9 | [Evaluation](#9-evaluation) | How good is a reading, including accents and breathings? | `greekocr.score` |
| 10 | [Deployment](#10-deployment) | How does the recognizer run inside a real document pipeline? | `greekocr.deploy` |
| 11 | [Speed](#11-speed) | How do we find lines fast enough for whole collections? | `prototypes/`, branches |
| 12 | [Provenance and operations](#12-provenance-and-operations) | How is every step reproducible and every long job watched? | `greekocr.ops` |

### 1. Sources

Discovery crawls digital libraries for Greek books: the Hellenic Parliament library, the Internet Archive, Anemi (the
University of Crete digital library), Wikimedia and others. Crawls respect robots rules and rate limits, and record
what was fetched. Rights are taken from the source's own metadata and never assumed; unknown rights stay unverified.
Other inputs are existing datasets (Polyton-DB, GRPOLY), born-digital PDFs, and web pages rendered with a browser so
that their text is known exactly.
Docs: [rendered web pages as label data](../shared/WEB_RENDER.md).

### 2. Page analysis

`greekocr.pages` turns a page image into text lines and recognition pieces. The steps:

1. Layout regions come from Docling. Our own code then prepares the pixels: local thresholds, connected ink, rules and
   gutters.
2. Text bands are fitted, and ink is assigned to its line.
3. Font guides (baseline, x-height and so on) are fitted along each line.
4. Tables are handled separately, so that recognition pieces never cross cell borders.
5. The page structure is recovered: leaves, columns, blocks, rows and reading order.

Lines judged not to be text (ornaments, rules, noise) are kept in the data as diagnostics. They are never drawn or sent
to recognition. Rotated-text handling exists but is parked.
Docs: [working with page images](../A_ocr_development/reference/PAGES_GUIDE.md), [pipeline](../A_ocr_development/reference/PAGES_PIPELINE.md),
[output format](../A_ocr_development/reference/PAGES_OUTPUT_FORMAT.md), [line-finding algorithm](../A_ocr_development/reference/PAGE_LINES_ALGORITHM.md),
[line segments](../A_ocr_development/reference/PAGE_LINE_SEGMENTS.md), [Docling tables study](research/DOCLING_TABLES_20261009.md),
[orientation study](research/ORIENTATION_20261009.md).

### 3. Line geometry

A recognizer reads a line only as well as the crop it gets. Geometry refinement straightens and tightens existing
line crops from their pixels, so that accents above and descenders below are not cut off. It is measured both with
pixel-only checks and with an independent reader. CLI: `greekocr geometry refine | measure | evaluate`.
Docs: [line geometry](../A_ocr_development/reference/O4D_GEOMETRY.md).

### 4. Readability and line metadata

These checks need no reference text:
- **Glyph measurements:** letters, accents and ink per line (`greekocr.glyphs`).
- **Readability:** image checks use only the pixels, and text checks use only the reading (`greekocr.verify`).
- **Line metadata:** script, font size and style, and word types (`greekocr.annotate`).

All of these are used to select and stratify lines, not to grade a recognizer.
Docs: [readability checks](../VERIFY.md), [line metadata](../A_ocr_development/reference/LINE_METADATA.md),
[glyph plan](glyphs/GLYPHS_PLAN.md), [glyph calibration](glyphs/GLYPHS_CALIBRATION.md).

### 5. Labels for real lines

Real lines have no ground truth, so labels come from independent readers:
- our own recognizer;
- other Greek models;
- cloud services, used only when called explicitly: Google Document AI, Google Cloud Vision and Transkribus.

Their agreement gives each line a tier. Two-reader adjudication and geometric gates decide what is kept, and a line
with bad geometry is rejected even when the readers agree. The pilot harvest records every line's source, page,
model and code version.
Docs: [Document AI reader](../B_training_data/a_google_ocr/readers/READERS_DOCAI.md), [Cloud Vision reader](../B_training_data/a_google_ocr/readers/READERS_VISION.md),
[Transkribus reader](../B_training_data/a_google_ocr/readers/READERS_TRANSKRIBUS.md), [pilot harvest](harvest/PILOT_v1.md),
[three engines compared](harvest/THREE_ENGINES_v1.md),
[commercial OCR survey](research/COMMERCIAL_OCR_20261008.md).

### 6. Synthetic lines

Synthetic lines are rendered with known text by a separate Rust line factory. Each recipe (fonts, text sources,
noise, layout) is identified by the SHA-256 of its bytes; v5, v7 and v8 are recorded here. `greekocr.synth` runs the
factory and builds reproducible mixes of synthetic and real lines. Before using a font, check that it covers every
needed character and accent.

### 7. Training-data custody

Lines are split by canonical work (the same text in different editions counts as one work), never by line. This keeps
held-out works out of training. Real shards are imported only through the line factory's `import-real` command.
A mix is valid only if its exact recipe bytes are committed in the custody repository. Every manifest lists its
shards with hashes.
Docs: [repository standard](../STANDARD.md), [API examples](../API.md).

### 8. Recognition models

Available readers: our own recognizer, Kalchas, a persistent CLLG worker, and native PaddleOCR references. They all
load lazily, so heavy dependencies are needed only when used. `greekocr.warmstart` converts weights from donor models
into our architecture and checks numerical parity against the native framework before a converted model is trusted.
Training itself runs on separate GPU workers.

### 9. Evaluation

There are two named scoring paths:
- **Strict:** character error rate on the model's raw output, never normalised to improve a score.
- **Bake-off:** compares different readers after canonical Unicode decomposition. It reports accent and breathing
  F1, and Greek/Latin look-alike confusions.

Results are summarised by line category, and evaluation uses held-out works only.

### 10. Deployment

The recognizer ships as a [Docling](https://github.com/docling-project/docling) OCR plugin (entry point `glossapi`):
1. Docling supplies layout regions.
2. Our page analysis prepares table-aware pieces.
3. Our recognizer reads each piece.
4. The plugin installs the text cells back into the document.

Deployment plans for GPU nodes are reviewable files, and pod operations run only when called.
Docs: [pipeline § How Docling fits](../A_ocr_development/reference/PAGES_PIPELINE.md#how-docling-fits), [GPU design](research/GPU_DESIGN.md).

### 11. Speed

Page analysis is exact but slow. The fast-lines work starts from an off-the-shelf line detector (PaddleOCR) and adds
corrections, each of which must track a real page feature and agree with the slow explicit model. A partial Rust port
is being measured. This work lives on development branches and in `prototypes/` until it is checked.
Docs: [fast lines charter](research/FAST_LINES_CHARTER.md).

### 12. Provenance and operations

`greekocr.ops` provides:
- receipts and hash verification;
- secrets read from the environment, never stored;
- rate-limited clients;
- bounded watching of long remote jobs, which reports stalls but never kills a workload.

`greekocr/_vendor` keeps the original source logic byte-for-byte, with its origin recorded in
[docs/INVENTORY.md](../INVENTORY.md).
Docs: [validation](verify_20261008/VALIDATION.md).

## Install

Python 3.11 or newer.

```sh
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -e '.[test]'
.venv/bin/python -m pytest -q
```

The base install covers pages, manifests, tags, scoring and text-layer extraction. Heavier dependencies are extras:

| Extra | Use |
| --- | --- |
| `readers` | local recognition models |
| `warmstart` | converting and checking donor model weights |
| `docling` | the Docling plugin and computed layout |
| `docai` | Google Document AI crop reader |
| `web` | rendering HTML pages as exact label data |
| `test` | everything the test suite needs |

## Quick start

Find the lines on a page image:

```python
from PIL import Image
from greekocr.pages import process_page

result = process_page(Image.open("page.png"), page_key="page-1")
print(len(result.lines), len(result.pieces))
```

Tag a string by script and word type, and list the synthetic-data recipes:

```sh
.venv/bin/greekocr annotate 'ἅλφα Latin'
.venv/bin/greekocr recipes
```

## Test material

The test fixtures include line and page crops from third-party digitised books and datasets. They are here only so
the tests can run, and they keep their sources' rights. Do not reuse them as a dataset.
