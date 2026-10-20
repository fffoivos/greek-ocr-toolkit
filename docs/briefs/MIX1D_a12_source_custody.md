# MIX1D: re-source A12 from the wave-2 control's synthetic build; run the A12 cross-check; redeploy (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

The base is MIX1C (`mix1/`, deployed `mix1_pkg/e87b9e8d`; the earlier intermediate `f1384fdb` also exists). Both packages are superseded by this brief and must not be submitted. `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`; `P=$W/greek-page-ocr/out`.

**The finding (lead, read-only):**
- MIX1 binds A12 = `$P/e1_run4/synthetic`: build_info sha `495453433c2efff88a8a0d7d39de32e856d878d815b923dbf3eb9354411bfbff`, codec v1.
- The wave-2 control's v2.1 derivative (`$W/e4_wave2_rel3_20261020/preparation/inventory03/control_synthetic_7/build_info.json`) derives from `$P/e4/wave1b/v2-codec/old_v2/synthetic`: build_info sha `94e899a34929ee82c564c935b21a6659515a30d3fbdddae42366dc0ed71219cc`, codec v2.
- `old_v2` is itself a v2 tag-only derivative of `e1_run4/synthetic`: the same recipe `2f228950…` / `76cef226…`, the same 190,486 / 9,208 / 3,999 rows, with labels, pixels and order unchanged.
- The codec sha matches: `eae613e8eb18fd144314f68ae3b6424fb48dd778a2134fef417b06ac2353c4b6`.
- **The custody contract requires the same source and the same codec sha**, so MIX1 must clone from `old_v2`.

## Do
1. **Re-source A12** to `$P/e4/wave1b/v2-codec/old_v2/synthetic` everywhere it is bound: inputs, text audit, M2 pools, export clone_build, manifests and the real-sample receipt. Keep `e1_run4/synthetic` bound only as the provenance root of the chain.
   - Assert **gt equality across the chain**: for every train/val/reserved row, `line_id`, `gt_nfd`, `gt_nfc` and `label_ids` in `old_v2` equal `e1_run4/synthetic`. Do this inside the export or manifests job, which hashes the big shards. On the login node, check a ≥ 1,000-row sample spanning ≥ 20 shards and record it.
   - The text-exposure audit result (A12: 287 dropped) must then be identical when computed on `old_v2`. Re-run the audit on `old_v2` labels (a small CPU read is fine, as before) and assert equal counts.
2. **E1 stays** cloned directly from `$P/e1_run4/real`; there is no v2 intermediate, and the training lead agrees.
3. **The A12 cross-check, now runnable** (inventory03 is complete). Run the VERIFY `crosscheck-a12` mode against the control's build_info, read-only.
   - Our A12 derivative is only produced by the export job, so the check has two parts.
   - **Pre-export (now):** our bound source build_info sha == the control's `encoding_derivation.source_receipt_sha256`, and our bound codec sha == its `codec_sha256`. It must print `CROSSCHECK_A12_CONTRACT_OK source 94e899a3… codec eae613e8…`.
   - **Post-export:** the job compares our derivative's `shard_inventory` sha with the control's: equal bytes is a bonus, and column-level equality is required otherwise. Put that in the export receipt.
4. Re-run the tests and the real-sample check. The 1,000-row real-crop round trip result from MIX1C stays valid if no real-pool code changed; state this, or re-run it.
5. Regenerate the manifests and deploy to a **new** `$W/scaling_w3/mix1_pkg/<sha8>/`, leaving `e87b9e8d`, `f1384fdb` and the earlier roots as they are. Read every sha back, then run VERIFY package, VERIFY inputs and `crosscheck-a12`.
6. **MIX1.md:**
   - a MIX1D section;
   - the exact coordinator block (manifests job, then export with afterok);
   - **the exact final cross-check line**, for the training lead to cite in the S1 REVIEW_INPUTS.

Write a guarded commit list. Do not run `git add` or `git commit`.

The last line must be exactly:
`MIX1D: done | A12 source old_v2 94e899a3 (chain gt-equal sample <n>) | text audit on old_v2 = 287 dropped (equal) | CROSSCHECK_A12_CONTRACT_OK | package <root> VERIFY package+inputs ok | tests <n> passed | no jobs submitted`
