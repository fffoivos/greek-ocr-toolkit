#!/usr/bin/env python3
"""Training driver for the greek-page-ocr line recognizer.

Contracts (frozen): docs/data_contracts.md; design: docs/architecture/04_recognizer.md,
docs/architecture/06_training_regimes.md.

Recipe (per 04 §4.1 / 06 §6.1): AdamW(lr 6.5e-4, wd 0.05) + OneCycleLR(pct_start=0.075)
over total optimizer steps, grad clip 5.0, CTCLoss(blank=0, zero_infinity=True).
AMP: bf16 autocast on cuda only; the CTC loss is ALWAYS computed in fp32 (log_probs are
cast .float() first — documented fp16 CTC NaN history, 06 §6.4).

Model selection / early stop (patience 6): on --transfer-mix CER when given, else on val
CER. Rationale (06): selecting on train-distribution val selects fit, not transfer.

Outputs in --out-dir: train_log.csv (epoch, step, train_loss, lr, val_cer, transfer_cer,
blank_rate, wall_s), best.pt, last.pt, checkpoint_meta.json (sha256 custody).

Architectures: --arch {compact,svtrv2,svtrv2_small} (default compact) — the A/B arms of
docs/iteration_2_plan.md; registry in train/model.py, reference arm in rec/svtrv2_model.py.

Modes:
  --selftest : no data needed — for EVERY arch: build, forward shapes (T == ceil(W/4) at
               W in {64,130,250,384}), log_softmax property (train+eval), fp32 CTC
               backward finite + one optimizer step.
  --smoke    : cap 2000 rows per dataset, 2 epochs, bs 32.
"""

from __future__ import annotations

import argparse
import csv
import copy
import hashlib
import json
import math
import os
import random
import struct
import sys
import time

# Keep manifest validation independent of Torch and device initialization.
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
if __package__:
    from .mix import MixError, validate, load_rows, assemble, provenance
else:
    from greekocr._vendor.train.mix import MixError, validate, load_rows, assemble, provenance

ARCH_CHOICES = ("compact", "a32", "b_a64", "svtrv2", "svtrv2_small")
HEAD_CHOICES = ("nfd", "precomposed", "two")


def _runtime():
    if "torch" in globals():
        return
    import numpy as np
    import torch
    import torch.nn as nn
    from greekocr._vendor.train import ckpt_io
    from greekocr._vendor.train.cer import load_codec
    from greekocr._vendor.train.ctc_health import CtcHealth
    from greekocr._vendor.train.heads import build_arm
    from greekocr._vendor.train.model import amp_dtype_for, autocast_ctx, build_model, ceil_div, count_params, masked_forward
    globals().update({k: v for k, v in locals().items() if not k.startswith("_")})

PATIENCE = 6
GRAD_CLIP = 5.0


def no_decay_param_groups(model, weight_decay):
    """AdamW two-group split (WP-A iv): weight decay only on >=2-D weights; biases + norm (1-D) params
    get 0 decay (standard practice). Enabled by --no-decay-norm-bias; the default recipe decays all
    params (matches S16 so the masked rerun stays a clean single-variable comparison)."""
    decay, no_decay = [], []
    for p in model.parameters():
        if p.requires_grad:
            (no_decay if p.ndim <= 1 else decay).append(p)
    return [{"params": decay, "weight_decay": weight_decay},
            {"params": no_decay, "weight_decay": 0.0}]
PCT_START = 0.075


# ---------------------------------------------------------------------------
# args / setup
# ---------------------------------------------------------------------------


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    supplied = sys.argv[1:] if argv is None else argv
    if any(x.split("=", 1)[0] in ("--train-dir", "--val-dir", "--transfer-dev") for x in supplied):
        p.error("loose data directories are retired; use --mix mix.json (optional --transfer-mix)")
    p.add_argument("--mix", help="validated mix.json: the only training/validation data input")
    p.add_argument("--transfer-mix", default=None, help="optional provenanced reserved-evaluation mix.json")
    p.add_argument("--selection-metric", choices=["auto", "val_cer"], default="auto",
                   help="val_cer keeps transfer monitoring out of checkpoint selection")
    p.add_argument("--transfer-final-only", action="store_true",
                   help="bind transfer provenance without epoch evaluation; final best is evaluated by readout")
    p.add_argument("--epoch-rows", type=int, help="cap assembled TRAIN rows each epoch (equal mixture exposure)")
    p.add_argument("--pack-bucket-tails", action="store_true",
                   help="combine width-bucket tails: exactly ceil(epoch rows / bs) batches")
    p.add_argument("--codec", help="codec vN JSON (data_contracts §1)")
    p.add_argument("--arch", choices=ARCH_CHOICES, default="compact",
                   help="architecture (iteration_2_plan §A/B): compact = arm M (default), "
                        "svtrv2 = vendored OpenOCR R-base, svtrv2_small = R-small")
    p.add_argument("--head", choices=HEAD_CHOICES, default="nfd",
                   help="P1 head arm (04 §4.4): nfd = arm B incumbent (default), "
                        "precomposed = arm A (NFC codec), two = arm C (base CTC + marks sigmoid). "
                        "precomposed/two fix --arch compact.")
    p.add_argument("--greek-only", action="store_true",
                   help="P1 pilot: train/val/transfer-dev on the Greek slice only "
                        "(script_class in {greek_mono, greek_poly}) — prereg_t1 §2.")
    p.add_argument("--out-dir", help="output dir for checkpoints/logs")
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--bs", type=int, default=256)
    p.add_argument("--accum", type=int, default=1, help="gradient accumulation steps")
    p.add_argument("--lr", type=float, default=6.5e-4)
    p.add_argument("--wd", type=float, default=0.05)
    # WP-A iv: optimizer recipe deltas for FUTURE runs. Defaults reproduce the S16 recipe EXACTLY so
    # S19-BKO Arm 0 (masked rerun) isolates the mask delta; opt in for T1'-era runs.
    p.add_argument("--no-decay-norm-bias", action="store_true",
                   help="WP-A iv: exclude biases + norm (1-D) params from AdamW weight decay")
    p.add_argument("--no-cycle-momentum", action="store_true",
                   help="WP-A iv: OneCycleLR cycle_momentum=False (recommended for Adam-family)")
    p.add_argument("--seed", type=int, default=0)
    # REV H.1(3) loader speedup (WP-A F3): opt-in dataloader workers + pinned memory for the TRAIN loader
    # (val/transfer stay in-process for eval reproducibility). Default 0 = the deterministic path; the
    # first-pod throughput probe decides whether to raise it.
    p.add_argument("--workers", type=int, default=0, help="train DataLoader worker processes (0 = in-process)")
    p.add_argument("--pin-memory", action="store_true", help="pin host memory for the train loader (cuda)")
    p.add_argument("--device", choices=["cuda", "mps", "cpu"], default=None, help="default: auto-detect")
    p.add_argument("--smoke", action="store_true", help="cap 2000 rows, 2 epochs, bs 32")
    p.add_argument("--resume", metavar="CKPT", default=None,
                   help="resume from a checkpoint (restores model+opt+sched+global_step+RNG; S15e(b))")
    p.add_argument("--init-from", metavar="CKPT", default=None,
                   help="strict weights-only initialization; fresh optimizer/scheduler/step/RNG")
    p.add_argument("--selftest", action="store_true", help="no data: model forward/backward check")
    args = p.parse_args(argv)
    if args.epoch_rows is not None and args.epoch_rows < 1:
        p.error("--epoch-rows must be positive")
    if args.init_from and args.resume:
        p.error("--init-from and --resume are mutually exclusive")

    if not args.selftest:
        if not args.mix:
            p.error("training data requires --mix mix.json")
        # BEFORE Torch imports, seed setting, filesystem outputs, or CUDA detection.
        validate(args.mix, role='train')
        if args.transfer_mix:
            validate(args.transfer_mix, role='transfer')
        missing = [n for n, v in [("--codec", args.codec), ("--out-dir", args.out_dir)] if not v]
        if missing:
            p.error(f"required (unless --selftest): {' '.join(missing)}")
        if args.smoke:
            args.epochs, args.bs = 2, 32
    return args


