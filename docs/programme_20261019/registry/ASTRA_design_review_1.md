# ASTRA — line registry design review — `6c8bf9558`

**Verdict: the design serves both requested uses, but the Clariden build is on hold until its source snapshot is staged and verified.**

Reviewed the requested commit; the live checkout is newer, but its design document is byte-identical. Read-only review throughout: no files written, transfers, submissions, or background jobs.

**Findings, most severe first**

1. **HIGH — the complete source join is not yet available on Clariden.**  
   The [preparation gap](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/registry/LINE_REGISTRY_DESIGN.md:97) remains real. The W mirror contains cached page images but lacks the expected page-record and raw-response directories. Older row records and manifests exist remotely, but the sampled legacy page image and expected Google response tree are absent. No complete alternative snapshot was identified in the inspected locations.

   All three sampled keys resolve uniquely in the remote census, with `split=train`, `disposition=ADMIT`, and empty reasons:

   | Parent | Row ID | Google index / envelope | Verification |
   |---|---|---|---|
   | `collect-v3-W1-20261018-0524` | `bsb_poly1850--027215cc6d2a7e8a--s000-l0001` | 0 / `[786,158,839,188]` | Remote page and crop hashes match; local raw response confirms polygon. |
   | `collect-v3-W2-20261018-0524` | `bsb_poly1850--91657e0569fe07c8--s014-l0001` | 0 / `[171,78,227,110]` | Remote page and crop hashes match; local raw response confirms polygon. |
   | `collection-v2-train` | `66112e132fd96ac8e30e5328-p000016-l0004` | 3 / `[693,151,1334,197]` | Remote `round1/records_all.jsonl`, line 516, supplies geometry and page hash; local page and response confirm both. |

   The join model is demonstrated across these three parents. **The requested end-to-end Clariden check is not passed**, because its final source objects are missing. Stage or locate a receipted snapshot, then repeat these joins entirely remotely before the build. Resolve crops through CROPS4C custody: the sampled W census `crop_path` values are stale, while the corresponding `collection_w{1,2}_originals` files exist and match.

2. **MEDIUM — distinguish stored response hashes from reconstructed original hashes.**  
   The legacy sample initially appeared inconsistent: its retained response hashes to `a768ce3f…`, whereas its receipt and historical inventory require `37dd6fab…`. The response explicitly records removal of embedded image content. Restoring that content from the retained PNG **in memory**, removing the stripping marker, and applying the original canonical serialization reproduced the exact receipt hash and **2,123,357 bytes**.

   This clears the suspected provenance failure. The importer must retain the stored-object hash, original-response hash, and reconstruction method separately. Archive handling alone does not cover this representation.

3. **MEDIUM — two feature definitions need tightening.**  
   The [feature contract](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/registry/LINE_REGISTRY_DESIGN.md:140) adequately defines NFC lengths, percentage denominators, bucket precedence, empty values, capitals, and polytonic marks. However:

   - Script counting is codec/NFD/name-based, **not Unicode-block counting**. Name that method accurately.
   - The referenced [script helper](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/greekocr/harvest/text_primitives.py:13) collapses every non-Greek/Latin/Cyrillic script to `other`. Hebrew plus Arabic therefore cannot satisfy the promised “named other scripts” mixed-script detection through that helper alone.
   - The language heuristic needs an explicit tie/mixed rule; heuristic confidence should remain null unless defined.

   These are bounded implementation clarifications, not reasons to redesign the feature system.

4. **MEDIUM — bind the toolkit hook to its actual export boundary and retain per-page outcomes.**  
   Existing toolkit JSON is `page`, `image_size`, `unit="line"`, and `items[].polygon`, with other item provenance. Its [serializer](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/prototypes/fast_lines/shared/review.py:35) removes discounted items and clips polygons to the page. The comparison adapter should explicitly consume that deployment output; internal pre-export candidates describe a different box set.

   Specify where `(run_id,page_id,status,box_count,result_hash/locator)` lives—a small relation or retained manifest suffices. Otherwise zero detections, failure, and an unprocessed page cannot reliably supply comparison denominators. Preserve emitted item order separately from the geometric top-to-bottom index. Close this before toolkit import; it need not delay the initial Google registry.

**Cleared items**

- **Schema and scope:** four core tables plus the proposed identity, crop, membership, and lineage relations are reasonable for the two uses. Composite row keys, page aliases, raw versus derived boxes, and multiple contributors address actual source differences.
- **Status and labels:** ADMIT→used, HOLD→held, DROP→dropped is explicit; “used” is correctly scoped separately from release membership or actual training consumption. Preserve complete reason objects verbatim. Remote examples include `correction_unresolved` with tool/status fields and `heldout_crop_identity`; reducing these to a newly invented reason would lose evidence. Raw-field precedence matches the existing source adapter; census corrections and v4 overlays remain distinct.
- **Comparison capability:** reading order, complete page box sets, canonical coordinates, polygon IoU, coverage, offsets, size differences, and split/merge graphs are covered. The three proposed analyses are sufficient. New segments remain candidates requiring new crop/label identities.
- **Counts:** freshly counted **167,946** v4 records and **207,243** CROPS4C records. The live census summary reconciles by parent/disposition to **592,466**; its hash matches the design. This was not a fresh scan of the entire 11 GB decision stream.
- **Builder and acceptance:** one bounded CPU job, disk-backed joins, deterministic page batches, checksum-bound resume, logical-hash resume validation, and atomic publication are suitable. Exact key reconciliation, every-used-row→one-primary-box→one-page, and independent feature recomputation on 1,000 rows are sufficient for this scope.
- **Costs:** the estimates are plausible planning allowances, not measured Clariden throughput. The main resource risk is storing full decision JSON in the temporary join: that stream alone exceeds the proposed 10 GB scratch budget. Project needed columns and locators, and measure the first batch.

**Cuts**

Keep membership/contributor arrays as views over their authoritative relations rather than separately maintained copies. Defer actual-training-consumption tracking and language inference beyond provider metadata or a simple defined script tag. Neither requested use requires a new decision pipeline or a broader analytics framework.

**Open-item disposition**

Before the build: close the HIGH source-staging gap, pin the selected source manifest and representation adapters, and demonstrate the three complete remote joins.

The build can establish global page/raw-box counts, full join coverage, alias reconciliation, manifest hashes, and measured storage/time. It can also reconcile the seven-page Vouli and four-entry Round1 discrepancies. Unresolved discrepancies must remain explicit; any that leave a used row without its required box/page prevent publication as complete.

VERDICT: Design suitable; hold the build until source staging and complete Clariden joins are verified | BLOCKERS: 0 | HIGH: 1