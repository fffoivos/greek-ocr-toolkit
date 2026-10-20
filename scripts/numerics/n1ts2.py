"""N1-TS2 offline partial rulings, geometry audit, and fresh-order r3 preparation."""
import json
import os
from pathlib import Path
import subprocess
from collections import Counter
import n1ts
from n1t_packs import rows, sha, typed_controls, build
from n1_render import SCRATCH
from greekocr.numerics.locks import load_locks
BASE=n1ts.BASE
ROOT=n1ts.ROOT
REASONS={'void_context':'VOID','invalid_context_provenance':'invalid provenance',
         'reader_disagreement':'disagreement','low_confidence':'low confidence'}


def jsonl(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in data))


def seal_rulings():
    index=json.loads((n1ts.DEST/'sheets_index.json').read_text())
    cells={c['cell_number']:(s,c) for s in index['sheets'] if s['set']=='raised' for c in s['cells']}
    if set(cells)!=set(range(1,25)):raise ValueError('raised mapping changed')
    template={r['slot_id']:r for r in rows(BASE/'lead_t_template.jsonl')}
    rulings=[]
    for n,(sheet,c) in sorted(cells.items()):
        if sha(n1ts.DEST/sheet['file'])!=sheet['sha256']:raise ValueError('lead sheet changed')
        truth='hold' if n<=2 else 'raised dot' if n<=19 or n==22 else 'baseline dot' if n<=21 else 'nothing'
        r=dict(template[c['slot_id']],truth=truth,note='Lead raised-cell ruling; too faint, unresolved' if truth=='hold' else 'Lead printed-glyph verification',
               lead_cell=n,lead_sheet=sheet['file'],lead_sheet_sha256=sheet['sha256'],
               ruling_source='docs/records/labelfix/secondary/N1T_LEAD_RAISED.md',
               ruling_source_sha256=sha(ROOT/'docs/records/labelfix/secondary/N1T_LEAD_RAISED.md'))
        rulings.append(r)
    target=BASE/'lead_t.jsonl'
    expected=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rulings)
    if target.exists() and target.read_text()!=expected:raise ValueError('existing lead rulings differ')
    target.write_text(expected);target.with_suffix('.jsonl.sha256').write_text(sha(target)+'  lead_t.jsonl\n')
    return rulings


def geometry_audit(slots,decisions):
    byid={d['slot_id']:d for d in decisions}
    audit=[]
    for s in slots:
        if s['read_reason']!='audit':continue
        d=byid[s['slot_id']]
        audit.append(dict(slot_id=s['slot_id'],reads=d['reads'],raw_agree=all(r['meaning']=='nothing' for r in d['reads']),
                          nonspace_marks=sorted({r['meaning'] for r in d['reads'] if r['meaning'] not in ('nothing','space')})))
    return dict(slots=audit,agree=sum(a['raw_agree'] for a in audit),
                disagreements=[a for a in audit if not a['raw_agree']],
                reader_meanings={r:dict(Counter(v['meaning'] for a in audit for v in a['reads'] if v['reader']==r)) for r in ('r1','r2')},
                safe=False,conclusion='Not safe as a transcription rule: space/nothing differs and non-space calls include baseline dot, comma, other and unreadable. Retain geometry-only decisions provisionally in this authorized sheet; lead should widen the read set before accepting them. No extra reading or automatic rewrite performed.')


