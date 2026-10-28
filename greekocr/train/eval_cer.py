#!/usr/bin/env python3
"""Standalone CER evaluation for a trained checkpoint on a shard directory.

Usage:
  python3 train/eval_cer.py --ckpt runs/x/best.pt --data-dir out/val --codec codec/v1.json [--limit N]

Prints: overall CER (corpus = total edits / total ref chars), per-script_class CER,
blank_rate (fraction of argmax==blank timesteps over valid, pre-pad timesteps), and the
10 worst lines (gt vs pred). Exits nonzero if the data directory yields no rows.

Scoring is strict NFD-codepoint CER (train/cer.py); ground truth is decoded from
`label_ids` via the codec — text is never re-encoded. `split=='reserved'` rows are
refused; train/val rows are both accepted here (eval directories vary in role).
"""

from __future__ import annotations

import argparse
import heapq
import sys
import unicodedata
from collections import defaultdict

import torch

from greekocr.train.cer import Codec, cer_line, greedy_decode_line, levenshtein, load_codec
from greekocr.train.model import amp_dtype_for, autocast_ctx, build_model, masked_forward


@torch.no_grad()
def evaluate(
    model,
    loader,
    codec: Codec,
    device: torch.device,
    amp_dtype=None,
    track_worst: int = 0,
    per_script: bool = False,
    arm=None,  # S15e(a): {"head","prec_codec","th"} for arms A/C; None/nfd = single-head greedy
    reference_codec=None,  # optional larger literal reference vocabulary, same metric
    line_callback=None,  # optional readout observer; exact scorer inputs, loader order
) -> dict:
    """Greedy-decode CER over a loader. Returns corpus CER, blank_rate, optional extras.

    blank_rate counts only valid timesteps (t < input_length[i]) — padding excluded.
    """
    model.eval()
    total_edits = 0
    total_ref = 0
    n_lines = 0
    blank_steps = 0
    valid_steps = 0
    per: dict = defaultdict(lambda: [0, 0, 0])  # script -> [edits, ref_len, lines]
    worst_heap: list = []  # min-heap of (line_cer, seq, ref, hyp, edits); keeps the k largest
    seq = 0

    head = (arm or {}).get("head", "nfd")
    for batch in loader:
        x = batch["images"].to(device)
        with autocast_ctx(device, amp_dtype):
            out = masked_forward(model, x, batch["input_lengths"])  # WP-A: pad-frame masking (mask-aware arches)
        if head == "two":  # arm C: (base_logprobs, marks_logits); blank_rate over the base head
            base_lp = out[0].to("cpu")
            marks_lg = out[1].to("cpu")
            am = base_lp.argmax(dim=-1).numpy()
        else:  # arm B (nfd) / arm A (precomposed): one head [B, T, C]
            lp_cpu = out.to("cpu")
            am = lp_cpu.argmax(dim=-1).numpy()
        in_lens = batch["input_lengths"].numpy()
        for i in range(am.shape[0]):
            L = int(in_lens[i])
            ids = am[i, :L]
            blank_steps += int((ids == 0).sum())
            valid_steps += L
            if head == "nfd":
                hyp = greedy_decode_line(ids, codec)
            elif head == "precomposed":
                from greekocr.train.heads import decode_precomposed
                hyp = decode_precomposed(lp_cpu[i, :L], arm["prec_codec"])
            else:  # two
                from greekocr.train.heads import decode_two_head
                hyp = decode_two_head(base_lp[i, :L], marks_lg[i, :L], arm["th"])
            ref = (reference_codec or codec).decode(batch["labels"][i])  # gt from label_ids, never re-encoded
            e = levenshtein(ref, hyp)
            if line_callback is not None:
                line_callback(ref, hyp, e)
            total_edits += e
            total_ref += len(ref)
            n_lines += 1
            if per_script:
                s = per[batch["script_class"][i]]
                s[0] += e
                s[1] += len(ref)
                s[2] += 1
            if track_worst > 0:
                item = (e / max(1, len(ref)), seq, ref, hyp, e)
                seq += 1
                if len(worst_heap) < track_worst:
                    heapq.heappush(worst_heap, item)
                else:
                    heapq.heappushpop(worst_heap, item)

    out = {
        "cer": total_edits / max(1, total_ref),
        "edits": total_edits,
        "ref_len": total_ref,
        "n_lines": n_lines,
        "blank_rate": blank_steps / max(1, valid_steps),
    }
    if per_script:
        out["per_script"] = {
            k: {"cer": v[0] / max(1, v[1]), "edits": v[0], "ref_len": v[1], "lines": v[2]}
            for k, v in sorted(per.items())
        }
    if track_worst > 0:
        out["worst"] = sorted(worst_heap, key=lambda t: (-t[0], t[1]))
    return out


