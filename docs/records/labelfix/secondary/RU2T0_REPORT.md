# RU2T-0: collection-v2 train preparation

**READY for readings: 200 sampled candidate lines, 3 contexts × 2. No readings ran.** The sample costs about 0.884 weekly points (442 item reads). Full coverage costs about 8.08 points (4040 reads).

Input: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`; SHA256 `5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3`. 214,436 train rows, 11,804 selected by `script_class == cyrillic` (case insensitive) OR at least three Unicode Cyrillic letters. Group key is `(source, doc)`; language is only a metadata guess. Parent labels are never normalized.

## Census and orthography

| Source / book (`doc`) | Language guess | Rows | ь final | ь pre_hyphen | ъ final | ъ pre_hyphen | ѣ | і | ѳ | ѵ | Class | Sample lines |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| archive_AA9613308335D0B014B:cyrillic:9a32fb66 | Russian (metadata guess) | 1712 | 318 | 11 | 1834 | 4 | 923 | 877 | 16 | 6 | pre_reform | 30 |
| archive_b24878935:cyrillic:94847f75 | Bulgarian (metadata guess) | 1172 | 225 | 0 | 788 | 4 | 314 | 3 | 0 | 0 | pre_reform | 20 |
| archive_bub_gb_Cmg6AQAAIAAJ:cyrillic:7235f8d0 | Serbian (metadata guess) | 1510 | 25 | 1 | 37 | 0 | 16 | 63 | 0 | 3 | pre_reform | 2 |
| archive_bub_gb_mG0mAQAAIAAJ:cyrillic:0b4bf868 | Russian (metadata guess) | 1556 | 619 | 7 | 3320 | 34 | 1266 | 1053 | 3 | 0 | pre_reform | 57 |
| archive_izvestiianabul25192530bul:cyrillic:252fd568 | Bulgarian (metadata guess) | 1400 | 193 | 1 | 1938 | 11 | 993 | 16 | 0 | 0 | pre_reform | 20 |
| archive_izvestiianabulga610193138bulg:cyrillic:ae1a00a3 | Bulgarian (metadata guess) | 1167 | 161 | 0 | 1566 | 15 | 921 | 26 | 0 | 1 | pre_reform | 16 |
| archive_izvestiianatsars12192829tsar:cyrillic:b930919b | Bulgarian (metadata guess) | 724 | 95 | 0 | 1152 | 10 | 650 | 39 | 0 | 1 | pre_reform | 9 |
| archive_izvestiianatsars1516194243tsar:cyrillic:4b2c4367 | Bulgarian (metadata guess) | 988 | 117 | 1 | 1388 | 11 | 664 | 26 | 0 | 1 | pre_reform | 12 |
| archive_sobranie_zakonov_i_raspoyazheniu_pravitelstva_sssr_1930:cyrillic:be2e7fa5 | Russian (metadata guess) | 1575 | 341 | 14 | 0 | 0 | 0 | 2 | 0 | 0 | pre_reform | 34 |

A sign needs a preceding Cyrillic letter and no immediately following Cyrillic letter. ASCII `-` gives `pre_hyphen`; all other boundaries give `final`, exactly as in the RU1 census helper. Sign census targets lowercase ь/ъ; historical-letter counts casefold uppercase forms. Offsets are Python Unicode code points in the original label.

`pre_reform` means at least five word-final Google ъ (final plus pre_hyphen), OR any ѣ/і/ѳ/ѵ, across the selected rows of the book. This is the requested mechanical label class, not independently established historical orthography. **All nine books qualify; zero modern books and zero eligible modern spot positions.** `modern_spot_positions.jsonl` is empty; its seeded 10-position request cannot be filled.

The Serbian volume and the Soviet 1930 volume also qualify under this rule. In particular, the 1930 source has no final ъ but historical letters in two rows; this does not establish that its general orthography is pre-reform. Source metadata and individual counts are retained in `build.json`; no classification override or language-based edit was made.

## Budget and selection

Full candidates: **2,129 positions in 1,831 lines** (2094 final; 35 pre_hyphen). Since this exceeds 225 lines, the plan is **sample 200**, not full coverage. Selected lines contain 233 candidate positions. The lead decides whether to extend beyond this sample.

Seed: `RU2T0:20261017:book-stratified-v1`. Allocate 200 line slots proportionally by candidate-line book counts using largest remainders (book key breaks ties), then sample sorted IDs independently within each book with the seeded RNG. All nine books are represented. The same seed fixes context/control order; opaque IDs are freshly random. Full lists: `candidate_positions.full.jsonl` and `candidate_lines.full.jsonl`; selected IDs: `selected_lines.jsonl`.

Cost assumes 0.2 points per 100 item reads, both readers, and about 10% control items. Full packing would use 21 contexts per reader with 189 control appearances per reader: 4040 reads, **8.08 points**. The sample has 21 controls per reader, 442 reads, **0.884 points**. These are estimates; no usage probe ran.

## Packs and controls

| Context | Candidate lines | Control lines | Total per reader |
|---|---:|---:|---:|
| ctx01 | 66 | 7 | 73 |
| ctx02 | 67 | 7 | 74 |
| ctx03 | 67 | 7 | 74 |

Pack root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru2t/`. Each r2 is the exact reverse of r1 with globally fresh opaque IDs. Each reader sees only the RU1 public item fields, masked yer slots, and byte-copied PNG crops named by SHA256. Private keys, truth and manifests remain outside reader folders. All six pack closures pass; each has at most 100 items.

