# R-eff: independent review of the adjudication-efficiency experiment (gpt-6.1-sol, xhigh, network OFF, read-only)

**You are a reviewer.** Do not modify anything except the one review file named below. A live W2 collection imports `collect_v3/` from this checkout, so never touch it.

## The owner's question, verbatim intent
Review the experiment's chains of thought (the readers' reasoning in their transcripts), its conclusion, and the condition the owner enforced. Then answer:
1. Is the conclusion **certain**, or not?
2. **Ideally**, would more work be done, and what exactly?
3. **Practically**, is it OK to rely on it?

## Context
- **Purpose.** Opus readers check OCR line labels against crops. The owner's rules:
  - the number of readers per item never drops;
  - an efficiency change is adopted only if an experiment shows no quality loss;
  - the adoption rule: agreement with the truth stays within the control's own reader-to-reader variance (E0 run twice), and unresolved answers do not rise.
- **Arms**, each changing one factor against the control E0:
  - E0a/E0b: control, run twice;
  - E1: all items of a bed in one reader context (100 BSB cards, 59 yer items) instead of 50 or about 30;
  - E2: word and letter crops only, no full line;
  - E3: compact prompt;
  - E4: E1 + E3.
- **Beds:**
  - BSB: 100 C1 cards; reference = the C1 verdicts.
  - yer: 59 items / 65 masked word-final ъ/ь positions; ink truth from a blind adjudication.
  - owner39: the owner's 39 adjudicated cards.
- **The condition the owner enforced mid-run:** "you are burning a lot of usage and we don't get a refresh until 40 hours from now … think smarter". The lead paused all readers, kept the partial outputs, and recommended:
  - stop E3/E4 (expected gain small, because images dominate the tokens);
  - reject E2;
  - adopt E1.
  The owner then said to cache the experiment and keep the conclusion. E3, E4 and owner39 were left incomplete.
- **The conclusion as recorded:** `docs/records/harvest/collect_v3/c1/efficiency/CACHED_STATE_20261017.md`.

## Materials (read-only)
- **Packs, keys, truth, scorer:** `docs/records/harvest/collect_v3/c1/efficiency/` (README.md, keys/truth.json, score.py, MANIFEST.json).
- **Reader outputs:** `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/eff/out/*.jsonl` (bsb and yer). owner39 answers: `docs/records/harvest/collect_v3/c1/efficiency/packs/owner39/*/*/answers.jsonl` (partial).
- **Usage:** `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/eff/usage_log.tsv`, measured per reader from agent results; there is no cached/uncached split.
- **Reader transcripts (the chains of thought):** `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/tasks/<agent>.output`, a JSONL agent transcript per reader. The agent-to-arm map is `scratchpad/eff/agents.tsv`.
  - They are large: sample them with tools (grep, head, jq-like parsing in Python). Do not load them whole.
  - Look for: how each reader actually worked (whole-crop vs zoom, composites, shortcuts); signs of fatigue or degradation late in the long E1 contexts; any key or truth access; and how the paused runs behaved.
- **C1 reference verdicts:** `docs/records/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__{a,b}.jsonl`. Yer truth: `docs/records/harvest/collect_v3/c1/yer_adjudication/` (table.json, ink_*.jsonl).

## Do
1. **Score what exists** with `score.py`, writing to a temp path outside the repo or under `/tmp`.
   - Score bsb and yer for every complete arm: E0a, E0b, E1, E2.
   - Report the paired E0a–E0b agreement (the variance bar) and each arm's agreement with truth and with E0a. Give per-card or per-slot counts, not only rates.
2. **Check the E1 claim specifically:**
   - Is the E1 agreement with truth within the E0a–E0b variance on both beds?
   - Is quality flat across the E1 context, first half vs second half (position effect)?
   - Is the token saving real per card, given the usage records? Note that reader durations and tool uses vary.
3. **Read a sample of the transcripts** for each arm and check whether the readers' reasoning supports their verdicts. Flag shortcuts that could inflate agreement:
   - accepting labels without zooming;
   - montage composites in E2;
   - copying earlier calls.
4. **Assess the statistics:** n per bed, one E1 reader per bed, two beds, and no repeat of E1. State what difference in quality this design could have detected.
5. **Judge whether stopping E3/E4 and leaving owner39 incomplete loses anything decision-relevant.**

## Output
Write `docs/records/harvest/collect_v3/c1/efficiency/REVIEW_R-eff.md` with:
- the score tables;
- the E1 checks;
- transcript findings with quotes and line references;
- a verdict per question:
  - (1) certain? yes / no / partly, and why;
  - (2) ideal additional work, as a list with cost in reader runs;
  - (3) practical reliance: OK / OK with conditions / not OK, with the conditions.

The last line must be exactly:
`R-eff: done | E1 within E0 variance: bsb <yes|no|n/a> yer <yes|no|n/a> | certain: <yes|no|partly> | rely in practice: <ok|ok-with-conditions|not-ok>`
