# SEG-CP5c receipt — coordinator rulings applied, 4/4 revised acceptance

18 October 2026. Authority: `docs/records/briefs/SEG_CP5c_rulings.md`, applying only the H1/H4 rulings from `docs/records/reviews/SEG_CP5_review_2.md`. All earlier CP5 constraints remain. Base HEAD, exact files and read-only dependencies are bound in `CP5_COMMIT_LIST.json`. CP5 closure does not qualify public admission: `gate=False`, GATE_FAIL remains, and no later-checkpoint execution or publication occurred.

## Rulings and implementation

1. Unknown local axes alone may inherit vertical from the existing `axis_regions` / `resolve_regions` page evidence. Every intersecting region must be vertical both in discovery and native block measurement; mixed, unresolved or absent regions give no inheritance. Region envelopes describe ink rather than padded crop canvases: line membership uses containment of the crop centre, with all intersecting regions required to agree. This accommodates the small canvas margin outside ebdc4d07's ink-region envelope; mere edge overlap gives no inheritance. Measured horizontal axes are returned unchanged. No axis hints, new detector, recognizer, OSD, ownership retuning or height/width axis decision were added.
2. Each measured native row records `decision_source`: `measured`, `regional` or `unknown`. Regional records retain page source SHA/frame, crop box and resolved regional records in the decision hash. Saved local observations cannot reuse page-context evidence without revalidation.
3. Unknown after inheritance stays `rotated=null`, status `orientation_unknown`. Only the orientation policy fails open. `compose_cp5` preserves the unknown measured union separately from policy admission and sets `verified_keep=false`. Structural/crossing positives and CP4c geometry-unavailable policy still drop independently. Matrices keep admitted unknowns outside verified TN/resolved denominators.

Coordinator condition (verbatim): **"if the CP7 fresh 100-card read finds ≥ 1 rotated crop admitted, orientation returns to CP5 before publication"**.

## Fresh native acceptance

| Requirement | Standalone | Union / composition |
|---|---|---|
| Adjudicated rotated positives | **4/4**, two measured + two regional; zero unknown | **4/4** positive measured unions, even with other screens unavailable |
| KEEP false drops | **0/22** | **0/22**; 22 policy admissions, **17 verified**, five orientation unknown |
| Upright control false drops | **0/11** | **0/11** orientation + clean structural/crossing controls; **0/5** text-eligible controls |
| Horizontal misses | C1 **0/6**, gallery **0/6** | **0**; overlap five, seven distinct native witnesses |
| Unknown accounting | Explicit status, source and ids | Admitted by orientation only, never counted as verified |

The measured rotated rows are `gazette_modern--8213d28643843855--s000-l0144` and `gazette_modern--83c3182a4175392a--s000-l0259`. Regional inheritance resolves `gazette_modern--b9f59878fb904d91--s000-l0034` and `gazette_modern--ebdc4d07ff8c4122--s000-l0265`. All four original crops remain in the standalone denominator. Text-first composition still reaches only 1/4 rotated rows and 19/22 KEEP; rejected metadata/text cases do not shrink standalone acceptance.

KEEP unknown after inheritance (**5**):

- `bsb_poly1850--e18cacecef3b4590--s005-l0076`
- `gazette_modern--0d0b2233a81e355c--s000-l0019`
- `gazette_modern--4b5e54c14bfb5810--s000-l0031`
- `gazette_modern--54876940c2de96c3--s000-l0062`
- `kosmopolis--109d033afd51aea6--s000-l0019`

The first, fourth and fifth have mixed local evidence; the second and third have line/block disagreement. Page evidence supplies no accepted unmixed vertical inheritance. These remain orientation unknown rather than certified horizontal lines. The earlier l0019 diagnosis remains: raw block vertical votes conflict with the actual horizontal native line and line diagnostic; the local disagreement veto prevents a false vertical DROP.

## CP7 counting hooks only

