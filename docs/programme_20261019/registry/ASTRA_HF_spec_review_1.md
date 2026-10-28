# ASTRA-HF — independent certification of `90dfbb56e`

**Verdict: the specification fits the owner’s requested structure; hold the full Clariden build until the source handoff is verified.**

Reviewed the specification, design, prior review, source manifest, staging plan, HF evidence and one-book artifacts. The checkout is now `d8373bd98`, but the registry package is unchanged from `90dfbb56e`. This review made no file changes, HF requests with credentials, uploads, submissions or background jobs.

**Findings, most severe first**

1. **HIGH — the source handoff remains incomplete.**  
   Fresh read-only Clariden checks still find no W1/W2 page-record directories, W response directory or expected legacy Round1 page-image directory. Neither proposed source-staging nor HF-v4 staging directory exists.

   The [new split build plan](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/registry/HF_REPO_SPEC.md:128) provides a reasonable alternative to transferring all **35,198,780,622 bytes**: package pages/Google geometry on the Mac, publish those artifacts, and give Clariden verified inputs pinned to that HF commit.

   **Closure:** complete either handoff and repeat the three W1/W2/legacy joins using the inputs the production builder will actually consume. With the HF route, verify the portable page/response locators and imported tables; requiring duplicate originals on Clariden would be unnecessary. Preparatory packaging can establish this handoff; the full population build must wait.

2. **MEDIUM — synthetic provenance is explicitly incomplete.**  
   The [contract](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/registry/HF_REPO_SPEC.md:208) names the necessary fields, but full font hashes and some original-text/seed/job locators remain unresolved. Preserve available provenance and distinguish unknown historical fields.

   Archiving the **203,693 existing image payloads and labels** supports reconstructing that dataset without rendering. It does **not** establish deterministic regeneration from fonts, source text and recipe alone. This distinction should remain in the release card.

3. **MEDIUM — the private-HF download step needs an authentication boundary.**  
   Phase 2 allows Clariden to fetch private Mac artifacts, while the authentication section describes launch-time injection only for uploading. Specify a separate foreground download/staging process using the same ephemeral injection mechanism, followed by a credential-free CPU builder. No token belongs in scheduler exports, scripts or persistent login state.

4. **MEDIUM — resolve the singleton database’s shard-cap treatment.**  
   The layout names one `analysis/registry.sqlite`, while acceptance says to re-shard every file above 1 GB. The small database is already **8.25 MB for 1,429 rows**; that is sufficient reason to address the issue before publication, although extrapolation is not a size measurement. Use a reconstructable transport split or another explicitly documented packaging treatment if the database exceeds the cap.

5. **MEDIUM — the proposed wall time undercovers the stated work.**  
   Joins/features at **30–90 minutes**, plus verification/re-sharding at **30–120 minutes**, total **60–210 minutes**. A two-hour allocation cannot cover the upper estimate. Measure the first batch and revise the allocation accordingly.

**Independent dry-run verification**

I checked the artifacts in [/private/tmp/runner4-hf-book-20261022/](/private/tmp/runner4-hf-book-20261022), without running the implementer’s builder.

| Check | Independent result |
|---|---|
| Bound artifacts and inputs | All 10 checked artifact/code/input bindings and all 118 book source-input hashes match |
| Table identities | 40 pages, 2,858 boxes, 1,429 rows, 2,858 feature records; no duplicate keys |
| Row → box → page | **1,429/1,429 pass**, including source-page identity and derived geometry |
| Raw Google geometry | **1,429/1,429** raw records, polygons and pixel/normalized envelopes agree with retained responses |
| Native coordinate frames | Dimensions agree for all 39 completed pages |
| v4 membership | **1,066/1,066** members match raw labels and crop hashes |
| Fresh Clariden crop readback | **1,078 files / 34,903,858 bytes**, zero hash mismatches |
| Missing crops | **296 held + 55 dropped**; no used crop missing |
| SQLite | Integrity check passes; join/status counts agree with Parquet |
| Features | **20 rows × 2 label variants × 36 fields = 1,440 comparisons**, zero mismatches |

The feature sample contains 12 used, four held and four dropped rows, selected within each status by ranking `SHA256("astra-hf-20261022:" + row_key)`. I independently recomputed text counts, percentages, scripts, capitals, marks, language/confidence selection and position features. Fresh remote PNG-header checks also confirm sample crop dimensions or explicit absence.

This sample covers Greek, Latin and mixed Greek/Latin. Its raw/corrected labels happen to be unchanged; it does not independently qualify correction transformations or every other script. The full production feature check remains necessary.

**Cleared items**

