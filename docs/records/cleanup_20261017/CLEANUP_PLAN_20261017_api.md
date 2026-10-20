# Recogniser + card tooling: API inventory and consolidation proposal

Read-only analysis, 17 Oct 2026. Sources: worktrees `greek-ocr-toolkit-spellcheck` (opus/spellcheck, b97cdd10, "SC" below),
`-l1f` (ed5037ae), `-s8` (2e1efb3b), `-r0` (7cef606f), `-r1` (f6d74a52), `-sol-collect` (e6d6d266), `greek-ocr-toolkit` (main/fable,
4e95489d) and `greek-page-ocr` (45e09f0). Facts are from code; "unclear" marks what the code does not settle.
Copies under `artifacts/*/deploy/` and `docs/records/reviews/*/before_sf2/` are frozen evidence snapshots. They are not counted as live code.

---

## Part 1: the OCR recogniser (E3 CTC, `full_s0`)

### 1.1 What exists: three independent recogniser stacks plus their copies

All of them build on the same vendored training code: `greekocr/_vendor/train/{model.py, cer.py, ckpt_io.py, data.py}`. Per
`greekocr/_vendor/origins.json`, these are copied from greek-page-ocr `train/` at b7818f3f with only the import paths relocated.

| # | Stack | Entry | Loader | Strip preprocessing | Forward | Decode | Output |
|---|---|---|---|---|---|---|---|
| A | **Serve/plugin** `Recognizer` | `greekocr/deploy/docling_plugin/recognizer/inference.py:Recognizer.recognize(strips)` | own `recognizer/ckpt_io.load_model_weights` (a copy of `_vendor/train/ckpt_io`, with safe_globals for NumPy, enforces codec_version + codec_sha256 + n_classes + head) | caller supplies **float32** strips from `recognizer/strips.extract_strip(page, box)`: 10% vertical pad, polarity flip, LANCZOS to 48, letterbox to 2560, min width 64 with a float bg | own `recognizer/model.masked_forward` (a copy of `_vendor/train/model.py` without the svtrv2/a32 arms); **float** own-bg halo (`np.median`, not rounded), DET_PAD_MARGIN=128 | own `recognizer/codec.greedy_decode_line` (a copy of `_vendor/train/cer.py`) | `(NFC text, mean max-prob)` |
| A' | Vendored twin of A | `greekocr/_vendor/pipeline/recognize.py:Recognizer` | `_vendor/train/ckpt_io` (no safe_globals; **no head/n_classes check**) | same as A | `_vendor/train/model.masked_forward` | `_vendor/train/cer.greedy_decode_line` | `(NFC text, conf)` |
| B | **Evaluation reader** `E1Reader` (`load_ours`) | `greekocr/readers/ours.py:load_ours -> _vendor/bench/e2_reader_parity.py:E1Reader.read(path)` | via `_vendor/bench/o4b_models.E1.__init__` -> stack A' | `o4b_models.strip(image)`: LANCZOS to 48, letterbox, **float `np.median`** bg on the min-64 canvas, then `np.rint(*255)` to uint8. 48-px L images pass through unchanged | `_vendor/train/data.collate_strips` (uint8, `int(round(median))` halo) + `masked_forward` under `inference_mode`, batch of 1 | `_vendor/train/cer.greedy_decode_line`, raw NFD | NFD text only (no confidence, no frames) |
| B' | `E1.read` / `E1.logits` | `_vendor/bench/o4b_models.py:E1` | stack A' | `strip()` float | `read`: A'.recognize (float halo, NFC). `logits`: `np.pad` float halo, returns **float64** log-probs | A' / none | NFC text / `[T,C]` float64 |
| C | **Labelfix aligner** | `greekocr/labelfix/ctc_align.py:Recognizer.align_batch / align_paths` | `_vendor/train/ckpt_io` (checks codec_version + n_classes, **not codec_sha256 or head**). Default codec `_vendor/codec/v1.json` | `make_strip(image)`: LANCZOS to 48 directly in uint8, letterbox (14-px floor), bg = **upper median** `sorted(tail)[n//2]` (not averaged), min 64 | uint8 canvas, `int(round(median))` halo, `(x/255-.5)/.5`, `masked_forward` under `no_grad`, width-sorted batches (bs 16 by default) | `frames_to_spans` (spike runs = collapse + drop blank) | `Alignment(prediction NFD, spans, n_frames, scale=w/nw, strip_width, confidence=float32 mean of max-prob incl. blank, frame_confidences float32->list)` |

The greek-page-ocr origins:
- `pipeline/recognize.py` is the origin of A' and A.
- `bench/o4b_models.py` and `bench/e2_reader_parity.py` are the origins of B and B'.
- `train/eval_cer.py:evaluate` is the reference evaluation path. It uses **bf16 autocast on CUDA** (`model.amp_dtype_for`; called from `bench/e1_eval.py:164`).
- `train/dump_preds.py` is a second ids-to-text dumper.
- `bench/o4b_align.py:forced/greedy/align_page` is a **CTC Viterbi forced aligner**. It is not vendored into the toolkit.

The E3 prediction files (`out/e3b/predictions/full_s0_*.jsonl`, the `model` field the labelfix code uses) were most likely produced through
the bf16 GPU evaluate path. The labelfix forward pass is fp32. This is plausibly why "recorded prediction ≠ re-run prediction", and so why
`transfer_alignment` exists. That last link is inferred: the code comment says only "re-run prediction differs slightly from the recorded one".

### 1.2 Inventory by file (live code, SC unless noted)

