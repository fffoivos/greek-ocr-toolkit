"""Offline N1-R2 final custody receipt and report append. No reading calls."""
from collections import Counter
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from n1r2_prepare import ROOT, OUT, PACK_ROOT, SCRATCH, sha, dump, rows
from n1_pack_closure import scan

COLLECTOR=Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python'

def main():
    priorpath=SCRATCH/'n1_review/n1r2_prior.json';prior=json.loads(priorpath.read_text())
    changed=[p for p,digest in prior.items() if not Path(p).is_file() or sha(p)!=digest]
    assert not changed,changed
    closure=[scan(PACK_ROOT/f'ctx{i:02}'/reader,OUT,completed=True) for i in range(1,8) for reader in ('r1','r2')]
    assert all(r['ok'] for r in closure)
    dry=[]
    env=dict(os.environ,PATH=str(COLLECTOR.parent)+':/usr/bin:/bin:/usr/sbin:/sbin')
    for i in range(1,8):
        cmd=['bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),'n1',f'ctx{i:02}','r2','--dry-run']
        result=subprocess.run(cmd,env=env,capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
        dry.append(dict(command=cmd,exit_code=result.returncode,result=json.loads(result.stdout)))
    assert not list((OUT/'answers').glob('ctx*.r2.*'))
    assert not any((PACK_ROOT/f'ctx{i:02}/r2/answers.jsonl').exists() for i in range(1,8))
    tests=[]
    for filename in ('N1R2_REGRESSION.xml','N1R2_SHARED_SCANNER.xml','N1R2_IMAGE_TESTS.xml'):
        path=OUT/filename; tree=ET.parse(path)
        cases=tree.findall('.//testcase'); bad=tree.findall('.//failure')+tree.findall('.//error')
        assert not bad
        tests.append(dict(junit=str(path),sha256=sha(path),passed=len(cases),failures=0))
    newcases=[c for c in ET.parse(OUT/'N1R2_REGRESSION.xml').findall('.//testcase') if c.get('classname')=='tests.test_n1r2']
    assert len(newcases)==35
    testresult=dict(new_n1r2_tests=35,regression_tests=tests,total_passed=sum(t['passed'] for t in tests),
                    deselected=['tests/test_n1cd.py::test_real_pack_coverage_and_v3_images'],
                    deselection_reason='Frozen pre-reading manifest excludes preserved r1 answers.jsonl and zoom/check*.png. Current sealed-content and runtime-aware closure independently pass for all 14 reader folders.',
                    commands=[
                      'PYTHONPATH=. '+str(COLLECTOR)+" -B -s -m pytest -q tests/test_n1r2.py tests/test_n1_score.py tests/test_n1_map_answers.py tests/test_n1_slots_geom.py tests/test_n1cd.py tests/test_n1cc_artifacts.py tests/test_n1cb_artifacts.py -k 'not test_real_pack_coverage_and_v3_images' --junitxml=artifacts/n1/N1R2_REGRESSION.xml",
                      'PYTHONPATH=. '+str(COLLECTOR)+' -B -s -m pytest -q tests/test_ru1_second_reader.py tests/test_ru1r3.py --junitxml=artifacts/n1/N1R2_SHARED_SCANNER.xml',
                      'x86_64 Python 3.11 -B -s, append collector site-packages for pure Python pytest only; pytest --noconftest -q tests/test_n1_packs_render.py --junitxml=artifacts/n1/N1R2_IMAGE_TESTS.xml'])
    dump(OUT/'N1R2_TESTS.json',testresult)
    indexpath=SCRATCH/'n1_review/raised/sheets_index.json';index=json.loads(indexpath.read_text())
    summary=json.loads((OUT/'decisions_summary.json').read_text())
    assert summary['bed_slots']==558 and summary['truth_candidates']==summary['applied_edits']==0
    assert (OUT/'lead_raised_template.jsonl').stat().st_size==0
    report=ROOT/'docs/records/labelfix/secondary/N1S_REPORT.md';before=sha(report)
    assert '\n## N1-R2\n' not in report.read_text()
    section=f'''

## N1-R2

**Seven r2 packs ready; closure 14/14. Lead reference substitution remains pending.** No reading run or usage probe was performed. The N1-S one-read tables above are historical reader evidence, not truth: the 9 control errors include three baseline-dot → raised-dot and one nothing → raised-dot error. A single read cannot qualify an N1 edit.

Each `sol_packs/n1/ctxNN/r2/` has the exact reverse of its r1 item order (bed and the same nine controls), new opaque IDs, and an independent per-item option permutation in which every letter changes meaning. The 558 bed slots occur once per reader; there are 63 control appearances per reader. Line and marked-zoom bytes are identical between reads. Private assignments are `artifacts/n1/keys/ctxNN.r2.json`; seals are `ctxNN/MANIFEST.r2.json`. Runtime-aware closure verifies all 14 folders against their sealed contents while preserving r1 answers and check images. Every previous N1 artifact and r1 file remains byte-identical; manifests were not rewritten. Full hashes and closure results are in `N1R2_PACKS.json` and `N1R2_RECEIPT.json`.

`run_n1.sh n1 ctxNN r2` now routes to r2 keys/packs and `artifacts/n1/answers/ctxNN.r2.*`. `--dry-run` validates locally and returns before probe, reader, attempt, or ledger writes. All seven real-pack r2 dry runs passed. The normal dispatch/output naming was also tested with an isolated executable fake reader; no real reader was invoked.

`scripts/numerics/n1_decide.py` joins the two private assignments per slot, independently decodes answers and gates each context using N1-S control-abstention rules, and requires successful run/v4-scan provenance. Missing/malformed/duplicate/unexpected answers fail closed. Two agreeing gate-passing reads are required for a truth candidate. A VOID read is retained as secondary evidence only and cannot satisfy the two-VALID requirement; the rule is symmetric for r1/r2. Disagreement, unreadable/other, or fewer than two valid reads yields `lead_review`. The exact Google glyph must be `-` or `.`, the primary grammar `position` must equal `thousands`, and the truth candidate must be raised dot for an `edit_candidate` of U+00B7. A range slot that also lists thousands among its grammar candidates is not eligible under this primary-position test. Every raised-dot call requires the lead's pixel check, even when reads agree. Decisions contain proposals only (`edit=null`, `apply_edit=false`); no label text was changed.

Current `decisions.jsonl`: **558 slots, 558 lead_review, zero truth candidates, zero edit candidates, zero applied edits**; all r2 reads are missing by design. `decisions_summary.json` records per-context gates and reasons. Rebuild after authorized r2 reads with `n1_decide.py`, then `n1_raised_sheets.py`; neither script launches readers.

Lead sheets: `{indexpath.parent}`. **39 bed cells on 5 PNG sheets**, covering ANY r1 raised-dot call, including VOID/low-confidence reads, union every 'Hyphen printed as raised dot' owner-sheet card. Each sheet has at most 8 bed cells plus 4 approved reference cells (≤12 total). Marked zooms are large, marked whole lines small; cells show Google glyph, slot ID, numbered identity and both read states. `sheets_index.json` binds cells, reads, reference approval identities and image hashes. `artifacts/n1/lead_raised_template.jsonl` is empty, and the rebuild preserves it if populated later. All five contact sheets and an enlarged cell were visually inspected for layout only; no lead glyph adjudication is claimed.

**Reference limitation:** all four approved raised-dot controls are in `elstat:GRESYE_01_0001_00090`, which has no approved baseline-dot controls. The two baseline references are approved controls from `elstat:GRESYE_01_0001_00429`. Both raised references are from the first document. Every sheet prominently labels this cross-document substitution; same-document reference compliance is **false**, awaiting two lead-approved baseline controls from the raised-reference document or a lead exception. The supplied approved set cannot fulfill that requirement, and no new truth labels were invented.

Validation: **35 N1-R2 tests passed**, within **87 N1 regression tests**, plus **34 shared-reader checks** and **8 x86 image/builder checks** (129 passed total). The historical frozen-manifest test remains deselected for the documented r1 runtime-file issue; it is preserved, and the new 14-folder closure test passes. The suite covers both VOID directions, disagreement, missing/invalid contexts, uncertain reads, exact glyph/primary-grammar edits, r2 mapping, control abstentions, order/control/image custody, option tampering, overwrite refusal, dry runs, fake dispatch and sheet union coverage. Results: `N1R2_TESTS.json` and JUnit files.

Image operations used `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -s` (Pillow 10.4.0); regression tests used the prescribed collector interpreter. Network OFF; no `.git` writes, prompt changes, live reader/probe, run.lock access, collector-root writes, locked-stratum rendering, fitting, publication or label application.
'''
    with report.open('a') as f:f.write(section)
    codepaths=[ROOT/p for p in [
        'scripts/numerics/n1r2_prepare.py','scripts/numerics/n1_decide.py','scripts/numerics/n1_raised_sheets.py','scripts/numerics/n1r2_receipt.py',
        'scripts/numerics/n1_pack_closure.py','scripts/numerics/n1_map_answers.py','scripts/numerics/n1_score.py',
        'scripts/secondary/reading/n1_launch.py','scripts/secondary/reading/run_n1.sh','scripts/secondary/reading/scan_packs.py','tests/test_n1r2.py']]
    outputpaths=[p for base in (OUT,PACK_ROOT,indexpath.parent) for p in base.rglob('*') if p.is_file() and str(p) not in prior]
    outputpaths += [report,*codepaths]
    from PIL import __version__ as pillow_version
    receipt=dict(task='N1-R2',status='READY_FOR_R2_READ_PENDING_SAME_DOCUMENT_REFERENCES',
                 network=False,git_writes=False,reader_run=False,live_probe=False,run_lock_access=False,
                 pack_root=str(PACK_ROOT),r2_packs=7,bed_slots=558,controls_per_context=9,
                 closure_ok=14,closure_total=14,closure=closure,dry_runs=dry,
                 tests=testresult,decisions=summary,
                 raised=dict(cells=index['bed_cells'],sheets=len(index['sheets']),index=str(indexpath),
                             complete_same_document_references=index['complete_same_document_references'],limitation=index['reference_limitation']),
                 prior_snapshot=dict(path=str(priorpath),sha256=sha(priorpath),files=len(prior),all_unchanged=True),
                 report_before_sha256=before,
                 renderer_interpreter=dict(executable=sys.executable,architecture=platform.machine(),python=platform.python_version(),pillow=pillow_version),
                 collector_interpreter=str(COLLECTOR),layout_qa=dict(all_sheets_opened=True,enlarged_cell_opened=True,classification_performed=False),
                 outputs={str(p):sha(p) for p in outputpaths})
    dump(OUT/'N1R2_RECEIPT.json',receipt)
    assert all(sha(p)==d for p,d in prior.items())
    assert all(sha(p)==d for p,d in receipt['outputs'].items())
    print(f'N1R2 READY: r2 packs 7 (closure 14/14); combiner tests 35 passed; raised-dot lead cells {index["bed_cells"]} on {len(index["sheets"])} sheets')

if __name__=='__main__': main()
