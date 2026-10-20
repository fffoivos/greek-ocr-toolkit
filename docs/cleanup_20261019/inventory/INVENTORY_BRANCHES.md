# CLEAN1C — local branches and worktrees

Inventory only; generated 2026-10-19T18:59:31.590Z. Owner brief: [OWNER_BRIEF.md](../OWNER_BRIEF.md). Full machine-readable records and **every modified/untracked source/doc filename**: [branches.json](branches.json). Other parallel-run files were not modified.

## Scope, definitions and limits

Measured **56 local branches and 45 worktree registrations**: 18 clean, **26 dirty**, one unavailable. Excluding environments/caches, **23 worktrees retain changes**, covering 29,526 paths: 1,848 modified/deleted source/doc paths, 22,659 untracked source/doc paths and 5,019 other artifact paths. Another 207 cache/environment paths are excluded from name lists. Statuses are per-worktree snapshots, not one atomic snapshot. They precede writing this run's three deliverables; existing parallel inventory evidence is included in the cleanup worktree's dirty count. All 56 branch heads were rechecked unchanged at 2026-10-19T18:58:35.378Z.

Local baseline: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558` (`main`, head committer date 2026-10-15T14:02:02+03:00). Current checkout: `cleanup/20261019` at `14fc9efe7544c2a2276861041179be222c94d9bc`. Only read-only Git queries and file reads were used. No test suite/project script, network access, Git state mutation or commit was performed.

**Owner classification:** A(i) slow OCR/segmenter; A(ii) next-generation development; A(iii) segmenter built on the small detector; B(a) page acquisition/Google Document AI; B(b) correction/filtering tools; B(c) exact organising pipeline; B(d) revision artifacts/sheets and human-review publication; shared infrastructure; obsolete; unsure. Multiple classifications are allowed. The fast-line documentation says the small-detector and current-revision work share `prototypes/fast_lines/stack`; therefore A(ii)/A(iii) are jointly tagged rather than inventing a third installed tree. The slow package is `greekocr/pages`.

**Status is an editorial inventory judgement, separate from classification.** INTEGRATE means the branch's current code/docs/provenance must be accounted for in a cleanup comparison, not that every historical artifact should be merged. CLOSED means contained support work or an explicitly closed/stopped/superseded track; it does not mean obsolete, accepted, or safe to delete. UNSURE preserves unresolved adoption decisions. ACTIVE is the baseline/current coordination branch. STALE marks the older public README. Counts: 10 INTEGRATE, 32 CLOSED, 11 UNSURE, 2 ACTIVE, 1 STALE.

Ahead/behind counts compare commits against local main. Changed-file counts compare `merge-base(main, head)` to the pinned head with `--no-renames`; binaries and tracked caches count, and a rename is an add/delete pair. Up to five significant paths are selected for owner-relevant entry points/contracts, then source/scripts/durable docs and line-change size; they are not the five largest generated artifacts. Containment lists all OTHER local branches reaching the head; no cherry-pick equivalence or runtime acceptance is inferred. Dates below are head **committer** dates.

## Every local branch

| Branch | Classification | Status | Head SHA | Last commit date | Ahead / behind main | Changed paths |
|---|---|---|---|---|---:|---:|
| `astra/curl-fix` | A(i) | CLOSED | `a4a14219367111e9c3867d10fac34663fc7d3750` | 2026-10-08T22:04:48+03:00 | 0 / 133 | 0 |
| `astra/ff-geometry` | A(ii); A(iii) | CLOSED | `b2c364120d6fd24ab5479871f7691882dfd5e95f` | 2026-10-11T17:32:14+03:00 | 41 / 76 | 305 |
| `astra/ff-ink` | A(ii); A(iii) | CLOSED | `046bd52dddeea7ada7727971f1038d34328ba5b7` | 2026-10-15T01:23:52+03:00 | 152 / 76 | 512 |
| `astra/ff-merged` | A(ii); A(iii) | INTEGRATE | `cae93fb49ac1e2e9332fdd57a60f920e266ba1ba` | 2026-10-15T09:03:13+03:00 | 191 / 76 | 525 |
| `astra/ff-plan` | A(ii); A(iii) | CLOSED | `c765336192cca23bf8ed6bbab0f9420a09b1e7ad` | 2026-10-15T09:02:23+03:00 | 96 / 76 | 351 |
| `astra/ff-r8-model` | A(ii); A(iii) | CLOSED | `880aee0da37a481fc03b82f3d5eb45a153f5b662` | 2026-10-11T21:10:53+03:00 | 48 / 76 | 311 |
| `astra/ff-r8-reference` | A(i); A(ii); A(iii) | CLOSED | `1eae16f4d43c593f6e5c4db2df1bc9b93c33a3c5` | 2026-10-11T22:17:26+03:00 | 50 / 76 | 311 |
| `astra/ff-r8-stack` | A(ii); A(iii) | CLOSED | `cd245656a14b9889a48c007b1adbaacd877649b1` | 2026-10-15T09:03:06+03:00 | 160 / 76 | 525 |
| `astra/ff-review` | A(ii); A(iii) | CLOSED | `2f1c91a09b844c87696b95b6c89cd5c3ff7beede` | 2026-10-15T02:27:18+03:00 | 155 / 76 | 523 |
| `astra/ff-rust` | A(ii); A(iii) | UNSURE | `953fc4ae5cd29d0dff54d5c0888d2690b3d58c19` | 2026-10-12T12:01:12+03:00 | 90 / 76 | 352 |
| `astra/ff-type` | A(ii); A(iii) | CLOSED | `07efa3f31440ef2762e3ce398c3e3df68f29535e` | 2026-10-10T23:59:44+03:00 | 17 / 76 | 209 |
| `astra/fl-falsepos` | A(ii); A(iii) | CLOSED | `8e5c522cd55bcc7f8da6eda276f2e86d3cabd1a6` | 2026-10-10T18:20:19+03:00 | 4 / 76 | 79 |
| `astra/fl-geometry` | A(ii); A(iii) | CLOSED | `a003886c3fb0219552c28dcb15eb169666166f21` | 2026-10-10T18:20:19+03:00 | 4 / 76 | 74 |
| `astra/fl-missed` | A(ii); A(iii) | CLOSED | `0b052afceb6175fef93f17162631cd3d4b049e5f` | 2026-10-10T18:20:19+03:00 | 4 / 76 | 72 |
| `astra/page-lines` | A(i); shared infrastructure | UNSURE | `bb99c16290e2688c36ef5c0c6fccf72ad02d6f78` | 2026-10-09T00:40:12+03:00 | 1 / 122 | 13 |
| `astra/page-lines-2` | A(i) | CLOSED | `f405fe38bc19febc7600c61a49cca05740fde73d` | 2026-10-09T02:17:42+03:00 | 0 / 115 | 0 |
| `astra/page-lines-3` | A(i) | CLOSED | `0c080157e2c3c34a3cab04ebdce16f7f8b396e77` | 2026-10-09T14:20:14+03:00 | 0 / 104 | 0 |
| `astra/page-lines-4` | A(ii); A(iii) | CLOSED | `b5199adcc475bcb609e31de470b7db3362b2e84f` | 2026-10-10T17:27:12+03:00 | 3 / 76 | 63 |
| `astra/r3-stopped-q9` | A(ii); A(iii) | CLOSED | `1af64bfd1323c6f9c9c930ab067151524f09302a` | 2026-10-10T17:55:07+03:00 | 4 / 76 | 67 |
| `cleanup/20261019` | shared infrastructure | ACTIVE | `14fc9efe7544c2a2276861041179be222c94d9bc` | 2026-10-19T21:51:39+03:00 | 152 / 0 | 3938 |
| `coord/review-sheets` | B(d) | INTEGRATE | `8172a6b7fdb2bdd71fd7e4924a86af976e184a88` | 2026-10-19T20:56:47+03:00 | 238 / 0 | 11004 |
| `fable/label-correction` | B(b); B(d) | INTEGRATE | `4e95489d9ae69b11a7870d916e31b2163bb865f1` | 2026-10-16T20:12:34+03:00 | 22 / 0 | 654 |
| `main` | A(i); B(a); B(b); shared infrastructure | ACTIVE | `7f50b69fbe5751fb9ff284cdbcb3bb954d173558` | 2026-10-15T14:02:02+03:00 | 0 / 0 | 0 |
| `opus/cleanup-1` | shared infrastructure; B(d) | CLOSED | `ccaa0e8dabada25ed2dcb077853b590aff1dbdcb` | 2026-10-18T10:30:17+03:00 | 232 / 0 | 10988 |
| `opus/r2-cards` | B(b); B(d) | UNSURE | `8de9d42a5ca062ae4b5cf2eddd3744282a1d5185` | 2026-10-18T07:44:58+03:00 | 143 / 0 | 4665 |
| `opus/r2-prep` | B(b); B(d) | UNSURE | `c25e3909885e979d25e6938774941503ef898c6e` | 2026-10-17T19:11:12+03:00 | 241 / 0 | 13130 |
| `opus/secondary-corrections` | B(b); B(d) | INTEGRATE | `7a4eee406b3d2340ed5e2e58731a2223bce83207` | 2026-10-18T10:44:17+03:00 | 333 / 0 | 15175 |
| `opus/seg-census` | B(b); B(c) | INTEGRATE | `20eb44bfb8c2a5f1eea8180131264959d8b7604b` | 2026-10-19T21:33:46+03:00 | 187 / 0 | 5559 |
| `opus/sol-reading` | B(d); shared infrastructure | INTEGRATE | `dcecc6d5e98245ac8f3b18c393120598db8c39ea` | 2026-10-19T05:54:53+03:00 | 90 / 0 | 10974 |
| `opus/spellcheck` | B(b); B(d) | INTEGRATE | `6e7fbb37ffbc7e972daf40b827effb400a1687b4` | 2026-10-19T14:40:55+03:00 | 268 / 0 | 13521 |
| `opus/spellcheck-align` | B(b); B(d) | CLOSED | `2f764c96de65d1ad56b34e81acb8805d4b1890e2` | 2026-10-16T21:29:37+03:00 | 37 / 0 | 809 |
| `opus/spellcheck-l1` | B(b); B(d) | CLOSED | `e3a694158996e5e29f1f67819853d79f8f44d724` | 2026-10-17T05:02:52+03:00 | 93 / 0 | 1620 |
| `opus/spellcheck-l1f` | B(b); B(d) | CLOSED | `ed5037aeeb108ed4cb58577f77071029eaa493f1` | 2026-10-17T08:43:54+03:00 | 140 / 0 | 4940 |
| `opus/spellcheck-l1r` | B(b); B(d) | CLOSED | `c18f3d869267c4362a50521238967336320e6510` | 2026-10-17T03:27:32+03:00 | 106 / 0 | 4324 |
| `opus/spellcheck-l1r2` | B(b); B(d) | CLOSED | `d57fcb4a05077eda0f87e568230a3ce0ca56902c` | 2026-10-17T05:41:05+03:00 | 115 / 0 | 4496 |
| `opus/spellcheck-l1r3` | B(b); B(d) | CLOSED | `4da66be4829a02bfd5d74cfe562079899552b3ce` | 2026-10-17T06:52:28+03:00 | 133 / 0 | 4748 |
| `opus/spellcheck-r0` | B(b); B(d) | CLOSED | `7cef606f5a7c2d728625d192fc394d64d45f7301` | 2026-10-17T02:40:37+03:00 | 88 / 0 | 3592 |
| `opus/spellcheck-r1` | B(b); B(d) | CLOSED | `f6d74a525c370419565bc04f6219b94e11101c74` | 2026-10-16T22:22:31+03:00 | 49 / 0 | 904 |
| `opus/spellcheck-s8` | B(b); B(d) | CLOSED | `2e1efb3be17494104653c4abad6666908442bba0` | 2026-10-17T07:08:06+03:00 | 156 / 0 | 10114 |
| `readme-public` | shared infrastructure | STALE | `703d4c9f977fe54ef323ee12d8ce3491cc645686` | 2026-10-12T12:19:47+03:00 | 2 / 53 | 1 |
| `rehearsal/merge-20261017` | shared infrastructure; B(b) | UNSURE | `a241ed75e64e6ae3af2891aafe43eed3539174d4` | 2026-10-17T11:27:25+03:00 | 203 / 0 | 10874 |
| `rehearsal/merge-final` | shared infrastructure; B(b) | CLOSED | `960a701639e9f50c55df44a54e59fcbcfc381b73` | 2026-10-17T12:46:37+03:00 | 212 / 0 | 10889 |
| `sol/census-v2-serbian` | B(b); B(c) | UNSURE | `504bdb1e13bed4883bd8d88c1ac3e795952d79c9` | 2026-10-18T02:16:04+03:00 | 101 / 0 | 1487 |
| `sol/collect-v3` | B(a); B(b); B(c) | INTEGRATE | `7a026c3d765c7aa36ea48a31065792c3d67b3d3b` | 2026-10-18T03:03:28+03:00 | 83 / 0 | 9769 |
| `sol/funnel-gr` | B(a); B(b) | UNSURE | `6e247e41fefb491265480c7731eab06bbe72e49a` | 2026-10-16T23:31:06+03:00 | 15 / 0 | 9848 |
| `sol/funnel-ia` | B(a) | UNSURE | `7266c42e444ab921cf5f3b9056cef00a503133ca` | 2026-10-16T21:34:46+03:00 | 8 / 0 | 6816 |
| `sol/funnel-intl` | B(a) | UNSURE | `e5529ae147e58aaf94654d141de7650bad17b2fe` | 2026-10-16T21:47:46+03:00 | 8 / 0 | 11290 |
| `sol/l1e-mask` | B(b) | UNSURE | `2007b07673424c35a99969559832bae663a14aa5` | 2026-10-17T04:19:59+03:00 | 38 / 0 | 784 |
| `sol/label-geometry` | B(b) | CLOSED | `4416f9b8482fcf0fd420f8ad222fabfcca33abab` | 2026-10-16T19:26:12+03:00 | 7 / 0 | 85 |
| `sol/recut-v1` | B(b); B(c); B(d) | INTEGRATE | `d82863463fb195cd43f11ab75d167c0da68d690a` | 2026-10-19T14:06:36+03:00 | 150 / 0 | 3933 |
| `sol/seg-cells` | B(b); B(c) | CLOSED | `22f0caf7a3fbd11c4d546ac2ab07161ef9179952` | 2026-10-19T12:39:13+03:00 | 155 / 0 | 3892 |
| `sol/seg-deskew` | B(b); B(c) | CLOSED | `cb042ae4ff74bb99c546e8af4de4b3e944aa2339` | 2026-10-19T10:57:44+03:00 | 149 / 0 | 3531 |
| `sol/seg-gate` | B(b); B(c) | CLOSED | `f9d83ec4bb2f7722f5518eb82600700eb76af75e` | 2026-10-19T11:42:35+03:00 | 151 / 0 | 3565 |
| `sol/seg-gate2` | B(b); B(c) | CLOSED | `2cffd85af1d92946195143ea9734e032d4c49d81` | 2026-10-19T12:03:44+03:00 | 152 / 0 | 3597 |
| `sol/source-inventory` | B(a); B(c) | INTEGRATE | `437dd9ab53d2ea58190834a4090042fbb4ef0351` | 2026-10-16T21:27:41+03:00 | 6 / 0 | 4328 |
| `sol/wikisource-r0` | B(a); B(d) | UNSURE | `db011b019386639bee159778621801f78b625e91` | 2026-10-17T02:04:55+03:00 | 25 / 0 | 947 |

### Purpose, merge-base, containment and significant paths

#### `astra/curl-fix`

- Classification / status: **A(i) / CLOSED**.
- Purpose: Smooth curled-line-start repair, already contained in main.
- Merge-base with main: `a4a14219367111e9c3867d10fac34663fc7d3750`.
- Contained in: `astra/ff-geometry`, `astra/ff-ink`, `astra/ff-merged`, `astra/ff-plan`, `astra/ff-r8-model`, `astra/ff-r8-reference`, `astra/ff-r8-stack`, `astra/ff-review`, `astra/ff-rust`, `astra/ff-type`, `astra/fl-falsepos`, `astra/fl-geometry`, `astra/fl-missed`, `astra/page-lines`, `astra/page-lines-2`, `astra/page-lines-3`, `astra/page-lines-4`, `astra/r3-stopped-q9`, `cleanup/20261019`, `coord/review-sheets`, `fable/label-correction`, `main`, `opus/cleanup-1`, `opus/r2-cards`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/seg-census`, `opus/sol-reading`, `opus/spellcheck`, `opus/spellcheck-align`, `opus/spellcheck-l1`, `opus/spellcheck-l1f`, `opus/spellcheck-l1r`, `opus/spellcheck-l1r2`, `opus/spellcheck-l1r3`, `opus/spellcheck-r0`, `opus/spellcheck-r1`, `opus/spellcheck-s8`, `readme-public`, `rehearsal/merge-20261017`, `rehearsal/merge-final`, `sol/census-v2-serbian`, `sol/collect-v3`, `sol/funnel-gr`, `sol/funnel-ia`, `sol/funnel-intl`, `sol/l1e-mask`, `sol/label-geometry`, `sol/recut-v1`, `sol/seg-cells`, `sol/seg-deskew`, `sol/seg-gate`, `sol/seg-gate2`, `sol/source-inventory`, `sol/wikisource-r0`.
- Upstream: none configured.

No paths changed from its merge-base to this head.

#### `astra/ff-geometry`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: Supporting fast-stack worker/planner/audit head; exact tip contained in astra/ff-merged. Prototype conservative column bend edits; keep T2c opt-in
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: `astra/ff-ink`, `astra/ff-merged`, `astra/ff-plan`, `astra/ff-r8-model`, `astra/ff-r8-reference`, `astra/ff-r8-stack`, `astra/ff-review`, `astra/ff-rust`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/geometry_page_rows.py` | A(ii); A(iii) | 450 / 0 |
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/shared/geometry_envelopes.py` | A(ii); A(iii) | 323 / 0 |
| `prototypes/fast_lines/shared/geometry_rows.py` | A(ii); A(iii) | 304 / 0 |

#### `astra/ff-ink`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: Supporting fast-stack worker/planner/audit head; exact tip contained in astra/ff-merged. Audit native M35 removals and seal glyph atlas construction
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: `astra/ff-merged`, `astra/ff-r8-stack`, `astra/ff-review`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/geometry_rows.py` | A(ii); A(iii) | 573 / 0 |
| `prototypes/fast_lines/shared/geometry_bands.py` | A(ii); A(iii) | 436 / 0 |
| `prototypes/fast_lines/shared/geometry_field_detector.py` | A(ii); A(iii) | 389 / 0 |
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/shared/type_completion.py` | A(ii); A(iii) | 358 / 0 |

#### `astra/ff-merged`

- Classification / status: **A(ii); A(iii) / INTEGRATE**.
- Purpose: Consolidated fast-stack round-8 code, audit, and owner-facing segmentation map; active allocation closed partial.
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/stack/pipeline.py` | A(ii); A(iii) | 188 / 0 |
| `prototypes/fast_lines/shared/geometry_rows.py` | A(ii); A(iii) | 573 / 0 |
| `docs/LINE_SEGMENTATION.md` | A(ii); A(iii) | 70 / 0 |
| `docs/records/research/round8/OWNER_CLOSING_SUMMARY.md` | A(ii); A(iii) | 19 / 0 |
| `docs/records/research/round8/PLAN.md` | A(ii); A(iii) | 2773 / 0 |

#### `astra/ff-plan`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: Supporting fast-stack worker/planner/audit head; exact tip contained in astra/ff-merged. Record owner direction to bound curvature work to the nominated edge
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: `astra/ff-merged`, `astra/ff-r8-stack`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/shared/geometry_envelopes.py` | A(ii); A(iii) | 323 / 0 |
| `prototypes/fast_lines/shared/geometry_rows.py` | A(ii); A(iii) | 305 / 0 |
| `prototypes/fast_lines/features_geometry/artifacts_round4.py` | A(ii); A(iii) | 251 / 0 |

#### `astra/ff-r8-model`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: Falsified physical replacement-model experiment; preserves failed G1 evidence.
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/physical_page/context.py` | A(ii); A(iii) | 337 / 0 |
| `prototypes/fast_lines/shared/geometry_envelopes.py` | A(ii); A(iii) | 323 / 0 |
| `prototypes/fast_lines/shared/geometry_rows.py` | A(ii); A(iii) | 305 / 0 |

#### `astra/ff-r8-reference`

- Classification / status: **A(i); A(ii); A(iii) / CLOSED**.
- Purpose: Slow-construction adapter experiment stopped at failed G1; distinct from accepted slow implementation.
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/shared/geometry_envelopes.py` | A(ii); A(iii) | 323 / 0 |
| `prototypes/fast_lines/shared/geometry_rows.py` | A(ii); A(iii) | 305 / 0 |
| `prototypes/fast_lines/features_geometry/artifacts_round4.py` | A(ii); A(iii) | 251 / 0 |

#### `astra/ff-r8-stack`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: Supporting fast-stack worker/planner/audit head; exact tip contained in astra/ff-merged. Merge FP8ap planner docs (owner one-side curvature direction)
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/geometry_rows.py` | A(ii); A(iii) | 573 / 0 |
| `prototypes/fast_lines/shared/geometry_bands.py` | A(ii); A(iii) | 436 / 0 |
| `prototypes/fast_lines/shared/geometry_field_detector.py` | A(ii); A(iii) | 389 / 0 |
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/shared/type_completion.py` | A(ii); A(iii) | 358 / 0 |

#### `astra/ff-review`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: Supporting fast-stack worker/planner/audit head; exact tip contained in astra/ff-merged. Audit retained round8 runtime, native evidence and final default cost
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: `astra/ff-merged`, `astra/ff-r8-stack`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/geometry_rows.py` | A(ii); A(iii) | 573 / 0 |
| `prototypes/fast_lines/shared/geometry_bands.py` | A(ii); A(iii) | 436 / 0 |
| `prototypes/fast_lines/shared/geometry_field_detector.py` | A(ii); A(iii) | 389 / 0 |
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/shared/type_completion.py` | A(ii); A(iii) | 358 / 0 |

#### `astra/ff-rust`

- Classification / status: **A(ii); A(iii) / UNSURE**.
- Purpose: Parked rectified-M17 Rust pilot; not included in consolidated head, no acceptance inferred.
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/rust_bands/src/lib.rs` | A(ii); A(iii) | 522 / 0 |
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/shared/geometry_envelopes.py` | A(ii); A(iii) | 323 / 0 |
| `prototypes/fast_lines/shared/geometry_rows.py` | A(ii); A(iii) | 316 / 0 |

#### `astra/ff-type`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: Supporting fast-stack worker/planner/audit head; exact tip contained in astra/ff-merged. Recover missed rows from native body ownership and complete paragraph initials
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: `astra/ff-geometry`, `astra/ff-ink`, `astra/ff-merged`, `astra/ff-plan`, `astra/ff-r8-model`, `astra/ff-r8-reference`, `astra/ff-r8-stack`, `astra/ff-review`, `astra/ff-rust`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/features_geometry/artifacts_round4.py` | A(ii); A(iii) | 251 / 0 |
| `prototypes/fast_lines/shared/type_tables.py` | A(ii); A(iii) | 237 / 0 |
| `prototypes/fast_lines/shared/type_residual_recovery.py` | A(ii); A(iii) | 199 / 0 |

#### `astra/fl-falsepos`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: WIP: error-type track falsepos (stopped after ~10 min; process steered back to feature-first)
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/layout_barriers/fast.py` | A(ii); A(iii) | 195 / 0 |
| `prototypes/fast_lines/workflow.py` | A(ii); A(iii) | 174 / 0 |
| `prototypes/fast_lines/write_report.py` | A(ii); A(iii) | 164 / 0 |

#### `astra/fl-geometry`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: WIP: error-type track geometry (stopped after ~10 min; process steered back to feature-first)
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/layout_barriers/fast.py` | A(ii); A(iii) | 195 / 0 |
| `prototypes/fast_lines/workflow.py` | A(ii); A(iii) | 174 / 0 |
| `prototypes/fast_lines/write_report.py` | A(ii); A(iii) | 164 / 0 |

#### `astra/fl-missed`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: WIP: error-type track missed (stopped after ~10 min; process steered back to feature-first)
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/layout_barriers/fast.py` | A(ii); A(iii) | 195 / 0 |
| `prototypes/fast_lines/workflow.py` | A(ii); A(iii) | 174 / 0 |
| `prototypes/fast_lines/write_report.py` | A(ii); A(iii) | 164 / 0 |

#### `astra/page-lines`

- Classification / status: **A(i); shared infrastructure / UNSURE**.
- Purpose: Early image-first pixel-line/Docling experiment; one unique commit, not contained in later named branches.
- Merge-base with main: `89dd3bda17890ac79ea082d3ac69aa5a396644b7`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/glyphs/page_text_lines.py` | A(i) | 482 / 0 |
| `greekocr/deploy/docling_plugin/model.py` | shared infrastructure | 65 / 3 |
| `scripts/glyphs/eval/page_line_report.py` | A(i); shared infrastructure | 139 / 0 |
| `scripts/glyphs/eval/page_line_holdout.py` | A(i); shared infrastructure | 136 / 0 |
| `scripts/glyphs/eval/page_line_issues.py` | A(i); shared infrastructure | 71 / 0 |

#### `astra/page-lines-2`

- Classification / status: **A(i) / CLOSED**.
- Purpose: Pixel-first curved page-line segmentation, already contained in main.
- Merge-base with main: `f405fe38bc19febc7600c61a49cca05740fde73d`.
- Contained in: `astra/ff-geometry`, `astra/ff-ink`, `astra/ff-merged`, `astra/ff-plan`, `astra/ff-r8-model`, `astra/ff-r8-reference`, `astra/ff-r8-stack`, `astra/ff-review`, `astra/ff-rust`, `astra/ff-type`, `astra/fl-falsepos`, `astra/fl-geometry`, `astra/fl-missed`, `astra/page-lines-3`, `astra/page-lines-4`, `astra/r3-stopped-q9`, `cleanup/20261019`, `coord/review-sheets`, `fable/label-correction`, `main`, `opus/cleanup-1`, `opus/r2-cards`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/seg-census`, `opus/sol-reading`, `opus/spellcheck`, `opus/spellcheck-align`, `opus/spellcheck-l1`, `opus/spellcheck-l1f`, `opus/spellcheck-l1r`, `opus/spellcheck-l1r2`, `opus/spellcheck-l1r3`, `opus/spellcheck-r0`, `opus/spellcheck-r1`, `opus/spellcheck-s8`, `readme-public`, `rehearsal/merge-20261017`, `rehearsal/merge-final`, `sol/census-v2-serbian`, `sol/collect-v3`, `sol/funnel-gr`, `sol/funnel-ia`, `sol/funnel-intl`, `sol/l1e-mask`, `sol/label-geometry`, `sol/recut-v1`, `sol/seg-cells`, `sol/seg-deskew`, `sol/seg-gate`, `sol/seg-gate2`, `sol/source-inventory`, `sol/wikisource-r0`.
- Upstream: none configured.

No paths changed from its merge-base to this head.

