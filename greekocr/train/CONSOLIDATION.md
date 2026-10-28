# Stage C consolidation (REL0-S2, 28 October 2026)

Source of truth: executed Stage C package, preserved unchanged. The ordinary release path retains packaging/import-only consolidation, with no numerical, preprocessing, decoder or codec edits. Separately, REL0-S2b makes a scoped compatibility change: historical recovery, replay, overlay and s1_selection modes are explicitly unsupported and raise MixError before validation or row access because their sealed adapter dependency closure is absent. This exclusion changes historical-mode behavior; it is not an import-only change. `export.py` is new release tooling, not a change to the trainer. Legacy detector helper is retained separately because Stage C contains no detector implementation.

## File origins and exact changes

### `greekocr/train/cer.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/cer.py`; SHA256 `4ac0bc16fa7380360eb30995184f00753b4394e436a2b3db3ec8fbbdafd5b331`.

Byte-identical; no change.

### `greekocr/train/ckpt_io.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/ckpt_io.py`; SHA256 `671514c94c93df347e15815b9d3d5af6e222412b10ec28d2d028da302b039d6b`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/ckpt_io.py
@@ -91,7 +91,7 @@
         raise RuntimeError(
             f"refusing to pickle a legacy checkpoint on the inference path: {ckpt_path} "
             f"(weights_only load failed: {e}). Convert ONCE in a trusted context: "
-            f"python -c \"from ckpt_io import convert_pt_to_safetensors as c; c('{ckpt_path}')\""
+            f"python -c \"from greekocr.train.ckpt_io import convert_pt_to_safetensors as c; c('{ckpt_path}')\""
         ) from e
     if not isinstance(ck, dict) or "model" not in ck:  # WP-A cert F8: clearer than a bare KeyError
         raise RuntimeError(
```

### `greekocr/train/ctc_health.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/ctc_health.py`; SHA256 `06bfed86a8c98635435176965052f1c3b27bae968285d6e6d787616934427260`.

Byte-identical; no change.

### `greekocr/train/data.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/data.py`; SHA256 `7f145aa9af70727bb54303bda0f9bb92a8b4b613508f1bf4566acc2c27b73ebc`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/data.py
@@ -231,7 +231,7 @@
     a strip's reading (eval preds) is deterministic regardless of batch composition (matches
     pipeline/recognize.py). Applies to eval + future training; frozen S16 preds were produced without
     it (see the WP-A cert F6 masked-eval note)."""
-    from model import DET_PAD_MARGIN  # local import to avoid ordering issues; single source in model.py
+    from greekocr.train.model import DET_PAD_MARGIN  # local import to avoid ordering issues; single source in model.py
     b = len(samples)
     canvas_w = max(s["width"] for s in samples) + DET_PAD_MARGIN
     canvas = np.empty((b, STRIP_HEIGHT, canvas_w), dtype=np.uint8)
```

### `greekocr/train/eval_cer.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/eval_cer.py`; SHA256 `3ee768a4501974085f32b8efd901415557ecfaa547b3471607f1193793785f21`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/eval_cer.py
@@ -23,8 +23,8 @@
 
 import torch
 
-from cer import Codec, cer_line, greedy_decode_line, levenshtein, load_codec
-from model import amp_dtype_for, autocast_ctx, build_model, masked_forward
+from greekocr.train.cer import Codec, cer_line, greedy_decode_line, levenshtein, load_codec
+from greekocr.train.model import amp_dtype_for, autocast_ctx, build_model, masked_forward
 
 
 @torch.no_grad()
@@ -75,10 +75,10 @@
             if head == "nfd":
                 hyp = greedy_decode_line(ids, codec)
             elif head == "precomposed":
-                from heads import decode_precomposed
+                from greekocr.train.heads import decode_precomposed
                 hyp = decode_precomposed(lp_cpu[i, :L], arm["prec_codec"])
             else:  # two
-                from heads import decode_two_head
+                from greekocr.train.heads import decode_two_head
                 hyp = decode_two_head(base_lp[i, :L], marks_lg[i, :L], arm["th"])
             ref = (reference_codec or codec).decode(batch["labels"][i])  # gt from label_ids, never re-encoded
             e = levenshtein(ref, hyp)
@@ -120,7 +120,7 @@
 def load_checkpoint(ckpt_path: str, codec: Codec, device: torch.device):
     # WP-A ii: SAFE load (no pickle) via ckpt_io -> (state_dict, metadata). A legacy resume-.pt with
     # no .safetensors sibling raises with conversion instructions rather than unpickling.
-    import ckpt_io
+    from greekocr.train import ckpt_io
     sd, meta = ckpt_io.load_model_weights(ckpt_path)
     if meta.get("codec_version") != codec.version:
         raise ValueError(
@@ -158,7 +158,7 @@
     device = torch.device(args.device)
 
     codec = load_codec(args.codec)
-    from data import StripDataset, make_loader  # after arg parsing: fast --help
+    from greekocr.train.data import StripDataset, make_loader  # after arg parsing: fast --help
 
     try:
         ds = StripDataset(
```

### `greekocr/train/heads.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/heads.py`; SHA256 `7d7371bf23624f82dc49700c3fdca6702279b6ffa819d6709ab23ba4179d6e05`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/heads.py
@@ -37,8 +37,8 @@
 import torch.nn as nn
 import torch.nn.functional as F
 
-from cer import Codec, collapse_ctc, load_codec  # noqa: F401 (load_codec used by callers)
-from model import ENC_DIM, SVTRv2CTC
+from greekocr.train.cer import Codec, collapse_ctc, load_codec  # noqa: F401 (load_codec used by callers)
+from greekocr.train.model import ENC_DIM, SVTRv2CTC
 
 # S15e(d) — FROZEN P1 arm-C hyperparameters (pinned in docs/prereg_t1.md Changelog 2026-07-08,
 # pre-results). Not tuned per result: λ = marks-BCE weight in two_head_loss; thresh = marks sigmoid
@@ -247,7 +247,7 @@
     if width_mult != 1.0 and (head != "nfd" or arch != "compact"):
         raise ValueError("width_mult requires compact with the NFD CTC head")
     if head == "nfd":
-        from model import build_model
+        from greekocr.train.model import build_model
 
         m, _ = build_model(n_classes=codec.n_classes, arch=arch, verbose=verbose, width_mult=width_mult)
         return m
```

### `greekocr/train/mix.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/mix.py`; SHA256 `9d3cf6e3443e9a98398f20a96733d112451fb47cfb1d06d704ce975a2babfcfe`.

Changes: preserve the legacy manifest repository root; explicitly reject unavailable historical modes (REL0-S2b). Exact line hunks:
```diff
--- sealed Stage C origin
+++ greekocr/train/mix.py
@@ -17,11 +17,30 @@
 import sys
 from collections import Counter
 
-ROOT = Path(__file__).resolve().parents[1]
+ROOT = Path(__file__).resolve().parents[1] / "_vendor"
 
 
 class MixError(ValueError):
     pass
+
+
+# These research adapters are absent from the sealed Stage C payload too.
+HISTORICAL_MODES = {
+    'codec_recovery': 'bench.e4_recovery',
+    'label_versions': 'bench.e4_wave1c',
+    'matched_replay': 'bench.e4_replay',
+    's1_selection': 'bench.s1_scaling',
+}
+SEALED_PACKAGE = 'docs/programme_20261025/TRAIN_FULL_v1/stage_c_package'
+
+
+def _reject_historical_modes(spec):
+    for mode, adapter in HISTORICAL_MODES.items():
+        if mode in spec:
+            raise MixError(
+                f'{mode} ({adapter}): historical mode not included in this release; '
+                f'see sealed package {SEALED_PACKAGE}'
+            )
 
 
 def sha256(path):
@@ -123,6 +142,7 @@
     if role not in ('train', 'val', 'eval', 'transfer', 'reserved', 'test'):
         raise MixError(f'unknown mix role: {role}')
     mix = _object(path)
+    _reject_historical_modes(mix)
     required = {'components', 'seed', 'codec_version', 'created_by', 'notes'}
     allowed = required | {'schema_version', 'matched_replay', 'codec_recovery', 'label_versions', 's1_selection'}
     if required - mix.keys() or mix.keys() - allowed:
@@ -223,48 +243,6 @@
         resolved['components'][i]['build_info_sha256'] = sha256(directory / 'build_info.json')
     if abs(math.fsum(fractions) - 1.0) > 1e-6:
         raise MixError(f'fractions sum to {math.fsum(fractions):.12g}, expected 1 (±1e-6)')
-    if 'codec_recovery' in mix:
-        if 'matched_replay' in mix or mix['codec_version'] != 'v2':
-            raise MixError('codec recovery requires v2 without matched replay')
-        spec = mix['codec_recovery']
-        if not isinstance(spec, dict) or set(spec) != {'path', 'sha256'}:
-            raise MixError('codec_recovery requires path and sha256')
-        resolved['codec_recovery']['path'] = str(_path(path.parent, spec['path'], 'codec_recovery.path'))
-        from bench.e4_recovery import load
-        plan = load(resolved['codec_recovery'])
-        if plan['seed'] != mix['seed'] or len(plan['old_counts']) != len(components):
-            raise MixError('codec recovery component/seed mismatch')
-    if 'matched_replay' in mix:
-        spec = mix['matched_replay']
-        if not isinstance(spec, dict) or set(spec) != {'path', 'sha256'}:
-            raise MixError('matched_replay requires path and sha256')
-        resolved['matched_replay']['path'] = str(_path(path.parent, spec['path'], 'matched_replay.path'))
-        plan = replay_plan(resolved['matched_replay'])
-        if (plan['replay_component'] != len(components)-1 or plan['base_components'] != len(components)-1
-                or plan['seed'] != mix['seed'] or components[-1]['kind'] != 'real'
-                or abs(components[-1]['fraction']-.1) > 1e-9):
-            raise MixError('matched replay component/seed contract mismatch')
-        expected = [c['fraction'] / .8 if c['kind'] == 'real' else c['fraction'] for c in components[:-1]]
-        if plan['base_fractions'] != expected:
-            # Accept only floating point rounding at the .8 inverse.
-            if len(expected) != len(plan['base_fractions']) or any(abs(x-y)>1e-12 for x,y in zip(expected,plan['base_fractions'])):
-                raise MixError('matched replay base fractions mismatch')
-    if 'label_versions' in mix:
-        if role != 'train' or mix['codec_version'] not in ('v2', 'v2.1'):
-            raise MixError('label_versions is a v2/v2.1 train-only overlay')
-        from bench.e4_wave1c import check_overlay
-        spec = copy.deepcopy(mix['label_versions'])
-        for key in ('registry', 'codec'):
-            spec[key] = str(_path(path.parent, spec[key], 'label_versions.' + key))
-        check_overlay(spec)
-        resolved['label_versions'] = spec
-    if 's1_selection' in mix:
-        if role != 'train' or mix['codec_version'] != 'v2.1' or any(k in mix for k in ('matched_replay','codec_recovery','label_versions')):
-            raise MixError('s1_selection requires raw v2.1 train pools')
-        selection = mix['s1_selection']
-        if set(selection) != {'subset','provenance'} or set(selection['subset']) != {'path','sha256','rows'}:
-            raise MixError('invalid s1_selection schema')
-        resolved['s1_selection']['subset']['path'] = str(_path(path.parent, selection['subset']['path'], 's1 subset'))
     return resolved
 
 
@@ -279,15 +257,7 @@
 
 
 def replay_plan(spec):
-    import gzip
-    path = Path(spec['path'])
-    if sha256(path) != spec['sha256']:
-        raise MixError('matched replay draw manifest hash mismatch')
-    with gzip.open(path, 'rt') as f:
-        plan = json.load(f)
-    if plan.get('schema') != 'e4-matched-replay-v1':
-        raise MixError('unsupported matched replay draw schema')
-    return plan
+    _reject_historical_modes({'matched_replay': spec})
 
 
 def build(components, out, *, seed, codec_version, created_by, notes='', repo=ROOT, role='train'):
@@ -323,6 +293,7 @@
 
 def load_rows(mix, split):
     """Load all contract rows for one role. Never silently accept a wrong directory role."""
+    _reject_historical_modes(mix)
     import pyarrow.parquet as pq
     groups = []
     for i, c in enumerate(mix['components']):
@@ -344,13 +315,6 @@
         if c['fraction'] > 0 and not rows:
             raise MixError(f'component {i}: no {split} rows')
         groups.append(rows)
-    if 's1_selection' in mix:
-        if split != 'train': raise MixError('S1 selection is train-only')
-        from bench.s1_scaling import select_rows
-        groups = select_rows(groups, mix['components'], mix['s1_selection'])
-    if 'label_versions' in mix and split == 'train':
-        from bench.e4_wave1c import substitute
-        groups, _ = substitute(groups, mix['components'], mix['label_versions'])
     return groups
 
 
@@ -361,18 +325,9 @@
     permutations when oversampling. Pool membership is redrawn each training epoch.
     """
     if recovery is not None:
-        if replay is not None:raise MixError('cannot combine replay and codec recovery')
-        from bench.e4_recovery import substitute
-        return substitute(groups, fractions, seed, epoch, max_rows, exact_rows, recovery)
+        _reject_historical_modes({'codec_recovery': recovery})
     if replay is not None:
-        from bench.e4_replay import apply_plan
-        plan = replay_plan(replay)
-        if (seed != plan['seed'] or max_rows != plan['epoch_rows'] or not exact_rows
-                or str(epoch) not in plan['epochs'] or len(groups) != plan['base_components']+1):
-            raise MixError('matched replay requires its exact seed, epoch, pool count and row budget')
-        rows, _ = assemble(groups[:-1], plan['base_fractions'], seed, epoch, max_rows, exact_rows=True)
-        rows = apply_plan(rows, groups[-1], plan['epochs'][str(epoch)], plan['replay_component'],plan['scanned_components'])
-        return rows, [sum(r['_component']==i for r in rows) for i in range(len(groups))]
+        _reject_historical_modes({'matched_replay': replay})
     n = sum(len(g) for g, f in zip(groups, fractions) if f > 0)
     if max_rows is not None:
         n = max_rows if exact_rows else min(n, max_rows)
```

### `greekocr/train/mix.schema.json`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/mix.schema.json`; SHA256 `2cbe95808e40cf2f87e13e871784224fe9074656d62feee4952c72e9e4359a80`.

Byte-identical; no change.

### `greekocr/train/model.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/model.py`; SHA256 `70acd681921b6ca07f178ccf1a787ca11113b31cd48501c04317b91870f442bc`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/model.py
@@ -41,7 +41,7 @@
 import torch.nn as nn
 import torch.nn.functional as F
 
-from cer import load_codec
+from greekocr.train.cer import load_codec
 
 STRIP_HEIGHT = 48  # data_contracts §2
 STRIDE = 4  # T = ceil(W / STRIDE) — the frozen stride contract
@@ -297,7 +297,7 @@
     root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
     if root not in sys.path:
         sys.path.insert(0, root)  # train/ scripts run with sys.path[0]=train/; add repo root
-    from rec.svtrv2_model import SVTRv2RCTC
+    from greekocr._vendor.rec.svtrv2_model import SVTRv2RCTC
 
     return SVTRv2RCTC(n_classes, variant=variant)
 
```

### `greekocr/train/s1_segment.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/s1_segment.py`; SHA256 `b0d4bfb0cfa40d1c506fdb130b6b00fa363365f25177f2ebdaa51c9406bb6edc`.

Byte-identical; no change.

### `greekocr/train/s1_timing.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/s1_timing.py`; SHA256 `09d3f726f1eb89e8447ab20bbe544aef03ae710a9ac9f7f8f17f0eac548ceb14`.

Byte-identical; no change.

### `greekocr/train/train.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/train.py`; SHA256 `5fc60b2e703e89ee3070cef73e4271155846b6e62a23104f759b1d3b4bf391eb`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/train.py
@@ -41,11 +41,10 @@
 
 # Keep manifest validation independent of Torch and device initialization.
 from pathlib import Path
-sys.path.insert(0, str(Path(__file__).resolve().parent))
 if __package__:
     from .mix import MixError, validate, load_rows, assemble, provenance
 else:
-    from mix import MixError, validate, load_rows, assemble, provenance
+    from greekocr.train.mix import MixError, validate, load_rows, assemble, provenance
 
 ARCH_CHOICES = ("compact", "a32", "b_a64", "svtrv2", "svtrv2_small")
 HEAD_CHOICES = ("nfd", "precomposed", "two")
@@ -57,11 +56,11 @@
     import numpy as np
     import torch
     import torch.nn as nn
-    import ckpt_io
-    from cer import load_codec
-    from ctc_health import CtcHealth
-    from heads import build_arm
-    from model import (amp_dtype_for, autocast_ctx, build_model, ceil_div, count_params,
+    from greekocr.train import ckpt_io
+    from greekocr.train.cer import load_codec
+    from greekocr.train.ctc_health import CtcHealth
+    from greekocr.train.heads import build_arm
+    from greekocr.train.model import (amp_dtype_for, autocast_ctx, build_model, ceil_div, count_params,
                        masked_forward)
     globals().update({k: v for k, v in locals().items() if not k.startswith("_")})
 
@@ -289,7 +288,7 @@
 def _selftest_head() -> None:
     """P1 head arms (04 §4.4): the heads.py battery (build/forward/decode/loss on a synthetic codec)
     plus a real-dimension forward-shape check on the shipped codec/v1.json."""
-    import heads
+    from greekocr.train import heads
 
     heads._selfcheck()  # arm A + C: build, forward, decode round-trips, arm-C dual loss + backward
     root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
@@ -795,7 +794,7 @@
         raise MixError("--codec version differs from mix codec_version")
     ck = load_resume(args)
     start_epoch = 1  # Donor epoch is untrusted until the complete preflight.
-    from data import ManifestDataset, make_loader
+    from greekocr.train.data import ManifestDataset, make_loader
     keep = {"greek_mono", "greek_poly"} if args.greek_only else None
     groups = {role: load_rows(mix, role) for role in ('train', 'val')
               if role != 'val' or not args.val_mix}
@@ -894,7 +893,7 @@
     # Per-arm training context (S15e(a)): arm A (precomposed) transcodes NFD->NFC precomposed CTC
     # targets; arm C (two) splits NFD->base+marks for two_head_loss; arm B (nfd) uses the batch's NFD
     # targets directly. All decode to NFD for the shared strict scorer.
-    from heads import (build_precomposed_index, build_two_head_codec, nfd_ids_to_base_marks,
+    from greekocr.train.heads import (build_precomposed_index, build_two_head_codec, nfd_ids_to_base_marks,
                        nfd_ids_to_precomposed_ids, two_head_loss)
     arm_prec_codec = arm_prec_index = arm_th = None
     if args.head == "precomposed":
@@ -920,7 +919,7 @@
     print(f"[optim] AdamW wd={args.wd} no_decay_norm_bias={args.no_decay_norm_bias} | "
           f"OneCycleLR pct_start={PCT_START} cycle_momentum={not args.no_cycle_momentum}")
 
-    from eval_cer import evaluate  # shared greedy-decode CER pass
+    from greekocr.train.eval_cer import evaluate  # shared greedy-decode CER pass
 
     build_info = {"mix": {"path": args.mix, "sha256": sha256_file(args.mix)},
                   "data_provenance": str(Path(args.out_dir) / 'data_provenance.json')}
@@ -1040,7 +1039,7 @@
 
     segment = None
     if args.segment:
-        from s1_segment import Segment
+        from greekocr.train.s1_segment import Segment
         segment = Segment(args, sys.modules[__name__], model, opt, sched, receipt)
         if segment.saved:
             saved=segment.saved
@@ -1049,7 +1048,7 @@
             best=saved['best'];bad_epochs=saved['bad_epochs'];receipt=saved['receipt']
     # Read flags in the process that executes the forwards, after segment setup.
     sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
-    from bench.o5_runtime import runtime_binding as execution_binding
+    from greekocr.train.bench.o5_runtime import runtime_binding as execution_binding
     trainer_execution = dict(execution_binding(device.type), ctc_device=loss_device.type,
                              workers=args.workers, pin_memory=args.pin_memory)
     os.makedirs(args.out_dir, exist_ok=True)
@@ -1061,7 +1060,7 @@
     if os.environ.get("S1_RUNTIME_QUALIFICATION") == "1":
         if not args.segment or not os.environ.get("SLURM_JOB_ID"):
             raise MixError("S1 timing requires a segment compute allocation")
-        from s1_timing import RuntimeTiming
+        from greekocr.train.s1_timing import RuntimeTiming
         timing = RuntimeTiming(torch, device, args.out_dir, global_step, invocation_started)
     csv_w = csv.writer(csv_f)
     if csv_new:
@@ -1267,8 +1266,8 @@
             # Keep the standalone script's flat imports: importing train.train here
             # would resolve this same file as a module instead of the namespace.
             _runtime()
-            from bench.e2_models import build_donor
-            import model as model_registry
+            from greekocr._vendor.bench.e2_models import build_donor
+            from greekocr.train import model as model_registry
             path = Path(os.environ['E3_R01_INIT'])
             donor = torch.load(path, map_location='cpu', weights_only=True)
             if (donor.get('state_hash_version') != 2
```

### `greekocr/train/bench/__init__.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/bench/__init__.py`; SHA256 `c89d3e4269708b16b1530e466202aa0412c6cc9cf55773714457d27f4fafee1f`.

Byte-identical; no change.

### `greekocr/train/bench/benchmark_suite.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/bench/benchmark_suite.py`; SHA256 `4abf4f095178a61c4d0c92befe191c5811c235a5ae740d0f414c0e8271297387`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/bench/benchmark_suite.py
@@ -11,8 +11,8 @@
 import json
 from pathlib import Path
 import unicodedata as ud
-from bench.common import read_rows, sha256, write_json
-from bench.score import aggregate, load_sealed
+from greekocr.train.bench.common import read_rows, sha256, write_json
+from greekocr.train.bench.score import aggregate, load_sealed
 
 VERSION = 'ocr-benchmark-suite/0.1'
 
```

### `greekocr/train/bench/common.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/bench/common.py`; SHA256 `44d618076b84f236d5123673efbfbdf5631c13a960bcb5737f3ec0e9e39d5de6`.

Byte-identical; no change.

### `greekocr/train/bench/o5_runtime.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/bench/o5_runtime.py`; SHA256 `54e345b32e031c199ed17e92b683d0f00f032d842b85c9ba7d9332a6e8f4aa84`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/bench/o5_runtime.py
@@ -10,10 +10,7 @@
 def runtime_binding(device):
     import torch
     # The trainer/evaluator use flat imports from train/, including train.py.
-    train_path = str(Path(__file__).resolve().parents[1]/'train')
-    if train_path not in sys.path:
-        sys.path.insert(0, train_path)
-    from model import amp_dtype_for
+    from greekocr.train.model import amp_dtype_for
 
     device = torch.device(device)
     dtype = amp_dtype_for(device)
```

### `greekocr/train/bench/score.py`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/bench/score.py`; SHA256 `0c443959331f0a94c40d3922d15e7f9f80a33622f277db1e24b6de2089ac0770`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/bench/score.py
@@ -12,8 +12,8 @@
 import unicodedata as ud
 from collections import defaultdict
 from pathlib import Path
-from bench.common import read_rows, sha256, write_json, script
-from train.cer import levenshtein
+from greekocr.train.bench.common import read_rows, sha256, write_json, script
+from greekocr.train.cer import levenshtein
 
 METRIC_VERSION='o1-metrics/v1'
 MODES=('nfc_char','nfd_atom','diacritic_insensitive')
```

### `greekocr/train/codec/v2.1.json`
Origin: `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/codec/v2.1.json`; SHA256 `eae613e8eb18fd144314f68ae3b6424fb48dd778a2134fef417b06ac2353c4b6`.

Byte-identical; no change.

### `greekocr/train/detector_common.py`
Origin: `greekocr/_vendor/train/detector_common.py`; SHA256 `0dc9bd99fa2635ade43ce02f018d4d95ae918a42c5219873c37d7e5916089a10`.

Changes: qualify imports so installed modules share one implementation; remove flat-import search-path bootstrap; preserve legacy manifest repository root where applicable. Exact line hunks:
```diff
--- origin
+++ greekocr/train/detector_common.py
@@ -21,7 +21,7 @@
 _HERE = os.path.dirname(os.path.abspath(__file__))
 _ROOT = os.path.dirname(_HERE)
 sys.path.insert(0, os.path.join(_ROOT, "pipeline"))
-from page_degrade import degrade  # noqa: E402
+from greekocr._vendor.pipeline.page_degrade import degrade  # noqa: E402
 
 MEAN = (0.798, 0.785, 0.772)
 STD = (0.264, 0.2749, 0.287)
```

## Compatibility users

Every legacy Python module now aliases the actual `greekocr.train` module object, including private helpers. Existing users therefore resolve to the maintained implementation without out-of-scope caller edits. The schema is a JSON reference. The Docling model and codec modules likewise point to the maintained model/scorer.

- `greekocr/_vendor/pipeline/page_ocr_detector.py:24` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/pipeline/recognize.py:26` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/pipeline/recognize.py:27` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/pipeline/recognize.py:28` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e1_common.py:12` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_reader_parity.py:41` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_reader_parity.py:46` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_reader_parity.py:47` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_reader_parity.py:58` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_reader_parity.py:59` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_reader_parity.py:60` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_reader_parity.py:95` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_reader_parity.py:109` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_reader_parity.py:110` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_bakeoff.py:71` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_models.py:117` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_models.py:118` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_warmstart.py:25` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_warmstart.py:91` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e1_eval.py:11` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e1_eval.py:44` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e1_eval.py:45` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e1_eval.py:46` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e1_eval.py:47` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e1_eval.py:143` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/o5_runtime.py:16` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e2_teachers.py:191` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e1_readout.py:11` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/e1_readout.py:259` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/o4b_models.py:37` → compatibility pointer (caller preserved within scope).
- `greekocr/_vendor/bench/o4b_models.py:49` → compatibility pointer (caller preserved within scope).
- `greekocr/real/importers.py:9` → compatibility pointer (caller preserved within scope).
- `greekocr/real/sources/parliament.py:10` → compatibility pointer (caller preserved within scope).
- `greekocr/labelfix/ctc_align.py:222` → compatibility pointer (caller preserved within scope).
- `greekocr/labelfix/ctc_align.py:223` → compatibility pointer (caller preserved within scope).
- `greekocr/labelfix/ctc_align.py:224` → compatibility pointer (caller preserved within scope).
- `greekocr/labelfix/ctc_align.py:246` → compatibility pointer (caller preserved within scope).
- `greekocr/annotate/__init__.py:8` → compatibility pointer (caller preserved within scope).
- `greekocr/harvest/text_primitives.py:8` → compatibility pointer (caller preserved within scope).
- `greekocr/score/__init__.py:5` → compatibility pointer (caller preserved within scope).
- `greekocr/synth/__init__.py:9` → compatibility pointer (caller preserved within scope).
- `greekocr/ops/receipts.py:6` → compatibility pointer (caller preserved within scope).
- `greekocr/recogniser/api.py:61` → compatibility pointer (caller preserved within scope).
- `greekocr/recogniser/api.py:62` → compatibility pointer (caller preserved within scope).
- `tests/test_data_root.py:102` → compatibility pointer (caller preserved within scope).
- `tests/test_warmstart_readers.py:109` → compatibility pointer (caller preserved within scope).
- `tests/test_warmstart_readers.py:110` → compatibility pointer (caller preserved within scope).
- `tests/test_custody.py:7` → compatibility pointer (caller preserved within scope).
- `tests/test_custody.py:133` → compatibility pointer (caller preserved within scope).
- `tests/test_real_annotate_score.py:12` → compatibility pointer (caller preserved within scope).
- `tests/recogniser/test_api.py:186` → compatibility pointer (caller preserved within scope).

## Other files

- `__init__.py`: new package marker.
- `export.py`: new checkpoint export / release binding implementation.
- `CONSOLIDATION.md`: this mapping.

REL0-S2b explicitly excludes the optional historical modes described below; no adapters are supplied.

## Complete pre-consolidation comparison

`LEGACY_COMPARISON.diff` is the line-level old-vendor → sealed-Stage-C comparison for every matching file, plus old-Docling model → Stage C and old inference/provenance → maintained loader. It was recovered read-only from the base toolkit checkout only after every input SHA matched this checkout's historical origins ledger. No Git command was used. This comparison records substantive Stage C changes; those changes were already executed, not introduced by consolidation. In particular, model/heads add width support, train/mix/eval/checkpoint modules include later executed training paths, and data.py differs by the model import.

| Original path | Verified original SHA256 | Comparison |
|---|---|---|
| `greekocr/_vendor/train/cer.py` | `4ac0bc16fa7380360eb30995184f00753b4394e436a2b3db3ec8fbbdafd5b331` | 0 unified-diff lines |
| `greekocr/_vendor/train/ckpt_io.py` | `c32fe83bab4f7a5440ff54c041aa98243ab4c8d2ecd6539c6ced7081c3f5f101` | 20 unified-diff lines |
| `greekocr/_vendor/train/ctc_health.py` | `06bfed86a8c98635435176965052f1c3b27bae968285d6e6d787616934427260` | 0 unified-diff lines |
| `greekocr/_vendor/train/data.py` | `ba0b037ba89aa687a34267184ffb8d82102670d9cb2aff7445cf9b09047b1213` | 11 unified-diff lines |
| `greekocr/_vendor/train/eval_cer.py` | `82538e37729618a1b20d6288a93a5bcb4fade1baf73108b5c937950b08397418` | 65 unified-diff lines |
| `greekocr/_vendor/train/heads.py` | `22aa92e4081c5070c19c41fec8a6a0fb673fea3137cf65c6fe12f593454a2799` | 37 unified-diff lines |
| `greekocr/_vendor/train/mix.py` | `5c27588383f0ce7277bed25f51ead2ae1489281e1cca498f283e8a5884a0b270` | 219 unified-diff lines |
| `greekocr/_vendor/train/mix.schema.json` | `2e7e066a9550c9217551cf934221273145fcd2c386b9289d9b9f010fda897a3d` | 45 unified-diff lines |
| `greekocr/_vendor/train/model.py` | `811869053e3143e5f0998a99232b0982d42b17b9c9195d5813af67bd82118683` | 119 unified-diff lines |
| `greekocr/_vendor/train/train.py` | `c737986897134ea400f377dc17d0f0f65e3b9945e294ac203003e857ba298546` | 477 unified-diff lines |
| `greekocr/deploy/docling_plugin/recognizer/model.py` | `90bcb3f9c1f1d593062145a5d23582eea862c4e98ab783bd0fd6cedf6adfb8ae` | 156 unified-diff lines |
| `greekocr/deploy/docling_plugin/recognizer/inference.py` | `32029d9142dbf0da37f7fb47d43e7b2a0e6dbaeaee1a941844497e7f6896bc45` | 83 unified-diff lines |
| `greekocr/deploy/docling_plugin/recognizer/VENDORED_FROM.json` | `92070adabc8f05cb9824df0eb6a37797db04f06ef847cf91141f4c1126ee3178` | 95 unified-diff lines |

New authored files have no upstream numerical origin: `export.py` (release format, exact SHA bindings, exact-state checks and tensor readback), `LEGACY_COMPARISON.diff` (generated comparison), `__init__.py` (package marker), and this document. The codec JSON and mix schema originate in Stage C as listed above. REL0-S2b additionally excludes the historical mix modes as documented below; the remaining copied implementations retain the exact import-only changes.

Plugin changes: `recognizer/model.py` and `recognizer/codec.py` lines 1–4 alias maintained modules; inference imports are qualified; constructor gains release-directory dispatch and width config/strict load; release batch preparation delegates to unchanged trainer collate to match integer halo pixels. Legacy float preprocessing is preserved. `options.py` adds optional embedded codec/config pin; `model.py::_get_recognizer` pins release config/weights before dispatch; VENDORED_FROM preserves its complete original attribution under historical_origin. These are serving/export adaptations, not changes to training/preprocessing/greedy-decoder implementations.

Legacy `train.py`, `eval_cer.py`, `mix.py` pointer lines 4–5 also forward module execution to the maintained `main`; import users share the exact module object. Remaining CLI selfchecks should use the maintained `greekocr.train` namespace.

## REL0-S2b live and historical provenance contract

`greekocr/_vendor/origins.json` retains every pre-consolidation record, including
its original absolute source path, source SHA256, vendored SHA256, commit and
logic hash. Superseded records have `record_type: historical`, a canonical-record
SHA256 `historical_id`, and `superseded_by` live paths. They describe historical
bytes, not the compatibility pointers now occupying those paths. Unrelated
records and historical bench exceptions retain their existing contract.

New `record_type: live` records bind current bytes with `vendored_sha256`, cite
this mapping with `consolidation` and `consolidation_sha256`, and link back via
`historical_records`. Their `origin` and `source_sha256` identify either the sealed
Stage C input or this mapping for locally authored serving/pointer/export changes.
The detector helper uses its retained historical identity. This mapping's own
hash is stored only in the ledger to avoid a circular self-hash. Tests pin the
canonical contents of all 1,108 original records and verify both directions of
the historical/live references, all current bytes and sealed source hashes.

The following live paths are covered (including compatibility pointers and
maintained serving adaptations):

- `greekocr/_vendor/train/cer.py`
- `greekocr/_vendor/train/ckpt_io.py`
- `greekocr/_vendor/train/ctc_health.py`
- `greekocr/_vendor/train/data.py`
- `greekocr/_vendor/train/detector_common.py`
- `greekocr/_vendor/train/eval_cer.py`
- `greekocr/_vendor/train/heads.py`
- `greekocr/_vendor/train/mix.py`
- `greekocr/_vendor/train/mix.schema.json`
- `greekocr/_vendor/train/model.py`
- `greekocr/_vendor/train/train.py`
- `greekocr/deploy/docling_plugin/model.py`
- `greekocr/deploy/docling_plugin/options.py`
- `greekocr/deploy/docling_plugin/recognizer/VENDORED_FROM.json`
- `greekocr/deploy/docling_plugin/recognizer/codec.py`
- `greekocr/deploy/docling_plugin/recognizer/inference.py`
- `greekocr/deploy/docling_plugin/recognizer/model.py`
- `greekocr/train/CONSOLIDATION.md`
- `greekocr/train/LEGACY_COMPARISON.diff`
- `greekocr/train/__init__.py`
- `greekocr/train/bench/__init__.py`
- `greekocr/train/bench/benchmark_suite.py`
- `greekocr/train/bench/common.py`
- `greekocr/train/bench/o5_runtime.py`
- `greekocr/train/bench/score.py`
- `greekocr/train/cer.py`
- `greekocr/train/ckpt_io.py`
- `greekocr/train/codec/v2.1.json`
- `greekocr/train/ctc_health.py`
- `greekocr/train/data.py`
- `greekocr/train/detector_common.py`
- `greekocr/train/eval_cer.py`
- `greekocr/train/export.py`
- `greekocr/train/heads.py`
- `greekocr/train/mix.py`
- `greekocr/train/mix.schema.json`
- `greekocr/train/model.py`
- `greekocr/train/s1_segment.py`
- `greekocr/train/s1_timing.py`
- `greekocr/train/train.py`

## REL0-S2b historical modes excluded from this release

`codec_recovery` (`bench.e4_recovery`), `label_versions` (`bench.e4_wave1c`),
`matched_replay` (`bench.e4_replay`) and `s1_selection` (`bench.s1_scaling`) are
optional research overlays/selections whose adapters are absent from the sealed
payload. Metadata validation, row loading and direct recovery/replay assembly
reject them with `MixError`: "historical mode not included in this release; see
sealed package docs/programme_20261025/TRAIN_FULL_v1/stage_c_package". The direct
replay-plan loader rejects the same mode. No external adapter lookup is attempted.
The sealed package is the historical reference, not a claim that it contains
these missing adapters. Re-enabling them requires a separate custody-backed task.

Ordinary no-overlay training, compact inference, decoding and release export are
unchanged. `LEGACY_COMPARISON.diff` remains the historical REL0-S2 comparison;
the mix diff above includes the subsequent REL0-S2b exclusions. The wheel ships
the codec JSON, mix schema, this mapping and the comparison. The comparison is
provenance documentation and is not read by inference, export or training.