def prepare_r3(slots,decisions):
    selected=[d for d in decisions if d['status']=='lead_review' and d['reason'] in REASONS]
    byid={s['slot_id']:s for s in slots};bed=[byid[d['slot_id']] for d in selected]
    controls=typed_controls(rows(BASE/'controls/approved.jsonl'),rows(BASE/'controls/dash_types.jsonl'))
    out=BASE/'n1t3';packs=SCRATCH/'sol_packs/n1t3'
    if (out/'pack_build.json').exists():
        result=json.loads((out/'pack_build.json').read_text())
        if [r['slot_id'] for r in rows(out/'slots.jsonl')]!=[s['slot_id'] for s in bed]:raise ValueError('r3 selection changed')
    else:
        result=build(bed,controls,packs,out,load_locks(BASE),readers=('r3',),seed='20261017:N1TS2:r3:fresh')
        jsonl(out/'slots.jsonl',bed);jsonl(out/'controls/approved.jsonl',controls)
        n1ts.dump(out/'pack_build.json',result)
    # Fresh opaque IDs and option permutations are checked against ALL previous reads.
    oldkeys=[json.loads(p.read_text()) for p in (BASE/'n1t2/keys').glob('*.json')]
    oldids={i for k in oldkeys for i in k['items']}
    from n1_pack_closure import scan
    closure=[];dry=[]
    env=dict(os.environ,PATH=str(Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin')+':/usr/bin:/bin:/usr/sbin:/sbin')
    for c in result['contexts']:
        ctx=c['context'];directory=packs/ctx/'r3'
        key=json.loads((out/'keys'/(ctx+'.r3.json')).read_text())
        if oldids.intersection(key['items']):raise ValueError('reused r3 IDs')
        if (directory/'answers.jsonl').exists():raise ValueError('r3 unexpectedly run')
        check=scan(directory,out,completed=True,meanings=n1ts.MEANINGS)
        if not check['ok']:raise ValueError(check['violations'])
        closure.append(check)
        cmd=['/usr/bin/arch','-arm64',str(Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python3'),'-B',str(ROOT/'scripts/secondary/reading/n1_launch.py'),'n1t3',ctx,'r3','--dry-run']
        r=subprocess.run(cmd,env=env,capture_output=True,text=True)
        if r.returncode:raise ValueError(r.stdout+r.stderr)
        dry.append(json.loads(r.stdout))
    return dict(slots=len(bed),contexts=len(result['contexts']),by_reason=dict(Counter(REASONS[d['reason']] for d in selected)),
                deferred_by_reason=dict(Counter(d['reason'] for d in decisions if d['status']=='lead_review' and d['reason'] not in REASONS)),
                pack_root=str(packs),closure=closure,dry_runs=dry,build=result,
                policy='One r3 VALID high-confidence vote may pair with one existing VALID high-confidence vote; VOID/INVALID votes cannot establish truth. Geometry/dash conflicts and unreadable/other remain outside this fresh-reader selection. No new result is presumed.',
                slot_ids=[s['slot_id'] for s in bed])


def main():
    rulings=seal_rulings()
    summary=n1ts.phase2(True)
    slots,original,_,_=n1ts.combine()
    final=json.loads((n1ts.OUT/'lead_decisions.json').read_text())['decisions']
    audit=geometry_audit(slots,original);r3=prepare_r3(slots,final)
    receipt=dict(task='N1-TS phase 2',status='BUILT; tests pending',sheet=summary,
                 rulings=dict(count=len(rulings),meanings=dict(Counter(r['truth'] for r in rulings)),sha256=sha(BASE/'lead_t.jsonl')),
                 geometry_audit=audit,r3=r3,network=False,git_writes=False,reader_run=False,label_edits=0,
                 original_lead_review=dict(Counter(d['reason'] for d in original if d['status']=='lead_review')),
                 final_lead_review=dict(Counter(d['reason'] for d in final if d['status']=='lead_review')),
                 source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'docs/records/labelfix/secondary/N1T_LEAD_RAISED.md',BASE/'N1TS_PHASE1.json',BASE/'lead_t_template.jsonl']})
    n1ts.dump(BASE/'N1TS2_RECEIPT.json',receipt)
    print(json.dumps(dict(sheet=summary,r3_slots=r3['slots'],r3_contexts=r3['contexts'],r3_reasons=r3['by_reason'],geometry_reader_meanings=audit['reader_meanings']),ensure_ascii=False,indent=2))


def finalize():
    import xml.etree.ElementTree as ET
    target=BASE/'N1TS2_RECEIPT.json';r=json.loads(target.read_text())
    tests=BASE/'N1TS2_TESTS.xml';tree=ET.parse(tests)
    if tree.findall('.//failure') or tree.findall('.//error'):raise ValueError('tests failed')
    passed=len(tree.findall('.//testcase'))-len(tree.findall('.//skipped'))
    summary=json.loads((BASE/'N1TS_PHASE2.json').read_text())
    for name,h in summary['hashes'].items():
        if sha(BASE/'owner_sheet'/name)!=h:raise ValueError('owner product changed')
    legacy=BASE/'n1t2/phase1_owner_cards.json'
    phase1=json.loads((BASE/'N1TS_PHASE1.json').read_text())
    if sha(legacy)!=phase1['owner_products']['cards.json']:raise ValueError('prior card archive mismatch')
    if sha(BASE/'n1t2/phase1_owner_sheet.html')!=phase1['owner_sheet_sha256']:raise ValueError('prior sheet archive mismatch')
    r.update(status='READY',sheet=summary,tests=dict(passed=passed,path=str(tests.relative_to(ROOT)),sha256=sha(tests)),
             note_compatibility=dict(legacy_mapping_sha256=sha(BASE/'n1t2/legacy_note_ids.json'),
                 legacy_cards_sha256=sha(legacy),legacy_sheet_sha256=sha(BASE/'n1t2/phase1_owner_sheet.html'),
                 prior_cards_match_phase1=True,policy='Line IDs remain v2 document keys; only when absent, load legacy slot notes and explicitly owner-edited Printed text. Mocked shipped-JS readback passes for both owner notes, without writes. No live remote note check or republication.'),
             box_audit=dict(unlocalized_slots=summary['unlocalized_slots'],
                 geometry_only_unboxed=1070,physical_qa='Viewed native-derived raster with changed red solid, unchanged green solid, unsure amber dashed, explicit slot numbers in an added lane; no detector run.',
                 note='639 physically drawn unsure boxes plus one unlocalized unsure record. No gap coordinates fabricated.'),
             interpreter='x86_64 Python 3.11 -B -s / Pillow 10.4, pure-Python pytest appended; launcher dry-runs use explicit arm64 collector Python',
             publication='Local file rebuilt at the same path; lead republishes. No remote write.')
    files=['scripts/numerics/n1ts.py','scripts/numerics/n1ts2.py','scripts/numerics/n1t_packs.py',
           'scripts/numerics/n1t_boxes.py','scripts/numerics/n1t_owner_sheet.py','scripts/numerics/n1_map_answers.py',
           'scripts/secondary/reading/n1_launch.py','scripts/secondary/reading/run_n1.sh','greekocr/numerics/owner_v2.py',
           'tests/test_n1ts2.py','tests/test_n1ts.py','tests/test_n1t.py','tests/test_n1tb.py','tests/test_n1cal2s.py','tests/test_n1_score.py']
    r['source_hashes'].update({p:sha(ROOT/p) for p in files})
    r['r3']['record_hashes']={str(p.relative_to(ROOT)):sha(p) for p in (BASE/'n1t3').rglob('*') if p.is_file()}
    n1ts.dump(target,r)
    a=r['geometry_audit'];q=r['r3'];mb=summary['sheet_bytes']/1_000_000
    text=['## N1-TS phase 2','',
          f'**READY.** Local owner sheet v2 rebuilt at `artifacts/n1/owner_sheet/n1_sheet.html`: **{mb:.2f} MB** ({summary["sheet_bytes"]:,} bytes), **{summary["cards"]} complete-line cards**, Printed prefilled from Ours on all cards. The lead republishes to the same URL. No network, `.git` write, reading run, probe or training-label edit. The previous phase-1 owner cards and HTML are archived byte-identically under `n1t2/phase1_owner_*` and checked against the phase-1 receipt.', '',
          'The 24 raised cells were mapped through the sealed scratchpad `t_lead/sheets_index.json` into `artifacts/n1/lead_t.jsonl`: **18 raised dot, 2 baseline dot, 2 nothing, 2 hold (too faint)**. The original template remains intact. SHA256 `'+r['rulings']['sha256']+'`, sidecar `lead_t.jsonl.sha256`. Cells 18 and 22 get U+00B7 despite being outside the thousands grammar. The other label-edit rule is unchanged; 18 lead-verified edit candidates are recorded but no labels are edited.', '',
          '**Partial authority:** 22 resolved lead rulings (12 reaffirm existing decisions), with **640 unresolved slots** remaining, including holds 1/2. No review-sheet cell receives a ruling just because it was displayed. Every unresolved slot keeps Google in Ours and has an `unsure:<reason>` Gaps entry and card tag. Only lead-verified or agreeing VALID two-read raised dots enter the raised-hyphen group.', '',
          '| Group | Cards |','|---|---:|']
    from greekocr.numerics.owner_v2 import GROUPS
    text += [f'| {g} | {summary["groups"].get(g,0)} |' for g in GROUPS]
    text += ['', '**Boxes:** 162 changed (red solid), 257 unchanged (green solid), **639 unsure (amber dashed)**. All 1,070 geometry-only nothing slots stay named in Gaps and unboxed. One additional unsure slot, `elstat--fa8be8ddafd5c043--s000-l0110:t0:s2`, has reversed digit boxes: it has no physical gap box or number location, retains its whole-line zoom and explicit misaligned/unsure Gaps entry, and is excluded from the drawn-box counts. No coordinates were guessed. Other numbers use the original slot number even after unboxed slots are omitted. Physical raster QA and a dashed/solid raster test passed.', '',
             'The intro includes the required dashed-outline sentence. Google/Ours names, typed dashes, zooms, editable prefill and line IDs remain. To preserve the two existing owner notes across the slot-to-line change, the shipped note loader reads the SHA-bound legacy slot IDs only when no line note exists, retaining explicitly edited Printed text. A mocked execution of the shipped JavaScript verifies both notes and the absence of remote writes; live remote note loading is not verified offline.', '',
             '### Geometry-only audit', '',
             '**Not safe as a transcription rule.** Both readers said nothing on 17/30; **13/30 disagree**. Five are space-only disagreements, while **8 slots include non-space calls**. One baseline-dot slot has two VALID high-confidence votes. The 1,070 automatic nothing proposals are retained provisionally for this requested sheet, not qualified by this audit; the lead should widen the read set. No broader read set was generated or run.', '',
             '| Audit slot | r1 meaning / confidence / context gate | r2 meaning / confidence / context gate | Both nothing |',
             '|---|---|---|---|']
    for item in a['slots']:
        rr={v['reader']:v for v in item['reads']}
        desc=lambda v:v['meaning']+' / '+v['confidence']+' / '+v['context_status']
        text.append('| `'+item['slot_id']+'` | '+desc(rr['r1'])+' | '+desc(rr['r2'])+' | '+('yes' if item['raw_agree'] else 'NO')+' |')
    text+=['','Non-space disagreements requiring widened lead review:','']
    text += ['- `'+v['slot_id']+'`: '+', '.join(v['nonspace_marks'])+'.' for v in a['disagreements'] if v['nonspace_marks']]
    text+=['','Reader totals: r1 '+json.dumps(a['reader_meanings']['r1'])+'; r2 '+json.dumps(a['reader_meanings']['r2'])+'.', '',
           '### Third-reader triage', '',
           '| Fresh r3 reason | Original phase-1 slots | Remaining after lead rulings |', '|---|---:|---:|']
    text += [f'| {label} | {r["original_lead_review"][reason]} | {q["by_reason"][label]} |' for reason,label in REASONS.items()]
    text+=['',f'**{q["slots"]} slots in {q["contexts"]} contexts**, fresh seeded order `20261017:N1TS2:r3:fresh`, reader `r3`, root `n1t3`, unchanged `sep2.md`. Packs: `'+q['pack_root']+'`; private keys, slots and controls: `artifacts/n1/n1t3/`. Nine distinct approved controls per context include raised dot and each typed dash. At most 89 items per context, 54 controls total, 533 appearances. New opaque IDs, fresh option permutations and order distinct from both previous readers are checked. **Closure 6/6 and launcher dry runs 6/6 PASS. No r3 answers, logs, probes or readings.**', '',
           'Deferred outside this r3 selection: '+json.dumps(q['deferred_by_reason'])+'. A third vote can pair only with an existing VALID high-confidence vote; it cannot by itself repair geometry/dash conflicts or establish truth with a VOID/INVALID vote. Two faint lead holds remain unresolved.', '',
           f'**Tests: {passed} passed**, `artifacts/n1/N1TS2_TESTS.xml`. Includes partial/hold authority, out-of-thousands lead edits, complete pending retention, real control/pack seals, fresh r3 order/IDs, physical dashed boxes and original numbering, existing combiner/geometry/mapper/scorer regressions, and shipped-JS note compatibility. Historical scorer tests use the SHA-verified old sheet archive; custody tests permit only the specifically authorized owner-output replacement. Receipt: `artifacts/n1/N1TS2_RECEIPT.json`.']
    path=ROOT/'docs/records/labelfix/secondary/N1T_REPORT.md'
    old=path.read_text().split('\n## N1-TS phase 2')[0]
    path.write_text(old.rstrip()+'\n\n'+'\n'.join(text)+'\n')
    print(json.dumps(dict(sheet_mb=mb,cards=summary['cards'],groups=summary['groups'],boxes=summary['boxes'],r3_slots=q['slots'],r3_contexts=q['contexts'],tests=passed),ensure_ascii=False))


if __name__=='__main__':
    import sys
    if sys.argv[1:]==['--finalize']:finalize()
    elif not sys.argv[1:]:main()
    else:raise ValueError('use no arguments to build, --finalize after tests')
