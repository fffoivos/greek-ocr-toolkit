# CP-H1 — independent certification of the H1 pilot sample (T13c) code and numbers. Reviewer: gpt-6.1-sol, xhigh.
ROLE: independent fresh-eyes certifier; implementer (Codex Sol) ≠ certifier. Verify firsthand, recompute, report raw. No network calls, no background jobs.
SANDBOX: workspace-write only so pytest can write temp files (set TMPDIR=$PWD/.review_tmp; delete it at the end); do not edit tracked files.
READ FIRST: docs/briefs/T13c_pilot_sample_anemi.md (the brief), docs/harvest/PILOT_v1.md (the report), docs/harvest/pilot_v1/summary.json and page_gates.json,
~/Projects/glossapi-development/docs/experiments/glossapi_improvement_20261006/PLAN_GLOSSAPI_v3_20261007.md §H1 (gates, tiers, list-return rule, rare-glyph rule).
Records (bulk, outside the repo): ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c/pilot_v1/records.jsonl (14,200 lines; 500 sampled),
Google raw responses under .../pilot_v1/google/, page renders under .../pilot_v1/pages/, review images under .../pilot_review_images/.
SCOPE: git range c699f4d..2bbd00f — greekocr/harvest/ (package + CLI), tests, docs/harvest/PILOT_v1.md, docs/harvest/pilot_review.html.
MANDATE / acceptance criteria:
1. The owner's constraints were honoured: ≤ 500 lines sent to Google; only long complete lines (width ≥ 0.8 column band, not edge-touching, all gates passed);
   all 150 target books attempted (142 yielded), 2 middle pages per book; no Vouli; cost ≤ USD 3 (report says USD 1.50 = 1,000 calls). Recompute from records.
2. Gate logic matches the plan: height ≤ 1.5 × body pitch, curled-edge exclusion, neighbour-height, column band, page gates (rotated / table / bend scout / non-body). Spot-check
   10 gate decisions against the page renders by eye (describe what you saw).
3. Tiering: tier 1 = exact NFD/whitespace agreement (incl. documented substitutions), tier 2 = ≤ 2 NFD edits, tier 3 = disagree, rejected = empty/obstructed/garbage; the
   list-return geometry rule (side-by-side joined, stacked rejected, garbage dropped/obstructed). Recompute the tier counts (188 / 217 / 82 / 13) from the raw Google responses.
4. The disagreement analysis: coordinator's recount on the 299 tier-2+3 lines: diacritics differ on 188 lines, punctuation 133, Greek letters 89; Vision has FEWER marks in 121
   lines vs DocAI fewer in 11; marks that differ: acute 106, grave 94, smooth breathing 69, circumflex 44, rough 36, iota subscript 23; 92 of 299 lines are identical once all
   diacritics are removed. Verify these numbers independently (they will go into the owner's morning report) and say whether "Vision systematically drops polytonic marks" is
   supported.
5. Provenance: every record carries stack_commit 52cee3b, harvest_code_sha256, gates, readers' raw outputs and confidences; images referenced by path; no credentials in any file.
6. Tests: run `.venv/bin/python -m pytest tests -q -p no:cacheprovider -k harvest` and report counts.
DISPOSITION: BLOCKER/HIGH fixed before any scale-up; MEDIUM/LOW logged.
DELIVERABLE: markdown; header; one-line verdict; findings most-severe-first with path:line and failure scenario; the recomputed numbers in a table (yours vs reported);
cleared items. Last line exactly: `VERDICT: <PASS|HOLD> ... | BLOCKERS: <n> | HIGH: <n>`.
