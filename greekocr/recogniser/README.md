# Recogniser API, phase 1

Every new OCR tool must call `greekocr.recogniser`. Pinned callers retain their
original imports until gate re-certification. This package imports the existing
implementations; it does not copy preprocessing, forward, decoding or alignment
algorithms.

```python
from greekocr.recogniser import load, align, AlignmentCache, forbid_forward

recogniser = load(checkpoint, device='cpu', threads=4)
readings = recogniser.read(crops, profile='labelfix', bs=16)
alignment = align(readings[0])
evidence = alignment.evidence(alignment.slots(), image_width)
reader = recogniser.as_reader(profile='eval')
text = reader.read(crop_path)
```

| Old entry | API |
|---|---|
| `ctc_align.Recognizer.align_batch` | `load(...).read(images, profile='labelfix')`, then `align(reading)` |
| `ctc_align.Alignment` | `Alignment` (subclass; inherited record/evidence methods) |
| `recognition_evidence` | `alignment.evidence(slots, image_width)` |
| `readers.ours.load_ours` / `E1Reader.read` | `load(...).as_reader(profile='eval')` |
| Docling `Recognizer.recognize` | `load(...).read(float32_strips, profile='serve')` |
| `E1.logits` | `recogniser.logits(images, dtype=np.float64)` |
| `transfer_alignment` / `transfer_record` | `transfer(alignment_or_record, new_text)` |
| `validate` / `sample` / `m2` caches | `AlignmentCache(path, recogniser).get(crops)` |
| shard forward loops | `run_shard(crops, recogniser, cache_path, bs=16)` |
| local replay monkeypatches | `with forbid_forward(): ...` |
| float64 frame-mean comparisons | `confidence_matches(frames, confidence)` |

`load(checkpoint, codec=None, device='cpu', threads=None, strict=True)` validates
codec version, codec SHA, class count and NFD head. Missing codec SHA fails strict
mode. A missing head retains the existing loaders' NFD default. `strict=False`
records binding issues and preserves each delegated profile's original checks;
it does not suppress failures in that original loader. Backends load lazily per
profile. No downloads or checkpoint conversion occur.

`labelfix` delegates to `ctc_align.Recognizer.align_batch`, keeping input order and
batch composition; its raw spans are **not rounded**. `eval` delegates to
`E1Reader.read`, one path at a time. PIL inputs are temporarily serialized as PNG
for that path-based API. `serve` delegates to the Docling plugin Recognizer;
prepared 48-row float32 strips pass through unchanged. PIL/path inputs use the
plugin's `extract_strip` on the whole crop. Serve text is NFC; eval and labelfix
retain their original atom strings. The profiles have distinct background/halo
rules; no profile is selected as a universal replacement.

`Reading` carries `text`, `profile`, `provenance`, optional `alignment`,
`confidence`, `frames`, `scale`, `strip_width`, and `ids`. Fields unavailable from
the original public method stay `None` (including `ids`; eval has no confidence
or alignment). `align()` explicitly rejects a reading with no alignment. No
extra forward is performed to synthesize missing fields. `logits()` delegates to
`E1.logits`, whose float halo differs from `E1Reader.read`, and casts to float32
by default; request float64 explicitly for the old returned dtype.

`Alignment.slots()` groups existing atom spans by the frozen text-cluster
function. It exports locator windows, not detector observations or physical ink
ownership. `evidence()` inherits the frozen score computation. Serialization and
alignment SHA contain no added provenance fields. Reading provenance and cache
row envelopes hold checkpoint/safetensors/codec/package/implementation hashes,
device, float32 model dtype, torch version and binding issues separately.

`transfer()` returns an Alignment for either record or object input. It always
normalizes the requested text to NFD, drops frame scores (and therefore their
serialized prediction hash), and flags `transferred`, including identity
transfers. It delegates nearest-neighbour span assignment to the old function.
This differs deliberately from the old identity no-op and from `transfer_record`,
which retains frame scores without an explicit flag. The originals stay frozen.

The cache delegates its sole strict `crop_key` to C1's existing helper: paths must
contain `docs/harvest/`. It round-trips **every** returned alignment through
`to_record`/`from_record`, including first-run results. It accepts old cache rows
without provenance, rejects duplicate canonical keys and reports unreadable
inputs by exception with their input index. It is a single-writer append-only
cache; shards must have distinct output paths. The replay guard is process-local,
nestable, and restores methods on exit; it is not a thread isolation mechanism.

Run offline golden/unit tests with `python -m pytest tests/recogniser -q -s`.
The frozen cache root defaults to the sibling spellcheck worktree and can be set
with `CU3_CACHE_ROOT`. Local R0 locked caches are included when present. The 17
L1F witnesses are copied verbatim into `tests/recogniser/fixtures/`.
`tests/recogniser/parity.py` is a separate explicit experiment, never collected
by pytest: 200 seeded distinct held-out crops, CPU, four intra-op threads, one
interop thread. It compares old and wrapper paths and measures profile text
differences without ranking them. Do not run it without forward authorization.
