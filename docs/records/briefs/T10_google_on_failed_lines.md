# T10 — Document how Google Document AI treats the line finder's known failures, before any harvest (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Google Document AI calls via the existing adapter; ADC credentials are
already configured on this Mac: project ocr-ground-truth-20261008, processor in `eu`, see docs/B_training_data/a_google_ocr/readers/READERS_DOCAI.md and
greekocr/readers/services/google_docai.py). No `.git` writes. The Mac is not a processing worker: this is ~430 small API calls, fine.

## Input: the failed-lines catalogue (read its README first)
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/failed_lines/
- controls_owner_marked.json (122 owner-verified controls, 181 current-output crops = the baseline for good crops)
- multi_line_segments.json (133 owner-marked multi-line segments, 271 current-output crops = what a harvest would send)
- page_comments.json (51 owner comments with failure_types; page-level; derive crops by intersecting the page's r7 <page>.json items
  with the region when feasible; otherwise report the type from the two crop files only)
- crops/ (707 grayscale polygon crops; 277 are Anemi `an-*`)
LICENCE RULE: EXCLUDE every Anemi crop (file or page id starting `an-`) from any Google call. Count them in the report as "withheld".

## Required
1. `prototypes/harvest/google_failed_lines.py` (+ a tiny CLI): for every non-Anemi crop in the two crop files, call the Document AI
   adapter ONCE (cache responses to `docs/records/harvest/docai_failed_lines/responses/<crop_id>.json` keyed by the crop's sha256; never re-call
   a cached crop), with language hints ('el',) and symbol-level output on. Record per crop: crop id, catalogue file, owner failure type /
   r7_status / expected_ocr_risk, crop width/height px, lines returned (count), text per line, total characters, characters per 100 px of
   width, mean and min symbol confidence, whether the output is empty, and the set of Greek characters emitted.
2. Characters table: for ALL calls pooled and per source (Vouli `s2-*` vs Internet Archive if present), the set of characters Google
   emitted, with counts; list specifically whether any of ϗ ȣ ϛ ϲ Ϲ ϝ ϙ ϡ ͅ ʹ ͵ appeared, and the polytonic combining marks it uses (NFD).
   This measures, it does not assume, what Google knows (owner, 11 Oct: "it might not be able to").
3. Report `docs/records/harvest/DOCAI_FAILED_LINES_v1.md`: per failure type (from the catalogue's types), n crops, how Google treated them
   (lines returned distribution, empty rate, confidence, chars/100px vs the controls' distribution), and a verdict per type: "Google
   exposes it" (multi-line return, empty, low confidence) or "Google absorbs it silently" (plausible single-line output with truncated or
   appended text) — the silent ones need line-finder-side filters. Include the controls' baseline numbers first. Raw table as CSV.
4. Review page `docs/records/harvest/docai_failed_lines_review.html` in the style of scripts/glyphs/pages_review.html (reuse its generator or
   format): one card per crop with the crop image, the owner's observation, failure type, Google's text (per line) and confidence, so the
   owner can read the treatment by eye; group by failure type; phone-width safe; images as files beside the page (not data URIs).
5. Cost receipt: number of calls, estimated cost (Document AI Enterprise OCR list price), written into the report and
   docs/records/harvest/docai_failed_lines/receipt.json. Stop and report if any call returns a billing/permission error.
6. Tests (no network): parsing of the two catalogue files, the Anemi exclusion, the per-crop metric computation from a stored sample
   response, the characters table. INVENTORY registration for fixtures. docs/API.md entry.
Last line exactly: `T10: done | calls: <n> | withheld_anemi: <n> | tests: <n> passed`.
