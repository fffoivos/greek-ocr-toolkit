"""Offline N1-Tb build and verification; never invokes a reader or probe."""
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)]
from greekocr.numerics.prune import prune, AUDIT_SEED
from greekocr.numerics.combine_v2 import MEANINGS, decide
from greekocr.numerics.locks import load_locks
from n1_render import SCRATCH, clean_png
from n1t_packs import rows, sha, dump, typed_controls, build
from n1t_prepare import jsonl
from n1_pack_closure import scan
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'artifacts/n1'
OUT = BASE/'n1t2'
PACKS = SCRATCH/'sol_packs'


def snapshot(roots):
    return {str(p):sha(p) for root in roots for p in root.rglob('*') if p.is_file()}


def prepare():
    from PIL import Image
    if OUT.exists(): raise ValueError('refusing to overwrite n1t2')
    old = snapshot([BASE/'n1t', PACKS/'n1t', BASE/'owner_sheet'])
    dump(OUT/'superseded.json', dict(status='superseded; preserved', files=old))
    mapping = {}
    for truth, cells in [('hyphen',[49,50,51,53,56,57,58,59,63,73,75,77,80,81]),
                         ('en dash',[54,65,67,68,76,78]),('em dash',[60,62,66,69,70]),('any dash',[61,64])]:
        mapping.update({cell:truth for cell in cells})
    assignments = [dict(r, truth=mapping[r['cell_number']],
                        lead_note='unsure en/em; any dash accepted' if r['cell_number'] in (61,64) else 'lead pixel ruling 2026-10-17')
                   for r in rows(BASE/'controls/dash_types_template.jsonl')]
    path = BASE/'controls/dash_types.jsonl'
    jsonl(path, assignments)
    (path.with_suffix('.jsonl.sha256')).write_text(sha(path)+'  dash_types.jsonl\n')
    controls = typed_controls(rows(BASE/'controls/approved.jsonl'), assignments)
    slots = prune(rows(BASE/'n1t/slots.jsonl'))
    lines = rows(BASE/'n1t/lines.jsonl'); byline = {l['line_id']:l for l in lines}
    locks = load_locks(BASE); locks.assert_fit_rows(s['line_id'] for s in slots)
    for s in slots:
        if s['geometry']['geom_status'] == 'ok': continue
        # No anchor is fabricated: both images show the complete native line.
        line = byline[s['line_id']]
        assert sha(line['crop']) == line['crop_sha256']
        with Image.open(line['crop']) as im:
            images = [im.convert('RGB'), im.convert('RGB').resize((im.width*3,im.height*3),Image.Resampling.LANCZOS)]
        for name, im in zip(('line','zoom'),images):
            data = clean_png(im)
            import hashlib
            digest = hashlib.sha256(data).hexdigest()
            p = SCRATCH/'n1_cache/n1t2_rendered'/(digest+'.png');p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(data);s[name]=str(p);s[name+'_sha256']=digest
        s['render_scope']='whole_line_unlocalized'
    jsonl(OUT/'slots.jsonl',slots);jsonl(OUT/'lines.jsonl',lines)
    jsonl(OUT/'geometry_decisions.jsonl',[decide(s,[]) for s in slots if s['read_reason']=='geometry-only'])
    bed = [s for s in slots if s['read_reason']!='geometry-only']
    summaries = {}
    for name, selected, calibration in [('n1t2',bed,False),('n1cal2',[],True)]:
        out = BASE/name
        jsonl(out/'controls/approved.jsonl',controls)
        summaries[name] = build(selected,controls,PACKS/name,out,locks,calibration)
        dump(out/'pack_build.json',summaries[name])
    assert all(sha(p)==h for p,h in old.items())
    dump(OUT/'build.json',dict(counts=dict(Counter(s['read_reason'] for s in slots)),audit_seed=AUDIT_SEED,
        source_slots_sha256=sha(BASE/'n1t/slots.jsonl'),dash_types_sha256=sha(path),summaries=summaries))
    print(json.dumps(dict(Counter(s['read_reason'] for s in slots))))


