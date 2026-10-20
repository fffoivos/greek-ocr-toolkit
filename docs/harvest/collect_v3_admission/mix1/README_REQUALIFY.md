# MIX1B requalification boundary

The coordinator text-exposure, census inventory and nine-wave rulings are implemented in `core.py`, `pipeline.py` and `generate.py`. The recorded production manifest entry point hashes all bound inputs before generating any arm. `QUALIFICATION.json` records measured evidence; it does not claim that full production manifests were generated.

`LOADER_CONTRACT.md`, `WAVE2_BINDING.json` and `EXPORT_STATUS.json` record the current wave-2 loader/codec custody and explicit EXPORT stops. No trainer code was changed. The canonical factory real-sample export is read by unchanged wave-2 `train/mix.py`; its temporary directory is removed. This is diagnostic evidence, not clearance of the v1 external-shard or fixed-draw-reader gaps.

Use the exact coordinator commands in `MIX1.md`. Manifest and export are separate CPU stages. The export wrapper and entry point both stop while EXPORT_STATUS is stopped. No allocation or job is submitted by verification, sampling, tests or deployment.

`VERIFY.sh package` fails without all 70 real-sample inputs, current code bindings and a successful 1000-row real export round trip. `VERIFY.sh inputs` additionally requires the exact bound subset receipt and ref output hashes. All files under the older a72c3a44 deployment remain untouched.
