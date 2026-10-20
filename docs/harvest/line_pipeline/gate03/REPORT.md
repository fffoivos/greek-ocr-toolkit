# Content gate 0.3

Implemented the owner's two exclusions using the unchanged `content_issues`, `inventory` and `expectations` definitions. The shared `content_gate_exclusion` is called immediately after recording the gate in `evaluate`, before crop identity or segmentation, and before census cache lookup/native scheduling in `prepare`.

Mixed-script words DROP, with their word evidence first and any unexpected-script evidence second. Other unexpected scripts HOLD, with script counts and offending characters. Both return through `finish`, mark `content_gate.excluded`, add no segmentation stage, and skip all five routes. Remaining unexpected-character, profile-anomaly and unexpected-language behavior is unchanged. No segmentation, routing, repair or final-eligibility rules were edited.

`PIPELINE_VERSION` remains 0.3 (its pre-change value). Only the content-gate tool generation becomes 0.3; all other tool version numbers remain unchanged. Shared source fingerprints and their dependent aggregate digests were regenerated.

## Verification

The four segmentation suites selected are `tests/test_seg_gate.py`, `tests/test_seg_deskew.py`, `tests/test_seg_curve.py`, and `tests/test_seg_small.py` (59 cases). The copied pipeline suite contains 130 cases. The source copy was taken read-only from `~/Projects/greek-ocr-toolkit-sol-recut/tests/test_line_pipeline.py`.

| Run | Passed | Failed | Verbatim output |
| --- | ---: | ---: | --- |
| Before implementation: copied pipeline + four segmentation suites | 169 | 20 | [tests-before.txt](tests-before.txt) |
| Before implementation: first eight new gate cases | 2 | 6 | [new-tests-before.txt](new-tests-before.txt) |
| After implementation, before updating the two old assertions; three additional bound-crop cases included | 178 | 22 | [tests-after-old-assertions.txt](tests-after-old-assertions.txt) |
| Final: new gate + copied pipeline + four segmentation suites | 180 | 20 | [tests-after.txt](tests-after.txt) |
| Final focused: new gate + four segmentation suites | 70 | 0 | [tests-focused.txt](tests-focused.txt) |

All 20 baseline failures remain unchanged. Their exception is verbatim:

```text
E   FileNotFoundError: [Errno 2] No such file or directory: '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/scripts/harvest/clariden/worker.py'
```

The linked raw logs preserve every failure name, traceback and assertion verbatim before and after. This is a pre-existing missing support file, not a green complete pipeline suite. No unrelated tests or support code were changed.

The 11 new gate cases verify Greek-page `日` HOLD; mixed word DROP; both issues DROP; precedence over both bound/unavailable crop status; mixed word DROP even when both scripts are expected; codec-outside COMBINING DOT ABOVE retaining segmentation and content repair; complete clear-row output equality with [clear-before.json](clear-before.json); and both excluded census kinds returning exactly `Observation()` with zero native attempts, zero cached measurements and no measurement entries. Census tests use only tiny temporary synthetic metadata and mock factories; no population census was run.

The only existing assertions updated are in `test_mixed_script_candidate_can_be_resolved_by_an_existing_tool` and `test_unrepaired_mixed_script_is_held`. Their old test names and all other test code remain unchanged. The exact assertion diff is:

```diff
--- sol-recut/tests/test_line_pipeline.py
+++ tests/test_line_pipeline.py
@@ -107,12 +107,12 @@
     r=row("λόγoς καὶ γράμματα")
     def correct(r,t,e):return None if t=="content_repair" else answer(r,t,"λόγος καὶ γράμματα")
     d=engine(corrector=correct).evaluate(r)
-    assert d["disposition"]=="ADMIT" and not d["final_inventory"]["mixed_words"]
+    assert d["disposition"]=="DROP" and d["reasons"][0]==dict(reason="mixed_script_word", words=["λόγoς"])
 
 
 def test_unrepaired_mixed_script_is_held():
     d=engine(corrector=lambda r,t,e:None if t=="content_repair" else answer(r,t)).evaluate(row("λόγoς καὶ γράμματα"))
-    assert d["disposition"]=="HOLD"
+    assert d["disposition"]=="DROP"
 
 
 def test_script_route_created_after_composition_is_not_skipped():
```

## Witness

A read-only search of the local `docs/records/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl` found no l0029 record. Therefore this uses a clearly synthetic canonical row with the owner's exact ID, text `日`, and source `gazette_modern`; synthetic parent/edition and crop hash are placeholders, not recovered physical evidence. The pipeline's own existing source policy resolves modern Greek, Greek script, and minority Latin policy. Both downstream adapters raise if called. [Witness input](witness-row.json); [complete decision JSON](witness-decision.json).

