"""Seal N1-Cc; document the unresolved C1 document conflict explicitly."""
import json
import re
from pathlib import Path
from n1cb_prepare import ROOT,OUT,SCRATCH,sha,write


def main():
    pending=SCRATCH/'n1_cache/n1cc_generation_pending.json'
    data=json.loads(pending.read_text())
    tests=[json.loads(Path('/private/tmp'/Path(name)).read_text()) for name in
           ['n1cc_text_tests.json','n1cc_image_tests.json','n1cc_artifact_tests.json']]
    assert all(t['exit_code']==0 for t in tests)
    passed=sum(int(re.search(r'(\d+) passed',t['stdout'])[1]) for t in tests)
    assert passed==58
    for section in ['inputs','outputs','prior_unchanged']:
        for p,d in data[section].items():assert sha(p)==d,p
    proposal=SCRATCH/'n1_cache/n1cc_approved_proposed.jsonl'
    data['outputs'][str(proposal)]=sha(proposal)
    data['status']='PENDING_C1_DOCUMENT_RULING'
    data['ambiguous_row_census']=json.loads(Path('/private/tmp/n1cc_ambiguous_census.json').read_text())
    data['layout_self_check']=dict(sheets_opened=[data['summary']['zoom_check']],purpose='layout only; no glyph classification')
    write(OUT/'N1Cc_GENERATION.json',data)
    write(OUT/'N1Cc_TESTS.json',dict(passed=passed,results=tests,
          approval_tests_target='82-row scratchpad proposal; approved.jsonl not written pending C1 document ruling'))
    s=data['summary'];report=ROOT/'docs/records/labelfix/secondary/N1C_REPORT.md'
    before=sha(report)
    section=f'''

## N1-Cc

**Rendering complete; approval sealing pending a C1 document-exclusion ruling.** All {s['zoom_rerendered']} previously rendered zooms were regenerated ({s['step1']} step1 and {s['controls']} reviewed controls), plus {s['candidates']} new candidate zooms. The renderer adds two 7-pixel-wide mid-grey triangles in new 12-pixel white margins after 3× scaling. Every prior zoom remains under its old hash; each new zoom has a new hash. All 640 zoom interiors are pixel-identical to their prior versions, all line hashes match, and all 640 recomputed side measurement records match after JSON serialization. `step1_rendered_v3.jsonl` contains the new step1 image references; `zoom_measurement_checks_cc.jsonl` records comparisons.

The review maps to exactly 82 distinct slots: 21 baseline dots, 23 commas, 27 hyphens/dashes, 7 nothing, 4 raised dots. No rejected cell is included. The cell mapping was taken from the existing `sheets_index.json`. **Conflict:** the four C1 controls are in document `elstat:GRESYE_01_0001_00090`, which occurs in step1. Their lines are outside the frame and reserved set, but their document fails the requested document exclusion. The other 78 controls pass both document exclusions. The explicit C1 control approval therefore needs to be reconciled with the document-level constraint. `controls/approved.jsonl` has not been written while that question is pending. The complete 82-row proposal with new renders is `{proposal}`. No C1 line was admitted to the candidate pool.

Raised-dot eligibility used the union of nonempty inner separators in 4+-digit tokens on the supplied ambiguous rows and Google `·`/`-` grammar-thousands slots in 4+-digit tokens on any W1 elstat/gazette row, with exact geometry required. After step1/reserved document and C1 line exclusions, the pool is **{s['raised_pool']} slots in {s['raised_pool_rows']} rows and {s['raised_pool_documents']} documents**; {s['raised_geometry_rejected']} further slot failed geometry. Both eligible slots were selected with seed `{s['seed']}`, below the three-per-document cap. These are candidates for the lead, without any new printed-glyph truth labels. Full pool, selected records and geometry rejection are in `controls/raised_pool_cc.jsonl`, `controls/raised_candidates_cc.jsonl` and `controls/raised_rejected_geometry_cc.jsonl`.

Candidate sheet: `{s['sheets'][0]}` (cells 101–102, Google glyph shown). Index: `{SCRATCH/'n1_ctrl_sheets/sheets_index_cc.json'}`. Sample sheet: `{s['zoom_check']}` (12 reviewed controls, cells 84, 87, 89, 90, 91, 92 and 94 first). Only the sample sheet was viewed, for layout; no glyphs were classified.

Both newly requested candidate line crops passed frozen SHA256 checks through the collector's arm64 Python 3.11.3/Pillow 12.3.0 using redirected shallow row copies. Rendering and measurements used x86 Python 3.11.3/Pillow 10.4.0 with `-B -s`; existing verified crops were rehashed. Existing component-helper poorly-conditioned fit warnings were nonfatal and measurement equality passed.

**{passed} tests passed**: 44 existing text/artifact checks, 8 image/builder fixtures (including zoom interior preservation and two crop-boundary marker tests), and 6 new approval-proposal/census/custody checks. Approval tests currently verify the proposal and explicitly record the four C1 document conflicts; they do not certify unconditional document exclusion. Commands and outputs are in `N1Cc_TESTS.json`.

All prior persistent N1 artifacts and earlier rendered images were rehashed unchanged before this report append. No real or calibration pack, reading run, network access, `.git` write, collector-root write, `run.lock` access, prompt edit or locked-evaluation rendering occurred. The receipt status remains `PENDING_C1_DOCUMENT_RULING`, rather than READY.
'''
    with report.open('a') as f:f.write(section)
    outputs=dict(data['outputs'])
    for p in [OUT/'N1Cc_GENERATION.json',OUT/'N1Cc_TESTS.json',report,
              ROOT/'scripts/numerics/n1cc_prepare.py',Path(__file__),
              ROOT/'scripts/numerics/n1_render.py',ROOT/'tests/test_n1_packs_render.py',ROOT/'tests/test_n1cc_artifacts.py']:
        outputs[str(p)]=sha(p)
    write(OUT/'N1Cc_RECEIPT.json',dict(data,outputs=outputs,tests=dict(passed=passed,results=tests),
        report_before_sha256=before,approved_file_written=False,proposal=str(proposal),
        unresolved='Four explicitly approved C1 slots share a step1 document. Awaiting control-only exception or reduction to 78 controls.'))
    for p,d in outputs.items():assert sha(p)==d,p
    print('N1Cc receipt: PENDING_C1_DOCUMENT_RULING;',passed,'tests passed')

if __name__=='__main__':main()
