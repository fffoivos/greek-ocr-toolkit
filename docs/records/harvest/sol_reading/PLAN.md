# Sol as a blind pixel reader: plan (17 Oct 2026, written 12:30 Athens)

Owner's question: can gpt-6.1-sol ("Sol", Codex CLI 0.159.2) do the blind card reading that Opus readers do today?
- (a) How fast does it consume the Codex limits on the same reading task?
- (b) How accurate is it on the same beds, and how much do results change from one reader to two?

Lead: the Opus "Sol reading experiments" session. Coordinator: the Fable coordinator. Branch `opus/sol-reading`.

## Constraints
- **No new Opus reader runs.** The Opus reference is the cached efficiency experiment only (`collect_v3/c1/efficiency`,
  CACHED_STATE_20261017.md).
- **Codex limit.** Run the probe before and after every run, and run one reading at a time so each delta can be attributed.
  STOP if weekly used would pass 80% (remaining < 20%). The credits balance is also recorded; a fall in it means spend on the
  owner's money, so the runs stop.
- **Labels are the ink.** Blind reading: isolated copied folders, no key in reach, items and options in random order, planted
  controls at about 10%. Leak scan of every pack and of every rollout.
- **Sol does the tooling.** Every pack builder, scorer, scanner and ledger is written and run by Sol from briefs (medium effort).
  The lead writes plans, prompts and briefs, launches the reading runs (the experiment itself), and reviews.

## Step 0: probes (done 12:27)
- **Limit baseline:** weekly bucket `codex` 32.0% used (window 10080 min, reset Thu 22 Oct 09:13). No 5-hour bucket is reported for
  this account. Credits balance 59,974.71.
- **Images: both mechanisms work.**
  - The `view_image` tool reads PNGs from the workspace. Codex runs it in code mode, inside an `exec` call whose input carries the path.
  - `codex exec -i` attaches images to the first prompt.
  - On 2 BSB cards (c001, c002), both forms read the line correctly. Both also caught the missing rough breathing on Ῥωσσίας that the
    C1 reference flags.
- **Cost of the probe:**
  - Tool form: 78.0k input tokens (62.6k of them cached) and 0.6k output for 2 cards with 4 image views. Every tool turn re-sends
    the whole context.
  - Attachment form: 19.0k input (5.5k cached) and 0.3k output.
  - The fixed Codex system prompt is about 13–18k tokens per turn.
- **Reads are not sandboxed.** A command in the reader sandbox read a canary file outside the workspace. `workspace-write` limits
  writes only. Blinding therefore rests on three things:
  - physical isolation (packs copied outside every repo, keys far away);
  - the prompt's boundary;
  - a mandatory rollout leak scan.

  The leak scan checks every tool input (exec commands and `view_image` paths) for any path outside the reader folder, and for the
  strings `key`, `truth`, `verdict`, `Projects`, `..` and `~`. Any hit invalidates the run. The cached Opus readers had the same
  file-layout boundary, without a scan.

**Mechanism chosen:** the tool form, all items of a bed in one context. It matches the Opus E1 protocol (view, then zoom with
ImageMagick), so the comparison isolates the reader. Single-item form is not needed. The attachment form is cheaper, but it cannot
zoom. It is recorded as a possible follow-up arm, and is not run here.

## Beds (same items as the Opus reference)

| Bed | Items | Truth | Opus reference (cached) |
|---|---|---|---|
| yer | 59 lines, 65 masked word-final ъ/ь slots | ink, two blind Opus readers plus INK.md (`keys/truth.json` → yer) | E0a and E0b: two full passes, each split over 2 readers; E1: one reader, all 59 |
| bsb | 100 C1 cards, bsb poly1850 | C1 verdicts (one Opus reader per card). This is a reader reference, not pixel truth. | E0a, E0b, E1 as above |
| owner39 | 39 word cards, R2 T4 protocol | owner-confirmed sheet; card `…l0013:s33` = ἦγε, breathing excluded (overlay v1.1) | partial E0a/E0b only: 5, 13, 8 and 7 of 39 cards |

**Owner39 selection.** The 39 cards are exactly the held-out slots where the neural mark reader R1-A disagrees with truth (spell-check
lead, 12:3x). R1-A is therefore 0 by construction here. 16 of the truth forms were set by Opus readers. The bed shows how Sol does on
cards that are hard for a model, not a population rate.

## Packs (built by Sol, brief SR-B1)
Each reader gets its own folder under the pack root
`/private/tmp/claude-501/…/scratchpad/sol_reading_packs/<bed>/<reader>/`, outside every repository. The folder holds:
- the item file and copied PNGs, with content-hash names, no symlinks and no metadata;
- for owner39, the R2 `README.md` and `answer_schema.json`, byte-identical.

Private keys (id map, orders, option permutations, control answers) stay in `docs/records/harvest/sol_reading/keys/` in the worktree.

**Order and ids.**
- r1 gets a fresh seeded random order. r2 gets the exact reverse, as in the Opus protocol.
- Every item gets a new opaque id, so the E1 ids and file names (c001…, a001…) are not reused.
- Owner39 option letters A–D are permuted per card (seeded), and the key maps them back.

