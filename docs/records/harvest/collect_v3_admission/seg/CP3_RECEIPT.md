# SEG-CP3b receipt

2026-10-18. Base HEAD `788c7ad8c681bd6b23a3bf26d88973b45b4dea72`. The inherited CP3 list named `89e0a59d7c9fc4c47a193b7e657def8ca3ad0dcc`; the intervening commit changes only the CP3 review/fix briefs, verified with `git diff --name-status`. The guard rejected that stale base before this explicit refresh.
Authority: SEG-CP3b fix brief, SEG-CP3 build constraints, and ASTRA-SEG1 plan items 2–3. **B1 resolved using (a), row-level unavailability. CP3 acceptance: 4/4 met. M1 process attribution remains partially unverified because the managed sandbox denies `ps`.** No CP4+ work or publication. The candidate remains explicitly unqualified for admission; CP1 GATE_FAIL and its protected artifacts remain unchanged.

| CP3 acceptance requirement | Measured value | Result |
|---|---|---|
| 22/22 owner KEEP preserved by merged screen | **22/22**, 0 false drops, 0 unresolved | Met |
| 7/7 C1 merge witnesses detected | **7/7**, 0 unresolved, 0 misses | Met |
| 6/6 pinned-gallery merge witnesses detected | **6/6**, 0 unresolved, 0 misses | Met |
| 0 planted single-row/half-letter/column false positives | **0/12** negative controls | Met |

Original denominators are unchanged. C1/gallery overlap is **5 ids**, yielding **8 distinct merge witnesses**, all detected. All six formerly unavailable Gazette witnesses (`l0039`, `l0138`, `l0141`, `l0146`, `l0162`, `l0228`) now have measured native row evidence. `CP3_verification.json` includes their original crop/source bindings, supported rows and local runs. Synthetic bars verify mechanics, not lexical whole-word truth or generalization.

## B1 diagnosis

The invalid structural record is `row-00077`, detector **line index 77**, reading order **72**, piece **0**, `single:column-0001:block-0001`, segment index **13**, segment position **[13,9,2]**, geometry source `joint-classes`. It is not the Google crop suffix `l0077`. The serialized detector cache has no unique text label for this structural row.

Its x interval is **[255,1609)**, x-height **13.2229114831 px**. The saved baseline slopes from **1488.240** to **1424.554**, and meanline from **1475.017** to **1411.331**. The minimum baseline-minus-meanline remains **13.222 px**: the body guides do not invert. Its **52 assigned native component ids**, retained verbatim in `CP3b_geometry_audit.json`, contain **2,784 pixels**, with exact owned bbox **[255,1405,1609,1492]**. This long sloping record spans the horizontal extents of text in both page columns; that observation does not establish correct physical ownership.

Saved top ranges **1412.148–1483.704** and bottom **1417.868–1485.802**. **516/1354 columns** have bottom below top. At **x=327**, top is **1483.686**, bottom **1474.799**, difference **−8.887 px**. This cannot be explained by three-decimal serialization rounding. The existing collector `greekocr/pages/lines.py::_boundaries()` sets each top to the maximum seam above and bottom to the minimum seam below, after extending and smoothing neighbouring seams; it does not enforce top < bottom after this aggregation. The saved row exhibits the resulting crossed envelope while its body guides stay positive. Attribution to conflicting extended seams is an inference from that code and the saved curves; the cache does not retain each intermediate seam. No detector/boundary refit was run to manufacture a corrected record.

Neighbour arrays reference detector **line indices**, not positions in the filtered cache row list. Structural identities resolve above **73,74,76** to `row-00073`, `row-00074`, `row-00076`; below **75,78,79** to `row-00075`, `row-00078`, `row-00079`; left/right are null. The adapter resolves dependencies using structural `line_indices`.

There is no defensible one-label assignment. Saved Google crop overlaps with these owned pixels are reported, not promoted to native row truth: `l0195` (“Κοινοτική ή Αστυνομική Αρχή ή Ελλη-”) contains 1,815 assigned pixels; `l0198` (“νική Τράπεζα στην οποία θα δηλώνεται ότι :”) contains 1,247; `l0197` (“Δημόσια, Δημοτική, Κα”) contains 1,065. These crops overlap one another. The audit lists all twelve intersecting labelled crops, including the much smaller left-column overlaps. All six required merge witnesses are vertically remote from this row, with crop y intervals **827–896, 408–476, 408–476, 526–597, 820–891, 2064–2130**, respectively. None intersects its conservative quarantine envelope or depends on this row as a recorded neighbour.

## Whole-cache read-only census

`audit_cp3b_geometry.py` enumerated **all 99** existing `detector.json.gz` records under live `run/cache/g1b` (**75**) and isolated `seg/CP3_geometry` (**24**), totaling **9,975 row records**. Every enumerated page has W1/W2 metadata: **38 W1**, **61 W2**. The snapshot found **181 inverted rows on 10 pages**. **Four** of these rows also contain zero-height columns; **zero additional degenerate-only rows**, **zero nonpositive body-guide rows**. No geometry payload was changed. Every enumerated payload SHA, per-row minimum, negative/zero column count and recorded tranche is in `CP3b_geometry_audit.json`.