#### `astra/page-lines-3`

- Classification / status: **A(i) / CLOSED**.
- Purpose: Pixel page-line guide/column refinements, already contained in main.
- Merge-base with main: `0c080157e2c3c34a3cab04ebdce16f7f8b396e77`.
- Contained in: `astra/ff-geometry`, `astra/ff-ink`, `astra/ff-merged`, `astra/ff-plan`, `astra/ff-r8-model`, `astra/ff-r8-reference`, `astra/ff-r8-stack`, `astra/ff-review`, `astra/ff-rust`, `astra/ff-type`, `astra/fl-falsepos`, `astra/fl-geometry`, `astra/fl-missed`, `astra/page-lines-4`, `astra/r3-stopped-q9`, `cleanup/20261019`, `coord/review-sheets`, `fable/label-correction`, `main`, `opus/cleanup-1`, `opus/r2-cards`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/seg-census`, `opus/sol-reading`, `opus/spellcheck`, `opus/spellcheck-align`, `opus/spellcheck-l1`, `opus/spellcheck-l1f`, `opus/spellcheck-l1r`, `opus/spellcheck-l1r2`, `opus/spellcheck-l1r3`, `opus/spellcheck-r0`, `opus/spellcheck-r1`, `opus/spellcheck-s8`, `readme-public`, `rehearsal/merge-20261017`, `rehearsal/merge-final`, `sol/census-v2-serbian`, `sol/collect-v3`, `sol/funnel-gr`, `sol/funnel-ia`, `sol/funnel-intl`, `sol/l1e-mask`, `sol/label-geometry`, `sol/recut-v1`, `sol/seg-cells`, `sol/seg-deskew`, `sol/seg-gate`, `sol/seg-gate2`, `sol/source-inventory`, `sol/wikisource-r0`.
- Upstream: none configured.

No paths changed from its merge-base to this head.

#### `astra/page-lines-4`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: Q8 printed-rule separators/first fast-line prototypes; exact head contained in later fast-line heads.
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: `astra/ff-geometry`, `astra/ff-ink`, `astra/ff-merged`, `astra/ff-plan`, `astra/ff-r8-model`, `astra/ff-r8-reference`, `astra/ff-r8-stack`, `astra/ff-review`, `astra/ff-rust`, `astra/ff-type`, `astra/fl-falsepos`, `astra/fl-geometry`, `astra/fl-missed`, `astra/r3-stopped-q9`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/layout_barriers/fast.py` | A(ii); A(iii) | 195 / 0 |
| `prototypes/fast_lines/workflow.py` | A(ii); A(iii) | 174 / 0 |
| `prototypes/fast_lines/write_report.py` | A(ii); A(iii) | 164 / 0 |

#### `astra/r3-stopped-q9`

- Classification / status: **A(ii); A(iii) / CLOSED**.
- Purpose: WIP: round 3 (Q9) partial row-support work, stopped by coordinator to split into parallel tracks
- Merge-base with main: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `prototypes/fast_lines/shared/paddle_db.py` | A(ii); A(iii) | 387 / 0 |
| `prototypes/fast_lines/round2.py` | A(ii); A(iii) | 353 / 0 |
| `prototypes/fast_lines/layout_barriers/fast.py` | A(ii); A(iii) | 195 / 0 |
| `prototypes/fast_lines/workflow.py` | A(ii); A(iii) | 174 / 0 |
| `prototypes/fast_lines/write_report.py` | A(ii); A(iii) | 164 / 0 |

#### `cleanup/20261019`

- Classification / status: **shared infrastructure / ACTIVE**.
- Purpose: Current inventory coordination branch, based on sol/recut-v1 plus two brief commits.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/harvest/admission.py` | shared infrastructure | 545 / 21 |
| `greekocr/harvest/neighbour_words.py` | shared infrastructure | 383 / 0 |
| `greekocr/labelfix/rules.py` | B(b) | 339 / 0 |
| `greekocr/labelfix/lexicon.py` | B(b) | 323 / 0 |

#### `coord/review-sheets`

- Classification / status: **B(d) / INTEGRATE**.
- Purpose: Adjudication package, reusable owner sheets and human-review publication/persistence contract.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/adjudicate/owner_sheet.py` | B(d) | 223 / 0 |
| `greekocr/adjudicate/owner_sheet.js` | B(d) | 184 / 0 |
| `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md` | B(d) | 56 / 0 |
| `greekocr/labelfix/sheet.py` | B(d) | 249 / 0 |
| `scripts/labelfix/sheet_build.py` | B(d) | 199 / 0 |

#### `fable/label-correction`

- Classification / status: **B(b); B(d) / INTEGRATE**.
- Purpose: Base labelfix package and original owner review sheet; exact ancestor of current correction/review heads.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `cleanup/20261019`, `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-cards`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/seg-census`, `opus/spellcheck`, `opus/spellcheck-align`, `opus/spellcheck-l1`, `opus/spellcheck-l1f`, `opus/spellcheck-l1r`, `opus/spellcheck-l1r2`, `opus/spellcheck-l1r3`, `opus/spellcheck-r0`, `opus/spellcheck-r1`, `opus/spellcheck-s8`, `rehearsal/merge-20261017`, `rehearsal/merge-final`, `sol/census-v2-serbian`, `sol/l1e-mask`, `sol/recut-v1`, `sol/seg-cells`, `sol/seg-deskew`, `sol/seg-gate`, `sol/seg-gate2`, `sol/wikisource-r0`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 317 / 0 |
| `scripts/labelfix/sheet_build.py` | B(d) | 139 / 0 |
| `greekocr/labelfix/deck.py` | B(d) | 314 / 0 |
| `greekocr/labelfix/rules.py` | B(b) | 339 / 0 |

#### `main`

- Classification / status: **A(i); B(a); B(b); shared infrastructure / ACTIVE**.
- Purpose: Local comparison baseline, collection v2 anomaly decisions; not equal to recorded origin/main.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `cleanup/20261019`, `coord/review-sheets`, `fable/label-correction`, `opus/cleanup-1`, `opus/r2-cards`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/seg-census`, `opus/sol-reading`, `opus/spellcheck`, `opus/spellcheck-align`, `opus/spellcheck-l1`, `opus/spellcheck-l1f`, `opus/spellcheck-l1r`, `opus/spellcheck-l1r2`, `opus/spellcheck-l1r3`, `opus/spellcheck-r0`, `opus/spellcheck-r1`, `opus/spellcheck-s8`, `rehearsal/merge-20261017`, `rehearsal/merge-final`, `sol/census-v2-serbian`, `sol/collect-v3`, `sol/funnel-gr`, `sol/funnel-ia`, `sol/funnel-intl`, `sol/l1e-mask`, `sol/label-geometry`, `sol/recut-v1`, `sol/seg-cells`, `sol/seg-deskew`, `sol/seg-gate`, `sol/seg-gate2`, `sol/source-inventory`, `sol/wikisource-r0`.
- Upstream: `origin/main` [ahead 53, behind 2].

No paths changed from its merge-base to this head.

#### `opus/cleanup-1`

- Classification / status: **shared infrastructure; B(d) / CLOSED**.
- Purpose: Prior cleanup/review-tool consolidation; exact head contained in coord/review-sheets.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |

#### `opus/r2-cards`

- Classification / status: **B(b); B(d) / UNSURE**.
- Purpose: R2 reader/card preparation/evidence; exact head uncontained in latest correction/review branches. CQ4e brief: diagnose 15 VOID contexts
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |

#### `opus/r2-prep`

- Classification / status: **B(b); B(d) / UNSURE**.
- Purpose: R2 reader/card preparation/evidence; exact head uncontained in latest correction/review branches. R2a-2 prereg amendment 1 (before any read): W-CAP from validation-role docs; canonical scanner v4.4
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |

#### `opus/secondary-corrections`

- Classification / status: **B(b); B(d) / INTEGRATE**.
- Purpose: RU1 Cyrillic corrections, N1 numerics and dash tooling with review evidence.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/numerics/tokens.py` | B(b) | 88 / 0 |
| `greekocr/numerics/dash.py` | B(b) | 41 / 0 |
| `greekocr/numerics/combine_v2.py` | B(b) | 69 / 0 |
| `greekocr/labelfix/lqb.py` | B(b) | 414 / 0 |
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |

#### `opus/seg-census`

- Classification / status: **B(b); B(c) / INTEGRATE**.
- Purpose: Frozen segmentation 0.9-s4, content gate 0.3 and exact line-filtering/census pipeline.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/harvest/line_pipeline.py` | B(c) | 498 / 0 |
| `greekocr/harvest/line_pipeline_census.py` | B(c) | 479 / 0 |
| `docs/records/harvest/line_pipeline_legacy/pipeline.mmd` | B(c) | 44 / 0 |
| `docs/records/harvest/line_pipeline_legacy/README.md` | B(c) | 159 / 0 |
| `greekocr/harvest/geometry_observations.py` | B(b) | 316 / 0 |

#### `opus/sol-reading`

- Classification / status: **B(d); shared infrastructure / INTEGRATE**.
- Purpose: Canonical transcript/reader scanner v4.5.5 and source-reading evidence.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `docs/records/harvest/sol_reading/tools/scan_rollout.py` | B(d) | 772 / 0 |
| `tests/test_scan_rollout.py` | B(d) | 211 / 0 |
| `docs/records/harvest/sol_reading/results/TABLES.md` | B(d) | 1299 / 0 |
| `collect_v3/runner.py` | B(a) | 293 / 0 |
| `collect_v3/tests/test_contracts.py` | B(a) | 526 / 0 |

#### `opus/spellcheck`

- Classification / status: **B(b); B(d) / INTEGRATE**.
- Purpose: SF7 polytonic correction, mark evidence, release binding and associated review tools.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/reading.py` | B(b) | 416 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |
| `greekocr/labelfix/sheet.py` | B(d) | 249 / 0 |

#### `opus/spellcheck-align`

- Classification / status: **B(b); B(d) / CLOSED**.
- Purpose: Supporting spellcheck experiment/worker head; exact tip contained in current correction/review heads. spellcheck C1 (gpt-6.1-sol): Clariden debug job 3678590 COMPLETED — recogniser alignments for 91,469 training lines (compound marks oversampled); large outputs kept in .cache/labelfix/clariden
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-cards`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`, `opus/spellcheck-l1`, `opus/spellcheck-l1f`, `opus/spellcheck-l1r`, `opus/spellcheck-l1r2`, `opus/spellcheck-l1r3`, `opus/spellcheck-r0`, `opus/spellcheck-r1`, `opus/spellcheck-s8`, `rehearsal/merge-20261017`, `rehearsal/merge-final`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 390 / 0 |
| `greekocr/labelfix/rules.py` | B(b) | 339 / 0 |

#### `opus/spellcheck-l1`

- Classification / status: **B(b); B(d) / CLOSED**.
- Purpose: Supporting spellcheck experiment/worker head; exact tip contained in current correction/review heads. L1M2: border-blob ownership (neighbour/unowned flags cleared by masking; own-ink flags 631 all persist); padding number: own-ink clipping 100/260 lines, sole AB hold 27/260, median 0.41 x-height
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`, `rehearsal/merge-20261017`, `rehearsal/merge-final`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/ink.py` | B(b) | 682 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |
| `greekocr/labelfix/reading.py` | B(b) | 382 / 0 |

#### `opus/spellcheck-l1f`

- Classification / status: **B(b); B(d) / CLOSED**.
- Purpose: Supporting spellcheck experiment/worker head; exact tip contained in current correction/review heads. L1R4b brief: join float32-mean tolerance 2e-7 -> 1e-6 (17/124,669 rows), witness test, redeploy; no submit
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`, `rehearsal/merge-20261017`, `rehearsal/merge-final`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |

#### `opus/spellcheck-l1r`

- Classification / status: **B(b); B(d) / CLOSED**.
- Purpose: Supporting spellcheck experiment/worker head; exact tip contained in current correction/review heads. L1C READY: analysis-only per-wave HOLD census of L1R (mock ok, deploy sha ok, test-only ok); not submitted
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`, `opus/spellcheck-l1f`, `opus/spellcheck-l1r2`, `opus/spellcheck-l1r3`, `opus/spellcheck-s8`, `rehearsal/merge-20261017`, `rehearsal/merge-final`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |
| `greekocr/labelfix/reading.py` | B(b) | 416 / 0 |

#### `opus/spellcheck-l1r2`

- Classification / status: **B(b); B(d) / CLOSED**.
- Purpose: Supporting spellcheck experiment/worker head; exact tip contained in current correction/review heads. L1R2 production 3680629/3680630 pulled: sf5 AB kept 11,896, corrected 1,089, alias-only 405, real mark lines 754 (457 with single-source deletion; keraia 11)
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`, `opus/spellcheck-l1f`, `opus/spellcheck-l1r3`, `opus/spellcheck-s8`, `rehearsal/merge-20261017`, `rehearsal/merge-final`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |
| `greekocr/labelfix/release_gate.py` | B(b) | 475 / 0 |

#### `opus/spellcheck-l1r3`

- Classification / status: **B(b); B(d) / CLOSED**.
- Purpose: Supporting spellcheck experiment/worker head; exact tip contained in current correction/review heads. L1R3 production 3680729/3680730 pulled (sf6: AB corrected 236, real mark lines 155, recogniser certification 0% on all 124,669 lines) + seeded 100-line audit draw
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`, `opus/spellcheck-s8`, `rehearsal/merge-20261017`, `rehearsal/merge-final`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |

#### `opus/spellcheck-r0`

- Classification / status: **B(b); B(d) / CLOSED**.
- Purpose: Supporting spellcheck experiment/worker head; exact tip contained in current correction/review heads. R0b (i-b): adjudicated letter+mark cards (controls 28/28 both readers; majority-of-3 tiebreak)
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`, `rehearsal/merge-20261017`, `rehearsal/merge-final`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |
| `greekocr/labelfix/reading.py` | B(b) | 414 / 0 |

#### `opus/spellcheck-r1`

- Classification / status: **B(b); B(d) / CLOSED**.
- Purpose: Supporting spellcheck experiment/worker head; exact tip contained in current correction/review heads. R1 mark reader: scripts, mock, deployment + sha256, sbatch test-only (no submission)
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-cards`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`, `opus/spellcheck-l1`, `opus/spellcheck-l1f`, `opus/spellcheck-l1r`, `opus/spellcheck-l1r2`, `opus/spellcheck-l1r3`, `opus/spellcheck-r0`, `opus/spellcheck-s8`, `rehearsal/merge-20261017`, `rehearsal/merge-final`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 575 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |
| `greekocr/labelfix/rules.py` | B(b) | 339 / 0 |

#### `opus/spellcheck-s8`

- Classification / status: **B(b); B(d) / CLOSED**.
- Purpose: Supporting spellcheck experiment/worker head; exact tip contained in current correction/review heads. L1A2 audit: reader naming sound; defect = missing insertion symmetry; ruling: sf6 release not bound
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`, `rehearsal/merge-20261017`, `rehearsal/merge-final`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/ink.py` | B(b) | 713 / 0 |
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |

#### `readme-public`

- Classification / status: **shared infrastructure / STALE**.
- Purpose: Earlier public README; equals recorded origin/main but differs from current local main.
- Merge-base with main: `68aec3988cdb9b60823a8c5e15c02ded5892ac11`.
- Contained in: none of the other local branches.
- Upstream: `origin/main` (equal at snapshot).

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `README.md` | shared infrastructure | 190 / 20 |

#### `rehearsal/merge-20261017`

- Classification / status: **shared infrastructure; B(b) / UNSURE**.
- Purpose: Older Option-C merge rehearsal; exact head uncontained, despite later final rehearsal adoption.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |

#### `rehearsal/merge-final`

- Classification / status: **shared infrastructure; B(b) / CLOSED**.
- Purpose: Option-C non-hashed adapter integration rehearsal; head contained in current correction/review heads.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `coord/review-sheets`, `opus/cleanup-1`, `opus/r2-prep`, `opus/secondary-corrections`, `opus/spellcheck`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/release_gate.py` | B(b) | 711 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 708 / 0 |
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/spellink.py` | B(b) | 487 / 0 |
| `greekocr/labelfix/spellcheck_validate.py` | B(b) | 485 / 0 |

#### `sol/census-v2-serbian`

- Classification / status: **B(b); B(c) / UNSURE**.
- Purpose: CENSUS3 secondary-script census and historical standard-v2 policy; reconcile with later owner gate before reuse.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/harvest/admission.py` | B(b); B(c) | 482 / 2 |
| `greekocr/labelfix/rules.py` | B(b) | 339 / 0 |
| `greekocr/labelfix/lexicon.py` | B(b) | 323 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 317 / 0 |

#### `sol/collect-v3`

- Classification / status: **B(a); B(b); B(c) / INTEGRATE**.
- Purpose: Collection-v3 source acquisition/Document AI collector and historical admission/reporting tools.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `collect_v3/runner.py` | B(a) | 293 / 0 |
| `collect_v3/vendor/admission.py` | B(a) | 306 / 0 |
| `docs/records/harvest/collect_v3/KNOWN_ISSUES.md` | B(a); B(b); B(c) | 19 / 0 |
| `docs/records/harvest/collect_v3/README.md` | B(a); B(b); B(c) | 100 / 0 |
| `collect_v3/tests/test_contracts.py` | B(a) | 526 / 0 |

#### `sol/funnel-gr`

- Classification / status: **B(a); B(b) / UNSURE**.
- Purpose: Greek-source census, blind pre-spend checks and historical look-alike policy.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `docs/records/harvest/inventory_v2/RIGHTS.md` | B(a) | 868 / 0 |
| `docs/records/harvest/screen_v1/receipts/prototype_g1b_scaled/REPORT.md` | B(a); B(b) | 299 / 0 |
| `docs/records/harvest/screen_v1/REPORT.md` | B(a); B(b) | 296 / 0 |
| `docs/records/harvest/pilots_v2/PILOTS.md` | B(a); B(b) | 220 / 0 |
| `docs/records/harvest/funnel_v1/gr/FUNNEL.md` | B(a); B(b) | 177 / 0 |

#### `sol/funnel-ia`

- Classification / status: **B(a) / UNSURE**.
- Purpose: Internet Archive source census, samples and Document AI route/cost evidence.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `docs/records/harvest/inventory_v2/RIGHTS.md` | B(a) | 868 / 0 |
| `docs/records/harvest/pilots_v2/PILOTS.md` | B(a) | 220 / 0 |
| `docs/records/harvest/sample_v1/ia/REPORT.md` | B(a) | 202 / 0 |
| `docs/records/harvest/funnel_v1/ia/FUNNEL.md` | B(a) | 166 / 0 |
| `docs/records/harvest/inventory_v2/INVENTORY.md` | B(a) | 128 / 0 |

#### `sol/funnel-intl`

- Classification / status: **B(a) / UNSURE**.
- Purpose: International source census, samples and Document AI evidence.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `docs/records/harvest/inventory_v2/RIGHTS.md` | B(a) | 868 / 0 |
| `docs/records/harvest/funnel_v1/intl/FUNNEL.md` | B(a) | 270 / 0 |
| `docs/records/harvest/pilots_v2/PILOTS.md` | B(a) | 220 / 0 |
| `docs/records/harvest/sample_v1/intl/REPORT.md` | B(a) | 171 / 0 |
| `docs/records/harvest/inventory_v2/INVENTORY.md` | B(a) | 128 / 0 |

#### `sol/l1e-mask`

- Classification / status: **B(b) / UNSURE**.
- Purpose: Standalone foreign-ink masking/ownership-map export; exact head not contained in recut or correction heads.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/rules.py` | B(b) | 339 / 0 |
| `greekocr/labelfix/lexicon.py` | B(b) | 323 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 317 / 0 |
| `greekocr/labelfix/deck.py` | B(d) | 314 / 0 |

#### `sol/label-geometry`

- Classification / status: **B(b) / CLOSED**.
- Purpose: Optional label-geometry audit/filter; tip explicitly closes unassigned geometry track.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/geometry/collection.py` | B(b) | 440 / 0 |
| `greekocr/labelfix/geometry/pilot.py` | B(b) | 284 / 0 |
| `greekocr/labelfix/geometry/repairs.py` | B(b) | 265 / 0 |
| `greekocr/labelfix/geometry/sheets.py` | B(b) | 259 / 0 |
| `greekocr/labelfix/geometry/io.py` | B(b) | 229 / 0 |

#### `sol/recut-v1`

- Classification / status: **B(b); B(c); B(d) / INTEGRATE**.
- Purpose: Crop recut/foreign-ink tools, admission evolution and W1/W2 edition split proposal.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `cleanup/20261019`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/harvest/geometry_observations.py` | B(b) | 308 / 0 |
| `greekocr/harvest/row_inclusion.py` | B(b) | 136 / 0 |
| `greekocr/harvest/admission.py` | B(b); B(c); B(d) | 545 / 21 |
| `greekocr/glyphs/foreign_ink.py` | B(b) | 177 / 0 |
| `docs/records/briefs/SPLIT1_w1w2_edition_split_proposal.md` | B(b); B(c); B(d) | 51 / 0 |

#### `sol/seg-cells`

- Classification / status: **B(b); B(c) / CLOSED**.
- Purpose: Segmentation pipeline worker head; exact tip contained in opus/seg-census. Append SEG-CELLS-1b completion hand-off and sample receipts
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `opus/seg-census`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/harvest/admission.py` | B(b); B(c) | 545 / 21 |
| `greekocr/harvest/neighbour_words.py` | B(b); B(c) | 383 / 0 |
| `greekocr/harvest/filtering_assets/crop-tools.py` | B(c) | 365 / 0 |
| `greekocr/harvest/line_pipeline_native.py` | B(c) | 361 / 0 |

#### `sol/seg-deskew`

- Classification / status: **B(b); B(c) / CLOSED**.
- Purpose: Segmentation pipeline worker head; exact tip contained in opus/seg-census. Record SEG-DESKEW-1 hand-off and implementation commit
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: `opus/seg-census`, `sol/seg-cells`, `sol/seg-gate`, `sol/seg-gate2`.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/harvest/admission.py` | B(b); B(c) | 545 / 21 |
| `greekocr/harvest/neighbour_words.py` | B(b); B(c) | 383 / 0 |
| `greekocr/labelfix/rules.py` | B(b) | 339 / 0 |
| `greekocr/harvest/line_pipeline_native.py` | B(c) | 336 / 0 |

#### `sol/seg-gate`

- Classification / status: **B(b); B(c) / CLOSED**.
- Purpose: Earlier segmentation policy checkpoint, superseded by frozen 0.9-s4/gate 0.3; exact head is not contained in seg-census.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/harvest/admission.py` | B(b); B(c) | 545 / 21 |
| `greekocr/harvest/neighbour_words.py` | B(b); B(c) | 383 / 0 |
| `greekocr/harvest/filtering_assets/crop-tools.py` | B(c) | 365 / 0 |
| `greekocr/harvest/line_pipeline_native.py` | B(c) | 361 / 0 |

#### `sol/seg-gate2`

- Classification / status: **B(b); B(c) / CLOSED**.
- Purpose: Earlier segmentation policy checkpoint, superseded by frozen 0.9-s4/gate 0.3; exact head is not contained in seg-census.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/harvest/admission.py` | B(b); B(c) | 545 / 21 |
| `greekocr/harvest/neighbour_words.py` | B(b); B(c) | 383 / 0 |
| `greekocr/harvest/filtering_assets/crop-tools.py` | B(c) | 365 / 0 |
| `greekocr/harvest/line_pipeline_native.py` | B(c) | 361 / 0 |

#### `sol/source-inventory`

- Classification / status: **B(a); B(c) / INTEGRATE**.
- Purpose: Source inventory, Open Archives provenance correction and metadata-only collection release.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `docs/records/harvest/oa_rebind_v1/o2/build_release.py` | B(a) | 229 / 0 |
| `docs/records/harvest/oa_rebind_v1/o2/RELEASE_NOTE.md` | B(a) | 154 / 0 |
| `docs/records/harvest/inventory_v2/build_inventory.py` | B(a) | 203 / 0 |
| `docs/records/harvest/oa_rebind_v1/o2/audit_duplicates.py` | B(a) | 236 / 0 |
| `docs/records/harvest/inventory_v2/INVENTORY.md` | B(a) | 128 / 0 |

#### `sol/wikisource-r0`

- Classification / status: **B(a); B(d) / UNSURE**.
- Purpose: Fixed Wikisource page selection and human R0 label alignment; exact head not contained in current review head.
- Merge-base with main: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.
- Contained in: none of the other local branches.
- Upstream: none configured.

| Significant changed path | Classification | + / − lines |
|---|---|---:|
| `greekocr/labelfix/validate.py` | B(b) | 624 / 0 |
| `greekocr/labelfix/rules.py` | B(b) | 339 / 0 |
| `greekocr/labelfix/lexicon.py` | B(b) | 323 / 0 |
| `greekocr/labelfix/ink.py` | B(b) | 317 / 0 |
| `greekocr/labelfix/deck.py` | B(d) | 314 / 0 |

## Integration ancestry and dependencies

All 45 pairs among the 10 INTEGRATE candidates were measured. The only ancestor edges between their **exact tips** are:

| Ancestor | Descendant | Classification |
|---|---|---|
| `fable/label-correction` | `coord/review-sheets` | B(d) |
| `fable/label-correction` | `opus/secondary-corrections` | B(b); B(d) |
| `fable/label-correction` | `opus/seg-census` | B(b); B(c) |
| `fable/label-correction` | `opus/spellcheck` | B(b); B(d) |
| `fable/label-correction` | `sol/recut-v1` | B(b); B(c); B(d) |

Thus account for `fable/label-correction` before its five descendants (or preserve it through one of those descendants). None of the other INTEGRATE tips is an ancestor of another. There is **no measured total merge order** among them. In particular, `sol/recut-v1` is not an ancestor of `opus/seg-census`, and neither `coord/review-sheets`, `opus/spellcheck` nor `opus/secondary-corrections` contains either of the others' current heads.

Functional review order, inferred from the inspected pipeline contract: source provenance/collector → crop identity and recut → SF7 plus RU1/N1/dash result contracts → frozen line pipeline/census → review-sheet consumers. This is a review dependency sequence, not a proven commit chain or merge authorization. Fast-stack development is its own A(ii)/A(iii) track and is not the B(b) segmentation-quality filter.

Contained supporting chains avoid mistaking every worker tip for a separate integration requirement:

- A(ii)/A(iii): `astra/page-lines-4` → `astra/ff-type` → `astra/ff-geometry` → `astra/ff-ink` → `astra/ff-review` → `astra/ff-merged`; `astra/ff-plan` also reaches both `astra/ff-r8-stack` and `astra/ff-merged`. No ancestor relation between those final two heads is implied.
- B(b)/B(d): `opus/spellcheck-align` → `opus/spellcheck-r1` → `opus/spellcheck-l1r` → `opus/spellcheck-l1r2` → `opus/spellcheck-l1r3` → `opus/spellcheck-s8` → `rehearsal/merge-final` → each current correction/review head. `opus/spellcheck-l1f`, `opus/spellcheck-l1` and `opus/spellcheck-r0` are also contained in those current heads.
- B(b)/B(c): `sol/seg-deskew` → `sol/seg-cells` → `opus/seg-census`. The exact `sol/seg-gate` and `sol/seg-gate2` heads are **not** contained in seg-census; their earlier 0.7/0.8 policy checkpoints were superseded by later frozen policy. Supersession is based on committed history/contracts, not claimed tip ancestry.
- B(d)/shared: `rehearsal/merge-final` → `opus/cleanup-1` → `coord/review-sheets`.

