# M2 — Combined accent checker on the new sources' blind-check lines (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head at launch). No `.git` writes. Network OFF.
Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU only; the MacBook
rule allows ≤ 10,000 crops: this task touches about 513 line crops. Measurement only: change no detector, reader or recogniser code
(new scripts under `scripts/labelfix/m2_*.py` are fine).

## Why (coordinator, 16 Oct)
R1-A was scored on 14 Wikisource books. The 140k tagged training rows come from new sources, whose Google mark errors differ
(sourcing lead's blind checks, lower bounds from printed→google pairs): grave→acute word-final (OA poly1900 7/39 cards, Lekythos
4/39, Kosmopolis 3/39, Gazette poly1900 2/38, Pleias 2/35, IA poly1850 1/39; zero on BSB poly1850, NLG, Anemi, IA Greek+Latin);
capital breathing dropped or emitted as an apostrophe (NLG); breathing→acute on ὁ/ἡ/ἑ (IA Greek+Latin, 9 marks); iota subscript
dropped (BSB poly1850, IA poly1850).

## Inputs
`~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/{t4c,c0}/` (read-only): per source `<src>/cards.jsonl`
(card → crop, Google label), `<src>/crops/`, `<src>_key.json` (card → line_id, class, tags), `<src>_out.jsonl` (blind verdict per
card: letters y/n, marks y/n/na, errors, detail with printed→google pairs). Read `LABEL_CHECK.md` and `t4c/agg.py` first.

## Pipeline per line (the combined system; nothing from Google at runtime)
1. Recogniser letters + CTC spans: E3 `full_s0` (`~/Projects/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt`) via
   `greekocr/labelfix/ctc_align.py`, CPU, these ~513 crops only; cache the alignments like `.cache/labelfix/align_s0.jsonl`.
2. Detector S6 (`reading.read_ink`) for presence, segmentation and apostrophes.
3. R1-A names: `artifacts/labelfix_r1/output_3678928/A/best.pt` (copy in `~/Projects/greek-ocr-toolkit-spellcheck-r1/artifacts/...`),
   windows exactly as `scripts/labelfix/clariden/r1_extract.py` builds them (font-size rule), CPU inference.
4. K1 filter (`reading.apply_constraints`, default rules).
5. Agreement modes: PRESENCE (detector and R1 agree on which mark kinds are present; names from R1; else HOLD) and FULL (identical
   mark sets; else HOLD). Write both readings + HOLD slots per line.

## Measure, per source and pooled
- For every printed→google mark pair in the blind verdicts: is it corrected (combined = printed), HOLD, or missed, per mode; by the
  four types (grave→acute, capital breathing dropped/apostrophe, breathing→acute on ὁ/ἡ/ἑ, subscript dropped) + other.
- On cards whose verdict says marks are correct ("marks": "y"): how many marks the combined reading changes (= new errors, upper bound),
  and how many go to HOLD.
- Lines with any HOLD per source; coverage (letters the font-size rule admits); cards skipped (crop/letter problems, non-Greek) with reason.
- Spot-check 20 changed words by viewing the crops yourself and say whether the change matches the print.

## Deliverables
`docs/records/labelfix/spellcheck/M2_REPORT.md` (table per source × type × mode), `M2_lines.jsonl.gz` (per line: Google label, recogniser text,
readings per mode, HOLD slots with reasons, change list), scripts, last line:
`M2 RESULT: <n> lines/<k> sources; Google mark errors <e>: PRESENCE corrected <a> HOLD <b> missed <c>; FULL corrected … ; new changes on marks-correct cards PRESENCE <x> FULL <y>; lines with HOLD PRESENCE <p>% FULL <q>%`.
