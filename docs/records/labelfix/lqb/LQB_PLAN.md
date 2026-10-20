# LQB: label quality benchmark, plan (17 Oct 2026, 18:54 Athens)

**The owner's question:** "OK there are errors but are they more or less." LQB answers it per fault class, for every label version,
on one frozen truth set. There is no new reading: Sol assembles and scores; the lead plans and reviews.

1. **Truth set** `lqb/truth_v1.jsonl`, frozen with a sha.
   - **Record:** `{line_id, slot?, class, printed, provenance, readers, tier, used_by[]}`.
   - **Sources, pixel-adjudicated only:**
     - the locked strata (release_exclusions `locked_eval`, ia/ib wikisource);
     - C1 verdicts (mark errors, superscript, dash, separator, lunate, lookalike, letter faults);
     - the owner's 39 cards and his sheet notes;
     - the yer adjudication and the RU1 lead rulings and audit;
     - N1: the 82 approved controls plus the lead-ruled slots;
     - CQ1 capitals.
   - **Tiers:**
     - A = owner, or two blind Opus readers;
     - B = lead pixel ruling;
     - C = two agreeing Sol reads. C is kept separate and is never mixed into A/B headlines.
   - **Ids** go into release_exclusions (registered by the sourcing lead), so truth never trains.
2. **In-sample guard.** `used_by` lists every label version whose construction saw that truth item: a control, a lead ruling, or
   rule fitting. The scorer reports such items separately as "in-sample", so a version is never credited for fixing what it was
   tuned on. Example: the RU1 lead review rows are in-sample for ru1_v1; the RU1 audit rows are out of sample.
3. **Version registry** `lqb/versions.json`, each entry by path + sha, with its parent:
   - raw Google (W1/W2 features `text`);
   - the post-convention `label`;
   - the sf6 release;
   - ru1_v1;
   - each W1/W2 admission file;
   - future N1 / punctuation outputs.
4. **Scorer** `greekocr.labelfix.lqb score --truth T --version A [--version B]`.
   - **Per class:** error count, errors per 100 lines or slots, and the paired A→B delta with a document-cluster bootstrap interval,
     reusing `greekocr.adjudicate.score` (Wilson/bootstrap) and the reader union scorer for marks.
   - **Trend table** across all registered versions.
   - "not measured" wherever a class has no truth in that version's population.
5. **Scoreboard page.** Built through `owner_sheet`:
   - a summary table at the top, with plain-language deltas ("fewer/more errors, by how much, how sure");
   - then the changed lines as cards, with Printed = the truth form;
   - one fixed URL, republished for every new version.
6. **First run:** raw Google vs sf6 vs ru1_v1, on the classes where truth exists.
7. **Order:** this plan → ask the peers for the inputs below by reference → a Sol assembly brief (truth + registry + scorer + tests)
   → lead review of the truth inventory → the first scoreboard.
   - From the spell-check lead: the marks truth rows and the sf6 release path.
   - From the sourcing lead: the locked-strata crops and the admission files.

**Codex:** build and score only, ≤1 weekly point (about 41% now).
