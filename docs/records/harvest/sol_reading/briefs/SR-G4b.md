# SR-G4b: accept pixel-exact reproduction, re-flag with p1c1, rebuild the re-read pack

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading`, and finish in this turn. The constraints are the same as SR-G4 (read it).

**Lead ruling (17 Oct).** A reproduced zoom image that is pixel-identical to the viewed image clears the provenance check: same mode, same dimensions, every RGB(A) pixel equal (MAD 0). The match is recorded as `match: "reproduced_pixels"`. PNG byte differences from embedded timestamps or metadata are not evidence of an outside source.
- Anything not pixel-identical stays a violation.
- Literal-path rules are unchanged.

1. Implement the ruling in scanner v4 and add a test: the same pixels with a different PNG tIME chunk pass, and a 1-pixel difference fails. Re-scan p1c1 and keep the previous scan as `.scan.v4a.json`.
2. If p1c1 is now ok, re-run `flag_full.py` over p1c1..p1c4 and regenerate `PASS1.{json,md}`.
3. Rebuild the re-read pack `PACK_ROOT/grave_full/p2/` from ALL flagged items. Overwriting the SR-G4 p2 folder is allowed, because no reader has opened it: check that it has no `answers.jsonl` and no `zoom/` first, and stop if it does. Run the closure scan.

Last line: `SR-G4b READY: scans <ok list> items=<n> flagged=<n> (by type …) p2 items=<n> controls=<n> G1 overlap agree=<x>/<n>`, or `SR-G4b BLOCKED: <reason>`.
