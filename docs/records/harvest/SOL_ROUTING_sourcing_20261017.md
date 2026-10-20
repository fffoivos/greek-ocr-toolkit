# Sourcing track: Sol routing (owner directive, 17 Oct 2026)

**Directive, verbatim:** "make sure that all coding/cli/scripting workflows are sent to sol; also … what other tasks that do not require finesse but execution precision can be sent to sol".

**Effective from ~11:45 on 17 Oct.** The sourcing lead (Opus) writes no code and runs no scripted pipelines. Every builder, verification, hash check, rsync, inventory, deletion and test run is a Sol brief, with tests and a receipt (effort medium for mechanical work). The lead keeps: planning, briefs, reviews, card reading and adjudication (Opus readers), rulings and reports.

## A. Compliance audit of 17 Oct: what I ran by hand

Everything below was done by hand in this session, before or around the directive. The disposition is one of:
- **M**: migrate into a Sol-maintained tool with tests (batch brief S-TOOLS below);
- **O**: one-off, with the reason;
- **R**: already replaced by a Sol-built tool.

| # | Operation (where) | Disposition |
|---|---|---|
| 1 | Collector code fixes I wrote and tested myself in sol/collect-v3: finalize textless (24060664), pre-read rejections (2f8e2032), owner_mac W2 + go cap (e6d6d266), gate extension + go entries (914def6b), DailyLimit deferral (43afde6d), worker PID (2c9dbd3f) | **O.** These were live-run fixes, each with tests. From now on every collector fix is a Sol brief, even when a live run is waiting; I pause the run at a page boundary instead of patching by hand. |
| 2 | Collector stop / kill / relaunch, run.lock holder diagnosis, MDZ window count (shell) | **M** → `collector-control` (launch, stop at a page boundary, resume, status, lock-holder report; a receipt per action) |
| 3 | W1 source × class census from features.jsonl, Latin label samples, per-book Greek yield ranking (scratchpad w1_tab.py and inline) | **M** → `census` (source × class × stratum tables, usable/held/excluded; per-item yield ranking); the Latin sample is **O** (a single diagnostic) |
| 4 | W2 IA floor filter of W2_manifest.jsonl (prefloor copy + receipt) | **M** → `manifest-filter` (rule file in, prefloor kept, receipt with hashes) |
| 5 | c1_gate.json write, W2_owner_go.json write and its second entry, gate snapshot, collector_pids.json | **M** → `gate-writer` / `go-writer` (validated against runner.gate_sources / go_entries; snapshot + receipt) |
| 6 | Release exclusion lists: unchecked_strata.json statuses + marks_bias, separator_ambiguous ids, rotated_crop ids (both rules) | **M** → `exclusions` (each class from a declared rule, counts per stratum, sha update of release_exclusions.json, tests) |
| 7 | C1 card split into reader halves, symlinked crops (the KEY-IN-REACH layout), aggregator c1_agg.py (Wilson CIs, lunate strict/codec, superscript/dash/separator tags, mark errors, neighbour ink) | **M** → `cards` (draw, isolated reader folders with **copied** crops and keys out of reach, aggregate with all tags); c1_agg.py retires |
| 8 | Yer adjudication packs (masking, the prior pack) and the table join | **R** (E-build packs/scorer generalise it); the yer record itself is kept as evidence |
| 9 | T6b: commit with large records kept local (.gitignore + LARGE_LOCAL_FILES.json + copy to data dir), masked-card split, probe-supplement draw, the T6b results / report writers | **M** → `cards` (draws and supplements) and `commit-large` (a guarded commit with a size policy and data-dir copy) |
| 10 | Wave-1d admission builder (build_w1_masked_1d.py; hash-validated) | **M** → `admissions` (rule-declared strata, exclusions, hash validation, summary) |
| 11 | C1 report and T6b report generation (Markdown from results JSON) | **M** → a report writer in `cards` (tables from results; the prose stays mine) |
| 12 | Efficiency packs copied to the scratchpad for readers; usage log of reader tokens | **M** → `cards` (reader-folder export) and `usage-log` (from agent results; never estimated) |
| 13 | Clariden read-only probe (ssh ls/find/wc/du) | **O** (one discovery, now inside the T6f brief) |
| 16 | W2 Gazette read: GATE2b gate install (two verbatim lines) and the collector launch, run by the lead at 17:59, because the Sol sandbox cannot write the run root or detach a networked collector; the same standing authorisation covers the BSB resume on 18 Oct | **O** (coordinator-authorised; receipt docs/records/harvest/collect_v3/w2_gate/LAUNCH_RECEIPT_GAZETTE_20261017.md) |
| 15 | T6h Mac v2 masking: the two README commands (50-crop mock gate, then the detached full run) run by the lead at 12:40 and 12:41, because the Sol sandbox cannot setsid or renice | **O** (coordinator-authorised one-off; receipt sol/recut-v1 docs/records/harvest/recut_v1/v2_full/receipts/LAUNCH_RECEIPT_20261017.md) |
| 14 | Disk and process checks, log tails, git status/log, commits of Sol outputs | **O / allowed:** status reading, plus committing Sol's guarded file lists (Sol's sandbox cannot write .git). No scripted transforms. |

**Batch brief S-TOOLS** (one Sol run, medium): implement the M items as `collect_v3/tools/` (a CLI separate from the collector run identity) or `docs/records/harvest/sourcing_tools/`, whichever keeps the live W2 identity untouched. Unit tests reproduce today's outputs byte-for-byte from today's inputs: census tables, unchecked_strata.json, rotated and separator id lists, w1_masked_1d.jsonl, the C1 aggregates. Scheduled after W2 closes, because the W2 checkout imports collect_v3/.

## B. Recurring execution-precision tasks: always Sol from now on

Each line gives the task, then the brief template's mandatory parts: inputs, outputs, tests, receipt.

1. **Collector launch / stop / resume** (W2 BSB resume tomorrow 02:30–11:00; the Gazette read):
   - inputs: run root, sources, go entry;
   - outputs: launch receipt with manifest/gate/go sha, PIDs (supervisor and worker), start time from `date`;
   - stop: page-boundary SIGTERM to the supervisor, with a receipt.
2. **Collector completion report** (W2 end, Gazette end):
   - pages, USD against the cap per source, usable rows per admitted class, failures and exclusions by reason, deferred sources;
   - from state.json, ledger and features. Never run materialize by hand.
3. **Gate and go writers:** gate entries only from recorded rulings; validated with the runner functions; snapshot.
4. **Admission and exclusion builders:** rule files in, id lists plus counts plus sha updates out; tests reproduce prior outputs.
5. **Card draws and reader packs:**
   - seeded uniform draws, supplements, isolated folders with copied crops, keys out of reach;
   - the reader manifest;
   - the aggregator with all tags.
6. **Census and ranking tables:** source × class × stratum; per-item yields; W2/W3 page plans with USD.
7. **Replay deletions** (after W2 closes, owner-approved list only):
   - `du -sh` before and after per path; delete only the listed paths;
   - refuse any code, doc or receipt path;
   - record in the clean-up plan.
8. **Remote packages** (Clariden): rsync, DEPLOY_SHA256, mock, `sbatch --test-only`; never a real submit (the coordinator submits).
9. **Large-artefact commits:** a guarded commit list; large files kept local with hashes plus a data-dir copy.
10. **Usage logging** for experiments: from agent results only.

## What stays with me
- Plans and briefs, and reviewing Sol's outputs against the brief.
- Reading and adjudicating cards with blind Opus readers.
- Rulings requests to the coordinator; reports with numbers.
- Status reading (logs, state files) to decide the next brief.