### Shared-path edits between INTEGRATE heads

For each pair, shared paths mean **changed on both sides since that pair's own merge-base**. The command was `git diff --stat A B -- <shared paths>` with pinned SHAs (plus `--numstat --no-renames` for machine records). Pair merge-bases, all shared paths, identical edits and exact stats are in `integration.pairs` in the JSON. This also catches `docs/INVENTORY.md` inherited through main, rather than looking only at each branch's delta from main. No merges were attempted; **textual merge conflicts remain UNKNOWN**.

| A | B | Classification | Shared edited paths | Different head paths | Potential conflict paths |
|---|---|---|---:|---:|---|
| `astra/ff-merged` | `coord/review-sheets` | A(ii); A(iii); B(d) | 1 | 1 | `docs/INVENTORY.md` |
| `astra/ff-merged` | `fable/label-correction` | A(ii); A(iii); B(b); B(d) | 1 | 1 | `docs/INVENTORY.md` |
| `astra/ff-merged` | `opus/secondary-corrections` | A(ii); A(iii); B(b); B(d) | 1 | 1 | `docs/INVENTORY.md` |
| `astra/ff-merged` | `opus/seg-census` | A(ii); A(iii); B(b); B(c) | 1 | 1 | `docs/INVENTORY.md` |
| `astra/ff-merged` | `opus/sol-reading` | A(ii); A(iii); B(d); shared infrastructure | 1 | 1 | `docs/INVENTORY.md` |
| `astra/ff-merged` | `opus/spellcheck` | A(ii); A(iii); B(b); B(d) | 1 | 1 | `docs/INVENTORY.md` |
| `astra/ff-merged` | `sol/collect-v3` | A(ii); A(iii); B(a); B(b); B(c) | 1 | 1 | `docs/INVENTORY.md` |
| `astra/ff-merged` | `sol/recut-v1` | A(ii); A(iii); B(b); B(c); B(d) | 1 | 1 | `docs/INVENTORY.md` |
| `astra/ff-merged` | `sol/source-inventory` | A(ii); A(iii); B(a); B(c) | 1 | 1 | `docs/INVENTORY.md` |
| `coord/review-sheets` | `fable/label-correction` | B(d); B(b) | 0 | 0 | none |
| `coord/review-sheets` | `opus/secondary-corrections` | B(d); B(b) | 0 | 0 | none |
| `coord/review-sheets` | `opus/seg-census` | B(d); B(b); B(c) | 3 | 2 | `greekocr/labelfix/text.py`, `pyproject.toml` |
| `coord/review-sheets` | `opus/sol-reading` | B(d); shared infrastructure | 0 | 0 | none |
| `coord/review-sheets` | `opus/spellcheck` | B(d); B(b) | 0 | 0 | none |
| `coord/review-sheets` | `sol/collect-v3` | B(d); B(a); B(b); B(c) | 0 | 0 | none |
| `coord/review-sheets` | `sol/recut-v1` | B(d); B(b); B(c) | 2 | 1 | `greekocr/labelfix/text.py` |
| `coord/review-sheets` | `sol/source-inventory` | B(d); B(a); B(c) | 0 | 0 | none |
| `fable/label-correction` | `opus/secondary-corrections` | B(b); B(d) | 0 | 0 | none |
| `fable/label-correction` | `opus/seg-census` | B(b); B(d); B(c) | 0 | 0 | none |
| `fable/label-correction` | `opus/sol-reading` | B(b); B(d); shared infrastructure | 0 | 0 | none |
| `fable/label-correction` | `opus/spellcheck` | B(b); B(d) | 0 | 0 | none |
| `fable/label-correction` | `sol/collect-v3` | B(b); B(d); B(a); B(c) | 0 | 0 | none |
| `fable/label-correction` | `sol/recut-v1` | B(b); B(d); B(c) | 0 | 0 | none |
| `fable/label-correction` | `sol/source-inventory` | B(b); B(d); B(a); B(c) | 0 | 0 | none |
| `opus/secondary-corrections` | `opus/seg-census` | B(b); B(d); B(c) | 2 | 1 | `greekocr/labelfix/text.py` |
| `opus/secondary-corrections` | `opus/sol-reading` | B(b); B(d); shared infrastructure | 0 | 0 | none |
| `opus/secondary-corrections` | `opus/spellcheck` | B(b); B(d) | 0 | 0 | none |
| `opus/secondary-corrections` | `sol/collect-v3` | B(b); B(d); B(a); B(c) | 0 | 0 | none |
| `opus/secondary-corrections` | `sol/recut-v1` | B(b); B(d); B(c) | 2 | 1 | `greekocr/labelfix/text.py` |
| `opus/secondary-corrections` | `sol/source-inventory` | B(b); B(d); B(a); B(c) | 0 | 0 | none |
| `opus/seg-census` | `opus/sol-reading` | B(b); B(c); B(d); shared infrastructure | 0 | 0 | none |
| `opus/seg-census` | `opus/spellcheck` | B(b); B(c); B(d) | 2 | 1 | `greekocr/labelfix/text.py` |
| `opus/seg-census` | `sol/collect-v3` | B(b); B(c); B(a) | 0 | 0 | none |
| `opus/seg-census` | `sol/recut-v1` | B(b); B(c); B(d) | 0 | 0 | none |
| `opus/seg-census` | `sol/source-inventory` | B(b); B(c); B(a) | 0 | 0 | none |
| `opus/sol-reading` | `opus/spellcheck` | B(d); shared infrastructure; B(b) | 0 | 0 | none |
| `opus/sol-reading` | `sol/collect-v3` | B(d); shared infrastructure; B(a); B(b); B(c) | 0 | 0 | none |
| `opus/sol-reading` | `sol/recut-v1` | B(d); shared infrastructure; B(b); B(c) | 1 | 1 | `.gitignore` |
| `opus/sol-reading` | `sol/source-inventory` | B(d); shared infrastructure; B(a); B(c) | 0 | 0 | none |
| `opus/spellcheck` | `sol/collect-v3` | B(b); B(d); B(a); B(c) | 0 | 0 | none |
| `opus/spellcheck` | `sol/recut-v1` | B(b); B(d); B(c) | 2 | 1 | `greekocr/labelfix/text.py` |
| `opus/spellcheck` | `sol/source-inventory` | B(b); B(d); B(a); B(c) | 0 | 0 | none |
| `sol/collect-v3` | `sol/recut-v1` | B(a); B(b); B(c); B(d) | 1 | 1 | `.gitignore` |
| `sol/collect-v3` | `sol/source-inventory` | B(a); B(b); B(c) | 0 | 0 | none |
| `sol/recut-v1` | `sol/source-inventory` | B(b); B(c); B(d); B(a) | 0 | 0 | none |

### Exact diff stats for shared paths with different contents

#### `astra/ff-merged` ↔ `coord/review-sheets`

Classification: A(ii); A(iii); B(d). Pair merge-base: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.

```text
docs/INVENTORY.md | 375 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 373 insertions(+), 2 deletions(-)
```

#### `astra/ff-merged` ↔ `fable/label-correction`

Classification: A(ii); A(iii); B(b); B(d). Pair merge-base: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.

```text
docs/INVENTORY.md | 375 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 373 insertions(+), 2 deletions(-)
```

#### `astra/ff-merged` ↔ `opus/secondary-corrections`

Classification: A(ii); A(iii); B(b); B(d). Pair merge-base: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.

```text
docs/INVENTORY.md | 375 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 373 insertions(+), 2 deletions(-)
```

#### `astra/ff-merged` ↔ `opus/seg-census`

Classification: A(ii); A(iii); B(b); B(c). Pair merge-base: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.

```text
docs/INVENTORY.md | 375 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 373 insertions(+), 2 deletions(-)
```

#### `astra/ff-merged` ↔ `opus/sol-reading`

Classification: A(ii); A(iii); B(d); shared infrastructure. Pair merge-base: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.

```text
docs/INVENTORY.md | 375 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 373 insertions(+), 2 deletions(-)
```

#### `astra/ff-merged` ↔ `opus/spellcheck`

Classification: A(ii); A(iii); B(b); B(d). Pair merge-base: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.

```text
docs/INVENTORY.md | 375 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 373 insertions(+), 2 deletions(-)
```

#### `astra/ff-merged` ↔ `sol/collect-v3`

Classification: A(ii); A(iii); B(a); B(b); B(c). Pair merge-base: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.

```text
docs/INVENTORY.md | 375 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 373 insertions(+), 2 deletions(-)
```

#### `astra/ff-merged` ↔ `sol/recut-v1`

Classification: A(ii); A(iii); B(b); B(c); B(d). Pair merge-base: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.

```text
docs/INVENTORY.md | 375 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 373 insertions(+), 2 deletions(-)
```

#### `astra/ff-merged` ↔ `sol/source-inventory`

Classification: A(ii); A(iii); B(a); B(c). Pair merge-base: `5b35ec091c1065ef400775bc284a6e6d27ceeb6a`.

```text
docs/INVENTORY.md | 375 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 373 insertions(+), 2 deletions(-)
```

#### `coord/review-sheets` ↔ `opus/seg-census`

Classification: B(d); B(b); B(c). Pair merge-base: `4e95489d9ae69b11a7870d916e31b2163bb865f1`.

```text
greekocr/labelfix/text.py | 72 ++++++++++++++++++++++++------------------------------------------------
 pyproject.toml            |  3 ++-
 2 files changed, 26 insertions(+), 49 deletions(-)
```

#### `coord/review-sheets` ↔ `sol/recut-v1`

Classification: B(d); B(b); B(c). Pair merge-base: `4e95489d9ae69b11a7870d916e31b2163bb865f1`.

```text
greekocr/labelfix/text.py | 72 ++++++++++++++++++++++++------------------------------------------------
 1 file changed, 24 insertions(+), 48 deletions(-)
```

#### `opus/secondary-corrections` ↔ `opus/seg-census`

Classification: B(b); B(d); B(c). Pair merge-base: `4e95489d9ae69b11a7870d916e31b2163bb865f1`.

```text
greekocr/labelfix/text.py | 72 ++++++++++++++++++++++++------------------------------------------------
 1 file changed, 24 insertions(+), 48 deletions(-)
```

#### `opus/secondary-corrections` ↔ `sol/recut-v1`

Classification: B(b); B(d); B(c). Pair merge-base: `4e95489d9ae69b11a7870d916e31b2163bb865f1`.

```text
greekocr/labelfix/text.py | 72 ++++++++++++++++++++++++------------------------------------------------
 1 file changed, 24 insertions(+), 48 deletions(-)
```

#### `opus/seg-census` ↔ `opus/spellcheck`

Classification: B(b); B(c); B(d). Pair merge-base: `4e95489d9ae69b11a7870d916e31b2163bb865f1`.

```text
greekocr/labelfix/text.py | 72 ++++++++++++++++++++++++++++++++++++++++++++++++------------------------
 1 file changed, 48 insertions(+), 24 deletions(-)
```

#### `opus/sol-reading` ↔ `sol/recut-v1`

Classification: B(d); shared infrastructure; B(b); B(c). Pair merge-base: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.

```text
.gitignore | 14 +++++---------
 1 file changed, 5 insertions(+), 9 deletions(-)
```

#### `opus/spellcheck` ↔ `sol/recut-v1`

Classification: B(b); B(d); B(c). Pair merge-base: `4e95489d9ae69b11a7870d916e31b2163bb865f1`.

```text
greekocr/labelfix/text.py | 72 ++++++++++++++++++++++++------------------------------------------------
 1 file changed, 24 insertions(+), 48 deletions(-)
```

#### `sol/collect-v3` ↔ `sol/recut-v1`

Classification: B(a); B(b); B(c); B(d). Pair merge-base: `7f50b69fbe5751fb9ff284cdbcb3bb954d173558`.

```text
.gitignore | 14 +++++---------
 1 file changed, 5 insertions(+), 9 deletions(-)
```

The same `docs/records/reviews/harness/run_review.sh` change is present on both sides of several correction/pipeline pairs and has identical head contents. Differences in inherited `ctc_align.py`, `ink.py`, `markshape.py`, `rules.py` and `sheet_build.py` are unilateral since the pair merge-base; they are preserved in JSON under `main_relative_head_comparison` and are not mislabeled as bilateral conflicts. The two tracked numerics `.pyc` files differ between spellcheck and secondary heads, also unilaterally; they are not source conflicts. Seg-census/recut head differences in `geometry_observations.py` and `row_inclusion.py` are unilateral at the committed tips, but recut has additional **uncommitted** edits to those paths.

## Every registered worktree

**DIRTY is the raw Git state**, even when only an ignored environment/cache path is present. “Relevant state” excludes caches/environments from the filename lists, as requested. Every dirty registration is flagged. The detached registration was already marked prunable by Git; its status command failed, so its cleanliness is unknown. Nothing was removed or pruned.

Complete exact names are in each JSON worktree record's `modified_source_doc`, `untracked_source_doc` and `other_changes` arrays. Those arrays carry porcelain status and classification for every retained entry. Table counts refer to source/docs; generated review images under `docs/` are included. Filenames are relative to that worktree.

| JSON worktree id | Path | Branch | Classification | Raw state | Relevant state | Modified/deleted source/docs | Untracked source/docs | Other retained | Ignored env/cache |
|---:|---|---|---|---|---|---:|---:|---:|---:|
| 0 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit` | `fable/label-correction` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 9 | 0 | 0 |
| 1 | `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/f1db7209-77e0-476f-b75b-886a69c81def/scratchpad/base_wt` | DETACHED | unsure | UNKNOWN | UNKNOWN | 0 | 0 | 0 | unknown |
| 2 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-curl` | `astra/curl-fix` | A(i) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 3 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines` | `astra/page-lines` | A(i); shared infrastructure | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 4 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines2` | `astra/page-lines-2` | A(i) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 5 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines3` | `astra/page-lines-3` | A(i) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 6 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4` | `astra/page-lines-4` | A(ii); A(iii) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 7 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup` | `opus/cleanup-1` | shared infrastructure; B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 201 | 413 | 0 |
| 8 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-geometry` | `astra/ff-geometry` | A(ii); A(iii) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 9 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-ink` | `astra/ff-ink` | A(ii); A(iii) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 10 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged` | `astra/ff-merged` | A(ii); A(iii) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 11 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-plan` | `astra/ff-plan` | A(ii); A(iii) | **DIRTY — UNCOMMITTED** | DIRTY | 7 | 0 | 0 | 0 |
| 12 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model` | `astra/ff-r8-model` | A(ii); A(iii) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 1 | 0 | 0 |
| 13 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-reference` | `astra/ff-r8-reference` | A(i); A(ii); A(iii) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 1 | 0 | 0 |
| 14 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-stack` | `astra/ff-r8-stack` | A(ii); A(iii) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 15 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-review` | `astra/ff-review` | A(ii); A(iii) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 16 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-rust` | `astra/ff-rust` | A(ii); A(iii) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 17 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-type` | `astra/ff-type` | A(ii); A(iii) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 18 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next` | `cleanup/20261019` | shared infrastructure | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 653 | 0 | 0 |
| 19 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-readme` | `readme-public` | shared infrastructure | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 20 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-review` | `coord/review-sheets` | B(d) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 21 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-secondary` | `opus/secondary-corrections` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 7 | 0 | 0 |
| 22 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus` | `opus/seg-census` | B(b); B(c) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 2 | 0 | 0 |
| 23 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-census` | `sol/census-v2-serbian` | B(b); B(c) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 24 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect` | `sol/collect-v3` | B(a); B(b); B(c) | **DIRTY — UNCOMMITTED** | DIRTY | 7 | 29 | 0 | 1 |
| 25 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-funnel-gr` | `sol/funnel-gr` | B(a); B(b) | **DIRTY — UNCOMMITTED** | CLEAN | 0 | 0 | 0 | 1 |
| 26 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-funnel-ia` | `sol/funnel-ia` | B(a) | **DIRTY — UNCOMMITTED** | DIRTY | 1 | 1 | 0 | 1 |
| 27 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-funnel-intl` | `sol/funnel-intl` | B(a) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 17 | 0 | 1 |
| 28 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-inventory` | `sol/source-inventory` | B(a); B(c) | **DIRTY — UNCOMMITTED** | DIRTY | 1826 | 3492 | 0 | 0 |
| 29 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-l1emask` | `sol/l1e-mask` | B(b) | **DIRTY — UNCOMMITTED** | CLEAN | 0 | 0 | 0 | 1 |
| 30 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-reading` | `opus/sol-reading` | B(d); shared infrastructure | **DIRTY — UNCOMMITTED** | DIRTY | 2 | 5 | 0 | 0 |
| 31 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut` | `sol/recut-v1` | B(b); B(c); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 4 | 1938 | 1 | 201 |
| 32 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-wsr0` | `sol/wikisource-r0` | B(a); B(d) | **DIRTY — UNCOMMITTED** | CLEAN | 0 | 0 | 0 | 1 |
| 33 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck` | `opus/spellcheck` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 3261 | 174 | 0 |
| 34 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-align` | `opus/spellcheck-align` | B(b); B(d) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 35 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1` | `opus/spellcheck-l1` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 150 | 56 | 0 |
| 36 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1f` | `opus/spellcheck-l1f` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 541 | 74 | 0 |
| 37 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1r` | `opus/spellcheck-l1r` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 793 | 68 | 0 |
| 38 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1r2` | `opus/spellcheck-l1r2` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 455 | 57 | 0 |
| 39 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1r3` | `opus/spellcheck-l1r3` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 493 | 57 | 0 |
| 40 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r0` | `opus/spellcheck-r0` | B(b); B(d) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |
| 41 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r1` | `opus/spellcheck-r1` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 114 | 145 | 0 |
| 42 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r2cards` | `opus/r2-cards` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 1 | 9505 | 1463 | 0 |
| 43 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r2prep` | `opus/r2-prep` | B(b); B(d) | **DIRTY — UNCOMMITTED** | DIRTY | 0 | 991 | 2511 | 0 |
| 44 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-s8` | `opus/spellcheck-s8` | B(b); B(d) | CLEAN | CLEAN | 0 | 0 | 0 | 0 |

### Uncommitted work details

#### Worktree 0: `fable/label-correction`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:17.565Z. Full filename lists: `branches.json → worktrees[0]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **9**; all names below.

| Path | Classification |
|---|---|
| `greekocr/labelfix/spellink.py` | B(b) |
| `docs/records/reviews/CP-G1_review_1.codexlog` | B(b); B(d) |
| `docs/records/reviews/CP-G1c2_review_1.codexlog` | B(b); B(d) |
| `docs/records/reviews/CP-G1c3_review_1.codexlog` | B(b); B(d) |
| `docs/records/reviews/CP-G2_review_1.codexlog` | B(b); B(d) |
| `docs/records/reviews/CP-G3_review_1.codexlog` | B(b); B(d) |
| `docs/records/reviews/CP-G3c2_review_1.codexlog` | B(b); B(d) |
| `docs/records/reviews/CP-G4_review_1.codexlog` | B(b); B(d) |
| `docs/records/reviews/LOCAL_PRUNE_fastlines_20261017.md` | B(b); B(d) |

#### Worktree 1: `detached registration`

Path: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/f1db7209-77e0-476f-b75b-886a69c81def/scratchpad/base_wt`. Classification: unsure. Raw state: **UNKNOWN**. Git registration head: `fea451c5ec234e196076074cc1f9bd9233da41f3`; prunable reason: gitdir file points to non-existent location. git status failed: fatal: not a git repository (or any of the parent directories): .git. Clean/dirty and filenames are UNKNOWN.

#### Worktree 7: `opus/cleanup-1`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup`. Classification: shared infrastructure; B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:17.807Z. Full filename lists: `branches.json → worktrees[7]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **201**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `out/disk1/duplicates.py` | shared infrastructure; B(d) |
| `out/disk1/evidence.py` | shared infrastructure; B(d) |
| `out/disk1/finalize.py` | shared infrastructure; B(d) |
| `out/disk1/model_provenance.py` | shared infrastructure; B(d) |
| `out/disk1/models.py` | shared infrastructure; B(d) |
| `out/disk1/refresh_changed_files.py` | shared infrastructure; B(d) |
| `out/disk1/refresh_sizes.py` | shared infrastructure; B(d) |
| `out/disk1/report.py` | shared infrastructure; B(d) |
| `out/disk1/revalidate.py` | shared infrastructure; B(d) |
| `out/disk1/scan.py` | shared infrastructure; B(d) |
| `out/disk1/sparse.py` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/audit101.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/census_fixture.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/contact_sheet_fixture/sheets/index.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/crosstab.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/overlay/evidence/tranche6/answer_r1.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/overlay/evidence/tranche6/answer_r2.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/overlay/evidence/tranche6/answer_r3.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/overlay/truth_overlay_v1.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/overlay/truth_overlay_v1_1.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/overlay_reproduction_receipt.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/page_spec_index.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/pin_receipt.json` | shared infrastructure; B(d) |
| `artifacts/cleanup_sr1/pinned_after.json` | shared infrastructure; B(d) |

Other retained artifact changes: 413; exact filenames and statuses are in `other_changes`.

#### Worktree 11: `astra/ff-plan`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-plan`. Classification: A(ii); A(iii). Raw state: **DIRTY**. Measured 2026-10-19T18:54:17.807Z. Full filename lists: `branches.json → worktrees[11]`. 0 cache/environment entries omitted.

<details>
<summary>All 7 modified/deleted source/doc filenames</summary>

| Status | Path | Classification |
|---|---|---|
| ` M` | `docs/records/research/round8/LOOP_HANDOFF.md` | A(ii); A(iii) |
| ` M` | `docs/records/research/round8/OWNER_CLOSING_SUMMARY.md` | A(ii); A(iii) |
| ` M` | `docs/records/research/round8/PLAN.md` | A(ii); A(iii) |
| ` M` | `docs/records/research/round8/ROSTER.json` | A(ii); A(iii) |
| ` M` | `docs/records/research/round8/RUST_COMPLETION_PLAN.md` | A(ii); A(iii) |
| ` M` | `docs/records/research/round8/SOL_TRANSFER.md` | A(ii); A(iii) |
| ` M` | `docs/records/research/round8/SOL_WORKER_HANDOFF.md` | A(ii); A(iii) |

</details>

Untracked source/docs: none.

#### Worktree 12: `astra/ff-r8-model`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-model`. Classification: A(ii); A(iii). Raw state: **DIRTY**. Measured 2026-10-19T18:54:17.931Z. Full filename lists: `branches.json → worktrees[12]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **1**; all names below.

| Path | Classification |
|---|---|
| `commit-F8-R8-01.sh` | A(ii); A(iii) |

#### Worktree 13: `astra/ff-r8-reference`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-r8-reference`. Classification: A(i); A(ii); A(iii). Raw state: **DIRTY**. Measured 2026-10-19T18:54:17.931Z. Full filename lists: `branches.json → worktrees[13]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **1**; all names below.

| Path | Classification |
|---|---|
| `commit-F8-R8-01b.sh` | A(i); A(ii); A(iii) |

#### Worktree 18: `cleanup/20261019`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next`. Classification: shared infrastructure. Raw state: **DIRTY**. Measured 2026-10-19T18:54:18.540Z. Full filename lists: `branches.json → worktrees[18]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **653**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `docs/cleanup_20261019/inventory/evidence/COVERAGE.json` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/METHOD.json` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-009daf6642c66b2a8c5936ddd2636b1ec3ba4d33.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-0b90f69a21c4578366b3c7c3acbef9fa8838a54c.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-0e250ff30f47e294c0c2903006f07e7a47eacfcc.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-10037556a87945c84adef3be530bdd9d13067e66.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-19fe9f6faa6d43f5b357f35b1db812bd1c02d88c.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-21785808cb60f5839331e3a40a118a0f64d773dd.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-287f1e7765feeda89a00f0d007b1f676aa808268.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-41e5ef7cf4b56435877001654da748c7a5c60e80.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-4cca241eca17c78e1a04e347d8dece4e7e0fdb84.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-4df0b6041429630ecb90a34be3a91048d611679f.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-50d61add43c7ac63558555bbe9eae6779a003fd7.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-50fb3be9d322e067bd395ec69aed0675d5714809.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-62e88c1f726c9533c4fb3f5c75f8f7f7e47c01e6.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-6fe8e39034130ce2010dcd52e48adba95ac3ab62.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-7aef640e9dd105fa54a7197cfae6cb0a2774b0ff.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-7b23c50cbe0e60a7ddd540759b38aa9d38092fca.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-8baf1e10dcfc092b32eff470c7dad4cf8f2aaee9.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-9b143a328b54a700e0dddde988d1530655d3fab8.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-b88f93624df3f44e91df337c0775d4848a9982aa.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-bce2f28ce04ae191369e4334c7ff6a038f5cf438.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-c5187a400d51942a8b7f9234050dfb44fe07495a.txt` | shared infrastructure |
| `docs/cleanup_20261019/inventory/evidence/blob-cd9a1ee5321b623d4b48e5d5dcae70efe4492352.txt` | shared infrastructure |

#### Worktree 21: `opus/secondary-corrections`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-secondary`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:18.540Z. Full filename lists: `branches.json → worktrees[21]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **7**; all names below.

| Path | Classification |
|---|---|
| `scripts/secondary/ru4ef3.py` | B(b) |
| `scripts/secondary/ru4ef3_score.py` | B(b) |
| `tests/test_n1w1_r3.py` | B(b); B(d) |
| `tests/test_ru4e.py` | B(b); B(d) |
| `tests/test_ru4e2.py` | B(b); B(d) |
| `tests/test_ru4ef1.py` | B(b); B(d) |
| `docs/CONTEXT_20261019_segmentation_and_secondary.md` | B(b); B(d) |

#### Worktree 22: `opus/seg-census`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus`. Classification: B(b); B(c). Raw state: **DIRTY**. Measured 2026-10-19T18:54:18.540Z. Full filename lists: `branches.json → worktrees[22]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **2**; all names below.

| Path | Classification |
|---|---|
| `docs/records/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl` | B(b) |
| `docs/records/harvest/seg09/cp1_initial_hashes.json` | B(b) |

#### Worktree 24: `sol/collect-v3`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect`. Classification: B(a); B(b); B(c). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.027Z. Full filename lists: `branches.json → worktrees[24]`. 1 cache/environment entries omitted.

<details>
<summary>All 7 modified/deleted source/doc filenames</summary>

