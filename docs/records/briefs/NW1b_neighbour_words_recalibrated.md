# NW1b: the `neighbour_words` screen, recalibrated on the owner's own verdicts (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**This supersedes NW1** (docs/records/briefs/NW1_neighbour_words_screen.md). NW1 was stopped mid-run because its calibration truth was wrong. Its partial work is left uncommitted in this worktree (greekocr/harvest/neighbour_words.py, admission.py, stage_crops.py and test edits, docs/records/harvest/collect_v3_admission/nw1/). **Review it, keep what is sound, and redo the calibration below.** Also include the untracked `tests/test_adm5b_schema.py` and `greekocr/_vendor/codec/v2.json` if ADM5b needs them (check `.gitignore`), and say what you did.

**Owner rule (verbatim):** "In general there has been at least a whole word from one of the other lines to show for it to be even worth considering for filtration". The owner marked 22 cards "this is fine" that the checkers had called readable overruns.

Everything else from NW1 stands:
- use the existing foreign-ink ownership measure (`greekocr/glyphs/foreign_ink.py` + `greekocr/glyphs/recut.py`, frozen params 801d517e), measure only, no masking;
- the run root is read-only;
- byte-exact interpreter `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`;
- schema, withdrawn list, no PNG deletion.

## 1. Whole-word criterion (defaults)
A connected run of foreign-ink components whose combined extent reaches a full word:
- **≥ 4 components**;
- **≥ 3 x-heights wide**;
- **median component height ≥ 0.6 × x-height**.

**Half-letters at the edge are never a reason to drop.**

## 2. Calibration truth (replaces NW1's)
**KEEP (22, the owner's "this is fine"):**
- bsb_poly1850--e18cacecef3b4590--s005-l0076
- bsb_poly1850--e18cacecef3b4590--s007-l0061
- gazette_modern--0d0b2233a81e355c--s000-l0019
- gazette_modern--4b5e54c14bfb5810--s000-l0031
- gazette_modern--54876940c2de96c3--s000-l0062
- gazette_modern--5af16c5d518d2ebb--s000-l0059
- gazette_modern--5af16c5d518d2ebb--s000-l0131
- gazette_modern--7f0595fd3a453e0b--s000-l0025
- gazette_modern--836a4d5d06d0f16d--s000-l0045
- gazette_modern--f375bcf80bc8fca3--s000-l0025
- ia_poly1850--36dcee7ce4c29f8b--s004-l0062
- ia_poly1850--63f57af8d450f3e8--s003-l0021
- ia_poly1850--c39403323b6d5d89--s005-l0007
- ia_poly1850--c39403323b6d5d89--s005-l0031
- ia_poly1850--f806d3f10b2ecf9c--s003-l0050
- ia_russian--61f76a57b26f9b13--s004-l0002
- ia_russian--6cfc00f06e0f7241--s007-l0003
- kosmopolis--109d033afd51aea6--s000-l0019
- kosmopolis--62ca52b56ebe780a--s005-l0028
- kosmopolis--ecc23d7812913d0a--s005-l0011
- nlg--1144074169f43992--s006-l0032
- nlg--3d6bd7bd688acb61--s006-l0005

**BORDERLINE (report its value; not gating):** ia_poly1850--36dcee7ce4c29f8b--s004-l0032 (owner: "a column to the right … less than fine").

**DROP:**
- every screen_merged card (two or more complete lines) shown in `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/` (commit 83aaab5d; read its manifest), including the three-line crops;
- the 8 owner "true issue" cards: gazette_modern--0020420cfe156a73--s000-l0039, -l0138, -l0141, -l0162, -l0228; gazette_modern--1f7db88d63c02afa--s000-l0287; nlg--6146c0455e0103d2--s001-l0006 (and the eighth, if the gallery lists it; otherwise say so).
- **Note:** screen_merged already drops the merged cards. Report the screen's result on them both standalone and combined with screen_merged.

## 3. Gate (before applying it anywhere)
- **0 false drops on the 22 KEEP cards**, and **every DROP card dropped** (by neighbour_words, or by neighbour_words ∪ screen_merged; report both).
- Report precision/recall on this set, the measured run (components, width in x-heights, median height) for every card, and a small grid around the defaults.
- If the defaults fail the gate, choose the nearest setting that passes. If none passes, **do not apply**: write `nw1b/GATE_FAIL.md` and stop.

## 4. Apply (only if the gate passes)
As in NW1:
- add rule `neighbour_words` to the admission tool and bump the version;
- re-issue the W1 admission (input `w1_originals_v3.jsonl`), with drop counts per source × class;
- write `w1_neighbour_words_withdrawn.txt`;
- mark `admitted: false` in the crops manifest, with no PNG deletion;
- later admissions pick it up via the same CLI.

## Tests
The planted cases (a full neighbour word → drop; descender halves → keep; clean → keep), the 22-keep gate as a test, and the existing tests.

Leave a guarded commit list. The last line must be exactly:
`NW1b: done | gate: <pass|fail> | keep false drops: <n>/22 | drop recall: <a>/<b> (nw alone <c>/<b>) | borderline: <value> | thresholds: <...> | W1: 28798 -> <pass> (neighbour_words drops <n>) | withdrawn: <n> | tests: <n> passed`
