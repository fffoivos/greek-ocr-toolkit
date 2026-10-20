"""SVTRv2+RCTC reference recognizer (arm R of the ARCH A/B) — wrapper over vendored OpenOCR.

Exposes the exact model interface of train/model.py's compact net so train/train.py,
train/eval_cer.py and the pipeline can swap architectures behind one flag:

  Input : grayscale [B, 1, 48, W], normalized (px/255 - 0.5) / 0.5.
  Output: log-probs [B, T, n_classes] (log_softmax over classes), T = ceil(W/4) exactly.
  Classes: id 0 = CTC blank, ids 1..len(atoms) = codec v1 atoms.

REFERENCES (docs/iteration_2_plan.md §Mechanism):
  Source (verbatim, vendored):
    - Topdu/OpenOCR @ 0d522801ec6dc1df852c6b6d4ed6a08f5127ed97 (Apache-2.0), files
      openrec/modeling/encoders/svtrv2_lnconv_two33.py (SVTRv2LNConvTwo33),
      openrec/modeling/decoders/rctc_decoder.py (RCTCDecoder),
      openrec/modeling/common.py — vendored byte-faithful into rec/openocr_vendored/
      (only the two intra-repo import lines rewritten; see PROVENANCE.md).
    - Paper: Du et al., "SVTRv2: CTC Beats Encoder-Decoder Models in Scene Text
      Recognition", arXiv:2411.15858.
  Taken verbatim (constants):
    - `base` variant kwargs = the Architecture.Encoder section of
      rec/openocr_vendored/svtrv2_rctc.yml, verbatim: dims [128,256,384], depths [6,6,6],
      num_heads [4,8,12], mixer [[Conv x6],[Conv,Conv,FGlobal,Global,Global,Global],
      [Global x6]], local_k [[5,5],[5,5],[-1,-1]], sub_k [[1,1],[2,1],[-1,-1]],
      use_pos_embed False, last_stage False, feat2d True. All remaining constructor
      defaults (qkv_bias True, mlp_ratio 4, drop_path_rate 0.1, eps 1e-6, kernel_sizes 3,
      num_convs [[2x3],[2,2,2,3,3,3],[3x3]]) are upstream defaults, exactly what the yml
      run builds. NOTE (upstream behavior, kept): the yml's `local_k` lands in the
      constructor's **kwargs and is unused — conv mixers use kernel_sizes defaults (3x3);
      we pass it anyway so our construction is the yml's construction.
  Adapted at the seams ONLY (each also in rec/README.md; vendored block code untouched):
    - S1 in_channels=1 (constructor arg; upstream trains RGB): strips are grayscale.
    - S2 height 48 (upstream trains 32): no code change needed — with use_pos_embed=False
      the encoder is input-size-agnostic; H: 48 -POPE/4-> 12 -stage0 sub_k(1,1)-> 12
      -stage1 sub_k(2,1)-> 6 rows into the decoder (upstream: 4). RCTCDecoder pools H by
      char-token attention, so it is H-agnostic by design.
    - S3 T = ceil(W/4) contract: upstream's overall W-stride is exactly 4 (two stride-2
      stem convs; k=3,p=1 conv gives ceil(W/2) per conv -> ceil(W/4); no later W-stride),
      so NO projection/interpolation neck is needed. Verified, not assumed: forward()
      hard-asserts T == ceil(W/4) (and H' == 6). Why odd widths survive upstream's
      POPatchEmbed returning floor-divided sz [H//4, W//4]: stage 0 ends in a Conv mixer,
      so its SubSample2D recomputes sz from the real tensor before any sz-consuming
      module (SubSample1D/Feat2D) runs. The assert guards this config-dependent fact.
    - S4 output contract: vendored RCTCDecoder returns raw logits in train mode but
      F.softmax probs in eval mode (upstream's engine decodes probs). We normalize both
      branches to log-probs: log_softmax(logits) in train; log(probs) in eval (clamped at
      float tiny to avoid log(0) = -inf from fp32 underflow) — mathematically the same
      log_softmax, so the interface is mode-independent.
    - S5 variable-width right-padded batches (upstream: ratio-bucketed, no padding):
      no code change — encoder/decoder are width-agnostic; CTC masks padded timesteps via
      input_lengths (= pre-pad T), same treatment as the compact arm.
  Ours:
    - `small` variant (capacity-controlled R-small vs arm M): upstream's tiny config
      (svtrv2_tiny_rctc.yml: dims [64,128,256], depths [3,6,3], heads [2,4,8]) measures
      5.14M params here — outside the +/-15% window around the compact arm's 3.77M. We
      keep tiny's structure (depths, mixer, sub_k, head_dim 32) and scale ONE knob,
      dims[2] 256->192 (heads[2] 8->6 to keep head_dim 32): dims [64,128,192],
      depths [3,6,3], heads [2,4,6] -> 3,639,894 params @ n_classes=246 (codec v1), which
      is -3.5% of the compact arm's 3,770,678 (window: 3.20M..4.34M). Labeled ours
      (derived), unvalidated until the A/B runs.
    - This wrapper file itself (interface glue + contract asserts). No trained-weight
      compatibility is claimed for `small`; `base` keeps upstream state_dict key names
      under the `encoder.`/`decoder.` prefixes.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from .openocr_vendored.rctc_decoder import RCTCDecoder
    from .openocr_vendored.svtrv2_lnconv_two33 import SVTRv2LNConvTwo33
except ImportError:  # script execution (`python rec/svtrv2_model.py`): no parent package
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from greekocr._vendor.rec.openocr_vendored.rctc_decoder import RCTCDecoder
    from greekocr._vendor.rec.openocr_vendored.svtrv2_lnconv_two33 import SVTRv2LNConvTwo33

STRIP_HEIGHT = 48  # docs/data_contracts.md §2
STRIDE = 4  # frozen contract: T = ceil(W / 4)


def ceil_div(a: int, b: int) -> int:
    return -(-a // b)


# Encoder kwargs per variant. `base` == rec/openocr_vendored/svtrv2_rctc.yml verbatim;
# `small` == svtrv2_tiny_rctc.yml structure with dims[2] 256->192, heads[2] 8->6 (ours,
# derived — see REFERENCES). Everything not listed here is an upstream constructor default.
VARIANTS = {
    "base": dict(
        dims=[128, 256, 384],
        depths=[6, 6, 6],
        num_heads=[4, 8, 12],
        mixer=[
            ["Conv", "Conv", "Conv", "Conv", "Conv", "Conv"],
            ["Conv", "Conv", "FGlobal", "Global", "Global", "Global"],
            ["Global", "Global", "Global", "Global", "Global", "Global"],
        ],
        local_k=[[5, 5], [5, 5], [-1, -1]],  # unused upstream (**kwargs); passed for yml parity
        sub_k=[[1, 1], [2, 1], [-1, -1]],
        use_pos_embed=False,
        last_stage=False,
        feat2d=True,
    ),
    "small": dict(
        dims=[64, 128, 192],
        depths=[3, 6, 3],
        num_heads=[2, 4, 6],
        mixer=[
            ["Conv", "Conv", "Conv"],
            ["Conv", "Conv", "Conv", "FGlobal", "Global", "Global"],
            ["Global", "Global", "Global"],
        ],
        local_k=[[5, 5], [5, 5], [-1, -1]],  # unused upstream (**kwargs); passed for yml parity
        sub_k=[[1, 1], [2, 1], [-1, -1]],
        use_pos_embed=False,
        last_stage=False,
        feat2d=True,
    ),
}


class SVTRv2RCTC(nn.Module):
    """Vendored SVTRv2LNConvTwo33 encoder + RCTCDecoder behind the train/model.py interface."""

    def __init__(self, n_classes: int, variant: str = "base") -> None:
        super().__init__()
        if n_classes < 2:
            raise ValueError(f"n_classes must be >= 2 (blank + atoms), got {n_classes}")
        if variant not in VARIANTS:
            raise ValueError(f"variant must be one of {sorted(VARIANTS)}, got {variant!r}")
        self.n_classes = n_classes
        self.variant = variant
        cfg = VARIANTS[variant]
        # Seam S1: in_channels=1 (grayscale strips); a constructor arg, no vendored-code edit.
        self.encoder = SVTRv2LNConvTwo33(in_channels=1, **cfg)
        # RCTCDecoder(out_channels=n_classes): the CTC class head. Class-id semantics
        # (blank=0, codec atom order) come from OUR data/loss, not from the decoder.
        self.decoder = RCTCDecoder(in_channels=cfg["dims"][-1], out_channels=n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        assert x.dim() == 4 and x.shape[1] == 1, f"expected [B,1,48,W], got {tuple(x.shape)}"
        assert x.shape[2] == STRIP_HEIGHT, f"strip height must be {STRIP_HEIGHT}, got {x.shape[2]}"
        w_in = x.shape[3]
        t_expected = ceil_div(w_in, STRIDE)

        feat = self.encoder(x)  # [B, dims[-1], H'=6, T] (feat2d=True)
        # Seam S3: verify the frozen stride contract on the REAL tensor, every forward.
        assert feat.dim() == 4 and feat.shape[2] == STRIP_HEIGHT // 8 and feat.shape[3] == t_expected, (
            f"stride contract violated: encoder gave {tuple(feat.shape)}, "
            f"expected H'={STRIP_HEIGHT // 8}, T=ceil({w_in}/{STRIDE})={t_expected}"
        )

        out = self.decoder(feat)  # [B, T, n_classes]
        # Seam S4: vendored decoder returns logits in train mode, softmax probs in eval
        # mode; normalize both to log-probs so the interface is mode-independent.
        if self.decoder.training:
            return F.log_softmax(out, dim=-1)
        return out.clamp_min(torch.finfo(out.dtype).tiny).log()


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Build SVTRv2+RCTC variants and print param counts.")
    ap.add_argument("--n-classes", type=int, default=246, help="default 246 = codec v1 (245 atoms + blank)")
    args = ap.parse_args()
    for variant in ("base", "small"):
        m = SVTRv2RCTC(args.n_classes, variant=variant)
        n = count_params(m)
        enc = count_params(m.encoder)
        dec = count_params(m.decoder)
        print(f"[svtrv2:{variant}] n_classes={args.n_classes} params={n:,} ({n / 1e6:.2f}M) "
              f"[encoder {enc:,} + decoder {dec:,}]")
