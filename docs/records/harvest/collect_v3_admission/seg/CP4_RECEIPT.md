# SEG-CP4c receipt

18 October 2026. Base HEAD `c79d9ec47e7cabd39924c088ead9b7cab5d9f92b` (CP4c brief; prior CP4b receipt base `9937b6206c8ba80e681ae1aabca6428c9f020f58`). Applied only the coordinator's two rulings in `docs/records/briefs/SEG_CP4c_rulings.md`, following `docs/records/reviews/SEG_CP4_review_2.md`. **CP3 native acceptance passes; CP4 acceptance is 5/5 under the revised composed policy.** The collector documentation destination is blocked by this session's filesystem policy, so the complete requested task is not yet done.

## Coordinator rulings

1. Added `geometry_unavailable` to `greekocr.harvest.admission.RULES`, with table version `ADM5c-20261018.CP4c` and tool version `SEG-20261018.CP4c`. Invalid/inconsistent geometry, unavailable targets, and missing/stale binding fail closed. Public output fields are unchanged; only the rule vocabulary changes. Full binding validation now precedes the qualification check, so an unqualified tag cannot hide stale/invalid geometry. Valid bound geometry retains the previous qualification behavior. This does not authorize applying or publishing the candidate.

   `nlg--6146c0455e0103d2--s001-l0006` is **DROP under the composed decision**, solely because geometry is unavailable. It remains **unavailable and undetected**: required DROP is **9/9 composed, 8/9 measured**. `CP4_verification.json` records its raw status, composed decision, separate unavailable list, and measured-only matrices. Unavailable geometry never enters measured-detection or verified-KEEP counts. Unresolved word/letter evidence remains unresolved; it is not silently recategorized as unavailable geometry.

   The CP7 counting hook is the existing overlapping `drops_per_rule` and `drops_per_source_class[source + "|" + class]` counters, now initialized with the new rule id. A temporary five-row fixture verifies three losses in the correct source × class group. **No real admission file was evaluated or rewritten.**

2. Reclassified c068 (`gazette_modern--2e613d9290dd13d4--s000-l0209`) through `seg/freeze_truth.py` as **label-error witness, non-gating**. It remains in `cases`, retains its original card/verdict provenance and measured negative, and has a separate `non_gating_witnesses` entry. It is neither a required merge witness nor a KEEP. Reason, verbatim:

   > The card's verdict is a label error (label appends 'μένης αργίλλου' from the next line, which is only partly inside the crop). The neighbour word is clipped (token box 216–257×1233–1254 vs crop 217–715×1211–1249); under the owner's whole-word standard a clipped neighbour word is not a drop reason. Coordinator ruling 18 Oct.

   Re-frozen ledger SHA-256: **`76ea2d35f374b20326db3ab434e94d57d942d3d610128551e1475b1c8f172f0f`**. The builder binds itself and the coordinator brief. Only this adjudication and its provenance change: KEEP=22, required DROP=9, C1=6, gallery merges=6; C1/gallery overlap=5 and distinct merge witnesses=7. The original 101,098 feature rows, 33,301 eligible rows, ordered eligible-id SHA and all prior source bindings are unchanged. The eighth owner issue remains unidentified.

## Fresh acceptance on the re-frozen ledger

| Acceptance | Result | Evidence |
|---|---:|---|
| CP3 KEEP | 22/22 measured | `CP4_CP3_verification.json` |
| CP3 C1 | 6/6 measured | same |
| CP3 gallery | 6/6 measured | same |
| CP3 planted negatives | 0/11 false positives | `CP4_controls.json:cp3_planted`, executed single-row/half-letter/column/rule controls |
| CP4 KEEP | 22/22 measured; 0 false drops composed | `CP4_verification.json` |
| CP4 C1 / gallery | 6/6 / 6/6 measured | same |
| Required DROP | **9/9 composed; 8/9 measured** | `composed_drops` versus `drops` |
| Geometry unavailable (required KEEP/DROP) | **1**, dropped by policy | separate `geometry_unavailable` list |
| Unresolved required, excluding unavailable | **0** | `required_unresolved_non_unavailable`; covers KEEP, D, C1 and gallery |
| Original fragment controls | neighbour 0/9; union 0/9 drops | `CP4_controls.json` |
| Expanded fragment controls | neighbour 0/12; union 0/12 drops | same; one unresolved, **not a verified KEEP** |
| Mechanical short positives | neighbour 10/10; union 10/10 | same; mechanics only |
| Recorded native short probes | **3/3**, 0 unresolved | tokens 549 Ο, 567 Ο, 652 ο; source/response-bound, row-local |

