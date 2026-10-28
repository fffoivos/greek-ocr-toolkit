# Export and real-weight Docling parity — step 6, coordinator on Clariden

REL0-S2 only runs tiny fixtures on the Mac. These are prepared commands, not an executed real-weight result. No SSH, scheduler submission, Hub download/upload or Git command is part of this handoff.

## Release directory contract

Each width has its own directory:

```
compact-w1/                  # similarly compact-w1.5/, compact-w2/
  model.safetensors          # original fp32 tensors, unchanged keys/shapes/values
  config.json                # exact bytes SHA-bound in safetensors metadata
  codec.json                 # byte-identical v2.1, SHA-bound in config and metadata
  MANIFEST.json              # path/bytes/SHA256 of all three files + export input custody
```

Config: `arch=compact`, `width_mult=1.0|1.5|2.0`, `head=nfd`, `n_classes=266`, `input_height=48`, `codec_version=v2.1`, `codec_sha256=eae613e8eb18fd144314f68ae3b6424fb48dd778a2134fef417b06ac2353c4b6`, `normalisation={mean:0.5,std:0.5,padding:own-background-right-halo,pad_margin:128}`, `decode={method:greedy_ctc,internal:NFD,output:NFC}`. The loader validates every field and strict state keys/shapes. Neither weights nor codec ordering is converted. The manifest is an integrity inventory, not a signature; pin the final export hashes in MODELS.json and in the consumer options.

`Recognizer(release_directory)` loads via `greekocr.train.export.load_release`. Actual Docling engine:

```python
from pathlib import Path
from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
options = GlossapiOcrOptions(
    checkpoint=Path('/release/compact-w1.5'), replace_policy='all',
    # Fill from the verified final export; both optional external pins bind it:
    checkpoint_sha256=WEIGHTS_SHA256, config_sha256=CONFIG_SHA256,
)
```

Legacy file checkpoints plus an explicit codec remain supported. For release directories the codec is read from the directory. Release recognition reconstructs uint8 crop pixels and uses the trainer collate function, including its integer-rounded median halo. Legacy serving keeps its historical float-median behavior. Page-to-strip geometry is outside this loading gate: parity uses the **stored trainer PNGs**, with no polarity/resize/Docling page extraction.

## Resolve exact selected inputs first

Read each terminal COMPLETE/selection receipt, PLAN, config, CLAIM/RUN_BINDING and checkpoint SHA. `MODELS.json` contains verified local source identities, not final remote checkpoint readback. Use only:

| Width | Attempt | Trial | Physical run config / output name |
|---|---|---|---|
| ×1 | full-v1-014-w1-h14 | h14 | `full/configs/w1-full.json`, `full/runs/w1-full`; dashboard alias w1h14-full |
| ×1.5 | full-v1-013-stage-c-sel | h14 | `full/configs/w1.5-full.json`, `full/runs/w1.5-full` |
| ×2 | full-v1-013-stage-c-sel | h04 | `full/configs/w2-full.json`, `full/runs/w2-full` |

Do not use attempt013's retired ×1/h13. ×1 final completion is not asserted in the local 28 October ledger. Bind each **selected** best.pt to its dev-selection step, and select the corresponding stored dev prediction files (not simply the final step). Preserve seal04 diagnostic/exposure qualifications. Test predictions/scores are report-only.

## Export each selected best.pt

With the existing credential-free training environment and the reviewed release checkout deployed/verified, set `REL0_RELEASE_ROOT` to a **fresh** output root and `REL0_TRAIN_ROOT` to the existing `…/greek-ocr-e3/train_full`. No installation or compute launch is implied:

