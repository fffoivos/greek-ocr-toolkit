"""Append SF6c from verified saved replay receipts; preserve SF6/SF6b verbatim."""
from collections import Counter,defaultdict
import json
import re

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden.r1_common import rows
from scripts.labelfix.sf6c_measure import EV,FROZEN
from scripts.labelfix.sf6b_measure import table,arrow,vector


def read(p):return json.loads(p.read_text())


def report():
    c=read(EV/'comparison.json');audit=read(EV/'runtime_audit.json')
    assert c['policy_after']==gate.policy_binding()
    log=(EV/'tests_after.log').read_text();assert 'FAILED ' not in log
    passed=int(re.findall(r'(\d+) passed',log)[-1]);errors=int(re.findall(r'(\d+) error',log)[-1]) if re.findall(r'(\d+) error',log) else 0
    assert '75 passed' in (EV/'reviewer_after.log').read_text()
    assert '12 failed, 63 passed' in (EV/'reviewer_before.log').read_text()
    L=['','## SF6c — evidence certification (B01/B02)','',
       'Before = **SF6b** (`8c5ad361` production sources); after = **SF6c**. Policy id remains `sf6-release-v1`. The SF6 Boolean rule, character inventory, SF5 composer, slot decisions and same-kind capital MOVE exception are unchanged. This section supersedes the original SF6 claim that the old loader never filled a missing score.', '',
       f'Policy sha **`{c["policy_after"]["sha256"]}`**, previously `{c["policy_before"]["sha256"]}`. The binding now covers the score loader, frame-score provenance and all live M2/Clariden runtime builders, as well as the original gate/consumer sources. [Comparison and source binding](SF6c_evidence/comparison.json).', '',
       '### Diffs and confidence floor','',
       '- **B01:** `Alignment.confidence` defaults to `None`; omitted/null scores remain missing through load, save, transfer, M2 and Clariden. Legacy runtime copies explicitly retain `scored: false` with missing/unprovenanced provenance. A genuine **0.0 is never positive**. Recogniser absence requires an explicit finite line score **> 0.5**, plus explicit scored observation of the complete saved target window, also **> 0.5**. A finite line average alone cannot authorize absence.',
       '- The `ctc-window-score-v1` envelope binds the alignment digest, transcript digest, NFD start/base, image width, target window, valid frame range and score method. Regional confidence is the **minimum** max posterior over **every overlapping frame**, including blanks. New alignments retain actual frame probabilities with their original transcript digest; legacy alignments without them produce **no regional scores**. Object transfers preserve a transferred flag; record transfers are detected by the frame/transcript ownership digest. Transferred spans cannot supply regional observation. The historical shared transfer helper and its old scoring receipt remain unchanged. No saved frame score is invented.',
       '- M2 inference and cached-detector replay write those fields. `l1_infer`, `l1e_run` and the held-out L1E builder preserve explicit score/provenance or explicitly mark it unavailable. The historical L1 detector builder existed only in the immutable `artifacts/labelfix_l1e/reference/` snapshot: `scripts/labelfix/clariden/l1_detect.py` is the same builder with only confidence, regional evidence and native width added. Historical references/deploy snapshots remain unchanged. R1 extraction records `line_confidence_missing`, rather than converting missing to zero.',
       '- **B02:** MOVE, ordinary reader A/B/E absence, and recogniser locator/window validation all call `_source_in_window`. Native source spans must be finite, inside the image, and contained in the saved target-letter window. A scored recogniser region must cover the **whole** target window. Padded reader inputs need not have the detector window dimensions. Historical R1 coverage retains the extractor’s explicit native-span check (`window_contract`, known/scored state, recorded empty uncertainty); `out_of_image_span` disqualifies it. Generic finite spans without native bounds provenance remain unavailable. This preserves both saved capital MOVEs without inventing image widths.',
       '- Recognition score, regional provenance and image width are included in the content-bound runtime envelope. No recogniser/detector/reader decisions, alias handling, independent-signal combinations or whole-line HOLD dispatch change.', '',
       '**Floor justification.** `0.5` is the existing saved R1 extraction admissibility cutoff, not a threshold fitted to release outcomes. A strict majority posterior on every observed frame is a conservative lower bound for a positive scored observation; zero and values at the floor HOLD. The saved distribution below places all 666 held-out and all 273 DEV line scores above it, while the broader saved C1 cache has 8/91,469 at or below it. Thus the floor does not manufacture a yield change in these cohorts. These are **line averages**, not regional minimum scores or calibrated absence probabilities: the saved evidence cannot calibrate regional accuracy. Missing regional observations HOLD regardless of a high line mean. Provenance and full-window observation, not the floor alone, repair B01.', '']
    dist=[('held-out matching S0 alignments',audit['heldout_alignment_distribution']),
          ('M2 DEV runtime',next(r for r in audit['runtime_sources'] if r['path']=='.cache/labelfix/m2/runtime.jsonl')),
          ('C1 saved alignment cache',next(r for r in audit['alignment_sources'] if 'C1_alignments' in r['path']))]
    L+=table(['Saved score population','n','min','p01','median','max','at/below 0.5'],[[n,r['records'],*[f'{r["quantiles"][k]:.6f}' for k in ('min','p01','median','max')],r['states'].get('below_or_at_floor',0)] for n,r in dist])
    L+=['','### Runtime-source audit and newly held lines','',
        'Every loose runtime/combined/detector-shard and witness-input source on disk was enumerated and hashed; original-label overlays were compared under frozen SF6b and SF6c. DEV filtering occurs **before JSON decoding** for every M2 variant. The locked R0 alignment file was hashed only; locked stratum (ii) decoded/composed **0**. [Per-file audit, distributions, writer paths and status counts](SF6c_evidence/runtime_audit.json).','']
    L+=table(['Source','Records audited','Score representation','Regional score records','New HOLD line/mode records'],[[r['path'],r['records'],', '.join(f'{k}={v}' for k,v in r['states'].items()),r['regional_scores'],len(r['newly_hold'])] for r in audit['runtime_sources']])
    L+=['','Nine packed code/measurement/mock archives were also checked without extraction or mutation. Four runtime members (64 records each) in the two mock64 archives all omit confidence and regional scores; SF6c adds zero HOLDs. The other seven archives contain no runtime members. Their complete hashes and member results are in the same audit receipt.','']
    L+=table(['Archive','Runtime member','n','Missing scores','New HOLD line/mode records'],[[ar['path'],r['member'],r['records'],r['states'].get('missing',0),len(r['newly_hold'])] for ar in audit['archive_sources'] for r in ar['runtime_members']])
    L+=['','The 40 missing-score records per S7 runtime are already skipped/out of scope. All 168 SF6/SF6b witness runtimes omit the confidence key (56 SF5 + 48 L1A + 64 synthetic quote probes); the held-out SF6 instrument also omits it for all 666 lines. The five local Clariden mock detector/combined sources each omit it for all 64 records. No observed production score is silently reclassified as zero. The reviewer fixtures separately retain explicit missing/default-zero cases.', '',
        f'**New HOLDs:** held-out 0; M2 DEV 0; SF5/L1A/quote witnesses 0; all other audited local runtime sources {sum(len(r["newly_hold"]) for r in audit["runtime_sources"])}. The main replay changes {c["changed_checks"]} M2 line/mode check records on 11 unique lines: recogniser absence becomes unavailable because regional scoring was never saved. Every affected line was already HOLD. No mark or release outcome changes. [Exact check changes](SF6c_evidence/check_changes.jsonl), [new-HOLD list](SF6c_evidence/line_changes.jsonl).','']
    changes=defaultdict(list)
    for r in rows(EV/'check_changes.jsonl'):changes[r['id']].append(r['mode'])
    L+=table(['Already-held DEV line','Modes with recogniser signal revoked'],[[k,', '.join(v)] for k,v in changes.items()])
    L+=['','### Held-out 666 — SF6b → SF6c','']
    a=read(EV/'before/heldout/metrics.json');b=read(EV/'after/heldout/metrics.json');rr=[]
    for m in gate.MODES:
        x=a['marks']['after'][m];y=b['marks']['after'][m]
        rr.append([m,'mark',*[arrow(x[k],y[k]) for k in ('corrected','wrong','missed','HOLD','new','lines_held')]])
        rr.append([m,'elision kept/deleted/added',arrow('/'.join(str(a['elision']['after'][m][k]) for k in ('kept','deleted','added')),'/'.join(str(b['elision']['after'][m][k]) for k in ('kept','deleted','added'))),'—','—','—','—','—'])
        rr.append([m,'raw deleted mark/apostrophe/quote/keraia/other',arrow(vector(a['deletions'][m]['after']),vector(b['deletions'][m]['after'])),'—','—','—','—','—'])
    L+=table(['Mode','Row','Corrected /80, K/D/A or raw deleted','Wrong','Missed','HOLD errors','New','Instrument lines held /666'],rr)
    L+=['','This remains the **incomplete local frozen-slot instrument**, not full-runtime recomposition. It has no saved B/E extraction coverage, no recogniser score and no positive absence signals. The original 81,700 slot/mode records stay identical. The 11 AB corrected marks are an instrument result; actual AB released corrected **lines** remain 6. [Before](SF6c_evidence/before/heldout/metrics.json), [after](SF6c_evidence/after/heldout/metrics.json).','',
        '### M2 DEV 273 — SF6b → SF6c','']
    da=read(EV/'before/m2_dev/metrics.json');db=read(EV/'after/m2_dev/metrics.json');rr=[]
    for m in gate.MODES:
        x=da['marks']['after']['modes'][m];y=db['marks']['after']['modes'][m]
        rr.append([m,'mark',*[arrow(x['errors'].get(k,0),y['errors'].get(k,0)) for k in ('corrected','wrong','missed','HOLD')],arrow(x['accepted_changed_slots'],y['accepted_changed_slots']),arrow(x['lines_with_HOLD'],y['lines_with_HOLD'])])
        rr.append([m,'elision','UNKNOWN → UNKNOWN','—','—','—','—','—'])
        rr.append([m,'raw deleted mark/apostrophe/quote/keraia/other',arrow(vector(da['deletions'][m]['after']),vector(db['deletions'][m]['after'])),'—','—','—','—','—'])
    L+=table(['Mode','Row','Corrected /43 or raw deleted','Wrong','Missed','HOLD errors','Changed control slots','Instrument lines held /273'],rr)
    L+=['','B/E remain missing; no reader is copied into another arm. DEV punctuation truth remains UNKNOWN. [Before](SF6c_evidence/before/m2_dev/metrics.json), [after](SF6c_evidence/after/m2_dev/metrics.json).','',
        'Actual whole-line status counts (corrected/unchanged/HOLD):','']
    L+=table(['Cohort','Mode','SF6b → SF6c'],[[pool,m,arrow('/'.join(str(x['release_counts']['after'][m].get(k,0)) for k in ('corrected','unchanged','hold')),'/'.join(str(y['release_counts']['after'][m].get(k,0)) for k in ('corrected','unchanged','hold')))] for pool,x,y in [('held-out',a,b),('M2 DEV',da,db)] for m in gate.MODES])
    L+=['','### Witnesses — SF6b → SF6c','']
    wa=list(rows(EV/'before/witness_results.jsonl.gz'));wb=list(rows(EV/'after/witness_results.jsonl.gz'));rr=[]
    for cohort in ('sf5','l1a','quote_probe'):
        for mode in gate.MODES:
            old=[r for r in wa if r['cohort']==cohort and r['mode']==mode];new=[r for r in wb if r['cohort']==cohort and r['mode']==mode]
            if not old:continue
            def statuses(rs):return '/'.join(str(sum(r['after']['status']==k for r in rs)) for k in ('corrected','unchanged','hold'))
            rr.append([cohort,mode,len(old),arrow(statuses(old),statuses(new))])
    L+=table(['Witness cohort','Mode','n','Corrected/unchanged/HOLD: SF6b → SF6c'],rr)
    L+=['','Deletion-related HOLD lines by class (classes may overlap; unchanged across SF6b → SF6c):','']
    wma=read(EV/'before/witness_metrics.json');wmb=read(EV/'after/witness_metrics.json');rr=[]
    pools=[('held-out',a['deletions'],b['deletions']),('M2 DEV',da['deletions'],db['deletions'])]
    pools.extend((cohort,wma['cohorts'][cohort],wmb['cohorts'][cohort]) for cohort in ('sf5','l1a','quote_probe'))
    for pool,old,new in pools:
        for mode in gate.MODES:
            if pool in ('sf5','l1a') and mode!='ENSEMBLE_AB':continue
            rr.append([pool,mode,arrow(vector(old[mode]['all_held']),vector(new[mode]['all_held']))])
    L+=table(['Cohort','Mode','mark/apostrophe/quote/keraia/other HOLD lines'],rr)
    L+=['','Both saved capital witnesses still release the exact SF6b labels with one `operation=MOVE`, no absence signals. Mismatched kind, unnamed reader, extra deletion and invalid-location controls HOLD. The keraia witness remains HOLD and quote probes remain 64/64 HOLD. Raw spacing-sign removals remain 2 per SF5/L1A cohort, all MOVEs; true released deletions remain zero. Punctuation-deletion HOLD counts by class are unchanged. Census witnesses remain pending: the requested L1R2 report/census is absent on disk.', '',
        'All **16/16** saved reviewer JSON cases now HOLD: the 12 formerly unsafe releases (3 witness paths × 4 modes) plus 4 already-held missing-key controls. [Inputs retained read-only](../../reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_evidence/unsafe_release_witnesses.json), [after overlays](SF6c_evidence/unsafe_witnesses_after.json).','',
        '### Tests, scope and reproduction','',
        'The reviewer’s 75 cases are now `tests/labelfix/test_sf6_reviewer.py`: frozen SF6b reproduces **12 failed / 63 passed**; SF6c passes **75/75**. Its only harness adaptation changes the obsolete loader-default assertion from `0.0` to `None`; every release/HOLD assertion is preserved. The shared positive synthetic fixture now explicitly supplies image width and actual synthetic regional frame scores; production saved evidence is untouched. Every existing test assertion is unchanged. An additional 95 certification cases cover missing/zero/floor/invalid scores, regional provenance, all reader arms, bounds, transfers, both real runtime writers under mocked inference, and the saved unsafe JSON.', '',
        f'Full labelfix: **{passed} passed, {errors} environment setup error, 0 assertion failures**. Baseline was **1260 passed, 1 identical setup error**. The unchanged `test_capture.py::test_server_appends_each_decision_and_serves_static` cannot bind a loopback socket in this sandbox (`PermissionError: [Errno 1] Operation not permitted`). No skip, deselection, mock or test weakening is used for that test. **All-green acceptance remains unmet in this environment**. [Baseline log](SF6c_evidence/tests_before.log), [full after log](SF6c_evidence/tests_after.log), [reviewer before](SF6c_evidence/reviewer_before.log), [reviewer after](SF6c_evidence/reviewer_after.log).', '',
        'Saved evidence only; network OFF; detector/R1/CTC inference runs 0; no `.git` writes by this run; other worktrees read-only. This checkout’s HEAD, branch and index remain unchanged. Concurrent activity changed the separate `spellcheck-s8` worktree’s shared Git metadata; those differences are recorded separately and were not restored or edited. [Git custody differences](SF6c_evidence/git_metadata_changes.json). Before replay matches every saved SF6b row and metric. [Scope/custody verification](SF6c_evidence/verification.json).','',
        '```sh','export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1','PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python',
        '$PY scripts/labelfix/sf6c_measure.py','$PY scripts/labelfix/sf6c_audit.py',
        '$PY -m pytest tests/labelfix/test_sf6_reviewer.py -q -p no:cacheprovider > docs/labelfix/spellcheck/SF6c_evidence/reviewer_after.log 2>&1',
        '$PY -m pytest tests/labelfix -q -p no:cacheprovider > docs/labelfix/spellcheck/SF6c_evidence/tests_after.log 2>&1',
        '$PY scripts/labelfix/sf6c_report.py','$PY scripts/labelfix/sf6c_verify.py','```','',
        f'SF6c RESULT: B01 fixed yes (floor 0.5); B02 fixed yes; reviewer tests 75/75; held-out AB corrected {b["marks"]["after"]["ENSEMBLE_AB"]["corrected"]}, wrong {b["marks"]["after"]["ENSEMBLE_AB"]["wrong"]}; tests {passed} passed; policy sha {c["policy_after"]["sha256"]}']
    path=EV.parent/'SF6_REPORT.md';prefix=(FROZEN/'docs/labelfix/spellcheck/SF6_REPORT.md').read_text()
    path.write_text(prefix.rstrip()+'\n'+'\n'.join(L)+'\n')


if __name__=='__main__':report()