For neighbour, structural and union separately, measured-only required-ledger matrices remain **TP=8, FP=0, FN=0, TN=22, unknown=1**. Measured precision/recall remain 8/8 (Wilson 95% `[0.6755924351,1]`), while measured required-positive coverage remains 8/9. KEEP false-drop and survivor-defect rates are 0/22 (`[0,0.1486548746]`). Composed DROP coverage adds one explicit policy loss; it does not improve measured recall. The borderline stays non-gating with negative neighbour/structural/union evidence. These selected development witnesses do not establish generalization.

## Preserved CP4b evidence and scope

H1's complete-group-before-owner repair, H2's full native parent/split-child extent conservation, and H3's explicitly bound recorded-word evidence are unchanged. `CP4_C1_conflict.json` retains c068's measured negative and token 943 box `[216,1233,257,1254]` against crop `[217,1211,715,1249]`. The rule, geometry, ownership parameters (`801d517e…`) and detector behavior were not retuned to restore a clipped-word positive.

The historical CP4b cache census is preserved, not rerun against concurrent materialization: **75 live entries/3 inconsistent**, **24 inherited/1 inconsistent**, **1 fallback/1 inconsistent**. Excluding the duplicate fallback gives 4/99 ≈4%; including it gives 5/100 entries representing four distinct pages. Live mismatches are 3,517, 2,959 and 1,742 pixels; NLG has 41,068 label-without-foreground pixels in `[1102,0,1192,1724]`. The read-only diagnosis identifies labeling before scan-edge foreground clearing in collector `greekocr/pages/pixels.py:625,643–648`. The sole authorized fallback remains **1 attempt, 1 serialized cache, 0 usable pages**, with identical inherited/fallback payload hashes. No preparation was repeated or validation relaxed.

The CP3b historical census remains **181 inverted rows on 10 pages**, among **9,975 rows in 99 caches** (75 live + 24 isolated; 38 W1 + 61 W2), four also containing zero-height columns and no additional degenerate-only rows. Evidence: `CP3b_geometry_audit.json` and `CP3_RECEIPT.md`. Envelope aggregation in `greekocr/pages/lines.py::_boundaries()` is the recorded code diagnosis, with seam-conflict attribution explicitly an inference.

## Collector documentation write blocked

The complete document is prepared as `seg/CP4c_KNOWN_ISSUES.md`, with both issues marked **for a later fix**, exact evidence paths and the CP3b/CP4b counts above. Intended destination:

`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/KNOWN_ISSUES.md`

The tool rejected the write: **“patch rejected: writing outside of the project; rejected by user approval settings”**. This session permits writes only to sol-recut and temporary directories; approval policy is `never`. No sol-collect code or documentation was changed. `CP4_COMMIT_LIST.json` includes a separate **sol-collect docs-only commit group**, target SHA and prepared source, marked `blocked_outside_writable_roots`. The local guard verifies the prepared bytes and reports that status; it does not pretend the target has been written. This remaining filesystem action prevents reporting the requested `known issues: written` / `SEG-CP4c: done` line honestly.

## Tests and reproduction

**366 tests passed** in the final suite (`CP4_pytest.log`), including inconsistent-plane fail-closed, inverted target fail-closed, valid geometry unchanged, stale unqualified binding, unresolved targets, preservation of unavailable measurement under composition, unchanged valid composed KEEP, and source × class policy-loss counting. Existing text-policy assertions now include the additional failure when geometry is absent; historical published schema/hash checks retain their original version.

Run with `PYTHONDONTWRITEBYTECODE=1` and the exact collector interpreter:

```sh
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp4c-final-tests tests/test_seg_cp4c.py tests/test_seg_cp4.py tests/test_seg_cp3.py tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
```

The same interpreter ran `seg/freeze_truth.py` to re-freeze, then `seg/verify_cp4_controls.py` → `CP4_controls.json`, `seg/verify_cp4.py` → `CP4_verification.json`, and `seg/verify_cp3.py` → `CP4_CP3_verification.json`. `seg/guard_cp4_commit.py` checks the regenerated commit list read-only. The commit list is review material; no Git staging/commits were requested or made.

Native verifiers report **0 runtime write attempts and 0 detector/network calls**, all **9 protected artifact hashes** unchanged, and all **28,798 crop PNG hashes** matching their manifest. All **120 inherited cache-file hashes** and **5 isolated fallback-file hashes** remain bound by the guard. No admission application, crop/mask change, network, collector preparation, training, CP5+ implementation, publication, or write/lock to the live run root occurred. The old NW1b `GATE_FAIL.md` remains untouched; its historical qualification report cannot authorize publication of this new checkpoint.

SEG-CP4c: blocked (collector docs write) | geometry_unavailable rule: added | ledger sha: 76ea2d35f374b20326db3ab434e94d57d942d3d610128551e1475b1c8f172f0f (c068 non-gating) | KEEP 22/22 | C1 6/6 | gallery 6/6 | D composed 9/9 (measured 8/9) | fragment union 0/12 | short native 3/3 | unresolved required (non-unavailable) 0 | known issues: prepared; target write blocked | tests: 366 passed