| Status | Path | Classification |
|---|---|---|
| ` M` | `docs/records/harvest/collect_v3/segmentation_gallery/NOTE.md` | B(a); B(b); B(c) |
| ` M` | `docs/records/harvest/collect_v3/segmentation_gallery/README.md` | B(a); B(b); B(c) |
| ` M` | `docs/records/harvest/collect_v3/segmentation_gallery/counts.json` | B(a); B(b); B(c) |
| ` M` | `docs/records/harvest/collect_v3/segmentation_gallery/examples.jsonl` | B(a); B(b); B(c) |
| ` M` | `docs/records/harvest/collect_v3/segmentation_gallery/index.html` | B(a); B(b); B(c) |
| ` M` | `docs/records/harvest/collect_v3/test_evidence/credential_scrub_receipt.json` | B(a); B(b); B(c) |
| ` M` | `docs/records/harvest/collect_v3/test_evidence/rate_receipt.json` | B(a); B(b); B(c) |

</details>

Untracked source/docs: **29**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r1/answers.jsonl` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r1/zoom/ans.py` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r1/zoom/crop.sh` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r1/zoom/pix.sh` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r2/answers.jsonl` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r2/zoom/add.py` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r1/answers.jsonl` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r1/zoom/asc.py` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r1/zoom/w1.py` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r1/zoom/z.py` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/answers.jsonl` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/zoom/a` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/zoom/ascii.py` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/zoom/crop.py` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/zoom/crop.sh` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/E0b/r2/zoom/w.py` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/segmentation_gallery/SG2.md` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/segmentation_gallery/build_sg2.py` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/segmentation_gallery/sg2-01-strip.png` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/segmentation_gallery/sg2-02-strip.png` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/segmentation_gallery/sg2-03-strip.png` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/segmentation_gallery/sg2-recovered-page_index.jsonl` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/segmentation_gallery/sg2-source-CENSUS.md` | B(a); B(b); B(c) |
| `docs/records/harvest/collect_v3/segmentation_gallery/sg2-source-REPORT.md` | B(a); B(b); B(c) |

#### Worktree 25: `sol/funnel-gr`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-funnel-gr`. Classification: B(a); B(b). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.027Z. Full filename lists: `branches.json → worktrees[25]`. 1 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: none.

#### Worktree 26: `sol/funnel-ia`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-funnel-ia`. Classification: B(a). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.027Z. Full filename lists: `branches.json → worktrees[26]`. 1 cache/environment entries omitted.

<details>
<summary>All 1 modified/deleted source/doc filenames</summary>

| Status | Path | Classification |
|---|---|---|
| ` M` | `docs/records/harvest/sample_v1/ia/receipts/commit-result.json` | B(a) |

</details>

Untracked source/docs: **1**; all names below.

| Path | Classification |
|---|---|
| `docs/records/harvest/sample_v1/ia/google/ledger.lock` | B(a) |

#### Worktree 27: `sol/funnel-intl`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-funnel-intl`. Classification: B(a). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.027Z. Full filename lists: `branches.json → worktrees[27]`. 1 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **17**; all names below.

| Path | Classification |
|---|---|
| `docs/records/harvest/sample_v1/intl/google/ledger.lock` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/bsb/preview_1.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/bsb/preview_2.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/bsb/preview_3.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/bsb/preview_4.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/bulgarian/preview_1.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/bulgarian/preview_2.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/bulgarian/preview_3.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/bulgarian/preview_4.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/serbian/preview_1.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/serbian/preview_2.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/serbian/preview_3.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/serbian/preview_4.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/wikisource_ru/preview_1.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/wikisource_ru/preview_2.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/wikisource_ru/preview_3.jpg` | B(a) |
| `docs/records/harvest/sample_v1/intl/label_cards/wikisource_ru/preview_4.jpg` | B(a) |

#### Worktree 28: `sol/source-inventory`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-inventory`. Classification: B(a); B(c). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.028Z. Full filename lists: `branches.json → worktrees[28]`. 0 cache/environment entries omitted.

<details>
<summary>All 1826 modified/deleted source/doc filenames</summary>

