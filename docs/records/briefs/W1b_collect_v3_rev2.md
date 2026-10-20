# W1b: update `collect_v3` to plan rev 2 and close the build checklist (gpt-6.1-sol, xhigh, network OFF, no spend, ≤ 90 min)

**Where to work.** This worktree, branch `sol/collect-v3`; the base is your W1 build, commit 9b82f923.

**Read-only inputs:**
- the plan, rev 2: `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/SOURCING_T5_COLLECTION_PLAN_20261016.md`, §1, §3, §5, §6 and §7. It is under review, so do not edit it.
- the reply: `SOURCING_T5_CP5_REPLY_20261017.md` in the same directory.
- the look-alike rule: `~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/v2r/lookalike_rule.py`.
- the crop_ok definition: `.../blind_checks_v1/v2/LABEL_CHECK_v2.md`.

**Nothing is collected.** W1 starts only after the owner's go and his execution-host decision.

## Changes to match rev 2 (plan §3)

| Source | Rev 2 setting |
|---|---|
| BSB poly1850 | 1,600 pages |
| IA poly1850 | 1,000 |
| IA Greek+Latin | 1,000; apply the look-alike rule as an admission step, with mapped and excluded counts |
| IA Russian | 400 |
| Serbia | 300, **with the codec option that adds ј ћ њ љ ђ џ on by default** |
| NLG | 400 |
| ELSTAT | 60 |
| Kosmopolis | 600: the remaining pre-1900 issue `xrysallis-4141`, ≤40 pages, plus poly1900-period issues |
| Lekythos | 290, **≤24 pages per issue, ≥12 issues** |
| Government Gazette | **1982–1990 issues only**, 1,200, year-stratified, ≤20% of pages per year |

- **Remove** Gazette 1910–1959 and every BSB mixed/Fraktur stratum.
- W1 is 20% of each source (1,370 pages). Caps: W1 USD 2.15; W2 USD 8.30.

## Build checklist (plan §7)

1. **Frozen exclusion manifest.**
   - Build it once, hash-bound: v1/v2/test/dev books plus F2 items. Keys: provider id, PDF/image hashes, normalised title+year+author.
   - Add cross-provider edition/alias resolution: bibliographic identity plus page-hash evidence where available.
   - **Quarantine** ambiguous matches; never draw them.
   - Write the manifest hash into every W1/W2 record. Show counts per key and how many were quarantined.
   - Re-derive the draws against it, and report the exact remaining inventory per source after exclusions (plan §5).
2. **Host limiter.**
   - One limiter per host shared **across processes** (file lock).
   - It covers every request: metadata, redirects, retries.
   - Honour Retry-After, refresh robots at W1 start, and enforce the documented MDZ daily Image-API limit. If you cannot find that limit offline, set a conservative configurable cap and say so.
   - Test it with two concurrent mocked processes.
3. **Retention.**
   - Default **no pruning**: keep the page raster that crops are cut from, plus the Google line/token geometry, for every read page.
   - Report the projected disk use for 6,850 pages.
4. **Labels and rules.**
   - Roman-numeral fixes only with context: adjacent §, κεφ., τόμ., vol., cap., a chapter heading, or a numeral sequence. Otherwise exclude.
   - The hyphen rule plus a W1 validation hook, which emits a witness list of hyphen-as-letter cases for checking.
   - Keep literal and normalised labels.
   - Count the ELSTAT raised-dot convention ("·" printed → "." in numeric strings).
   - Columns: `crop_tight_page` (Gazette, Lekythos, Kosmopolis rows; **not admitted**, kept apart in outputs), `marks_correction_required` (all polytonic except Gazette modern and IA poly1850, with the measured rate per row), `screen_merged` (flag only).
   - Spread-cap report: no book/issue above 10% of its class's new rows; no Gazette year above 20% of new modern rows.
5. **C1 / C2 support.**
   - `run.py cards` draws the 100-card uniform seeded sets per source/class in the v2 shape: card_id, crop, google_text, **word_scripts**, with a separate key.
   - It also writes a **separate** supplement file where needed.
   - It applies the small-pool rule: when fewer than 60 pages are available, all pages go to the page check.
   - It runs the W1 changed-line collateral audit for the T4b fix and measures duplicate loss.

## Prove it offline
- Re-run the dry-run parity, resume, rate, credential-scrub and two-process limiter tests.
- Produce the rev-2 `W1_manifest.jsonl` and `W2_manifest.jsonl`, plus the remaining-inventory table.

## Hand-off
- Update `docs/records/harvest/collect_v3/README.md`.
- Commit if git allows; otherwise use the guarded helper.

The last line must be exactly:
`W1b: done | W1 pages: <n> usd cap: <x> | exclusion manifest: <sha12> quarantined: <n> | limiter 2-proc: <ok> | retention: <GB> | tests: <n> passed`
