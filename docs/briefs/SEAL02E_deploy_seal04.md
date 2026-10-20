# SEAL02E: deploy the SEAL02D package for seal04 and verify it (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend, no jobs)

ASTRA-CP3 has returned.
- Its only seal finding (HIGH 1) is the dev/test identical-crop collision. SEAL02D (commit 3319576ef) fixes it and was held for CP3. There is no other seal change.
- The coordinator says: deploy now.

## Do
1. Check that the local `seal02/` matches commit 3319576ef: `git status` is clean for every DEPLOY_PATHS entry, and `DEPLOY_SHA256SUMS` verifies. The package sha8 must be `fdaf8ca2`. If it differs, stop and report.
2. Deploy to `$W/benchmark_0.2/pkg/fdaf8ca2/` (`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`).
   - The directory must not already exist. Leave `ac4709c0` and `253921bf` as they are; overwrite nothing.
   - Read every sha back, then run `VERIFY.sh package`.
3. Scratch bind to `$W/benchmark_0.2/verify_scratch/fdaf8ca2.inputs.json` using the new package template and the five real inputs. Read each sha live; the expected values are:
   - final_list `$W/benchmark_0.2/lf1_inputs_v2/final_list.jsonl` `0fa4a1fe747e06dfeb9bdb4e6c1a8f3027140b4b160330c4ce07621a9315a08b`;
   - final_receipt `…/lf1_inputs_v2/finalize.receipt.json` `0001652776fd2e45261081bdeffd67b05749edec5a5abadd4162d3d893be6537`;
   - verdicts `…/lf1_inputs_v2/line_verdicts_merged.jsonl` `a203509cbd8105f4c7aeeba04f2ecc32fcb43662a26af8a87902c12b142d12e9`;
   - w1_receipt `$W/crops4_attempts/crops4_c05_w1_full_01/upload_receipt.json` `8062f8e7254eab958a7a51bf5025f9ed3ebe47d779b9247579db9ab64e29e6c4`;
   - w2_receipt `$W/crops4_attempts/crops4_c05_full_01/upload_receipt.json` `975fd41350fd013782ab3e25c87b628338741cddae5ba081a634f8730afa1ffc`.

   Then run `VERIFY.sh inputs --bindings <scratch> --require-complete`. It must pass. Quote its output.
4. Check read-only that `$W/benchmark_0.2/seal04.inputs.json` and `$W/benchmark_0.2/seal04` do not exist. Do not build, and do not submit.
5. Add a SEAL02E section to `SEAL02.md`:
   - the deploy root and readback;
   - the verbatim VERIFY outputs;
   - **the exact coordinator block** with `CONFIG=$W/benchmark_0.2/seal04.inputs.json`, `OUTPUT=$W/benchmark_0.2/seal04`, root `fdaf8ca2` and the five full shas, in the same form as the seal03 block;
   - what to check after the job:
     - status SEALED, version 0.2, mock false, `bindings_sha256` = CONFIG_SHA;
     - `cross_panel_pixel_duplicates_dropped` has exactly 1 entry (dev `serbia--27b182bf4116728f--s009-l0006`);
     - rows 2,690 = images 2,690;
     - test 2,253, dev 437;
     - dev:font_extremes:small sealed 11, deficit 2;
     - `suite_sha256` re-hashed.

Write a guarded commit list. Do not run `git add` or `git commit`. Do not touch `scaling_w3/`, where another run is working.

The last line must be exactly:
`SEAL02E: done | package <root> VERIFY package ok | inputs --require-complete ok (scratch) | seal04 targets absent | no jobs submitted`
