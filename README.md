# Greek OCR toolkit

Tools for reading printed Greek, especially polytonic Greek from 19th- and 20th-century books, with OCR.

The toolkit covers the whole path from page image to text:

- finding the text lines on a page;
- cutting them into recognition pieces;
- making synthetic training lines and collecting real ones;
- running and comparing line readers;
- scoring the results;
- plugging a reader into [Docling](https://github.com/docling-project/docling).

Everything sits behind one typed Python package, `greekocr`, with a command-line tool of the same name and an offline test suite.

> **Status: in active development.** APIs, file formats and results still change between commits. Experimental work
> lives on branches before it reaches `main`.

## Principles

- **A PDF text layer is another OCR, not ground truth.** It is never a reference, a judge input or a calibration target.
- **Provenance is recorded.** Data, recipes and results carry the hashes and receipts needed to reproduce them.
- **Fast methods are checked against slow, explicit ones.** A heuristic stays only if it tracks a real feature of the
  page and agrees with the explicit method.
- **Offline by default.** Network calls (source discovery, cloud OCR services, pod operations) happen only when the
  matching function is called explicitly. The tests use recorded responses and mocks.

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

Tag a string by script and word type:

```sh
.venv/bin/greekocr annotate 'ἅλφα Latin'
```

List the synthetic-data recipes:

```sh
.venv/bin/greekocr recipes
```

## What is in the package

| Module | What it does |
| --- | --- |
| `greekocr.pages` | Page analysis: text lines, their geometry and recognition pieces (`process_page`, `process_book`). |
| `greekocr.glyphs` | Glyph-level measurements of line crops (letters, accents, ink) without a reference text. |
| `greekocr.readers` | Local line readers and explicitly enabled service readers (Document AI, Cloud Vision, Transkribus). |
| `greekocr.score` | Strict character error rate, accent F1, look-alike diagnostics and per-category summaries. |
| `greekocr.synth` | Synthetic-line recipes, calls to the Rust line factory, and reproducible data mixes. |
| `greekocr.real` | Collecting real lines: source parsers, text-layer extraction, two-reader adjudication, import. |
| `greekocr.annotate` | Script, word and line tags, plus line metadata. |
| `greekocr.verify` | Independent checks of image readability and text quality. |
| `greekocr.harvest` | Provenance-preserving harvesting of pilot labels. |
| `greekocr.warmstart` | Converting donor model weights and checking numerical parity. |
| `greekocr.deploy` | The Docling `glossapi` OCR plugin and reviewable deployment plans. |
| `greekocr.ops` | Receipts, hash checks, rate limits, secrets from the environment, bounded job watching. |

`greekocr/_vendor` holds the original source logic that the typed APIs wrap, kept byte-for-byte with its origin
recorded in [docs/INVENTORY.md](docs/INVENTORY.md). `prototypes/` holds experimental code that is not yet part of the
package.

## Documentation

- [Working with page images](docs/PAGES_GUIDE.md), [page pipeline](docs/PAGES_PIPELINE.md),
  [output format](docs/PAGES_OUTPUT_FORMAT.md), [line-finding algorithm](docs/PAGE_LINES_ALGORITHM.md)
- [API examples](docs/API.md), [line metadata](docs/LINE_METADATA.md)
- Service readers: [Document AI](docs/READERS_DOCAI.md), [Cloud Vision](docs/READERS_VISION.md),
  [Transkribus](docs/READERS_TRANSKRIBUS.md)
- [Readability checks](docs/VERIFY.md), [rendered web pages as label data](docs/WEB_RENDER.md)
- [Repository standard](docs/STANDARD.md), [validation](docs/VALIDATION.md)
- Research notes and reviews: [docs/research](docs/research), [docs/reviews](docs/reviews)

## Test material

The test fixtures include line and page crops from third-party digitised books and datasets. They are here only so
the tests can run, and they keep their sources' rights. Do not reuse them as a dataset.