**Planted controls (about 10%, not announced beyond the owner39 prompt's verbatim sentence).**
- **bsb, 10 cards:** taken from another LABEL_CHECK_v2 polytonic stratum (nlg poly1850 C1 cards with verdict y/y/y), with one
  injected error in `google_text`:
  - 5 letter controls: one interior base letter of a ≥5-letter word is replaced by a visually distinct Greek letter, so the
    expected answer is letters=n;
  - 5 mark controls: the accent is removed from one ≥5-letter word, so the expected answer is marks=n.

  The expected answer holds whether or not the original label was right.
- **yer, 6 items:** from ia_russian cyrillic C1 cards outside the 59, using the same masking:
  - 3 masked word-final ъ that Google wrote (Google's ъ was never wrong, 0/26) in pre-1918 lines;
  - 3 masked word-final ь in lines with no ъ, ѣ or і (modern orthography).

  The lead pixel-checks all 6 on a contact sheet before any reader starts.
- **owner39, 4 cards:** pixel-verified planted controls from the R2 T2/T4 decks, rendered the same way.

**Gate.** As in R2, a reader with more than one control error in a run is flagged, and its answers are reported separately.

## Arms
Each reader is one `codex exec` context over a whole bed: gpt-6.1-sol, effort medium (the guide's default), no network, no web search.
- **S1:** one Sol reader (r1). r2 is a second, independent S1 sample, and r1 vs r2 is Sol's run-to-run variance. It compares
  directly with Opus E0a vs E0b.
- **S2:** r1 + r2, plus a Sol tie-break reader r3 on the disagreements only, resolved 2-of-3.
  - r3 runs in a fresh context, in random order, with controls at about 10% (at least 1).
  - The disagreement unit is a card's (letters, marks, crop_ok) for bsb, a slot for yer, and the anchor tuple (base + 4 heads)
    for owner39.
  - When r3 matches neither r1 nor r2, the item is unresolved.

Runs (9, sequential): owner39 r1 (the pilot), yer r1, bsb r1, owner39 r2, yer r2, bsb r2, then 3 tie-breaks.

**Budget gate after the pilot.** From the owner39 r1 delta (weekly points per 100 cards), project the remaining 8 runs. Continue
only if the projected end is ≤ 75% weekly used. Otherwise, cut in this order: bsb r2 + bsb tie-break, then yer r2.

## Measures (per bed × arm)
- **Accuracy against truth,** with the existing scorer (`efficiency/score.py`) after Sol maps the opaque ids back:
  - bsb: letters, marks, crop_ok, and the joint card;
  - yer: slot accuracy and item accuracy;
  - owner39: base, accent, breathing, diaeresis and subscript per head, and the joint anchor.
- **Agreement with Opus:** E0a, E0b and E1 per bed, and the owner39 partial E0 cards.
- **Disagreement mix:** unresolved, `u`/`unknown`/`unreadable` counts, and control pass.
- **Cost:** tokens per card (input, cached input, output, reasoning, from the rollout's `total_token_usage`), tool calls, and
  wall time.
- **Limits:** weekly percent and credits delta per run, and per 100 cards.
- **S1→S2:** cards whose verdict changes, the net accuracy change, and the cost ratio S2/S1. The yardsticks are Opus E0a vs E0b
  and Sol r1 vs r2.
- **Cost against Opus:**
  - Claude token totals from `usage_log.tsv` (E1 is about 1.3k tokens per card for bsb and about 2.2k per item for yer);
  - Sol limit points per 100 cards.

  The two meters are different, so the report gives both. It does not convert one into the other.

Where Sol and the bsb reference disagree, the reference is itself an Opus reading. Those cards are listed for a later pixel check, and
neither side is called right.

## Prompts
The prompts are in `prompts/{bsb,yer,owner39}.md`. Each protocol is verbatim from the Opus packs. The changes are below; guide notes
are in `GUIDE_NOTES.md`.
1. **Header for non-interactive runs:** infer intent, do not ask, finish in this turn. (GPT-6 guide: initiative; Codex guide:
   autonomy for evals.)
2. **Tool names:** "Read tool" → `view_image`, and "Write tool" → shell writes.
3. **Batched image views,** about 5–10 per call. (Codex guide: batch reads and maximise parallelism. This also cuts the per-turn
   re-send cost measured in the probe.)
4. **Explicit "Done when" criteria** (count, order and coverage, checked by a command, then a short plain final reply). (GPT-6 guide:
   clear completion and stop criteria; concise final answers.)
5. **yer contradiction removed:** "crop (absolute path)" → "relative path". The old wording contradicted the packs. (GPT-6 guide: audit
   for conflicting instructions.)
6. **Placeholders bound:** CARDS, OUT, ZOOM and <BATCH_DIR> are bound to the current folder.

Every task rule, every field and the answer format are unchanged.

## Deliverables
- `PLAN.md` and `GUIDE_NOTES.md`;
- `prompts/` verbatim, and `briefs/`;
- `keys/` (private);
- `answers/<bed>/<reader>.jsonl`;
- `usage_ledger.json` and `RESULTS.md`.

All are committed on `opus/sol-reading` by Sol, with no push.