| Status | Path | Classification |
|---|---|---|
| ` D` | `docs/records/harvest/analysis/A_language_script/book_stats.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/A_language_script/line_flags.jsonl.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/B_content_style/book_stats.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/B_content_style/line_flags.jsonl.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/B_content_style/test_first20k/line_flags.jsonl.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/C_geometry_quality/book_stats.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/C_geometry_quality/line_flags.jsonl.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/C_geometry_quality/test_first20k/line_flags.jsonl.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/C_geometry_quality/test_first20k/vocab_support.tsv.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/C_geometry_quality/vocab_support.tsv.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/D_duplicates_pages/book_stats.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/D_duplicates_pages/duplicates.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/D_duplicates_pages/line_flags.jsonl.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/D_duplicates_pages/page_profiles.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/book_profiles.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/clean_preview/admitted_all_clean_preview.jsonl.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/analysis/clean_preview/dropped_preview.jsonl.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/collection/admitted_all.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/collection/import_real_all.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/collection/import_real_dev.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/collection/import_real_test.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/collection/import_real_train.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/collection/v2/dropped_v2.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/collection/v2/relabels_v2.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/cyrillic/admitted.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/cyrillic/inventory.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/cyrillic/plan.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/cyrillic/records.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/cyrillic/rejected.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/cyrillic/train_pool.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/docai_failed_lines/inventory.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/docai_failed_lines/metrics.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/fix1/post_fix1_gate.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/fix2/page_gates.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/fix2/post_fix2_gate.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/fix2/sampled_post_fix2_gate.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/0200d6f8ab778707efd7e8d82f0bd37350fb31731ab37ba8d50bafe668955040.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/1168747f82da2a5826f5c645d51fc2fd22b14e20be9052fa421e26ad2da16072.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/1581203970a8fca9deee640335f3f333c9c47af5d9906d64e029219420410d36.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/2813f8872f7d6380ea4a5fe385fee378efeb0bb12f5d51874034e614d0e9d90e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/368496dcd9de483787b6108983da1c1cc6d9d88fa48262008ceebfd109724073.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/4964097009306cc0ed7a624ad204e3a859f613417e30362d84c8d4dbd4227655.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/5088f253765ee70cb4dab30c140a022ace28d69d1081856da91d1a6dcd267b15.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/6085a8b0e2aee710504df40ea45e5642eef278de9f7c72544b63ef953ea806cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/60d86381ef3fcbcc61554643ca3eaf11a2cd37224e0d24deb4b9ad96fb59f5c7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/702a1452aafaaf9e5cef6005fc627931985c7debcb8ced09aa31b94eda05b9e3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/915eb8e7f6e27b24ceac5a3622d7d577a3607badf88e508c9bf07db7e590f1b7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/9a1528bfdb904bd73cfa1e6434346102a0aa56accaef4eb22d7f858d79c8dac0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/b1075d8ff332d7297982ad948747bd5b57e3955e0eacf7d1fe2832e13bd059ce.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/bd47f52029e7594bf534115718adddfc1fb057db2a7dec988e155340efecd75c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/d8365f8e45da031a4efd8cd3a6209ea2048485545e4164210d1a8c027221731f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/e6e81cea0e2f76cf77b784036c2b7b47bebae8a934fd3fbd02fa1b311d03158b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/f495fc60702bdebce600e438911ee1c5a696c8e01d051f3e700055291fdd1097.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/f4ec50ebf02208237526b53b91a8a3f04a5398b4cecb84f163d2ee91cc70c01e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/http/f7b9cfa33c4975dad784afc8cd36f6fac58809d0bb0c6fb13d5b1f638c9bef2b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-body-Wecklein1894_0087-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-body-Wecklein1894_0087.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-body-bsb10234118_0096-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-body-bsb10234118_0096.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-body-cu31924087948174_0063-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-body-cu31924087948174_0063.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-body-sophoclesplaysa05campgoog_0136-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-body-sophoclesplaysa05campgoog_0136.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-page-0-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-page-0.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-page-1-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-page-1.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-page-2-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-page-2.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-page-3-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/ajax-commentaries/probe-page-3.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/anemi/http/cd21ec2eff01bfb8f8368cc3463023a74a946b5748a6a144014de32ad88a09c0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/anemi/http/f086186129cbd0b2c61041b50057896bcbfdf038edd4c2a89ddc866f9d4cfffc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/anemi/http/f6bd6fb2bbf894319e326f1c832b1297f7e21526cbf1a1a7581e5a5954a7ea48.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bank-of-greece/http/48d4b42b67b60501a63f172a0650ed4bd60558997fd4ba7becf02672bed62429.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bank-of-greece/http/8adffa23d3ab11d110da41348c3efd44df086484d676bd59d4f1de0675cc6d20.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bank-of-greece/http/c76c1eb674117d2b250ea075a783bcf0b778659422d28ee09f0544c7dae4664c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bank-of-greece/http/f121606f45933867f971320aae06a8115a497cb2ce9955d110a5735fc1447c34.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/0fbd952551270af8b9260008836d895e60ba32a1af17d681c17bc3d1d2053945.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/17dfabeea9aa1b039f66f36a7de5f13f5d3394c6761ed636ca2791f18d6442e9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/2207c3cd5b46eb10510e2f7f3150cd068ef63a3227e3a602be885eefacb2109a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/390109a516b2f92310cf212e705921e5fba093cb19069fb9a9d5529c9f428dd6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/3d5b11f2fa539ceeb675a40557487ea2ba421c438b9eb265f60f86b1ed22ea6e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/4d7c0423ca45fcf691e17778009331b5a828c90a991c110c4c0f23c8df4cab4a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/60df97c023ee3548df06795250185ed2952c27eb66347e95dc93c6ff3d9046d4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/796afeeb940386dd6502cbf66d5ce85f83955090f396544e697af137d056bb7b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/9034b7cf4ad35b0e2a5327450dc4265145bb0299d0566838b2a0f82c5515463a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/93bb577130112beb205b1f16f6ace5bf1e9401e76e12cde9d8fbfcb73c7b3698.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/http/b6edda6be6ef60dc7d6e25b8dba88223d3b09b55618bfa8c77264f9478b048d1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/probe-philologus-10-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/probe-philologus-10.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/probe-philologus-100-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/probe-philologus-100.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/probe-philologus-400-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/probe-philologus-400.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/probe-philologus-760-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bsb-mdz/probe-philologus-760.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bulgarian-national-library/http/151622d7fa5cafbb09355bb9c7d38cdc65e8922c6962d055c3de0bc890b15eec.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bulgarian-national-library/http/1d7d827a25ff58b430f28c103eb2c375b2a3bd43efbb2d75c48a2081180b5efa.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bulgarian-national-library/http/6cdcb7b0e4ddd3094bd68af8de64193a8545d220dacb97284179fabe6745ca9d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/bulgarian-national-library/http/78e86103acbfa9a0b212e8c47414e79d831e5794d4f88aaf3f341c8dc88d6f0f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/e-periodica/http/145a8e5d9025f84e97d66905c629fc0338240d5b244fe591b350b36b0803d46f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/e-rara/http/e5a6dd0513ff83a41fb3d2bc9f3f2689a9723ed0b355af7c37dc80ae5f8d6172.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/elstat/http/0ae95f6790bee2bbbc4b7adfdfb283f94c1e1ae12325611c0eb568c0e7b54f43.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/elstat/http/24144eb267014a4bd5a0b0ed215aa36140c9494dbbcfce88e73d8e358ddc41b1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/elstat/http/6f4f0d4a8ad98a46091fd9ca3c44e6dd078698b60203d43b6ef485527d33c8f2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/elstat/http/759edc4de3aa7c62b03e98e8277ca38dee84c4268067e917e770617a6c648a33.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/elstat/http/c06fb6da3493221e9880e013e0165fbdc3a60b903bfcf404f6f1d994e5134ef2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/elstat/http/c54e2c836370a406731fd9f351840477556edda20ac1b7d17501f91cb96d3687.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gallica/http/4d929f1a5de12d7654d09bb13a34a90d903017783f9116fa5f13786fd230a1a4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gallica/http/cb361984af66e1e06abbcc35f4e62cbfdf583a287e3329be714464d40bcefbdb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gallica/http/ec4322316cbeee6121a6eec7e73fbafb473cfd0831f7cf8bdb501c575824e210.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gennadius/http/1de2687877e7215f6b03082152f24b171dbd42c478c9b5fc1ad4e3dbc3097f06.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gennadius/http/376c1de3cc1ca3df0c1ced4dc337cd876b80b6e097d62fcf60d610245e8a9315.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gennadius/http/b33c2ff15e7333049c70505ff09d3f43da6d16f1968d7bff4aad7ed4e1a48570.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gennadius/http/b7c1bb09f4b03999341c9a20e4ff8bb5cb44e6e23e50ef40fefb80a6c26ebbe7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gennadius/http/fda5248d6db0e76133336376217393622073106dec884b35484ebb0313a26114.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/google-books/http/0d74caf2951b603879a2fd440c8366a3071d2238454d6afe0c75bd6d1c9faf41.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/google-books/http/20308f158834ed8583e513dc2a1dd1482181b540d66a82c74e9f6cb1c9208314.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/google-books/http/6c419b5dbd349f4386b2050369b6becf129dd0752c07ad3fc5d790335a3304eb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/google-books/http/9987a6313c4287a92bdfb8d7db110d42aa8267e403163ad6c636b6ef6b604a3e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/google-books/http/ad3713fded157dffc13c908a74b0753850c3e6f5c0968f29f2f703b123385121.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/google-books/http/b11a42a94ee15eba367900a4a7fa0b10bd6187bfaf78b85479e4226e3b577c9d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/google-books/http/b5d9f9dc6d4e216c059eebdda88694cb52cf3d716fb45a1b0edd6dc1ca6edec9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/google-books/http/c792aa4d1015013c25128e06a03238db3dc244150ee9723726c6731208c79797.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/google-books/http/f43dc010d9d19db753080c31adfa6f4db1c08fa2687d17184d1977dbcbcfb946.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/government-gazette/http/2dadbb0cf130551e3e3a5d22d307c14e99e1a603d82ed48f212cdf2a7a51bdca.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/government-gazette/http/7b67709150351744607eabed415e06eb89c414355bb235007adc6f0e72d951a2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/government-gazette/http/9005bd3e2d86e57c30dbe8e75e88e26d3162e3605de1a88f7d1e48940a712343.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/government-gazette/http/c89b2546dbfe5ac11b69b57c9077e19f4f53ef623d7d33910e32f42da0db8265.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/government-gazette/http/ee7d1c8b0c7ea345ba12d74d19d1e78119dcf86acb6824aed513c07e287bbe7b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/government-gazette/http/ee94ea213ce0329d09d1368a0a96e09b0fecc6f74228e065a10d5e3d5c3529f3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/00f0947e503de4d3b5e59900f0b4eaf2734a3d876e7ec8f59ebe45a5bcc3742c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/01b011401b32a032af998575cd3256e1cad05f71d1b221f965967c14ff4b0403.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/01c1d3bf77743a42c5cbbf9b3e429d8106c6113268476883b69f44a71bb14b43.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/02402cb14d62cbf74534bd77e28ee264f6301a8637e247b74f76c0faedd253d3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/03d01a1f45982e6a4c9323363784957601638ae2cb4cd935e4ed337358b772a0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/041a7eb214512f77fa043b898d30a0ce4d0a7abb0f1ee521896bdaf5086232a9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/04435db8a6b103df81782f3a9b2804a805ace32cefbd08e615e2470860ffe32d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0594be091bd7e57f495607bfdecf83e79f5ff19675ec24680482af2268c8fdbf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/05d451a1b018bae4d967fd454ae1beae113dd1ad372a762fb4bdca32c2cb0d59.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0609591a38c2f6d7d6528ee29d89bcb51da46c115954e1dbc12cbc79a2843e7b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/062655c2b10282c637989af491dc482840bac0d4df59b04445571be386fcd72d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/07c06f1fe26f33a5fa3fd3f6651e6902578b19b77c2dadc55c637b4a39b11c5f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/082c13ea00b21037a56432e2837e2017f7d5f72bca9fc950e09916acedc7875a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/08e1fd75f48c18d96f527343f0569329a812189ad11bc051130873ab33c36cae.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0a10900e851a75119c792806771b57123ee09dbb674ca8b6642db8ffb13fa2be.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0a540d9b8c9167f7311d63cde03841b09301303c9562f3e7585a948d34670ced.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0adadeff1f97f3215ad1931c7fdecc313db38da42106778125e332c43d6a36ef.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0b8d512cda6df74d25d819571110241e4ac8533aaddc3eced869bd71b067dc20.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0be3d0d83a89fddd158aced307479528fea754f65bbe42414b637f9b3f7efef1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0c0a756d5902bb6a69bb5b12abd0d380b40b367e6d60b8651f3c4889e551bf59.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0cf06761deeed61fbac4ddcb9823c7118023d481e865b3de725194a66335a85e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0e311498ac33300e76fa073241dd8eab488b7ccd2a68c9d099488365421f4a7e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0ead2f7036a1da84880482a4aa3e3ce9d79bbfee7c229c2c59867637164d4f21.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0f2a231ad171e37f54a4eb01693521e69adcbc72d125f2f59b160edf79e455bc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/0f4356602d9821e7250c9518714326da0c716e5afec0d8584c32e403db86ff38.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1015821d9bbf9b9fa7fe411aa7a28ac38c4c541c1bf64837350c338b5d770a6e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/102f5ab9715257e6d24dfb37e054267c330a917321bbb1d6323b2c5f9b895dd9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/106e885f783dc498e0f0f74a246b7422ff150562fc6a10812a90d6dbc0a05d09.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/10f7ac3a1237e31494a9f9640c8e5ee4d9422952d63e2bab531b14f647f08642.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/11cd106173c7fb97a92999ef1ea0267c5a8733b4236a3031296b68a851e4ecd2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/120020d6c3c9f4cebedb88ede72a2a32346d3f70db2fe120b4224ce96a37289c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/12bba733da68709931e11aaf96d13490db3b03a9e8971a7187a1c1009957062a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1300a1801de20a7f8e6cf895c3f8657807d65cd9b37ff714bda5b8d914e0be41.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/13a784f1b1bcc463a00dbdebdd1e9e6f579bb4c35f6cd7326b6a45d477dc4690.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/14e843052da55f23fb5cf94109e3cc4558a078f1678886272ffbcbfa281721c7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/14f7e9a07cef847e17fd3bb42a675e0ae53e97a9e1c60136bb5cd7837c1253c0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1526cff804cdaab271d0027950413999883058c9b7be4427b4ceb14d87c767d3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/15acad15fd8f70afb3ad4307c33a69c2a4156bc6b0e4b0b4ceeacd9d45feb383.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1768cdc0aa32700a2427e480a696ee566ea821dab437e46d6943f59a7a5fb285.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/17721c0460548724b7d790af5e4bc3ae0b6b36ce264188869d12f4be9120a371.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/17a85f8862a128a71e5aa2a67b9027a96bb60d6b6a5a546f75072e81f5052335.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/17f4fbe8526e737d50f365d936fceaa35ee299e50339766e1021ed3c000b2628.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/18afe1798ed507bf553d7cb6c86a940439043d8292817f08d4bd3cb5a0e5eb5c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1909db3fed1c555aa4e487f1d46374bc8074d06e1d04977971b0afc61dc1a672.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/19326d710b43139fd00403e4f41b6fd72cbbe19e2ff020be3f4e31bbf4652595.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1b40238c23c3db7a22b7809e9f56f755341d844ebb7ef918e23118c218d42876.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1b445a18bdcbb4f1139cf067b1907d08c53f2cb2e0dd764128352770e9b20856.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1bd06162ca301e7bef9ba84569464a55b356fe80f91802c43b5e6ccf6c3a3677.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1be51de8432af8baf1abdf6aea09b527e57f1e0e47747fc4ebd86440c99b83fb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1c5f93fb66b71d7a91f87710c8df826c2e1748e9523bf185ac99743db80c7e0b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1c92731cf1259fc3b75bc4bb9a149ccab0420e9d98fa678cd19c888de657cc29.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1d4530b29212da3f96758d6faf721161ca79e74ec465dd21a1ab7f81edd82a44.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1d7aa1f19981e73ffae3f3f326b6e93754555b8848cd06372c8a77dfb5b7597b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1dd1c6dfbc08bb204e836d7e93636a32953407188bcd62b2229dde0fe6588606.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1e1feff4e6ee6135cdd1e5c4dd0b8d25412693c5472fcc7fff5dacd97c96166e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/1e611692256282f81c430e1a82873710bb0bf15f9eb3cf9dd71c976f7f038ecb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/204c0b566a53686e988d8efb2fb7b2c59753d1a2a45ff10ace640c6016f3825b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/20fcf884cbea4e101d612857a7707e0967f6d3d72283897b5c349103d2eb6db4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2126953005a42f9357ee47362a22185e485e439e3a81a9b432c2c9cd64c4c0bd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/21343b6774145e54280b80ef8d7348b3079b5627cea2ce69e9792b636424bdad.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2216d49ee8ac1c7fcd4a4a5ec7c2fdf5d507fbb90ba4ec29672aa6eaded0e19a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/22a5e5da8841ca520bbb96570df184fb2c526dc542bb3077a5ea15626089a7fe.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/22cb31c784dfc84c77f2aaafc3448e5cf1cbf0c6ad6a085e86a05bf6247890a4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2372e51f2fd37b138100b3d0c06576b22339ce1cbf3e6fd9c2ec6ec9c4427f24.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/250715854b0ec8e94f4f14e26b48d31ec5350935e934bff417925c63ad3a2c33.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2596ab902a4d07c2f265298906939e8fbd378b268135eadf85fb20cf007b623f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/25ba2906d11db6105b0b825b5ddc7312395dbbaf7143d77241c44db565ab31cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/25c0242858e7577f36ae86a103c28f62edecaf10dad31a99538c91fcca12df3f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/25e9bee7bdd230a73dd705dd8ea9564c5f24417fba5297762cd74593ea6ade5f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/25f12ceaa5357ab5ed1919cc2facbeac43aeb74884431a3a98911265805cf688.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2615335b878f441a2a2050edd44c9f7ebc60d1747044ccca36bb67b9776e0661.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/262dd29311b12bd8f3c67e4a0876500a31320374a13ab5b9f466b4c618dff343.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/263c452579acada7dd66f83b731f04b6f14538967bc87781210407f7d7f618d3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/28511876e5cae67f0c9ffe065f93e9be2ecbfeec2507c506f3c51371e9e1b12a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/290be8c2b5ac331160a11561cdff504109216c1d4126fe61ff74ed8e12ea892a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/293e10c7e265308e344c0c421a545a6432346b095f7d02a1547a773914b2519c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/296bab4d4d36627582d96620816f7417e2f8c6114307f6a4eedf6d36997f5596.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/29bab6991470c828abb312cef9a4f57a2065e35df4c2f79c9f608305b1c8ceb6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2a070ee77eb022a91ba66ef2455366e4c6803541644b5ed701dce53a1716bf48.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2afe43241e3b818b123beeab2d088bdccc75ce2ae78d14a83dabef4bc0e801c5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2b25843816fa4b557379017d96d06bb2bed83fdca16262f652d88133b4b368eb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2ca42f7d2b0abb875e8c2ac5399f08620f4686ac1745fe110db1ced3c26d8ad2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2d9b0c40288ff253fae91304948616b2e545e1c76217fa754594a01f5e6ea36d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2dc82a845a515af660e65e82f51f3d1b22966407d6ea32866de28b7bc93b7d9d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2e7dc582e1e3d765eec227fb3a25a03009469f41fcea48ce0953cf188abc998a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2fc050d02f03c93d7d5e7d283baca73744db04c7af086d43158abec807e490fa.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/2fcd8fe3da526a3a87183a3c88f6283d52e45940511830ceedb6923b9d0f7fd0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/310b89570eadfe8615a391a7dfdb1b72c757e54f3026b618a8fd96d5db2109e3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/31fc00425c11cbb7ffc33b981954b5d43b061ac2ef44fe45cc77c40bab3d7b51.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/320f1ba5f80d87ab039eb4b8295a3eb2daa0275167f3542cf7230cf3606487a1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3216d6b9215f41af0b5e0fe346c09149a014187fd43c7231a8f4b79ee7804b65.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3358c39e0aec23a438b0f50bd4d04750e977106ddc407b23f51cebb9c48a26b7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/33aaf235b2003c80e64acba3c6c275fe09f9d1a9ad3bb84f5ff5a6f9f557c39c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/34928e062001d02ec2b2ace2fde9c36fae23ace737b5d091e4140a7ee4fe2bd7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/34e71401dbda0e6ac401277fc6868a61c11388f2a461b86ee8ebb5cfba352622.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/358b080ddef6db56569fa572fa15700a8ef4516429c3995fe8fcdf9cc03131c6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3646658f1dcb1cbb6d741d5ee3f3b0abfa82781e9f7e8d1c42753a1b87bdee2e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3726ae6194d9df57873c8cb75ab76996237c3a72baaccc092ca2ee2b3bd96902.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/374c69f11e88233580bb62407f883d58cd9b8f9bbe6fb0b3b1f444690bfa2327.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/38b4475c4f61d5d980c41d6db02e417618e88286389069abc7469bf0944e6170.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/38e5c370fba5231c2c223df9bf8aedaf20712412e2bd1ac9ef43f18ad991b616.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/39137fb3f078174e9e2b45984e6c30d9fc29c0fb7a0a9aa620e086a62779f987.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/392fd7c27ccec53342921d330f171853b7556445c524b46e3de60d2a45025da8.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/39eb6ff4c87e76c805c2b947450609bfb2eac44cd205009269e7122f7ea82a4c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3a5b613221606a28e761a0c0bd55f09bd8dbd4ad40b8a3d4b198fe6c1e66e8f1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3bc815321d277859873667c1b5dc11cc224b1b931a8da7fd41de081ef9b3ed09.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3bdad168d820eb1115dca3f5ae713c80bea40919281c840113c78f0f650d3354.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3c600a2fb1817365b14a8f21984cf3a0014f84dc630063670c6c2dd2d5cd3149.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3c86d6582111f62e886a9510dde0ac4684d7b462f003f1e6f479fe129c52d803.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3c9fe34f7c36f0b416c911d3a50e06b7ec163988c1a5557d981b38fae4d06b53.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3d023a471dc76644d7bd53074c9d01603db57c570bd1066a24a1459c059696c1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3d65aaa4a409f47c5576606b15aa5071dc1c08ba8e33b19572d3ee0a25aa2728.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3d821f8261a733b92d100142345fb27fa4b95b9f4b13a88d6561306e0ebde0dd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3d9eef1570fd51001c07d7a73289c748ae7aa60f6a6fa0c380a9cb86cdde571f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3e21bd8fe1a8d16bfa678160d690a9a763b5644255e0329bdd79fc9a56662676.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/3e2d23d1c3ab5a8efc563d9b0ac583e617a2398075f80a62dcb309e29e2a6e05.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/400c8d27fc14eadc14f897658ac368bf53a4a87bb3963bb87fef6cd320f59871.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/41280fa4ca7b3d9528ed2e077817d9ab269eeed4c22bdeb567bd173a1c0737b6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/41390ed5f4d2e439dbfb61b2802523f6a58c11668f23041b48630ac23fc0e4ce.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/41796524006b089262ba074ce6640fba17c93614d7d9c38fa7180243e639fdb6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/42648149c0f23c35492028516a5c02026363d09927c18cb14db95df3bb195588.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/428f5101794cdaa79b656306bf9aa3af1a7cf148709aa0ba38d5c5b3a2bb6504.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/42b040dbfa15deaa8bd9cfbfa109670edcf6eee266fa375c00228157adb9d8b8.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/43752109a67ae1dc642a43c4c80c435cc29987c85038677a14d50357799f9db1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/4384b9ed7258a62b3b428dcd5fed3bc94105cd7dc32f8d4b83d83c260b866568.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/43e842d4da8cc0954c2fb9241af84f2eded026ec1ec124ea1a69998138d18e99.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/448b7a609db41884827aa6bc10922de31fb35c0d3cb09fa3e98a6fd729bef695.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/4544bf836fa43e5128ec4d3a83d7e2ecce0cfe346a91adf8a49397b326a2e232.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/45fbf37f1f35e33296253ca7e60230d9145d187ebb24d663d1db1a5ffe7e03e3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/47373170a5e3211a7301d76d729d7cbb496155bf96593df48bf3ad9bc65d033f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/474360c1497044e4c7994683eaf13cf68811628696e2a1ca2114a4a28b5e6200.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/47d4316539aff929c9a0e3adb74e821dab57aafb0ed438006cba00feb0f529ba.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/49506953e57c6deecd2c47bafdbf2424e74b4f9766806bd3aadfd355039bc0bc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/499fba55190ee261c80ac1664bb71ca7af6885743b5bea95fc58dc5799ca28ee.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/49d5719d60f98d222847a95df6f58353a81e7acf119fc78d53c65d6c9c6a6287.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/4b5f1360b070d1f3fcbcfefe230b96fb1b47154cc24d8d04959de096663fd7b1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/4b8ec7e6827e6da128296c3cef7b6e7cc0e58f0f182c0cb8094696d45a006173.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/4bfa5316cc05f14b1bd7e511814ba8c4fb775a03779e8c154b22ba26e8fb4afa.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/4c900d062cc94fcf407c746cab942d1017b35581452a92fbd75c9fbdafe7ebd0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/4d388e005b0a0e3f01bf699d5a73b4b33ab3d62324c1537b1fd0fb6df2da71c1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/4f5f55c65cb9a5c658ab82f342e5e3e4d04ecb66d1dcbd7fdf82605a03e5620e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/4fd53824d8b1f6f1845d3d77b7ac095b5493100a7f59f2d482014d6cf5451c95.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/50223f6ed45af0f0e8bd65014446444b8d5afb80100e7145875137685bdc3108.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/502323f720f83a3482e3c059e31393a3f1faeaa9099a0943ed2dcf6ba3f4bffb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/509b6b1b9830a2fb2934df02921a2dd58082735d1a98579950a9a1f1597ed2ac.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/50b2dd9cf3b1f220af6c7afd260a548fb259fdc61e5f9ccdc909a89287f4813d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/50f26a68daccd071fa9909bcc54beb37d9988e3d2b3685ea8fb0eb73063cb222.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/512280c1ca02c91b580673a3bc2ed122f816efd9cc3c84841822e10c8fc4947e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/51ee8a2dfee9770b26412c88831d71465cd3f9bced8653038abb4029ab64c3fc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/52bddc87dd56440e232fec3ebfe1db834465c8fe344f11e89e3d1d94cb3370fe.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/52fe7a5a9cb95a38825720ea22265e53a5965ca4327fe3080f288c9937bf0982.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/53011b84c3225112400f2596c956064a7e33397079bccb1a2ef47f95e594a968.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/544650720946f6cbc8f7b3e2eb88043a2e35f771d0276fea5a9f97effa6dc959.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/54ff0f4260d8be2d369248521ff5b873ced71514aa7d6c2d2e60371b9b12ef65.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5538742ad745b195608178f6fe246a52a4949a67fe1a4998be5ba31a20774cce.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/553fd6bfa543bc9157eccc7ee0c0c794ba5fde0d8b35cbcdc23ea5c5f5b33008.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/55b9c6a9e365b0374840c3446f0042cd022bec0c976625c6bf0e4783447c5e1e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5635d7a2cda041f1ae2f6887c69305f3708f087906ddaaa3c6ef8379586e2354.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/572a7dfe8addaca360348ca9ec2f14e87d026d6cf8f4c575c2d978626f647ee6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/576b93091e224c522aea3f50d761be0c14c71571959c8a7ceccd40df22b0e88e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/57ff8f5172dbab116beb1f329898650736bddd907afff280fc5356044a792579.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5850d1584bb59d418ac1e32e2af61060787c449ba37b8ae10a9c81f5237376c0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/585816615958191ff218bc11947bd260e32e0e6f44f8cf47e9c36ef3cef2f170.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/588b16d428594dbf99bcb3425f34e01bf00d11fccf46fe7a7579316df4af3c06.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/58b39fdf20a176fded3971ed77a34635b65783c0e65518e30115c2d73170e36a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/59eaa2781529ab79387f94e508afe8828f35168f8d23f2f2058b156846525bd8.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5a2051df9bb62b6612b8a9d047db4edc0062a2d54c49cea48a2086fadd93dbbb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5af831c574f5f2affc6aadcc4a2f828dbcb9dab681204e3a70a73c932028a6ae.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5b4d36d0334c34204167409d1025efe3813410b3ce786b2db3a96e72e366c8cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5b67f3a823f1fdc0362023a1a93de190293ee072c2cf79d4b4ceaf4aff92f007.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5c7d9afdfd82f084359dfbc70964ed03cc780589806c70380b003799b81d9409.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5ea9279715703f655627ce82d950b7f1799a3504e804ae979d4dc4491aeccf74.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5ecccc8741cbf4e6de52969cc47c073d31592774a81b6e9266aa27b14b05af8c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5f0bf48c8f900835aa802206e16a35e39457d9bdd20391a0af8ac247477bd101.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5f73ebeaa85bab9a851b004bf3c024a46918c76433543c2aa0738af4ef741f03.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/5f85f7ab6861672d77d65e491a3e6edcfab9cbbdf981ccaa2b8ebf16149b1335.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/621296390901a3a9a21ad31c481b2985ab5dd19a7add223c1c14ad2ba7c4fa20.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/624e464c6961d52aed06344082fc27b2378e092d4a0765c3845ea01823f26208.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6258f404843a124100242494f1f69e07c0abce991d7d299e49149e5708fc6891.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6291c5c92b4f78a04b82eccae1850d37f776a512cc184efe13bca148f973c40e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/632c6cba301cc24870da99619383c470af85760f7229c079d94f930ecae89945.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/641a4c6929a5f5aae4efa147e32cf06a2bd04d9bed0b33f02fbbb433453fc594.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/641f4de3a6f921bbf38ddea13ae0a044c8b40f495342b882c809781801acdfa6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/648ec80809389546cff9904a0b69c6f9da0b1232fa1f73b58ace305868f6e04e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/65faca21f65a1dce19cf97a1cdad7487a084049103eb7b76d2e99b734288eb8b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/67185e451f04d16c2f730f1336e2fb5259d2692006181ffbf29c482cb7497b50.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/671f7d0740fa85ddc63c5aa85be265cdc209bf0398ec02b88daf1f376d4fee0d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/673fd3c0a803830ca769091e0ff8b0a2392226e12f2409e19b13a2ff366fa30e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6809f3af61f7dd81b049cbda46320462b8edb128e8402c5ec624df1831da833e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/692107073998957cb19eb2e1a9d362a54fe47befb0c4a43f307aea41263515a0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6932b2868ba79e29554cb1bb8f8b2ac9231306c703b92ec3cc00ae6f9b305155.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6977f900e59187434abdab1025f23a9432e6b851acd44f9007c00f3e9c7caf6a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6a570c6bc964c3e6a215ebbb930c789ba85ec97c6ddba94bfd093826a65a6162.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6ae7ef777380c31a37b0401f2320d2bf9f1b9cb796004ab5c047923d71ad9ed7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6ba580e484bf6850ed5f59e19e874706a3af0514dddaaeca061dc5307d1968a2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6ba8be7092a6c4ddfdc12ce25f68ca50a8c19a0ff04c0588cf5bb552126a09ea.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6baed8f45dd975271317887f1d740df667a6853907b04c18e254806ba845cd4d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6c9b250e2ec8bd676c6a959a304de970ab582daabb95a0295da65b19f6c08883.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6de9ec328371a0da5b8a27613958668839e83b31aeea1306c6eb62e5ecbd8927.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6e7a4d081c93d3a883b7168d4bb5b17e34a525c9947bb1120760839ffeb75dee.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6f2eb8758477794405de8cdea188e9a73ddf4d3478e66c1bccdb0447a0424dba.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/6fa97f7d20b101308061577e86398925d04c70d827a13b3cbe64c3143e74606b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7048b8ba98f9c7bdc5d3628d3c5f12865cc057713e08ba81b3ca55da4cad9cd6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/714bfb2bd6be628c148336a2b99c37c1f33511e8f2c8010301c3d0825e830e46.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/71cdd040932298827dc4e07972d757fbb0de091a367a6d311fae09c300c3753e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/71eeb7dbf138b86a9ae7662b1bd4d8a0afb6ba8d126c26dcea0f14ce8972b810.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7203b2a1d001630a1ffa54eca0073842b844670b2675ce4ae4f55e9ff412c047.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7324d1cf2edb832bd72d35c23c62e55c1690105af1162d688582aee6cb25de4b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/73983a6bf0b8c5bedbed421028f7ea1e9724a5812d9284752efda97a1c81ff0a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/745007865022be0a4ebef64bf69acdfdeed2031ab40647af78fc3daec9178eb9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7601dddf331a7f3ba0bdd47b4a4fd6823d75c856725031bb58d1f263c05e72cb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/764ce6c87d3423102e4e70073d52a758155069b5a6d64e56c1dc330b6860de08.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/76de2e764b88e76131511cf532c2cfc57687c6a424c0a058264ffddbd1e04fda.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/772bfadcd853e0328381c0fa745d34886a1ecbc84c048fd29656bb04987de851.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7743c23170fc0178a31332de9769d34bdf9c7ec95cca8d02f68775e72306404b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/77953ca907b8a0c17b841fa4065d6ec2c86772d587ed7e89daf95368b7b7a938.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/77f0cae8895fdfe313fc09fbccc159abd7a060b9d5497a4a8a15b9ed10986df1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/78c3f07cc5fea56abc594a6163778f79776d2a9d6585868d953212149f980d91.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/78da0327465c96c696308908792f640be59a0c7d84c219c7705ca3e3761941fb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/793e00ecff5c83039aced0e9b9619e7cf6c1fb154a98a77fe48d7cd8fc399afb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/795aa7b62aaced46e5fa3ae2f59e7853aa238ae6be497617a92e43e4844dc49f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7a1f92aedb5d4430501e0ef59a2fbc762753c036e0fc3d02f0587272e5eebf6c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7b1a6b172c64d97b893f60c57b0b87fe5008b4f5843b333a6827e7a4bec1e21c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7c5f88194d5856769ca74a9627de419fb1e038fba2f3a0811bd15534255b2463.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7cd89af6086c42ebd0c34ec48dc32685ab9b27ad37d6ff398b56f54865749254.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7d58cb5a35c1e59f8537418f04efcb0fa0bf83ad2020160d5fe13bff6590d560.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7e4d0ae31bc14d803a06cfc7a50a85366c927447d3523caf558659dcd8425c08.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/7f9a089e86a924c3ed3cb44c36c7273097bc134a7ee1a93671aba5812f2bb8f1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/809ba7e841d84dbcd2427af7b0e3210aa44d70cb04acd6448e2e97da7a93e3c0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/81e1cf81fab0343887f13faaffe2ca2eae85ffca672915c3f1d64d3007aee221.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8293ae8b17248ea44986f40c00df2f4e551f6b5d5caa17aa60e35cfb26276ac4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/82ca8591b23bbe549896f4f4c71c951a379a422bd1ae9f61cf318b81b4110fa5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/82f6ccf3849cb70bbff93bb7acc6043ec97b684326467d252a328ff6b3c47d81.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/831c23dab05bb886a31ee26abc4eabcf8f28efea4cd2d27d8e66c4c911ec6b88.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8320a9d02802c2910b957514a34fe2cb351f7c3d9ca38b35ba92e99263989563.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/84cf6639465afff925849859d0b8b9538950985e6cfec8d19f53a451f8337040.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/85aff0136c9f65e5cff923f0182bcfe3a8b1f6f8d2b0b9faac36f8c87d957512.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/85cdf231954c04f5ee0e33af6b4f705f89d5473d690a2ff1086cfa1d55e5984f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/861394d9fe25601115c4246aaa7085252437e5b8b8e7afe666088e4969b62436.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8616869a63e4abfc6d4bd8cb86cd79f498fe5b87960a136522cc7ff68aa715d8.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/869174895744f047aa878d1e7f6b07e196b1086409a346d0e1d5db4e59453ee3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/872df9c0441cae73c51cbb5ddbbcbe0b30774c7e276bbb1dc0a83700adc8f28f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/874c82bb4c4b4eaa90009b2c59e1708172300c49461a259e3d382bdb97ac2d0c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/88ea5062947c42cd312af6aff5d42c43257967bdc1c44b315e48216a09d43a3e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/89497fe6106d9cfb31abd32ec600e5643decc5699aca4f1d6b142cb142166cb6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/89738b69a15c24cd6f8df439b0a1b231e826d72113316e7c05bf93577fc88deb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/89f0d84547b6b344a045a35aa8331138e661cb43a5fd0d08a171e4076a141c47.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8a16ac98b5874f86a261cda38ba226361844d11473b8100a73638b29977a2166.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8a30218166c1ad7f655ab69819807295bfca71e77df72a203b640d9992881fed.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8a83e161d59a379abd6392193900f6103cc778f17e70e3c134f0e6853b76c59e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8a9f20d6de1e7b452ccffa3df2a79ac5b2b6dc6d6adfaa65768d91315f15c27a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8d9e96f5d2826e4989b3cd2534ef66cba20cbdf4909f393a3dd44fd3445709d0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8eb1379f47176423a6f9858e8f5e0e6453712fba6a4d9ce2a06fdb7c714969ab.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/8f930574c8513ff805f7fb5f8a9e603627830b93bf8b059b689f442912c6f221.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/90652ffc22c74a907dec91fd17352f8148eb5391deefd7ec5fd083cfd9d144c9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/907dc91afcbc8a4a701a8203f8c556e7fd53068ed2c9734031d2740907580450.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9129514b59574c17a40c61d7399bbd51f3d8776a05e1b54d6ee95c428a2c1ba1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/923656caf7661e0f692ac347f1a2722b91a8cc17df0fd3153d4508a221240d6e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9288a54eaddd1e57cb78b2ebec00f10bfc6e0cfec132f2885e1a9f895f92cf17.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/92bf0f6460ed2fdb04cc5161dd3bd7a85ab1623d6c0a7038427ce857a2155f51.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/94acc37275a2c4ad98f2d4271be0c8bd102e6f2c57b36e68720e2dbe28f30f93.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/94c284a780faeca04af267fe73ba361ad1b4717e185209e6688b0518293723a4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/95f3ae0a9994a52d9c7ec68ddb899c87e5c50846edf29731092fe3ad51957269.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/96f850e818ee8703ad5ba586d6611b45d3da6f08e9fb31e2d4e728b4832eea27.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/97d4b4d47d60956169d06f0b4d832989a7eaebff2a4f52deac6340f565ec17ae.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/98ba982d4566458feee17078cdb47810d6eabfb99fb1b81463bb055f3ec27321.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/99001ba33b19a0c969683294bf58ec1923e2adf3960148aae58228c2746a87b9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/991c236d3678eec7f00cc02b35897d1c6492ecaf72e0d4df56e7192be89bac94.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/997ff990d77dcd84ee400f9f7ef98cd2a6eb6b5731729414c39927d8fe74aedd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9994b7c0f00421a43e47736bf84272c301a0ccb90b46d07f93106041a4af4e41.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/99b010d7cb03ce51b29829525c092ee50eb5c5eaa8c1db571acf0fde48a45fe5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9a072c867e17b4c6da41b97db93b9ab698f2f567b0bc7d0cd8702a2708836eae.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9a571ca1fda1769c6b42735784c1ec7aaae0cd1bed0346deeeb6743714a5b7a2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9b91d42c262691bb90a18e85294f825b2d7bb4037ae0ad247141e58fbd8eb3f9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9bf783e85c6b5473fbe0d1f1689ca56cf0835a3c092d24bcd041ccba8fc7e896.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9c49f70f00698f3d9bf6db8a33bf41869c78ff32a25b65f57476ee98dd402aee.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9c8339c60dcfe7a232fad534ee1eb6eea2fe4a65fa31a13e5cfcb67a32b325fa.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9c8425a333fc19cbd8a3bc77552a361149b2d56db5ec6a95588482b570ee8a1a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9d025c2c60819078e64d5a755ed95e50d334b608f70424818e4993a53c0071ee.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9d1ef95cfeffb8edf55f778e673ebf1ae5817cabce8f775243a8b6f7486c93f7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9d6b64f51f18fa64a376af1c7cf724bd05a15e1b4bbdb4b1f847fed9fe228ffe.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9d85a40ff5cd8110bb1cca2f8ca8ab73a161c1f344497d8fba13e318aa93965e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9d8725c179ec55260ddb5b6a8593b8fc9f10f16e1732973a68717d0ffcc9450d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9e768f079fa5584900db2ca22072af4ce537919225e6e638c45e6889a591d337.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9e9f95dfbe180489523a819b167d661dfa840b0d526be758077210c20a3296a4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9f17a6078e03b84b84fbe6d145a14b0780f05f523d57b30b2a15e6baf05fa7b7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9f1c5d20cbb2340778c648adfcd0a4bbc33c6cfc0742982bad9cc36aa030875b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/9f899f44737c5be3cc6c583f3b7ce1d51eb40cabf4cebbd59eae49aaab31db57.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a0c26ef1b5693e73e4ff582c1059d078658591fc2ff77cb19e8f32ca820701c2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a1aa5deb8425228fb3146be9d81b9acb6267f0a1c6e0078eb78107b872aff255.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a3eadf1c3c640fff88cc0040e9c4e5b3e69c6cc570481283c3bc7863ae97182d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a440fe3e35318f97d00fff109721febda1bf7431c10ac548e3d7f3c2454aaf6f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a46dae9e05dbf847b282d0fea575497ef6939671ab62053ee941f1da824f4089.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a4d3a4545057d7b3b174aaa06d3b9f10c1467b7a13f6736cf1894041386b5323.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a5164430f7db8db3766b292f6f9977eccb99025972a683898cd4197c9ad28e57.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a5741503896d87b03cee072794f6b75846e802109d85792a739797562af58a35.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a59442f4ce8a065b6e7c1e460b0234044f1a7070f660cd961dd985d748c94403.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a6198a2d751fba4ac5dd902f856146d703d82b8b8aa0ceefac253b1e1f5d2da7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a642186ac87b15b44be20a9c8cd467ab4396602450dc357a5470e8e309fdb0dc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a75a69b3536fd51f95676b0d7e9974f443c91ebc8b05408bd7ca13df1836acd1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a88a24dd599ab67e45e0c8c60c71f7a3d944580dec74f4b3839a43cf2c1a9f15.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a8ff90db637fa501eb2324ef34b05adebf7b56b74558c94beea3d8dc306a5496.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a90e0918f74b411b8ea714cd7aee5c27f5492d49b3a43c59f3c4537bc2d0225c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a9329dcad1a27bd2603d45555af9873346b8fdcbc72020ae7c62ed88d1ac0359.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/a97ede9c02cb418137d868326415a4e50600d1ec2e14553f58973d2a358ae491.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ac52b5683c4660d37c86ddfe4027bdbeb043839d617face4a41c9216756000da.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ac8d84d31940428cec3685f47f889a0580e1c17f7aafd9595f4b49a85c109d7f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/acd8975ff4e1c3ebb5d1dbf11935148334e2270ea8f9037b918fd44e4eee494a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ada1fc9d73a018c31ccc7f6eb882932e5477b9ce172027ac8dab0ea8ffbafcf5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ae97579e56f3dfb381abe233a01931b57d100aeb910c9c772b8e6f80a04c7ee0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/aedfb3f1665b86bab54337eb970a986b42d79cf74bb3e69f4248bf2530612436.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b15b3bf1a1e74e7735e6e48feacff323c89b3d0f3393735d21e9385f46916b86.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b160586572ff7e462794f7a67cdfd65dc2a002a45d9cdbc7011d39116dd71751.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b247fa616e4e7704b391a342ee29afc04f34bf0eee6f54d2494ad3258e4107d4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b4159b4d6deb55908481f4d356747d2861eed4eb54b52b112dfb9f617711b9bc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b46c87f40fbaa56a1631ef4aeccdd0a45a306ec39224ddd2a87154f95a4a7293.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b50f65aed1d4eb07194b2dc5b814a14a88aa8c02aa887e0bfc1372dd0e515a14.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b645d8610ab2e1f301b0958f9412ab8adecc0eb2646a2affce7d7c791d93278d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b6fce26bfe7311f3e753d6a294f1730e88f1117818c058edf9d46a459bfa9a8b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b7d14160461538a55c9da37a28d9c2cb3e9b3c99038e1edd8957e26e6fc8d849.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b8202685e52bcc09478962d76b7094ec93fdac0e22af63d830500cf942d79748.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/b89786c3d24b08b22b98ddd8b7d98ccd53d27796d23e0fa5ca84151ad1c3d208.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ba153d29bcb3d4967458dd6817a73972a538bdb58e21a954d3602ed7b2b380f6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/bb3987f59a9c089a2c2a6fffdb415fd51b8c1ab3b86d5314ce8e99ee4b5422ae.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/bda91c7a89ab05c3c2c9181ed9cef73f1b36bf8e6d23f4e29794a1b3d2a0e128.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/bf9a54c24ce02af93e39d377ae5870728b868e2e40a2d78cb3f483ee80412f14.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/bfc504cfc939ff46b7d9b4b0e61841c167858190d1915b334fc5a72b54e14084.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/bfcb38910c7a7c9e8a1c764eac9965480f33a15e9a9969efe9ffce0fecabd14f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c0a1000f1dccca362b49ad5c6c4d041c081da6e37de6c5222d3e0a84d17daa55.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c1846c0e6fb02c74ef6b4b4c6009f1710ee1166b2efa3592e8c0860e1fc37b79.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c1d2481fde1e6e5509c98f2a041070a6ef867fe5d17294c80d98cdc477c9b2b6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c1f26b8f5cf895ef34a92511c9254f1d8f338519ece7408deccedd3554034440.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c2ebbbdd172519d61256f5fc46049b8dae1350747645098f534ccaf701f22534.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c4235e5062a9ce68d92ba9b0f8921ea29a636e6d757d5c4b04b573ffcf84d507.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c4376c4e58502c8016ccd573d7c153c5d5f7db1e8acc1c698282df3fe87396e0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c45ad85957e1b766447eeea8a14917a3713fc3716a1444c52704bcab496f2171.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c499fae6022c933d585dd0e5cc1aaffea6aa40da34e2847813db4f0405816fd9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c4ad88be047ab5ee8068ddfe7a7380dd5fb9cb5646a57631c25c1d673ed0ff0f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c5e35b62e4cab681765e3c3acf58f2402c0d372809452bb94f210cc818d38534.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c609c2e650efa7edcc20808f220193dfe62860d7584a3f752cc5e9a103f2874f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c68354da5e195a77889476fc9a7bae81896b374ccce5085cdf8c7be35db58293.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c69ac2cf273d3786b569c11b54005a675c4be22fef53a9b6af65870bad3991a0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c70c570b73c013038af7ae738afbdb2d31a7fc62d84f5006b7404709caf6aa44.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c8208681994dcb0be6c478fbbe3834fef78ff3d46693ad18bb43e49563bc3688.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c8291a23199fd061493e3272298df51c1b3458171e1f8ee2de3a6867fca50eb7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c857098396b48a48ce4252de4ff7be45666e0f60d185b2585aae38734e202faf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c860daaa39540b6667311b9098b37e978b3a8ca667894a0e5e53a03a1c87772a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c8a0142db5bc73f25d3f52142691ea6ae64b447c4286839b5acdc0e75f99ba9b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/c95d5a14d706071edff1d3b076f38563c86c1e506fcd5445a157d1619811582f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ca5b2946f3684275fa9d1a01b3dcae472fd3adbe2cc1ffcbcc8a3e59462cac4e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ca62fca024bf1096a2e5604b7752c4b77c8bde612651a4899821d6f561f399d4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/caf4252705c84482315202663c76569324f04fc386464101e04e4d79c7d3938d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/cb04343f512c37820986eba18b48b9a94dff40e896a2fae6f88fc2bcc0129f17.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/cb4f55e781a8367176b30c2477eede7ef536bbd4d5cdb2043b4ea501bf32cd4c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/cce117d9a1420d963659c532867547e7279d45fb5d0ab30c4a8c6e654ed750c3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/cd4590dfd76d8def917486c14a51ac9a31f7359ed61ce6defe6aa7b55da53948.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ce486758f5077464bf4fcd2ea2b5b63226635783e2907b8e35f906fd456d910a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ceafd330704aa213427043a6d8c3c0e2c2b46d2c44958ee7ec6373bb61d7df00.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/cf1a59d641fa9cf3a8a1fd6a97ffa7488b8e52dee71152762b35083b3f3e6cac.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/cf514d508411b2bde9726a172905e4d9d409576cd3a1905487d45fbbb7537f67.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/cf6d69bb29805face2be208ed1b9bb41ccd5c4de2c34b74e5089871bfa5a24b1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d0c3673d3f2a4634d9d68a949bb65b77f779d6b3548301c2269c6c7bb1658a74.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d21336e9b467c32543c3346901236cdaa5cf26b6a5552ae21aff63f79df6f182.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d382f909e9d59377cd5c0f8a0b8b447e21904be036acc1b14fe2c82b41802175.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d4ed809ae09350aaa2ec74da9204fbeead44567b7b22d3c3c4a2b46e68107952.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d4ee25f2c4861065e3fc4017035af6a9e3a8e0585ca7c216b4137f1f397a7cd0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d501525ecc058954adca1f1504bca094696f47beb2b661b531830891112fa722.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d7954a7fe81e501c31099fdb5d3fca650b7e6b430db3ffdaf0a9ce47318570d2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d80f4edeb6d96060f2934ed3e1fdaab39d73f9204178a58f0ec976181b8bdad6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d8e08775cdb11b2e8d95bf806f0dc7dac7147f447aab146a9a8a692ee927fa05.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/d9d0b6b71e96be6e49437d5f22bdbfa5bfd587179f300f89c9aa472e331908f0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/da7b64c41b5b7f45bd324542c3224a66169b2989d07d6c2d1187093c998f2613.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/daca62ffe1ed2bc619beb5d85d1379d1889dbc7a134af0dbde2d587745c487e4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/db89454f96d08b4fac9e64f47294dee6fbffb41d6a616ed3293ecb92ac15c670.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/dbec30ce3419ba0c3099dc5a0446b3f290dae11a063d25f7da114c49b8ebd68e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/dc8f8039c72aa00e017487caac07730c8b53440b7ac2fca98bab4b4abffbbbb2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/dc98687f8343ffe26c1d638aefa476105c992e61eca042505ac326714a8d6633.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/dca719087ba946842b6415d43f3b627cd76579b40e39edb8b21c3b75eb7bdf5e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/dcf70903b7fed5c30d8c82661495e79b56a7119866626e3fc8729cff2be59ee9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/dde3ca364b98522084186f48f190e426811ea8eccb7615e47534b86ec9ce2ebe.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/de8dcd7015d4d0c48636a5b5600b4ee41cc8f35a897dfe667e066c1525d33452.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/df094299b6f87f3a3641fc40f3a92b2e369d79e8cfadfe5f0a6ea0b503d8dba3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/dfb796a723a28ddfb93531531d3bc5d63294f28dc1cd687ea6d2ab448d7c425d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e0bc0654e7c124181cea574b86bf97efc431a18418ba8a954b9c58f1fa4db3eb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e0dbc7d95245b3709ac288eabac9be14a3dd15db9ece3b3985c21be29069e823.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e12b93d139a7f04621eb476c9f9f1525786e3faf1c50d7d51d655a6464fec0f0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e17d715f0486943a5fcefa928642174f103111a878b62be7163cf0ad1f1a8b1a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e2cc3e68ef0b45476ae217ea486256e346f4935d15b83af026978bf4c0efef6e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e3026c7ac9c644667d9885899e186294fe7c2b2a0472be15e96f622fe4c3085d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e3c42bb2c7f187d52b4c9b691938a3f7563ea9125ac4efedce4f1031d8fbd11f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e3c4fcbe7eb4d4bb86d8e5e438f912c37d5cd63c3d20339d1489884f430586af.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e41f826e26174f7a319be3709e5f259adee450d756a504a8d45e67eb47eabed8.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e54b466431ea0b46063b3298f74ac8c5ee1d934a5852b671f66509f21e67678b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e5921dacf63440a851ce272399e35d42c936c573bd9ca93838196820cc5a323d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e59c633fa2292f38c4abcc5d8b64ef55a1d868b2a921dffe5522e20dfa562ca2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e5c6362a6a42ae5472e2da10a9062cf911817d38e7428bbe1e61a708279e3384.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e694832f55d9887cc1491d07434fa3c1646853ea434978497bae24f9a45afee6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e6f3f9d4958c20d840b430046c558565141ba1c2161c393c0058b787982f4da6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e75d27a0f627959d650405603f9b69f2760968b9a0353c28db3c2f14dc214b9d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e7d6cd5bd9e37ad5f1c73fa54c9105821717a34de073972eedbe888609e3d64e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e833714ef5b90d881d11e582f2bf77edba2a819bc03d49d64fb95e21baeab9cc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e84cf8eb02506e35c04d7860d7095f32ff9ba943ca7d363704c99e6907faf05b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e8843fff501fb03137413166f8fe1efc124d4b349ba84f255547a5f36d461ddd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e898c0f5aa1cc6ad6c96baae0c7d966634c76bac3167b26d6524f8d4d225449b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e89ec327f611e6dcc79640bd4c67f1564efd68df68c4bca08b01fa50231ed487.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e8f6212e9cd01985c33a1454c742877c0a44d85e324fabb9444ef1b6c1069c3e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e974e027d633a5f91beddc2c62b1fc0876328f8a6b4486491e6d44a17d0c9272.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/e9829e5881863008d3f951875107698b0dade39b442d1da5f75f94f7acb83c7c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ea971f0e28d6ce342664f2f4e344bbd5397187410487da820768ee352cc5c066.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ea9c5ac1e826bfb2ad562e18470a2cfb6cdb656631c5d1d5251b7036da4f63b9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ea9dcb7eeb7465958839c07df36e1f98782d827a786714c8b30686ef457f18c4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/eb32c626048063575365fb80fda7108cf63f0537dcfd4e7a0c575a2018c50137.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/eb97accc59df91b3afc14b86414edc1a98458b0447dc61cb47cc8c9a44e1051c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/edd30c4b44d88f05857202eba04125189d7248dc520921e371abdfbfc11c59dd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/edd463178e9f6819459cafcb71d8c4b6805f452f4390494fec1256b309ab8b7c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/eec88680471bd2965aa92b7dd72389ef5227ca234346931d84a208e94ecd88b0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/efbd927eb33bb967e4309c1e743d20ab2b2177b6ffde568a984a4661ab1008cd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f00cc2aeb9adda46c05fff67ce23fed6415e21aa5e5cb4f46f07409946ec48e7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f0b65897794489b0c5c6149fd004c199c13db7b7f5407f5e3f972c99926673aa.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f1504baa553d3a3ad098ba55853f826c399c9be37f99ad163f1beed2da700043.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f1c4bb141c211de504df8ff0b3a2caf8c35c1a60f3d45d7cb84876b71044d91b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f35cda97e4d775e9b91522392c19a37a6acc455de6857862327e6286f34bf260.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f5944af030e9daccf1db80f1b717cacc6e3e39f6e19ea689bc192b9533360b05.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f7030847e957c0153f059c6701f9805ee3451b59bdf1090a15f20a4362c691d6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f7ff28f58edf24be603d3f5f98a78a4e9de87ad219fdf459dd32af4ec9c94c41.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f8125570341e9c5c1c184fbfac4f468bbc72c011e8d3629a177a03f4854d7781.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f8604619bce0f1f2242dc9185c3a2fd796042dbec4c8efab930411b866f412eb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f8ba7d3e6bd8ac48bca380c07586454973cb27803b65f95096fa786f7d4f8226.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f9703c1689f43eb7f72e66b382fac0dbc0b26c0c25b376648e4a83a44dcfde37.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f990c14f58b0f40e84ccd628f995c8f16c32db6c06d80f45529da5d87620ca16.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/f9b7e4538316c8f3295d1c6c8bc8abacd2134b09897c6f20e3e74ffc413fbbf3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fa35f3d2398a52c508de6876b9acb6ad84e6e8b0dcd4c28151ed897c4afc8b9c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fa688e80fcff74c2444f71b940e11be27cdc84a42b3fb5723d67cf80f0a3bc49.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fa6fdafa7af9a3bb270ebc4bae8f825be1df96a72dc9209a3b3803a445547d83.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fb1b3dc8743b7e720a9a26138ccc5a245d2eea8211e3584691a2adfeecfb2741.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fb5d7fb9205746780a2da6f04b864a3cfb40bfa69eff5711d9cb4565102ceb4c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fc1689a988ad6428ae855fa6cbde6a79943194e01c115efb511c6e4ac37f95e2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fc3fbd24bde523d975c281ddb7ee9bf8a8a07c39ccff98e41f1a8143412351b2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fcf1ed66fd827e056a4450c6b47f26a6b13adcba5ecf07cb71ea08342e79b95f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fd0ef263735b9a3db424ee872763a13b63e048a873c59730b252d8035d827d4a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fd1a324552f59a1b367213b765b50e3a0de2c3ebbd8b3014ae5e397d8efdde4c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fddf132f1c0055ce7f24dda876288f1a83386ebaf90d188f34832bf6b1495160.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fe4e3b550972ecc35452ba71d058a008cb9c66f27eb0aa6f47695dbaa7f6e69f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/fe61307d43d171793e35c10b98e27768cd3cb7b6bb70f8d55545b746368e987a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ff1ebeb94f73e110fa885f9816f0af765b96556696b34da24af76efb42a7cc7b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/gutenberg-greek/http/ff2895831d0d50fb9da90ba047b29c84b5f71a045d342363eb058d6d4efe6def.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hathitrust/http/25cf2b1caaef2ba94b00f7daedbd98290d20c148335dd6ec1a642cb6c6ea6670.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hathitrust/http/2e10971208a325061e0a182f46c158cd0d732617d6e6890b16369f6df0bfd01b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hathitrust/http/5cfccea630e9ed334ec6898764c9cb52764ce09f392196b34ac00536195d711f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hathitrust/http/5ef7acf91bf0a98c058f05947314076acf98ff91cc49a0f8b2a6b6a4ed5dfa36.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hathitrust/http/6a1315815f881b462040804a13ff16c79869314f6cc480db839e98a5b479eb90.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hathitrust/http/be9bcfa0fd001a4eea801b3b5d3e001e7f5e869ddbdcffc3bd2536917103ec91.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hathitrust/http/d026ef5a7c48472671c74ba2781516a477c490a77b558307722e051d72343a84.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/http/1e2cc9e6d749fc3aede9fdcaf71bd99ff6a41d216c41d29301fa403fc72ec18b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/http/3ac5926c221c73d03f794de2e7686dd07f3de7c9ef3054231d874c5a2b672130.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/http/8ff1c493e9c32d291af7104b06782f41d401dbcfd456be0ffbdfeac64b924a9d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/http/c2d1f3da33f148d6380a2247d5fb9af6afbb1b6cb8903fc1f8f75450ad85455f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/http/d2f393726f89d4e32bc2263a82bbc8fe25a93ee2f904a08ce0d36c1bd5e9306b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/http/ef3d05e6d361311eb67d909d0dab86f899d0ba0a926665ebc524ad14c493169d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/http/fdcfc4da700b71ce0bed47531912099f06b84a7a0e6ce1d4203aed626c02a83a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/probe-local-parliament-30fff481-000033-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/probe-local-parliament-30fff481-000033.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/probe-local-parliament-b4557a07-000021-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/hellenic-parliament/probe-local-parliament-b4557a07-000021.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive-code/http/0200d6f8ab778707efd7e8d82f0bd37350fb31731ab37ba8d50bafe668955040.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive-code/http/da2e4b2610e8d57db11918bd4358a1122d7aca25cf9a981560c3f6e54fa4c5f5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/0200d6f8ab778707efd7e8d82f0bd37350fb31731ab37ba8d50bafe668955040.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/07990f5350d7206fc7ca98b307c809700a1052e0aa48e5560e95436f78738bdd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/0c0596d2ef66ce4cdb76d7b6866fa376154496dc274e20443737f07dda849413.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/0e16d7f066067f066f65796d38254832fc3281baeb437831c8f45f04432db2ad.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/153ffe3eb42989986e40354223a33693457d1fcc61db41089afec13c1e59a003.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/1acc47dc20d930d64b471896e5c25ff9e1365119f9054ddc7c7c53c2285e00f0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/1ca255e64652c4ea4e4eb954557a5bdd671fce07a4f127132047c84d40695c10.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/1f95e2d551ad61fee7186c957799d1d5b488152a1b48adbb2f211ede542fecd6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/2468dcc2a5f2cf32cb1ba6f7a8518d8fb4a571358d7143cbabf9241881e4c12a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/28551dbcccc83830c52c8786c608220c95f847906c21482ec6a0097659048236.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/3885186de257fc43c7db16ddd7f9e6a2250fd6c9fa71586f848750837e68eb7d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/4eda551d83d14197f29f36229d7f3766ca07b64cc309b74aa091e36f94187a1d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/53216afb917572a5f07800449307f93f879ea77628a56adb8460a3109f7a3c28.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/6aafe5319bb32fe142286c41e6fc029a4404c8a44a89368130c31c40a3b50949.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/6e699ff1440a58425cc79553b4a1b92e103a1e3db907e5ca27a391fa4f17a047.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/6eb16927a2810a5f4bb147e5e0d8787aa60da3a9b8d85293bc00d47e639e1cb3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/6ff156a7173828b268bb81dff7b15f62400dbb2ab10ebacc034589e357a2a564.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/74f95f3a91f4ebb912f28bd887913aee9c365478ed53f234e599620c3a673f3a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/77c6a2004e418f3c2d7020682df0f08510f60ec8db33472c1d770f3959946937.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/84b31309f42154b41593810ed7c389c769c3170b31879b0ad7776916b4fee3fe.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/95551c4bd69fdb8030f15c6abcba7a8b3a0789ba0464b4546e30a99709929463.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/97a2f7c22334a42c9e57708d02be6129b55b700a357942efffc17caaaed7af59.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/99d1aada01a30008a4c74e76f4eeec447edd8d0783cc5b7f3007cdd9216c585e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/9bafb19c61b1037c3bb1c8ac94cd5e6334224e1c49835ab7632d621970205a88.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/9d5917f562f6ecd112243a66214c3f437058050c488cfbeba1114786448917fb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/9fd392cf7af1a8291316e7e271a4f08e303bdec2759b33a5a4c91f202cec4b66.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/a2d135e35549e8251912e27e1064c2c2e4c7f3edaacb3f26a9b8238640865e60.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/abd008f6a76731d93179484271887fff8d04e97a0c6661edfb2c88a88c9057e6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/aecb68aec790cf286a6d877211e85bb134901cb92dc8ed55fed2c583bc22489a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/b15b8f193699d9b474ca35538542fc046bb50aa4a7990560e1366ded95274242.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/b207dcf1f83facb2a5ab70800ad3ce69844e3fee2e5445e776c5bcdf07dcc8d8.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/b586b86265a290f4adc8ddb0c73a81604e6ba9e5b17d43c6a25c7c9d26d8af6d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/b5c44b116eb0903645d04709288bf0a16785666006dee1f1f23fd17bc70d5ab3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/b6e03a14181d7bea19810626ee1930b986ccf5703f272f7c7a5863be193d31bf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/b7b460c15d4f0b72e256a9320d5ac6fa4ca738257e16a6d57beb850314019326.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/bff802c4052918f4cc076e7d3b9e16b0578bcfa10905e548db9df1f218280efd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/d24d28705046a7a61b500cfc07e24e59d3264748dad8a1d470675e642dc645fa.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/d3313b202361af3eb63dd6a7f6d2035a12b0454df5e608068024af57b6591460.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/d6cc4ec0c0cfbda70b77f2c0c3bc4f77b8402eb9f8c7d0b3f368b9030e336ee6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/db3ea03878e73fd9dca66d66b82bebddcec0ddd7cfaee6762c6d8a3632530a37.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/e105699e9e39f66fd80e3f77ba0e80153caf453900d15753ab6b112be4a105eb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/e7a1ef054e036d4996a1a0b4755e60e3fa08fa2536483ec83741233a283a552e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/e9c9a0813c12930796147a8017d79f9731965686a319c1bf1024ac7e586400dd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/ec326afb8637ef3df1217dbc7ea60a1558cfc2a258fbe4a3d85aaf735f44a5f7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/eca9f247ef3f493f7bdbc424a0f33b69a91f0fa46d94f7c0803be49037db662c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/f0813c9a8c4a8759d15847636f3df61081f8d29b5fae96aaa94c8cc50e8150bd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/f460981e15330a8757dd5298874fe8c54164d96feaf490d6ecec21bc78898052.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/f66a49c00a6bc0fcc5e32165839374721e4ead1b61ee9ffe890c63bf5fbd32e9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/fb5834676939883bc09cf849810d170be636802d2545d8d0d1fe5a9acec507c9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/http/ff0c2d88e6abdc99a05591be581ef73c255f8a1814bacf4ff9db08f608e34414.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-b33028709-n15-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-b33028709-n15.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-b33028709-n40-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-b33028709-n40.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-bub_gb_rvqeZk26deUC-n35-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-bub_gb_rvqeZk26deUC-n35.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-greekboyathomest01rousuoft-n20-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-greekboyathomest01rousuoft-n20.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-local-cyrillic-252fd568-000316-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-local-cyrillic-252fd568-000316.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-local-cyrillic-363040a9-000273-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-local-cyrillic-363040a9-000273.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-neoellnikaanale00unkngoog-n20-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/internet-archive/probe-neoellnikaanale00unkngoog-n20.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/kosmopolis/http/1100993cc59fa6858800608f6f22b0fe010cd9aa061534e51c5868c7bfc20ceb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/kosmopolis/http/31d471e287e1d253dc0fb11cbfea61a2a4a05b8af4ee26b9b941df7a2e73808a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/kosmopolis/http/b804591d94e261cc8176856a0b341718c74921823bb1aab866bbbedd60ccc014.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/kosmopolis/http/ee5d8721e2177d9221417938db07e80f8b1ff2da1f9996ae5fb04645a13f3e4a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/kosmopolis/http/f292a755031ea021660431f0059e50c4af86f0df96f86495e80c6ccb7af4915b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/laskaridis-travelogues/http/1c53118a4729b0657e9bb3dea5f0e09d2eb10991e8543cbd44f9605993dca884.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/laskaridis-travelogues/http/508675bfd41c43540f793ca4ac497e68d155f0f654b577c77a7333a85a1e4534.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/laskaridis-travelogues/http/6ce59afc06245e0c5a856a4900b75398750ce28afcffa6031760d0b868eb0a46.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/laskaridis-travelogues/http/a32dc9828858c37a5a09edfd167545ee24a38432f3c739dc84ca6bb131177413.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/laskaridis-travelogues/http/a692576a22f2dfcdaa6de17011d452461410806d431dd3086af4ebbdf24b1dfa.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/laskaridis-travelogues/http/c58355ece04a43c1cd372c290fd5cfecc019a9a09293f6ac023a4b5d882dbf88.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/laskaridis-travelogues/http/fbda7a46f03ac797098da6bab4b12c62ac39539d4e4399c9fbcc6cfb2f90dd53.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lekythos/http/19e41736af26995d71022164a7cff26690c21dab4d325333f25548818bfb189f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lekythos/http/3dff54500feb8bd18b5b5f44234373ad5f968f7ccc7d8735832dd2dc6ebd1178.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lekythos/http/8eb6f2a879598229cc462ffb50d4621ec5d3fac3b91a8ce708926a8f3c83b966.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/015111895aa4ea2a8a0ea97e54a01f7c463bb3555155b518b3e8b1159a81c2e6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/0200d6f8ab778707efd7e8d82f0bd37350fb31731ab37ba8d50bafe668955040.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/577657cc0180a2ada5d282976b99e072a3c216b85126767164320c61c8d740b6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/6085a8b0e2aee710504df40ea45e5642eef278de9f7c72544b63ef953ea806cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/9b13849b6aabee0f61f4f3a63c3c4fefe5b4c943d5a2f38f88340ea57cc84281.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/a7bb9cbcc645309e887516120ba61b946f727bfdc602f658d03f7d634c4e0dd9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/c3996221d93d115ddc674fa3a16c0f3a8b35a532882e85e205c1193804769317.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/d0aa55575881b5347a8384d6ad884e00d930662c0c809a0bb13842f483187f7c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/logios-kalchas/http/f419eaf25fbcb1fdb6737f42b079f88bdeaf3effee00652a774e43d6991c671c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/01014ee0da642d3f49218b3e93059462f07b57c55bcd33c7be869881834cc4ff.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/0200d6f8ab778707efd7e8d82f0bd37350fb31731ab37ba8d50bafe668955040.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/0a24f02f87c410ebef730e4e0b653d4fbe00b480b0e986232c6e957a1d290702.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/0e16d7f066067f066f65796d38254832fc3281baeb437831c8f45f04432db2ad.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/1b5c73e51e5622d5f0b8c70744d1e966676d01850f70b7949c14a2a8156035bc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/1c6f6080bc25ad75f2f464a8a9ca169add9a3d76fdfd4b6de9784f3e83d62053.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/3eb99aeab9cea09d1757cc109f2d05e5f44a69efebac4bb09270ca9bbd6f2813.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/6085a8b0e2aee710504df40ea45e5642eef278de9f7c72544b63ef953ea806cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/6f404f674ed987439b4d6574e8231364ad57635924181bbfb6cd4dc7a09f0c1e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/888fb24caeea0748000d2aea1a42bf7a57b5be45eeb45ed760387a4d10b09477.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/8d7d443158ea527d8ad873c1c0a7aea8785c0b5afa5ac96239ff95066dc754e8.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/939d268290316b306080856700a9810f47e84bb27efb2cb902ec26f402fe9255.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/9d38ae77b710c0a13e6e74dd001438c04207ca3fad1636240b29e06b95ebfd2a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/b3a4285ea754d5b921b1001f93104057f1836ec71c2d04b26badc8f6b4676458.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/bab2e36a8b4d32ac99b37adfa600ece9b21e7552efa846577cfedc04c39828ca.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/http/edbc963688d81305c73ec5e721ba472343d459c1c4baa839dde8e934c56b8343.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/probe-dictionary-page-100-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/probe-dictionary-page-100.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/probe-edition-page-20-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/lsj-1940/probe-edition-page-20.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/medusa-veria/http/67c8252bee33a3deff857d97d160d228e7b7e90e2840fdddaf19e1f77d4d3194.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/medusa-veria/http/7838705bea09f7dc1465d548485fdfeed3353baf9555bf7a06431bb37be8fa0a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/medusa-veria/http/ae21707c6628b8d838af722cd91f0d9b0c7ca91efac706d8f38ae92ce75932c5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/national-bank-serbia/http/22d57245b2578d76a3470a886f5711240a614a5c390712bdee416da81152dff5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/national-bank-serbia/http/47bf4da09ff507bea68e6e110eb694dfa380257f2457f115674f09795c622fb9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/national-bank-serbia/http/831d3b4a0868b08909c8fec1c27c9245a5614e08cbc48317d013550ba319f5e3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/national-bank-serbia/http/8edf79c1eb9315888a08aad8a7e47f68545b8ca0b4966686a423dd7a4038a4bd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/national-bank-serbia/http/973265da69890a446ff649395cf450e453eb4581ece2da7ee17d22a3ece4c8b5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/national-bank-serbia/http/ce2d4493e24dacc6aacac049dfb6b9a40eae12f54901c1b004686a2d6542d2c3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/national-bank-serbia/http/f9938ef36c96d4200e73cbf14d7716d6961e006653ad91b7754998e03d452861.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-digital/http/38f6d55bfb964b5c444b84297f5daa1ac2858e362ffb0d3095881b43b1760f0e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-digital/http/5cc4e921dd4d0bb0c1643e314534b270a0d0b3af75d93b775705037628aeb504.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-digital/http/a11725a7defb8780e014279488b24be94382cac12556fb476e3bc81a3d37eb8e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-digital/http/d2817ab1e2fea3fc869aa827057a946373e7dd19ae13a665b9edd7e179d456d0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-digital/http/d28b80040ebc40277f32e519af44a33ff3fd5df481456c57fdbf762ecf59b242.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/208bef9803d4eb830bb9a4513108a005e0ce996404490c00c02519d1d1a64723.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/33001c44bcbf2b93d8040f60664d09b35485fdfe5932f12b24240d806dfdb04e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/58630b60ed011adea48b53d0df91fb483241a3ae3e22f9f96107547818d27d0c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/6173d9994159f227936a81f9fb0b1ce7125624e9b92b49645e78674c1b25bdff.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/6803ebaf3f39e9c1b916d8341a9444706a83d3f41ca11cbdc142e7fd745b0bb2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/6b7ebe4febb9ce7a2cf91e5fbb134e0498141f119a6bb1267874727f0520def4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/acbd3260cafb23f22e86205ba4975d99f8e3f1162de6fb255e5972bca9e6547f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/e62eecaeca73bae862cb06661b1a87899f9d8428dec0ca292f47b5e523dd0ca3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/nlg-newspapers/http/fcc1c86fa47c6f250f2726cb2e97608ff5fc52e6f953f7649e57ccdc7902e5c5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/0307ae266c052e484df6086ca1f5ced5848cd7655486ca86ec284ea4a3dfa8ae.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/234c1b40598a740f99dd6ea685fbc6e3ec2ffef1201cafbea2cb49be53342643.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/28e57ce67fa5d4f4946cf56b1e855f4f2bc14bd67bb9b35db3167947593005cd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/2e778369e03718e4302053ed1634f8bfe546961abcc6a033bc1909b5ef83bd04.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/5780a1b8d4c7c9cec47bd51d0d7019ef344e64e18359ccc6da2d436243557312.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/902789c34d22b15cd78f10dad061deffc916d1b7f619e9b6ad50e0c19a4e7c06.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/9a2a1c184beaf1b7fe5db78a110338cdf31cfedb18d2577825566d012c35b83d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/a5bd25fbebb9dff90bdf506666e21c0236f79fb545de7d034dbad5fa9f00f059.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/d457a5b47842c65a97c571584bfa078b0825aaf01b2a41c538645b9f046a52fb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/http/f0e594ef69d3a791b6b2d145d290003bda353b9371769e91a17297f483e61186.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/probe-local-openarchives-01794a41-000104-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/probe-local-openarchives-01794a41-000104.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/probe-local-openarchives-5b6f51a1-000099-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/openarchives/probe-local-openarchives-5b6f51a1-000099.png` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/0200d6f8ab778707efd7e8d82f0bd37350fb31731ab37ba8d50bafe668955040.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/0659c5d76a872316852c03b2a608fa433b3d7af2783f2c71be3e84e749866418.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/2be07cbfe6870d58f2eb4dc7555956f7da71ee41c429a086bbb5e6db28cf3ef5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/4d4b54b217b10337359a3a824cc1ef375182e0b12cf8794dd46ebc88874801fd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/6085a8b0e2aee710504df40ea45e5642eef278de9f7c72544b63ef953ea806cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/61ba37134a36c09c5ff39b87f7f1ef94e9f78e8bcc8b3b1bb111175cf644430c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/98c77a159b2e3c31298ef51d493a16dd2b18ad286ba1a74625799aa1b565e4dd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/a86ef5ce4c58c60a87a976e4dedd928df0e0924a568f3c4c14f70c08ba34a3df.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/c87be83a076ec74e8b47c111fe6f9cdcd7516955542499ee32211a73cf93cd31.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/cf18424e40b9af59c326276365598efdf637e0036c8386fe17489cff514cc227.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/patrologia-graeca/http/e8074ac87898d453cbeda75c0963562d87a14aeab6efe2a9fc3eb5d516a0d560.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/01ac9f229a4205ef7d5e9536ebe77acef07dc38c95e3e745a63975703ee10425.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/05ccc084f9305024d4b1e597827905d8b79ae4b08a5d2495fb05a9b293d23bce.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/07d236ca91da9751a1c6a6e6424aee8e5db532b33c3f01bd93b1b2add051dcd8.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/22f5edd95b0f6288bad9be621709300162a7250f75ef24ff98a59a28eaa90e81.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/2cbcbcb899e20b55449a8edb5abef94a40382592764912a140510397dc6e9b22.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/3e3c8d57fec9885012623c5bf49d7ef9361692814d5a2f6696149a161206615a.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/402a936a43feb0b233a220dc07ffbc4522097e2e9defbdbdc183509051c895e3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/8193dd60b7be11611d5a39963f4a85d314d322d7d5737f044cf2215ed4dec8bf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/8c6a6a0317513744318a2ccaf7ac6bc244c0ed4f22ab30c61a8ebe356a9904fd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/e33f863ef6cb4ea2019d74d36f91e5466bf8a8e7eadda06da5676802204e27c6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/http/fbe0a1207349aed485b844bb7ab13cb38123e3b77cd43d4516dcd7224154e054.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/probe-historical-page-2342404-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pergamos/probe-historical-page-2342404.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/persee-bch/http/ac378e082dd455919abe25a3ca44b4f44f9867c986303dfa42a6abb9f3b150e9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/005a61279cf2c38bcffc4ce5ca3712c1b570dfe401115c47ebb372e420fcd31f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/0200d6f8ab778707efd7e8d82f0bd37350fb31731ab37ba8d50bafe668955040.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/0844b1179accaef64cd911d55545617963623da18aa232395eceefaafa3095d5.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/0e16d7f066067f066f65796d38254832fc3281baeb437831c8f45f04432db2ad.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/1126e47e4b31b6717d9e92858b234fbfda5b3d054983c9813b6cf0f47498105d.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/12f5c57441a16f6ff6a3b339d4c80331a5fb18e87d011c0fbe67c39e4bb512ba.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/1672cd674150423c2c79f2f0f41dd33f1e93403741361f99f8b8d48610058c9f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/1b1fc20c232ac36899bed9d51082e9f8f536f969e359d25623deb5cc2a02dc76.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/2222bd26416e3621c9f44aa749a33931a86f31d3ceb662b0574f541a5c878937.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/4811b2566c2efd1c8049644ef89062a63dd473b28c9eebfdfb4d03050b661933.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/6085a8b0e2aee710504df40ea45e5642eef278de9f7c72544b63ef953ea806cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/a2d3143fe51dc052299944ec6eb6c31db5905c59c559f4072e19a2a2bb653321.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/baee288b85951113c99b7e1b2c57a97f9ed072071b0baf6e152f9e518e965f94.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/f21f3faf897f232a9caae23de2fc25d0035e647befee0ab4744e6e5603357d16.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/fc4b10d1f16004c49a8954c6273ccf18e9c3114b7b24d912b43e8b453fdf8312.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/http/fe95d85c4cac0c699d09ce94622f69c5f4ac4c2579aec0c70761529e9b9f5987.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/probe-edition-page-425-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/perseus-first1k/probe-edition-page-425.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pleias/http/01993bb7cad5df5a0149079b85274264b5ace9eb1b60be3df461a9e5cf58cac9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pleias/http/0a265d46be739b2f059e0e009430628e7bdd064c1eb77ad7aeb961ea51f4ca45.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pleias/http/176742bfde0aca03061d68d7fcef5ad9877065c28436faf58efc11a1da326fe1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pleias/http/581916b9ab2cf226587e6bc36349df31bd0042b53101c754b111eaa7fb320ad3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pleias/http/f156b7ae343b8054f4e676a3e84e86b66e26b317347028587379bc091442e03c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pleias/http/f98b233d720b3105d6038b9c3e4f3528315b9a1bab0bfa4d48478f91e829a9bd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pogretra/http/0200d6f8ab778707efd7e8d82f0bd37350fb31731ab37ba8d50bafe668955040.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pogretra/http/2603a61c3b9319155a5f5c4c4942713815cad26b1a8441414059b31ddb7d7b4e.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pogretra/http/6085a8b0e2aee710504df40ea45e5642eef278de9f7c72544b63ef953ea806cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pogretra/http/61ba37134a36c09c5ff39b87f7f1ef94e9f78e8bcc8b3b1bb111175cf644430c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pogretra/http/6ee24b2bc64b5ed4b021b4015ef025253c1d87be1a0d1d1e33c360e5941003c9.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/pogretra/http/a62a4cd9c8809e4d8e56c220ec759e88403eeb212b0afd53552579fc60f40004.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/polyton-db/http/0f0e3548b4bce4a5f006a80ec9cb787237bebb288f35c0beb85882056f4b9cb3.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/polyton-db/http/13af39d8e69960bcd5ddbcbfdeeba65a7ab2cffca122f52c0e32ecf6beb316a7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/polyton-db/http/6085a8b0e2aee710504df40ea45e5642eef278de9f7c72544b63ef953ea806cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/polyton-db/http/6c46f98196fa22401a4bc3b78d856a1fa72ad49bcf0f5553cf88164bac0a404f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/psifiothiki/http/77c4e75d364bc84060b7607a856a878b6fda7b9e48ee1158d057c79e1f16edf1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/psifiothiki/http/a46e446ef88486d8ec6f004324b146d8ab81017af3b646354dc8066ca7b35cb1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/psifiothiki/http/ae371a8e54d82239a0415d285b1b111e32e5b60a7b1eef6a7ed511f110551b39.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/psifiothiki/http/f2bf4ea380e42db68dd1048810c2f26ffbfdbb63dbe3b92f588ab037e1606dfb.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/russian-national-library/http/21628b7616dc0e54ae944a2211f625bb55968c96e26e91823f64b19cf62c82cf.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/russian-national-library/http/231a3ef47894cc4f0665b6a74c1320fb9f8fbe0f7f01cd30eeae50b4cfe53d9f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/serbian-national-library/http/18dd0cf801d69b057dbf1b173f5aab5926c945ee69bf247f2be59af8ed2e4c78.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/serbian-national-library/http/739818d7f08c0b59ce286eac13a4f466acbb55772a2b6452eadc9e893df5e8cc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/serbian-national-library/http/a533a3c71cc22b7326c0343858e5cd7ef486bd721358971783373c4d6e06fae2.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/serbian-national-library/http/d34721d02fe590ee44277b4d241c938235de8a5a403f8894737c5a271b486144.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/serbian-national-library/http/e724c763d178ad8b01a69c2328d1cf79bd400c87915ff79fa8370b1ac3e2c6a7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-bg/http/55695fef8eb2abe9be0a5bd09e48e75b7de19ce5d8c9dfb50ee2156bcbd0e0f8.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-bg/http/85f7936709562c54a852c6210403d78abbfc553646b282598e8c14f947d3761c.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/00cc5e80d8d7a6f9bcceb71a3190d4f8ee7ee09d3e59e2519bf2b0c5b82f4fc1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/087db7a689cf6cd6106bb0e4fc2d4e677a4d55b4cabe5b4bdc04ec4b2092d7cc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/0f40f9fe408d6deb63945ced35654e0a26eac78cbe51ced04647caf4bf3e11dd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/1ea930b50e8d95eb59749dd9ab4d6f5350e4fc059b3199fe07b080c19533c5ec.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/20c66063c90a9777b127c68553d66b742ff69dcc0372f741d0bdf195f2f689e0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/25c61248601fffa854d8fe3360f3e226e9211ed427643ef1220dcca20cbedd09.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/3d6bd85e46c9b9ca72f258ad857e63a1ecec139fd986df90cab108738629afc1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/4e0e8d43f4305485c03e95f08c5aa98318a349290510d9d19b7b5c496b182958.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/642869c60e8e4bce47a5e27209cca6d74d2af804770e4c43048aa00fd7dbe901.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/67e16119c408dd393e871b72aa2414ab2d4891c0e60f215977ed880333b76f86.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/70bd0eaa3db648fe9b2727a68afc1972b104a89eafdbf70a19c373914cbadf14.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/7199cbcb697809cf95caec7b8f8a1b97a3308913d9f54751f6981163a700d6c1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/845a2b5dd5ec94fb7ea0337f025f1230c4b6fe73297806882dbada38a3bc64c7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/94ab5424c192001be6342e54af6b372d3a53c0e95acd4329395f84985ee8b3b4.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/9c4b676037c3e08924658bb861326500bcd06a2b60ad0ed8526509833929ae6b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/9ec4b070daa00e12c9a0d4c64f4efd976e014a921236d3a8de641798aac3aa24.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/a605b62bf2d742b4cbbeb388501e1d35dc1c08a5f4622e787524cfd7ef70adf1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/bd0cdbf1f0c00270dc4960087b697532e475c97c62133bc8027fbe9ec7bb3e61.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/cd4196450f8fab73bc6b7c435905b4ae04c542ca2be468aeca15d08a8f77c2f7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/http/d221f84c2569b2db3b60ad64d68788fce90314be0f49cf82dff3adf1a56ef7fc.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/probe-scan-page-10-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-el/probe-scan-page-10.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/025de43cdd02c1cd0924a42db2e0fef640a1a2ed3ca23edb06c2fc97e9251a6b.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/0f40f9fe408d6deb63945ced35654e0a26eac78cbe51ced04647caf4bf3e11dd.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/20c66063c90a9777b127c68553d66b742ff69dcc0372f741d0bdf195f2f689e0.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/60747682e078ff90ba6b217299a15f99f24717d7178ab0e929d619b6056c241f.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/61f884f5b83817fdda79b2ac7e17cb06f581555a0acc823f52109078113ed874.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/625905116c7baf66e1c0402bf8f21b87c9b44f26f19eeced4dc6c7e9eb9e5a73.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/a605b62bf2d742b4cbbeb388501e1d35dc1c08a5f4622e787524cfd7ef70adf1.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/a6f442e64f909d326af24c45062109aaea8ef1ae789d116365621535979bdd69.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/aff16210d6a9c6664ec804c2bd3a07983c3abb7d6f7ba35fcd1cad664fec8671.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/cd4196450f8fab73bc6b7c435905b4ae04c542ca2be468aeca15d08a8f77c2f7.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/http/e01e95169a66ab15c9b4c9002622f7410c719e7f9de67b78bd29c921757ac116.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/probe-scan-edition-page5-preview.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-ru/probe-scan-edition-page5.jpg` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-sr/http/5f606152a6652b13c3f668ea43cc0bd07fdf9c8c5bf9c99b32477cc225a95ba6.body` | B(a) |
| ` D` | `docs/records/harvest/inventory_v2/receipts/wikisource-sr/http/f11e7629200ae371e0364294255da83ae7aea60b03cf9359aa3613fe396e5078.body` | B(a) |
| ` D` | `docs/records/harvest/mixed/admitted.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/plan.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/records.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/rejected.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/repository_order.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/source_preview_A.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/source_preview_B.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/source_preview_C.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/train_pool.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/visual_samples/C_p0415_l0080_expected_crop.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/visual_samples/bad_page_A_heading.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/visual_samples/bad_page_B_heading.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/visual_samples/compiled_C_native.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/visual_samples/sheet_cyrillic_top.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/visual_samples/sheet_greek_latin_cs_top.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/visual_samples/sheet_greek_mono_top.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/visual_samples/sheet_greek_poly_top.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/mixed/visual_samples/sheet_latin_top.jpg` | B(a); B(c) |
| ` D` | `docs/records/harvest/montage_v1/determinism/norule/images/n20-000.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/montage_v1/determinism/norule/images/n20-001.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/montage_v1/flush/comparisons.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/montage_v1/flush/preview_n10.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/oa_rebind_v1/o2/books.jsonl` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/o2/v2_meta1/admitted_all_v2.jsonl` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/o2/v2_meta1/dropped_v2.jsonl` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/o2/v2_meta1/import_real_v2_all.jsonl` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/o2/v2_meta1/import_real_v2_dev.jsonl` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/o2/v2_meta1/import_real_v2_test.jsonl` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/o2/v2_meta1/import_real_v2_train.jsonl` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/o2/v2_meta1/relabels_v2.jsonl` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/0300e4c7c14269132618e34b73f34d2170951f62e24961b753bfdde3724926f2.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/04be2d16f6e5d6a3e1d0432fc26a76d3b7fda2e718dad90bfc477dbcfe530c38.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/09838077f514efcc4ba999b9f9b618017753219b1224d15a127e45c34ff450f7.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/0b6da399b54aaabd6e2a0eb94a8d86aa7767d9e9c6305fd07478492caa92538c.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/0c8fe8e1f46279859b987d62b7d4eb9311f8a5b76e1d624e0c6c837fe37454a2.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/0d9665402d8497f4e04936878dd64096e4667e6bec7ca20cf4812e8af5efa9a3.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/0db25a31678fdc4c22a6db592a0256aed6ba6ebfab5cc4e9c3e4c645ddeaa917.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/0eb2ad7bdb114e93600eb34e575fb09d8625a62e5df293f19ceefe24f2c8aa4d.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/10c0c7144cbf984a7e49b457694ef3a04c8e0b3dc52ecf5d6cd1b90f297b8a79.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/118ee059b03a1a39f942519d23ae5e8da1ac5f919d53d6f19cdb4ce2afc4d896.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/11c0084e9c09ad8016a8c2d76b4f2a2e7b6637a2f31cc1816458612003edff1b.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/13020516edc4be116f3dbe22dc31423f44d0706d7cf20a7b0ff5ad304d697f51.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/14949be1db4efb25fb6a52ad57a57d03f12d844069d1c341bb0141031542270d.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/155e3d59e74ece4f6049f1c7dadc2cab2094de8f517d41927342c7b3738330e5.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/1aa926a157832fa1e6410f49f8b045a12f3c433eab690e0f260279645c18c24d.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/1c4bd42c22c2ca647689911fba363501bc8cac6c66e867598c2f15d8fd0722d6.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/1d3cd90af831e50763997c1f441bdab15ecadd39ad1791265631fc8e5eedf3aa.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/1e401e7b8de8aa2353d5bba2c4e3624c0f090f66fba26c2bfa8a1e66cb1eddf9.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/21758ba8df71e2fe3d056c9454dac13200f4bf91914a70e815082a2eaeab3cb4.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/22de7de03b411b3cda4f66e3b36ec4c7486ab00edfa03a779a55439c0ce57233.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/25f653eae0b7f560c7fdcb8ca12fd458650cd51675524f3da6e728e62d3cf1e2.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/2998f7a633c54fe627381d98d7cb2ed8802578d879c85e367291e83264ee7eb3.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/29d166f6ccc4b36c2bdf86f620a3e4679ce214706f7ac625388b7925ded3f46d.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/2be68715d6f480626d810392780a779b86b0edfe82435d1ee33344603523b451.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/2bfffcbb88c386ea28c2bfecc7947d6b9ad67389a0ae40605052e83df441f580.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/2d4f091adeb27a16de9edbb0ddc566cb2aba6b03fd282ec0696aa714edf95a83.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/2d5e8f6269013074e702ee5e22921f44e18cb938c0cd328fe1087d01ae3b4b4e.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/2dfb4ea7d81513f9014f430db54c7308b6ef90dfe926e3c329821956088c8061.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/2ee904e310c4ea242a15bf3d6650b21177fd7ad8cde1ab5309b88166908f1532.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/32426a6705c81ebcd84eb9433f3634b32dccbcf51b0654e1527edfd0a3cbdec2.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/324d88b666f5db441d6cf05dcbb11e88151f28bebd911773e5895641763e6f4b.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/33d7f6e3f1776820a40f8d909ab47e2c7419cc969992019c5832fcdd81681b6d.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/3516a6a7bd5a372c85e0dd067c7090912e1a621b3bf6ce34e730595700b9670f.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/35832ec2774b4b31b50bc6e7e7fb4074b76c35231fdbe301a4b0d3c83737373d.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/35d7d589f126da5ef7a78fd3c0107ca59b27b11a6cdd0a6dcb303fc1ac5992d4.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/3729c30c0c1a662ad8bd0863a1262a955c2bbebdd4d908a6e4d8df0129bf02b4.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/37e2fb8a14b8efc235c35352f925c5c288c852198d6357fda5b347d8ffbbb75c.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/3ac94d4539b390c2b702ca3ce37ae3cb1ec28045f93c5def09ac38d45004fbac.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/3ced0ec81550878d202792dc42009e092379dcfe3ea3f8ced709d661fa0398a9.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/411b5d8618f65ed756dd2978fce2099f96faf20717f9c5101ba4ff96e277a250.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/49c5d0d14dc22ba642498f9bfc456a83c4574a096495cb7a4a62e6ff43c11034.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/4a1e573f1f0425b65679a4a8061600281a9a07cc5643a0eaf1caa38e5c715126.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/4a3045f75eaca26b1a96fdfa7302da4af459821169d0e56706f02ae79ea2ea26.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/4a715e8c26eafbb9037ced83bdf7e95755947d9827416eaeaa75db7c51994491.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/4c82928f68f2f48cedb372f032dffab1528f442b35732f15aad99aceaf5368a8.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/4cc82d88daef1a709ca8337e0eeed3ef351c43bd8cafae2e29874218b09c5913.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/4dae94697e9c4c25aa1475421c1937591f5f47f9eb37315ece873e3fbe6e4c68.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/4f7b7e4ff62e6c77eca3591bff36de450eefe6126e64b0b6619c370404a3b766.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/4fb0c589b04926d9da9b0dfb455c689fe8c029daf3f1fb9957c3235f67a810f9.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/4fb591b15a19c3c9b7f0813b111a5e4f824100b9ad1bd2dbecacb5a0d4f6aedc.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/53d5e9bd069fb9d4964a146b37d80ff9c12cc8475a6340b0f1804a362cb91985.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/567582274926f4426c6e72ff383ecc7eaa63b7bb2f424f27b2fec8d162c41e11.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/576b3c11f11885cb33b04705ea7310c212236716f7c16e6291670ec8755bbba0.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/64754bd07b6eb035b2aa8358409459b773f85e7c5df9435986c543170e1d18b5.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/648333ef8a74cffdd87fb91ea82c51bb69ce0823dbcf43ead409247fbfea7028.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/64ca564764d9b62a68894857656f71fbbcb657fe972fc452f72a89200f0095f6.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/65108cc84956abd1e3d8bcba79e679ff8fac3904cea5b83cd7100d654bdd2783.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/679bfc55b33d0e15ed07999854634f5aebd892c1557e85eea1c6bfadea356023.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/6875335cb92cf8d7630c3f797d14da020b1732f7406abe1ceb79c46903823efa.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/6bf87f41db8520f91396cb898f6fa8ca89d82435f55d4bc59642fa2bf4c78376.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/6e9e393407e174faa84354e1ac5c6a27938897599f9efdaf082958676f7ccab6.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/6f6cf3d90292cccda3810ee31817e6f93b6424d7f0e096e8bc3cb6293b59cbd7.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/70f5dc9cddc943f9110fdb9b37e8c82bd3ca44d72116a3954c181d9985fb7460.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/710121e4cd802e16c566eb4f701b9cea9067c29db5c8e7621b0b71758de93100.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/711b2c94532e646a98580fa1346254910cb8b25a019bc0716f2b24b99f248ff5.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/713dd8ed815e8bed50bbdc07c8bfc90a04a2be0fac89035c9f38827769cf1c42.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/7328065aef37a4fafe4dac769635227803091770aeb03ee9d598955d673038a8.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/7780bc5cc9a050ff3d328a5edcc796a45418ae9d91aec10b652714a1273bd992.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/780ccd56f6e844937c3eae0475d0f8606f2236408d39ea0adac50c0321fd9a29.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/79bda8198caa50a1560f1ceb954ff1b3764e79914ad724a5f261c81de6af2940.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/7aacd13364c800e8725b7dbf342f0dafdb5e7940256a2cad8367950731de162e.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/7c8c07930b6a19a7422bb18d5289d6d765b8916872f6aaeb0c2e3364f42d3d31.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/7f9cb575211c15ef92b1faa81a2005752ec4f866caef76f9b791266b34722067.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/800940c4f21e461e19b0fd72737bb41219218c9e3685ff7a8f389f7173eb6a78.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/81a5a6f4cb029bf1c0beb3225ce2551af0829bbe92482a491c146ca3a43c1dd6.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/82eecbcf9cab5dad08aa7f10e07d9416d2d94ac7d6b8caedb5ad38d417071ef5.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/8343595a6c673ae674b401c460dd04cfe607d1585c79bee01a8b57774bb55635.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/84acf12d00f36f54229c5de9bd182aec51f04096416d28f3ce91798ed9e86cbc.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/85377e0b66184d0b4d8c3070d30fc14e5cde2a431f9dd913c994be8114ec6dfc.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/859e81d5a1f15a16778380761e448517ef7d5556b515b906681d5808ac53d1a6.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/85ec6a0f616fadf92c8ce27d0e12bdd34b174ea6671ccccfc17e0e3cbb3ab6c2.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/89d7a1f21a26e224185dd89a7bfedfc02ab835cc31ca123d4b3914235b119f2e.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/8a8ba5be25d21fa18489013f46c2ebf1edc724a6f6917f37100d5e97c03190b7.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/8c2b18c36b69a140d233ceb9d2da65d497306c369b956c7a5a8d8339d62ab8d3.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/8d7ebe390c4d4419a205e972c5337b55e90453df871a61a4b53f018a418e2aa5.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/8f4bc8a89d2d1da2a114daf056f50faec2dc46dc1edc27afc17530918cf282f2.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/8fbe09f8a170746c33effe05569bfefd9bfdc0ec1a817398bdd8d840c6face05.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/909cb7377ebde890efee91be582f1f473f4eb1cacda21ffba97fd1609502b59a.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/946b519b809691bef8cedab4a784f862c9339d0516a379b18aba7c6c8a4f1ac6.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/96286b95d970ebcdf6f16de88eed9b54d3fc17178250e8a766925ec969d6192c.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/97c3f2b817fa676a52fcad8a8215ff0e2ac20c74a5bc187663923e88da485112.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/97d87e6b2fb7bcb896119cda132bd14fe3500c137d5685fdff9dbdfd1a40caa1.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/9c95700bec74c59891558676c7d30de4fa2b3c9262d72a4141128b8de79a220f.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/9df674030aa7c45a9ed042a61415c1afecfdd2641272e81d2db03c54292f1f3a.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/9e99933f587fba7fb8e70d0ee94410121dfcb99b656997cd249f949a149951a1.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/9f81fe40096ad31bdd59cf30fa8172d952f61d9c4cc345ad7135701f427339a5.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/a14351cd7265fb74e325af0dc9aadbb851c0b350314fee2b7ae11b28bcbb35b6.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/a369e69d3dba9ffa53320877bcc86909a3f01555b3ca8203e8b880a844acc46e.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/a43f21fe89ead6816446b5a6ed2321033e143b0fefa1f2ad2b743a4670991265.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/a62882e0aca8eae6ee9cb174fb0c63da6b0a7ee393f4a9124813559e1e5cdff0.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/a7bb86e4ccf31d9e58652d89cfc55c143e1b130571be4575221e241d0034f914.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/a8617a861d3c245496212e3aed56d6dc1417294e2793ed0a5cd5bd9236375e38.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/a8922a934ed2e68e5e565bc095d31e23538aa88394c224e04683171b2d22f207.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/aa49945d5b32c768a29d7c5698dfbf6bc123ff93ab97f0f9139fcaf56d6d424f.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/ab5df1373f62c22e789081271059d7f42e616422d2878895984abd40c7d4b618.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/aecd162d6b506b32d19c04bbb2f2f9218cf130ef53c61c9c1fe24ad2db9bfed6.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/afb11f6b0ea689dc4ac5c82760d28867f25aeefb907ee56f9b8e3d9b9fb9b95b.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/b535facddf372c8263ee210f6bf7d87615ad58eceff0b2c8c393fdc0d2e36d52.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/b6a0b7fd5f6b338104473616f9205cd22c8dd2fceeb5c554daef58a9be407703.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/b755723d9577c9cf09d5e83741533cce9b5ec8411bf0b8a45372bd656d1067e0.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/b76a73a2c7934eed85c24a5c25a796b5c2493b84cc6dd8dfb642a2ffdf100582.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/b92c020c55e9263ad1fbb265831a26ba0ba8d8171187ae1c6e5a4a761e6a07ee.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/baa519d02c3c9bb6739f580eef41512d9ed653598095df9e9b5a6b8ac93bb9d5.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/bb5af3dfb6b0a7e862e83ed326e3bd748eb426e23d60d1edc9a1be6116a561cb.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/bca5a0a7a1001f92b99ab26f51298d427873baf19aa0a1cb00af0f80eea28411.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/be3f4984b9c0ad51d0a003d80c625fdeb5b7fe961667e56239f83224e4d73d05.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/bef601d2717647916411cb741845c3237c686689a6c72b21133c9fa5bb2be87a.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/bf2d720ed725980df4f14f20b34e83a5a6feaf607107973cc8b4b83f7b5c852a.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/c1d07e959044c654e5a2d9b58af4e224c5a4a0e0c11c7333d34fc5d37a618d4e.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/c4c96c52f97b6ad88822b44cb7b23c2a95afc8ca75c5dc62184e83a862785005.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/c52c4fc124e2ed2359bbd9f525b2764b34649b3a813c0b4643cf3dadb482cddf.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/c6563c8fd573732ae1c52cd01d821b9678b626536cbb017f6d4a9b6623588547.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/c85d907872fee3e87a7025086721dc9014cd2dbe03b9bf123dd12f3d3039c051.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/c8fa87d934c296c0580c0f14d242816d846fd7bc2665ada5011302fb38ab117b.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/cb4913076aef862ca5cd4621aeadf20f9183905329b9b8215ccbfe7c85da6e8b.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/cb9b8dffc2dcdbd9b73ab6c100f17b2347c95b1d3dafb4e8319eff29125445bd.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/ceac12f986f33af7b0fa5e4a91982462061b896211594e39b2eaabddb8c39a4d.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/d3061cc42da2530b24e24c5861b03b436c85b0f09428c5df45fd64e0509c58d0.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/d5ee252aea56424521a41ffbcaa6a82e1957b9fc7828e31fb15bcd0d4c3efb46.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/d60a8c47597af620cf2977f2aa9341599c9f795293fab33caa6d65bd79df3a3e.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/d76a43b4959e7c5c52b12efa8690a58597aa42bac025a03c4b21aef4906cf2b1.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/da451f86585cd4dd6676eefd321c2a190571237a3a8c49c6c230b8ea9caa729e.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/ddbaee6f1d5b549f5f671d7b714deda9acc5b7112bf133e83741933366e1da4a.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/dea9943f2f67bf473e3cc7f117e7da1324e022b0c5c49c1e604d56ed95aa0cf6.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/e0583efbaadb943e0a1c746c95cb4749796bbeb0b7f40dd31c9aa96387a3f7f1.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/e1734bda55073d1b1114c75af3b1c37ebb2ca76d1ec39e33704b4b845d26c5b2.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/e351346760e874226e8a631d554deeb8acf2d83295afb2c93b5cfb1f4eafbb74.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/e3dbfed543958e73bfb96d81470ed3b81c4a9e346625590d9ad82bfd7bb6f137.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/e646d9b0d693607c224293279b9ec19d22f292e062c526aa90d6905b43f664b8.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/e76ad98d6e6af645b6385aa78a3c84d087c1197e6b593b279853d62ace61eda7.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/e86ec3f2de31fda2156d7533cc612d46df1e90009991d4c5941b9514cf6dbc96.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/eac6feb91bab71987c84a0b72300a947184d62dcd75620dd0bc24bfb670f4115.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/eee90c7c9dc8b376070b0dfaeb1b873785b283a765354145b16eb248096fcd72.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/ef7825f1bf843c302dc9a0d212bdfcd2de6d304bedc302ac69e5c9613ec90558.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/f05a60619af4a82de4477d2bbeab35a30d66777fc73f56b216dfa856a3f2143c.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/fd66ac370fc1439f7657336d4193e503a3247f1f2026d250d3c2cc6ea48edd4e.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/fe8cbd293ee72cab77da329fa39dd7c0537bc3b8084e4a5a79220ed9262d8a64.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/fe9e222719672e2f3e394f837bdec07da03e2ec1e77d539b7e660611de08276f.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/fecf3ce15180087a50bee64d9e49309f333851cf0c557a646aaed65d1bb13028.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/bodies/fee42c139de683951cc3fa1b9471bbda0d418f93a4c2dade1e305509147cca39.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/dione-python-robots.body` | B(a) |
| ` D` | `docs/records/harvest/oa_rebind_v1/receipts/line-exposure.jsonl` | B(a) |
| ` D` | `docs/records/harvest/openarchives/acquisition_results.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/admitted.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/candidates.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/inventory.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/plan.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/records.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/selection.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/t24b_preflight/candidates.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/t24b_preflight/wave5_candidates.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/train_pool.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/openarchives/wave5_candidates.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000107.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000107.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-2c8742589d947f8d749c7ba2-v83646daf-p000023.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-2c8742589d947f8d749c7ba2-v83646daf-p000023.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-3cb3c1caf7324ded3b11c1e5-v223759e7-p000032.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-3cb3c1caf7324ded3b11c1e5-v223759e7-p000032.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-55beb2ad05d46b48576a486d-v1f7c0bc3-p000032.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-55beb2ad05d46b48576a486d-v1f7c0bc3-p000032.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-6c82556081bbe4aada41e496-v553d11a4-p000027.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-6c82556081bbe4aada41e496-v553d11a4-p000027.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-6c82556081bbe4aada41e496-v553d11a4-p000028.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-6c82556081bbe4aada41e496-v553d11a4-p000028.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-7cb612112b4f28a4f704a9cb-v1ec86169-p000043.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-7cb612112b4f28a4f704a9cb-v1ec86169-p000043.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-7cb612112b4f28a4f704a9cb-v1ec86169-p000044.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-7cb612112b4f28a4f704a9cb-v1ec86169-p000044.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-b08a5423fb059fbb291900aa-v3b9bbcc1-p000120.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-b08a5423fb059fbb291900aa-v3b9bbcc1-p000120.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-b08a5423fb059fbb291900aa-v3b9bbcc1-p000121.docai.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/assignments/anemi-b08a5423fb059fbb291900aa-v3b9bbcc1-p000121.vision.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/comparisons.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/failure_images/docai-lost.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/failure_images/docai-merged.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/failure_images/docai-split.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/failure_images/vision-lost.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/failure_images/vision-merged.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/failure_images/vision-split.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/page_reads_v1/sample.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/admitted.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/01c618de-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0590d5cb-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0b33fccd-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0b33fccd-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0b33fccd-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0b33fccd-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0b33fccd-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0b33fccd-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0b33fccd-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/0b33fccd-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/100763df-p000034.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/129cff40-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/129cff40-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/129cff40-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/129cff40-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/129cff40-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/129cff40-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/129cff40-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/129cff40-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/129cff40-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/133c1ea6-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13dcc39a-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/13ea41c1-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000045.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000048.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000055.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000060.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/18369cae-p000064.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000037.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a035976-p000047.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a915aad-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a915aad-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a915aad-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a915aad-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1a915aad-p000037.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1d27927c-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1d27927c-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1d27927c-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1d27927c-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1d27927c-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1d27927c-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1d27927c-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1d27927c-p000035.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1efea0f4-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1efea0f4-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1efea0f4-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1efea0f4-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1efea0f4-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/1efea0f4-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000036.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000043.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/20900789-p000047.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000055.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000071.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000090.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000108.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000127.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000143.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000159.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/26ee7610-p000176.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000038.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000041.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000047.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000051.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/29bccf95-p000055.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000050.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000061.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000069.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000080.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000090.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000098.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000109.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/2b989b7d-p000117.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000043.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000050.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000055.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30d76051-p000057.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000038.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000042.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000044.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000050.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/30fff481-p000053.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3455d0e7-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/37e22f57-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000037.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3bbe5ef7-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000038.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/3be8f3b1-p000043.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/4534d6a1-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000037.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000043.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000053.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000061.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000069.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000078.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000087.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000096.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/48a58eb5-p000102.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/51e4207d-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/51e4207d-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/51e4207d-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/51e4207d-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/51e4207d-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/51e4207d-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/51e4207d-p000036.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/51e4207d-p000037.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/52b46e46-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/548cab64-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/55062aa4-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/55062aa4-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/55062aa4-p000034.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/55062aa4-p000043.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/55062aa4-p000055.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/55062aa4-p000063.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/55062aa4-p000107.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000035.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5674da8d-p000041.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/5a2536ee-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000036.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000043.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000049.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/608b6841-p000051.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/6260d773-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/6260d773-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/6260d773-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/6260d773-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/6260d773-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/6260d773-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/64dc8c3d-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/71d82b4d-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76aff04c-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000036.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000041.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/76d25f50-p000043.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7765f98b-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7a1452d8-p000034.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7aea9867-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7aea9867-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7aea9867-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7aea9867-p000034.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7aea9867-p000038.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7aea9867-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7aea9867-p000046.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7aea9867-p000051.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000036.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7b996aa5-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000035.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000046.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000051.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7bd6c40b-p000055.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000034.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7c411292-p000041.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/7f661ed4-p000034.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/847e1ec1-p000036.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/859c90dc-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/859c90dc-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/859c90dc-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/859c90dc-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/859c90dc-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/859c90dc-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/859c90dc-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/859c90dc-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000037.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/87d33c70-p000038.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000035.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000044.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000048.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/95d812ab-p000051.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000034.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000038.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000041.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/96acdae7-p000043.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9864afa9-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9a494f31-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9a494f31-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9a494f31-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9a494f31-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9a494f31-p000048.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/9a494f31-p000054.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a5914b37-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a5914b37-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a5914b37-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a5914b37-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a5914b37-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a5914b37-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a5914b37-p000036.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a5914b37-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a5914b37-p000043.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a65a813d-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a65a813d-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a65a813d-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a65a813d-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a65a813d-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a65a813d-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a65a813d-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a65a813d-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a8b6ae98-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000045.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000051.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000057.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000063.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/a92e918e-p000069.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/aac90dd4-p000032.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b4557a07-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b567b1c6-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b567b1c6-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b567b1c6-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b567b1c6-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b567b1c6-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b567b1c6-p000046.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b567b1c6-p000060.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b567b1c6-p000083.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/b567b1c6-p000089.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000035.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000046.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000050.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000055.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/be486d8c-p000059.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000003.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/c72a5c9e-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/d4c4e5ce-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/d4c4e5ce-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/d4c4e5ce-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/d4c4e5ce-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/d4c4e5ce-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/d4c4e5ce-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/d4c4e5ce-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000023.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000037.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000045.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/dd625312-p000047.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000037.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/de9da003-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e345c3be-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e345c3be-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e345c3be-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e345c3be-p000017.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e345c3be-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000010.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000034.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000038.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/e8ea7178-p000041.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/ebb7b04b-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/ebb7b04b-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/ebb7b04b-p000012.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000029.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000030.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f1cf6e4b-p000033.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000005.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000009.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000022.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000024.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f36aba38-p000027.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000015.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000020.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000028.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000036.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000040.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000044.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000046.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f401a95f-p000052.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f47c50c8-p000004.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f47c50c8-p000007.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f47c50c8-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f47c50c8-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f47c50c8-p000013.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f47c50c8-p000014.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f47c50c8-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f47c50c8-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f47c50c8-p000019.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000006.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000008.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000011.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000016.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000018.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000021.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000025.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000026.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000031.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000035.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000037.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/assignments/f74236d5-p000039.json.gz` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/inventory.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/plan.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/records.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/rejected.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/parliament/train_pool.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/pilot_v1/crop_smoke_review.png` | B(a); B(c) |
| ` D` | `docs/records/harvest/pilot_v1/input_pages.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/pilot_v1/page_gates.json` | B(a); B(c) |
| ` M` | `docs/records/harvest/pilots_v2/FILES.tsv` | B(a); B(c) |
| ` D` | `docs/records/harvest/pilots_v2/alignment_regions.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/pilots_v2/p1b/alignment.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/pilots_v2/p1b/alignment_pages.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/admitted.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/git_audit.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/reads_d1/records.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/reads_rest/inventory.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/reads_rest/plan.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/reads_rest/records.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/records_all.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/rejected.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/rescue/git_audit.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/rescue/selection.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/round1/selection.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/round2/admitted.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/round2/inventory.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/round2/plan.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/round2/records.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/round2/train_pool.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/transkribus_failed_lines/inventory.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/transkribus_failed_lines/metrics.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/transkribus_failed_lines/three_engines.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/vision_failed_lines/inventory.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/vision_failed_lines/metrics.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/vouli/admitted.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/vouli/inventory.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/vouli/plan.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/vouli/records.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/vouli/rejected.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/vouli/train_pool.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/wikisource/admitted.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/wikisource/plan.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/wikisource/records.jsonl` | B(a); B(c) |
| ` D` | `docs/records/harvest/wikisource/selection.json` | B(a); B(c) |
| ` D` | `docs/records/harvest/wikisource/source_books.json` | B(a); B(c) |

</details>

Untracked source/docs: **3492**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `docs/records/briefs/O1_oa_rebind_finding.md` | B(a); B(c) |
| `docs/records/briefs/O2_dedupe_and_rebind_release.md` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/.gitignore` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/acquire.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/acquire_oa.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/acquire_pdf.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/acquire_perseus.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/acquire_pg.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/acquire_wiki.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/ajax_geometry.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/ajax_outputs.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/ajax_reframe.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/align.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/blind.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/classify.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/delta_p1b.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/discover.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/front_matter.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/make_files.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/p1b_align.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/pilotlib.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/prepare_detector.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/process_reads.py` | B(a); B(c) |
| `docs/records/harvest/pilots_v2/read_pilots.py` | B(a); B(c) |

#### Worktree 29: `sol/l1e-mask`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-l1emask`. Classification: B(b). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.028Z. Full filename lists: `branches.json → worktrees[29]`. 1 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: none.

