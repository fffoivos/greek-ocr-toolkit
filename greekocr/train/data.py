"""Parquet strip dataset + width-bucket batching for the greek-page-ocr trainer.

Contracts (frozen): docs/data_contracts.md §2 (strip), §3 (shard schema), §4 (splits).

- Reads a directory of `shard-*.parquet`; uses the `image_png`, `width`, `label_ids`,
  `script_class`, `split` columns (plus `codec_version` for a defense-in-depth check).
  Text is NEVER re-encoded: training/scoring consume `label_ids` as stored.
- Split defense in depth: rows whose `split` differs from the directory's expected role are
  REFUSED (hard error, not filtered), and `split == "reserved"` is refused everywhere.
- Batching: bucket key = ceil(width/128)*128 (contract §2); indices are shuffled within
  buckets each epoch (seeded), cut into batches of similar widths, and the batch order is
  shuffled too. Each strip is padded RIGHT to the batch max width with its OWN background
  level (median of its last 2 pixel columns); input_lengths[i] = ceil(orig_width_i / 4).
- Pixel normalization matches the model input spec: px/255 then (x - 0.5) / 0.5.

Memory note: shard payloads (PNG bytes + label ids) are held in RAM — right-sized for the
pilot/P1 scale this stack targets (~1M rows ≈ a few GB). Revisit (doc 06 §6.6) before 5–20M runs.
"""

from __future__ import annotations

import glob
import io
import math
import os
from collections import Counter
from typing import Dict, Iterator, List, Optional, Sequence

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, Sampler

STRIP_HEIGHT = 48
WIDTH_MIN, WIDTH_MAX = 64, 2560  # contract §2
BUCKET_STEP = 128  # contract §2: width buckets are multiples of 128 px
STRIDE = 4  # T = ceil(W/4)

_COLUMNS = ["image_png", "width", "label_ids", "script_class", "split", "codec_version"]
_VALID_SPLITS = ("train", "val", "reserved")


