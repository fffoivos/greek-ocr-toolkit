# Sol routing for the spell-check track, 17 Oct 2026

Owner directive (verbatim, via coordinator): "make sure that all coding/cli/scripting workflows are sent to sol; also … what other tasks
that do not require finesse but execution precision can be sent to sol".

**From now on the lead writes no code and runs no scripted pipelines.**
- **Sol does** every script, deck builder, resolver fix, census, export, verification, rsync readback, hash check, inventory, git
  merge/rebase and test run. Each one is a Sol brief, medium effort for mechanical work, with tests and a receipt.
- **The lead keeps** planning, briefs, reviews of Sol's output, pixel adjudication and card reading, rulings and reports.
- **Opus reader agents** (blind card reading) are unchanged.

## A. Compliance audit of today (operations the lead ran by hand)

"Migrate" means the operation goes into a Sol-maintained tool with tests in **one batch brief, SR1**. SR1 runs on `opus/cleanup-1` after
CU4 lands, because most of these belong in `greekocr.adjudicate` / `greekocr.recogniser`. "One-off" means it will not recur; the reason
is given.

| # | What I ran by hand | Where | Disposition |
|---|---|---|---|
| 1 | Owner pages: `build_audit_page.py`, `build_audit_template.py` (audit 100 + highlights + tags + magnifier), `build_subst_page.py`, `build_r1a_errors.py` (39-card sheet) | scratchpad; now committed under `R2_evidence/page_builders/` | **Migrate**: CU4 `owner_sheet.render` plus re-emission tests (already briefed). SR1 adds the page specs as data files. |
| 2 | Tag/ink crosstab (additions with/without detector ink vs print verdict), incl. the slot-lookup bug I made and then fixed (`start <` vs `<=`) | inline Python | **Migrate**: SR1 tool `edit_evidence_crosstab` (per change: kind, head, slot, ink, verdict), with a test on the 101 audit changes; the bug was mine, so a test pins it. |
| 3 | Substitution census (`contra.py`), substitution sample (`subst_sample.py`), owner-note follow-up (`notes6.py`): read-only scans of the release overlay on the Clariden login node | scratchpad + Clariden | **Migrate**: SR1 tool `release_census` (substitution tiers, per wave, seeded sampler, single-line evidence dump), run as Sol briefs on the login node. Needed again for R2b override acquisition (tranche 5). |
| 4 | L1F diagnostics (`l1f_diag.py`, `l1f_extract17.py`) | Clariden | **One-off**: L1R4 was cancelled by the owner's "recogniser only locates" decision; the float32-tolerance predicate now lives in `greekocr.recogniser.confidence_matches` (CU3). |
| 5 | DEV-truth hallucination counts by letter/context; training-label prior counts (ο/οι, numeral Α) | inline Python | **Migrate**: these are the R2 target/non-target slice definitions. SR1 adds them to `r2_score.py` as named slices (capital/ALL-CAPS/numeral, ο/monotonic, subscript, exact-name), with tests. |
| 6 | Source/document counts for plan Addendum A (W1 strata, v2 outside the 316, teacher-seen lines) | inline Python | **One-off**: superseded by R2C `doc_roles.json` and R2P2 `population/counts.json`, which compute and record the same counts with receipts. |
| 7 | Control contact sheets for pixel verification | scratchpad | **Migrate**: SR1 adds `controls_review_sheets` to the deck builder (grid of word zoom + expected form, ≤ 12 per sheet). The lead still does the pixel judgement. |
| 8 | Pilot / control gate checks on reader answers (`ctrl_check.py`) | scratchpad | **Migrate**: covered by R2C2's resolver dry-run mode. SR1 adds a `--batch-check` CLI so each finished batch is checked through Sol. |
| 9 | Reader batch folder preparation (copying blind cards into isolated folders, splitting into 110-card batches, reverse order for reader 2) | inline Python | **Migrate**: SR1 tool `deal_batches` (implements `protocol.deal` from CU4: isolated folder, no key reachable, receipt with hashes). |
| 10 | Tranche (6) single-card render (line / word 3× / letter 8×) | inline Python | **Migrate**: same as #9, profile `mark` of `build_deck`. |
| 11 | Exports: R2 evidence (owner remarks, sheet notes), 39-card export, final owner export, card-inputs JSON | inline Python | **Migrate**: SR1 tool `owner_notes_export` (artifact db → JSONL + card join + status convention per sheet). The db read itself stays a lead action (artifact tool), and its output file is the tool's input. |
| 12 | Truth overlay v1.1 written by hand | `r2prep` | **Migrate**: SR1 tool `truth_overlay add` (validates the tuple, parent, evidence paths), with a test. |
| 13 | File custody: LARGE_FILES sha manifest (R2C), the 61 r1 files copied + sha-verified into main `artifacts/`, fixture copies into the cleanup worktree, the R2C commit/re-commit | shell | **Migrate**: SR1 tool `artifact_custody` (copy + sha manifest + verify), plus Sol does all commits. |
| 14 | Full test-suite runs (cleanup worktree, rehearsal worktree) as lead verification | shell | **Recurring → Sol** (template B4). The lead reviews the report. |
| 15 | Git: worktree creation, branch tables, ctc_align blob table, commits of briefs and Sol output | shell | **Recurring → Sol** (B8). The lead commits only briefs (one `git add` + `git commit` of the brief file), until the git-capable Sol launcher is confirmed. |
| 16 | Policy digest / hashed-set diff checks | shell + Python | **Recurring → Sol** (B4/B8). |
| 17 | Clariden status checks (`sacct`, log reads) | ssh | **Recurring → Sol** (B2/B3). The coordinator watches the queue. |

