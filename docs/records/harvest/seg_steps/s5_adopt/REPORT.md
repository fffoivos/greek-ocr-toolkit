# SEG10 — integration fixes ported; segmentation 0.9-s5 adopted

Completed the two exact census_03 integration ports and the single inclusive length-band adoption. Native replay: **1,705/1,705** match the saved S4 measurements and new-band native decisions; **zero measurement differences**. Exact changed owner-judged IDs: **59 before gate exclusions, 38 after**, both equal the saved s5 sets. Specified suite: **248 passed in 4.21s**, zero failures. The lead/coordinator commits; no commit was made.

## Authority and boundaries

**Coordinator decision, not an owner ruling.** The task supplies this provenance: the coordinator adopted 0.30–2.00 under the owner's end-to-end mandate (“you don't have to wait for me, resolve these end to end”), recorded it in the coordinator ledger on **19 Oct 2026 at 21:34**, and reported it to the owner in writing: “frozen the configuration at 0.9-s4 measurement, gate 0.3, band 0.30–2.00, one band for everything”. No objection since was reported in the task. This run does not claim an independent ledger/message readback. The provenance is also in the manifest and pipeline README.

One band applies to numeric/non-numeric and small/non-small rows. Mode 2, padding 1.5, the S4 small path, gate, detector, predictor and geometry remain unchanged. The band was fitted on owner marks; finite-set improvements do not establish independent census generalization.

Start: clean `cleanup/20261019` at `b56e9b9f82020d888841610e02d435be32785c2f` (CLEAN4L); CLEAN4T `65c978494` is committed in its ancestry. `git status --porcelain` was empty. Network OFF; no readers, corpus census, deployment or `.git` writes. Only tiny mock census plumbing ran inside the requested tests. Protected package and remote evidence file sizes/mtimes/ctimes are unchanged; absent historical census03_baseline paths were not recreated.

Coordinator commits advanced HEAD during the run to `f810aa35eb918d4aad8bdb9190c5062cc9c4a5cd`; their changed files are `['docs/programme_20261019/NIGHT_STATE.json']`. They contain no SEG10 source, test or replay changes. This task issued no mutating git command.

## Exact integration ports

`automatic_result()` now identifies digit/separator/digit adjacency with the supplied regex. Candidate rows `1.234`, `12 - 3`, `4·5` produce no automatic verified-negative; `Α.Β. 12`, `12.`, `-5` produce `verified_no_change`. Census deduplication unions configured held-out crop hashes into the existing observed held-out set and retains the existing `heldout_crop_identity` rule. The mock fixtures prove config-only protection with zero dev/test observations, observed protection, and an unaffected train row.

[port_check.json](port_check.json): both complete hunks, including all added bytes and context, equal the archived diff after normalizing line offsets. Full hunk diff:

```diff
--- census_02/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py
+++ census_03/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py
@@ -313,7 +313,7 @@
     status = "verified_no_change"
     if tool == "dashes":
         status, evidence = "tag_only", dict(dashes=[dict(offset=i, character=c) for i, c in enumerate(text) if c in "-–—−"], policy="no qualified general dash repair")
-    elif tool == "numerics" and not any(c in text for c in ".-·"):
+    elif tool == "numerics" and not re.search(r"\d\s*[.\-·]\s*\d", text):
         evidence = dict(candidate_scan="no adjacent numeric separator candidate")
     elif tool == "cyrillic":
         lang = {s.lower() for s in expected["languages"]}
--- census_02/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py
+++ census_03/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py
@@ -162,6 +162,8 @@
     def deduplicate(self):
         """Exact crop identity and held-out protection; never silently union parents."""
         held_crops={r[0] for r in self.db.execute("SELECT DISTINCT json_extract(payload,'$.crop_sha256') FROM observations WHERE split!='train' AND split!='unassigned'")}
+        binding=json.loads(self.db.execute("SELECT value FROM run WHERE key='binding'").fetchone()[0])
+        held_crops.update(binding.get("config",{}).get("final_policy",{}).get("heldout_crop_sha256",[]))
         groups={}
         for parent,i,payload,decision in self.db.execute("SELECT o.parent,o.id,o.payload,d.payload FROM observations o JOIN decisions d USING(parent,id) WHERE o.split='train' ORDER BY o.parent,o.id"):
             row=json.loads(payload);d=json.loads(decision)
```