def ceil_div(a: int, b: int) -> int:
    return -(-a // b)


class StripDataset(Dataset):
    """One row per strip, loaded from `<data_dir>/shard-*.parquet`.

    expected_split: "train" or "val" — the directory's role (rows must match), or None to
    accept train/val mixtures (e.g. a transfer-dev directory). "reserved" is refused UNLESS
    allow_reserved=True.

    allow_reserved: the sanctioned reserved-EVAL role. Default False refuses split='reserved' in
    every consumer (data_contracts §4: the never-trainable band must never reach a TRAIN/VAL loader).
    Set True ONLY for the transfer-dev / eval consumer (train.py --transfer-dev), which reads the
    reserved band as a held-out eval set and never backprops through it. This is what makes the
    pre-registered transfer-dev (reserved × held-out fonts) loadable (prereg_t1 §6a / review F1).
    """

    def __init__(
        self,
        data_dir: str,
        expected_split: Optional[str],
        expected_codec_version: Optional[str] = None,
        max_label_id: Optional[int] = None,
        max_rows: Optional[int] = None,
        allow_reserved: bool = False,
        keep_classes: Optional[set] = None,
    ) -> None:
        import pyarrow.parquet as pq

        # keep_classes: if set, keep ONLY rows whose script_class is in it (P1 --greek-only filter,
        # prereg_t1 §2: the head-arm pilot trains on the Greek slice greek_mono+greek_poly).
        self.keep_classes = keep_classes
        valid_expected = ("train", "val", "reserved") if allow_reserved else ("train", "val")
        if expected_split is not None and expected_split not in valid_expected:
            raise ValueError(
                f"expected_split must be one of {valid_expected} or None, got {expected_split!r}"
            )
        self.allow_reserved = allow_reserved
        self.data_dir = data_dir
        shard_paths = sorted(glob.glob(os.path.join(data_dir, "shard-*.parquet")))
        if not shard_paths:
            raise FileNotFoundError(f"no shard-*.parquet files in {data_dir}")

        images: List[bytes] = []
        widths: List[int] = []
        labels: List[np.ndarray] = []
        scripts: List[str] = []

        for path in shard_paths:
            tbl = pq.read_table(path, columns=_COLUMNS)

            splits = tbl.column("split").to_pylist()
            counts = Counter(splits)
            bad = [s for s in counts if s not in _VALID_SPLITS]
            if bad:
                raise ValueError(f"{path}: unknown split values {bad} (counts={dict(counts)})")
            if not self.allow_reserved and counts.get("reserved", 0) > 0:
                raise ValueError(
                    f"{path}: {counts['reserved']} rows have split='reserved' — the never-trainable "
                    f"band must not appear in any consumed directory (data_contracts §4). "
                    f"Only the transfer/eval consumer may pass allow_reserved=True."
                )
            if expected_split is not None:
                wrong = {s: c for s, c in counts.items() if s != expected_split}
                if wrong:
                    raise ValueError(
                        f"{path}: directory role is split='{expected_split}' but found {wrong} "
                        f"(defense in depth: refusing, not filtering)"
                    )

            if expected_codec_version is not None:
                vers = set(tbl.column("codec_version").to_pylist())
                if vers != {expected_codec_version}:
                    raise ValueError(
                        f"{path}: codec_version {sorted(vers)} != expected {expected_codec_version!r}"
                    )

            shard_widths = tbl.column("width").to_pylist()
            shard_labels = tbl.column("label_ids").to_pylist()
            shard_scripts = tbl.column("script_class").to_pylist()
            shard_images = tbl.column("image_png").to_pylist()

            for k in range(len(shard_widths)):
                if self.keep_classes is not None and shard_scripts[k] not in self.keep_classes:
                    continue  # P1 --greek-only: keep only the pre-registered class slice
                w = int(shard_widths[k])
                if not WIDTH_MIN <= w <= WIDTH_MAX:
                    raise ValueError(f"{path} row {k}: width {w} outside contract [{WIDTH_MIN},{WIDTH_MAX}]")
                ids = shard_labels[k]
                if not ids:
                    raise ValueError(f"{path} row {k}: empty label_ids")
                arr = np.asarray(ids, dtype=np.int64)
                if arr.min() < 1:
                    raise ValueError(f"{path} row {k}: label id {arr.min()} < 1 (blank=0 must not appear)")
                if max_label_id is not None and arr.max() > max_label_id:
                    raise ValueError(f"{path} row {k}: label id {arr.max()} > codec max {max_label_id}")
                images.append(shard_images[k])
                widths.append(w)
                labels.append(arr)
                scripts.append(shard_scripts[k])
                if max_rows is not None and len(images) >= max_rows:
                    break
            if max_rows is not None and len(images) >= max_rows:
                break

        if not images:
            raise ValueError(f"{data_dir}: zero usable rows")

        self.images = images
        self.widths = np.asarray(widths, dtype=np.int64)
        self.labels = labels
        self.scripts = scripts

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, i: int) -> Dict:
        img = Image.open(io.BytesIO(self.images[i]))
        if img.mode != "L":
            raise ValueError(f"row {i}: PNG mode {img.mode!r}, contract requires 8-bit grayscale 'L'")
        arr = np.asarray(img, dtype=np.uint8)
        if arr.shape != (STRIP_HEIGHT, int(self.widths[i])):
            raise ValueError(
                f"row {i}: decoded image {arr.shape} != contract (48, width={int(self.widths[i])})"
            )
        return {
            "image": arr,
            "width": int(self.widths[i]),
            "label": self.labels[i],
            "script_class": self.scripts[i],
        }