#### Worktree 30: `opus/sol-reading`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-reading`. Classification: B(d); shared infrastructure. Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.718Z. Full filename lists: `branches.json → worktrees[30]`. 0 cache/environment entries omitted.

<details>
<summary>All 2 modified/deleted source/doc filenames</summary>

| Status | Path | Classification |
|---|---|---|
| ` M` | `tests/fixtures/v45/README.md` | B(d); shared infrastructure |
| ` M` | `tests/test_scan_rollout.py` | B(d) |

</details>

Untracked source/docs: **5**; all names below.

| Path | Classification |
|---|---|
| `docs/records/briefs/SC45R_review.md` | B(d); shared infrastructure |
| `docs/records/briefs/SC45_scanner_v45.md` | B(d); shared infrastructure |
| `tests/fixtures/v45/helper_overwrites.json` | B(d); shared infrastructure |
| `tests/fixtures/v45/recorder_overwrites.json` | B(d); shared infrastructure |
| `tests/fixtures/v45/rejected_recorder_overwrites.json` | B(d); shared infrastructure |

#### Worktree 31: `sol/recut-v1`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut`. Classification: B(b); B(c); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.718Z. Full filename lists: `branches.json → worktrees[31]`. 201 cache/environment entries omitted.

<details>
<summary>All 4 modified/deleted source/doc filenames</summary>

