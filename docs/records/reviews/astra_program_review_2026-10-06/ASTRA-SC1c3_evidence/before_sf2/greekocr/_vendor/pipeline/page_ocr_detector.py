"""End-to-end page OCR with the NEURAL detector as the layout stage: detector -> line boxes -> strips ->
recognizer. Times the LAYOUT stage (detector) vs the LINES stage (strip extract + recognizer) separately.

  .venv/bin/python pipeline/page_ocr_detector.py --pages ~/greek_ocr_demo_v3/eval_v5_10pages --out out/detector/ocr_10pages
"""
from __future__ import annotations

import argparse
import glob
import os
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision.transforms import Normalize

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_ROOT, "train"))
from greekocr._vendor.train.detector_common import build_model, MEAN, STD, INPUT, pick_device  # noqa: E402
from strips import extract_strip  # noqa: E402
from recognize import Recognizer  # noqa: E402
from layout_v0 import otsu_threshold  # noqa: E402
import detect_postproc as pp  # noqa: E402

DET_CKPT = "out/detector/gpu_final/best.pt"
REC_CKPT = "out/t1prime_a32_v5/best.pt"
CODEC = "codec/v1.json"


def load_gray(png):
    return np.asarray(Image.open(png).convert("L"), dtype=np.float32) / 255.0


@torch.no_grad()
def _infer(model, gray, dev, size_hw, box_thresh):
    """Run the detector at one input size; return line boxes as (x0,y0,x1,y1,score) in PAGE px.
    docTR returns relative coords for any (even non-square) input, so page px = rel * (W,H)."""
    model.postprocessor.box_thresh = box_thresh
    H, W = gray.shape
    rgb = torch.from_numpy(gray).unsqueeze(0).repeat(3, 1, 1)
    x = F.interpolate(rgb.unsqueeze(0), size=size_hw, mode="bilinear", align_corners=False)[0]
    x = Normalize(MEAN, STD)(x).unsqueeze(0).to(dev)
    preds = model(x, return_preds=True)["preds"][0]["words"]     # (M,5) rel
    return [(float(a) * W, float(b) * H, float(c) * W, float(d) * H, float(s))
            for a, b, c, d, s in preds]