class WidthBucketBatchSampler(Sampler[List[int]]):
    """Groups indices by width bucket (ceil(w/128)*128), shuffles within buckets per epoch.

    Deterministic: rng is seeded from (seed, epoch). Call set_epoch(e) each epoch to reshuffle.
    shuffle=False gives a fixed bucket-then-width-sorted order (for val/eval passes).
    """

    def __init__(self, widths: Sequence[int], batch_size: int, seed: int = 0, shuffle: bool = True) -> None:
        widths = np.asarray(widths, dtype=np.int64)
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        self.batch_size = int(batch_size)
        self.seed = int(seed)
        self.shuffle = bool(shuffle)
        self._epoch = 0

        bucket_keys = (np.ceil(widths / BUCKET_STEP) * BUCKET_STEP).astype(np.int64)
        self.buckets: Dict[int, np.ndarray] = {}
        for key in np.unique(bucket_keys):
            idx = np.nonzero(bucket_keys == key)[0]
            # stable secondary order: by width, then index (deterministic for shuffle=False)
            order = np.lexsort((idx, widths[idx]))
            self.buckets[int(key)] = idx[order]
        self._n_batches = sum(ceil_div(len(v), self.batch_size) for v in self.buckets.values())

    def set_epoch(self, epoch: int) -> None:
        self._epoch = int(epoch)

    def __len__(self) -> int:
        return self._n_batches

    def __iter__(self) -> Iterator[List[int]]:
        batches: List[List[int]] = []
        rng = np.random.default_rng([self.seed, self._epoch]) if self.shuffle else None
        for key in sorted(self.buckets):
            idx = self.buckets[key]
            if rng is not None:
                idx = idx[rng.permutation(len(idx))]
            for s in range(0, len(idx), self.batch_size):
                batches.append([int(v) for v in idx[s : s + self.batch_size]])
        if rng is not None:
            batches = [batches[k] for k in rng.permutation(len(batches))]
        return iter(batches)


def _background_level(arr: np.ndarray) -> int:
    """Strip's own background estimate: median of its last 2 pixel columns (contract §2)."""
    tail = arr[:, -2:] if arr.shape[1] >= 2 else arr
    return int(round(float(np.median(tail))))


def collate_strips(samples: List[Dict]) -> Dict:
    """Pad right to (batch max width + DET_PAD_MARGIN) with each strip's OWN background; normalize;
    pack CTC targets. WP-A F1: EVERY strip (incl. the batch-widest) gets a >=128px own-background halo
    so its boundary conv frames see its own background, not the tensor edge / another strip's width ->
    a strip's reading (eval preds) is deterministic regardless of batch composition (matches
    pipeline/recognize.py). Applies to eval + future training; frozen S16 preds were produced without
    it (see the WP-A cert F6 masked-eval note)."""
    from greekocr.train.model import DET_PAD_MARGIN  # local import to avoid ordering issues; single source in model.py
    b = len(samples)
    canvas_w = max(s["width"] for s in samples) + DET_PAD_MARGIN
    canvas = np.empty((b, STRIP_HEIGHT, canvas_w), dtype=np.uint8)
    input_lengths = np.empty(b, dtype=np.int64)
    target_lengths = np.empty(b, dtype=np.int64)
    for i, s in enumerate(samples):
        arr = s["image"]
        w = s["width"]
        canvas[i, :, :w] = arr
        canvas[i, :, w:] = _background_level(arr)  # ALWAYS fill the remainder with this strip's own bg
        input_lengths[i] = ceil_div(w, STRIDE)  # pre-pad T (contract §2)
        target_lengths[i] = len(s["label"])

    x = canvas.astype(np.float32) / 255.0
    x = (x - 0.5) / 0.5  # model input spec
    images = torch.from_numpy(x).unsqueeze(1)  # [B, 1, 48, w_max]

    targets = torch.from_numpy(np.concatenate([s["label"] for s in samples]))  # 1D int64
    return {
        "images": images,
        "input_lengths": torch.from_numpy(input_lengths),
        "targets": targets,
        "target_lengths": torch.from_numpy(target_lengths),
        "labels": [s["label"] for s in samples],
        "script_class": [s["script_class"] for s in samples],
    }


