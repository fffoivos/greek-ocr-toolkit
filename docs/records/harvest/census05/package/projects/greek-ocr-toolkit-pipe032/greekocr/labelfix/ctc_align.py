"""Recogniser forward pass with CTC frame alignment -> per-character x ranges in crop pixels.

The crop is turned into the 48-row strip exactly as the factory's `import_real` does
(Lanczos resize to height 48, width = round(w*48/h), min canvas width 64, background =
median of the last two columns; see greek-page-ocr factory/src/import_real.rs::strip).
PIL's Lanczos is not byte-identical to the Rust `image` crate's, but the smoke test on a
wikisource crop reproduced the recorded prediction exactly.

Frame -> x: frame t covers strip columns [4t, 4t+4) (STRIDE = 4); a character emitted at
frames [t0, t1) is placed between the midpoints to its neighbours' spikes, then scaled
back to crop pixels by h_crop / 48.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import time

import numpy as np
from PIL import Image

VENDOR_CODEC = Path(__file__).resolve().parents[1] / '_vendor' / 'codec' / 'v1.json'
STRIP_HEIGHT = 48
STRIDE = 4
MAX_WIDTH = 2560
MIN_WIDTH = 64


def recognition_fields(runtime):
    """Carry saved score provenance through runtime copies, without upgrading it."""
    from copy import deepcopy
    fields = dict(recognition_confidence=runtime.get('recognition_confidence'),
        recognition_evidence=deepcopy(runtime.get('recognition_evidence') or dict(
            schema='ctc-window-score-v1', scored=False, scope='line', regions=[],
            provenance='legacy_runtime_without_score_provenance' if runtime.get('recognition_confidence') is not None
                       else 'missing_runtime_confidence')))
    if 'image_width' in runtime:fields['image_width']=runtime['image_width']
    return fields


def make_strip(image: Image.Image) -> tuple[np.ndarray, float]:
    """Factory strip replica. Returns (uint8 [48, W] array, crop pixels per strip pixel)."""
    im = image.convert('L')
    w, h = im.size
    if w <= 0 or h <= 0:
        raise ValueError('empty crop')
    nw = max(1, int(round(w * 48.0 / h)))
    nh = 48
    if nw > MAX_WIDTH:
        nh = int(round(h * MAX_WIDTH / w))
        if nh < 14:
            raise ValueError('strip_below_14px_floor')
        nw = MAX_WIDTH
    resized = np.asarray(im.resize((nw, nh), Image.LANCZOS), dtype=np.uint8)
    tail = np.sort(resized[:, max(nw - 2, 0):].ravel())
    bg = int(tail[len(tail) // 2])
    canvas = np.full((STRIP_HEIGHT, max(nw, MIN_WIDTH)), bg, np.uint8)
    y0 = (STRIP_HEIGHT - nh) // 2
    canvas[y0:y0 + nh, :nw] = resized
    return canvas, w / nw


@dataclass
class CharSpan:
    char: str          # NFD codepoint (atom)
    index: int         # position in the decoded prediction string
    frame0: int        # first spike frame
    frame1: int        # last spike frame + 1
    x0: float          # crop-pixel x range assigned to this character
    x1: float


@dataclass
class Alignment:
    prediction: str
    spans: list = field(default_factory=list)   # CharSpan per decoded codepoint
    n_frames: int = 0
    scale: float = 1.0                          # crop px per strip px
    strip_width: int = 0
    confidence: float | None = None
    frame_confidences: list | None = None       # max posterior, including blank, per valid frame

    def span(self, i: int) -> CharSpan:
        return self.spans[i]

    def window(self, i0: int, i1: int) -> tuple[float, float]:
        """Crop x range covering prediction indices [i0, i1)."""
        s = self.spans[i0:i1]
        return (min(c.x0 for c in s), max(c.x1 for c in s)) if s else (0.0, 0.0)

    def char_width(self) -> float:
        base = [c.x1 - c.x0 for c in self.spans if not _is_mark(c.char) and c.char != ' ']
        return float(np.median(base)) if base else 0.0

    def to_record(self) -> dict:
        record = dict(prediction=self.prediction, n_frames=self.n_frames, scale=self.scale, strip_width=self.strip_width,
                    confidence=self.confidence,
                    spans=[[c.char, c.frame0, c.frame1, round(c.x0, 1), round(c.x1, 1)] for c in self.spans])
        if self.frame_confidences is not None:
            record['frame_confidences'] = list(self.frame_confidences)
            import hashlib
            record['frame_prediction_sha256'] = hashlib.sha256(self.prediction.encode()).hexdigest()
        if getattr(self, 'transferred', False):record['transferred'] = True
        return record

    @classmethod
    def from_record(cls, r: dict) -> 'Alignment':
        a = cls(r['prediction'], [], r['n_frames'], r['scale'], r['strip_width'], r.get('confidence'),
                r.get('frame_confidences'))
        a.spans = [CharSpan(ch, i, f0, f1, x0, x1) for i, (ch, f0, f1, x0, x1) in enumerate(r['spans'])]
        import hashlib
        if (r.get('transferred') or a.frame_confidences is not None
                and r.get('frame_prediction_sha256') != hashlib.sha256(a.prediction.encode()).hexdigest()):
            a.transferred = True
        return a

    def recognition_evidence(self, slots, image_width):
        """Bind actual scored frames to each detector window; never fill legacy gaps.

        A line mean (which includes blanks) cannot certify an omitted region.
        Regional confidence is the minimum max-posterior of ALL overlapping
        frames. This is model observation, not calibrated independent truth.
        Transferred locations do not establish original frame ownership.
        """
        import hashlib
        import json
        import math
        from .text import nfd
        evidence = dict(schema='ctc-window-score-v1', scored=self.confidence is not None,
            provenance='saved_alignment_confidence' if self.confidence is not None else 'missing_alignment_confidence',
            scope='line', regions=[],
            alignment_sha256=hashlib.sha256(json.dumps(self.to_record(),sort_keys=True).encode()).hexdigest(),
            text_sha256=hashlib.sha256(nfd(self.prediction).encode()).hexdigest())
        scores = self.frame_confidences
        if (getattr(self, 'transferred', False) or scores is None or len(scores) != self.n_frames
                or not self.scale > 0 or not math.isfinite(self.scale)
                or not all(isinstance(x, (int, float)) and not isinstance(x, bool)
                           and math.isfinite(x) and 0 <= x <= 1 for x in scores)):
            return evidence
        for slot in slots:
            ev = slot.get('evidence', {})
            ev = ev.to_record() if hasattr(ev, 'to_record') else ev
            window = ev.get('window')
            if not (isinstance(window, (list, tuple)) and len(window) == 2
                    and all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in window)
                    and 0 <= window[0] < window[1] <= image_width):
                continue
            lo, hi = math.floor(window[0] / (STRIDE*self.scale)), math.ceil(window[1] / (STRIDE*self.scale))
            if not 0 <= lo < hi <= len(scores):continue
            evidence['regions'].append(dict(start=slot['start'], base=slot['base'], window=list(window),
                image_width=image_width, scored=True, confidence=min(scores[lo:hi]),
                frames=[lo, hi], provenance='minimum_max_frame_posterior_including_blank'))
        return evidence


def _is_mark(c: str) -> bool:
    import unicodedata
    return unicodedata.combining(c) != 0


def frames_to_spans(ids: np.ndarray, decode_atom, scale: float) -> list[CharSpan]:
    """Greedy CTC path -> spikes -> spans. `ids` are argmax ids for the valid frames."""
    spikes = []   # (id, t0, t1)
    prev = 0
    t0 = 0
    for t, v in enumerate(list(ids) + [0]):
        v = int(v)
        if v != prev:
            if prev != 0:
                spikes.append((prev, t0, t))
            prev, t0 = v, t
    spans: list[CharSpan] = []
    n = len(spikes)
    for k, (v, a, b) in enumerate(spikes):
        left = (spikes[k - 1][2] + a) / 2 if k else max(0.0, a - 1.0)
        right = (b + spikes[k + 1][1]) / 2 if k + 1 < n else b + 1.0
        spans.append(CharSpan(decode_atom(v), k, a, b, left * STRIDE * scale, right * STRIDE * scale))
    return spans


def transfer_alignment(text: str, al: Alignment) -> Alignment:
    """Spans for `text` (e.g. a recorded prediction) borrowed from an alignment of a near-identical
    reading: matched characters keep their span, unmatched ones take the nearest matched
    neighbour's. Used when the re-run prediction differs slightly from the recorded one."""
    from .candidates import align_chars
    if text == al.prediction:
        return al
    path = align_chars(text, al.prediction)
    owner = [None] * len(text)
    for i, j in path:
        if i is not None and j is not None:
            owner[i] = j
    last = None
    for i in range(len(text)):
        if owner[i] is None:
            owner[i] = last
        else:
            last = owner[i]
    nxt = None
    for i in range(len(text) - 1, -1, -1):
        if owner[i] is None:
            owner[i] = nxt
        else:
            nxt = owner[i]
    spans = []
    for i, ch in enumerate(text):
        src = al.spans[owner[i]] if owner[i] is not None and al.spans else None
        spans.append(CharSpan(ch, i, src.frame0 if src else 0, src.frame1 if src else 0,
                              src.x0 if src else 0.0, src.x1 if src else 0.0))
    out = Alignment(text, spans, al.n_frames, al.scale, al.strip_width, al.confidence)
    out.transferred = True
    return out


