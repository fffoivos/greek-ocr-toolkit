# T12 — Transkribus (public model "19th-century Greek 8.0", id 148525) on the failed-lines catalogue, Anemi first; compare with the two Google engines (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Transkribus metagrapho/processing API + its documentation; web search allowed for the API docs).
No `.git` writes. CREDENTIALS: environment variables TRANSKRIBUS_USERNAME and TRANSKRIBUS_PASSWORD are set in your process; read them from the
environment only, never print, log, or write them into any file, test or receipt; receipts record only that env credentials were used.
Owner (12 Oct 2026): "you can use both for tests; especially to see if we get better results with Anemi; otherwise we will use easier books."

## Context
T10/T11 (docs/harvest/DOCAI_FAILED_LINES_v1.md, docs/harvest/VISION_VS_DOCAI_v1.md) measured Google Document AI and Cloud Vision on the
469-crop catalogue (same inputs: ~/Projects/greek-ocr-toolkit-ff-merged/.astra/fast_lines/out/stack/r7/failed_lines/, see its README).
Neither emits the early-print glyphs (ϗ ȣ ϛ ϲ…); Vision expands ϗ to "καὶ"; the two disagree strongly on Anemi (between-engine CER 0.30).
docs/research/COMMERCIAL_OCR_20261008.md §Transkribus has what was found about the model, tariffs and API (unresolved); the processing
("metagrapho") API is documented by READ-COOP (find the current docs; token endpoint already verified:
POST https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/token, grant_type=password, client_id=processing-api-client).

## Required
1. `greekocr/readers/services/transkribus.py`: service reader in the same shape as google_docai.py / google_vision.py: token via the endpoint
   above (refresh on expiry), submit one image per process with text recognition by model 148525 (make the model id a parameter; if
   layout analysis is required by the API before HTR, use its default line detection but ALSO try the mode that treats the whole image as
   one line/region if the API offers it — our crops are single lines), poll to completion with a bounded wait, fetch the PAGE XML / JSON
   result, parse lines with text + per-line (and per-char if given) confidence. Cache by crop sha256 under
   docs/harvest/transkribus_failed_lines/responses/. Record credits: query the account's credit balance before the run and after
   (whatever the API exposes), and STOP the run if the balance would go below 50 credits or if any call reports insufficient credits;
   report the credits consumed per page.
2. Order: run the 174 Anemi crops FIRST (the question is Anemi), then the Vouli crops if credits allow (report where you stopped).
   Extend `prototypes/harvest/google_failed_lines.py` with `--engine transkribus` (same per-crop metrics, same characters table with the
   rare-glyph rows, same treatment-by-failure-type table and controls baseline; `--include-anemi`).
3. Three-way comparison `docs/harvest/THREE_ENGINES_v1.md`: per crop the three readings; pairwise NFD CER (DocAI–Vision, DocAI–Transkribus,
   Vision–Transkribus) per source; majority agreement (how often two of three agree exactly, NFD, ignoring line breaks); the rare-glyph
   table for all three; the kai-sign crops (where DocAI wrote "κὶ") with all three readings; a short list of crops where Transkribus emits
   any of ϗ ȣ ϛ ϲ ϝ ϙ ϡ. Raw CSV. State clearly which engine looks best on Anemi by these measures AND that none is a reference.
4. Review page `docs/harvest/three_engines_review.html` in the existing format (reuse the generator): crop + three readings + confidences,
   Anemi group first; images as files beside the page.
5. Cost/credit receipt (credits before/after, per page, calls) in the report and receipt.json; no credentials anywhere.
6. Tests (no network): token/response parsing from stored samples, engine switch, three-way metrics. INVENTORY; docs/API.md + docs/READERS_TRANSKRIBUS.md.
Last line exactly: `T12: done | crops: <n> | credits_used: <n> | rare_glyph_crops_transkribus: <n> | tests: <n> passed`.