## Policy and versions

Old policy SHA256: `e5b635ff9a04cc66f454a68e01ce9773229672e655b3ee08296ee5c0d149ee15`. New: `5888fe704e6170b51081d6fa4200a725d2b29f0c70301f238faf7b32088b5b99`. `service.mjs` hashes these exact policy bytes; the service itself is unchanged. Only `lower=.5,upper=1.5` → `lower=.30,upper=2.00` changes in both `boxLengthJudgement` and `combinedBoxJudgement`.

| Tool | Version | Iteration count | Recorded change |
| --- | --- | --- | --- |
| Segmentation | 0.9-s4 → 0.9-s5 | 12 → 13 | length band 0.30–2.00 (coordinator decision under the owner's end-to-end mandate, 19 Oct 21:34; fitted on owner marks, s5) |
| Numerics | 0.2 → 0.3 | 2 → 3 | Exact numeric-adjacency automatic-negative fix |
| Census | 0.5 → 0.6 | 5 → 6 | Configured held-out crop union |
| Pipeline | 0.3 → 0.3.1 | patch ID | Both integration fixes and policy adoption |

Ownership: `Pipeline` calls `automatic_result(row, tool, ..., self.versions[tool]["version"], self.versions[tool]["digest"], ...)`; the changed branch emits a **numerics** result, so its iteration is numerics. The manifest previously listed only its legacy N1 artifact; its owning integration component `line_pipeline.py` is now also fingerprinted there. Shared component hashes refresh for other tools without inventing unrelated generations.

The 0.n tools still have n documented iterations; segmentation preserves the established eight base iterations plus s1–s5 convention (13 total). `iteration_count == len(documented_iterations)` is verified for every tool. `build_filter_versions.py` regenerated the manifest normally: **no fallback**. All component hashes and digests revalidate; an in-memory fresh build equals the saved JSON. Local component keys now name this main-next checkout rather than the manifest's former segcensus prefix.

## Native replay and acceptance

The unchanged S4 worker factory, S2 source-context handling, S1 network audit hook and 120-second per-row timeout processed the original 150+888+250 crops and 417 non-control typology crops. Saved input rows and crop SHA256s were checked. Each fresh S5 result equals the native service applied to its saved S4 evidence, ignoring only elapsed seconds, version label and policy fingerprint. All other evidence, frame, warnings, binding and decisions match. Runtime: **64.11113916710019 s**. No detector or predictor fit was run.

There are **111 cohort-entry verdict flips** (overlap between panels is retained), all caused by a length-band change and carrying `length:` reasons. Three additional rows stay DROP but advance from length to the unchanged padding reason; they are listed with saved ratios in [reason_only.jsonl](reason_only.jsonl).

Among **533 unique owner-judged IDs**, the changed set equals the 59 `scheme=overall` IDs in `s5/changed_lines.jsonl` exactly; its numeric-scheme rows are duplicates/subsets. Removing content-gate 0.3 failures leaves exactly the same **38 IDs** as the gate re-report. [owner_judged_flips.jsonl](owner_judged_flips.jsonl) records them. [acceptance_differences.jsonl](acceptance_differences.jsonl) and [measurement_differences.jsonl](measurement_differences.jsonl) are empty. **No differing lines; no tuning.**

Scores retain S4 definitions: 150 FP=DROP/fine, FN=KEEP/faulty, UNC=every uncertain; 888 agreement uses explicit ratings only; owner marks use latest timestamp then file order; typology excludes the 20 controls and scores its 185 explicit marks. Content gate 0.3 removes saved failing rows, as in gate_rereport; it does not change segmentation verdicts.

| Metric | Unfiltered s4 → s5 | Gate 0.3 failures removed: s4 → s5 |
| --- | --- | --- |
| 150 FP/FN/UNC | 16/15/0 → 4/19/0 (n=150) | 11/15/0 → 2/18/0 (n=137) |
| 888 rated agreement | 109/135 → 117/135 | 77/91 → 82/91 |
| Owner marks agreement | 189/235 → 209/235 | 157/191 → 170/191 |
| Typology marked agreement | 160/185 → 173/185 | 153/176 → 165/176 |
| 250 cells KEEP/DROP/UNC | 230/15/5 → 242/3/5 | 205/3/5 → 205/3/5 (n=213) |

Cohort denominators before → after gate: 150→137, 888→819, 250→213, 417→284. Scored denominators: 135→91 ratings, 235→191 marks, 185→176 typology marks. Full confusion matrices are in [summary.json](summary.json).

| Overall band objective | S4 0.50–1.50 fd/fk | S5 0.30–2.00 fd/fk |
| --- | --- | --- |
| Before content gate (500 population; 490 objective) | 59/16 | 10/24 |
| Gate failures removed (420 population; 412 objective) | 38/16 | 5/20 |

All four values exactly equal the s5/gate_rereport fixed-band figures. As before, owner-DROP notes that length cannot assess are outside the objective (10 before /8 after), but remain in the population and changed-ID check. This is why these objective errors differ from the separate panels' confusion counts. Wider bounds reduce false drops while some false keeps increase; the recorded band is adopted without tuning.

## Tests and layout compatibility

`tests/test_content_gate.py`, `test_line_pipeline.py`, `test_seg_{gate,deskew,curve,small}.py`, and `test_integration_fixes.py`: **`248 passed in 4.21s`**, **0 failed**. New mode-2 boundary tests exercise regular and small branches: 0.30/2.00 KEEP; 0.2999/2.0001 DROP.

The existing band expectation changes only its default endpoints. Two identity assertions also need the authorized version/fingerprint changes: the clear-row fixture retains exact output equality after its expected pipeline stamp changes to 0.3.1; the non-small geometry comparison explicitly verifies differing policy hashes and compares every remaining normalized field/evidence byte. The historic fixtures were not rewritten. All test diffs:

```diff
diff --git a/tests/test_content_gate.py b/tests/test_content_gate.py
index f81114348..06ef389e1 100644
--- a/tests/test_content_gate.py
+++ b/tests/test_content_gate.py
@@ -56,7 +56,10 @@ def test_codec_mark_keeps_segmentation_and_content_repair():
 
 
 def test_clear_row_matches_pre_change_output_exactly():
-    assert engine().evaluate(row()) == json.loads((ARTIFACTS / 'clear-before.json').read_text())
+    before = json.loads((ARTIFACTS / 'clear-before.json').read_text())
+    assert before['pipeline_version'] == '0.3'
+    before['pipeline_version'] = '0.3.1'
+    assert engine().evaluate(row()) == before
 
 
 @pytest.mark.parametrize('text,disposition', [('日', 'HOLD'), ('Αθηνa', 'DROP')])
diff --git a/tests/test_seg_gate.py b/tests/test_seg_gate.py
index dfb541135..4000d2278 100644
--- a/tests/test_seg_gate.py
+++ b/tests/test_seg_gate.py
@@ -50,7 +50,7 @@ def test_cut_witness_decides_by_frozen_length(native):
     assert box == before['evidence']['box_evidence']
     ratio = (answer['evidence']['characters']+1)/(box['predictions'][2]+1)
     assert answer['evidence']['padding_evidence']['total_padding_line_heights'] <= 1.5
-    assert answer['verdict'] == ('DROP' if ratio < .5 or ratio > 1.5 else 'KEEP')
+    assert answer['verdict'] == ('DROP' if ratio < .30 or ratio > 2.00 else 'KEEP')
     print(f'{rid}: length ratio={ratio!r}; verdict={answer["verdict"]}')
 
 
@@ -234,3 +234,17 @@ def test_s2_horizontal_orientation_byte_identical_to_s1(native,size):
     a,af=old.orient_crop(image,None,None,QuarterTurn)
     b,bf=native.crop_tools.orient_crop(image,None,None,QuarterTurn)
     assert a.tobytes()==b.tobytes() and af==bf
+
+
+@pytest.mark.parametrize('chars,verdict', [(2999, 'KEEP'), (19999, 'KEEP'), (2998, 'DROP'), (20000, 'DROP')])
+def test_s5_mode2_length_boundaries(native, chars, verdict):
+    # (chars+1)/(9999+1) = .30, 2.00, .2999, 2.0001.
+    # Both orchestration branches exercise the two default-band entry points.
+    for small in (False, True):
+        evidence = dict(characters=chars, small_segment=small,
+            box_evidence=dict(available=True, predictions=[None, None, 9999]),
+            padding_evidence=dict(available=True, total_padding_line_heights=0),
+            lines=[dict(side='main', votes=1)])
+        result = native.service.call(dict(operation='decide', policy_sha256=native.policy_sha, evidence=evidence))
+        assert result['verdict'] == verdict
+        assert result['reason'].startswith('length:')
diff --git a/tests/test_seg_small.py b/tests/test_seg_small.py
index 556fc1286..fd237632e 100644
--- a/tests/test_seg_small.py
+++ b/tests/test_seg_small.py
@@ -56,5 +56,8 @@ def test_non_small_native_result_is_byte_identical_to_s3(turned,tmp_path):
  old,new=replay.worker('s3'),replay.worker()
  try:a,b=old(row),new(row)
  finally:old.close();new.close()
+ # S5 changes the default band and its policy fingerprint, not geometry.
+ assert a['policy_sha256'] != b['policy_sha256']
+ a=dict(a);b=dict(b);a.pop('policy_sha256');b.pop('policy_sha256')
  assert replay.canonical(replay.norm(a))==replay.canonical(replay.norm(b))
  assert replay.canonical(a['evidence'])==replay.canonical(b['evidence'])
```

CLEAN3 moved saved replay JSONL inputs into `../greek-ocr-data`; CLEAN4L moved historical scripts under `docs/records`. Existing tests still reference the old paths and historical scripts calculate the root at their original depth. [prepare_view.py](prepare_view.py) creates a temporary layout view under `/private/tmp`, verifies mirrored file SHA256s against CLEAN3 receipts, links current production assets, and copies the four historical replay scripts and seven tests byte for byte at their original depth. It also copies the unchanged gate03 analysis script for its original root calculation. Source/archives are not restored or edited. [view_receipt.json](view_receipt.json) records the exact paths and verified hashes. This is the only replay/test layout fallback; manifest regeneration had none.

The initial suite result was `9 failed, 239 passed in 4.39s`: four missing compatibility-view fixtures, three old version/hash expectations, and two new test-fixture construction errors. All were corrected; [tests_initial.log](tests_initial.log) is preserved. No test was skipped or marked expected-failure.

Exact executed command: [tests_command.txt](tests_command.txt). Reproduce with the sol-recut interpreter and `PYTHONPATH=.`:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. ../greek-ocr-toolkit-sol-recut/.venv/bin/python -B docs/records/harvest/seg_steps/s5_adopt/run_tests.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. ../greek-ocr-toolkit-sol-recut/.venv/bin/python -B docs/records/harvest/seg_steps/s5_adopt/replay.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. ../greek-ocr-toolkit-sol-recut/.venv/bin/python -B docs/records/harvest/seg_steps/s5_adopt/summarize.py
```

## Scope and receipts

[scope_guard.json](scope_guard.json) lists changed files, SHA256s and protected-tree verification. [scope_guard.diff](scope_guard.diff) contains every production, manifest, README and test change, including the new integration tests. [receipt.json](receipt.json) fingerprints all generated artifacts, source inputs, interpreter and replay bindings. [replay.jsonl](replay.jsonl) retains all 1,705 before/after native results; [flips.jsonl](flips.jsonl) lists every cohort-entry verdict flip. No other tool rules changed.

SEG10 READY: fixes ported numeric-adjacency ok heldout-union ok (hunks identical yes); policy sha e5b635ff → 5888fe70; segmentation 0.9-s5; pipeline 0.3.1; changed owner-judged lines 59 (= s5 yes); 150 FP/FN/UNC 16/15/0 → 4/19/0; 888 109/135 → 117/135; marks 189/235 → 209/235; typology 160/185 → 173/185; tests 248 passed 0 failed