```json
{
  "schema": "line-filter-decision-v1",
  "pipeline_version": "0.3",
  "toolchain_digest": "b4b233dc6638f7266ce646c628af57b9fe9d7e0806745a8fd2806fd6e8efe55f",
  "toolchain_versions": {
    "polytonic": "0.7",
    "cyrillic": "0.3",
    "numerics": "0.2",
    "dashes": "0.1",
    "segmentation": "0.9-s4",
    "content_gate": "0.3",
    "content_repair": "0.2",
    "composer": "0.2",
    "final_eligibility": "0.2",
    "census": "0.5",
    "inventory": "0.1"
  },
  "binding": {
    "parent_id": "synthetic-witness",
    "id": "gazette_modern--67dfc161a690ff25--s000-l0029",
    "split": "train",
    "crop_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "raw_text_sha256": "85217f7aff77841438439fb3e7cf37bb3062fb026453c7692247d3a5641a0115",
  "final_text": "日",
  "stages": [
    {
      "stage": "content_gate",
      "suspicious": [
        {
          "reason": "unexpected_script",
          "scripts": [
            "other"
          ]
        },
        {
          "reason": "unexpected_character",
          "characters": [
            "日"
          ]
        }
      ],
      "profile_flags": [],
      "excluded": "unexpected_script"
    }
  ],
  "routes": {
    "polytonic": {
      "status": "not_run_due_to_prior_exclusion"
    },
    "cyrillic": {
      "status": "not_run_due_to_prior_exclusion"
    },
    "numerics": {
      "status": "not_run_due_to_prior_exclusion"
    },
    "dashes": {
      "status": "not_run_due_to_prior_exclusion"
    },
    "content_repair": {
      "status": "not_run_due_to_prior_exclusion"
    }
  },
  "reasons": [
    {
      "reason": "unexpected_script",
      "scripts": [
        "other"
      ],
      "script_counts": {
        "other": 1
      },
      "characters": [
        "日"
      ]
    }
  ],
  "disposition": "HOLD",
  "admitted": false,
  "expectations": {
    "languages": [
      "modern Greek (monotonic)"
    ],
    "scripts": [
      "greek"
    ],
    "orthography": "monotonic",
    "provenance": "docs/records/briefs/ADM5_standard_admission_tool.md, owner rules 5-7 (2026-10-17)",
    "allowed_characters": [],
    "latin_policy": "mixed_class_or_minority"
  },
  "raw_inventory": {
    "greek_letters": 0,
    "latin_letters": 0,
    "cyrillic_letters": 0,
    "other_letters": 1,
    "digits": 0,
    "greek_punctuation": 0,
    "other_symbols": 0,
    "other_script_letters": {
      "CJK": 1
    },
    "other_letter_names": {
      "CJK UNIFIED IDEOGRAPH-65E5": 1
    },
    "mixed_words": [],
    "latin_words": [],
    "letter_count": 1,
    "nonspace_count": 1,
    "scripts": {
      "other": 1
    },
    "characters": 1,
    "raw_codepoints": 1,
    "raw_text_sha256": "85217f7aff77841438439fb3e7cf37bb3062fb026453c7692247d3a5641a0115",
    "character_counts": {
      "日": 1
    }
  }
}
```

## Version build

The ordinary builder invocation initially failed because this worktree lacks `scripts/harvest/clariden/worker.py` and four other packaging dependencies. The actual `build()` was then used with precisely those five missing files read-only from `sol-recut`; their SHA256 hashes all match the previous manifest. No source files were copied or changed for this workaround. [Paths and hashes](version-build-fallbacks.json); [reproduction wrapper](rebuild_versions.py). Run `python3 docs/harvest/line_pipeline/gate03/rebuild_versions.py` from this checkout to reproduce it.

Regeneration also replaces the old `greek-ocr-toolkit-sol-recut/` component path prefixes with this worktree's `greek-ocr-toolkit-segcensus/` prefixes, as the standard builder derives names from its root. Thus some aggregate digests change despite unchanged component bytes and unchanged method versions. No segmentation component was modified.

## Scope guard

Eight source/document/test paths were created or changed:

- `greekocr/harvest/line_pipeline.py`
- `greekocr/harvest/line_pipeline_census.py`
- `scripts/harvest/build_filter_versions.py`
- `docs/records/harvest/line_pipeline_legacy/README.md`
- `docs/records/harvest/line_pipeline_legacy/pipeline.mmd`
- `docs/harvest/line_pipeline/tool_versions.json`
- `tests/test_line_pipeline.py`
- `tests/test_content_gate.py`

All additional evidence is confined to this `gate03/` directory. [Full source diff, including both new test files](scope.patch); [stat](scope-stat.txt); [source hashes](source-hashes.json); [receipt and exhaustive artifact manifest](receipt.json). The copied suite's separate two-assertion diff is [existing-assertions.patch](existing-assertions.patch). Baseline source snapshots are in `baseline/`.

```text
 docs/records/harvest/line_pipeline_legacy/README.md          |  5 +-
 docs/records/harvest/line_pipeline_legacy/pipeline.mmd       |  4 +-
 docs/harvest/line_pipeline/tool_versions.json | 83 ++++++++++++++-------------
 greekocr/harvest/line_pipeline.py             | 21 ++++++-
 greekocr/harvest/line_pipeline_census.py      |  5 +-
 scripts/harvest/build_filter_versions.py      |  2 +
 6 files changed, 73 insertions(+), 47 deletions(-)
 tests/test_line_pipeline.py | 1022 lines (copied suite; two assertions updated)
 tests/test_content_gate.py | 82 lines (new)
```

Network remained off. No `.git` writes, commits, reader runs, population measurements or census execution were performed. The forbidden package directory, `seg09/`, and the untracked census evidence file were not written. Existing unrelated untracked briefs and evidence remain outside this change.

GATE 0.3 READY: witness l0029 HOLD; mixed DROP ok; foreign HOLD ok; codec-mark repair route kept ok; census prepare skips ok; tests 180 passed 20 failed; files greekocr/harvest/line_pipeline.py, greekocr/harvest/line_pipeline_census.py, scripts/harvest/build_filter_versions.py, docs/records/harvest/line_pipeline_legacy/README.md, docs/records/harvest/line_pipeline_legacy/pipeline.mmd, docs/harvest/line_pipeline/tool_versions.json, tests/test_line_pipeline.py, tests/test_content_gate.py, docs/harvest/line_pipeline/gate03/*
