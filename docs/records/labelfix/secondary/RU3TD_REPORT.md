# RU3T-D — exact-import correction overlay

READY. Issued `artifacts/ru1/ru1_v3_edits.jsonl`, registered in `docs/records/labelfix/lqb/versions.json` as an overlay of `google_raw_v2_import`; marked `ru1_v3_train` superseded, retaining its original artifact and SHA. No network, readers, browser/computer-use, or .git writes were used.

## Parent trace and the misleading inherited-difference claim

RU2T used **`label` in `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`**, SHA256 `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`. `scripts/secondary/ru2t.py` defines SOURCE and `apply_version` reads `r['label']`, replaces decided characters and writes `label`. Its registry parent was `collection_v2_train`, also explicitly `text_field=label`. There is no literal `label_parent` field in the v2/v3 train records: that is a conceptual parent, not a Google/text fallback.

`ru1_v2_train.jsonl` (SHA `b47c113ff926bf73adc9d76bb46d1ad443befbd014ae4c8a22c5d83c55ba40e8`) differs from that import on **48 rows / 55 characters, exclusively ь→ъ**. RU3T takes that file's `label` as its immediate text parent (`ru3t.py: merge_labels`; `ru3t_f4.py: finalize` passes `prior_rows` as both data and prior). Decision offsets still index the original import `label`; the earlier replacements preserve length. `ru1_v3_train.jsonl` (SHA `e23fcab1a47893e3fd4d59d7fc5a398c770dbfb411e327bea6cffd29503907a2`) adds 396 edits on 378 disjoint rows. Cumulatively import→v3 is **426 rows / 451 characters, exclusively ь→ъ**. Every other import label is unchanged. The coordinator's staged import copy is text-identical to the specified original.

**No RU2T/RU3T NFC/NFD, apostrophe, whitespace, or codec transform produced 11,637 differences in those files relative to the import.** That premise conflates a raw label comparison with the factory-label comparison in the bind. `bench/e4_wave1c.py: substitute` encodes the overlay text, then compares its IDs with the existing pool row's `label_ids`. It does not compare raw import strings.

We decoded the frozen local `out/e4/wave1c_reg/pools_projection.json.gz` using `codec/v2.json` and examined every ID in `bind_final/substitution.json`. All 11,951 control texts exactly equal the original import after **v1** NFD/fold/whitespace normalization. Rust `factory/src/codec.rs:146-150` folds U+1FBD `᾽` and U+1FBF `᾿` to ASCII apostrophe and drops U+0384 spacing tonos. In contrast, the overlay encoder (`bench/e4_wave1c.py:106-114`) applies NFD, then preserves the seven added v2 literal atoms before applying other folds, then collapses whitespace. Those additions include `᾽`, `᾿`, and `΄`. Re-encoding unchanged raw text therefore restores those literals against the older factory baseline. NFD is common to both sides; it is not the cause. Whitespace normalization around restored tonos explains the few space-containing insertion spans. No unrelated inherited transform was found.

## Bind classification

The coordinator's 11,637 residual rows, after excluding the 314 new RU3T edit rows:

| Kind | Rows |
|---|---:|
| Apostrophe restoration only | 9,304 |
| Spacing tonos restoration only | 2,224 |
| Both restorations | 66 |
| Inherited RU2T ь→ъ correction | 43 |
| **Total** | **11,637** |

Thus **11,594 are encoding-policy differences** and **43 are intended inherited RU2T edits (50 characters)**. There are 9,370 rows involving apostrophes and 2,290 involving tonos; those overlapping totals must not be added. Alignment spans: ASCII apostrophe→`᾿` 6,078; ASCII apostrophe→`᾽` 3,904; paired apostrophes→`᾽᾽` 4; paired apostrophes→`᾿᾿` 1. Tonos insertion spans: `΄` 2,433; `΄΄` 9; ` ΄΄` 3; `΄΄ ` 2; `΄ ` 1. Span counts are not row counts.

Full bind arithmetic: **314 new rows / 331 new edits + 43 inherited RU2T rows / 50 edits + 11,594 policy-only rows = 11,951 substituted rows**.

