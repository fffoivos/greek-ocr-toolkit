# RUNNER4 — Phase 1 Mac source package

22 October 2026. **HF PHASE 1 PACKAGED** locally; no HF repository creation/upload, bulk network transfer, production census/feature build, cluster job, token retrieval or git commit.

Actual package: **`/private/tmp/hf-staging/greek-ocr-lines/`**. Requested durable destination **`~/Projects/hf-staging/greek-ocr-lines/`** is outside this session's writable roots and is still unpopulated. The package and its adjacent resume receipts require later local relocation; the exact unexecuted `mv` commands are in [NEXT_SUBMIT.sh](../../../out/runner4/NEXT_SUBMIT.sh). No extra payload copy is needed for that same-volume move. Temporary scratch is not durable custody.

## Sizes, counts and byte custody

**40,711,310,115 bytes = 40.71131 GB**, **110 files**. Of those, **91 data shards** carry images, Google objects, source metadata and raw boxes; 17 small indexes/outcomes/source-pin files plus the final manifest/checksum list complete the package. Every artifact is below the owner's 1,000,000,000-byte cap; the largest is **511,979,520 bytes**. Shard target: 512,000,000 bytes.

| Part | Selected objects / rows | Stored bytes | Shards |
| --- | ---: | ---: | ---: |
| Legacy original PNGs | 8,574 | 22,247,716,474 | 46 Parquet |
| W original JPEG cache | 5,389 | 4,455,421,261 | 9 Parquet |
| Auxiliary composites | 18 | 3,367,642 | 1 Parquet |
| Legacy + W Google source objects | 13,099 + 4,612 | 12,079,575,040 | 24 TAR (13 + 11) |
| Page/state/legacy/source/assignment metadata | 10,923 | 1,768,161,280 | 9 TAR |
| Imported raw Google line boxes | 737,178 | 135,040,502 | 2 Parquet |
| Indexes, outcomes, pinned inventories | 17 files | 21,990,763 | small support files |
| Final manifest and checksum list | 2 files | 37,153 | small support files |

Embedded image payloads preserve **26,701,562,861 original bytes**; stored Google/metadata TAR members preserve **13,826,824,065 original bytes**. The combined selected input is **42,615 files / 40,528,386,926 bytes**. Eight legacy raw-row JSONLs from the wider selection are intentionally not repackaged: they are the already resident Clariden parent inputs for Phase 2. No source original was changed, deleted or re-encoded. There are **13,981 physical image locators / 13,972 distinct image hashes**; aliases are retained without merging edition/split identities.

Google's 17,711 selected objects comprise **11,154 response payloads, 6,542 receipt sidecars and 15 recorded request errors**. Outcomes: **11,095 nonempty pages + 59 zero-detection pages**. The raw import has **390,470 legacy + 346,708 W boxes**. All 6,542 receipt locators resolve to packaged payload objects, including both `.json.dedup.gz` and Wikisource `.json.gz` forms. Provider original-response hash claims match their resolved response bindings. Stored representation hashes and original/reconstructed hashes remain different fields; no global original-response reconstruction is claimed.

The manifest uses only relative payload locators. `pages/pages.parquet` is the Phase 1 physical-image index, not the final census logical-page table. W observations/rights and exact source page records are retained separately; final book/edition/split/row joins use the resident parents and archived metadata. All source types, including Anemi, use the same packaging; licence declarations are retained and never gate membership.

## Readback and three joins

[HF_PHASE1_VALIDATION.json](../../../out/runner4/HF_PHASE1_VALIDATION.json) binds the complete package manifest, validator, fresh remote witness and legacy representation receipt. The validator read back **all 108 listed artifacts**, checked their closed sizes/SHA256s and the manifest/checksum inventory, and rehashed **every embedded image and all 28,634 TAR source members**. Zero payload/checksum mismatches; zero duplicate imported box IDs; zero boxes without a retained raster-hash match. Independent full readback plus three joins took **58.92 seconds**.

The read-only Clariden query ran on **clariden-ln004**, using exactly three indexed generation-2 observations/decisions, unchanged CURRENT and the existing crop bytes. No page/response bulk data was transferred from the Mac. The subsequent join validator reads only the portable package and these small witnesses, not original Mac payload paths.

| Witness | Result |
| --- | --- |
| W1 `bsb_poly1850--027215cc6d2a7e8a--s000-l0001` | 1 row → 1 retained raw Google box → 1 packaged raster; text, polygon envelope, dimensions, response/page hashes and remote crop hash agree |
| W2 `bsb_poly1850--91657e0569fe07c8--s014-l0001` | Same checks pass |
| Legacy `66112e132fd96ac8e30e5328-p000016-l0004` | Same checks pass via the exact keyed original harvest record (record 516); census page-image hash stays null; stored stripped response and reconstructed original hashes are distinct and both match their pins |