- **Owner’s structure:** the [schema](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/registry/HF_REPO_SPEC.md:61) supplies pages → boxes per segmenter → existing row identities, decisions/reasons, geometry and content features. Unused boxes and excluded/failed pages remain queryable. Census acceptance and actual trainer membership are correctly separate.
- **Exact training images:** original crop hashes and transformed trainer-image hashes are distinct. Copying embedded `image_png` values during re-sharding is the correct preservation method. Full source-to-factory mappings and payload verification remain production work; the book probe checks original crops.
- **Labels and references:** raw, census-corrected and release-overlay labels remain distinct. The specified seal04, v2 common/full and validation references have appropriate membership/image storage. Preserve the actual `VERSIONS.v4.json`, RU1/N1/SF7 inputs, codec and mix configurations: **904 SF7 records alone do not represent the 1,071 changed add_corr labels**.
- **Second segmenter:** yes, it can add run-keyed boxes and per-page outcomes without changing existing rows. Existing rows retain their primary boxes; newly selected crops receive new identities. Comparison includes unmatched boxes and split/merge relationships.
- **Licences:** per-item recording, without an admission/upload gate, matches the owner’s instruction. Anemi receives the same treatment.
- **Publication:** private creation plus explicit visibility verification, serialized Mac/Clariden uploads, checksum-bound build resume, final manifests last, and immutable release tags are suitable. Namespace permission and storage entitlement remain unverified.
- **Authentication:** the proposed upload launcher keeps credentials in process memory and outside scheduler spooling. Installed `huggingface_hub` is **1.1.6**; its upload metadata stores progress fields rather than the token. Environment-token authentication and separate card configurations are supported by the official [environment documentation](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables) and [dataset configuration documentation](https://huggingface.co/docs/hub/datasets-data-files-configuration).

**Sizes and shard plan**

Six claims were checked firsthand through local file stats or read-only Clariden stats:

| Payload | Files | Verified bytes |
|---|---:|---:|
| Legacy native PNGs | 8,574 | 22,244,548,982 |
| W JPEG cache | 5,389 | 4,453,652,987 |
| W raw responses | 4,612 | 5,489,236,156 |
| `union_0` training Parquet | 1 | 5,764,362,247 |
| `union_1` training Parquet | 1 | 1,722,535,902 |
| Current synthetic Parquets | 51 | 6,225,008,494 |

All match the specification.

**75–95 GB is a reasonable planning envelope, not a measured final total.** The additive baseline is approximately 60.8 GB; the stated allowances produce roughly **71.8–94.8 GB** before accounting precisely for overlap, deduplication and unresolved crop custody. WebP expansion and the complete legacy-crop inventory remain uncertain. The 120 GB publication allowance plus 20 GB scratch is reasonable provisional headroom.

The **512 MB target / 1,000,000,000-byte maximum** is sensible. Both oversized training Parquets must be re-sharded, preserving embedded image bytes, labels and original row identity/order mappings. Check closed-file sizes and payload hashes, rather than estimating shard size from row counts.

**First concrete steps for v4**

| Order | Action | Machine and planning cost |
|---|---|---|
| 1 | Pin the production input bundle: source inventories, immutable g2 decisions, trainer pools/mixes, correction registry, codec, synthetic and reference manifests. Define the Mac→Clariden handoff and authentication boundary. | Mac coordination; implementation time unmeasured |
| 2 | Implement and validate one deterministic page batch, then package the selected pages, raw responses and Google boxes. | Mac; JPEG→WebP allowance **1.8–2.9 hours**, plus unmeasured hashing/packing |
| 3 | Make those inputs available to Clariden and close HIGH 1 with the three representative joins. | HF handoff, or the alternative **35.20 GB** direct staging; direct-transfer plan allows **30–120 minutes** |
| 4 | Build rows/features/relations from immutable exports; archive exact crops, trainer/synthetic payloads and references; re-shard oversized files. | Clariden, initially **8 CPUs / 32 GiB**, **1–3.5 hours** provisional; benchmark before fixing wall time |
| 5 | Reconcile all memberships, reasons, mappings and coverage; verify payload preservation, independent features and interrupt/resume equivalence. | Included where possible in the Clariden allowance; revise from measured throughput |
| 6 | Upload Mac artifacts first, Clariden payloads second, final tables/card/manifests last; read back and tag the exact complete commit `v4`. | Total 75–95 GB payload: **25–32 min at 50 MB/s**, **50–63 min at 25 MB/s**, **125–158 min at 10 MB/s**, excluding retries/readback |

For the owner: this is the right structure for the archive you requested, and the one-book checks work. It can preserve the exact real and synthetic training images, expose why rows were accepted or rejected, and support comparisons with another segmenter. The immediate requirement is to complete the source handoff. Missing held/dropped crops and incomplete historical synthetic provenance must stay visible; neither should be disguised as recovered data.

VERDICT: Specification suitable; hold the full Clariden build until the source handoff is verified | BLOCKERS: 0 | HIGH: 1