## B. Recurring execution-precision tasks → Sol (brief templates)

Every brief names: the worktree and branch; network on/off; the files allowed to change; and the hard constraints:
- `greekocr/labelfix` and the 16 policy paths byte-identical;
- digest 6f62925a;
- no submission;
- cert rule: never refresh; auth error = stop.

Every brief ends with a single `<NAME> READY: …` last line and writes a receipt (inputs + outputs with sha256).

| ID | Task | Template essentials |
|---|---|---|
| B1 | **Cluster package: deploy + sha + test-only** | Build the package; local mock through the exact entry point; deploy; `*_DEPLOY_SHA256.txt` local vs remote; `sbatch --test-only`; recipe disclosure table; submit and pull commands in the report. The coordinator submits. |
| B2 | **Readback + verify** | Pull receipts/exports/checkpoints listed in the handoff only; verify every sha against the stage receipts; READBACK_RECEIPT.json; stop on mismatch; finish before the cert deadline. |
| B3 | **Digest / scoring** | Scorer on fixed cohorts with overlays applied symmetrically; per-seed tables; paired ledgers; cluster intervals; timings vs forecast; no new inference beyond what is named. |
| B4 | **Full test suite + report** | Run `tests/` (and named subsets) outside the sandbox where possible; list failures vs the known pre-existing set (collection_outputs 3, provenance_cli_api 2, apply_clean 5 errors, flaky deadline test); policy digest + greekocr sha list. |
| B5 | **Deck build** | Spec → `build_deck` (blind + private key outside, content-hash names, leak scan, controls shuffled); `controls_review_sheets` for the lead's pixel check; batch dealing into isolated folders (#9). |
| B6 | **Tranche resolve + inventory** | Resolver on reader answers (controls gate, invalid votes, tiebreak deck), usable-slot inventory per slice, Opus usage table from the agent results the lead supplies; report section. |
| B7 | **Owner sheet build** | Spec → `owner_sheet.render` → HTML file. The lead reviews and publishes through the artifact tool; notes export (#11) afterwards. |
| B8 | **Git operations** | Merge/rebase rehearsal and execution, archive moves, worktree add/remove (after an untracked-file listing), commits; hashed-set diff + digest + suite after every change; never push. |
| B9 | **Census on the cluster (read-only)** | Login-node scans of saved outputs with `release_census`; ≤ a few minutes; output small JSON. |
| B10 | **Custody / cleanup** | Copy + sha + verify (#13); approved deletions only, from the owner's approval sheet, with listing + sizes before and after. |
| B11 | **Truth overlay updates** | `truth_overlay add` from adjudication evidence; symmetric-rescore check. |

**Sol capability needed for B8/B10:** the Sol sandbox can't write the shared `.git` of these worktrees (`~/Projects/greek-ocr-toolkit/.git`).
A launcher variant adds that path as a writable root for git-operation briefs only. The lead creates that launcher variant once, as a
copy, without editing the shared launcher.

## C. In flight now, all through Sol

- **R2RB:** readback of job 3681404 + digest.
- **CU4:** `greekocr.adjudicate`.
- **MERGE** (owner-approved): fresh rehearsal + real merge into opus/spellcheck per the decision sheet. Briefed next, with the
  git-capable launcher.
- **Deletions (owner-approved):**
  - §6 small items, through Sol;
  - `v2_masked/l1e_sample_r2` (no citation found);
  - `l1e_sample`, `l1e_sample_r3` and `l1e_sample_vouli` ARE cited (sol-l1emask run/README/tests; L1M evidence receipts), so they are KEPT
    unless the owner rules otherwise.
- **Reader batches T2/T4:** Opus readers; checks and resolution through Sol (B6).
