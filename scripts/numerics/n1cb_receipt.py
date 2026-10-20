"""Seal N1-Cb receipts after tests and the two-sheet layout check."""
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/n1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    data=json.loads((OUT/'N1Cb_GENERATION.json').read_text());summary=data['summary']
    tests=json.loads((OUT/'N1Cb_TESTS.json').read_text());assert all(t['exit_code']==0 for t in tests)
    passed=sum(int(re.search(r'(\d+) passed',t['stdout'])[1]) for t in tests);assert passed==50
    old=json.loads((OUT/'N1C_RECEIPT.json').read_text());report=ROOT/'docs/records/labelfix/secondary/N1C_REPORT.md'
    for group in ['inputs','outputs']:
        for name,entry in old[group].items():
            p=Path(name)
            if not p.is_absolute():p=ROOT/p
            assert sha(p)==entry['sha256'],name
    report_before=sha(report)
    dropped=[json.loads(s) for s in (OUT/'step1_dropped_misaligned_v2.jsonl').read_text().splitlines()]
    outside=[r for r in dropped if r['reason']=='digit box outside crop'];assert len(outside)==28
    with (OUT/'step1_crop_outside_v2.jsonl').open('x') as f:
        for r in outside:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    base=Path(summary['sheets'][0]).parent
    section='''

## N1-Cb

**Ready for lead control review: 558/558 usable step1 slots rendered, 0 crop_unavailable; 94 rendered control candidates on eight sheets plus one C1 reference sheet.** All 623 unique line crops matched their frozen SHA256s. Crop checks include the original 85 control candidates (even the 15 dropped for geometry), selected replacements and the two eligible C1 cards. `controls/crop_checks_v2.jsonl` lists every check; the unavailable list is empty. `ensure_crop` always received a shallow row copy whose `crop` pointed into scratchpad `n1_cache/crops/`; no substitute bytes or hashes were used.

Collector invocation: `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, arm64, Python 3.11.3, Pillow 12.3.0. Its resolved `sys.executable` is `~/Projects/greek-ocr-toolkit/.venv/bin/python`. Rendering/measurement: `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -s`, Python 3.11.3, Pillow 10.4.0. Both interpreter records are in the receipt. Rendering consumed only verified crop bytes.

The **42 misaligned step1 slots were dropped without replacement**: **28 digit boxes outside the crop**, 13 line-text/label disagreements, and 1 reversed digit-box order. All ids and reasons are in `artifacts/n1/step1_dropped_misaligned_v2.jsonl`. The 28 crop-outside cases are separately listed in `artifacts/n1/step1_crop_outside_v2.jsonl` for clipped-crop review. `artifacts/n1/step1_rendered_v2.jsonl` contains all 558 usable slots with line/zoom paths and hashes, exact geometry, and private raw digit-band/component measurements. The original frame and geometry artifact are unchanged. The existing component helper emitted nonfatal poorly-conditioned curve-fit warnings; these remain raw measurements, without a fitted rule or glyph judgment.

`artifacts/n1/controls/candidates_v2.jsonl` has **24 thousands dots, 24 decimal commas, 22 range hyphens, 12 inner hyphens, and 12 empty inner gaps**. Version 1 is retained unchanged. All 15 misaligned v1 controls were dropped; 13 replacements came from the same category pools with the replayed `20261017:N1C:ctrl` shuffle stream. Three further misaligned replacement proposals were skipped. Every rejected id, category, stage and reason is in `controls/rejected_v2.jsonl`. All 70 geometry-ok v1 controls were retained.

The original 13 range candidates include two misaligned slots (one crop-outside, one label disagreement). Applying the explicit misaligned-drop ruling retains **11 of 13**. The entire W1 range pool after the same step1-document, reserved-document and C1 exclusions contains **24 slots total**, including those two invalid ones. The **11 additional slots** were drawn with `20261017:N1C:ctrl:range`. All 22 usable range slots were taken; the two-control shortfall is explicit. Selection origin and source are recorded per candidate.

The reserved C1 card `elstat--c5f7ea1f26d39839--s000-l0367` was refused by the lock guard and excluded. The other two cards' four slots are reference-only records in `controls/c1_references_v2.jsonl`, on one separate sheet labelled **C1 reference**, absent from the candidate census and any pack.

Eight control sheets contain at most 12 cells each (12/12/12/12/12/12/12/10). Each has a large zoom panel, a small whole-line panel, the cell number and Google's glyph. The cell-to-slot mapping, with reference status, is in:

'''
    section+=f'- `{base}/sheets_index.json`\n'
    section+='\nControl sheets:\n\n'+''.join(f'- `{p}`\n' for p in summary['sheets'])
    section+='\nSeparate reference sheet:\n\n'+f'- `{summary["c1_sheet"]}`\n'
    section+='''
Exactly two sheets were opened for layout only: control sheet 01 and the C1 reference sheet. Small native zooms initially left excess white space; all sheets were regenerated with zooms enlarged to fit the large panel. No additional sheet views or glyph classifications followed. The renderer's original 3× zoom files are unchanged; this enlargement is sheet presentation only.

**50 tests passed**: the original 45 plus five artifact checks for exact bed/drop partitioning, control exclusions/replacements, sheet-index/reference isolation, input/output custody and interpreter identity, and verified crops/private measurements. Exact commands and results are in `artifacts/n1/N1Cb_TESTS.json`. Renderer/builder/mapper fixture tests, including marker pixel preservation, lock refusal and calibration mode, passed again; tests built fixture packs only.

No real pack or calibration pack was built; controls await lead approval. No reader run, glyph classification, prompt edit, network access, `.git` write, collector-root write, `run.lock` access or locked-evaluation rendering occurred. Prior N1-C inputs and outputs were hash-checked unchanged before this authorized report append. Full hashes, interpreters, crop failures (empty), drop lists, counts and layout-check scope are in `artifacts/n1/N1Cb_RECEIPT.json`. No live usage probe was run under network OFF.
'''
    with report.open('a') as f:f.write(section)
    inputs=dict(data['inputs']);outputs=dict(data['outputs'])
    for path in [OUT/'N1Cb_GENERATION.json',OUT/'N1Cb_TESTS.json',OUT/'step1_crop_outside_v2.jsonl',ROOT/'scripts/numerics/n1cb_prepare.py',Path(__file__),ROOT/'tests/test_n1cb_artifacts.py',report]:outputs[str(path)]=sha(path)
    for name in ['scripts/numerics/n1_render.py','greekocr/numerics/slots_geom.py','greekocr/glyphs/components.py']:
        inputs[str(ROOT/name)]=sha(ROOT/name)
    for name in ['collect_v3/storage.py','collect_v3/common.py']:
        p=Path.home()/'Projects/greek-ocr-toolkit-sol-collect'/name;inputs[str(p)]=sha(p)
    receipt=dict(status='READY_FOR_LEAD_CONTROL_REVIEW',inputs=inputs,outputs=outputs,summary=summary,interpreters=data['interpreters'],
        collector_invocation=dict(requested_interpreter=str(Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python'),architecture='arm64',method='collect_v3.storage.ensure_crop with redirected shallow row copy'),
        renderer_command=['/usr/bin/arch','-x86_64','/Library/Frameworks/Python.framework/Versions/3.11/bin/python3','-B','-s','scripts/numerics/n1cb_prepare.py'],
        tests=dict(passed=passed,results=tests),crop_unavailable=[],dropped_step1=dropped,crop_outside_step1=outside,
        range_shortfall=dict(target=24,original=13,original_misaligned=2,retained=11,other_W1_added=11,usable=22,shortfall=2,eligible_whole_W1_pool=24,seed='20261017:N1C:ctrl:range'),
        layout_self_check=dict(sheets_opened=[summary['sheets'][0],summary['c1_sheet']],purpose='layout only',glyphs_classified=0,adjustment='enlarge native small zooms to fill large panel; no additional image views'),
        checks=dict(prior_inputs_outputs_unchanged_before_report_append=True,report_before_sha256=report_before,reserved_id_refused=True,all_crops_hash_verified=True,unique_line_crops=623,real_packs_built=False,calibration_pack_built=False,reader_run=False,network=False,git_writes=False,collector_root_writes=False,run_lock_access=False,locked_eval_rendered=False))
    with (OUT/'N1Cb_RECEIPT.json').open('x') as f:f.write(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
    for name,digest in outputs.items():assert sha(name)==digest,name
    print('Receipt written; prior N1-C artifacts and all output hashes verified; tests',passed)
if __name__=='__main__':main()
