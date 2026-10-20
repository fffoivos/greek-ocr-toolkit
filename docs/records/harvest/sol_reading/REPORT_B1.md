# SR-B1b follow-up

Status: READY for the requested control-fix handoff. No readers launched. No git, codex or network calls were made. The original SR-B1 receipt below is historical; its pending pixel review and old option/copy descriptions are superseded by this follow-up.

The lead's ink review is now a reproducible s003 source override: slots 1–2 are ь, slots 3–5 are ъ, with provenance `lead pixel review 2026-10-17 12:41 (LEAD_REVIEW.md)`. The reviewed five-control yer population remains intact.

All 39 owner39 source option tables reproduce the fixed accent-head generator. The four controls now use that generator and the common seeded A–D permutation. Forms and heads are unchanged; choices use exact NFC equality. Pack PNGs and all bsb/yer public files retain their original hashes. Review outputs are written only under keys/control_review; PACK_ROOT has only the three beds and their reader folders/manifests.

Tests and all six scans are recorded in TEST_RESULTS_B1b.txt and PACK_SCAN_B1b.json. BUILD_RECEIPT_B1b.json binds the corrected keys, manifests and implementation and records deterministic rebuild verification.

---

# SR-B1 implementation receipt

Status: **BLOCKED**, with the remaining implementation and validation complete.

| Bed | Bed items | Controls built / required | Items per reader | Folders |
|---|---:|---:|---:|---:|
| bsb | 100 | 10 / 10 | 110 | 2 |
| yer | 59 | 5 / 6 | 64 | 2 |
| owner39 | 39 | 4 / 4 | 43 | 2 |

All six folders pass the closure, public-schema, opaque-ID, PNG decode/metadata, independent-copy and reverse-order scans. Their manifests are beside the reader folders and are bound into BUILD_RECEIPT_B1.json. Pack scan output is in PACK_SCAN_B1.json. The contact sheets are generated at keys/control_review/ and copied outside the repository to PACK_ROOT/control_review/. PNGs are ignored and must not be committed. Lead pixel review is pending.

The yer shortage is source-bound: the 100 uniform C1 cards plus 40 supplement cards contain only two eligible distinct soft-sign lines outside the 59-item bed: c010 and s003. Five other qualifying lines are already in the bed. The full candidate inventory, including bed membership and source line IDs, is in the private build receipt. The three hard-sign controls all have pre-1918 publication years in source page metadata. Four control crops have exactly aligned token boxes; the supplement soft-sign line fails token-text alignment and is shown without an estimated box. The masking rule reproduces every one of the 59 existing masked items exactly. No experiment reader or new truth adjudication was run. During contact-sheet layout inspection, the s003 crop appeared to contain terminal hard signs despite the Google soft-sign label. Treat that candidate as suspect until the lead checks it; the requested expected call has not been silently changed.

The owner39 controls come from records explicitly marked lead_verified=true in T2's private controls_proposed.json. These later per-record pixel notes contradict the stale public summary and initial deck receipt; the build preserves those source files and records which evidence it used. The four selected controls include a marked anchor and literal answers. E0 rendering is reproduced and required to be pixel-identical to the saved R2 zoom. The E0 README and answer schema are byte-identical copies.

The cached Opus reference has been copied with a SHA256 manifest: all 20 bsb/yer arm-reader output files, the two usage/agent TSVs, and all four discovered owner39 answers files. Nothing was moved or edited in source worktrees.

The rollout scanner flags the actual probe canary read outside reader_dir, exits 2, and reports four image views, four distinct images, two shell commands and final usage. The probe's absent manifest is explicitly skipped. The synthetic planted-leak fixture is also rejected. Tests cover answer completeness/order, yer coverage, owner heads and option remapping, control gating, integrity mutations/additions, hardlinks, call formats, and measured ledger parsing/duplicates. Synthetic answers and mapped output are labelled and isolated under validation/. No experiment answers or usage ledger entries were created.

Git operations failed under the session's filesystem policy:

- Before/current HEAD: 50ef367bd886b983da3e03defa42326649622714.
- Required fast-forward target sol/collect-v3: 55a302d463fcb0f22bcc163211070f4679d230d5.
- `git merge --ff-only sol/collect-v3`: could not create ORIG_HEAD.lock, Operation not permitted.
- `git add -- docs/records/harvest/sol_reading`: could not create index.lock, Operation not permitted.

No commit exists and no push was attempted. The lead's PLAN.md, GUIDE_NOTES.md, prompts/ and briefs/ remain present alongside the implementation. No readers or codex commands were launched. README_B1.md documents commands, assumptions and scanner limits. TEST_RESULTS_B1.txt records the unittest result.
