"""Render SF5's saved-evidence report; no inference or network."""
from collections import Counter
import json
from pathlib import Path
import re

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden.r1_common import rows

DOC=Path('docs/records/labelfix/spellcheck')
EV=DOC/'SF5_evidence'


def table(headers,records):
    return ['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']+[
        '| '+' | '.join(str(x).replace('|','&#124;').replace('\n',' ') for x in r)+' |' for r in records]


def main():
    h=json.loads((EV/'heldout/metrics.json').read_text())
    dev=json.loads((EV/'m2_dev/metrics.json').read_text())
    w=list(rows(EV/'witness_results.jsonl.gz'))
    inp=list(rows(EV/'witness_inputs.jsonl.gz'))
    log=(EV/'tests_after.log').read_text()
    passed=int(re.findall(r'(\d+) passed',log)[-1])
    beforelog=(EV/'witness_tests_before.log').read_text()
    failed=int(re.findall(r'(\d+) failed',beforelog)[-1])
    kept=sum(r['consensus_kept'] for r in w);n=sum(r['consensus'] for r in w)
    assert kept==n and not any(r['consensus_deleted'] for r in w)
    assert not any(r['combining_marks_changed'] for r in w)
    seed=[r for r in w if r['kind']=='seeded_elision']
    ab0=h['elision']['before']['ENSEMBLE_AB']['effective_release']
    ab1=h['elision']['after']['ENSEMBLE_AB']['effective_release']
    L=['# SF5 — elision release rules', '',
       f'Policy **`{gate.POLICY}`**. Saved-evidence dry run, 17 October 2026. **{kept}/{n} consensus elision atoms retained**, **2/2 doubled breathings repaired**, and both known reader errors remain wrong. The 666 mark outcomes are identical to frozen SF4 in all four modes. Effective AB labels retain **'+str(ab1['kept'])+'/213** adjudicated printed apostrophes, versus **'+str(ab0['kept'])+'/213** before SF5.', '',
       f'**All-green acceptance remains unmet:** {passed} labelfix tests pass; the unchanged HTTP capture test has one environment setup error because the sandbox rejects its loopback `socket.bind` with `PermissionError: [Errno 1] Operation not permitted`. The baseline has the identical error (627 passes). No test was skipped, deselected, weakened or changed to hide it. M2 DEV elision accuracy is **UNKNOWN**, because this pool has no certified punctuation truth; its row and source census are reported explicitly.', '',
       'Launch HEAD: `f4a9e48cc25601dbb002112032fc3ef5925ffc92`, branch `opus/spellcheck`. All three changed production files at launch match `c6064650` exactly. No network, detector/R1/CTC inference, training, publication, other-worktree writes or `.git` writes. Policy digest: `'+gate.policy_binding()['sha256']+'`.', '',
       '## Exact rule changes', '',
       '1. `text.word_final_elision` recognizes the five declared aliases after a letter cluster, including its combining marks. `release_gate.release_text` preserves a word-final elision at the same letter boundary when Google and the recogniser both have it, even when the detector supplies no apostrophe. Full letter sequences must agree; a base mismatch retains the existing release HOLD. Single-source presence behavior is retained and recorded in `elision_census`.',
       '2. `text.spacing_breathing` classifies spacing U+1FBF/U+1FBD before a capital, or word-initial before a vowel, as a breathing. The composer consumes it when attaching a combining breathing. At the Google release boundary, a duplicate recogniser prefix apostrophe is consumed in that same label edit; the punctuation guard permits exactly that substitution at the same letter. An unattached spacing mark keeps Google’s codepoint. Uncertain/held lines keep the original Google label.',
       '3. Existing Google word-final elisions keep their original codepoint, including beside real mark edits. A pure alias difference is `status=unchanged`, `changes=[]`, `label=original`, and `alias_only=true`. The release manifest has a separate `alias_only` count, also broken down by wave/source; it is a subset of `unchanged`, never another status or a correction. The codec v2.1 U+2019 fold is left to training.', '',
       'Production changes are limited to `greekocr/labelfix/text.py`, `greekocr/labelfix/release_gate.py`, and `scripts/labelfix/clariden/l1_common.py`. Observation, agreement, coverage, K1, mark naming and supported-character rules are unchanged. In particular, no rule for **ἐν→ἑν** or **διορίσῃ→διορίση** was added.', '',
       '## The 56 saved-runtime witnesses', '',
       'All 56 frozen SF4 labels/statuses were reproduced before applying SF5. The six L1M witnesses use the **masked** saved detector, the runtime that produced the audited wrong corrections. The seeded 50 use the supplied complete AB overlay records and their per-edit evidence. The raw gate inputs are reconstructed from saved detector fields, A predictions/coverage and B predictions/coverage; the six retain the full raw detector. No diagnostic E input was retained in these overlays, and none was invented. A new evidence envelope binds the reconstructed inputs; the original full-envelope evidence digest is not claimed as reproduced. Exact SF4 label parity and identical accepted slot records are checked for every line.', '',
       f'The seeded 50 contain **{sum(bool(r["consensus"]) for r in seed)} lines / {sum(r["consensus"] for r in seed)} atoms** with Google/recogniser consensus. All survive. **44** lines become unchanged. **Four** keep their existing combining-mark edits and regain their elision; **one** keeps an existing opening-quote change and regains its elision; **one** remains corrected solely because Google has a mark the recogniser lacks (`a300f5e1c3f6a38d97201791-p000442-l0085`). That single-source deletion is intentionally unchanged. Across all 56 lines, the SF4→SF5 combining-mark outputs and every slot decision/reason/physical record are identical; the two capital witnesses lose only the duplicate spacing/prefix sign. Alias spelling beside retained real edits is restored to Google’s spelling.', '',
       'Inputs and frozen outputs: [witness_inputs.jsonl.gz](SF5_evidence/witness_inputs.jsonl.gz), [source bindings and 56/56 parity](SF5_evidence/witness_inputs_receipt.json). Full labels, recogniser text, edit evidence and source census: [witness_results.jsonl.gz](SF5_evidence/witness_results.jsonl.gz). Every row below is a repository test in `tests/labelfix/test_sf5.py`.', '']
    def note(r):
        if r['kind'].startswith('known_reader_'):return 'KNOWN WRONG; unchanged'
        if r['kind']=='capital_breathing':return 'one breathing; duplicate removed'
        if not r['consensus']:return 'Google-only deletion retained'
        return f"{r['consensus_kept']}/{r['consensus']} elisions kept; {r['after_status']}"
    L+=table(['Line ID','Google original','SF4 label','SF5 label','Result'],[
        [r['id'],r['google'],r['before'],r['after'],note(r)] for r in w])
    L+=['','Other Google→released changes on the six still-corrected seeded lines are retained from SF4, without new print-precision claims:', '']
    L+=table(['Line ID','Other retained edit'],[
        ['a300f5e1c3f6a38d97201791-p000442-l0085','Google-only word-final apostrophe deleted; no combining-mark edit'],
        ['453f156dc6352286456a08cb-p000100-l0002',"ι→ὶ; initial ᾿→ASCII apostrophe before στὸν"],
        ['143e78b5de2e6e784534ee0d-p000061-l0032','ί→ῖ'],
        ['b518f9f9b73fe9a3257fe2f0-p000041-l0022',"initial ᾿→“' before ποὺ; existing opening-quote/prefix change, no combining-mark edit"],
        ['137e9af6a0045d5746e26efa-p000008-l0008','ἂ→ἃ'],
        ['8961f6bdd6daf004b4a84dfa-p000025-l0051','ἓ→ἕ'],
    ])
    L+=['','## Held-out 666 — SF4 → SF5','',
        'The existing frozen instrument scores **80 Google combining-mark errors**, **10,046 known** and **300 unknown-truth** mapped/scored slots per mode. Unknown truth is excluded from outcomes. Mark outcomes are slot based; line release additionally requires every slot and both Google edit guards to clear. The mark rows below are reproduced exactly with the same scorer. **81,700 slot/mode records are identical**, including parts, status and reasons. Every wrong/new identity and event is unchanged; there are no mark-slot changes to explain.', '',
        'This remains a **saved-decision text replay**, because complete 666-line extraction coverage is unavailable locally. It retains the actual SF4 decisions and vetoes and rerenders only the two text rules. Missing coverage is never synthesized. The 56 witnesses and the 273-card DEV pool are actual saved-runtime recompositions.', '']
    records=[]
    for m in gate.MODES:
        a=h['mark_rows']['before'][m];b=h['mark_rows']['after'][m]
        records.append([m,'combining marks',*[f'{a[k]} → {b[k]}' for k in ('corrected','wrong','missed','HOLD','new','lines_held')]])
        a=h['elision']['before'][m]['effective_release'];b=h['elision']['after'][m]['effective_release']
        records.append([m,'**elision: kept / deleted / added**',f"**{a['kept']} / {a['deleted']} / {a['added']} → {b['kept']} / {b['deleted']} / {b['added']}**",'—','—','—','—','—'])
    L+=table(['Mode','Row','Corrected /80 or elision K/D/A','Wrong','Missed','HOLD errors','New','Lines held /666'],records)
    t=h['truth']
    L+=['',f'**Elision truth and coverage:** {t["positive_sites"]} print-positive sites and {t["known_negative_sites"]} explicitly absent sites on **{t["lines"]}/666 lines**; **0 complete lines** certified. At **212/213 positive sites**, the human Wikisource emission is pixel-adjudicated by R0 and supplies the text; the remaining positive uses the literal R0 adjudication. Across all 218 scored scopes, sources are {t["sources"]["human_Wikisource_pixel_adjudicated_by_R0"]} pixel-supported human sites and {t["sources"]["R0_adjudication"]} R0 fallback sites. Ten adjudicated quote sites are excluded from elision scoring, including two printed closing single quotes; one unresolved site is excluded. The five declared aliases are one presence atom. R0 also adjudicates two **word-initial** elisions (`\'ς`, `\'φελα`): their emitted signs count as kept, while the SF5 consensus-preservation rule remains restricted to word-final elisions.', '',
        'The elision rows above score the **effective label**: original Google when held, the proposed label when released. “Deleted” means absent relative to adjudicated print, including an original omission. The residual **1** is `51fe7386-p000024-l0017`, where Google has `ἐς` at the printed `\'ς`; the line remains held and unchanged. The residual **1 added** sign is already in Google at the R0 “absent” site `384c3f89-p000179-l0019`; SF5 does not introduce it. Added counts apply only to the five certified absent scopes, not all unadjudicated positions.', '',
        'For visibility into held proposals, the same printed sites are also scored before line-level fallback:', '']
    L+=table(['Mode','Candidate elision kept','Candidate elision deleted','Candidate elision added'],[
        [m,*[f"{h['elision']['before'][m]['candidate'][k]} → {h['elision']['after'][m]['candidate'][k]}" for k in ('kept','deleted','added')]] for m in gate.MODES])
    L+=['','Candidate residual omissions are the single-source `ἀλλ\'` at `384c3f89-p000050-l0037` and a line with recogniser base errors (`384c3f89-p000091-l0014`). Both lines are held; their Google marks survive in the effective labels. These counts are proposal diagnostics, not released deletions.', '',
        'The release source census below concerns the **608 lines with identical letter sequences**, not print truth. All **201 word-final consensus atoms** are retained after SF5. The 58 base-mismatched lines retain the existing HOLD; their 10 Google/recogniser marks are outside the aligned census. The sole aligned Google-only mark keeps the previous proposal behavior; it occurs on a held line. There are no aligned recogniser-only marks in this cohort.', '']
    L+=table(['Mode','Both kept / deleted','Google-only kept / deleted','Recogniser-only kept / deleted'],[
        [m,*[f"{h['elision_census']['before'][m][p+'_kept']} / {h['elision_census']['before'][m][p+'_deleted']} → {h['elision_census']['after'][m][p+'_kept']} / {h['elision_census']['after'][m][p+'_deleted']}" for p in ('both','google_only','recogniser_only')]] for m in gate.MODES])
    L+=['','Evidence: [metrics and truth coverage](SF5_evidence/heldout/metrics.json), [per-site print outcomes](SF5_evidence/heldout/elision_events.jsonl), [all 81,700 identical slot/mode records](SF5_evidence/heldout/per_slot_proof.jsonl.gz), [before/after release labels and source census](SF5_evidence/heldout/release_labels.jsonl.gz), [source-bound receipt](SF5_evidence/heldout/receipt.json).', '',
        '## M2 DEV only — SF4 → SF5','',
        'The frozen **273-card DEV allowlist** is filtered before cached runtime records are decoded. No locked stratum (ii) runtime or truth row is decoded or composed. There are **43 enumerated Google combining-mark error pairs** and **212 marks-correct reference cards**; the historical blind verdicts remain reference evidence. All paired mark outcomes, control edits, slot records and HOLDs are identical in both phases. AB/AE have no saved B/E predictions here, so their missing-evidence HOLDs remain intact.', '']
    records=[]
    for m in gate.MODES:
        a=dev['before']['marks']['modes'][m];b=dev['after']['marks']['modes'][m]
        records.append([m,'combining marks',*[f"{a['errors'].get(k,0)} → {b['errors'].get(k,0)}" for k in ('corrected','missed','HOLD')],f"{a['accepted_changed_slots']} → {b['accepted_changed_slots']}",f"{a['lines_with_HOLD']} → {b['lines_with_HOLD']}"])
        records.append([m,'**elision: kept / deleted / added**','**UNKNOWN → UNKNOWN (0 truth sites)**','—','—','—','—'])
    L+=table(['Mode','Row','Corrected /43 or elision K/D/A','Missed','HOLD errors','Accepted changed control slots','Lines held /273'],records)
    L+=['','**DEV elision truth coverage is 0/273 lines and 0 positive/negative sites.** All 273 human fields are null, and no DEV line has an R0 punctuation-site adjudication. The locked (ii) truth is excluded. No zero-error or elision-accuracy claim is made. The source-agreement census can still be measured from saved text:', '']
    L+=table(['Mode','Both kept / deleted','Google-only kept / deleted','Recogniser-only kept / deleted'],[
        [m,*[f"{dev['before']['elision_census'][m][p+'_kept']} / {dev['before']['elision_census'][m][p+'_deleted']} → {dev['after']['elision_census'][m][p+'_kept']} / {dev['after']['elision_census'][m][p+'_deleted']}" for p in ('both','google_only','recogniser_only')]] for m in gate.MODES])
    d=dev['after']['elision_census']['PRESENCE']
    L+=['',f'This is an aligned source census on {d["aligned_lines"]}/273 lines, with {d["unaligned_lines"]} base-mismatched lines excluded from site matching. It contains four consensus sites and one Google-only site; the other Google sign is on a base-mismatched line. The held-line effective labels remain Google. [DEV metrics](SF5_evidence/m2_dev/metrics.json), [identical per-slot proof](SF5_evidence/m2_dev/per_slot_proof.jsonl.gz), [DEV allowlist, truth-coverage and input receipt](SF5_evidence/m2_dev/receipt.json).', '',
        '## Alias accounting','',
        'The historical production audit identifies **431 AB**, **216 PRESENCE** and **200 FULL** alias-only corrections. Those are frozen SF4 audit counts, not a new full-production recomposition. SF5 preserves Google’s alias bytes and counts such accepted lines under `unchanged`, with a separate overlapping `alias_only` counter. The full training release was not regenerated. The 431 AB IDs remain in `SF5_witness/alias_only_ids_sf4.txt` for review.', '',
        'The local 666 replay measures the resulting whole-line accounting:', '']
    L+=table(['Mode','Corrected lines','Unchanged lines','Held lines','Alias-only subset of unchanged (SF5)'],[
        [m,*[f"{h['release_counts']['before'][m].get(k,0)} → {h['release_counts']['after'][m].get(k,0)}" for k in ('corrected','unchanged','hold')],h['release_counts']['after'][m]['alias_only']] for m in gate.MODES])
    L+=['','M2 DEV has 0 alias-only accepted lines in each mode in both phases. The 56 elision-deletion witnesses have 0 pure alias-only lines. Synthetic release tests read back the actual manifests, source/wave buckets, overlays and paired original-label controls; status totals remain disjoint and alias counts never inflate them.', '',
        '## Verification and reproduction','',
        f'- New SF5 suite: **220 tests**; **{failed} fail on the frozen c6064650 sources** and all pass on SF5. Positive controls, the single-source residual and the two known reader errors intentionally pass on the baseline. The two text rules and alias accounting each have failing-before/passing-after witnesses. [Baseline witness log](SF5_evidence/witness_tests_before.log).',
        f'- Full labelfix suite: **{passed} passed, 1 environment setup error**, no assertion failures. [Full result](SF5_evidence/tests_after.log), [unchanged baseline socket error](SF5_evidence/tests_before.log). Existing tests were not edited.',
        '- `git diff --check` passes. [Verification receipt](SF5_evidence/verification.json) checks all source/evidence hashes, frozen source identity, the production change scope and unchanged Git metadata. The report makes no full-production precision claim.', '',
        'Use the requested Python with bytecode and pytest cache disabled:', '',
        '```bash',
        'export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 GIT_OPTIONAL_LOCKS=0',
        'PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python',
        '$PY scripts/labelfix/sf5_measure.py prepare',
        '$PY scripts/labelfix/sf5_measure.py witnesses',
        '$PY scripts/labelfix/sf5_measure.py heldout',
        '$PY scripts/labelfix/sf5_measure.py m2',
        'SF5_TEST_BASELINE=1 $PY -m pytest tests/labelfix/test_sf5.py -q -p no:cacheprovider',
        '$PY -m pytest tests/labelfix -q -p no:cacheprovider',
        '$PY scripts/labelfix/sf5_report.py',
        '$PY scripts/labelfix/sf5_verify.py',
        '```','',
        f'SF5 RESULT: policy sf5-release-v1; witnesses elision-kept {kept}/{n}, double-breathing fixed 2/2, known reader errors unchanged 2/2; held-out AB corrected 45, wrong 2, new 6, elision deleted {ab0["deleted"]}→{ab1["deleted"]}; alias-only lines no longer counted; tests {passed} passed']
    (DOC/'SF5_REPORT.md').write_text('\n'.join(L)+'\n')
    print('wrote',DOC/'SF5_REPORT.md')


if __name__=='__main__':main()