| File:function | Capability | Inputs -> outputs | Duplicates / notes |
|---|---|---|---|
| `greekocr/labelfix/ctc_align.py:make_strip` | preprocess | PIL crop -> uint8 [48,W], crop px per strip px | 4th strip implementation (vs `strips.extract_strip`, `o4b_models.strip`, `_vendor/bench/extract_lines`, factory `import_real.rs`) |
| `ctc_align.py:Recognizer.__init__` | load | ckpt path (`.pt`; resolves the `.safetensors` sibling), codec -> model | duplicates A/A' loading with weaker binding checks |
| `ctc_align.py:Recognizer.align_batch` | forward + decode + frame confidence | PIL list -> `[Alignment]` | the **canonical labelfix forward pass**. Every L1/C1/R0/M2 path runs through it |
| `ctc_align.py:Recognizer.align_paths` | batching | paths -> `{path: Alignment}`; sorts by aspect ratio, **silently skips** unreadable crops | callers re-implement the sort (l1f_run) or isolation (c1_run) |
| `ctc_align.py:frames_to_spans` | align | argmax ids -> CharSpan (midpoint-of-neighbour-spikes, x = t·4·scale) | unique |
| `ctc_align.py:Alignment.{to_record,from_record}` | serialise | rounds x0/x1 to 0.1 px; adds `frame_prediction_sha256`; marks `transferred` | in validate/sample the **first run returns unrounded objects** and the replay returns rounded ones (m2_run deliberately round-trips; validate.alignments_for and sample.align_records do not) |
| `ctc_align.py:Alignment.window/char_width/span` | slot geometry | index range -> crop x range | used by sheet, spellink, print_truth, candidates |
| `ctc_align.py:Alignment.recognition_evidence(slots, image_width)` | evidence | detector slots -> `ctc-window-score-v1` regions (min of frame confidences over `[floor(x0/4s), ceil(x1/4s))`) | **consumed by the frozen gate** (`release_gate._recogniser_scored`) |
| `ctc_align.py:recognition_fields(runtime)` | evidence carry | runtime dict -> confidence/evidence/image_width with a legacy default | used by l1_infer, l1e_run, l1e_measure, l1r4_join |
| `ctc_align.py:transfer_alignment(text, al)` | alignment transfer | text + Alignment -> Alignment (matched chars keep spans, unmatched take the nearest neighbour; **drops frame_confidences**, sets `transferred`) | **copied** as `scripts/labelfix/clariden/r1_common.py:transfer_record` |
| `scripts/labelfix/clariden/r1_common.py:transfer_record(text, rec)` | alignment transfer on dict records | -> (record, transferred) | Differences from `transfer_alignment`: (a) NFD-normalises `text` first; (b) **keeps** `confidence`, `frame_confidences` and `frame_prediction_sha256` in the dict and sets no `transferred` flag. `from_record` still flags it through the sha mismatch, but only when frame_confidences are present; (c) works on record-rounded spans. test_r1 asserts equal spans |
| `greekocr/labelfix/validate.py:alignments_for` / `sample.py:align_records` | cache + forward | lines -> `{crop: Alignment}`, append-only `align_s{seed}.jsonl` | **near-identical twins** (only the cache name and crop prefix differ). Keyed by raw crop path. Readers (`sheet.load_alignments`) key by `crop_key` |
| `greekocr/labelfix/sheet.py:load_alignments, crop_key` | cache read | jsonl -> `{crop_key: Alignment}` | `crop_key` is **duplicated** in `clariden/c1_common.crop_key` with different semantics: sheet returns the path unchanged if `docs/harvest/` is absent; c1 **raises** |
| `greekocr/labelfix/segmentation.py:recogniser_slots` | slot export | ink, text, alignment -> per-letter regions | calls transfer_alignment(nfd(text)); overlaps conceptually with `toolkit_geometry.physical_slots` |
| `greekocr/labelfix/toolkit_geometry.py:physical_slots` | slot export | ink, text, alignment -> slots with `locator_span` | second span->component owner assignment (sqrt-width normalised overlap) |
| `greekocr/labelfix/reading.py:read_ink` | slot export + evidence windows | ink, text, alignment, detector -> `LineReading.slots` (each with `evidence.window`) | producer of the windows `recognition_evidence` scores |
| `greekocr/labelfix/{candidates,linemetric,markshape_train,spellink,spellcheck_validate}.py` | transfer callers | `if nfd(al.prediction)!=model: transfer_alignment(model, al)` | idiom repeated ~20 times. **Some pass `l['model']` un-normalised** (linemetric:71, spellcheck_validate:73, markshape_train:34, s3_validate:70, print_truth/build:22) and others pass `nfd(...)`. Whether `model` is always NFD is unclear: the E3 predictions are raw NFD atoms, but owner_pages loads `nfc(gt)` for other fields |
| `scripts/labelfix/clariden/c1_run.py:worker` | cluster forward | selection shard -> `worker_{rank}.jsonl.gz` of `alignment.to_record()` | per-crop isolation fallback; **CUDA** device, `threads` |
| `scripts/labelfix/clariden/r1_extract.py:extract_line, window_geometry, window` | slot export (R1 windows) | record + alignment dict + image -> 128×64 windows, coverage (`r1-trained-full-height-v1`) | uses `transfer_record`; gates on line `confidence < .5` (the same floor as `release_gate.RECOGNISER_ABSENCE_FLOOR`, defined separately) |
| `scripts/labelfix/clariden/r1_pixels.py` | font size / fused ink | independent Otsu + union-find | "independent of ink.py" by design; a third connected-components implementation |
| `scripts/labelfix/clariden/l1_detect.py:chunk` | evidence | saved alignment -> runtime with `recognition_evidence` | from_record of C1 alignments. **C1 records carry no frame_confidences** (ctc_align 1a753b30 was pinned for C1), so this evidence is unscored |
| `scripts/labelfix/clariden/l1_infer.py`, `l1e_run.py`, `l1e_measure.py` | evidence carry | `recognition_fields(r)` | R1 MarkReader load duplicated: `l1_infer.load_reader`, `l1e_run` ×2, `m2_run:208`, `r0_freeze_ib:281` (the last with **weights_only=False**) |
| **l1f** `scripts/labelfix/clariden/l1f_run.py:worker, make_record` | re-forward + evidence | saved C1 alignment + runtime -> frame evidence `l1f-frame-evidence-v1` | re-implements the `align_paths` sort ("align_paths' original stable width sort"), then calls `align_batch`. Identity check `IDENTITY_KEYS` against the saved record. **CUDA** |
| **l1f** `l1r4_join.py:validate_record` | evidence verify | recomputes the float64 mean of the frames vs the float32 `confidence` (`abs_tol=2e-7`) | **failed on 17/124,669 rows** (gap ≤ 2.48e-7). The L1R4b brief changes it to 1e-6. The code at ed5037ae still reads 2e-7 (brief committed, fix pending) |
| **l1f** `l1f_mock_check.py:39` | same predicate | `abs_tol=2e-7` | brief says to leave it (L1F closed) |
| `scripts/labelfix/m2_run.py` | forward + cache + evidence | `make_strip` as a crop validity probe; `align_batch`; round-trips `to_record`; `recognition_evidence` | its own CTC cache (`align_s0.jsonl` with checkpoint+crop sha). Guards `Recognizer.__init__/align_batch=forbidden` in replay |
| `scripts/labelfix/r0_prepare.py`, `r0_freeze_ia.py`, `r0_freeze_ib.py` | forward + cache | `align_paths(bs=8 \| 16)` -> `align_locked_{s0,ia,ib}.jsonl`; `code_sha256=sha(ctc_align.py)` | bs differs (8 vs 16). Halo padding is meant to make results batch-invariant; float-level batch effects on CPU are unclear |
| `scripts/labelfix/{k1_validate,cn1_offline,s6,s7_validate,s7_launch_baseline}.py` | no-forward guards | monkeypatch `Recognizer.*=forbidden` | five copies of the same guard |
| `scripts/labelfix/{owner_pages_build,owner_pages_build_combined,owner_implicit_adjudication_prep,s2_validate,s3_validate,sf2_replay}.py`, `docs/records/labelfix/spellcheck/{memo/*.py,print_truth/build.py}` | transfer callers | cache + transfer + window | doc-folder scripts are live importers of `ctc_align` |
| `greekocr/glyphs/orientation.py:recognizer_polarity` (sol-collect, SC) | serve use | uses stack A (`strips.extract_strip` + `.recognize`) | correct reuse |
| `greekocr/cli.py:308` | evaluation use | `load_ours` (stack B) | correct reuse |
| `greekocr/_vendor/bench/e2_teachers.py:reader`, `e2_reader_parity.qualify_readers` | load | `torch.load(weights_only=False)` for state-hash checks | vendored evaluation, trusted-path only |
| sol-collect `collect_v3/*` | none | Document AI only (`collect_v3/reader.py`) | no recogniser code |

