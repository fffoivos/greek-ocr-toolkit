"""Shared docTR-DBNet detector plumbing for train/detector_train.py + pipeline/detector_eval.py.
Model factory, the fixed input normalization, and the transform stacks (with page_degrade as on-the-fly
image augmentation). Keeping this in one place so the trainer and eval use byte-identical preprocessing.

docTR API (locked, per docs/detector_plan.md): input (N,3,1024,1024) float, Normalize(MEAN,STD);
model(x, target=)->{"loss"}; model(x, return_preds=True)->{"preds": list[dict{"words":(M,5)}]} rel-coords.
"""
from __future__ import annotations

import functools
import os
import sys

import numpy as np
import torch
from torchvision.transforms import Compose, Normalize

from doctr.models import db_mobilenet_v3_large, db_resnet50
from doctr.transforms import RandomResize, RandomRotate, Resize, SampleCompose

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "pipeline"))
from page_degrade import degrade  # noqa: E402

MEAN = (0.798, 0.785, 0.772)
STD = (0.264, 0.2749, 0.287)
INPUT = 1024


def pick_device(pref: str = "") -> torch.device:
    if pref:
        return torch.device(pref)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def build_model(arch: str = "db_mobilenet_v3_large", ckpt: str | None = None, device="cpu"):
    fn = db_mobilenet_v3_large if "mobilenet" in arch else db_resnet50
    # warm ImageNet backbone only when training from scratch (no ckpt)
    model = fn(pretrained=False, pretrained_backbone=(ckpt is None))
    if ckpt:
        blob = torch.load(ckpt, map_location="cpu", weights_only=False)
        model.load_state_dict(blob["model"] if isinstance(blob, dict) and "model" in blob else blob)
    return model.to(device)


def _degrade_t(img: torch.Tensor, seed) -> torch.Tensor:
    """img: (3,H,W) float[0,1]. Degrade the grayscale (composer pages are gray → channel 0), re-broadcast to 3ch."""
    g = img[0].cpu().numpy()                                   # HxW [0,1]
    s = int(np.random.randint(0, 2**31 - 1)) if seed is None else int(seed)
    dg = degrade(g, s)                                          # HxW [0,1]
    return torch.from_numpy(dg).float().unsqueeze(0).repeat(3, 1, 1)


def img_transforms(train: bool, do_degrade: bool = True):
    steps = []
    if do_degrade:
        seed = None if train else 0                            # train: random aug; eval: fixed realization
        steps.append(functools.partial(_degrade_t, seed=seed))  # picklable (DataLoader workers)
    steps.append(Normalize(MEAN, STD))
    return Compose(steps)


def worker_init(worker_id):
    """Give each DataLoader worker its own numpy stream so page_degrade augmentation varies across workers."""
    np.random.seed((torch.initial_seed() % 2**31) + worker_id)


# Box-aware SCALE JITTER (guide_W3_fable §2.2: "vary body size so pitch at the 1024 input spans
# ~16–55px" + Phase-3 scale diversity). docTR's RandomResize rescales the page (h,w independently)
# BEFORE the canonical square Resize and co-transforms the polygon target; when h,w scale unequally
# the intermediate is aspect-padded, so after the final square-stretch the content occupies a random
# sub-region of the 1024 canvas -> the effective glyph PITCH varies per sample (down-scale only, so
# text gets smaller/denser -> the many-lines regime the detector fails on). TRAIN-ONLY: eval and the
# product/eval harness keep the frozen square-stretch geometry so the val metric stays comparable.
SCALE_JITTER_RANGE = (0.6, 1.0)
SCALE_JITTER_P = 0.5


def sample_transforms(train: bool, scale_jitter: bool = True):
    ts = []
    if train and scale_jitter:
        ts.append(RandomResize(SCALE_JITTER_RANGE, preserve_aspect_ratio=True, symmetric_pad=True, p=SCALE_JITTER_P))
    ts.append(Resize((INPUT, INPUT)))
    if train:
        ts.append(RandomRotate(3, expand=False))  # box-aware: co-rotates the polygon targets (F.rotate_sample)
    return SampleCompose(ts)
