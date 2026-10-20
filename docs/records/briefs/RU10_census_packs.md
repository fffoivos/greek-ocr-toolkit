# RU1-0: Russian hard-sign census + blind yer packs (gpt-6.1-sol, medium, network OFF; no .git writes; Mac CPU only; no reading run)

You work in the worktree `~/Projects/greek-ocr-toolkit-secondary` (branch `opus/secondary-corrections`). Plan:
`docs/records/labelfix/secondary/PLAN.md` §3.

**Fault.** In pre-1918 Russian prints, Google writes a printed word-final ъ as ь. Google's own word-final ъ was never wrong (0/26).
Repair is one-directional: ь → ъ only where a blind ink reader says ъ. You build the census and the reader packs. You do NOT run any
reader and do NOT look at the crops yourself beyond the automatic checks below.

**Read-only inputs.**
- `~/Projects/collect-v3-data/run/W1/features.jsonl`, rows with `source == "ia_russian"`. Use the `label` field: it is the current
  label. This is a LIVE collector root: read only. Never create, take or touch `run.lock`, and write nothing under
  `~/Projects/collect-v3-data/`.
- **Crops are not on disk.** Regenerate them with `collect_v3.storage.ensure_crop` from `~/Projects/greek-ocr-toolkit-sol-collect`
  (import it read-only, via `sys.path`). `ensure_crop` writes to `row['crop']`, which is inside the run root, so ALWAYS pass a shallow
  copy of the row whose `crop` is rewritten to the cache path
  `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/ru1_cache/crops/<crop_sha256>.png`.
  The function checks both the source sha and `crop_sha256`. Any mismatch → record the row as `crop_unavailable`; never substitute.
- The yer adjudication (the controls): `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/`
  (`table.json`, `key.json`, `items_a.jsonl`, `items_b.jsonl`, `ink_a.jsonl`, `ink_b.jsonl`, `prior.jsonl`, `INK.md`, `PRIOR.md`). Its
  65 slots carry ink truth from two blind readers. Map each one to its W1 row id via `key.json` and the C1 key
  `~/Projects/collect-v3-data/run/W1/c1/ia_russian__cyrillic_key.json`.
- The Sol-reading tooling, to copy and not modify:
  - `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/` (`HANDOVER.md`, `prompts/yer.md`, `launchers/`,
    `tools/scan_rollout.py` v4 with its test, `tools/scan_packs.py`, `tools/build_packs.py`, `tools/map_answers.py`,
    `tools/ledger.py`, `tools/common.py`, `tools/replay_literal.py`);
  - the "usable rows" definition, which you take from the sourcing lead's rule in
    `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/` (rows not excluded by `release_exclusions/` line classes
    such as `w1_rotated_crop_ids.txt`, and with a crop). The sourcing lead counts **1,146 usable ia_russian rows** (cyrillic 949,
    numerics 156, latin 40, nonletter 1). Reproduce that count and state the exact rule. If you cannot reproduce it, report the
    difference and use the closest documented rule.

**Do.**
1. **Census** (`scripts/secondary/ru1_census.py`, with tests).
   - **Positions.** A word-final yer is ъ or ь preceded by a Cyrillic letter and not followed by a Cyrillic letter. Classify each:
     `final` (followed by space, punctuation or end of line), or `pre_hyphen` (followed by `-`; at line end this means a broken word,
     so record it but exclude it from the bed).
   - **Counts** per book (`source:item` from the row id or page metadata) and per class (`primary_class`): Google final ъ and Google
     final ь, over all rows and over usable rows.
   - **Book orthography.** A book is `pre1918` if Google wrote ≥5 word-final ъ or any ѣ і ѳ ѵ in it; otherwise it is `modern`.
   - **Prior.** For every Google-ь position, record a text-only orthographic prior (`ъ_only` / `ь_only` / `both` / `unknown`). Use a
     deterministic, documented method, e.g. a small rule set plus wordlists built from the W1 ia_russian labels themselves (a stem seen
     with final ъ elsewhere vs with ь), with the method stated. The prior is a cross-check for the lead, never a decider, and it is
     never shown to readers.