### 1.3 Duplication matrix (live code)

`●` = implements, `○` = calls the canonical one, `◐` = re-implements the logic partly or as a copy, blank = not involved.

| Capability | deploy `inference.py` (A) | `_vendor/pipeline/recognize` (A') | `o4b_models.E1` / `E1Reader` (B) | `ctc_align.py` (C) | `r1_common` | `validate`/`sample` | `c1_run` | `l1f_run` | `l1r4_join` | `m2_run` | `r0_*` | `segmentation`/`toolkit_geometry` | `r1_extract` | greek-page-ocr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| load checkpoint | ● own ckpt_io copy | ● | ○ A' | ● | | ○ | ○ | ○ | | ○ | ○ | | | ● `eval_cer.load_checkpoint` |
| codec binding check | ● ver+sha+n+head | ● ver+sha | ○ | ◐ ver+n only | | | | ◐ adds the sha check itself | | ◐ checkpoint sha | ◐ ckhash | | | ● |
| preprocess (strip) | ● `strips.extract_strip` | (caller) | ● `strip` float + uint8 requant | ● `make_strip` uint8 | | | | | | ○ probe | | | | ● Rust `import_real`, `dump_preds` |
| halo pad + normalise | ● float bg | ● float bg | ● `collate_strips` int bg | ● int bg | | | | | | | | | | ● `collate_strips` |
| forward | ● | ● | ● | ● | | | | ○ align_batch | | ○ | ○ | | | ● bf16 on CUDA |
| greedy decode | ● (NFC out) | ● (NFC) | ● raw NFD | ◐ via spikes (NFD) | | | | | | | | | | ● |
| frame confidence | ◐ line mean only | ◐ line mean | | ● frames + mean (float32) | | | | ○ | ◐ recomputes float64 mean | | | | ◐ reads line conf | |
| batching / sort | ● width sort | ● | (bs 1) | ● aspect sort | | | ◐ isolation | ◐ re-sorts | | ◐ own sort | ○ | | | ● |
| alignment cache | | | | | | ● ×2 twins | ● writer | ● sqlite plan | | ● own cache | ● `align_locked_*` | | | |
| alignment transfer | | | | ● | ◐ **copy** | | | | | | ○ | ○ | ○ (copy) | (Viterbi `o4b_align.forced`) |
| slot export | | | | ◐ `window` | | | | | | | | ● ×2 | ● R1 windows | |
| evidence | | | | ● `recognition_evidence`/`recognition_fields` | | | | ○ + identity | ◐ reconstructs | ○ | | | ◐ coverage | |
| no-forward guard | | | | | | | | | | ● | | | | |

### 1.4 Behavioural differences that matter (bit-level hazards)

1. **Strip background**: `ctc_align.make_strip` takes the *upper* median of the uint8 tail. `o4b_models.strip` takes the *averaged* `np.median`
   in float and then `rint`s it (round-half-even). The two differ only on the fill area: the min-64 pad and the letterbox bands. So
   **E1Reader text and the ctc_align prediction can differ on narrow (<64 px) or letterboxed strips**. Unclear how often; no parity test
   compares B and C.
2. **Halo**: stacks A and A' use a float `np.median` halo and float32 strips that are never quantised. Stacks B and C quantise to uint8 and
   round the bg. So serving output and evaluation/labelfix output are not guaranteed bit-identical.
3. **Text normal form**: A and A' return **NFC**. B and C return **raw NFD atoms**. `E1.read` (B') returns NFC while `E1Reader.read` returns
   NFD, under the same class name family.
4. **Confidence**: C's line `confidence` is a numpy **float32** mean of float32 per-frame maxima. `frame_confidences` holds the exact float32
   values as Python floats. Any consumer that recomputes in float64 (`l1r4_join`, `l1f_mock_check`) sees gaps up to about 2.5e-7. That is
   the L1R4 failure. Device matters too: C1 and L1F ran on **CUDA**, R0 and M2 on **CPU**.
5. **Precision of the recorded text**: E3 predictions (the `model` field) come from the bf16-autocast evaluator on GPU (likely). Labelfix
   re-runs in fp32. Hence transfers.
6. **Transfer semantics**: `transfer_alignment` drops frame_confidences (the evidence then becomes unscored by construction).
   `transfer_record` keeps them in the dict. `from_record` re-flags `transferred` through `frame_prediction_sha256`, but only if
   `frame_confidences` is present. A record transferred before frames existed carries no flag. It is currently harmless, because no frames
   means unscored.
7. **Rounding on first run vs replay**: `to_record` rounds spans to 0.1 px. `validate.alignments_for` and `sample.align_records` return
   unrounded objects on the first run and rounded ones on the replay. `m2_run` normalises; these two do not.
8. **Codec binding**: only stack A checks `codec_sha256` and `head`. C checks `codec_version` and `n_classes`. `l1f_run` adds a codec sha
   check by hand.
9. **Silent skips**: `align_paths` drops unreadable crops without reporting them. `c1_run` compensates; `validate`, `sample` and `r0_*` do not.
10. **`crop_key`**: lenient (`sheet.py`) vs strict (`c1_common.py`).
11. **Two ckpt_io copies**: the deploy copy has safe_globals and no converter; the vendored copy is older (doc mentions
    `convert_pt_to_safetensors`). Both resolve the `.safetensors` sibling first, so `full_s0/best.pt` loads `best.safetensors` everywhere.

### 1.5 Deploy-pinned and gate-bound files (cannot change silently)

| Pin | `ctc_align.py` | `release_gate.py` | `r1_common.py` | others recogniser-relevant |
|---|---|---|---|---|
| `C1_DEPLOY_SHA256.txt` (SC) | 1a753b30 (old: no frames) | — | — | `_vendor/train/{model,cer,ckpt_io}.py`, `codec/v1.json`, `clariden/c1_*.py` |
| `R1_DEPLOY_SHA256.txt` (SC) | 1a753b30 | — | 45aff915 | `reading.py`, `sample.py`, `validate.py`, `spellcheck_validate.py`, all `clariden/r1_*.py`, `.cache/labelfix/align_s0.jsonl`, `C1_alignments.jsonl.gz` |
| `L1E_evidence/L1E_DEPLOY_SHA256.txt` (SC) | 1a753b30 | c82f7fb3 | 45aff915 | **all** `_vendor/bench/*`, `_vendor/train/*`, `readers/*`, `labelfix/{reading,sample,validate,spellcheck_validate}.py`, `clariden/{c1,l1,l1e,l1r,r1}_*.py`, `m2_run.py`, `k1_validate.py`, `owner_reading.py`, `s2..s7_validate.py` |
| l1f `L1F_/L1R3_/L1R4_DEPLOY_SHA256.txt` | **3ecb1a20** (current) | **9ef1d646** (current) | 45aff915 | as L1E, plus `l1f_*.py`, `l1r*_*.py`, `r0_score_validate.py` |
| s8 `S8_DEV/evidence/S8a3/S8F_DEPLOY_SHA256.txt` | — | — | — | data + `s8_fetch_job.sbatch` only |

