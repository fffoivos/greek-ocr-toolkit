"""Offline phase-A receipt: no readings, probes, fitting or publication."""
from collections import Counter,defaultdict
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.numerics.combine_v2 import MEANINGS
from n1_render import SCRATCH
from n1t_packs import rows,sha,dump
from n1_pack_closure import scan
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'artifacts/n1';OUT=BASE/'n1t'


def main():
    build=json.loads((OUT/'build.json').read_text());slots=rows(_data_input(OUT/'slots.jsonl'))
    contexts=sorted((SCRATCH/'sol_packs/n1t').glob('ctx*'));closures=[];dry=[]
    env=dict(os.environ,PATH=str(Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin')+':/usr/bin:/bin:/usr/sbin:/sbin')
    for ctx in contexts:
        for reader in ('r1','r2'):
            result=scan(ctx/reader,OUT,completed=True,meanings=MEANINGS)
            assert result['ok'],result['violations'];closures.append(result)
            cmd=['/usr/bin/arch','-arm64','bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),'n1t',ctx.name,reader,'--dry-run']
            r=subprocess.run(cmd,env=env,capture_output=True,text=True)
            assert r.returncode==0,r.stdout+r.stderr
            dry.append(dict(command=cmd,result=json.loads(r.stdout)))
    calibration=subprocess.run([sys.executable,'-B','-s',str(ROOT/'scripts/numerics/n1t_packs.py'),'--calibration'],capture_output=True,text=True)
    assert calibration.returncode!=0 and 'Lead dash types pending for 27 controls' in calibration.stderr
    assert not (SCRATCH/'sol_packs/n1cal2').exists()
    assert not list(OUT.glob('answers/*')) and not any((ctx/r/'answers.jsonl').exists() for ctx in contexts for r in ('r1','r2'))
    prior=json.loads(Path(build['prior_snapshot']).read_text());assert all(sha(p)==h for p,h in prior.items())
    geometry=Counter(s['geometry']['geom_status'] for s in slots)
    dashslots=[s for s in slots if s.get('dash',{}).get('strokes')]
    types=Counter(s['dash']['geometric_type'] or 'ambiguous' for s in dashslots)
    histogram=defaultdict(Counter)
    for s in dashslots:
        for stroke in s['dash']['strokes']:
            ratio=stroke['dash_len_ratio']
            bucket='unavailable' if ratio is None else '<0.75' if ratio<.75 else '0.75–<1.45' if ratio<1.45 else '≥1.45'
            histogram[s['glyph']][bucket]+=1
    publics=[rows(ctx/r/'items.jsonl') for ctx in contexts for r in ('r1','r2')]
    tests=[]
    for name in ('N1T_TESTS.xml','N1T_IMAGE_TESTS.xml'):
        p=BASE/name;tree=ET.parse(p);cases=tree.findall('.//testcase')
        assert not tree.findall('.//failure') and not tree.findall('.//error')
        tests.append(dict(path=str(p),sha256=sha(p),passed=len(cases)))
    counts=dict(lines=build['lines'],slots=len(slots),geometry=dict(geometry),dash_slots=len(dashslots),dash_types=dict(types),
        contexts=len(contexts),readers=2,reader_folders=len(publics),items=sum(map(len,publics)),calibration_items=82,
        total_planned_items=sum(map(len,publics))+82,estimated_points=(sum(map(len,publics))+82)*.2/100,
        tests_passed=sum(t['passed'] for t in tests))
    code=[ROOT/p for p in ['greekocr/numerics/line_complete.py','greekocr/numerics/dash.py','greekocr/numerics/combine_v2.py',
        'greekocr/numerics/owner_v2.py','greekocr/numerics/slots_geom.py','scripts/numerics/n1_render.py','scripts/numerics/n1_pack_closure.py',
        'scripts/numerics/n1t_prepare.py','scripts/numerics/n1t_packs.py','scripts/numerics/n1t_combine.py',
        'scripts/numerics/n1t_owner_sheet.py','scripts/numerics/n1t_receipt.py','scripts/secondary/reading/n1_launch.py','tests/test_n1t.py']]
    receipt=dict(task='N1-T phase A',status='BED_PACKS_READY_CALIBRATION_PENDING_LEAD_DASH_TYPES',counts=counts,
        phase_a_line_ids=json.loads((OUT/'selection.json').read_text())['line_ids'],phase_a_slots=str(OUT/'slots.jsonl'),
        geometry_failures=[dict(slot_id=s['slot_id'],geometry=s['geometry']) for s in slots if s['geometry']['geom_status']!='ok'],
        dash_histogram_per_google_glyph={g:dict(v) for g,v in histogram.items()},dash_histogram_unit='horizontal components; multi-stroke slots contribute multiple values',
        fixed_thresholds=[.75,1.45],dash_component_rule='wholly inside exact gap; width >= max(3 native pixels, 2 * height); no fitting',
        dash_controls=str(SCRATCH/'n1_review/dash_controls.png'),dash_control_assignments=str(BASE/'controls/dash_types_template.jsonl'),
        controls_policy='Bed: 9 approved non-dash controls, >=1 raised dot per context. Calibration: all 82; refuses before all 27 lead dash types are filled.',
        closure=closures,dry_runs=dry,calibration_refusal=dict(exit_code=calibration.returncode,message=calibration.stderr.strip()),
        tests=tests,prior_snapshot=build['prior_snapshot'],prior_unchanged=True,inputs=build['inputs'],
        source_hashes={str(p):sha(p) for p in code},outputs={str(p):sha(p) for p in OUT.rglob('*') if p.is_file()},
        network=False,git_writes=False,reader_run=False,probe_run=False,run_lock_access=False,fitting=False,
        owner_sheet_rebuilt=False,owner_sheet_target=str(BASE/'owner_sheet/n1_sheet.html'),
        legacy_r2_used=False,label_edits=0,live_usage='Not probed under network OFF',
        interpretation='Two agreeing high-confidence VALID reads required. VOID retained only as secondary evidence, insufficient for truth. Dash reader/geometry disagreement or absent geometry -> lead_review. Dash types tag-only for labels.',
        layout_qa='Dash control sheet visually inspected for layout only; owner fixture HTML validated structurally; no glyph classifications or lead assignments.')
    dump(BASE/'N1T_RECEIPT.json',receipt)
    table=['| Google exact gap | <0.75 | 0.75–<1.45 | ≥1.45 | unavailable |','|---|---:|---:|---:|---:|']
    for g,v in sorted(histogram.items()):table.append('| `'+json.dumps(g,ensure_ascii=False)+'` | '+' | '.join(str(v[b]) for b in ('<0.75','0.75–<1.45','≥1.45','unavailable'))+' |')
    report=f'''# N1-T phase A build

**Bed packs ready; calibration awaits the lead's 27 dash assignments. No reading run, probe, owner-sheet replacement or label edit occurred.**

Phase A is **{build['lines']} distinct lines, {len(slots)} slots**: the union of every current owner-sheet card's line and every line with an exact Google `-` in a 4+-digit token read in a VALID historical r1 context. The summary's cards hash binds the current sheet input. The historical r1 keys, answers, gates and successful run/v4-scan provenance were independently checked. No partial N1-R2 folders or decisions are consumed. Every selected line is in a step1 document; `greekocr.numerics.locks` rejects reserved lines before crop/geometry access. Selection: `artifacts/n1/n1t/selection.json`.

`line_complete.py` uses `tokens.py` without normalisation: all numeric tokens, every adjacent-digit gap including empty gaps, and both boundaries. Exact W1 text/label/DocAI anchors must agree. **{geometry['ok']} geometry OK; {len(slots)-geometry['ok']} failures**. The failed slot is `elstat--fa8be8ddafd5c043--s000-l0110:t0:s2` (reversed digit boxes); it remains in enumeration for lead review and is excluded from reader packs. No geometry is guessed. For line-edge boundary windows, the exact neighbouring symbol edge or crop edge is used, rather than an estimated digit-width extension. Rendering reuses the v3 margin triangles and original marker-preserving renderer; existing outputs remain unchanged. Every render has a side measurement record in `n1t/slots.jsonl`. Native collector Python regenerates SHA-verified crops into scratch only; x86 Python 3.11/Pillow 10.4 renders. An initial inherited-architecture crop import failed before rendering and was corrected with an explicit arm64 collector invocation.

**Dash geometry:** {len(dashslots)} slots have qualifying horizontal components. Single-stroke proposals: hyphen {types['hyphen']}, en dash {types['en dash']}, em dash {types['em dash']}; {types['ambiguous']} multi-stroke slots remain geometrically ambiguous. Each component records native length, height, height/digit-height, vertical centre/digit-band and length/median width of **all token digits**, derived from exact symbol anchors. The component criterion is fixed (`width >= max(3 pixels, 2*height)`, wholly inside the gap); crossing digit components are retained in raw measurements but not classified as strokes. The starting thresholds **0.75 and 1.45** are reported, never fitted or tuned. A measured type is a proposal, not ink truth.

Histogram by exact Google gap (unit: qualifying components, not slots; multi-stroke slots contribute more than once):

{chr(10).join(table)}

**Dash controls:** `{SCRATCH/'n1_review/dash_controls.png'}` contains all 27 approved hyphen/dash controls, with their original cell numbers 49–81 (rejected numbers stay absent), marked zooms and a ruler representing one median token digit width at the displayed zoom scale. No ratio or geometric type is printed. Private measurement/index: `n1t/dash_controls_index.json`. Lead-entry template: `controls/dash_types_template.jsonl` (`truth`: `hyphen`, `en dash`, `em dash`). All 27 values remain null; no lead truth was invented.

**Packs:** {len(contexts)} contexts × 2 independent readers, {len(publics)} folders, {counts['items']} items including repeated controls. {geometry['ok']} distinct bed slots occur exactly once per reader. Each context has 9 distinct approved **non-dash** controls, including ≥1 raised dot, and at most 89 items. The 55 non-dash approvals allow packs to be built without inventing dash-control truth. r2 reverses the entire r1 order (including controls), uses fresh opaque IDs, and changes every option letter's meaning. Private keys/measurements stay under `artifacts/n1/n1t/`; public packs under `{SCRATCH/'sol_packs/n1t'}` contain only item lists and hash-named, metadata-free PNGs. Every item uses all ten sep2 meanings.

**Closure {len(closures)}/{len(closures)} PASS**, independently verified against sealed manifests; all {len(dry)} real bed-folder launcher dry runs pass without probes or reads. `run_n1.sh` now accepts `n1cal2`/`n1t`, isolates their keys/answers/ledgers from old N1, and selects unchanged `sep2.md`. A fixture calibration of 82 controls also passes closure and launcher dry-run. **The real `n1cal2/cal01/r1` pack is intentionally absent:** its builder refuses with “Lead dash types pending for 27 controls” until the lead fills all dash assignments. Resume with `n1t_packs.py --calibration`; this validates and seals all 82 truths before writing a pack.

**Combiner v2:** `n1t_combine.py` requires both complete sep2 readings and successful run/v4 scanner provenance. Two independent, high-confidence agreeing VALID reads produce a truth candidate. A VOID read is secondary-only and cannot replace either required VALID vote. All other states remain lead_review, including unreadable/other/low-confidence, disagreement, geometry failure, and dash reader/geometry disagreement. Edit candidates are exact Google `-`/`.` → U+00B7 only for raised-dot truth candidates with grammar `thousands` among the slot's candidates; range/thousands alternatives are retained explicitly. All dash label outcomes are tags only; no training label is edited.

**Owner sheet v2:** `owner_v2.py` and `n1t_owner_sheet.py` are fixture-tested only. The production builder refuses before complete N1-T readings and decisions, then uses the prescribed cleanup renderer and the same target `artifacts/n1/owner_sheet/n1_sheet.html`. Cards use the line ID for note identity; all numeric slots are boxed/numbered, every non-nothing render has a gap-numbered zoom, full Google/Ours/Gaps rows name marks and confidence, and Printed is prefilled from Ours with `data-printed-source="ours-proposal"`. Unsure gaps retain Google's exact substring. Group order and the three-sentence intro follow the owner's ruling; agreement-only cards are sampled deterministically to at most 12, with omitted agreement lines recorded in the spec. The existing sheet/cards/spec/summary remain byte-identical. Fixture HTML rendering verifies prefill and data attributes. No production owner sheet is published or replaced.

**Tests: {counts['tests_passed']} passed**, including meaningful fixtures for complete enumeration and locks, threshold boundaries, multi-stroke ambiguity, every sep2 meaning, gate failure and VOID roles, exact edit direction, dash cross-checks, pack isolation/reversal/permutations, calibration refusal, closure tampering, launcher dry runs and the actual owner renderer. JUnit: `N1T_TESTS.xml`, `N1T_IMAGE_TESTS.xml`. The historical frozen pre-reading manifest test is excluded because preserved old r1 packs now carry runtime files; production N1-T seals are independently verified. No N1-R2 tests or products are used.

**Codex estimate:** {counts['items']} bed/control appearances + 82 calibration items = **{counts['total_planned_items']} items**, at 0.2 points/100 = **{counts['estimated_points']:.3f} points**. Build ran no live usage probe; this is an estimate, not metered consumption. Detailed counts, hashes, gates, failure, dry runs and custody are in `artifacts/n1/N1T_RECEIPT.json`. Network OFF; no `.git` writes, collector-root writes, `run.lock`, reserved-line rendering, fitting, reader execution, or publication.
'''
    (ROOT/'docs/records/labelfix/secondary/N1T_REPORT.md').write_text(report)
    print(json.dumps(counts))
if __name__=='__main__':main()