class Recognizer:
    """Loads a greek-page-ocr checkpoint through the vendored training stack (safe loader)."""

    def __init__(self, ckpt_path: str | Path, codec_path: str | Path = VENDOR_CODEC, device: str = 'cpu',
                 threads: int | None = None):
        import torch
        from greekocr._vendor.train import ckpt_io
        from greekocr._vendor.train.cer import load_codec
        from greekocr._vendor.train.model import build_model
        if threads:
            torch.set_num_threads(threads)
        self.torch = torch
        self.codec = load_codec(str(codec_path))
        sd, meta = ckpt_io.load_model_weights(str(ckpt_path))
        if meta.get('codec_version') != self.codec.version:
            raise ValueError(f'checkpoint codec {meta.get("codec_version")!r} != {self.codec.version!r}')
        if int(meta.get('n_classes', -1)) != self.codec.n_classes:
            raise ValueError('checkpoint n_classes mismatch')
        self.meta = meta
        self.device = torch.device(device)
        self.model, _ = build_model(n_classes=self.codec.n_classes, arch=meta.get('arch', 'compact'), verbose=False)
        self.model.load_state_dict(sd)
        self.model.to(self.device).eval()
        self.ckpt_path = str(ckpt_path)

    def _decode_atom(self, v: int) -> str:
        return self.codec.atom_by_id[v]

    def align_batch(self, images: list[Image.Image]) -> list[Alignment]:
        torch = self.torch
        from greekocr._vendor.train.model import DET_PAD_MARGIN, masked_forward
        strips, scales = zip(*(make_strip(im) for im in images))
        widths = [s.shape[1] for s in strips]
        canvas_w = max(widths) + DET_PAD_MARGIN
        canvas = np.empty((len(strips), STRIP_HEIGHT, canvas_w), np.uint8)
        for i, s in enumerate(strips):
            w = s.shape[1]
            canvas[i, :, :w] = s
            canvas[i, :, w:] = int(round(float(np.median(s[:, -2:]))))
        x = torch.from_numpy(((canvas.astype(np.float32) / 255.0) - 0.5) / 0.5).unsqueeze(1).to(self.device)
        lengths = torch.tensor([-(-w // STRIDE) for w in widths])
        with torch.no_grad():
            out = masked_forward(self.model, x, lengths)
        lp = out.float().cpu()
        am = lp.argmax(-1).numpy()
        probs = lp.exp().max(-1).values.numpy()
        results = []
        for i in range(len(strips)):
            L = int(lengths[i])
            ids = am[i, :L]
            spans = frames_to_spans(ids, self._decode_atom, scales[i])
            pred = ''.join(c.char for c in spans)
            results.append(Alignment(pred, spans, L, scales[i], widths[i], float(probs[i, :L].mean()),
                                     probs[i, :L].tolist()))
        return results

    def align_paths(self, paths: list[str | Path], bs: int = 16, log=None) -> dict:
        """Width-sorted batches; returns {path: Alignment}. Crops that fail to open are skipped."""
        opened = []
        for p in paths:
            try:
                im = Image.open(p)
                im.load()
                opened.append((str(p), im))
            except (OSError, ValueError):
                continue
        opened.sort(key=lambda t: t[1].size[0] / max(1, t[1].size[1]))
        out = {}
        t0 = time.time()
        for k in range(0, len(opened), bs):
            batch = opened[k:k + bs]
            for (p, _), al in zip(batch, self.align_batch([im for _, im in batch])):
                out[p] = al
            if log and (k // bs) % 20 == 0:
                log(f'[align] {min(k + bs, len(opened))}/{len(opened)} ({time.time() - t0:.0f}s)')
        return out
