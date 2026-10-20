# KR1: kosmopolis poly1850 HANDOVER packs

Prepared offline; network OFF. KR1 readers have run: c1 is clean and stands; c2 is VOID. KR1b prepares c2b as its replacement; c2b has not been launched. Scoring is deferred. This is a release-v3 candidate handoff, with no new adjudication or admission result.

| Run | Protocol status | Cards | Controls | Letters | crop_ok |
| --- | --- | ---: | ---: | ---: | ---: |
| SRK1/SRK2, `87db4392` | **pre-handover, no controls** | 100 | 0 | 96/100 | 99/100 |
| KR1, bed `kosmo2` | HANDOVER; prepared for readers | same T6g 100 | 10 reused | pending | pending |

The first run remains historical evidence. KR1 scoring happens later, in a separate brief after the readers run. Sol letters and crop_ok are the decision fields; marks remain pending Opus. Every flag or unreadable needs eye review; more than one control error flags its context.

## Cards, order and controls

Input is exactly `../cards_kosmo_poly1850/reader/cards.jsonl` and its 100 masked crop files, bound by `../cards_kosmo_poly1850_key.json`. Every crop is copied byte-for-byte in its original grayscale L mode. No crop was regenerated or re-encoded. Labels and word_scripts are unchanged. The only permitted interpreter for any future regeneration is `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`.

`random.Random("kr1:kosmo:poly1850").shuffle` over the card-id-ordered 100 establishes a new bed order; it differs from SRK1. Split that order into two disjoint groups of 50. Each group receives its five CAPS1 controls, then uses seed `kr1:kosmo:poly1850:order:c1` or `:c2` for context order. Fresh IDs are `k` plus ten SHA256 hex digits from seed, context and line ID; all 110 are unique and absent from existing public packs at build time. Images use their full content SHA256 as filename and are independent copies, with no metadata, symlinks or hardlinks.

The exact ten lead-approved CAPS1/CAPS1b controls are reused: c057, c009, c013, c026, c046, c041, c029, c072, c035, c066. Approved truth and context assignment are byte-identical in `keys/control_truth.json`; control images match CAPS1 byte-for-byte. There are seven letters=y/crop_ok=y controls and three negative controls overall. No new control selection or pixel review was needed. Controls are from bsb_poly1850; bed rows are kosmopolis. Both use primary_class=poly1850, so the private contract checks the source/stratum pair rather than class alone.

Private ID maps, control truth, draw and copy custody are in `keys/`, outside PACK_ROOT. Public contexts are at the requested PACK_ROOT under `kosmo2/c1/` and `kosmo2/c2/`. Each contains only `cards.jsonl` and `crops/`; public `MANIFEST.c1.json` and `MANIFEST.c2.json` sit beside them. No keys, reports or contact sheets were added to PACK_ROOT.

## Prompt, closure and scanner v4

`prompts/kosmo2.md` is verbatim Sol-reading `prompts/bsb.md`, SHA256 `1b27b5d2fac6491ffa5c84f3d12f762883bbaa0af01de2d91a17576760741f57`. Its bytes have no reader-clause placeholder, so launcher rendering preserves them unchanged.

Reference worktree HEAD is `ad1889bd92e9165cd73f4f7b1ac5395aee9642f7`. HANDOVER matches the requested commit byte-for-byte (SHA256 `d5b03b80977dc0f7e02ddae5dab1c3f4ef5084a3a8ccfaab9b141555c7b20062`). All reference files remain read-only. `build_receipt.json` and `runtime_bindings.json` bind inputs and reference tools by SHA256.

Closure is **clean** for both 55-card contexts, using the explicitly requested CAPS1 adapter. The grayscale allowance and disjoint 50+5 contract are retained. After literal caps1/CAPS1 -> kosmo2/KOSMO2 vocabulary changes, only the private source/stratum pair checks differ (`adapter.diff`). The reference closure changes remain just the RGB-only and reversed-duplicate-reader assumptions. `scan/closure.json` includes the in-memory reference diff, manifest hashes and no violations. Ten contamination cases test fail-closed behavior, including private fields, source IDs, nonopaque IDs, extra/key/truth files, path escape, links and damaged originals.

