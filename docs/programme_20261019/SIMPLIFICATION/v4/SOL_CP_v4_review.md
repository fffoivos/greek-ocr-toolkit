# SOL-CP-v4 — Release v4 acceptance

**ACCEPT for wave-2 smoke input, with two MEDIUM quality findings; no BLOCKER or HIGH findings.**

Reviewed firsthand using read-only local inspection and Clariden commands. No files written or jobs submitted.

## Findings

1. **MEDIUM — duplicated breathing in one sampled sf7 overlay.**  
   `lekythos--3bfc4a385d61b883--s001-l0106` changes `στὴν᾿ Αθήνα.` → `στὴν᾿ Ἀθήνα.` The crop shows one breathing before Α; the overlay adds the composed breathing while retaining the detached `᾿`. Found in **1/20** sampled overlays. This affects corrected text; the raw release label remains unchanged.

2. **MEDIUM — residual raw OCR error confirmed.**  
   RELEASE_CHECK example **09**, `gazette_modern--dacf995fd419bebd--s000-l0113`, preserves `Χρξώστες Διάφοροι`; the [crop reads Χρεώστες Διάφοροι](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/out/runner1/SIMPLIFIED/RELEASE_HANDOFF/09.png). Found in **1/5** inspected handoff examples. This is documented and consistent with the raw-label contract. Neither sample establishes a population error rate.

## Cleared items

**Identity and integrity.** Live receipt SHA256 matches exactly:

`dbc99bdc7fd9c770e25880139ef3bd3184392bfe65e1eb2baf89544c8e390f32`

Package is `fde561ca`; bound builder/contract hashes match sol-recut `b083574d4`. All **5/5 release outputs** match receipt sizes and hashes. Census remains completed generation **2**; its readout reports **592,466 rows**, **456,967 ADMIT / 84,754 HOLD / 50,745 DROP**, and **16/16 invariants PASS**, each with zero violations.

**Counts.** Independently summed census strata and counted release rows:

| Parent | Census rows | ADMIT, all splits | HOLD | DROP | Held-out ADMIT | Released train |
|---|---:|---:|---:|---:|---:|---:|
| W1 | 101,098 | 68,578 | 21,728 | 10,792 | 17,956 | 50,622 |
| W2 | 219,381 | 138,665 | 51,971 | 28,745 | 21,341 | 117,324 |
| **Total** | **320,479** | **207,243** | **73,699** | **39,537** | **39,297** | **167,946** |

Thus **207,243 − 39,297 = 167,946**, exactly matching W1/W2 census train ADMIT. Train exclusions comprise **54,413 HOLD + 31,043 DROP**. Additional release exclusions for benchmark keys/pixels, held-out editions and missing crops are each **0**.

Direct v3/v4 membership comparison gives **168,637 → 167,946**, **0 added / 691 removed**: **114 W1 + 577 W2**, all ELSTAT. All **691/691** flip decisions match live census records with **HOLD / polytonic required_evidence_unresolved**; none remains released.

**Labels and overlays.**

- **167,946/167,946** labels match their recorded raw-text hashes; **0** duplicate keys, duplicate row IDs or non-train rows.
- **75/75** sampled rows match census observation `raw_text` and their referenced decision digest.
- **904** unique sf7 overlays: **284 W1 / 620 W2**. All have matching raw parents, valid span composition, registered tool/ledger bindings, and changed text.
- Registry correctly declares sf7 **0.7**, `external_registered_not_applied`, `applied_to_release=false`.
- Inspected **20 overlays, 10 per parent**, using seed `20261021`: **20/20** differ from raw; **19/20** look plausible against their crops, with the finding above.
- Non-sf7 edits file: **0 bytes / 0 rows**.

**Exposure.** Rehashed the suite and both panels against suite `9447f09c…`: **2,253 test + 437 dev = 2,690** unique keys and crop hashes, spanning **199 editions**. Edition mappings agree for **2,690/2,690** rows. Across the entire release, overlaps are **0 keys / 0 row IDs / 0 crop hashes / 0 seal04 editions**; overlap with all **200** SPLIT2 dev/test editions is also **0**.

**Crops.** Recounted **207,243** manifest entries; every released row has matching path/hash identity: **167,946/167,946**, **0 gaps**. Physical sample: **50/50 PNGs**, **25 per parent**, totaling **749,245 bytes**, all present and hash-exact. The bound CROPS4C receipt independently reports **207,243/207,243 byte-exact**, **0 failures / 0 mismatches**.

**Handoff visuals.** Personally inspected examples **01, 03, 06, 09 and 10**. All five local images match live crop hashes. Examples 01 and 06 support the registered accent/breathing changes; 03 agrees with its label; 10 retains the visible continuation and hyphen, with minor edge fragments; 09 has the error above.

The census multi-GB JSONL files were not rescanned or rehashed. Census reconciliation used the bound summary/readout plus indexed sample lookups. No release-level issue found makes v4 unusable for smoke; factory intersection and codec counts remain wave-2 preparation results.

VERDICT: ACCEPT v4 for wave-2 smoke input; two MEDIUM findings logged | BLOCKERS: 0 | HIGH: 0