| Status | Path | Classification |
|---|---|---|
| ` M` | `docs/records/harvest/collect_v3_admission/segeval1/launchers/limit_probe.log` | B(b) |
| ` M` | `greekocr/harvest/geometry_observations.py` | B(b) |
| ` M` | `greekocr/harvest/row_inclusion.py` | B(b) |
| ` M` | `pyproject.toml` | shared infrastructure |

</details>

Untracked source/docs: **1938**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/magnitude.py` | B(c) |
| `greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/ownership.py` | B(c) |
| `greekocr/harvest/filtering_assets/crop-tools.py` | B(c) |
| `greekocr/harvest/filtering_assets/segmentation-policy.js` | B(c) |
| `greekocr/harvest/filtering_assets/service.mjs` | B(c) |
| `greekocr/harvest/line_pipeline.py` | B(c) |
| `greekocr/harvest/line_pipeline_adapters.py` | B(c) |
| `greekocr/harvest/line_pipeline_census.py` | B(c) |
| `greekocr/harvest/line_pipeline_native.py` | B(c) |
| `greekocr/harvest/line_pipeline_parallel.py` | B(c) |
| `greekocr/harvest/line_pipeline_runtime.py` | B(c) |
| `greekocr/harvest/line_pipeline_sources.py` | B(c) |
| `greekocr/harvest/numeric_cells.py` | B(b) |
| `scripts/harvest/build_filter_versions.py` | B(c) |
| `scripts/harvest/clariden/bootstrap.py` | B(c) |
| `scripts/harvest/clariden/filter_crop_paths.py` | B(c) |
| `scripts/harvest/clariden/filter_worker.sbatch` | B(c) |
| `scripts/harvest/clariden/package.py` | B(c) |
| `docs/CONTEXT_20261019_sourcing.md` | B(b); B(c); B(d) |
| `docs/records/harvest/collect_v3_admission/ADMW2.bundle` | B(b); B(c); B(d) |
| `docs/records/harvest/collect_v3_admission/ADMW2_CODE.patch` | B(b); B(c); B(d) |
| `docs/records/harvest/collect_v3_admission/admw2/builder_tests.log` | B(b); B(c); B(d) |
| `docs/records/harvest/collect_v3_admission/admw2/input_verification.json` | B(b); B(c); B(d) |
| `docs/records/harvest/collect_v3_admission/admw2/package_commit.py` | B(b); B(c); B(d) |

Other retained artifact changes: 1; exact filenames and statuses are in `other_changes`.

#### Worktree 32: `sol/wikisource-r0`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-wsr0`. Classification: B(a); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.718Z. Full filename lists: `branches.json → worktrees[32]`. 1 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: none.