| Page | Tranche | Inverted rows |
|---|---|---:|
| `bsb_poly1850--b05b8313ad5d52e2--s003` | W1 | 1 |
| `gazette_modern--0020420cfe156a73--s000` | W1 | 1 |
| `gazette_modern--35ddd7b10ced9323--s000` | W2 | 3 |
| `gazette_modern--3eb4bdd4963fb2eb--s000` | W2 | 9 |
| `gazette_modern--681c44c04401998f--s000` | W2 | 8 |
| `gazette_modern--8f9af1b3948911aa--s000` | W2 | 22 |
| `gazette_modern--8fa1fb650976300d--s000` | W2 | 6 |
| `gazette_modern--c003210b1a688317--s000` | W2 | 3 |
| `gazette_modern--fa6a958aa9c8a7c5--s000` | W1 | 3 |
| `serbia--6b577f99816f3331--s006` | W2 | 125 |

This is the complete enumerated cache snapshot, not a historical count of every collected page: the running collector discards regenerable caches, and the live tree is not an atomic snapshot. Absent/discarded geometry cannot be assessed by this census.

## Resolution (a), without preparation or geometry changes

The adapter preserves the invalid raw record with `status=invalid_geometry`, its reason, minimum bottom-minus-top, native component ids, curves and a conservative unavailable box covering owned ink and all saved guide extents. It reports `invalid_geometry_count` per page. Valid rows still pass unchanged vendor `prepare_row()`. Source/frame/options/code/payload hashes, structure, native components, positive body guides and finite curve shapes remain strict page-level checks. Only a nonpositive envelope becomes row-local unavailability; unrelated contract errors still reject the page.

The shared consumer checks quarantine **before counting**: intersection with the invalid row, explicit invalid target, or a relevant row's saved neighbour dependency returns unavailable. `merged` is null, never false/KEEP or detected. The invalid row is neither repaired nor silently removed. Healthy row counts disclose the page's invalid count. Tests cover inverted and exactly degenerate envelopes, remote valid crops, invalid target/crop/neighbour cases, and malformed curves/body/native ids that must still fail.

Option (a) is supported because the required witnesses are remote and have complete independent valid-row support. Option (b) would repeat an already performed once-per-source preparation without evidence of a different valid result. **New preparations: 0**. The original **24** exclusive source-bound attempts, **24** receipts and **122.843 s archival detector-time sum** are unchanged; all **120** prepared-evidence SHAs still match the original commit list.

CP2 now loads **23/24** witness pages. The unrelated NLG page `nlg--6146c0455e0103d2--s001` remains rejected for **41,068** label/ink disagreement pixels; its required DROP remains unresolved outside the CP3 merge denominators. Acceptance here does not resolve CP4 or qualify the full admission union.

## M1: measured write assurance and remaining process evidence

`CP3b_collector_window.json` records a **25.010-second** observation with **no SEG execution**, only stat and sleep. `W2/crops` mtime/ctime changed from **1792279463537785358** to **1792279488852134750 ns**; `cache/g1b` changed from **1792279463538105445** to **1792279488852417003 ns**. This establishes live-root changes independent of SEG execution.

The requested `ps -axo pid,lstart,command` failed with **PermissionError: [Errno 1] Operation not permitted: 'ps'** in the managed sandbox. There is no permitted escalation. The user identifies the writer as collector `materialize --tranche W2`, started 00:20; its current PID/start/command could not be independently verified here. Live `collector_pids.json` contains supervisor 70258 / worker 70269, but these belong to an older collector receipt and are **not evidence of the current materialize PID**. A request for the missing `ps` output was made; no process identity is fabricated.

Read-only source inspection supports the stated mechanism: collector `collect_v3/storage.py::materialize()` calls `runner.finalize()`; `page_rows()` calls `pipeline.analyse()` with `W2/crops`; `discard_page_work()` removes generated crops and `cache/g1b/<page>`. These paths explain both directory metadata changes. Without the requested process listing this is consistent attribution, not a verified PID-bound result. **M1 is partial**, pending that listing.

The assurance is therefore limited to: **no write by SEG code during guarded measurement; live root changed during a no-SEG window, consistent with the user-identified collector materialize process (PID unverified)**. No historical, whole-tree, all-process immutability claim is made.

## Validation and protected artifacts

**321 tests passed**, including **31 CP3 cases** (twelve new CP3b regressions) and the original twelve negative planted controls. Command:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp3b-tests-final3 tests/test_seg_cp3.py tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
```

`verify_cp3.py` reran the original frozen denominators against the original pre-screen feature population and unchanged crops. Its Python audit guard recorded **0 runtime write attempts**, **0 detector/network calls**, **0 preparations during measurement**. All **9 protected artifact SHAs** and **28,798/28,798 manifest-referenced crop PNG SHAs** match their frozen values. No admission, manifest, crop PNG, ownership parameters, live-root lock or publication artifact was written by SEG. No OCR/reading run, network access, spend, staging or commit was performed. Repository writes are confined to the isolated CP3 review/code/test artifacts; other drafts remain outside scope.

`CP3_COMMIT_LIST.json` and its guard bind **13** exact implementation/test/evidence files, read-only dependencies, base HEAD, and all **120 unchanged preparation files**. The manifest is not self-hashed; the independently scoped guard never stages, commits or publishes. No later-checkpoint acceptance or deployment is claimed.

SEG-CP3b: done | B1: a (explicit row unavailability) | inverted rows in cache: 181 | acceptance: 4/4 met | KEEP 22/22? | C1 7/7 | gallery 6/6 | planted FP 0 | publish actions: 0 | tests: 321 passed