## 396 versus 331

396 is new RU3T decision positions relative to v2, not the cumulative v3/import count. Exactly **331 edits on 314 rows were substituted**. The other **65 edits on 64 rows are all explicitly in `bind_final/substitution.json: unmatched.ru1_v3_train`**. No duplicate decision positions, mixed-base rows, or matched-but-unchanged cases account for this gap. This proves unmatched membership; it does not attribute each absent row to an admission exclusion versus original pool absence. The full v3 import overlay includes the 55 RU2T edits too: 451 total. The remaining RU2T population is five unmatched rows / five edits (48−43 and 55−50).

[Exact unmatched RU3T decisions](../../../../artifacts/ru1/ru3td/unmatched_ru3t_edits.jsonl) preserve the 65 witnesses. [Bind comparison ledger](../../../../artifacts/ru1/ru3td/bind_differences.jsonl) preserves raw import, decoded control, encoded overlay and difference spans on every substituted ID.

## Issuance and verification

The sparse file has **680 rows: 426 edited rows, 256 hold rows, with two rows in both groups**. It contains **451 edits (55 RU2T + 396 RU3T)** and **284 hold positions (2 inherited + 282 new)**. There are 254 hold-only rows. Each output record includes exact `label_parent`, edited `label`, full original decision dictionaries with reader/lead evidence, original ledger path and SHA, offset, and status. All 451 offsets and all hold offsets already index the original import correctly; **zero offset remaps were necessary**. Holdings retain their original characters; rows with edits and holds retain their accepted edits and are marked hold.

For every emitted row, changing its listed offsets back reconstructs the import UTF-8 bytes exactly; there are no other text differences. Every omitted row has exactly the import label. Output was read back and checked. The actual `greekocr.labelfix.lqb.load_version` loader resolved the registered overlay to all 214,436 rows with exact parent inheritance. Native Python's installed NumPy has an architecture mismatch; the loader check passed under `arch -x86_64 python3`. No scores or scientific evaluation claims were regenerated.

SHA256: **`4f1a51f5eb80788fb1cdc7a01220c90df028e79711cf0eeec2d0ace2ee42d1d0`**.

[Manifest](../../../../artifacts/ru1/ru1_v3_edits_manifest.json), [SHA file](../../../../artifacts/ru1/ru1_v3_edits.sha256), [receipt](../../../../artifacts/ru1/ru3td/RU3TD_RECEIPT.json), [row verification](../../../../artifacts/ru1/ru3td/row_verification.jsonl), [LQB loader check](../../../../artifacts/ru1/ru3td/lqb_load_validation.json). The original registry snapshot is preserved in `artifacts/ru1/ru3td/versions_before.json`. Reproduce locally with `python3 scripts/secondary/ru3td_bind_probe.py` then `python3 scripts/secondary/ru3td_edits.py`; neither invokes readers or network operations.

## Coordinator comparison

Found `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1c/out/e4/wave1c_reg2/inputs/releases/ru1_v3_edits.jsonl`, SHA256 `5926e4e43ab09d1f0b894d2c1a7a2d79f2c488cc78046b3d3652b2a5b023c17b`. Its 426 row IDs and labels exactly equal this version's edited subset, containing the same 451 corrections. **The files are not identical**: the coordinator file excludes 254 hold-only rows and retains the old record schema; this file includes those holds and full per-edit provenance. Its coordinator registry parent was `ru1_v3_train`; this registration correctly uses `google_raw_v2_import`. No coordinator files were modified.

RU3TD READY: parent used label/import_real_v2_train.jsonl → ru1_v2_train.label; inherited diffs 11637 by kind apostrophe-only 9304, tonos-only 2224, both 66, RU2T 43; edits mine 396 vs bind 331 (65 edits on 64 unmatched rows); ru1_v3_edits rows 680 edits 451 holds 256 sha256 4f1a51f5eb80788fb1cdc7a01220c90df028e79711cf0eeec2d0ace2ee42d1d0; matches coordinator's no
