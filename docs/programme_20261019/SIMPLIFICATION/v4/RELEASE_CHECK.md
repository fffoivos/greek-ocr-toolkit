# Release v4 check — handoff complete; spot-check limitations recorded

Job **3713178 COMPLETED 0:0**, elapsed **00:15:37**; all batch/extern steps completed, queue empty. Bind job 3713174 completed 0:0 in 42 seconds. Full logs and terminal accounting: [REL4B_GENERALISED_RUN](SIMPLIFIED/REL4B_GENERALISED_RUN/).

Release: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v4/rel4_c06_full_01`. Receipt SHA256: `dbc99bdc7fd9c770e25880139ef3bd3184392bfe65e1eb2baf89544c8e390f32` (107,683 bytes).

Producing source: sol-recut `b083574d4e71ddaf771f2152d6ee19741526fc6d`; prepackage `6889b7eb`; bound release package `fde561ca305425db4a5a8418300f07f61581f60bc04574d78101c6e1bea0c80a`. Census `31316332c860d411`, generation 2. No package or code changes in this continuation.

## Census to release

Existing authoritative readout: 592,466 rows, pipeline 0.3.3, complete=true, all 16 invariants PASS, INFRA_ERROR=0 and UNPROCESSED=0. Readout: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/census_06_20261020/attempts/full-split-002.readout/readout.json`, SHA256 `a73c0f59c88495547813e77b5e7164ea52568f5961c29da3f31de3fd140eb0af`. No readout rerun.

| Census parent | ADMIT (all splits) | HOLD | DROP |
| --- | ---: | ---: | ---: |
| collect-v3-W1-20261018-0524 | 68,578 | 21,728 | 10,792 |
| collect-v3-W2-20261018-0524 | 138,665 | 51,971 | 28,745 |
| collection-v2-dev | 13,000 | 229 | 293 |
| collection-v2-test | 40,490 | 1,904 | 1,635 |
| collection-v2-train | 196,234 | 8,922 | 9,280 |

Whole census: **456,967 ADMIT / 84,754 HOLD / 50,745 DROP**. Census admitted_train is **364,180** across all parents. Collection-v2-train contributes **196,234** of those and is outside this W1/W2 release scope. W1/W2 ADMIT across all splits is **207,243**, of which **39,297** are held-out diagnostics; the train input and final release are **167,946**. These scope/split differences are not release failures.

| Release count | Rows |
| --- | ---: |
| `edited_rows` | 0 |
| `excluded_benchmark_key` | 0 |
| `excluded_benchmark_pixels` | 0 |
| `excluded_dev_test_edition` | 0 |
| `excluded_missing_exact_crop` | 0 |
| `input_w1_w2_train` | 167,946 |
| `missing_crop_new_admits` | 0 |
| `released` | 167,946 |
| `sf7_edited_rows` | 904 |

The release adds no further exclusions: dev/test editions 0, benchmark keys 0, benchmark pixels 0, missing exact crops 0. Non-sf7 edits output is intentionally empty; the admissions retain the immutable raw labels. **904** applied sf7 corrections are exported separately and registered without being applied to the base release.

## Release flips

Compared with v3: **0 additions, 691 removals**, all source `elstat`, reason `polytonic hold`: W1 **114**, W2 **577**. This is release-membership evidence from the built-in exporter; no separate census flip report was run.

## Seal04, editions and crop custody

The successful exporter enforces benchmark-key and dev/test-edition assertions, excludes benchmark pixel matches, binds both seal04 test/dev inputs and the sealed suite, and checks exact crop bytes before admission. The receipt reports zero exclusions for each of these branches; this records the existing built-in protection, not a new independent audit.

CROPS4C full receipt SHA256 `dbead984d9425dc3181efae0d00e5448e6334227b6d366e160d8a619bb9f7148`: **207,243 selected = 207,243 byte-exact = 0 written + 207,243 skipped-valid**, including **167,946 train + 39,297 held-out**. Smoke 500/500 passed in the same generation. Release crop gaps are **0**, and `missing_crop_new_admits` is **0** in both parents.