An in-memory SQLite import independently confirms **3/3 row→box→page joins**. All three Google pages have matching native dimensions and no recorded transforms. Legacy original-response reconstruction is performed only for this verified witness. The initial validator incorrectly assumed the legacy census page hash was non-null; the preserved first-attempt log records that failure, and the corrected validator explicitly binds row/page/book/text to the source harvest record before using its image hash. No census field was filled or rewritten.

## Coordinate frames and remaining handoff

**194 response page dimensions differ from their retained input raster: 14 legacy (8 round1, 2 round2, 3 mixed, 1 page_reads_v1) and 180 W.** Every affected source-object ID is listed in the validation receipt. Raw Google polygons, dimensions, full response transforms and image metadata remain preserved in the archives. Matching dimensions elsewhere do not prove absence of transforms. Provider-frame polygons must not be called native-page polygons or used in toolkit overlap/native-position analyses until the per-page mapping is verified. This packaging step does not repair, rescale, rotate or regenerate them. Exact historical embedded Google image bytes may be unreconstructable for transformed/stripped pages; stored responses are still fully byte-verified.

The three representative joins close the **local portable-input demonstration**, not the complete source availability finding on Clariden. Astra's handoff HIGH remains open until an authorized HF upload, immutable commit pin, foreground authenticated Clariden staging and SHA readback succeed. Full logical-page aliases, contributor lineage, census/release membership, native frame qualification, crops/trainer bytes, features, references and synthetic archives remain Phase 2. No full-population join claim is made here.

## Measured costs and review changes

First bounded W batch: **5,389 JPEGs / 4,453,652,987 input bytes → 9 Parquets / 4,455,421,261 bytes in 9.30 seconds**, including source hashing and closed-file SHA generation. The next run exercised completed-group resume and rehashed/reused these nine shards. Legacy PNG packaging took **40.40 seconds**; legacy Google import/archive **117.58 seconds**; W Google **81.16 seconds**. Cumulative source-group work was **254.36 seconds**, excluding preflight, resume readback and independent validation. This is measured Mac packaging, not a Clariden builder-rate estimate. No fixed two-hour full build is qualified; the spec requires a measured representative Clariden CPU batch before selecting its wall time.

Free disk at final receipt: **85,774,835,712 bytes (85.77 GB)**, leaving **45.77 GB** after the 40 GB W3 allowance, above the owner's 10 GB floor. Packaging used a 50 GB combined reserve and checked it between shards.

[HF_REPO_SPEC.md](HF_REPO_SPEC.md) fixes review MEDIUM 2–5: archive synthetic payloads and mark unknown historical fields; promise dataset reconstruction, not deterministic regeneration; separate ephemeral-token foreground download/upload from the credential-free CPU builder; split SQLite transport above 1 GB with full reassembly hash/integrity check; derive later allocation time from a measured first Clariden batch.

Reviewable upload commands: [NEXT_SUBMIT.sh](../../../out/runner4/NEXT_SUBMIT.sh). It performs offline readback first, then private dataset creation/explicit privacy check, `staging-v4` branch creation and serialized Mac upload using `HF_TOKEN` injection on each command only. It never tags this partial archive `v4`. The script passed `bash -n` and has **not run**; namespace entitlement and repository state remain unchecked.

## Pins and implementation

- Original selection SHA256: `f468812a38687cad4aa025290c207ea9148eac2068aa721f7809f933e78c6578`; unchanged.
- Package manifest: `/private/tmp/hf-staging/greek-ocr-lines/manifests/mac-artifacts.json`, SHA256 **`8f2c43ff8d3d102850e7200529d0dab2c4408d490e4df21b0adc40bced0c5548`**.
- Producing HEAD: `8ea1ddc8fc0d7dc7acaa9f27691a7b5dbadb1274`; implementation uncommitted, bound by code SHA.
- Packager: [package_mac.py](../../../scripts/line_registry/package_mac.py), SHA256 `eb31afe0e967c3f724db891fcce35ce741720dbfb9e8eafb48e4a78f8f878c53`.
- Readback/join verifier: [validate_mac_package.py](../../../scripts/line_registry/validate_mac_package.py), SHA256 `c091cc4766183ae1b9536e310af01e0b6b2e06790d32096a4d8a013b2dc177d6`.
- Small remote-only witness producer: [probe_three_rows_remote.py](../../../scripts/line_registry/probe_three_rows_remote.py).
- Durable small custody receipt: [runner4_hf_phase1_20261022.json](../../cleanup_20261019/data_out/RECEIPTS/runner4_hf_phase1_20261022.json).

HF PHASE 1 PACKAGED — **40.71 GB**, **91 data shards**, **3/3 representative joins**; requested durable-path relocation, publication and Clariden handoff remain pending.