`CP5_verification.json:cp7_orientation_unknown_hooks` groups all **110** post-inheritance unknown-axis native census rows by declared source × class. Each group contains counts and exact ids, plus the **105** unknown rows the old rotated-crop policy would exclude. Membership in the exact 1,681-id `w1_rotated_crop_ids.txt` and the `h>w ∧ ≥4 non-space characters` rule are retained independently, with their deduplicated union count/ids. No old heuristic supplies a new exclusion or truth label. Per-row flags are also retained. These are hooks for CP7; no fresh draw, reading or replay was performed.

Fresh census: **1715** native crops, all **1,681** historical ids individually audited. Historical final axes: `{"unknown": 105, "vertical": 1576}`; KEEP final axes: `{"horizontal": 17, "unknown": 5}`. Full standalone, text-eligible and union matrices retain unknowns separately in `CP5_verification.json`.

## CP3/CP4 unchanged

Fresh `verify_cp4.py` output equals the earlier `CP5_cp4_verification.json` exactly. Fresh `verify_cp4_controls.py` and `review_cp4c.py` outputs likewise exactly match their earlier artifacts:

- KEEP **22/22**, C1 **6/6**, gallery **6/6**.
- D **9/9 composed**, **8/9 measured**, one unavailable NLG; no non-unavailable unresolved required structural case.
- Fragments **0/12 drops**, with the previously reported one unresolved; CP3 planted false positives **0/11**, complete short-run mechanics **10/10**, recorded native one-letter words **3/3**.
- Frozen ledger SHA `76ea2d35f374b20326db3ab434e94d57d942d3d610128551e1475b1c8f172f0f`; ownership `801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8`.

## Tests, reproduction and preservation

**406 passed**, zero skips/xfails, including **40 CP5 tests**. New tests cover unknown in vertical/unmixed and mixed regions, measured horizontal preservation, unresolved regional evidence, edge overlap without membership, fail-open versus unknown measurement/verified-keep accounting, independent structural positives and saved regional revalidation. Existing native separator and horizontal planted regressions remain in the suite.

Use `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` with `PYTHONDONTWRITEBYTECODE=1` and `-B`:

```sh
python -B docs/records/harvest/collect_v3_admission/seg/verify_cp4.py
python -B docs/records/harvest/collect_v3_admission/seg/verify_cp4_controls.py
python -B docs/records/harvest/collect_v3_admission/seg/review_cp4c.py
python -B docs/records/harvest/collect_v3_admission/seg/diagnose_cp5.py
python -B docs/records/harvest/collect_v3_admission/seg/verify_cp5.py
python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/seg-cp5c-final-tests tests/test_seg_cp5.py tests/test_seg_cp4c.py tests/test_seg_cp4.py tests/test_seg_cp3.py tests/test_seg_cp2.py tests/test_harvest_admission.py tests/test_adm5b_schema.py tests/test_adm5c_variants.py tests/test_neighbour_words.py tests/test_seg_cp1.py
python -B docs/records/harvest/collect_v3_admission/seg/guard_cp5_commit.py
```

Verifiers write stdout only; redirect reproduction into `/tmp`. The final census recorded **zero forbidden attempts**, **zero publish actions**; native audit hooks forbid filesystem mutation, network, processes, page detection, recognizer polarity and OSD. Polynomial-fit warnings remain in `CP5_measurement.log`. Original missing historical crops are reconstructed byte-identically only in memory. The 23 existing separator inventories are reused without preparation or attempt-claim changes. `CP5_native_diagnostics.json` was rerun natively.

The verifier/guard check all nine protected artifacts and **28,798 retained PNGs**, source/cache/dependency hashes and base HEAD. Eight tracked protected files are compared with HEAD; the untracked census remains explicitly snapshot-only in `protected_without_HEAD`. No live-run writes/locks, admission/manifest/crop modifications, Git index changes, commits or publish actions were performed. Existing unrelated drafts remain outside the exact review scope. Collector KNOWN_ISSUES handoff remains recorded at its earlier commit `7a026c3d7`.

SEG-CP5c: done | rotated 4/4 (measured 2, regional 2) | KEEP false drops 0/22 | KEEP unknown after inheritance 5 | upright FP 0 | horizontal misses 0 | CP3/CP4 unchanged: yes | hooks: added | tests: 406 passed
