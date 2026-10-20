# CQ1 build handoff

No reader or limit probe has been launched. Closure and synthetic checks pass; the lead control review remains pending. No empirical score.json exists until the run.

- Pack: /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/solcap_qual/cap1/r1/
- Truth, options and exact slot identities: keys/cap1.json
- Existing-v2 overlap: keys/v2_overlap.json (60 bed + 6 controls)
- Reserve these slots from future top-up: keys/topup_exclusions.jsonl
- Lead review: control_review/controls.png, index.json, REVIEW.md, lead_review.json
- Launch after review: bash artifacts/cq1/RUN_CMD.sh from any directory
- Scorer: tools/score_cq1.py; results replace docs/labelfix/spellcheck/R2/CQ1_REPORT.md

The builder uses seed 20261017, preserves native line pixels, and draws boxes without modifying the line strip. Missing original raster paths fall back to the original R2 native line strip; each chosen asset and its hash are recorded privately. All 66 anchors bind to exact v2 slots through the hash-verified saved recogniser alignments. Box adjustments for touching components and numeral prefixes are recorded in keys/box_overrides.json. Rendering/geometry sheets and rejected control previews stay outside the pack.

No capital grave exists in resolved T2, so that tuple remains unqualified. Existing-v2 reuse follows the brief's parenthetical qualification-only allowance; selecting a bed with no existing-v2 overlap cannot supply the requested compounds.

Build stages (on an empty pack destination): tools/build_cq1.py --allow-existing-v2, tools/bind_v2_overlap.py, tools/scan_packs.py <reader-folder>, tools/validate_build.py. Use the handover's x86_64 Python 3.11 with -B. The builder refuses to overwrite completed item assignments. Never regenerate after lead signoff or a reader start.