def verify():
    buildinfo=json.loads((OUT/'build.json').read_text()); slots=rows(OUT/'slots.jsonl')
    closures=[];dry=[]
    env=dict(os.environ, PATH=str(Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin')+':/usr/bin:/bin:/usr/sbin:/sbin')
    for name in ('n1t2','n1cal2'):
        for ctx in sorted((PACKS/name).iterdir()):
            if not ctx.is_dir():continue
            for reader in ('r1','r2') if name=='n1t2' else ('r1',):
                result=scan(ctx/reader,BASE/name,completed=True,meanings=MEANINGS)
                assert result['ok'],result['violations'];closures.append(result)
                cmd=['/usr/bin/arch','-arm64','bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),name,ctx.name,reader,'--dry-run']
                r=subprocess.run(cmd,env=env,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
                dry.append(dict(command=cmd,result=json.loads(r.stdout)))
                assert not (ctx/reader/'answers.jsonl').exists()
    # Also validate the preserved root requested by the brief; it remains runnable only by explicit name.
    for ctx in sorted((PACKS/'n1t').glob('ctx*')):
        for reader in ('r1','r2'):
            cmd=['/usr/bin/arch','-arm64','bash',str(ROOT/'scripts/secondary/reading/run_n1.sh'),'n1t',ctx.name,reader,'--dry-run']
            r=subprocess.run(cmd,env=env,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
            dry.append(dict(command=cmd,result=json.loads(r.stdout),superseded=True))
    old=json.loads((OUT/'superseded.json').read_text())['files'];assert all(sha(p)==h for p,h in old.items())
    for name in ('n1t2','n1cal2'):assert not (BASE/name/'answers').exists()
    tests=[]
    for name in ('N1Tb_TESTS.xml','N1Tb_IMAGE_TESTS.xml'):
        p=BASE/name;t=ET.parse(p);assert not t.findall('.//failure') and not t.findall('.//error')
        tests.append(dict(path=str(p),sha256=sha(p),passed=len(t.findall('.//testcase'))-len(t.findall('.//skipped'))))
    summaries=buildinfo['summaries'];contexts=len(summaries['n1t2']['contexts'])
    items=sum(sum(c['readers'].values()) for v in summaries.values() for c in v['contexts'])
    counts=dict(buildinfo['counts'],read_slots=sum(s['read_reason']!='geometry-only' for s in slots),
        phase_a_slots=len(slots),lines=len(rows(OUT/'lines.jsonl')),contexts=contexts,calibration_items=82,
        total_items=items,estimated_points=items*.2/100,tests_passed=sum(t['passed'] for t in tests))
    receipt=dict(task='N1-Tb',status='READY',counts=counts,dash_types_sha256=buildinfo['dash_types_sha256'],
        lead_rulings=dict(path='docs/labelfix/secondary/N1_DASH_CONTROL_TYPES.md',sha256=sha(ROOT/'docs/labelfix/secondary/N1_DASH_CONTROL_TYPES.md')),
        audit_seed=AUDIT_SEED,audit_slot_ids=[s['slot_id'] for s in slots if s['read_reason']=='audit'],
        reason_precedence=['geom-fail','google-mark','ink-only','audit','geometry-only'],
        ink_policy='Any positive-width gap intersection with a measured component bounding box beyond digit-box edges; crossing components retained conservatively. No dash-length filter.',
        geometry_failure_policy='Complete-line native context and 3x full-line zoom; no guessed marker or geometry; combiner retains lead_review.',
        controls_policy='9 distinct controls per context; >=1 raised dot and >=1 each hyphen/en/em. Two unsure controls accept any dash, every non-dash wrong, including unreadable.',
        geometry_decisions=str(OUT/'geometry_decisions.jsonl'),superseded_inventory=str(OUT/'superseded.json'),superseded_unchanged=True,
        active_root='n1t2',calibration_root='n1cal2',closure=closures,dry_runs=dry,tests=tests,
        test_exclusions={'test_real_pack_coverage_and_v3_images':'Historical pre-reading manifest test; old r1 packs contain runtime files. Superseded N1-T/new packs independently sealed and validated.'},
        interpreters={'build':'arch -x86_64 Python 3.11 -B -s; Pillow 10.4', 'verification':'arch -arm64 collector .venv Python -B -s', 'image_tests':'x86_64 Python 3.11 -B -s with pure-Python pytest appended'},
        network=False,git_writes=False,reader_run=False,probe_run=False,label_edits=0,owner_sheet_rebuilt=False,
        live_usage='Not probed; estimate only',outputs=snapshot([OUT,BASE/'n1cal2']),
        source_hashes={str(p):sha(p) for p in [ROOT/'greekocr/numerics/prune.py',ROOT/'scripts/numerics/n1tb_prepare.py',ROOT/'scripts/numerics/n1t_packs.py',ROOT/'greekocr/numerics/combine_v2.py',ROOT/'greekocr/numerics/owner_v2.py',ROOT/'scripts/numerics/n1t_combine.py',ROOT/'scripts/numerics/n1t_owner_sheet.py',ROOT/'scripts/secondary/reading/n1_launch.py',ROOT/'scripts/numerics/n1_calibration.py',ROOT/'scripts/numerics/n1_map_answers.py',ROOT/'tests/test_n1tb.py']})
    (BASE/'N1Tb_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    report=ROOT/'docs/labelfix/secondary/N1T_REPORT.md'
    if '\n## N1-Tb\n' in report.read_text():
        report.write_text(report.read_text().split('\n## N1-Tb\n')[0])
    with report.open('a') as f:
        f.write(f'''\n## N1-Tb\n\n**READY.** This section supersedes the original pack/count and calibration-pending statements above. Lead dash types are sealed in `controls/dash_types.jsonl`, SHA256 `{buildinfo['dash_types_sha256']}` (sidecar `.jsonl.sha256`). Assignments: 14 hyphens, 6 en dashes, 5 em dashes, 2 unsure cells (61/64) scored as any dash; every non-dash answer is wrong, including unreadable on these two controls. The template is preserved.\n\nAll 2,129 slots remain in `n1t2/slots.jsonl` on the same 207 complete lines. Exclusive reason counts, with geometry failures first: **{counts['google-mark']} google-mark** (any nonempty Google substring, including spaces), **{counts['ink-only']} ink-only**, **{counts['geom-fail']} geom-fail**, **{counts['audit']} audit** = **{counts['read_slots']} read slots**. The remaining **{counts['geometry-only']} geometry-only slots** have `nothing (geometry)` decisions, preserved in the full line record. Audit seed: `{AUDIT_SEED}`; 30 slots selected by SHA256 rank from the geometry-only pool before removal. Audited slots require both readings and do not inherit automatic decisions.\n\nInk screening retains any component bounding box intersecting a positive-width gap beyond digit-box edges, including crossing-component overhangs; this conservative screen may retain extra slots. It uses every component, not just horizontal strokes, with no fitted threshold. The one failed geometry is included using the complete native line plus a 3× whole-line zoom, without a fabricated gap marker; its truth still requires lead review.\n\n**Packs:** {contexts} contexts ×2 readers under `{PACKS/'n1t2'}`, plus `n1cal2/cal01/r1` (82 calibration items). Nine distinct controls per bed context include ≥1 raised dot and ≥1 each hyphen/en/em dash. Reverse order, fresh IDs, deranged option letters, ten sep2 meanings, and private measurements retain the N1-T structure. The original 54 `n1t` folders and private records remain byte-identical and superseded, inventoried with hashes in `n1t2/superseded.json`. The launcher explicitly accepts `n1t2`; post-reading combiner/owner builder now target that root.\n\nThe combiner requires both complete readings for every selected slot, including audit/failure slots, and inserts geometry-only nothing decisions for omitted slots. Owner rows preserve every gap and the complete Ours line, with geometry provenance named; nothing/space slots are not boxed. The existing owner sheet has not been rebuilt.\n\n**Closure {len(closures)}/{len(closures)} PASS** on all new packs; dry runs PASS for all new folders and all 54 preserved `n1t` folders. **{counts['tests_passed']} tests passed**, JUnit `N1Tb_TESTS.xml` and `N1Tb_IMAGE_TESTS.xml`. One historical pre-reading manifest test remains excluded because old r1 packs contain runtime files; preserved N1-T and new packs are independently sealed and verified. **Codex estimate:** {items-82} bed/control appearances + 82 calibration = **{items} items**, at 0.2 points/100 = **{counts['estimated_points']:.3f} points** (original estimate 9.648). No live usage probe, reading run, network, `.git` write, label edit, collector write, or owner-sheet publication. Receipt: `artifacts/n1/N1Tb_RECEIPT.json`.\n''')
    print(json.dumps(counts))


if __name__=='__main__':
    if sys.argv[1:]==['--verify']:verify()
    elif not sys.argv[1:]:prepare()
    else:raise ValueError('use no arguments to build, --verify after tests')