def load_checkpoint(ckpt_path: str, codec: Codec, device: torch.device):
    # WP-A ii: SAFE load (no pickle) via ckpt_io -> (state_dict, metadata). A legacy resume-.pt with
    # no .safetensors sibling raises with conversion instructions rather than unpickling.
    from greekocr.train import ckpt_io
    sd, meta = ckpt_io.load_model_weights(ckpt_path)
    if meta.get("codec_version") != codec.version:
        raise ValueError(
            f"checkpoint codec_version {meta.get('codec_version')!r} != codec {codec.version!r}"
        )
    if int(meta.get("n_classes", -1)) != codec.n_classes:
        raise ValueError(f"checkpoint n_classes {meta.get('n_classes')} != codec {codec.n_classes}")
    # arch is stored in the checkpoint since --arch landed; older checkpoints are compact
    model, _ = build_model(n_classes=codec.n_classes, arch=meta.get("arch", "compact"), verbose=True,
                           width_mult=float(meta.get("width_mult", 1.0)))
    model.load_state_dict(sd)
    model.to(device)
    return model, meta


def _display(s: str) -> str:
    """NFC for terminal readability ONLY — scoring above is strict NFD, untouched."""
    return unicodedata.normalize("NFC", s)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ckpt", required=True, help="checkpoint .pt (best.pt/last.pt from train.py)")
    ap.add_argument("--data-dir", required=True, help="directory of shard-*.parquet")
    ap.add_argument("--codec", required=True, help="codec vN JSON (data_contracts §1)")
    ap.add_argument("--limit", type=int, default=None, metavar="N", help="cap rows read (default: all)")
    ap.add_argument("--device", choices=["cuda", "mps", "cpu"], default=None, help="default: auto")
    ap.add_argument("--bs", type=int, default=128, help="eval batch size (default 128)")
    ap.add_argument("--allow-reserved", action="store_true",
                    help="allow split='reserved' (transfer-dev eval only; never for train/val) — S15e(a)")
    args = ap.parse_args(argv)

    if args.device is None:
        args.device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    device = torch.device(args.device)

    codec = load_codec(args.codec)
    from greekocr.train.data import StripDataset, make_loader  # after arg parsing: fast --help

    try:
        ds = StripDataset(
            args.data_dir,
            expected_split=None,  # eval dirs may be train- or val-split rows
            expected_codec_version=codec.version,
            max_label_id=codec.n_classes - 1,
            max_rows=args.limit,
            allow_reserved=args.allow_reserved,  # S15e(a): transfer-dev eval passthrough (opt-in)
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if len(ds) == 0:  # unreachable (StripDataset raises), kept as a belt-and-braces gate
        print(f"ERROR: {args.data_dir}: no rows", file=sys.stderr)
        return 2

    model, _ = load_checkpoint(args.ckpt, codec, device)
    loader, _ = make_loader(ds, batch_size=args.bs, shuffle=False)
    res = evaluate(
        model, loader, codec, device,
        amp_dtype=amp_dtype_for(device), track_worst=10, per_script=True,
    )

    print(f"\ndata_dir     : {args.data_dir}  ({res['n_lines']} lines, {res['ref_len']} ref chars)")
    print(f"overall CER  : {res['cer']:.6f}  ({res['edits']} edits / {res['ref_len']} ref chars)")
    print(f"blank_rate   : {res['blank_rate']:.4f}")
    print("\nper-script_class CER:")
    for k, v in res["per_script"].items():
        print(f"  {k:<16} {v['cer']:.6f}  ({v['edits']:>8} / {v['ref_len']:>8}, {v['lines']} lines)")
    print("\n10 worst lines (per-line CER desc; shown NFC for readability, scored NFD):")
    for rank, (lc, _, ref, hyp, e) in enumerate(res.get("worst", []), 1):
        print(f"  #{rank}  cer={lc:.3f} edits={e} ref_len={len(ref)}")
        print(f"      gt  : {_display(ref)}")
        print(f"      pred: {_display(hyp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
