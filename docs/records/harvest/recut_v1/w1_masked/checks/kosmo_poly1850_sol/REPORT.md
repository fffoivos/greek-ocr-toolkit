# SRK2 — kosmopolis poly1850 Sol reading

**Done. Audit clean; crop coverage 100/100; gate pass.** Letters and crop_ok are final. Marks are `pending_opus`. The masked stratum is eligible for wave-1d admission preparation; no admission was performed.

| Metric | y | n | u / na | Ruling |
| --- | ---: | ---: | ---: | --- |
| letters | 96 | 4 | 0 u | final |
| crop_ok | 99 | 1 | — | final |
| marks | 90 | 10 | 0 na | pending_opus |

Denominator: 100 distinct answers, T6g cards, and line IDs. Gate: letters y ≥ 90 and crop_ok y ≥ 90. Values, error labels, and details are copied mechanically from the final answers; no visual re-adjudication or correction was performed.

## Rollout leakage and pack custody

Unchanged lead scanner v3: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py` (SHA256 `30aca0ec1d8f290807447b90c8550e1aee6f525a025e6f47071a37e511904138`). Its `inspect(rollout, pack, skip_manifest=True)` returned `ok=true`, zero violations. Every one of the 17 recorded exec calls and its shell command was also reviewed: experiment inputs were cards, answers, and pack crops; writes were answers and zoom sheets. No access to repository, key, truth, or external experiment-data paths occurred in the recorded calls. The rollout records gpt-6.1-sol, medium effort, pack cwd, and `network_access=false`.

SRK1 intentionally supplied no reader-accessible manifest. The scanner’s documented missing-manifest option was used, then all 101 original files were checked against the external SRK1 pack-scan receipt. All hashes match; no links or hardlinks exist. Additions are exactly answers.jsonl and 23 zoom PNGs. This audits recorded data access and image provenance; it does not prove OS-level isolation.

## Coverage proof

**100/100 original crop IDs were viewed through image attachments returned by view_image.** There were zero direct original-crop views, 23 completed ImageView events, and 23 returned PNG attachments. Twenty primary sheets contain five consecutive crops each (100 distinct crops), and three recheck sheets contain 15 repeated crop appearances. Every returned attachment matches its saved PNG bytes exactly. Each sheet was independently rebuilt to stdout from the reviewed fixed ImageMagick recipe, using original pack crops; dimensions and all RGB pixels match exactly. No generated image was counted without a returned attachment.

The primary recipe is 200% resizing, 30 white pixels above each crop, then vertical append. Rechecks use 350%, 35 pixels, and the explicitly listed indices. Full per-crop IDs, input hashes, original dimensions, content bounding boxes, sheet hashes, and attachment records are in scan.json → coverage.sheets. Record indices below are zero-based JSONL record numbers (file line = record + 1).

| Returned sheet | Sol positions (1-based) | ImageView record | Image attachment record | Pixel reconstruction |
| --- | --- | ---: | ---: | --- |
| zoom/b00.png | 1, 2, 3, 4, 5 | 34 | 36 | exact |
| zoom/b01.png | 6, 7, 8, 9, 10 | 35 | 36 | exact |
| zoom/b02.png | 11, 12, 13, 14, 15 | 43 | 45 | exact |
| zoom/b03.png | 16, 17, 18, 19, 20 | 44 | 45 | exact |
| zoom/b04.png | 21, 22, 23, 24, 25 | 51 | 54 | exact |
| zoom/b05.png | 26, 27, 28, 29, 30 | 53 | 54 | exact |
| zoom/b06.png | 31, 32, 33, 34, 35 | 63 | 65 | exact |
| zoom/b07.png | 36, 37, 38, 39, 40 | 64 | 65 | exact |
| zoom/b08.png | 41, 42, 43, 44, 45 | 79 | 82 | exact |
| zoom/b09.png | 46, 47, 48, 49, 50 | 80 | 82 | exact |
| zoom/b10.png | 51, 52, 53, 54, 55 | 89 | 91 | exact |
| zoom/b11.png | 56, 57, 58, 59, 60 | 90 | 91 | exact |
| zoom/b12.png | 61, 62, 63, 64, 65 | 97 | 100 | exact |
| zoom/b13.png | 66, 67, 68, 69, 70 | 98 | 100 | exact |
| zoom/b14.png | 71, 72, 73, 74, 75 | 114 | 117 | exact |
| zoom/b15.png | 76, 77, 78, 79, 80 | 115 | 117 | exact |
| zoom/b16.png | 81, 82, 83, 84, 85 | 126 | 128 | exact |
| zoom/b17.png | 86, 87, 88, 89, 90 | 127 | 128 | exact |
| zoom/b18.png | 91, 92, 93, 94, 95 | 135 | 137 | exact |
| zoom/b19.png | 96, 97, 98, 99, 100 | 136 | 137 | exact |
| zoom/recheck.png | 2, 30, 33, 35, 38 | 72 | 73 | exact |
| zoom/recheck2.png | 8, 17, 62, 70, 50 | 107 | 108 | exact |
| zoom/recheck3.png | 3, 9, 88, 93, 94 | 144 | 145 | exact |

The lead scanner’s `view_image_calls=15` counts static literal call sites and does not expand loops. Coverage uses completed ImageView events plus returned attachments and pixel provenance. Two early sheet-generation attempts failed (missing `python`, then missing Helvetica); neither returned an image or contributes coverage. The later successful sheets cover all crops. Negative checks confirm that no returned images yields 0/100, and removing the final sheet or failing its pixel proof yields 95/100 and cannot pass coverage.

## Failures and recorded flags

Final gate-metric failures: 5 rows (letters n: 4; crop_ok n: 1). They are listed below together with every pending mark failure and punctuation flag. All marks in this table remain pending_opus. Blank details were preserved in mapped answers.

| Sol position | T6g card | Line ID | letters | crop_ok | marks (pending_opus) | Error types | Detail |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 8 | c062 | kosmopolis--aaa124307e36f113--s001-l0085 | y | n | y | crop_clipped | ἰσχυρόταται (τελικὸ ι κομμένο) → ἰσχυρόταται |
| 17 | c095 | kosmopolis--aaa124307e36f113--s001-l0019 | n | y | y | wrong_letter | Ἐν → ἐν |
| 21 | c086 | kosmopolis--aaa124307e36f113--s005-l0055 | n | y | y | wrong_letter | Ἑλληνισμὸν → ἑλληνισμὸν |
| 25 | c064 | kosmopolis--aaa124307e36f113--s006-l0036 | y | y | n | missing_mark | Ἀγκαλιασμένα → Αγκαλιασμένα |
| 27 | c076 | kosmopolis--aaa124307e36f113--s003-l0048 | y | y | n | missing_mark | Ἡ → Η |
| 28 | c049 | kosmopolis--aaa124307e36f113--s003-l0073 | y | y | y | punctuation | ἁρμονίας. → ἁρμονίας, |
| 30 | c063 | kosmopolis--aaa124307e36f113--s002-l0072 | y | y | n | missing_mark | παρατηρήσῃ → παρατηρήση |
| 31 | c074 | kosmopolis--aaa124307e36f113--s002-l0035 | y | y | n | extra_mark | ἐπιοῦσαν → ἐπιοῦσὰν |
| 41 | c061 | kosmopolis--aaa124307e36f113--s004-l0084 | n | y | y | wrong_letter | Ὁποῖα → ὁποῖα |
| 48 | c029 | kosmopolis--aaa124307e36f113--s006-l0068 | n | y | y | wrong_letter | ἀληθέστατα → ἀληθέςατα |
| 56 | c065 | kosmopolis--aaa124307e36f113--s006-l0095 | y | y | n | wrong_mark | Ῥάμφος → 'Ράμφος |
| 70 | c077 | kosmopolis--aaa124307e36f113--s005-l0034 | y | y | y | punctuation | Κυρία. → Κυρία |
| 74 | c045 | kosmopolis--aaa124307e36f113--s001-l0008 | y | y | n | missing_mark | Ἡ → Η |
| 86 | c032 | kosmopolis--aaa124307e36f113--s005-l0020 | y | y | n | missing_mark | Ἀγγλίᾳ → Αγγλίᾳ |
| 90 | c058 | kosmopolis--aaa124307e36f113--s001-l0054 | y | y | n | missing_mark | τοὐναντίον → τουναντίον |
| 93 | c078 | kosmopolis--aaa124307e36f113--s000-l0062 | y | y | n | missing_mark, punctuation | ἀνυψώσῃς → ἀνυψώσης; ’νὰ → νὰ |
| 94 | c036 | kosmopolis--aaa124307e36f113--s003-l0080 | y | y | n | missing_mark | Ἐσυλ- → Εσυλ- |

| Error type | Answers |
| --- | ---: |
| crop_clipped | 1 |
| extra_mark | 1 |
| missing_mark | 8 |
| punctuation | 3 |
| wrong_letter | 4 |
| wrong_mark | 1 |

17 answers have an error label; an answer can have multiple labels. Error labels include pending mark observations and do not override the final letter/crop verdicts.

## Exact usage

| Quantity | Recorded value | Source |
| --- | ---: | --- |
| Launcher wall time | 153 s | launcher JSON |
| Rollout task duration | 151480 ms | task_complete record 158 |
| Input tokens | 874,758 | launcher JSON = rollout |
| Cached input tokens | 801,792 | launcher JSON = rollout |
| Cache-write input tokens | 0 | launcher JSON = rollout |
| Output tokens | 7,111 | launcher JSON = rollout |
| Reasoning output tokens (included in output) | 1,832 | launcher JSON = rollout |
| Total tokens | 881,869 | launcher JSON = rollout |
| Exec calls / shell commands | 17 / 17 | launcher JSON = rollout |
| Codex weekly usage snapshot | 33.0% / 10,080 minutes | launcher JSON = rollout |

The launcher output was recovered verbatim from the lead’s recorded tool-result message at `/Users/foivoskarounos-zamparloukos/.claude/projects/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4.jsonl`, line 11568, entry `61107bec-922d-4fd9-8510-ef86e8900c0e`. Its JSON-line SHA256 is `e2f1f9fb5af326600749413eac3a074dc101fd939cd0abe0989c2dc170017f83`. The complete JSON and locator are embedded in scan.json → usage_provenance.launcher. Model, return code, rollout path, usage, tool calls, and rate-limit snapshot agree with the rollout; all per-response token usage records also sum exactly to the final totals. Launcher wall time and rollout duration are separate recorded quantities. No cost, per-run weekly usage delta, or other usage estimate is inferred.

## Guarded commit list

Exactly these four repository paths are in scope:

```text
docs/records/harvest/recut_v1/w1_masked/checks/kosmo_poly1850_sol/scan.json
docs/records/harvest/recut_v1/w1_masked/checks/kosmo_poly1850_sol/answers_mapped.jsonl
docs/records/harvest/recut_v1/w1_masked/checks/kosmo_poly1850_sol/results.json
docs/records/harvest/recut_v1/w1_masked/checks/kosmo_poly1850_sol/REPORT.md
```

The SHA256-bound list is `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/srk2_validation/commit-inputs.json`; its read-only checker is `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/srk2_validation/guard.py`. The checker requires the recorded branch and HEAD, an empty index, the exact four-file scope, unchanged evidence hashes, and the same recorded launcher JSON line. It never stages or commits. Existing unrelated untracked paths are excluded.

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/srk2_validation/guard.py
```

No staging, commit, admission, or Opus adjudication was performed.

SRK2: done | letters y: 96 | crop_ok y: 99 | marks y: 90 (pending opus) | gate: pass | tokens: 881869