def make_loader(
    dataset: StripDataset,
    batch_size: int,
    seed: int = 0,
    shuffle: bool = True,
    num_workers: int = 0,
    pin_memory: bool = False,
    pack_bucket_tails: bool = False,
):
    """DataLoader + its sampler (call sampler.set_epoch(e) each training epoch).

    REV H.1(3) loader speedup (WP-A F3): num_workers>0 + pin_memory + prefetch + persistent workers
    are OPT-IN (default 0 = the deterministic in-process path). Order is preserved (the batch_sampler
    fixes batch order; the DataLoader returns batches in sampler order regardless of worker count) and
    __getitem__ is RNG-free (strips are pre-rendered at build time), so workers do not perturb
    reproducibility — safe for the frozen-loader-order eval path. Enable via train.py --workers when
    the first-pod throughput probe shows a leg is loader-bound (the standing gate)."""
    sampler = WidthBucketBatchSampler(dataset.widths, batch_size, seed=seed, shuffle=shuffle)
    if pack_bucket_tails:
        sampler = PackedWidthBatchSampler(dataset.widths, batch_size, seed=seed, shuffle=shuffle)
    kw = dict(
        batch_sampler=sampler,
        collate_fn=collate_strips,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )
    if num_workers > 0:  # these DataLoader args are invalid when num_workers == 0
        kw["persistent_workers"] = True
        kw["prefetch_factor"] = 4
    loader = torch.utils.data.DataLoader(dataset, **kw)
    return loader, sampler


class PackedWidthBatchSampler(WidthBucketBatchSampler):
    """Keep full width-bucket batches; combine their tails into full batches.

    Every row occurs once and len == ceil(N/bs), independent of width distribution.
    Opt-in for equal-update mixture sweeps; images/widths are never modified.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._n_batches = ceil_div(sum(len(v) for v in self.buckets.values()), self.batch_size)

    def __iter__(self):
        rng = np.random.default_rng([self.seed, self._epoch]) if self.shuffle else None
        batches, tails = [], []
        for key in sorted(self.buckets):
            idx = self.buckets[key]
            if rng is not None:
                idx = idx[rng.permutation(len(idx))]
            full = len(idx) // self.batch_size * self.batch_size
            batches.extend([[int(v) for v in idx[s:s+self.batch_size]]
                            for s in range(0, full, self.batch_size)])
            tails.extend(int(v) for v in idx[full:])
        batches.extend([tails[s:s+self.batch_size] for s in range(0, len(tails), self.batch_size)])
        if rng is not None:
            batches = [batches[k] for k in rng.permutation(len(batches))]
        return iter(batches)


class ManifestDataset(StripDataset):
    """Rows assembled from a validated mix; targets remain the factory's label_ids."""

    def __init__(self, rows, codec_version, max_label_id, split):
        self.rows = rows
        self.images, self.labels, self.scripts = [], [], []
        widths = []
        for i, row in enumerate(rows):
            if row['split'] != split or row['codec_version'] != codec_version:
                raise ValueError(f'assembled row {i}: split/codec mismatch')
            w, ids = row['width'], row['label_ids']
            if not WIDTH_MIN <= w <= WIDTH_MAX or not ids or min(ids) < 1 or max(ids) > max_label_id:
                raise ValueError(f'assembled row {i}: invalid width or label_ids')
            with Image.open(io.BytesIO(row['image_png'])) as image:
                if image.mode != 'L' or image.size != (w, STRIP_HEIGHT):
                    raise ValueError(f'assembled row {i}: PNG violates strip contract')
            self.images.append(row['image_png'])
            widths.append(w)
            self.labels.append(np.asarray(ids, dtype=np.int64))
            self.scripts.append(row['script_class'])
        if not rows:
            raise ValueError(f'empty assembled {split} set')
        self.widths = np.asarray(widths, dtype=np.int64)