@torch.no_grad()
def detect_lines(model, gray, dev, box_thresh=0.1, *, two_pass=True, ink_gate=True,
                 gutter_suppress=False, dt8_order=True, return_debug=False):
    """Return line boxes (x0,y0,x1,y1) in page pixels, reading-ordered.

    Phase-0 inference pipeline (all model-free post-processing on the frozen detector):
      - gutter_suppress: lift dark vertical bands to paper BEFORE inference (I8; W4 §2D).
      - two_pass:        pass 1 @ 1024x1024 stretch, estimate line pitch, pass 2 aspect-preserving
                         at a pitch-matched scale, fuse both with containment+IoU NMS (W3 §2.1).
      - ink_gate:        drop phantom boxes with near-zero ink (W4 §2A).
      - dt8_order:       multi-column pages -> ink-snap -> column-band blocks -> XY-Cut++
                         (num_lines) -> within-block emit; single-column -> legacy (y,x) sort
                         (byte-identical); disabled -> legacy (y,x) sort (W4 §2B).

    Every stage is behind a flag; disabling all of them (two_pass=False, ink_gate=False,
    gutter_suppress=False, dt8_order=False) reproduces the original single-pass behaviour except
    box_thresh is now wired (was a dead param). Set return_debug=True to get the stage breakdown.
    """
    dbg = {}
    if gutter_suppress:
        gray, n_g = pp.suppress_gutter(gray)
        dbg["gutter_cols_lifted"] = n_g
    H, W = gray.shape
    thr = otsu_threshold(gray)

    boxes = _infer(model, gray, dev, (INPUT, INPUT), box_thresh)   # pass 1 (page px + score)
    dbg["pass1_raw"] = len(boxes)
    pitch = n_wide = None
    if two_pass:
        pitch, n_wide = pp.estimate_pitch(boxes, W)
        hw2 = pp.pass2_input_hw(H, W, pitch) if pitch else None
        dbg["pitch"] = pitch; dbg["pass2_hw"] = hw2
        if hw2 is not None:
            boxes2 = _infer(model, gray, dev, hw2, box_thresh)      # pitch-matched primary
            dbg["pass2_raw"] = len(boxes2)
            boxes = pp.fuse_two_pass(boxes2, boxes)                 # pass2 primary, pass1 backfill
        else:
            boxes = pp.fuse_boxes(boxes)                            # dedup the single pass anyway
    else:
        # legacy width/height fragment filter (rel: w>3%W, h>0.6%H) for the single-pass baseline
        boxes = [b for b in boxes if (b[2] - b[0]) > 0.03 * W and (b[3] - b[1]) > 0.006 * H]
    dbg["fused"] = len(boxes)

    if ink_gate:
        boxes, dropped = pp.ink_gate(boxes, gray, thr)
        dbg["phantoms_removed"] = len(dropped)

    xyxy = [tuple(int(round(v)) for v in b[:4]) for b in boxes]
    if dt8_order:
        perm = pp.reading_order(xyxy, gray, thr)
    else:
        perm = sorted(range(len(xyxy)), key=lambda i: (xyxy[i][1], xyxy[i][0]))
    ordered = [xyxy[i] for i in perm]
    dbg["final"] = len(ordered)
    if return_debug:
        return ordered, dbg
    return ordered


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="~/greek_ocr_demo_v3/eval_v5_10pages")
    ap.add_argument("--out", default="out/detector/ocr_10pages")
    ap.add_argument("--device", default="")
    ap.add_argument("--box-thresh", type=float, default=0.1)
    ap.add_argument("--single-pass", action="store_true",
                    help="legacy single-pass detect (disables two-pass fuse, ink-gate, DT8, gutter)")
    ap.add_argument("--no-two-pass", action="store_true", help="disable pitch-adaptive pass 2 + fuse")
    ap.add_argument("--no-ink-gate", action="store_true", help="disable the phantom ink-gate")
    ap.add_argument("--no-dt8", action="store_true", help="disable DT8-lite order (use legacy y,x sort)")
    ap.add_argument("--gutter", action="store_true",
                    help="opt in to I8 gutter suppression (default off: measured net-neutral on this suite)")
    args = ap.parse_args()

    det_cfg = dict(
        box_thresh=args.box_thresh,
        two_pass=not (args.single_pass or args.no_two_pass),
        ink_gate=not (args.single_pass or args.no_ink_gate),
        gutter_suppress=(args.gutter and not args.single_pass),
        dt8_order=not (args.single_pass or args.no_dt8),
    )

    dev = pick_device(args.device)
    outdir = os.path.join(_ROOT, args.out) if not os.path.isabs(args.out) else args.out
    os.makedirs(outdir, exist_ok=True)

    det = build_model("db_mobilenet_v3_large", os.path.join(_ROOT, DET_CKPT), dev)
    det.eval()
    rec = Recognizer(os.path.join(_ROOT, REC_CKPT), os.path.join(_ROOT, CODEC),
                     device=("mps" if dev.type == "mps" else "cpu"))

    page_dirs = sorted(glob.glob(os.path.join(os.path.expanduser(args.pages), "*/")))
    pages = [(os.path.basename(d.rstrip("/")), os.path.join(d, "page.png")) for d in page_dirs]
    pages = [(n, p) for n, p in pages if os.path.exists(p)]

    # warmup (first MPS call compiles kernels — don't count it in the timings)
    g0 = load_gray(pages[0][1]); detect_lines(det, g0, dev, **det_cfg)
    rec.recognize([np.zeros((48, 128), np.float32)])

    print(f"device={dev}  detector={DET_CKPT}  recognizer={REC_CKPT}")
    print(f"detect cfg: {det_cfg}\n")
    hdr = f"{'page':22s} {'lines':>5s} {'layout_s':>9s} {'lines_s':>8s} {'total_s':>8s} {'ms/line':>8s}"
    print(hdr); print("-" * len(hdr))
    tot_layout = tot_lines = tot_n = 0.0
    for name, png in pages:
        gray = load_gray(png)
        t0 = time.perf_counter()
        boxes = detect_lines(det, gray, dev, **det_cfg)
        t_layout = time.perf_counter() - t0

        t0 = time.perf_counter()
        strips, keep = [], []
        for b in boxes:
            s = extract_strip(gray, b)
            if s is not None:
                strips.append(s); keep.append(b)
        texts = rec.recognize(strips) if strips else []
        t_lines = time.perf_counter() - t0

        n = len(strips)
        lines_out = [t for t, c in texts]
        open(os.path.join(outdir, f"{name}.txt"), "w").write("\n".join(lines_out))
        mspl = 1000 * t_lines / n if n else 0
        print(f"{name:22s} {n:5d} {t_layout:9.3f} {t_lines:8.3f} {t_layout+t_lines:8.3f} {mspl:8.1f}")
        tot_layout += t_layout; tot_lines += t_lines; tot_n += n

    print("-" * len(hdr))
    print(f"{'TOTAL':22s} {int(tot_n):5d} {tot_layout:9.3f} {tot_lines:8.3f} {tot_layout+tot_lines:8.3f}")
    print(f"\nper-page avg: layout {tot_layout/len(pages):.3f}s  lines {tot_lines/len(pages):.3f}s")
    print(f"layout share of total: {100*tot_layout/(tot_layout+tot_lines):.0f}%  |  text written to {outdir}/")


if __name__ == "__main__":
    main()