#### Worktree 33: `opus/spellcheck`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.718Z. Full filename lists: `branches.json → worktrees[33]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **3261**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `artifacts/cq4/cq6c_package/evaluate.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/build_cq6c.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/r1_common.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/r1_extract.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/r1_model.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/r1_train.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/r2_manifest.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/r2_score.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/r2a_digest.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/r2a_job.sbatch` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/r2a_run.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/evidence/seal_cq6c.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/slurm/evaluate.sbatch` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/slurm/prepare.sbatch` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/slurm/smoke.sbatch` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/slurm/train.sbatch` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/test_admission.py` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/test_instrument.py` | B(b); B(d) |
| `artifacts/cq4/CQ6C_HANDOFF.md` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/CQ6C_HANDOFF.md` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/DATA_MANIFEST.json` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/DEPLOY_FILES.txt` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/DEPLOY_SHA256.txt` | B(b); B(d) |
| `artifacts/cq4/cq6c_package/EVALUATION.md` | B(b); B(d) |

Other retained artifact changes: 174; exact filenames and statuses are in `other_changes`.

#### Worktree 35: `opus/spellcheck-l1`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:19.719Z. Full filename lists: `branches.json → worktrees[35]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **150**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `artifacts/labelfix_l1/binding/L1_input_documents.txt` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/binding.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/exclusions.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/input_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/mock_remaining_selection.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/mock_selection.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/parity_crop_sha256.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/parity_expected.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/parity_selection.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/policy.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/remaining_selection.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding/selection.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/L1_input_documents.txt` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/binding.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/exclusions.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/input_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/mock_remaining_selection.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/mock_selection.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/parity_crop_sha256.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/parity_expected.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/parity_selection.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/policy.json` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/remaining_selection.jsonl` | B(b); B(d) |
| `artifacts/labelfix_l1/binding_initial/selection.jsonl` | B(b); B(d) |

Other retained artifact changes: 56; exact filenames and statuses are in `other_changes`.

#### Worktree 36: `opus/spellcheck-l1f`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1f`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:20.409Z. Full filename lists: `branches.json → worktrees[36]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **541**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `artifacts/labelfix_l1r4/build_package.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/check_protected.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/configure.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/__init__.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/__main__.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/__init__.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/admission.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/codec_coverage.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/common.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/e1_common.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/e1_eval.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/e1_readout.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/e2_bakeoff.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/e2_cllg_contract.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/e2_models.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/e2_native.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/e2_parity.py` | B(b); B(d) |
| `artifacts/labelfix_l1r4/deploy/greekocr/_vendor/bench/e2_reader_parity.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/binding/binding.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/combined/shard-00000-receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/detector_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-samples.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/input_receipt.json` | B(b); B(d) |

Other retained artifact changes: 74; exact filenames and statuses are in `other_changes`.

#### Worktree 37: `opus/spellcheck-l1r`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1r`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:20.409Z. Full filename lists: `branches.json → worktrees[37]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **793**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `artifacts/labelfix_l1c/deploy/l1c_census.py` | B(b); B(d) |
| `artifacts/labelfix_l1c/deploy/l1c_job.sbatch` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/__init__.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/__main__.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/__init__.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/admission.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/codec_coverage.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/common.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e1_common.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e1_eval.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e1_readout.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e2_bakeoff.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e2_cllg_contract.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e2_models.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e2_native.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e2_parity.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e2_reader_parity.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/deploy/greekocr/_vendor/bench/e2_teachers.py` | B(b); B(d) |
| `artifacts/labelfix_l1c/deploy/L1C_DEPLOY_SHA256.txt` | B(b); B(d) |
| `artifacts/labelfix_l1c/mock64/CENSUS.json` | B(b); B(d) |
| `artifacts/labelfix_l1c/mock64/CENSUS.md` | B(b); B(d) |
| `artifacts/labelfix_l1c/mock64/binding.json` | B(b); B(d) |
| `artifacts/labelfix_l1c/mock64/input_verification.json` | B(b); B(d) |
| `artifacts/labelfix_l1c/mock64/partials/shard-00000/counts.json` | B(b); B(d) |

Other retained artifact changes: 68; exact filenames and statuses are in `other_changes`.

#### Worktree 38: `opus/spellcheck-l1r2`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1r2`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:20.409Z. Full filename lists: `branches.json → worktrees[38]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **455**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `artifacts/labelfix_l1r2/deploy/greekocr/__init__.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/__main__.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/__init__.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/admission.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/codec_coverage.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/common.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e1_common.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e1_eval.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e1_readout.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e2_bakeoff.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e2_cllg_contract.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e2_models.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e2_native.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e2_parity.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e2_reader_parity.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e2_teachers.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/e2_warmstart.py` | B(b); B(d) |
| `artifacts/labelfix_l1r2/deploy/greekocr/_vendor/bench/extract_lines.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/binding/binding.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/combined/shard-00000-receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/detector_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-samples.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/input_receipt.json` | B(b); B(d) |

Other retained artifact changes: 57; exact filenames and statuses are in `other_changes`.

#### Worktree 39: `opus/spellcheck-l1r3`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-l1r3`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:20.409Z. Full filename lists: `branches.json → worktrees[39]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **493**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `artifacts/labelfix_l1r3/build_l1r3b.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/__init__.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/__main__.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/__init__.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/admission.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/codec_coverage.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/common.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e1_common.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e1_eval.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e1_readout.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e2_bakeoff.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e2_cllg_contract.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e2_models.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e2_native.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e2_parity.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e2_reader_parity.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e2_teachers.py` | B(b); B(d) |
| `artifacts/labelfix_l1r3/deploy/greekocr/_vendor/bench/e2_warmstart.py` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/binding/binding.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/combined/shard-00000-receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/detector_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-receipt.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/detector/shard-00000-samples.json` | B(b); B(d) |
| `artifacts/labelfix_l1e/fixture_v4/mock/historical/input_receipt.json` | B(b); B(d) |

Other retained artifact changes: 57; exact filenames and statuses are in `other_changes`.

#### Worktree 41: `opus/spellcheck-r1`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r1`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:20.409Z. Full filename lists: `branches.json → worktrees[41]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **114**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `artifacts/labelfix_r1/heldout/REJECTED_COLUMN_FILTER.txt` | B(b); B(d) |
| `artifacts/labelfix_r1/heldout/extraction_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/A/data_provenance.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/A/heldout_predictions.jsonl` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/A/heldout_predictions.receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/A/run_binding.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/A/train_log.csv` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/A/training_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/B/data_provenance.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/B/heldout_predictions.jsonl` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/B/heldout_predictions.receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/B/run_binding.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/B/train_log.csv` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/B/training_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/C/data_provenance.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/C/heldout_predictions.jsonl` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/C/heldout_predictions.receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/C/run_binding.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/C/train_log.csv` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/C/training_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/D/data_provenance.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/D/heldout_predictions.jsonl` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/D/heldout_predictions.receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r1/mock_font/D/run_binding.json` | B(b); B(d) |

Other retained artifact changes: 145; exact filenames and statuses are in `other_changes`.

#### Worktree 42: `opus/r2-cards`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r2cards`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:50.475Z. Full filename lists: `branches.json → worktrees[42]`. 0 cache/environment entries omitted.

<details>
<summary>All 1 modified/deleted source/doc filenames</summary>

| Status | Path | Classification |
|---|---|---|
| ` M` | `docs/records/briefs/CQ4_capitals_witness_and_topup_build.md` | B(b); B(d) |

</details>

Untracked source/docs: **9505**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `artifacts/cq1/launchers/limit_probe.sh` | B(b); B(d) |
| `artifacts/cq1/launchers/run_bed.sh` | B(b); B(d) |
| `artifacts/cq1/launchers/run_read.sh` | B(b); B(d) |
| `artifacts/cq4/AGGREGATE.sh` | B(b); B(d) |
| `artifacts/cq4/BUILD.sh` | B(b); B(d) |
| `artifacts/cq4/BUILD_REREAD.sh` | B(b); B(d) |
| `artifacts/cq4/RUN_ALL.sh` | B(b); B(d) |
| `artifacts/cq4/launchers/limit_probe.sh` | B(b); B(d) |
| `artifacts/cq4/launchers/run_read.sh` | B(b); B(d) |
| `artifacts/cq4/prior_cq4/inventory.py` | B(b); B(d) |
| `artifacts/cq4/prior_cq4b/inventory.py` | B(b); B(d) |
| `artifacts/cq4/prior_cq4b/test_inventory.py` | B(b); B(d) |
| `artifacts/cq4/tools/build.py` | B(b); B(d) |
| `artifacts/cq4/tools/closure.py` | B(b); B(d) |
| `artifacts/cq4/tools/common.py` | B(b); B(d) |
| `artifacts/cq4/tools/finalize.py` | B(b); B(d) |
| `artifacts/cq4/tools/inventory.py` | B(b); B(d) |
| `artifacts/cq4/tools/replay_literal.py` | B(b); B(d) |
| `artifacts/cq1/BUILD.md` | B(b); B(d) |
| `artifacts/cq1/GUIDE_NOTES.md` | B(b); B(d) |
| `artifacts/cq1/HANDOVER.md` | B(b); B(d) |
| `artifacts/cq1/adaptations.diff` | B(b); B(d) |
| `artifacts/cq1/build_hashes.json` | B(b); B(d) |
| `artifacts/cq1/build_receipt.json` | B(b); B(d) |

Other retained artifact changes: 1463; exact filenames and statuses are in `other_changes`.

#### Worktree 43: `opus/r2-prep`

Path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-r2prep`. Classification: B(b); B(d). Raw state: **DIRTY**. Measured 2026-10-19T18:54:20.904Z. Full filename lists: `branches.json → worktrees[43]`. 0 cache/environment entries omitted.

Modified/deleted source/docs: none.

Untracked source/docs: **991**; selected names below; complete names are in the JSON array, with no truncation.

| Path | Classification |
|---|---|
| `artifacts/labelfix_r2/write_r2p2_report.py` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/B/dev/extraction_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/B/native/extraction_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/B/overlay_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/B/witness/extraction_receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/data_provenance.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_01.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_02.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_03.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_04.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_05.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_06.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_07.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_08.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_09.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_10.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_11.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_12.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_13.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_14.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/exposure_epoch_15.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/heldout_predictions.jsonl` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/heldout_predictions.receipt.json` | B(b); B(d) |
| `artifacts/labelfix_r2/output_3683130/C/20261016/run_binding.json` | B(b); B(d) |

Other retained artifact changes: 2511; exact filenames and statuses are in `other_changes`.

### Material uncommitted findings

- **B(b)/B(c), recut:** tracked edits to `greekocr/harvest/geometry_observations.py`, `greekocr/harvest/row_inclusion.py` and `pyproject.toml`; untracked `line_pipeline*.py`, filtering assets, native runtime and numerous review/evidence files. These are not part of the pinned recut tip or the cleanup branch created from it. Similar named committed files exist on seg-census; byte equality of working copies was not audited.
- **B(a)/B(c), source inventory:** 1,825 tracked deletions plus one tracked modification and 3,492 untracked source/doc files. Their cause, intent and recoverability are unknown. A branch-tip comparison cannot inventory this as committed work.
- **A(ii)/A(iii), ff-plan:** seven tracked planning/handoff/roster edits, despite its committed head being contained in the consolidated branch. **B(d)/shared, scanner:** two tracked test/fixture-doc edits and five untracked files. **B(a)/B(c), collector:** seven tracked gallery/receipt edits and 29 untracked source/doc files.
- **B(b), secondary corrections:** seven untracked source/test/context files. **B(b)/B(c), seg-census:** two untracked evidence files. Correction/R2/cleanup worktrees also contain substantial untracked review artifacts; all names are in the JSON. “Contained” or “CLOSED” never covers those working files.

## Locally recorded remote state

No fetch or network access. The live remote and last fetch time are **UNKNOWN**. Remote tip dates are commit dates, not evidence of freshness.

| Recorded ref | Classification | SHA / target | Last commit date |
|---|---|---|---|
| `origin/HEAD` | shared infrastructure | → `origin/main` | symbolic ref |
| `origin/main` | shared infrastructure | `703d4c9f977fe54ef323ee12d8ce3491cc645686` | 2026-10-12T12:19:47+03:00 |
| `origin/astra/page-lines-4` | shared infrastructure | `5b35ec091c1065ef400775bc284a6e6d27ceeb6a` | 2026-10-10T10:51:14+03:00 |

| Local branch | Classification | Configured upstream | Ahead | Behind |
|---|---|---|---:|---:|
| `main` | A(i); B(a); B(b); shared infrastructure | `origin/main` | 53 | 2 |
| `readme-public` | shared infrastructure | `origin/main` | 0 | 0 |

All other 54 local branches have no configured upstream in the branch metadata. `astra/page-lines-4` is 3 ahead / 0 behind the recorded `origin/astra/page-lines-4`, but does not track it. `readme-public` equals recorded `origin/main`; local main is 53 ahead / 2 behind that ref. No publication status is inferred for branches without tracking.

## Coordinator questions

1. B(b)/B(c): which recut working-copy edits and untracked pipeline copies are the authoritative uncommitted work, versus copies already committed on seg-census?
2. B(a)/B(c): are the 1,825 source-inventory deletions and 3,492 untracked files intentional, and which must be preserved as live evidence?
3. A(ii)/A(iii): should consolidated `astra/ff-merged` be the development comparison head, while keeping the dirty planner docs and parked reference/Rust experiments separately accounted for? Its closing note explicitly says the allocation finished with partial goals.
4. B(a)/B(b)/B(d): which uncontained UNSURE survey, census, mask, Wikisource and R2 heads still supply live consumers? Current owner gate rules supersede the older mixed-script allowances; source provenance and historical measurements remain separate evidence.
5. Shared infrastructure: how should the two recorded `origin/main`-only README commits relate to the owner's new README brief? Live remote state remains unknown.

No target-layout recommendation or integration execution is included.