Scanner v4 is loaded from the source-bound Sol-reading tool with the same CAPS1 path-vocabulary routing, including pixel-exact literal replay, image provenance, tool-input literal checks, and original/addition manifest checks. Only answers.jsonl and zoom/** may be added during reading. Saved post-reader scans are in `scan/kosmo2/`: c1 is clean; c2 is VOID as documented below.

## Launch lines

The original c1/c2 lines below are historical. c1 is clean and stands; c2 is VOID. Use the KR1b c2b launch line below for the replacement. Each exact line performs closure preflight and uses the existing `sol_packs/launchers/run_bed.sh`; its dispatch now routes only bed kosmo2 to the private driver, preserving existing caps1/caps3 routing. Public run_read.sh and limit_probe.sh are unchanged. `public_launcher.diff` records the dispatch; `launchers.diff` records reference-to-local path substitutions. Reader and probe outputs stay under this private kosmo2 directory (`answers/kosmo2/`, `scan/kosmo2/`, launcher logs and usage_ledger.json).

```bash
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/kosmo2/tools/scan_packs.py /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo2/c1 && bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers/run_bed.sh kosmo2 c1
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/kosmo2/tools/scan_packs.py /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo2/c2 && bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers/run_bed.sh kosmo2 c2
```

Reader settings: gpt-6.1-sol, medium, network OFF, web/apps/plugins/multi-agent disabled, project docs disabled, workspace-write cwd in assigned context, approval never. The existing driver probes before and after, refuses to start at >=78%, and retains mandatory v4 scanning, mapping and ledger flow. Inspect the 10080-minute weekly bucket; stop at >=80%; the owner's dashboard wins. Credits must never be spent. A DONE string alone does not establish successful leak/control checks. Mapping is the standard HANDOVER output step; KR1 aggregate scoring remains deferred.

## Mechanical verification

**12 tests passed**, zero failures/errors/skips: exact T6g card set; byte-identical crops and labels/scripts; approved truth; five controls per disjoint context; deterministic seed; fresh order/IDs; closure; contamination rejection; copy/hash/metadata custody; verbatim prompt and launch settings/syntax; source-bound v4 routing; adapter policy diff. Evidence: `tests.log`, `tests.xml`, `scan/closure.json`, `pack_inventory/`.

Re-run qualification offline:

```bash
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python -B docs/records/harvest/recut_v1/w1_masked/kosmo2/test_kosmo2.py
```

`build.py` refuses to overwrite an existing bed. `COMMIT_FILES.txt` and `commit-inputs.json` list and hash only this handoff's text files, excluding PNGs and unrelated existing work. No staging or commit was attempted.

KR1: done | cards: 100 (same as T6g) | controls: 10 reused | closure: clean | launch lines: 2 | tests: 12 passed

## KR1b: c2 VOID and replacement c2b

c2 is **VOID**: scanner v4 reported two violations, quoted exactly as "absolute path outside reader_dir", path `/zoom/$`, at rollout records 22 and 44. c1 is clean and stands. c2b replaces c2; c2 and its saved scan, rollout and answers remain evidence and must not be scored as a valid context. `SCANNER_NOTE.md` quotes both tool inputs and explains the likely template-path false positive. The scanner is unchanged.

c2b contains exactly c2's 50 bed cards and five controls, with byte-identical crops, google_text, word_scripts and private metadata. `random.Random("kr1b:kosmo:c2b").shuffle` over c2's opaque-id-sorted cards supplies the new order. IDs are `k` plus ten SHA256 hex digits of `kr1b:kosmo:c2b:<line_id>`, checked against existing public packs. Only cards.jsonl and copied crops are in the fresh c2b reader folder. No answers or zooms were carried over.

Private assignment and custody: `keys/kosmo2_c2b.json`, `keys/c2b_crop_custody.json`; the shared `keys/kosmo2.json` gains c2b additively, preserving original c1/c2 assignments. `tools/map_answers.py` accepts c2b for the existing launcher mapping step. Launchers and scanner sources are unchanged. Public manifest: `PACK_ROOT/kosmo2/MANIFEST.c2b.json`; saved clean closure: `scan/c2b.closure.json`; build and unchanged-c2 evidence: `c2b_build_receipt.json`. The existing private contract continues to check the original disjoint c1/c2 population; KR1b separately verifies c2b equivalence and fresh IDs.

Run only when the replacement reading is authorized; preparation did not execute a reader or a limit probe. Same launcher settings and budget gates apply. Exact line also saved in `launch_lines.c2b.txt`:

```bash
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/kosmo2/tools/scan_packs.py /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo2/c2b && bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers/run_bed.sh kosmo2 c2b
```