2. **Bed.**
   - **Items.** Every usable `pre1918`-book line that contains ≥1 Google-final ь at a `final` position, minus the lines that carry the
     65 control slots. Plus a 20-position spot check from `modern` books: the lines that carry them, seeded.
   - **Masking.** Mask **every** word-final yer in the line, Google ъ and ь alike, as ⟦1⟧, ⟦2⟧, … in reading order. This is exactly the
     yer protocol, so masking leaks nothing about which sign Google wrote.
   - Report the line and slot counts.
3. **Controls.** The 59 C1/v2 lines carrying the 65 adjudicated slots, masked the same way, with truth from `table.json` (`ink=`).
   Each context gets about 10% controls (≈9 of ≤100 items), drawn round-robin so each control line appears in as few contexts as
   possible. A control line may repeat across contexts but never within one.
4. **Packs** (`scripts/secondary/ru1_build_packs.py`, adapted from `build_packs.py`).
   - **PACK_ROOT:**
     `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru1/`.
     One folder per context, `ctxNN/r1/`, containing only `items.jsonl` and `crops/`. Fields: `item_id` (`k` + 10 hex, fresh),
     `crop` (relative path, content-hash PNG name, copied bytes, no symlinks), `masked_text`, `slots`.
   - Seeded random order. ≤100 items per context.
   - `MANIFEST.r1.json` sits beside each `ctxNN/` folder, per HANDOVER §4.
   - **Keys** go to the worktree at `artifacts/ru1/keys/`, never under PACK_ROOT. Per item: W1 row id, every slot's char offset,
     Google glyph, prior, control truth, book, orthography class.
   - Run `scan_packs.py` (copied) for closure: no key or truth reachable from a pack, no symlinks, only allowed files.
5. **Launchers.** Copy and adapt the sol-reading launchers and tools into `scripts/secondary/reading/` for this track:
   - `S`/`W`/`D` point to this worktree and PACK_ROOT;
   - answers and scans go to `artifacts/ru1/answers/`;
   - ledger at `artifacts/ru1/usage_ledger.json`;
   - the prompt is `prompts/yer.md`, copied **verbatim** to `docs/records/labelfix/secondary/prompts/yer.md`; do not edit the protocol body;
   - keep the 78% refusal and the before/after limit probes.

   Adapt `map_answers.py` into `ru1_map_answers.py`. It maps answers back to keys, scores controls per context (more than 1 error →
   that context is VOID), and writes `artifacts/ru1/answers/<ctx>.mapped.jsonl`. Add tests on fixture answers covering: a void
   context, an "u" call, an "other" call, a missing item, and a Google-ъ slot read as ь (counted, but it never produces an edit).
   Copy and run `test_scan_rollout_v4.py` so the copied scanner is proven.
6. **Receipt.** Write `artifacts/ru1/RU10_RECEIPT.json` (inputs + outputs with sha256; counts; the usable-rule statement; the
   pack-closure result; tests) and a report `docs/records/labelfix/secondary/RU10_REPORT.md`. The report has a census table per book, the
   prior distribution on Google-ь positions, the bed and control counts, the context list, and a Codex estimate at 0.2 weekly points
   per 100 items.

**Constraints.**
- Allowed writes: `scripts/secondary/`, `tests/` (new files only), `artifacts/ru1/`, `docs/records/labelfix/secondary/` (new files only),
  the scratchpad `ru1_cache/` and `sol_packs/ru1/`.
- Do not touch `greekocr/labelfix/`, any other worktree, or the run root.
- Pillow needs `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`.
- Pure-text tests run with `python3 -m pytest --noconftest -q`.

**Last line:** `RU10 READY: usable rows <n> (rule reproduced <yes|no>); pre1918 books <n>, modern <n>; Google-final ь positions <n> (usable <n>); bed lines <n> slots <n> (+20 modern spot); controls <n> lines; contexts <n>; crop_unavailable <n>; closure <ok|FAIL>; tests <n> passed`