- `release_gate.policy_binding()` hashes `ctc_align.py`, `m2_run.py`, `segmentation.py`, `text.py`, `owner_reading.py`,
  `owner_pages_build_combined.py`, `clariden/{l1_common,l1r_recompose,r1_extract,l1_infer,l1e_measure,l1e_run,l1_detect,r1_common}.py`
  into the policy sha. **Any byte change to any of them changes the release policy digest.** The L1R4b brief requires `release_gate.py` and
  `ctc_align.py` byte-identical to d893a04d (3ecb1a20 / 9ef1d646).
- The gate's evidence contract lives in `release_gate._recogniser_scored`: schema `ctc-window-score-v1`, provenance
  `saved_alignment_confidence` / `minimum_max_frame_posterior_including_blank`, `text_sha256` over NFD, a 64-hex `alignment_sha256`
  (sha of `json.dumps(Alignment.to_record(), sort_keys=True)`), frames as ints, floor 0.5. A refactor that changes `to_record` key order or
  content, rounding, or the frame bounds changes `alignment_sha256` and breaks verification of every saved row.

### 1.6 Proposed API: `greekocr.recogniser`

One package, one forward pass, behaviour pinned to **today's `ctc_align` semantics** (stack C), because that is what every saved alignment,
evidence row and gate digest was produced with. Stacks A and B become *profiles* of the same pipeline, not separate code.

```python
# greekocr/recogniser/__init__.py
from .model import Recogniser, load            # load(checkpoint, codec=VENDOR_CODEC, device='cpu', threads=None) -> Recogniser
from .strip import Strip, make_strip, PROFILES # PROFILES = {'labelfix': ctc_align.make_strip, 'eval': o4b_models.strip, 'serve': strips.extract_strip}
from .reading import Reading                   # text_nfd, frames (float32 ndarray [T]), confidence (float32), argmax ids, strip geometry
from .alignment import Alignment, CharSpan, align, transfer, frames_to_spans
from .evidence import window_evidence, recognition_fields   # schema ctc-window-score-v1, byte-identical output
from .cache import AlignmentCache              # jsonl/gz, keyed by crop_key (one strict definition), stores checkpoint+crop+code sha
from .batch import run_shard                   # cluster entry: selection shard -> records + receipt (c1_run / l1f_run worker)
from .provenance import Provenance             # checkpoint_sha256, safetensors_sha256, codec_sha256, code_sha256 (module digest), device, dtype, torch version
from .guard import forbid_forward              # replaces the five monkeypatch copies
```

- `load(checkpoint, codec) -> Recogniser`: one loader (the deploy `ckpt_io` with safe_globals). It enforces codec_version, codec_sha256,
  n_classes and head, which is the union of today's checks. It records `Provenance`.
- `Recogniser.read(images, *, profile='labelfix', bs=16) -> [Reading]`: width/aspect-sorted batches with the halo. Each Reading has
  `text` (NFD), `frames` (float32 per-frame max posterior incl. blank), `confidence` (float32 mean, stored as `float(np.float32)`),
  `ids`, `scale`, `strip_width`. `profile` selects the strip function, the halo (int vs float bg) and the output normal form. `serve` =
  today's A (NFC out). `eval` = B (bit-parity with `E1Reader`). `labelfix` = C. Reports unreadable inputs explicitly instead of skipping them.
- `Recogniser.logits(images) -> [ndarray]` (replaces `E1.logits`; float64 only by explicit `dtype=`).
- `align(reading) -> Alignment`: `frames_to_spans`, unchanged.
- `Alignment.slots()` (span list per cluster) and `Alignment.evidence(slots, image_width)`: the current `recognition_evidence`,
  **byte-identical**.
- `transfer(alignment, new_text) -> Alignment`: one implementation over a record-or-object. It always NFD-normalises, always drops frames
  and always sets `transferred`. `r1_common.transfer_record` becomes a 3-line adapter.
- `confidence_matches(frames, confidence)`: **one predicate with the float32 tolerance** (recompute the mean in float32, or `abs_tol=1e-6`),
  used by l1r4_join and l1f_mock_check.
- Provenance on every record: `checkpoint_sha256`, `safetensors_sha256`, `codec_sha256`, `code_sha256` (sha of the `greekocr/recogniser`
  package files), `device`, `dtype`, `torch`.
- Later and optional: `force_align(reading, text)`, a Viterbi path over the frame log-probs, ported from greek-page-ocr
  `bench/o4b_align.forced`. This is the principled replacement for nearest-neighbour transfer. It **changes outputs**, so it needs its own
  validation round and must not be swapped in.

### 1.7 What replaces each duplicate, and which callers change