```sh
python -m greekocr.train.export \
  --checkpoint "$REL0_TRAIN_ROOT/attempts/full-v1-014-w1-h14/full/runs/w1-full/best.pt" \
  --run-config "$REL0_TRAIN_ROOT/attempts/full-v1-014-w1-h14/full/configs/w1-full.json" \
  --codec "$REL0_TRAIN_ROOT/pkg/e808f6ffe1363bd0/vendor/codec/v2.1.json" \
  --output "$REL0_RELEASE_ROOT/compact-w1" --trusted-checkpoint
python -m greekocr.train.export \
  --checkpoint "$REL0_TRAIN_ROOT/attempts/full-v1-013-stage-c-sel/full/runs/w1.5-full/best.pt" \
  --run-config "$REL0_TRAIN_ROOT/attempts/full-v1-013-stage-c-sel/full/configs/w1.5-full.json" \
  --codec "$REL0_TRAIN_ROOT/pkg/7e8a497f21527b90/vendor/codec/v2.1.json" \
  --output "$REL0_RELEASE_ROOT/compact-w1.5" --trusted-checkpoint
python -m greekocr.train.export \
  --checkpoint "$REL0_TRAIN_ROOT/attempts/full-v1-013-stage-c-sel/full/runs/w2-full/best.pt" \
  --run-config "$REL0_TRAIN_ROOT/attempts/full-v1-013-stage-c-sel/full/configs/w2-full.json" \
  --codec "$REL0_TRAIN_ROOT/pkg/7e8a497f21527b90/vendor/codec/v2.1.json" \
  --output "$REL0_RELEASE_ROOT/compact-w2" --trusted-checkpoint
```

`--trusted-checkpoint` explicitly authorizes pickle reading of **our own-custody** resume .pt during export only. Inference uses safe tensors. Export does not resolve a safetensors sibling or cast tensors; it reads the specified .pt and compares every exported tensor on readback.

## Gate the final artifacts through the actual recognizer

From the reviewed checkout root (module imports do not depend on pytest conftest), run both `seal04_dev` and `harvest_dev`, for **all three widths**, using the selected checkpoint's stored `step-<step>-<panel>.predictions.jsonl`. Take its expected SHA from the corresponding selected eval receipt's `prediction_files`, never a convenient unbound copy. Run on Clariden, in a suitably allocated **CPU** job under the existing job rules; do not run this population check on the Mac.

```sh
python -B -m scripts.release_v0_export.verify_dev \
  --release "$REL0_RELEASE_ROOT/compact-w1.5" \
  --runtime "$REL0_TRAIN_ROOT/attempts/full-v1-005-genn/data/prepared/runtime.json" \
  --runtime-sha256 21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4 \
  --panel seal04_dev --predictions "$REL0_SELECTED_DEV_PREDICTIONS" \
  --predictions-sha256 "$REL0_SELECTED_DEV_PREDICTIONS_SHA256" \
  --output "$REL0_RELEASE_ROOT/compact-w1.5/seal04_dev-parity.json"
```

Repeat for ×1 and ×2 and harvest_dev, with each selected file/pin. The script checks exact pool files/row IDs, uses the unchanged `ManifestDataset` and width-bucket `make_loader(bs=64,shuffle=False)`, requires identical trainer/plugin fp32 logits, compares their greedy outputs and the stored dev hypotheses in NFD, and writes a PASS/FAIL receipt. Docling's own recognizer returns NFC. Config/codec/model byte pins are revalidated on every load.

**Precision caveat to resolve with the real artifacts:** the sealed `full_hook.py::evaluate_panel` uses `autocast_ctx(device, amp_dtype_for(device))` on the training device before converting logits to fp32 CPU. Stored GPU predictions may therefore reflect bfloat16 AMP, while this acceptance run deliberately uses fp32. Any differing hypotheses are a failed gate to investigate and record, not permission to change training, choose convenient examples, use test data, or relabel an fp32/AMP mismatch as parity. Preserve the stored prediction provenance and obtain the coordinator's disposition at step 6.

Archive command/config/runtime/prediction/export/receipt SHAs and fill final MODELS fields. Publish only after all three final artifact directories pass; later upload must preserve exactly these bytes and be read back at its pinned HF commit. This is a bounded artifact-load check; the owner's full segmentation/PDF/Docling/glossAPI phase follows separately.
