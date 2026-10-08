# Provenance — vendored OpenOCR files

- **Upstream repo:** https://github.com/Topdu/OpenOCR
- **License:** Apache-2.0 (upstream `LICENSE`, vendored verbatim in this directory)
- **Pinned commit:** `0d522801ec6dc1df852c6b6d4ed6a08f5127ed97` (`main` at fetch time;
  resolved via the GitHub API, commit dated 2026-05-20)
- **Fetch date:** 2026-07-06, via `raw.githubusercontent.com/Topdu/OpenOCR/<sha>/<path>`
- **Why these files:** the SVTRv2 encoder + RCTC decoder named by
  `configs/rec/svtrv2/svtrv2_rctc.yml` (`SVTRv2LNConvTwo33` + `RCTCDecoder`), plus the one
  base module they import (`openrec/modeling/common.py` — the full import closure beyond
  torch/numpy). Wired into training via `rec/svtrv2_model.py` (`--arch svtrv2|svtrv2_small`).

## File list

| vendored file | upstream path (at pinned sha) | sha256 of upstream original | edits |
|---|---|---|---|
| `common.py` | `openrec/modeling/common.py` | `82903551fbbac55d15c4dbedf2a4325a3f89ef0d80d7cc774894d6e87ead3ba1` | none (byte-identical) |
| `svtrv2_lnconv_two33.py` | `openrec/modeling/encoders/svtrv2_lnconv_two33.py` | `cdc0ea032be8a2be1ba7a6a433e5493515f9b98f8937e1123a4bbaa594971dde` | 1 import line (see below) |
| `rctc_decoder.py` | `openrec/modeling/decoders/rctc_decoder.py` | `ce20cd2145f6321c87021b07b67de86f24cdb7ea0a20304c65676352c72d05ac` | 1 import line (see below) |
| `svtrv2_rctc.yml` | `configs/rec/svtrv2/svtrv2_rctc.yml` | `37bf5eec639a3ddee04bdb27724cab04ee3044560ef74afe219bafe21d39c204` | none (byte-identical; reference for the `base` variant kwargs) |
| `svtrv2_tiny_rctc.yml` | `configs/rec/svtrv2/svtrv2_tiny_rctc.yml` | `ca74267bff522150d202aae6b66af1638eb6dff091a5a9a0103628023739c718` | none (byte-identical; structural reference for the `small` variant) |
| `LICENSE` | `LICENSE` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | none (byte-identical) |

## Edits (complete list)

The upstream package layout (`openrec.modeling.*`) is not vendored, so the two intra-repo
imports were rewritten to this flat directory. Each edit is a single line, marked in-file
with `# [greek-page-ocr] adapted:`:

1. `svtrv2_lnconv_two33.py` line 6:
   `from openrec.modeling.common import DropPath, Identity, Mlp` → `from .common import ...`
2. `rctc_decoder.py` line 6:
   `from openrec.modeling.common import Block` → `from .common import Block`

No other byte of any vendored file was changed. To audit: fetch the upstream paths at the
pinned sha, check the sha256s above, and diff against these files — the only diffs must be
the two marked lines.

## Not vendored (deliberately)

Upstream training engine, dataloaders (`RatioDataSetTVResize`/`RatioSampler`), losses,
post-processing, and `openrec/modeling/{__init__,base_recognizer}.py` (registry/builder
indirection): this project trains with its own frozen contracts (`docs/data_contracts.md`)
and its own driver (`train/train.py`). All seam adaptation (1-channel input, 48-px strips,
T = ceil(W/4) contract, log-prob output) lives in `rec/svtrv2_model.py`, never here.