| Existing | Replaced by | Callers to change |
|---|---|---|
| `labelfix/ctc_align.py` (Recognizer, make_strip, Alignment, frames_to_spans, transfer_alignment, recognition_*) | `greekocr.recogniser.*` (code moved). **`ctc_align.py` stays as a frozen shim** | none at first; new code imports `greekocr.recogniser` |
| `deploy/docling_plugin/recognizer/{inference,ckpt_io,codec,model}.py` | `greekocr.recogniser` with `profile='serve'`. The plugin keeps its own copy **only if** it must ship standalone (it is the glossAPI plugin). Then generate it from `greekocr.recogniser` with a parity test | `deploy/docling_plugin/model.py`, `glyphs/orientation.py` |
| `_vendor/pipeline/recognize.py` | delete from vendor or keep as origin record; route `o4b_models.E1` to `greekocr.recogniser` | `_vendor/bench/o4b_models.py` (vendored, so record the transform in `origins.json`) |
| `readers/ours.py:load_ours -> E1Reader` | `greekocr.recogniser.load(...).as_reader(profile='eval')` | `cli.py:308`, `tests/test_warmstart_readers.py` |
| `validate.alignments_for` + `sample.align_records` + `sheet.load_alignments` + m2/r0 caches | `AlignmentCache(path, recogniser).get(crops)` (round-trips every new result through `to_record`) | validate, sample, sheet, owner_pages*, print_truth, memo/*, s2/s3, sf2_replay, m2_run, r0_* |
| `sheet.crop_key` + `c1_common.crop_key` | `greekocr.recogniser.cache.crop_key(strict=...)` | all |
| `r1_common.transfer_record` | `recogniser.transfer` on records | r1_extract (pinned, see below) |
| `l1r4_join` / `l1f_mock_check` mean checks | `recogniser.confidence_matches` | l1r4_join (L1R4b is already editing it) |
| `c1_run.worker`, `l1f_run.worker` forward loops | `recogniser.batch.run_shard` | c1_run, l1f_run (pinned) |
| 5× `Recognizer.*=forbidden` | `recogniser.guard.forbid_forward()` | k1_validate, cn1_offline, s6/s7_validate, s7_launch_baseline, m2_run |
| R1 MarkReader loading (5 sites) | `scripts/labelfix/clariden/r1_model.load(checkpoint)` (weights_only=True everywhere) | l1_infer, l1e_run, m2_run, r0_freeze_ib |
| repeated `if nfd(al.prediction)!=model: transfer(...)` idiom | `alignment.for_text(text)` (NFD-normalises once) | ~20 call sites; fixes the un-normalised ones |

### 1.8 Shims for pinned and gate-bound code

- **Do not edit `ctc_align.py`, `release_gate.py`, `r1_common.py`, `r1_extract.py`, `m2_run.py`, `l1_*`, `l1e_*`, `l1r_*` and
  `segmentation.py` in place.** Their bytes are in `release_gate.policy_binding()` and in the L1E/L1F/L1R3/L1R4 manifests.
- Phase 1: build `greekocr.recogniser` by **importing from** `ctc_align` (the new package wraps the old code, so it has zero behaviour
  change and no pinned bytes change). New callers use the API.
- Phase 2, at the next gate re-certification (a new policy version): invert it. The code moves into `greekocr.recogniser` and `ctc_align.py`
  becomes `from greekocr.recogniser.compat import *`. Then:
  - (a) `policy_binding()` must list the new package files (the policy digest changes on purpose, under a new `POLICY` schema name);
  - (b) a **golden test** must show byte-identical `to_record()`, `recognition_evidence()` and `alignment_sha256` on the frozen
    `align_s0.jsonl`, `align_locked_*.jsonl` and the 124,669 L1F rows;
  - (c) a re-forward parity check (CPU, 200+ crops) must match `align_batch` exactly.
- Keep the evidence schema strings and the `to_record` key set/rounding frozen as constants in `recogniser/evidence.py`, with a test that
  pins `alignment_sha256` for fixed fixtures.
- The serving plugin's parity with `profile='serve'` should be a test, not a promise.

---

## Part 2: card / adjudication tooling

Worktrees: SC, S8, L1F, R0, R1, COL (sol-collect), MAIN, SP (this session's scratchpad). Same-name files are byte-identical across SC, S8 and
L1F unless noted.

Older variants:
- R0: `reading.py`, `owner_pages_build_combined.py`, `owner_reading.py`, `m2_score.py`, `owner_implicit_changes.py`; no `r0_wholeline_score.py`.
- R1: `reading.py`, `clariden/r1_owner.py`.
- MAIN: `sheet_build.py`, older. It has no `printed_edited`, its db write is `set` without merge, and it has no stored-slot replay.

About 25 further `greek-ocr-toolkit-*` worktrees were not inspected (sol-funnel-*, sol-wsr0, spellcheck-l1/l1r*/align, ff-*, astra-*).

### 2.1 Inventory