## Raw labels and sf7 uncertainty

| Parent | Applied (separate overlay) | kept_unverified (raw retained) | verified_no_change |
| --- | ---: | ---: | ---: |
| collect-v3-W1-20261018-0524 | 284 | 23,836 | 2,565 |
| collect-v3-W2-20261018-0524 | 620 | 20,659 | 6,107 |

`kept_unverified` is retained raw text with stated uncertainty and no polytonic edit. The 44,495 such rows are not verified corrections. The ten inspected examples below cover both W1/W2, including applied, kept-unverified, verified-no-change and not-applicable results.

## Five release outputs

| File | Bytes | Producer receipt SHA256 |
| --- | ---: | --- |
| `corrections_registry.json` | 14,843 | `36d7d9957edfffb5743aef5f367936442d45b7f5e6dde4311698f3d4838d1756` |
| `release_v4_admission.jsonl` | 173,049,274 | `dcae2aebc239c2f22eb5bec6da01218958fb235388553730f3ece14dca6dfa75` |
| `release_v4_edits.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `release_v4_flips.jsonl` | 9,421,374 | `ee9734211c9118dc1982cd0af85ea23e0472be691efa00c261c035a0d72d7dca` |
| `release_v4_sf7_edits.jsonl` | 4,374,139 | `823f9e20064feb1c2bb6f22bfc60ef4e02d4dfea26b6b742beb9292792e22538` |

## Completed handoff and receipt checks

Handoff job **3713294 COMPLETED 0:0 in 00:02:46** (batch and extern also completed; queue empty). The existing `handoff_release_v4.py --receipt` ran once inside the normal allocation and fully hashed its downstream custody inputs. The allocation then checked the other two release outputs, exact sample crop hashes, immutable raw labels, census decision hashes, applied span composition, source-ledger record hashes, and absence of overlays for unedited sample rows. It finished with `HANDOFF_HASHES_PASS; TEN_EXISTING_CROPS_READY_FOR_VISUAL_REVIEW`.

Full [job log](SIMPLIFIED/RELEASE_HANDOFF/handoff-3713294.log), [chain log](SIMPLIFIED/RELEASE_HANDOFF/chain-handoff.log), [terminal accounting](SIMPLIFIED/RELEASE_HANDOFF/LATEST_POLL.json), [handoff arguments](SIMPLIFIED/RELEASE_HANDOFF/HANDOFF_ARGUMENTS.json), [prepared evidence](SIMPLIFIED/RELEASE_HANDOFF/RELEASE_CHECK_EVIDENCE.json) and [transfer checksums](SIMPLIFIED/RELEASE_HANDOFF/EVIDENCE_SHA256SUMS) are retained. All transferred files passed their checksums locally. All heavy source reads stayed in the allocation in this continuation.

Final census `CURRENT` remains completed generation **2**, export `g2-e310b8ef84cc4763b036fd0abfc0295d`, binding `3e05d2f2b5b908f11e20010c7f85dc046920717590f82ba1520f7b0df92febe4`. The final tool-manifest pin is `04920d8f967f03a271228cac1cf0cb616d392a804adb6a6ebef3ca1c3d7b1c0e`. Seal04 suite pin is `9447f09c6073028c1085996e1663232a18ac70ef8b81eda4be5c232a4025b924`; edition map pin is `1cf086f3d4bb41a7159e1ac395915d38a839925bef56dcca7ac0400691a92854`. The existing release protections and final checks passed; no new independent exposure audit was performed.

| Parent | Census ADMIT all splits | Held-out diagnostics | Released train | New-admit crop gaps |
| --- | ---: | ---: | ---: | ---: |
| W1 | 68,578 | 17,956 | 50,622 | 0 |
| W2 | 138,665 | 21,341 | 117,324 | 0 |
| Total | 207,243 | 39,297 | 167,946 | 0 |

## Ten crop / raw-label / sf7 spot checks

All ten original PNGs were inspected at native resolution in this continuation; each copied crop matches its recorded SHA256. Five examples per parent were selected deterministically by the submitted collector, covering the available sf7 statuses. Every sample's release label equals census raw_text. The two applied examples have exact registered sf7 overlay/provenance and source-ledger matches; the other eight have no sf7 overlay. All are retained release members; there are no added members to sample.

**Limits observed:** example 9 retains a raw OCR error (`Χρξώστες` versus printed `Χρεώστες`); examples 4, 6 and 10 show neighbouring fragments, and fine marks in kept-unverified samples remain uncertain. These findings are recorded, with no change to the accepted raw-label release contract. This is a ten-example agent inspection, not an accuracy benchmark, exhaustive segmentation qualification, or owner adoption.

### 01 — W1 / nlg / applied

Row: `nlg--3d71f4f87abea186--s004-l0012`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/01.png); SHA256 `642552c3fb1462e06e55c86050b926397ca42b6a1c03c224d9a35f3c44e08edb`.

![Crop 01](SIMPLIFIED/RELEASE_HANDOFF/01.png)

Raw release label: **ἔχῃ, ὃν ὁ περὶ θεογονίας μῦθος ἔχει, οὔτε τόσον πτωχός**

Separate sf7 overlay: **ἔχῃ, ὃν ὁ περὶ θεογονίας μῦθος ἔχει, οὔτε τόσον πτωχὸς**

The line and final word are visible; the printed grave in πτωχὸς supports the acute→grave sf7 substitution. Base admission still contains raw πτωχός; only the separate overlay changes it.

### 02 — W1 / lekythos / kept_unverified

Row: `lekythos--e9f314aab488b65f--s003-l0234`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/02.png); SHA256 `be554f4e45ebbae1c0a51410abc31ae032014d52ad38f542981b10b5bf2a6a25`.

![Crop 02](SIMPLIFIED/RELEASE_HANDOFF/02.png)

Raw release label: **τῆς χάϊδευε τὰ μαλλιά : «Κατερίνα Φρέ·**

Separate sf7 overlay: **none**.

The corresponding Greek line and its ending are present. Fine marks/end punctuation are not certified by this spot check. The route reports detector_clipped_top/bottom; raw text is retained and no sf7 edit is exported.

### 03 — W1 / ia_greek_latin / verified_no_change

Row: `ia_greek_latin--77e4b1c97043141f--s002-l0010`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/03.png); SHA256 `683fce5de300507b7e9c947486586bdd6d22585a19cf7ac4a574ae167afb0cde`.

![Crop 03](SIMPLIFIED/RELEASE_HANDOFF/03.png)

Raw release label: **καὶ ὅτι ἐξ ὧν ἔκαμε λαβὼν ἀφήρηται.**

Separate sf7 overlay: **none**.

Visible line agrees with the raw label at this inspection; verified_no_change exports no sf7 edit.

### 04 — W1 / gazette_modern / not_applicable

Row: `gazette_modern--1f7db88d63c02afa--s000-l0046`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/04.png); SHA256 `7696dea6e170c2ad7a7c8ed4901109de7dcff29667968976e62d39ef624876d4`.

![Crop 04](SIMPLIFIED/RELEASE_HANDOFF/04.png)

Raw release label: **Αξία Αποσβέσεις Αναπόσβεστη**

Separate sf7 overlay: **none**.

The three header labels are visible at very small native size. Fragments from the neighbouring header appear at the upper edge. No sf7 route applies; this is not a claim of clean segmentation.

### 05 — W1 / bsb_poly1850 / kept_unverified

Row: `bsb_poly1850--91657e0569fe07c8--s006-l0030`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/05.png); SHA256 `6d2c1c58a4da3132424795d4663a86e55e387ad37012a4d2492cd2c44239a53f`.

![Crop 05](SIMPLIFIED/RELEASE_HANDOFF/05.png)

Raw release label: **W.: τὸν Διὸς**

Separate sf7 overlay: **none**.

The short mixed Latin/Greek line W.: τὸν Διὸς is present. The route records detector_clipped_bottom at Δ; no sf7 edit is exported. Raw punctuation/marks remain unverified.

### 06 — W2 / nlg / applied

Row: `nlg--df6ccc87357b61b6--s034-l0033`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/06.png); SHA256 `d889a2ec4f881d9f48525e396087f9ebbed45c4049e1346e787ce9ec0799964c`.

![Crop 06](SIMPLIFIED/RELEASE_HANDOFF/06.png)

Raw release label: **Μπουδροῦμι (Αλικαρνασσόν), ὅπου ἐλλιμένιζαν οἱ στόλοι, ὁ**

Separate sf7 overlay: **Μπουδροῦμι (Ἁλικαρνασσόν), ὅπου ἐλλιμένιζαν οἱ στόλοι, ὁ**

The rough breathing beside the capital Α in Ἁλικαρνασσόν is visible and supports the sf7 Α→Ἁ edit. The base label retains Α; the breathing is present only in the separate overlay. Neighbour fragments are visible at the lower edge.

### 07 — W2 / ia_poly1850 / kept_unverified

Row: `ia_poly1850--ed3079bf091f7255--s009-l0026`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/07.png); SHA256 `4d1ed10ff733dbd490e90e8344bdc31a34de681941b1b93d28395289f6248140`.

![Crop 07](SIMPLIFIED/RELEASE_HANDOFF/07.png)

Raw release label: **ἱστορικός. Περὶ τοῦ ὠκεανοῦ καὶ τῶν κατ' αὐτόν.**

Separate sf7 overlay: **none**.

The matching Greek line is present. The route retains raw text because of detector_unnamed_mark at ρ/ο; no sf7 edit is exported. This check does not promote the line to verified correction.

### 08 — W2 / ia_poly1850 / verified_no_change

Row: `ia_poly1850--34543d92a48213e7--s014-l0015`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/08.png); SHA256 `1d16a7a3d48cf73949849b25141d2e3cbcf5335b48169b8c92b54ebe7e226f82`.

![Crop 08](SIMPLIFIED/RELEASE_HANDOFF/08.png)

Raw release label: **Ἑλλήνων ἐς λόγους, αὐχεῖτε τοσοῦτον, ὅρα μὴ μάτην κόμπος ὁ**

Separate sf7 overlay: **none**.

Visible Greek line agrees with the raw label at this inspection; verified_no_change has no separate sf7 edit.

### 09 — W2 / gazette_modern / not_applicable

Row: `gazette_modern--dacf995fd419bebd--s000-l0113`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/09.png); SHA256 `9967b78a191564907e2060d680a30d7e76efd5e15ada17c80e6220f3ed1ede00`.

![Crop 09](SIMPLIFIED/RELEASE_HANDOFF/09.png)

Raw release label: **Χρξώστες Διάφοροι**

Separate sf7 overlay: **none**.

Residual raw OCR error: the crop reads Χρεώστες Διάφοροι, while the immutable raw label is Χρξώστες Διάφοροι. sf7 is not applicable, so the release preserves that error. No repair/replay is part of this handoff.

### 10 — W2 / gazette_modern / not_applicable

Row: `gazette_modern--631b1db25886c9d5--s000-l0077`. [Existing crop](SIMPLIFIED/RELEASE_HANDOFF/10.png); SHA256 `c6a5fca585f52ca925f210f22e20ec5d6d3eb9b72bb643086254849b13f1ccad`.

![Crop 10](SIMPLIFIED/RELEASE_HANDOFF/10.png)

Raw release label: **στασης της Ανώνυμης Εταιρείας με την επωνυμία «PRINTA Εμπο-**

Separate sf7 overlay: **none**.

The target line and end-of-line hyphen are present; raw text begins with the word continuation στασης and ends Εμπο-. Small neighbouring fragments remain at the edges. sf7 is not applicable; no edit is exported.

## Handoff outcome

Aspect A deliverables are complete, with the raw-label and crop limitations above recorded. Exact downstream custody arguments and source-input row counts are in [V4_HANDOFF.md](V4_HANDOFF.md). Wave-2 preparation must report its actual factory/codec/intersection counts and exposure checks; its assigned acceptance and launch reviews remain required. No job submission, cancellation, commit, package change, census replay, verifier/scheduler rerun, audit, probe or separate flip_report occurred in this continuation.
