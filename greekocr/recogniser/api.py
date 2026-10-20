"""Named profiles delegate preprocessing, loading, forward and decoding to old stacks."""
from __future__ import annotations
from collections.abc import Iterable

from dataclasses import dataclass
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import numpy as np
from PIL import Image
from greekocr.labelfix import ctc_align as ctc
from .alignment import Alignment, wrap
from numpy.typing import DTypeLike, NDArray

__all__ = ['Reading', 'Recogniser', 'load']


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def binding_errors(meta, codec, codec_path):
    errors = []
    if meta.get('codec_version') != codec.version:
        errors.append('codec_version mismatch or missing')
    if meta.get('codec_sha256') != sha256(codec_path):
        errors.append('codec_sha256 mismatch or missing')
    try:
        classes_match = int(meta.get('n_classes', -1)) == codec.n_classes
    except (ValueError, TypeError):
        classes_match = False
    if not classes_match:
        errors.append('n_classes mismatch or missing')
    if meta.get('head', 'nfd') != 'nfd':
        errors.append('head must be nfd')
    return errors


@dataclass
class Reading:
    text: str
    profile: str
    provenance: dict
    alignment: object = None
    confidence: float | None = None
    frames: list | None = None
    ids: object = None  # old public methods do not expose argmax IDs
    scale: float | None = None
    strip_width: int | None = None


class Recogniser:
    def __init__(self, checkpoint: str | Path, codec: str | Path | None = None,
                 device: str = 'cpu', threads: int | None = None, *, strict: bool = True) -> None:
        import torch
        from greekocr._vendor.train.ckpt_io import load_model_weights
        from greekocr._vendor.train.cer import load_codec
        if threads is not None:
            if threads < 1:
                raise ValueError('threads must be positive')
            torch.set_num_threads(threads)
        self.checkpoint = Path(checkpoint)
        self.codec_path = Path(codec or ctc.VENDOR_CODEC)
        self.device = str(device)
        self.strict = strict
        weights, meta = load_model_weights(str(checkpoint))
        del weights
        self.binding_errors = binding_errors(meta, load_codec(str(self.codec_path)), self.codec_path)
        if strict and self.binding_errors:
            raise ValueError('; '.join(self.binding_errors) + '; strict=False retains each legacy profile checks')
        sibling = self.checkpoint.with_suffix('.safetensors')
        safe = self.checkpoint if self.checkpoint.suffix == '.safetensors' else sibling
        package = Path(__file__).parent
        sources = {p.name: sha256(p) for p in sorted(package.glob('*.py'))}
        import json
        self.provenance = dict(checkpoint_sha256=sha256(self.checkpoint) if self.checkpoint.is_file() else None,
            safetensors_sha256=sha256(safe) if safe.is_file() else None,
            codec_sha256=sha256(self.codec_path), code_sha256=hashlib.sha256(
                json.dumps(sources, sort_keys=True).encode()).hexdigest(), code_sources=sources,
            implementation_sources={str(p): sha256(p) for p in (
                Path(ctc.__file__), Path(__file__).parents[1]/'_vendor/bench/e2_reader_parity.py',
                Path(__file__).parents[1]/'deploy/docling_plugin/recognizer/inference.py')},
            device=self.device, dtype='float32', torch=torch.__version__,
            strict=strict, binding_errors=list(self.binding_errors))
        self._backends = {}

    def _backend(self, profile):
        if profile not in ('labelfix', 'eval', 'serve'):
            raise ValueError(f'unknown profile: {profile}')
        if profile not in self._backends:
            args = (str(self.checkpoint), str(self.codec_path), self.device)
            if profile == 'labelfix':
                backend = ctc.Recognizer(*args)
            elif profile == 'eval':
                from greekocr._vendor.bench.e2_reader_parity import E1Reader
                backend = E1Reader(*args)
            else:
                from greekocr.deploy.docling_plugin.recognizer.inference import Recognizer
                backend = Recognizer(*args)
            self._backends[profile] = backend
        return self._backends[profile]

    def read(self, images: Iterable[str | Path | Image.Image | NDArray], *,
             profile: str = 'labelfix', bs: int = 16) -> list[Reading]:
        if bs < 1:
            raise ValueError('bs must be positive')
        backend = self._backend(profile)
        images = list(images)
        if not images:
            return []
        with tempfile.TemporaryDirectory(prefix='recogniser-') as temp:
            opened, paths = [], []
            for i, item in enumerate(images):
                try:
                    if isinstance(item, (str, Path)):
                        with Image.open(item) as im:
                            im.load()
                            opened.append(im.copy())
                        paths.append(str(item))
                    elif isinstance(item, Image.Image):
                        item.load()
                        opened.append(item)
                        path = Path(temp)/f'{i}.png'
                        if profile == 'eval':
                            item.save(path)
                        paths.append(str(path))
                    elif profile == 'serve' and isinstance(item, np.ndarray):
                        opened.append(item)
                        paths.append(None)
                    else:
                        raise TypeError('expected path or PIL image (serve also accepts prepared float32 strips)')
                except (OSError, ValueError, TypeError) as error:
                    raise ValueError(f'unreadable input at index {i}: {item!r}: {error}') from error
            provenance = dict(self.provenance, profile=profile)
            if profile == 'labelfix':
                result = []
                for k in range(0, len(opened), bs):
                    for al in backend.align_batch(opened[k:k+bs]):
                        al = wrap(al)
                        result.append(Reading(al.prediction, profile, provenance, al, al.confidence,
                                              al.frame_confidences, None, al.scale, al.strip_width))
                return result
            if profile == 'eval':
                return [Reading(backend.read(p), profile, provenance) for p in paths]
            from greekocr.deploy.docling_plugin.recognizer.strips import extract_strip
            strips = []
            for i, im in enumerate(opened):
                if isinstance(im, np.ndarray):
                    s = im
                    if s.dtype != np.float32 or s.ndim != 2 or s.shape[0] != 48 or not 64 <= s.shape[1] <= 2560 or not np.isfinite(s).all() or s.min() < 0 or s.max() > 1:
                        raise ValueError(f'invalid serve strip at index {i}')
                else:
                    page = np.asarray(im.convert('L'), dtype=np.float32)/255
                    s = extract_strip(page, (0, 0, im.width, im.height))
                    if s is None:
                        raise ValueError(f'unreadable serve crop at index {i}')
                strips.append(s)
            return [Reading(text, profile, provenance, confidence=confidence)
                    for text, confidence in backend.recognize(strips, bs=bs)]

    def logits(self, images: Iterable[str | Path | Image.Image], *,
               dtype: DTypeLike = np.float32) -> list[NDArray]:
        """Delegate E1.logits (float halo, distinct from E1Reader.read)."""
        backend = self._backend('eval')
        output = []
        for i, item in enumerate(images):
            try:
                if isinstance(item, Image.Image):
                    output.append(backend.logits(item).astype(dtype))
                else:
                    with Image.open(item) as im:
                        output.append(backend.logits(im).astype(dtype))
            except (OSError, ValueError, TypeError) as error:
                raise ValueError(f'unreadable input at index {i}: {error}') from error
        return output

    def as_reader(self, *, profile: str = 'eval') -> SimpleNamespace:
        self._backend(profile)
        return SimpleNamespace(read=lambda path: self.read([path], profile=profile)[0].text,
                               binding=dict(self.provenance, profile=profile))


def load(checkpoint: str | Path, codec: str | Path | None = None,
         device: str = 'cpu', threads: int | None = None, *, strict: bool = True) -> Recogniser:
    return Recogniser(checkpoint, codec, device, threads, strict=strict)
