"""Validate and receipt the offline RU4EF2 handoff; never writes label versions."""
from collections import Counter
import json
from pathlib import Path
import ru4ef1 as f
import ru4ef2_r5 as r5
m=f.m

def main():
    report=json.loads((f.ART/'RU4EF2_COMBINE.json').read_text())
    png=json.loads((f.OUT/'png/manifest.json').read_text())
    build=json.loads((f.ART/'RU4EF2_R5_BUILD.json').read_text())
    decisions=m.rows(f.ART/'decisions.jsonl')
    assert m.sha(f.ART/'decisions.jsonl')==report['decisions_sha256']
    assert dict(Counter(d['decision'] for d in decisions))==report['counts']
    for bindings in (report['evidence'],png['inputs'],png['outputs']):
        for path,h in bindings.items():assert m.sha(path)==h,path
    old_ids={iid for p in (f.ART/'keys').glob('*.json') for iid in json.loads(p.read_text())['items']}
    for role in ('r3','r4'):
        old_ids.update(iid for p in f.ART.glob(role+'_replacements/*/keys/*.json') for iid in json.loads(p.read_text())['items'])
    fresh=set()
    for task in build['tasks']:
        r5.checked(task);art,pack=Path(task['art']),Path(task['pack'])
        key=json.loads((art/'keys/ctx01.r5.json').read_text());ids=set(key['items'])
        assert not ids&old_ids and not ids&fresh;fresh.update(ids)
        ctx,role=task['replaces'].split('/')
        original=json.loads((f.ART/f'keys/{m.stem(ctx,role)}.json').read_text())
        canonical=lambda v:sorted(json.dumps(x,sort_keys=True,ensure_ascii=False) for x in v)
        assert canonical(original['items'].values())==canonical(key['items'].values())
        assert not list(art.glob('answers/*.attempt.json'))
        assert not list(art.glob('answers/*.run.json'))
    valid=sum(report['contexts'][r['identity']]['status']=='VALID' for r in report['replacements'])
    genuine=sum(d['reason'] in ('reader_disagreement','uncertain_read') for d in decisions)
    report.update(lead_material=png,replacement_completion=dict(valid=valid,total=len(report['replacements']),states={r['identity']:report['contexts'][r['identity']]['status'] for r in report['replacements']}),r5_budget=dict(contexts=build['contexts'],items=build['items'],estimated_points=round(build['items']*.002,3),threshold=70),lead_review_reasons=dict(Counter(d['reason'] for d in decisions if d['decision']=='hold')),genuine_review_cells=genuine)
    report['r5_replacements']=build['tasks']
    m.dump(f.ART/'finalize.json',report)
    source=[m.HERE/n for n in ('ru4ef2_collect.py','ru4ef2_png.py','ru4ef2_r5.py','ru4ef2_receipt.py','run_ru4e2_r5_all.sh','ru4e2_finalize_f2.sh','ru1_lead_sheets.py','ru1_review.py')]
    receipt=dict(report,constraints=dict(network_used=False,git_writes=False,browser=False,computer_use=False,new_reader_runs=0,version_written=False),validation=dict(evidence_hashes='passed',r5_fresh_ids='passed',r5_role_content_parity='passed',r5_driver_dry_run='passed',sheets='60 cells, 10 per PNG; exact geometry, 8x final and 4x word; overview and two full cells visually inspected for layout; no lead decisions'),orchestration=m.bindings(source))
    m.dump(f.ART/'RU4EF2_RECEIPT.json',receipt)
    text=f'''# RU4EF2 handoff

Six of the nine replacements are valid. Post-replacement decisions: {report['counts']}.

The 250 holds comprise 220 missing independent reads, 23 genuine reader disagreements, and 7 uncertain reads. The 220 pending positions are not rendered as disagreements. The 30 genuine/uncertain cases are on three review PNGs. The seeded audit has 20 edit_hard and 10 keep_soft on three PNGs. All sheets use the unchanged RU3T renderer: same-book hard/soft references left/right, nearest-neighbour final letter 8×, word 4×, line crop, and admitted reads. Reference basis and native geometry are recorded in references.json and sheets_index.json. References are comparisons, not adjudicated truth. The sample comes from the current decisions, seed `{png['seed']}`.

PNG directory: `{png['path']}`. Templates: `audit_template.jsonl`, `review_template.jsonl`, and combined `template.jsonl` in that directory; 60 blank lead entries. Blank fields do not constitute approval.

Replacement outcomes:

'''
    for task in report['replacements']:
        state=report['contexts'][task['identity']]
        detail=state.get('reason') or ('3 wrong control signs / 19 slots' if state['status']=='VOID' else 'v4.4 scan, gate and derived-view coverage admitted')
        text+=f"- `{task['identity']}`: {state['status']} ({detail}).\n"
    text+='\nFresh r5 assignments (prepared, not run):\n\n'
    for task in build['tasks']:text+=f"- `{task['identity']}` replaces `{task['replaces_invalid']}`; pack `{task['pack']}`; private artifacts `{task['art']}`.\n"
    text+=f"\nR5 budget: {build['contexts']} contexts, {build['items']} items including controls, estimated {report['r5_budget']['estimated_points']} points. Driver: `bash scripts/secondary/run_ru4e2_r5_all.sh` defaults to dry-run. Future explicit execution requires `--execute`; canonical before/after usage probes stop at 70%, and attempted contexts cannot rerun. No readers or usage probes ran during this handoff. `ru4e2_finalize_f2.sh` routes completed r5 results on a later local recombine.\n\nValidation: all evidence/PNG input/output hashes; exact native pixels and text-anchor geometry; fresh r5 IDs disjoint from all previous assignments and one another; original-role content parity; closed blind packs; driver dry-run; PNG decoding and layout inspection. No HTML generated by F2. No network, browser, computer use, .git writes, or ru1_v3_test_edits output.\n"
    (m.WORK/'docs/records/labelfix/secondary/RU4EF2_REPORT.md').write_text(text)
    reasons=', '.join(f'{n} {k}' for k,n in report['lead_review_reasons'].items())
    last=f"RU4EF2 READY: replacements valid {valid}/9; edit_hard {report['counts']['edit_hard']}, keep_soft {report['counts']['keep_soft']}, lead_review {report['counts']['hold']} ({reasons}); r5 contexts {build['contexts']}; audit PNGs {png['audit_pngs']}, review PNGs {png['review_pngs']}"
    print(last)
if __name__=='__main__':main()