Controls reuse the 31 slot-bearing RU1 adjudicated lines containing all 65 positions; the 28 zero-slot lines are excluded. The seeded round-robin selection uses 21 distinct controls per reader, reused in reverse order for r2. Control truth and pixel hashes come from the retained RU1 inventory/private assignments and verified original cache. The RU1 disputed control exclusion and wrong-sign gate are preserved: more than one wrong scored sign voids a context; abstentions and excluded controls are reported separately.

All 11,804 Cyrillic crop references were checked for local existence; **zero missing**. `crop_unavailable.jsonl` is empty. Selected crops were copied directly from collection-v2 paths, without fetching or regeneration; all copied bytes match the recorded source SHA256. Only automatic PNG decoding was used; no images were displayed.

## Finalisation and registration

Prepared launcher (not executed): `scripts/secondary/reading/run_ru2t.sh ru2t ctx01 r1` (repeat for r2 and ctx02–03). Add `--dry-run` for local validation without a probe or reader. It reuses the existing Sol launcher with gpt-6.1-sol, medium, network/web disabled, isolated pack cwd, before/after usage accounting and the 78% usage refusal. It refuses to overwrite an attempt.

After all readings: `scripts/secondary/ru2t_finalize.sh`. It verifies pinned parent/tool/pack hashes, canonical v4.4 rollout scans, actual rollout model/effort, distinct rollout evidence, crop coverage, complete answer mappings and control gates before emitting the label version. Scanner SHA256: `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547` (the adopted N1TS3 canonical hash); the scanner was not changed.

**Owner scope extension:** the older RU1 combiner excluded pre_hyphen positions. This task asks every word-final ь to receive two reads, so both final and pre_hyphen positions are candidates here; the wrapper reuses the RU1 vote/gate decision on both. Two independent hard calls permit ъ only if at least one context has a VALID RU1 control gate. Two soft calls keep ь. Unreadable/other/disagreement, missing evidence, or two VOID hard votes hold. Google ъ is never edited. No lexical prior overrides the glyph votes; modern-book candidates are absent by construction.

The finaliser writes a complete parent-ID label stream to `artifacts/ru1/ru1_v2_train.jsonl`, preserving every unsampled and unedited label, plus `ru1_v2_train_manifest.json`, `ru2t/decisions.jsonl` and `ru2t/per_row_decision_counts.jsonl` (all parent rows). It then registers `collection_v2_train` as the SHA-bound parent and `ru1_v2_train` in `docs/records/labelfix/lqb/versions.json`, preserving existing entries. The output is a sampled correction version, not a claim of full candidate coverage.

**Pending readings:** no real `ru1_v2_train.jsonl` or LQB version entry has been fabricated or published at this preparation stage. The finaliser refuses the current incomplete readings. The registry workflow was exercised only on temporary fixtures.

## Validation

**32 tests passed**: 21 RU2T fixture tests and 11 canonical scanner regressions. RU2T tests include all 16 call pairs, unreadable holds, VOID gates, pre_hyphen scope, modern exclusion, thresholds, deterministic stratification, full parent preservation, actual scanner→mapper→combiner→output→LQB loader round trip, and refusals for missing answers/run, changed parent/pack, forbidden paths, wrong model and reused rollout. Shell syntax and all six launcher dry runs pass. No reader, network, browser, computer use, source-input write or `.git` write occurred.

Reproduce fixtures with `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -m unittest discover -s tests -p test_ru2t.py`; scanner fixtures use `-s scripts/secondary/reading -p test_scan_rollout_v4.py`. The x86_64 interpreter is required by the installed Pillow binary. Pack regeneration refuses a nonempty destination.

RU2T0 READY: cyrillic rows 11804; books pre_reform 9 / modern 0; candidate ь positions 2129 in 1831 lines; plan sample 200 (8.08 pts for full); contexts 3 ×2; closure ok; tests 32 passed


## RU2T-0b: external pack relocation (2026-10-17)

The six reader folders now live at `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru2t/`, outside every git worktree. Copied all 454 files (5,245,748 bytes) first, verified every relative filename and SHA256 against the original, then removed only the approved in-repo `sol_packs/ru2t` copy. Reader payloads and all six context manifests remain byte-identical after closure. The prior brief's in-repo root is superseded by this relocation.

The shared builder/launcher/finaliser root, build bindings, preparation receipt, closure results and launcher dry-run records now use the external root. Tool bindings were refreshed only after all other existing input and pack hashes passed verification. The builder, launcher and finaliser reject roots with a `.git` ancestor, checking both lexical and resolved paths without invoking git. Tests cover git directories, linked-worktree `.git` files, symlinks into a repository, refusal before source reads or output creation, and an allowed external nonexistent root.

Validation: 6/6 closures pass; `run_ru2t.sh ru2t ctx01–03 r1/r2 --dry-run` passes all six combinations; all 24 RU2T fixture tests pass, including the three new guard tests; launcher/finaliser shell syntax passes. No reader, usage probe, network, browser, computer use, source-data write or `.git` write ran. Finalisation was not executed. Copy inventory and validation evidence: `artifacts/ru1/ru2t/relocation_RU2T0b.json`, `closure.json`, `launcher_dry_runs.json`, `tests_RU2T0b.txt`; receipt: `artifacts/ru1/RU2T0b_RECEIPT.json`.