| # | Builder (file:function) | Inputs | Card format (crop / zoom) | Controls | Randomisation | Key separation | Instructions | Answer schema | Scoring / gate |
|---|---|---|---|---|---|---|---|---|---|
| A | `greekocr/labelfix/deck.py:build/card_image/stratified` (+ `deck_serve.py`, `ingest_decisions.py`, `pull_firefox.py`) | candidates + three-way controls | word window ±2 chars, full height, native PNG; browser zoom 2/3/4× pixelated; red letter box, blue word underline | neg 20 + pos 10 per rule (real outcomes); none on `--append` | `Random(20261016)` (+1 on append), wave-stratified, shuffled; shows the correction on 70% of cards (`SHOW_MODEL_SHARE`) | **none**: `deck_data.js` carries `shown_is_model`, `kind`, google, model, human | page text + README template | localStorage `labelfix-deck-v1` `{d:y/n/u}`; POST `/decision`; rows `{id,rule,line_id,word_index,shown,shown_is_model,kind,google,proposed,decision,time}` | per-rule precision + **JS LB95** (lgamma bisection); ingest repeats it with `validate.lb95` (scipy Clopper-Pearson); no gate |
| B | `greekocr/labelfix/sheet.py:render/render_spellcheck/spellcheck_zoom` | results | line base64, box ±3 px; zoom pad xh, 3× NEAREST, guides | – | – | not blind | – | – | – (also hosts `load_alignments`/`crop_key`) |
| C | `scripts/labelfix/r0_prepare.py:planned_cards/card_window/build_cards/preview_controls` | 666 continuity + strata, alignments, S5/S4/M2 candidates | bbox or transferred CTC window, pad 0.6·h, `min(3,900/w)` LANCZOS + full line | `ceil(n·.08/.92)` from `controls_pixel_verified.jsonl`; planted letter (swapcase every 3rd, else confusable) | `Random(20261017)`, items then options | blind `R0_cards[_tag]/items_blind.json` `{id,img,line_img,A,B,C}`; key `R0_adjudication_private[/tag]/items_key.json` (`xb` only when tagged) | `R0_cards/README.md` | viewer localStorage `r0-blind-v1` `{choice,note}`; truth template `R0_expected_truth.json` `{reader_1,reader_2,adjudicated{status:PENDING_R0b}}` | asserts ≥8% controls |
| D | `r0_freeze_ia.py:cards` | – | imports C (`tag='ia'`) | i | i | audit hook forbids private reads; O_EXCL key | i | i | asserts schema, ≥8%, zoom ≤3 |
| E | `r0_freeze_ib.py:cards/preview` | – | **copy of C** (card 0.6·h ≤3×; preview 0.2·h ≤2×) | letter + mark quotas; mark map psili↔dasia, acute↔grave, circ→acute, drop ypogegrammeni and dialytika | `Random(20261017)`, NFC-dedup, 1–3 options | write-once | `R0_cards_ib/README.md` | `r0-blind-ib-v1`, + `full_line_marks` | asserts |
| F | R0 two-reader merge + tiebreak | SP `r0b/*.json`, `mk*.py`, `write_ib2.py` (hand-entered answers) | – | – | tiebreak reuses the original option order | – | – | readers `{id,answer,printed,confidence:str,note}`; tiebreak r3 confidence **numeric** | **no builder in code**; output AGREED/CONTROL/MAJORITY_OF_3/UNRESOLVED |
| G | `r0_score.py` (+ `_report`, `_validate`) | keys + expected truth | review page localStorage `r0c-owner-notes-v1` | – | – | – | – | – | **control gate**: every control correct for both readers on `bare()`; exact status counts asserted; Levenshtein + stratified case estimator; no CI |
| H | `r0_finish.py:review_page` | 60 lines round-robin | SVG native + CTC spans | – | – | not blind | – | `r0-owner-position-v1` | – |
| I | R0 whole-line deck | `R0_wholeline/wl_blind.json` `{id,img}` | – | none | – | `wl_key.json` separate, **but `img` is an absolute path that reveals book/page/line (verified: `…/sol-wsr0/…/r0-ws-df94dc99-p000175-l0005.png`)** | – | `{id,text,confidence,note}`; r3 tiebreak (SP `wl/z3/write.py`) | `scripts/labelfix/r0_wholeline_score.py`: r1==r2 after normalisation, else r3 majority; CER; hard-coded absolute paths; **builder not in code** |
| J | `docs/records/labelfix/spellcheck/print_truth/build.py` + `reconcile.py` + `census_pt.py` | 189 mark diffs + 20 planted | composite PNG: line ≤1600 px + word `min(4,1500/w)` + vowel `min(8,1500/w)` LANCZOS | 20 planted (SWAP map) | `Random(20261016)`, A/B reversed p=.5 | `items_public.json` and `key_SEALED.json` **in the same dir** | none in code | `{id,answer:A/B/NEITHER,printed,confidence,reason}`; r2 files in reverse order | reconcile -> `print_truth_s0.json`; **does not read `answers_tiebreak_r3.jsonl`** (how the tiebreak was applied is unclear); controls counted only |
| K | `scripts/labelfix/owner_implicit_adjudication_prep.py` (= SP `adj_prep.py`) | owner HTML (regex) + regressions | **copy of C crop** (0.6·h, ≤3×) | 8 planted, **appended at end, not position-shuffled** | `Random(20261016)` A/B only | key and blind in the same dir | – | `{id,answer:A/B/neither,printed,confidence,reason}` | scorer not in code |
| L | S8 `scripts/labelfix/s8_prepare.py:census/audit_plan/word_box/control_preview/planted/cards` | waves | **copy of C crop** (0.6·h, ≤3×) | `ceil(n·.08/.92)` round-robin per wave; mark-only planting (odd swap acute↔grave, even delete) | string seeds `'S8a-20261017'+…`; ids `item_`+sha | `private/<tag>/items_key.json` (overwritable) | `<tag>/README.md` | blind `{id,img,line_img,options{},other_options:['none of these','unreadable']}`; blank `{id,choice,transcription,uncertain,note}` | validators `s8_validate_audit/dev.py` |
| M | S8 `s8_score_truth.py:vote/wilson/estimate/score_presence` | blind 1793, cut 703, readers, tiebreak `items_tb.json` (options re-randomised) | – | – | cut seed `S8DEV-adjudication-cut-20261017` | – | – | `{id,answer,printed,confidence,note}`; r2 written in **descending order** by SP `r2*.py` | **control gate** 82/84 per reader, no shared misses; Hájek weights; **document-cluster bootstrap REPS=4000** + Wilson-Kish fallback; writes `dev_truth.jsonl.gz`. Cut/tiebreak deck builders **not in code** |
| N | S8 `scripts/labelfix/l1a2_cards.py` (audit100) | ids, labels, overlays | span ∪ evidence bboxes, pad **0.4·h**, `min(3,1200/w)` | ceil 8%; plant = **delete last mark** | `'L1A2-cards-20261017'+…` | `private/audit100/items_key.json` + **leak scan** (`validate()`) | `audit100/README.md` | S8 schema; r2 reverse; tiebreak re-randomised | final `audit100_final.json` writer **not in code** |
| O | owner sheets: `scripts/labelfix/sheet_build.py:detect/main`, `owner_pages_build.py`, `owner_pages_build_combined.py`, SP `snap4/build_owner_s4.py`, `snap6/build_owner.py` (= `tools/build_owner.py`), `tools/build_owner_r1.py` | runtimes / detector | full line 2× NEAREST if W<700, cap 1000 LANCZOS; green above / blue below / grey attached boxes; slot numbers | – | – | not blind (Google + Ours shown) | page intro | `window.claude` db `notes/{line_id}` `{note,updated}` (+`printed`, `printed_edited`, merge in SC sheet_build); 900 ms debounce | – |
| P | SP `build_audit_template.py`, `build_subst_page.py`, `build_r1a_errors.py`, `build_audit_page.py`, `memo/*_sheet.py`, `lens_check.js` | S8 keys, finals, samples | CSS/JS **taken by `src.split("CSS = '''")` from snap6** (subst splits build_audit_template's source); **hover magnifier** Z=3, lens 300×130, clean crop, tap-toggle; r1a errors: line + word 3× LANCZOS + letter 8× NEAREST | – | `subst_sample` `Random(20261017)` | not blind | intro | db notes; r1a uses doc id `{line_id}:s{slot}` `{note,printed,line_id,slot,updated}` | – |
| Q | `scripts/labelfix/m2_review.py` | m2_score queue | ±18 px, 3× NEAREST, panels of 5 | – | – | not blind | – | – | – |
| R | COL `collect_v3/cards.py:draw/emit/cards/wilson_lower`, `collect_v3/review.py:summarize`, `docs/records/harvest/collect_v3/c1/c1_agg.py` | pools per source×class | byte-copied crop, no zoom (readers zoom with `magick -resize 300%`) | **none** | `Random(f"{seed}:{phase}:{tranche}:{source}:{cls}…")`, n=100 | sibling `<name>_key.json` | `c1/LABEL_CHECK_v2.md` (+ v1 `blind_checks_v1/*.md`) | `{card_id,letters:y/n/u,marks:y/n/na,crop_ok:y/n,errors[],detail}`; one reader per card | **two gates that disagree**: review.py pass if n≥40 & letters≥.9 & crop≥.9 (point estimates); c1_agg pass if **n==100** & ≥90 with a strict lunate adjustment; Wilson z 1.959963… vs 1.96 |
| S | COL `c1/yer_adjudication/{INK,PRIOR}.md` | Russian ъ/ь | `magick -resize 400%`, ⟦n⟧ slots | none | – | `key.json` in the same folder | INK.md / PRIOR.md | ink `{item_id,slots{n:ъ/ь/other/u},confidence,…}`; prior `{…prior,word,likelier,why}` | builder not in code |
| T | `greekocr/harvest/page_reads.py:build_blind_review(seed=15)` | engine reads | straight crop, no zoom | – | `Random(15)`, A/B per engine | key returned separately -> `blind_key.json` | page text | A/B/Same/Neither + notes, export button | – |
| U | SP reader zoom helpers (`crop.py`, `r2tools/zoom.*`, `b1tools/z.*`, `r0b_b4zoom/z.py`, `wl/zoom.py`, `wl/z3/zoom.*`, `mkcomp_b1r2.py`) | – | int/float factors; LANCZOS, magick or sips | – | – | – | – | – | contradicts the "magick only, no sips/Pillow" rule in LABEL_CHECK_v2/INK.md (that rule is C1/yer-only) |

### 2.2 Duplication matrix (X = implements, c = copy or re-implementation, i = imports, – = absent)

| Capability | deck | sheet | r0_prepare | r0_ia | r0_ib | r0_score | r0_wholeline | print_truth | implicit_prep | s8_prepare | s8_score_truth | l1a2 | owner sheets (O) | SP pages (P) | collect_v3 | page_reads |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crop / zoom | X | X | X | i | c | – | – | X | c | c | – | X | X | c + X | X | X |
| blind items + private key | – | – | X | i | c | – | ? (leaky img path) | X (same dir) | X (same dir) | X | – | X (+leak scan) | – | – | X | X |
| controls insertion | X (real) | – | X | i | c | – | – | X | X | X | – | X | – | – | – | – |
| option shuffle / seed | – | – | X | i | c | – | ? | X | X | X | – | X | – | – | sample only | X |
| HTML / deck render | X | X | X | i | c | X | – | – | – | X (static) | – | c | X | c | – | X |
| reader instructions | X | – | X | i | c | – | – | – | – | X | – | X | intro | intro | md | text |
| answer schema / parse | X | – | template | i | template | X | X | X | ? | template | X | template | db | db | X | X |
| controls gate | report | – | ≥8% | assert | assert | X all-correct | – | count | – | ≥8% | X 82/84 | ≥8% | – | – | – | – |
| second reader reverse | – | – | – | – | – | – | ? | files only | ? | – | SP r2*.py only | files only | – | – | – | – |
| tie-break | – | – | – | – | – | consumes | X | file unused | – | – | X | deck, scorer missing | – | – | – | – |
| Wilson / bootstrap / LB95 | X JS | – | – | – | – | – | – | – | – | – | X | – | – | – | X ×2 | – |
| truth writer | – | – | template | i | c | – | X | X | – | – | X | missing | – | – | X | – |
| owner notes db | localStorage + server | – | localStorage | i | localStorage | localStorage | – | – | – | – | – | – | `window.claude` db | `window.claude` db | – | export |

Statistical duplicates:
- LB95 is implemented twice, once in JS (deck) and once in Python (`validate.lb95`).
- Wilson is implemented three times: `s8_score_truth.wilson`, `collect_v3/cards.wilson_lower` and `c1_agg.wilson`.
- The bootstrap is implemented twice: `s8_score_truth`, and again in `s8b_measure.py:140`.
- The 0.6·h / ≤3× crop appears four times: r0_prepare, r0_freeze_ib, implicit_prep and s8_prepare.

### 2.3 Differences that matter

1. **Crop.** The padding and zoom rules differ by builder:

   | Builder | Padding | Zoom |
   |---|---|---|
   | R0, S8, implicit | 0.6·h | ≤3×, 900 px cap |
   | L1A2 | 0.4·h | 1200 px cap |
   | print_truth | – | word ≤4×, vowel ≤8× |
   | build_r1a_errors | – | letter 8× NEAREST |
   | sheet | xh | 3× NEAREST |
   | deck | – | browser 2–4× |
   | C1 | none | none (readers zoom 300% in magick) |

2. **Planted controls.** Six different rules are in use:

   | Builder | Planting rule |
   |---|---|
   | R0a | letter swap |
   | R0 ib | letter swap + mark map |
   | S8 | swap / delete alternating |
   | L1A2 | delete last mark |
   | print_truth | SWAP map |
   | implicit | remove / swap, appended unshuffled, so position reveals the control |
   | C1, yer, wl | none |

3. **"Other" option** spelling: `other` / `NEITHER` / `neither` / `none of these` + `unreadable`.
4. **Note field**: `note` vs `reason`.
5. **Confidence**: a string, but numeric in the R0 tiebreak.
6. **Template fields vs reader fields**: the R0 truth template uses `choice`/`transcription`, while readers wrote `answer`/`printed`. The merge code is not in any repo.
7. **Key custody**: write-once in R0 (tagged) and ib; overwritable in S8 and L1A2; same directory as the blind items in print_truth, implicit and yer; a leaky image path in wl.
8. **Control gates**: R0 requires all controls correct on bare letters; S8 requires exactly 82/84 per reader; print_truth only counts; C1 has no controls at all.
9. **Tiebreak option order**: R0 keeps the original order; S8 and audit100 re-randomise and decode against `items_tb.json`.
10. **Reverse-order second reader** exists only in the answer files and in SP writer scripts. No builder emits a reversed deck.
11. **C1 gate**: two implementations with different n and threshold rules (review.py vs c1_agg.py).
12. **Steps with no code in any repo**:
    - the R0 merge and tiebreak;
    - the S8 cut and tiebreak decks;
    - `audit100_final.json`;
    - the wl deck;
    - the yer items;
    - the SP owner pages and audit pages.

    These are not reproducible from the repos.

### 2.4 Proposal: one card builder, one reader protocol, one owner-sheet renderer

Package `greekocr.adjudicate`, built **from** C (r0_prepare, the most audited path: write-once key, audit hook, schema assert) and N
(l1a2 leak scan), and replacing the copies.

**(a) Card builder:** `build_deck(spec) -> DeckReceipt`

- `spec` (JSON, hashed into the receipt):
  - `items[]`: `{source_ref, image, region|span, options[] or free_text}`;
  - `crop`: `{pad_h: 0.6, max_zoom: 3, max_width: 900, resample: 'lanczos', line_image: true}` (profiles `letter`, `word`, `mark`, `line`, `page`; the l1a2/print_truth/r1a values become named profiles, not code);
  - `controls`: `{fraction: .08, planting: 'letter'|'mark_swap'|'mark_delete'|'swap_map', source: verified_pool}`;
  - `seed` (string);
  - `other_options: ['none of these','unreadable']`.
- Outputs:
  - `blind/` with `items_blind.json` `{id,img,line_img,options{A..},other_options}`, index.html, README, and opaque image names: **content-hash names, never source paths**;
  - `private/` (a sibling tree, outside `blind/`) with `items_key.json` written **O_EXCL** and holding `expected_choice`, `is_control`, `crop_box`, `zoom`, `source_ref`;
  - `receipt.json` with the spec sha, code sha, counts, and the sha of every image and json.
- Built-in invariants (from D and N):
  - blind keys are a whitelisted set;
  - no source path or id strings appear in blind/;
  - the control fraction holds;
  - zoom ≤ the cap;
  - controls are **shuffled into position**.

**(b) Reader protocol:** `greekocr.adjudicate.protocol`

- One instructions template, with the zoom tool fixed to one implementation (magick `-resize`, as LABEL_CHECK_v2 rules; or the builder pre-renders the zoom so readers use no tools).
- One answer schema, `{id, answer: option letter | 'none of these' | 'unreadable', printed, confidence: 'high'|'medium'|'low', note}`.
- `deal(deck, reader=1|2)` returns the reader's order: reader 2 = **reverse order**, emitted by code.
- `tiebreak_deck(disagreements)` re-randomises options under a new seed and keeps its own key, as S8 does.
- `resolve()` takes agreement of the two readers, else majority of 3, else UNKNOWN. Controls are decoded and gated **before** resolution: each reader passes the control threshold set in the spec (all correct, or k/n), with no shared misses.
- `score()`:
  - Wilson (z=1.959963984540054) for simple proportions;
  - document-cluster bootstrap (from `s8_score_truth`) for weighted estimates;
  - LB95 (Clopper-Pearson) where today's deck uses it. One Python implementation each; the deck JS reads the computed numbers.
- Truth writer: `truth.jsonl.gz` with per-item `{id, r1, r2, r3?, status, verdict, control}` + summary.
  - This replaces `print_truth/reconcile.py`, the missing R0 merge, `r0_wholeline_score.py` and the S8 truth writer.
  - The C1 single-reader checks become `readers=1` with the spec's gate. That puts the review.py and c1_agg.py gates into one function.

**(c) Owner-sheet renderer:** `greekocr.adjudicate.owner_sheet.render(lines, spec) -> html`

- Owner template, per line:
  - full line with detections (green above, blue below, grey attached, slot numbers);
  - Google and Ours rows;
  - tags;
  - **one** autosaving note per line in the artifact db (`window.claude` db, collection `notes`, doc `{line_id}`, merge, 900 ms debounce + blur flush);
  - optional `Printed` field (stored with `printed_edited`);
  - optional per-slot notes (doc `{line_id}:s{slot}`, from build_r1a_errors);
  - hover magnifier (Z=3, 300×130, clean crop, tap toggle).
- CSS and JS live as real files in the package (`owner_sheet.css`, `owner_sheet.js`), **not** extracted by `src.split` from other scripts.
- Inputs are a normalised line record `{line_id, crop, google, ours, detections, tags, highlights}`, so S4, S6, R1 and audit pages differ only in data.

**Replacements:**

| Existing | Replaced by |
|---|---|
| deck.py (+deck_serve, ingest_decisions, pull_firefox) | build_deck profile `word` + `protocol.score(lb95)`. **Key moves out of `deck_data.js`**, so the owner deck becomes blind for the first time; flag that this changes the protocol |
| sheet.py render/spellcheck_zoom | owner_sheet (read-only mode); `load_alignments`/`crop_key` move to `greekocr.recogniser.cache` |
| r0_prepare build_cards / r0_freeze_ia / r0_freeze_ib cards | build_deck profiles `letter`, `letter+mark`; R0 scripts keep only selection |
| R0 merge + tiebreak (SP mk*.py) | protocol.resolve + tiebreak_deck |
| r0_score / r0_wholeline_score | protocol.score (+ the stratum estimator as a scorer plug-in) |
| print_truth build/reconcile | build_deck profile `mark` (composite = line + word + vowel) + protocol |
| owner_implicit_adjudication_prep | build_deck (fixes the unshuffled controls and the shared key dir) |
| s8_prepare cards, l1a2_cards, s8_score_truth | build_deck profiles + protocol; s8_score_truth's bootstrap becomes `protocol.score.cluster_bootstrap`; s8b_measure imports it |
| collect_v3 cards/review, c1_agg | build_deck profile `line` (no controls; **adding controls is a protocol change**) + protocol.score(wilson, gate spec) |
| yer INK/PRIOR | build_deck with free-slot answers (`slots{}`) |
| sheet_build, owner_pages_build*, SP snap4/snap6/build_owner*, build_audit_template, build_subst_page, build_r1a_errors, build_audit_page, memo/*_sheet | owner_sheet.render |
| page_reads.build_blind_review | build_deck profile `page` with A/B options |
| SP zoom helpers | one `greekocr.adjudicate.zoom` CLI (or pre-rendered zooms) |
| m2_review, r0_finish review_page | owner_sheet (read-only) |

---

## Part 3: migration order

1. **Freeze evidence first.**
   - Commit the SP builders (`snap6/build_owner.py`, `build_audit_template.py`, `build_subst_page.py`, `build_r1a_errors.py`, `mk*.py`, `r2*.py`, `wl/*`, `subst_sample.py`) into the repo as historical scripts under `docs/.../provenance/`.
   - Record which output each one produced. Today they exist only in a temporary scratchpad.
2. **`greekocr.recogniser` phase 1 (wrapper, zero byte change to pinned files).**
   - Add the package importing from `ctc_align`.
   - Add the golden tests: `to_record`/`recognition_evidence`/`alignment_sha256` on frozen caches, and a CPU re-forward parity check on 200 crops.
   - Add the `confidence_matches` predicate, the `AlignmentCache`, one `crop_key` and `forbid_forward`.
3. **Move unpinned callers** to the API:
   - validate/sample/sheet;
   - the owner pages;
   - the memo and print_truth scripts;
   - s2/s3/sf2;
   - `readers/ours.py` (profile `eval`) with an E1Reader bit-parity test;
   - `glyphs/orientation.py` (profile `serve`).
4. **`greekocr.adjudicate`.**
   - First: `owner_sheet` (most builders, all unblinded, so low risk).
   - Then `build_deck` + `protocol` with the R0 path as the reference implementation. Re-emit one past deck (R0 ib) from its spec and diff it against the frozen blind files.
   - Then S8/L1A2, print_truth, implicit, and C1.
5. **Recogniser phase 2 (invert the shim)** only at the next release-gate re-certification:
   - new `POLICY` schema;
   - `policy_binding()` lists the package files;
   - new deploy manifests;
   - pinned scripts (c1_run, l1f_run, r1_extract/r1_common, m2_run, l1_*) switch to `recogniser.batch.run_shard`/`transfer`.
6. **Optional, separate validation round:** a Viterbi `force_align` (from greek-page-ocr `o4b_align.forced`) to replace nearest-neighbour transfer, and bf16-vs-fp32 alignment of the recorded E3 predictions.

## Part 4: hazards

- **Gate digest:**
  - `release_gate.policy_binding()` hashes `ctc_align.py`, `segmentation.py`, `text.py`, `m2_run.py`, `owner_reading.py`, `owner_pages_build_combined.py` and 8 `clariden/*` scripts. Touching any byte silently changes the policy sha.
  - L1R4b requires ctc_align `3ecb1a20` and release_gate `9ef1d646`, byte-identical.
- **Deploy manifests:**
  - C1/R1/L1E pin the **old** ctc_align `1a753b30`; L1F/L1R3/L1R4 pin `3ecb1a20`.
  - Any refactor before the in-flight L1R4 job 2 completes will break the remote sha check.
  - Per memory, never edit files that are bound by hash or pasted into briefs while a pass is in flight.
- **Evidence identity:** `alignment_sha256` is the sha of `json.dumps(to_record(), sort_keys=True)`. Changing span rounding, key names or the frame list type breaks the verification of every saved L1F/L1R row.
- **float32 vs float64:** keep the line confidence as a float32 mean, and give every consumer one shared predicate. The open L1R4b fix (2e-7 -> 1e-6) is still unapplied in `l1r4_join.py` at ed5037ae.
- **Device / precision:** C1 and L1F ran on CUDA fp32, R0 and M2 on CPU fp32, and the E3 recorded predictions likely came from bf16 CUDA. A "unified" API must record device and dtype in its provenance, and must not claim cross-device bit-identity.
- **Preprocessing parity:** the bg medians differ between E1Reader (averaged float median then rint) and ctc_align (upper median), and serving differs again (float halo, no quantisation). Choosing one silently would change outputs. Keep them as named profiles until a parity measurement decides.
- **Blinding changes are protocol changes:**
  - moving deck.py's key out of the page;
  - shuffling implicit_prep's controls;
  - adding controls to C1;
  - removing the path leak in wl.

  Results from the old decks stay valid only under their old protocol; label them.
- **Missing builders:** R0 merge, S8 cut/tiebreak, audit100 final, wl, yer and all SP pages. Their outputs cannot be regenerated from code. Commit the scripts (step 1) before cleanup deletes the scratchpad.
- **Unclear:**
  - whether the `l['model']` texts passed to `transfer_alignment` without `nfd` are always NFD;
  - how the print_truth tiebreak was applied;
  - whether `c1_agg.py` runs from its committed location;
  - whether CPU batch size (8 vs 16) changes float outputs.
