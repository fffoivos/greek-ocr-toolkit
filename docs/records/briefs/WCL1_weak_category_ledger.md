# WCL1: first version of the weak-category ledger (gpt-6.1-sol, medium, network OFF, no spend, no reading)

**Owner request, via the coordinator.** `docs/records/harvest/collect_v3/WEAK_CATEGORY_LEDGER.md` is the living page the owner uses to steer the next data round (release v3). It replaces RELEASE_V3_INPUTS.md. Write only under `docs/records/harvest/collect_v3/` (ledger + `weak_ledger/` data). A live collector (W2 Gazette) is running from the run root: read only, take no locks, and never touch `collect_v3/`.

## Rows, one per weak category
1. all-caps / headings;
2. punctuation-heavy / dialogue;
3. dotted leaders;
4. numerics in lines;
5. Cyrillic;
6. mixed Greek+Latin;
7. polytonic 1850–1890;
8. polytonic 1900–1982;
9. monotonic / born-digital.

## Columns, each with a source path
- **E3 CER** for the category: `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/E3_RESULTS.md` and DATA_PLAN_v2.3 (find them read-only).
- **Plan quota:** the DATA_PLAN_v2 §3 table.
- **Rows collected so far, by source,** split into **passed / pending check / failed / unchecked:**
  - W1, from `~/Projects/collect-v3-data/run/W1/features.jsonl` and `release_exclusions/unchecked_strata.json`;
  - W2 main run, from `run/W2/features.jsonl` if present, else the W2 receipt classes (34,439 usable: poly1850 19,325, numerics 7,250, cyrillic 5,054, poly1900 2,108, greek_poly 702);
  - masked admissions, from `release_admissions/w1_masked_1d.jsonl` per arm: wave-1d 16,562; release-v3-candidate kosmopolis poly1850 462 and headings_caps 1,626.
  - Map collector primary classes to these categories, and state the mapping.
- **Pending rows:** mark BSB (deferred; resumes 18 Oct) and Gazette (reading now) as **"pending"**, using the planned page counts and the W1 yield per page.
- **Gap to quota.**
- **The source and page-band reads the plan named for the category,** including the never-ordered page-band reads (0–8% and 95–100%) for caps and leaders, with the cost to fill the gap in pages and USD at USD 0.0015/page. Source: SOURCING_T5_COLLECTION_PLAN rev 2.2 (`~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/`).
- **Google label faults seen in the category, with tags:** from `c1/c1_results.json` (superscript, dash, separator, lunate, marks_bias, mark errors), CAPS/KR/RUC results, and the RU1 residual classes.
- **Correction column:** by reference only. Write "see the spell-check lead's answer (pending)" until a path is supplied.

## Also
- Write `weak_ledger/ledger.json` (machine-readable, the same columns) and a short "how to update" note: what changes when BSB, Gazette or a new check closes.
- Quote only numbers that come from files, and put a source path under every number. Where a figure cannot be found, write "not found" with the paths searched.

Leave a guarded commit list. The last line must be exactly:
`WCL1: done | categories: 9 | numbers sourced: <n> | not found: <n> | pending rows marked: BSB, Gazette`