def set_seeds(seed: int) -> None:
    """Seed python/numpy/torch. Full determinism is not forced
    (torch.use_deterministic_algorithms stays off); seeds are recorded in the meta json."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_build_info(data_dir: str):
    """data_contracts §3: build_info.json sits at the dataset root, beside {train,val,reserved}/."""
    for cand in (os.path.join(data_dir, "build_info.json"),
                 os.path.join(os.path.dirname(os.path.abspath(data_dir)), "build_info.json")):
        if os.path.isfile(cand):
            return {"path": cand, "sha256": sha256_file(cand)}
    return None


def initialize_weights(model, path: str, *, arch: str, head: str, codec) -> dict:
    """Strict weights-only transfer; never inherit donor optimization or RNG state."""
    _runtime()
    if path.endswith(".safetensors"):
        sd, meta = ckpt_io.load_model_weights(path)
    else:
        # Resume wrappers contain numpy RNG arrays. Allow only these standard types;
        # weights_only=True still refuses arbitrary/custom pickle globals. No optional
        # safetensors dependency or sibling-weight ambiguity for .pt initialization.
        from numpy.core.multiarray import _reconstruct
        allowed = [_reconstruct, np.ndarray, np.dtype, type(np.dtype("uint32"))]
        if _reconstruct.__module__ != "numpy.core.multiarray":
            allowed.append((_reconstruct, "numpy.core.multiarray._reconstruct"))
        with torch.serialization.safe_globals(allowed):
            ck = torch.load(path, map_location="cpu", weights_only=True)
        sd, meta = ck["model"], ck
    expected = {"arch": arch, "head": head, "codec_version": codec.version,
                "n_classes": codec.n_classes}
    for key, value in expected.items():
        actual = meta.get(key)
        if key == "n_classes" and actual is not None:
            actual = int(actual)
        if actual != value:
            raise ValueError(f"--init-from {key}: {actual!r} != {value!r}")
    model.load_state_dict(sd, strict=True)
    return {"path": path, "sha256": sha256_file(path)}


# ---------------------------------------------------------------------------
# --selftest: no data needed
# ---------------------------------------------------------------------------


def _selftest_arch(arch: str, n_classes: int = 101) -> None:
    """One arch through the full battery: shapes, log_softmax, fp32 CTC backward + step."""
    print(f"[selftest] --- arch={arch} (n_classes={n_classes}, cpu) ---")
    torch.manual_seed(0)
    model, _ = build_model(n_classes=n_classes, arch=arch)  # prints param count
    model.to(torch.device("cpu"))

    # forward shapes, incl. widths that are NOT multiples of 4 (T = ceil(W/4) contract);
    # checked in BOTH modes (svtrv2's vendored decoder branches on train/eval — the
    # wrapper must return log-probs either way).
    for w in (64, 130, 250, 384):
        x = torch.rand(2, 1, 48, w) * 2 - 1  # normalized input domain [-1, 1)
        t = ceil_div(w, 4)
        for mode in ("train", "eval"):
            model.train(mode == "train")
            if mode == "train":
                out = model(x)
            else:
                with torch.no_grad():
                    out = model(x)
            assert out.shape == (2, t, n_classes), \
                f"{arch} W={w} {mode}: got {tuple(out.shape)}, want (2,{t},{n_classes})"
            lse = torch.logsumexp(out, dim=-1)
            assert torch.allclose(lse, torch.zeros_like(lse), atol=1e-4), \
                f"{arch} W={w} {mode}: output is not log_softmax"
    print(f"[selftest] {arch}: forward OK — T == ceil(W/4) for W in (64, 130, 250, 384), "
          "log_softmax holds in train+eval")

    # backward through fp32 CTC (blank=0, zero_infinity=True) + one optimizer step
    model.train()
    w = 192
    x = torch.rand(4, 1, 48, w) * 2 - 1
    out = model(x)  # [B, T, C]
    t = out.shape[1]
    input_lengths = torch.tensor([t, t - 3, t - 10, t], dtype=torch.long)
    target_lengths = torch.tensor([10, 8, 5, 12], dtype=torch.long)
    targets = torch.randint(1, n_classes, (int(target_lengths.sum()),), dtype=torch.long)
    ctc = nn.CTCLoss(blank=0, zero_infinity=True)
    loss = ctc(out.float().transpose(0, 1), targets, input_lengths, target_lengths)
    assert torch.isfinite(loss), f"{arch}: CTC loss not finite: {loss}"
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.05)
    loss.backward()
    grads = [p.grad for p in model.parameters() if p.grad is not None]
    assert grads, f"{arch}: no gradients after backward"
    assert all(torch.isfinite(g).all() for g in grads), f"{arch}: non-finite gradients"
    torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
    opt.step()
    print(f"[selftest] {arch}: backward OK — ctc_loss={loss.item():.4f} (fp32), "
          "grads finite, opt step ran")


def _selftest_head() -> None:
    """P1 head arms (04 §4.4): the heads.py battery (build/forward/decode/loss on a synthetic codec)
    plus a real-dimension forward-shape check on the shipped codec/v1.json."""
    from greekocr._vendor.train import heads

    heads._selfcheck()  # arm A + C: build, forward, decode round-trips, arm-C dual loss + backward
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    codec = load_codec(os.path.join(root, "codec", "v1.json"))
    th = heads.build_two_head_codec(codec)
    n_prec = len(heads.derive_precomposed_atoms(codec)) + 1  # + blank
    armA = heads.PrecomposedRecognizer(n_prec)
    armC = heads.TwoHeadRecognizer(th.n_base, th.n_marks)
    for w in (64, 130, 250, 384):
        t = ceil_div(w, 4)
        x = torch.rand(2, 1, 48, w) * 2 - 1
        outA = armA(x)
        assert outA.shape == (2, t, n_prec), f"arm A W={w}: {tuple(outA.shape)} != (2,{t},{n_prec})"
        lse = torch.logsumexp(outA, dim=-1)
        assert torch.allclose(lse, torch.zeros_like(lse), atol=1e-4), f"arm A W={w}: not log_softmax"
        baseLP, markLG = armC(x)
        assert baseLP.shape == (2, t, th.n_base), f"arm C base W={w}: {tuple(baseLP.shape)}"
        assert markLG.shape == (2, t, th.n_marks), f"arm C marks W={w}: {tuple(markLG.shape)}"
    print(f"[selftest] heads: arm A (precomposed n={n_prec}) + arm C (base {th.n_base}, marks {th.n_marks}) "
          "forward OK — T == ceil(W/4); heads.py battery PASS")


def run_selftest() -> int:
    _runtime()
    for arch in ARCH_CHOICES:  # compact, svtrv2, svtrv2_small — ALL must pass
        _selftest_arch(arch)
    _selftest_head()  # P1 head arms A/C (04 §4.4)
    print(f"SELFTEST PASS ({', '.join(ARCH_CHOICES)} archs + P1 heads {', '.join(HEAD_CHOICES)})")
    return 0


# ---------------------------------------------------------------------------
# training
# ---------------------------------------------------------------------------


def load_resume(args):
    """Read the full CPU checkpoint; validate_resume owns every state check."""
    if not args.resume:
        return None
    try:
        return torch.load(args.resume, map_location="cpu", weights_only=False)
    except Exception as e:
        raise MixError(f"resume checkpoint cannot be loaded: {e}") from e


def state_tensors(value, path='state'):
    """Visit tensor occurrences, including repeated objects, without memoization."""
    if torch.is_tensor(value):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from state_tensors(item, f'{path}[{key!r}]')
        yield from state_tensors(getattr(value, '_metadata', None), path + '._metadata')
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from state_tensors(item, f'{path}[{index}]')


def tensor_storage_range(tensor):
    storage = tensor.untyped_storage()
    start = storage.data_ptr()
    # _cdata distinguishes zero-byte storages, whose data_ptr can all be zero.
    return (str(tensor.device), storage._cdata, start, start + storage.nbytes())


def assert_state_independent(value, label, *, contiguous=False):
    """Require separate full storage allocations and provably no internal overlap."""
    seen = []
    for path, tensor in state_tensors(value):
        if tensor.layout != torch.strided or tensor.is_quantized:
            raise MixError(f'{label}: unsupported tensor layout at {path}')
        # Sorted strides prove injectivity cheaply, including dense transposes
        # and ordinary slices. Unprovable exotic layouts fail closed.
        span = 1
        for stride, size in sorted((s, n) for s, n in zip(tensor.stride(), tensor.shape) if n > 1):
            if stride < span:
                raise MixError(f'{label}: internal storage overlap (or unprovable layout) at {path}')
            span += (size - 1) * stride
        if contiguous and (not tensor.is_contiguous() or tensor.storage_offset() != 0):
            raise MixError(f'{label}: tensor is not fresh contiguous storage at {path}')
        device, identity, start, end = tensor_storage_range(tensor)
        for old_device, old_identity, old_start, old_end, old_path in seen:
            if device == old_device and (identity == old_identity or (
                    start < old_end and old_start < end)):
                raise MixError(f'{label}: shared/overlapping storage at {old_path} and {path}')
        seen.append((device, identity, start, end, path))


def clone_state_tensors(value):
    """Clone each occurrence into independent storage; never preserve tensor aliases."""
    if torch.is_tensor(value):
        return value.detach().clone().contiguous()
    if isinstance(value, dict):
        result = copy.copy(value)
        result.clear()
        result.update((key, clone_state_tensors(item)) for key, item in value.items())
        if hasattr(value, '_metadata'):
            result._metadata = clone_state_tensors(value._metadata)
        return result
    if isinstance(value, list):
        return [clone_state_tensors(item) for item in value]
    if isinstance(value, tuple):
        return tuple(clone_state_tensors(item) for item in value)
    return copy.deepcopy(value)


def checkpoint_state_sha256(ck):
    """Hash canonical state, independent of pickle, pointer addresses and dict order.

    Version 2 covers EVERY checkpoint field, including the receipt snapshot and
    model's state_dict metadata. Only the top-level digest and the current epoch's
    embedded receipt digest are omitted to break their self-reference. Prior
    epoch digests remain covered. Tensors include dtype, shape and all logical
    bytes in contiguous little-endian order, strides, offsets, storage sizes and
    structural storage sharing/overlap; container/scalar types are framed.
    Unsupported values fail closed rather than being silently dropped.
    """
    payload = dict(ck)
    payload.pop('state_sha256', None)
    binding = payload.get('data_provenance')
    if isinstance(binding, dict) and isinstance(binding.get('receipt'), dict):
        binding = payload['data_provenance'] = dict(binding)
        snapshot = binding['receipt'] = dict(binding['receipt'])
        if isinstance(snapshot.get('epochs'), dict):
            epochs = snapshot['epochs'] = dict(snapshot['epochs'])
            key = str(payload.get('epoch'))
            if isinstance(epochs.get(key), dict):
                epochs[key] = dict(epochs[key])
                epochs[key].pop('state_sha256', None)

    def blob(tag, raw):
        yield tag + struct.pack('>Q', len(raw))
        yield raw

    storages = []

    def parts(value):
        if value is None:
            yield b'N'
        elif type(value) is bool:
            yield b'T' if value else b'F'
        elif type(value) is int:
            yield from blob(b'I', str(value).encode('ascii'))
        elif type(value) is float:
            yield b'D' + struct.pack('>d', value)
        elif isinstance(value, str):
            yield from blob(b'S', value.encode('utf-8'))
        elif isinstance(value, bytes):
            yield from blob(b'B', value)
        elif torch.is_tensor(value):
            if value.layout != torch.strided or value.is_quantized:
                raise MixError('unsupported checkpoint tensor layout')
            tensor = value.detach().cpu().contiguous()
            raw = tensor.reshape(-1).view(torch.uint8).numpy().tobytes()
            if sys.byteorder != 'little' and tensor.element_size() > 1:
                n = tensor.element_size()
                raw = b''.join(raw[i:i+n][::-1] for i in range(0, len(raw), n))
            yield b'X'
            yield from parts(str(tensor.dtype))
            yield from parts(tuple(tensor.shape))
            yield from parts(tuple(value.stride()))
            yield from parts(value.storage_offset())
            yield from parts(int(torch._debug_has_internal_overlap(value)))
            device, identity, start, end = tensor_storage_range(value)
            storage_id = next((i for i, old in enumerate(storages)
                               if old[:2] == (device, identity)), None)
            if storage_id is None:
                storage_id = len(storages)
                storages.append((device, identity, start, end))
            overlaps = tuple(i for i, (d, _, a, b) in enumerate(storages[:storage_id])
                             if d == device and start < b and a < end)
            # IDs are first-encounter ordinals in canonical traversal, never
            # process-specific pointers. Separate equivalent allocations agree.
            yield from parts((storage_id, end - start, overlaps))
            yield from blob(b'B', raw)
        elif isinstance(value, (np.ndarray, np.generic)):
            array = np.asarray(value)
            if array.dtype.hasobject or array.dtype.fields:
                raise MixError('unsupported checkpoint numpy dtype')
            array = array.astype(array.dtype.newbyteorder('<'), copy=False)
            yield b'A'
            yield from parts(array.dtype.str)
            yield from parts(tuple(array.shape))
            yield from blob(b'B', array.tobytes(order='C'))
        elif isinstance(value, dict):
            yield b'M' + struct.pack('>Q', len(value))
            keys = sorted((b''.join(parts(k)), k) for k in value)
            for encoded, key in keys:
                yield encoded
                yield from parts(value[key])
            yield from parts(getattr(value, '_metadata', None))
        elif isinstance(value, (list, tuple)):
            yield (b'L' if isinstance(value, list) else b'Q') + struct.pack('>Q', len(value))
            for item in value:
                yield from parts(item)
        else:
            raise MixError(f'unsupported checkpoint value type: {type(value).__name__}')

    digest = hashlib.sha256(b'greek-page-ocr/checkpoint-state/v2\0')
    for part in parts(payload):
        digest.update(part)
    return digest.hexdigest()


def validate_resume(ck, plan, receipt):
    """One fail-closed gate for donor state, planned schedule and existing custody.

    No run-output writes. Runtime initialization may use system temporary/cache
    paths before this gate. Strict restoration is part of validation: PyTorch's
    scheduler load alone accepts partial dictionaries and incompatible horizons.
    """
    try:
        if not isinstance(ck, dict):
            raise MixError("resume checkpoint must be an object")
        # Integrity is FIRST, before field validation or any live-state restore.
        # Legacy state cannot be certified after the fact: migration is none.
        recorded = ck.get('state_sha256')
        if recorded is None:
            raise MixError('legacy checkpoint missing state_sha256; migration: none, retrain')
        if ck.get('state_hash_version') != 2:
            raise MixError('unsupported checkpoint state_hash_version; migration: none, retrain')
        if (not isinstance(recorded, str) or len(recorded) != 64
                or checkpoint_state_sha256(ck) != recorded):
            raise MixError('resume checkpoint state_sha256 mismatch')
        epoch_key = str(ck.get('epoch'))
        for source, label in ((receipt, 'receipt'),
                              (ck.get('data_provenance', {}).get('receipt'), 'snapshot')):
            if (not isinstance(source, dict) or not isinstance(source.get('epochs'), dict)
                    or not isinstance(source['epochs'].get(epoch_key), dict)
                    or source['epochs'][epoch_key].get('state_sha256') != recorded):
                raise MixError(f'resume {label} epoch state_sha256 mismatch')
        args, codec = plan['args'], plan['codec']
        required = {'model', 'opt', 'sched', 'rng', 'epoch', 'args', 'global_step',
                    'best', 'bad_epochs', 'data_provenance', 'arch', 'head',
                    'codec_version', 'codec_sha256', 'n_classes', 'seed'}
        if required - ck.keys():
            raise MixError(f"incomplete resume checkpoint: {sorted(required - ck.keys())}")
        for key, value in dict(arch=args.arch, head=args.head, codec_version=codec.version,
                               n_classes=codec.n_classes, seed=args.seed,
                               codec_sha256=sha256_file(args.codec)).items():
            if ck[key] != value:
                raise MixError(f"resume checkpoint {key} mismatch")
        if type(ck['epoch']) is not int or not 1 <= ck['epoch'] <= args.epochs:
            raise MixError("resume checkpoint epoch outside training horizon")
        if not isinstance(ck['args'], dict) or ck['args'].get('epochs') != args.epochs:
            raise MixError("resume --epochs mismatch: re-run the SAME command")
        for key in ('arch', 'head', 'seed', 'bs', 'accum', 'lr', 'wd', 'greek_only', 'smoke', 'epoch_rows',
                    'pack_bucket_tails', 'no_decay_norm_bias', 'no_cycle_momentum',
                    'selection_metric', 'transfer_final_only'):
            if key not in ck['args'] or ck['args'][key] != getattr(args, key):
                raise MixError(f"resume checkpoint argument mismatch: {key}")
        for key in ('model', 'opt', 'sched', 'rng', 'best'):
            if not isinstance(ck[key], dict):
                raise MixError(f"resume checkpoint {key} must be an object")
        if any(type(ck[k]) is not int or ck[k] < 0 for k in ('global_step', 'bad_epochs')):
            raise MixError("invalid resume counters")
        step, total = ck['global_step'], plan['total_steps']
        completed_limit = sum(plan['epoch_steps'][:ck['epoch']])
        if not 0 <= step <= completed_limit <= total:
            raise MixError("resume updates outside completed-epoch schedule")

        expected_sched = plan['sched'].state_dict()
        state = ck['sched']
        if state.keys() != expected_sched.keys():
            raise MixError(f"resume scheduler keys mismatch: missing "
                           f"{sorted(expected_sched.keys() - state.keys())}, unexpected "
                           f"{sorted(state.keys() - expected_sched.keys())}")
        # Compare every fixed field, including total_steps, all phase endpoints,
        # annealing/momentum configuration and per-group base rates. New scheduler
        # fields are fixed unless explicitly reviewed as a progress field here.
        progress_fields = {'last_epoch', '_step_count', '_last_lr'}
        for key in expected_sched.keys() - progress_fields:
            if state[key] != expected_sched[key]:
                raise MixError(f"resume scheduler {key} mismatch with planned schedule")
        if type(state['total_steps']) is not int or state['total_steps'] != total:
            raise MixError("resume scheduler total_steps mismatch with planned horizon")
        if type(state['last_epoch']) is not int or not 0 <= state['last_epoch'] <= total:
            raise MixError("resume scheduler last_epoch outside horizon")
        if state['last_epoch'] != step or type(state['_step_count']) is not int or state['_step_count'] != step + 1:
            raise MixError("resume scheduler progress differs from global_step")

        expected_opt = plan['opt'].state_dict()
        opt_state = ck['opt']
        if opt_state.keys() != expected_opt.keys() or not isinstance(opt_state['state'], dict):
            raise MixError("resume optimizer keys mismatch")
        groups = opt_state['param_groups']
        if not isinstance(groups, list) or len(groups) != len(expected_opt['param_groups']):
            raise MixError("resume optimizer parameter groups mismatch")
        params = {}
        for old, fresh, live in zip(groups, expected_opt['param_groups'], plan['opt'].param_groups):
            if not isinstance(old, dict) or old.keys() != fresh.keys() or old['params'] != fresh['params']:
                raise MixError("resume optimizer parameter group keys/parameters mismatch")
            for key in fresh.keys() - {'lr', 'betas'}:
                if old[key] != fresh[key]:
                    raise MixError(f"resume optimizer {key} mismatch")
            betas = old['betas']
            if not isinstance(betas, (tuple, list)) or len(betas) != 2 or betas[1] != fresh['betas'][1]:
                raise MixError("resume optimizer betas mismatch")
            if args.no_cycle_momentum:
                beta_ok = betas[0] == fresh['betas'][0]
            else:
                beta_ok = isinstance(betas[0], (int, float)) and fresh['base_momentum'] <= betas[0] <= fresh['max_momentum']
            if not beta_ok:
                raise MixError("resume optimizer momentum outside planned cycle")
            params.update(zip(old['params'], live['params']))
        rates = state['_last_lr']
        if not isinstance(rates, list) or len(rates) != len(groups):
            raise MixError("resume scheduler learning-rate groups mismatch")
        for rate, group in zip(rates, groups):
            if not isinstance(rate, (int, float)) or not math.isfinite(rate) or rate < 0 or rate != group['lr']:
                raise MixError("resume scheduler/optimizer learning rates mismatch")
        # This trainer has no freezes or per-parameter schedules. If that changes,
        # deliberately update this invariant; arbitrary subsets are never valid.
        active = {param_id for param_id, param in params.items() if param.requires_grad}
        if opt_state['state'].keys() != active:
            raise MixError("resume optimizer parameter state set mismatch: missing "
                           f"{sorted(active - opt_state['state'].keys())}, unexpected "
                           f"{sorted(opt_state['state'].keys() - active)}")
        for param_id, values in opt_state['state'].items():
            expected_keys = {'step', 'exp_avg', 'exp_avg_sq'}
            if not isinstance(values, dict) or values.keys() != expected_keys:
                raise MixError("resume optimizer parameter state keys mismatch")
            counter = values['step']
            if not torch.is_tensor(counter) or counter.ndim != 0:
                raise MixError("resume optimizer step must be a scalar tensor")
            count = counter.item()
            if not math.isfinite(count) or count != int(count) or count != step:
                raise MixError("resume optimizer step differs from global_step")
            for key in ('exp_avg', 'exp_avg_sq'):
                value = values[key]
                if not torch.is_tensor(value) or value.shape != params[param_id].shape or value.dtype != params[param_id].dtype:
                    raise MixError(f"resume optimizer {key} tensor mismatch")

        if not {'torch', 'numpy', 'python', 'cuda'} <= ck['rng'].keys():
            raise MixError("incomplete resume RNG state")
        cuda_rng = ck['rng']['cuda']
        if cuda_rng is not None and (not isinstance(cuda_rng, list) or any(
                not torch.is_tensor(v) or v.dtype != torch.uint8 or v.ndim != 1 for v in cuda_rng)):
            raise MixError("invalid resume CUDA RNG state")
        if not {'metric', 'epoch'} <= ck['best'].keys():
            raise MixError("incomplete resume best state")
        best = ck['best']
        if (type(best['epoch']) is not int or not 0 <= best['epoch'] <= ck['epoch']
                or not isinstance(best['metric'], (int, float)) or math.isnan(best['metric'])
                or best['metric'] < 0 or ck['bad_epochs'] > ck['epoch']):
            raise MixError("invalid resume best/patience state")

        if not isinstance(receipt, dict) or not isinstance(receipt.get('epochs'), dict):
            raise MixError("invalid resume provenance epochs")
        current = plan['provenance']
        for key in ('mix_sha256', 'mix', 'resolved_mix', 'recipe_sha256s', 'training_schedule', 'transfer'):
            old, new = receipt.get(key), current.get(key)
            if key == 'transfer' and isinstance(old, dict) and isinstance(new, dict):
                old = {k: v for k, v in old.items() if k != 'git_head'}
                new = {k: v for k, v in new.items() if k != 'git_head'}
            if old != new:
                raise MixError(f"resume provenance changed: {key}")
        binding = ck['data_provenance']
        if not isinstance(binding, dict):
            raise MixError("resume checkpoint lacks data_provenance binding")
        for key in ('mix_sha256', 'transfer_mix_sha256'):
            expected = current['mix_sha256'] if key == 'mix_sha256' else current.get('transfer', {}).get('mix_sha256')
            if key not in binding or binding[key] != expected:
                raise MixError(f"resume checkpoint {key} mismatch")
        snapshot = binding.get('receipt')
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get('epochs'), dict):
            raise MixError("resume checkpoint lacks provenance snapshot")
        for key in ('mix_sha256', 'mix', 'resolved_mix', 'recipe_sha256s', 'training_schedule', 'transfer'):
            if snapshot.get(key) != receipt.get(key):
                raise MixError(f"resume checkpoint receipt changed: {key}")
        for epoch in range(1, ck['epoch'] + 1):
            key = str(epoch)
            if key not in receipt['epochs'] or snapshot['epochs'].get(key) != receipt['epochs'][key]:
                raise MixError(f"resume checkpoint epoch {epoch} provenance mismatch")
        if any(not k.isdecimal() or not 1 <= int(k) <= min(args.epochs, ck['epoch'] + 1) for k in receipt['epochs']):
            raise MixError("resume provenance has incompatible future epochs")
        # Skipped nonfinite batches can reduce updates below the nominal horizon;
        # exact completed-epoch counts must agree with the existing receipt.
        for source in (receipt, snapshot):
            if not isinstance(source.get('checkpoint_updates'), dict) or str(ck['epoch']) not in source['checkpoint_updates']:
                raise MixError("invalid resume provenance checkpoint_updates")
        for source in (receipt, snapshot):
            progress = source['checkpoint_updates']
            previous = 0
            for epoch_key in sorted(progress, key=lambda k: int(k) if k.isdecimal() else -1):
                if not epoch_key.isdecimal() or not 1 <= int(epoch_key) <= ck['epoch'] + 1:
                    raise MixError("resume provenance update epoch outside horizon")
                updates = progress[epoch_key]
                limit = sum(plan['epoch_steps'][:int(epoch_key)])
                if type(updates) is not int or not previous <= updates <= limit:
                    raise MixError("resume provenance updates outside epoch schedule")
                previous = updates
            for epoch_key, updates in progress.items():
                if int(epoch_key) <= ck['epoch'] and receipt.get('checkpoint_updates', {}).get(epoch_key) != snapshot.get('checkpoint_updates', {}).get(epoch_key):
                    raise MixError("resume checkpoint receipt update history mismatch")
            if progress.get(str(ck['epoch'])) != step:
                raise MixError("resume checkpoint updates differ from existing receipt")
            if any(int(k) > ck['epoch'] for k in progress):
                raise MixError("resume receipt has a newer completed checkpoint")
        if not isinstance(receipt.get('sessions', []), list):
            raise MixError("invalid resume provenance sessions")
        next_epoch = str(ck['epoch'] + 1)
        if next_epoch in receipt['epochs'] and receipt['epochs'][next_epoch] != plan['next_epoch']['epochs'][next_epoch]:
            raise MixError(f"resume epoch {next_epoch} assembled rows differ from prior provenance")

        # Inspect the FILE state before cloning: a resealed alias is a refusal,
        # never a silent repair. Check opt and sched together for cross-aliases.
        assert_state_independent((opt_state, state), 'resume file optimizer/scheduler')
        restored_opt = clone_state_tensors(opt_state)
        restored_sched = clone_state_tensors(state)
        assert_state_independent((restored_opt, restored_sched),
                                 'resume cloned optimizer/scheduler', contiguous=True)
        try:
            plan['model'].load_state_dict(ck['model'], strict=True)
            plan['opt'].load_state_dict(restored_opt)
            plan['sched'].load_state_dict(restored_sched)
            assert_state_independent((plan['opt'].state_dict(), plan['sched'].state_dict()),
                                     'resume live optimizer/scheduler', contiguous=True)
            if any(values['step'].ndim != 0 for values in plan['opt'].state.values()):
                raise MixError('resume live optimizer step must be its own scalar tensor')
            # Recompute LR/momentum at the saved progress without a scheduler or
            # optimizer step. Equal corrupted LR fields cannot evade this check.
            with torch.optim.lr_scheduler._enable_get_lr_call(plan['sched']):
                expected_rates = plan['sched'].get_lr()
            if expected_rates != rates:
                raise MixError("resume learning rates differ from planned progress")
            if any(live['betas'] != saved['betas'] for live, saved in zip(plan['opt'].param_groups, groups)):
                raise MixError("resume momentum differs from planned progress")
            rng = ck['rng']
            torch.set_rng_state(rng['torch'].cpu())
            np.random.set_state(rng['numpy'])
            random.setstate(rng['python'])
            if rng['cuda'] is not None and torch.cuda.is_available():
                torch.cuda.set_rng_state_all(rng['cuda'])
        except (ValueError, RuntimeError, KeyError, TypeError, AttributeError, IndexError) as e:
            raise MixError(f"resume state cannot be restored: {e}") from e
    except MixError:
        raise
    except (ValueError, RuntimeError, KeyError, TypeError, AttributeError, OverflowError, IndexError) as e:
        raise MixError(f"invalid resume state: {e}") from e


def continue_provenance(args, current, ck, prior=None):
    """Append to an already validated receipt; this helper is not a preflight."""
    session = dict(start_epoch=1 if ck is None else ck['epoch'] + 1,
                   git_head=current['git_head'], args=copy.deepcopy(vars(args)),
                   mix_sha256=current['mix_sha256'])
    if ck is None:
        current['sessions'] = [session]
        return current
    result = copy.deepcopy(prior)
    session['resume'] = dict(path=str(Path(args.resume).resolve()), sha256=sha256_file(args.resume),
                             checkpoint_epoch=ck['epoch'])
    result.setdefault('sessions', []).append(session)
    return result


def add_epoch_provenance(receipt, report):
    for epoch, roles in report['epochs'].items():
        if epoch in receipt['epochs'] and receipt['epochs'][epoch] != roles:
            raise MixError(f"resume epoch {epoch} assembled rows differ from prior provenance")
        receipt['epochs'].setdefault(epoch, roles)


def train(args: argparse.Namespace) -> int:
    mix = validate(args.mix, role='train')
    transfer_mix = validate(args.transfer_mix, role='transfer') if args.transfer_mix else None
    _runtime()
    codec = load_codec(args.codec)
    if codec.version != mix['codec_version']:
        raise MixError("--codec version differs from mix codec_version")
    ck = load_resume(args)
    start_epoch = 1  # Donor epoch is untrusted until the complete preflight.
    from greekocr._vendor.train.data import ManifestDataset, make_loader
    keep = {"greek_mono", "greek_poly"} if args.greek_only else None
    groups = {role: load_rows(mix, role) for role in ('train', 'val')}
    if keep:
        groups = {role: [[r for r in group if r['script_class'] in keep] for group in pools]
                  for role, pools in groups.items()}
    fractions = [c['fraction'] for c in mix['components']]
    max_rows = 2000 if args.smoke else None

    def dataset(role, epoch):
        cap = args.epoch_rows if role == 'train' and args.epoch_rows is not None else max_rows
        rows, _ = assemble(groups[role], fractions, mix['seed'], epoch, cap)
        return ManifestDataset(rows, codec.version, codec.n_classes - 1, role)

    train_ds, val_ds = dataset('train', start_epoch), dataset('val', 0)
    transfer_ds = None
    if transfer_mix:
        if transfer_mix['codec_version'] != codec.version:
            raise MixError("transfer mix codec_version mismatch")
        transfer_groups = load_rows(transfer_mix, 'reserved')
        if keep:
            transfer_groups = [[r for r in g if r['script_class'] in keep] for g in transfer_groups]
        rows, _ = assemble(transfer_groups, [c['fraction'] for c in transfer_mix['components']],
                           transfer_mix['seed'], 0, max_rows)
        transfer_ds = ManifestDataset(rows, codec.version, codec.n_classes - 1, 'reserved')
    # Compute every epoch's loader horizon without doing a model forward/step. Width
    # buckets change with the sampled rows, so OneCycle gets the actual step total.
    horizons = []
    for epoch in range(1, args.epochs + 1):
        ds = train_ds if epoch == start_epoch else dataset('train', epoch)
        _, sampler = make_loader(ds, args.bs, seed=mix['seed'], shuffle=True,
                                 pack_bucket_tails=args.pack_bucket_tails)
        horizons.append(len(sampler))
    assembled = {} if ck is not None else {1: {'train': train_ds.rows, 'val': val_ds.rows}}
    receipt = provenance(args.mix, mix, assembled)
    receipt['training_schedule'] = dict(epoch_rows=args.epoch_rows,
        pack_bucket_tails=args.pack_bucket_tails, epoch_batches=horizons,
        selection_metric=args.selection_metric)
    if transfer_mix:
        receipt['transfer'] = provenance(args.transfer_mix, transfer_mix,
                                          {0: {'reserved': transfer_ds.rows}})

    def write_provenance():
        path = Path(args.out_dir) / 'data_provenance.json'
        candidate = path.with_suffix('.json.tmp')
        candidate.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
        candidate.replace(path)

    set_seeds(args.seed)
    if args.device is None:
        args.device = "cuda" if torch.cuda.is_available() else (
            "mps" if torch.backends.mps.is_available() else "cpu")
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        print("ERROR: --device cuda but CUDA is unavailable", file=sys.stderr)
        return 1
    if device.type == "mps" and not torch.backends.mps.is_available():
        print("ERROR: --device mps but MPS is unavailable", file=sys.stderr)
        return 1
    amp_dtype = amp_dtype_for(device)
    loss_device = torch.device("cpu") if device.type == "mps" else device
    print(f"[setup] codec={codec.version} device={device.type} data_seed={mix['seed']}")
    train_loader, train_sampler = make_loader(train_ds, args.bs, seed=mix['seed'], shuffle=True,
                                              num_workers=args.workers, pin_memory=args.pin_memory,
                                              pack_bucket_tails=args.pack_bucket_tails)
    val_loader, _ = make_loader(val_ds, args.bs, shuffle=False)  # eval: in-process (reproducible order)
    transfer_loader = None
    if transfer_ds is not None and not args.transfer_final_only:
        transfer_loader, _ = make_loader(transfer_ds, args.bs, shuffle=False)
    select_metric = "transfer_cer" if transfer_loader is not None and args.selection_metric == 'auto' else "val_cer"
    print(f"[setup] train={len(train_ds)} rows, val={len(val_ds)} rows"
          + (f", transfer-dev={len(transfer_ds)} rows" if transfer_ds is not None else ""))
    print(f"[setup] model-select/early-stop on {select_metric} (patience {PATIENCE})")

    model = build_arm(args.head, args.arch, codec)  # prints param count
    init_from = (initialize_weights(model, args.init_from, arch=args.arch, head=args.head,
                                    codec=codec) if args.init_from else None)
    model.to(device)
    # Per-arm training context (S15e(a)): arm A (precomposed) transcodes NFD->NFC precomposed CTC
    # targets; arm C (two) splits NFD->base+marks for two_head_loss; arm B (nfd) uses the batch's NFD
    # targets directly. All decode to NFD for the shared strict scorer.
    from greekocr._vendor.train.heads import build_precomposed_index, build_two_head_codec, nfd_ids_to_base_marks, nfd_ids_to_precomposed_ids, two_head_loss
    arm_prec_codec = arm_prec_index = arm_th = None
    if args.head == "precomposed":
        arm_prec_codec = load_codec(f"codec/precomposed_{codec.version}.json")
        arm_prec_index = build_precomposed_index(arm_prec_codec)
    elif args.head == "two":
        arm_th = build_two_head_codec(codec)
    arm_ctx = {"head": args.head, "prec_codec": arm_prec_codec, "th": arm_th}

    # WP-A iv: opt-in optimizer recipe deltas (defaults reproduce S16 exactly).
    opt_params = (no_decay_param_groups(model, args.wd) if args.no_decay_norm_bias
                  else model.parameters())
    opt = torch.optim.AdamW(opt_params, lr=args.lr, weight_decay=args.wd)
    steps_per_epoch = len(train_sampler)
    opt_steps_per_epoch = ceil_div(steps_per_epoch, args.accum)
    total_opt_steps = sum(ceil_div(n, args.accum) for n in horizons)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=args.lr, total_steps=total_opt_steps, pct_start=PCT_START,
        cycle_momentum=not args.no_cycle_momentum)
    ctc = nn.CTCLoss(blank=0, zero_infinity=True)
    print(f"[setup] {steps_per_epoch} batches/epoch, accum={args.accum} -> "
          f"{opt_steps_per_epoch} opt steps/epoch, {total_opt_steps} total")
    print(f"[optim] AdamW wd={args.wd} no_decay_norm_bias={args.no_decay_norm_bias} | "
          f"OneCycleLR pct_start={PCT_START} cycle_momentum={not args.no_cycle_momentum}")

    from greekocr._vendor.train.eval_cer import evaluate  # shared greedy-decode CER pass

    build_info = {"mix": {"path": args.mix, "sha256": sha256_file(args.mix)},
                  "data_provenance": str(Path(args.out_dir) / 'data_provenance.json')}

    def save_ckpt(path: str, epoch: int) -> None:
        # Bind exact completed-epoch updates in both the existing receipt and
        # checkpoint snapshot. This writer is only reachable after the gate.
        receipt.setdefault('checkpoint_updates', {})[str(epoch)] = global_step
        checkpoint = {
            "state_hash_version": 2,
            "model": model.state_dict(),
            "opt": opt.state_dict(),
            "epoch": epoch,
            "arch": args.arch,  # load-time dispatch (eval_cer.load_checkpoint)
            "head": args.head,  # P1 arm (nfd/precomposed/two)
            "codec_version": codec.version,
            "codec_sha256": sha256_file(args.codec),
            "n_classes": codec.n_classes,
            "seed": args.seed,  # S15e-cert F2: top-level so dump_preds groups by the real seed (not 0)
            "args": vars(args),
            "data_provenance": {
                "mix_sha256": receipt['mix_sha256'],
                "transfer_mix_sha256": receipt.get('transfer', {}).get('mix_sha256'),
                "receipt": copy.deepcopy(receipt),
            },
            **({"init_from": init_from} if init_from is not None else {}),
            # S15e(b) resume state: scheduler + global_step + RNG so a killed leg resumes equivalently.
            # S15e-cert F4: also persist best/bad_epochs so a resumed leg keeps its pre-kill best + patience.
            "sched": sched.state_dict(),
            "global_step": global_step,
            "best": best,
            "bad_epochs": bad_epochs,
            "rng": {
                "torch": torch.get_rng_state(),
                "numpy": np.random.get_state(),
                "python": random.getstate(),
                "cuda": (torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None),
            },
        }
        checkpoint['state_sha256'] = checkpoint_state_sha256(checkpoint)
        receipt['epochs'][str(epoch)]['state_sha256'] = checkpoint['state_sha256']
        checkpoint['data_provenance']['receipt'] = copy.deepcopy(receipt)
        torch.save(checkpoint, path)
        write_provenance()
        # WP-A ii: also write a weights-only safetensors sibling for SAFE inference load (no pickle),
        # bound to codec+arch+head (+codec sha256). Best-effort — skipped if safetensors is absent so
        # training never fails on it; the full-state .pt above is the resume artifact.
        st_meta = ckpt_io.build_meta(
            arch=args.arch, head=args.head, codec_version=codec.version,
            n_classes=codec.n_classes, codec_path=args.codec, seed=args.seed, epoch=epoch,
        )
        ckpt_io.save_safetensors(model.state_dict(), st_meta,
                                 os.path.splitext(path)[0] + ".safetensors")

    def write_meta(best: dict) -> None:
        # S15e-cert L2: a resume into a fresh out-dir where no post-resume epoch improves has best["epoch"]>0
        # (restored) but no local best.pt -> guard the sha instead of crashing after all compute is spent.
        best_pt = os.path.join(args.out_dir, "best.pt")
        meta = {
            "best_pt": best_pt,
            "best_pt_sha256": (sha256_file(best_pt) if os.path.exists(best_pt) else None),
            "best_epoch": best["epoch"],
            "best_metric": best["metric"],
            "select_metric": select_metric,
            "arch": args.arch,
            "head": args.head,  # P1 arm (nfd/precomposed/two)
            "codec_version": codec.version,
            "n_classes": codec.n_classes,
            "param_count": count_params(model),
            "seed": args.seed,
            "args": vars(args),
            "build_info": build_info,  # dataset custody: sha256 of build_info.json when present
            "versions": {"torch": torch.__version__, "numpy": np.__version__,
                         "python": sys.version.split()[0]},
            "ctc_health": ctc_health.as_dict(),  # WP-A iii: feasibility/NaN/rare counters (run cumulative)
        }
        if init_from is not None:
            meta["init_from"] = init_from
        with open(os.path.join(args.out_dir, "checkpoint_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    best = {"metric": math.inf, "epoch": 0}
    bad_epochs = 0
    global_step = 0
    if args.resume:
        path = Path(args.out_dir) / 'data_provenance.json'
        try:
            prior = json.loads(path.read_text())
        except (OSError, ValueError) as e:
            raise MixError(f"resume requires an existing valid data_provenance.json: {e}") from e
        # The donor epoch selects evidence only; validate_resume checks its
        # type/range and identity before the selected rows can be published.
        donor_epoch = ck.get('epoch') if isinstance(ck, dict) else None
        next_report = {}
        if type(donor_epoch) is int and 1 <= donor_epoch <= args.epochs:
            next_report = provenance(args.mix, mix, {donor_epoch + 1: {
                'train': dataset('train', donor_epoch + 1).rows, 'val': val_ds.rows}})
        plan = dict(args=args, codec=codec, model=model, opt=opt, sched=sched,
                    total_steps=total_opt_steps, epoch_steps=[ceil_div(n, args.accum) for n in horizons],
                    provenance=receipt, next_epoch=next_report)
        validate_resume(ck, plan, prior)  # THE only resume gate, before any write.
        start_epoch = ck['epoch'] + 1
        train_ds = dataset('train', start_epoch)
        receipt = continue_provenance(args, receipt, ck, prior)
        if start_epoch <= args.epochs:
            add_epoch_provenance(receipt, next_report)
        init_from = ck.get('init_from')
        global_step, best, bad_epochs = ck['global_step'], ck['best'], ck['bad_epochs']
        print(f"[resume] {args.resume}: epoch {ck['epoch']} done -> resume at {start_epoch}, "
              f"global_step={global_step}, best={best['metric']:.4f}@{best['epoch']}, bad={bad_epochs}")
    else:
        receipt = continue_provenance(args, receipt, None)

    os.makedirs(args.out_dir, exist_ok=True)
    write_provenance()  # full donor state passed; append session atomically
    csv_path = os.path.join(args.out_dir, "train_log.csv")
    csv_new = not os.path.exists(csv_path)
    csv_f = open(csv_path, "a", newline="", encoding="utf-8")
    csv_w = csv.writer(csv_f)
    if csv_new:
        csv_w.writerow(["epoch", "step", "train_loss", "lr", "val_cer", "transfer_cer",
                        "blank_rate", "wall_s"])
        csv_f.flush()

    # WP-A iii: cross-run CTC health — feasibility (T>=U+R) / NaN-batch / rare-token counters +
    # compound-abort so an infeasible-alignment run (which zero_infinity would silently zero) fails
    # loud instead of training on no signal. Counters reset per run session (not restored on resume).
    ctc_health = CtcHealth()
    try:  # WP-A cert F5: warn ONCE if the weights-only sibling can't be written (silent no-op otherwise)
        import safetensors  # noqa: F401
    except ImportError:
        print("[warn] safetensors not installed — checkpoints will NOT write a weights-only .safetensors "
              "sibling; inference falls back to the pickle path (pip install safetensors). [WP-A cert F5]")
    for epoch in range(start_epoch, args.epochs + 1):
        t0 = time.time()
        model.train()
        if epoch != 1:
            train_ds = dataset('train', epoch)
            train_loader, train_sampler = make_loader(
                train_ds, args.bs, seed=mix['seed'], shuffle=True,
                num_workers=args.workers, pin_memory=args.pin_memory,
                pack_bucket_tails=args.pack_bucket_tails)
        train_sampler.set_epoch(epoch)
        epoch_report = provenance(args.mix, mix, {epoch: {'train': train_ds.rows, 'val': val_ds.rows}})
        add_epoch_provenance(receipt, epoch_report)
        write_provenance()
        losses = []
        skipped = 0
        pending = 0
        opt.zero_grad(set_to_none=True)

        def opt_step():
            nonlocal pending, global_step
            torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            opt.step()
            if global_step < total_opt_steps:  # guard: never step the schedule past its horizon
                sched.step()
            opt.zero_grad(set_to_none=True)
            pending = 0
            global_step += 1

        for batch in train_loader:
            x = batch["images"].to(device)
            in_lens = batch["input_lengths"].to(loss_device)
            with autocast_ctx(device, amp_dtype):
                # WP-A: mask each strip's own right-pad frames (only for mask-aware arches; the vendored
                # svtrv2 forward takes x only -> masked_forward falls back to model(x)).
                out = masked_forward(model, x, in_lens)
            if args.head == "two":  # arm C: base CTC + marks BCE, ALL fp32 (06 §6.4 / S15e(a,d))
                base_lp, marks_lg = out
                base_lp = base_lp.float().to(loss_device)
                marks_lg = marks_lg.float().to(loss_device)
                base_t, marks_t = [], []
                for lab in batch["labels"]:
                    b_ids, m = nfd_ids_to_base_marks(list(lab), arm_th)
                    base_t.append(b_ids)
                    marks_t.append(m)
                loss = two_head_loss(base_lp, marks_lg, base_t, marks_t, in_lens)
            else:  # arm B (nfd) or arm A (precomposed): one CTC head, fp32, shape (T, B, C)
                lp = out.float().transpose(0, 1)
                if loss_device != device:
                    lp = lp.to(loss_device)
                if args.head == "precomposed":  # transcode NFD labels -> NFC precomposed ids
                    seqs = [nfd_ids_to_precomposed_ids(list(lab), codec, arm_prec_index)
                            for lab in batch["labels"]]
                    targets = torch.tensor([i for s in seqs for i in s], dtype=torch.long).to(loss_device)
                    tgt_lens = torch.tensor([len(s) for s in seqs], dtype=torch.long).to(loss_device)
                else:  # nfd
                    targets = batch["targets"].to(loss_device)
                    tgt_lens = batch["target_lengths"].to(loss_device)
                    # WP-A iii: screen the nfd CTC targets for feasibility (T>=U+R) before the loss —
                    # the deployable + S19-BKO Arm 0 + future-run head. (precomposed/two arms retired.)
                    ctc_health.update_batch(batch["targets"].tolist(),
                                            batch["target_lengths"].tolist(),
                                            batch["input_lengths"].tolist())
                    if ctc_health.batches % 200 == 0:  # WP-A cert F7: abort mid-epoch, not only at epoch end
                        ctc_health.check_abort()
                loss = ctc(lp, targets, in_lens, tgt_lens)
            if not torch.isfinite(loss):
                skipped += 1  # rare with zero_infinity; drop the whole accumulation group
                ctc_health.note_nan_batch()
                opt.zero_grad(set_to_none=True)
                pending = 0
                continue
            (loss / args.accum).backward()
            losses.append(loss.item())
            pending += 1
            if pending == args.accum:
                opt_step()
        if pending:  # flush a trailing partial accumulation group
            opt_step()

        train_loss = float(np.mean(losses)) if losses else float("nan")
        if skipped:
            print(f"[warn] epoch {epoch}: skipped {skipped} non-finite-loss batches")
        # WP-A iii: surface CTC health, then compound-abort (fails LOUD if too many samples are
        # infeasible T<U+R — which zero_infinity would silently zero — or too many NaN batches).
        _h = ctc_health.as_dict()
        if _h["infeasible"] or _h["nan_batches"]:
            print(f"[ctc-health] cumulative: infeasible={_h['infeasible']}/{_h['samples']} "
                  f"({_h['infeasible_frac']:.4%}), nan_batches={_h['nan_batches']}/{_h['batches']}")
        ctc_health.check_abort()

        val_res = evaluate(model, val_loader, codec, device, amp_dtype=amp_dtype, arm=arm_ctx)
        val_cer, blank_rate = val_res["cer"], val_res["blank_rate"]
        transfer_cer = None
        if transfer_loader is not None:
            transfer_cer = evaluate(model, transfer_loader, codec, device, amp_dtype=amp_dtype, arm=arm_ctx)["cer"]
        wall_s = time.time() - t0
        lr_now = sched.get_last_lr()[0]

        csv_w.writerow([epoch, global_step, f"{train_loss:.6f}", f"{lr_now:.8f}",
                        f"{val_cer:.6f}", "" if transfer_cer is None else f"{transfer_cer:.6f}",
                        f"{blank_rate:.6f}", f"{wall_s:.1f}"])
        csv_f.flush()

        current = transfer_cer if select_metric == 'transfer_cer' else val_cer
        improved = current < best["metric"]
        if improved:
            best = {"metric": current, "epoch": epoch}
            bad_epochs = 0
            save_ckpt(os.path.join(args.out_dir, "best.pt"), epoch)
            write_meta(best)
        else:
            bad_epochs += 1
        save_ckpt(os.path.join(args.out_dir, "last.pt"), epoch)

        print(f"[epoch {epoch}/{args.epochs}] step={global_step} train_loss={train_loss:.4f} "
              f"lr={lr_now:.2e} val_cer={val_cer:.4f}"
              + (f" transfer_cer={transfer_cer:.4f}" if transfer_cer is not None else "")
              + f" blank_rate={blank_rate:.3f} wall_s={wall_s:.1f}"
              + f" | best {select_metric}={best['metric']:.4f}@{best['epoch']}"
              + ("" if improved else f" (bad {bad_epochs}/{PATIENCE})"))

        if bad_epochs >= PATIENCE:
            print(f"[early-stop] no {select_metric} improvement for {PATIENCE} epochs")
            break

    csv_f.close()
    if best["epoch"] > 0:  # best.pt exists iff at least one epoch completed
        write_meta(best)
    print(f"[done] best {select_metric}={best['metric']:.6f} @ epoch {best['epoch']} | "
          f"artifacts: {args.out_dir}/best.pt, last.pt, train_log.csv, checkpoint_meta.json")
    return 0


def main(argv=None) -> int:
    try:
        args = parse_args(argv)
        if args.selftest:
            return run_selftest()
        return train(args)
    except (MixError, ValueError, OSError) as e:
        print(f"data provenance refused: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
